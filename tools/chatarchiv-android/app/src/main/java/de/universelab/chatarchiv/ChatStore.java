package de.universelab.chatarchiv;

import android.content.Context;
import android.net.Uri;
import android.util.JsonReader;
import android.util.JsonToken;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.File;
import java.io.FilterInputStream;
import java.io.FileInputStream;
import java.io.ByteArrayOutputStream;
import java.util.LinkedHashSet;
import java.util.Arrays;
import java.util.HashMap;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Enumeration;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.zip.ZipOutputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipInputStream;

/** Private, offline storage. This class never performs network operations. */
final class ChatStore {
    static final String PROJECT = "projekt";
    static final String OTHER = "andere";
    static final String TRASH = "papierkorb";
    private static final String PURGE_PENDING = "loeschung-ausstehend";
    private static final long MAX_ZIP_JSON_BYTES = 3L * 1024 * 1024 * 1024;
    private static final int MAX_ZIP_JSON_ENTRIES = 100;
    private static final long MAX_MANIFEST_BYTES = 2L * 1024 * 1024;
    private static final long MAX_SAVED_VERSIONS_BYTES = 1024L * 1024 * 1024;
    private static final long MAX_ARCHIVED_PREVIEW_BYTES = 32L * 1024 * 1024;
    private static final DateTimeFormatter DATE = DateTimeFormatter.ofPattern("dd.MM.yyyy", Locale.GERMAN);

    static final class Entry {
        final String id;
        final String title;
        final String originalTitle;
        final boolean customTitle;
        final String file;
        final long created;
        final String category;
        final String digest;
        final String originCategory;
        final long trashedAt;

        Entry(String id, String title, String file, long created, String category, String digest) {
            this(id, title, file, created, category, digest, "", 0, title, false);
        }

        Entry(String id, String title, String file, long created, String category, String digest,
              String originCategory, long trashedAt) {
            this(id, title, file, created, category, digest, originCategory, trashedAt, title, false);
        }

        Entry(String id, String title, String file, long created, String category, String digest,
              String originCategory, long trashedAt, String originalTitle, boolean customTitle) {
            this.id = id;
            this.title = title;
            this.originalTitle = originalTitle;
            this.customTitle = customTitle;
            this.file = file;
            this.created = created;
            this.category = category;
            this.digest = digest;
            this.originCategory = originCategory;
            this.trashedAt = trashedAt;
        }

        boolean inTrash() {
            return TRASH.equals(category) || PURGE_PENDING.equals(category);
        }

        Entry withCategory(String target) {
            return new Entry(id, title, file, created, target, digest,
                    originCategory, trashedAt, originalTitle, customTitle);
        }

        Entry withLocalTitle(String requested) {
            boolean changed = !originalTitle.equals(requested);
            return new Entry(id, changed ? requested : originalTitle, file, created, category, digest,
                    originCategory, trashedAt, originalTitle, changed);
        }

        Entry withImportedTitle(String imported, long time, String newDigest) {
            return new Entry(id, customTitle ? title : imported, file, time, category, newDigest,
                    originCategory, trashedAt, imported, customTitle && !title.equals(imported));
        }

        Entry moveToTrash(long when) {
            if (inTrash()) return this;
            return new Entry(id, title, file, created, TRASH, digest,
                    category, when, originalTitle, customTitle);
        }

        Entry restoreFromTrash() {
            if (!TRASH.equals(category)) throw new IllegalStateException("Chat nicht wiederherstellbar");
            String target = PROJECT.equals(originCategory) ? PROJECT : OTHER;
            return new Entry(id, title, file, created, target, digest,
                    "", 0, originalTitle, customTitle);
        }

        Entry beginPermanentDeletion() {
            if (!inTrash()) throw new IllegalStateException("Chat muss im Papierkorb liegen");
            return new Entry(id, title, file, created, PURGE_PENDING, digest,
                    originCategory, trashedAt, originalTitle, customTitle);
        }

        String prettyDate() {
            if (created <= 0) return "Datum unbekannt";
            return DATE.format(Instant.ofEpochSecond(created).atZone(ZoneId.systemDefault()));
        }

        JSONObject asJson() throws JSONException {
            JSONObject json = new JSONObject();
            json.put("id", id);
            json.put("title", title);
            json.put("file", file);
            json.put("created", created);
            json.put("category", category);
            json.put("digest", digest);
            if (customTitle) {
                json.put("custom_title", true);
                json.put("original_title", originalTitle);
            }
            if (inTrash()) {
                json.put("origin_category", originCategory);
                json.put("trashed_at", trashedAt);
            }
            return json;
        }
    }

    /** Metadata for a previously preserved conversation; no chat contents are loaded for inventory. */
    static final class SavedVersion {
        final String digest;
        final long bytes;
        final long savedAt;

        SavedVersion(String digest, long bytes, long savedAt) {
            this.digest = digest;
            this.bytes = bytes;
            this.savedAt = savedAt;
        }

        String displayName() {
            String timestamp = savedAt > 0
                    ? java.time.format.DateTimeFormatter.ofPattern("dd.MM.yyyy HH:mm", Locale.GERMAN)
                        .format(Instant.ofEpochMilli(savedAt).atZone(ZoneId.systemDefault()))
                    : "Datum unbekannt";
            return "Lokal gesichert: " + timestamp + " · " + (bytes / 1024L) + " KiB"
                    + "\nSHA-256: " + digest.substring(0, 12) + "…";
        }
    }

    interface Progress {
        void onProgress(int imported, int updated, int unchanged);
    }

    interface Cancelled {
        boolean isCancelled();
    }

    interface ExportProgress {
        void onProgress(int done, int total);
    }

    static final class ImportResult {
        int imported;
        int updated;
        int unchanged;
        int archived;
        int skippedTrashed;
        int failed;
        boolean cancelled;
        final Set<String> newIds = new HashSet<>();
        final List<String> errors = new ArrayList<>();

        String summary() {
            String output = "Neu: " + imported + " · Geändert: " + updated
                    + " · Bereits identisch: " + unchanged;
            if (archived > 0) output += " · Ältere/abweichende Versionen gesichert: " + archived;
            if (skippedTrashed > 0) output += " · Im Papierkorb belassen: " + skippedTrashed;
            if (failed > 0) output += " · Fehler: " + failed;
            if (cancelled) output += " · Abgebrochen (bisheriger Stand gesichert)";
            if (!errors.isEmpty()) output += "\n" + errors.get(0);
            return output;
        }
    }

    private final Context context;
    private final File conversations;
    private final File versions;
    private final File index;
    private long savedVersionBytes;
    private final Map<String, Entry> entries = new LinkedHashMap<>();

    ChatStore(Context context) throws IOException {
        this.context = context.getApplicationContext();
        conversations = new File(context.getFilesDir(), "conversations");
        if (!conversations.isDirectory() && !conversations.mkdirs()) {
            throw new IOException("Interner Speicher konnte nicht erstellt werden");
        }
        versions = new File(context.getFilesDir(), "conversation-versions");
        if (!versions.isDirectory() && !versions.mkdirs()) {
            throw new IOException("Versionsspeicher konnte nicht erstellt werden");
        }
        File[] previousVersions = versions.listFiles();
        if (previousVersions != null) {
            for (File saved : previousVersions) if (saved.isFile()) savedVersionBytes += saved.length();
        }
        index = new File(context.getFilesDir(), "index.json");
        loadIndex();
    }

