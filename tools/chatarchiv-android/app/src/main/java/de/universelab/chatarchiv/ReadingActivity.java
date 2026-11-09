package de.universelab.chatarchiv;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.graphics.Typeface;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;

import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Read one long source contribution with selectable text and an explicit,
 * pixel-based position slider. Never alters or uploads chat data.
 */
public final class ReadingActivity extends Activity {
    private static final int MAX_DISPLAY_CHARACTERS = 2_000_000;
    private final ExecutorService loader = Executors.newSingleThreadExecutor();
    private String originalBody = "";

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        String chatId = getIntent().getStringExtra("chatId");
        int sourceIndex = getIntent().getIntExtra("sourceMessageIndex", -1);
        if (chatId == null || chatId.isEmpty() || sourceIndex < 0) {
            finish();
            return;
        }

        LinearLayout root = Ui.column(this, 12);
        setContentView(root);
        Ui.applySystemBarInsets(root);

        Button back = Ui.button(this, "‹ Zurück zum Gespräch");
        back.setOnClickListener(view -> finish());
        root.addView(back);

        TextView label = Ui.text(this, "Beitrag wird geladen …", 15, true);
        label.setTextColor(Ui.ACCENT);
        root.addView(label);

        Button copy = Ui.button(this, "Vollständigen Beitrag kopieren");
        copy.setEnabled(false);
        copy.setOnClickListener(view -> {
            ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
            clipboard.setPrimaryClip(ClipData.newPlainText("Gesprächsbeitrag", originalBody));
            Toast.makeText(this, "Vollständiger Beitrag kopiert", Toast.LENGTH_SHORT).show();
        });
        root.addView(copy);

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(false);
        scroll.setVerticalScrollBarEnabled(true);
        scroll.setScrollbarFadingEnabled(false);
        scroll.setScrollBarStyle(View.SCROLLBARS_INSIDE_INSET);
        scroll.setPadding(0, 0, Ui.dp(this, 10), 0);

        TextView body = Ui.text(this, "", 16, false);
        body.setTextIsSelectable(true);
        body.setLineSpacing(Ui.dp(this, 2), 1.08f);
        scroll.addView(body, new ScrollView.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
        root.addView(scroll, Ui.fillRemaining());

        TextView position = Ui.text(this, "Textposition · 0 %", 12, false);
        position.setTextColor(Ui.ACCENT);
        root.addView(position);
        SeekBar seek = new SeekBar(this);
        seek.setMax(ScrollPosition.MAX_PROGRESS);
        seek.setEnabled(false);
        root.addView(seek);

        seek.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar bar, int progress, boolean user) {
                if (!user) return;
                int offset = ScrollPosition.offsetFor(progress, body.getHeight(), scroll.getHeight());
                scroll.scrollTo(0, offset);
                position.setText("Textposition · " + Math.round(progress / 10.0f) + " %");
            }
            @Override public void onStartTrackingTouch(SeekBar bar) { }
            @Override public void onStopTrackingTouch(SeekBar bar) { }
        });
        scroll.setOnScrollChangeListener((view, x, y, oldX, oldY) -> {
            int progress = ScrollPosition.progressFor(y, body.getHeight(), scroll.getHeight());
            seek.setProgress(progress);
            position.setText("Textposition · " + Math.round(progress / 10.0f) + " %");
        });

        loader.execute(() -> {
            try {
                JSONObject conversation = new ChatStore(this).loadConversation(chatId);
                List<ConversationLogic.Message> messages =
                        ConversationLogic.visibleMessages(conversation);
                if (sourceIndex >= messages.size()) throw new IllegalStateException("Beitrag fehlt");
                ConversationLogic.Message message = messages.get(sourceIndex);
                String raw = message.body;
                boolean shortened = raw.length() > MAX_DISPLAY_CHARACTERS;
                String displayed = shortened
                        ? raw.substring(0, MAX_DISPLAY_CHARACTERS)
                                + "\n\n[Anzeige begrenzt; für den vollständigen Text bitte exportieren.]"
                        : raw;
                int mode = getSharedPreferences("chatarchiv-display", MODE_PRIVATE)
                        .getInt("formula-mode", 0);
                if (mode == 1) displayed = MathUnicode.convert(displayed);
                String finalDisplayed = displayed;
                runOnUiThread(() -> {
                    if (isFinishing() || isDestroyed()) return;
                    originalBody = raw;
                    body.setText(finalDisplayed);
                    if (mode == 2) body.setTypeface(Typeface.MONOSPACE);
                    label.setText(("user".equals(message.role) ? "DU" : "CHATGPT")
                            + " · Beitrag " + (sourceIndex + 1) + " von " + messages.size()
                            + (shortened ? " · Vorschau begrenzt" : ""));
                    copy.setEnabled(true);
                    body.post(() -> seek.setEnabled(body.getHeight() > scroll.getHeight()));
                });
            } catch (Exception exception) {
                runOnUiThread(() -> {
                    if (!isFinishing() && !isDestroyed())
                        label.setText("Lesefehler: " + exception.getMessage());
                });
            }
        });
    }

    @Override protected void onDestroy() {
        loader.shutdownNow();
        super.onDestroy();
    }
}
