package de.universelab.chatarchiv;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.content.ClipData;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.DisplayMetrics;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.inputmethod.InputMethodManager;
import android.content.Context;
import android.database.Cursor;
import android.provider.DocumentsContract;
import android.provider.OpenableColumns;
import android.widget.Button;
import android.widget.BaseAdapter;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.ScrollView;
import android.widget.TextView;

import java.io.IOException;
import java.io.OutputStream;
import java.time.LocalDate;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashSet;
import java.util.Set;
import java.util.TreeSet;
import java.util.List;
import java.util.Locale;
import java.util.TreeMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicBoolean;

public final class MainActivity extends Activity {
    private static final int PICK_JSON = 801;
    private static final int PICK_FOLDER = 802;
    private static final int PICK_ZIP = 803;
    private static final int PICK_JSON_FOLDER = 804;
    private static final int SAVE_ARCHIVE = 806;
    private static final int PICK_SCAN_TREE = 807;
    private static final int MAX_JSON_CHOICES = 2000;
    private static final String PREFS = "chatarchiv-import";
    private static final String FOLDER_PREF = "read-only-tree-uri";
    private static final String SCAN_FOLDERS_PREF = "authorized-scan-tree-uris";

    private ChatStore store;
    private final ExecutorService importWorker = Executors.newSingleThreadExecutor();
    private final ExecutorService searchWorker = Executors.newSingleThreadExecutor();
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final AtomicInteger searchVersion = new AtomicInteger();
    private final AtomicBoolean cancelStorageScan = new AtomicBoolean();
    private final List<ChatStore.Entry> displayed = new ArrayList<>();
    private ChatAdapter adapter;
    private TextView status;
    private TextView counts;
    private TextView firstRunHint;
    private EditText search;
    private Button cancelScanButton;
    private String category = ChatStore.PROJECT;
    private String importSummary = "";
    private boolean importing;

    private static final class ScanFolder {
        final Uri tree;
        final String documentId;
        final String relativePath;
        final int depth;
        final ScanRootStats root;

        ScanFolder(Uri tree, String documentId, String relativePath, int depth, ScanRootStats root) {
            this.tree = tree;
            this.documentId = documentId;
            this.relativePath = relativePath;
            this.depth = depth;
            this.root = root;
        }
    }

    private static final class ScanRootStats {
        final String label;
        int folders;
        int files;
        int json;
        int zips;
        int unreadable;

        ScanRootStats(String label) { this.label = label; }
    }

    private static final class JsonChoice {
        final String name;
        final Uri uri;

        JsonChoice(String name, Uri uri) {
            this.name = name;
            this.uri = uri;
        }
    }

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
        Ui.applySystemBarInsets(root);

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

        android.widget.Button backupButton = Ui.button(this, "Alle Gespräche als ZIP sichern");
        backupButton.setOnClickListener(view -> offerArchiveExport());
        root.addView(backupButton);

        Button researchButton = Ui.button(this, "Forschungsnavigator · offene Fragen");
        researchButton.setOnClickListener(view ->
                startActivity(new Intent(this, ResearchActivity.class)));
        root.addView(researchButton);

        Button handoffButton = Ui.button(this, "Chat-Übergabe · neuen Chat vorbereiten");
        handoffButton.setOnClickListener(view ->
                startActivity(new Intent(this, HandoffActivity.class)));
        root.addView(handoffButton);

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

        cancelScanButton = Ui.button(this, "Speichersuche / Import abbrechen");
        cancelScanButton.setVisibility(View.GONE);
        cancelScanButton.setOnClickListener(view -> {
            cancelStorageScan.set(true);
            status.setText("Abbruch angefordert; bereits importierte Chats bleiben erhalten …");
        });
        root.addView(cancelScanButton);

