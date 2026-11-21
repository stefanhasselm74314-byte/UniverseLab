package de.universelab.sternfenster;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.Shader;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.TimeZone;

/** Für Android-Widgets optimierte Offline-Himmelskarte. */
final class SkyRenderer {
    private static final double PI = Math.PI;
    private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
    private Canvas canvas;
    private int width, height;
    private double scale, az0, alt0;
    private static final String[] DIRS = {"NORD", "OST", "SÜD", "WEST"};

    static Bitmap draw(Context context, int width, int height,
                       double latitude, double longitude, int direction, boolean gps) {
        return new SkyRenderer().render(context, width, height, latitude, longitude, direction, gps);
    }

    private Bitmap render(Context context, int w, int h, double lat, double lon, int direction, boolean gps) {
        width = Math.max(280, Math.min(900, w));
        height = Math.max(160, Math.min(520, h));
        Bitmap bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.RGB_565);
        canvas = new Canvas(bitmap);
        long now = System.currentTimeMillis();
        az0 = direction*90.0;
        alt0 = 42.0;
        scale = (height * 0.5) / Math.toRadians(58.0);
        Paint bg = new Paint();
        bg.setShader(new LinearGradient(0,0,0,height,0xff030817,0xff112c4d, Shader.TileMode.CLAMP));
        canvas.drawRect(0,0,width,height,bg);
        drawGrid();
        List<StarCatalog.Star> stars = StarCatalog.load(context);
        double[] vec = new double[3];
        // Sichtbarkeitsprüfung auf Basis desselben Orts- und Zeitpunkts wie die Karte.
        for (StarCatalog.Star s : stars) {
            double[] v = SkyMath.horizonVector(s.ra, s.dec, lat, lon, now);
            if (v[2] <= 0) continue; // unter dem mathematischen Horizont
            float[] xy = project(v);
            if (xy == null || xy[0] < -20 || xy[0] > width+20 || xy[1] < -20 || xy[1] > height+20) continue;
            float radius = (float)Math.max(0.65, Math.min(5.5, 3.8 - 0.53*s.mag));
            int col = s.bv > 1.35 ? 0xffffc4a7 : s.bv > 0.65 ? 0xffffe6c0 : s.bv < -0.05 ? 0xffc2ddff : 0xfff2f7ff;
            p.setStyle(Paint.Style.FILL);
            p.setColor(col); p.setAlpha(Math.max(90,(int)(255 - Math.max(0,s.mag)*16)));
            if (s.mag < 1.5) {
                p.setColor(col); p.setAlpha(30);
                canvas.drawCircle(xy[0],xy[1],radius*3.3f,p);
                p.setAlpha(72); canvas.drawCircle(xy[0],xy[1],radius*2.0f,p);
            }
            p.setColor(col); p.setAlpha(255); canvas.drawCircle(xy[0],xy[1],radius,p);
            // Nur helle, benannte Sterne beschriften, um die kleine Fläche lesbar zu halten.
            if (s.mag <= 1.95 && !s.name.isEmpty() && width >= 380) {
                p.setColor(0xffc1d7f4); p.setTextSize(Math.max(13, height/31f));
                p.setTypeface(android.graphics.Typeface.create("sans-serif",0));
                canvas.drawText(s.name,xy[0]+radius+5,xy[1]-5,p);
            }
        }
        // Halbtransparente Beschriftungsleiste.
        p.setStyle(Paint.Style.FILL); p.setColor(0xb903101e);
        canvas.drawRoundRect(8,8,width-8,Math.max(43,height/6f),12,12,p);
        p.setColor(0xff99d9ff); p.setTextSize(Math.max(14,height/22f));
        p.setTypeface(android.graphics.Typeface.create("sans-serif-medium",1));
        canvas.drawText("STERNFENSTER   ·   "+DIRS[direction],20,Math.max(27,height/13f),p);
        SimpleDateFormat fmt = new SimpleDateFormat("dd.MM. HH:mm",Locale.GERMANY);
        fmt.setTimeZone(TimeZone.getDefault());
        p.setTypeface(android.graphics.Typeface.create("sans-serif",0));
        p.setTextSize(Math.max(12,height/28f)); p.setColor(0xffc9ddf4);
        canvas.drawText(fmt.format(new Date(now)) + "  ·  " +(gps?"GPS-Standort":"Dresden (Standard)"),
                20,Math.max(44,height/6f-6),p);
        p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(1.3f);p.setColor(0x6683b6ee);
        canvas.drawRoundRect(1,1,width-2,height-2,14,14,p);
        p.setStyle(Paint.Style.FILL);p.setShader(null);
        return bitmap;
    }

    /** Winkelabstandstreue Azimutalprojektion auf die Blickrichtung. */
    private float[] project(double[] v) {
        double azi = Math.toRadians(az0), alti = Math.toRadians(alt0);
        double ce = Math.cos(alti)*Math.sin(azi), cn = Math.cos(alti)*Math.cos(azi), cu = Math.sin(alti);
        double dot = Math.max(-1,Math.min(1,v[0]*ce+v[1]*cn+v[2]*cu));
        double a = Math.acos(dot);
        if (a>Math.toRadians(142)) return null;
        double xx = v[0]*Math.cos(azi)-v[1]*Math.sin(azi);
        double yy = -v[0]*Math.sin(alti)*Math.sin(azi)-v[1]*Math.sin(alti)*Math.cos(azi)+v[2]*Math.cos(alti);
        double ss=Math.hypot(xx,yy);
        if(ss<1e-9) return new float[]{width/2f,height/2f};
        return new float[]{(float)(width*.5+scale*a*xx/ss),(float)(height*.5-scale*a*yy/ss)};
    }
    private float[] projectHorizontal(double altitude, double azimuth) {
        double a=Math.toRadians(altitude), z=Math.toRadians(azimuth);
        return project(new double[]{Math.cos(a)*Math.sin(z),Math.cos(a)*Math.cos(z),Math.sin(a)});
    }
    private void drawGrid() {
        p.setStyle(Paint.Style.STROKE);
        for(int alt=0;alt<=60;alt+=30) {
            p.setColor(alt==0?0x8d67bad6:0x24599cc8);p.setStrokeWidth(alt==0?2.0f:1.0f);
            float[] prev=null;
            for(int az=0;az<=360;az+=2){
                float[] q=projectHorizontal(alt,az);
                if(q!=null && prev!=null && Math.hypot(q[0]-prev[0],q[1]-prev[1]) < 90)
                    canvas.drawLine(prev[0],prev[1],q[0],q[1],p);
                prev=q;
            }
        }
        p.setColor(0x24599cc8);p.setStrokeWidth(1.0f);
        for(int az=0;az<360;az+=30){
            float[] prev=null;
            for(int alt=0;alt<=90;alt+=3){
                float[] q=projectHorizontal(alt,az);
                if(q!=null && prev!=null && Math.hypot(q[0]-prev[0],q[1]-prev[1]) < 70)
                    canvas.drawLine(prev[0],prev[1],q[0],q[1],p);
                prev=q;
            }
        }
        // Himmelsrichtungsmarkierung knapp über dem Horizont.
        p.setStyle(Paint.Style.FILL); p.setTextSize(Math.max(12,height/29f));p.setColor(0xff85bddb);
        String[] dirs={"N","O","S","W"};
        for(int i=0;i<4;i++){
            float[] pos=projectHorizontal(5,i*90);
            if(pos!=null && pos[0]>=15&&pos[0]<=width-15&&pos[1]>=55&&pos[1]<=height-10)
                canvas.drawText(dirs[i],pos[0],pos[1],p);
        }
    }
}
