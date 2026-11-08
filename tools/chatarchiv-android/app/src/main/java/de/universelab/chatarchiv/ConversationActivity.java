package de.universelab.chatarchiv;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;

import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class ConversationActivity extends Activity {
    private static final int SAVE_CHAT = 811;
    private static final String DISPLAY_PREFS = "chatarchiv-display";
    private static final String DISPLAY_MODE = "formula-mode";
    private final ExecutorService loader = Executors.newSingleThreadExecutor();
    private final List<ConversationLogic.Message> full = new ArrayList<>();
    private final List<ConversationLogic.Message> visible = new ArrayList<>();
    private TextView information;
    private EditText filter;
    private ConversationAdapter adapter;
    private String chatId;
    private String chatTitle = "Gespräch";
    private int displayMode;
    private Button exportButton;
    private Button displayButton;
    private ExportFormatter.Format pendingFormat;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        chatId = getIntent().getStringExtra("chatId");
        if (chatId == null || chatId.isEmpty()) { finish(); return; }
        displayMode = getSharedPreferences(DISPLAY_PREFS, MODE_PRIVATE).getInt(DISPLAY_MODE, 0);
        if (state != null && state.containsKey("pending-format")) {
            int ordinal = state.getInt("pending-format", -1);
            if (ordinal >= 0 && ordinal < ExportFormatter.Format.values().length) {
                pendingFormat = ExportFormatter.Format.values()[ordinal];
            }
        }

        LinearLayout root = Ui.column(this, 12);
        setContentView(root);
        android.widget.Button back = Ui.button(this, "‹ Zurück zum Archiv");
        back.setOnClickListener(view -> finish());
        root.addView(back);

        information = Ui.text(this, "Gespräch wird geladen …", 15, true);
        information.setTextColor(Ui.ACCENT);
        root.addView(information);

        LinearLayout tools = Ui.row(this);
        exportButton = Ui.button(this, "Exportieren");
        exportButton.setEnabled(false);
        exportButton.setOnClickListener(view -> showExportOptions());
        displayButton = Ui.button(this, modeLabel());
        displayButton.setOnClickListener(view -> showDisplayOptions());
        Button selectButton = Ui.button(this, "Markieren");
        selectButton.setOnClickListener(view -> {
            Intent intent = new Intent(this, SelectionActivity.class);
            intent.putExtra("chatId", chatId);
            startActivity(intent);
        });
        tools.addView(exportButton, Ui.weight(1));
        tools.addView(displayButton, Ui.weight(1));
        tools.addView(selectButton, Ui.weight(1));
        root.addView(tools);

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
                JSONObject conversation = store.loadConversation(chatId);
                List<ConversationLogic.Message> messages = ConversationLogic.visibleMessages(conversation);
                String title = conversation.optString("title", "Gespräch");
                runOnUiThread(() -> {
                    if (isFinishing() || isDestroyed()) return;
                    full.clear();
                    full.addAll(messages);
                    chatTitle = title;
                    information.setText(title + " · " + full.size() + " sichtbare Beiträge");
                    exportButton.setEnabled(true);
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

    private String modeLabel() {
        return displayMode == 1 ? "Unicode" : displayMode == 2 ? "Monospace" : "Original";
    }

    private void showDisplayOptions() {
        String[] choices = {"Original (unverändert)", "Unicode (häufige LaTeX-Formeln)",
                "Monospace (Quelltext)"};
        new AlertDialog.Builder(this).setTitle("Formeldarstellung")
                .setSingleChoiceItems(choices, displayMode, (dialog, which) -> {
                    displayMode = which;
                    getSharedPreferences(DISPLAY_PREFS, MODE_PRIVATE)
                            .edit().putInt(DISPLAY_MODE, displayMode).apply();
                    displayButton.setText(modeLabel());
                    adapter.notifyDataSetChanged();
                    dialog.dismiss();
                }).setNegativeButton("Abbrechen", null).show();
    }

    private void showExportOptions() {
        ExportFormatter.Format[] formats = ExportFormatter.Format.values();
        String[] names = new String[formats.length];
        for (int i = 0; i < names.length; i++) names[i] = formats[i].label;
        new AlertDialog.Builder(this).setTitle("Gespräch vollständig exportieren")
                .setItems(names, (dialog, which) -> {
                    pendingFormat = formats[which];
                    Intent save = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                    save.addCategory(Intent.CATEGORY_OPENABLE);
                    save.setType(pendingFormat.mime);
                    save.putExtra(Intent.EXTRA_TITLE, ExportFormatter.fileName(chatTitle, pendingFormat));
                    save.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
                    startActivityForResult(save, SAVE_CHAT);
                }).setNegativeButton("Abbrechen", null).show();
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != SAVE_CHAT || resultCode != RESULT_OK || data == null
                || data.getData() == null || pendingFormat == null) return;
        Uri destination = data.getData();
        ExportFormatter.Format format = pendingFormat;
        pendingFormat = null;
        exportButton.setEnabled(false);
        information.setText("Chat-Export wird gespeichert …");
        loader.execute(() -> {
            try (OutputStream output = getContentResolver().openOutputStream(destination, "w")) {
                if (output == null) throw new IOException("Speicherziel nicht beschreibbar");
                JSONObject conversation = new ChatStore(this).loadConversation(chatId);
                ExportFormatter.write(conversation, format, output);
                runOnUiThread(() -> {
                    if (isFinishing() || isDestroyed()) return;
                    information.setText(chatTitle + " · " + full.size() + " sichtbare Beiträge");
                    exportButton.setEnabled(true);
                    Toast.makeText(this, "Chat als " + format.extension.toUpperCase(Locale.ROOT)
                            + " gespeichert", Toast.LENGTH_LONG).show();
                });
            } catch (Exception exception) {
                runOnUiThread(() -> {
                    if (isFinishing() || isDestroyed()) return;
                    information.setText("Exportfehler: " + exception.getMessage());
                    exportButton.setEnabled(true);
                });
            }
        });
    }

    @Override protected void onSaveInstanceState(Bundle outState) {
        if (pendingFormat != null) outState.putInt("pending-format", pendingFormat.ordinal());
        super.onSaveInstanceState(outState);
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
            String shown = displayMode == 1 ? MathUnicode.convert(message.body) : message.body;
            TextView body = Ui.text(ConversationActivity.this, shown, 16, false);
            if (displayMode == 2) body.setTypeface(Typeface.MONOSPACE);
            body.setTextIsSelectable(true);
            body.setLineSpacing(Ui.dp(ConversationActivity.this, 2), 1.08f);
            panel.addView(body);
            return panel;
        }
    }
}
