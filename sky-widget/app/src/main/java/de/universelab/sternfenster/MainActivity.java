package de.universelab.sternfenster;

import android.Manifest;
import android.app.Activity;
import android.appwidget.AppWidgetManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Typeface;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.text.DateFormat;
import java.util.Date;
import java.util.Locale;

/** Settings and optional foreground-only location acquisition. */
public class MainActivity extends Activity {
    private static final int LOCATION_REQUEST=81;
    private final Handler handler=new Handler(Looper.getMainLooper());
    private TextView status;
    private LocationManager locationManager;
    private LocationListener locationListener;
    private boolean locating;
    private final Runnable timeout=()->{
        stopLocation();status.setText("Keine neue Position erhalten.\n"+locationText());
    };
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);
        LinearLayout panel=new LinearLayout(this);panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(Ui.dp(this,20),Ui.dp(this,20),Ui.dp(this,20),Ui.dp(this,24));
        scroll.addView(panel);
        TextView title=Ui.text(this,"STERNFENSTER",27,0xffb9dcf4);
        title.setTypeface(Typeface.DEFAULT,Typeface.BOLD);panel.addView(title);
        TextView version=Ui.text(this,"0.3.1 · Sternfenster folgt deinem Handy",14,Ui.MUTED);
        version.setPadding(0,Ui.dp(this,8),0,Ui.dp(this,18));panel.addView(version);
        Ui.addButton(this,panel,"Live-Sternkarte öffnen",()->startActivity(new Intent(this,SkyActivity.class)));
        Ui.addButton(this,panel,"Schwebendes Live-Fenster starten",()->startActivity(new Intent(this,SkyActivity.class).putExtra("open_pip",true)));
        panel.addView(Ui.text(this,"„Handy folgen“ übernimmt die Richtung der rückseitigen Kamera: Drehe, neige oder kippe das Handy, und die Sternkarte bewegt sich mit. Beim ersten Start ist dieser Modus eingeschaltet. Die Karte wird fortlaufend im Displaytakt gezeichnet und läuft im schwebenden Fenster über dem Startbildschirm weiter.",15,Ui.MUTED));
        panel.addView(Ui.text(this,"Richte die Rückseite des Handys zum Himmel. „Handy folgen“ schaltet die Sensorsteuerung um. Wischen, N/O/S/W, Zurücksetzen und Rundblick wechseln zur manuellen Ansicht; Zoomen lässt die Sensorsteuerung eingeschaltet. Bei „Kompass ungenau“ das Handy langsam in verschiedenen Richtungen bewegen und Abstand von Magneten halten. Für die Himmelsrichtung wird die Nordkorrektur aus dem unten angezeigten Standort geschätzt.",13,Ui.MUTED));
        Ui.heading(this,panel,"Standort");
        status=Ui.text(this,locationText(),15,Ui.TEXT);panel.addView(status);
        Ui.addButton(this,panel,"Standort ermitteln",this::requestLocation);
        panel.addView(Ui.text(this,"Die Position wird gespeichert und nur auf Knopfdruck neu ermittelt. Sie bleibt auf deinem Gerät.",13,Ui.MUTED));
        Ui.heading(this,panel,"Startbildschirm · Vorschau-Widget");
        Ui.addButton(this,panel,"Widget hinzufügen",this::pinWidget);
        Ui.addButton(this,panel,"Alle Widgets jetzt aktualisieren",()->{
            SkyWidgetProvider.updateAll(this);status.setText("Widgets aktualisiert.\n"+locationText());
        });
        panel.addView(Ui.text(this,"Alternativ: Startbildschirm lange drücken → Widgets → Sternfenster. Eine Größe von 4 × 3 Feldern bietet Platz für Karte und Beschriftung.\n\nEin Tipp auf die Karte öffnet unsere eigene Vollansicht. „Neu“ aktualisiert das Widget; „Richtung“ wechselt den Himmelsausschnitt.",14,Ui.MUTED));
        Ui.heading(this,panel,"Zusätzliche App");
        Ui.addButton(this,panel,"Universe Star Finder öffnen",this::openStarFinder);
        panel.addView(Ui.text(this,"Diese optionale Schaltfläche startet die andere App. Bei deren Meldung „engine_view_recreated“ die App über ihre App-Info beenden und direkt neu starten.",13,Ui.MUTED));
        Ui.heading(this,panel,"Darstellung und Aktualisierung");
        panel.addView(Ui.text(this,"Vollansicht und schwebendes Live-Fenster zeichnen kontinuierlich im Displaytakt mit einem Ziel von mindestens 60 FPS. Die erreichte Render-Rate wird gemessen; Android entscheidet über die verfügbare Bildrate. „Rundblick“ schwenkt die Blickrichtung gleichmäßig. „Zeit“ wechselt zwischen echter Uhrzeit (1×) und deutlich gekennzeichnetem Zeitraffer (60× / 600×). „Zurücksetzen“ stellt echte Uhrzeit und den Blick nach Süden wieder her. Das Vorschau-Widget bleibt ein gelegentlich aktualisiertes Bild; für fortlaufende Bewegung das schwebende Live-Fenster starten.\n\nDie Karte zeigt Sternpositionen auch am Tag. Sie berücksichtigt weder Tageslicht, Wetter noch Gebäude. Katalogkoordinaten: J2000, ohne Präzession, Eigenbewegung und Refraktion. Keine Teleskop-Navigation. Sonne, Mond und Planeten sind noch nicht enthalten.",13,Ui.MUTED));
        Ui.install(this,scroll);
    }
    @Override protected void onResume() {
        super.onResume();
        if(status!=null&&!locating)status.setText(locationText());
        SkyWidgetProvider.updateAll(this);
    }
    private String locationText() {
        SharedPreferences p=getSharedPreferences(SkyWidgetProvider.PREFS,MODE_PRIVATE);
        if(!p.getBoolean("has_gps",false))return "Dresden · Standardstandort\nNoch keine eigene Position gespeichert.";
        double lat=p.getFloat("lat",51.0504f),lon=p.getFloat("lon",13.7373f);
        String label=String.format(Locale.GERMANY,"Gespeicherter Standort: %.4f° %s, %.4f° %s",
                Math.abs(lat),lat>=0?"N":"S",Math.abs(lon),lon>=0?"O":"W");
        long time=p.getLong("location_time",0);
        if(time>0)label+="\nErmittelt: "+DateFormat.getDateTimeInstance(DateFormat.SHORT,DateFormat.SHORT,Locale.GERMANY).format(new Date(time));
        return label;
    }
    private void pinWidget() {
        AppWidgetManager manager=AppWidgetManager.getInstance(this);
        if(manager.isRequestPinAppWidgetSupported()) {
            boolean sent=manager.requestPinAppWidget(new ComponentName(this,SkyWidgetProvider.class),null,null);
            if(!sent)status.setText("Bitte über den Startbildschirm hinzufügen: lange drücken → Widgets → Sternfenster.");
        } else status.setText("Über den Startbildschirm hinzufügen: lange drücken → Widgets → Sternfenster.");
    }
    private void openStarFinder() {
        Intent launch=getPackageManager().getLaunchIntentForPackage("com.youvendo.international_space_registry");
        if(launch==null){status.setText("Universe Star Finder ist nicht verfügbar. Unsere Live-Sternkarte kannst du oben öffnen.");return;}
        try{startActivity(launch);}
        catch(RuntimeException e){status.setText("Die andere App konnte nicht geöffnet werden. Unsere Sternkarte bleibt verfügbar.");}
    }
    private boolean hasLocationPermission() {
        return checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED
                ||checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION)==PackageManager.PERMISSION_GRANTED;
    }
    private void requestLocation() {
        if(!hasLocationPermission())requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION},LOCATION_REQUEST);
        else locate();
    }
    @Override public void onRequestPermissionsResult(int request,String[] permissions,int[] results) {
        super.onRequestPermissionsResult(request,permissions,results);
        if(request!=LOCATION_REQUEST)return;
        if(hasLocationPermission())locate();
        else status.setText("Standortfreigabe nicht erteilt.\n"+locationText());
    }
    @SuppressWarnings("MissingPermission") private void locate() {
        stopLocation();
        locationManager=(LocationManager)getSystemService(Context.LOCATION_SERVICE);
        if(locationManager==null){status.setText("Standortdienst nicht verfügbar.\n"+locationText());return;}
        Location cached=null;
        for(String provider:new String[]{LocationManager.NETWORK_PROVIDER,LocationManager.GPS_PROVIDER}) {
            try{
                Location l=locationManager.getLastKnownLocation(provider);
                if(l!=null&&(cached==null||l.getTime()>cached.getTime()))cached=l;
            }catch(RuntimeException ignored){}
        }
        if(cached!=null&&cached.getTime()>=getSharedPreferences(SkyWidgetProvider.PREFS,MODE_PRIVATE).getLong("location_time",0))saveLocation(cached);
        locationListener=new LocationListener(){
            @Override public void onLocationChanged(Location l){saveLocation(l);stopLocation();status.setText(locationText());}
            @Override public void onProviderEnabled(String provider){}
            @Override public void onProviderDisabled(String provider){}
            @Override public void onStatusChanged(String provider,int value,Bundle extras){}
        };
        boolean requested=false;
        for(String provider:new String[]{LocationManager.NETWORK_PROVIDER,LocationManager.GPS_PROVIDER}) {
            try{
                if(locationManager.isProviderEnabled(provider)){
                    locationManager.requestLocationUpdates(provider,1000,0,locationListener);requested=true;
                }
            }catch(RuntimeException ignored){}
        }
        locating=requested;
        if(requested){status.setText("Standort wird ermittelt …\n"+locationText());handler.postDelayed(timeout,20000);}
        else{stopLocation();status.setText("Keine nutzbare Standortquelle. Prüfe Standortdienste und Standortfreigabe.\n"+locationText());}
    }
    private void saveLocation(Location l) {
        if(!Double.isFinite(l.getLatitude())||!Double.isFinite(l.getLongitude()))return;
        getSharedPreferences(SkyWidgetProvider.PREFS,MODE_PRIVATE).edit()
                .putFloat("lat",(float)l.getLatitude()).putFloat("lon",(float)l.getLongitude())
                .putBoolean("has_gps",true).putLong("location_time",l.getTime()).apply();
        SkyWidgetProvider.updateAll(this);
    }
    private void stopLocation() {
        handler.removeCallbacks(timeout);
        if(locationManager!=null&&locationListener!=null){
            try{locationManager.removeUpdates(locationListener);}catch(RuntimeException ignored){}
        }
        locationListener=null;locating=false;
    }
    @Override protected void onStop(){stopLocation();super.onStop();}
}
