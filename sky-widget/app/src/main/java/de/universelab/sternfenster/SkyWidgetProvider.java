package de.universelab.sternfenster;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.Resources;
import android.os.Bundle;
import android.widget.RemoteViews;
import android.graphics.Bitmap;

/** Eigenes Widget; die Fremd-App wird nur per explizitem Start-Intent geöffnet. */
public class SkyWidgetProvider extends AppWidgetProvider {
    private static final String ACTION_NEXT = "de.universelab.sternfenster.NEXT";
    private static final String ACTION_REFRESH = "de.universelab.sternfenster.REFRESH";
    static final String PREFS = "sky_prefs";

    @Override public void onUpdate(Context c, AppWidgetManager m, int[] ids) {
        for(int id:ids) updateOne(c,m,id);
    }
    @Override public void onAppWidgetOptionsChanged(Context c, AppWidgetManager m, int id, Bundle options) {
        updateOne(c,m,id);
    }
    @Override public void onReceive(Context c, Intent intent) {
        super.onReceive(c,intent);
        String action = intent.getAction();
        if(ACTION_NEXT.equals(action)||ACTION_REFRESH.equals(action)){
            int id = intent.getIntExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, -1);
            AppWidgetManager m=AppWidgetManager.getInstance(c);
            if(id!=-1){
                if(ACTION_NEXT.equals(action)){
                    SharedPreferences pr=c.getSharedPreferences(PREFS,Context.MODE_PRIVATE);
                    int dir=(pr.getInt("dir_"+id,2)+1)%4;
                    pr.edit().putInt("dir_"+id,dir).apply();
                }
                updateOne(c,m,id);
            }else updateAll(c);
        }
    }
    static void updateAll(Context c){
        AppWidgetManager m=AppWidgetManager.getInstance(c);
        int[] ids=m.getAppWidgetIds(new ComponentName(c,SkyWidgetProvider.class));
        for(int id:ids)updateOne(c,m,id);
    }
    private static PendingIntent broadcast(Context c,int id,String action,int offset){
        Intent i=new Intent(c,SkyWidgetProvider.class).setAction(action);
        i.putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID,id);
        return PendingIntent.getBroadcast(c,id*4+offset,i,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
    }
    static void updateOne(Context c,AppWidgetManager mgr,int id){
        SharedPreferences pref=c.getSharedPreferences(PREFS,Context.MODE_PRIVATE);
        int dir=pref.getInt("dir_"+id,2);
        double lat=pref.getFloat("lat",51.0504f), lon=pref.getFloat("lon",13.7373f);
        boolean gps=pref.getBoolean("has_gps",false);
        Bundle options=mgr.getAppWidgetOptions(id);
        int wd=options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_WIDTH,290);
        int hd=options.getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT,150);
        float density=c.getResources().getDisplayMetrics().density;
        // 900x520 RGB_565 <= 0.94 MB; unter dem Android-17-Bitmap-Limit.
        int w=Math.max(280,Math.min(900,Math.round(wd*density)));
        int h=Math.max(160,Math.min(520,Math.round(hd*density)));
        Bitmap bitmap=SkyRenderer.draw(c,w,h,lat,lon,dir,gps);
        RemoteViews remote=new RemoteViews(c.getPackageName(),R.layout.widget_sky);
        remote.setImageViewBitmap(R.id.sky_image,bitmap);
        Intent launch=c.getPackageManager().getLaunchIntentForPackage("com.youvendo.international_space_registry");
        if(launch==null)launch=new Intent(c,MainActivity.class);
        launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        PendingIntent open=PendingIntent.getActivity(c,id*4+1,launch,
                PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        remote.setOnClickPendingIntent(R.id.sky_image,open);
        remote.setOnClickPendingIntent(R.id.dir_button,broadcast(c,id,ACTION_NEXT,2));
        remote.setOnClickPendingIntent(R.id.refresh_button,broadcast(c,id,ACTION_REFRESH,3));
        mgr.updateAppWidget(id,remote);
        bitmap.recycle();
    }
    @Override public void onDeleted(Context c,int[] ids){
        SharedPreferences.Editor editor=c.getSharedPreferences(PREFS,Context.MODE_PRIVATE).edit();
        for(int id:ids) editor.remove("dir_"+id);
        editor.apply();
    }
}