    private synchronized void loadIndex() throws IOException {
        if (!index.isFile()) return;
        try {
            JSONArray json = new JSONArray(new String(Files.readAllBytes(index.toPath()), StandardCharsets.UTF_8));
            for (int i = 0; i < json.length(); i++) {
                JSONObject record = json.optJSONObject(i);
                if (record == null) continue;
                String id = record.optString("id", "");
                String file = record.optString("file", "");
                if (id.isEmpty() || !file.matches("[0-9a-f]{64}\\.json")) continue;
                String category = record.optString("category", OTHER);
                if (!PROJECT.equals(category) && !OTHER.equals(category)
                        && !TRASH.equals(category) && !PURGE_PENDING.equals(category)) category = OTHER;
                String origin = record.optString("origin_category", "");
                if (!PROJECT.equals(origin) && !OTHER.equals(origin)) origin = OTHER;
                long trashedAt = Math.max(0, record.optLong("trashed_at", 0));
                String title = record.optString("title", "Ohne Titel");
                boolean custom = record.optBoolean("custom_title", false);
                String original = custom ? record.optString("original_title", title) : title;
                entries.put(id, new Entry(id, title,
                        file, record.optLong("created", 0), category,
                        record.optString("digest", ""), origin, trashedAt, original, custom));
            }
        } catch (JSONException exception) {
            throw new IOException("Gesprächsindex beschädigt: " + exception.getMessage(), exception);
        }
    }

    synchronized List<Entry> snapshot() {
        ArrayList<Entry> result = new ArrayList<>();
        for (Entry entry : entries.values()) if (!entry.inTrash()) result.add(entry);
        result.sort(Comparator.comparingLong((Entry item) -> item.created).reversed());
        return result;
    }

    synchronized List<Entry> trashSnapshot() {
        ArrayList<Entry> result = new ArrayList<>();
        for (Entry entry : entries.values()) if (entry.inTrash()) result.add(entry);
        result.sort(Comparator.comparingLong((Entry item) -> item.trashedAt).reversed());
        return result;
    }

    /**
     * Atomic batch of category assignments or recoverable trash moves.
     * Validates every chat ID before making any change; commits one index update.
     */
    synchronized int batchUpdate(List<String> selectedIds, String destination) throws IOException {
        if (!PROJECT.equals(destination) && !OTHER.equals(destination) && !TRASH.equals(destination))
            throw new IOException("Unbekanntes Ziel");
        if (selectedIds == null || selectedIds.isEmpty()) return 0;
        Set<String> unique = new LinkedHashSet<>(selectedIds);
        if (unique.size() > 2000) throw new IOException("Maximal 2000 Chats pro Sammelaktion");
        for (String id : unique) {
            Entry original = entries.get(id);
            if (original == null || original.inTrash())
                throw new IOException("Auswahl ist nicht mehr aktuell; bitte neu auswählen");
        }
        Map<String, Entry> originals = new LinkedHashMap<>();
        long now = System.currentTimeMillis() / 1000;
        for (String id : unique) {
            Entry original = entries.get(id);
            Entry next = TRASH.equals(destination) ? original.moveToTrash(now)
                    : original.withCategory(destination);
            if (original.category.equals(next.category)) continue;
            originals.put(id, original);
            entries.put(id, next);
        }
        if (originals.isEmpty()) return 0;
        try { saveIndex(); }
        catch (IOException error) {
            for (Map.Entry<String, Entry> old : originals.entrySet())
                entries.put(old.getKey(), old.getValue());
            throw error;
        }
        return originals.size();
    }

    synchronized void moveToTrash(String id) throws IOException {
        Entry existing = entries.get(id);
        if (existing == null || existing.inTrash()) throw new IOException("Gespräch nicht aktiv");
        Entry updated = existing.moveToTrash(System.currentTimeMillis() / 1000);
        entries.put(id, updated);
        try { saveIndex(); }
        catch (IOException error) { entries.put(id, existing); throw error; }
    }

    synchronized void restoreTrash(String id) throws IOException {
        Entry existing = entries.get(id);
        if (existing == null || !TRASH.equals(existing.category))
            throw new IOException("Gespräch nicht wiederherstellbar");
        if (!new File(conversations, existing.file).isFile())
            throw new IOException("Chatdatei nicht mehr vorhanden – keine Wiederherstellung");
        entries.put(id, existing.restoreFromTrash());
        try { saveIndex(); }
        catch (IOException error) { entries.put(id, existing); throw error; }
    }

    /**
     * Permanent deletion is an explicit second step. A durable pending marker
     * remains in the index until private files and archived versions are removed.
     * If I/O fails, retry through the trash; never silently reinstate partial data.
     */
    synchronized void permanentlyDeleteFromTrash(String id) throws IOException {
        Entry current = entries.get(id);
        if (current == null || !current.inTrash()) throw new IOException("Chat nicht im Papierkorb");
        if (!PURGE_PENDING.equals(current.category)) {
            Entry pending = current.beginPermanentDeletion();
            entries.put(id, pending);
            try { saveIndex(); }
            catch (IOException error) { entries.put(id, current); throw error; }
            current = pending;
        }
        File[] archived = versions.listFiles();
        if (archived == null) throw new IOException("Versionsspeicher nicht lesbar – Löschung kann erneut versucht werden");
        String chatHash = sha256(id);
        Files.deleteIfExists(new File(conversations, current.file).toPath());
        Files.deleteIfExists(new File(conversations, chatHash + ".search").toPath());
        String expectedPrefix = chatHash + "-";
        for (File file : archived) {
            String name = file.getName();
            if (file.isFile() && name.startsWith(expectedPrefix)
                    && name.substring(expectedPrefix.length()).matches("[0-9a-f]{64}\\.json")) {
                long bytes = file.length();
                if (Files.deleteIfExists(file.toPath())) savedVersionBytes = Math.max(0, savedVersionBytes - bytes);
            }
        }
        entries.remove(id);
        try { saveIndex(); }
        catch (IOException error) { entries.put(id, current); throw error; }
    }

    /** Renames the LOCAL display title only. Original ChatGPT JSON and indexes remain intact. */
    synchronized void renameChat(String id, String requested) throws IOException {
        Entry old = entries.get(id);
        if (old == null || PURGE_PENDING.equals(old.category))
            throw new IOException("Gespräch nicht zum Umbenennen verfügbar");
        String name = validateLocalTitle(requested);
        Entry updated = old.withLocalTitle(name);
        if (old.title.equals(updated.title) && old.customTitle == updated.customTitle) return;
        entries.put(id, updated);
        try { saveIndex(); }
        catch (IOException error) { entries.put(id, old); throw error; }
    }

    static String validateLocalTitle(String value) throws IOException {
        if (value == null) throw new IOException("Titel fehlt");
        String title = value.trim();
        if (title.isEmpty()) throw new IOException("Titel darf nicht leer sein");
        if (title.length() > 180) throw new IOException("Titel darf maximal 180 Zeichen lang sein");
        for (int i = 0; i < title.length(); i++) {
            if (Character.isISOControl(title.charAt(i)))
                throw new IOException("Titel darf keine Zeilenumbrüche oder Steuerzeichen enthalten");
        }
        return title;
    }

    synchronized Entry entryForDisplay(String id) {
        return entries.get(id);
    }

    synchronized void restoreOriginalTitle(String id) throws IOException {
        Entry old = entries.get(id);
        if (old == null || PURGE_PENDING.equals(old.category))
            throw new IOException("Gespräch nicht zum Zurücksetzen verfügbar");
        if (!old.customTitle) return;
        entries.put(id, old.withLocalTitle(old.originalTitle));
        try { saveIndex(); }
        catch (IOException error) { entries.put(id, old); throw error; }
    }

