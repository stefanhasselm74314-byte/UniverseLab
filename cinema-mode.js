(()=>{
  'use strict';

  if(window.__UNIVERSELAB_CINEMA__||!/universe3d\.html$/i.test(location.pathname))return;
  window.__UNIVERSELAB_CINEMA__=true;

  const init=()=>{
    const hud=document.querySelector('.hud');
    const buttons=document.querySelector('.buttons');
    const epochOutput=document.querySelector('#epoch');
    const timeSlider=document.querySelector('#time');
    const canvas=document.querySelector('#view');
    if(!hud||!buttons||!epochOutput)return;

    document.title='UniverseLab 0.8.5 · 3D Cosmic Flight';
    const badge=document.querySelector('.badge');
    if(badge)badge.textContent='Alpha 0.8.5';

    const style=document.createElement('style');
    style.id='ul-cinema-style';
    style.textContent=`
      .buttons{grid-template-columns:repeat(5,minmax(0,1fr))!important}
      .hud,.ul-shell{transition:opacity .22s ease,transform .22s ease}
      .ul-cinema-tools,.ul-cinema-epoch{display:none;position:fixed;z-index:10005;pointer-events:auto}
      .ul-cinema-tools{right:max(12px,env(safe-area-inset-right));bottom:max(12px,env(safe-area-inset-bottom));flex-direction:column;align-items:stretch;gap:7px}
      .ul-cinema-tools button{min-height:40px;padding:8px 11px;border:1px solid #3a456e;border-radius:12px;background:#0a0f20e8;color:#f4f6ff;font:750 11px system-ui;backdrop-filter:blur(12px);box-shadow:0 12px 34px #0008;opacity:.78}
      .ul-cinema-tools button:hover,.ul-cinema-tools button:focus-visible{opacity:1;border-color:#8d7cff}
      .ul-cinema-tools .ul-cinema-leave{font-size:10px;color:#b8c1df;background:#080c18d9}
      .ul-cinema-epoch{left:50%;top:max(12px,env(safe-area-inset-top));transform:translateX(-50%);align-items:center;gap:7px;padding:7px 11px;border:1px solid #334066;border-radius:999px;background:#080d1bcc;color:#dfe4ff;font:800 11px system-ui;backdrop-filter:blur(12px);box-shadow:0 10px 30px #0007}
      .ul-cinema-epoch::before{content:'✦';color:#78e1b8}
      body.ul-cinema{padding-top:0!important}
      body.ul-cinema .hud{opacity:0;pointer-events:none}
      body.ul-cinema.ul-cinema-controls .hud{opacity:1;pointer-events:none}
      body.ul-cinema .ul-shell{opacity:0;pointer-events:none;transform:translateY(-115%)}
      body.ul-cinema .ul-cinema-tools,body.ul-cinema .ul-cinema-epoch{display:flex}
      body.ul-cinema.ul-cinema-controls .ul-cinema-epoch{opacity:.35}
      body.ul-cinema .cross{opacity:.34}
      @media(max-width:720px){.buttons{grid-template-columns:repeat(2,minmax(0,1fr))!important}.ul-cinema-tools{right:10px;bottom:10px}}
    `;
    document.head.appendChild(style);

    const cinemaButton=document.createElement('button');
    cinemaButton.id='cinema';
    cinemaButton.type='button';
    cinemaButton.textContent='Kino';
    cinemaButton.setAttribute('aria-pressed','false');
    const firstLink=buttons.querySelector('a');
    buttons.insertBefore(cinemaButton,firstLink||null);

    const epochChip=document.createElement('div');
    epochChip.className='ul-cinema-epoch';
    epochChip.setAttribute('aria-live','polite');
    epochChip.textContent=epochOutput.value||epochOutput.textContent||'Heute';
    document.body.appendChild(epochChip);

    const tools=document.createElement('div');
    tools.className='ul-cinema-tools';
    tools.innerHTML='<button type="button" class="ul-cinema-controls-toggle">Steuerung einblenden</button><button type="button" class="ul-cinema-leave">Kino beenden</button>';
    document.body.appendChild(tools);
    const controlsToggle=tools.querySelector('.ul-cinema-controls-toggle');
    const leaveButton=tools.querySelector('.ul-cinema-leave');

    let active=false;
    let controlsVisible=false;
    let savedScroll={x:0,y:0};

    const syncEpoch=()=>{
      epochChip.textContent=epochOutput.value||epochOutput.textContent||'Kosmische Reise';
    };
    timeSlider?.addEventListener('input',()=>requestAnimationFrame(syncEpoch),{passive:true});
    syncEpoch();

    const setControls=show=>{
      controlsVisible=Boolean(show)&&active;
      document.body.classList.toggle('ul-cinema-controls',controlsVisible);
      controlsToggle.textContent=controlsVisible?'Steuerung ausblenden':'Steuerung einblenden';
      cinemaButton.textContent=active?(controlsVisible?'HUD ausblenden':'HUD einblenden'):'Kino';
    };

    const applyState=next=>{
      active=Boolean(next);
      document.body.classList.toggle('ul-cinema',active);
      cinemaButton.setAttribute('aria-pressed',String(active));
      if(!active){
        controlsVisible=false;
        document.body.classList.remove('ul-cinema-controls');
        cinemaButton.textContent='Kino';
        controlsToggle.textContent='Steuerung einblenden';
      }else{
        setControls(false);
      }
    };

    const enterCinema=async()=>{
      savedScroll={x:scrollX,y:scrollY};
      applyState(true);
      if(!document.fullscreenElement&&document.documentElement.requestFullscreen){
        try{await document.documentElement.requestFullscreen({navigationUI:'hide'});}catch{}
      }
      if(screen.orientation?.lock){try{await screen.orientation.lock('landscape');}catch{}}
    };

    const leaveCinema=async()=>{
      applyState(false);
      if(screen.orientation?.unlock){try{screen.orientation.unlock();}catch{}}
      if(document.fullscreenElement&&document.exitFullscreen){
        try{await document.exitFullscreen();}catch{}
      }
      requestAnimationFrame(()=>scrollTo(savedScroll.x,savedScroll.y));
    };

    cinemaButton.addEventListener('click',event=>{
      event.preventDefault();
      if(!active)enterCinema();
      else setControls(!controlsVisible);
    });
    controlsToggle.addEventListener('click',event=>{
      event.preventDefault();
      setControls(!controlsVisible);
    });
    leaveButton.addEventListener('click',event=>{
      event.preventDefault();
      leaveCinema();
    });
    canvas?.addEventListener('dblclick',event=>{
      if(!active)return;
      event.preventDefault();
      setControls(!controlsVisible);
    });
    document.addEventListener('fullscreenchange',()=>{
      if(active&&!document.fullscreenElement){
        applyState(false);
        requestAnimationFrame(()=>scrollTo(savedScroll.x,savedScroll.y));
      }
    });
    addEventListener('keydown',event=>{
      const key=event.key.toLowerCase();
      if(key==='h'&&active){event.preventDefault();setControls(!controlsVisible);}
      if(key==='k'&&!event.ctrlKey&&!event.metaKey&&!event.altKey){
        event.preventDefault();
        active?leaveCinema():enterCinema();
      }
    });
  };

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
