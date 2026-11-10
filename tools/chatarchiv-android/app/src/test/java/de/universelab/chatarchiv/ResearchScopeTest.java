package de.universelab.chatarchiv;

import org.junit.Test;

import java.util.Collections;
import java.util.List;

import static org.junit.Assert.assertEquals;

public final class ResearchScopeTest {
    private static ResearchFinder.Finding find(String title, String line) {
        List<ResearchFinder.Finding> findings = ResearchFinder.extract("id", title,
                Collections.singletonList(new ConversationLogic.Message("assistant", line)), 5);
        assertEquals(1, findings.size());
        return findings.get(0);
    }

    @Test public void organizationalActionInPhysicsChatIsNotAPhysicsBlocker() {
        ResearchFinder.Finding found = find("6D Hyperzeit Theorie",
                "1. Einreichung anlegen → blockiert");
        assertEquals("Blocker", found.kind);
        assertEquals(ResearchScope.ORGANIZATION, found.scope);
    }

    @Test public void unreleasedGateRemainsGovernance() {
        ResearchFinder.Finding found = find("HZT Konsistenzprüfung",
                "K1-D = NOT RELEASED.");
        assertEquals(ResearchScope.GOVERNANCE, found.scope);
    }

    @Test public void unresolvedNullmodeRemainsPhysics() {
        ResearchFinder.Finding found = find("HZT Konsistenzprüfung",
                "[OFFEN] Die Nullmoden-Norm ist nicht nachgewiesen.");
        assertEquals(ResearchScope.PHYSICS, found.scope);
    }

    @Test public void softwareProblemRemainsVisible() {
        ResearchFinder.Finding found = find("Hilfe Chat",
                "Blocker: Der Android APK-Export ist blockiert.");
        assertEquals(ResearchScope.SOFTWARE, found.scope);
    }

    @Test public void uncategorizedFindingStaysVisibleWithUnclearLabel() {
        ResearchFinder.Finding found = find("Allgemeine Prüfung",
                "[OFFEN] Eine konkrete Bedingung ist noch ungeklärt.");
        assertEquals(ResearchScope.UNCLEAR, found.scope);
    }

    @Test public void engineeringProblemRemainsEngineering() {
        ResearchFinder.Finding found = find("Raumschiff",
                "[OFFEN] Die Reaktor-Thermik ist noch nicht validiert.");
        assertEquals(ResearchScope.ENGINEERING, found.scope);
    }
}
