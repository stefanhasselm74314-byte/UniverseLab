(()=>{
  'use strict';

  const init=()=>{
    const canvas=document.querySelector('#c.sim');
    const stage=document.querySelector('.stage');
    const toolbar=document.querySelector('.toolbar');
    if(!canvas||!stage||!toolbar)return;

    document.title='UniverseLab 0.6 · Emergenz';
    const badge=document.querySelector('header .badge');
    if(badge)badge.textContent='MVP 0.6';

    const style=document.createElement('style');
    style.id='ul-emergence-view-style';
    style.textContent=`
      #c.sim{touch-action:none;-ms-touch-action:none;overscroll-behavior:contain;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;cursor:crosshair;transform-origin:50% 50%;will-change:transform}
      #c.sim.ul-pan-mode{cursor:grab}#c.sim.ul-pan-mode:active{cursor:grabbing}
      .toolbar.ul-touch-toolbar{grid-template-columns:repeat(5,minmax(0,1fr))}
      .ul-fullscreen-button{white-space:nowrap}
      .ul-view-controls{position:absolute;z-index:4;right:10px;top:10px;display:flex;gap:5px;align-items:center;padding:4px;border:1px solid #303758;border-radius:12px;background:#070914dd;backdrop-filter:blur(12px);box-shadow:0 9px 28px #0008}
      .ul-view-controls button{width:auto;min-width:36px;min-height:36px;padding:6px 8px;border-radius:9px;font-size:13px;line-height:1;background:#11162a}
      .ul-view-controls .ul-view-mode{min-width:88px}
      .ul-view-zoom{min-width:48px;color:#b9c3e4;text-align:center;font-size:10px;font-variant-numeric:tabular-nums}
      .stage:fullscreen,.stage.ul-fallback-fullscreen{display:grid;place-items:center;width:100vw;height:100vh;max-width:none;border:0;border-radius:0;background:#000}
      .stage:fullscreen .sim,.stage.ul-fallback-fullscreen .sim{width:min(100vw,100vh);height:min(100vw,100vh);max-width:100vw;max-height:100vh;aspect-ratio:1;object-fit:contain}
      .stage:fullscreen .hud,.stage.ul-fallback-fullscreen .hud,.stage:fullscreen .ul-view-controls,.stage.ul-fallback-fullscreen .ul-view-controls{z-index:5}
      .stage.ul-fallback-fullscreen{position:fixed;z-index:20000;inset:0}
      body.ul-draw-lock{overflow:hidden!important;touch-action:none}
      @media(max-width:760px){
        .toolbar.ul-touch-toolbar{grid-template-columns:repeat(2,minmax(0,1fr))}.ul-fullscreen-button{grid-column:1/-1}
        .ul-view-controls{right:7px;top:7px;gap:3px;padding:3px}.ul-view-controls button{min-width:32px;min-height:32px;padding:5px;font-size:12px}.ul-view-controls .ul-view-mode{min-width:74px;font-size:10px}.ul-view-zoom{display:none}
      }
    `;
    document.head.appendChild(style);

    const originalPointerDown=canvas.onpointerdown;
    canvas.onpointerdown=null;

    const view={scale:1,x:0,y:0};
    const pointers=new Map();
    let drawPointer=null;
    let lastPoint=null;
    let navigationMode=false;
    let panStart=null;
    let pinchStart=null;
    let suppressUntilRelease=false;

    const clamp=(value,min,max)=>Math.max(min,Math.min(max,value));
    const stageCenter=()=>{
      const rect=stage.getBoundingClientRect();
      return{rect,cx:rect.left+rect.width/2,cy:rect.top+rect.height/2};
    };
    const constrainView=()=>{
      const rect=stage.getBoundingClientRect();
      const maxX=Math.max(0,rect.width*(view.scale-1)/2);
      const maxY=Math.max(0,rect.height*(view.scale-1)/2);
      view.x=clamp(view.x,-maxX,maxX);
      view.y=clamp(view.y,-maxY,maxY);
    };
    const applyView=()=>{
      constrainView();
      canvas.style.transform=`translate3d(${view.x}px,${view.y}px,0) scale(${view.scale})`;
      const zoom=document.querySelector('.ul-view-zoom');
      if(zoom)zoom.textContent=`${Math.round(view.scale*100)} %`;
    };
    const resetView=()=>{
      view.scale=1;view.x=0;view.y=0;applyView();
    };
    const zoomAt=(factor,clientX,clientY)=>{
      const {cx,cy}=stageCenter();
      const px=clientX-cx,py=clientY-cy;
      const worldX=(px-view.x)/view.scale;
      const worldY=(py-view.y)/view.scale;
      const next=clamp(view.scale*factor,1,5);
      view.x=px-worldX*next;
      view.y=py-worldY*next;
      view.scale=next;
      applyView();
    };
    const zoomCenter=factor=>{
      const {cx,cy}=stageCenter();
      zoomAt(factor,cx,cy);
    };

    const paintPoint=(x,y)=>{
      if(typeof originalPointerDown!=='function')return;
      originalPointerDown.call(canvas,{clientX:x,clientY:y});
    };
    const paintSegment=(x,y)=>{
      if(!lastPoint){paintPoint(x,y);lastPoint={x,y};return;}
      const dx=x-lastPoint.x,dy=y-lastPoint.y;
      const distance=Math.hypot(dx,dy);
      const rect=canvas.getBoundingClientRect();
      const stepSize=Math.max(2,Math.min(rect.width,rect.height)/220);
      const steps=Math.max(1,Math.ceil(distance/stepSize));
      for(let i=1;i<=steps;i++)paintPoint(lastPoint.x+dx*i/steps,lastPoint.y+dy*i/steps);
      lastPoint={x,y};
    };

    const pointerPair=()=>[...pointers.values()].slice(0,2);
    const beginPinch=()=>{
      const pair=pointerPair();
      if(pair.length<2)return;
      drawPointer=null;lastPoint=null;panStart=null;suppressUntilRelease=true;
      const [a,b]=pair;
      const midpoint={x:(a.x+b.x)/2,y:(a.y+b.y)/2};
      const distance=Math.max(1,Math.hypot(a.x-b.x,a.y-b.y));
      const {cx,cy}=stageCenter();
      const px=midpoint.x-cx,py=midpoint.y-cy;
      pinchStart={distance,scale:view.scale,worldX:(px-view.x)/view.scale,worldY:(py-view.y)/view.scale};
    };
    const updatePinch=()=>{
      const pair=pointerPair();
      if(pair.length<2||!pinchStart)return;
      const [a,b]=pair;
      const midpoint={x:(a.x+b.x)/2,y:(a.y+b.y)/2};
      const distance=Math.max(1,Math.hypot(a.x-b.x,a.y-b.y));
      const {cx,cy}=stageCenter();
      const px=midpoint.x-cx,py=midpoint.y-cy;
      const next=clamp(pinchStart.scale*distance/pinchStart.distance,1,5);
      view.scale=next;
      view.x=px-pinchStart.worldX*next;
      view.y=py-pinchStart.worldY*next;
      applyView();
    };

    const startPointer=event=>{
      if(event.pointerType==='mouse'&&event.button!==0)return;
      event.preventDefault();
      pointers.set(event.pointerId,{x:event.clientX,y:event.clientY});
      try{canvas.setPointerCapture(event.pointerId);}catch{}

      if(pointers.size>=2){beginPinch();return;}
      if(suppressUntilRelease)return;

      if(navigationMode){
        panStart={id:event.pointerId,x:event.clientX,y:event.clientY,viewX:view.x,viewY:view.y};
        return;
      }
      drawPointer=event.pointerId;
      lastPoint=null;
      paintSegment(event.clientX,event.clientY);
    };

    const movePointer=event=>{
      if(!pointers.has(event.pointerId))return;
      event.preventDefault();
      pointers.set(event.pointerId,{x:event.clientX,y:event.clientY});

      if(pointers.size>=2){updatePinch();return;}
      if(suppressUntilRelease)return;

      if(navigationMode&&panStart?.id===event.pointerId){
        view.x=panStart.viewX+event.clientX-panStart.x;
        view.y=panStart.viewY+event.clientY-panStart.y;
        applyView();
        return;
      }
      if(drawPointer!==event.pointerId)return;
      const events=typeof event.getCoalescedEvents==='function'?event.getCoalescedEvents():[event];
      for(const point of events)paintSegment(point.clientX,point.clientY);
    };

    const stopPointer=event=>{
      if(!pointers.has(event.pointerId))return;
      event.preventDefault();
      pointers.delete(event.pointerId);
      if(drawPointer===event.pointerId){drawPointer=null;lastPoint=null;}
      if(panStart?.id===event.pointerId)panStart=null;
      pinchStart=null;
      try{canvas.releasePointerCapture(event.pointerId);}catch{}
      if(pointers.size===0)suppressUntilRelease=false;
    };

    canvas.addEventListener('pointerdown',startPointer,{passive:false});
    canvas.addEventListener('pointermove',movePointer,{passive:false});
    canvas.addEventListener('pointerup',stopPointer,{passive:false});
    canvas.addEventListener('pointercancel',stopPointer,{passive:false});
    canvas.addEventListener('lostpointercapture',event=>{
      pointers.delete(event.pointerId);drawPointer=null;lastPoint=null;panStart=null;pinchStart=null;
      if(pointers.size===0)suppressUntilRelease=false;
    });
    canvas.addEventListener('contextmenu',event=>event.preventDefault());
    canvas.addEventListener('wheel',event=>{
      event.preventDefault();
      zoomAt(event.deltaY<0?1.16:1/1.16,event.clientX,event.clientY);
    },{passive:false});

    const controls=document.createElement('div');
    controls.className='ul-view-controls';
    controls.setAttribute('aria-label','Ansichtssteuerung');
    controls.innerHTML='<button type="button" class="ul-view-mode" aria-pressed="false">✎ Zeichnen</button><button type="button" class="ul-view-out" aria-label="Verkleinern">−</button><span class="ul-view-zoom">100 %</span><button type="button" class="ul-view-in" aria-label="Vergrößern">+</button><button type="button" class="ul-view-reset" aria-label="Ansicht zentrieren">◎</button>';
    stage.appendChild(controls);

    const modeButton=controls.querySelector('.ul-view-mode');
    const setNavigationMode=active=>{
      navigationMode=Boolean(active);
      canvas.classList.toggle('ul-pan-mode',navigationMode);
      modeButton.textContent=navigationMode?'✋ Ansicht':'✎ Zeichnen';
      modeButton.setAttribute('aria-pressed',String(navigationMode));
      drawPointer=null;lastPoint=null;panStart=null;
    };
    modeButton.addEventListener('click',()=>setNavigationMode(!navigationMode));
    controls.querySelector('.ul-view-out').addEventListener('click',()=>zoomCenter(1/1.25));
    controls.querySelector('.ul-view-in').addEventListener('click',()=>zoomCenter(1.25));
    controls.querySelector('.ul-view-reset').addEventListener('click',resetView);

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
      requestAnimationFrame(applyView);
    };
    const leaveFullscreen=async()=>{
      if(isNativeFullscreen())try{await document.exitFullscreen();}catch{}
      stage.classList.remove('ul-fallback-fullscreen');
      updateFullscreenButton();
    };
    const enterFullscreen=async()=>{
      if(stage.requestFullscreen){
        try{await stage.requestFullscreen({navigationUI:'hide'});updateFullscreenButton();return;}catch{}
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
      if(event.key==='0')resetView();
      if(event.key==='+'||event.key==='=')zoomCenter(1.25);
      if(event.key==='-')zoomCenter(1/1.25);
      if(event.key.toLowerCase()==='v')setNavigationMode(!navigationMode);
    });
    addEventListener('resize',()=>requestAnimationFrame(applyView));

    applyView();
    updateFullscreenButton();
  };

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
