package de.universelab.chatarchiv;

import org.junit.Test;

import java.util.Arrays;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;

import static org.junit.Assert.*;

public final class HandoffQualityTest {
    private static ResearchFinder.Finding finding(String id, String title, String quote,
            String kind, double date, int messageNo) {
        return new ResearchFinder.Finding(id, title, messageNo, "assistant", quote,
                kind, "Allgemeine Prüfung", "Was wäre ein Beleg?", "Quelle kontrollieren",
                "Blocker".equals(kind) ? 100 : 70, date);
    }

    @Test public void emptySchemaRowsAndShortStatusCellsAreNotResearchTasks() {
        assertTrue(HandoffQuality.falsePositive(finding("a", "Test",
                "GENAU NÄCHSTER SCHRITT =", "Nächster Schritt", 1, 1)));
        assertTrue(HandoffQuality.falsePositive(finding("a", "Test",
                "Subsystem C | [BLOCKIERT] |", "Blocker", 1, 1)));
        assertTrue(HandoffQuality.falsePositive(finding("a", "Test",
                "Friedmann-Modul | noch offen |", "Offener Punkt", 1, 1)));
        assertTrue(HandoffQuality.falsePositive(finding("a", "Test",
                "Nächster Schritt: Ich könnte dir eine Testfunktion schreiben.",
                "Nächster Schritt", 1, 1)));
    }

    @Test public void gatingEchoesAreNotPromotedToThreeTasks() {
        assertTrue(HandoffQuality.falsePositive(finding("b", "Status",
                "K1-D = NOT_RELEASED", "Blocker", 10, 1)));
        assertTrue(HandoffQuality.falsePositive(finding("b", "Status",
                "K1-E = NOT_ADMISSIBLE", "Blocker", 11, 2)));
        assertFalse(HandoffQuality.falsePositive(finding("b", "HZT-Full",
                "K1-D: Die Nullmoden-Herleitung ist nach wie vor nicht bewiesen und blockiert.",
                "Blocker", 12, 3)));
    }

    @Test public void generalExpositionIsNotAnAgreedProjectTask() {
        assertTrue(HandoffQuality.falsePositive(finding("a", "Einführung",
                "Der Ursprung des Parameters bleibt in der Kosmologie ungeklärt.",
                "Offener Punkt", 2, 1)));
        assertTrue(HandoffQuality.falsePositive(finding("a", "Einführung",
                "Konflikt: kosmologische Konstante in der Standardtheorie.",
                "Konflikt", 2, 1)));
        assertFalse(HandoffQuality.falsePositive(finding("a", "HZT",
                "[OFFEN] Nullmoden-Normierung in HZT-M0 analytisch nicht nachgewiesen.",
                "Offener Punkt", 2, 1)));
    }

    @Test public void generatedReadmeAndFencedCodeCannotSupplyAUserTask() {
        String message = "from textwrap import dedent\n"
                + "readme = dedent(f" + "\"\"\"" + "\n"
                + "Nächster Schritt: Ich kann später einen Adapter bauen.\n"
                + "\"\"\"" + ")\nwith open('README.md', 'w') as f:\n"
                + "  f.write(readme)\n";
        List<ConversationLogic.Message> messages = List.of(
                new ConversationLogic.Message("assistant", message));
        List<ResearchFinder.Finding> raw = ResearchFinder.extract(
                "c", "HZT-Code", messages, 20);
        assertEquals(1, raw.size());
        assertTrue(HandoffQuality.screen(raw, messages,
                HandoffQuality.Scope.ALL, 10).isEmpty());

        List<ConversationLogic.Message> fenced = List.of(
                new ConversationLogic.Message("assistant",
                        "Skript-Dokumentation:\n" + String.valueOf((char) 96).repeat(3)
                                + "md\nTODO: Nicht als Aufgabe behandeln.\n"
                                + String.valueOf((char) 96).repeat(3)
                                + "\nEchte Aufgabe: [OFFEN] Normbeweis fehlt."));
        List<ResearchFinder.Finding> c = ResearchFinder.extract("d", "6D", fenced, 10);
        assertEquals(2, c.size());
        assertEquals(1, HandoffQuality.screen(c, fenced,
                HandoffQuality.Scope.PHYSICS, 10).size());
    }

