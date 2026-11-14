package de.universelab.chatarchiv;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.os.Bundle;
import android.text.InputFilter;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.BaseAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.Spinner;
import android.widget.TextView;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/** Explicitly curated research records. None represents an automatic scientific confirmation. */
public final class ResearchRegisterActivity extends Activity {
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
                panel.setBackgroundColor(Ui.SURFACE);
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
