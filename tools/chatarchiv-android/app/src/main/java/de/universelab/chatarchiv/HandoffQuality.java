package de.universelab.chatarchiv;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Handoff-only screening. All decisions are heuristics; original chats and the
 * Research Navigator's findings remain unchanged.
 */
final class HandoffQuality {
    enum Scope {
        PHYSICS("6D-Physik"), SOFTWARE("Software/UniverseLab"),
        ENGINEERING("Engineering"), ALL("Alle Bereiche");

        final String label;
        Scope(String label) { this.label = label; }
    }

    private static final Pattern EMPTY_FIELD = Pattern.compile(
            "(?iu)^(?:GENAU\\s+)?(?:NÄCHSTER\\s+SCHRITT|NEXT\\s+STEP|"
                    + "BLOCKER(?:\\s*/\\s*ABHÄNGIGKEIT)?|RÜCKGABE\\s+AN|"
                    + "TASK[-_ ]?ID|LIEFEROBJEKT)\\s*[:=]\\s*(?:[-–—.]|\\[\\s*\\])?\\s*$");
    private static final Pattern BARE_TABLE = Pattern.compile(
            "(?iu)^.{2,85}\\|\\s*(?:\\*|\\[|\\s)*(?:(?:WEITERHIN|NOCH)\\s+)?"
                    + "(?:BLOCKIERT|OFFEN|NOT[_ -]?(?:RELEASED|ADMISSIBLE|READY))"
                    + "(?:\\s*/\\s*(?:OFFEN|BLOCKIERT))?\\s*(?:\\]|\\*|\\s)*\\|?\\s*$");
    private static final Pattern CODE_OFFER = Pattern.compile(
            "(?iu)^(?:NÄCHSTER\\s+SCHRITT|NEXT\\s+STEP)\\s*[:=]\\s*"
                    + "(?:ICH\\s+(?:KANN|KÖNNTE|WÜRDE|WERDE\\s+DIR)|"
                    + "WENN\\s+DU\\s+(?:WILLST|MÖCHTEST))\\b");
    private static final Pattern GATE_ECHO = Pattern.compile(
            "(?iu)\\bK1-[DE]\\b.{0,100}\\b(?:NOT[_ -]?(?:RELEASED|ADMISSIBLE)|"
                    + "NICHT\\s+FREIGEGEBEN|BLOCKIERT)\\b");
    private static final Pattern TASK_ID = Pattern.compile(
            "(?iu)(?<![\\p{L}\\p{N}_])(?:K\\d+-[A-Z0-9]{1,6}|K-2T\\.\\d+|"
                    + "Z\\d+[A-Z]?(?:[-._][A-Z0-9]+){1,6}|"
                    + "(?:SIM|MD)-\\d+[A-Z0-9_-]*|ULSH-[A-Z0-9]+(?:-[A-Z0-9]+)+)"
                    + "(?![\\p{L}\\p{N}_])");

    private HandoffQuality() { }

    static List<ResearchFinder.Finding> screen(List<ResearchFinder.Finding> raw,
            List<ConversationLogic.Message> visible, Scope scope, int maximum) {
        if (raw == null || maximum <= 0) return Collections.emptyList();
        List<ResearchFinder.Finding> result = new ArrayList<>();
        for (ResearchFinder.Finding f : raw) {
            if (f == null || (scope != Scope.ALL && classify(f) != scope)) continue;
            if (falsePositive(f) || inCodeExample(f, visible)) continue;
            result.add(f);
            if (result.size() >= maximum) break;
        }
        return result;
    }

    /** A classification of the cited task, not of the scientific truth of a chat. */
    static Scope classify(ResearchFinder.Finding f) {
        String title = lower(f.chatTitle);
        String text = lower(f.excerpt + " " + f.field);
        // Explicitly non-physics source chats take precedence over incidental HZT mentions.
        if (has(title, "medien designer", "raumschiff", "antriebs", "engineering",
                "schiffsplanung", "bauplan", "raumfahrttechnik")) return Scope.ENGINEERING;
        if (has(title, "tagesmonitor", "chatarchiv", "chat archiv", "website",
                "webseite", "portal", "software", "github", "programmierung",
                "app-entwicklung", "browser", "dashboard",
                "forschungsplattform", "forschungsaufbau", "überwachung",
                "chat audit worker")) return Scope.SOFTWARE;
        if (has(text, "rotor", "reaktor", "schubkraft", "schubsystem",
                "fan-web", "rootblock", "taper", "eclss", "engineeringgeometrie",
                "hzt-last", "antrieb", "triebwerk", "werkstoff")) {
            return Scope.ENGINEERING;
        }
        if (has(text, "android", "quellcode", "browser", "scrollbalken",
                "css", "javascript", "webseite", "app-modul", "frontend", "html",
                "export-datei", "importfunktion", "cache", "deployment",
                "github actions", "ci pipeline", "chatarchiv", "scanner",
                "connector", "pr-aufruf", "pull request", "im branch")) return Scope.SOFTWARE;
        return Scope.PHYSICS;
    }