    synchronized void setCategory(String id, String category) throws IOException {
        Entry previous = entries.get(id);
        if (previous == null || previous.inTrash()) return;
        if (!PROJECT.equals(category) && !OTHER.equals(category)) return;
        entries.put(id, previous.withCategory(category));
        try { saveIndex(); }
        catch (IOException failure) { entries.put(id, previous); throw failure; }
    }

    /** No modification, deletion, automatic selection or restoration of previous versions. */
    List<SavedVersion> listArchivedVersions(String chatId) throws IOException {
        if (chatId == null || chatId.isEmpty()) throw new IOException("Chat-ID fehlt");
        String prefix = sha256(chatId) + "-";
        File[] files = versions.listFiles();
        if (files == null) throw new IOException("Versionsspeicher nicht lesbar");
        List<SavedVersion> found = new ArrayList<>();
        for (File file : files) {
            String name = file.getName();
            if (!file.isFile() || !name.startsWith(prefix) || !name.endsWith(".json")) continue;
            String digest = name.substring(prefix.length(), name.length() - 5);
            if (!digest.matches("[0-9a-f]{64}")) continue;
            found.add(new SavedVersion(digest, file.length(), file.lastModified()));
        }
        found.sort(Comparator.comparingLong((SavedVersion v) -> v.savedAt).reversed());
        return found;
    }

    /** Integrity-checked, bounded, read-only access to one explicitly selected historical JSON. */
    JSONObject loadArchivedVersion(String chatId, String digest) throws IOException {
        final String fileName;
        try { fileName = archivedVersionFilename(chatId, digest); }
        catch (IllegalArgumentException invalid) { throw new IOException("Ungültige Archivversion", invalid); }
        File source = new File(versions, fileName);
        if (!source.isFile()) throw new IOException("Archivversion nicht vorhanden");
        long length = Files.size(source.toPath());
        if (length > MAX_ARCHIVED_PREVIEW_BYTES) {
            throw new IOException("Archivversion größer als 32 MiB: Anzeige zum Speicherschutz begrenzt");
        }
        String raw = new String(Files.readAllBytes(source.toPath()), StandardCharsets.UTF_8);
        if (!sha256(raw).equals(digest)) throw new IOException("Integritätsfehler: Archivversion verändert");
        try {
            JSONObject conversation = new JSONObject(raw);
            if (!chatId.equals(conversation.optString("id", "")))
                throw new IOException("Integritätsfehler: andere Chat-ID in Archivversion");
            return conversation;
        } catch (JSONException invalidJson) {
            throw new IOException("Archivversion enthält kein gültiges JSON", invalidJson);
        }
    }

    static String archivedVersionFilename(String chatId, String digest) {
        if (chatId == null || chatId.isEmpty() || digest == null || !digest.matches("[0-9a-f]{64}"))
            throw new IllegalArgumentException("Invalid archive reference");
        return sha256(chatId) + "-" + digest + ".json";
    }

    JSONObject loadConversation(String id) throws IOException {
        Entry entry;
        synchronized (this) { entry = entries.get(id); }
        if (entry == null) throw new IOException("Gespräch nicht gefunden");
        try {
            return new JSONObject(new String(Files.readAllBytes(new File(conversations, entry.file).toPath()),
                    StandardCharsets.UTF_8));
        } catch (JSONException exception) {
            throw new IOException("Gesprächsdaten ungültig", exception);
        }
    }

    ImportResult importFiles(List<Uri> files, Progress progress) {
        ImportResult result = new ImportResult();
        for (Uri fileUri : files) {
            if (Thread.currentThread().isInterrupted()) break;
            try (InputStream input = context.getContentResolver().openInputStream(fileUri)) {
                if (input == null) throw new IOException("Datei kann nicht geöffnet werden");
                try (BufferedInputStream buffered = new BufferedInputStream(input, 65536)) {
                    buffered.mark(8);
                    int first = buffered.read();
                    int second = buffered.read();
                    buffered.reset();
                    if (first == 'P' && second == 'K') {
                        importZip(buffered, result, progress);
                    } else {
                        try (JsonReader reader = new JsonReader(new InputStreamReader(buffered, StandardCharsets.UTF_8))) {
                            importJsonArray(reader, result, progress);
                        }
                    }
                }
                synchronized (this) { saveIndex(); }
            } catch (Exception exception) {
                result.failed++;
                if (result.errors.size() < 3) result.errors.add(exception.getMessage() == null
                        ? "Unbekannter Importfehler" : exception.getMessage());
                try {
                    synchronized (this) { saveIndex(); }
                } catch (IOException secondary) {
                    result.errors.add("Index konnte nicht gespeichert werden: " + secondary.getMessage());
                }
            }
        }
        progress.onProgress(result.imported, result.updated, result.unchanged);
        return result;
    }

    /** Imports only the explicit, scanned local files; never opens other files. */
    ImportResult importLocalFiles(List<File> files, Progress progress, Cancelled cancelled) {
        ImportResult result = new ImportResult();
        for (File file : files) {
            if (cancelled.isCancelled() || Thread.currentThread().isInterrupted()) {
                result.cancelled = true;
                break;
            }
            try {
                if (!file.isFile()) throw new IOException("Datei nicht mehr vorhanden: " + file.getName());
                if (file.getName().toLowerCase(Locale.ROOT).endsWith(".zip")) {
                    importZipIndexed(file, result, progress, cancelled);
                } else if (StorageScanner.isConversationJson(file.getName())) {
                    try (InputStream input = new BufferedInputStream(new FileInputStream(file), 65536);
                         JsonReader reader = new JsonReader(new InputStreamReader(input, StandardCharsets.UTF_8))) {
                        importJsonArray(reader, result, progress, cancelled);
                    }
                } else {
                    throw new IOException("Nicht unterstützter Export: " + file.getName());
                }
                synchronized (this) { saveIndex(); }
            } catch (Exception exception) {
                if (cancelled.isCancelled() || Thread.currentThread().isInterrupted()) {
                    result.cancelled = true;
                } else {
                    result.failed++;
                    if (result.errors.size() < 3) result.errors.add(file.getName() + ": "
                            + (exception.getMessage() == null ? "Importfehler" : exception.getMessage()));
                }
                try { synchronized (this) { saveIndex(); } }
                catch (IOException secondary) {
                    if (result.errors.size() < 3) result.errors.add("Indexspeicherung fehlgeschlagen: " + secondary.getMessage());
                }
                if (result.cancelled) break;
            }
        }
        progress.onProgress(result.imported, result.updated, result.unchanged);
        return result;
    }

    /** Interoperable backup ZIP; media and historical versions are not included. */
    void exportAllToZip(OutputStream destination, ExportProgress progress,
                        Cancelled cancelled) throws IOException {
        List<Entry> records = snapshot();
        try (ZipOutputStream zip = new ZipOutputStream(destination, StandardCharsets.UTF_8)) {
            zip.putNextEntry(new ZipEntry("conversations-000.json"));
            zip.write('[');
            byte[] buffer = new byte[65536];
            for (int i = 0; i < records.size(); i++) {
                if (cancelled.isCancelled() || Thread.currentThread().isInterrupted()) {
                    throw new IOException("Archiv-Export abgebrochen");
                }
                Entry record = records.get(i);
                if (i > 0) zip.write(',');
                try (InputStream input = new BufferedInputStream(
                        new FileInputStream(new File(conversations, record.file)), 65536)) {
                    int length;
                    while ((length = input.read(buffer)) != -1) {
                        if (cancelled.isCancelled() || Thread.currentThread().isInterrupted()) {
                            throw new IOException("Archiv-Export abgebrochen");
                        }
                        zip.write(buffer, 0, length);
                    }
                }
                progress.onProgress(i + 1, records.size());
            }
            zip.write(']');
            zip.closeEntry();

            JSONObject categories = new JSONObject();
            JSONObject localTitles = new JSONObject();
            JSONObject manifest = new JSONObject();
            try {
                for (Entry record : records) {
                    categories.put(record.id, record.category);
                    if (record.customTitle) localTitles.put(record.id, record.title);
                }
                manifest.put("title_overrides_by_id", localTitles);
                manifest.put("format", "universelab-chatarchiv");
                manifest.put("version", 1);
                manifest.put("conversation_count", records.size());
                manifest.put("category_by_id", categories);
                manifest.put("notice", "Nur gespeicherte Hauptfassungen der Chat-JSONs; Medien und Altversionen nicht enthalten.");
            } catch (JSONException exception) {
                throw new IOException("Backup-Metadaten konnten nicht geschrieben werden", exception);
            }
            zip.putNextEntry(new ZipEntry("chatarchiv_manifest.json"));
            zip.write(manifest.toString().getBytes(StandardCharsets.UTF_8));
            zip.closeEntry();
            zip.finish();
        }
    }

