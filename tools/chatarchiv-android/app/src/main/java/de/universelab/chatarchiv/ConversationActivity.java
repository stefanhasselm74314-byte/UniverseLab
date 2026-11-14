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
import android.widget.SeekBar;
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
    private ListView list;
    private Button jumpButton;
    private String chatId;
    private String archivedDigest;
    private String chatTitle = "Gespräch";
    private Button versionsButton;
    private int displayMode;
    private Button exportButton;
    private Button displayButton;
    private ExportFormatter.Format pendingFormat;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        chatId = getIntent().getStringExtra("chatId");
        archivedDigest = getIntent().getStringExtra("archivedDigest");
        if (chatId == null || chatId.isEmpty()) { finish(); return; }
        final int focusMessage = getIntent().getIntExtra("focusMessageIndex", -1);
        displayMode = getSharedPreferences(DISPLAY_PREFS, MODE_PRIVATE).getInt(DISPLAY_MODE, 0);
        if (state != null && state.containsKey("pending-format")) {
            int ordinal = state.getInt("pending-format", -1);
            if (ordinal >= 0 && ordinal < ExportFormatter.Format.values().length) {
                pendingFormat = ExportFormatter.Format.values()[ordinal];
            }
        }

        LinearLayout root = Ui.column(this, 12);
        setContentView(root);
        Ui.applySystemBarInsets(root);
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
        if (archivedDigest != null) {
            // An archived view must not accidentally export/mark/read the current version.
            exportButton.setVisibility(View.GONE);
            selectButton.setVisibility(View.GONE);
        } else {
            versionsButton = Ui.button(this, "Gesicherte Altversionen prüfen");
            versionsButton.setEnabled(false);
            versionsButton.setOnClickListener(view -> showArchivedVersions());
            root.addView(versionsButton);
        }

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

        jumpButton = Ui.button(this, "Zu Beitrag springen");
        jumpButton.setEnabled(false);
        jumpButton.setOnClickListener(view -> showJumpDialog());
        root.addView(jumpButton);

        list = new WideGripListView(this);
        list.setDivider(null);
        list.setDividerHeight(Ui.dp(this, 9));
        Ui.configurePersistentFastScroll(list);
        adapter = new ConversationAdapter();
        list.setAdapter(adapter);
        root.addView(list, Ui.fillRemaining());

        loader.execute(() -> {
            try {
                ChatStore store = new ChatStore(this);
                JSONObject conversation = archivedDigest == null
                        ? store.loadConversation(chatId) : store.loadArchivedVersion(chatId, archivedDigest);
                List<ChatStore.SavedVersion> saved = archivedDigest == null
                        ? store.listArchivedVersions(chatId) : java.util.Collections.emptyList();
                List<ConversationLogic.Message> messages = ConversationLogic.visibleMessages(conversation);
                // Show the local alias for the current version; archived snapshots
                // retain their own original title and are never rewritten.
                ChatStore.Entry metadata = archivedDigest == null ? store.entryForDisplay(chatId) : null;
                String title = metadata != null
                        ? metadata.title : conversation.optString("title", "Gespräch");
                runOnUiThread(() -> {
                    if (isFinishing() || isDestroyed()) return;
                    full.clear();
                    full.addAll(messages);
                    chatTitle = title;
                    information.setText((archivedDigest == null ? "" : "ALTVERSION · NUR LESEN\n")
                            + title + " · " + full.size() + " sichtbare Beiträge");
                    if (versionsButton != null) {
                        versionsButton.setEnabled(true);
                        versionsButton.setText(saved.isEmpty() ? "Keine gesicherten Altversionen"
                                : "Gesicherte Altversionen ansehen · " + saved.size());
                    }
                    if (archivedDigest == null) exportButton.setEnabled(true);
                    applyFilter();
                    if (focusMessage >= 0 && focusMessage < full.size()) {
                        list.post(() -> list.setSelection(focusMessage));
                    }
                });
            } catch (IOException exception) {
                runOnUiThread(() -> information.setText("Lesefehler: " + exception.getMessage()));
            }
        });
    }

    private void showArchivedVersions() {
        if (archivedDigest != null || versionsButton == null) return;
        versionsButton.setEnabled(false);
        loader.execute(() -> {
            try {
                List<ChatStore.SavedVersion> saved = new ChatStore(this).listArchivedVersions(chatId);
                runOnUiThread(() -> {
                    if (isFinishing() || isDestroyed()) return;
                    versionsButton.setEnabled(true);
                    if (saved.isEmpty()) {
                        new AlertDialog.Builder(this)
                                .setTitle("Gesicherte Altversionen")
                                .setMessage("Für dieses Gespräch sind keine zusätzlichen Fassungen im lokalen Versionsspeicher hinterlegt.")
                                .setPositiveButton("OK", null).show();
                        return;
                    }
                    String[] labels = new String[saved.size()];
                    for (int i = 0; i < labels.length; i++) labels[i] = saved.get(i).displayName();
                    new AlertDialog.Builder(this)
                            .setTitle("Gesicherte Altversionen · nur lesen")
                            .setItems(labels, (dialog, index) -> {
                                Intent intent = new Intent(this, ConversationActivity.class);
                                intent.putExtra("chatId", chatId);
                                intent.putExtra("archivedDigest", saved.get(index).digest);
                                startActivity(intent);
                            }).setNegativeButton("Schließen", null).show();
                });
            } catch (IOException exception) {
                runOnUiThread(() -> {
                    if (isFinishing() || isDestroyed()) return;
                    versionsButton.setEnabled(true);
                    new AlertDialog.Builder(this)
                            .setTitle("Versionsspeicher nicht lesbar")
                            .setMessage(exception.getMessage()).setPositiveButton("OK", null).show();
                });
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
        if (jumpButton != null) {
            jumpButton.setEnabled(!visible.isEmpty());
            jumpButton.setText(visible.isEmpty()
                    ? "Keine passenden Beiträge"
                    : "Zu Beitrag springen · " + visible.size() + " Beiträge");
        }
    }

    private void showJumpDialog() {
        if (visible.isEmpty() || list == null) return;
        LinearLayout panel = Ui.column(this, 12);
        TextView chosen = Ui.text(this, "", 14, true);
        chosen.setTextColor(Ui.ACCENT);
        panel.addView(chosen);
        SeekBar selector = new SeekBar(this);
        selector.setMax(visible.size() - 1);
        selector.setProgress(Math.max(0,
                Math.min(visible.size() - 1, list.getFirstVisiblePosition())));
        chosen.setText("Beitrag " + (selector.getProgress() + 1) + " von " + visible.size());
        selector.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar bar, int progress, boolean fromUser) {
                chosen.setText("Beitrag " + (progress + 1) + " von " + visible.size());
            }
            @Override public void onStartTrackingTouch(SeekBar bar) { }
            @Override public void onStopTrackingTouch(SeekBar bar) { }
        });
        panel.addView(selector);
        new AlertDialog.Builder(this)
                .setTitle("Zu einem Beitrag springen")
                .setView(panel)
                .setNegativeButton("Abbrechen", null)
                .setPositiveButton("Springen",
                        (dialog, choice) -> list.setSelectionFromTop(selector.getProgress(), 0))
                .show();
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
            Ui.outlineSurface(ConversationActivity.this, panel);
            LinearLayout bar = Ui.row(ConversationActivity.this);
            TextView role = Ui.text(ConversationActivity.this,
                    "user".equals(message.role) ? "DU" : "CHATGPT", 12, true);
            role.setTextColor(Ui.ACCENT);
            bar.addView(role, new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1));
            android.widget.Button copy = Ui.button(ConversationActivity.this, "Kopieren");
            bar.addView(copy);
            android.widget.Button reader = Ui.button(ConversationActivity.this, "Lesen");
            reader.setOnClickListener(view -> {
                int index = full.indexOf(message);
                if (index < 0) return;
                Intent intent = new Intent(ConversationActivity.this, ReadingActivity.class);
                intent.putExtra("chatId", chatId);
                intent.putExtra("sourceMessageIndex", index);
                startActivity(intent);
            });
            if (archivedDigest == null) bar.addView(reader);
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
