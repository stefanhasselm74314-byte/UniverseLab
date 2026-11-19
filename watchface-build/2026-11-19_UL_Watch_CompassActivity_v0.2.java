package de.universelab.compass;

import android.app.Activity;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;

import java.util.Locale;

/**
 * Separate Wear OS activity. WFF itself cannot host arbitrary sensor code.
 * Uses magnetic north (not true north), without location permission.
 * The compass has no fake reading: a missing sensor yields an explicit error.
 */
public final class CompassActivity extends Activity implements SensorEventListener {
    private SensorManager sensors;
    private Sensor rotationVector;
    private Sensor accelerometer;
    private Sensor magnetometer;
    private CompassView gauge;
    private final float[] gravity = new float[3];
    private final float[] magnetic = new float[3];
    private final float[] rotation = new float[9];
    private final float[] orientation = new float[3];
    private boolean hasGravity = false;
    private boolean hasMagnetic = false;
    private boolean hasHeading = false;
    private float smoothedHeading = 0.0f;
    private int accuracy = SensorManager.SENSOR_STATUS_UNRELIABLE;

    @Override
    public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN);
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        sensors = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        rotationVector = sensors.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR);
        accelerometer = sensors.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        magnetometer = sensors.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);
        gauge = new CompassView(this);
        setContentView(gauge);
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (rotationVector != null) {
            sensors.registerListener(this, rotationVector, SensorManager.SENSOR_DELAY_UI);
        } else if (accelerometer != null && magnetometer != null) {
            sensors.registerListener(this, accelerometer, SensorManager.SENSOR_DELAY_UI);
            sensors.registerListener(this, magnetometer, SensorManager.SENSOR_DELAY_UI);
        }
    }

    @Override
    protected void onPause() {
        sensors.unregisterListener(this);
        super.onPause();
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int value) {
        accuracy = value;
        gauge.invalidate();
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        final int type = event.sensor.getType();
        if (type == Sensor.TYPE_ROTATION_VECTOR) {
            SensorManager.getRotationMatrixFromVector(rotation, event.values);
        } else if (rotationVector == null) {
            if (type == Sensor.TYPE_ACCELEROMETER) {
                System.arraycopy(event.values, 0, gravity, 0, 3);
                hasGravity = true;
            } else if (type == Sensor.TYPE_MAGNETIC_FIELD) {
                System.arraycopy(event.values, 0, magnetic, 0, 3);
                hasMagnetic = true;
            }
            if (!hasGravity || !hasMagnetic ||
                !SensorManager.getRotationMatrix(rotation, null, gravity, magnetic)) {
                return;
            }
        } else {
            return;
        }

        SensorManager.getOrientation(rotation, orientation);
        float next = (float) Math.toDegrees(orientation[0]);
        next = ((next % 360.0f) + 360.0f) % 360.0f;
        if (!hasHeading) {
            smoothedHeading = next;
            hasHeading = true;
        } else {
            // Shortest circular difference, safe at the 359° -> 0° boundary.
            float delta = (next - smoothedHeading + 540.0f) % 360.0f - 180.0f;
            smoothedHeading = (smoothedHeading + 0.22f * delta + 360.0f) % 360.0f;
        }
        gauge.invalidate();
    }

    private final class CompassView extends View {
        private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
        CompassView(Context ctx) { super(ctx); setLayerType(View.LAYER_TYPE_HARDWARE, null); }

        private void line(Canvas c, float x1,float y1,float x2,float y2,
                          int color,float stroke) {
            paint.setStyle(Paint.Style.STROKE);
            paint.setColor(color);
            paint.setStrokeWidth(stroke);
            c.drawLine(x1,y1,x2,y2,paint);
            paint.setStyle(Paint.Style.FILL);
        }

        private void label(Canvas c,String text,float x,float y,float size,int color) {
            paint.setStyle(Paint.Style.FILL);
            paint.setColor(color);
            paint.setTypeface(android.graphics.Typeface.create("sans-serif-medium", 0));
            paint.setTextAlign(Paint.Align.CENTER);
            paint.setTextSize(size);
            c.drawText(text,x,y+size*0.34f,paint);
        }

        private float x(float r,float deg) { return (float)(r*Math.sin(Math.toRadians(deg))); }
        private float y(float r,float deg) { return (float)(-r*Math.cos(Math.toRadians(deg))); }

        @Override
        protected void onDraw(Canvas canvas) {
            super.onDraw(canvas);
            canvas.drawColor(Color.rgb(3, 9, 18));
            float s = Math.min(getWidth(),getHeight()) / 450.0f;
            canvas.save();
            canvas.translate(getWidth()/2.0f,getHeight()/2.0f);
            canvas.scale(s,s);
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth(3);
            paint.setColor(Color.rgb(79, 112, 137));
            canvas.drawCircle(0,0,214,paint);
            paint.setStrokeWidth(1);
            paint.setColor(Color.rgb(25, 57, 79));
            canvas.drawCircle(0,0,170,paint);
            paint.setStyle(Paint.Style.FILL);

            // A fixed top index; the degree rose turns opposite to heading.
            if (hasHeading) {
                canvas.save();
                canvas.rotate(-smoothedHeading);
                for (int degree=0; degree<360; degree+=5) {
                    boolean major=degree%30==0;
                    float r0=major?181:194;
                    line(canvas,x(r0,degree),y(r0,degree),
                        x(206,degree),y(206,degree),
                        major?Color.rgb(205,232,248):Color.rgb(93,130,155),
                        major?3:1);
                }
                final String[] names={"N","NE","E","SE","S","SW","W","NW"};
                for (int k=0;k<8;k++) {
                    int deg=k*45;
                    label(canvas,names[k],x(158,deg),y(158,deg),
                        k%2==0?24:14,k==0?Color.rgb(255,83,96):Color.rgb(192,231,252));
                }
                canvas.restore();
            }
            Path north = new Path();
            north.moveTo(0,-215); north.lineTo(-10,-190); north.lineTo(10,-190);
            north.close();
            paint.setColor(Color.rgb(255,83,96));
            canvas.drawPath(north,paint);
            line(canvas,0,-187,0,-171,Color.rgb(255,83,96),3);

            label(canvas,"UNIVERSELAB · 6D",0,-95,16,Color.rgb(124,204,248));
            if (!hasHeading) {
                label(canvas,"— — —",0,-12,42,Color.WHITE);
                label(canvas,"KEIN KOMPASS-SIGNAL",0,39,12,Color.rgb(255,139,144));
            } else {
                int rounded=Math.round(smoothedHeading)%360;
                label(canvas,String.format(Locale.ROOT,"%03d°",rounded),0,-4,
                      60,Color.rgb(229,245,255));
                label(canvas,direction(rounded),0,54,20,Color.rgb(122,209,255));
            }
            label(canvas,"MAGNETISCH",0,103,13,Color.rgb(112,157,186));
            if (accuracy == SensorManager.SENSOR_STATUS_UNRELIABLE && hasHeading) {
                label(canvas,"KALIBRIERUNG PRÜFEN",0,137,10,Color.rgb(255,127,135));
            }
            canvas.restore();
        }
    }

    private static String direction(float degrees) {
        String[] d={"N","NO","O","SO","S","SW","W","NW"};
        return d[Math.round(degrees/45f)%8];
    }
}
