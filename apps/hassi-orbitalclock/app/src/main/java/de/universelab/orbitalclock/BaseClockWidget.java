package de.universelab.orbitalclock;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.content.Intent;
import android.widget.RemoteViews;

/** Uses Android TextClock, which updates on minute ticks in the host process. */
public abstract class BaseClockWidget extends AppWidgetProvider {
    protected abstract int layoutId();

    @Override public void onUpdate(Context context, AppWidgetManager manager, int[] ids) {
        super.onUpdate(context, manager, ids);
        for (int id : ids) update(context, manager, id);
    }

    @Override public void onAppWidgetOptionsChanged(Context context,
              AppWidgetManager manager, int widgetId, android.os.Bundle options) {
        super.onAppWidgetOptionsChanged(context, manager, widgetId, options);
        update(context, manager, widgetId);
    }

    private void update(Context context, AppWidgetManager manager, int id) {
        RemoteViews views = new RemoteViews(context.getPackageName(), layoutId());
        Intent launch = new Intent(context, MainActivity.class);
        PendingIntent click = PendingIntent.getActivity(context, 0, launch,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        views.setOnClickPendingIntent(R.id.widget_root, click);
        manager.updateAppWidget(id, views);
    }
}
