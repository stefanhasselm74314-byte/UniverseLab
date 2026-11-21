package de.universelab.sternfenster;

import android.app.Activity;
import android.graphics.Insets;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

final class Ui {
    static final int BG=0xff0c1420, TEXT=0xffecf3fa, MUTED=0xffaebed0;
    private Ui() { }
    static int dp(Activity a,float value) {return Math.round(value*a.getResources().getDisplayMetrics().density);}
    static TextView text(Activity a,String content,float size,int color) {
        TextView v=new TextView(a);
        v.setText(content);v.setTextSize(size);v.setTextColor(color);v.setLineSpacing(dp(a,3),1);
        return v;
    }
    static Button button(Activity a,String label,Runnable action) {
        Button b=new Button(a);
        b.setText(label);b.setAllCaps(false);b.setTextSize(15);b.setTextColor(TEXT);
        b.setMinHeight(dp(a,50));b.setMinimumHeight(dp(a,50));b.setMinWidth(0);b.setMinimumWidth(0);
        b.setPadding(dp(a,12),dp(a,9),dp(a,12),dp(a,9));
        GradientDrawable bg=new GradientDrawable();
        bg.setColor(0xff253548);bg.setCornerRadius(dp(a,12));bg.setStroke(dp(a,1),0xff405c72);
        b.setBackground(bg);b.setOnClickListener(v->action.run());
        return b;
    }
    static void addButton(Activity a,LinearLayout panel,String label,Runnable action) {
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);
        lp.setMargins(0,dp(a,6),0,dp(a,6));panel.addView(button(a,label,action),lp);
    }
    static void heading(Activity a,LinearLayout panel,String label) {
        TextView v=text(a,label,18,0xffb9dcf4);v.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        v.setPadding(0,dp(a,22),0,dp(a,10));panel.addView(v);
    }
    static void install(Activity a,View root) {
        a.getWindow().setStatusBarColor(BG);a.getWindow().setNavigationBarColor(BG);
        root.setBackgroundColor(BG);
        if(android.os.Build.VERSION.SDK_INT>=30) {
            a.getWindow().setDecorFitsSystemWindows(false);
            int l=root.getPaddingLeft(),t=root.getPaddingTop(),r=root.getPaddingRight(),b=root.getPaddingBottom();
            root.setOnApplyWindowInsetsListener((v,insets)->{
                Insets i=insets.getInsets(WindowInsets.Type.systemBars()|WindowInsets.Type.displayCutout());
                v.setPadding(l+i.left,t+i.top,r+i.right,b+i.bottom);return insets;
            });
            WindowInsetsController c=a.getWindow().getInsetsController();
            if(c!=null)c.setSystemBarsAppearance(0,WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS
                    |WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS);
        }
        a.setContentView(root);root.requestApplyInsets();
    }
}
