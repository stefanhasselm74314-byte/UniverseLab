package de.universelab.chatarchiv;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.Deque;
import java.util.Enumeration;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.TreeMap;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

/** Read-only inventory of ChatGPT exports in an explicitly authorized storage tree. */
final class StorageScanner {
    private static final int MAX_DIRECTORIES = 100_000;
    private static final int MAX_FILES = 500_000;
    private static final int MAX_MATCHES = 15_000;

    interface Cancelled { boolean isCancelled(); }
    interface Progress { void onProgress(Result current); }

    static final class Result {
        final List<File> matches = new ArrayList<>();
        int folders;
        int inspectedFiles;
        int jsonFiles;
        int zipFiles;
        int unreadableFolders;
        int unreadableArchives;
        boolean cancelled;
    }

    private static final class Folder {
        final File directory;
        final int depth;
        Folder(File directory, int depth) { this.directory = directory; this.depth = depth; }
    }

    static boolean isConversationJson(String name) {
        return name != null && name.toLowerCase(Locale.ROOT)
                .matches("conversations(?:-[0-9]+)?(?:\\([0-9]+\\))?\\.json");
    }

    static Result scan(File root, Progress progress, Cancelled cancelled) throws IOException {
        if (root == null || !root.isDirectory()) throw new IOException("Speicher-Hauptverzeichnis nicht verfügbar");
        Result result = new Result();
        Deque<Folder> pending = new ArrayDeque<>();
        Set<String> visited = new HashSet<>();
        pending.push(new Folder(root, 0));
        while (!pending.isEmpty()) {
            if (cancelled.isCancelled()) { result.cancelled = true; break; }
            Folder folder = pending.pop();
            if (folder.depth > 64 || Files.isSymbolicLink(folder.directory.toPath())) continue;
            String canonical;
            try { canonical = folder.directory.getCanonicalPath(); }
            catch (IOException | SecurityException ignored) { result.unreadableFolders++; continue; }
            if (!visited.add(canonical)) continue;
            if (++result.folders > MAX_DIRECTORIES) throw new IOException("Zu viele Ordner; Suche aus Sicherheitsgründen begrenzt");
            File[] children;
            try { children = folder.directory.listFiles(); }
            catch (SecurityException ignored) { children = null; }
            if (children == null) { result.unreadableFolders++; continue; }
            Arrays.sort(children, Comparator.comparing(File::getName, String.CASE_INSENSITIVE_ORDER));
            for (File file : children) {
                if (cancelled.isCancelled()) { result.cancelled = true; break; }
                if (Files.isSymbolicLink(file.toPath())) continue;
                if (file.isDirectory()) {
                    pending.push(new Folder(file, folder.depth + 1));
                    continue;
                }
                if (!file.isFile()) continue;
                if (++result.inspectedFiles > MAX_FILES) throw new IOException("Mehr als 500.000 Dateien; Suche begrenzt");
                String name = file.getName();
                if (isConversationJson(name)) {
                    result.matches.add(file);
                    result.jsonFiles++;
                } else if (name.toLowerCase(Locale.ROOT).endsWith(".zip") && containsChatJson(file, result)) {
                    result.matches.add(file);
                    result.zipFiles++;
                }
                if (result.matches.size() > MAX_MATCHES) throw new IOException("Mehr als 15.000 Chat-Exportdateien; bitte Suche eingrenzen");
                if (result.inspectedFiles % 250 == 0) progress.onProgress(result);
            }
            if (result.cancelled) break;
        }
        result.matches.sort(Comparator.comparing(File::getAbsolutePath, String.CASE_INSENSITIVE_ORDER));
        progress.onProgress(result);
        return result;
    }

    private static boolean containsChatJson(File archive, Result result) {
        // ZipFile reads the ZIP central directory, not the potentially huge
        // image/file-*.dat payloads (which can exceed 40 GiB per archive).
        try (ZipFile zip = new ZipFile(archive)) {
            Enumeration<? extends ZipEntry> entries = zip.entries();
            while (entries.hasMoreElements()) {
                ZipEntry entry = entries.nextElement();
                if (entry.isDirectory()) continue;
                String path = entry.getName();
                String name = path.substring(path.lastIndexOf('/') + 1);
                if (isConversationJson(name)) return true;
            }
        } catch (IOException | SecurityException ignored) {
            // An unrelated, protected, encrypted or truncated ZIP must not
            // abort discovery of all other exports.
            result.unreadableArchives++;
        }
        return false;
    }

    private StorageScanner() { }
}

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

/**
 * Deduplicates references to one provider document without reopening it.
 * Matching filename and size is only a possible copy: distinct documents are
 * always left for the established content-aware ChatStore importer.
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
