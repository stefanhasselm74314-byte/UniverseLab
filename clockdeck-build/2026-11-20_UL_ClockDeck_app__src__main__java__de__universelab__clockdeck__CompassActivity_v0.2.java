package de.universelab.clockdeck;

import android.app.Activity;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.os.Build;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.WindowInsets;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.util.Locale;

/** Live tilt-compensated magnetic heading, with safe areas on Android 15+. */
public final class CompassActivity extends Activity implements SensorEventListener {
    private SensorManager sensors;
    private Sensor accel,magnet;
    private final float[] gravity=new float[3],magField=new float[3];
    private boolean hasG=false,hasM=false;
    private float heading=Float.NaN;
    private TextView status;
    private View dial;
    private int dp(float d){return Math.round(d*getResources().getDisplayMetrics().density);}
    private static final int BACK=Color.rgb(6,12,22);

    @Override public void onCreate(Bundle state){super.onCreate(state);
        getWindow().setStatusBarColor(BACK);
        getWindow().setNavigationBarColor(BACK);
        sensors=(SensorManager)getSystemService(SENSOR_SERVICE);
        accel=sensors.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        magnet=sensors.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);

        ScrollView scroll=new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setClipToPadding(false);
        scroll.setBackgroundColor(BACK);
        scroll.setPadding(dp(16),dp(18),dp(16),dp(24));
        LinearLayout content=new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setGravity(Gravity.CENTER_HORIZONTAL);
        scroll.addView(content,new ScrollView.LayoutParams(-1,-2));

        TextView title=new TextView(this);
        title.setText("UNIVERSELAB  /  MAGNETKOMPASS");
        title.setTextColor(Color.rgb(124,224,255));
        title.setTextSize(16);
        title.setGravity(Gravity.CENTER);
        title.setPadding(0,dp(6),0,dp(8));
        content.addView(title,new LinearLayout.LayoutParams(-1,-2));

        status=new TextView(this);
        status.setText("Magnetsensor wird ausgelesen …");
        status.setTextColor(Color.WHITE);
        status.setTextSize(25);
        status.setGravity(Gravity.CENTER);
        status.setPadding(0,dp(12),0,dp(8));
        content.addView(status,new LinearLayout.LayoutParams(-1,-2));

        dial=new View(this){
            private final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
            private final ClockRenderer renderer=new ClockRenderer();
            @Override protected void onDraw(Canvas c){super.onDraw(c);
                int w=getWidth(),h=getHeight();
                float r=Math.min(w,h)*.485f;
                renderer.drawFace(c,w/2f,h/2f,r,1,System.currentTimeMillis(),
                    System.nanoTime()/1e9,0,0,heading,Battery.percent(CompassActivity.this),true);
                if(!Float.isNaN(heading)){
                    c.save();c.rotate(-heading,w/2f,h/2f);
                    p.setColor(Color.rgb(255,76,86));p.setStrokeWidth(dp(2.1f));
                    c.drawLine(w/2f,h/2f-dp(9),w/2f,h/2f-r*.60f,p);
                    p.setColor(Color.WHITE);c.drawCircle(w/2f,h/2f,dp(2.5f),p);
                    c.restore();
                }
            }
        };
        int screenWidth=getResources().getDisplayMetrics().widthPixels;
        int dialSize=Math.min(screenWidth-dp(40),dp(430));
        LinearLayout.LayoutParams disc=new LinearLayout.LayoutParams(-1,dialSize);
        disc.topMargin=dp(12);disc.bottomMargin=dp(8);
        content.addView(dial,disc);

        TextView warning=new TextView(this);
        warning.setText("Magnetischer Norden · Handy waagerecht halten. Bei Abweichungen " +
                "das Gerät in einer Acht bewegen. Nicht zur sicherheitskritischen Navigation verwenden.");
        warning.setTextColor(Color.rgb(171,191,210));
        warning.setTextSize(13);
        warning.setGravity(Gravity.CENTER);
        warning.setPadding(dp(5),dp(9),dp(5),dp(18));
        content.addView(warning,new LinearLayout.LayoutParams(-1,-2));
        setContentView(scroll);

        if(Build.VERSION.SDK_INT>=30){
            scroll.setOnApplyWindowInsetsListener((v,insets)->{
                android.graphics.Insets sys=insets.getInsets(
                    WindowInsets.Type.systemBars()|WindowInsets.Type.displayCutout());
                scroll.setPadding(dp(16)+sys.left,dp(18)+sys.top,
                                  dp(16)+sys.right,dp(24)+sys.bottom);
                return insets;
            });
            scroll.requestApplyInsets();
        }
        if(accel==null||magnet==null){
            status.setText("Magnetometer oder Beschleunigungssensor fehlt");
        }
    }
    @Override protected void onResume(){super.onResume();
        if(accel!=null)sensors.registerListener(this,accel,SensorManager.SENSOR_DELAY_UI);
        if(magnet!=null)sensors.registerListener(this,magnet,SensorManager.SENSOR_DELAY_UI);
    }
    @Override protected void onPause(){sensors.unregisterListener(this);super.onPause();}
    @Override public void onSensorChanged(SensorEvent e){
        if(e.sensor.getType()==Sensor.TYPE_ACCELEROMETER){smooth(gravity,e.values);hasG=true;}
        else if(e.sensor.getType()==Sensor.TYPE_MAGNETIC_FIELD){smooth(magField,e.values);hasM=true;}
        if(hasG&&hasM){
            float[] rotation=new float[9],orientation=new float[3];
            if(SensorManager.getRotationMatrix(rotation,null,gravity,magField)){
                SensorManager.getOrientation(rotation,orientation);
                float next=(float)((Math.toDegrees(orientation[0])+360)%360);
                if(Float.isNaN(heading))heading=next;
                else heading=(heading+((next-heading+540)%360-180)*.19f+360)%360;
                status.setText(String.format(Locale.GERMANY,"%03d°  ·  %s",
                    Math.round(heading)%360,cardinal(heading)));
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
