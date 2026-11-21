package de.universelab.sternfenster;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.hardware.GeomagneticField;
import android.os.SystemClock;
import android.util.Log;
import android.view.Choreographer;
import android.view.Display;
import android.view.GestureDetector;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import android.view.View;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;
import java.util.Locale;

/** One independently owned, vsync-driven sky; never retains an Activity. */
final class OverlaySkyView extends View implements Choreographer.FrameCallback {
    private final SharedPreferences preferences;
    private final LiveSkyRenderer renderer;
    private final DeviceOrientationTracker orientation;
    private final ScaleGestureDetector scale;
    private final GestureDetector gestures;
    private final Paint hudPaint=new Paint(Paint.ANTI_ALIAS_FLAG);
    private final double[] cameraBasis=new double[9];
    private final long[] drawDurations=new long[512],sortedDurations=new long[512];
    private final SimpleDateFormat clock=new SimpleDateFormat("HH:mm:ss",Locale.GERMANY);
    private final Runnable statusRefresh=this::refreshStatus;
    private Runnable controlsChanged;
    private double latitude,longitude,azimuth,altitude,fov,declination;
    private double declinationLatitude=Double.NaN,declinationLongitude=Double.NaN;
    private double fps=Double.NaN;
    private boolean following,pan,hasCameraPose,screenUsable,active,disposed;
    private long previousFrame,statisticsStart,declinationTime,lastSensorLog;
    private long simulatedAnchor,elapsedAnchor;
    private int timeRate=1,drawnFrames,durationCount;
    private String hudTime="",hudState="Render-FPS werden gemessen";

