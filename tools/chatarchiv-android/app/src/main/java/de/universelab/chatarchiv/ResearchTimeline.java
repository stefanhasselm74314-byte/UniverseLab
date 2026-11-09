package de.universelab.chatarchiv;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Local, conservative comparison of explicitly keyed chat-status statements.
 * Later wording is a review candidate, not a verified project decision.
 */
final class ResearchTimeline {
    private static final Pattern KEY = Pattern.compile(
            "(?iu)(?<![\\p{L}\\p{N}_])(?:K\\d+-[A-Z0-9]{1,6}|K-2T\\.\\d+|"
                    + "Z\\d+[A-Z]?(?:[-._][A-Z0-9]+){1,6}|"
                    + "(?:SIM|MD)-\\d+[A-Z0-9_-]*|"
                    + "ULSH-[A-Z0-9]+(?:-[A-Z0-9]+)+)(?![\\p{L}\\p{N}_])");
    private static final Pattern OPEN = Pattern.compile(
            "(?iu)(?:\\bNOT[_ -]?(?:RELEASED|ADMISSIBLE|READY|CLOSED|DONE)\\b|"
                    + "\\b(?:NICHT|NOCH\\s+NICHT|NOT)\\s+"
                    + "(?:ERLEDIGT|ABGESCHLOSSEN|GESCHLOSSEN|FREIGEGEBEN|VALIDIERT)\\b|"
                    + "\\b(?:OFFEN|BLOCKIERT|UNGEKLÄRT|PENDING|REOPENED)\\b|"
                    + "\\bNICHT\\s+(?:NACHGEWIESEN|BELEGT|QUALIFIZIERT)\\b)");
    private static final Pattern CLOSED = Pattern.compile(
            "(?iu)\\b(?:RELEASED|ADMISSIBLE|CLOSED|DONE|PASSED|"
                    + "ERLEDIGT|ABGESCHLOSSEN|GESCHLOSSEN|FREIGEGEBEN|VALIDIERT)\\b");
    private static final Pattern CONDITIONAL = Pattern.compile(
            "(?iu)\\b(?:WÜRDE|WÜRDEN|WÄRE|KÖNNTE|KÖNNTEN|SOLLTE|VIELLEICHT|"
                    + "HYPOTHETISCH|BEISPIEL|ANGENOMMEN|FALLS)\\b");
    private static final Pattern DISPUTED = Pattern.compile(
            "(?iu)(?:\\bNICHT\\s+(?:BESTÄTIGT|GÜLTIG|BELEGT)\\b|\\bUNBESTÄTIGT\\b)");

    enum State { OPEN, CLOSED }

    static final class StatusEvidence {
        final String identifier;
        final State state;
        final String chatId;
        final String chatTitle;
        final int messageNumber;
        final String role;
        final double created;
        final String excerpt;

        StatusEvidence(String identifier, State state, String chatId, String chatTitle,
                int messageNumber, String role, double created, String excerpt) {
            this.identifier = identifier;
            this.state = state;
            this.chatId = chatId;
            this.chatTitle = chatTitle;
            this.messageNumber = messageNumber;
            this.role = role;
            this.created = created;
            this.excerpt = excerpt;
        }
    }

    static final class Review {
        final String code;
        final String summary;
        final String identifier;
        final StatusEvidence source;

        Review(String code, String summary, String identifier, StatusEvidence source) {
            this.code = code;
            this.summary = summary;
            this.identifier = identifier;
            this.source = source;
        }
    }

    private ResearchTimeline() { }

