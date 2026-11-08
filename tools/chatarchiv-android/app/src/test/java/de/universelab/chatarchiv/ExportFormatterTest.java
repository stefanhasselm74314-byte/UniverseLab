package de.universelab.chatarchiv;

import org.json.JSONObject;
import org.junit.Test;

import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

public final class ExportFormatterTest {
    private static JSONObject example() throws Exception {
        return new JSONObject("{\"id\":\"uuid-1\",\"title\":\"A < B\",\"current_node\":\"bot\",\"mapping\":{"
                + "\"root\":{\"parent\":null,\"message\":null},"
                + "\"u\":{\"parent\":\"root\",\"message\":{\"author\":{\"role\":\"user\"},"
                + "\"content\":{\"content_type\":\"text\",\"parts\":[\"Test\"]}}},"
                + "\"bot\":{\"parent\":\"u\",\"message\":{\"author\":{\"role\":\"assistant\"},"
                + "\"content\":{\"content_type\":\"text\",\"parts\":[\"\\\\alpha = 1 < 2\"]}}},"
                + "\"other\":{\"parent\":\"root\",\"message\":{\"author\":{\"role\":\"assistant\"},"
                + "\"content\":{\"content_type\":\"text\",\"parts\":[\"Abzweigung\"]}}}}}");
    }

    @Test public void rawJsonPreservesInactiveBranches() throws Exception {
        ByteArrayOutputStream stream = new ByteArrayOutputStream();
        ExportFormatter.write(example(), ExportFormatter.Format.JSON, stream);
        JSONObject exported = new JSONObject(stream.toString(StandardCharsets.UTF_8.name()));
        assertTrue(exported.getJSONObject("mapping").has("other"));
        assertEquals("bot", exported.getString("current_node"));
    }

    @Test public void htmlEscapesMarkupAndOnlyExportsVisiblePath() throws Exception {
        ByteArrayOutputStream stream = new ByteArrayOutputStream();
        ExportFormatter.write(example(), ExportFormatter.Format.HTML, stream);
        String html = stream.toString(StandardCharsets.UTF_8.name());
        assertTrue(html.contains("A &lt; B"));
        assertTrue(html.contains("α = 1 &lt; 2"));
        assertTrue(!html.contains("Abzweigung"));
        assertEquals("ChatArchiv_A _ B.html", ExportFormatter.fileName("A < B", ExportFormatter.Format.HTML));
    }
}
