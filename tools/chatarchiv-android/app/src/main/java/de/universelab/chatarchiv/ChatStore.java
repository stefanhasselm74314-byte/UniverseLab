package de.universelab.chatarchiv;

import android.content.Context;
import android.net.Uri;
import android.util.JsonReader;
import android.util.JsonToken;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
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
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/** Private, offline storage. This class never performs network operations. */
final class ChatStore {
    static final String PROJECT = "projekt";
    static final String OTHER = "andere";
    private static final DateTimeFormatter DATE = DateTimeFormatter.ofPattern("dd.MM.yyyy", Locale.GERMAN);

    static final class Entry {
        final String id;
        final String title;
        final String file;
        final long created;
        final String category;
        final String digest;

        Entry(String id, String title, String file, long created, String category, String digest) {
            this.id = id;
            this.title = title;
            this.file = file;
            this.created = created;
            this.category = category;
            this.digest = digest;
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
            return json;
        }
    }

    interface Progress {
        void onProgress(int imported, int updated, int unchanged);
    }

    interface Cancelled {
        boolean isCancelled();
    }

    static final class ImportResult {
        int imported;
        int updated;
        int unchanged;
        int failed;
        final List<String> errors = new ArrayList<>();

        String summary() {
            String output = "Neu: " + imported + " · Geändert: " + updated
                    + " · Bereits identisch: " + unchanged;
            if (failed > 0) output += " · Fehler: " + failed;
            if (!errors.isEmpty()) output += "\n" + errors.get(0);
            return output;
        }
    }

    private final Context context;
    private final File conversations;
    private final File index;
    private final Map<String, Entry> entries = new LinkedHashMap<>();

    ChatStore(Context context) throws IOException {
        this.context = context.getApplicationContext();
        conversations = new File(context.getFilesDir(), "conversations");
        if (!conversations.isDirectory() && !conversations.mkdirs()) {
            throw new IOException("Interner Speicher konnte nicht erstellt werden");
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
                entries.put(id, new Entry(id, record.optString("title", "Ohne Titel"),
                        file, record.optLong("created", 0), record.optString("category", OTHER),
                        record.optString("digest", "")));
            }
        } catch (JSONException exception) {
            throw new IOException("Gesprächsindex beschädigt: " + exception.getMessage(), exception);
        }
    }

    synchronized List<Entry> snapshot() {
        ArrayList<Entry> result = new ArrayList<>(entries.values());
        result.sort(Comparator.comparingLong((Entry item) -> item.created).reversed());
        return result;
    }

    synchronized void setCategory(String id, String category) throws IOException {
        Entry previous = entries.get(id);
        if (previous == null) return;
        if (!PROJECT.equals(category) && !OTHER.equals(category)) return;
        entries.put(id, new Entry(previous.id, previous.title, previous.file,
                previous.created, category, previous.digest));
        saveIndex();
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
                try (JsonReader reader = new JsonReader(new InputStreamReader(input, StandardCharsets.UTF_8))) {
                    if (reader.peek() != JsonToken.BEGIN_ARRAY) {
                        throw new IOException("Erwartet wird conversations-xxx.json mit JSON-Array");
                    }
                    reader.beginArray();
                    while (reader.hasNext()) {
                        if (Thread.currentThread().isInterrupted()) throw new IOException("Import unterbrochen");
                        Object value = readValue(reader, 0);
                        if (!(value instanceof JSONObject)) continue;
                        JSONObject conversation = (JSONObject) value;
                        String id = conversation.optString("id", "");
                        if (id.isEmpty() || conversation.optJSONObject("mapping") == null) continue;
                        ImportChange change = upsert(conversation, id);
                        if (change == ImportChange.UNCHANGED) result.unchanged++;
                        else if (change == ImportChange.UPDATED) result.updated++;
                        else result.imported++;
                        int total = result.imported + result.updated + result.unchanged;
                        if (total % 10 == 0) progress.onProgress(result.imported, result.updated, result.unchanged);
                    }
                    reader.endArray();
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

    private enum ImportChange { ADDED, UPDATED, UNCHANGED }

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
            if (previous != null && digest.equals(previous.digest)) return ImportChange.UNCHANGED;
        }
        String indexed = ConversationLogic.indexText(data);

        writeAtomic(new File(conversations, fileName), serialized);
        writeAtomic(new File(conversations, sha256(id) + ".search"), indexed);

        synchronized (this) {
            Entry previous = entries.get(id);
            String category = previous != null ? previous.category : categoryFromTitle(title);
            entries.put(id, new Entry(id, title, fileName, created, category, digest));
            return previous != null ? ImportChange.UPDATED : ImportChange.ADDED;
        }
    }

    private static String categoryFromTitle(String title) {
        String normalized = title.toLowerCase(Locale.ROOT);
        return normalized.matches("(?s).*(universelab|hyperzeit|hzt|hpvs|mond|brane|baryogenese).*")
                ? PROJECT : OTHER;
    }

    static List<Entry> search(List<Entry> items, String category, String phrase, Cancelled cancelled,
                              File privateConversationDirectory) {
        String query = phrase.trim().toLowerCase(Locale.ROOT);
        List<Entry> matching = new ArrayList<>();
        for (Entry item : items) {
            if (cancelled.isCancelled()) break;
            if (!"alle".equals(category) && !category.equals(item.category)) continue;
            if (query.isEmpty() || item.title.toLowerCase(Locale.ROOT).contains(query)) {
                matching.add(item);
                continue;
            }
            File searchable = new File(privateConversationDirectory, item.file.replace(".json", ".search"));
            try {
                if (fileContains(searchable, query, cancelled)) matching.add(item);
            } catch (IOException ignored) {
                // One unavailable index file must not prevent searching remaining chats.
            }
        }
        return matching;
    }

    File privateConversationDirectory() { return conversations; }

    private static boolean fileContains(File file, String needle, Cancelled cancelled) throws IOException {
        if (!file.isFile()) return false;
        try (BufferedReader reader = Files.newBufferedReader(file.toPath(), StandardCharsets.UTF_8)) {
            char[] block = new char[8192];
            String suffix = "";
            int n;
            while ((n = reader.read(block)) != -1) {
                if (cancelled.isCancelled()) return false;
                String chunk = suffix + new String(block, 0, n);
                if (chunk.toLowerCase(Locale.ROOT).contains(needle)) return true;
                int overlap = Math.min(chunk.length(), needle.length() + 3);
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
