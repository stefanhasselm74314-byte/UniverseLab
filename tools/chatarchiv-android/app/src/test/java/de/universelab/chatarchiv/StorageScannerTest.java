package de.universelab.chatarchiv;

import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;

import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public final class StorageScannerTest {
    @Rule public TemporaryFolder temp = new TemporaryFolder();

    @Test public void findsNestedChatJsonAndMatchingZipButNotOtherFiles() throws Exception {
        File root = temp.newFolder("storage");
        File nested = new File(root, "Download/Rettung/Unterordner");
        assertTrue(nested.mkdirs());
        Files.write(new File(nested, "conversations-000.json").toPath(), "[]".getBytes(StandardCharsets.UTF_8));
        Files.write(new File(nested, "conversation_asset_file_names.json").toPath(), "{}".getBytes(StandardCharsets.UTF_8));
        Files.write(new File(nested, "Urlaubsbild.jpg").toPath(), new byte[] {1, 2, 3});
        File archive = new File(root, "Export 2024.zip");
        try (ZipOutputStream zip = new ZipOutputStream(new FileOutputStream(archive))) {
            zip.putNextEntry(new ZipEntry("assets/photo.jpg"));
            zip.write(new byte[] {1, 2});
            zip.closeEntry();
            zip.putNextEntry(new ZipEntry("history/conversations.json"));
            zip.write("[]".getBytes(StandardCharsets.UTF_8));
            zip.closeEntry();
        }
        File unrelatedArchive = new File(root, "Andere.zip");
        try (ZipOutputStream zip = new ZipOutputStream(new FileOutputStream(unrelatedArchive))) {
            zip.putNextEntry(new ZipEntry("readme.txt"));
            zip.write(new byte[] {1});
            zip.closeEntry();
        }

        StorageScanner.Result result = StorageScanner.scan(root, ignored -> { }, () -> false);
        assertFalse(result.cancelled);
        assertEquals(2, result.matches.size());
        assertEquals(1, result.jsonFiles);
        assertEquals(1, result.zipFiles);
        assertTrue(result.matches.contains(new File(nested, "conversations-000.json")));
        assertTrue(result.matches.contains(archive));
    }

    @Test public void recognizesExportCopiesAndCancelsWithoutImporting() throws Exception {
        assertTrue(StorageScanner.isConversationJson("conversations.json"));
        assertTrue(StorageScanner.isConversationJson("conversations-004(2).json"));
        assertFalse(StorageScanner.isConversationJson("conversation_asset_file_names.json"));
        StorageScanner.Result result = StorageScanner.scan(temp.newFolder("empty"),
                ignored -> { }, () -> true);
        assertTrue(result.cancelled);
        assertEquals(0, result.matches.size());
    }

    @Test public void labelsPersistedSamsungRescueFolderWithoutGuessingOpaquePaths() {
        assertTrue(ScanPathLabel.hasLocalPath("primary:Download/ChatGPT_Rettung_2026-11-08"));
        assertEquals("Interner Speicher/Download/ChatGPT_Rettung_2026-11-08",
                ScanPathLabel.describe("primary:Download/ChatGPT_Rettung_2026-11-08", null,
                        "com.android.externalstorage.documents"));
        assertEquals("Interner Speicher", ScanPathLabel.describe("primary:", null, null));
        assertEquals("Speicher ABCD-1234/Exports",
                ScanPathLabel.describe("abcd-1234:Exports", null, null));
        assertFalse(ScanPathLabel.hasLocalPath("opaque-token:abc-984"));
        assertEquals("Exportarchiv (Anbieter: documents.example)",
                ScanPathLabel.describe("opaque-token:abc-984", "Exportarchiv", "documents.example"));
        assertEquals("Ordner bei documents.example (Pfad nicht verfügbar)",
                ScanPathLabel.describe("opaque-token:abc-984", null, "documents.example"));
    }

    @Test public void sourceIndexSkipsReferencesButPreservesDistinctPossibleCopies() {
        ScanSourceIndex index = new ScanSourceIndex();
        assertTrue(index.register("media", "doc1", "conversations-005.json", 6333444L,
                "Ordner 1/conversations-005.json"));
        assertFalse(index.register("media", "doc1", "conversations-005.json", 6333444L,
                "Ordner 2/conversations-005.json"));
        assertTrue(index.register("media", "doc2", "conversations-005.json", 6333444L,
                "Ordner 1/SAF-Test/conversations-005.json"));
        assertEquals(1, index.repeatedReferences());
        assertEquals(1, index.possibleCopyGroups());
        assertEquals(1, index.possibleCopyExamples(2).size());

        ScanSourceIndex different = new ScanSourceIndex();
        assertTrue(different.register("provider", "a", "conversations-000.json", 10, "A"));
        assertTrue(different.register("provider", "b", "conversations-000.json", 11, "B"));
        assertTrue(different.register("provider", "c", "conversations-000.json", -1, "C"));
        assertEquals(0, different.possibleCopyGroups());
    }
}
