package de.universelab.sternfenster;

import android.app.AppOpsManager;
import android.app.KeyguardManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.content.pm.ServiceInfo;
import android.content.res.Configuration;
import android.graphics.Insets;
import android.graphics.PixelFormat;
import android.graphics.Rect;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.hardware.display.DisplayManager;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.PowerManager;
import android.provider.Settings;
import android.text.TextUtils;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.ContextThemeWrapper;
import android.view.Display;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowManager;
import android.view.WindowMetrics;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

/** User-started overlay, independent of the Activity task; no alarms or boot restarts. */
public final class FloatingSkyService extends Service {
    public static final String ACTION_SHOW="de.universelab.sternfenster.SHOW_FLOATING";
    public static final String ACTION_CLOSE="de.universelab.sternfenster.CLOSE_FLOATING";
    private static final String ACTIVE="overlay_user_active",CHANNEL="floating_sky";
    private static final int NOTIFICATION_ID=730;
    private final Handler main=new Handler(Looper.getMainLooper());
    private final Rect available=new Rect();
    private SharedPreferences preferences;
    private WindowManager manager;
    private WindowManager.LayoutParams parameters;
    private Context windowContext;
    private Display display;
    private LinearLayout root;
    private OverlaySkyView sky;
    private AppOpsManager appOps;
    private float density=1;
    private boolean attached,receiverRegistered,destroyed;
    private final AppOpsManager.OnOpChangedListener permissionChanged=(op,pkg)->main.post(()->{
        if(!destroyed&&root!=null&&!Settings.canDrawOverlays(this))closeWindow();
    });
    private final BroadcastReceiver screenEvents=new BroadcastReceiver(){
        @Override public void onReceive(Context context,Intent intent){
            if(sky==null)return;
            if(Intent.ACTION_SCREEN_OFF.equals(intent.getAction()))sky.setScreenUsable(false);else updateScreenState();
        }
    };

