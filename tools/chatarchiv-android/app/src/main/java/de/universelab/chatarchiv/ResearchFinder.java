package de.universelab.chatarchiv;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Conservative, offline-only discovery of *candidate* open work from visible chat text.
 * A finding is evidence of a statement in a chat, never proof that it is still open.
 */
final class ResearchFinder {
    // Explicit status claims are stronger evidence than a mere mention of a column name.
    private static final Pattern BLOCKED = Pattern.compile(
            "(?iu)\\b(?:BLOCKIERT|NOT[_ -]?(?:RELEASED|ADMISSIBLE|READY))\\b");
    private static final Pattern BLOCKER_ASSIGNMENT = Pattern.compile(
            "(?iu)\\bBLOCKER\\s*[:=]\\s*(?!KEIN(?:E|EN|ER|ES)?\\b|NEIN\\b|0\\b|N/A\\b).{12,}");
    private static final Pattern BLOCKER_CLAIM = Pattern.compile(
            "(?iu)(?:\\b(?:IST|BLEIBT|WIRD)\\s+(?:EIN(?:E|EN)?\\s+)?BLOCKER\\b|"
                    + "\\bGILT\\s+ALS\\s+BLOCKER\\b|\\bBLOCKER\\s+BESTEHT\\b)");
    private static final Pattern NEGATED_BLOCKER = Pattern.compile(
            "(?iu)(?:\\b(?:KEIN(?:E|EN|ER|ES)?|OHNE)\\s+(?:AKTUELLE[NMR]?\\s+)?"
                    + "(?:BLOCKER|BLOCKADE|BLOCKIERUNG)\\b|\\bNICHT\\s+BLOCKIERT\\b|"
                    + "\\bBLOCKER\\s*(?:/\\s*ABHÄNGIGKEIT)?\\s*[:=]\\s*"
                    + "(?:KEIN(?:E|EN|ER|ES)?|NEIN|0|N/A)\\b)");
    private static final Pattern CONFLICT = Pattern.compile(
            "(?iu)(?:\\[\\s*(?:WIDERSPRUCH|KONFLIKT|INKONSISTENZ)\\s*\\]|"
                    + "\\b(?:WIDERSPRUCH|INKONSISTENZ|KONFLIKT)\\s*[:=]|\\bWIDERSPRICHT\\b)");
    private static final Pattern NEGATED_CONFLICT = Pattern.compile(
            "(?iu)(?:\\b(?:KEIN(?:E|EN|ER|ES)?|OHNE)\\s+(?:MATERIELLE[NMR]?\\s+)?"
                    + "(?:WIDERSPRUCH|INKONSISTENZ|KONFLIKT)\\b|\\bWIDERSPRUCHSFREI\\b)");
    // Only a technical assertion, not a courteous hypothetical disagreement,
    // should be recorded as a candidate contradiction.
    private static final Pattern EXPLICIT_CONFLICT = Pattern.compile(
            "(?iu)(?:\\[\\s*(?:WIDERSPRUCH|KONFLIKT|INKONSISTENZ)\\s*\\]|"
                    + "\\b(?:WIDERSPRUCH|INKONSISTENZ|KONFLIKT)\\s*[:=])");
    private static final Pattern POLITE_HYPOTHETICAL = Pattern.compile(
            "(?iu)\\b(?:FALLS|WENN|SOFERN)\\b.{0,180}"
                    + "\\b(?:DEIN\\p{L}*|MEIN\\p{L}*|IHR\\p{L}*|UNSER\\p{L}*)\\b"
                    + ".{0,75}\\b(?:MEINUNG|ANSICHT|EINSCHÄTZUNG)\\b"
                    + ".{0,60}\\bWIDERSPRICHT\\b");
    private static final Pattern NEGATED_VERBAL_CONFLICT = Pattern.compile(
            "(?iu)\\bWIDERSPRICHT\\b[^.,!?;:]{0,75}\\bNICHT\\b(?!\\s+NUR\\b)");
    private static final Pattern SECTION_PLACEHOLDER = Pattern.compile(
            "(?iu)^(?:\\d+(?:\\.\\d+){0,4}\\.?\\s+)?(?:NOCH\\s+)?OFFEN"
                    + "(?:\\s*[/|–—-]\\s*(?:SPÄTERE[RNS]?\\s+)?"
                    + "(?:AUSBAU|FORTSETZUNG|ERGÄNZUNG))?\\s*\\.?$");
    private static final Pattern EMPTY_OPEN_HEADING = Pattern.compile(
            "(?iu)^(?:\\d+(?:\\.\\d+){0,4}\\.?\\s+)?"
                    + "(?:WAS\\s+)?(?:NOCH\\s+)?OFFEN"
                    + "(?:\\s+IST|\\s+FÜR\\s+DIE\\s+NÄCHSTE\\s+STUFE"
                    + "|\\s+PUNKTE)?\\s*[:.!?]?$");
    private static final Pattern FIELD_LIST = Pattern.compile(
            "(?iu)(?:\\bTASK[-_ ]?ID\\s*,[^:=]{0,120}\\bBLOCKER\\b|"
                    + "\\b(?:FELDER|SCHEMA|VORLAGE|TEMPLATE|CHECKLISTE)\\b[^:=]{0,120}"
                    + "\\b(?:BLOCKER|WIDERSPRUCH|TODO)\\b)");
    private static final Pattern OPEN = Pattern.compile(
            "(?iu)(?:\\[\\s*OFFEN\\s*\\]|\\bUNGEKLÄRT\\b|\\bPENDING(?:_[A-Z]+)*\\b|"
                    + "\\bNICHT\\s+(?:NACHGEWIESEN|QUALIFIZIERT|BELEGT|VALIDIERT)\\b|"
                    + "\\b(?:BLEIBT|IST|NOCH|WEITERHIN)\\s+OFFEN\\b|\\bOFFEN\\s*[:=])");
    private static final Pattern NEXT = Pattern.compile(
            "(?iu)(?:\\bNÄCHSTER\\s+SCHRITT\\s*[:=]|\\bNEXT\\s+STEP\\s*[:=]|"
                    + "(?:^|\\[)\\s*TODO\\s*[:=\\]]|"
                    + "\\bNOCH\\s+ZU\\s+PRÜFEN\\b)");

