package de.universelab.chatarchiv;

import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;

import java.io.File;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.FileOutputStream;
import java.util.List;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.assertNotEquals;
import static org.junit.Assert.fail;

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

    @Test public void trashEntryRetainsItsCategoryAndNeverBecomesAnActiveRecord() throws Exception {
        ChatStore.Entry active = new ChatStore.Entry("test-id", "New chat", "a".repeat(64) + ".json",
                123L, ChatStore.OTHER, "b".repeat(64));
        assertFalse(active.inTrash());
        ChatStore.Entry deleted = active.moveToTrash(456L);
        assertTrue(deleted.inTrash());
        assertEquals(ChatStore.TRASH, deleted.category);
        assertEquals(ChatStore.OTHER, deleted.originCategory);
        assertEquals(456L, deleted.trashedAt);
        assertEquals(ChatStore.TRASH, deleted.asJson().getString("category"));
        assertEquals(ChatStore.OTHER, deleted.asJson().getString("origin_category"));
        assertEquals(456L, deleted.asJson().getLong("trashed_at"));

        ChatStore.Entry restored = deleted.restoreFromTrash();
        assertEquals(ChatStore.OTHER, restored.category);
        assertFalse(restored.inTrash());
        assertEquals(active.id, restored.id);
        assertEquals(active.digest, restored.digest);
        assertTrue(deleted.beginPermanentDeletion().inTrash());
        try {
            deleted.beginPermanentDeletion().restoreFromTrash();
            fail("Pending permanent deletion must never restore a possibly incomplete chat");
        } catch (IllegalStateException expected) {
            // Marker prevents partially deleted records reappearing.
        }
    }

    @Test public void archivedVersionFilesAreBoundToOneChatAndValidSha256() {
        String digest = "0123456789abcdef".repeat(4);
        String oneChat = ChatStore.archivedVersionFilename("id-one", digest);
        String another = ChatStore.archivedVersionFilename("id-two", digest);
        assertNotEquals(oneChat, another);
        assertTrue(oneChat.matches("[0-9a-f]{64}-[0-9a-f]{64}\\.json"));
        try {
            ChatStore.archivedVersionFilename("id-one", "../" + digest);
            fail("Untrusted file name must not be accepted");
        } catch (IllegalArgumentException expected) {
            // Checked before any file can be accessed.
        }
        try {
            ChatStore.archivedVersionFilename("", digest);
            fail("An empty chat identity must not be accepted");
        } catch (IllegalArgumentException expected) {
            // Checked before any file can be accessed.
        }
    }

    @Test public void sha256ComparesActualBytesWithoutTrustingMetadata() throws Exception {
        byte[] a = "private-json-A".getBytes(StandardCharsets.UTF_8);
        byte[] copy = "private-json-A".getBytes(StandardCharsets.UTF_8);
        byte[] different = "private-json-B".getBytes(StandardCharsets.UTF_8);
        assertEquals(StorageScanner.sha256(new ByteArrayInputStream(a), a.length, () -> false),
                StorageScanner.sha256(new ByteArrayInputStream(copy), copy.length, () -> false));
        assertNotEquals(StorageScanner.sha256(new ByteArrayInputStream(a), a.length, () -> false),
                StorageScanner.sha256(new ByteArrayInputStream(different), different.length, () -> false));
        try {
            StorageScanner.sha256(new ByteArrayInputStream(a), a.length - 1, () -> false);
            fail("Exceeded bound must not be accepted");
        } catch (IOException expected) {
            assertTrue(expected.getMessage().contains("Prüfgrenze"));
        }
        try {
            StorageScanner.sha256(new ByteArrayInputStream(a), a.length, () -> true);
            fail("Cancelled inspection must not read");
        } catch (IOException expected) {
            assertTrue(expected.getMessage().contains("abgebrochen"));
        }
    }

    @Test public void searchUnquotedTermsAreOrAndQuotedPhrasesAreContiguous() throws Exception {
        File index = temp.newFolder("keyword-index");
        List<ChatStore.Entry> chats = new java.util.ArrayList<>();
        String names[] = {"Nur New", "Nur Chats", "New Chats", "Andere Chats einbeziehen",
                "Nur anderes Thema", "Newspaper and chattering", "New – später Chats"};
        String bodies[] = {"leer", "leer", "leer", "enthält Wörter aus dem Thema",
                "Hier steht ausdrücklich New Chats in einem sichtbaren Beitrag",
                "nur newspaper und chattering", "leer"};
        for (int i = 0; i < names.length; i++) {
            String filename = String.format(java.util.Locale.ROOT, "entry%02d.json", i);
            chats.add(new ChatStore.Entry("qa-" + i, names[i], filename,
                    0L, ChatStore.OTHER, "digest-" + i));
            Files.write(new File(index, filename.replace(".json", ".search")).toPath(),
                    bodies[i].getBytes(StandardCharsets.UTF_8));
        }
        // Unquoted: OR. Every title with either word and the one body-only hit appears.
        assertEquals(6, ChatStore.search(chats, "alle", "New Chats", () -> false, index).size());
        // Quoted: exact contiguous phrase, in either title or visible message contents.
        assertEquals(2, ChatStore.search(chats, "alle", "\"New Chats\"", () -> false, index).size());
        // Title scoping must exclude the body-only phrase occurrence.
        assertEquals(1, ChatStore.search(chats, "alle", "titel:\"New Chats\"", () -> false, index).size());
        assertEquals(1, ChatStore.search(chats, "alle", "title:\"new chats\"", () -> false, index).size());
        // Whole words: Newspaper or chattering must not count as New or Chats.
        assertEquals(4, ChatStore.search(chats, "alle", "new", () -> false, index).size());
        assertEquals(5, ChatStore.search(chats, "alle", "chats", () -> false, index).size());
        assertEquals(0, ChatStore.search(chats, "alle", "\"news chats\"", () -> false, index).size());
        assertEquals(0, ChatStore.search(chats, ChatStore.PROJECT, "new", () -> false, index).size());
    }

    @Test public void quotedPhraseMatchesAcrossBufferedIndexBoundary() throws Exception {
        File index = temp.newFolder("long-index");
        String filename = "boundary.json";
        ChatStore.Entry chat = new ChatStore.Entry("boundary-id", "Unerwarteter Titel",
                filename, 0, ChatStore.OTHER, "");
        String padding = "x".repeat(8190);
        Files.write(new File(index, "boundary.search").toPath(),
                (padding + " New Chats are searchable.").getBytes(StandardCharsets.UTF_8));
        assertEquals(1, ChatStore.search(java.util.Collections.singletonList(chat), "alle",
                "\"New Chats\"", () -> false, index).size());
        assertEquals(0, ChatStore.search(java.util.Collections.singletonList(chat), "alle",
                "\"New Chat\"", () -> false, index).size());

        // Guard against a false word boundary at the end of an 8192-character block.
        Files.write(new File(index, "boundary.search").toPath(),
                ("x".repeat(8188) + " New" + "spaper").getBytes(StandardCharsets.UTF_8));
        assertEquals(0, ChatStore.search(java.util.Collections.singletonList(chat), "alle",
                "New", () -> false, index).size());
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
        assertEquals(1, index.contentCheckCandidates(8).size());
        assertEquals(6333444L, index.contentCheckCandidates(8).get(0).size);
        assertEquals(2, index.contentCheckCandidates(8).get(0).paths.size());

        ScanSourceIndex different = new ScanSourceIndex();
        assertTrue(different.register("provider", "a", "conversations-000.json", 10, "A"));
        assertTrue(different.register("provider", "b", "conversations-000.json", 11, "B"));
        assertTrue(different.register("provider", "c", "conversations-000.json", -1, "C"));
        assertEquals(0, different.possibleCopyGroups());
    }
}