    static boolean falsePositive(ResearchFinder.Finding f) {
        String quote = f.excerpt == null ? "" : f.excerpt.trim();
        String q = lower(quote);
        if (EMPTY_FIELD.matcher(quote).matches() || BARE_TABLE.matcher(quote).matches()
                || CODE_OFFER.matcher(quote).find()
                || ResearchFinder.isGenericOutline(quote)
                || ("Konflikt".equals(f.kind)
                        && ResearchFinder.isConversationalNonConflict(quote))) return true;
        if (q.matches("(?s)^(?:genau\\s+)?(?:nächster schritt|next step)\\s*[:=]\\s*$"))
            return true;
        // Repeated gate labels belong in the source-hierarchy context, not as
        // multiple newly discovered research problems.
        // LaTeX may split gate identifiers across \mathrm{K1\-D}, etc.
        // Normalize only for screening of bare gate-status echoes.
        String compact = q.replace("\\texttt", "").replace("\\text", "")
                .replace("\\mathrm", "").replace("\\boxed", "")
                .replaceAll("[^a-z0-9]+", "");
        boolean latexGate = (compact.contains("k1d") || compact.contains("k1e"))
                && (compact.contains("notreleased") || compact.contains("notadmissible"));
        if ((GATE_ECHO.matcher(quote).find() || latexGate)
                && !has(q, "nullmod", "ghost", "herleitung", "beweis",
                        "falsifikation", "radion", "kovarianz", "forward map"))
            return true;
        // A primer's statement about what cosmology does not yet explain is
        // not necessarily an actual UniverseLab work order.
        if (q.contains("ungeklärt") && !has(q, "[offen]", "noch zu prüfen",
                "hzt-", "6d-", "universelab", "nullmod", "radion", "ghost",
                "freigabe", "task-id", "todo:", "nächster schritt"))
            return true;
        if ("Konflikt".equals(f.kind)
                && has(q, "kosmologische konstante", "kosmologischen konstante")
                && !has(q, "hzt-", "6d-", "universelab", "unser modell"))
            return true;
        return false;
    }

    private static boolean inCodeExample(ResearchFinder.Finding f,
            List<ConversationLogic.Message> visible) {
        if (visible == null || f.messageNumber < 1 || f.messageNumber > visible.size())
            return false;
        ConversationLogic.Message message = visible.get(f.messageNumber - 1);
        if (message == null || message.body == null) return false;
        String target = normalized(f.excerpt);
        if (target.isEmpty()) return false;
        String needle = target.substring(0, Math.min(65, target.length()));
        boolean fence = false;
        boolean generatedReadme = false;
        for (String line : message.body.split("\\R")) {
            String trim = line.trim();
            if ((trim.length() >= 3 && trim.charAt(0) == 96
                    && trim.charAt(1) == 96 && trim.charAt(2) == 96)
                    || trim.startsWith("~~~")) {
                fence = !fence;
                continue;
            }
            if (has(lower(trim), "readme = dedent(", "readme=dedent(",
                    "readme = textwrap.dedent(") && trim.contains("\"\"\""))
                generatedReadme = true;
            boolean matched = normalized(line).startsWith(needle);
            if (matched && (fence || generatedReadme
                    || trim.matches("(?i)^(?:#\\s*)?(?:print|return|assert)\\s*\\(.*")))
                return true;
            if (generatedReadme && trim.contains("\"\"\"")
                    && !has(lower(trim), "readme = dedent(", "readme=dedent("))
                generatedReadme = false;
        }
        return false;
    }

    static List<ResearchFinder.Finding> deduplicate(List<ResearchFinder.Finding> findings) {
        if (findings == null) return Collections.emptyList();
        List<ResearchFinder.Finding> sorted = new ArrayList<>(findings);
        sorted.sort(Comparator.comparingDouble(
                (ResearchFinder.Finding f) -> Double.isFinite(f.created) ? f.created : 0)
                .reversed().thenComparingInt(f -> -f.priority)
                .thenComparing(f -> f.chatId)
                .thenComparingInt(f -> -f.messageNumber));
        Map<String, ResearchFinder.Finding> unique = new LinkedHashMap<>();
        for (ResearchFinder.Finding f : sorted) {
            if (f == null) continue;
            Matcher match = TASK_ID.matcher(f.excerpt);
            String id = null;
            while (match.find()) {
                String next = match.group().toUpperCase(Locale.ROOT);
                if (id != null && !id.equals(next)) { id = null; break; }
                id = next;
            }
            String key = id != null
                    ? "ID:" + classify(f) + ":" + f.kind + ":" + id
                    : "TEXT:" + lower(f.excerpt).replaceAll(
                            "(?iu)^[\\s*#|>:-]*(?:blocker|offener punkt|konflikt|"
                                    + "nächster schritt)\\s*[:=\\-]+", "")
                            .replaceAll("[\\s\\p{Punct}]+", " ").trim();
            unique.putIfAbsent(key, f);
        }
        return new ArrayList<>(unique.values());
    }

    private static String normalized(String line) {
        if (line == null) return "";
        return line.trim().replaceAll("^[#*|>+\\-\\s]+", "")
                .replace("**", "").replace(String.valueOf((char) 96), "").trim();
    }

    private static String lower(String s) {
        return (s == null ? "" : s.toLowerCase(Locale.ROOT));
    }

    private static boolean has(String text, String... needles) {
        for (String needle : needles) if (text.contains(needle)) return true;
        return false;
    }
}
