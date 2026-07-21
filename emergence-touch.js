(()=>{
  'use strict';

  const init=()=>{
    const canvas=document.querySelector('#c.sim');
    const stage=document.querySelector('.stage');
    const toolbar=document.querySelector('.toolbar');
    if(!canvas||!stage||!toolbar)return;

    const style=document.createElement('style');
    style.textContent=`
      #c.sim{touch-action:none;-ms-touch-action:none;overscroll-behavior:contain;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;cursor:crosshair}
      .toolbar.ul-touch-toolbar{grid-template-columns:repeat(5,minmax(0,1fr))}
      .ul-fullscreen-button{white-space:nowrap}
      .stage:fullscreen,.stage.ul-fallback-fullscreen{display:grid;place-items:center;width:100vw;height:100vh;max-width:none;border:0;border-radius:0;background:#000}
      .stage:fullscreen .sim,.stage.ul-fallback-fullscreen .sim{width:min(100vw,100vh);height:min(100vw,100vh);max-width:100vw;max-height:100vh;aspect-ratio:1;object-fit:contain}
      .stage:fullscreen .hud,.stage.ul-fallback-fullscreen .hud{z-index:2}
      .stage.ul-fallback-fullscreen{position:fixed;z-index:20000;inset:0}
      body.ul-draw-lock{overflow:hidden!important;touch-action:none}
      @media(max-width:760px){.toolbar.ul-touch-toolbar{grid-template-columns:repeat(2,minmax(0,1fr))}.ul-fullscreen-button{grid-column:1/-1}}
    `;
    document.head.appendChild(style);

    const originalPointerDown=canvas.onpointerdown;
    canvas.onpointerdown=null;

    let activePointer=null;
    let lastPoint=null;

    const paintPoint=(x,y)=>{
      if(typeof originalPointerDown!=='function')return;
      originalPointerDown.call(canvas,{clientX:x,clientY:y});
    };

    const paintSegment=(x,y)=>{
      if(!lastPoint){paintPoint(x,y);lastPoint={x,y};return;}
      const dx=x-lastPoint.x;
      const dy=y-lastPoint.y;
      const distance=Math.hypot(dx,dy);
      const rect=canvas.getBoundingClientRect();
      const stepSize=Math.max(2,Math.min(rect.width,rect.height)/220);
      const steps=Math.max(1,Math.ceil(distance/stepSize));
      for(let i=1;i<=steps;i++){
        paintPoint(lastPoint.x+dx*i/steps,lastPoint.y+dy*i/steps);
      }
      lastPoint={x,y};
    };

    const startDrawing=event=>{
      if(event.pointerType==='mouse'&&event.button!==0)return;
      event.preventDefault();
      activePointer=event.pointerId;
      lastPoint=null;
      try{canvas.setPointerCapture(event.pointerId);}catch{}
      paintSegment(event.clientX,event.clientY);
    };

    const continueDrawing=event=>{
      if(activePointer!==event.pointerId)return;
      event.preventDefault();
      const events=typeof event.getCoalescedEvents==='function'?event.getCoalescedEvents():[event];
      for(const point of events)paintSegment(point.clientX,point.clientY);
    };

    const stopDrawing=event=>{
      if(activePointer!==event.pointerId)return;
      event.preventDefault();
      activePointer=null;
      lastPoint=null;
      try{canvas.releasePointerCapture(event.pointerId);}catch{}
    };

    canvas.addEventListener('pointerdown',startDrawing,{passive:false});
    canvas.addEventListener('pointermove',continueDrawing,{passive:false});
    canvas.addEventListener('pointerup',stopDrawing,{passive:false});
    canvas.addEventListener('pointercancel',stopDrawing,{passive:false});
    canvas.addEventListener('lostpointercapture',()=>{activePointer=null;lastPoint=null;});
    canvas.addEventListener('contextmenu',event=>event.preventDefault());

    toolbar.classList.add('ul-touch-toolbar');
    const fullscreenButton=document.createElement('button');
    fullscreenButton.type='button';
    fullscreenButton.className='ul-fullscreen-button';
    fullscreenButton.textContent='⛶ Vollbild zeichnen';
    fullscreenButton.setAttribute('aria-label','Zeichenfläche im Vollbild öffnen');
    toolbar.appendChild(fullscreenButton);

    const isFallbackFullscreen=()=>stage.classList.contains('ul-fallback-fullscreen');
    const isNativeFullscreen=()=>document.fullscreenElement===stage;

    const updateFullscreenButton=()=>{
      const active=isNativeFullscreen()||isFallbackFullscreen();
      fullscreenButton.textContent=active?'✕ Vollbild verlassen':'⛶ Vollbild zeichnen';
      fullscreenButton.setAttribute('aria-pressed',String(active));
      document.body.classList.toggle('ul-draw-lock',active);
    };

    const leaveFullscreen=async()=>{
      if(isNativeFullscreen()){
        try{await document.exitFullscreen();}catch{}
      }
      stage.classList.remove('ul-fallback-fullscreen');
      updateFullscreenButton();
    };

    const enterFullscreen=async()=>{
      if(stage.requestFullscreen){
        try{
          await stage.requestFullscreen({navigationUI:'hide'});
          updateFullscreenButton();
          return;
        }catch{}
      }
      stage.classList.add('ul-fallback-fullscreen');
      updateFullscreenButton();
    };

    fullscreenButton.addEventListener('click',()=>{
      if(isNativeFullscreen()||isFallbackFullscreen())leaveFullscreen();
      else enterFullscreen();
    });

    document.addEventListener('fullscreenchange',updateFullscreenButton);
    document.addEventListener('keydown',event=>{
      if(event.key==='Escape'&&isFallbackFullscreen())leaveFullscreen();
    });

    updateFullscreenButton();
  };

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
