package de.universelab.sternfenster;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.SystemClock;
import android.util.Log;

/** Visible-window sensor subscription. All callbacks and rendering use the UI thread. */
final class DeviceOrientationTracker implements SensorEventListener {
    private static final int SAMPLE_MICROS=10_000; // 100 Hz, below Android's 200-Hz permission boundary.
    private static final long STALE_NANOS=2_000_000_000L;
    private final SensorManager manager;
    private final Sensor rotation,acceleration,magnetic;
    private final float[] gravity=new float[3],field=new float[3],matrix=new float[9];
    private final float[] sensorQuaternion=new float[4],drawVector=new float[4],drawMatrix=new float[9];
    private final double[] target=new double[4],smooth=new double[4];
    private boolean listening,usingRotation,hasGravity,hasField,hasTarget,hasSmooth;
    private long lastSampleNanos,lastFrameNanos,lastGravityNanos,lastFieldNanos;
    private int accuracy=SensorManager.SENSOR_STATUS_UNRELIABLE;
    private String source="keine Sensoren";

    DeviceOrientationTracker(Context context){
        manager=(SensorManager)context.getSystemService(Context.SENSOR_SERVICE);
        Sensor candidate=manager==null?null:manager.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR);
        if(candidate==null&&manager!=null)candidate=manager.getDefaultSensor(Sensor.TYPE_GEOMAGNETIC_ROTATION_VECTOR);
        rotation=candidate;
        acceleration=manager==null?null:manager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        magnetic=manager==null?null:manager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);
    }
    boolean isAvailable(){return rotation!=null||(acceleration!=null&&magnetic!=null);}
    boolean isListening(){return listening;}
    boolean hasFreshSample(){
        long now=SystemClock.elapsedRealtimeNanos();
        return listening&&hasTarget&&now-lastSampleNanos<STALE_NANOS
                &&(usingRotation||(now-lastGravityNanos<STALE_NANOS&&now-lastFieldNanos<STALE_NANOS));
    }
    int accuracy(){return accuracy;}
    String source(){return source;}

    boolean start(){
        if(listening)return true;
        if(manager==null||!isAvailable())return false;
        hasGravity=hasField=hasTarget=hasSmooth=false;
        lastFrameNanos=lastSampleNanos=lastGravityNanos=lastFieldNanos=0;accuracy=SensorManager.SENSOR_STATUS_UNRELIABLE;
        try{
            if(rotation!=null&&manager.registerListener(this,rotation,SAMPLE_MICROS,0)){
                listening=usingRotation=true;
                source=rotation.getType()==Sensor.TYPE_ROTATION_VECTOR?"rotation_vector":"geomagnetic_rotation_vector";
            }else if(acceleration!=null&&magnetic!=null){
                boolean a=manager.registerListener(this,acceleration,SAMPLE_MICROS,0);
                boolean m=manager.registerListener(this,magnetic,SAMPLE_MICROS,0);
                listening=a&&m;usingRotation=false;source="accelerometer_magnetic";
                if(!listening)manager.unregisterListener(this);
            }
        }catch(RuntimeException e){
            manager.unregisterListener(this);listening=false;Log.w("SternfensterSensor","Sensor registration failed",e);
        }
        if(listening)Log.i("SternfensterSensor","listening_started mode="+source);
        return listening;
    }
    void stop(){
        if(manager!=null&&listening)manager.unregisterListener(this);
        if(listening)Log.i("SternfensterSensor","listening_stopped");
        listening=false;hasTarget=hasSmooth=false;lastFrameNanos=0;
    }
    @Override public void onSensorChanged(SensorEvent event){
        if(!listening||event.values.length<3)return;
        if(usingRotation){
            if(event.sensor.getType()!=rotation.getType())return;
            SensorManager.getQuaternionFromVector(sensorQuaternion,event.values);
            double norm=0;
            for(int i=0;i<4;i++){
                if(!Float.isFinite(sensorQuaternion[i]))return;
                norm+=(double)sensorQuaternion[i]*sensorQuaternion[i];
            }
            if(norm<1e-12)return;
            double inverse=1/Math.sqrt(norm);
            for(int i=0;i<4;i++)target[i]=sensorQuaternion[i]*inverse;
            accuracy=event.accuracy;
        }else{
            int type=event.sensor.getType();
            long now=SystemClock.elapsedRealtimeNanos();
            if(type==Sensor.TYPE_ACCELEROMETER){
                if(!lowPass(event.values,gravity,hasGravity))return;hasGravity=true;lastGravityNanos=now;
            }else if(type==Sensor.TYPE_MAGNETIC_FIELD){
                if(!lowPass(event.values,field,hasField))return;hasField=true;lastFieldNanos=now;accuracy=event.accuracy;
            }else return;
            if(!hasGravity||!hasField||now-lastGravityNanos>=STALE_NANOS||now-lastFieldNanos>=STALE_NANOS
                    ||!SensorManager.getRotationMatrix(matrix,null,gravity,field)
                    ||!DeviceOrientationMath.quaternionFromMatrix(matrix,target))return;
        }
        hasTarget=true;lastSampleNanos=SystemClock.elapsedRealtimeNanos();
    }
    private static boolean lowPass(float[] input,float[] output,boolean initialized){
        for(int i=0;i<3;i++)if(!Float.isFinite(input[i]))return false;
        for(int i=0;i<3;i++)output[i]=initialized?output[i]+.2f*(input[i]-output[i]):input[i];
        return true;
    }
    @Override public void onAccuracyChanged(Sensor sensor,int value){
        if((usingRotation&&sensor==rotation)||sensor==magnetic)accuracy=value;
    }

    /** Smooth quaternions in the sensor frame; apply display rotation only afterwards. */
    boolean cameraBasis(long frameTimeNanos,int displayRotation,double declination,double[] output){
        if(!listening||!hasTarget)return false;
        double seconds=lastFrameNanos==0?0:(frameTimeNanos-lastFrameNanos)/1_000_000_000.0;
        if(!hasSmooth||seconds<=0||seconds>1){
            System.arraycopy(target,0,smooth,0,4);hasSmooth=true;
        }else{
            double alpha=1-Math.exp(-seconds/.025);
            if(!DeviceOrientationMath.blendQuaternion(smooth,target,alpha,smooth))return false;
        }
        lastFrameNanos=frameTimeNanos;
        // Android rotation vectors are x/y/z/w, unlike getQuaternionFromVector's w/x/y/z.
        drawVector[0]=(float)smooth[1];drawVector[1]=(float)smooth[2];
        drawVector[2]=(float)smooth[3];drawVector[3]=(float)smooth[0];
        SensorManager.getRotationMatrixFromVector(drawMatrix,drawVector);
        return DeviceOrientationMath.cameraBasis(drawMatrix,displayRotation,declination,output);
    }
}
