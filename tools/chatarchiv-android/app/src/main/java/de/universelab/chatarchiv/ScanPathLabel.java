package de.universelab.chatarchiv;

import java.util.Locale;

/** Human-readable SAF locations; never assumes that an opaque provider ID is a file path. */
final class ScanPathLabel {
    static boolean hasLocalPath(String documentId) {
        if (documentId == null) return false;
        int separator = documentId.indexOf(':');
        if (separator < 0) return false;
        String volume = documentId.substring(0, separator);
        return "primary".equalsIgnoreCase(volume)
                || volume.matches("(?i)[0-9a-f]{4}-[0-9a-f]{4}");
    }

    static String describe(String documentId, String displayName, String authority) {
        if (hasLocalPath(documentId)) {
            int separator = documentId.indexOf(':');
            String volume = documentId.substring(0, separator);
            String suffix = clean(documentId.substring(separator + 1).replace('\\', '/'));
            String prefix = "primary".equalsIgnoreCase(volume)
                    ? "Interner Speicher" : "Speicher " + volume.toUpperCase(Locale.ROOT);
            return suffix.isEmpty() ? prefix : prefix + "/" + suffix;
        }
        String name = clean(displayName);
        String provider = clean(authority);
        if (!name.isEmpty()) return provider.isEmpty() ? name : name + " (Anbieter: " + provider + ")";
        return provider.isEmpty() ? "Unbekannter freigegebener Ordner"
                : "Ordner bei " + provider + " (Pfad nicht verfügbar)";
    }

    private static String clean(String value) {
        if (value == null) return "";
        String singleLine = value.replaceAll("[\\p{Cntrl}]+", " ").trim();
        return singleLine.length() > 100 ? singleLine.substring(0, 100) + "…" : singleLine;
    }

    private ScanPathLabel() { }
}
