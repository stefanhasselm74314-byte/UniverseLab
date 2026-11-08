package de.universelab.chatarchiv;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.webkit.CookieManager;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.LinearLayout;
import android.widget.TextView;

import java.io.ByteArrayInputStream;

/** A restricted viewer for the public GitHub Pages site. No script, login or forms. */
public final class WebsiteActivity extends Activity {
    private static final String WEBSITE_HOST = "stefanhasselm74314-byte.github.io";
    private static final String WEBSITE = "https://" + WEBSITE_HOST + "/UniverseLab/";
    private WebView browser;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout root = Ui.column(this, 10);
        setContentView(root);
        root.addView(Ui.text(this, "UniverseLab Webseite · Lesemodus", 19, true));
        TextView explanation = Ui.text(this,
                "Skript-Ausführung, Anmeldung und externe Domains sind gesperrt. Interaktive Elemente können deshalb fehlen.",
                12, false);
        explanation.setTextColor(Ui.MUTED);
        root.addView(explanation);
        android.widget.Button back = Ui.button(this, "‹ GitHub-Dateien");
        back.setOnClickListener(view -> finish());
        root.addView(back);

        browser = new WebView(this);
        browser.setBackgroundColor(Color.WHITE);
        browser.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return !isAllowed(request.getUrl().getScheme(), request.getUrl().getHost());
            }

            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                if (!isAllowed(request.getUrl().getScheme(), request.getUrl().getHost())) {
                    return new WebResourceResponse("text/plain", "utf-8", new ByteArrayInputStream(new byte[0]));
                }
                return null;
            }
        });
        WebSettings settings = browser.getSettings();
        settings.setJavaScriptEnabled(false);
        settings.setDomStorageEnabled(false);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setCacheMode(WebSettings.LOAD_NO_CACHE);
        settings.setSupportMultipleWindows(false);
        CookieManager.getInstance().setAcceptCookie(false);
        browser.setDownloadListener((url, userAgent, contentDisposition, mimetype, length) -> { });
        root.addView(browser, Ui.fillRemaining());
        browser.loadUrl(WEBSITE);
    }

    private static boolean isAllowed(String scheme, String host) {
        return "https".equalsIgnoreCase(scheme) && WEBSITE_HOST.equalsIgnoreCase(host);
    }

    @Override protected void onDestroy() {
        if (browser != null) {
            browser.stopLoading();
            browser.destroy();
        }
        super.onDestroy();
    }
}