    @Override public void onCreate(){
        super.onCreate();preferences=getSharedPreferences(SkyWidgetProvider.PREFS,MODE_PRIVATE);
        IntentFilter filter=new IntentFilter();filter.addAction(Intent.ACTION_SCREEN_OFF);
        filter.addAction(Intent.ACTION_SCREEN_ON);filter.addAction(Intent.ACTION_USER_PRESENT);
        if(Build.VERSION.SDK_INT>=33)registerReceiver(screenEvents,filter,Context.RECEIVER_NOT_EXPORTED);
        else registerReceiver(screenEvents,filter);
        receiverRegistered=true;
        appOps=getSystemService(AppOpsManager.class);
        if(appOps!=null)try{appOps.startWatchingMode(AppOpsManager.OPSTR_SYSTEM_ALERT_WINDOW,getPackageName(),permissionChanged);}
        catch(RuntimeException e){Log.w("SternfensterOverlay","Cannot watch overlay permission",e);}
    }
    @Override public int onStartCommand(Intent intent,int flags,int startId){
        String action=intent==null?null:intent.getAction();
        if(ACTION_CLOSE.equals(action)){closeWindow();return START_NOT_STICKY;}
        boolean requested=ACTION_SHOW.equals(action);
        if(!requested&&(intent!=null||!preferences.getBoolean(ACTIVE,false))){stopSelf();return START_NOT_STICKY;}
        if(!Settings.canDrawOverlays(this)){closeWindow();return START_NOT_STICKY;}
        try{
            promoteForeground();
            if(root==null)createWindow(intent);else if(requested)sky.applyIntent(intent);
            preferences.edit().putBoolean(ACTIVE,true).apply();updateScreenState();
            return START_STICKY;
        }catch(RuntimeException e){
            Log.e("SternfensterOverlay","Cannot attach live window",e);
            Toast.makeText(this,"Live-Fenster konnte nicht geöffnet werden. Prüfe „Über anderen Apps anzeigen“.",Toast.LENGTH_LONG).show();
            closeWindow();return START_NOT_STICKY;
        }
    }
    private void promoteForeground(){
        NotificationManager notifications=getSystemService(NotificationManager.class);
        NotificationChannel channel=new NotificationChannel(CHANNEL,"Schwebendes Livefenster",NotificationManager.IMPORTANCE_LOW);
        channel.setDescription("Status und Schließen des sichtbaren Sternfensters");notifications.createNotificationChannel(channel);
        int pendingFlags=PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE;
        PendingIntent open=PendingIntent.getActivity(this,730,new Intent(this,MainActivity.class)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TOP),pendingFlags);
        PendingIntent close=PendingIntent.getService(this,731,new Intent(this,FloatingSkyService.class).setAction(ACTION_CLOSE),pendingFlags);
        Notification notification=new Notification.Builder(this,CHANNEL).setSmallIcon(R.drawable.app_icon)
                .setContentTitle("Sternfenster · Live-Fenster").setContentText("Über anderen Apps aktiv · Hier öffnen oder schließen")
                .setContentIntent(open).setOngoing(true).setOnlyAlertOnce(true).setCategory(Notification.CATEGORY_SERVICE)
                .addAction(new Notification.Action.Builder(android.R.drawable.ic_menu_close_clear_cancel,"Fenster schließen",close).build()).build();
        if(Build.VERSION.SDK_INT>=34)startForeground(NOTIFICATION_ID,notification,ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE);
        else startForeground(NOTIFICATION_ID,notification);
    }
    private void createWindow(Intent intent){
        DisplayManager displays=getSystemService(DisplayManager.class);display=displays.getDisplay(Display.DEFAULT_DISPLAY);
        if(display==null)throw new IllegalStateException("No display");
        Context displayContext=createDisplayContext(display);
        Context base=Build.VERSION.SDK_INT>=30?displayContext.createWindowContext(WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,null):displayContext;
        windowContext=new ContextThemeWrapper(base,android.R.style.Theme_Material_NoActionBar);
        manager=windowContext.getSystemService(WindowManager.class);density=windowContext.getResources().getDisplayMetrics().density;
        root=new LinearLayout(windowContext);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(4),dp(4),dp(4),dp(4));
        GradientDrawable background=new GradientDrawable();background.setColor(0xff0c1926);background.setCornerRadius(dp(16));
        background.setStroke(dp(1),0xff4c7086);root.setBackground(background);root.setClipToOutline(true);root.setElevation(dp(8));
        LinearLayout header=new LinearLayout(windowContext);header.setGravity(Gravity.CENTER_VERTICAL);
        TextView title=new TextView(windowContext);title.setText("Sternfenster · Live");title.setTextColor(0xffc1e5fa);
        title.setTextSize(13);title.setTypeface(Typeface.DEFAULT,Typeface.BOLD);title.setGravity(Gravity.CENTER_VERTICAL);
        title.setPadding(dp(8),0,0,0);title.setSingleLine(true);title.setEllipsize(TextUtils.TruncateAt.END);
        title.setContentDescription("Live-Fenster verschieben");title.setOnTouchListener(new WindowGesture(false));
        header.addView(title,new LinearLayout.LayoutParams(0,-1,1));
        Button close=button("×","Live-Fenster schließen",this::closeWindow);
        close.setTextSize(23);header.addView(close,new LinearLayout.LayoutParams(dp(42),-1));
        root.addView(header,new LinearLayout.LayoutParams(-1,dp(40)));
        sky=new OverlaySkyView(windowContext,preferences,intent);root.addView(sky,new LinearLayout.LayoutParams(-1,0,1));
        LinearLayout controls=new LinearLayout(windowContext);controls.setGravity(Gravity.CENTER_VERTICAL);controls.setBaselineAligned(false);
        Button follow=button("Handy folgen","Handy im Live-Fenster folgen",()->sky.setFollowing(!sky.isFollowing()));
        controls.addView(follow,new LinearLayout.LayoutParams(0,-1,1));
        sky.setControlsChanged(()->{follow.setEnabled(sky.hasSensors());follow.setText(sky.isFollowing()?"Handy: an":"Handy: aus");});
        controls.addView(button("−","Im Live-Fenster herauszoomen",()->sky.zoom(1.22)),new LinearLayout.LayoutParams(dp(36),-1));
        controls.addView(button("+","Im Live-Fenster hineinzoomen",()->sky.zoom(1/1.22)),new LinearLayout.LayoutParams(dp(36),-1));
        TextView resize=new TextView(windowContext);resize.setText("↘");resize.setTextSize(25);resize.setTextColor(0xffbbd5e5);
        resize.setGravity(Gravity.CENTER);resize.setContentDescription("Live-Fenstergröße ändern");resize.setOnTouchListener(new WindowGesture(true));
        controls.addView(resize,new LinearLayout.LayoutParams(dp(40),-1));root.addView(controls,new LinearLayout.LayoutParams(-1,dp(44)));
        parameters=new WindowManager.LayoutParams(1,1,WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE|WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN
                        |WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED,PixelFormat.TRANSLUCENT);
        parameters.gravity=Gravity.TOP|Gravity.LEFT;parameters.setTitle("Sternfenster Live-Fenster");
        if(Build.VERSION.SDK_INT>=30)parameters.setFitInsetsTypes(0);
        measureAvailable();restoreBounds();requestSmoothDisplay();
        manager.addView(root,parameters);attached=true;
        sky.post(()->{if(!destroyed){requestSmoothDisplay();updateScreenState();}});
        Log.i("SternfensterOverlay","window_attached");
    }
    private Button button(String label,String description,Runnable action){
        Button b=new Button(windowContext);b.setText(label);b.setAllCaps(false);b.setTextSize(11);b.setTextColor(0xffe3f0f9);
        b.setMinHeight(0);b.setMinimumHeight(0);b.setMinWidth(0);b.setMinimumWidth(0);b.setPadding(dp(3),0,dp(3),0);
        b.setBackgroundColor(0x00000000);b.setContentDescription(description);b.setOnClickListener(v->action.run());return b;
    }
    private int dp(float value){return Math.round(value*density);}
    private void measureAvailable(){
        if(Build.VERSION.SDK_INT>=30){
            WindowMetrics metrics=manager.getMaximumWindowMetrics();Rect b=metrics.getBounds();
            Insets insets=metrics.getWindowInsets().getInsetsIgnoringVisibility(WindowInsets.Type.systemBars()|WindowInsets.Type.displayCutout());
            available.set(b.left+insets.left,b.top+insets.top,b.right-insets.right,b.bottom-insets.bottom);
        }else{
            DisplayMetrics metrics=new DisplayMetrics();display.getRealMetrics(metrics);
            int status=getResources().getIdentifier("status_bar_height","dimen","android");
            int nav=getResources().getIdentifier("navigation_bar_height","dimen","android");
            available.set(0,status==0?0:getResources().getDimensionPixelSize(status),metrics.widthPixels,
                    metrics.heightPixels-(nav==0?0:getResources().getDimensionPixelSize(nav)));
        }
        available.inset(dp(5),dp(5));
    }
    private void restoreBounds(){
        parameters.width=dp(preferences.getFloat("overlay_width_dp",280));parameters.height=dp(preferences.getFloat("overlay_height_dp",352));
        parameters.x=available.left+dp(preferences.getFloat("overlay_x_dp",10));parameters.y=available.top+dp(preferences.getFloat("overlay_y_dp",58));
        clampBounds();
    }
    private void clampBounds(){
        int maxWidth=Math.max(1,Math.min(dp(620),(int)(available.width()*.94f)));
        int maxHeight=Math.max(1,Math.min(dp(740),(int)(available.height()*.94f)));
        parameters.width=Math.max(Math.min(dp(212),maxWidth),Math.min(maxWidth,parameters.width));
        parameters.height=Math.max(Math.min(dp(242),maxHeight),Math.min(maxHeight,parameters.height));
        parameters.x=Math.max(available.left,Math.min(available.right-parameters.width,parameters.x));
        parameters.y=Math.max(available.top,Math.min(available.bottom-parameters.height,parameters.y));
    }
    private void saveBounds(){
        if(parameters==null)return;
        preferences.edit().putFloat("overlay_width_dp",parameters.width/density).putFloat("overlay_height_dp",parameters.height/density)
                .putFloat("overlay_x_dp",(parameters.x-available.left)/density).putFloat("overlay_y_dp",(parameters.y-available.top)/density).apply();
    }
    private void updateLayout(){
        if(!attached||destroyed)return;
        try{manager.updateViewLayout(root,parameters);}
        catch(RuntimeException e){Log.w("SternfensterOverlay","Window no longer available",e);closeWindow();}
    }
    private void requestSmoothDisplay(){
        if(display==null||parameters==null)return;
        Display.Mode current=display.getMode(),best=current;
        for(Display.Mode mode:display.getSupportedModes())if(mode.getPhysicalWidth()==current.getPhysicalWidth()
                &&mode.getPhysicalHeight()==current.getPhysicalHeight()&&mode.getRefreshRate()>best.getRefreshRate())best=mode;
        parameters.preferredDisplayModeId=best.getModeId();parameters.preferredRefreshRate=Math.max(60,best.getRefreshRate());
        if(Build.VERSION.SDK_INT>=35&&sky!=null)sky.setRequestedFrameRate(parameters.preferredRefreshRate);
        updateLayout();
    }
    private void updateScreenState(){
        if(sky==null||destroyed)return;
        if(!Settings.canDrawOverlays(this)){closeWindow();return;}
        PowerManager power=getSystemService(PowerManager.class);KeyguardManager keyguard=getSystemService(KeyguardManager.class);
        sky.setScreenUsable(power!=null&&power.isInteractive()&&(keyguard==null||!keyguard.isKeyguardLocked()));
    }
    private void closeWindow(){
        preferences.edit().putBoolean(ACTIVE,false).apply();
        if(sky!=null)sky.dispose();saveBounds();removeWindow();stopForeground(STOP_FOREGROUND_REMOVE);stopSelf();
    }
    private void removeWindow(){
        if(attached){attached=false;try{manager.removeViewImmediate(root);}catch(RuntimeException e){Log.w("SternfensterOverlay","Window already detached",e);}}
        root=null;sky=null;parameters=null;
    }
    @Override public void onConfigurationChanged(Configuration configuration){
        super.onConfigurationChanged(configuration);if(!attached)return;
        saveBounds();density=windowContext.getResources().getDisplayMetrics().density;
        measureAvailable();restoreBounds();requestSmoothDisplay();updateLayout();updateScreenState();
    }
    @Override public void onTaskRemoved(Intent rootIntent){
        if(sky!=null)sky.persistState();saveBounds();Log.i("SternfensterOverlay","task_removed window_kept");super.onTaskRemoved(rootIntent);
    }
    @Override public void onDestroy(){
        destroyed=true;main.removeCallbacksAndMessages(null);
        if(sky!=null)sky.dispose();saveBounds();removeWindow();
        if(receiverRegistered){unregisterReceiver(screenEvents);receiverRegistered=false;}
        if(appOps!=null)try{appOps.stopWatchingMode(permissionChanged);}catch(RuntimeException e){Log.w("SternfensterOverlay","Permission watcher already removed",e);}
        stopForeground(STOP_FOREGROUND_REMOVE);super.onDestroy();
    }
    @Override public IBinder onBind(Intent intent){return null;}

    private final class WindowGesture implements View.OnTouchListener {
        private final boolean resize;
        private float touchX,touchY;
        private int initialX,initialY,initialWidth,initialHeight;
        WindowGesture(boolean resize){this.resize=resize;}
        @Override public boolean onTouch(View view,MotionEvent event){
            if(parameters==null||destroyed)return false;
            switch(event.getActionMasked()){
                case MotionEvent.ACTION_DOWN:
                    touchX=event.getRawX();touchY=event.getRawY();initialX=parameters.x;initialY=parameters.y;
                    initialWidth=parameters.width;initialHeight=parameters.height;return true;
                case MotionEvent.ACTION_MOVE:
                    int dx=Math.round(event.getRawX()-touchX),dy=Math.round(event.getRawY()-touchY);
                    if(resize){parameters.width=initialWidth+dx;parameters.height=initialHeight+dy;}
                    else{parameters.x=initialX+dx;parameters.y=initialY+dy;}
                    clampBounds();updateLayout();return true;
                case MotionEvent.ACTION_UP:
                    saveBounds();view.performClick();return true;
                case MotionEvent.ACTION_CANCEL:saveBounds();return true;
                default:return true;
            }
        }
    }
}