    private static final class Signal {
        final int start;
        final int end;
        final String label;

        Signal(int start, int end, String label) {
            this.start = start;
            this.end = end;
            this.label = label;
        }
    }

    static final class Finding {
        final String chatId;
        final String chatTitle;
        final int messageNumber;
        final String role;
        final String excerpt;
        final String displayExcerpt;
        final String signal;
        final String kind;
        final String field;
        final String scope;
        final String question;
        final String verification;
        final int priority;
        final double created;

        Finding(String chatId, String chatTitle, int messageNumber, String role,
                String excerpt, String displayExcerpt, String signal, String kind,
                String field, String scope, String question, String verification,
                int priority, double created) {
            this.chatId = chatId;
            this.chatTitle = chatTitle;
            this.messageNumber = messageNumber;
            this.role = role;
            this.excerpt = excerpt;
            this.displayExcerpt = displayExcerpt;
            this.signal = signal;
            this.kind = kind;
            this.field = field;
            this.scope = scope;
            this.question = question;
            this.verification = verification;
            this.priority = priority;
            this.created = created;
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
                String sourceLine = clean(rawLine);
                if (sourceLine.length() < 18) continue;
                int priority = priority(sourceLine);
                if (priority == 0) continue;
                Signal signal = signalFor(sourceLine, priority);
                String excerpt = sourceLine.length() > 360
                        ? sourceLine.substring(0, 357) + "…" : sourceLine;
                String displayExcerpt = evidenceWindow(sourceLine, signal);
                String key = excerpt.toLowerCase(Locale.ROOT).replaceAll("\\s+", " ")
                        + " | " + signal.label.toLowerCase(Locale.ROOT);
                if (!seen.add(key)) continue;

                String kind = priority >= 100 ? "Blocker" : priority >= 90 ? "Konflikt"
                        : priority >= 70 ? "Offener Punkt" : "Nächster Schritt";
                String field = field(excerpt);
                String scope = ResearchScope.classify(chatTitle,
                        displayExcerpt + " " + excerpt, field);
                candidates.add(new Finding(chatId, chatTitle, i + 1, message.role,
                        excerpt, displayExcerpt, signal.label, kind, field, scope,
                        question(kind), verification(field), priority, message.created));
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

    static boolean isGenericOutline(String line) {
        if (line == null) return false;
        String cleaned = clean(line);
        return SECTION_PLACEHOLDER.matcher(cleaned).matches()
                || EMPTY_OPEN_HEADING.matcher(cleaned).matches();
    }

    static boolean isConversationalNonConflict(String line) {
        if (line == null || EXPLICIT_CONFLICT.matcher(line).find()) return false;
        return POLITE_HYPOTHETICAL.matcher(line).find()
                || NEGATED_VERBAL_CONFLICT.matcher(line).find();
    }

    /** Identify the literal keyword that caused the heuristic candidate. */
    private static Signal signalFor(String line, int priority) {
        Pattern[] patterns = priority >= 100
                ? new Pattern[] {BLOCKED, BLOCKER_ASSIGNMENT, BLOCKER_CLAIM}
                : priority >= 90 ? new Pattern[] {CONFLICT}
                : priority >= 70 ? new Pattern[] {OPEN}
                : new Pattern[] {NEXT};
        Signal earliest = null;
        for (Pattern pattern : patterns) {
            Matcher match = pattern.matcher(line);
            if (!match.find()) continue;
            String token = pattern == BLOCKER_ASSIGNMENT ? "BLOCKER:"
                    : match.group().trim();
            if (token.length() > 72) token = token.substring(0, 69) + "…";
            if (earliest == null || match.start() < earliest.start) {
                earliest = new Signal(match.start(), match.end(), token);
            }
        }
        return earliest == null ? new Signal(0, 0, "Regel nicht bestimmbar") : earliest;
    }

    /** Expose a late trigger without changing the archived quote used for chronology. */
    private static String evidenceWindow(String fullLine, Signal signal) {
        if (fullLine.length() <= 360) return fullLine;
        if (signal.start < 280) return fullLine.substring(0, 357) + "…";
        int from = Math.max(0, signal.start - 90);
        int to = Math.min(fullLine.length(), from + 350);
        if (to < signal.end) {
            to = Math.min(fullLine.length(), signal.end + 100);
            from = Math.max(0, to - 350);
        }
        return (from > 0 ? "… " : "") + fullLine.substring(from, to)
                + (to < fullLine.length() ? " …" : "");
    }

    private static int priority(String line) {
        // Lists of field names (e.g. "Task-ID, Quelle, Blocker, Rückgaberoute")
        // document a template, not an unresolved research issue.
        if (FIELD_LIST.matcher(line).find() || isGenericOutline(line)) return 0;
        if (!NEGATED_BLOCKER.matcher(line).find()
                && (BLOCKED.matcher(line).find() || BLOCKER_ASSIGNMENT.matcher(line).find()
                || BLOCKER_CLAIM.matcher(line).find())) return 100;
        if (!NEGATED_CONFLICT.matcher(line).find()
                && !isConversationalNonConflict(line) && CONFLICT.matcher(line).find()) return 90;
        if (OPEN.matcher(line).find()) return 70;
        if (NEXT.matcher(line).find()) return 50;
        return 0;
    }

    private static String field(String line) {
        String lower = line.toLowerCase(Locale.ROOT);
        if (lower.matches(".*(governance|freigabe|not[_ -]?(released|admissible|ready)|"
                + "projektkanon|entscheidungsprotokoll|gate[- _]|k1-[de]).*"))
            return "Governance";
        if (lower.matches(".*(ghost|kinetik|nullmod|jacobi|wirkung|symmetrie|randbedingung).*"))
            return "Mathematik";
        if (lower.matches(".*(radion|brane|moden|gravit|kk[- _]|geometrie|fünfte kraft).*"))
            return "Physikalisches Modell";
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
            case "Governance":
                return "Kanonischen Status prüfen → Freigabebedingung → aktuellen Beleg → Entscheidung.";
            case "Mathematik":
                return "Definitionen und Annahmen → Herleitung → Dimensionen/Grenzfälle → Gegenbeispiel.";
            case "Physikalisches Modell":
                return "Freiheitsgrade und Annahmen → Dynamik → Grenzfälle → beobachtbarer Test.";
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

/**
 * Only a navigational guess based on wording, never a verified research status.
 * Areas do not affect which findings are retained or the priority of a finding.
 */
final class ResearchScope {
    static final String PHYSICS = "Physik/Mathematik";
    static final String GOVERNANCE = "Governance/Freigabe";
    static final String ORGANIZATION = "Organisation/Prozess";
    static final String DOCUMENTATION = "Dokumentation/Redaktion";
    static final String SOFTWARE = "Software/Archiv";
    static final String ENGINEERING = "Engineering";
    static final String UNCLEAR = "Unklar/Gemischt";

    static final String[] FILTERS = {
            "Alle Bereiche", PHYSICS, GOVERNANCE, ORGANIZATION,
            DOCUMENTATION, SOFTWARE, ENGINEERING, UNCLEAR
    };

    private static final Pattern GOVERNANCE_CUE = Pattern.compile(
            "(?iu)(?:\\bK1[-_][DE]\\b|\\bNOT[_ -]?(?:RELEASED|ADMISSIBLE|READY)\\b|"
                    + "\\bGOVERNANCE\\b|\\bFREIGABESPERRE\\b|\\bFREIGABEGATE\\b)");
    private static final Pattern ORGANIZATION_CUE = Pattern.compile(
            "(?iu)\\b(?:EINREICHUNG|ANTRAG|FORMULAR|REGISTRIERUNG|TERMINPLAN|"
                    + "PROJEKTBOARD)\\b");
    private static final Pattern DOCUMENTATION_CUE = Pattern.compile(
            "(?iu)(?:\\b(?:TAFEL|KAPITEL)\\s+\\d+\\b|"
                    + "\\b(?:WORD|DOCX|POWERPOINT|PRÄSENTATION|GLIEDERUNG|"
                    + "POSTER|LAYOUT|FORMATIERUNG|ABBILDUNG|REDAKTION|"
                    + "LEKTORAT|DRUCKAUFTRAG|AUSHANG)\\b)");
    private static final Pattern SUBSTANTIVE_PHYSICS_CUE = Pattern.compile(
            "(?iu)\\b(?:GHOSTFREIHEIT|NULLMODEN?|RANDBEDINGUNGEN?|"
                    + "EICHINVARIANZ|KOPPLUNG|GLEICHUNGEN?|ASYMPTOTIK|"
                    + "HERLEITUNG|BEWEIS|FALSIFIKATION|KOVARIANZ)\\b");
    private static final Pattern SOFTWARE_CUE = Pattern.compile(
            "(?iu)\\b(?:APK|ANDROID|GITHUB|HTML|CSS|JAVASCRIPT|SOFTWARE|"
                    + "IMPORT|EXPORT|ZIP|ARCHIV|CACHE|SCROLLBALKEN|BENUTZEROBERFLÄCHE)\\b");
    private static final Pattern ENGINEERING_CUE = Pattern.compile(
            "(?iu)\\b(?:ECLSS|WERKSTOFF|RESONATOR|REAKTOR|ROTOR|LAGER|SCHUB|THERMIK)\\b");
    private static final Pattern PHYSICS_CUE = Pattern.compile(
            "(?iu)(?:\\b(?:HZT|HPVS|MOND|SPARC|DESI|KIDS|EUCLID|"
                    + "GHOSTFREIHEIT|GRAVITATION|NULLMODE|NULLMODEN|"
                    + "BARYOGENESE|KK[-_ ]?MODEN|BRANE|RADION|"
                    + "KOSMOLOGIE|HYPERZEIT)\\b|\\b6D\\b)");

    private ResearchScope() { }

    static String classify(String chatTitle, String excerpt, String field) {
        String line = excerpt == null ? "" : excerpt;
        String title = chatTitle == null ? "" : chatTitle;
        // Workflow actions may occur in otherwise scientific conversations:
        // the excerpt takes precedence over the chat's project title.
        if ("Governance".equals(field) || GOVERNANCE_CUE.matcher(line).find()) {
            return GOVERNANCE;
        }
        if (ORGANIZATION_CUE.matcher(line).find()) {
            return ORGANIZATION;
        }
        if (DOCUMENTATION_CUE.matcher(line).find()
                && !SUBSTANTIVE_PHYSICS_CUE.matcher(line).find()) {
            return DOCUMENTATION;
        }
        if ("Daten/Archiv".equals(field) || SOFTWARE_CUE.matcher(line).find()) {
            return SOFTWARE;
        }
        if ("Engineering".equals(field) || ENGINEERING_CUE.matcher(line).find()) {
            return ENGINEERING;
        }
        if ("Mathematik".equals(field) || "Physikalisches Modell".equals(field)
                || "Numerik".equals(field) || "Empirie".equals(field)
                || PHYSICS_CUE.matcher(line).find() || PHYSICS_CUE.matcher(title).find()) {
            return PHYSICS;
        }
        return UNCLEAR;
    }
}
