package de.universelab.chatarchiv;

import org.json.JSONObject;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

public final class ConversationRevisionPolicyTest {
    private static JSONObject chat(Object time) throws Exception {
        JSONObject value = new JSONObject();
        if (time != null) value.put("update_time", time);
        return value;
    }

    @Test public void protectsNewerStoredChatAgainstOldExport() throws Exception {
        assertEquals(ConversationRevisionPolicy.Action.KEEP_OLDER,
                ConversationRevisionPolicy.decide(chat(200.0), chat(100.0)));
    }

    @Test public void permitsOnlyStrictlyNewerSnapshot() throws Exception {
        assertEquals(ConversationRevisionPolicy.Action.ACCEPT_NEWER,
                ConversationRevisionPolicy.decide(chat(100.0), chat(200.0)));
    }

    @Test public void marksEqualTimestampAsConflict() throws Exception {
        assertEquals(ConversationRevisionPolicy.Action.REQUIRE_REVIEW,
                ConversationRevisionPolicy.decide(chat(100.0), chat(100.0)));
    }

    @Test public void refusesMissingAndUntrustedTimestamps() throws Exception {
        assertEquals(ConversationRevisionPolicy.Action.REQUIRE_REVIEW,
                ConversationRevisionPolicy.decide(chat(null), chat(200.0)));
        assertEquals(ConversationRevisionPolicy.Action.REQUIRE_REVIEW,
                ConversationRevisionPolicy.decide(chat(100.0), chat("2026-06-04")));
        assertEquals(ConversationRevisionPolicy.Action.REQUIRE_REVIEW,
                ConversationRevisionPolicy.decide(chat(0.0), chat(300.0)));
    }
}
