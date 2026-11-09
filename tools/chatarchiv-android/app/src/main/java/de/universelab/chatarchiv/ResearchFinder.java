package de.universelab.chatarchiv;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.regex.Pattern;

/**
 * Conservative, offline-only discovery of *candidate* open work from visible chat text.
 * A finding is evidence of a statement in a chat, never proof that it is still open.
 */
final class ResearchFinder {
    private static final Pattern BLOCKED = Pattern.compile(
            "(?iu)\\b(?:BLOCKER|BLOCKIERT|NOT[_ -]?(?:RELEASED|ADMISSIBLE|READY))\\b");
    private static final Pattern CONFLICT = Pattern.compile(
            "(?iu)\\b(?:WIDERSPRUCH|INKONSISTENZ|KONFLIKT)\\b");
    private static final Pattern OPEN = Pattern.compile(
            "(?iu)(?:\\[\\s*OFFEN\\s*\\]|\\bOFFEN\\b|\\bUNGEKLÄRT\\b|\\bPENDING(?:_[A-Z]+)*\\b|"
                    + "\\bNICHT\\s+(?:NACHGEWIESEN|QUALIFIZIERT|BELEGT|VALIDIERT)\\b)");
    private static final Pattern NEXT = Pattern.compile(
            "(?iu)(?:\\bNÄCHSTER\\s+SCHRITT\\b|\\bNEXT\\s+STEP\\b|\\bTODO\\b|"
                    + "\\bNOCH\\s+ZU\\s+PRÜFEN\\b)");

    static final class Finding {
        final String chatId;
        final String chatTitle;
        final int messageNumber;
        final String role;
        final String excerpt;
        final String kind;
        final String field;
        final String question;
        final String verification;
        final int priority;

        Finding(String chatId, String chatTitle, int messageNumber, String role,
                String excerpt, String kind, String field, String question,
                String verification, int priority) {
            this.chatId = chatId;
            this.chatTitle = chatTitle;
            this.messageNumber = messageNumber;
            this.role = role;
            this.excerpt = excerpt;
            this.kind = kind;
            this.field = field;
            this.question = question;
            this.verification = verification;
            this.priority = priority;
        }
    }

    private ResearchFinder() { }

    static List<Finding> extract(String chatId, String chatTitle,
                                 List<ConversationLogic.Message> messages, int maxPerChat) {
        List<Finding> candidates = new ArrayList<>();
        if (maxPerChat <= 0 || messages == null) return candidates;
        Set<String> seen = new HashSet<>();
        // The latest 350 visible messages are the most relevant. Older claims may be superseded.
        int lower = Math.max(0, messages.size() - 350);
        // Collect more than we display: recent low-priority TODOs must not hide a
        // higher-priority blocker recorded a little earlier in the same chat.
        for (int i = messages.size() - 1; i >= lower && candidates.size() < 120; i--) {
            ConversationLogic.Message message = messages.get(i);
            if (message == null || message.body == null) continue;
            // Bound CPU and memory for unusually long exports; this is a screening pass.
            String body = message.body.length() > 120000
                    ? message.body.substring(message.body.length() - 120000) : message.body;
            int inMessage = 0;
            for (String rawLine : body.split("\\R")) {
                String line = clean(rawLine);
                if (line.length() < 18) continue;
                int priority = priority(line);
                if (priority == 0) continue;
                if (line.length() > 360) line = line.substring(0, 357) + "…";
                String key = line.toLowerCase(Locale.ROOT).replaceAll("\\s+", " ");
                if (!seen.add(key)) continue;

                String kind = priority >= 100 ? "Blocker" : priority >= 90 ? "Konflikt"
                        : priority >= 70 ? "Offener Punkt" : "Nächster Schritt";
                String field = field(line);
                candidates.add(new Finding(chatId, chatTitle, i + 1, message.role, line,
                        kind, field, question(kind), verification(field), priority));
                if (++inMessage >= 2 || candidates.size() >= 120) break;
            }
        }
        candidates.sort(Comparator.comparingInt((Finding f) -> f.priority).reversed()
                .thenComparing(Comparator.comparingInt((Finding f) -> f.messageNumber).reversed()));
        return candidates.size() > maxPerChat
                ? new ArrayList<>(candidates.subList(0, maxPerChat)) : candidates;
    }

    private static String clean(String source) {
        String line = source == null ? "" : source.trim();
        line = line.replaceAll("^[#*|>+\\-\\s]+", "");
        line = line.replace("**", "").replace("`", "");
        return line.trim();
    }

    private static int priority(String line) {
        if (BLOCKED.matcher(line).find()) return 100;
        if (CONFLICT.matcher(line).find()) return 90;
        if (OPEN.matcher(line).find()) return 70;
        if (NEXT.matcher(line).find()) return 50;
        return 0;
    }

    private static String field(String line) {
        String lower = line.toLowerCase(Locale.ROOT);
        if (lower.matches(".*(ghost|kinetik|nullmod|jacobi|wirkung|symmetrie|randbedingung).*"))
            return "Mathematik";
        if (lower.matches(".*(solver|fem|mesh|konvergenz|residual|simulation|numerisch).*"))
            return "Numerik";
        if (lower.matches(".*(desi|kids|euclid|sparc|beobachtung|messung|datenpunkt|kovarianz).*"))
            return "Empirie";
        if (lower.matches(".*(rotor|lager|reaktor|antrieb|thermik|werkstoff|eclss|schub).*"))
            return "Engineering";
        if (lower.matches(".*(archiv|datei|hash|quelle|provenienz|export).*"))
            return "Daten/Archiv";
        return "Allgemeine Prüfung";
    }

    private static String question(String kind) {
        if ("Konflikt".equals(kind)) return "Welche zwei Aussagen widersprechen sich, und welcher Beleg entscheidet?";
        if ("Nächster Schritt".equals(kind)) return "Wurde dieser Schritt inzwischen erledigt und nachvollziehbar geprüft?";
        return "Welche konkrete Bedingung müsste erfüllt sein, um diesen Punkt zu schließen?";
    }

    private static String verification(String field) {
        switch (field) {
            case "Mathematik":
                return "Definitionen und Annahmen → Herleitung → Dimensionen/Grenzfälle → Gegenbeispiel.";
            case "Numerik":
                return "Originalcode und Eingaben → reproduzierbarer Lauf → Konvergenz → unabhängiger Test.";
            case "Empirie":
                return "Messgröße und Datensatz → Unsicherheiten → Forward-Modell → Alternativerklärung.";
            case "Engineering":
                return "Lastfall und Schnittstelle → Energie-/Massenbilanz → Materialdaten → Nachweis.";
            case "Daten/Archiv":
                return "Originaldatei und Hash → Version/Quelle → Vollständigkeit → Freigabestatus.";
            default:
                return "Originalkontext lesen → aktuellen Status abgleichen → kleinstmöglichen Test definieren.";
        }
    }
}
