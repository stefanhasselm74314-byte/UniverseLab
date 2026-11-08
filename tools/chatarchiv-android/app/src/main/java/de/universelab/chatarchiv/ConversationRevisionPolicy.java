package de.universelab.chatarchiv;

import org.json.JSONObject;

/**
 * Conservative protection against importing older snapshots over newer chats.
 * The file's timestamp is only used when both sides expose a positive numeric
 * update_time; missing or tied timestamps require manual review.
 */
final class ConversationRevisionPolicy {
    enum Action { ACCEPT_NEWER, KEEP_OLDER, REQUIRE_REVIEW }

    static Action decide(JSONObject stored, JSONObject incoming) {
        double before = updateTime(stored);
        double after = updateTime(incoming);
        if (!Double.isFinite(before) || !Double.isFinite(after)
                || before <= 0.0 || after <= 0.0) {
            return Action.REQUIRE_REVIEW;
        }
        if (after > before + 0.001) return Action.ACCEPT_NEWER;
        if (after < before - 0.001) return Action.KEEP_OLDER;
        return Action.REQUIRE_REVIEW;
    }

    private static double updateTime(JSONObject chat) {
        Object value = chat.opt("update_time");
        return value instanceof Number ? ((Number) value).doubleValue() : Double.NaN;
    }

    private ConversationRevisionPolicy() {}
}
