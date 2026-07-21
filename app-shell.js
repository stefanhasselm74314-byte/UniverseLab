(()=>{
  'use strict';

  if(window.__UNIVERSELAB_SHELL__)return;
  window.__UNIVERSELAB_SHELL__=true;

  const init=()=>{
    const rawPath=(location.pathname.split('/').pop()||'index.html').toLowerCase();
    const pageKey=rawPath==='index.html'||rawPath==='portal.html'
      ?'portal'
      :rawPath==='emergence.html'
        ?'emergence'
        :rawPath.replace('.html','');

    if(rawPath==='portal.html')history.replaceState(history.state,'','./');

    document.querySelectorAll(
      'a[href="./index.html?lab=1"],a[href="index.html?lab=1"],a[href="./index.html"][data-emergence]'
    ).forEach(link=>{link.href='./emergence.html';});

    const pages=[
      ['./','⌂','Portal','portal'],
      ['./emergence.html','▦','UniverseLab','emergence'],
      ['./journey.html','◉','Journey','journey'],
      ['./observatory.html','⌁','Observatory','observatory'],
      ['./compare.html','≋','Modelle','compare'],
      ['./hyperlab.html','◇','HyperLab','hyperlab'],
      ['./universe3d.html','✦','3D-Flug','universe3d'],
      ['./validation.html','✓','Validierung','validation'],
      ['./about.html','◎','Über uns','about']
    ];

    const currentPage=pages.find(([, , ,key])=>key===pageKey)||['./','•','UniverseLab','portal'];
    const currentIcon=currentPage[1];
    const currentLabel=currentPage[2];

    const statuses={
      hyperlab:['#ff7894','Spekulatives Modell'],
      validation:['#70dfb3','Interner Test'],
      emergence:['#ff9b62','Simulation / ΛCDM'],
      about:['#8d7cff','Projektinformation']
    };
    const status=statuses[pageKey]||['#70dfb3','ΛCDM / Analyse'];

    document.documentElement.classList.add('ul-shell-ready');

    const style=document.createElement('style');
    style.id='ul-shell-style';
    style.textContent=`
      :root{--ul-shell-h:50px;--ul-accent:#8d7cff}
      body{padding-top:var(--ul-shell-h)!important}
      .topnav,body>.back,main>.back{display:none!important}
      .ul-skip{position:fixed;z-index:10003;left:12px;top:-64px;padding:9px 12px;border-radius:9px;background:#fff;color:#111;text-decoration:none;font:700 12px system-ui;transition:top .15s}
      .ul-skip:focus{top:7px}
      .ul-shell{position:fixed;z-index:10000;inset:0 0 auto;height:var(--ul-shell-h);display:flex;align-items:center;gap:6px;padding:5px max(10px,env(safe-area-inset-left));background:#080b17f2;border-bottom:1px solid #2c3558;box-shadow:0 6px 24px #0008;backdrop-filter:blur(18px);font:11.5px system-ui,-apple-system,"Segoe UI",sans-serif;color:#f4f6ff}
      .ul-menu,.ul-back{flex:0 0 auto;width:34px;height:34px;padding:0;border:1px solid #2c3558;border-radius:9px;background:#11172b;color:#fff;cursor:pointer}
      .ul-menu{display:none;font-size:18px}.ul-back{font-size:17px}
      .ul-menu:hover,.ul-back:hover,.ul-menu:focus-visible,.ul-back:focus-visible{border-color:var(--ul-accent);background:#171f39}
      .ul-brand{display:flex;align-items:center;gap:7px;min-width:max-content;font-weight:800;color:#fff;text-decoration:none}
      .ul-mark{display:grid;place-items:center;width:30px;height:30px;border-radius:9px;background:linear-gradient(135deg,#6551e8,#a179ff);box-shadow:0 0 20px #7e69ff55;font-size:11px}
      .ul-current{display:none;align-items:center;gap:7px;min-width:0;padding:6px 9px;border:1px solid color-mix(in srgb,var(--ul-accent) 62%,#2c3558);border-radius:9px;background:color-mix(in srgb,var(--ul-accent) 19%,#0d1326);box-shadow:inset 0 -2px 0 var(--ul-accent);font-weight:800;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
      .ul-current-icon{color:var(--ul-accent);font-size:14px}
      .ul-tabs{display:flex;gap:3px;overflow-x:auto;scrollbar-width:none;flex:1;scroll-behavior:smooth}
      .ul-tabs::-webkit-scrollbar{display:none}
      .ul-tabs a{position:relative;display:flex;align-items:center;gap:5px;min-width:max-content;padding:7px 8px;border:1px solid transparent;border-radius:9px;color:#aeb6d4;text-decoration:none;font-weight:700}
      .ul-tabs a:hover,.ul-tabs a:focus-visible{color:#fff;background:#131a31}
      .ul-tabs a.active{color:#fff;border-color:var(--ul-accent);background:color-mix(in srgb,var(--ul-accent) 21%,#11172b);box-shadow:inset 0 -3px 0 var(--ul-accent),0 0 15px color-mix(in srgb,var(--ul-accent) 18%,transparent)}
      .ul-tabs a.active span:first-child{color:var(--ul-accent)}
      .ul-state{display:flex;align-items:center;gap:6px;min-width:max-content;padding:6px 8px;border:1px solid #2c3558;border-radius:999px;background:#0d1326;color:#b8c1df}
      .ul-led{width:7px;height:7px;border-radius:50%;background:var(--ul-led);box-shadow:0 0 8px var(--ul-led)}
      .ul-overlay{display:none;position:fixed;z-index:10001;inset:0;background:#000a}
      .ul-overlay.open{display:block}
      .ul-drawer{position:absolute;left:0;top:0;bottom:0;width:min(310px,86vw);padding:calc(env(safe-area-inset-top) + 13px) 11px 18px;background:#090d1b;border-right:1px solid #30395c;box-shadow:20px 0 60px #000b;transform:translateX(-105%);transition:transform .2s ease}
      .ul-overlay.open .ul-drawer{transform:translateX(0)}
      .ul-drawer-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
      .ul-drawer-head strong{font-size:15px}.ul-close{width:36px;height:36px;border:1px solid #30395c;border-radius:9px;background:#11172b;color:#fff;font-size:19px}
      .ul-drawer a{display:flex;align-items:center;gap:9px;padding:10px 11px;border:1px solid transparent;border-radius:11px;color:#c3cae3;text-decoration:none;font-weight:750;margin:2px 0}
      .ul-drawer a.active{background:color-mix(in srgb,var(--ul-accent) 22%,#11172b);color:#fff;border-color:var(--ul-accent);box-shadow:inset 4px 0 0 var(--ul-accent)}
      .ul-drawer-status{margin-top:12px;padding:10px;border:1px solid #30395c;border-radius:11px;color:#aeb6d4;font-size:11px;line-height:1.45}

      @media(min-width:1000px){
        body>main{padding-top:clamp(18px,2.4vw,34px)!important}
        body>main.app{padding-top:14px!important}
        body>main>header{margin-bottom:8px!important}
        body>main>header h1{font-size:18px!important}
        .hero{min-height:min(570px,calc(100vh - 94px))!important;padding:clamp(28px,3vw,38px)!important}
        .hero h1{font-size:clamp(2.8rem,5.8vw,5.35rem)!important}
        .card,.module-card,.principle,.roadmap{padding:clamp(18px,2vw,23px)!important}
        .section-head{margin-top:58px!important}
        .status-section{margin-top:60px!important}
      }

      @media(max-width:980px){
        .ul-state span{display:none}.ul-state{padding:6px}
        .ul-tabs a{padding-inline:7px}
      }

      @media(max-width:1120px){
        :root{--ul-shell-h:50px}
        .ul-shell{gap:5px;padding-right:7px}
        .ul-menu,.ul-back{display:block}
        .ul-brand,.ul-tabs{display:none}
        .ul-current{display:flex;flex:1}
        .ul-state{margin-left:auto;flex:0 0 auto}
      }

      @media(max-width:390px){
        .ul-menu,.ul-back{width:33px;height:33px}
        .ul-current{padding:6px 8px}.ul-current-icon{display:none}.ul-state{display:none}
      }

      @media(prefers-reduced-motion:reduce){
        .ul-drawer,.ul-tabs,.ul-skip{transition:none;scroll-behavior:auto}
      }
    `;
    document.head.appendChild(style);

    const main=document.querySelector('main');
    if(main&&!main.id)main.id='main-content';

    const skip=document.createElement('a');
    skip.className='ul-skip';
    skip.href=main?'#main-content':'#';
    skip.textContent='Zum Inhalt springen';
    document.body.prepend(skip);

    const links=pages.map(([href,icon,label,key])=>
      `<a href="${href}" class="${pageKey===key?'active':''}" ${pageKey===key?'aria-current="page"':''}><span>${icon}</span><span>${label}</span></a>`
    ).join('');

    const nav=document.createElement('nav');
    nav.className='ul-shell';
    nav.setAttribute('aria-label','UniverseLab Hauptnavigation');
    nav.style.setProperty('--ul-led',status[0]);
    nav.style.setProperty('--ul-accent',status[0]);
    nav.innerHTML=`
      <button class="ul-menu" aria-label="Menü öffnen" aria-expanded="false">☰</button>
      <button class="ul-back" aria-label="Zurück" title="Zurück">←</button>
      <a class="ul-brand" href="./"><span class="ul-mark">UL</span><strong>UniverseLab</strong></a>
      <div class="ul-current" aria-label="Aktuelle Seite"><span class="ul-current-icon">${currentIcon}</span><span>${currentLabel}</span></div>
      <div class="ul-tabs">${links}</div>
      <div class="ul-state" title="${status[1]}"><i class="ul-led"></i><span>${status[1]}</span></div>
    `;
    document.body.prepend(nav);

    const goBack=()=>{
      let sameSiteReferrer=false;
      try{sameSiteReferrer=Boolean(document.referrer)&&new URL(document.referrer).origin===location.origin;}catch{}
      if(sameSiteReferrer&&history.length>1)history.back();
      else location.assign('./');
    };
    nav.querySelector('.ul-back').addEventListener('click',goBack);

    requestAnimationFrame(()=>{
      nav.querySelector('.ul-tabs a.active')?.scrollIntoView({block:'nearest',inline:'center'});
    });

    const overlay=document.createElement('div');
    overlay.className='ul-overlay';
    overlay.style.setProperty('--ul-accent',status[0]);
    overlay.setAttribute('aria-hidden','true');
    overlay.innerHTML=`
      <aside class="ul-drawer" aria-label="UniverseLab Seitenmenü" role="dialog" aria-modal="true">
        <div class="ul-drawer-head"><strong>UniverseLab</strong><button class="ul-close" aria-label="Menü schließen">×</button></div>
        ${links}
        <div class="ul-drawer-status"><b>Wissenschaftlicher Status</b><br>${status[1]}<br><br>Grün: etabliert oder intern geprüft<br>Orange: heuristisch oder modellabhängig<br>Rot: spekulativ</div>
      </aside>
    `;
    document.body.appendChild(overlay);

    const menu=nav.querySelector('.ul-menu');
    const close=overlay.querySelector('.ul-close');
    const focusables=()=>[...overlay.querySelectorAll('a,button')];
    let previousOverflow='';

    const setOpen=open=>{
      overlay.classList.toggle('open',open);
      overlay.setAttribute('aria-hidden',String(!open));
      menu.setAttribute('aria-expanded',String(open));
      if(open){
        previousOverflow=document.documentElement.style.overflow;
        document.documentElement.style.overflow='hidden';
        setTimeout(()=>close.focus(),0);
      }else{
        document.documentElement.style.overflow=previousOverflow;
        menu.focus();
      }
    };

    menu.addEventListener('click',()=>setOpen(true));
    close.addEventListener('click',()=>setOpen(false));
    overlay.addEventListener('click',event=>{if(event.target===overlay)setOpen(false);});

    addEventListener('keydown',event=>{
      if(event.key==='Escape'&&overlay.classList.contains('open'))setOpen(false);
      if(event.key==='Tab'&&overlay.classList.contains('open')){
        const items=focusables();
        const first=items[0];
        const last=items[items.length-1];
        if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
        else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
      }
      if(event.altKey&&event.key==='ArrowLeft'){
        event.preventDefault();
        goBack();
      }
    });
  };

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
