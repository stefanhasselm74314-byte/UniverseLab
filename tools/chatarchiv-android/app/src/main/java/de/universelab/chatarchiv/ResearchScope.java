package de.universelab.chatarchiv;

import java.util.regex.Pattern;

/**
 * Only a navigational guess based on wording, never a verified research status.
 * Areas do not affect which findings are retained or the priority of a finding.
 */
final class ResearchScope {
    static final String PHYSICS = "Physik/Mathematik";
    static final String GOVERNANCE = "Governance/Freigabe";
    static final String ORGANIZATION = "Organisation/Prozess";
    static final String SOFTWARE = "Software/Archiv";
    static final String ENGINEERING = "Engineering";
    static final String UNCLEAR = "Unklar/Gemischt";

    static final String[] FILTERS = {
            "Alle Bereiche", PHYSICS, GOVERNANCE, ORGANIZATION, SOFTWARE, ENGINEERING, UNCLEAR
    };

    private static final Pattern GOVERNANCE_CUE = Pattern.compile(
            "(?iu)(?:\\bK1[-_][DE]\\b|\\bNOT[_ -]?(?:RELEASED|ADMISSIBLE|READY)\\b|"
                    + "\\bGOVERNANCE\\b|\\bFREIGABESPERRE\\b|\\bFREIGABEGATE\\b)");
    private static final Pattern ORGANIZATION_CUE = Pattern.compile(
            "(?iu)\\b(?:EINREICHUNG|ANTRAG|FORMULAR|REGISTRIERUNG|TERMINPLAN|"
                    + "PROJEKTBOARD|WORD|DOCX|POWERPOINT|PRÄSENTATION|"
                    + "GLIEDERUNG|DRUCKAUFTRAG|AUSHANG)\\b");
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