    /** ZIP central directory allows random access without scanning huge media entries. */
    private void importZipIndexed(File file, ImportResult result, Progress progress,
                                  Cancelled cancelled) throws IOException {
        try (ZipFile zip = new ZipFile(file)) {
            Enumeration<? extends ZipEntry> entries = zip.entries();
            int relevantEntries = 0;
            long extractedBytes = 0;
            while (entries.hasMoreElements()) {
                if (cancelled.isCancelled()) throw new IOException("Import abgebrochen");
                ZipEntry entry = entries.nextElement();
                if (entry.isDirectory()) continue;
                String name = entry.getName();
                name = name.substring(name.lastIndexOf('/') + 1);
                if (!StorageScanner.isConversationJson(name)) continue;
                if (++relevantEntries > MAX_ZIP_JSON_ENTRIES) {
                    throw new IOException("ZIP-Grenze: mehr als 100 Gesprächsdateien");
                }
                long remaining = MAX_ZIP_JSON_BYTES - extractedBytes;
                if (remaining <= 0 || (entry.getSize() >= 0 && entry.getSize() > remaining)) {
                    throw new IOException("ZIP-Grenze: Gesprächsdateien über 3 GiB");
                }
                try (InputStream input = new BufferedInputStream(zip.getInputStream(entry), 65536)) {
                    CountingInputStream bounded = new CountingInputStream(input, remaining);
                    JsonReader reader = new JsonReader(new InputStreamReader(bounded, StandardCharsets.UTF_8));
                    importJsonArray(reader, result, progress, cancelled);
                    extractedBytes += bounded.count;
                }
            }
            if (relevantEntries == 0) throw new IOException("ZIP enthält keine Gesprächs-JSON");
            ZipEntry manifest = zip.getEntry("chatarchiv_manifest.json");
            if (manifest != null && manifest.getSize() <= MAX_MANIFEST_BYTES) {
                try (InputStream input = zip.getInputStream(manifest)) {
                    applyBackupCategories(new CountingInputStream(input, MAX_MANIFEST_BYTES), result);
                }
            }
        }
    }

    private void importZip(InputStream stream, ImportResult result, Progress progress) throws IOException {
        boolean foundConversations = false;
        int relevantEntries = 0;
        long extractedBytes = 0;
        try (ZipInputStream zip = new ZipInputStream(stream, StandardCharsets.UTF_8)) {
            ZipEntry entry;
            while ((entry = zip.getNextEntry()) != null) {
            if (Thread.currentThread().isInterrupted()) throw new IOException("ZIP-Import unterbrochen");
                String fullName = entry.getName();
                String name = fullName.substring(fullName.lastIndexOf('/') + 1);
                boolean isChatJson = StorageScanner.isConversationJson(name) && !entry.isDirectory();
                if (!isChatJson) {
                    if ("chatarchiv_manifest.json".equals(name)) {
                        applyBackupCategories(new CountingInputStream(zip, MAX_MANIFEST_BYTES), result);
                        zip.closeEntry();
                        continue;
                    }
                    // ChatGPT archives usually put their JSON files first. Stop at the
                    // first media blob after them; never traverse tens of GB of attachments.
                    if (foundConversations && name.startsWith("file-") && name.endsWith(".dat")) break;
                    zip.closeEntry();
                    continue;
                }
                foundConversations = true;
                relevantEntries++;
                if (relevantEntries > MAX_ZIP_JSON_ENTRIES) {
                    throw new IOException("ZIP-Grenze: zu viele Gesprächs-JSON-Einträge");
                }
                long remaining = MAX_ZIP_JSON_BYTES - extractedBytes;
                if (remaining <= 0) throw new IOException("ZIP-Grenze: Gesprächsdaten zu groß");
                CountingInputStream bounded = new CountingInputStream(zip, remaining);
                // Deliberately do not close the reader: that would also close the ZIP
                // stream and prevent importing conversations-001.json etc.
                JsonReader reader = new JsonReader(new InputStreamReader(bounded, StandardCharsets.UTF_8));
                importJsonArray(reader, result, progress);
                extractedBytes += bounded.count;
                zip.closeEntry();
            }
        }
        if (!foundConversations) throw new IOException("Im ZIP wurde keine conversations*.json gefunden");
    }

    private void importJsonArray(JsonReader reader, ImportResult result, Progress progress) throws IOException {
        importJsonArray(reader, result, progress, () -> false);
    }

    private void importJsonArray(JsonReader reader, ImportResult result, Progress progress,
                                 Cancelled cancelled) throws IOException {
        if (reader.peek() != JsonToken.BEGIN_ARRAY) {
            throw new IOException("Erwartet wird conversations*.json als JSON-Array");
        }
        reader.beginArray();
        while (reader.hasNext()) {
            if (Thread.currentThread().isInterrupted() || cancelled.isCancelled()) {
                throw new IOException("Import unterbrochen");
            }
            Object value = readValue(reader, 0);
            if (!(value instanceof JSONObject)) continue;
            JSONObject conversation = (JSONObject) value;
            String id = conversation.optString("id", "");
            if (id.isEmpty() || conversation.optJSONObject("mapping") == null) continue;
            ImportChange change = upsert(conversation, id);
            if (change == ImportChange.UNCHANGED) result.unchanged++;
            else if (change == ImportChange.UPDATED) result.updated++;
            else if (change == ImportChange.ARCHIVED) result.archived++;
            else if (change == ImportChange.TRASHED) result.skippedTrashed++;
            else { result.imported++; result.newIds.add(id); }
            int total = result.imported + result.updated + result.unchanged + result.skippedTrashed;
            if (total % 10 == 0) progress.onProgress(result.imported, result.updated, result.unchanged);
        }
        reader.endArray();
    }

    private void applyBackupCategories(InputStream source, ImportResult result) throws IOException {
        JsonReader reader = new JsonReader(new InputStreamReader(source, StandardCharsets.UTF_8));
        Object decoded = readValue(reader, 0);
        if (!(decoded instanceof JSONObject)) return;
        JSONObject manifest = (JSONObject) decoded;
        if (!"universelab-chatarchiv".equals(manifest.optString("format", ""))) return;
        JSONObject map = manifest.optJSONObject("category_by_id");
        JSONObject titles = manifest.optJSONObject("title_overrides_by_id");
        if (map == null && titles == null) return;
        synchronized (this) {
            for (String id : result.newIds) {
                Entry previous = entries.get(id);
                if (previous == null || previous.inTrash()) continue;
                Entry updated = previous;
                if (map != null) {
                    String category = map.optString(id, "");
                    if (PROJECT.equals(category) || OTHER.equals(category))
                        updated = updated.withCategory(category);
                }
                if (titles != null && titles.has(id) && !updated.customTitle) {
                    try { updated = updated.withLocalTitle(validateLocalTitle(titles.optString(id, ""))); }
                    catch (IOException ignored) { /* Ignore invalid optional title alias. */ }
                }
                entries.put(id, updated);
            }
        }
    }

