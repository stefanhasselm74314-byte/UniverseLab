package de.universelab.chatarchiv;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/** Extracts only the active, user-visible message path from a ChatGPT export. */
final class ConversationLogic {
    static final class Message {
        final String role;
        final String body;

        Message(String role, String body) {
            this.role = role;
            this.body = body;
        }
    }

    private ConversationLogic() { }

    static List<Message> visibleMessages(JSONObject conversation) {
        JSONObject mapping = conversation.optJSONObject("mapping");
        if (mapping == null) return Collections.emptyList();

        String nodeId = conversation.optString("current_node", "");
        List<Message> reversed = new ArrayList<>();
        Set<String> visited = new HashSet<>();

        // Export graphs may contain regenerated branches. Follow the current path
        // rather than merging all nodes into a falsely ordered conversation.
        while (!nodeId.isEmpty() && visited.add(nodeId) && visited.size() < 100000) {
            JSONObject node = mapping.optJSONObject(nodeId);
            if (node == null) break;
            Message message = fromNode(node);
            if (message != null) reversed.add(message);
            nodeId = node.optString("parent", "");
        }

        Collections.reverse(reversed);
        return reversed;
    }

    private static Message fromNode(JSONObject node) {
        JSONObject message = node.optJSONObject("message");
        if (message == null) return null;
        JSONObject author = message.optJSONObject("author");
        String role = author == null ? "" : author.optString("role", "");
        if (!"user".equals(role) && !"assistant".equals(role)) return null;

        JSONObject metadata = message.optJSONObject("metadata");
        if (metadata != null && metadata.optBoolean("is_visually_hidden_from_conversation", false)) return null;
        String channel = metadata == null ? "" : metadata.optString("channel", "");
        if ("analysis".equals(channel) || "justify".equals(channel)
                || "confidence".equals(channel) || "summary".equals(channel)) return null;

        if ("assistant".equals(role)) {
            String recipient = message.optString("recipient", "all");
            if (!"all".equals(recipient) && !"".equals(recipient)) return null;
        }

        JSONObject content = message.optJSONObject("content");
        if (content == null) return null;
        String contentType = content.optString("content_type", "");
        if (!"text".equals(contentType) && !"multimodal_text".equals(contentType)) return null;

        JSONArray parts = content.optJSONArray("parts");
        if (parts == null) return null;
        StringBuilder body = new StringBuilder();
        boolean attachment = false;
        for (int i = 0; i < parts.length(); i++) {
            Object part = parts.opt(i);
            if (part instanceof String) {
                if (body.length() > 0) body.append('\n');
                body.append((String) part);
            } else if (part instanceof JSONObject) {
                JSONObject object = (JSONObject) part;
                String text = object.optString("text", "");
                if (!text.isEmpty()) {
                    if (body.length() > 0) body.append('\n');
                    body.append(text);
                } else {
                    attachment = true;
                }
            }
        }
        if (attachment) {
            if (body.length() > 0) body.append("\n\n");
            body.append("[Medienanhang: benötigt zusätzliche Exportdatei]");
        }
        String visible = body.toString().trim();
        if (visible.isEmpty()) return null;
        return new Message(role, visible);
    }

    static String indexText(JSONObject conversation) {
        StringBuilder search = new StringBuilder();
        for (Message message : visibleMessages(conversation)) {
            search.append(message.body).append('\n');
        }
        return search.toString().toLowerCase(Locale.ROOT);
    }
}
