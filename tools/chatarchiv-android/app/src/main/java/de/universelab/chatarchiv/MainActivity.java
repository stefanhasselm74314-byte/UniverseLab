package de.universelab.chatarchiv;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.Intent;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.InputMethodManager;
import android.content.Context;
import android.widget.BaseAdapter;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

public final class MainActivity extends Activity {
    private static final int PICK_JSON = 801;

    private ChatStore store;
    private final ExecutorService importWorker = Executors.newSingleThreadExecutor();
    private final ExecutorService searchWorker = Executors.newSingleThreadExecutor();
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final AtomicInteger searchVersion = new AtomicInteger();
    private final List<ChatStore.Entry> displayed = new ArrayList<>();
    private ChatAdapter adapter;
    private TextView status;
    private TextView counts;
    private EditText search;
    private String category = ChatStore.PROJECT;
    private String importSummary = "";
    private boolean importing;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        try {
            store = new ChatStore(this);
        } catch (IOException exception) {
            new AlertDialog.Builder(this).setTitle("Archiv nicht lesbar")
                    .setMessage(exception.getMessage()).setPositiveButton("Schließen", (dialog, which) -> finish())
                    .setCancelable(false).show();
            return;
        }
        buildScreen();
        refresh();
    }

    private void buildScreen() {
        LinearLayout root = Ui.column(this, 12);
        setContentView(root);

        root.addView(Ui.text(this, "UniverseLab ChatArchiv", 23, true));
        TextView subtitle = Ui.text(this, "Lokal · private Chats · GitHub nur lesen", 12, false);
        subtitle.setTextColor(Ui.MUTED);
        root.addView(subtitle);
        Ui.addGap(this, root, 8);

        LinearLayout actions = Ui.row(this);
        android.widget.Button importButton = Ui.button(this, "Import / Update");
        android.widget.Button githubButton = Ui.button(this, "GitHub ansehen");
        actions.addView(importButton, Ui.weight(1));
        actions.addView(githubButton, Ui.weight(1));
        root.addView(actions);
        importButton.setOnClickListener(view -> chooseJson());
        githubButton.setOnClickListener(view -> startActivity(new Intent(this, GitHubActivity.class)));

        Ui.addGap(this, root, 10);
        LinearLayout tabs = Ui.row(this);
        android.widget.Button all = Ui.button(this, "Alle");
        android.widget.Button project = Ui.button(this, "UniverseLab");
        android.widget.Button other = Ui.button(this, "Weitere Chats");
        tabs.addView(all, Ui.weight(0.7f));
        tabs.addView(project, Ui.weight(1.3f));
        tabs.addView(other, Ui.weight(1.4f));
        root.addView(tabs);
        all.setOnClickListener(view -> chooseCategory("alle"));
        project.setOnClickListener(view -> chooseCategory(ChatStore.PROJECT));
        other.setOnClickListener(view -> chooseCategory(ChatStore.OTHER));

        search = new EditText(this);
        search.setSingleLine(true);
        search.setHint("Titel und Gesprächstext suchen …");
        search.setHintTextColor(Ui.MUTED);
        search.setTextColor(Ui.TEXT);
        search.setTextSize(15);
        search.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Ui.ACCENT));
        root.addView(search);
        search.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) { }
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) { scheduleSearch(); }
            @Override public void afterTextChanged(Editable e) { }
        });

        counts = Ui.text(this, "", 12, false);
        counts.setTextColor(Ui.MUTED);
        root.addView(counts);
        status = Ui.text(this, "", 12, false);
        status.setTextColor(Ui.ACCENT);
        root.addView(status);

        ListView list = new ListView(this);
        list.setDividerHeight(Ui.dp(this, 6));
        list.setDivider(null);
        adapter = new ChatAdapter();
        list.setAdapter(adapter);
        list.setOnItemClickListener((parent, view, position, id) -> {
            if (position < 0 || position >= displayed.size()) return;
            Intent intent = new Intent(this, ConversationActivity.class);
            intent.putExtra("chatId", displayed.get(position).id);
            startActivity(intent);
        });
        list.setOnItemLongClickListener((parent, view, position, id) -> {
            if (position >= 0 && position < displayed.size()) moveChat(displayed.get(position));
            return true;
        });
        root.addView(list, Ui.fillRemaining());

        TextView footer = Ui.text(this, "Lange auf ein Gespräch tippen: Bereich ändern · Kein Cloud-Backup", 11, false);
        footer.setTextColor(Ui.MUTED);
        root.addView(footer);
    }

    private void chooseCategory(String value) {
        category = value;
        refresh();
    }

    private void moveChat(ChatStore.Entry entry) {
        String destination = ChatStore.PROJECT.equals(entry.category) ? ChatStore.OTHER : ChatStore.PROJECT;
        String label = ChatStore.PROJECT.equals(destination) ? "UniverseLab" : "Weitere Chats";
        new AlertDialog.Builder(this)
                .setTitle("Gespräch zuordnen")
                .setMessage("„" + entry.title + "“ nach „" + label + "“ verschieben?")
                .setNegativeButton("Abbrechen", null)
                .setPositiveButton("Verschieben", (dialog, choice) -> {
                    try {
                        store.setCategory(entry.id, destination);
                        refresh();
                    } catch (IOException exception) {
                        status.setText("Speicherfehler: " + exception.getMessage());
                    }
                }).show();
    }

    private void chooseJson() {
        if (importing) return;
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        startActivityForResult(intent, PICK_JSON);
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != PICK_JSON || resultCode != RESULT_OK || data == null) return;
        ArrayList<Uri> files = new ArrayList<>();
        ClipData clip = data.getClipData();
        if (clip != null) {
            for (int i = 0; i < clip.getItemCount(); i++) files.add(clip.getItemAt(i).getUri());
        } else if (data.getData() != null) {
            files.add(data.getData());
        }
        if (files.isEmpty()) return;
        importing = true;
        status.setText("Import läuft … (" + files.size() + " Datei(en))");
        importWorker.execute(() -> {
            ChatStore.ImportResult result = store.importFiles(files, (added, updated) ->
                    runOnUiThread(() -> status.setText("Import: " + added + " neu, " + updated + " aktualisiert …")));
            runOnUiThread(() -> {
                importing = false;
                importSummary = result.summary();
                refresh();
            });
        });
    }

    private void refresh() {
        if (store == null) return;
        List<ChatStore.Entry> all = store.snapshot();
        int project = 0;
        for (ChatStore.Entry entry : all) if (ChatStore.PROJECT.equals(entry.category)) project++;
        counts.setText(all.size() + " Gespräche · " + project + " UniverseLab · "
                + (all.size() - project) + " weitere");
        scheduleSearch();
    }

    private void scheduleSearch() {
        if (search == null || store == null) return;
        int serial = searchVersion.incrementAndGet();
        String phrase = search.getText().toString();
        String selected = category;
        List<ChatStore.Entry> copy = store.snapshot();
        handler.postDelayed(() -> {
            if (searchVersion.get() != serial) return;
            status.setText(phrase.trim().isEmpty() ? importSummary : "Suche im Archiv …");
            searchWorker.execute(() -> {
                List<ChatStore.Entry> matches = ChatStore.search(copy, selected, phrase,
                        () -> searchVersion.get() != serial || Thread.currentThread().isInterrupted(),
                        store.privateConversationDirectory());
                runOnUiThread(() -> {
                    if (searchVersion.get() != serial) return;
                    displayed.clear();
                    displayed.addAll(matches);
                    adapter.notifyDataSetChanged();
                    if (!phrase.trim().isEmpty()) status.setText(matches.size() + " Treffer");
                    else status.setText(importSummary);
                });
            });
        }, 220);
    }

    @Override protected void onDestroy() {
        searchVersion.incrementAndGet();
        handler.removeCallbacksAndMessages(null);
        searchWorker.shutdownNow();
        importWorker.shutdownNow();
        super.onDestroy();
    }

    private final class ChatAdapter extends BaseAdapter {
        @Override public int getCount() { return displayed.size(); }
        @Override public Object getItem(int position) { return displayed.get(position); }
        @Override public long getItemId(int position) { return position; }

        @Override public View getView(int position, View convertView, ViewGroup parent) {
            LinearLayout box = Ui.column(MainActivity.this, 10);
            box.setBackgroundColor(Ui.SURFACE);
            ChatStore.Entry entry = displayed.get(position);
            TextView title = Ui.text(MainActivity.this, entry.title, 16, true);
            title.setMaxLines(3);
            box.addView(title);
            String description = entry.prettyDate() + " · " +
                    (ChatStore.PROJECT.equals(entry.category) ? "UniverseLab" : "Weitere Chats");
            TextView sub = Ui.text(MainActivity.this, description, 12, false);
            sub.setTextColor(Ui.MUTED);
            box.addView(sub);
            return box;
        }
    }
}
