package de.universelab.chatarchiv;

import android.app.Activity;
import android.app.AlertDialog;
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
import java.util.IdentityHashMap;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/** Local screening, no AI service, account access, uploads or repository mutations. */
public final class ResearchActivity extends Activity {
    private static final String[] TYPE_FILTERS = {
            "Alle Kategorien", "Blocker", "Konflikt", "Offener Punkt", "Nächster Schritt"};
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private final AtomicBoolean cancel = new AtomicBoolean();
    private final List<ResearchFinder.Finding> allFindings = new ArrayList<>();
    private final List<ResearchFinder.Finding> findings = new ArrayList<>();
    private final Map<ResearchFinder.Finding, ResearchTimeline.Review> reviews =
            new IdentityHashMap<>();
    private TextView status;
    private Button cancelButton;
    private Button filterButton;
    private Button scopeButton;
    private Button moreButton;
    private FindingsAdapter adapter;
    private boolean scanning;
    private boolean scanInterrupted;
    private int checkedChats;
    private int unreadableChats;
    private int selectedFilter;
    private int selectedScope;
    private int showLimit = 100;

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        LinearLayout root = Ui.column(this, 12);
        setContentView(root);
        Ui.applySystemBarInsets(root);

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

        filterButton = Ui.button(this, "Filter: Alle Kategorien ▾");
        filterButton.setOnClickListener(view -> new AlertDialog.Builder(this)
                .setTitle("Hinweisarten auswählen")
                .setSingleChoiceItems(TYPE_FILTERS, selectedFilter, (dialog, which) -> {
                    selectedFilter = which;
                    showLimit = 100;
                    filterButton.setText("Filter: " + TYPE_FILTERS[which] + " ▾");
                    showFilteredResults();
                    dialog.dismiss();
                }).setNegativeButton("Abbrechen", null).show());
        root.addView(filterButton);

        scopeButton = Ui.button(this, "Bereich: Alle Bereiche ▾");
        scopeButton.setOnClickListener(view -> new AlertDialog.Builder(this)
                .setTitle("Heuristischen Fachbereich auswählen")
                .setSingleChoiceItems(ResearchScope.FILTERS, selectedScope, (dialog, which) -> {
                    selectedScope = which;
                    showLimit = 100;
                    scopeButton.setText("Bereich: " + ResearchScope.FILTERS[which] + " ▾");
                    showFilteredResults();
                    dialog.dismiss();
                }).setNegativeButton("Abbrechen", null).show());
        root.addView(scopeButton);

        ListView list = new WideGripListView(this);
        list.setDivider(null);
        list.setDividerHeight(Ui.dp(this, 7));
        Ui.configurePersistentFastScroll(list);
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
        // Short tap keeps the original source link. Long tap opens a later candidate
        // status statement, when a uniquely keyed link could be made.
        list.setOnItemLongClickListener((parent, view, position, id) -> {
            if (position < 0 || position >= findings.size()) return false;
            ResearchTimeline.Review review = reviews.get(findings.get(position));
            if (review == null || review.source == null) return false;
            Intent intent = new Intent(this, ConversationActivity.class);
            intent.putExtra("chatId", review.source.chatId);
            intent.putExtra("focusMessageIndex", review.source.messageNumber - 1);
            startActivity(intent);
            return true;
        });
        root.addView(list, Ui.fillRemaining());