    private static final class CountingInputStream extends FilterInputStream {
        private final long maximum;
        long count;

        CountingInputStream(InputStream source, long maximum) {
            super(source);
            this.maximum = maximum;
        }

        @Override public int read() throws IOException {
            int value = in.read();
            if (value != -1 && ++count > maximum) throw new IOException("ZIP-Grenze überschritten");
            return value;
        }

        @Override public int read(byte[] bytes, int offset, int length) throws IOException {
            int n = in.read(bytes, offset, length);
            if (n > 0 && (count += n) > maximum) throw new IOException("ZIP-Grenze überschritten");
            return n;
        }
    }

    private enum ImportChange { ADDED, UPDATED, UNCHANGED, ARCHIVED, TRASHED }

    private ImportChange upsert(JSONObject data, String id) throws IOException {
        String fileName = sha256(id) + ".json";
        String title = data.optString("title", "Ohne Titel");
        if (title.trim().isEmpty()) title = "Ohne Titel";
        long created = 0;
        Object time = data.opt("create_time");
        if (time instanceof Number) created = ((Number) time).longValue();
        String serialized = data.toString();
        String digest = sha256(serialized);
        synchronized (this) {
            Entry previous = entries.get(id);
            // Explicitly deleted records are not resurrected by a later bulk import.
            if (previous != null && previous.inTrash()) return ImportChange.TRASHED;
            if (previous != null && digest.equals(previous.digest)) return ImportChange.UNCHANGED;
            File current = new File(conversations, fileName);
            if (previous != null && current.isFile()) {
                String older = new String(Files.readAllBytes(current.toPath()), StandardCharsets.UTF_8);
                JSONObject oldObject;
                try { oldObject = new JSONObject(older); }
                catch (JSONException exception) { throw new IOException("Vorhandene Chatversion nicht lesbar", exception); }
                long oldTime = updatedAt(oldObject);
                long incomingTime = updatedAt(data);
                int oldNodes = oldObject.optJSONObject("mapping") == null ? 0
                        : oldObject.optJSONObject("mapping").length();
                int newNodes = data.optJSONObject("mapping").length();
                // Older exports must not replace a newer conversation. Ties
                // favor the richer node map; other variants remain recoverable.
                if (incomingTime < oldTime || (incomingTime == oldTime && newNodes <= oldNodes)) {
                    return archiveVersion(id, digest, serialized)
                            ? ImportChange.ARCHIVED : ImportChange.UNCHANGED;
                }
                archiveVersion(id, sha256(older), older);
            }
            String indexed = ConversationLogic.indexText(data);
            writeAtomic(current, serialized);
            writeAtomic(new File(conversations, sha256(id) + ".search"), indexed);
            String category = previous != null ? previous.category : categoryFromTitle(title);
            entries.put(id, previous == null
                    ? new Entry(id, title, fileName, created, category, digest)
                    : previous.withImportedTitle(title, created, digest));
            return previous != null ? ImportChange.UPDATED : ImportChange.ADDED;
        }
    }

    private boolean archiveVersion(String id, String digest, String serialized) throws IOException {
        File preserved = new File(versions, archivedVersionFilename(id, digest));
        if (preserved.isFile()) return false;
        long bytes = serialized.getBytes(StandardCharsets.UTF_8).length;
        if (savedVersionBytes + bytes > MAX_SAVED_VERSIONS_BYTES) {
            throw new IOException("Versionsspeicher-Limit (1 GiB) erreicht; aktuelle Chatfassung unverändert");
        }
        writeAtomic(preserved, serialized);
        savedVersionBytes += bytes;
        return true;
    }

    private static long updatedAt(JSONObject conversation) {
        double timestamp = conversation.optDouble("update_time", 0);
        return Double.isFinite(timestamp) && timestamp > 0 ? (long) timestamp : 0;
    }

    private static String categoryFromTitle(String title) {
        String normalized = title.toLowerCase(Locale.ROOT);
        return normalized.matches("(?s).*(universelab|hyperzeit|hzt|hpvs|mond|brane|baryogenese).*")
                ? PROJECT : OTHER;
    }

    /**
     * Search syntax:
     * - 'New Chats' = OR between the two complete words.
     * - '"New Chats"' = contiguous phrase, respecting word boundaries.
     * - 'titel:"New Chats"' = phrase restricted to chat titles.
     * Unqualified terms search both titles and indexed visible message text.
     */
    private static final class SearchTerm {
        final String value;
        final boolean titleOnly;
        SearchTerm(String value, boolean titleOnly) {
            this.value = value.toLowerCase(Locale.ROOT);
            this.titleOnly = titleOnly;
        }
    }

    private static List<SearchTerm> parseSearchTerms(String input) {
        List<SearchTerm> terms = new ArrayList<>();
        if (input == null) return terms;
        int i = 0;
        // Bound query complexity without ever treating a nonempty query as "show all".
        while (i < input.length() && terms.size() < 64) {
            while (i < input.length() && Character.isWhitespace(input.charAt(i))) i++;
            if (i >= input.length()) break;
            boolean titleOnly = false;
            if (input.regionMatches(true, i, "titel:", 0, 6)) {
                titleOnly = true;
                i += 6;
            } else if (input.regionMatches(true, i, "title:", 0, 6)) {
                titleOnly = true;
                i += 6;
            }
            if (i >= input.length()) break;
            boolean quoted = input.charAt(i) == '"';
            if (quoted) i++;
            int start = i;
            if (quoted) {
                while (i < input.length() && input.charAt(i) != '"') i++;
            } else {
                while (i < input.length() && !Character.isWhitespace(input.charAt(i))) i++;
            }
            String term = input.substring(start, i).trim();
            if (quoted && i < input.length()) i++;
            if (!term.isEmpty()) {
                String normalized = (term.length() > 256 ? term.substring(0, 256) : term)
                        .toLowerCase(Locale.ROOT);
                // A repeated query term is still one distinct condition, not extra rank.
                boolean duplicate = false;
                for (SearchTerm existing : terms) {
                    if (existing.titleOnly == titleOnly && existing.value.equals(normalized)) {
                        duplicate = true;
                        break;
                    }
                }
                if (!duplicate) terms.add(new SearchTerm(normalized, titleOnly));
            }
        }
        return terms;
    }

    private static boolean wordCodePoint(int point) {
        int kind = Character.getType(point);
        return Character.isLetterOrDigit(point) || point == '_'
                || kind == Character.NON_SPACING_MARK
                || kind == Character.COMBINING_SPACING_MARK
                || kind == Character.ENCLOSING_MARK;
    }

    private static boolean containsCompleteTerm(String lowerCaseText, String lowerCaseTerm,
                                                boolean realBeginning, boolean realEnd) {
        int offset = 0;
        while ((offset = lowerCaseText.indexOf(lowerCaseTerm, offset)) >= 0) {
            int end = offset + lowerCaseTerm.length();
            boolean left = offset == 0 ? realBeginning
                    : !wordCodePoint(lowerCaseText.codePointBefore(offset));
            boolean right = end == lowerCaseText.length() ? realEnd
                    : !wordCodePoint(lowerCaseText.codePointAt(end));
            if (left && right) return true;
            offset++;
        }
        return false;
    }

