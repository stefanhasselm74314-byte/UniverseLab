(()=>{
  'use strict';

  if(window.__UNIVERSELAB_MODEL_PICKER_V1__)return;
  window.__UNIVERSELAB_MODEL_PICKER_V1__=true;

  const SELECT_ID='ul-model-preset';
  const LAYER_ID='ul-model-picker-layer';
  const TRIGGER_CLASS='ul-model-picker-trigger';
  const modelApi=()=>window.UniverseLabModel;
  let trigger=null;
  let layer=null;
  let previousFocus=null;
  let previousOverflow='';

  const number=(value,digits=3)=>Number(value).toLocaleString('de-DE',{
    minimumFractionDigits:digits,
    maximumFractionDigits:digits
  });

  const activePreset=()=>{
    const state=modelApi()?.get?.()||{};
    const presets=modelApi()?.presets||{};
    return Object.prototype.hasOwnProperty.call(presets,state.preset)?state.preset:'custom';
  };

  const currentState=()=>modelApi()?.get?.()||{};

  const optionMeta=(id,preset)=>{
    const state=id==='custom'?currentState():preset;
    if(!state)return'';
    if(id==='custom'){
      return `Aktuelle Werte beibehalten · H₀ ${number(state.H0,1)} · Ωₘ ${number(state.Om)} · w ${number(state.w,2)}`;
    }
    return `H₀ ${number(state.H0,1)} · Ωₘ ${number(state.Om)} · ΩΛ ${number(state.Ol)} · w ${number(state.w,2)} · σ₈ ${number(state.s8)}`;
  };

  const pickerEntries=()=>{
    const presets=modelApi()?.presets||{};
    return [
      ['custom',{label:'Eigenes Modell'}],
      ...Object.entries(presets)
    ];
  };

  const focusable=()=>layer?[...layer.querySelectorAll('button:not([disabled])')]:[];

  const setOpen=open=>{
    if(!layer||!trigger)return;
    layer.hidden=!open;
    layer.setAttribute('aria-hidden',String(!open));
    trigger.setAttribute('aria-expanded',String(open));

    if(open){
      previousFocus=document.activeElement;
      previousOverflow=document.documentElement.style.overflow;
      document.documentElement.style.overflow='hidden';
      render();
      requestAnimationFrame(()=>{
        layer.querySelector('.ul-model-picker-option[aria-checked="true"]')?.focus()
          ||layer.querySelector('.ul-model-picker-option')?.focus();
      });
    }else{
      document.documentElement.style.overflow=previousOverflow;
      const target=previousFocus instanceof HTMLElement?previousFocus:trigger;
      target?.focus?.();
    }
  };

  const choose=id=>{
    const api=modelApi();
    if(!api)return;

    if(id==='custom'){
      const state=api.get();
      api.set({H0:state.H0,Om:state.Om,Ol:state.Ol,w:state.w,s8:state.s8},{
        label:'Eigenes Modell',
        source:'model-picker'
      });
    }else{
      api.applyPreset(id);
    }

    const select=document.getElementById(SELECT_ID);
    if(select){
      select.value=id;
      select.dispatchEvent(new Event('change',{bubbles:true}));
    }
    render();
    setOpen(false);
  };

  const render=()=>{
    if(!layer||!trigger)return;
    const state=currentState();
    const selected=activePreset();
    const label=state.label||'Eigenes Modell';
    const labelNode=trigger.querySelector('.ul-model-picker-trigger-label');
    if(labelNode)labelNode.textContent=label;
    trigger.title=`Aktuelles Modell: ${label}`;

    const list=layer.querySelector('.ul-model-picker-list');
    if(!list)return;
    list.replaceChildren();

    pickerEntries().forEach(([id,preset])=>{
      const button=document.createElement('button');
      button.type='button';
      button.className='ul-model-picker-option';
      button.dataset.preset=id;
      button.setAttribute('role','radio');
      button.setAttribute('aria-checked',String(id===selected));
      button.innerHTML=`
        <span class="ul-model-picker-option-copy">
          <span class="ul-model-picker-option-title"></span>
          <span class="ul-model-picker-option-meta"></span>
        </span>
        <span class="ul-model-picker-radio" aria-hidden="true"></span>
      `;
      button.querySelector('.ul-model-picker-option-title').textContent=preset.label;
      button.querySelector('.ul-model-picker-option-meta').textContent=optionMeta(id,preset);
      button.addEventListener('click',()=>choose(id));
      list.appendChild(button);
    });
  };

  const buildLayer=()=>{
    if(document.getElementById(LAYER_ID))return document.getElementById(LAYER_ID);
    const node=document.createElement('div');
    node.id=LAYER_ID;
    node.className='ul-model-picker-layer';
    node.hidden=true;
    node.setAttribute('aria-hidden','true');
    node.innerHTML=`
      <section class="ul-model-picker-dialog" role="dialog" aria-modal="true" aria-labelledby="ul-model-picker-title">
        <header class="ul-model-picker-head">
          <div class="ul-model-picker-head-copy">
            <span class="ul-model-picker-kicker">UniverseLab Observatory</span>
            <h2 class="ul-model-picker-title" id="ul-model-picker-title">Modell auswählen</h2>
          </div>
          <button type="button" class="ul-model-picker-close" aria-label="Modellauswahl schließen">×</button>
        </header>
        <div class="ul-model-picker-list" role="radiogroup" aria-label="Kosmologische Modell-Presets"></div>
        <div class="ul-model-picker-foot">Die Auswahl wird automatisch in Journey, Modelle und 3D-Flug übernommen. Manuelle Regleränderungen erzeugen wieder ein eigenes Modell.</div>
      </section>
    `;
    document.body.appendChild(node);
    node.querySelector('.ul-model-picker-close').addEventListener('click',()=>setOpen(false));
    node.addEventListener('click',event=>{if(event.target===node)setOpen(false);});
    return node;
  };

  const enhance=select=>{
    if(!select||select.dataset.ulModelPicker==='ready')return false;
    const bar=select.closest('.ul-presetbar');
    if(!bar)return false;

    select.dataset.ulModelPicker='ready';
    select.classList.add('ul-native-preset-hidden');
    select.setAttribute('aria-hidden','true');
    select.tabIndex=-1;

    trigger=document.createElement('button');
    trigger.type='button';
    trigger.className=TRIGGER_CLASS;
    trigger.setAttribute('aria-haspopup','dialog');
    trigger.setAttribute('aria-expanded','false');
    trigger.setAttribute('aria-controls',LAYER_ID);
    trigger.innerHTML=`<span class="ul-model-picker-trigger-label">Eigenes Modell</span><span class="ul-model-picker-trigger-icon" aria-hidden="true">⌄</span>`;
    bar.insertBefore(trigger,select);

    layer=buildLayer();
    trigger.addEventListener('click',()=>setOpen(true));
    render();
    return true;
  };

  const init=()=>{
    if(!/observatory\.html$/i.test(location.pathname))return;
    const select=document.getElementById(SELECT_ID);
    if(enhance(select))return;

    const observer=new MutationObserver(()=>{
      if(enhance(document.getElementById(SELECT_ID)))observer.disconnect();
    });
    observer.observe(document.documentElement,{subtree:true,childList:true});
    setTimeout(()=>observer.disconnect(),6000);
  };

  addEventListener('universelab:modelchange',()=>render());
  addEventListener('keydown',event=>{
    if(!layer||layer.hidden)return;
    if(event.key==='Escape'){
      event.preventDefault();
      setOpen(false);
      return;
    }
    if(event.key==='Tab'){
      const items=focusable();
      if(!items.length)return;
      const first=items[0];
      const last=items[items.length-1];
      if(event.shiftKey&&document.activeElement===first){
        event.preventDefault();
        last.focus();
      }else if(!event.shiftKey&&document.activeElement===last){
        event.preventDefault();
        first.focus();
      }
    }
  });

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