        moreButton = Ui.button(this, "Weitere Fundstellen anzeigen");
        moreButton.setVisibility(View.GONE);
        moreButton.setOnClickListener(view -> {
            showLimit += 100;
            showFilteredResults();
        });
        root.addView(moreButton);
        beginScan(false);
    }

    private void beginScan(boolean includeAll) {
        if (scanning) return;
        scanning = true;
        cancel.set(false);
        allFindings.clear();
        findings.clear();
        reviews.clear();
        adapter.notifyDataSetChanged();
        showLimit = 100;
        filterButton.setEnabled(false);
        scopeButton.setEnabled(false);
        moreButton.setVisibility(View.GONE);
        cancelButton.setVisibility(View.VISIBLE);
        status.setText("Suche nach expliziten offenen Punkten und Prüfaufträgen …");
        worker.execute(() -> {
            List<ResearchFinder.Finding> next = new ArrayList<>();
            List<ResearchTimeline.StatusEvidence> chronology = new ArrayList<>();
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
                        List<ConversationLogic.Message> visible =
                                ConversationLogic.visibleMessages(conversation);
                        next.addAll(ResearchFinder.extract(entry.id, entry.title, visible, 5));
                        chronology.addAll(ResearchTimeline.collect(entry.id, entry.title, visible));
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
            Map<ResearchFinder.Finding, ResearchTimeline.Review> statusReviews =
                    ResearchTimeline.reconcile(next, chronology);
            List<ResearchFinder.Finding> result = next;
            int done = checked;
            int failed = errors;
            boolean interrupted = cancel.get();
            runOnUiThread(() -> {
                if (isFinishing() || isDestroyed()) return;
                allFindings.clear();
                allFindings.addAll(result);
                reviews.clear();
                reviews.putAll(statusReviews);
                scanning = false;
                scanInterrupted = interrupted;
                checkedChats = done;
                unreadableChats = failed;
                cancelButton.setVisibility(View.GONE);
                filterButton.setEnabled(true);
                scopeButton.setEnabled(true);
                showFilteredResults();
            });
        });
    }

    private void showFilteredResults() {
        findings.clear();
        int matching = 0;
        for (ResearchFinder.Finding finding : allFindings) {
            if (selectedFilter != 0 && !TYPE_FILTERS[selectedFilter].equals(finding.kind)) continue;
            if (selectedScope != 0 && !ResearchScope.FILTERS[selectedScope].equals(finding.scope)) continue;
            matching++;
            if (findings.size() < showLimit) findings.add(finding);
        }
        adapter.notifyDataSetChanged();
        int linked = 0;
        for (ResearchFinder.Finding finding : findings) {
            ResearchTimeline.Review review = reviews.get(finding);
            if (review != null && review.source != null) linked++;
        }
        int remaining = matching - findings.size();
        moreButton.setVisibility(remaining > 0 ? View.VISIBLE : View.GONE);
        if (remaining > 0) moreButton.setText("Weitere " + Math.min(100, remaining) + " anzeigen · " + remaining + " übrig");
        status.setText((scanInterrupted ? "Abgebrochen · " : "Prüfung abgeschlossen · ")
                + checkedChats + " Chats · " + allFindings.size() + " heuristische Hinweise · "
                + findings.size() + " von " + matching + " im Filter angezeigt"
                + " · " + linked + " spätere Statusverknüpfungen unter angezeigten Fundstellen"
                + (unreadableChats > 0 ? " · " + unreadableChats + " nicht lesbar" : "")
                + ". Antippen öffnet den Originalbeitrag.");
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
            TextView scopeLabel = Ui.text(ResearchActivity.this,
                    "Bereich [HEURISTISCH]: " + f.scope, 11, false);
            scopeLabel.setTextColor(Ui.MUTED);
            card.addView(scopeLabel);
            TextView triggerLabel = Ui.text(ResearchActivity.this,
                    "Auslöser [HEURISTISCH]: " + f.signal, 11, false);
            triggerLabel.setTextColor(Ui.ACCENT);
            card.addView(triggerLabel);
            TextView evidence = Ui.text(ResearchActivity.this,
                    "Fundstelle aus " + f.role + "-Beitrag " + f.messageNumber + ": "
                            + f.displayExcerpt, 13, false);
            evidence.setMaxLines(5);
            card.addView(evidence);
            card.addView(Ui.text(ResearchActivity.this,
                    "Prüffrage: " + f.question + "\nPrüfweg: " + f.verification, 12, false));
            TextView warning = Ui.text(ResearchActivity.this,
                    "[HEURISTISCH] · Stand nicht verifiziert · Tippen: Quellchat öffnen", 11, false);
            warning.setTextColor(Ui.MUTED);
            card.addView(warning);

            ResearchTimeline.Review review = reviews.get(f);
            if (review != null) {
                TextView current = Ui.text(ResearchActivity.this,
                        "Verlaufsabgleich [HEURISTISCH]: " + review.summary, 11, false);
                current.setTextColor(review.source == null ? Ui.MUTED : Ui.ACCENT);
                card.addView(current);
                if (review.source != null) {
                    card.addView(Ui.text(ResearchActivity.this,
                            "Spätere Aussage zu " + review.identifier + ": "
                                    + review.source.chatTitle + " · "
                                    + review.source.role + "-Beitrag "
                                    + review.source.messageNumber + "\n"
                                    + review.source.excerpt
                                    + "\nLange tippen: diesen späteren Beitrag öffnen.",
                            11, false));
                }
            }
            return card;
        }
    }
}
