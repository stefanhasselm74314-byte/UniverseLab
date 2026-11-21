package de.universelab.sternfenster;

import android.Manifest;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

/** Visible, user-initiated permission flow; never starts an overlay from the background. */
public final class OverlaySetupActivity extends Activity {
    private static final int NOTIFICATION_REQUEST = 82;
    private static final String NOTIFICATION_ASKED = "overlay_notification_asked";
    private boolean resumed, launching, notificationPending;
    private TextView status;

    public static void launch(Activity source, Intent serviceIntent) {
        Intent setup = new Intent(source, OverlaySetupActivity.class);
        if (serviceIntent.getExtras() != null) setup.putExtras(serviceIntent.getExtras());
        source.startActivity(setup);
    }

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        notificationPending = state != null && state.getBoolean("notificationPending", false);
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        LinearLayout panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(Ui.dp(this,20), Ui.dp(this,20), Ui.dp(this,20), Ui.dp(this,24));
        scroll.addView(panel);
        Ui.heading(this, panel, "Freies Live-Fenster");
        panel.addView(Ui.text(this, "Die Sternkarte bleibt über anderen Apps sichtbar. Ziehe sie an der Titelleiste an die gewünschte Stelle; der Griff unten rechts ändert die Größe. Mit × schließt du das Fenster.", 16, Ui.TEXT));
        status = Ui.text(this, "Erlaube Sternfenster einmalig „Über anderen Apps anzeigen“. Kehre anschließend hierher zurück; das Fenster startet dann automatisch.", 15, Ui.MUTED);
        status.setPadding(0, Ui.dp(this,16), 0, Ui.dp(this,12));
        panel.addView(status);
        Ui.addButton(this, panel, "Über anderen Apps erlauben / Fenster starten", () -> {
            if (Settings.canDrawOverlays(this)) maybeStart();
            else openOverlaySettings();
        });
        panel.addView(Ui.text(this, "Eine laufende Benachrichtigung bietet zusätzlich „Fenster schließen“. Das Fenster läuft unabhängig von der Hauptansicht. Bei gesperrtem oder ausgeschaltetem Bildschirm pausieren Darstellung und Sensoren.", 14, Ui.MUTED));
        Ui.addButton(this, panel, "Zurück", this::finish);
        Ui.install(this, scroll);
    }

    private void openOverlaySettings() {
        try {
            startActivity(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    Uri.parse("package:" + getPackageName())));
        } catch (ActivityNotFoundException | SecurityException unavailable) {
            try {
                startActivity(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION));
            } catch (ActivityNotFoundException | SecurityException alsoUnavailable) {
                status.setText("Öffne Einstellungen → Apps → Spezieller Zugriff → Über anderen Apps anzeigen und erlaube Sternfenster. Kehre danach hierher zurück.");
            }
        }
    }

    @Override protected void onResume() {
        super.onResume();
        resumed = true;
        maybeStart();
    }

    @Override protected void onPause() {
        resumed = false;
        super.onPause();
    }

    @Override protected void onSaveInstanceState(Bundle state) {
        state.putBoolean("notificationPending", notificationPending);
        super.onSaveInstanceState(state);
    }

    private void maybeStart() {
        if (!resumed || launching || notificationPending || !Settings.canDrawOverlays(this)) return;
        SharedPreferences prefs = getSharedPreferences(SkyWidgetProvider.PREFS, MODE_PRIVATE);
        if (Build.VERSION.SDK_INT >= 33
                && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
                && !prefs.getBoolean(NOTIFICATION_ASKED, false)) {
            prefs.edit().putBoolean(NOTIFICATION_ASKED, true).apply();
            notificationPending = true;
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, NOTIFICATION_REQUEST);
            return;
        }
        Intent service = new Intent(this, FloatingSkyService.class).setAction(FloatingSkyService.ACTION_SHOW);
        if (getIntent().getExtras() != null) service.putExtras(getIntent().getExtras());
        launching = true;
        try {
            // This call happens while this Activity is resumed. Notification denial does not block FGS.
            startForegroundService(service);
            finish();
        } catch (RuntimeException failure) {
            launching = false;
            status.setText("Das freie Fenster konnte nicht gestartet werden. Prüfe die Freigabe „Über anderen Apps anzeigen“ und tippe erneut auf „Fenster starten“.");
            android.util.Log.e("SternfensterOverlay", "User-initiated foreground start failed", failure);
        }
    }

    @Override public void onRequestPermissionsResult(int request, String[] permissions, int[] results) {
        super.onRequestPermissionsResult(request, permissions, results);
        if (request != NOTIFICATION_REQUEST) return;
        notificationPending = false;
        // Both granted and denied lead to a foreground service; the visible overlay remains controllable.
        if (resumed) maybeStart();
    }
}