        firstRunHint = Ui.text(this,
                "NOCH KEINE CHATS IMPORTIERT\n\n" +
                "Deine geretteten Gespräche sind auf dem Handy, nicht in dieser APK.\n\n" +
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

        ListView list = new WideGripListView(this);
        Ui.configurePersistentFastScroll(list);
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
                ? new String[] {"Rettungsordner auswählen (empfohlen)", "Nur JSON-Dateien im Ordner anzeigen", "Einzelne JSON-Dateien (Android-Dialog)", "Ältere Export-ZIPs auswählen", "Gewählten Ordner inkl. Unterordner nach Chat-JSON durchsuchen"}
                : new String[] {"Gespeicherten Ordner aktualisieren", "Anderen Rettungsordner auswählen", "Nur JSON-Dateien im Ordner anzeigen", "Einzelne JSON-Dateien (Android-Dialog)", "Ältere Export-ZIPs auswählen", "Gewählten Ordner inkl. Unterordner nach Chat-JSON durchsuchen"};
        new AlertDialog.Builder(this)
                .setTitle("Chats lokal importieren · kein Upload")
                .setItems(options, (dialog, which) -> {
                    if (which == options.length - 1) chooseScanFolder();
                    else if (saved != null && which == 0) importFolder(Uri.parse(saved));
                    else if ((saved == null && which == 0) || (saved != null && which == 1)) chooseFolder();
                    else if (which == options.length - 2) chooseZip();
                    else if (which == options.length - 4) chooseJsonFolder();
                    else chooseJson();
                }).setNegativeButton("Abbrechen", null).show();
    }

    private void offerArchiveExport() {
        if (importing) return;
        int count = store.snapshot().size();
        if (count == 0) {
            status.setText("Noch keine Chats vorhanden, die gesichert werden können.");
            return;
        }
        new AlertDialog.Builder(this).setTitle("Gesprächsarchiv als ZIP sichern")
                .setMessage("Die Sicherung enthält " + count + " gespeicherte Hauptfassungen "
                        + "als importierbare Chat-JSONs sowie ein Manifest mit den Kategoriezuordnungen. "
                        + "Gesondert gesicherte Altversionen und Medienanhänge sind nicht enthalten. "
                        + "Du wählst das Ziel selbst; ein Cloud-Speicheranbieter würde die Datei gegebenenfalls hochladen.")
                .setNegativeButton("Abbrechen", null)
                .setPositiveButton("Speicherort wählen", (dialog, which) -> {
                    Intent save = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                    save.addCategory(Intent.CATEGORY_OPENABLE);
                    save.setType("application/zip");
                    save.putExtra(Intent.EXTRA_TITLE, "UniverseLab_ChatArchiv_"
                            + LocalDate.now() + ".zip");
                    save.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
                    startActivityForResult(save, SAVE_ARCHIVE);
                }).show();
    }

    private void startArchiveExport(Uri target) {
        if (importing) return;
        importing = true;
        cancelStorageScan.set(false);
        cancelScanButton.setVisibility(View.VISIBLE);
        status.setText("Sicherung aller Chats wird geschrieben …");
        importWorker.execute(() -> {
            try (OutputStream output = getContentResolver().openOutputStream(target, "w")) {
                if (output == null) throw new IOException("Ziel-Datei nicht beschreibbar");
                store.exportAllToZip(output, (done, total) -> runOnUiThread(() ->
                        status.setText("ZIP-Export: " + done + " / " + total + " Gespräche …")),
                        cancelStorageScan::get);
                runOnUiThread(() -> {
                    importing = false;
                    cancelScanButton.setVisibility(View.GONE);
                    importSummary = "Archiv-ZIP erfolgreich erstellt. "
                            + "Alle Hauptfassungen sind für einen späteren Reimport enthalten.";
                    refresh();
                });
            } catch (Exception exception) {
                runOnUiThread(() -> {
                    importing = false;
                    cancelScanButton.setVisibility(View.GONE);
                    status.setText("ZIP-Export nicht abgeschlossen: " + exception.getMessage()
                            + " · Die angelegte Zieldatei kann unvollständig sein.");
                });
            }
        });
    }

    /**
     * Recursively inspect only an Android document tree selected by the user.
     * No global storage permission, raw file path or automatic ZIP extraction.
     */
    private Set<String> savedScanFolders() {
        Set<String> result = new TreeSet<>(getPreferences(MODE_PRIVATE).getStringSet(
                SCAN_FOLDERS_PREF, java.util.Collections.emptySet()));
        // Reuse the existing persisted rescue-folder grant from earlier versions.
        String earlier = getPreferences(MODE_PRIVATE).getString(FOLDER_PREF, null);
        if (earlier != null) result.add(earlier);
        return result;
    }

