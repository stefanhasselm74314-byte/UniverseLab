(()=>{'use strict';
const card=document.querySelector('.live-card');
if(!card)return;
const values=[...card.querySelectorAll('.metric b')];
if(values.length<6)return;

const head=card.querySelector('.live-head');
const title=head?.querySelector('b');
const state=head?.querySelector('span');
if(state)state.textContent='● berechnet';
card.setAttribute('aria-label','Animierte ΛCDM-Referenzrechnung über verschiedene kosmische Epochen');
card.setAttribute('aria-live','off');

const style=document.createElement('style');
style.textContent=`.ul-live-track{height:4px;margin-top:11px;border-radius:999px;background:#1a2340;overflow:hidden}.ul-live-track i{display:block;height:100%;width:0;background:linear-gradient(90deg,#69c9ff,#8d7cff,#ff9c64);box-shadow:0 0 12px #8d7cff88}.ul-live-caption{display:flex;justify-content:space-between;gap:10px;margin-top:6px;color:#7f8bad;font-size:9px;text-transform:uppercase;letter-spacing:.06em}`;
document.head.appendChild(style);
const track=document.createElement('div');
track.className='ul-live-track';
track.innerHTML='<i></i>';
const caption=document.createElement('div');
caption.className='ul-live-caption';
caption.innerHTML='<span>frühes Universum</span><span>heute</span>';
card.append(track,caption);
const fill=track.firstElementChild;

const H0=67.4;
const Or=0.000092;
const Om=0.315;
const Ol=0.684908;
const Ok=1-Or-Om-Ol;
const minA=1e-3;
const maxA=1;
const duration=26000;
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
let started=performance.now();
let pausedAt=0;
let paused=reduced;

const decimal=(n,d=3)=>Number(n).toLocaleString('de-DE',{minimumFractionDigits:d,maximumFractionDigits:d});
const scientific=n=>n.toExponential(2).replace('.',',').replace('e+',' × 10^').replace('e-',' × 10^-');
const compact=(n,d=3)=>Math.abs(n)>=100000||Math.abs(n)<0.001&&n!==0?scientific(n):decimal(n,d);

function model(a){
  const r=Or/a**4;
  const m=Om/a**3;
  const k=Ok/a**2;
  const l=Ol;
  const e2=r+m+k+l;
  const fr=r/e2,fm=m/e2,fk=k/e2,fl=l/e2;
  const q=.5*(2*fr+fm-2*fl);
  const epoch=fr>=fm&&fr>=fl?'Strahlungsära':fm>=fl?'Materieära':'Vakuumära';
  return{H:H0*Math.sqrt(e2),fm,fl,q,epoch};
}

function render(u){
  const a=Math.exp(Math.log(minA)+(Math.log(maxA)-Math.log(minA))*u);
  const z=1/a-1;
  const x=model(a);
  values[0].textContent=compact(a,a<.01?4:3);
  values[1].textContent=compact(z,z>100?1:3);
  values[2].textContent=compact(x.H,x.H>1000?1:1);
  values[3].textContent=decimal(x.fm,3);
  values[4].textContent=decimal(x.fl,3);
  values[5].textContent=decimal(x.q,3);
  if(title)title.textContent=`ΛCDM-Referenz · ${x.epoch}`;
  fill.style.width=`${(u*100).toFixed(2)}%`;
  const panel=document.querySelector('.universe-panel');
  if(panel){
    panel.style.setProperty('--ul-era',String(u));
    panel.style.filter=`saturate(${.82+.38*u}) brightness(${.9+.12*u})`;
  }
}

function frame(now){
  if(!paused){
    const u=((now-started)%duration)/duration;
    render(u);
  }
  requestAnimationFrame(frame);
}

card.title=reduced?'Animation durch Systemeinstellung angehalten':'Klicken, um die ΛCDM-Vorschau anzuhalten oder fortzusetzen';
card.style.cursor='pointer';
card.tabIndex=0;
card.addEventListener('click',()=>{
  if(paused){
    started=performance.now()-pausedAt;
    paused=false;
    if(state)state.textContent='● berechnet';
  }else{
    pausedAt=(performance.now()-started)%duration;
    paused=true;
    if(state)state.textContent='● pausiert';
  }
});
card.addEventListener('keydown',event=>{
  if(event.key==='Enter'||event.key===' '){event.preventDefault();card.click()}
});
document.addEventListener('visibilitychange',()=>{
  if(document.hidden&&!paused){pausedAt=(performance.now()-started)%duration;paused=true}
});

render(reduced?1:0);
requestAnimationFrame(frame);
})();