    private static boolean anySearchTermMatches(String lowerCaseText, List<SearchTerm> terms,
                                                 boolean realBeginning, boolean realEnd) {
        for (SearchTerm term : terms)
            if (containsCompleteTerm(lowerCaseText, term.value, realBeginning, realEnd)) return true;
        return false;
    }

    /** One matching term counts once per chat, irrespective of repetitions or location. */
    private static final class RankedEntry {
        final Entry entry;
        final int matchingTerms;
        RankedEntry(Entry entry, int matchingTerms) {
            this.entry = entry;
            this.matchingTerms = matchingTerms;
        }
    }

    static List<Entry> search(List<Entry> items, String category, String phrase, Cancelled cancelled,
                              File privateConversationDirectory) {
        List<SearchTerm> terms = parseSearchTerms(phrase);
        boolean noQuery = phrase == null || phrase.trim().isEmpty();
        List<Entry> ordinary = new ArrayList<>();
        List<RankedEntry> ranked = new ArrayList<>();
        for (Entry item : items) {
            if (cancelled.isCancelled()) break;
            if (!"alle".equals(category) && !category.equals(item.category)) continue;
            if (noQuery) {
                ordinary.add(item);
                continue;
            }
            if (terms.isEmpty()) continue;

            boolean[] found = new boolean[terms.size()];
            String title = item.title.toLowerCase(Locale.ROOT);
            boolean needContents = false;
            for (int i = 0; i < terms.size(); i++) {
                SearchTerm term = terms.get(i);
                found[i] = containsCompleteTerm(title, term.value, true, true);
                if (!found[i] && !term.titleOnly) needContents = true;
            }
            // Previously, one title match returned early, losing additional body
            // matches. Read the index once and mark each distinct remaining term.
            if (needContents) {
                File searchable = new File(privateConversationDirectory,
                        item.file.replace(".json", ".search"));
                try {
                    collectContentMatches(searchable, terms, found, cancelled);
                } catch (IOException ignored) {
                    // Unavailable index: keep the known title hits, do not invent any.
                }
            }
            if (cancelled.isCancelled()) break;
            int matched = 0;
            for (boolean value : found) if (value) matched++;
            if (matched > 0) ranked.add(new RankedEntry(item, matched));
        }
        if (noQuery) return ordinary;
        // TimSort is stable: same-score chats retain their prior newest-first order.
        ranked.sort((left, right) -> Integer.compare(right.matchingTerms, left.matchingTerms));
        for (RankedEntry hit : ranked) ordinary.add(hit.entry);
        return ordinary;
    }

    File privateConversationDirectory() { return conversations; }

    private static void collectContentMatches(File file, List<SearchTerm> terms,
                                              boolean[] found, Cancelled cancelled)
            throws IOException {
        if (!file.isFile()) return;
        int longest = 0;
        int missing = 0;
        for (int i = 0; i < terms.size(); i++) {
            if (!terms.get(i).titleOnly && !found[i]) {
                missing++;
                longest = Math.max(longest, terms.get(i).value.length());
            }
        }
        if (missing == 0) return;
        try (BufferedReader reader = Files.newBufferedReader(file.toPath(), StandardCharsets.UTF_8)) {
            char[] block = new char[8192];
            String suffix = "";
            int n;
            long processedChars = 0;
            while (missing > 0 && (n = reader.read(block)) != -1) {
                if (cancelled.isCancelled()) return;
                String chunk = suffix + new String(block, 0, n);
                processedChars += n;
                String lower = chunk.toLowerCase(Locale.ROOT);
                // The current last character is not a proven word boundary
                // until the next block is read.
                boolean beginning = processedChars == n;
                for (int i = 0; i < terms.size(); i++) {
                    if (found[i] || terms.get(i).titleOnly) continue;
                    if (containsCompleteTerm(lower, terms.get(i).value, beginning, false)) {
                        found[i] = true;
                        missing--;
                    }
                }
                int overlap = Math.min(chunk.length(), longest + 4);
                suffix = chunk.substring(chunk.length() - overlap);
            }
            if (missing == 0 || cancelled.isCancelled() || suffix.isEmpty()) return;
            String lower = suffix.toLowerCase(Locale.ROOT);
            for (int i = 0; i < terms.size(); i++) {
                if (!found[i] && !terms.get(i).titleOnly
                        && containsCompleteTerm(lower, terms.get(i).value,
                                processedChars == suffix.length(), true)) {
                    found[i] = true;
                }
            }
        }
    }

    static final class AuditReport {
        int total, active, trash, checked, zeroVisible, corrupt, missing, noIndex, tooLarge, archived;
        boolean cancelled;
        final List<String> examples = new ArrayList<>();

        void note(String message) {
            if (examples.size() < 16) examples.add("• " + message);
        }

        String summary() {
            StringBuilder out = new StringBuilder("Gespräche insgesamt (Index): " + total
                    + "\nAktive Gespräche: " + active + "\nIm Papierkorb: " + trash
                    + "\nUntersuchte Chatdateien: " + checked
                    + "\n0 sichtbare Beiträge (nur Prüfkandidaten): " + zeroVisible
                    + "\nFehlende Chatdateien: " + missing
                    + "\nBeschädigt / Prüfsumme abweichend: " + corrupt
                    + "\nFehlende Suchindizes: " + noIndex
                    + "\nÜber 16 MiB (Inhaltsprüfung übersprungen): " + tooLarge
                    + "\nGespeicherte Altversionsdateien: " + archived
                    + (cancelled ? "\n\nPrüfung abgebrochen – Angaben unvollständig." : "\n\nPrüfung abgeschlossen.")
                    + "\n0 sichtbare Beiträge bedeutet NICHT zwingend leere Quelldaten."
                    + "\nEs wurde kein Chat geändert oder gelöscht.\n");
            for (String message : examples) out.append("\n").append(message);
            return out.toString();
        }
    }

    AuditReport auditArchive(Cancelled cancelled, ExportProgress progress) {
        AuditReport report = new AuditReport();
        List<Entry> rows;
        synchronized (this) { rows = new ArrayList<>(entries.values()); }
        report.total = rows.size();
        for (Entry item : rows) {
            if (item.inTrash()) report.trash++;
            else report.active++;
        }
        File[] saved = versions.listFiles();
        if (saved != null) for (File file : saved)
            if (file.isFile() && file.getName().matches("[0-9a-f]{64}-[0-9a-f]{64}\\.json"))
                report.archived++;
        for (int i = 0; i < rows.size(); i++) {
            if (cancelled.isCancelled() || Thread.currentThread().isInterrupted()) {
                report.cancelled = true;
                break;
            }
            Entry item = rows.get(i);
            File file = new File(conversations, item.file);
            String label = item.title + " · ID " + item.id.substring(0, Math.min(8, item.id.length()));
            if (!file.isFile()) {
                report.missing++;
                report.note("Fehlende Chatdatei: " + label);
            } else if (file.length() > 16L * 1024 * 1024) {
                report.tooLarge++;
                report.note("Inhaltsprüfung auf 16 MiB begrenzt: " + label);
            } else {
                try {
                    String serialized = new String(Files.readAllBytes(file.toPath()),
                            StandardCharsets.UTF_8);
                    if ((!item.digest.isEmpty() && !sha256(serialized).equals(item.digest))) {
                        report.corrupt++;
                        report.note("Prüfsumme abweichend: " + label);
                    } else {
                        JSONObject obj = new JSONObject(serialized);
                        if (!item.id.equals(obj.optString("id", ""))) {
                            report.corrupt++;
                            report.note("Chat-ID stimmt nicht: " + label);
                        } else {
                            report.checked++;
                            if (ConversationLogic.visibleMessages(obj).isEmpty()) {
                                report.zeroVisible++;
                                report.note("0 sichtbare Beiträge: " + label);
                            }
                        }
                    }
                } catch (Exception invalid) {
                    report.corrupt++;
                    report.note("Chatdaten nicht lesbar: " + label);
                }
            }
            String name = item.file.replace(".json", ".search");
            if (!new File(conversations, name).isFile()) report.noIndex++;
            if (i % 8 == 0) progress.onProgress(i + 1, rows.size());
        }
        progress.onProgress(report.checked + report.missing + report.corrupt + report.tooLarge, rows.size());
        return report;
    }

