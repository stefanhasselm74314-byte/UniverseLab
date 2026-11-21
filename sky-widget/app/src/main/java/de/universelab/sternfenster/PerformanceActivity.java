package de.universelab.sternfenster;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

/** A local report the user can copy after measuring the actual phone. */
public final class PerformanceActivity extends Activity {
    private final Handler handler=new Handler(Looper.getMainLooper());
    private TextView result,status;
    private boolean resumed;
    private final Runnable refresh=new Runnable(){public void run(){
        showResult();if(resumed)handler.postDelayed(this,1000);
    }};
    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);
        LinearLayout panel=new LinearLayout(this);panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(Ui.dp(this,20),Ui.dp(this,20),Ui.dp(this,20),Ui.dp(this,24));scroll.addView(panel);
        Ui.heading(this,panel,"Bildrate auf diesem Handy");
        panel.addView(Ui.text(this,"Nach 2 Sekunden Aufwärmen wird die gewählte Ansicht 20 Sekunden gemessen. Halte das Testfenster sichtbar, bewege das Handy und benutze das Fenster wie gewohnt. Das freie Fenster läuft nach der Messung weiter. Kehre danach hierher zurück.",15,Ui.TEXT));
        Ui.addButton(this,panel,"Im freien Fenster messen (20 s)",()->OverlaySetupActivity.launch(this,
                new Intent(this,FloatingSkyService.class).setAction(FloatingSkyService.ACTION_SHOW).putExtra(PerformanceSession.EXTRA_MEASURE,true)));
        Ui.addButton(this,panel,"In Vollansicht messen (20 s)",()->startActivity(new Intent(this,SkyActivity.class)
                .putExtra(PerformanceSession.EXTRA_MEASURE,true)));
        status=Ui.text(this,"",14,Ui.MUTED);status.setContentDescription("Status der Bildratenmessung");panel.addView(status);
        Ui.heading(this,panel,"Letztes Ergebnis");
        result=Ui.text(this,"",14,Ui.TEXT);result.setContentDescription("Ergebnis der Bildratenmessung");result.setTextIsSelectable(true);panel.addView(result);
        Ui.addButton(this,panel,"Ergebnis kopieren",()->{
            String text=prefs().getString(PerformanceSession.RESULT_TEXT,"");
            if(text.isEmpty()){Toast.makeText(this,"Noch keine abgeschlossene Messung",Toast.LENGTH_SHORT).show();return;}
            getSystemService(ClipboardManager.class).setPrimaryClip(ClipData.newPlainText("Sternfenster-Bildratenmessung",text));
            Toast.makeText(this,"Ergebnis kopiert",Toast.LENGTH_SHORT).show();
        });
        panel.addView(Ui.text(this,"Der Bericht enthält Gerätemodell, Fenstergröße und Zeitmessungen. Er bleibt auf deinem Gerät und enthält keinen Standort. Bei Unterbrechung bleibt das vorherige Ergebnis erhalten.",13,Ui.MUTED));
        Ui.addButton(this,panel,"Zurück",this::finish);Ui.install(this,scroll);showResult();
    }
    private SharedPreferences prefs(){return getSharedPreferences(SkyWidgetProvider.PREFS,MODE_PRIVATE);}
    private void showResult(){
        String report=prefs().getString(PerformanceSession.RESULT_TEXT,"Noch keine abgeschlossene Messung.");
        if(!report.contentEquals(result.getText()))result.setText(report);
        String active=PerformanceSession.activeStatus();
        String state=active.isEmpty()?prefs().getString(PerformanceSession.LAST_STATUS,"Wähle oben die Ansicht für die Messung."):active;
        if(active.isEmpty()&&state.startsWith("Messung gestartet"))state="Die letzte Messung wurde unterbrochen. Du kannst oben neu starten.";
        if(!state.contentEquals(status.getText()))status.setText(state);
    }
    @Override protected void onResume(){super.onResume();resumed=true;handler.removeCallbacks(refresh);refresh.run();}
    @Override protected void onPause(){resumed=false;handler.removeCallbacks(refresh);super.onPause();}
}
