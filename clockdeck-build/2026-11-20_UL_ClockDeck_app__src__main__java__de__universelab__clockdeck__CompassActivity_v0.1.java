package de.universelab.clockdeck;

import android.app.Activity;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.os.Bundle;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.util.Locale;

/** Tilt-compensated magnetic bearing. Not intended for safety-critical navigation. */
public final class CompassActivity extends Activity implements SensorEventListener {
    private SensorManager sensors;
    private Sensor accel,magnet;
    private float[] gravity=new float[3],magField=new float[3];
    private boolean hasG=false,hasM=false;
    private float heading=Float.NaN;
    private TextView status;
    private View dial;
    @Override public void onCreate(Bundle state){super.onCreate(state);
        getWindow().setStatusBarColor(Color.rgb(4,10,20));
        getWindow().setNavigationBarColor(Color.BLACK);
        sensors=(SensorManager)getSystemService(SENSOR_SERVICE);
        accel=sensors.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        magnet=sensors.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);
        LinearLayout main=new LinearLayout(this);main.setOrientation(LinearLayout.VERTICAL);
        main.setGravity(android.view.Gravity.CENTER_HORIZONTAL);
        main.setPadding(22,36,22,22);main.setBackgroundColor(Color.rgb(6,12,22));
        TextView title=new TextView(this);title.setText("UNIVERSELAB / MAGNETKOMPASS");
        title.setTextColor(Color.rgb(124,224,255));title.setTextSize(18);
        main.addView(title);
        status=new TextView(this);status.setTextColor(Color.WHITE);status.setTextSize(17);
        status.setGravity(android.view.Gravity.CENTER);
        status.setPadding(0,24,0,6);main.addView(status);
        dial=new View(this){
            private final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
            @Override protected void onDraw(Canvas c){super.onDraw(c);
                int w=getWidth(),h=getHeight();float r=Math.min(w,h)*.45f;
                new ClockRenderer().drawFace(c,w/2f,h/2f,r,1,System.currentTimeMillis(),
                        System.nanoTime()/1e9,0,0,heading,Battery.percent(CompassActivity.this),true);
                if(!Float.isNaN(heading)){
                    c.save();c.rotate(-heading,w/2f,h/2f);
                    p.setColor(Color.rgb(255,63,71));p.setStrokeWidth(7);
                    c.drawLine(w/2f,h/2f-25,w/2f,h/2f-r*.60f,p);
                    p.setColor(Color.WHITE);c.drawCircle(w/2f,h/2f,6,p);c.restore();
                }
            }
        };
        main.addView(dial,new LinearLayout.LayoutParams(-1,0,1f));
        TextView warning=new TextView(this);
        warning.setText("Magnetischer Norden · Handy waagerecht halten · bei Abweichung in einer Acht bewegen. Nicht zur sicherheitskritischen Navigation verwenden.");
        warning.setTextColor(Color.rgb(151,171,189));warning.setTextSize(13);
        main.addView(warning);
        setContentView(main);
        if(accel==null||magnet==null)status.setText("Keine Magnetometer-/Beschleunigungssensordaten verfügbar");
    }
    @Override protected void onResume(){super.onResume();
        if(accel!=null)sensors.registerListener(this,accel,SensorManager.SENSOR_DELAY_UI);
        if(magnet!=null)sensors.registerListener(this,magnet,SensorManager.SENSOR_DELAY_UI);
    }
    @Override protected void onPause(){sensors.unregisterListener(this);super.onPause();}
    @Override public void onSensorChanged(SensorEvent e){
        if(e.sensor.getType()==Sensor.TYPE_ACCELEROMETER){
            smooth(gravity,e.values);hasG=true;
        }else if(e.sensor.getType()==Sensor.TYPE_MAGNETIC_FIELD){
            smooth(magField,e.values);hasM=true;
        }
        if(hasG&&hasM){
            float[] rotation=new float[9],orientation=new float[3];
            if(SensorManager.getRotationMatrix(rotation,null,gravity,magField)){
                SensorManager.getOrientation(rotation,orientation);
                float next=(float)((Math.toDegrees(orientation[0])+360)%360);
                if(Float.isNaN(heading))heading=next;
                else heading=(heading+((next-heading+540)%360-180)*.19f+360)%360;
                status.setText(String.format(Locale.GERMANY,"%03d°  ·  %s",Math.round(heading)%360,cardinal(heading)));
                dial.invalidate();
            }else status.setText("Magnetfeld gestört / Sensor kalibrieren");
        }
    }
    private void smooth(float[] out,float[] in){for(int i=0;i<3;i++)out[i]=out[i]==0?in[i]:out[i]*.82f+in[i]*.18f;}
    private static String cardinal(float deg){String[] s={"N","NO","O","SO","S","SW","W","NW"};return s[Math.round(deg/45f)%8];}
    @Override public void onAccuracyChanged(Sensor sensor,int accuracy){
        if(sensor.getType()==Sensor.TYPE_MAGNETIC_FIELD && accuracy==SensorManager.SENSOR_STATUS_UNRELIABLE)
            status.setText("Magnetfeld unzuverlässig – bitte kalibrieren");
    }
}
