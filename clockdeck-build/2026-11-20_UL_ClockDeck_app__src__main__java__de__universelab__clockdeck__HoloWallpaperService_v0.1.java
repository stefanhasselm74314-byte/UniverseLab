package de.universelab.clockdeck;

import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Handler;
import android.os.Looper;
import android.os.PowerManager;
import android.service.wallpaper.WallpaperService;
import android.view.SurfaceHolder;
import java.util.Calendar;
import java.util.Locale;

/** Native interactive, CPU-bounded 2.5D clock wallpaper, no permissions required. */
public final class HoloWallpaperService extends WallpaperService {
    @Override public Engine onCreateEngine(){return new DialEngine();}

    private final class DialEngine extends Engine implements SensorEventListener {
        private final Handler h=new Handler(Looper.getMainLooper());
        private final Runnable painter=this::paintFrame;
        private final ClockRenderer renderer=new ClockRenderer();
        private final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
        private final SharedPreferences prefs=getSharedPreferences("settings",MODE_PRIVATE);
        private final SensorManager sensors=(SensorManager)getSystemService(Context.SENSOR_SERVICE);
        private final Sensor accel=sensors.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        private final Sensor magnetic=sensors.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);
        private final PowerManager power=(PowerManager)getSystemService(Context.POWER_SERVICE);
        private final float[] g={0,0,9.81f},m={0,0,0};
        private boolean haveG=false,haveM=false,visible=false,surfaceReady=false;
        private float tx=0,ty=0,heading=Float.NaN;
        private int battery=-1;
        private long lastBattery=0;
        @Override public void onVisibilityChanged(boolean show){
            visible=show;h.removeCallbacks(painter);
            sensors.unregisterListener(this);
            if(show){
                if(accel!=null)sensors.registerListener(this,accel,SensorManager.SENSOR_DELAY_UI);
                if(magnetic!=null)sensors.registerListener(this,magnetic,SensorManager.SENSOR_DELAY_UI);
                paintFrame();
            }
        }
        @Override public void onSurfaceCreated(SurfaceHolder holder){super.onSurfaceCreated(holder);surfaceReady=true;if(visible)paintFrame();}
        @Override public void onSurfaceChanged(SurfaceHolder holder,int format,int width,int height){super.onSurfaceChanged(holder,format,width,height);surfaceReady=true;if(visible)paintFrame();}
        @Override public void onSurfaceDestroyed(SurfaceHolder holder){surfaceReady=false;h.removeCallbacks(painter);super.onSurfaceDestroyed(holder);}
        @Override public void onDestroy(){visible=false;surfaceReady=false;sensors.unregisterListener(this);h.removeCallbacks(painter);super.onDestroy();}
        @Override public void onSensorChanged(SensorEvent event){
            if(event.sensor.getType()==Sensor.TYPE_ACCELEROMETER){
                for(int i=0;i<3;i++)g[i]=g[i]*.87f+event.values[i]*.13f;
                tx=Math.max(-14,Math.min(14,g[1]*1.5f));
                ty=Math.max(-14,Math.min(14,-g[0]*1.5f));
                haveG=true;
            }else if(event.sensor.getType()==Sensor.TYPE_MAGNETIC_FIELD){
                for(int i=0;i<3;i++)m[i]=m[i]*.86f+event.values[i]*.14f;
                haveM=true;
            }
            if(haveG&&haveM){
                float[] R=new float[9],orient=new float[3];
                if(SensorManager.getRotationMatrix(R,null,g,m)){
                    SensorManager.getOrientation(R,orient);
                    float next=(float)((Math.toDegrees(orient[0])+360)%360);
                    if(Float.isNaN(heading))heading=next;
                    else heading=(heading+((next-heading+540)%360-180)*.15f+360)%360;
                }
            }
        }
        @Override public void onAccuracyChanged(Sensor sensor,int accuracy){}
        private void label(Canvas c,String text,float x,float y,float sz,int color){
            p.setColor(color);p.setStyle(Paint.Style.FILL);p.setTypeface(android.graphics.Typeface.create("sans-serif-condensed",android.graphics.Typeface.BOLD));
            p.setTextSize(sz);p.setTextAlign(Paint.Align.CENTER);c.drawText(text,x,y,p);
        }
        private void paintFrame(){
            h.removeCallbacks(painter);
            if(!visible||!surfaceReady)return;
            Canvas c=null;
            try{
                c=getSurfaceHolder().lockCanvas();if(c==null)return;
                int w=c.getWidth(),hh=c.getHeight();
                c.drawColor(Color.rgb(2,5,13));
                long now=System.currentTimeMillis();
                if(now-lastBattery>30000||battery<0){battery=Battery.percent(HoloWallpaperService.this);lastBattery=now;}
                int style=prefs.getInt("wall_style",2);
                boolean parallax=prefs.getBoolean("parallax",true);
                float dx=parallax?tx:0,dy=parallax?ty:0;
                // Procedural stars and ghosted orbital arcs, all below the widgets/icons.
                for(int i=0;i<130;i++){
                    int xx=((i*1271+37)%1009)*w/1009,yy=((i*1907+103)%1543)*hh/1543;
                    p.setColor(Color.argb(30+i%6*10,124,176,224));
                    c.drawCircle(xx+dx*.21f,yy+dy*.21f,(i%4==0?1.6f:.7f)*Math.max(1f,w/1080f),p);
                }
                float r=Math.min(w*.465f,hh*.315f);
                float cx=w*.50f+dx*1.15f,cy=hh*.42f+dy*.85f;
                renderer.drawFace(c,cx,cy,r,style,now,now/1000.0,dx,dy,
                        style==1?heading:Float.NaN,battery,true);
                label(c,"U N I V E R S E L A B",w/2f,hh*.79f,Math.min(w*.039f,35),Color.rgb(171,211,229));
                label(c,style==0?"TITAN  /  SKELETON":style==1?"MAGNETIC  /  COMPASS":"HOLO  /  SIX-DIMENSIONAL",w/2f,hh*.82f,
                        Math.min(w*.025f,23),style==2?Color.rgb(61,196,245):Color.rgb(174,192,211));
                Calendar date=Calendar.getInstance();date.setTimeInMillis(now);
                label(c,String.format(Locale.GERMANY,"%02d.%02d.%04d",date.get(Calendar.DAY_OF_MONTH),date.get(Calendar.MONTH)+1,date.get(Calendar.YEAR)),
                        w/2f,hh*.87f,Math.min(w*.035f,31),Color.rgb(147,172,196));
            }catch(Exception ignored){
                // The surface can disappear during launcher transitions.
            }finally{if(c!=null)try{getSurfaceHolder().unlockCanvasAndPost(c);}catch(Exception ignored){}
                if(visible&&surfaceReady){
                    int fps=prefs.getInt("fps",18);
                    if(power!=null&&power.isPowerSaveMode())fps=Math.min(fps,5);
                    h.postDelayed(painter,Math.max(50,1000/Math.max(1,fps)));
                }
            }
        }
    }
}
