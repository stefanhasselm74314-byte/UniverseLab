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
import android.database.Cursor;
import android.provider.DocumentsContract;
import android.widget.BaseAdapter;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.TreeMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

public final class MainActivity extends Activity {
    private static final int PICK_JSON = 801;
    private static final int PICK_FOLDER = 802;
    private static final int PICK_ZIP = 803;
    private static final String PREFS = "chatarchiv-import";
    private static final String FOLDER_PREF = "read-only-tree-uri";

    private ChatStore store;
    private final ExecutorService importWorker = Executors.newSingleThreadExecutor();
    private final ExecutorService searchWorker = Executors.newSingleThreadExecutor();
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final AtomicInteger searchVersion = new AtomicInteger();
    private final List<ChatStore.Entry> displayed = new ArrayList<>();
    private ChatAdapter adapter;
    private TextView status;
    private TextView counts;
    private TextView firstRunHint;
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
        android.widget.Button importButton = Ui.button(this, "Chats importieren");
        android.widget.Button githubButton = Ui.button(this, "GitHub ansehen");
        actions.addView(importButton, Ui.weight(1));
        actions.addView(githubButton, Ui.weight(1));
        root.addView(actions);
        importButton.setOnClickListener(view -> showImportOptions());
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

        firstRunHint = Ui.text(this,
                "NOCH KEINE CHATS IMPORTIERT\n\n" +
                "Deine 545 geretteten Gespräche sind auf dem Handy, nicht in dieser APK.\n\n" +
                "1. Oben auf „Chats importieren“ tippen.\n" +
                "2. „Rettungsordner auswählen“ wählen.\n" +
                "3. Den Ordner „ChatGPT_Rettung_2026-11-08“ in Downloads auswählen.\n\n" +
                "Die sechs conversations-*.json werden dann gemeinsam eingelesen. " +
                "Ältere Export-ZIPs kannst du ebenfalls über „Chats importieren“ auswählen. " +
                "Die Dateien verlassen dein Smartphone nicht.", 15, false);
        firstRunHint.setTextColor(Ui.TEXT);
        firstRunHint.setBackgroundColor(Ui.SURFACE);
        firstRunHint.setPadding(Ui.dp(this, 13), Ui.dp(this, 14), Ui.dp(this, 13), Ui.dp(this, 14));
        root.addView(firstRunHint);

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

    private void showImportOptions() {
        if (importing) return;
        String saved = getPreferences(MODE_PRIVATE).getString(FOLDER_PREF, null);
        String[] options = saved == null
                ? new String[] {"Rettungsordner auswählen (empfohlen)", "Einzelne JSON-Dateien auswählen", "Ältere Export-ZIPs auswählen"}
                : new String[] {"Gespeicherten Ordner aktualisieren", "Anderen Rettungsordner auswählen", "Einzelne JSON-Dateien auswählen", "Ältere Export-ZIPs auswählen"};
        new AlertDialog.Builder(this)
                .setTitle("Chats lokal importieren · kein Upload")
                .setItems(options, (dialog, which) -> {
                    if (saved != null && which == 0) importFolder(Uri.parse(saved));
                    else if ((saved == null && which == 0) || (saved != null && which == 1)) chooseFolder();
                    else if (which == options.length - 1) chooseZip();
                    else chooseJson();
                }).setNegativeButton("Abbrechen", null).show();
    }

    private void chooseFolder() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        startActivityForResult(intent, PICK_FOLDER);
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

    private void chooseZip() {
        if (importing) return;
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        startActivityForResult(intent, PICK_ZIP);
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode != RESULT_OK || data == null) return;
        if (requestCode == PICK_FOLDER) {
            Uri tree = data.getData();
            if (tree == null) return;
            try {
                getContentResolver().takePersistableUriPermission(tree, Intent.FLAG_GRANT_READ_URI_PERMISSION);
                getPreferences(MODE_PRIVATE).edit().putString(FOLDER_PREF, tree.toString()).apply();
            } catch (SecurityException exception) {
                status.setText("Ordnerfreigabe nicht dauerhaft möglich: " + exception.getMessage());
            }
            importFolder(tree);
            return;
        }
        if (requestCode != PICK_JSON && requestCode != PICK_ZIP) return;
        ArrayList<Uri> files = new ArrayList<>();
        ClipData clip = data.getClipData();
        if (clip != null) {
            for (int i = 0; i < clip.getItemCount(); i++) files.add(clip.getItemAt(i).getUri());
        } else if (data.getData() != null) {
            files.add(data.getData());
        }
        startImport(files);
    }

    private void importFolder(Uri tree) {
        if (importing) return;
        status.setText("Suche conversations-*.json im ausgewählten Ordner …");
        importWorker.execute(() -> {
            try {
                TreeMap<String, Uri> selected = new TreeMap<>();
                String treeId = DocumentsContract.getTreeDocumentId(tree);
                Uri children = DocumentsContract.buildChildDocumentsUriUsingTree(tree, treeId);
                String[] projection = {
                        DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                        DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                        DocumentsContract.Document.COLUMN_MIME_TYPE
                };
                try (Cursor cursor = getContentResolver().query(children, projection, null, null, null)) {
                    if (cursor == null) throw new IOException("Ordnerinhalt nicht lesbar");
                    while (cursor.moveToNext()) {
                        String id = cursor.getString(0);
                        String name = cursor.getString(1);
                        String mime = cursor.getString(2);
                        if (name == null || DocumentsContract.Document.MIME_TYPE_DIR.equals(mime)) continue;
                        if (!name.matches("conversations(-[0-9]+)?\\.json")) continue;
                        selected.put(name, DocumentsContract.buildDocumentUriUsingTree(tree, id));
                    }
                }
                if (selected.isEmpty()) throw new IOException("Keine conversations-*.json gefunden. Bitte den Unterordner ChatGPT_Rettung_2026-11-08 auswählen.");
                runOnUiThread(() -> startImport(new ArrayList<>(selected.values())));
            } catch (Exception exception) {
                runOnUiThread(() -> new AlertDialog.Builder(this)
                        .setTitle("Importordner nicht lesbar")
                        .setMessage(exception.getMessage())
                        .setPositiveButton("Ordner neu auswählen", (dialog, which) -> chooseFolder())
                        .setNegativeButton("Schließen", null).show());
            }
        });
    }

    private void startImport(List<Uri> files) {
        if (files.isEmpty() || importing) return;
        importing = true;
        status.setText("Import läuft … (" + files.size() + " Datei(en))");
        importWorker.execute(() -> {
            ChatStore.ImportResult result = store.importFiles(files, (added, updated, unchanged) ->
                    runOnUiThread(() -> status.setText("Import: " + added + " neu, " + updated
                            + " geändert, " + unchanged + " bereits identisch …")));
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
        if (firstRunHint != null) firstRunHint.setVisibility(all.isEmpty() ? View.VISIBLE : View.GONE);
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
