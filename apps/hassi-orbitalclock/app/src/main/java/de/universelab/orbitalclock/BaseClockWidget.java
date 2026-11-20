package de.universelab.orbitalclock;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.content.Intent;
import android.content.res.Configuration;
import android.os.Build;
import android.os.Bundle;
import android.util.TypedValue;
import android.widget.RemoteViews;

/**
 * Clock artwork and TextClock overlays share one fixed-aspect art frame.
 * When Nova Launcher resizes the outer widget, the artwork is centered and
 * scaled proportionally (never fitXY). The host area is fully transparent;
 * the clock images have alpha-rounded edges so wallpaper shows through.
 * Android 12+ RemoteViews size updates are applied on each resize.
 */
public abstract class BaseClockWidget extends AppWidgetProvider {
    protected abstract int layoutId();
    protected abstract float artworkAspectRatio(); // width / height

    @Override public void onUpdate(Context context, AppWidgetManager manager, int[] ids) {
        super.onUpdate(context, manager, ids);
        for (int id : ids) update(context, manager, id);
    }

    @Override public void onAppWidgetOptionsChanged(Context context,
            AppWidgetManager manager, int widgetId, Bundle options) {
        super.onAppWidgetOptionsChanged(context, manager, widgetId, options);
        update(context, manager, widgetId);
    }

    private void update(Context context, AppWidgetManager manager, int id) {
        RemoteViews views = new RemoteViews(context.getPackageName(), layoutId());
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            Bundle options = manager.getAppWidgetOptions(id);
            if (options != null) {
                // Per Android widget options: portrait is generally the smaller
                // width and larger height. Landscape reverses both choices.
                boolean landscape = context.getResources().getConfiguration().orientation
                        == Configuration.ORIENTATION_LANDSCAPE;
                int wDp = options.getInt(landscape
                        ? AppWidgetManager.OPTION_APPWIDGET_MAX_WIDTH
                        : AppWidgetManager.OPTION_APPWIDGET_MIN_WIDTH, 0);
                int hDp = options.getInt(landscape
                        ? AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT
                        : AppWidgetManager.OPTION_APPWIDGET_MAX_HEIGHT, 0);
                if (wDp > 0 && hDp > 0) {
                    // Android supplies launcher-size options in dp, excluding host-specific
                    // margins on some launchers. 4dp guard prevents clipping.
                    float wAvailable = Math.max(1f, wDp - 4f);
                    float hAvailable = Math.max(1f, hDp - 4f);
                    float aspect = artworkAspectRatio();
                    float artW = Math.min(wAvailable, hAvailable * aspect);
                    float artH = artW / aspect;
                    views.setViewLayoutWidth(R.id.widget_art, artW,
                            TypedValue.COMPLEX_UNIT_DIP);
                    views.setViewLayoutHeight(R.id.widget_art, artH,
                            TypedValue.COMPLEX_UNIT_DIP);
                    // Time text scales with the actual artwork, not the widget
                    // host's stretched bounds.
                    float sp = Math.max(10f, Math.min(39f, artW * .128f));
                    views.setTextViewTextSize(R.id.hour_clock,
                            TypedValue.COMPLEX_UNIT_SP, sp);
                    views.setTextViewTextSize(R.id.minute_clock,
                            TypedValue.COMPLEX_UNIT_SP, sp);
                }
            }
        }
        Intent launch = new Intent(context, MainActivity.class);
        PendingIntent click = PendingIntent.getActivity(context, 0, launch,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        views.setOnClickPendingIntent(R.id.widget_root, click);
        manager.updateAppWidget(id, views);
    }
}
