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
}