    private String scanRootLabel(Uri tree) {
        try {
            String documentId = DocumentsContract.getTreeDocumentId(tree);
            String name = null;
            if (!ScanPathLabel.hasLocalPath(documentId)) {
                Uri document = DocumentsContract.buildDocumentUriUsingTree(tree, documentId);
                name = documentName(document);
            }
            return ScanPathLabel.describe(documentId, name, tree.getAuthority());
        } catch (RuntimeException providerError) {
            // An old or revoked grant must not prevent the other roots from being displayed.
            return ScanPathLabel.describe(null, null, tree.getAuthority());
        }
    }

    private void chooseScanFolder() {
        if (importing) return;
        Set<String> saved = savedScanFolders();
        if (saved.isEmpty()) {
            explainScanAndPick();
            return;
        }
        String scanAllLabel = "Alle " + saved.size() + " gespeicherten Ordner erneut durchsuchen";
        if (saved.size() == 1) {
            scanAllLabel += "\n" + scanRootLabel(Uri.parse(saved.iterator().next()));
        }
        new AlertDialog.Builder(this)
                .setTitle("Automatische Suche in freigegebenen Ordnern")
                .setItems(new String[] {
                        scanAllLabel,
                        "Einen weiteren Ordner hinzufügen",
                        "Gespeicherte Ordner einzeln verwalten"
                }, (dialog, which) -> {
                    if (which == 0) {
                        List<Uri> roots = new ArrayList<>();
                        for (String value : saved) roots.add(Uri.parse(value));
                        scanSelectedTrees(roots);
                    } else if (which == 1) {
                        explainScanAndPick();
                    } else {
                        manageScanFolders();
                    }
                }).setNegativeButton("Abbrechen", null).show();
    }

    private void manageScanFolders() {
        if (importing) return;
        List<String> saved = new ArrayList<>(savedScanFolders());
        if (saved.isEmpty()) {
            status.setText("Keine gespeicherten Ordnerfreigaben vorhanden.");
            return;
        }
        String[] labels = new String[saved.size()];
        for (int i = 0; i < saved.size(); i++) {
            labels[i] = (i + 1) + ". " + scanRootLabel(Uri.parse(saved.get(i)));
        }
        new AlertDialog.Builder(this)
                .setTitle("Gespeicherte Ordner verwalten")
                .setItems(labels, (dialog, index) -> manageScanFolder(Uri.parse(saved.get(index))))
                .setNegativeButton("Schließen", null).show();
    }

    private void manageScanFolder(Uri tree) {
        String label = scanRootLabel(tree);
        new AlertDialog.Builder(this)
                .setTitle(label)
                .setItems(new String[] {"Nur diesen Ordner durchsuchen", "Diese Ordnerfreigabe entfernen"},
                        (dialog, which) -> {
                            if (which == 0) scanSelectedTree(tree);
                            else confirmRemoveScanFolder(tree, label);
                        }).setNegativeButton("Zurück", (dialog, ignored) -> manageScanFolders()).show();
    }

    private void confirmRemoveScanFolder(Uri tree, String label) {
        new AlertDialog.Builder(this)
                .setTitle("Diese Ordnerfreigabe entfernen?")
                .setMessage(label + "\n\nNur diese gespeicherte Freigabe wird entfernt. "
                        + "Falls dies der bisherige Rettungsordner ist, wird auch dessen "
                        + "gespeicherte Importfreigabe aufgehoben. Bereits importierte Chats "
                        + "und die Dateien im Ordner bleiben unverändert.")
                .setNegativeButton("Abbrechen", null)
                .setPositiveButton("Freigabe entfernen", (dialog, ignored) -> {
                    String value = tree.toString();
                    android.content.SharedPreferences prefs = getPreferences(MODE_PRIVATE);
                    Set<String> remaining = new TreeSet<>(prefs.getStringSet(
                            SCAN_FOLDERS_PREF, java.util.Collections.emptySet()));
                    remaining.remove(value);
                    android.content.SharedPreferences.Editor edit = prefs.edit();
                    if (remaining.isEmpty()) edit.remove(SCAN_FOLDERS_PREF);
                    else edit.putStringSet(SCAN_FOLDERS_PREF, remaining);
                    if (value.equals(prefs.getString(FOLDER_PREF, null))) edit.remove(FOLDER_PREF);
                    edit.apply();
                    try {
                        getContentResolver().releasePersistableUriPermission(
                                tree, Intent.FLAG_GRANT_READ_URI_PERMISSION);
                    } catch (SecurityException | IllegalArgumentException alreadyRevoked) {
                        // Keep the local list consistent even if Android already revoked it.
                    }
                    status.setText("Freigabe für „" + label + "“ entfernt; private Chats erhalten.");
                }).show();
    }

