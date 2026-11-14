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
        final String file;
        final long created;
        final String category;
        final String digest;
        final String originCategory;
        final long trashedAt;

        Entry(String id, String title, String file, long created, String category, String digest) {
            this(id, title, file, created, category, digest, "", 0);
        }

        Entry(String id, String title, String file, long created, String category, String digest,
              String originCategory, long trashedAt) {
            this.id = id;
            this.title = title;
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

        Entry moveToTrash(long when) {
            if (inTrash()) return this;
            return new Entry(id, title, file, created, TRASH, digest, category, when);
        }

        Entry restoreFromTrash() {
            if (!TRASH.equals(category)) throw new IllegalStateException("Chat nicht wiederherstellbar");
            String target = PROJECT.equals(originCategory) ? PROJECT : OTHER;
            return new Entry(id, title, file, created, target, digest);
        }

        Entry beginPermanentDeletion() {
            if (!inTrash()) throw new IllegalStateException("Chat muss im Papierkorb liegen");
            return new Entry(id, title, file, created, PURGE_PENDING, digest, originCategory, trashedAt);
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
                entries.put(id, new Entry(id, record.optString("title", "Ohne Titel"),
                        file, record.optLong("created", 0), category,
                        record.optString("digest", ""), origin, trashedAt));
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

    synchronized void setCategory(String id, String category) throws IOException {
        Entry previous = entries.get(id);
        if (previous == null || previous.inTrash()) return;
        if (!PROJECT.equals(category) && !OTHER.equals(category)) return;
        entries.put(id, new Entry(previous.id, previous.title, previous.file,
                previous.created, category, previous.digest));
        saveIndex();
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
            JSONObject manifest = new JSONObject();
            try {
                for (Entry record : records) categories.put(record.id, record.category);
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
        if (map == null) return;
        synchronized (this) {
            for (String id : result.newIds) {
                Entry previous = entries.get(id);
                if (previous == null) continue;
                String category = map.optString(id, "");
                if (!PROJECT.equals(category) && !OTHER.equals(category)) continue;
                entries.put(id, new Entry(id, previous.title, previous.file, previous.created,
                        category, previous.digest));
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
            entries.put(id, new Entry(id, title, fileName, created, category, digest));
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
            if (!term.isEmpty()) terms.add(new SearchTerm(
                    term.length() > 256 ? term.substring(0, 256) : term, titleOnly));
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

    private static boolean containsCompleteTerm(String lowerCaseText, String lowerCaseTerm) {
        int offset = 0;
        while ((offset = lowerCaseText.indexOf(lowerCaseTerm, offset)) >= 0) {
            int end = offset + lowerCaseTerm.length();
            boolean left = offset == 0 || !wordCodePoint(lowerCaseText.codePointBefore(offset));
            boolean right = end == lowerCaseText.length()
                    || !wordCodePoint(lowerCaseText.codePointAt(end));
            if (left && right) return true;
            offset++;
        }
        return false;
    }

    private static boolean anySearchTermMatches(String lowerCaseText, List<SearchTerm> terms) {
        for (SearchTerm term : terms)
            if (containsCompleteTerm(lowerCaseText, term.value)) return true;
        return false;
    }

    static List<Entry> search(List<Entry> items, String category, String phrase, Cancelled cancelled,
                              File privateConversationDirectory) {
        List<SearchTerm> terms = parseSearchTerms(phrase);
        boolean noQuery = phrase == null || phrase.trim().isEmpty();
        List<SearchTerm> contentTerms = new ArrayList<>();
        for (SearchTerm term : terms) if (!term.titleOnly) contentTerms.add(term);
        List<Entry> matching = new ArrayList<>();
        for (Entry item : items) {
            if (cancelled.isCancelled()) break;
            if (!"alle".equals(category) && !category.equals(item.category)) continue;
            if (noQuery) {
                matching.add(item);
                continue;
            }
            if (terms.isEmpty()) continue;
            String title = item.title.toLowerCase(Locale.ROOT);
            if (anySearchTermMatches(title, terms)) {
                matching.add(item);
                continue;
            }
            if (contentTerms.isEmpty()) continue;
            File searchable = new File(privateConversationDirectory, item.file.replace(".json", ".search"));
            try {
                if (fileContainsAny(searchable, contentTerms, cancelled)) matching.add(item);
            } catch (IOException ignored) {
                // An unreadable search index does not invalidate title matches in other chats.
            }
        }
        return matching;
    }

    File privateConversationDirectory() { return conversations; }

    private static boolean fileContainsAny(File file, List<SearchTerm> terms,
                                           Cancelled cancelled) throws IOException {
        if (!file.isFile()) return false;
        int longest = 0;
        for (SearchTerm term : terms) longest = Math.max(longest, term.value.length());
        try (BufferedReader reader = Files.newBufferedReader(file.toPath(), StandardCharsets.UTF_8)) {
            char[] block = new char[8192];
            String suffix = "";
            int n;
            while ((n = reader.read(block)) != -1) {
                if (cancelled.isCancelled()) return false;
                String chunk = suffix + new String(block, 0, n);
                String lower = chunk.toLowerCase(Locale.ROOT);
                if (anySearchTermMatches(lower, terms)) return true;
                // Keep a character before and after possible terms across block boundaries.
                int overlap = Math.min(chunk.length(), longest + 4);
                suffix = chunk.substring(chunk.length() - overlap);
            }
        }
        return false;
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