    /** Complete local snapshot for preservation, not yet a supported one-tap restore format. */
    ArchiveBundle.Report exportCompleteBackup(OutputStream output,
                           Cancelled cancelled, ExportProgress progress) throws IOException {
        if (!index.isFile()) throw new IOException("Gesprächsindex fehlt – Backup nicht möglich");
        List<ArchiveBundle.Item> files = new ArrayList<>();
        files.add(new ArchiveBundle.Item("index.json", index));
        File registerFile = new File(context.getFilesDir(), ResearchRegister.FILE_NAME);
        if (registerFile.isFile())
            files.add(new ArchiveBundle.Item(ResearchRegister.FILE_NAME, registerFile));
        List<Entry> snapshot;
        synchronized (this) { snapshot = new ArrayList<>(entries.values()); }
        int active = 0, trashed = 0, missingSearch = 0;
        for (Entry entry : snapshot) {
            if (entry.inTrash()) trashed++; else active++;
            if (!entry.file.matches("[0-9a-f]{64}\\.json"))
                throw new IOException("Ungültige Datei im Gesprächsindex");
            File current = new File(conversations, entry.file);
            if (!current.isFile()) throw new IOException("Chatdatei fehlt: " + entry.file);
            files.add(new ArchiveBundle.Item("conversations/" + entry.file, current));
            File searchable = new File(conversations, entry.file.replace(".json", ".search"));
            if (searchable.isFile())
                files.add(new ArchiveBundle.Item("conversations/" + searchable.getName(), searchable));
            else missingSearch++;
        }
        int older = 0;
        File[] saved = versions.listFiles();
        if (saved == null) throw new IOException("Versionsspeicher nicht lesbar");
        Arrays.sort(saved, Comparator.comparing(File::getName));
        for (File file : saved) {
            if (!file.isFile() || !file.getName().matches("[0-9a-f]{64}-[0-9a-f]{64}\\.json"))
                continue;
            files.add(new ArchiveBundle.Item("conversation-versions/" + file.getName(), file));
            older++;
        }
        return ArchiveBundle.create(output, files, active, trashed, older, missingSearch,
                cancelled, progress);
    }

    private synchronized void saveIndex() throws IOException {
        JSONArray array = new JSONArray();
        try {
            for (Entry entry : entries.values()) array.put(entry.asJson());
        } catch (JSONException exception) {
            throw new IOException("Index konnte nicht geschrieben werden", exception);
        }
        writeAtomic(index, array.toString());
    }

    private static void writeAtomic(File target, String value) throws IOException {
        File temp = new File(target.getParentFile(), target.getName() + ".tmp");
        Files.write(temp.toPath(), value.getBytes(StandardCharsets.UTF_8));
        try {
            Files.move(temp.toPath(), target.toPath(), StandardCopyOption.ATOMIC_MOVE,
                    StandardCopyOption.REPLACE_EXISTING);
        } catch (AtomicMoveNotSupportedException exception) {
            Files.move(temp.toPath(), target.toPath(), StandardCopyOption.REPLACE_EXISTING);
        }
    }

    private static String sha256(String input) {
        try {
            byte[] hash = MessageDigest.getInstance("SHA-256").digest(input.getBytes(StandardCharsets.UTF_8));
            StringBuilder value = new StringBuilder(64);
            for (byte b : hash) value.append(String.format(Locale.ROOT, "%02x", b & 0xff));
            return value.toString();
        } catch (NoSuchAlgorithmException exception) {
            throw new AssertionError(exception);
        }
    }

    private static Object readValue(JsonReader reader, int depth) throws IOException {
        if (depth > 120) throw new IOException("JSON ist zu tief verschachtelt");
        JsonToken token = reader.peek();
        if (token == JsonToken.BEGIN_OBJECT) {
            JSONObject object = new JSONObject();
            reader.beginObject();
            while (reader.hasNext()) {
                String name = reader.nextName();
                try { object.put(name, readValue(reader, depth + 1)); }
                catch (JSONException exception) { throw new IOException("Ungültiges JSON-Feld", exception); }
            }
            reader.endObject();
            return object;
        }
        if (token == JsonToken.BEGIN_ARRAY) {
            JSONArray array = new JSONArray();
            reader.beginArray();
            while (reader.hasNext()) array.put(readValue(reader, depth + 1));
            reader.endArray();
            return array;
        }
        if (token == JsonToken.STRING) return reader.nextString();
        if (token == JsonToken.NUMBER) {
            String raw = reader.nextString();
            try { return Long.valueOf(raw); }
            catch (NumberFormatException ignored) { return new BigDecimal(raw); }
        }
        if (token == JsonToken.BOOLEAN) return reader.nextBoolean();
        if (token == JsonToken.NULL) { reader.nextNull(); return JSONObject.NULL; }
        throw new IOException("Unerwartetes JSON-Token: " + token);
    }
}

/**
 * Streamed, read-only full archive snapshot with per-file SHA-256. Verification
 * is independent from the app's database and never extracts a ZIP entry.
 */
final class ArchiveBundle {
    static final String FORMAT = "universelab-chatarchiv-full";
    private static final int LIMIT_FILES = 30000;
    private static final long LIMIT_TOTAL = 12L * 1024 * 1024 * 1024;
    private static final long LIMIT_FILE = 3L * 1024 * 1024 * 1024;
    private static final int MANIFEST_LIMIT = 8 * 1024 * 1024;

    static final class Item {
        final String name;
        final File source;
        Item(String name, File source) { this.name = name; this.source = source; }
    }

    static final class Report {
        final int files, active, trash, versions, missingSearch;
        final long bytes;
        Report(int files, int active, int trash, int versions, int missingSearch, long bytes) {
            this.files = files;
            this.active = active;
            this.trash = trash;
            this.versions = versions;
            this.missingSearch = missingSearch;
            this.bytes = bytes;
        }
        String summary() {
            return "Hauptfassungen aktiv: " + active + " · Papierkorb: " + trash
                    + " · Altversionen: " + versions + "\nGesicherte Dateien: " + files
                    + " · Nutzdaten: " + (bytes / 1024 / 1024) + " MiB"
                    + "\nFehlende optionale Suchindizes: " + missingSearch
                    + "\nPrüfsummen: SHA-256 je Datei. Bitte das fertige ZIP über "
                    + "„Vollbackup prüfen“ unabhängig verifizieren."
                    + "\nKeine Medienanhänge enthalten, die nicht im lokalen Archiv gespeichert sind."
                    + "\nWiederherstellen aus diesem neuen Gesamtformat ist noch nicht freigegeben.";
        }
    }

    private static boolean validName(String name) {
        return "index.json".equals(name)
                || ResearchRegister.FILE_NAME.equals(name)
                || name.matches("conversations/[0-9a-f]{64}\\.(json|search)")
                || name.matches("conversation-versions/[0-9a-f]{64}-[0-9a-f]{64}\\.json");
    }

