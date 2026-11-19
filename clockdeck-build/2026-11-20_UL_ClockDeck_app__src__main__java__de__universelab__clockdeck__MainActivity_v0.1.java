package de.universelab.clockdeck;

import android.app.Activity;
import android.app.WallpaperManager;
import android.appwidget.AppWidgetManager;
import android.content.ComponentName;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.os.Bundle;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowInsets;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

/** No web runtime, tracker, account or network permission. */
public final class MainActivity extends Activity {
    private final Handler loop=new Handler(Looper.getMainLooper());
    private SharedPreferences prefs;
    private int style;
    private boolean inFront=false;
    private Preview preview;
    private TextView styleTitle,info;
    private Button[] themeButtons=new Button[3];
    private final int BACK=Color.rgb(6,11,21),PANEL=Color.rgb(18,27,40),WHITE=Color.rgb(233,243,255),MUTED=Color.rgb(167,183,201);
    private final Runnable refresh=new Runnable(){@Override public void run(){if(inFront&&preview!=null){preview.invalidate();loop.postDelayed(this,120);}}};

    private int dp(int n){return Math.round(getResources().getDisplayMetrics().density*n);}
    private TextView label(String s,int size,int col){TextView v=new TextView(this);v.setText(s);v.setTextSize(size);v.setTextColor(col);v.setGravity(Gravity.CENTER_HORIZONTAL);return v;}
    private void add(LinearLayout parent,View child,int w,int h){parent.addView(child,new LinearLayout.LayoutParams(w<0?w:dp(w),h<0?h:dp(h)));}
    private Button button(String s,Runnable click){Button b=new Button(this);b.setText(s);b.setAllCaps(false);b.setTextColor(WHITE);b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(PANEL));b.setOnClickListener(v->click.run());return b;}

    @Override public void onCreate(Bundle state){super.onCreate(state);
        getWindow().setStatusBarColor(BACK);getWindow().setNavigationBarColor(BACK);
        prefs=getSharedPreferences("settings",MODE_PRIVATE);style=prefs.getInt("wall_style",2);
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);scroll.setBackgroundColor(BACK);
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(18),dp(24),dp(18),dp(34));scroll.addView(root);
        if(Build.VERSION.SDK_INT>=35){
            scroll.setOnApplyWindowInsetsListener((view,insets)->{
                android.graphics.Insets b=insets.getInsets(WindowInsets.Type.systemBars()|WindowInsets.Type.displayCutout());
                root.setPadding(dp(18),dp(24)+b.top,dp(18),dp(34)+b.bottom);
                return insets;
            });
        }
        add(root,label("UNIVERSELAB   /   CLOCKDECK",14,Color.rgb(112,220,252)),-1,28);
        add(root,label("Uhren für Android",27,WHITE),-1,48);
        add(root,label("3 Widgets · 3 Live-Hintergründe · echte Uhrzeit",13,MUTED),-1,30);
        preview=new Preview();
        LinearLayout.LayoutParams pv=new LinearLayout.LayoutParams(-1,dp(350));pv.topMargin=dp(10);pv.bottomMargin=dp(12);
        root.addView(preview,pv);
        styleTitle=label("",20,WHITE);add(root,styleTitle,-1,36);
        info=label("",13,MUTED);add(root,info,-1,64);
        LinearLayout themes=new LinearLayout(this);themes.setOrientation(LinearLayout.HORIZONTAL);
        String[] names={"Titan","Kompass","Holo-6D"};
        for(int i=0;i<3;i++){
            final int theme=i;Button b=button(names[i],()->choose(theme));
            themeButtons[i]=b;LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(0,dp(54),1);
            params.setMargins(dp(2),dp(2),dp(2),dp(2));themes.addView(b,params);
        }
        add(root,themes,-1,60);
        Button wallpaper=button("Live-Hintergrund auswählen",this::applyWallpaper);
        add(root,wallpaper,-1,57);
        Button widget=button("Uhr-Widget zum Startbildschirm hinzufügen",this::addWidget);
        add(root,widget,-1,58);
        Button compass=button("Echten Magnetkompass testen",()->startActivity(new Intent(this,CompassActivity.class)));
        add(root,compass,-1,57);
        Button energy=button("",()->{
            int fps=prefs.getInt("fps",18);
            fps=fps>=25?10:fps>=18?25:18;
            prefs.edit().putInt("fps",fps).apply();
            Toast.makeText(this,"Animation: "+fps+" Bilder/s",Toast.LENGTH_SHORT).show();
            updateEnergy();
        });
        energy.setTag("energy");add(root,energy,-1,57);
        Button tilt=button("",()->{
            boolean enabled=!prefs.getBoolean("parallax",true);
            prefs.edit().putBoolean("parallax",enabled).apply();
            updateEnergy();
        });
        tilt.setTag("tilt");add(root,tilt,-1,57);
        add(root,label("Hinweis: Widget-Zifferblätter sind auf Akkuschonung ausgelegt. " +
            "Die Echtzeit-Sensoranimation läuft nur im sichtbaren Live-Hintergrund. " +
            "Alle Designs sind originale, programmatisch gezeichnete Modelle – keine 1:1-Kopien der Luxusuhr-Vorbilder.",12,MUTED),-1,-2);
        setContentView(scroll);
        choose(style);updateEnergy();
    }
    private void updateEnergy(){
        ScrollView s=(ScrollView)((ViewGroup)findViewById(android.R.id.content)).getChildAt(0);
        for(View view:walk((ViewGroup)s.getChildAt(0))){
            if("energy".equals(view.getTag())&&view instanceof Button)
                ((Button)view).setText("Animation: "+prefs.getInt("fps",18)+" FPS  ·  tippen zum Ändern");
            if("tilt".equals(view.getTag())&&view instanceof Button)
                ((Button)view).setText("Neigungsparallaxe: "+(prefs.getBoolean("parallax",true)?"EIN":"AUS"));
        }
    }
    private java.util.List<View> walk(ViewGroup root){
        java.util.ArrayList<View> all=new java.util.ArrayList<>();
        for(int i=0;i<root.getChildCount();i++){
            View v=root.getChildAt(i);all.add(v);
            if(v instanceof ViewGroup)all.addAll(walk((ViewGroup)v));
        }return all;
    }
    private void choose(int i){
        style=Math.max(0,Math.min(i,2));prefs.edit().putInt("wall_style",style).apply();
        String[] titles={"TITAN SKELETON","COMPASS INSTRUMENT","HOLO-6D ORBITAL"};
        String[] descriptions={
            "Titanfarbene Zahnräder, Rubinlager und ein rotierender Dreiachsenkäfig.",
            "Präzisionsskala und echter magnetischer Kompass in der Sensoransicht.",
            "Irisierende Ringe, dreidimensionale Projektion und reaktive Tiefenebenen."};
        styleTitle.setText(titles[style]);info.setText(descriptions[style]);
        for(int j=0;j<3;j++)themeButtons[j].setBackgroundTintList(
                android.content.res.ColorStateList.valueOf(j==style?Color.rgb(32,91,115):PANEL));
        if(preview!=null)preview.invalidate();
    }
    private void applyWallpaper(){
        Intent intent=new Intent(WallpaperManager.ACTION_CHANGE_LIVE_WALLPAPER);
        intent.putExtra(WallpaperManager.EXTRA_LIVE_WALLPAPER_COMPONENT,
                new ComponentName(this,HoloWallpaperService.class));
        try{startActivity(intent);}catch(Exception e){
            try{startActivity(new Intent(WallpaperManager.ACTION_LIVE_WALLPAPER_CHOOSER));}
            catch(Exception inner){Toast.makeText(this,"Kein Live-Wallpaper-Auswahldialog gefunden",Toast.LENGTH_LONG).show();}
        }
    }
    private void addWidget(){
        AppWidgetManager manager=AppWidgetManager.getInstance(this);
        if(Build.VERSION.SDK_INT>=26 && manager.isRequestPinAppWidgetSupported()){
            Class<?> provider=style==0?TitanWidget.class:style==1?CompassWidget.class:HoloWidget.class;
            manager.requestPinAppWidget(new ComponentName(this,provider),null,null);
        }else Toast.makeText(this,"Homescreen lange drücken → Widgets → UniverseLab ClockDeck",Toast.LENGTH_LONG).show();
    }
    private class Preview extends View {
        private final ClockRenderer renderer=new ClockRenderer();
        private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
        Preview(){super(MainActivity.this);setLayerType(View.LAYER_TYPE_SOFTWARE,null);}
        @Override protected void onDraw(Canvas c){super.onDraw(c);
            int w=getWidth(),h=getHeight();
            paint.setColor(PANEL);c.drawRoundRect(0,0,w,h,dp(24),dp(24),paint);
            float r=Math.min(w*.42f,h*.43f);
            renderer.drawFace(c,w*.5f,h*.50f,r,style,System.currentTimeMillis(),
                    System.currentTimeMillis()/1000.0,0,0,Float.NaN,Battery.percent(MainActivity.this),true);
        }
    }
    @Override protected void onResume(){super.onResume();inFront=true;loop.removeCallbacks(refresh);loop.post(refresh);}
    @Override protected void onPause(){inFront=false;loop.removeCallbacks(refresh);super.onPause();}
}
