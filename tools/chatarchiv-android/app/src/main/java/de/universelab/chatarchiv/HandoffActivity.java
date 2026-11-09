package de.universelab.chatarchiv;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.View;
import android.view.Window;
import android.util.DisplayMetrics;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Create a bounded source-backed handoff in local memory. No network access, app-archive
 * mutation, unattended sharing, canon promotion, or automatic ChatGPT injection.
 */
public final class HandoffActivity extends Activity {
    private static final int SAVE_HANDOFF = 824;
    private static final String DEFAULT_FOCUS = "6D-Hyperzeit · HPVS → HZT-M0 → HZT-Full";
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private final AtomicBoolean cancelled = new AtomicBoolean();
    private final List<ResearchFinder.Finding> findings = new ArrayList<>();
    private final Map<ResearchFinder.Finding, ResearchTimeline.Review> reviews =
            new IdentityHashMap<>();

    private EditText focus;
    private TextView status;
    private TextView preview;
    private TextView position;
    private ScrollView scroll;
    private SeekBar seek;
    private Button scanButton;
    private Button cancelButton;
    private Button copyButton;
    private Button saveButton;
    private Button scopeButton;
    private Button chooseButton;
    private HandoffQuality.Scope currentScope = HandoffQuality.Scope.PHYSICS;
    private final List<ResearchFinder.Finding> approved = new ArrayList<>();
    private boolean selectionApproved;

    private boolean scanning;
    private boolean ready;
    private int inspectedChats;
    private int unreadableChats;
    private String snapshotTime = "";
    private String handoffText = "";
    private String pendingSave;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout root = Ui.column(this, 12);
        setContentView(root);
        Ui.applySystemBarInsets(root);

        Button back = Ui.button(this, "‹ Zurück zum ChatArchiv");
        back.setOnClickListener(view -> finish());
        root.addView(back);
        root.addView(Ui.text(this, "UniverseLab · Chat-Übergabe", 21, true));

        TextView note = Ui.text(this,
                "Bereitet eine kopierbare Fortsetzung für einen NEUEN Chat vor. "
                        + "Alle Fundstellen sind heuristisch und nicht mit dem aktuellen "
                        + "Projektkanon abgeglichen. Keine Chats werden hochgeladen.", 12, false);
        note.setTextColor(Ui.MUTED);
        root.addView(note);

        focus = new EditText(this);
        focus.setHint("Thema für die nächste Sitzung");
        focus.setTextColor(Ui.TEXT);
        focus.setHintTextColor(Ui.MUTED);
        focus.setTextSize(14);
        focus.setSingleLine(false);
        focus.setMaxLines(2);
        focus.setBackgroundTintList(
                android.content.res.ColorStateList.valueOf(Ui.ACCENT));
        focus.setText(state == null ? DEFAULT_FOCUS : state.getString("focus", DEFAULT_FOCUS));
        root.addView(focus);

        if (state != null) {
            int saved = state.getInt("scope", 0);
            HandoffQuality.Scope[] values = HandoffQuality.Scope.values();
            if (saved >= 0 && saved < values.length) currentScope = values[saved];
        }
        LinearLayout optionsRow = Ui.row(this);
        scopeButton = Ui.button(this, "Bereich: " + currentScope.label);
        chooseButton = Ui.button(this, "Fundstellen auswählen");
        chooseButton.setEnabled(false);
        optionsRow.addView(scopeButton, Ui.weight(1.1f));
        optionsRow.addView(chooseButton, Ui.weight(1.2f));
        root.addView(optionsRow);
        scopeButton.setOnClickListener(view -> selectScope());
        chooseButton.setOnClickListener(view -> selectFindings());

        LinearLayout scanRow = Ui.row(this);
        scanButton = Ui.button(this, "Übergabe neu sammeln");
        cancelButton = Ui.button(this, "Abbrechen");
        cancelButton.setVisibility(View.GONE);
        scanRow.addView(scanButton, Ui.weight(1.5f));
        scanRow.addView(cancelButton, Ui.weight(1));
        root.addView(scanRow);
        scanButton.setOnClickListener(view -> scanProjectChats());
        cancelButton.setOnClickListener(view -> {
            cancelled.set(true);
            status.setText("Abbruch angefordert · noch kein Übergabepaket.");
        });

        LinearLayout outputRow = Ui.row(this);
        copyButton = Ui.button(this, "Für neuen Chat kopieren");
        saveButton = Ui.button(this, "Als .md speichern");
        copyButton.setEnabled(false);
        saveButton.setEnabled(false);
        outputRow.addView(copyButton, Ui.weight(1.2f));
        outputRow.addView(saveButton, Ui.weight(1));
        root.addView(outputRow);
        copyButton.setOnClickListener(view -> copyToClipboard());
        saveButton.setOnClickListener(view -> requestSave());

