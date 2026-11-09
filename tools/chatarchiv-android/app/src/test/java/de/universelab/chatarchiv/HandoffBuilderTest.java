package de.universelab.chatarchiv;

import org.junit.Test;

import java.util.ArrayList;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.time.Instant;

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
        assertTrue(p.markdown.contains("**nicht** live abgeglichen"));
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


    private static ResearchFinder.Finding withKind(String chat, String kind, String field,
            double when) {
        int score = "Blocker".equals(kind) ? 100 : "Konflikt".equals(kind) ? 90
                : "Offener Punkt".equals(kind) ? 70 : 50;
        return new ResearchFinder.Finding(chat, "Chat " + chat, 10,
                "assistant", kind + ": spezifischer Nachweis " + chat,
                kind, field, "Wie prüfen?", "Quelltext lesen", score, when);
    }

    @Test public void handoffShowsOpenIssuesConflictsAndNextStepsAlongsideBlockers() {
        List<ResearchFinder.Finding> list = new ArrayList<>();
        for (int i = 0; i < 25; i++)
            list.add(withKind("block-" + i, "Blocker", "Governance", 10000 + i));
        for (int i = 0; i < 8; i++) {
            list.add(withKind("open-" + i, "Offener Punkt", "Mathematik", 9000 + i));
            list.add(withKind("conflict-" + i, "Konflikt", "Empirie", 8000 + i));
            list.add(withKind("next-" + i, "Nächster Schritt", "Daten/Archiv", 7000 + i));
        }
        List<ResearchFinder.Finding> selected =
                HandoffBuilder.selectWorkBalanced(list, 12, "HZT-M0");
        assertEquals(12, selected.size());
        assertEquals(5, selected.stream().filter(f -> "Blocker".equals(f.kind)).count());
        assertEquals(3, selected.stream().filter(f -> "Offener Punkt".equals(f.kind)).count());
        assertEquals(2, selected.stream().filter(f -> "Konflikt".equals(f.kind)).count());
        assertEquals(2, selected.stream().filter(f -> "Nächster Schritt".equals(f.kind)).count());
        assertEquals(12, selected.stream().map(f -> f.chatId).distinct().count());
    }

    @Test public void chosenFocusHasLimitedRecencyBonusAndDoesNotOverrideYears() {
        double reference = Instant.parse("2026-11-09T12:00:00Z").getEpochSecond();
        ResearchFinder.Finding recent = withKind(
                "newest", "Offener Punkt", "Empirie", reference);
        ResearchFinder.Finding focused = new ResearchFinder.Finding(
                "focused", "Nullmoden Prüfung", 5, "assistant",
                "[OFFEN] Nullmoden normalisieren", "Offener Punkt", "Mathematik",
                "Prüffrage", "Quellnachweis", 70, reference - 5 * 86400);
        ResearchFinder.Finding ancient = new ResearchFinder.Finding(
                "ancient", "Nullmoden Test", 5, "assistant",
                "[OFFEN] alte Nullmoden", "Offener Punkt", "Mathematik",
                "Prüffrage", "Quellnachweis", 70, reference - 365 * 86400);
        List<ResearchFinder.Finding> selected = HandoffBuilder.selectWorkBalanced(
                List.of(recent, focused, ancient), 1, "Nullmoden");
        assertEquals("focused", selected.get(0).chatId);
        assertNotEquals("ancient", selected.get(0).chatId);
    }

    @Test public void sourceDateIsIncludedAndDoesNotImplyFreshCanon() {
        double when = Instant.parse("2026-11-09T12:00:00Z").getEpochSecond();
        ResearchFinder.Finding f = new ResearchFinder.Finding(
                "c1", "Projektstatus", 25, "assistant",
                "K1-D NOT RELEASED", "Blocker", "Governance",
                "Prüffrage", "Kanon prüfen", 100, when);
        HandoffBuilder.Packet p = HandoffBuilder.build(
                "HZT", "10.11.2026", 1, 0, List.of(f), null);
        assertTrue(p.markdown.contains("Beitragsdatum 09.11.2026"));
        assertTrue(p.markdown.contains("Projektkanon"));
        assertTrue(p.markdown.contains("nicht** live abgeglichen"));
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
        assertTrue(p.markdown.contains("1 Gespräch konnte nicht gelesen werden"));
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
