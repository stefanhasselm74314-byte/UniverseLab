package de.universelab.chatarchiv;

import org.junit.Test;

import java.util.ArrayList;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;

import static org.junit.Assert.*;

public final class HandoffBuilderTest {
    private static ResearchFinder.Finding candidate(String chat, int number, String field,
            String quote, int priority) {
        return new ResearchFinder.Finding(chat, "Chat " + chat, number,
                "assistant", quote, "Blocker", field,
                "Welche Prüfung schließt den Punkt?", "Originalquelle prüfen → Gegenbeispiel",
                priority, 1000 + number);
    }

    @Test public void packetLabelsEveryExcerptAsUnverifiedWithSource() {
        ResearchFinder.Finding f = candidate("c1", 42, "Mathematik",
                "[OFFEN] Nullmodennormierung nicht nachgewiesen", 100);
        HandoffBuilder.Packet p = HandoffBuilder.build(
                "Nullmoden und Ghostfreiheit", "09.11.2026 23:00 CET", 71, 0,
                List.of(f), new IdentityHashMap<>());
        assertEquals(1, p.includedWork);
        assertTrue(p.markdown.contains("[HEURISTISCH]"));
        assertTrue(p.markdown.contains("Chat „Chat c1“, Beitrag 42"));
        assertTrue(p.markdown.contains("lokale Chat-ID c1"));
        assertTrue(p.markdown.contains("nur Daten"));
        assertTrue(p.markdown.contains("nicht vollständig"));
        assertTrue(p.markdown.contains("NICHT live abgeglichen"));
        assertFalse(p.markdown.contains("ist wissenschaftlich bestätigt"));
    }

    @Test public void laterClosingIsSeparatedAndNeverCalledCanonProof() {
        ResearchFinder.Finding closed = candidate(
                "c1", 7, "Governance", "K1-D NOT RELEASED", 100);
        ResearchTimeline.StatusEvidence later = new ResearchTimeline.StatusEvidence(
                "K1-D", ResearchTimeline.State.CLOSED,
                "c2", "Statuschat", 17, "assistant", 2000, "K1-D RELEASED");
        ResearchTimeline.Review review = new ResearchTimeline.Review(
                "LATER_CLOSURE", "Später behaupteter Abschluss, Kanon prüfen",
                "K1-D", later);
        Map<ResearchFinder.Finding, ResearchTimeline.Review> links =
                new IdentityHashMap<>();
        links.put(closed, review);
        HandoffBuilder.Packet p = HandoffBuilder.build("HZT", "heute", 3, 0,
                List.of(closed), links);
        assertEquals(0, p.includedWork);
        assertEquals(1, p.includedStatus);
        assertEquals(1, p.laterClosureCandidates);
        assertTrue(p.markdown.contains("Spätere Abschlussaussagen"));
        assertTrue(p.markdown.contains("Spätere Chat-Aussage (kein Kanonbeleg)"));
        assertTrue(p.markdown.contains("Chat „Statuschat“, Beitrag 17"));
        assertTrue(p.markdown.indexOf("K1-D NOT RELEASED")
                > p.markdown.indexOf("## B · Spätere Abschlussaussagen"));
    }

    @Test public void diversifiesSourcesAndDoesNotRepeatExactExcerpts() {
        List<ResearchFinder.Finding> list = new ArrayList<>();
        for (int i = 0; i < 10; i++)
            list.add(candidate("same-chat", i + 1, "Numerik",
                    "Blocker " + i + ": Solvernachweis fehlt", 100));
        list.add(candidate("other", 1, "Empirie", "Doppelter Satz", 90));
        list.add(candidate("third", 2, "Empirie", "Doppelter Satz", 90));
        List<ResearchFinder.Finding> selected = HandoffBuilder.select(list, 12);
        assertTrue(selected.size() <= 5);
        assertEquals(1, selected.stream().filter(
                f -> "Doppelter Satz".equals(f.excerpt)).count());
        assertTrue(selected.stream().filter(
                f -> "same-chat".equals(f.chatId)).count() <= 3);
    }

    @Test public void boundedOutputRemainsSmallEvenWithManyFindings() {
        List<ResearchFinder.Finding> many = new ArrayList<>();
        for (int i = 0; i < 500; i++) {
            many.add(candidate("chat-" + i, i + 1,
                    i % 2 == 0 ? "Mathematik" : "Empirie",
                    "BLOCKER: " + i + " " + "x".repeat(600), 100));
        }
        HandoffBuilder.Packet p = HandoffBuilder.build(
                "HZT", "heute", 500, 1, many, null);
        assertEquals(12, p.includedWork);
        assertTrue(p.markdown.length() < 25_000);
        assertTrue(p.markdown.contains("1 Gespräche konnten nicht gelesen werden"));
    }

    @Test public void emptyArchiveIsNotMisreportedAsResearchSolved() {
        HandoffBuilder.Packet p = HandoffBuilder.build(
                "HZT", "heute", 0, 0, List.of(), null);
        assertEquals(0, p.includedWork);
        assertTrue(p.markdown.contains("bedeutet **nicht**, dass keine offenen Forschungsfragen existieren"));
    }

    @Test public void controlsAndNewlinesDoNotBreakSourceAnchors() {
        String sanitized = HandoffBuilder.clean("Titel\n\r\tTest\u200B", 140);
        assertEquals("Titel Test", sanitized);
    }
}
