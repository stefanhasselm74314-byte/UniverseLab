(()=>{
  'use strict';

  if(window.__UNIVERSELAB_CINEMA__||!/universe3d\.html$/i.test(location.pathname))return;
  window.__UNIVERSELAB_CINEMA__=true;

  const init=()=>{
    const hud=document.querySelector('.hud');
    const buttons=document.querySelector('.buttons');
    const epochOutput=document.querySelector('#epoch');
    const timeSlider=document.querySelector('#time');
    if(!hud||!buttons||!epochOutput)return;

    document.title='UniverseLab 0.8.4 · 3D Cosmic Flight';
    const badge=document.querySelector('.badge');
    if(badge)badge.textContent='Alpha 0.8.4';

    const style=document.createElement('style');
    style.id='ul-cinema-style';
    style.textContent=`
      .buttons{grid-template-columns:repeat(5,minmax(0,1fr))!important}
      .hud,.ul-shell{transition:opacity .24s ease,transform .24s ease}
      .ul-cinema-exit,.ul-cinema-epoch{display:none;position:fixed;z-index:10005;pointer-events:auto}
      .ul-cinema-exit{right:max(12px,env(safe-area-inset-right));bottom:max(12px,env(safe-area-inset-bottom));min-height:40px;padding:8px 11px;border:1px solid #3a456e;border-radius:12px;background:#0a0f20d9;color:#f4f6ff;font:750 11px system-ui;backdrop-filter:blur(12px);box-shadow:0 12px 34px #0008;opacity:.66}
      .ul-cinema-exit:hover,.ul-cinema-exit:focus-visible{opacity:1;border-color:#8d7cff}
      .ul-cinema-epoch{left:50%;top:max(12px,env(safe-area-inset-top));transform:translateX(-50%);align-items:center;gap:7px;padding:7px 11px;border:1px solid #334066;border-radius:999px;background:#080d1bcc;color:#dfe4ff;font:800 11px system-ui;backdrop-filter:blur(12px);box-shadow:0 10px 30px #0007}
      .ul-cinema-epoch::before{content:'✦';color:#78e1b8}
      body.ul-cinema{padding-top:0!important}
      body.ul-cinema .hud{opacity:0;pointer-events:none}
      body.ul-cinema .ul-shell{opacity:0;pointer-events:none;transform:translateY(-115%)}
      body.ul-cinema .ul-cinema-exit,body.ul-cinema .ul-cinema-epoch{display:flex}
      body.ul-cinema .cross{opacity:.34}
      @media(max-width:720px){.buttons{grid-template-columns:repeat(2,minmax(0,1fr))!important}}
    `;
    document.head.appendChild(style);

    const cinemaButton=document.createElement('button');
    cinemaButton.id='cinema';
    cinemaButton.type='button';
    cinemaButton.textContent='Kino';
    cinemaButton.setAttribute('aria-pressed','false');
    const secondLink=buttons.querySelector('a');
    buttons.insertBefore(cinemaButton,secondLink||null);

    const epochChip=document.createElement('div');
    epochChip.className='ul-cinema-epoch';
    epochChip.setAttribute('aria-live','polite');
    epochChip.textContent=epochOutput.value||epochOutput.textContent||'Heute';
    document.body.appendChild(epochChip);

    const exitButton=document.createElement('button');
    exitButton.type='button';
    exitButton.className='ul-cinema-exit';
    exitButton.textContent='Steuerung einblenden';
    exitButton.setAttribute('aria-label','Kino-Modus beenden');
    document.body.appendChild(exitButton);

    let active=false;

    const syncEpoch=()=>{
      epochChip.textContent=epochOutput.value||epochOutput.textContent||'Kosmische Reise';
    };
    timeSlider?.addEventListener('input',()=>requestAnimationFrame(syncEpoch),{passive:true});
    syncEpoch();

    const applyState=next=>{
      active=Boolean(next);
      document.body.classList.toggle('ul-cinema',active);
      cinemaButton.textContent=active?'Steuerung':'Kino';
      cinemaButton.setAttribute('aria-pressed',String(active));
    };

    const setCinema=async(next,manageFullscreen=true)=>{
      applyState(next);
      if(active){
        if(manageFullscreen&&!document.fullscreenElement&&document.documentElement.requestFullscreen){
          try{await document.documentElement.requestFullscreen({navigationUI:'hide'});}catch{}
        }
        if(screen.orientation?.lock){try{await screen.orientation.lock('landscape');}catch{}}
      }else{
        if(screen.orientation?.unlock){try{screen.orientation.unlock();}catch{}}
        if(manageFullscreen&&document.fullscreenElement&&document.exitFullscreen){
          try{await document.exitFullscreen();}catch{}
        }
      }
    };

    cinemaButton.addEventListener('click',()=>setCinema(true));
    exitButton.addEventListener('click',()=>setCinema(false));
    document.addEventListener('fullscreenchange',()=>{
      if(active&&!document.fullscreenElement)applyState(false);
    });
    addEventListener('keydown',event=>{
      if(event.key.toLowerCase()==='k'&&!event.ctrlKey&&!event.metaKey&&!event.altKey){
        event.preventDefault();
        setCinema(!active);
      }
    });
  };

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