    @Test public void separatesPhysicsFromSoftwareAndEngineering() {
        ResearchFinder.Finding physics = finding("a", "Hyperzeit-Theorie Forschung",
                "[OFFEN] Radion-Kopplung an Materie noch nicht getestet.",
                "Offener Punkt", 1, 1);
        ResearchFinder.Finding software = finding("b", "UniverseLab Tagesmonitor",
                "[OFFEN] Filterlogik der Website testen.",
                "Offener Punkt", 2, 1);
        ResearchFinder.Finding engineering = finding("c", "Raumschiff Bauplan",
                "BLOCKER: Rotor-Lagerdaten fehlen.", "Blocker", 3, 1);
        assertEquals(HandoffQuality.Scope.PHYSICS, HandoffQuality.classify(physics));
        assertEquals(HandoffQuality.Scope.SOFTWARE, HandoffQuality.classify(software));
        assertEquals(HandoffQuality.Scope.ENGINEERING, HandoffQuality.classify(engineering));
        assertEquals(1, HandoffQuality.screen(Arrays.asList(physics, software, engineering),
                Collections.emptyList(), HandoffQuality.Scope.PHYSICS, 8).size());
        assertEquals(3, HandoffQuality.screen(Arrays.asList(physics, software, engineering),
                Collections.emptyList(), HandoffQuality.Scope.ALL, 8).size());
    }

    @Test public void mergesSameKeyButPreservesSeparateWorkOrders() {
        ResearchFinder.Finding a = finding("a", "HZT",
                "Z8B-01 BLOCKER: Kopplung nicht geprüft", "Blocker", 100, 2);
        ResearchFinder.Finding b = finding("b", "HZT",
                "Z8B-01 BLOCKER: Kopplung ist weiterhin ungeprüft", "Blocker", 200, 5);
        ResearchFinder.Finding c = finding("c", "HZT",
                "Z8B-02 BLOCKER: Normierung nicht geprüft", "Blocker", 150, 3);
        List<ResearchFinder.Finding> dedup =
                HandoffQuality.deduplicate(Arrays.asList(a, b, c));
        assertEquals(2, dedup.size());
        assertTrue(dedup.contains(b));
        assertTrue(dedup.contains(c));
        assertFalse(dedup.contains(a));
    }

    @Test public void shortStatusTablesAreNotDuplicateResearchOrders() {
        assertTrue(HandoffQuality.falsePositive(finding("d", "Projekt",
                "6D-Identifikation | weiterhin blockiert |",
                "Blocker", 10, 1)));
        assertTrue(HandoffQuality.falsePositive(finding("d", "Projekt",
                "6D-Identifikation | weiterhin offen/blockiert |",
                "Offener Punkt", 10, 2)));
        assertFalse(HandoffQuality.falsePositive(finding("d", "Projekt",
                "6D-Identifikation | blockiert, solange die Forward Map nicht vorliegt |",
                "Blocker", 10, 3)));
    }

    @Test public void latexGateAndPlatformWorkStayOutOfPhysicsSelection() {
        assertTrue(HandoffQuality.falsePositive(finding("d", "Projekt",
                "K1\\text{D}=\\texttt{NOT RELEASED}", "Blocker", 10, 1)));
        ResearchFinder.Finding platform = finding("p", "UniverseLab Forschungsplattform",
                "BLOCKER: Der Status des aktiven Webmoduls ist unklar.",
                "Blocker", 10, 2);
        ResearchFinder.Finding scanner = finding("p", "Technischer Nebenchat",
                "BLOCKER: Scanner ist im Branch, der Connector ist nicht verfügbar.",
                "Blocker", 10, 3);
        assertEquals(HandoffQuality.Scope.SOFTWARE, HandoffQuality.classify(platform));
        assertEquals(HandoffQuality.Scope.SOFTWARE, HandoffQuality.classify(scanner));
    }

    @Test public void approvedPacketIncludesOnlyTheChosenQuote() {
        ResearchFinder.Finding a = finding("a", "HZT",
                "[OFFEN] erster Normbeweis fehlt", "Offener Punkt", 100, 1);
        ResearchFinder.Finding b = finding("b", "HZT",
                "[OFFEN] zweiter Materietest fehlt", "Offener Punkt", 110, 2);
        HandoffBuilder.Packet p = HandoffBuilder.buildSelected(
                "6D-Normierung", "heute", 71, 0, Arrays.asList(a, b),
                new IdentityHashMap<>(), List.of(a), "6D-Physik");
        assertEquals(1, p.includedWork);
        assertEquals(2, p.totalCandidates);
        assertTrue(p.markdown.contains("erster Normbeweis"));
        assertFalse(p.markdown.contains("zweiter Materietest"));
        assertTrue(p.markdown.contains("Vom Nutzer bewusst ausgewählt"));
        assertTrue(p.markdown.contains("aktueller Status offline nicht verifiziert"));
        assertTrue(p.markdown.contains("github.com/stefanhasselm74314-byte/UniverseLab/blob/main"));
    }
}
