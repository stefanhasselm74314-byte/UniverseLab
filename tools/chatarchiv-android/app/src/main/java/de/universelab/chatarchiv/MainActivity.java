package de.universelab.chatarchiv;

import android.app.Activity;
import android.app.AlertDialog;
import android.Manifest;
import android.content.pm.PackageManager;
import android.content.ClipData;
import android.content.Intent;
import android.os.Build;
import android.os.Environment;
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
import android.provider.OpenableColumns;
import android.provider.Settings;
import android.widget.Button;
import android.widget.BaseAdapter;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;

import java.io.IOException;
import java.io.File;
import java.io.OutputStream;
import java.time.LocalDate;
import java.util.ArrayList;
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
    private static final int ASK_LEGACY_STORAGE = 805;
    private static final int SAVE_ARCHIVE = 806;
    private static final int MAX_JSON_CHOICES = 2000;
    private static final String PREFS = "chatarchiv-import";
    private static final String FOLDER_PREF = "read-only-tree-uri";

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
    private boolean scanningAfterSettings;

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
                ? new String[] {"Rettungsordner auswählen (empfohlen)", "Nur JSON-Dateien im Ordner anzeigen", "Einzelne JSON-Dateien (Android-Dialog)", "Ältere Export-ZIPs auswählen", "Gesamten Handyspeicher nach Chat-Exporten durchsuchen"}
                : new String[] {"Gespeicherten Ordner aktualisieren", "Anderen Rettungsordner auswählen", "Nur JSON-Dateien im Ordner anzeigen", "Einzelne JSON-Dateien (Android-Dialog)", "Ältere Export-ZIPs auswählen", "Gesamten Handyspeicher nach Chat-Exporten durchsuchen"};
        new AlertDialog.Builder(this)
                .setTitle("Chats lokal importieren · kein Upload")
                .setItems(options, (dialog, which) -> {
                    if (which == options.length - 1) requestFullStorageScan();
                    else if (saved != null && which == 0) importFolder(Uri.parse(saved));
                    else if ((saved == null && which == 0) || (saved != null && which == 1)) chooseFolder();
                    else if (which == options.length - 2) chooseZip();
                    else if (which == options.length - 4) chooseJsonFolder();
                    else chooseJson();
                }).setNegativeButton("Abbrechen", null).show();
    }

    private void requestFullStorageScan() {
        if (importing) return;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            if (Environment.isExternalStorageManager()) {
                beginFullStorageScan();
                return;
            }
            new AlertDialog.Builder(this)
                    .setTitle("Nur lesender Zugriff auf den gemeinsamen Speicher")
                    .setMessage("Android erfordert die Sonderberechtigung „Zugriff auf alle Dateien“. "
                            + "Die App durchsucht damit lokale Ordner und prüft ZIP-Inhaltsverzeichnisse. "
                            + "Sie öffnet zum Importieren ausschließlich conversations*.json, "
                            + "verändert keine Quelldateien und überträgt keine Chats ins Internet. "
                            + "Geschützte App-Daten bleiben unzugänglich. Du kannst die Berechtigung jederzeit entziehen.")
                    .setNegativeButton("Abbrechen", null)
                    .setPositiveButton("Berechtigung erlauben", (dialog, which) -> {
                        scanningAfterSettings = true;
                        Intent intent = new Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION,
                                Uri.parse("package:" + getPackageName()));
                        try { startActivity(intent); }
                        catch (Exception unavailable) {
                            startActivity(new Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION));
                        }
                    }).show();
            return;
        }
        if (checkSelfPermission(Manifest.permission.READ_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED) {
            beginFullStorageScan();
        } else {
            requestPermissions(new String[] {Manifest.permission.READ_EXTERNAL_STORAGE}, ASK_LEGACY_STORAGE);
        }
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

    @Override protected void onResume() {
        super.onResume();
        if (scanningAfterSettings) {
            scanningAfterSettings = false;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R && Environment.isExternalStorageManager()) {
                handler.post(this::beginFullStorageScan);
            } else if (status != null) {
                status.setText("Keine Speicherberechtigung erteilt. Andere Importarten bleiben verfügbar.");
            }
        }
    }

    @Override public void onRequestPermissionsResult(int requestCode, String[] permissions,
                                                       int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == ASK_LEGACY_STORAGE && grantResults.length > 0
                && grantResults[0] == PackageManager.PERMISSION_GRANTED) beginFullStorageScan();
    }

    private void beginFullStorageScan() {
        if (importing) return;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R && !Environment.isExternalStorageManager()) {
            status.setText("Speicherberechtigung nicht vorhanden.");
            return;
        }
        importing = true;
        cancelStorageScan.set(false);
        cancelScanButton.setVisibility(View.VISIBLE);
        status.setText("Durchsuche gemeinsamen Speicher und ZIP-Verzeichnisse …");
        importWorker.execute(() -> {
            try {
                File root = Environment.getExternalStorageDirectory();
                StorageScanner.Result result = StorageScanner.scan(root, progress -> {
                    int folders = progress.folders;
                    int inspected = progress.inspectedFiles;
                    int matched = progress.matches.size();
                    runOnUiThread(() -> status.setText("Speichersuche: " + folders + " Ordner, "
                            + inspected + " Dateien, " + matched + " Chat-Exporte …"));
                }, cancelStorageScan::get);
                runOnUiThread(() -> {
                    importing = false;
                    cancelScanButton.setVisibility(View.GONE);
                    if (result.cancelled) {
                        status.setText("Speichersuche abgebrochen; keine Dateien importiert.");
                    } else {
                        showScanResults(root, result);
                    }
                });
            } catch (Exception exception) {
                runOnUiThread(() -> {
                    importing = false;
                    cancelScanButton.setVisibility(View.GONE);
                    status.setText("Speichersuche fehlgeschlagen: " + exception.getMessage());
                });
            }
        });
    }

    private void showScanResults(File root, StorageScanner.Result result) {
        if (result.matches.isEmpty()) {
            status.setText("Keine Chat-Exportdateien im zugänglichen Speicher gefunden.");
            new AlertDialog.Builder(this).setTitle("Keine Chat-Exporte gefunden")
                    .setMessage("Geprüft: " + result.folders + " Ordner, " + result.inspectedFiles
                            + " Dateien. Gesucht wurden conversations*.json und ZIPs mit solchen Dateien. "
                            + "Nicht lesbare oder beschädigte ZIP-Dateien können unentdeckt bleiben.")
                    .setPositiveButton("OK", null).show();
            return;
        }
        StringBuilder preview = new StringBuilder("Gefunden: " + result.jsonFiles + " Chat-JSON-Dateien und "
                + result.zipFiles + " ZIPs mit Chat-JSON.\n\nGeprüft: " + result.folders
                + " Ordner, " + result.inspectedFiles + " Dateien.\n\nBeispiele:\n");
        for (int i = 0; i < Math.min(12, result.matches.size()); i++) {
            String path = result.matches.get(i).getAbsolutePath();
            String prefix = root.getAbsolutePath() + File.separator;
            if (path.startsWith(prefix)) path = path.substring(prefix.length());
            preview.append("• ").append(path).append('\n');
        }
        if (result.matches.size() > 12) preview.append("… und ")
                .append(result.matches.size() - 12).append(" weitere.\n");
        preview.append("\nBeim Import werden nur Gesprächs-JSON-Daten gelesen. "
                + "Gleiche Chats werden abgeglichen; abweichende Altversionen bleiben gesichert. "
                + "Bei großen Archiven kann der Import länger dauern.");
        status.setText(result.matches.size() + " Chat-Exportdateien gefunden; Import freigeben.");
        new AlertDialog.Builder(this).setTitle("Gefundene Chat-Exporte prüfen")
                .setMessage(preview.toString())
                .setNegativeButton("Nicht importieren", null)
                .setPositiveButton("Alle Chat-Exporte importieren", (dialog, which) ->
                        startLocalImport(result.matches)).show();
    }

    private void startLocalImport(List<File> matches) {
        if (importing || matches.isEmpty()) return;
        importing = true;
        cancelStorageScan.set(false);
        cancelScanButton.setVisibility(View.VISIBLE);
        status.setText("Import aus " + matches.size() + " geprüften Dateien läuft …");
        importWorker.execute(() -> {
            ChatStore.ImportResult result = store.importLocalFiles(matches, (added, updated, unchanged) ->
                    runOnUiThread(() -> status.setText("Import: " + added + " neu, " + updated
                            + " geändert, " + unchanged + " bereits identisch …")), cancelStorageScan::get);
            runOnUiThread(() -> {
                importing = false;
                cancelScanButton.setVisibility(View.GONE);
                importSummary = result.summary();
                refresh();
            });
        });
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