    OverlaySkyView(Context context,SharedPreferences preferences,Intent intent){
        super(context);this.preferences=preferences;
        renderer=new LiveSkyRenderer(context);orientation=new DeviceOrientationTracker(context);
        setClickable(true);setContentDescription("Live-Sternkarte; wischen und mit zwei Fingern zoomen");
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
                if(following)setFollowing(false);
                pan=false;double degrees=fov/Math.max(1,getHeight());
                azimuth+=dx*degrees;altitude-=dy*degrees;clamp();return true;
            }
            @Override public boolean onSingleTapUp(MotionEvent event){performClick();return true;}
        });
        applyIntent(intent);
    }

    void setControlsChanged(Runnable callback){controlsChanged=callback;refreshStatus();}
    boolean isFollowing(){return following;}
    boolean hasSensors(){return orientation.isAvailable();}

    void applyIntent(Intent intent){
        azimuth=number(intent,"az",preferences.getFloat("live_az",180));
        altitude=number(intent,"alt",preferences.getFloat("live_alt",42));
        fov=number(intent,"fov",preferences.getFloat("live_fov",100));
        following=(intent!=null?intent.getBooleanExtra("follow",preferences.getBoolean("follow_phone",true))
                :preferences.getBoolean("follow_phone",true))&&orientation.isAvailable();
        pan=!following&&(intent==null?preferences.getBoolean("overlay_pan",false):intent.getBooleanExtra("pan",false));
        timeRate=intent==null?preferences.getInt("overlay_time_rate",1):intent.getIntExtra("timeRate",1);
        if(timeRate!=60&&timeRate!=600)timeRate=1;
        long elapsed=SystemClock.elapsedRealtime();
        simulatedAnchor=intent==null?preferences.getLong("overlay_sky_time",System.currentTimeMillis())
                :intent.getLongExtra("skyTime",System.currentTimeMillis());
        if(intent==null&&timeRate!=1){
            long saved=preferences.getLong("overlay_elapsed_time",elapsed);
            if(elapsed>=saved)simulatedAnchor+=(elapsed-saved)*timeRate;
        }
        elapsedAnchor=elapsed;hasCameraPose=false;clamp();loadLocation();
        if(active){if(following)orientation.start();else orientation.stop();}
        persistState();refreshStatus();invalidate();
    }
    private static double number(Intent intent,String name,double fallback){
        double value=intent==null?fallback:intent.getDoubleExtra(name,fallback);
        return Double.isFinite(value)?value:fallback;
    }
    void setFollowing(boolean enabled){
        following=enabled&&orientation.isAvailable();
        if(following){pan=false;if(active&&!orientation.start())following=false;}
        if(!following){orientation.stop();hasCameraPose=false;}
        clamp();persistState();refreshStatus();invalidate();
    }
    void zoom(double factor){fov*=factor;clamp();persistState();refreshStatus();invalidate();}
    void setScreenUsable(boolean value){screenUsable=value;syncRunning();}
    private void syncRunning(){
        boolean run=!disposed&&screenUsable&&isAttachedToWindow()&&getWindowVisibility()==VISIBLE&&isShown();
        if(run==active)return;
        active=run;previousFrame=0;
        if(run){
            if(following&&!orientation.start())following=false;
            statisticsStart=System.nanoTime();drawnFrames=durationCount=0;fps=Double.NaN;
            refreshStatus();Choreographer.getInstance().postFrameCallback(this);
            Log.i("SternfensterPerf","rendering_started mode=overlay");
        }else{
            Choreographer.getInstance().removeFrameCallback(this);removeCallbacks(statusRefresh);
            orientation.stop();hasCameraPose=false;
            Log.i("SternfensterPerf","rendering_stopped mode=overlay");
            Log.i("SternfensterSensor","mode=overlay listening_stopped");
        }
    }
    void dispose(){persistState();disposed=true;screenUsable=false;syncRunning();orientation.stop();removeCallbacks(statusRefresh);}
    @Override protected void onAttachedToWindow(){super.onAttachedToWindow();syncRunning();}
    @Override protected void onDetachedFromWindow(){
        boolean permitted=screenUsable;screenUsable=false;syncRunning();screenUsable=permitted;super.onDetachedFromWindow();
    }
    @Override protected void onWindowVisibilityChanged(int visibility){super.onWindowVisibilityChanged(visibility);if(orientation!=null)syncRunning();}
    @Override protected void onVisibilityChanged(View changed,int visibility){super.onVisibilityChanged(changed,visibility);if(orientation!=null)syncRunning();}

    private void clamp(){
        azimuth=Double.isFinite(azimuth)?SkyMath.wrap360(azimuth):180;
        altitude=Double.isFinite(altitude)?Math.max(following?-90:0,Math.min(following?90:89,altitude)):42;
        fov=Double.isFinite(fov)?Math.max(35,Math.min(135,fov)):100;
    }
    private long skyTime(){return timeRate==1?System.currentTimeMillis():simulatedAnchor+(SystemClock.elapsedRealtime()-elapsedAnchor)*timeRate;}
    void persistState(){
        preferences.edit().putFloat("live_az",(float)azimuth).putFloat("live_alt",(float)altitude)
                .putFloat("live_fov",(float)fov).putBoolean("follow_phone",following)
                .putBoolean("overlay_pan",pan).putInt("overlay_time_rate",timeRate)
                .putLong("overlay_sky_time",skyTime()).putLong("overlay_elapsed_time",SystemClock.elapsedRealtime()).apply();
    }
    private void loadLocation(){
        latitude=preferences.getFloat("lat",51.0504f);longitude=preferences.getFloat("lon",13.7373f);
        if(!Double.isFinite(latitude)||Math.abs(latitude)>90)latitude=51.0504;
        if(!Double.isFinite(longitude)||Math.abs(longitude)>180)longitude=13.7373;
        long now=System.currentTimeMillis();
        if(latitude!=declinationLatitude||longitude!=declinationLongitude||Math.abs(now-declinationTime)>86_400_000L){
            declination=new GeomagneticField((float)latitude,(float)longitude,0,now).getDeclination();
            if(!Double.isFinite(declination))declination=0;
            declinationLatitude=latitude;declinationLongitude=longitude;declinationTime=now;
        }
    }
    private float displayHz(){Display display=getDisplay();return display==null?0:display.getRefreshRate();}
    private void refreshStatus(){
        if(disposed)return;
        loadLocation();
        String mode=following?(orientation.hasFreshSample()?"Handy folgt":"Warte auf Sensoren"):pan?"Rundblick":"Manuell";
        hudTime=clock.format(new Date(skyTime()))+(timeRate==1?" · Echtzeit":" · Zeitraffer "+timeRate+"×");
        hudState=(Double.isNaN(fps)?"Messung …":String.format(Locale.GERMANY,"%.1f Render-FPS",fps))+" · "+mode;
        long now=SystemClock.elapsedRealtime();
        if(active&&now-lastSensorLog>=900){
            Log.i("SternfensterSensor",String.format(Locale.US,
                    "mode=overlay following=%s listening=%s fresh=%s az=%.2f alt=%.2f source=%s accuracy=%d",
                    following,orientation.isListening(),orientation.hasFreshSample(),azimuth,altitude,orientation.source(),orientation.accuracy()));
            lastSensorLog=now;
        }
        if(controlsChanged!=null)controlsChanged.run();
    }
    @Override public void doFrame(long frameTimeNanos){
        if(!active)return;
        if(following){
            Display display=getDisplay();
            if(orientation.cameraBasis(frameTimeNanos,display==null?0:display.getRotation(),declination,cameraBasis)){
                hasCameraPose=true;azimuth=DeviceOrientationMath.azimuth(cameraBasis,azimuth);
                altitude=DeviceOrientationMath.altitude(cameraBasis);
            }
        }
        if(previousFrame!=0&&pan){
            double seconds=Math.max(0,Math.min(.1,(frameTimeNanos-previousFrame)/1_000_000_000.0));
            azimuth=SkyMath.wrap360(azimuth+5*seconds);
        }
        previousFrame=frameTimeNanos;invalidate();Choreographer.getInstance().postFrameCallback(this);
    }
    @Override protected void onDraw(Canvas canvas){
        super.onDraw(canvas);if(getWidth()<=0||getHeight()<=0)return;
        long begin=System.nanoTime();
        renderer.draw(canvas,getWidth(),getHeight(),latitude,longitude,azimuth,altitude,fov,skyTime(),true,
                following&&hasCameraPose?cameraBasis:null);
        float font=Math.max(8,Math.min(11*getResources().getDisplayMetrics().density,getWidth()*.043f));
        hudPaint.setTextSize(font);hudPaint.setColor(0xc508121e);
        canvas.drawRect(0,0,getWidth(),font*3.1f,hudPaint);hudPaint.setColor(0xffd6eaf5);
        canvas.drawText(hudTime,font*.55f,font*1.2f,hudPaint);canvas.drawText(hudState,font*.55f,font*2.6f,hudPaint);
        long end=System.nanoTime();
        if(!active)return;
        drawnFrames++;if(durationCount<drawDurations.length)drawDurations[durationCount++]=end-begin;
        long elapsed=end-statisticsStart;
        if(elapsed>=1_000_000_000L){
            fps=drawnFrames*1_000_000_000.0/elapsed;
            System.arraycopy(drawDurations,0,sortedDurations,0,durationCount);Arrays.sort(sortedDurations,0,durationCount);
            double p95=durationCount==0?0:sortedDurations[Math.min(durationCount-1,(int)Math.ceil(durationCount*.95)-1)]/1_000_000.0;
            Log.i("SternfensterPerf",String.format(Locale.US,
                    "mode=overlay frames=%d fps=%.2f draw_p95_ms=%.3f hz=%.1f pan=%s",drawnFrames,fps,p95,displayHz(),pan));
            statisticsStart=end;drawnFrames=durationCount=0;post(statusRefresh);
        }
    }
    @Override public boolean onTouchEvent(MotionEvent event){
        scale.onTouchEvent(event);gestures.onTouchEvent(event);
        if(event.getActionMasked()==MotionEvent.ACTION_UP||event.getActionMasked()==MotionEvent.ACTION_CANCEL){persistState();refreshStatus();}
        return true;
    }
    @Override public boolean performClick(){super.performClick();return true;}
}
