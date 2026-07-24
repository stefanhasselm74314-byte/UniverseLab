(()=>{
  'use strict';

  if(window.__UNIVERSELAB_EVENTS__)return;
  const page=(location.pathname.split('/').pop()||'').toLowerCase();
  if(page!=='journey.html'&&page!=='universe3d.html')return;
  window.__UNIVERSELAB_EVENTS__=true;

  const isJourney=page==='journey.html';
  const slider=document.querySelector(isJourney?'#timeline':'#time');
  if(!slider)return;

  const clamp=(value,min,max)=>Math.max(min,Math.min(max,value));
  const mapA=value=>{
    const x=Number(value)/1000;
    if(x<.82)return 10**(-8+8*x/.82);
    return 10**((x-.82)/.18*1.2);
  };
  const valueForA=a=>{
    const safe=Math.max(1e-8,Number(a)||1e-8);
    if(safe<=1)return clamp(820*(Math.log10(safe)+8)/8,0,820);
    return clamp(820+180*Math.log10(safe)/1.2,820,1000);
  };
  const params=()=>window.UniverseLabModel?.params?.()||{H0:67.4,Or:9.2e-5,Om:.315,Ol:.684908,Ok:0,w:-1};

  const E=(a,p)=>Math.sqrt(Math.max(1e-30,
    p.Or/a**4+p.Om/a**3+(p.Ok||0)/a**2+p.Ol*a**(-3*(1+(p.w??-1)))
  ));
  const ageAt=(a,p=params())=>{
    const low=Math.log(1e-10),high=Math.log(Math.max(1e-10,a));
    if(high<=low)return 0;
    const n=420,h=(high-low)/n;
    let sum=0;
    for(let i=0;i<=n;i++){
      const x=low+i*h,A=Math.exp(x),f=1/E(A,p);
      sum+=(i===0||i===n?1:i%2?4:2)*f;
    }
    return 9.778/(p.H0/100)*sum*h/3;
  };
  const formatAge=gyr=>{
    if(gyr<1e-7)return`${Math.max(1,Math.round(gyr*365.25*24*60))} Minuten`;
    if(gyr<1e-6)return`${Math.max(1,Math.round(gyr*1e9))} Jahre`;
    if(gyr<1e-3)return`${Math.round(gyr*1e6).toLocaleString('de-DE')} Tsd. Jahre`;
    if(gyr<1)return`${(gyr*1e3).toLocaleString('de-DE',{maximumFractionDigits:1})} Mio. Jahre`;
    return`${gyr.toLocaleString('de-DE',{maximumFractionDigits:2})} Mrd. Jahre`;
  };
  const redshift=a=>1/a-1;
  const formatRedshift=a=>{
    const z=redshift(a);
    if(z>1000)return`z ≈ ${z.toExponential(1).replace('.',',')}`;
    if(z>10)return`z ≈ ${Math.round(z).toLocaleString('de-DE')}`;
    return`z ≈ ${z.toLocaleString('de-DE',{maximumFractionDigits:2})}`;
  };

  const accelerationA=p=>{
    const q=a=>{
      const r=p.Or/a**4,m=p.Om/a**3,l=p.Ol*a**(-3*(1+(p.w??-1)));
      const sum=r+m+(p.Ok||0)/a**2+l;
      return sum?(.5*(2*r+m+(1+3*(p.w??-1))*l)/sum):NaN;
    };
    let previousA=1e-4,previousQ=q(previousA);
    for(let i=1;i<=260;i++){
      const a=10**(-4+i*(Math.log10(5)+4)/260),currentQ=q(a);
      if(Number.isFinite(previousQ)&&Number.isFinite(currentQ)&&previousQ*currentQ<=0){
        let lo=previousA,hi=a,loQ=previousQ;
        for(let j=0;j<55;j++){
          const mid=Math.sqrt(lo*hi),midQ=q(mid);
          if(loQ*midQ<=0)hi=mid;
          else{lo=mid;loQ=midQ;}
        }
        return Math.sqrt(lo*hi);
      }
      previousA=a;previousQ=currentQ;
    }
    return null;
  };

  const buildEvents=()=>{
    const p=params();
    const equality=clamp(p.Or/Math.max(p.Om,1e-9),1e-8,5);
    const acceleration=accelerationA(p);
    const events=[
      {id:'bbn',a:1e-8,name:'Nukleosynthese',short:'Erste Atomkerne',text:'In den ersten Minuten entstehen vor allem Wasserstoff-, Helium- und geringe Lithiumkerne.'},
      {id:'equality',a:equality,name:'Materie–Strahlung-Gleichheit',short:'Gleichheit',text:'Materie und Strahlung tragen gleich stark zur kosmischen Energiedichte bei.'},
      {id:'cmb',a:1/1090,name:'Rekombination und CMB',short:'CMB',text:'Elektronen binden sich an Atomkerne; das Universum wird für Licht transparent.'},
      {id:'stars',a:1/21,name:'Erste Sterne',short:'Erste Sterne',text:'Die ersten massereichen Sterne entzünden sich und beginnen das dunkle Zeitalter zu beenden.'},
      {id:'galaxies',a:1/11,name:'Frühe Galaxien',short:'Frühe Galaxien',text:'Sternsysteme wachsen zu frühen Galaxien und Protoclustern zusammen.'},
      {id:'reionization',a:1/8,name:'Reionisierung',short:'Reionisierung',text:'Ultraviolettes Licht früher Sterne und Galaxien ionisiert das intergalaktische Gas.'},
      {id:'solar',a:.71,name:'Entstehung des Sonnensystems',short:'Sonnensystem',text:'Rund 9,2 Milliarden Jahre nach dem Urknall entsteht unser Sonnensystem.'},
      {id:'today',a:1,name:'Heute',short:'Heute',text:'Das beobachtbare Universum ist ungefähr 13,8 Milliarden Jahre alt.'},
      {id:'future',a:5,name:'Ferne Zukunft',short:'Zukunft',text:'Bei anhaltender dunkler Energie entfernen sich nicht gebundene Strukturen zunehmend aus unserem Horizont.'}
    ];
    if(acceleration)events.push({id:'acceleration',a:acceleration,name:'Beginn der Beschleunigung',short:'Beschleunigung',text:'Die Expansion wechselt im aktuellen Modell von abgebremst zu beschleunigt.'});
    return events.sort((a,b)=>a.a-b.a);
  };

  const style=document.createElement('style');
  style.id='ul-cosmic-events-style';
  style.textContent=`
    .ul-events{margin:8px 0 5px;padding:7px 8px;border:1px solid #283252;border-radius:12px;background:#080c18b8;min-width:0}
    .ul-event-head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:2px;color:#aeb7d6;font:750 9px system-ui;text-transform:uppercase;letter-spacing:.06em}
    .ul-event-head span:last-child{font-weight:600;text-transform:none;letter-spacing:0;color:#7e89aa}
    .ul-event-track{position:relative;height:30px;margin:0 7px}
    .ul-event-track::before{content:'';position:absolute;left:0;right:0;top:14px;height:2px;border-radius:999px;background:linear-gradient(90deg,#6053d9,#8d7cff 68%,#79e3bc)}
    .ul-event-marker{position:absolute;z-index:1;left:var(--event-x);top:4px;width:22px!important;min-width:22px!important;height:22px!important;min-height:22px!important;padding:0!important;transform:translateX(-50%);border:2px solid #a9a1ff!important;border-radius:50%!important;background:#11172b!important;box-shadow:0 0 0 3px #080c18,0 0 12px #8d7cff44;touch-action:manipulation}
    .ul-event-marker::after{content:'';position:absolute;inset:5px;border-radius:50%;background:#8d7cff}
    .ul-event-marker.active{border-color:#79e3bc!important;box-shadow:0 0 0 3px #080c18,0 0 16px #79e3bc88}
    .ul-event-marker.active::after{background:#79e3bc}
    .ul-event-marker:focus-visible{outline:2px solid #fff;outline-offset:3px}
    .ul-event-detail{display:grid;grid-template-columns:30px minmax(0,1fr) 30px;align-items:center;gap:6px;min-height:42px}
    .ul-event-detail button{width:30px!important;min-width:30px!important;height:30px!important;min-height:30px!important;padding:0!important;border-radius:9px!important;background:#11172b!important;color:#fff!important;font-size:15px!important}
    .ul-event-copy{min-width:0;text-align:left}.ul-event-copy strong{display:block;color:#f4f6ff;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.ul-event-copy span{display:block;color:#9fa9c9;font-size:9.5px;line-height:1.35;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.ul-event-copy small{display:block;color:#7ce0bb;font-size:8.5px;margin-top:1px}
    .ul-events-journey{margin:8px 0 3px}.ul-events-journey .ul-event-copy span{white-space:normal}.ul-events-journey .ul-event-detail{min-height:50px}
    .ul-events-3d{margin:3px 0 6px;padding:5px 7px}.ul-events-3d .ul-event-head{display:none}.ul-events-3d .ul-event-track{height:25px}.ul-events-3d .ul-event-track::before{top:12px}.ul-events-3d .ul-event-marker{top:2px;width:20px!important;min-width:20px!important;height:20px!important;min-height:20px!important}.ul-events-3d .ul-event-marker::after{inset:5px}.ul-events-3d .ul-event-detail{min-height:32px}.ul-events-3d .ul-event-copy span{display:none}.ul-events-3d .ul-event-copy strong{font-size:10px}.ul-events-3d .ul-event-copy small{font-size:8px}
    @media(max-width:520px){.ul-events{padding-inline:6px}.ul-event-track{margin-inline:5px}.ul-event-marker{width:20px!important;min-width:20px!important;height:20px!important;min-height:20px!important}.ul-event-marker::after{inset:5px}.ul-event-copy span{display:none}.ul-event-detail{min-height:34px}}
  `;
  document.head.appendChild(style);

  const wrapper=document.createElement('section');
  wrapper.className=`ul-events ${isJourney?'ul-events-journey':'ul-events-3d'}`;
  wrapper.setAttribute('aria-label','Kosmische Ereignismarker');
  wrapper.innerHTML='<div class="ul-event-head"><span>Kosmische Ereignisse</span><span>Marker antippen</span></div><div class="ul-event-track"></div><div class="ul-event-detail"><button type="button" class="ul-event-prev" aria-label="Vorheriges Ereignis">‹</button><div class="ul-event-copy" aria-live="polite"><strong>–</strong><span>–</span><small>–</small></div><button type="button" class="ul-event-next" aria-label="Nächstes Ereignis">›</button></div>';

  if(isJourney){
    const scale=document.querySelector('.scale');
    (scale?.parentNode||slider.parentNode).insertBefore(wrapper,scale?.nextSibling||slider.nextSibling);
    document.title='UniverseLab 1.4 · Cosmic Journey';
    const badge=document.querySelector('header .badge');
    if(badge)badge.textContent='MVP 1.4';
  }else{
    const row=slider.closest('.row');
    row?.parentNode.insertBefore(wrapper,row.nextSibling);
    document.title='UniverseLab 0.8.6 · 3D Cosmic Flight';
    const badge=document.querySelector('.badge');
    if(badge)badge.textContent='Alpha 0.8.6';
  }

  let events=[];
  let selectedIndex=0;
  const track=wrapper.querySelector('.ul-event-track');
  const copy=wrapper.querySelector('.ul-event-copy');

  const showEvent=index=>{
    if(!events.length)return;
    selectedIndex=(index+events.length)%events.length;
    const event=events[selectedIndex];
    copy.querySelector('strong').textContent=event.name;
    copy.querySelector('span').textContent=event.text;
    copy.querySelector('small').textContent=`${formatAge(ageAt(event.a))} · ${formatRedshift(event.a)}`;
    track.querySelectorAll('.ul-event-marker').forEach((marker,i)=>marker.classList.toggle('active',i===selectedIndex));
  };
  const jumpTo=index=>{
    showEvent(index);
    slider.value=String(Math.round(valueForA(events[selectedIndex].a)));
    slider.dispatchEvent(new Event('input',{bubbles:true}));
    slider.dispatchEvent(new Event('change',{bubbles:true}));
  };
  const nearestIndex=()=>{
    const current=Number(slider.value);
    let best=0,distance=Infinity;
    events.forEach((event,index)=>{
      const d=Math.abs(valueForA(event.a)-current);
      if(d<distance){distance=d;best=index;}
    });
    return best;
  };
  const syncFromSlider=()=>showEvent(nearestIndex());

  const render=()=>{
    events=buildEvents();
    track.replaceChildren();
    events.forEach((event,index)=>{
      const marker=document.createElement('button');
      marker.type='button';
      marker.className='ul-event-marker';
      marker.style.setProperty('--event-x',`${valueForA(event.a)/10}%`);
      marker.title=event.name;
      marker.setAttribute('aria-label',`${event.name}: ${formatAge(ageAt(event.a))}, ${formatRedshift(event.a)}`);
      marker.addEventListener('click',()=>jumpTo(index));
      track.appendChild(marker);
    });
    syncFromSlider();
  };

  wrapper.querySelector('.ul-event-prev').addEventListener('click',()=>jumpTo(selectedIndex-1));
  wrapper.querySelector('.ul-event-next').addEventListener('click',()=>jumpTo(selectedIndex+1));
  slider.addEventListener('input',syncFromSlider,{passive:true});
  addEventListener('universelab:modelchange',render);
  render();
})();
