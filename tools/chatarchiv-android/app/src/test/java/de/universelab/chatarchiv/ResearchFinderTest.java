package de.universelab.chatarchiv;

import org.junit.Test;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public final class ResearchFinderTest {
    @Test public void reportsBlockerWithTraceableMessageNumber() {
        List<ConversationLogic.Message> chat = Arrays.asList(
                new ConversationLogic.Message("user", "Go"),
                new ConversationLogic.Message("assistant",
                        "K-2T.27: Die Isolation ist ein BLOCKER, noch nicht qualifiziert."));
        List<ResearchFinder.Finding> results = ResearchFinder.extract("id", "Schiff", chat, 5);
        assertEquals(1, results.size());
        assertEquals("Blocker", results.get(0).kind);
        assertEquals(2, results.get(0).messageNumber);
        assertEquals("id", results.get(0).chatId);
    }

    @Test public void doesNotInventAProblemFromOrdinaryConversation() {
        List<ResearchFinder.Finding> results = ResearchFinder.extract("id", "Titel",
                Arrays.asList(new ConversationLogic.Message("user", "Go"),
                        new ConversationLogic.Message("assistant", "Die Berechnung ist fertig.")), 5);
        assertTrue(results.isEmpty());
    }

    @Test public void distinguishesOpenPointAndNextStep() {
        List<ConversationLogic.Message> chat = Collections.singletonList(
                new ConversationLogic.Message("assistant",
                        "[OFFEN] Nullmoden-Norm nicht nachgewiesen.\n"
                                + "Nächster Schritt: Eine unabhängige analytische Kontrolle aufstellen."));
        List<ResearchFinder.Finding> results = ResearchFinder.extract("id", "HZT", chat, 4);
        assertEquals(2, results.size());
        assertEquals("Offener Punkt", results.get(0).kind);
        assertEquals("Mathematik", results.get(0).field);
        assertEquals("Nächster Schritt", results.get(1).kind);
    }

    @Test public void honorsLimitAndKeepsUnverifiedStatus() {
        List<ResearchFinder.Finding> results = ResearchFinder.extract("id", "HZT",
                Collections.singletonList(new ConversationLogic.Message("assistant",
                        "[OFFEN] Erste prüfbare Frage.\n[OFFEN] Zweite prüfbare Frage.")), 1);
        assertEquals(1, results.size());
        assertFalse(results.get(0).question.isEmpty());
    }

    @Test public void olderBlockerOutranksNewerTodos() {
        List<ConversationLogic.Message> chat = Arrays.asList(
                new ConversationLogic.Message("assistant", "BLOCKER: Die Ghostfreiheit ist noch nicht belegt."),
                new ConversationLogic.Message("assistant", "TODO: Zuerst Tests ergänzen."),
                new ConversationLogic.Message("assistant", "TODO: Danach Dokumentation ergänzen."));
        List<ResearchFinder.Finding> results = ResearchFinder.extract("id", "HZT", chat, 1);
        assertEquals(1, results.size());
        assertEquals("Blocker", results.get(0).kind);
        assertEquals(1, results.get(0).messageNumber);
    }

    @Test public void ignoresTemplateFieldListFromRealDeviceScreenshot() {
        List<ResearchFinder.Finding> results = ResearchFinder.extract("id", "Medien Designer",
                Collections.singletonList(new ConversationLogic.Message("assistant",
                        "vollständiger Aufgabenblock mit Task-ID, Quelle, Lieferobjekt, "
                                + "Blocker, nächstem Schritt und Rückgaberoute;")), 5);
        assertTrue(results.isEmpty());
    }

    @Test public void ignoresExplicitNoBlockerEvenIfOpenIsMentionedAsALabel() {
        List<ResearchFinder.Finding> results = ResearchFinder.extract("id", "Medien Designer",
                Collections.singletonList(new ConversationLogic.Message("assistant",
                        "BLOCKER / ABHÄNGIGKEIT = keine für die technische Kommunikationsgrafik; "
                                + "offene Engineeringgeometrie bleibt sichtbar als OPEN, APPROX oder ENVELOPE gekennzeichnet")), 5);
        assertTrue(results.isEmpty());
    }

    @Test public void keepsActualBlockedBranchFromRealDeviceScreenshot() {
        List<ResearchFinder.Finding> results = ResearchFinder.extract("id", "Relativitätstheorien",
                Collections.singletonList(new ConversationLogic.Message("assistant",
                        "Radion | Möglicher zusätzlicher Freiheitsgrad | Leichter, "
                                + "ungescreenter Minimalzweig blockiert |")), 5);
        assertEquals(1, results.size());
        assertEquals("Blocker", results.get(0).kind);
        assertEquals("Physikalisches Modell", results.get(0).field);
    }

    @Test public void keepsExplicitNonReleaseGateAndItsGovernanceScope() {
        List<ResearchFinder.Finding> results = ResearchFinder.extract("id", "Website Absicherung",
                Collections.singletonList(new ConversationLogic.Message("assistant",
                        "Die Freigabesperren bleiben korrekt dokumentiert: "
                                + "K1-D NOT RELEASED und K1-E NOT ADMISSIBLE.")), 5);
        assertEquals(1, results.size());
        assertEquals("Blocker", results.get(0).kind);
        assertEquals("Governance", results.get(0).field);
    }

    @Test public void metadataPrefaceMustNotHideARealTaskBlocker() {
        List<ResearchFinder.Finding> results = ResearchFinder.extract("id", "HZT",
                Collections.singletonList(new ConversationLogic.Message("assistant",
                        "TASK-ID = Z8B-01; BLOCKER: Nullmoden-Norm ist nicht nachgewiesen.")), 5);
        assertEquals(1, results.size());
        assertEquals("Blocker", results.get(0).kind);
    }

    @Test public void ignoresNegatedConflictAndIncidentalKeyword() {
        List<ResearchFinder.Finding> results = ResearchFinder.extract("id", "Titel",
                Collections.singletonList(new ConversationLogic.Message("assistant",
                        "Es gibt keinen Widerspruch zwischen diesen beiden Definitionen.\n"
                                + "Die Tabelle hat eine Spalte Blocker für jeden Aufgabenblock.")), 5);
        assertTrue(results.isEmpty());
    }
}
