package de.universelab.clockdeck;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.widget.RemoteViews;
import android.os.Bundle;

/** Widget backgrounds are periodic bitmaps; Android TextClock shows live local time. */
public abstract class WidgetBase extends AppWidgetProvider {
    protected abstract int style();
    @Override public void onUpdate(Context context,AppWidgetManager manager,int[] ids){
        for(int id:ids) updateOne(context,manager,id,style());
    }
    @Override public void onAppWidgetOptionsChanged(Context context,AppWidgetManager mgr,int id,Bundle options){
        updateOne(context,mgr,id,style());
    }
    static void updateOne(Context c,AppWidgetManager mgr,int widgetId,int style){
        Bundle options=mgr.getAppWidgetOptions(widgetId);
        // Bitmap dimensions chosen to keep the Binder transfer under ~1 MB.
        int width=640,height=348;
        if(options!=null){
            int minHeight=options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT,150);
            height=Math.max(264,Math.min(420,Math.round(minHeight*2.1f)));
        }
        Bitmap bitmap=Bitmap.createBitmap(width,height,Bitmap.Config.ARGB_8888);
        Canvas canvas=new Canvas(bitmap);
        new ClockRenderer().drawWidget(canvas,width,height,style,System.currentTimeMillis(),Battery.percent(c));
        RemoteViews v=new RemoteViews(c.getPackageName(),R.layout.widget_clock);
        v.setImageViewBitmap(R.id.widget_background,bitmap);
        int battery=Battery.percent(c);
        v.setTextViewText(R.id.widget_battery,battery<0?"AKKU --%":"AKKU "+battery+"%");
        Intent launch=new Intent(c,style==1?CompassActivity.class:MainActivity.class);
        launch.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent tap=PendingIntent.getActivity(c,widgetId,launch,
                PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        v.setOnClickPendingIntent(R.id.widget_root,tap);
        mgr.updateAppWidget(widgetId,v);
        bitmap.recycle();
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
