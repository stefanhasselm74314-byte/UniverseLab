#!/usr/bin/env python3
"""Reproducible original drawables; install Pillow before running."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from math import sin,cos,pi
base=Path(__file__).resolve().parents[1]/'app/src/main/res/drawable'
base.mkdir(parents=True,exist_ok=True)
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def draw_icon(name,w,h,theme):
    im=Image.new('RGBA',(w,h),(0,0,0,0));d=ImageDraw.Draw(im)
    d.rounded_rectangle((4,4,w-4,h-4),radius=w//9,fill=(4,13,25,255),outline=(130,151,174,255),width=3)
    cx,cy,r=(w*.39,h*.50,min(w*.34,h*.43)) if w>h else (w*.5,h*.5,w*.38)
    palette=[(198,205,216),(226,178,100),(50,197,255)];metal=palette[theme]
    for rr in (r,r*.91,r*.64):d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=(*metal,240),width=max(2,w//115))
    for i in range(60):
        a=i*2*pi/60;r0=r*(.85 if i%5==0 else .91)
        d.line((cx+cos(a)*r0,cy+sin(a)*r0,cx+cos(a)*r*.97,cy+sin(a)*r*.97),fill=(218,229,243,198),width=max(1,w//280))
    for k in range(3):
        rx=r*(.58-.12*k);d.ellipse((cx-rx,cy-rx*.38,cx+rx,cy+rx*.38),outline=(*palette[(theme+k)%3],255),width=max(2,w//120))
    for gx,gy in [(-.38,-.28),(.38,-.27),(-.35,.31),(.33,.29)]:
        gr=r*.14;x=cx+r*gx;y=cy+r*gy
        d.ellipse((x-gr,y-gr,x+gr,y+gr),outline=(*metal,255),width=max(2,w//140))
        for i in range(6):
            a=i*pi/3;d.line((x,y,x+gr*cos(a),y+gr*sin(a)),fill=(*metal,160),width=max(1,w//170))
    d.ellipse((cx-4,cy-4,cx+4,cy+4),fill=(211,32,83,255))
    for idx,ch in enumerate(('N','E','S','W')):
        x=cx+cos((idx-1)*pi/2)*r*.76;y=cy+sin((idx-1)*pi/2)*r*.76
        ft=ImageFont.truetype(fontpath,max(9,int(w*.029)))
        d.text((x,y),ch,font=ft,anchor='mm',fill=(234,242,249,245))
    if w>h:
        ft=ImageFont.truetype(fontpath,int(w*.06));d.text((w*.73,h*.49),'10:08',font=ft,anchor='mm',fill=(238,247,254,255))
        ft2=ImageFont.truetype(fontpath,int(w*.024));d.text((w*.74,h*.64),['TITAN','COMPASS','HOLO 6D'][theme],font=ft2,anchor='mm',fill=(*metal,255))
    else:
        ft=ImageFont.truetype(fontpath,int(w*.065));d.text((cx,cy+r*.70),'6D',font=ft,anchor='mm',fill=(*metal,255))
    im.save(base/name)
draw_icon('app_icon.png',384,384,2)
for i,n in enumerate(['widget_preview_titan.png','widget_preview_compass.png','widget_preview_holo.png']):draw_icon(n,700,370,i)
print('Generated drawable previews and icon')
