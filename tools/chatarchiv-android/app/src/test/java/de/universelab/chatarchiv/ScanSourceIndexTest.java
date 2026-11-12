package de.universelab.chatarchiv;

import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public final class ScanSourceIndexTest {
    @Test public void skipsOnlySameProviderDocumentAndPreservesDistinctCopies() {
        ScanSourceIndex index = new ScanSourceIndex();
        assertTrue(index.register("media", "doc1", "conversations-005.json", 6333444L, "Ordner 1/conversations-005.json"));
        assertFalse(index.register("media", "doc1", "conversations-005.json", 6333444L, "Ordner 2/conversations-005.json"));
        assertTrue(index.register("media", "doc2", "conversations-005.json", 6333444L, "Ordner 1/SAF-Test/conversations-005.json"));
        assertEquals(1, index.repeatedReferences());
        assertEquals(1, index.possibleCopyGroups());
        assertEquals(1, index.possibleCopyExamples(2).size());
    }

    @Test public void doesNotAssumeDifferentContentOrUnknownSizesAreCopies() {
        ScanSourceIndex index = new ScanSourceIndex();
        assertTrue(index.register("provider", "a", "conversations-000.json", 10, "A"));
        assertTrue(index.register("provider", "b", "conversations-000.json", 11, "B"));
        assertTrue(index.register("provider", "c", "conversations-000.json", -1, "C"));
        assertEquals(0, index.possibleCopyGroups());
    }
}
