package de.universelab.clockdeck;

import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.LinearGradient;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RadialGradient;
import android.graphics.RectF;
import android.graphics.Shader;
import android.graphics.Typeface;
import java.util.Calendar;
import java.util.Locale;

/** Independent procedural graphics. None of the original luxury watch images are embedded. */
public final class ClockRenderer {
    private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG | Paint.FILTER_BITMAP_FLAG);
    private static final int INK = Color.rgb(5, 9, 18);
    private static final int METAL = Color.rgb(175, 193, 205);
    private static final int BRIGHT = Color.rgb(238, 248, 255);
    private static final int BLUE = Color.rgb(30, 187, 255);
    private static final int GOLD = Color.rgb(234, 168, 70);

    private void fill(int color) { p.reset(); p.setAntiAlias(true); p.setColor(color); p.setStyle(Paint.Style.FILL); }
    private void stroke(int color,float width) { fill(color); p.setStyle(Paint.Style.STROKE); p.setStrokeWidth(width); p.setStrokeCap(Paint.Cap.ROUND); }
    private static int alpha(int a,int c) {return (Math.max(0,Math.min(255,a))<<24) | (c & 0x00ffffff);}
    private void circle(Canvas c,float x,float y,float r,int color) {fill(color);c.drawCircle(x,y,r,p);}
    private void ring(Canvas c,float x,float y,float r,int color,float w) {stroke(color,w);c.drawCircle(x,y,r,p);}
    private void line(Canvas c,float a,float b,float x,float y,int col,float w) {stroke(col,w);c.drawLine(a,b,x,y,p);}
    private void text(Canvas c,String s,float x,float y,float sz,int color,boolean heavy) {
        fill(color);p.setTypeface(Typeface.create(heavy?"sans-serif-condensed":"sans-serif",heavy?Typeface.BOLD:Typeface.NORMAL));
        p.setTextSize(sz);p.setTextAlign(Paint.Align.CENTER);c.drawText(s,x,y,p);
    }
    private void gradient(Canvas c,float x,float y,float r,int center,int edge) {
        fill(center); p.setShader(new RadialGradient(x-r*.23f,y-r*.30f,r*1.32f,
                new int[]{center,edge,INK},new float[]{0f,.68f,1f}, Shader.TileMode.CLAMP));
        c.drawCircle(x,y,r,p); p.setShader(null);
    }
    private void drawGear(Canvas c,float x,float y,float r,float rot,int color) {
        int teeth=18;
        for(int i=0;i<teeth;i++){
            float a=(float)(rot+i*2*Math.PI/teeth);
            float x1=x+(float)Math.cos(a)*(r*.91f), y1=y+(float)Math.sin(a)*(r*.91f);
            float x2=x+(float)Math.cos(a)*r*1.11f, y2=y+(float)Math.sin(a)*r*1.11f;
            line(c,x1,y1,x2,y2,alpha(210,color),Math.max(2.8f,r*.13f));
        }
        circle(c,x,y,r,Color.rgb(22,29,39));
        ring(c,x,y,r,alpha(240,color),1.7f);
        circle(c,x,y,r*.71f,Color.rgb(7,13,22));
        ring(c,x,y,r*.71f,alpha(130,color),1.4f);
        for(int i=0;i<5;i++){
            float a=(float)(rot+i*2*Math.PI/5);
            line(c,x+(float)Math.cos(a)*r*.11f,y+(float)Math.sin(a)*r*.11f,
                    x+(float)Math.cos(a)*r*.73f,y+(float)Math.sin(a)*r*.73f,
                    alpha(205,color),Math.max(2.3f,r*.14f));
        }
        circle(c,x,y,r*.15f,Color.rgb(95,12,38));
        ring(c,x,y,r*.15f,alpha(220,Color.WHITE),1f);
    }
    private void metalBridge(Canvas c,float x1,float y1,float x2,float y2) {
        line(c,x1,y1,x2,y2,Color.rgb(20,27,39),9f);
        line(c,x1,y1,x2,y2,Color.rgb(124,142,160),5f);
        line(c,x1-1,y1-1,x2-1,y2-1,Color.rgb(219,231,239),1.15f);
        circle(c,x1,y1,3.3f,Color.rgb(21,32,43));
        ring(c,x1,y1,3.3f,Color.rgb(181,195,206),.8f);
    }
    private void background(Canvas c,int style,float x,float y,float r) {
        int core=(style==2)?Color.rgb(4,18,40):style==1?Color.rgb(12,21,28):Color.rgb(17,21,29);
        gradient(c,x,y,r,core,INK);
        ring(c,x,y,r-2,Color.rgb(160,169,180),3.5f);
        ring(c,x,y,r-7,alpha(150,Color.WHITE),.7f);
        ring(c,x,y,r-13,alpha(130,style==2?BLUE:METAL),1.2f);
        ring(c,x,y,r-24,alpha(67,style==2?BLUE:METAL),.9f);
        if(style==2){
            for(int i=0;i<48;i++){
                float a=(float)(i*2*Math.PI/48);
                float rr=r*(.18f+((i*37)%49)/100f);
                circle(c,x+rr*(float)Math.cos(a),y+rr*(float)Math.sin(a),.4f+(i%3)*.23f,alpha(140,BLUE));
            }
        }
    }
    private void outerScale(Canvas c,int style,float x,float y,float r,float heading) {
        // Rotation relative to the screen; in the sensor compass the heading is magnetic.
        c.save();
        if(style==1 && !Float.isNaN(heading)) c.rotate(-heading,x,y);
        for(int i=0;i<72;i++){
            float a=(float)(i*2*Math.PI/72-Math.PI/2);
            float r0=r-(i%6==0?14:10), r1=r-5;
            int col=(i%6==0)?BRIGHT:alpha(130,METAL);
            line(c,x+(float)Math.cos(a)*r0,y+(float)Math.sin(a)*r0,
                x+(float)Math.cos(a)*r1,y+(float)Math.sin(a)*r1,col,i%6==0?1.9f:.75f);
        }
        for(int i=0;i<4;i++){
            float a=(float)(i*Math.PI/2-Math.PI/2);
            text(c,new String[]{"N","E","S","W"}[i],x+(r-29)*(float)Math.cos(a),
                 y+(r-29)*(float)Math.sin(a)+4f,13.5f,i==0?Color.rgb(255,85,77):BRIGHT,true);
        }
        c.restore();
        // Fixed triangular sight marking.
        Path mark=new Path();mark.moveTo(x,y-r+1);mark.lineTo(x-4.2f,y-r+9f);
        mark.lineTo(x+4.2f,y-r+9f);mark.close();fill(style==1?Color.RED:BRIGHT);c.drawPath(mark,p);
    }
    private void skeleton(Canvas c,int style,float x,float y,float r,double t) {
        int col=style==2?Color.rgb(93,149,198):METAL;
        float spin=(float)t*.22f;
        float[][] gears={{-.45f,-.36f,.18f},{.44f,-.34f,.16f},{-.46f,.38f,.20f},{.45f,.40f,.20f},{0f,0f,.24f}};
        for(int i=0;i<gears.length;i++){
            float[] g=gears[i];drawGear(c,x+g[0]*r,y+g[1]*r,r*g[2],spin*(i%2==0?1:-1.2f)+i*.7f,col);
        }
        metalBridge(c,x-r*.61f,y-r*.52f,x-r*.32f,y+r*.54f);
        metalBridge(c,x+r*.61f,y-r*.52f,x+r*.32f,y+r*.54f);
        metalBridge(c,x-r*.49f,y-r*.48f,x+r*.49f,y-r*.48f);
        metalBridge(c,x-r*.49f,y+r*.51f,x+r*.49f,y+r*.51f);
    }
    private void ellipse3d(Canvas c,float x,float y,float radius,
                           float phase,float tiltX,float tiltY,int axis,int color) {
        // Render a wireframe circular gimbal in 3-D; display projection is intentionally monoscopic.
        double angle=phase*(axis==1?-.75:axis==2?1.19:1.0);
        double ax=(axis==0?.86:.12)+Math.toRadians(tiltY)*.47;
        double ay=(axis==1?.93:.12)+Math.toRadians(tiltX)*.47;
        double az=axis==2?Math.PI*.29:.0;
        float[] old=null;
        for(int i=0;i<=120;i++){
            double a=i*2*Math.PI/120;
            double xx=Math.cos(a), yy=Math.sin(a), zz=0;
            double y1=yy*Math.cos(ax)-zz*Math.sin(ax),z1=yy*Math.sin(ax)+zz*Math.cos(ax);
            double x2=xx*Math.cos(ay)+z1*Math.sin(ay),z2=-xx*Math.sin(ay)+z1*Math.cos(ay);
            double x3=x2*Math.cos(angle+az)-y1*Math.sin(angle+az);
            double y3=x2*Math.sin(angle+az)+y1*Math.cos(angle+az);
            double depth=1.0+z2*.10;
            float[] now={(float)(x+x3*radius*depth),(float)(y+y3*radius*depth),(float)z2};
            if(old!=null){
                int shadow=old[2]+now[2]>0?color:Color.rgb(52,67,81);
                line(c,old[0]+1.4f,old[1]+2.1f,now[0]+1.4f,now[1]+2.1f,
                    alpha(140,Color.BLACK),5.8f);
                line(c,old[0],old[1],now[0],now[1],shadow,4.2f);
                if(old[2]+now[2]>0)line(c,old[0]-1,old[1]-1,now[0]-1,now[1]-1,alpha(182,BRIGHT),.9f);
            }
            old=now;
        }
    }
    private void gimbal(Canvas c,int style,float x,float y,float r,double t,float tx,float ty) {
        if(style==1){
            // A compass with a real orientation needle in the dedicated full-screen sensor activity.
            ring(c,x,y,r*.52f,alpha(140,GOLD),1.1f);
            ring(c,x,y,r*.32f,alpha(160,METAL),1f);
            for(int i=0;i<4;i++){
                float a=(float)(i*Math.PI/2);line(c,x-r*.58f*(float)Math.cos(a),y-r*.58f*(float)Math.sin(a),
                    x+r*.58f*(float)Math.cos(a),y+r*.58f*(float)Math.sin(a),alpha(110,METAL),1.3f);
            }
        }
        int m=style==2?BLUE:METAL;
        ellipse3d(c,x,y,r*.62f,(float)(t*.22),tx,ty,0,m);
        ellipse3d(c,x,y,r*.52f,(float)(t*.31),tx,ty,1,style==2?Color.rgb(140,108,255):Color.rgb(202,160,112));
        ellipse3d(c,x,y,r*.41f,(float)(t*.46),tx,ty,2,style==2?Color.rgb(104,228,253):METAL);
        circle(c,x,y,10f,Color.rgb(11,20,32));ring(c,x,y,10f,METAL,2f);
        circle(c,x,y,3.7f,style==2?BLUE:Color.rgb(190,34,72));
    }
    private void spectrum(Canvas c,float x,float y,float r) {
        for(int i=0;i<120;i++){
            float a0=i*3, a1=a0+3.1f;
            float hue=(i*3+280)%360;
            int rgb=Color.HSVToColor(new float[]{hue,.79f,.99f});
            stroke(alpha(198,rgb),2f);
            c.drawArc(new RectF(x-r,y-r,x+r,y+r),a0,a1,false,p);
        }
    }
    /** Circular watch dial, all drawing in virtual units. 'clockText' is false inside Android widgets. */
    public void drawFace(Canvas c,float x,float y,float radius,int style,long now,
                         double phase,float tiltX,float tiltY,float heading,int battery,boolean clockText) {
        c.save();
        float scale=radius/210f;c.translate(x,y);c.scale(scale,scale);
        final float cx=0,cy=0,r=210;
        background(c,style,cx,cy,r);
        if(style==2)spectrum(c,cx,cy,r-18);
        outerScale(c,style,cx,cy,r,heading);
        c.save();c.clipPath(circlePath(0,0,168));
        skeleton(c,style,cx,cy,r*.88f,phase);
        c.save();c.translate(tiltY*.28f,tiltX*.28f);
        gimbal(c,style,cx,cy+8f,r*.92f,phase,tiltX,tiltY);
        c.restore();c.restore();
        ring(c,0,0,151,alpha(150,style==2?BLUE:METAL),1.1f);
        text(c,"UNIVERSELAB",0,-163,16,BRIGHT,true);
        text(c,"6D / "+(style==0?"TITAN":style==1?"COMPASS":"HOLO"),0,-144,10,
                style==2?BLUE:Color.rgb(201,166,115),true);
        if(clockText){
            Calendar d=Calendar.getInstance();d.setTimeInMillis(now);
            String hm=String.format(Locale.GERMANY,"%02d:%02d",d.get(Calendar.HOUR_OF_DAY),d.get(Calendar.MINUTE));
            text(c,hm,0,-104,40,BRIGHT,true);
            String date=String.format(Locale.GERMANY,"%02d.%02d.%04d",d.get(Calendar.DAY_OF_MONTH),
                    d.get(Calendar.MONTH)+1,d.get(Calendar.YEAR));
            text(c,date,0,148,15,Color.rgb(204,223,237),false);
            text(c,battery>=0?"AKKU  "+battery+"%":"AKKU  --%",0,169,11,
                    style==2?BLUE:Color.rgb(198,222,238),true);
            if(style==1 && !Float.isNaN(heading))
                text(c,String.format(Locale.GERMANY,"%03d°  MAG",Math.round(heading)%360),0,123,16,Color.rgb(255,188,105),true);
        }
        c.restore();
    }
    private Path circlePath(float x,float y,float r){Path q=new Path();q.addCircle(x,y,r,Path.Direction.CW);return q;}
    /** Rectangular homescreen widget background with its own uncluttered clock area on the right. */
    public void drawWidget(Canvas c,int w,int h,int style,long now,int battery){
        c.drawColor(Color.TRANSPARENT);
        float rad=Math.min(h*.40f,w*.25f); // left-side movement fits the smallest default widget.
        fill(Color.rgb(6,12,21));RectF box=new RectF(3,3,w-3,h-3);
        c.drawRoundRect(box,22,22,p);
        stroke(alpha(180,style==2?BLUE:METAL),1.5f);c.drawRoundRect(box,22,22,p);
        float cx=rad+17,cy=h*.50f;
        drawFace(c,cx,cy,rad,style,now,(now/1000.0)*.05f,0,0,Float.NaN,battery,false);
        float panelX=w*.72f;
        text(c,"UNIVERSELAB",panelX,h*.16f,Math.min(19,h*.10f),BRIGHT,true);
        text(c,style==0?"TITAN":style==1?"COMPASS":"HOLO 6D",panelX,h*.26f,Math.min(16,h*.077f),
                style==2?BLUE:Color.rgb(187,202,217),true);
        // Clocks and battery are drawn separately by RemoteViews over this image.
    }
}
