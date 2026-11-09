package de.universelab.chatarchiv;

import org.junit.Test;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

public final class ResearchTimelineTest {
    private static ConversationLogic.Message msg(String role, String text, double time) {
        return new ConversationLogic.Message(role, text, time);
    }

    private static ResearchFinder.Finding finding(String id, String title,
            ConversationLogic.Message message) {
        List<ResearchFinder.Finding> list = ResearchFinder.extract(id, title,
                Collections.singletonList(message), 5);
        assertEquals(1, list.size());
        return list.get(0);
    }

    private static ResearchTimeline.Review review(ResearchFinder.Finding finding,
            List<ResearchTimeline.StatusEvidence> events) {
        Map<ResearchFinder.Finding, ResearchTimeline.Review> result =
                ResearchTimeline.reconcile(Collections.singletonList(finding), events);
        return result.get(finding);
    }

    @Test public void laterExplicitClosureLinksAcrossChatsWithTimestamps() {
        ResearchFinder.Finding original = finding("old", "HZT",
                msg("assistant", "TASK-ID = Z8B-01; BLOCKER: Nullmoden-Norm nicht nachgewiesen.", 1000));
        List<ResearchTimeline.StatusEvidence> later = ResearchTimeline.collect("new", "Statusreview",
                Collections.singletonList(msg("assistant", "Z8B-01 Status: CLOSED", 2000)));
        ResearchTimeline.Review linked = review(original, later);
        assertEquals("LATER_CLOSURE", linked.code);
        assertEquals("Z8B-01", linked.identifier);
        assertEquals("new", linked.source.chatId);
        assertEquals(1, linked.source.messageNumber);
    }

    @Test public void laterReopeningWinsOverEarlierClosure() {
        ResearchFinder.Finding original = finding("old", "HZT",
                msg("assistant", "[OFFEN] Z8B-01 bleibt noch zu prüfen.", 1000));
        List<ResearchTimeline.StatusEvidence> all = new ArrayList<>();
        all.addAll(ResearchTimeline.collect("a", "Vorläufig", Collections.singletonList(
                msg("assistant", "Z8B-01 Status: CLOSED", 2000))));
        all.addAll(ResearchTimeline.collect("b", "Neu", Collections.singletonList(
                msg("assistant", "Z8B-01 Status: REOPENED", 3000))));
        ResearchTimeline.Review linked = review(original, all);
        assertEquals("LATER_OPEN", linked.code);
        assertEquals("b", linked.source.chatId);
    }

    @Test public void differentTaskNeverClosesOriginal() {
        ResearchFinder.Finding original = finding("old", "HZT",
                msg("assistant", "[OFFEN] Z8B-01 muss untersucht werden.", 1000));
        List<ResearchTimeline.StatusEvidence> later = ResearchTimeline.collect("new", "Andere Aufgabe",
                Collections.singletonList(msg("assistant", "Z8B-02 Status: CLOSED", 2000)));
        assertEquals("NO_LATER", review(original, later).code);
    }

    @Test public void differentChatsWithoutTimestampsCannotBeOrdered() {
        ResearchFinder.Finding original = finding("old", "HZT",
                msg("assistant", "[OFFEN] Z8B-01 muss untersucht werden.", 0));
        List<ResearchTimeline.StatusEvidence> later = ResearchTimeline.collect("new", "Unbekannte Zeit",
                Collections.singletonList(msg("assistant", "Z8B-01 Status: CLOSED", 0)));
        assertEquals("NO_LATER", review(original, later).code);
    }

    @Test public void sameChatCanUseVisibleMessageOrderWhenTimeMissing() {
        List<ConversationLogic.Message> messages = Arrays.asList(
                msg("assistant", "[OFFEN] Z8B-01 muss untersucht werden.", 0),
                msg("assistant", "Z8B-01 Status: CLOSED", 0));
        ResearchFinder.Finding original = ResearchFinder.extract("same", "HZT", messages, 5).stream()
                .filter(f -> f.messageNumber == 1).findFirst().get();
        List<ResearchTimeline.StatusEvidence> events = ResearchTimeline.collect("same", "HZT", messages);
        ResearchTimeline.Review linked = review(original, events);
        assertEquals("LATER_CLOSURE", linked.code);
        assertEquals(2, linked.source.messageNumber);
    }

    @Test public void noAutomaticClosureForTwoDifferentIdsInOneFinding() {
        ResearchFinder.Finding original = finding("old", "Governance",
                msg("assistant", "K1-D NOT RELEASED und K1-E NOT ADMISSIBLE.", 1000));
        List<ResearchTimeline.StatusEvidence> later = ResearchTimeline.collect("new", "Review",
                Collections.singletonList(msg("assistant", "K1-D Status: RELEASED", 2000)));
        ResearchTimeline.Review linked = review(original, later);
        assertEquals("NO_ID", linked.code);
        assertNull(linked.source);
    }

    @Test public void hypotheticalCompletionIsNotStatusEvidence() {
        List<ConversationLogic.Message> text = Arrays.asList(
                msg("assistant", "Wenn Z8B-01 CLOSED wäre, könnten wir fortfahren.", 2000),
                msg("assistant", "Z8B-01 Status: CLOSED?", 2100),
                msg("assistant", "Z8B-01 Status: CLOSED, aber nicht bestätigt.", 2200));
        assertTrue(ResearchTimeline.collect("new", "Fiktion", text).isEmpty());
    }

    @Test public void negatedReleaseIsNeverAClosure() {
        ResearchFinder.Finding original = finding("old", "Governance",
                msg("assistant", "K1-D NOT RELEASED.", 1000));
        List<ResearchTimeline.StatusEvidence> later = ResearchTimeline.collect("new", "Gate",
                Collections.singletonList(msg("assistant", "K1-D bleibt NOT RELEASED.", 2000)));
        assertEquals("LATER_OPEN", review(original, later).code);
    }

    @Test public void userConditionalWithoutTaskIdIsNotPromotedToDecision() {
        ResearchFinder.Finding original = finding("userchat", "Wimpzilla",
                msg("user", "Nächster Schritt: Sie würden diese Wimpzilla-Masse "
                        + "als primären Dunkle-Materie-Kandidaten festlegen.", 1000));
        ResearchTimeline.Review linked = review(original, Collections.emptyList());
        assertEquals("NO_ID", linked.code);
        assertTrue(linked.summary.contains("Nutzerbeitrag"));
    }
}
