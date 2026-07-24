(()=>{
  'use strict';

  if(window.__UNIVERSELAB_SNAPSHOTS__)return;
  window.__UNIVERSELAB_SNAPSHOTS__=true;

  const KEY='universelab:snapshots:v1';
  const PENDING_KEY='universelab:snapshot:pending';
  const MODEL_KEY='universelab:model:v1';
  const MAX_SNAPSHOTS=12;
  let layer=null;
  let listNode=null;
  let triggerButton=null;

  const readSnapshots=()=>{
    try{
      const value=JSON.parse(localStorage.getItem(KEY)||'[]');
      return Array.isArray(value)?value:[];
    }catch{return[];}
  };
  const writeSnapshots=snapshots=>{
    try{localStorage.setItem(KEY,JSON.stringify(snapshots.slice(0,MAX_SNAPSHOTS)));}catch{}
    updateTrigger();
  };
  const uid=()=>`${Date.now().toString(36)}-${Math.random().toString(36).slice(2,8)}`;
  const pageName=()=>document.querySelector('.ul-current span:last-child')?.textContent?.trim()
    ||document.querySelector('h1')?.textContent?.trim()
    ||'UniverseLab';
  const modelState=()=>{
    try{
      if(window.UniverseLabModel?.get)return window.UniverseLabModel.get();
      return JSON.parse(localStorage.getItem(MODEL_KEY)||'null');
    }catch{return null;}
  };
  const currentPage=()=>`${location.pathname}${location.search.replace(/([?&])(snapshot|r)=[^&]*/g,'$1').replace(/[?&]$/,'')}`;

  const captureControls=()=>{
    const controls={};
    document.querySelectorAll('input[id],select[id],textarea[id]').forEach(element=>{
      const type=(element.type||'').toLowerCase();
      if(['button','submit','reset','file','password','hidden'].includes(type))return;
      controls[element.id]={
        tag:element.tagName.toLowerCase(),
        type,
        value:element.value,
        checked:'checked' in element?Boolean(element.checked):undefined
      };
    });
    return controls;
  };

  const captureStorage=()=>{
    const stored={};
    let total=0;
    try{
      for(let i=0;i<localStorage.length;i++){
        const key=localStorage.key(i);
        if(!key||key===KEY)continue;
        const value=localStorage.getItem(key);
        if(value==null||value.length>350000||total+value.length>1200000)continue;
        stored[key]=value;
        total+=value.length;
      }
    }catch{}
    return stored;
  };

  const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
  const captureSnapshot=async name=>{
    if(/emergence\.html$/i.test(location.pathname)){
      const save=document.querySelector('#save');
      if(save){save.click();await wait(40);}
    }
    return{
      version:1,
      id:uid(),
      name,
      createdAt:new Date().toISOString(),
      page:currentPage(),
      pageName:pageName(),
      model:modelState(),
      controls:captureControls(),
      storage:captureStorage()
    };
  };

  const defaultName=()=>{
    const count=readSnapshots().length+1;
    const model=modelState();
    const suffix=model?.label&&model.label!=='Eigenes Modell'?` · ${model.label}`:'';
    return`Experiment ${count}${suffix}`;
  };

  const saveCurrent=async()=>{
    const proposed=defaultName();
    const entered=window.prompt('Name für dieses Experiment:',proposed);
    if(entered===null)return;
    const name=entered.trim()||proposed;
    const snapshot=await captureSnapshot(name);
    const snapshots=readSnapshots();
    snapshots.unshift(snapshot);
    writeSnapshots(snapshots);
    renderList();
    showToast(`„${name}“ wurde gespeichert.`);
  };

  const restoreModel=model=>{
    if(!model)return;
    try{
      if(window.UniverseLabModel?.set){
        window.UniverseLabModel.set(model,{keepPreset:true,source:'snapshot'});
      }else{
        localStorage.setItem(MODEL_KEY,JSON.stringify(model));
      }
    }catch{}
  };

  const restoreStorage=storage=>{
    if(!storage||typeof storage!=='object')return;
    try{
      Object.entries(storage).forEach(([key,value])=>{
        if(key!==KEY&&typeof value==='string')localStorage.setItem(key,value);
      });
    }catch{}
  };

  const restoreControls=controls=>{
    if(!controls||typeof controls!=='object')return;
    Object.entries(controls).forEach(([id,saved])=>{
      const element=document.getElementById(id);
      if(!element||!saved)return;
      try{
        if(saved.checked!==undefined&&'checked' in element)element.checked=Boolean(saved.checked);
        if(saved.value!==undefined)element.value=String(saved.value);
        element.dispatchEvent(new Event('input',{bubbles:true}));
        element.dispatchEvent(new Event('change',{bubbles:true}));
      }catch{}
    });
  };

  const applySnapshot=async(snapshot,{shared=false}={})=>{
    restoreStorage(snapshot.storage);
    restoreModel(snapshot.model);
    restoreControls(snapshot.controls);
    await wait(120);
    restoreControls(snapshot.controls);
    if(/emergence\.html$/i.test(location.pathname))document.querySelector('#load')?.click();
    cleanRestoreAddress();
    showToast(shared?'Geteiltes Experiment wurde geladen.':`„${snapshot.name||'Experiment'}“ wurde geladen.`);
  };

  const queueRestore=snapshot=>{
    try{sessionStorage.setItem(PENDING_KEY,JSON.stringify(snapshot));}catch{}
    const target=new URL(snapshot.page||location.pathname,location.href);
    target.searchParams.set('snapshot',snapshot.id||'shared');
    target.searchParams.set('r',Date.now().toString(36));
    closeLayer();
    location.assign(target.href);
  };

  const cleanRestoreAddress=()=>{
    const url=new URL(location.href);
    let changed=false;
    for(const key of ['snapshot','r']){
      if(url.searchParams.has(key)){url.searchParams.delete(key);changed=true;}
    }
    if(url.hash.startsWith('#ulsnapshot=')){url.hash='';changed=true;}
    if(changed)history.replaceState(history.state,'',`${url.pathname}${url.search}${url.hash}`);
  };

  const base64UrlEncode=value=>{
    const bytes=new TextEncoder().encode(JSON.stringify(value));
    let binary='';
    bytes.forEach(byte=>{binary+=String.fromCharCode(byte);});
    return btoa(binary).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
  };
  const base64UrlDecode=value=>{
    const padded=value.replace(/-/g,'+').replace(/_/g,'/')+'==='.slice((value.length+3)%4);
    const binary=atob(padded);
    const bytes=Uint8Array.from(binary,char=>char.charCodeAt(0));
    return JSON.parse(new TextDecoder().decode(bytes));
  };

  const shareSnapshot=async snapshot=>{
    const portable={
      version:1,
      id:snapshot.id,
      name:snapshot.name,
      createdAt:snapshot.createdAt,
      page:snapshot.page,
      pageName:snapshot.pageName,
      model:snapshot.model,
      controls:snapshot.controls
    };
    let encoded;
    try{encoded=base64UrlEncode(portable);}catch{return showToast('Der Link konnte nicht erzeugt werden.');}
    if(encoded.length>7000)return showToast('Das Experiment ist für einen Link zu groß. Bitte JSON exportieren.');
    const url=new URL(snapshot.page||location.pathname,location.href);
    url.searchParams.delete('snapshot');
    url.searchParams.delete('r');
    url.hash=`ulsnapshot=${encoded}`;
    try{
      await navigator.clipboard.writeText(url.href);
      showToast('Teilbarer Link wurde kopiert.');
    }catch{
      window.prompt('Teilbaren Link kopieren:',url.href);
    }
  };

  const downloadJson=(data,filename)=>{
    const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});
    const url=URL.createObjectURL(blob);
    const anchor=document.createElement('a');
    anchor.href=url;
    anchor.download=filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  };

  const importSnapshot=file=>{
    const reader=new FileReader();
    reader.onload=()=>{
      try{
        const data=JSON.parse(String(reader.result));
        const incoming=Array.isArray(data)?data:data.snapshots||[data];
        const valid=incoming.filter(item=>item&&typeof item==='object'&&(item.model||item.controls||item.storage));
        if(!valid.length)throw new Error('Keine Snapshots');
        const normalized=valid.map(item=>({...item,id:item.id||uid(),name:item.name||'Importiertes Experiment',createdAt:item.createdAt||new Date().toISOString()}));
        writeSnapshots([...normalized,...readSnapshots()]);
        renderList();
        showToast(`${normalized.length} Experiment${normalized.length===1?'':'e'} importiert.`);
      }catch{showToast('Diese JSON-Datei enthält kein gültiges Experiment.');}
    };
    reader.readAsText(file);
  };

  const removeSnapshot=id=>{
    const snapshots=readSnapshots();
    const snapshot=snapshots.find(item=>item.id===id);
    if(!snapshot)return;
    if(!confirm(`„${snapshot.name}“ wirklich löschen?`))return;
    writeSnapshots(snapshots.filter(item=>item.id!==id));
    renderList();
  };

  const makeButton=(label,className,handler)=>{
    const button=document.createElement('button');
    button.type='button';
    button.className=className;
    button.textContent=label;
    button.addEventListener('click',handler);
    return button;
  };

  const renderList=()=>{
    if(!listNode)return;
    listNode.replaceChildren();
    const snapshots=readSnapshots();
    if(!snapshots.length){
      const empty=document.createElement('p');
      empty.className='ul-snapshot-empty';
      empty.textContent='Noch keine Experimente gespeichert.';
      listNode.appendChild(empty);
      return;
    }
    snapshots.forEach(snapshot=>{
      const card=document.createElement('article');
      card.className='ul-snapshot-card';
      const head=document.createElement('div');
      head.className='ul-snapshot-card-head';
      const title=document.createElement('strong');
      title.textContent=snapshot.name||'Experiment';
      const meta=document.createElement('span');
      const date=new Date(snapshot.createdAt||Date.now());
      meta.textContent=`${snapshot.pageName||'UniverseLab'} · ${date.toLocaleString('de-DE',{dateStyle:'short',timeStyle:'short'})}`;
      head.append(title,meta);

      const values=document.createElement('div');
      values.className='ul-snapshot-values';
      const model=snapshot.model||{};
      const entries=[['H₀',model.H0],['Ωₘ',model.Om],['w',model.w]];
      entries.forEach(([label,value])=>{
        if(value===undefined)return;
        const chip=document.createElement('span');
        chip.textContent=`${label} ${Number(value).toLocaleString('de-DE',{maximumFractionDigits:3})}`;
        values.appendChild(chip);
      });

      const actions=document.createElement('div');
      actions.className='ul-snapshot-card-actions';
      actions.append(
        makeButton('Laden','primary',()=>queueRestore(snapshot)),
        makeButton('Link','',()=>shareSnapshot(snapshot)),
        makeButton('JSON','',()=>downloadJson(snapshot,`${(snapshot.name||'universelab-experiment').replace(/[^a-z0-9äöüß_-]+/gi,'-')}.json`)),
        makeButton('Löschen','danger',()=>removeSnapshot(snapshot.id))
      );
      card.append(head,values,actions);
      listNode.appendChild(card);
    });
  };

  const addStyles=()=>{
    if(document.getElementById('ul-snapshot-style'))return;
    const style=document.createElement('style');
    style.id='ul-snapshot-style';
    style.textContent=`
      .ul-snapshot-chip{flex:0 0 auto;display:flex;align-items:center;gap:5px;min-height:30px;padding:5px 8px;border:1px solid #3b466e;border-radius:999px;background:#10162b;color:#e8ebff;font:750 10px system-ui;cursor:pointer;white-space:nowrap}
      .ul-snapshot-chip::before{content:'◫';color:#78e1b8;font-size:13px}.ul-snapshot-count{display:grid;place-items:center;min-width:17px;height:17px;padding:0 4px;border-radius:999px;background:#263052;color:#fff;font-size:9px}
      .ul-snapshot-layer{position:fixed;z-index:11000;inset:0;display:grid;place-items:center;padding:12px;background:#000b;backdrop-filter:blur(8px)}.ul-snapshot-layer[hidden]{display:none}
      .ul-snapshot-dialog{width:min(680px,100%);max-height:min(760px,calc(100dvh - 24px));display:flex;flex-direction:column;border:1px solid #364166;border-radius:18px;background:#090e1ff7;color:#f4f6ff;box-shadow:0 28px 90px #000d;font:12px system-ui;overflow:hidden}
      .ul-snapshot-head{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:13px 14px;border-bottom:1px solid #293252}.ul-snapshot-head strong{font-size:16px}.ul-snapshot-close{width:36px;height:36px;border:1px solid #303a5d;border-radius:10px;background:#11172b;color:#fff;font-size:19px}
      .ul-snapshot-actions{display:grid;grid-template-columns:1fr 1fr 1fr;gap:7px;padding:10px 12px;border-bottom:1px solid #202943}.ul-snapshot-actions button,.ul-snapshot-card-actions button{min-height:36px;padding:7px 9px;border:1px solid #303a5d;border-radius:9px;background:#11172b;color:#fff;font:750 11px system-ui}.ul-snapshot-actions .primary,.ul-snapshot-card-actions .primary{border:0;background:linear-gradient(135deg,#6551e8,#8d7cff)}
      .ul-snapshot-list{display:grid;gap:8px;padding:11px;overflow:auto;overscroll-behavior:contain}.ul-snapshot-empty{margin:22px;text-align:center;color:#9da7c7}
      .ul-snapshot-card{padding:10px;border:1px solid #293252;border-radius:13px;background:#0d1326}.ul-snapshot-card-head{display:grid;gap:2px}.ul-snapshot-card-head strong{font-size:13px}.ul-snapshot-card-head span{color:#9fa8c7;font-size:10px}
      .ul-snapshot-values{display:flex;flex-wrap:wrap;gap:5px;margin:8px 0}.ul-snapshot-values span{padding:4px 6px;border:1px solid #293252;border-radius:999px;background:#080c19;color:#b9c3e2;font-size:9.5px}
      .ul-snapshot-card-actions{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px}.ul-snapshot-card-actions .danger{color:#ff9aaa;border-color:#623344;background:#21101a}
      .ul-snapshot-toast{position:fixed;z-index:12000;left:50%;bottom:max(16px,env(safe-area-inset-bottom));transform:translate(-50%,20px);max-width:min(430px,calc(100vw - 24px));padding:9px 12px;border:1px solid #3b466e;border-radius:11px;background:#0a0f20f3;color:#fff;font:750 11px system-ui;box-shadow:0 15px 50px #000b;opacity:0;transition:.2s;pointer-events:none}.ul-snapshot-toast.show{opacity:1;transform:translate(-50%,0)}
      @media(max-width:1120px){.ul-snapshot-chip span:first-of-type{display:none}.ul-snapshot-chip{padding-inline:7px}}
      @media(max-width:520px){.ul-snapshot-actions{grid-template-columns:1fr 1fr}.ul-snapshot-actions .ul-export-all{grid-column:1/-1}.ul-snapshot-card-actions{grid-template-columns:1fr 1fr}.ul-snapshot-chip{min-width:30px}.ul-snapshot-count{display:none}}
      @media(max-width:390px){.ul-snapshot-chip{display:none}}
    `;
    document.head.appendChild(style);
  };

  const showToast=message=>{
    let toast=document.querySelector('.ul-snapshot-toast');
    if(!toast){toast=document.createElement('div');toast.className='ul-snapshot-toast';document.body.appendChild(toast);}
    toast.textContent=message;
    toast.classList.remove('show');
    requestAnimationFrame(()=>toast.classList.add('show'));
    clearTimeout(showToast.timer);
    showToast.timer=setTimeout(()=>toast.classList.remove('show'),2600);
  };

  const closeLayer=()=>{
    if(!layer)return;
    layer.hidden=true;
    document.documentElement.style.overflow='';
    triggerButton?.focus();
  };
  const openLayer=()=>{
    ensureLayer();
    renderList();
    layer.hidden=false;
    document.documentElement.style.overflow='hidden';
    layer.querySelector('.ul-snapshot-close')?.focus();
  };

  const ensureLayer=()=>{
    if(layer)return layer;
    layer=document.createElement('div');
    layer.className='ul-snapshot-layer';
    layer.hidden=true;
    layer.innerHTML='<section class="ul-snapshot-dialog" role="dialog" aria-modal="true" aria-label="Experiment-Snapshots"><header class="ul-snapshot-head"><strong>Experiment-Snapshots</strong><button type="button" class="ul-snapshot-close" aria-label="Schließen">×</button></header><div class="ul-snapshot-actions"></div><div class="ul-snapshot-list"></div></section>';
    const actions=layer.querySelector('.ul-snapshot-actions');
    const fileInput=document.createElement('input');
    fileInput.type='file';
    fileInput.accept='application/json,.json';
    fileInput.hidden=true;
    fileInput.addEventListener('change',()=>{
      const file=fileInput.files?.[0];
      if(file)importSnapshot(file);
      fileInput.value='';
    });
    actions.append(
      makeButton('Aktuelles Experiment speichern','primary',saveCurrent),
      makeButton('JSON importieren','',()=>fileInput.click()),
      makeButton('Alle exportieren','ul-export-all',()=>downloadJson({version:1,exportedAt:new Date().toISOString(),snapshots:readSnapshots()},'universelab-experimente.json')),
      fileInput
    );
    listNode=layer.querySelector('.ul-snapshot-list');
    layer.querySelector('.ul-snapshot-close').addEventListener('click',closeLayer);
    layer.addEventListener('click',event=>{if(event.target===layer)closeLayer();});
    document.body.appendChild(layer);
    return layer;
  };

  const updateTrigger=()=>{
    if(!triggerButton)return;
    const count=readSnapshots().length;
    const countNode=triggerButton.querySelector('.ul-snapshot-count');
    if(countNode)countNode.textContent=String(count);
    triggerButton.title=`Experiment-Snapshots${count?` (${count})`:''}`;
  };

  const attachTrigger=()=>{
    const shell=document.querySelector('.ul-shell');
    if(!shell||document.querySelector('.ul-snapshot-chip'))return false;
    triggerButton=document.createElement('button');
    triggerButton.type='button';
    triggerButton.className='ul-snapshot-chip';
    triggerButton.setAttribute('aria-label','Experiment-Snapshots öffnen');
    triggerButton.innerHTML='<span>Experimente</span><span class="ul-snapshot-count">0</span>';
    const state=shell.querySelector('.ul-state');
    shell.insertBefore(triggerButton,state||null);
    triggerButton.addEventListener('click',openLayer);
    updateTrigger();
    return true;
  };

  const restorePending=async()=>{
    let pending=null;
    try{
      pending=JSON.parse(sessionStorage.getItem(PENDING_KEY)||'null');
      sessionStorage.removeItem(PENDING_KEY);
    }catch{}
    if(pending)await applySnapshot(pending);
  };

  const restoreShared=async()=>{
    if(!location.hash.startsWith('#ulsnapshot='))return false;
    try{
      const snapshot=base64UrlDecode(location.hash.slice('#ulsnapshot='.length));
      await applySnapshot(snapshot,{shared:true});
      return true;
    }catch{
      showToast('Der geteilte Experiment-Link ist beschädigt.');
      return false;
    }
  };

  const init=async()=>{
    addStyles();
    ensureLayer();
    if(!attachTrigger()){
      const observer=new MutationObserver(()=>{if(attachTrigger())observer.disconnect();});
      observer.observe(document.documentElement,{subtree:true,childList:true});
      setTimeout(()=>observer.disconnect(),6000);
    }
    if(!(await restoreShared()))await restorePending();
    addEventListener('keydown',event=>{
      if(event.key==='Escape'&&layer&&!layer.hidden)closeLayer();
      if(event.ctrlKey&&event.shiftKey&&event.key.toLowerCase()==='s'){
        event.preventDefault();saveCurrent();
      }
    });
  };

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
