package de.universelab.chatarchiv;

import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public final class ScanPathLabelTest {
    @Test public void identifiesSamsungRescueFolderFromPrimaryDocumentId() {
        assertTrue(ScanPathLabel.hasLocalPath("primary:Download/ChatGPT_Rettung_2026-11-08"));
        assertEquals("Interner Speicher/Download/ChatGPT_Rettung_2026-11-08",
                ScanPathLabel.describe("primary:Download/ChatGPT_Rettung_2026-11-08", null, "com.android.externalstorage.documents"));
    }

    @Test public void handlesVolumeRootAndRemovableStorage() {
        assertEquals("Interner Speicher", ScanPathLabel.describe("primary:", null, null));
        assertEquals("Speicher ABCD-1234/Exports", ScanPathLabel.describe("abcd-1234:Exports", null, null));
    }

    @Test public void doesNotPresentOpaqueProviderIdsAsRealPaths() {
        assertFalse(ScanPathLabel.hasLocalPath("opaque-token:abc-984"));
        assertEquals("Exportarchiv (Anbieter: documents.example)",
                ScanPathLabel.describe("opaque-token:abc-984", "Exportarchiv", "documents.example"));
        assertEquals("Ordner bei documents.example (Pfad nicht verfügbar)",
                ScanPathLabel.describe("opaque-token:abc-984", null, "documents.example"));
    }
}
