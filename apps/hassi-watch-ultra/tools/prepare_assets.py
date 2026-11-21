from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math
base=Path('apps/hassi-orbitalclock/app/src/main/res/drawable-nodpi')
out=Path('apps/hassi-watch-ultra')
S=720
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def vignette(im,strength):
    mask=Image.new('L',(S,S))
    m=mask.load()
    for y in range(S):
        for x in range(S):
            r=math.hypot((x-S/2)/(S/2),(y-S/2)/(S/2))
            f=1-strength*max(0,(r-.5)/.75)**2
            m[x,y]=int(max(0,min(1,f))*255)
    return Image.composite(im,Image.new('RGB',(S,S),'black'),mask)
def round_crop(im):
    mask=Image.new('L',(S,S))
    d=ImageDraw.Draw(mask)
    d.ellipse((2,2,S-2,S-2),fill=255)
    return Image.composite(im,Image.new('RGB',(S,S),'#03060a'),mask.filter(ImageFilter.GaussianBlur(1.5)))
def save_face(name,img):
    target=out/name/'src/main/res/drawable'
    target.mkdir(parents=True,exist_ok=True)
    img.resize((480,480),Image.Resampling.LANCZOS).save(target/'background.png',optimize=True)
    p=img.copy();draw=ImageDraw.Draw(p)
    if name=='watchface-dial':
        f=ImageFont.truetype(font,70)
        for t,(x,y) in [('09',(165,192)),('43',(540,192))]:
            bb=draw.textbbox((0,0),t,font=f)
            draw.text((x-(bb[2]-bb[0])/2,y-(bb[3]-bb[1])/2-8),t,font=f,fill='#f3f8ff')
    else:
        f=ImageFont.truetype(font,90)
        bb=draw.textbbox((0,0),'09:43',font=f)
        draw.text(((S-(bb[2]-bb[0]))/2,575),'09:43',font=f,fill='#f3f8ff')
    p.resize((480,480),Image.Resampling.LANCZOS).save(target/'preview.png',optimize=True)
dial=Image.open(base/'orbital_dial.webp').convert('RGB').resize((S,S),Image.Resampling.LANCZOS)
save_face('watchface-dial',round_crop(vignette(dial,.35)))
src=Image.open(base/'orbital_tall.webp').convert('RGB')
station=src.crop((0,5,709,714)).resize((S,S),Image.Resampling.LANCZOS)
station=vignette(station,.50).convert('RGBA')
veil=Image.new('RGBA',(S,S));p=veil.load()
for y in range(int(S*.67),S):
    a=int(180*(max(0.0,(y-S*.67)/(S*.33))**1.12))
    for x in range(S): p[x,y]=(2,6,14,max(0,min(255,a)))
station=Image.alpha_composite(station,veil).convert('RGB')
save_face('watchface-station',round_crop(station))
print('Watch artwork + previews generated')
