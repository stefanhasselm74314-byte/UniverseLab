package de.universelab.sternfenster;

import android.app.Activity;
import android.app.PictureInPictureParams;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.content.res.Configuration;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Rect;
import android.graphics.Typeface;
import android.hardware.GeomagneticField;
import android.hardware.SensorManager;
import android.os.Build;
import android.os.Bundle;
import android.os.SystemClock;
import android.util.Log;
import android.util.Rational;
import android.view.Choreographer;
import android.view.Display;
import android.view.GestureDetector;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;
import java.util.Locale;

/** Vsync-driven native sky. PiP stays animated until the Activity is no longer visible. */
public final class SkyActivity extends Activity {
    private static final String[] DIRECTIONS={"Nord","Nordost","Ost","Südost","Süd","Südwest","West","Nordwest"};
    private static final int[] TIME_RATES={1,60,600};
    private final SimpleDateFormat clock=new SimpleDateFormat("HH:mm:ss",Locale.GERMANY);
    private final SimpleDateFormat simulationClock=new SimpleDateFormat("dd.MM. HH:mm:ss",Locale.GERMANY);
    private SkyView sky;
    private LinearLayout root,header,controls;
    private TextView info,location,performance;
    private Button followButton,panButton,timeButton,windowButton;
    private DeviceOrientationTracker orientation;
    private final double[] cameraBasis=new double[9];
    private double latitude,longitude,azimuth=180,altitude=42,fov=100;
    private boolean hasLocation,started,pan,pendingPip,followPhone,hasCameraPose;
    private double declination,declinationLat=Double.NaN,declinationLon=Double.NaN;
    private long declinationTime,lastSensorLog;
    private int timeRateIndex;
    private long simulatedAnchorMillis,elapsedAnchorMillis;
    private double renderFps=Double.NaN,drawP95Millis;
    private String pipTime="",pipStats="Render-FPS werden gemessen";

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        SharedPreferences p=getSharedPreferences(SkyWidgetProvider.PREFS,MODE_PRIVATE);
        orientation=new DeviceOrientationTracker(this);
        followPhone=saved!=null?saved.getBoolean("followPhone",true)
                :p.getBoolean("follow_phone",true);
        if(!orientation.isAvailable())followPhone=false;
        if(saved!=null){
            azimuth=saved.getDouble("az",180);altitude=saved.getDouble("alt",42);fov=saved.getDouble("fov",100);
            pan=saved.getBoolean("pan",false);timeRateIndex=Math.max(0,Math.min(2,saved.getInt("timeRate",0)));
            simulatedAnchorMillis=saved.getLong("simulatedTime",System.currentTimeMillis());
        }else if(getIntent().hasExtra("direction")){
            azimuth=Math.floorMod(getIntent().getIntExtra("direction",2),4)*90;
        }else{
            azimuth=p.getFloat("live_az",180);altitude=p.getFloat("live_alt",42);fov=p.getFloat("live_fov",100);
        }
        if(simulatedAnchorMillis==0)simulatedAnchorMillis=System.currentTimeMillis();
        elapsedAnchorMillis=SystemClock.elapsedRealtime();
        pendingPip=saved==null&&getIntent().getBooleanExtra("open_pip",false);
        clamp();loadLocation();
        root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);
        header=new LinearLayout(this);header.setOrientation(LinearLayout.VERTICAL);
        header.setPadding(Ui.dp(this,12),Ui.dp(this,5),Ui.dp(this,12),Ui.dp(this,6));
        LinearLayout top=new LinearLayout(this);top.setGravity(android.view.Gravity.CENTER_VERTICAL);
        Button back=Ui.button(this,"‹",this::finish);back.setContentDescription("Zurück");
        top.addView(back,new LinearLayout.LayoutParams(Ui.dp(this,44),Ui.dp(this,44)));
        TextView title=Ui.text(this,"  Sternfenster · Live",19,0xffc1e5fa);title.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        top.addView(title,new LinearLayout.LayoutParams(0,-2,1));header.addView(top);
        info=Ui.text(this,"",13,Ui.TEXT);info.setPadding(0,Ui.dp(this,5),0,0);header.addView(info);
        location=Ui.text(this,"",12,Ui.MUTED);header.addView(location);
        performance=Ui.text(this,"Render-FPS werden gemessen …",12,0xffa9d7eb);header.addView(performance);
        root.addView(header);
        sky=new SkyView(this);root.addView(sky,new LinearLayout.LayoutParams(-1,0,1));
        controls=new LinearLayout(this);controls.setOrientation(LinearLayout.VERTICAL);
        controls.setPadding(Ui.dp(this,9),Ui.dp(this,2),Ui.dp(this,9),Ui.dp(this,5));
        LinearLayout directions=new LinearLayout(this);
        String[] names={"N","O","S","W"};
        String[] descriptions={"Nach Norden blicken","Nach Osten blicken","Nach Süden blicken","Nach Westen blicken"};
        for(int i=0;i<4;i++){
            final int direction=i;
            addControl(directions,names[i],1,descriptions[i],()->{
                setFollowing(false);
                pan=false;azimuth=direction*90;altitude=42;refreshInfo();
            });
        }
        controls.addView(directions);
        LinearLayout zoom=new LinearLayout(this);
        addControl(zoom,"−",1,"Herauszoomen",()->{fov*=1.22;clamp();refreshInfo();});
        addControl(zoom,"Zurücksetzen",2,"Blick nach Süden zurücksetzen",this::resetSky);
        addControl(zoom,"+",1,"Hineinzoomen",()->{fov/=1.22;clamp();refreshInfo();});
        controls.addView(zoom);
        LinearLayout motion=new LinearLayout(this);
        // Mixed one/two-line captions must not shift taller buttons below the row.
        motion.setBaselineAligned(false);
        motion.setGravity(android.view.Gravity.CENTER_VERTICAL);
        followButton=addControl(motion,"Handy folgen: an",1,"Blickrichtung des Handys folgen",()->{
            setFollowing(!followPhone);refreshInfo();
        });
        followButton.setEnabled(orientation.isAvailable());
        panButton=addControl(motion,"Rundblick: aus",1,"Automatischen Rundblick umschalten",()->{
            boolean enable=!pan;if(enable)setFollowing(false);pan=enable;refreshInfo();
        });
        timeButton=addControl(motion,"Zeit: 1×",1,"Zeitraffer umschalten",this::cycleTimeRate);
        windowButton=addControl(motion,"Live-Fenster",1,"Schwebendes Live-Fenster öffnen",this::enterLiveWindow);
        followButton.setTextSize(11);panButton.setTextSize(11);timeButton.setTextSize(11);windowButton.setTextSize(11);
        controls.addView(motion);root.addView(controls);
        if(!getPackageManager().hasSystemFeature(PackageManager.FEATURE_PICTURE_IN_PICTURE))windowButton.setEnabled(false);
        Ui.install(this,root);
        refreshInfo();
    }

    private Button addControl(LinearLayout row,String label,float weight,String description,Runnable action){
        Button button=Ui.button(this,label,action);button.setContentDescription(description);
        button.setMinHeight(Ui.dp(this,46));button.setMinimumHeight(Ui.dp(this,46));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-2,weight);
        lp.setMargins(Ui.dp(this,3),Ui.dp(this,3),Ui.dp(this,3),0);row.addView(button,lp);return button;
    }
    private void clamp(){
        if(!Double.isFinite(azimuth))azimuth=180;
        if(!Double.isFinite(altitude))altitude=42;
        if(!Double.isFinite(fov))fov=100;
        azimuth=SkyMath.wrap360(azimuth);altitude=Math.max(followPhone?-90:0,Math.min(followPhone?90:89,altitude));fov=Math.max(35,Math.min(135,fov));
    }
    private void setFollowing(boolean enabled){
        if(enabled&&!orientation.isAvailable())return;
        followPhone=enabled;
        if(enabled){
            pan=false;
            if(started&&!orientation.start()){
                followPhone=false;
                Toast.makeText(this,"Lagesensoren sind derzeit nicht verfügbar.",Toast.LENGTH_LONG).show();
            }
        }else{orientation.stop();hasCameraPose=false;}
        getSharedPreferences(SkyWidgetProvider.PREFS,MODE_PRIVATE).edit().putBoolean("follow_phone",followPhone).apply();
        clamp();
    }
    private void resetSky(){
        setFollowing(false);
        pan=false;azimuth=180;altitude=42;fov=100;timeRateIndex=0;
        simulatedAnchorMillis=System.currentTimeMillis();elapsedAnchorMillis=SystemClock.elapsedRealtime();refreshInfo();
    }
    private long skyTimeMillis(){
        if(timeRateIndex==0)return System.currentTimeMillis();
        return simulatedAnchorMillis+(SystemClock.elapsedRealtime()-elapsedAnchorMillis)*TIME_RATES[timeRateIndex];
    }
    private void cycleTimeRate(){
        long now=skyTimeMillis();timeRateIndex=(timeRateIndex+1)%TIME_RATES.length;
        simulatedAnchorMillis=timeRateIndex==0?System.currentTimeMillis():now;
        elapsedAnchorMillis=SystemClock.elapsedRealtime();refreshInfo();
    }
    private void loadLocation(){
        SharedPreferences p=getSharedPreferences(SkyWidgetProvider.PREFS,MODE_PRIVATE);
        latitude=p.getFloat("lat",51.0504f);longitude=p.getFloat("lon",13.7373f);hasLocation=p.getBoolean("has_gps",false);
        long now=System.currentTimeMillis();
        if(latitude!=declinationLat||longitude!=declinationLon||Math.abs(now-declinationTime)>86_400_000L){
            declination=new GeomagneticField((float)latitude,(float)longitude,0,now).getDeclination();
            if(!Double.isFinite(declination))declination=0;
            declinationLat=latitude;declinationLon=longitude;declinationTime=now;
        }
    }
    private float displayHz(){Display display=sky==null?null:sky.getDisplay();return display==null?0:display.getRefreshRate();}
    private void requestSmoothDisplay(){
        Display display=sky.getDisplay();if(display==null)return;
        Display.Mode current=display.getMode(),best=current;
        for(Display.Mode mode:display.getSupportedModes()){
            if(mode.getPhysicalWidth()==current.getPhysicalWidth()&&mode.getPhysicalHeight()==current.getPhysicalHeight()
                    &&mode.getRefreshRate()>best.getRefreshRate())best=mode;
        }
        WindowManager.LayoutParams attrs=getWindow().getAttributes();
        attrs.preferredDisplayModeId=best.getModeId();attrs.preferredRefreshRate=Math.max(60f,best.getRefreshRate());
        getWindow().setAttributes(attrs);
        if(Build.VERSION.SDK_INT>=35)sky.setRequestedFrameRate(Math.max(60f,best.getRefreshRate()));
    }
    private void refreshInfo(){
        if(sky==null)return;
        // MainActivity can save a new site while this Activity remains visible in PiP.
        loadLocation();
        clamp();String direction=DIRECTIONS[(int)Math.round(azimuth/45)%8];
        String time=(timeRateIndex==0?clock:simulationClock).format(new Date(skyTimeMillis()));
        String rate=timeRateIndex==0?"Echtzeit 1×":"Zeitraffer "+TIME_RATES[timeRateIndex]+"×";
        pipTime=time+" · "+rate;
        String followStatus=followPhone?(orientation.hasFreshSample()?"Handy folgt":"Warte auf Sensoren"):"Manuell";
        pipStats=(Double.isNaN(renderFps)?"Messung …":String.format(Locale.GERMANY,"%.1f Render-FPS",renderFps))
                +(followPhone?" · "+followStatus:pan?" · Rundblick":"");
        long now=SystemClock.elapsedRealtime();
        if(started&&now-lastSensorLog>=900){
            Log.i("SternfensterSensor",String.format(Locale.US,
                    "following=%s listening=%s fresh=%s az=%.2f alt=%.2f mode=%s accuracy=%d",
                    followPhone,orientation.isListening(),orientation.hasFreshSample(),azimuth,altitude,orientation.source(),orientation.accuracy()));
            lastSensorLog=now;
        }
        if(isInPictureInPictureMode())return;
        info.setText(String.format(Locale.GERMANY,"%s · %s %.0f° · Blickhöhe %.0f°",time,direction,azimuth,altitude));
        String sensorHint=followPhone?" · "+followStatus:"";
        if(followPhone&&orientation.hasFreshSample()&&orientation.accuracy()<=SensorManager.SENSOR_STATUS_ACCURACY_LOW)
            sensorHint+=" · Kompass ungenau";
        if(followPhone&&hasCameraPose&&altitude<0)sensorHint+=" · unter dem Horizont";
        location.setText((hasLocation?"Standort gespeichert":"Dresden · Standard")+" · "+rate+sensorHint);
        performance.setText(Double.isNaN(renderFps)?"Render-FPS werden gemessen …":String.format(Locale.GERMANY,
                "%.1f Render-FPS · %.0f Hz · Sichtfeld %.0f°",renderFps,displayHz(),fov));
        panButton.setText(pan?"Rundblick: an":"Rundblick: aus");
        followButton.setText(followPhone?"Handy folgen: an":"Handy folgen: aus");
        timeButton.setText("Zeit: "+TIME_RATES[timeRateIndex]+"×");
        String description="Sternkarte nach "+direction+", Blickhöhe "+Math.round(altitude)+" Grad. Mit Richtungstasten und Zoom bedienbar.";
        if(!description.contentEquals(sky.getContentDescription()==null?"":sky.getContentDescription()))sky.setContentDescription(description);
    }
    private void enterLiveWindow(){
        pendingPip=false;
        if(isInPictureInPictureMode())return;
        if(!getPackageManager().hasSystemFeature(PackageManager.FEATURE_PICTURE_IN_PICTURE)){
            Toast.makeText(this,"Dieses Gerät bietet kein Bild-im-Bild-Fenster.",Toast.LENGTH_LONG).show();return;
        }
        Rect bounds=new Rect();sky.getGlobalVisibleRect(bounds);
        PictureInPictureParams.Builder builder=new PictureInPictureParams.Builder().setAspectRatio(new Rational(1,1));
        if(!bounds.isEmpty())builder.setSourceRectHint(bounds);
        if(Build.VERSION.SDK_INT>=31)builder.setSeamlessResizeEnabled(false);
        try{
            if(!enterPictureInPictureMode(builder.build()))Toast.makeText(this,"Bild-im-Bild ist für Sternfenster derzeit nicht verfügbar.",Toast.LENGTH_LONG).show();
        }catch(IllegalStateException|IllegalArgumentException e){
            Log.w("Sternfenster","PiP unavailable",e);
            Toast.makeText(this,"Live-Fenster konnte nicht geöffnet werden. Die Vollansicht bleibt verfügbar.",Toast.LENGTH_LONG).show();
        }
    }
    private void applyWindowMode(){
        boolean pip=isInPictureInPictureMode();
        if(pip)pendingPip=false;
        header.setVisibility(pip?View.GONE:View.VISIBLE);controls.setVisibility(pip?View.GONE:View.VISIBLE);
        root.requestApplyInsets();sky.resetStatistics();refreshInfo();
        if(started)sky.startFrames();
    }
    @Override public void onPictureInPictureModeChanged(boolean pip,Configuration configuration){
        super.onPictureInPictureModeChanged(pip,configuration);applyWindowMode();
    }
    @Override public void onConfigurationChanged(Configuration configuration){
        super.onConfigurationChanged(configuration);applyWindowMode();sky.post(this::requestSmoothDisplay);
    }
    @Override protected void onStart(){
        super.onStart();started=true;loadLocation();applyWindowMode();
        if(followPhone)setFollowing(true);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        sky.post(this::requestSmoothDisplay);
    }
    @Override protected void onResume(){super.onResume();loadLocation();refreshInfo();}
    @Override protected void onPause(){
        // PiP is paused but still visible: rendering deliberately continues here.
        getSharedPreferences(SkyWidgetProvider.PREFS,MODE_PRIVATE).edit()
                .putFloat("live_az",(float)azimuth).putFloat("live_alt",(float)altitude).putFloat("live_fov",(float)fov).apply();
        super.onPause();
    }
    @Override protected void onStop(){
        started=false;orientation.stop();hasCameraPose=false;sky.stopFrames();getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);super.onStop();
    }
    @Override protected void onSaveInstanceState(Bundle out){
        out.putDouble("az",azimuth);out.putDouble("alt",altitude);out.putDouble("fov",fov);
        out.putBoolean("pan",pan);out.putBoolean("followPhone",followPhone);out.putInt("timeRate",timeRateIndex);out.putLong("simulatedTime",skyTimeMillis());super.onSaveInstanceState(out);
    }
    @Override protected void onNewIntent(Intent intent){
        super.onNewIntent(intent);setIntent(intent);
        if(intent.hasExtra("direction")){
            // A widget's sector is the initial/manual view, not an implicit opt-out
            // from the user's sensor-follow preference.
            pan=false;azimuth=Math.floorMod(intent.getIntExtra("direction",2),4)*90;altitude=42;fov=100;
        }
        pendingPip=intent.getBooleanExtra("open_pip",false)&&!isInPictureInPictureMode();loadLocation();refreshInfo();
    }

    private final class SkyView extends View implements Choreographer.FrameCallback {
        private final LiveSkyRenderer renderer;
        private final GestureDetector gestures;
        private final ScaleGestureDetector scale;
        private final Paint hudPaint=new Paint(Paint.ANTI_ALIAS_FLAG);
        private final long[] drawDurations=new long[512],sortedDurations=new long[512];
        private boolean active;
        private long previousFrame,statisticsStart;
        private int drawnFrames,durationCount;
        SkyView(Context context){
            super(context);setFocusable(true);setClickable(true);
            renderer=new LiveSkyRenderer(context);
            scale=new ScaleGestureDetector(context,new ScaleGestureDetector.SimpleOnScaleGestureListener(){
                @Override public boolean onScaleBegin(ScaleGestureDetector detector){pan=false;return true;}
                @Override public boolean onScale(ScaleGestureDetector detector){
                    fov/=Math.max(.1,detector.getScaleFactor());clamp();return true;
                }
            });
            gestures=new GestureDetector(context,new GestureDetector.SimpleOnGestureListener(){
                @Override public boolean onDown(MotionEvent event){return true;}
                @Override public boolean onScroll(MotionEvent first,MotionEvent current,float dx,float dy){
                    if(scale.isInProgress()||current.getPointerCount()>1)return true;
                    if(followPhone)setFollowing(false);
                    pan=false;double degrees=fov/Math.max(1,getHeight());azimuth+=dx*degrees;altitude-=dy*degrees;clamp();return true;
                }
                @Override public boolean onSingleTapUp(MotionEvent event){performClick();return true;}
            });
        }
        void startFrames(){
            if(active)return;active=true;previousFrame=0;resetStatistics();
            Choreographer.getInstance().postFrameCallback(this);
        }
        void stopFrames(){
            active=false;previousFrame=0;Choreographer.getInstance().removeFrameCallback(this);
            Log.i("SternfensterPerf","rendering_stopped");
        }
        void resetStatistics(){statisticsStart=System.nanoTime();drawnFrames=0;durationCount=0;renderFps=Double.NaN;}
        @Override public void doFrame(long frameTimeNanos){
            if(!active)return;
            if(followPhone){
                Display display=getDisplay();
                if(orientation.cameraBasis(frameTimeNanos,display==null?0:display.getRotation(),declination,cameraBasis)){
                    hasCameraPose=true;
                    azimuth=DeviceOrientationMath.azimuth(cameraBasis,azimuth);
                    altitude=DeviceOrientationMath.altitude(cameraBasis);
                }
            }
            if(previousFrame!=0&&pan){
                double seconds=Math.max(0,Math.min(.1,(frameTimeNanos-previousFrame)/1_000_000_000.0));
                azimuth=SkyMath.wrap360(azimuth+seconds*5.0);
            }
            previousFrame=frameTimeNanos;invalidate();Choreographer.getInstance().postFrameCallback(this);
        }
        @Override protected void onDraw(Canvas canvas){
            super.onDraw(canvas);if(getWidth()<=0||getHeight()<=0)return;
            long start=System.nanoTime();
            renderer.draw(canvas,getWidth(),getHeight(),latitude,longitude,azimuth,altitude,fov,skyTimeMillis(),true,
                    followPhone&&hasCameraPose?cameraBasis:null);
            boolean pip=isInPictureInPictureMode();
            if(pip){
                float font=Math.max(8,Math.min(14*getResources().getDisplayMetrics().density,getWidth()*.045f));
                hudPaint.setTextSize(font);hudPaint.setStyle(Paint.Style.FILL);hudPaint.setColor(0xbb08121e);
                float pad=font*.5f;canvas.drawRect(0,0,getWidth(),font*3.2f,hudPaint);
                hudPaint.setColor(0xffd6eaf5);canvas.drawText(pipTime,pad,font*1.25f,hudPaint);
                canvas.drawText(pipStats,pad,font*2.65f,hudPaint);
            }
            long end=System.nanoTime();
            if(active){
                drawnFrames++;if(durationCount<drawDurations.length)drawDurations[durationCount++]=end-start;
                long elapsed=end-statisticsStart;
                if(elapsed>=1_000_000_000L){
                    renderFps=drawnFrames*1_000_000_000.0/elapsed;
                    System.arraycopy(drawDurations,0,sortedDurations,0,durationCount);
                    Arrays.sort(sortedDurations,0,durationCount);
                    drawP95Millis=durationCount==0?0:sortedDurations[Math.min(durationCount-1,(int)Math.ceil(durationCount*.95)-1)]/1_000_000.0;
                    Log.i("SternfensterPerf",String.format(Locale.US,
                            "mode=%s frames=%d fps=%.2f draw_p95_ms=%.3f hz=%.1f pan=%s",
                            pip?"pip":"fullscreen",drawnFrames,renderFps,drawP95Millis,displayHz(),pan));
                    statisticsStart=end;drawnFrames=0;durationCount=0;
                    post(SkyActivity.this::refreshInfo);
                }
            }
            if(pendingPip&&started&&!pip){pendingPip=false;post(SkyActivity.this::enterLiveWindow);}
        }
        @Override public boolean onTouchEvent(MotionEvent event){
            scale.onTouchEvent(event);gestures.onTouchEvent(event);
            if(event.getActionMasked()==MotionEvent.ACTION_UP||event.getActionMasked()==MotionEvent.ACTION_CANCEL)refreshInfo();
            return true;
        }
        @Override public boolean performClick(){super.performClick();return true;}
    }
}
