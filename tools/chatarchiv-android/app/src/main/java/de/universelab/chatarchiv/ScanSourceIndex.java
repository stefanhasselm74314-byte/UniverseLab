package de.universelab.chatarchiv;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.TreeMap;

/**
 * Avoids reopening a document referenced through overlapping SAF grants.
 * A matching filename and byte length is ONLY a possible copy, never proof of
 * identical content and never a reason to omit a distinct document from import.
 */
final class ScanSourceIndex {
    private final Set<String> documentIds = new HashSet<>();
    private final TreeMap<String, List<String>> sameNameAndSize = new TreeMap<>();
    private int repeatedReferences;

    boolean register(String authority, String documentId, String name, long size, String relativePath) {
        if (!documentIds.add(authority + '\0' + documentId)) {
            repeatedReferences++;
            return false;
        }
        if (size >= 0 && name != null) {
            String key = name.toLowerCase(Locale.ROOT) + '\0' + size;
            sameNameAndSize.computeIfAbsent(key, ignored -> new ArrayList<>()).add(relativePath);
        }
        return true;
    }

    int repeatedReferences() { return repeatedReferences; }

    int possibleCopyGroups() {
        int total = 0;
        for (List<String> paths : sameNameAndSize.values()) if (paths.size() > 1) total++;
        return total;
    }

    List<String> possibleCopyExamples(int maxGroups) {
        List<String> examples = new ArrayList<>();
        for (List<String> paths : sameNameAndSize.values()) {
            if (paths.size() < 2) continue;
            if (examples.size() == maxGroups) break;
            examples.add(paths.get(0) + " ↔ " + paths.get(1));
        }
        return examples;
    }
}
