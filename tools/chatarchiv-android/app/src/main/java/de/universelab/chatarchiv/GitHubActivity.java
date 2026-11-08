package de.universelab.chatarchiv;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.os.Bundle;
import android.util.Base64;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.ScrollView;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Anonymous GET-only public repository browser. No GitHub login, token, or write API. */
public final class GitHubActivity extends Activity {
    private static final String REPO = "stefanhasselm74314-byte/UniverseLab";
    private static final String API = "https://api.github.com/repos/" + REPO + "/contents/";
    private final ExecutorService network = Executors.newSingleThreadExecutor();
    private final List<FileItem> files = new ArrayList<>();
    private RepoAdapter adapter;
    private TextView status;
    private String currentPath = "";
    private int requestedPage;

    private static final class FileItem {
        final String name;
        final String path;
        final String type;
        final long size;

        FileItem(JSONObject json) {
            name = json.optString("name", "");
            path = json.optString("path", "");
            type = json.optString("type", "");
            size = json.optLong("size", 0);
        }
    }

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout root = Ui.column(this, 12);
        setContentView(root);
        root.addView(Ui.text(this, "UniverseLab GitHub · nur lesen", 20, true));
        TextView privacy = Ui.text(this, "Öffentliches Repository, Branch main. Nur anonyme GET-Abfragen; kein Login und keine Schreibfunktion.", 12, false);
        privacy.setTextColor(Ui.MUTED);
        root.addView(privacy);

        LinearLayout actions = Ui.row(this);
        android.widget.Button back = Ui.button(this, "Ordner zurück");
        android.widget.Button website = Ui.button(this, "Webseite ansehen");
        actions.addView(back, Ui.weight(1));
        actions.addView(website, Ui.weight(1));
        root.addView(actions);
        back.setOnClickListener(view -> {
            if (currentPath.isEmpty()) finish();
            else {
                int slash = currentPath.lastIndexOf('/');
                loadDirectory(slash < 0 ? "" : currentPath.substring(0, slash));
            }
        });
        website.setOnClickListener(view -> startActivity(new Intent(this, WebsiteActivity.class)));

