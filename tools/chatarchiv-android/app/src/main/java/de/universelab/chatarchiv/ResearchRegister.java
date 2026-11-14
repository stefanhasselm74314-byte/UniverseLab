package de.universelab.chatarchiv;

import android.content.Context;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Locally curated research references, separate from heuristic discovery.
 * Nothing stored here establishes the truth of a scientific assertion.
 * No network, ChatGPT account access, or changes to source conversations.
 */
final class ResearchRegister {
    static final String FILE_NAME = "research-register.json";
    static final String[] STAGES = {"Nicht zugeordnet", "HPVS", "HZT-M0", "HZT-Full", "Übergreifend"};
    static final String[] STATES = {
            "Unbewertet", "Offen", "In Prüfung", "Zurückgestellt", "Abgeschlossen (manuell)"
    };
    private static final String FORMAT = "universelab-research-register";
    private static final int MAX_ENTRIES = 5000;
    private static final long MAX_JSON_BYTES = 16L * 1024 * 1024;

    static final class Record {
        final String id;
        final String chatId;
        final String chatTitle;
        final int messageNumber;
        final String role;
        final String excerpt;
        final String kind;
        final String stage;
        final String state;
        final String note;
        final long createdAt;
        final long updatedAt;

        Record(String id, String chatId, String chatTitle, int messageNumber, String role,
               String excerpt, String kind, String stage, String state, String note,
               long createdAt, long updatedAt) {
            this.id = id;
            this.chatId = chatId;
            this.chatTitle = chatTitle;
            this.messageNumber = messageNumber;
            this.role = role;
            this.excerpt = excerpt;
            this.kind = kind;
            this.stage = stage;
            this.state = state;
            this.note = note;
            this.createdAt = createdAt;
            this.updatedAt = updatedAt;
        }

        Record withReview(String nextStage, String nextState, String nextNote) {
            return new Record(id, chatId, chatTitle, messageNumber, role, excerpt, kind,
                    nextStage, nextState, nextNote, createdAt, System.currentTimeMillis());
        }

        JSONObject toJson() throws JSONException {
            return new JSONObject()
                    .put("id", id).put("chat_id", chatId).put("chat_title_snapshot", chatTitle)
                    .put("message_number", messageNumber).put("role", role)
                    .put("excerpt", excerpt).put("kind", kind)
                    .put("stage", stage).put("state", state).put("note", note)
                    .put("created_at", createdAt).put("updated_at", updatedAt);
        }

        static Record fromJson(JSONObject data) throws IOException {
            if (data == null) throw new IOException("Leerer Forschungseintrag");
            String id = data.optString("id", "");
            String chatId = data.optString("chat_id", "");
            String stage = data.optString("stage", "");
            String state = data.optString("state", "");
            String note = data.optString("note", "");
            int message = data.optInt("message_number", 0);
            if (!id.matches("[0-9a-f]{64}") || chatId.isEmpty() || message <= 0
                    || !validChoice(STAGES, stage) || !validChoice(STATES, state)
                    || note.length() > 2000)
                throw new IOException("Ungültiger Forschungseintrag");
            return new Record(id, chatId, data.optString("chat_title_snapshot", ""), message,
                    data.optString("role", ""), data.optString("excerpt", ""),
                    data.optString("kind", ""), stage, state, note,
                    Math.max(0, data.optLong("created_at", 0)),
                    Math.max(0, data.optLong("updated_at", 0)));
        }
    }

    private final File file;
    private final Map<String, Record> records = new LinkedHashMap<>();

    ResearchRegister(Context context) throws IOException {
        file = new File(context.getFilesDir(), FILE_NAME);
        load();
    }

    synchronized List<Record> snapshot() {
        List<Record> result = new ArrayList<>(records.values());
        result.sort(Comparator.comparingLong((Record r) -> r.updatedAt).reversed());
        return result;
    }

    synchronized Record get(String id) { return records.get(id); }

