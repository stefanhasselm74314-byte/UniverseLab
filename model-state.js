(()=>{
  'use strict';

  if(window.UniverseLabModel)return;

  const KEY='universelab:model:v1';
  const OR=9.2e-5;
  const presets={
    planck:{label:'Planck-ähnlich',H0:67.4,Om:.315,Ol:.684908,w:-1,s8:.811},
    highH0:{label:'Hoher H₀-Wert',H0:73,Om:.30,Ol:.699908,w:-1,s8:.81},
    matter:{label:'Materiedominiert',H0:67.4,Om:.70,Ol:.299908,w:-1,s8:.90},
    darkenergy:{label:'Dunkle Energie',H0:67.4,Om:.20,Ol:.799908,w:-1,s8:.75},
    phantom:{label:'Phantomenergie',H0:70,Om:.30,Ol:.699908,w:-1.20,s8:.82},
    eds:{label:'Einstein–de Sitter',H0:67.4,Om:.999908,Ol:0,w:-1,s8:.811}
  };
  const defaults={...presets.planck,preset:'planck',updatedAt:Date.now()};
  let state=load();
  let syncing=false;

  function finite(value,fallback){
    const number=Number(value);
    return Number.isFinite(number)?number:fallback;
  }
  function clamp(value,min,max){return Math.max(min,Math.min(max,value));}
  function normalize(input={}){
    const next={
      H0:clamp(finite(input.H0,defaults.H0),40,100),
      Om:clamp(finite(input.Om,defaults.Om),0,1.5),
      Ol:clamp(finite(input.Ol,defaults.Ol),-.5,1.8),
      w:clamp(finite(input.w,defaults.w),-3,0),
      s8:clamp(finite(input.s8,defaults.s8),.1,2),
      preset:typeof input.preset==='string'?input.preset:'custom',
      label:typeof input.label==='string'&&input.label.trim()?input.label.trim():'Eigenes Modell',
      updatedAt:finite(input.updatedAt,Date.now())
    };
    return next;
  }
  function load(){
    try{
      const stored=JSON.parse(localStorage.getItem(KEY)||'null');
      return stored?normalize(stored):normalize(defaults);
    }catch{return normalize(defaults);}
  }
  function save(){
    try{localStorage.setItem(KEY,JSON.stringify(state));}catch{}
  }
  function detail(){return{...state,...params()};}
  function notify(){
    save();
    window.dispatchEvent(new CustomEvent('universelab:modelchange',{detail:detail()}));
    updateUI();
  }
  function params(){
    return{
      H0:state.H0,
      Om:state.Om,
      Ol:state.Ol,
      w:state.w,
      s8:state.s8,
      Or:OR,
      Ok:1-OR-state.Om-state.Ol
    };
  }
  function set(partial={},meta={}){
    const isPreset=Boolean(meta.preset&&presets[meta.preset]);
    const merged={...state,...partial};
    if(isPreset){
      merged.preset=meta.preset;
      merged.label=presets[meta.preset].label;
    }else if(meta.keepPreset!==true){
      merged.preset='custom';
      merged.label=meta.label||'Eigenes Modell';
    }
    merged.updatedAt=Date.now();
    state=normalize(merged);
    notify();
    return detail();
  }
  function applyPreset(id='planck'){
    const preset=presets[id]||presets.planck;
    return set(preset,{preset:presets[id]?id:'planck'});
  }
  function reset(){return applyPreset('planck');}
  function get(){return detail();}
  function label(){return state.label;}

  const inputMap={
    H0:['H0','h0'],
    Om:['Om','om'],
    Ol:['Ol','ol'],
    w:['w'],
    s8:['s8']
  };
  function controls(){
    const found={};
    for(const [key,ids] of Object.entries(inputMap)){
      for(const id of ids){
        const element=document.getElementById(id);
        if(element){found[key]=element;break;}
      }
    }
    return found;
  }
  function writeInputs(){
    const found=controls();
    syncing=true;
    for(const [key,element] of Object.entries(found)){
      element.value=String(state[key]);
      element.dispatchEvent(new Event('input',{bubbles:true}));
    }
    syncing=false;
    const select=document.getElementById('ul-model-preset');
    if(select)select.value=state.preset in presets?state.preset:'custom';
  }
  function readInputs(){
    if(syncing)return;
    const found=controls();
    const patch={};
    for(const [key,element] of Object.entries(found))patch[key]=Number(element.value);
    if(found.Om&&!found.Ol)patch.Ol=1-OR-patch.Om;
    if(Object.keys(patch).length)set(patch,{label:'Eigenes Modell'});
  }
  function bindInputs(){
    const found=controls();
    for(const element of Object.values(found))element.addEventListener('input',readInputs,{passive:true});
    const resetButton=document.getElementById('reset');
    if(resetButton)resetButton.addEventListener('click',()=>setTimeout(readInputs,0));
    writeInputs();
  }

  function addStyles(){
    if(document.getElementById('ul-model-style'))return;
    const style=document.createElement('style');
    style.id='ul-model-style';
    style.textContent=`
      .ul-model-chip{flex:0 0 auto;display:flex;align-items:center;gap:5px;min-height:30px;max-width:150px;padding:5px 8px;border:1px solid #46517e;border-radius:999px;background:#10162b;color:#e8ebff;font:750 10px system-ui;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:pointer}
      .ul-model-chip::before{content:'M';display:grid;place-items:center;width:17px;height:17px;border-radius:50%;background:#8d7cff;color:white;font-size:9px}
      .ul-model-pop{position:fixed;z-index:10002;top:56px;right:10px;width:min(310px,calc(100vw - 20px));padding:12px;border:1px solid #364166;border-radius:14px;background:#0a0f20f5;box-shadow:0 20px 60px #000b;backdrop-filter:blur(16px);color:#f4f6ff;font:12px system-ui}
      .ul-model-pop[hidden]{display:none}.ul-model-pop strong{display:block;font-size:14px;margin-bottom:8px}.ul-model-values{display:grid;grid-template-columns:repeat(2,1fr);gap:6px}.ul-model-values span{padding:7px;border:1px solid #293252;border-radius:9px;background:#090d1b;color:#b8c1df}.ul-model-pop a{display:block;margin-top:9px;padding:8px;border-radius:9px;background:#171d39;color:#fff;text-align:center;text-decoration:none;font-weight:750}
      .ul-presetbar{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:6px;align-items:center;margin:7px 0 6px}.ul-presetbar select{width:100%;min-height:34px;padding:6px 9px;border:1px solid #293252;border-radius:9px;background:#0a0f20;color:#f4f6ff;font:700 11px system-ui}.ul-preset-note{grid-column:1/-1;color:#9fa8c7;font-size:9.5px;line-height:1.35}
      @media(max-width:1120px){.ul-model-chip{max-width:105px;padding-inline:7px}.ul-model-chip::before{display:none}}
      @media(max-width:520px){.ul-model-chip{max-width:72px;font-size:9px}}
      @media(max-width:390px){.ul-model-chip{display:none}}
    `;
    document.head.appendChild(style);
  }
  function shortLabel(){
    if(state.preset==='planck')return'ΛCDM';
    if(state.preset==='custom')return'Eigenes Modell';
    return state.label;
  }
  function ensurePopover(){
    let pop=document.getElementById('ul-model-pop');
    if(pop)return pop;
    pop=document.createElement('aside');
    pop.id='ul-model-pop';
    pop.className='ul-model-pop';
    pop.hidden=true;
    document.body.appendChild(pop);
    document.addEventListener('click',event=>{
      if(!pop.hidden&&!pop.contains(event.target)&&!event.target.closest('.ul-model-chip'))pop.hidden=true;
    });
    addEventListener('keydown',event=>{if(event.key==='Escape')pop.hidden=true;});
    return pop;
  }
  function renderPopover(pop){
    const p=params();
    pop.innerHTML=`<strong>${state.label}</strong><div class="ul-model-values"><span>H₀ ${p.H0.toFixed(1)}</span><span>Ωₘ ${p.Om.toFixed(3)}</span><span>ΩΛ ${p.Ol.toFixed(3)}</span><span>w ${p.w.toFixed(2)}</span><span>σ₈ ${p.s8.toFixed(3)}</span><span>Ωₖ ${p.Ok.toExponential(1)}</span></div><a href="./observatory.html?v=model1">Im Observatory bearbeiten</a>`;
  }
  function attachChip(){
    const shell=document.querySelector('.ul-shell');
    if(!shell||document.querySelector('.ul-model-chip'))return false;
    const chip=document.createElement('button');
    chip.type='button';
    chip.className='ul-model-chip';
    chip.setAttribute('aria-label','Aktuelles kosmologisches Modell anzeigen');
    const stateNode=shell.querySelector('.ul-state');
    shell.insertBefore(chip,stateNode||null);
    const pop=ensurePopover();
    chip.addEventListener('click',()=>{renderPopover(pop);pop.hidden=!pop.hidden;});
    updateUI();
    return true;
  }
  function watchShell(){
    if(attachChip())return;
    const observer=new MutationObserver(()=>{if(attachChip())observer.disconnect();});
    observer.observe(document.documentElement,{subtree:true,childList:true});
    setTimeout(()=>observer.disconnect(),5000);
  }
  function injectPresetBar(){
    if(!/observatory\.html$/i.test(location.pathname)||document.getElementById('ul-model-preset'))return;
    const anchor=document.querySelector('.param-grid')||document.querySelector('.controls');
    if(!anchor)return;
    const bar=document.createElement('div');
    bar.className='ul-presetbar';
    const options=Object.entries(presets).map(([id,preset])=>`<option value="${id}">${preset.label}</option>`).join('');
    bar.innerHTML=`<select id="ul-model-preset" aria-label="Kosmologisches Preset"><option value="custom">Eigenes Modell</option>${options}</select><button type="button" id="ul-model-reset">Planck</button><div class="ul-preset-note">Änderungen werden automatisch in Journey, Modelle und 3D-Flug übernommen.</div>`;
    anchor.parentNode.insertBefore(bar,anchor);
    const select=bar.querySelector('select');
    select.value=state.preset in presets?state.preset:'custom';
    select.addEventListener('change',()=>{if(select.value!=='custom')applyPreset(select.value);});
    bar.querySelector('#ul-model-reset').addEventListener('click',()=>applyPreset('planck'));
  }
  function updateUI(){
    const chip=document.querySelector('.ul-model-chip');
    if(chip){chip.textContent=shortLabel();chip.title=state.label;}
    const pop=document.getElementById('ul-model-pop');
    if(pop&&!pop.hidden)renderPopover(pop);
    const select=document.getElementById('ul-model-preset');
    if(select)select.value=state.preset in presets?state.preset:'custom';
  }
  function init(){
    addStyles();
    bindInputs();
    injectPresetBar();
    watchShell();
    updateUI();
  }

  window.UniverseLabModel={get,params,set,applyPreset,reset,label,presets:{...presets}};
  addEventListener('universelab:modelchange',writeInputs);
  addEventListener('storage',event=>{
    if(event.key!==KEY)return;
    state=load();
    writeInputs();
    updateUI();
    window.dispatchEvent(new CustomEvent('universelab:modelchange',{detail:detail()}));
  });
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