        status = Ui.text(this, "Repository wird geladen …", 13, false);
        status.setTextColor(Ui.ACCENT);
        root.addView(status);
        ListView list = new ListView(this);
        list.setDivider(null);
        list.setDividerHeight(Ui.dp(this, 6));
        adapter = new RepoAdapter();
        list.setAdapter(adapter);
        list.setOnItemClickListener((parent, view, position, id) -> {
            if (position < 0 || position >= files.size()) return;
            FileItem item = files.get(position);
            if ("dir".equals(item.type)) loadDirectory(item.path);
            else if ("file".equals(item.type)) preview(item);
        });
        root.addView(list, Ui.fillRemaining());
        loadDirectory("");
    }

    private void loadDirectory(String path) {
        int page = ++requestedPage;
        currentPath = path;
        status.setText("Lade /" + path + " …");
        network.execute(() -> {
            try {
                String json = getPublic(API + encodedPath(path) + "?ref=main", 4_000_000);
                JSONArray response = new JSONArray(json);
                ArrayList<FileItem> listed = new ArrayList<>();
                for (int i = 0; i < response.length(); i++) {
                    JSONObject object = response.optJSONObject(i);
                    if (object != null) listed.add(new FileItem(object));
                }
                listed.sort(Comparator.comparing((FileItem f) -> !"dir".equals(f.type))
                        .thenComparing(f -> f.name.toLowerCase(java.util.Locale.ROOT)));
                runOnUiThread(() -> {
                    if (isFinishing() || isDestroyed() || requestedPage != page) return;
                    files.clear();
                    files.addAll(listed);
                    adapter.notifyDataSetChanged();
                    status.setText("main / " + (path.isEmpty() ? "" : path + "/") + " · " + files.size() + " Einträge");
                });
            } catch (Exception exception) {
                runOnUiThread(() -> {
                    if (requestedPage == page) status.setText("GitHub-Lesefehler: " + exception.getMessage());
                });
            }
        });
    }

    private void preview(FileItem file) {
        if (file.size > 190_000) {
            new AlertDialog.Builder(this).setTitle(file.name)
                    .setMessage("Datei zu groß für die Mobilvorschau (" + file.size + " Bytes). Die Quelle bleibt im GitHub-Repository unverändert.")
                    .setPositiveButton("OK", null).show();
            return;
        }
        status.setText("Lade Vorschau: " + file.name);
        network.execute(() -> {
            try {
                JSONObject object = new JSONObject(getPublic(API + encodedPath(file.path) + "?ref=main", 450_000));
                if (!"base64".equals(object.optString("encoding"))) {
                    throw new IOException("Keine Textvorschau verfügbar");
                }
                byte[] data = Base64.decode(object.optString("content", ""), Base64.DEFAULT);
                if (!looksText(data)) throw new IOException("Binärdatei – keine Textvorschau");
                String contents = new String(data, StandardCharsets.UTF_8);
                runOnUiThread(() -> {
                    if (isFinishing() || isDestroyed()) return;
                    status.setText("main / " + currentPath);
                    ScrollView scroll = new ScrollView(this);
                    TextView text = Ui.text(this, contents, 13, false);
                    text.setTypeface(android.graphics.Typeface.MONOSPACE);
                    text.setTextIsSelectable(true);
                    text.setPadding(Ui.dp(this, 14), Ui.dp(this, 12), Ui.dp(this, 14), Ui.dp(this, 12));
                    scroll.addView(text);
                    new AlertDialog.Builder(this).setTitle(file.name + " · read-only")
                            .setView(scroll).setPositiveButton("Schließen", null).show();
                });
            } catch (Exception exception) {
                runOnUiThread(() -> new AlertDialog.Builder(this).setTitle("Vorschau nicht verfügbar")
                        .setMessage(exception.getMessage()).setPositiveButton("OK", null).show());
            }
        });
    }

    private static boolean looksText(byte[] bytes) {
        for (byte b : bytes) if (b == 0) return false;
        return true;
    }

    private static String encodedPath(String path) {
        if (path.isEmpty()) return "";
        StringBuilder result = new StringBuilder();
        for (String segment : path.split("/")) {
            if (segment.isEmpty() || "..".equals(segment) || ".".equals(segment)) {
                throw new IllegalArgumentException("Ungültiger Repository-Pfad");
            }
            if (result.length() > 0) result.append('/');
            result.append(URLEncoder.encode(segment, StandardCharsets.UTF_8).replace("+", "%20"));
        }
        return result.toString();
    }

    private static String getPublic(String url, int maxBytes) throws IOException {
        URL destination = new URL(url);
        if (!"https".equals(destination.getProtocol()) || !"api.github.com".equals(destination.getHost())) {
            throw new IOException("Nicht erlaubter GitHub-Host");
        }
        HttpURLConnection connection = (HttpURLConnection) destination.openConnection();
        connection.setInstanceFollowRedirects(false);
        connection.setRequestMethod("GET");
        connection.setConnectTimeout(12000);
        connection.setReadTimeout(15000);
        connection.setRequestProperty("Accept", "application/vnd.github+json");
        connection.setRequestProperty("User-Agent", "UniverseLabChatArchiv-ReadOnly/0.1");
        try {
            int code = connection.getResponseCode();
            if (code != 200) throw new IOException("HTTP " + code + " (öffentliches API-Limit möglich)");
            try (InputStream stream = connection.getInputStream(); ByteArrayOutputStream output = new ByteArrayOutputStream()) {
                byte[] block = new byte[8192];
                int n;
                while ((n = stream.read(block)) != -1) {
                    if (output.size() + n > maxBytes) throw new IOException("Antwort zu groß");
                    output.write(block, 0, n);
                }
                return output.toString(StandardCharsets.UTF_8.name());
            }
        } finally {
            connection.disconnect();
        }
    }

    @Override protected void onDestroy() {
        network.shutdownNow();
        super.onDestroy();
    }

    private final class RepoAdapter extends BaseAdapter {
        @Override public int getCount() { return files.size(); }
        @Override public Object getItem(int position) { return files.get(position); }
        @Override public long getItemId(int position) { return position; }

        @Override public View getView(int position, View old, ViewGroup parent) {
            FileItem item = files.get(position);
            LinearLayout box = Ui.column(GitHubActivity.this, 9);
            box.setBackgroundColor(Ui.SURFACE);
            box.addView(Ui.text(GitHubActivity.this,
                    ("dir".equals(item.type) ? "📁 " : "📄 ") + item.name, 15, true));
            TextView meta = Ui.text(GitHubActivity.this,
                    "dir".equals(item.type) ? "Verzeichnis" : "Datei · " + item.size + " Bytes", 12, false);
            meta.setTextColor(Ui.MUTED);
            box.addView(meta);
            return box;
        }
    }
}