    private void explainScanAndPick() {
        new AlertDialog.Builder(this)
                .setTitle("Ordnersuche ohne Vollzugriff")
                .setMessage("Du wählst einen Ordner einmal aus. Die App kann ihn und "
                        + "alle Unterordner auch später automatisch durchsuchen. "
                        + "Weitere Ordner kannst du ergänzen. ZIP-Dateien werden bei der "
                        + "Suche gezählt, aber nicht ungefragt geöffnet; ZIP-Import "
                        + "bleibt separat verfügbar. Android erlaubt die Freigabe "
                        + "des Speicher- oder Download-Hauptordners nicht; "
                        + "wähle einen Unterordner.")
                .setNegativeButton("Abbrechen", null)
                .setPositiveButton("Ordner auswählen", (dialog, which) -> {
                    Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
                    intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION
                            | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
                    startActivityForResult(intent, PICK_SCAN_TREE);
                }).show();
    }

    private void scanSelectedTree(Uri tree) {
        scanSelectedTrees(java.util.Collections.singletonList(tree));
    }

    private void scanSelectedTrees(List<Uri> roots) {
        if (importing || roots.isEmpty()) return;
        importing = true;
        cancelStorageScan.set(false);
        cancelScanButton.setVisibility(View.VISIBLE);
        status.setText("Durchsuche freigegebenen Ordner und Unterordner nach Chat-JSON …");
        importWorker.execute(() -> {
            try {
                Deque<ScanFolder> queue = new ArrayDeque<>();
                Set<String> visited = new HashSet<>();
                TreeMap<String, Uri> matches = new TreeMap<>();
                ScanSourceIndex sources = new ScanSourceIndex();
                List<ScanRootStats> rootStats = new ArrayList<>();
                int rootNumber = 0;
                for (Uri tree : roots) {
                    ScanRootStats root = new ScanRootStats(scanRootLabel(tree));
                    rootStats.add(root);
                    queue.add(new ScanFolder(tree, DocumentsContract.getTreeDocumentId(tree),
                            "Ordner " + (++rootNumber) + "/", 0, root));
                }
                int scannedFolders = 0;
                int scannedFiles = 0;
                int zipCandidates = 0;
                int unreadableFolders = 0;
                boolean cancelled = false;
                String[] projection = {
                        DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                        DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                        DocumentsContract.Document.COLUMN_MIME_TYPE,
                        DocumentsContract.Document.COLUMN_SIZE
                };
                while (!queue.isEmpty()) {
                    if (cancelStorageScan.get() || Thread.currentThread().isInterrupted()) {
                        cancelled = true;
                        break;
                    }
                    ScanFolder folder = queue.removeFirst();
                    if (folder.depth > 64 || !visited.add(folder.tree.toString() + "|" + folder.documentId)) continue;
                    folder.root.folders++;
                    if (++scannedFolders > 100_000) {
                        throw new IOException("Mehr als 100.000 Ordner; bitte den Suchbereich verkleinern.");
                    }
                    Uri children = DocumentsContract.buildChildDocumentsUriUsingTree(
                            folder.tree, folder.documentId);
                    try (Cursor cursor = getContentResolver().query(
                            children, projection, null, null, null)) {
                        if (cursor == null) {
                            unreadableFolders++;
                            folder.root.unreadable++;
                            continue;
                        }
                        while (cursor.moveToNext()) {
                            if (cancelStorageScan.get() || Thread.currentThread().isInterrupted()) {
                                cancelled = true;
                                break;
                            }
                            String id = cursor.getString(0);
                            String name = cursor.getString(1);
                            String mime = cursor.getString(2);
                            if (id == null || name == null) continue;
                            if (DocumentsContract.Document.MIME_TYPE_DIR.equals(mime)) {
                                if (folder.depth < 64) {
                                    queue.addLast(new ScanFolder(folder.tree, id, folder.relativePath
                                            + name + "/", folder.depth + 1, folder.root));
                                }
                                continue;
                            }
                            if (++scannedFiles > 500_000) {
                                throw new IOException("Mehr als 500.000 Dateien; bitte kleineren Ordner wählen.");
                            }
                            folder.root.files++;
                            if (StorageScanner.isConversationJson(name)) {
                                String path = folder.relativePath + name;
                                long size = cursor.getColumnCount() > 3 && !cursor.isNull(3)
                                        ? cursor.getLong(3) : -1L;
                                if (sources.register(folder.tree.getAuthority(), id, name, size, path)) {
                                    matches.put(path,
                                            DocumentsContract.buildDocumentUriUsingTree(folder.tree, id));
                                    folder.root.json++;
                                    if (matches.size() > 15_000) {
                                        throw new IOException("Mehr als 15.000 Chat-Dateien; Suche begrenzt.");
                                    }
                                }
                            } else if (name.toLowerCase(Locale.ROOT).endsWith(".zip")) {
                                zipCandidates++;
                                folder.root.zips++;
                            }
                            if (scannedFiles % 250 == 0) {
                                final int countFolders = scannedFolders;
                                final int countFiles = scannedFiles;
                                final int countMatches = matches.size();
                                runOnUiThread(() -> status.setText("Ordnersuche: "
                                        + countFolders + " Ordner, " + countFiles
                                        + " Dateien, " + countMatches + " Chat-JSON …"));
                            }
                        }
                    } catch (SecurityException exception) {
                        unreadableFolders++;
                        folder.root.unreadable++;
                    }
                    if (cancelled) break;
                }
                final int foundFolders = scannedFolders;
                final int foundFiles = scannedFiles;
                final int foundZips = zipCandidates;
                final int unreadable = unreadableFolders;
                final boolean stopped = cancelled;
                runOnUiThread(() -> {
                    importing = false;
                    cancelScanButton.setVisibility(View.GONE);
                    if (stopped) {
                        status.setText("Ordnersuche abgebrochen; keine Datei importiert.");
                    } else {
                        showSelectedTreeResults(matches, foundFolders, foundFiles,
                                foundZips, unreadable, rootStats, sources);
                    }
                });
            } catch (Exception exception) {
                runOnUiThread(() -> {
                    importing = false;
                    cancelScanButton.setVisibility(View.GONE);
                    status.setText("Ordnersuche fehlgeschlagen: " + exception.getMessage());
                });
            }
        });
    }