    /** Evidence is generated from imported visible messages, never a network source. */
    static List<StatusEvidence> collect(String chatId, String title,
            List<ConversationLogic.Message> messages) {
        List<StatusEvidence> events = new ArrayList<>();
        if (messages == null) return events;
        int lower = Math.max(0, messages.size() - 350);
        for (int i = lower; i < messages.size() && events.size() < 150; i++) {
            ConversationLogic.Message message = messages.get(i);
            if (message == null || message.body == null) continue;
            String body = message.body.length() > 120000
                    ? message.body.substring(message.body.length() - 120000) : message.body;
            for (String raw : body.split("\\R")) {
                if (events.size() >= 150) break;
                String line = raw.trim();
                // Very long data rows are not reliable standalone status statements.
                if (line.length() < 8 || line.length() > 1200) continue;
                Matcher matcher = KEY.matcher(line);
                List<int[]> ranges = new ArrayList<>();
                List<String> keys = new ArrayList<>();
                while (matcher.find() && keys.size() < 12) {
                    keys.add(matcher.group().toUpperCase(Locale.ROOT));
                    ranges.add(new int[] {matcher.start(), matcher.end()});
                }
                if (keys.isEmpty() || keys.size() == 12) continue;
                for (int n = 0; n < keys.size() && events.size() < 150; n++) {
                    int from = ranges.get(n)[1];
                    int to = n + 1 < keys.size() ? ranges.get(n + 1)[0] : line.length();
                    String clause = line.substring(from, Math.min(to, from + 180));
                    State state = status(clause);
                    if (state == null) continue;
                    String excerpt = line.length() > 260 ? line.substring(0, 257) + "…" : line;
                    events.add(new StatusEvidence(keys.get(n), state, chatId, title,
                            i + 1, message.role, message.created, excerpt));
                }
            }
        }
        return events;
    }

    private static State status(String text) {
        if (CONDITIONAL.matcher(text).find() || DISPUTED.matcher(text).find()) return null;
        if (OPEN.matcher(text).find()) return State.OPEN;
        if (CLOSED.matcher(text).find()) return State.CLOSED;
        return null;
    }

    private static String oneIdentifier(String text) {
        Matcher matcher = KEY.matcher(text);
        String selected = null;
        while (matcher.find()) {
            String candidate = matcher.group().toUpperCase(Locale.ROOT);
            if (selected != null && !selected.equals(candidate)) return null;
            selected = candidate;
        }
        return selected;
    }

    /** Only timestamped cross-chat statements or later entries in the SAME chat are comparable. */
    private static boolean after(ResearchFinder.Finding finding, StatusEvidence event) {
        if (finding.chatId.equals(event.chatId)) {
            return event.messageNumber > finding.messageNumber
                    && (finding.created <= 0 || event.created <= 0
                    || event.created >= finding.created);
        }
        return finding.created > 0 && event.created > finding.created;
    }

    private static boolean newer(StatusEvidence candidate, StatusEvidence current) {
        if (candidate.created > 0 && current.created > 0)
            return candidate.created > current.created;
        return candidate.chatId.equals(current.chatId)
                && candidate.messageNumber > current.messageNumber;
    }

    static Map<ResearchFinder.Finding, Review> reconcile(
            List<ResearchFinder.Finding> findings, List<StatusEvidence> events) {
        Map<String, List<StatusEvidence>> byId = new HashMap<>();
        for (StatusEvidence event : events)
            byId.computeIfAbsent(event.identifier, ignored -> new ArrayList<>()).add(event);

        Map<ResearchFinder.Finding, Review> reviews = new IdentityHashMap<>();
        for (ResearchFinder.Finding finding : findings) {
            String id = oneIdentifier(finding.excerpt);
            if (id == null) {
                reviews.put(finding, new Review("NO_ID",
                        "Keine eindeutige Aufgabenkennung: historischer Chat-Hinweis, "
                                + "kein automatisch bestätigter offener Projektpunkt.", null, null));
                continue;
            }
            StatusEvidence latest = null;
            for (StatusEvidence event : byId.getOrDefault(id, java.util.Collections.emptyList())) {
                if (!after(finding, event)) continue;
                if (latest == null || newer(event, latest)) latest = event;
            }
            if (latest == null) {
                reviews.put(finding, new Review("NO_LATER",
                        "Kein eindeutig zuordenbarer späterer Status im geprüften Chatbestand.",
                        id, null));
            } else if (latest.state == State.CLOSED) {
                reviews.put(finding, new Review("LATER_CLOSURE",
                        "Spätere Abschluss-/Freigabeaussage gefunden — "
                                + "Projektkanon und Nachweis weiterhin prüfen.", id, latest));
            } else {
                reviews.put(finding, new Review("LATER_OPEN",
                        "Spätere Offen-/Sperraussage gefunden — "
                                + "aktuellen Projektkanon weiterhin prüfen.", id, latest));
            }
        }
        return reviews;
    }
}
