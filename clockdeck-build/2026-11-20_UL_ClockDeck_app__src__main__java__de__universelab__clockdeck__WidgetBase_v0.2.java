package de.universelab.clockdeck;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.os.Bundle;
import android.util.TypedValue;
import android.widget.RemoteViews;

/** The rendered dial remains square in every launcher layout. Time is driven by TextClock. */
public abstract class WidgetBase extends AppWidgetProvider {
    protected abstract int style();
    @Override public void onUpdate(Context context, AppWidgetManager manager, int[] ids) {
        for (int id : ids) updateOne(context, manager, id, style());
    }
    @Override public void onAppWidgetOptionsChanged(Context context, AppWidgetManager manager,
                                                    int id, Bundle newOptions) {
        updateOne(context, manager, id, style());
    }
    static void updateOne(Context c, AppWidgetManager mgr, int widgetId, int style) {
        // 340x340 ARGB_8888 is < 500 KB, below typical RemoteViews binder limits.
        final int side = 340;
        Bitmap bmp = Bitmap.createBitmap(side, side, Bitmap.Config.ARGB_8888);
        Canvas canvas = new Canvas(bmp);
        new ClockRenderer().drawFace(canvas,side/2f,side/2f,side*.48f,style,
                System.currentTimeMillis(),0,0,0,Float.NaN,Battery.percent(c),false);

        RemoteViews rv = new RemoteViews(c.getPackageName(),R.layout.widget_clock);
        rv.setImageViewBitmap(R.id.widget_background,bmp);
        rv.setTextViewText(R.id.widget_theme,
            new String[]{"TITAN SKELETON","KOMPASS","HOLO-6D"}[Math.max(0,Math.min(2,style))]);
        int battery = Battery.percent(c);
        rv.setTextViewText(R.id.widget_battery,
            battery<0 ? "AKKU --%" : "AKKU " + battery + "%");

        Bundle options = mgr.getAppWidgetOptions(widgetId);
        int minWidth = options == null ? 280
            : options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_WIDTH,280);
        // Keep the digital clock legible when Samsung's widget is squeezed.
        float clockSp = minWidth < 210 ? 23f : minWidth < 270 ? 27f : 31f;
        rv.setTextViewTextSize(R.id.widget_time, TypedValue.COMPLEX_UNIT_SP,clockSp);
        if(minWidth<210){
            rv.setTextViewTextSize(R.id.widget_brand,TypedValue.COMPLEX_UNIT_SP,8.5f);
            rv.setTextViewTextSize(R.id.widget_theme,TypedValue.COMPLEX_UNIT_SP,8.5f);
            rv.setTextViewTextSize(R.id.widget_date,TypedValue.COMPLEX_UNIT_SP,10.5f);
        }
        Intent launch = new Intent(c,style==1?CompassActivity.class:MainActivity.class);
        launch.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent tap = PendingIntent.getActivity(c,widgetId,launch,
            PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        rv.setOnClickPendingIntent(R.id.widget_root,tap);
        mgr.updateAppWidget(widgetId,rv);
        bmp.recycle();
    }
    public static void refreshAll(Context c){
        AppWidgetManager mgr=AppWidgetManager.getInstance(c);
        for(Class<?> clz:new Class<?>[]{TitanWidget.class,CompassWidget.class,HoloWidget.class}){
            int[] ids=mgr.getAppWidgetIds(new ComponentName(c,clz));
            int style=clz==TitanWidget.class?0:clz==CompassWidget.class?1:2;
            for(int id:ids)updateOne(c,mgr,id,style);
        }
    }
}
