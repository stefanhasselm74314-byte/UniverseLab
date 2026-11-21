package de.universelab.sternfenster;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Canvas;
import android.graphics.Typeface;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.GestureDetector;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/** Canvas sky screen. No external engine, background service or GPU surface management. */
public final class SkyActivity extends Activity {
    private final Handler handler=new Handler(Looper.getMainLooper());
    private final SimpleDateFormat clock=new SimpleDateFormat("HH:mm:ss",Locale.GERMANY);
    private SkyView sky;
    private TextView info,location;
    private double latitude,longitude,azimuth=180,altitude=42,fov=100;
    private boolean hasLocation,visible;
    private final Runnable tick=new Runnable(){
        @Override public void run(){
            if(!visible)return;
            refresh();handler.postDelayed(this,1000-System.currentTimeMillis()%1000);
        }
    };
    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        SharedPreferences p=getSharedPreferences(SkyWidgetProvider.PREFS,MODE_PRIVATE);
        if(saved!=null){azimuth=saved.getDouble("az",180);altitude=saved.getDouble("alt",42);fov=saved.getDouble("fov",100);}
        else if(getIntent().hasExtra("direction"))azimuth=Math.floorMod(getIntent().getIntExtra("direction",2),4)*90;
        else{azimuth=p.getFloat("live_az",180);altitude=p.getFloat("live_alt",42);fov=p.getFloat("live_fov",100);}
        clamp();
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(Ui.dp(this,12),Ui.dp(this,6),Ui.dp(this,12),Ui.dp(this,8));
        LinearLayout top=new LinearLayout(this);top.setGravity(android.view.Gravity.CENTER_VERTICAL);
        Button back=Ui.button(this,"‹",this::finish);back.setContentDescription("Zurück");
        top.addView(back,new LinearLayout.LayoutParams(Ui.dp(this,48),Ui.dp(this,48)));
        TextView title=Ui.text(this,"  Sternfenster · Live",19,0xffc1e5fa);title.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        top.addView(title,new LinearLayout.LayoutParams(0,-2,1));root.addView(top);
        info=Ui.text(this,"",14,Ui.TEXT);info.setPadding(0,Ui.dp(this,8),0,0);root.addView(info);
        location=Ui.text(this,"",12,Ui.MUTED);location.setPadding(0,Ui.dp(this,3),0,Ui.dp(this,6));root.addView(location);
        sky=new SkyView(this);root.addView(sky,new LinearLayout.LayoutParams(-1,0,1));
        LinearLayout directions=new LinearLayout(this);
        String[] names={"N","O","S","W"};
        for(int i=0;i<4;i++){
            final int d=i;
            Button button=Ui.button(this,names[i],()->{azimuth=d*90;altitude=42;refresh();});
            button.setContentDescription(new String[]{"Nach Norden blicken","Nach Osten blicken","Nach Süden blicken","Nach Westen blicken"}[i]);
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-2,1);
            lp.setMargins(Ui.dp(this,3),Ui.dp(this,6),Ui.dp(this,3),Ui.dp(this,3));directions.addView(button,lp);
        }
        root.addView(directions);
        LinearLayout zoom=new LinearLayout(this);
        addControl(zoom,"−",()->{fov*=1.22;clamp();refresh();},"Herauszoomen");
        addControl(zoom,"Zurücksetzen",()->{azimuth=180;altitude=42;fov=100;refresh();},"Blick nach Süden zurücksetzen");
        addControl(zoom,"+",()->{fov/=1.22;clamp();refresh();},"Hineinzoomen");
        root.addView(zoom);
        TextView hint=Ui.text(this,"Wischen: Blickrichtung · Zwei Finger: Zoom",12,Ui.MUTED);
        hint.setPadding(0,Ui.dp(this,5),0,0);hint.setGravity(android.view.Gravity.CENTER);root.addView(hint);
        Ui.install(this,root);
    }
    private void addControl(LinearLayout row,String label,Runnable action,String description) {
        Button b=Ui.button(this,label,action);b.setContentDescription(description);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-2,label.length()>2?2:1);
        lp.setMargins(Ui.dp(this,3),Ui.dp(this,3),Ui.dp(this,3),0);row.addView(b,lp);
    }
    private void clamp() {
        if(!Double.isFinite(azimuth))azimuth=180;
        if(!Double.isFinite(altitude))altitude=42;
        if(!Double.isFinite(fov))fov=100;
        azimuth=SkyMath.wrap360(azimuth);altitude=Math.max(0,Math.min(89,altitude));fov=Math.max(35,Math.min(135,fov));
    }
    private void loadLocation() {
        SharedPreferences p=getSharedPreferences(SkyWidgetProvider.PREFS,MODE_PRIVATE);
        latitude=p.getFloat("lat",51.0504f);longitude=p.getFloat("lon",13.7373f);hasLocation=p.getBoolean("has_gps",false);
    }
    private void refresh() {
        clamp();long now=System.currentTimeMillis();
        String[] dirs={"Nord","Nordost","Ost","Südost","Süd","Südwest","West","Nordwest"};
        String direction=dirs[(int)Math.round(azimuth/45)%8];
        info.setText(String.format(Locale.GERMANY,"%s · %s %.0f° · Blickhöhe %.0f°",clock.format(new Date(now)),direction,azimuth,altitude));
        location.setText((hasLocation?"Gespeicherter Standort":"Dresden · Standard")+" · Sternpositionen auch tagsüber");
        sky.setContentDescription("Sternkarte nach "+direction+", Blickhöhe "+Math.round(altitude)+" Grad. Mit Richtungstasten und Zoom bedienbar.");
        sky.invalidate();
    }
    @Override protected void onResume(){super.onResume();loadLocation();visible=true;handler.removeCallbacks(tick);handler.post(tick);}
    @Override protected void onPause(){
        visible=false;handler.removeCallbacks(tick);
        getSharedPreferences(SkyWidgetProvider.PREFS,MODE_PRIVATE).edit()
                .putFloat("live_az",(float)azimuth).putFloat("live_alt",(float)altitude).putFloat("live_fov",(float)fov).apply();
        super.onPause();
    }
    @Override protected void onSaveInstanceState(Bundle out){
        out.putDouble("az",azimuth);out.putDouble("alt",altitude);out.putDouble("fov",fov);super.onSaveInstanceState(out);
    }
    @Override protected void onNewIntent(Intent intent){
        super.onNewIntent(intent);setIntent(intent);
        if(intent.hasExtra("direction")){azimuth=Math.floorMod(intent.getIntExtra("direction",2),4)*90;altitude=42;fov=100;}
        loadLocation();refresh();
    }
    private final class SkyView extends View {
        private final GestureDetector gestures;
        private final ScaleGestureDetector scale;
        SkyView(Context context){
            super(context);setFocusable(true);setClickable(true);
            scale=new ScaleGestureDetector(context,new ScaleGestureDetector.SimpleOnScaleGestureListener(){
                @Override public boolean onScale(ScaleGestureDetector detector){
                    fov/=Math.max(0.1,detector.getScaleFactor());clamp();refresh();return true;
                }
            });
            gestures=new GestureDetector(context,new GestureDetector.SimpleOnGestureListener(){
                @Override public boolean onDown(MotionEvent event){return true;}
                @Override public boolean onScroll(MotionEvent first,MotionEvent current,float dx,float dy){
                    if(scale.isInProgress()||current.getPointerCount()>1)return true;
                    double degrees=fov/Math.max(1,getHeight());azimuth+=dx*degrees;altitude-=dy*degrees;refresh();return true;
                }
                @Override public boolean onSingleTapUp(MotionEvent event){performClick();return true;}
            });
        }
        @Override protected void onDraw(Canvas canvas){
            super.onDraw(canvas);
            if(getWidth()>0&&getHeight()>0)SkyRenderer.paint(canvas,getContext(),getWidth(),getHeight(),latitude,longitude,
                    azimuth,altitude,fov,System.currentTimeMillis(),true);
        }
        @Override public boolean onTouchEvent(MotionEvent event){scale.onTouchEvent(event);gestures.onTouchEvent(event);return true;}
        @Override public boolean performClick(){super.performClick();return true;}
    }
}