    private void showSelectedTreeResults(TreeMap<String, Uri> matches, int folders,
                                         int files, int zips, int unreadable,
                                         List<ScanRootStats> roots, ScanSourceIndex sources) {
        StringBuilder details = new StringBuilder("Durchsucht: " + folders
                + " Ordner und " + files + " Dateien.\n"
                + "Chat-JSON gefunden: " + matches.size()
                + "\nZIP-Dateien gesehen: " + zips
                + " (Inhalt nicht geprüft; ZIPs bitte separat auswählen).\n"
                + "Nicht lesbare Ordner: " + unreadable + ".\n\n");
        details.append("Suchbereiche:\n");
        for (int i = 0; i < roots.size() && i < 8; i++) {
            ScanRootStats root = roots.get(i);
            details.append("• ").append(i + 1).append(": ").append(root.label)
                    .append("\n  ").append(root.folders).append(" Ordner, ")
                    .append(root.files).append(" Dateien, ").append(root.json)
                    .append(" Chat-JSON, ").append(root.unreadable)
                    .append(" nicht lesbar\n");
        }
        if (roots.size() > 8) details.append("… und ").append(roots.size() - 8)
                .append(" weitere Suchbereiche\n");
        if (sources.repeatedReferences() > 0) details.append("Mehrfachreferenzen auf dieselbe Datei: ")
                .append(sources.repeatedReferences()).append(" (nur einmal zum Import vorgemerkt).\n");
        if (sources.possibleCopyGroups() > 0) {
            details.append("Mögliche Dateikopien mit gleichem Namen und gleicher Größe: ")
                    .append(sources.possibleCopyGroups())
                    .append(" Gruppen (Inhalt nicht verglichen; keine automatische Auslassung).\n");
            for (String example : sources.possibleCopyExamples(2))
                details.append("  • ").append(example).append('\n');
        }
        details.append("\nGefundene Pfade (bis zu 12):\n");
        int shown = 0;
        for (String path : matches.keySet()) {
            if (shown++ >= 12) break;
            details.append("• ").append(path).append('\n');
        }
        if (matches.size() > 12) details.append("… und ")
                .append(matches.size() - 12).append(" weitere.\n");
        details.append("\nDie ausgewählten JSON-Dateien werden nur lokal eingelesen. "
                + "Vorhandene Chats werden abgeglichen; die Originaldateien bleiben unverändert.");
        if (matches.isEmpty()) {
            status.setText("Keine Chat-JSON-Dateien im freigegebenen Ordner gefunden.");
            showScanReportDialog("Ordnersuche abgeschlossen", details, null);
            return;
        }
        status.setText(matches.size() + " Chat-JSON-Dateien gefunden; bitte Import bestätigen.");
        showScanReportDialog("Gefundene Chat-JSON prüfen", details,
                () -> startImport(new ArrayList<>(matches.values())));
    }

