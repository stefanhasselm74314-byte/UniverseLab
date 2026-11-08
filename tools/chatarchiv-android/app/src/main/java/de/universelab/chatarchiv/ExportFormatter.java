package de.universelab.chatarchiv;

import org.json.JSONObject;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.util.List;

/** Offline, text-only export; raw JSON preserves the entire stored conversation graph. */
final class ExportFormatter {
    enum Format {
        JSON("Vollständige Chat-JSON (alle Zweige)", "application/json", "json"),
        MARKDOWN("Lesbarer Chat als Markdown", "text/markdown", "md"),
        TEXT("Lesbarer Chat als Text", "text/plain", "txt"),
        HTML("Lesbarer Chat als HTML (Unicode-Formeln)", "text/html", "html");

        final String label;
        final String mime;
        final String extension;
        Format(String label, String mime, String extension) {
            this.label = label;
            this.mime = mime;
            this.extension = extension;
        }
    }

    static String fileName(String title, Format format) {
        String stem = (title == null ? "Gespräch" : title)
                .replaceAll("[^\\p{L}\\p{N} ._-]", "_").trim();
        if (stem.isEmpty()) stem = "Gespräch";
        if (stem.length() > 68) stem = stem.substring(0, 68).trim();
        return "ChatArchiv_" + stem + "." + format.extension;
    }

    static void write(JSONObject conversation, Format format, OutputStream destination) throws IOException {
        Writer writer = new BufferedWriter(new OutputStreamWriter(destination, StandardCharsets.UTF_8), 65536);
        String title = conversation.optString("title", "Gespräch");
        String id = conversation.optString("id", "");
        if (format == Format.JSON) {
            // This includes the complete mapping, active node, metadata and
            // alternative reply branches. External media files are not stored.
            writer.write(conversation.toString());
        } else if (format == Format.HTML) {
            writer.write("<!doctype html><html lang=\"de\"><head><meta charset=\"UTF-8\">"
                    + "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
                    + "<title>");
            writer.write(escapeHtml(title));
            writer.write("</title><style>body{font:16px/1.55 system-ui,sans-serif;max-width:980px;"
                    + "margin:2rem auto;padding:0 1rem;background:#0b111a;color:#edf4fc}"
                    + "article{background:#192330;margin:1.1rem 0;padding:1rem;border-radius:10px}"
                    + "h2{font-size:1rem;color:#81c5ff}pre{white-space:pre-wrap;overflow-wrap:anywhere;"
                    + "font:inherit;margin:0}small{color:#a5b9cd}"
                    + "@media print{body{background:white;color:black}article{background:white;"
                    + "border:1px solid #bbb;break-inside:avoid}h2,small{color:black}}</style></head><body><h1>");
            writer.write(escapeHtml(title));
            writer.write("</h1><small>Chat-ID: ");
            writer.write(escapeHtml(id));
            writer.write(" · Aktiver Gesprächspfad · Medienanhänge nicht eingebettet</small>");
            for (ConversationLogic.Message message : ConversationLogic.visibleMessages(conversation)) {
                writer.write("<article><h2>");
                writer.write("user".equals(message.role) ? "DU" : "CHATGPT");
                writer.write("</h2><pre>");
                writer.write(escapeHtml(MathUnicode.convert(message.body)));
                writer.write("</pre></article>");
            }
            writer.write("</body></html>");
        } else {
            if (format == Format.MARKDOWN) {
                writer.write("# " + title.replace("\n", " ") + "\n\n");
                writer.write("Chat-ID: `" + id + "` · Aktiver Gesprächspfad\n\n");
            } else {
                writer.write(title + "\nChat-ID: " + id + "\nAktiver Gesprächspfad\n\n");
            }
            for (ConversationLogic.Message message : ConversationLogic.visibleMessages(conversation)) {
                String who = "user".equals(message.role) ? "DU" : "CHATGPT";
                writer.write(format == Format.MARKDOWN ? "## " + who + "\n\n" : "=== " + who + " ===\n");
                writer.write(message.body);
                writer.write(format == Format.MARKDOWN ? "\n\n---\n\n" : "\n\n");
            }
        }
        writer.flush();
    }

    static String selectionText(String title, List<ConversationLogic.Message> messages, int maximum) {
        StringBuilder builder = new StringBuilder(Math.min(maximum, 65536));
        builder.append(title).append("\n\n");
        for (ConversationLogic.Message message : messages) {
            String part = ("user".equals(message.role) ? "DU" : "CHATGPT") + "\n\n"
                    + message.body + "\n\n────────────────────────\n\n";
            if (builder.length() + part.length() > maximum) {
                builder.append("[Weitere Inhalte nicht in der Markieransicht geladen. "
                        + "Für einen vollständigen Chat den Export verwenden.]");
                break;
            }
            builder.append(part);
        }
        return builder.toString();
    }

    private static String escapeHtml(String text) {
        return text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace("\"", "&quot;");
    }

    private ExportFormatter() { }
}
