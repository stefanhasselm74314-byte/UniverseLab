package de.universelab.chatarchiv;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class ConversationActivity extends Activity {
    private final ExecutorService loader = Executors.newSingleThreadExecutor();
    private final List<ConversationLogic.Message> full = new ArrayList<>();
    private final List<ConversationLogic.Message> visible = new ArrayList<>();
    private TextView information;
    private EditText filter;
    private ConversationAdapter adapter;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        String id = getIntent().getStringExtra("chatId");
        if (id == null || id.isEmpty()) { finish(); return; }

        LinearLayout root = Ui.column(this, 12);
        setContentView(root);
        android.widget.Button back = Ui.button(this, "‹ Zurück zum Archiv");
        back.setOnClickListener(view -> finish());
        root.addView(back);

        information = Ui.text(this, "Gespräch wird geladen …", 15, true);
        information.setTextColor(Ui.ACCENT);
        root.addView(information);

        filter = new EditText(this);
        filter.setSingleLine(true);
        filter.setHint("In diesem Gespräch suchen …");
        filter.setTextColor(Ui.TEXT);
        filter.setHintTextColor(Ui.MUTED);
        filter.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Ui.ACCENT));
        root.addView(filter);
        filter.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) { }
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) { applyFilter(); }
            @Override public void afterTextChanged(Editable editable) { }
        });

        ListView list = new ListView(this);
        list.setDivider(null);
        list.setDividerHeight(Ui.dp(this, 9));
        list.setFastScrollEnabled(true);
        adapter = new ConversationAdapter();
        list.setAdapter(adapter);
        root.addView(list, Ui.fillRemaining());

        loader.execute(() -> {
            try {
                ChatStore store = new ChatStore(this);
                JSONObject conversation = store.loadConversation(id);
                List<ConversationLogic.Message> messages = ConversationLogic.visibleMessages(conversation);
                String title = conversation.optString("title", "Gespräch");
                runOnUiThread(() -> {
                    if (isFinishing() || isDestroyed()) return;
                    full.clear();
                    full.addAll(messages);
                    information.setText(title + " · " + full.size() + " sichtbare Beiträge");
                    applyFilter();
                });
            } catch (IOException exception) {
                runOnUiThread(() -> information.setText("Lesefehler: " + exception.getMessage()));
            }
        });
    }

    private void applyFilter() {
        if (adapter == null) return;
        String query = filter.getText().toString().trim().toLowerCase(Locale.ROOT);
        visible.clear();
        if (query.isEmpty()) visible.addAll(full);
        else for (ConversationLogic.Message message : full) {
            if (message.body.toLowerCase(Locale.ROOT).contains(query)) visible.add(message);
        }
        adapter.notifyDataSetChanged();
    }

    @Override protected void onDestroy() {
        loader.shutdownNow();
        super.onDestroy();
    }

    private final class ConversationAdapter extends BaseAdapter {
        @Override public int getCount() { return visible.size(); }
        @Override public Object getItem(int position) { return visible.get(position); }
        @Override public long getItemId(int position) { return position; }

        @Override public View getView(int position, View existing, ViewGroup parent) {
            ConversationLogic.Message message = visible.get(position);
            LinearLayout panel = Ui.column(ConversationActivity.this, 12);
            panel.setBackgroundColor(Ui.SURFACE);
            LinearLayout bar = Ui.row(ConversationActivity.this);
            TextView role = Ui.text(ConversationActivity.this,
                    "user".equals(message.role) ? "DU" : "CHATGPT", 12, true);
            role.setTextColor(Ui.ACCENT);
            bar.addView(role, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1));
            android.widget.Button copy = Ui.button(ConversationActivity.this, "Kopieren");
            bar.addView(copy);
            copy.setOnClickListener(view -> {
                ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
                clipboard.setPrimaryClip(ClipData.newPlainText("Gesprächsbeitrag", message.body));
                Toast.makeText(ConversationActivity.this, "Beitrag kopiert", Toast.LENGTH_SHORT).show();
            });
            panel.addView(bar);
            TextView body = Ui.text(ConversationActivity.this, message.body, 16, false);
            body.setTextIsSelectable(true);
            body.setLineSpacing(Ui.dp(ConversationActivity.this, 2), 1.08f);
            panel.addView(body);
            return panel;
        }
    }
}
