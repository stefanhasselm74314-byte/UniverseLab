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
import android.widget.Spinner;
import android.widget.EditText;
import android.widget.ArrayAdapter;
import android.text.InputFilter;

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

        // Two compact navigation controls instead of a growing stack of scan buttons.
        LinearLayout actions = Ui.row(this);
        Button scanMenu = Ui.button(this, "Chats prüfen ▾");
        Button registerButton = Ui.button(this, "Forschungsregister");
        actions.addView(scanMenu, Ui.weight(1));
        actions.addView(registerButton, Ui.weight(1));
        root.addView(actions);
        scanMenu.setOnClickListener(view -> new AlertDialog.Builder(this)
                .setTitle("Chats für Fundstellenprüfung")
                .setItems(new String[]{"UniverseLab prüfen", "Alle Chats prüfen"},
                        (dialog, index) -> beginScan(index == 1))
                .setNegativeButton("Abbrechen", null).show());
        registerButton.setOnClickListener(view ->
                startActivity(new Intent(this, ResearchRegisterActivity.class)));

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

        filterButton = Ui.button(this, "Hinweisart ▾");
        filterButton.setOnClickListener(view -> new AlertDialog.Builder(this)
                .setTitle("Hinweisarten auswählen")
                .setSingleChoiceItems(TYPE_FILTERS, selectedFilter, (dialog, which) -> {
                    selectedFilter = which;
                    showLimit = 100;
                    filterButton.setText(selectedFilter == 0 ? "Hinweisart ▾" : TYPE_FILTERS[which] + " ▾");
                    showFilteredResults();
                    dialog.dismiss();
                }).setNegativeButton("Abbrechen", null).show());

        scopeButton = Ui.button(this, "Fachbereich ▾");
        scopeButton.setOnClickListener(view -> new AlertDialog.Builder(this)
                .setTitle("Heuristischen Fachbereich auswählen")
                .setSingleChoiceItems(ResearchScope.FILTERS, selectedScope, (dialog, which) -> {
                    selectedScope = which;
                    showLimit = 100;
                    scopeButton.setText(selectedScope == 0 ? "Fachbereich ▾" : ResearchScope.FILTERS[which] + " ▾");
                    showFilteredResults();
                    dialog.dismiss();
                }).setNegativeButton("Abbrechen", null).show());
        LinearLayout filters = Ui.row(this);
        filters.addView(filterButton, Ui.weight(1));
        filters.addView(scopeButton, Ui.weight(1));
        root.addView(filters);

        ListView list = new WideGripListView(this);
        list.setDivider(null);
        list.setDividerHeight(Ui.dp(this, 7));
        Ui.configurePersistentFastScroll(list);
        adapter = new FindingsAdapter();
        list.setAdapter(adapter);
        list.setOnItemClickListener((parent, view, position, id) -> {
            if (position < 0 || position >= findings.size()) return;
            ResearchFinder.Finding finding = findings.get(position);
            openContribution(finding.chatId, finding.messageNumber);
        });
        // A heuristic candidate is never automatically promoted to a reviewed item.
        // Long press offers an explicit, manually confirmed research registration.
        list.setOnItemLongClickListener((parent, view, position, id) -> {
            if (position < 0 || position >= findings.size()) return false;
            showFindingActions(findings.get(position));
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

    private void openContribution(String chatId, int messageNumber) {
        Intent intent = new Intent(this, ConversationActivity.class);
        intent.putExtra("chatId", chatId);
        intent.putExtra("focusMessageIndex", messageNumber - 1);
        startActivity(intent);
    }

    private void showFindingActions(ResearchFinder.Finding finding) {
        ResearchTimeline.Review review = reviews.get(finding);
        boolean hasLater = review != null && review.source != null;
        String[] actions = hasLater
                ? new String[]{"Fundstelle ins Forschungsregister aufnehmen",
                        "Originalbeitrag öffnen", "Spätere Statusaussage öffnen"}
                : new String[]{"Fundstelle ins Forschungsregister aufnehmen",
                        "Originalbeitrag öffnen"};
        new AlertDialog.Builder(this).setTitle("Fundstelle: " + finding.kind)
                .setItems(actions, (dialog, index) -> {
                    if (index == 0) saveManualFinding(finding);
                    else if (index == 1) openContribution(finding.chatId, finding.messageNumber);
                    else if (hasLater) openContribution(
                            review.source.chatId, review.source.messageNumber);
                }).setNegativeButton("Abbrechen", null).show();
    }

    private void saveManualFinding(ResearchFinder.Finding finding) {
        if (scanning) return;
        try {
            ResearchRegister register = new ResearchRegister(this);
            ResearchRegister.Record existing = register.get(ResearchRegister.idForFinding(finding));
            ResearchRegisterActivity.promptReview(this, existing, (stage, state, note) -> {
                register.addFinding(finding, stage, state, note);
            }, () -> status.setText("Fundstelle manuell im Forschungsregister gespeichert. "
                    + "Das ist keine wissenschaftliche Bestätigung."));
        } catch (IOException unreadable) {
            new AlertDialog.Builder(this).setTitle("Forschungsregister nicht verfügbar")
                    .setMessage(unreadable.getMessage())
                    .setPositiveButton("Schließen", null).show();
        }
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
            Ui.outlineSurface(ResearchActivity.this, card);
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
                    "[HEURISTISCH] · Tippen: Quelle · lange tippen: Register / Optionen", 11, false);
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

public static final class ResearchRegisterActivity extends Activity {
    interface ReviewSaved {
        void save(String stage, String state, String note) throws IOException;
    }

    private final List<ResearchRegister.Record> shown = new ArrayList<>();
    private ResearchRegister register;
    private TextView information;
    private BaseAdapter adapter;
    private String stageFilter = "Alle Stufen";

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        try { register = new ResearchRegister(this); }
        catch (IOException unreadable) {
            new AlertDialog.Builder(this).setTitle("Forschungsregister nicht lesbar")
                    .setMessage(unreadable.getMessage())
                    .setPositiveButton("Schließen", (dialog, which) -> finish())
                    .setCancelable(false).show();
            return;
        }
        LinearLayout root = Ui.column(this, 10);
        setContentView(root);
        Ui.applySystemBarInsets(root);

        LinearLayout top = Ui.row(this);
        Button back = Ui.button(this, "‹ Zurück");
        back.setOnClickListener(view -> finish());
        Button filter = Ui.button(this, "Stufe ▾");
        filter.setOnClickListener(view -> showStageFilter());
        top.addView(back, Ui.weight(1));
        top.addView(filter, Ui.weight(1));
        root.addView(top);
        root.addView(Ui.text(this, "UniverseLab · Forschungsregister", 21, true));
        TextView warning = Ui.text(this,
                "Nur manuell aufgenommene Fundstellen. Statuswerte beschreiben die "
                        + "Bearbeitung, nicht den mathematischen oder empirischen Beweis.",
                12, false);
        warning.setTextColor(Ui.MUTED);
        root.addView(warning);
        information = Ui.text(this, "", 12, false);
        information.setTextColor(Ui.ACCENT);
        root.addView(information);

        ListView list = new WideGripListView(this);
        list.setDivider(null);
        list.setDividerHeight(Ui.dp(this, 7));
        Ui.configurePersistentFastScroll(list);
        adapter = new BaseAdapter() {
            @Override public int getCount() { return shown.size(); }
            @Override public Object getItem(int pos) { return shown.get(pos); }
            @Override public long getItemId(int pos) { return pos; }
            @Override public View getView(int pos, View convertView, ViewGroup parent) {
                ResearchRegister.Record item = shown.get(pos);
                LinearLayout panel = Ui.column(ResearchRegisterActivity.this, 10);
                Ui.outlineSurface(ResearchRegisterActivity.this, panel);
                TextView heading = Ui.text(ResearchRegisterActivity.this,
                        item.chatTitle + "\n" + item.stage + " · " + item.state, 15, true);
                heading.setTextColor(Ui.ACCENT);
                panel.addView(heading);
                panel.addView(Ui.text(ResearchRegisterActivity.this,
                        "Quelle: Chat-ID " + item.chatId.substring(0, Math.min(8, item.chatId.length()))
                                + " · " + item.role + "-Beitrag " + item.messageNumber
                                + "\n" + item.excerpt, 12, false));
                if (!item.note.isEmpty())
                    panel.addView(Ui.text(ResearchRegisterActivity.this, "Notiz: " + item.note, 12, false));
                TextView footer = Ui.text(ResearchRegisterActivity.this,
                        "Manuell aufgenommen · antippen: Originalbeitrag · lange tippen: bearbeiten",
                        11, false);
                footer.setTextColor(Ui.MUTED);
                panel.addView(footer);
                return panel;
            }
        };
        list.setAdapter(adapter);
        list.setOnItemClickListener((parent, view, position, id) -> {
            if (position >= 0 && position < shown.size()) openSource(shown.get(position));
        });
        list.setOnItemLongClickListener((parent, view, position, id) -> {
            if (position < 0 || position >= shown.size()) return false;
            showActions(shown.get(position));
            return true;
        });
        root.addView(list, Ui.fillRemaining());
        refresh();
    }

    @Override protected void onResume() {
        super.onResume();
        if (register != null && adapter != null) refresh();
    }

    private void refresh() {
        List<ResearchRegister.Record> all = register.snapshot();
        shown.clear();
        for (ResearchRegister.Record record : all)
            if ("Alle Stufen".equals(stageFilter) || stageFilter.equals(record.stage))
                shown.add(record);
        adapter.notifyDataSetChanged();
        information.setText(all.size() + " manuell aufgenommene Fundstellen · "
                + shown.size() + " im Filter"
                + (shown.isEmpty() ? "\nNeue Fundstellen im Forschungsnavigator lange antippen." : ""));
    }

    private void showStageFilter() {
        String[] labels = new String[ResearchRegister.STAGES.length + 1];
        labels[0] = "Alle Stufen";
        System.arraycopy(ResearchRegister.STAGES, 0, labels, 1, ResearchRegister.STAGES.length);
        new AlertDialog.Builder(this).setTitle("Forschungsstufe")
                .setItems(labels, (dialog, index) -> {
                    stageFilter = labels[index];
                    refresh();
                }).setNegativeButton("Abbrechen", null).show();
    }

    private void openSource(ResearchRegister.Record item) {
        Intent view = new Intent(this, ConversationActivity.class);
        view.putExtra("chatId", item.chatId);
        view.putExtra("focusMessageIndex", item.messageNumber - 1);
        startActivity(view);
    }

    private void showActions(ResearchRegister.Record item) {
        new AlertDialog.Builder(this)
                .setTitle("Registereintrag verwalten")
                .setItems(new String[]{
                        "Originalbeitrag öffnen", "Forschungsstufe / Status / Notiz bearbeiten",
                        "Eintrag aus Forschungsregister entfernen"
                }, (dialog, index) -> {
                    if (index == 0) openSource(item);
                    else if (index == 1) showEdit(item);
                    else confirmRemove(item);
                }).setNegativeButton("Abbrechen", null).show();
    }

    private void showEdit(ResearchRegister.Record item) {
        promptReview(this, item, (stage, state, note) ->
                register.updateReview(item.id, stage, state, note), this::refresh);
    }

    private void confirmRemove(ResearchRegister.Record item) {
        new AlertDialog.Builder(this).setTitle("Nur Registereintrag entfernen?")
                .setMessage("Der Verweis auf „" + item.chatTitle + "“ wird aus dem "
                        + "Forschungsregister entfernt. Das ursprüngliche Gespräch und "
                        + "alle seine Nachrichten bleiben vollständig erhalten.")
                .setNegativeButton("Abbrechen", null)
                .setPositiveButton("Verweis entfernen", (dialog, index) -> {
                    try { register.remove(item.id); refresh(); }
                    catch (IOException error) { information.setText("Fehler: " + error.getMessage()); }
                }).show();
    }

    /** Shared, explicitly confirmed manual review form for register and research navigator. */
    static void promptReview(Activity context, ResearchRegister.Record existing,
                             ReviewSaved save, Runnable success) {
        LinearLayout body = Ui.column(context, 12);
        TextView explain = Ui.text(context,
                "Bearbeitungsstatus und Quellenzuordnung werden manuell gespeichert. "
                        + "Ein Abschluss ist kein wissenschaftlicher Evidenznachweis.", 12, false);
        body.addView(explain);

        body.addView(Ui.text(context, "Forschungsstufe", 12, true));
        Spinner stage = buildSpinner(context, ResearchRegister.STAGES);
        stage.setSelection(indexOf(ResearchRegister.STAGES,
                existing == null ? "Nicht zugeordnet" : existing.stage));
        body.addView(stage);

        body.addView(Ui.text(context, "Bearbeitungsstatus", 12, true));
        Spinner status = buildSpinner(context, ResearchRegister.STATES);
        status.setSelection(indexOf(ResearchRegister.STATES,
                existing == null ? "Unbewertet" : existing.state));
        body.addView(status);

        body.addView(Ui.text(context, "Prüfnotiz (optional)", 12, true));
        EditText note = new EditText(context);
        note.setText(existing == null ? "" : existing.note);
        note.setHint("Annahme, Gegenprüfung, nächste Evidenzquelle …");
        note.setMinLines(2);
        note.setMaxLines(5);
        note.setSingleLine(false);
        note.setTextColor(Ui.TEXT);
        note.setTextSize(14);
        note.setFilters(new InputFilter[]{new InputFilter.LengthFilter(2000)});
        body.addView(note);

        AlertDialog dialog = new AlertDialog.Builder(context)
                .setTitle(existing == null ? "Fundstelle manuell aufnehmen" : "Eintrag bearbeiten")
                .setView(body)
                .setNegativeButton("Abbrechen", null)
                .setPositiveButton("Speichern", null)
                .create();
        dialog.setOnShowListener(v -> dialog.getButton(AlertDialog.BUTTON_POSITIVE)
                .setOnClickListener(clicked -> {
                    try {
                        save.save(stage.getSelectedItem().toString(),
                                status.getSelectedItem().toString(), note.getText().toString());
                        dialog.dismiss();
                        success.run();
                    } catch (IOException invalid) {
                        note.setError(invalid.getMessage());
                    }
                }));
        dialog.show();
    }

    private static Spinner buildSpinner(Activity context, String[] values) {
        Spinner spinner = new Spinner(context);
        ArrayAdapter<String> options = new ArrayAdapter<>(context,
                android.R.layout.simple_spinner_item, values);
        options.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinner.setAdapter(options);
        return spinner;
    }

    private static int indexOf(String[] values, String target) {
        for (int i = 0; i < values.length; i++) if (values[i].equals(target)) return i;
        return 0;
    }
}


}
