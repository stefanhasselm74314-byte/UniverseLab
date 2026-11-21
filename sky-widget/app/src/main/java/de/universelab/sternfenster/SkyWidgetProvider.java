package de.universelab.sternfenster;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.Configuration;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.widget.RemoteViews;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/** Eigene Sternkarte; Antippen öffnet immer die eigene Sternfenster-Vollansicht. */
public class SkyWidgetProvider extends AppWidgetProvider {
    private static final String ACTION_NEXT = "de.universelab.sternfenster.NEXT";
    private static final String ACTION_REFRESH = "de.universelab.sternfenster.REFRESH";
    private static final String ACTION_VIEW = "de.universelab.sternfenster.VIEW_SKY";
    private static final String[] DIRECTIONS = {"NORD", "OST", "SÜD", "WEST"};
    static final String PREFS = "sky_prefs";
    // Native header, footer and vertical padding in widget_sky.xml.
    private static final int HEADER_DP = 56;
    private static final int FOOTER_DP = 48;
    private static final int PADDING_DP = 16;

    @Override public void onUpdate(Context context, AppWidgetManager manager, int[] ids) {
        for (int id : ids) updateOne(context, manager, id);
    }
    @Override public void onAppWidgetOptionsChanged(Context context, AppWidgetManager manager,
                                                   int id, Bundle options) {
        updateOne(context, manager, id);
    }
    @Override public void onReceive(Context context, Intent intent) {
        super.onReceive(context, intent);
        String action = intent.getAction();
        if (!ACTION_NEXT.equals(action) && !ACTION_REFRESH.equals(action)) return;
        AppWidgetManager manager = AppWidgetManager.getInstance(context);
        int id = intent.getIntExtra(AppWidgetManager.EXTRA_APPWIDGET_ID,
                AppWidgetManager.INVALID_APPWIDGET_ID);
        // Ignore old/deleted IDs and IDs belonging to another provider.
        if (!ownsWidget(context, manager, id)) return;
        if (ACTION_NEXT.equals(action)) {
            SharedPreferences preferences = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
            int direction = (normalDirection(preferences.getInt("dir_" + id, 2)) + 1) % 4;
            preferences.edit().putInt("dir_" + id, direction).apply();
        }
        updateOne(context, manager, id);
    }
    private static boolean ownsWidget(Context context, AppWidgetManager manager, int id) {
        if (id == AppWidgetManager.INVALID_APPWIDGET_ID) return false;
        for (int owned : manager.getAppWidgetIds(new ComponentName(context, SkyWidgetProvider.class))) {
            if (owned == id) return true;
        }
        return false;
    }
    static void updateAll(Context context) {
        AppWidgetManager manager = AppWidgetManager.getInstance(context);
        int[] ids = manager.getAppWidgetIds(new ComponentName(context, SkyWidgetProvider.class));
        for (int id : ids) updateOne(context, manager, id);
    }
    private static int normalDirection(int direction) { return ((direction % 4) + 4) % 4; }
    private static PendingIntent broadcast(Context context, int id, String action, String operation) {
        Intent intent = new Intent(context, SkyWidgetProvider.class).setAction(action)
                .setData(Uri.parse("sternfenster://widget/" + id + "/" + operation))
                .putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, id);
        return PendingIntent.getBroadcast(context, id, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }
    private static PendingIntent openSky(Context context, int id, int direction) {
        Intent intent = new Intent(context, SkyActivity.class).setAction(ACTION_VIEW)
                .setData(Uri.parse("sternfenster://widget/" + id + "/open"))
                .putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, id)
                .putExtra("direction", direction)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        return PendingIntent.getActivity(context, id, intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }
    static void updateOne(Context context, AppWidgetManager manager, int id) {
        SharedPreferences preferences = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        int direction = normalDirection(preferences.getInt("dir_" + id, 2));
        double latitude = preferences.getFloat("lat", 51.0504f);
        double longitude = preferences.getFloat("lon", 13.7373f);
        boolean hasLocation = preferences.getBoolean("has_gps", false);
        Bundle options = manager.getAppWidgetOptions(id);
        boolean landscape = context.getResources().getConfiguration().orientation
                == Configuration.ORIENTATION_LANDSCAPE;
        int widthDp = options.getInt(landscape ? AppWidgetManager.OPTION_APPWIDGET_MAX_WIDTH
                : AppWidgetManager.OPTION_APPWIDGET_MIN_WIDTH, 290);
        int heightDp = options.getInt(landscape ? AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT
                : AppWidgetManager.OPTION_APPWIDGET_MAX_HEIGHT, 220);
        if (widthDp <= 0) widthDp = 290;
        if (heightDp <= 0) heightDp = 220;
        float density = context.getResources().getDisplayMetrics().density;
        int width = Math.max(1, Math.round(Math.max(1, widthDp - PADDING_DP) * density));
        int height = Math.max(1, Math.round(Math.max(1,
                heightDp - PADDING_DP - HEADER_DP - FOOTER_DP) * density));
        // Both dimensions are reduced together by the renderer. fitCenter then
        // preserves the sky's angular geometry at every launcher size.
        Bitmap bitmap = SkyRenderer.draw(context, width, height, latitude, longitude,
                direction, hasLocation);
        RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.widget_sky);
        views.setTextViewText(R.id.widget_title, "STERNFENSTER · " + DIRECTIONS[direction]);
        String timestamp = new SimpleDateFormat("dd.MM. HH:mm", Locale.GERMANY).format(new Date());
        views.setTextViewText(R.id.widget_status, timestamp + " · "
                + (hasLocation ? "Standort gespeichert" : "Dresden (Standard)"));
        views.setImageViewBitmap(R.id.sky_image, bitmap);
        views.setContentDescription(R.id.sky_image,
                "Sternkarte, Blickrichtung " + DIRECTIONS[direction]
                        + ". Tippen öffnet die eigene Live-Sternkarte.");
        PendingIntent open = openSky(context, id, direction);
        views.setOnClickPendingIntent(R.id.sky_image, open);
        views.setOnClickPendingIntent(R.id.open_button, open);
        views.setOnClickPendingIntent(R.id.refresh_button,
                broadcast(context, id, ACTION_REFRESH, "refresh"));
        views.setOnClickPendingIntent(R.id.dir_button,
                broadcast(context, id, ACTION_NEXT, "next"));
        manager.updateAppWidget(id, views);
        bitmap.recycle();
    }
    @Override public void onDeleted(Context context, int[] ids) {
        SharedPreferences.Editor editor = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit();
        for (int id : ids) editor.remove("dir_" + id);
        editor.apply();
    }
}