        status = Ui.text(this, "Prüfung des lokalen UniverseLab-Archivs startet …", 12, false);
        status.setTextColor(Ui.ACCENT);
        root.addView(status);

        scroll = new ScrollView(this);
        scroll.setVerticalScrollBarEnabled(true);
        scroll.setScrollbarFadingEnabled(false);
        scroll.setScrollBarStyle(View.SCROLLBARS_INSIDE_INSET);
        scroll.setPadding(0, 0, Ui.dp(this, 9), 0);
        preview = Ui.text(this, "Noch keine Übergabe erzeugt.", 13, false);
        preview.setTextIsSelectable(true);
        preview.setLineSpacing(Ui.dp(this, 2), 1.08f);
        scroll.addView(preview, new ScrollView.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        root.addView(scroll, Ui.fillRemaining());

        position = Ui.text(this, "Vorschauposition · 0 %", 11, false);
        position.setTextColor(Ui.ACCENT);
        root.addView(position);
        seek = new SeekBar(this);
        seek.setMax(ScrollPosition.MAX_PROGRESS);
        seek.setEnabled(false);
        root.addView(seek);
        seek.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar bar, int progress, boolean user) {
                if (!user) return;
                scroll.scrollTo(0, ScrollPosition.offsetFor(
                        progress, preview.getHeight(), scroll.getHeight()));
                position.setText("Vorschauposition · " + Math.round(progress / 10f) + " %");
            }
            @Override public void onStartTrackingTouch(SeekBar bar) { }
            @Override public void onStopTrackingTouch(SeekBar bar) { }
        });
        scroll.setOnScrollChangeListener((view, x, y, oldX, oldY) -> {
            int percent = ScrollPosition.progressFor(
                    y, preview.getHeight(), scroll.getHeight());
            seek.setProgress(percent);
            position.setText("Vorschauposition · " + Math.round(percent / 10f) + " %");
        });

        focus.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) { }
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) {
                if (ready && !scanning) {
                    revokeSelection();
                    regeneratePreview();
                }
            }
            @Override public void afterTextChanged(Editable value) { }
        });

        if (state != null) pendingSave = state.getString("pending-save");
        scanProjectChats();
    }

    private void scanProjectChats() {
        if (scanning || worker.isShutdown()) return;
        scanning = true;
        ready = false;
        cancelled.set(false);
        handoffText = "";
        revokeSelection();
        chooseButton.setEnabled(false);
        copyButton.setEnabled(false);
        saveButton.setEnabled(false);
        scanButton.setEnabled(false);
        cancelButton.setVisibility(View.VISIBLE);
        preview.setText("Lese markierte Prüfpunkte aus den gespeicherten UniverseLab-Chats …");
        status.setText("Lokaler Quellabgleich läuft …");

        worker.execute(() -> {
            List<ResearchFinder.Finding> next = new ArrayList<>();
            List<ResearchTimeline.StatusEvidence> chronology = new ArrayList<>();
            int scanned = 0;
            int errors = 0;
            try {
                ChatStore store = new ChatStore(this);
                for (ChatStore.Entry entry : store.snapshot()) {
                    if (cancelled.get() || Thread.currentThread().isInterrupted()) break;
                    if (!ChatStore.PROJECT.equals(entry.category)) continue;
                    scanned++;
                    try {
                        JSONObject conversation = store.loadConversation(entry.id);
                        List<ConversationLogic.Message> visible =
                                ConversationLogic.visibleMessages(conversation);
                        List<ResearchFinder.Finding> raw = ResearchFinder.extract(
                                entry.id, entry.title, visible, 40);
                        next.addAll(HandoffQuality.screen(
                                raw, visible, HandoffQuality.Scope.ALL, 8));
                        chronology.addAll(ResearchTimeline.collect(
                                entry.id, entry.title, visible));
                    } catch (Exception unavailable) {
                        errors++;
                    }
                    if (scanned % 10 == 0) {
                        int done = scanned;
                        runOnUiThread(() -> {
                            if (!isFinishing() && !isDestroyed() && scanning)
                                status.setText(done + " Projektchats lokal geprüft …");
                        });
                    }
                }
            } catch (IOException failure) {
                errors++;
            }

            boolean interrupted = cancelled.get() || Thread.currentThread().isInterrupted();
            Map<ResearchFinder.Finding, ResearchTimeline.Review> matching = interrupted
                    ? new IdentityHashMap<>() : ResearchTimeline.reconcile(next, chronology);
            int checked = scanned;
            int failed = errors;
            runOnUiThread(() -> {
                if (isFinishing() || isDestroyed()) return;
                scanning = false;
                scanButton.setEnabled(true);
                cancelButton.setVisibility(View.GONE);
                if (interrupted) {
                    status.setText("Abgebrochen · keine unvollständige Übergabe freigegeben.");
                    preview.setText("Erneut sammeln startet eine vollständige neue Prüfung.");
                    return;
                }
                inspectedChats = checked;
                unreadableChats = failed;
                findings.clear();
                findings.addAll(HandoffQuality.deduplicate(next));
                reviews.clear();
                reviews.putAll(matching);
                snapshotTime = DateTimeFormatter.ofPattern(
                        "dd.MM.yyyy HH:mm z", Locale.GERMAN).format(ZonedDateTime.now());
                ready = true;
                chooseButton.setEnabled(!findings.isEmpty());
                regeneratePreview();
            });
        });
    }

    private void regeneratePreview() {
        if (!ready || scanning) return;
        String subject = focus.getText().toString().trim();
        if (subject.isEmpty()) subject = "UniverseLab · Thema noch festlegen";
        List<ResearchFinder.Finding> visible = scopedFindings();
        HandoffBuilder.Packet packet = HandoffBuilder.buildSelected(
                subject, snapshotTime, inspectedChats, unreadableChats,
                visible, reviews, selectionApproved ? approved : null, currentScope.label);
        handoffText = packet.markdown;
        preview.setText(handoffText);
        scroll.scrollTo(0, 0);
        seek.setProgress(0);
        preview.post(() -> {
            if (!isFinishing() && !isDestroyed())
                seek.setEnabled(preview.getHeight() > scroll.getHeight());
        });
        copyButton.setEnabled(selectionApproved);
        saveButton.setEnabled(selectionApproved);
        status.setText((selectionApproved ? "Auswahl bestätigt" : "Vorschau · Auswahl erforderlich")
                + " · " + inspectedChats + " Projektchats · "
                + packet.totalCandidates + " passende Hinweise · "
                + packet.includedWork + " Prüfkandidaten · "
                + packet.includedStatus + " spätere Abschlussaussagen zur Kontrolle"
                + (unreadableChats > 0 ? " · " + unreadableChats + " nicht lesbar" : "")
                + ". Nur manuelles Kopieren/Speichern überträgt Text.");
    }

    private List<ResearchFinder.Finding> scopedFindings() {
        List<ResearchFinder.Finding> scoped = new ArrayList<>();
        for (ResearchFinder.Finding f : findings) {
            if (currentScope == HandoffQuality.Scope.ALL
                    || HandoffQuality.classify(f) == currentScope) scoped.add(f);
        }
        return scoped;
    }

    private void revokeSelection() {
        selectionApproved = false;
        approved.clear();
        if (copyButton != null) copyButton.setEnabled(false);
        if (saveButton != null) saveButton.setEnabled(false);
    }

    private void selectScope() {
        HandoffQuality.Scope[] options = HandoffQuality.Scope.values();
        String[] labels = new String[options.length];
        for (int n = 0; n < options.length; n++) labels[n] = options[n].label;
        new AlertDialog.Builder(this)
                .setTitle("Arbeitsbereich für die Übergabe")
                .setSingleChoiceItems(labels, currentScope.ordinal(), (dialog, which) -> {
                    currentScope = options[which];
                    scopeButton.setText("Bereich: " + currentScope.label);
                    revokeSelection();
                    if (ready) regeneratePreview();
                    dialog.dismiss();
                })
                .setNegativeButton("Abbrechen", null)
                .show();
    }

    /** A deliberate user decision before text leaves the app via clipboard or SAF. */
    private void selectFindings() {
        if (!ready || scanning) return;
        String subject = focus.getText().toString().trim();
        List<ResearchFinder.Finding> choices = HandoffBuilder.selectWorkBalanced(
                scopedFindings(), 36, subject);
        if (choices.isEmpty()) {
            new AlertDialog.Builder(this).setTitle("Keine Kandidaten")
                    .setMessage("In diesem Bereich wurden keine passenden Prüfkandidaten "
                            + "gefunden. Das ist kein Beweis, dass alle Aufgaben erledigt sind.")
                    .setPositiveButton("OK", null).show();
            return;
        }
        List<ResearchFinder.Finding> proposed = HandoffBuilder.selectWorkBalanced(
                choices, HandoffBuilder.ACTIVE_LIMIT, subject);
        boolean[] checked = new boolean[choices.size()];
        String[] labels = new String[choices.size()];
        for (int n = 0; n < choices.size(); n++) {
            ResearchFinder.Finding f = choices.get(n);
            checked[n] = selectionApproved ? approved.contains(f) : proposed.contains(f);
            labels[n] = f.kind + " · " + HandoffBuilder.clean(f.chatTitle, 36)
                    + "\n" + HandoffBuilder.clean(f.excerpt, 90);
        }
        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle("Fundstellen auswählen · max. 12")
                .setMultiChoiceItems(labels, checked, (panel, which, enabled) -> {
                    checked[which] = enabled;
                    int count = 0;
                    for (boolean value : checked) if (value) count++;
                    if (count > HandoffBuilder.ACTIVE_LIMIT) {
                        checked[which] = false;
                        ((AlertDialog) panel).getListView().setItemChecked(which, false);
                        Toast.makeText(this, "Höchstens 12 Fundstellen", Toast.LENGTH_SHORT).show();
                    }
                })
                .setPositiveButton("Übernehmen", (panel, ignored) -> {
                    approved.clear();
                    for (int n = 0; n < choices.size(); n++)
                        if (checked[n]) approved.add(choices.get(n));
                    selectionApproved = true;
                    regeneratePreview();
                })
                .setNegativeButton("Abbrechen", null)
                .create();
        dialog.show();
        // On narrow Android 17 screens an unconstrained multi-choice AlertDialog
        // can extend into the gesture/navigation area. Keep both action buttons
        // within a centred, bounded window while the candidate list scrolls.
        Window window = dialog.getWindow();
        if (window != null) {
            DisplayMetrics display = getResources().getDisplayMetrics();
            int maxHeight = Math.min((int) (display.heightPixels * 0.76f),
                    Ui.dp(this, 680));
            int width = Math.min(display.widthPixels - Ui.dp(this, 28),
                    Ui.dp(this, 470));
            window.setLayout(width, maxHeight);
            window.setGravity(Gravity.CENTER);
        }
    }

    private void copyToClipboard() {
        if (!ready || !selectionApproved || handoffText.isEmpty()) return;
        ClipboardManager manager = (ClipboardManager) getSystemService(
                Context.CLIPBOARD_SERVICE);
        if (manager == null) {
            Toast.makeText(this, "Zwischenablage nicht verfügbar", Toast.LENGTH_LONG).show();
            return;
        }
        manager.setPrimaryClip(ClipData.newPlainText(
                "UniverseLab Chat-Übergabe (heuristisch)", handoffText));
        Toast.makeText(this,
                "Übergabepaket kopiert · in einen neuen Chat einfügen",
                Toast.LENGTH_LONG).show();
    }

    private void requestSave() {
        if (!ready || !selectionApproved || handoffText.isEmpty()) return;
        pendingSave = handoffText;
        Intent save = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        save.addCategory(Intent.CATEGORY_OPENABLE);
        save.setType("text/plain");
        save.putExtra(Intent.EXTRA_TITLE, "UniverseLab_ChatUebergabe_v0.1.md");
        save.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
        startActivityForResult(save, SAVE_HANDOFF);
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != SAVE_HANDOFF) return;
        String selectedText = pendingSave;
        pendingSave = null;
        if (resultCode != RESULT_OK || data == null || data.getData() == null
                || selectedText == null) return;
        Uri destination = data.getData();
        saveButton.setEnabled(false);
        worker.execute(() -> {
            try (OutputStream output = getContentResolver().openOutputStream(destination, "w")) {
                if (output == null) throw new IOException("Speicherziel nicht beschreibbar");
                output.write(selectedText.getBytes(StandardCharsets.UTF_8));
                output.flush();
                runOnUiThread(() -> {
                    if (isFinishing() || isDestroyed()) return;
                    saveButton.setEnabled(ready && selectionApproved);
                    Toast.makeText(this, "Übergabe als Markdown gespeichert",
                            Toast.LENGTH_LONG).show();
                });
            } catch (Exception failure) {
                runOnUiThread(() -> {
                    if (isFinishing() || isDestroyed()) return;
                    saveButton.setEnabled(ready && selectionApproved);
                    status.setText("Speichern fehlgeschlagen: " + failure.getMessage());
                });
            }
        });
    }

    @Override protected void onSaveInstanceState(Bundle outState) {
        outState.putString("focus", focus.getText().toString());
        outState.putInt("scope", currentScope.ordinal());
        if (pendingSave != null) outState.putString("pending-save", pendingSave);
        super.onSaveInstanceState(outState);
    }

    @Override protected void onDestroy() {
        cancelled.set(true);
        worker.shutdownNow();
        super.onDestroy();
    }
}
