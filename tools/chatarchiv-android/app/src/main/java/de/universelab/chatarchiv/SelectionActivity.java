package de.universelab.chatarchiv;

import android.app.Activity;
import android.graphics.Typeface;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import org.json.JSONObject;

import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

/** Single selectable TextView, including speaker changes across messages. */
public final class SelectionActivity extends Activity {
    private static final int MAX_SELECTABLE_CHARS = 2_000_000;
    private final ExecutorService loader = Executors.newSingleThreadExecutor();
    private final AtomicInteger renderVersion = new AtomicInteger();
    private TextView body;
    private TextView hint;
    private String raw = "";

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        String id = getIntent().getStringExtra("chatId");
        if (id == null || id.isEmpty()) { finish(); return; }

        LinearLayout root = Ui.column(this, 12);
        setContentView(root);
        Button back = Ui.button(this, "‹ Zurück zum Gespräch");
        back.setOnClickListener(view -> finish());
        root.addView(back);

        hint = Ui.text(this,
                "Durchgehende Markieransicht: lange auf Text drücken und Markierungsgriffe ziehen. "
                        + "Hier kannst du auch über die Grenzen einzelner Beiträge hinweg auswählen.",
                13, false);
        hint.setTextColor(Ui.ACCENT);
        root.addView(hint);

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        body = Ui.text(this, "Text wird vorbereitet …", 16, false);
        body.setTextIsSelectable(true);
        body.setLineSpacing(Ui.dp(this, 2), 1.08f);
        body.setPadding(Ui.dp(this, 5), Ui.dp(this, 15), Ui.dp(this, 5), Ui.dp(this, 20));
        scroll.addView(body);
        root.addView(scroll, Ui.fillRemaining());

        loader.execute(() -> {
            try {
                JSONObject chat = new ChatStore(this).loadConversation(id);
                List<ConversationLogic.Message> messages = ConversationLogic.visibleMessages(chat);
                String selection = ExportFormatter.selectionText(chat.optString("title", "Gespräch"),
                        messages, MAX_SELECTABLE_CHARS);
                runOnUiThread(() -> {
                    if (isFinishing() || isDestroyed()) return;
                    raw = selection;
                    render();
                });
            } catch (Exception exception) {
                runOnUiThread(() -> hint.setText("Markieransicht nicht lesbar: " + exception.getMessage()));
            }
        });
    }

    private void render() {
        int mode = getSharedPreferences("chatarchiv-display", MODE_PRIVATE).getInt("formula-mode", 0);
        int serial = renderVersion.incrementAndGet();
        hint.setText("Durchgehender Text · lange drücken und auch über Beitragsgrenzen markieren. "
                + "Für den gesamten Originalchat: Exportieren → JSON oder Markdown.");
        body.setText("Formelansicht wird vorbereitet …");
        loader.execute(() -> {
            String value = mode == 1 ? MathUnicode.convert(raw) : raw;
            runOnUiThread(() -> {
                if (renderVersion.get() != serial || isFinishing() || isDestroyed()) return;
                body.setTypeface(mode == 2 ? Typeface.MONOSPACE : Typeface.DEFAULT);
                body.setText(value);
                body.setTextIsSelectable(true);
            });
        });
    }

    @Override protected void onDestroy() {
        renderVersion.incrementAndGet();
        loader.shutdownNow();
        super.onDestroy();
    }
}
