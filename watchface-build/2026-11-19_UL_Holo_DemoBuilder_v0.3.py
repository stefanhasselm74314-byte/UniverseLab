#!/usr/bin/env python3
"""Build a standalone Android-browser preview of Holo-6D parallax.

The demo runs without network requests. Slider/touch simulation always works;
real DeviceOrientation may require HTTPS/browser permissions and is optional.
"""

import base64
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRAWABLE = ROOT / "holoface/src/main/res/drawable"
DEST = ROOT / "UniverseLab_Holo_6D_Offline_v0.3.html"


HTML = r'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>UniverseLab Holo-6D · Interaktive Offline-Vorschau</title>
<style>
:root{color-scheme:dark;font-family:system-ui,-apple-system,sans-serif;background:#050b15;color:#e5f5ff}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;background:radial-gradient(ellipse at 50% 22%,#193754 0%,#0a1323 42%,#02050b 90%)}
.wrap{max-width:850px;margin:0 auto;padding:22px 16px 40px}
h1{font-size:clamp(22px,4vw,34px);margin:0;color:#e8f7ff;letter-spacing:.04em}
.kicker{font-size:12px;letter-spacing:.2em;color:#74d9ff;margin:2px 0 6px}
.note{color:#9dbad0;line-height:1.5;font-size:14px}
.stage-wrap{max-width:540px;margin:22px auto;position:relative}
.stage{width:100%;aspect-ratio:1;position:relative;overflow:hidden;isolation:isolate;border-radius:50%;border:2px solid #4a7891;box-shadow:0 0 0 9px #172330,0 0 0 13px #829eaf,0 17px 65px #000b,0 0 75px #21aaff29;background:#020714;touch-action:none}
.plate{position:absolute;inset:0;display:block;width:100%;height:100%;object-fit:contain;user-select:none;-webkit-user-drag:none;pointer-events:none}
.depth{position:absolute;inset:0;will-change:transform;pointer-events:none}
.depth .plate{height:100%;width:100%}
.mid img{position:absolute;width:66.6667%;height:66.6667%;top:24.6667%;left:16.6667%;object-fit:contain}
#gyro_still{display:none}
.overlay{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
.overlay text{font-family:system-ui,sans-serif;fill:#e6f7ff;font-weight:800;text-anchor:middle;paint-order:stroke}
.overlay .num{font-size:45px;letter-spacing:-1px}
.overlay .gauge{font-size:20px}
.overlay .steps{font-size:15px}
.badge{border:1px solid #287498;border-radius:100px;padding:4px 10px;display:inline-block;color:#73d5ff;font-size:12px;margin-top:12px}
.controls{border:1px solid #31526d;background:#0c1b2bec;border-radius:19px;padding:20px;margin-top:23px;box-shadow:inset 0 1px #ffffff13}
.control{display:grid;grid-template-columns:130px 1fr 50px;gap:10px;align-items:center;margin:14px 0}
.control label{font-size:14px;color:#bfdbec}
input[type=range]{width:100%;accent-color:#51cbff}
button{border:1px solid #4bafd7;border-radius:12px;background:#123855;color:#dcf5ff;padding:11px 14px;font-size:14px;cursor:pointer;font-weight:600}
.row{display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.aod #holo_void,.aod #holo_back,.aod #holo_front{opacity:0}
.aod #gyro_anim{display:none}
.aod #gyro_still{display:block}
.aod .stage{filter:brightness(.45)}
.hint{font-size:12px;color:#83a7bb}
@media(max-width:420px){.control{grid-template-columns:95px 1fr 36px}.wrap{padding:16px 12px 25px}}
</style></head>
<body>
<main class="wrap" id="app">
<div class="kicker">UNIVERSELAB / HYPERZEIT / WEAR OS</div>
<h1>Holo-6D Edition <span style="color:#58d3ff">v0.3</span></h1>
<p class="note">Dreischichtige 2.5D-Parallaxe mit bewegungsabhängigem Gyroskop. Auf dem Smartphone direkt mit dem Finger über der Uhr wischen oder die Neigung einstellen.</p>
<div class="stage-wrap">
<div class="stage" id="stage" aria-label="Holo-6D-Watchface mit drei Tiefenschichten">
  <img class="plate" alt="" src="__WATCH_BG__">
  <img id="holo_void" class="plate" alt="" src="__HOLO_VOID__">
  <div id="rear" class="depth"><img id="holo_back" class="plate" alt="" src="__HOLO_BACK__"></div>
  <div id="middle" class="depth mid">
    <img id="gyro_anim" alt="" src="__GYRO_ANIM__">
    <img id="gyro_still" alt="" src="__GYRO_STILL__">
  </div>
  <div id="front" class="depth"><img id="holo_front" class="plate" alt="" src="__HOLO_FRONT__"></div>
  <svg class="overlay" viewBox="0 0 450 450" aria-hidden="true">
    <text class="num" id="time" x="225" y="108">20:59</text>
    <text class="gauge" x="82" y="145">76%</text>
    <text class="steps" x="368" y="145">12846</text>
    <text class="gauge" x="82" y="324">72</text>
    <text style="font-size:17px" id="date" x="368" y="324">19.11</text>
  </svg>
</div></div>
<div class="controls">
  <div class="row"><button id="sensors">Bewegungssensor versuchen</button><button id="reset">Neigung zurücksetzen</button><label><input id="aod" type="checkbox"> AOD-Vorschau</label></div>
  <div class="control"><label for="tiltX">Neigung X</label><input type="range" id="tiltX" min="-40" max="40" value="0"><output id="valX">0°</output></div>
  <div class="control"><label for="tiltY">Neigung Y</label><input type="range" id="tiltY" min="-40" max="40" value="0"><output id="valY">0°</output></div>
  <p class="hint" id="status">Touch und Regler funktionieren ohne Sensorfreigabe. Nur Uhrzeit/Datum sind echte Browserwerte; Schrittzahl, Puls und Akku sind Musterwerte.</p>
</div>
<div class="badge">VISUELLE SIMULATION · KEIN OPTISCHES HOLOGRAMM</div>
<p class="note">Technische Vorlage für eine Galaxy Watch Ultra: Die reale Wear-OS-Fassung verwendet die WFF-v1-Gyro-Effekte auf drei separaten Grafikschichten. Der Browser simuliert die gleiche geometrische Verschiebung; die Sensorfunktion hängt von den Berechtigungen des Browsers ab.</p>
</main>
<script>
const app=document.getElementById('app'),stage=document.getElementById('stage');
const rangeX=document.getElementById('tiltX'),rangeY=document.getElementById('tiltY');
const clamp=v=>Math.max(-40,Math.min(40,Number(v)||0));
function render(x,y){
 x=clamp(x);y=clamp(y);
 rangeX.value=x;rangeY.value=y;
 document.getElementById('valX').textContent=Math.round(x)+'°';
 document.getElementById('valY').textContent=Math.round(y)+'°';
 const move=(id,coef)=>{
   const ox=coef*y/450*100,oy=coef*x/450*100;
   document.getElementById(id).style.transform=`translate(${ox}%,${oy}%)`;
 };
 move('rear',-.12);move('middle',.08);move('front',.20);
}
rangeX.addEventListener('input',()=>render(rangeX.value,rangeY.value));
rangeY.addEventListener('input',()=>render(rangeX.value,rangeY.value));
stage.addEventListener('pointermove',e=>{
 if(e.buttons!==1 && e.pointerType!=='touch')return;
 const r=stage.getBoundingClientRect();
 const tx=(e.clientY-r.top)/r.height*80-40;
 const ty=(e.clientX-r.left)/r.width*80-40;
 render(tx,ty);
});
document.getElementById('reset').onclick=()=>render(0,0);
document.getElementById('aod').onchange=e=>app.classList.toggle('aod',e.target.checked);
document.getElementById('sensors').onclick=async()=>{
 const status=document.getElementById('status');
 try{
   if(!window.DeviceOrientationEvent)throw Error('Kein Bewegungssensor verfügbar');
   if(typeof DeviceOrientationEvent.requestPermission==='function'){
     if(await DeviceOrientationEvent.requestPermission()!=='granted')throw Error('Sensorfreigabe abgelehnt');
   }
   window.addEventListener('deviceorientation',e=>render(e.beta,e.gamma));
   status.textContent='Sensoren aktiviert, sofern dein Browser Orientierungsdaten bereitstellt. Andernfalls Touch/Regler verwenden.';
 }catch(err){status.textContent=String(err.message)+' – Touch/Regler funktionieren weiterhin.'}
};
function updateClock(){
 const d=new Date(),pad=n=>String(n).padStart(2,'0');
 document.getElementById('time').textContent=pad(d.getHours())+':'+pad(d.getMinutes());
 document.getElementById('date').textContent=pad(d.getDate())+'.'+pad(d.getMonth()+1);
}
render(0,0);updateClock();setInterval(updateClock,15000);
</script></body></html>'''


def uri(file: str) -> str:
    mime = "image/webp" if file.endswith(".webp") else "image/png"
    return "data:" + mime + ";base64," + base64.b64encode(
        (DRAWABLE / file).read_bytes()).decode("ascii")


def run():
    src = HTML
    for token, file in {
        "__WATCH_BG__": "watch_bg.png",
        "__HOLO_VOID__": "holo_void.png",
        "__HOLO_BACK__": "holo_back.png",
        "__GYRO_ANIM__": "gyro_anim.webp",
        "__GYRO_STILL__": "gyro_still.png",
        "__HOLO_FRONT__": "holo_front.png",
    }.items():
        src = src.replace(token, uri(file))
    DEST.write_text(src, encoding="utf-8")
    print(f"Wrote offline 2.5D demo: {DEST} ({DEST.stat().st_size:,} bytes)")


if __name__ == "__main__":
    run()