    private void showScanReportDialog(String title, CharSequence details, Runnable onImport) {
        // The Android 17 platform AlertDialog stacks its action buttons on this
        // device even after bounding the window. The lower button then clips.
        // Use a fixed horizontal action row; only the report itself may scroll.
        Dialog dialog = new Dialog(this);
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);

        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(Ui.dp(this, 16), Ui.dp(this, 12),
                Ui.dp(this, 16), Ui.dp(this, 8));
        GradientDrawable background = new GradientDrawable();
        background.setColor(Color.rgb(66, 66, 66));
        background.setCornerRadius(Ui.dp(this, 5));
        panel.setBackground(background);

        TextView heading = new TextView(this);
        heading.setText(title);
        heading.setTextSize(TypedValue.COMPLEX_UNIT_SP, 20);
        heading.setTextColor(Color.WHITE);
        heading.setPadding(Ui.dp(this, 6), Ui.dp(this, 8),
                Ui.dp(this, 6), Ui.dp(this, 12));
        panel.addView(heading, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        ScrollView report = new ScrollView(this);
        report.setFillViewport(false);
        report.setVerticalScrollBarEnabled(true);
        TextView body = new TextView(this);
        body.setText(details);
        body.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16);
        body.setTextColor(Color.WHITE);
        body.setPadding(Ui.dp(this, 6), Ui.dp(this, 8),
                Ui.dp(this, 6), Ui.dp(this, 12));
        report.addView(body, new ScrollView.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        panel.addView(report, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));

