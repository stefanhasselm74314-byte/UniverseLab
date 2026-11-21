package de.universelab.sternfenster;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.view.View;
import android.view.Gravity;

/** Einfaches Konfigurationsfenster, keine Werbung, kein Netzwerk. */
public class MainActivity extends Activity {
    private TextView status;
    private LocationManager lm;
    private LocationListener locationListener;
    private static final int REQ_LOCATION=81;
    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        getWindow().setStatusBarColor(0xff050d1b);
        getWindow().setNavigationBarColor(0xff050d1b);
        ScrollView outer=new ScrollView(this); outer.setBackgroundColor(0xff061225);
        LinearLayout panel=new LinearLayout(this);panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(22),dp(28),dp(22),dp(28));outer.addView(panel);
        text(panel,"STERNFENSTER",26,0xffb9dcff,true);
        text(panel,"Astronomische Sternkarte für deinen Android-Startbildschirm",16,0xffe8f4ff,false);
        text(panel,"Der angezeigte Himmelsausschnitt wird aus Sternkatalog, Uhrzeit und Standort berechnet – nicht aus dem Bild der Star-Finder-App gespiegelt.",14,0xffaebed4,false);
        status=text(panel,"",15,0xffdce7fa,false); updateStatus();
        button(panel,"1 · Standort ermitteln",()->requestLocation());
        button(panel,"2 · Sternkarte jetzt aktualisieren",()->{
            SkyWidgetProvider.updateAll(this);
            status.setText("Sternkarte aktualisiert.\n"+currentLocationText());
        });
        button(panel,"3 · Universe Star Finder öffnen",()->{
            Intent i=new Intent(Intent.ACTION_MAIN);
            i.setClassName("com.youvendo.international_space_registry","com.youvendo.star_finder.MainActivity");
            try{startActivity(i);}catch(Exception ex){status.setText("Universe Star Finder nicht gefunden.\n"+currentLocationText());}
        });
        text(panel,"WIDGET EINFÜGEN",19,0xff8ebdeb,true);
        text(panel,"Halte eine freie Stelle auf dem Startbildschirm gedrückt → Widgets → Sternfenster → hinzufügen.\n\nTippe auf die Sternkarte, um Universe Star Finder zu öffnen. Mit ↻ rechts die Blickrichtung wechseln; ⟳ links aktualisieren.",15,0xffd6e5f8,false);
        text(panel,"Aktualisierung: systemgesteuert ungefähr alle 30 Minuten (Verzögerungen im Energiesparmodus möglich). Positionen der Sterne sind echte Katalogdaten (J2000), ohne Refraktions- und Präzessionskorrektur.",13,0xff8b9fb8,false);
        setContentView(outer);
    }
    private int dp(float v){return Math.round(v*getResources().getDisplayMetrics().density);}
    private TextView text(LinearLayout p,String value,int sp,int color,boolean bold){
        TextView v=new TextView(this);v.setText(value);v.setTextSize(sp);v.setTextColor(color);
        v.setLineSpacing(dp(3),1);v.setPadding(0,dp(9),0,dp(14));
        if(bold)v.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        p.addView(v);return v;
    }
    private void button(LinearLayout p,String name,Runnable r){
        Button b=new Button(this);b.setText(name);
        b.setTextColor(Color.WHITE);b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(0xff24507b));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(56));lp.setMargins(0,0,0,dp(10));
        p.addView(b,lp);b.setOnClickListener(v->r.run());
    }
    private String currentLocationText(){
        android.content.SharedPreferences pr=getSharedPreferences(SkyWidgetProvider.PREFS,MODE_PRIVATE);
        return pr.getBoolean("has_gps",false)?
                String.format(java.util.Locale.GERMANY,"GPS: %.4f° N, %.4f° O",pr.getFloat("lat",0f),pr.getFloat("lon",0f)):
                "Standort: Dresden (Standardwert, noch keine GPS-Position)";
    }
    private void updateStatus(){status.setText(currentLocationText());}
    private void requestLocation(){
        if(checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)!=PackageManager.PERMISSION_GRANTED
            && checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION)!=PackageManager.PERMISSION_GRANTED){
            requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION,Manifest.permission.ACCESS_COARSE_LOCATION},REQ_LOCATION);
            return;
        }
        locateNow();
    }
    @Override public void onRequestPermissionsResult(int req,String[] p,int[] results){
        super.onRequestPermissionsResult(req,p,results);
        if(req==REQ_LOCATION){
            if(checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION)==PackageManager.PERMISSION_GRANTED
               ||checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED)locateNow();
            else status.setText("Standortfreigabe nicht erteilt. Es bleibt beim Standardstandort Dresden.");
        }
    }
    @SuppressWarnings("MissingPermission") private void locateNow(){
        lm=(LocationManager)getSystemService(Context.LOCATION_SERVICE);
        if(lm==null){status.setText("Standortdienst nicht verfügbar.");return;}
        Location best=null;
        for(String provider : lm.getProviders(true)){
            try{ Location l=lm.getLastKnownLocation(provider);
                if(l!=null&&(best==null||l.getTime()>best.getTime()))best=l;
            }catch(SecurityException ignored){}
        }
        if(best!=null) saveLocation(best);
        status.setText("GPS-/Netzwerkposition wird abgefragt …\n"+currentLocationText());
        locationListener=new LocationListener(){
            @Override public void onLocationChanged(Location l){
                saveLocation(l); status.setText(currentLocationText());
                try{lm.removeUpdates(this);}catch(Exception ignored){}
            }
            @Override public void onProviderEnabled(String p){}
            @Override public void onProviderDisabled(String p){}
        };
        try{
            boolean requested=false;
            if(lm.isProviderEnabled(LocationManager.NETWORK_PROVIDER)){
                lm.requestLocationUpdates(LocationManager.NETWORK_PROVIDER,0,0,locationListener);requested=true;}
            if(lm.isProviderEnabled(LocationManager.GPS_PROVIDER)){
                lm.requestLocationUpdates(LocationManager.GPS_PROVIDER,0,0,locationListener);requested=true;}
            if(!requested)status.setText("Standortdienste ausschalten? Bitte in den Android-Einstellungen aktivieren.");
        }catch(Exception e){status.setText("Standortabfrage nicht möglich: "+e.getMessage());}
    }
    private void saveLocation(Location l){
        getSharedPreferences(SkyWidgetProvider.PREFS,MODE_PRIVATE).edit()
            .putFloat("lat",(float)l.getLatitude()).putFloat("lon",(float)l.getLongitude())
            .putBoolean("has_gps",true).apply();
        SkyWidgetProvider.updateAll(this);
    }
    @Override protected void onStop(){super.onStop();
        if(lm!=null&&locationListener!=null)try{lm.removeUpdates(locationListener);}catch(Exception ignored){}
    }
}
