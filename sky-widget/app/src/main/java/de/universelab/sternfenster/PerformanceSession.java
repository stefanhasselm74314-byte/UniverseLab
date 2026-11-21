package de.universelab.sternfenster;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.widget.Toast;
import java.text.DateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.function.BooleanSupplier;
import org.json.JSONException;
import org.json.JSONObject;

/** User-started measurement of draw callbacks, deliberately not displayed frames. */
final class PerformanceSession {
    static final String EXTRA_MEASURE="measure_frame_pacing";
    static final String RESULT_TEXT="pacing_last_text",RESULT_JSON="pacing_last_json",LAST_STATUS="pacing_last_status";
    static final int FULLSCREEN=1,PIP=2,OVERLAY=4;
    private static final long WARMUP_MS=2000,DURATION_MS=20000;
    private static PerformanceSession current;
    private final Context context;
    private final SharedPreferences preferences;
    private final BooleanSupplier visible;
    private final Runnable changed;
    private final String label;
    private final Handler handler=new Handler(Looper.getMainLooper());
    private final FramePacingStats stats=new FramePacingStats();
    private final Runnable beginTask=this::begin,finishTask=this::finish;
    private boolean requested,collecting;
    private long requestTime,measurementTime;
    private int minWidth,maxWidth,minHeight,maxHeight,modes;
    private boolean hardwareSeen,softwareSeen,followingSeen,manualSeen;
    private String resultHint="";

