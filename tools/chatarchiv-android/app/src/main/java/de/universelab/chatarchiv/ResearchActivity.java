package de.universelab.chatarchiv;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;

import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/** Local screening, no AI service, account access, uploads or repository mutations. */
public final class ResearchActivity extends Activity {
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private final AtomicBoolean cancel = new AtomicBoolean();
    private final List<ResearchFinder.Finding> findings = new ArrayList<>();
    private TextView status;
    private Button cancelButton;
    private FindingsAdapter adapter;
    private boolean scanning;

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        LinearLayout root = Ui.column(this, 12);
        setContentView(root);

        Button back = Ui.button(this, "‹ Zurück zum ChatArchiv");
        back.setOnClickListener(view -> finish());
        root.addView(back);
        root.addView(Ui.text(this, "UniverseLab · Forschungsnavigator", 21, true));
        TextView note = Ui.text(this,
                "Offline-Prüfung gespeicherter Chats. Gefundene Stellen sind Hinweise, KEINE bestätigten "
                        + "Forschungslücken. Ältere Aussagen können längst überholt sein. "
                        + "Die App beweist keine Theorie und lädt keine Gespräche hoch.", 12, false);
        note.setTextColor(Ui.MUTED);
        root.addView(note);

        LinearLayout actions = Ui.row(this);
        Button project = Ui.button(this, "UniverseLab prüfen");
        Button all = Ui.button(this, "Alle Chats prüfen");
        actions.addView(project, Ui.weight(1));
        actions.addView(all, Ui.weight(1));
        root.addView(actions);
        project.setOnClickListener(view -> beginScan(false));
        all.setOnClickListener(view -> beginScan(true));

        cancelButton = Ui.button(this, "Prüfung abbrechen");
        cancelButton.setVisibility(View.GONE);
        cancelButton.setOnClickListener(view -> {
            cancel.set(true);
            status.setText("Abbruch angefordert …");
        });
        root.addView(cancelButton);

        status = Ui.text(this, "Bereit. Untersuchung auf diesem Gerät starten.", 12, false);
        status.setTextColor(Ui.ACCENT);
        root.addView(status);

        ListView list = new ListView(this);
        list.setDivider(null);
        list.setDividerHeight(Ui.dp(this, 7));
        adapter = new FindingsAdapter();
        list.setAdapter(adapter);
        list.setOnItemClickListener((parent, view, position, id) -> {
            if (position < 0 || position >= findings.size()) return;
            Intent intent = new Intent(this, ConversationActivity.class);
            intent.putExtra("chatId", findings.get(position).chatId);
            // Message numbers are 1-based in the result card, 0-based in the list.
            intent.putExtra("focusMessageIndex", findings.get(position).messageNumber - 1);
            startActivity(intent);
        });
        root.addView(list, Ui.fillRemaining());
        beginScan(false);
    }

    private void beginScan(boolean includeAll) {
        if (scanning) return;
        scanning = true;
        cancel.set(false);
        findings.clear();
        adapter.notifyDataSetChanged();
        cancelButton.setVisibility(View.VISIBLE);
        status.setText("Suche nach expliziten offenen Punkten und Prüfaufträgen …");
        worker.execute(() -> {
            List<ResearchFinder.Finding> next = new ArrayList<>();
            int checked = 0;
            int errors = 0;
            try {
                ChatStore store = new ChatStore(this);
                List<ChatStore.Entry> entries = store.snapshot();
                for (ChatStore.Entry entry : entries) {
                    if (cancel.get() || Thread.currentThread().isInterrupted()) break;
                    if (!includeAll && !ChatStore.PROJECT.equals(entry.category)) continue;
                    try {
                        JSONObject conversation = store.loadConversation(entry.id);
                        next.addAll(ResearchFinder.extract(entry.id, entry.title,
                                ConversationLogic.visibleMessages(conversation), 5));
                    } catch (Exception unreadable) {
                        errors++;
                    }
                    checked++;
                    if (checked % 5 == 0) {
                        int count = checked;
                        runOnUiThread(() -> {
                            if (!isFinishing()) status.setText(count + " Chats lokal geprüft …");
                        });
                    }
                }
            } catch (IOException unreadableIndex) {
                errors++;
            }
            next.sort(Comparator.comparingInt((ResearchFinder.Finding f) -> f.priority).reversed());
            int total = next.size();
            if (next.size() > 100) next = new ArrayList<>(next.subList(0, 100));
            List<ResearchFinder.Finding> result = next;
            int done = checked;
            int failed = errors;
            boolean interrupted = cancel.get();
            runOnUiThread(() -> {
                if (isFinishing() || isDestroyed()) return;
                findings.clear();
                findings.addAll(result);
                adapter.notifyDataSetChanged();
                scanning = false;
                cancelButton.setVisibility(View.GONE);
                status.setText((interrupted ? "Abgebrochen · " : "Prüfung abgeschlossen · ")
                        + done + " Chats · " + total + " Hinweise (max. 100 angezeigt)"
                        + (failed > 0 ? " · " + failed + " nicht lesbar" : "")
                        + ". Antippen öffnet den Originalchat.");
            });
        });
    }

    @Override protected void onDestroy() {
        cancel.set(true);
        worker.shutdownNow();
        super.onDestroy();
    }

    private final class FindingsAdapter extends BaseAdapter {
        @Override public int getCount() { return findings.size(); }
        @Override public Object getItem(int position) { return findings.get(position); }
        @Override public long getItemId(int position) { return position; }

        @Override public View getView(int position, View recycled, ViewGroup parent) {
            ResearchFinder.Finding f = findings.get(position);
            LinearLayout card = Ui.column(ResearchActivity.this, 9);
            card.setBackgroundColor(Ui.SURFACE);
            TextView title = Ui.text(ResearchActivity.this,
                    f.kind + " · " + f.field + "\n" + f.chatTitle, 15, true);
            title.setTextColor(Ui.ACCENT);
            card.addView(title);
            TextView evidence = Ui.text(ResearchActivity.this,
                    "Fundstelle aus " + f.role + "-Beitrag " + f.messageNumber + ": " + f.excerpt,
                    13, false);
            evidence.setMaxLines(5);
            card.addView(evidence);
            card.addView(Ui.text(ResearchActivity.this,
                    "Prüffrage: " + f.question + "\nPrüfweg: " + f.verification, 12, false));
            TextView warning = Ui.text(ResearchActivity.this,
                    "[HEURISTISCH] · Stand nicht verifiziert · Tippen: Quellchat öffnen", 11, false);
            warning.setTextColor(Ui.MUTED);
            card.addView(warning);
            return card;
        }
    }
}