        View separator = new View(this);
        separator.setBackgroundColor(Color.rgb(92, 92, 92));
        panel.addView(separator, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, Ui.dp(this, 1)));

        LinearLayout actions = new LinearLayout(this);
        actions.setOrientation(LinearLayout.HORIZONTAL);
        actions.setGravity(Gravity.CENTER_VERTICAL);
        if (onImport == null) {
            actions.addView(scanDialogButton("Schließen", dialog, null),
                    new LinearLayout.LayoutParams(0, Ui.dp(this, 52), 1f));
        } else {
            actions.addView(scanDialogButton("Nicht importieren", dialog, null),
                    new LinearLayout.LayoutParams(0, Ui.dp(this, 52), 1f));
            actions.addView(scanDialogButton("Alle importieren", dialog, onImport),
                    new LinearLayout.LayoutParams(0, Ui.dp(this, 52), 1f));
        }
        panel.addView(actions, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        dialog.setContentView(panel, new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        dialog.show();
        Window window = dialog.getWindow();
        if (window != null) {
            DisplayMetrics display = getResources().getDisplayMetrics();
            int maxHeight = Math.min((int) (display.heightPixels * 0.76f),
                    Ui.dp(this, 680));
            int width = Math.min(display.widthPixels - Ui.dp(this, 28),
                    Ui.dp(this, 470));
            window.setBackgroundDrawableResource(android.R.color.transparent);
            window.setLayout(width, maxHeight);
            window.setGravity(Gravity.CENTER);
        }
    }

    private Button scanDialogButton(String label, Dialog dialog, Runnable action) {
        Button button = new Button(this);
        button.setText(label);
        button.setAllCaps(false);
        button.setSingleLine(true);
        button.setTextSize(TypedValue.COMPLEX_UNIT_SP, 12);
        button.setAutoSizeTextTypeUniformWithConfiguration(10, 12, 1,
                TypedValue.COMPLEX_UNIT_SP);
        button.setTextColor(Color.rgb(132, 201, 255));
        button.setPadding(Ui.dp(this, 2), 0, Ui.dp(this, 2), 0);
        button.setMinimumWidth(0);
        button.setBackgroundColor(Color.TRANSPARENT);
        button.setOnClickListener(view -> {
            dialog.dismiss();
            if (action != null) action.run();
        });
        return button;
    }

    private void chooseFolder() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        startActivityForResult(intent, PICK_FOLDER);
    }

    private void chooseJsonFolder() {
        if (importing) return;
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        startActivityForResult(intent, PICK_JSON_FOLDER);
    }

    private void chooseJson() {
        if (importing) return;
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        // Android's system picker filters by MIME type, not by filename.
        // Never request */* here: it exposes every video/image in Downloads.
        intent.setType("application/json");
        intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        startActivityForResult(intent, PICK_JSON);
    }

    private void chooseZip() {
        if (importing) return;
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("application/zip");
        intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        startActivityForResult(intent, PICK_ZIP);
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode != RESULT_OK || data == null) return;
        if (requestCode == SAVE_ARCHIVE) {
            if (data.getData() != null) startArchiveExport(data.getData());
            return;
        }
        if (requestCode == PICK_SCAN_TREE) {
            Uri tree = data.getData();
            if (tree == null) return;
            try {
                getContentResolver().takePersistableUriPermission(
                        tree, Intent.FLAG_GRANT_READ_URI_PERMISSION);
                Set<String> saved = savedScanFolders();
                saved.add(tree.toString());
                getPreferences(MODE_PRIVATE).edit()
                        .putStringSet(SCAN_FOLDERS_PREF, saved).apply();
                List<Uri> roots = new ArrayList<>();
                for (String value : saved) roots.add(Uri.parse(value));
                scanSelectedTrees(roots);
            } catch (SecurityException notPersisted) {
                status.setText("Ordnerfreigabe nur für diese Sitzung verfügbar.");
                scanSelectedTree(tree);
            }
            return;
        }
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
        if (requestCode == PICK_JSON_FOLDER) {
            Uri tree = data.getData();
            if (tree != null) showJsonChoices(tree);
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
        // The picker is provided by Android/other document providers. Some
        // providers incorrectly report file MIME types, so verify the names
        // again before any file is opened or imported.
        String extension = requestCode == PICK_JSON ? ".json" : ".zip";
        for (Uri file : files) {
            String name = documentName(file);
            if (name == null || !name.toLowerCase(Locale.ROOT).endsWith(extension)) {
                new AlertDialog.Builder(this)
                        .setTitle("Falscher Dateityp")
                        .setMessage("Für diesen Import sind nur " + extension + "-Dateien erlaubt. "
                                + "Nicht akzeptiert: " + (name == null ? "unbekannter Dateiname" : name))
                        .setPositiveButton("OK", null).show();
                return;
            }
        }
        startImport(files);
    }

    private String documentName(Uri file) {
        try (Cursor cursor = getContentResolver().query(file,
                new String[] {OpenableColumns.DISPLAY_NAME}, null, null, null)) {
            if (cursor != null && cursor.moveToFirst()) return cursor.getString(0);
        } catch (Exception ignored) {
            // Reject the file if the provider cannot supply a filename.
        }
        return null;
    }

    private void showJsonChoices(Uri tree) {
        if (importing) return;
        status.setText("Suche ausschließlich .json-Dateien im gewählten Ordner …");
        importWorker.execute(() -> {
            try {
                List<JsonChoice> matches = new ArrayList<>();
                String treeId = DocumentsContract.getTreeDocumentId(tree);
                Uri children = DocumentsContract.buildChildDocumentsUriUsingTree(tree, treeId);
                String[] projection = {
                        DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                        DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                        DocumentsContract.Document.COLUMN_MIME_TYPE
                };
                try (Cursor cursor = getContentResolver().query(children, projection, null, null, null)) {
                    if (cursor == null) throw new IOException("Ordner kann nicht aufgelistet werden");
                    while (cursor.moveToNext()) {
                        String name = cursor.getString(1);
                        if (name == null || !name.toLowerCase(Locale.ROOT).endsWith(".json")
                                || DocumentsContract.Document.MIME_TYPE_DIR.equals(cursor.getString(2))) continue;
                        if (matches.size() >= MAX_JSON_CHOICES) {
                            throw new IOException("Mehr als " + MAX_JSON_CHOICES + " JSON-Dateien. Bitte einen kleineren Ordner wählen.");
                        }
                        Uri file = DocumentsContract.buildDocumentUriUsingTree(tree, cursor.getString(0));
                        matches.add(new JsonChoice(name, file));
                    }
                }
                matches.sort((a, b) -> a.name.compareToIgnoreCase(b.name));
                runOnUiThread(() -> presentJsonChoices(matches));
            } catch (Exception exception) {
                runOnUiThread(() -> new AlertDialog.Builder(this)
                        .setTitle("Ordner nicht lesbar")
                        .setMessage(exception.getMessage())
                        .setPositiveButton("Anderen Ordner auswählen", (dialog, which) -> chooseJsonFolder())
                        .setNegativeButton("Schließen", null).show());
            }
        });
    }

    private void presentJsonChoices(List<JsonChoice> choices) {
        if (choices.isEmpty()) {
            status.setText("In diesem Ordner wurden keine .json-Dateien gefunden.");
            new AlertDialog.Builder(this)
                    .setTitle("Keine JSON-Dateien")
                    .setMessage("Bitte den Ordner wählen, der die Gesprächsdateien direkt enthält. "
                            + "Android lässt den Download-Hauptordner möglicherweise nicht auswählen; "
                            + "verwende bei Bedarf einen Unterordner in Downloads.")
                    .setPositiveButton("Ordner erneut wählen", (dialog, which) -> chooseJsonFolder())
                    .setNegativeButton("Schließen", null).show();
            return;
        }

        String[] names = new String[choices.size()];
        boolean[] selected = new boolean[choices.size()];
        for (int i = 0; i < choices.size(); i++) names[i] = choices.get(i).name;
        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle("Nur JSON · " + choices.size() + " Datei(en)")
                .setMultiChoiceItems(names, selected, (whichDialog, index, checked) -> {
                    selected[index] = checked;
                    boolean any = false;
                    for (boolean value : selected) if (value) { any = true; break; }
                    ((AlertDialog) whichDialog).getButton(AlertDialog.BUTTON_POSITIVE).setEnabled(any);
                })
                .setNegativeButton("Abbrechen", null)
                .setPositiveButton("Ausgewählte importieren", (whichDialog, which) -> {
                    List<Uri> files = new ArrayList<>();
                    for (int i = 0; i < selected.length; i++) {
                        if (selected[i]) files.add(choices.get(i).uri);
                    }
                    startImport(files);
                }).create();
        dialog.setOnShowListener(ignored -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setEnabled(false));
        status.setText("Nur JSON-Dateien · bitte Dateien auswählen");
        dialog.show();
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
        cancelStorageScan.set(true);
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