    PerformanceSession(Context context,String label,BooleanSupplier visible,Runnable changed){
        this.context=context.getApplicationContext();this.label=label;this.visible=visible;this.changed=changed;
        preferences=this.context.getSharedPreferences(SkyWidgetProvider.PREFS,Context.MODE_PRIVATE);
    }
    void request(){
        if(current!=null)current.cancel("Neue Messung gestartet");
        current=this;requested=true;collecting=false;resultHint="";
        requestTime=System.nanoTime();measurementTime=0;
        minWidth=minHeight=Integer.MAX_VALUE;maxWidth=maxHeight=modes=0;
        hardwareSeen=softwareSeen=followingSeen=manualSeen=false;
        preferences.edit().putString(LAST_STATUS,"Messung gestartet; noch kein neues Ergebnis.").apply();
        handler.postDelayed(beginTask,WARMUP_MS);changed.run();
        Log.i("SternfensterMeasure","warmup mode="+label);
    }
    private void begin(){
        if(!requested)return;
        if(!visible.getAsBoolean()){cancel("Ansicht nicht sichtbar");return;}
        measurementTime=System.nanoTime();stats.start(measurementTime);collecting=true;
        handler.postDelayed(finishTask,DURATION_MS);changed.run();
        Log.i("SternfensterMeasure","started mode="+label+" duration_ms="+DURATION_MS);
    }
    boolean isCollecting(){return collecting;}
    void recordDraw(long start,long end,double displayHz,int width,int height,boolean hardware,boolean following,int mode){
        if(!collecting)return;
        stats.record(start,end,displayHz);
        minWidth=Math.min(minWidth,width);maxWidth=Math.max(maxWidth,width);
        minHeight=Math.min(minHeight,height);maxHeight=Math.max(maxHeight,height);
        modes|=mode;hardwareSeen|=hardware;softwareSeen|=!hardware;
        followingSeen|=following;manualSeen|=!following;
    }
    String progressText(){
        if(!requested)return resultHint;
        long now=System.nanoTime();
        if(!collecting)return "Messung startet in "+Math.max(1,(WARMUP_MS-(now-requestTime)/1_000_000L+999)/1000)+" s";
        long remaining=Math.max(0,DURATION_MS-(now-measurementTime)/1_000_000L);
        return "Bildrate messen · noch "+((remaining+999)/1000)+" s";
    }
    static String activeStatus(){return current==null?"":current.label+" · "+current.progressText();}
    private void finish(){
        if(!requested||!collecting)return;
        if(!visible.getAsBoolean()){cancel("Ansicht nicht sichtbar");return;}
        FramePacingStats.Summary s=stats.finish(System.nanoTime());
        collecting=requested=false;if(current==this)current=null;
        long completedAt=System.currentTimeMillis();
        try{
            JSONObject data=new JSONObject();
            data.put("version","0.4.1");data.put("measurement","onDraw callbacks; not compositor-presented frames");
            data.put("mode",label);data.put("window_modes",modes);data.put("completed_at_ms",completedAt);
            data.put("warmup_ms",WARMUP_MS);data.put("requested_duration_ms",DURATION_MS);
            data.put("frames",s.frames);data.put("duration_ns",s.durationNs);putFinite(data,"render_fps",s.renderFps);
            data.put("interval_count",s.intervalCount);data.put("interval_min_ns",s.intervalMinNs);
            putFinite(data,"interval_mean_ns",s.intervalMeanNs);putFinite(data,"interval_p95_ns",s.intervalP95Ns);
            data.put("interval_max_ns",s.intervalMaxNs);putFinite(data,"interval_fps",s.intervalFps);
            putFinite(data,"draw_p95_ns",s.drawP95Ns);data.put("intervals_above_20_ms",s.intervalsAbove20Ms);
            putFinite(data,"display_hz_min",s.displayHzMin);putFinite(data,"display_hz_max",s.displayHzMax);
            data.put("samples_overflowed",s.samplesOverflowed);data.put("invalid_events",s.invalidEvents);
            data.put("unknown_hz_samples",s.unknownHzSamples);data.put("complete",s.complete);data.put("cancelled",s.cancelled);
            data.put("width_min_px",minWidth==Integer.MAX_VALUE?0:minWidth);data.put("width_max_px",maxWidth);
            data.put("height_min_px",minHeight==Integer.MAX_VALUE?0:minHeight);data.put("height_max_px",maxHeight);
            data.put("hardware_canvas_seen",hardwareSeen);data.put("software_canvas_seen",softwareSeen);
            data.put("phone_follow_seen",followingSeen);data.put("manual_view_seen",manualSeen);
            data.put("device",Build.MANUFACTURER+" "+Build.MODEL);data.put("android_sdk",Build.VERSION.SDK_INT);
            data.put("minimum_60_presented_fps","NOT_ESTABLISHED_BY_THIS_MEASUREMENT");
            String report=format(s,completedAt);
            preferences.edit().putString(RESULT_TEXT,report).putString(RESULT_JSON,data.toString())
                    .putString(LAST_STATUS,"Letzte Messung gespeichert.").apply();
            resultHint=Double.isFinite(s.renderFps)?String.format(Locale.GERMANY,"Messung: Ø %.1f Render-FPS",s.renderFps):"Messung ohne verwertbare Bilder";
            Log.i("SternfensterMeasure","completed "+data);
            Toast.makeText(context,"Messung gespeichert · Ergebnis unter „Bildrate prüfen“",Toast.LENGTH_LONG).show();
        }catch(JSONException invalid){
            resultHint="Messung konnte nicht gespeichert werden";
            preferences.edit().putString(LAST_STATUS,resultHint).apply();
            Log.e("SternfensterMeasure","report_failed",invalid);
        }
        changed.run();
    }
    private static void putFinite(JSONObject object,String key,double value)throws JSONException{
        object.put(key,Double.isFinite(value)?value:JSONObject.NULL);
    }
    void cancel(String reason){
        if(!requested)return;
        handler.removeCallbacks(beginTask);handler.removeCallbacks(finishTask);
        stats.cancel();requested=collecting=false;if(current==this)current=null;
        resultHint="Messung abgebrochen";
        preferences.edit().putString(LAST_STATUS,"Messung abgebrochen: "+reason+". Das vorherige Ergebnis bleibt erhalten.").apply();
        Log.i("SternfensterMeasure","cancelled mode="+label+" reason="+reason);
        changed.run();
    }
    private static String number(double value,int digits){
        return Double.isFinite(value)?String.format(Locale.GERMANY,"%."+digits+"f",value):"nicht erfasst";
    }
    private String format(FramePacingStats.Summary s,long completedAt){
        String timestamp=DateFormat.getDateTimeInstance(DateFormat.SHORT,DateFormat.MEDIUM,Locale.GERMANY).format(new Date(completedAt));
        String mode=modes==0?"Fenstermodus nicht erfasst":modes==OVERLAY?"Freies Live-Fenster":modes==PIP?"Bild-im-Bild":modes==FULLSCREEN?"Live-Sternkarte":"Mehrere Fenstermodi";
        String quality=s.complete?(s.frames==0?"Messung abgeschlossen; keine Zeichenaufrufe erfasst":"Messung abgeschlossen")
                :"Messung unvollständig: "+s.invalidEvents+" ungültige Ereignisse; Speichergrenze: "+s.samplesOverflowed;
        double overPercent=s.intervalCount==0?Double.NaN:100.0*s.intervalsAbove20Ms/s.intervalCount;
        String hardware=!hardwareSeen&&!softwareSeen?"nicht erfasst":hardwareSeen?(softwareSeen?"gemischt":"ja"):"nein";
        String following=!followingSeen&&!manualSeen?"nicht erfasst":followingSeen?(manualSeen?"teilweise":"an"):"aus";
        String area=maxWidth==0?"nicht erfasst":minWidth+"–"+maxWidth+" × "+minHeight+"–"+maxHeight+" px";
        return "STERNFENSTER 0.4.1 · BILDRATENMESSUNG\n"+timestamp+"\n"+mode+"\n"
                +Build.MANUFACTURER+" "+Build.MODEL+" · Android "+Build.VERSION.RELEASE+"\n\n"
                +"Dauer: "+number(s.durationNs/1_000_000_000.0,2)+" s nach 2 s Aufwärmen\n"
                +"Zeichenaufrufe: "+s.frames+"\nØ Render-FPS: "+number(s.renderFps,2)+"\n"
                +"Display: "+number(s.displayHzMin,1)+"–"+number(s.displayHzMax,1)+" Hz\n"
                +"Zeichenaufrufe ohne Display-Hz: "+s.unknownHzSamples+"\n\n"
                +"Bildabstände: "+s.intervalCount+"\n95 % höchstens: "+number(s.intervalP95Ns/1_000_000.0,2)+" ms\n"
                +"Größter Abstand: "+(s.intervalCount==0?"nicht erfasst":number(s.intervalMaxNs/1_000_000.0,2)+" ms")+"\n"
                +"Abstände über 20 ms: "+s.intervalsAbove20Ms+" ("+number(overPercent,1)+" %)\n"
                +"Dauer des Zeichenaufrufs, 95 % höchstens: "+number(s.drawP95Ns/1_000_000.0,2)+" ms\n\n"
                +"Kartenfläche: "+area+"\nHardware-Canvas: "+hardware+"\nHandy folgen: "+following+"\n"+quality+"\n\n"
                +"Gemessen werden die Zeichenaufrufe und ihre Zeitabstände. Die Dauer des Zeichenaufrufs enthält keine anschließende GPU- oder Bildschirmausgabe; Wartezeiten innerhalb des Aufrufs können enthalten sein. "
                +"Bei 60 FPS beträgt der regelmäßige Bildabstand 16,67 ms, bei 120 FPS 8,33 ms. Die Grenze von 20 ms ist ein Diagnosewert. "
                +"Ein Mittelwert ab 60 beweist keine durchgehenden 60 FPS. Tatsächlich am Bildschirm präsentierte Bilder werden hier nicht gezählt.";
    }
}