    private static String digestHex(byte[] hash) {
        StringBuilder hex = new StringBuilder(hash.length * 2);
        for (byte value : hash) {
            hex.append(Character.forDigit((value >>> 4) & 0xf, 16));
            hex.append(Character.forDigit(value & 0xf, 16));
        }
        return hex.toString();
    }

    private static MessageDigest newDigest() {
        try { return MessageDigest.getInstance("SHA-256"); }
        catch (NoSuchAlgorithmException missing) { throw new AssertionError(missing); }
    }

    static Report create(OutputStream output, List<Item> inputs, int active, int trash,
                         int versions, int missingSearch, ChatStore.Cancelled cancelled,
                         ChatStore.ExportProgress progress) throws IOException {
        if (inputs.isEmpty() || inputs.size() > LIMIT_FILES)
            throw new IOException("Unzulässige Anzahl von Sicherungsdateien");
        JSONArray checks = new JSONArray();
        Set<String> seen = new HashSet<>();
        long allBytes = 0;
        byte[] buffer = new byte[65536];
        try (ZipOutputStream zip = new ZipOutputStream(output, StandardCharsets.UTF_8)) {
            for (int i = 0; i < inputs.size(); i++) {
                if (cancelled.isCancelled() || Thread.currentThread().isInterrupted())
                    throw new IOException("Vollbackup abgebrochen");
                Item file = inputs.get(i);
                if (!validName(file.name) || !seen.add(file.name))
                    throw new IOException("Ungültiger oder doppelter Sicherungspfad");
                if (!file.source.isFile()) throw new IOException("Sicherung benötigt fehlende Datei: " + file.name);
                long expected = file.source.length();
                if (expected > LIMIT_FILE || expected > LIMIT_TOTAL - allBytes)
                    throw new IOException("Sicherungsgröße überschreitet Schutzgrenze");
                MessageDigest digest = newDigest();
                long counted = 0;
                zip.putNextEntry(new ZipEntry(file.name));
                try (InputStream input = new BufferedInputStream(new FileInputStream(file.source), 65536)) {
                    int n;
                    while ((n = input.read(buffer)) != -1) {
                        if (cancelled.isCancelled() || Thread.currentThread().isInterrupted())
                            throw new IOException("Vollbackup abgebrochen");
                        counted += n;
                        if (counted > LIMIT_FILE || counted > LIMIT_TOTAL - allBytes)
                            throw new IOException("Sicherung überschreitet Größenlimit");
                        digest.update(buffer, 0, n);
                        zip.write(buffer, 0, n);
                    }
                }
                zip.closeEntry();
                allBytes += counted;
                try {
                    checks.put(new JSONObject().put("path", file.name).put("bytes", counted)
                            .put("sha256", digestHex(digest.digest())));
                } catch (JSONException malformed) {
                    throw new IOException("Sicherungsmanifest nicht erstellbar", malformed);
                }
                progress.onProgress(i + 1, inputs.size());
            }
            JSONObject manifest = new JSONObject();
            try {
                manifest.put("format", FORMAT).put("version", 1)
                        .put("active", active).put("trash", trash)
                        .put("historical_versions", versions)
                        .put("missing_search_indexes", missingSearch)
                        .put("files", checks);
            } catch (JSONException malformed) {
                throw new IOException("Sicherungsmanifest nicht erstellbar", malformed);
            }
            byte[] metadata = manifest.toString().getBytes(StandardCharsets.UTF_8);
            if (metadata.length > MANIFEST_LIMIT) throw new IOException("Sicherungsmanifest zu groß");
            zip.putNextEntry(new ZipEntry("manifest.json"));
            zip.write(metadata);
            zip.closeEntry();
            zip.finish();
        }
        return new Report(inputs.size(), active, trash, versions, missingSearch, allBytes);
    }

    static Report verify(InputStream input, ChatStore.Cancelled cancelled,
                         ChatStore.ExportProgress progress) throws IOException {
        Map<String, String> actual = new HashMap<>();
        Map<String, Long> actualSizes = new HashMap<>();
        byte[] buffer = new byte[65536];
        byte[] manifestBytes = null;
        long total = 0;
        int count = 0;
        try (ZipInputStream zip = new ZipInputStream(new BufferedInputStream(input, 65536),
                StandardCharsets.UTF_8)) {
            ZipEntry entry;
            while ((entry = zip.getNextEntry()) != null) {
                if (cancelled.isCancelled() || Thread.currentThread().isInterrupted())
                    throw new IOException("Backup-Prüfung abgebrochen");
                if (entry.isDirectory()) throw new IOException("Unbekannter Ordner im Backup");
                String name = entry.getName();
                if ("manifest.json".equals(name)) {
                    if (manifestBytes != null) throw new IOException("Doppeltes Sicherungsmanifest");
                    ByteArrayOutputStream bytes = new ByteArrayOutputStream();
                    int n;
                    while ((n = zip.read(buffer)) != -1) {
                        if (cancelled.isCancelled()) throw new IOException("Backup-Prüfung abgebrochen");
                        if (bytes.size() + n > MANIFEST_LIMIT) throw new IOException("Manifest zu groß");
                        bytes.write(buffer, 0, n);
                    }
                    manifestBytes = bytes.toByteArray();
                    zip.closeEntry();
                    continue;
                }
                if (manifestBytes != null) throw new IOException("Datei nach Manifest");
                if (!validName(name) || actual.containsKey(name) || ++count > LIMIT_FILES)
                    throw new IOException("Unbekannte oder doppelte Datei im Backup");
                MessageDigest digest = newDigest();
                long bytes = 0;
                int n;
                while ((n = zip.read(buffer)) != -1) {
                    if (cancelled.isCancelled()) throw new IOException("Backup-Prüfung abgebrochen");
                    bytes += n;
                    if (bytes > LIMIT_FILE || bytes > LIMIT_TOTAL - total)
                        throw new IOException("Backup-Prüfung: Größe überschritten");
                    digest.update(buffer, 0, n);
                }
                zip.closeEntry();
                total += bytes;
                actualSizes.put(name, bytes);
                actual.put(name, digestHex(digest.digest()));
                progress.onProgress(count, 0);
            }
        }
        if (manifestBytes == null || !actual.containsKey("index.json"))
            throw new IOException("Sicherungsmanifest oder Index fehlt");
        try {
            JSONObject manifest = new JSONObject(new String(manifestBytes, StandardCharsets.UTF_8));
            if (!FORMAT.equals(manifest.optString("format")) || manifest.optInt("version") != 1)
                throw new IOException("Unbekanntes Sicherungsformat");
            JSONArray expected = manifest.optJSONArray("files");
            if (expected == null || expected.length() != actual.size())
                throw new IOException("Dateienanzahl stimmt nicht");
            Set<String> listed = new HashSet<>();
            for (int i = 0; i < expected.length(); i++) {
                JSONObject file = expected.optJSONObject(i);
                if (file == null) throw new IOException("Manifestdatei fehlt");
                String name = file.optString("path");
                if (!listed.add(name) || !actual.containsKey(name)
                        || !actual.get(name).equals(file.optString("sha256"))
                        || actualSizes.get(name) != file.optLong("bytes", -1))
                    throw new IOException("Prüfsumme/Dateigröße falsch: " + name);
            }
            return new Report(count, manifest.optInt("active"), manifest.optInt("trash"),
                    manifest.optInt("historical_versions"),
                    manifest.optInt("missing_search_indexes"), total);
        } catch (JSONException malformed) {
            throw new IOException("Ungültiges Sicherungsmanifest", malformed);
        }
    }

    private ArchiveBundle() { }
}