    synchronized Record addFinding(ResearchFinder.Finding finding, String stage,
                                   String state, String note) throws IOException {
        if (finding == null || finding.chatId == null || finding.chatId.isEmpty()
                || finding.messageNumber <= 0)
            throw new IOException("Fundstelle nicht eindeutig identifiziert");
        validateReview(stage, state, note);
        String id = idForFinding(finding);
        Record former = records.get(id);
        if (former == null && records.size() >= MAX_ENTRIES)
            throw new IOException("Forschungsregister ist auf 5000 Einträge begrenzt");
        long time = System.currentTimeMillis();
        Record next = new Record(id, finding.chatId, limit(finding.chatTitle, 180),
                finding.messageNumber, limit(finding.role, 30), limit(finding.excerpt, 700),
                limit(finding.kind, 80), stage, state, note,
                former == null ? time : former.createdAt, time);
        records.put(id, next);
        try { persist(); }
        catch (IOException error) {
            if (former == null) records.remove(id);
            else records.put(id, former);
            throw error;
        }
        return next;
    }

    synchronized void updateReview(String id, String stage, String state, String note) throws IOException {
        validateReview(stage, state, note);
        Record former = records.get(id);
        if (former == null) throw new IOException("Registereintrag nicht gefunden");
        records.put(id, former.withReview(stage, state, note));
        try { persist(); }
        catch (IOException error) { records.put(id, former); throw error; }
    }

    synchronized void remove(String id) throws IOException {
        Record former = records.get(id);
        if (former == null) throw new IOException("Registereintrag nicht gefunden");
        records.remove(id);
        try { persist(); }
        catch (IOException error) { records.put(id, former); throw error; }
    }

    static String idForFinding(ResearchFinder.Finding finding) {
        return fingerprint(finding.chatId + "\n" + finding.messageNumber
                + "\n" + finding.kind + "\n" + finding.signal);
    }

    static void validateReview(String stage, String state, String note) throws IOException {
        if (!validChoice(STAGES, stage) || !validChoice(STATES, state))
            throw new IOException("Ungültige Forschungsstufe oder Bearbeitungsstatus");
        if (note == null || note.length() > 2000)
            throw new IOException("Notiz darf höchstens 2000 Zeichen lang sein");
    }

    private static boolean validChoice(String[] choices, String value) {
        for (String choice : choices) if (choice.equals(value)) return true;
        return false;
    }

    static String fingerprint(String content) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256")
                    .digest(content.getBytes(StandardCharsets.UTF_8));
            StringBuilder hex = new StringBuilder(64);
            for (byte value : digest)
                hex.append(String.format(java.util.Locale.ROOT, "%02x", value & 0xff));
            return hex.toString();
        } catch (NoSuchAlgorithmException error) { throw new AssertionError(error); }
    }

    private static String limit(String source, int length) {
        if (source == null) return "";
        return source.length() <= length ? source : source.substring(0, length);
    }

    private void load() throws IOException {
        if (!file.isFile()) return;
        if (file.length() > MAX_JSON_BYTES) throw new IOException("Forschungsregister zu groß");
        try {
            JSONObject root = new JSONObject(new String(Files.readAllBytes(file.toPath()),
                    StandardCharsets.UTF_8));
            if (!FORMAT.equals(root.optString("format")) || root.optInt("version") != 1)
                throw new IOException("Forschungsregister: unbekanntes Format");
            JSONArray list = root.optJSONArray("entries");
            if (list == null || list.length() > MAX_ENTRIES)
                throw new IOException("Forschungsregister: ungültige Eintragsanzahl");
            for (int i = 0; i < list.length(); i++) {
                Record record = Record.fromJson(list.optJSONObject(i));
                if (records.put(record.id, record) != null)
                    throw new IOException("Doppelter Registereintrag: " + record.id);
            }
        } catch (JSONException invalid) {
            throw new IOException("Forschungsregister beschädigt", invalid);
        }
    }

    private void persist() throws IOException {
        JSONArray rows = new JSONArray();
        try {
            for (Record row : records.values()) rows.put(row.toJson());
            JSONObject root = new JSONObject()
                    .put("format", FORMAT).put("version", 1).put("entries", rows);
            byte[] bytes = root.toString().getBytes(StandardCharsets.UTF_8);
            if (bytes.length > MAX_JSON_BYTES)
                throw new IOException("Forschungsregister überschreitet 16 MiB");
            File pending = new File(file.getParentFile(), FILE_NAME + ".tmp");
            Files.write(pending.toPath(), bytes);
            try {
                Files.move(pending.toPath(), file.toPath(),
                        StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
            } catch (AtomicMoveNotSupportedException unsupported) {
                Files.move(pending.toPath(), file.toPath(), StandardCopyOption.REPLACE_EXISTING);
            }
        } catch (JSONException malformed) {
            throw new IOException("Registereintrag nicht serialisierbar", malformed);
        }
    }
}
