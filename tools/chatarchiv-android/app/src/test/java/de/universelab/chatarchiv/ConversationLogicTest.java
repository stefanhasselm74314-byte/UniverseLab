package de.universelab.chatarchiv;

import org.json.JSONObject;
import org.junit.Test;

import java.util.List;

import static org.junit.Assert.assertEquals;

public final class ConversationLogicTest {
    @Test public void followsActiveBranchAndOmitsToolsAndThoughts() throws Exception {
        JSONObject chat = new JSONObject("{" +
                "\"current_node\":\"final\",\"mapping\":{" +
                "\"root\":{\"parent\":null,\"message\":null}," +
                "\"a\":{\"parent\":\"root\",\"message\":{" +
                "\"author\":{\"role\":\"user\"},\"content\":{\"content_type\":\"text\",\"parts\":[\"Hallo\"]}}}," +
                "\"hidden\":{\"parent\":\"a\",\"message\":{" +
                "\"author\":{\"role\":\"assistant\"},\"content\":{\"content_type\":\"thoughts\",\"parts\":[]}}}," +
                "\"tool\":{\"parent\":\"hidden\",\"message\":{" +
                "\"author\":{\"role\":\"tool\"},\"content\":{\"content_type\":\"text\",\"parts\":[\"secret\"]}}}," +
                "\"final\":{\"parent\":\"tool\",\"message\":{" +
                "\"author\":{\"role\":\"assistant\"},\"recipient\":\"all\",\"content\":{\"content_type\":\"text\",\"parts\":[\"Antwort\"]}}}," +
                "\"abandoned\":{\"parent\":\"root\",\"message\":{" +
                "\"author\":{\"role\":\"assistant\"},\"content\":{\"content_type\":\"text\",\"parts\":[\"Nicht aktiv\"]}}}}}");
        List<ConversationLogic.Message> messages = ConversationLogic.visibleMessages(chat);
        assertEquals(2, messages.size());
        assertEquals("Hallo", messages.get(0).body);
        assertEquals("Antwort", messages.get(1).body);
    }

    @Test public void terminatesOnCycleAndHandlesMissingNodes() throws Exception {
        JSONObject chat = new JSONObject("{\"current_node\":\"one\",\"mapping\":{" +
                "\"one\":{\"parent\":\"one\",\"message\":null}}}");
        assertEquals(0, ConversationLogic.visibleMessages(chat).size());
        assertEquals("", ConversationLogic.indexText(chat));
    }

    @Test public void marksUnavailableMedia() throws Exception {
        JSONObject chat = new JSONObject("{\"current_node\":\"one\",\"mapping\":{" +
                "\"one\":{\"parent\":null,\"message\":{" +
                "\"author\":{\"role\":\"user\"},\"content\":{\"content_type\":\"multimodal_text\"," +
                "\"parts\":[\"Ein Bild\",{\"content_type\":\"image_asset_pointer\"}]}}}}}");
        List<ConversationLogic.Message> messages = ConversationLogic.visibleMessages(chat);
        assertEquals(1, messages.size());
        assertEquals(true, messages.get(0).body.contains("Medienanhang"));
    }
}
