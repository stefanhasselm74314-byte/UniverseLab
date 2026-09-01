(()=>{
  'use strict';

  const VERSION='2.0.0';
  const C=globalThis.UniverseLabCosmology;
  const $=id=>document.getElementById(id);
  const canvas=$('chart');
  const ctx=canvas?.getContext('2d')||null;
  const inputIds=['H0','Om','Ol','s8','beta','ib','rchi'];
  const reference=Object.freeze({H0:67.4,Om:.315,Ol:.684908,w:-1,s8:.811,beta:.05,ib:.4,rchi:1,z:1});
  const outputIds=['ageL','ageB','dev1','S8','dc','dm','dl','da','mu','dcB','dmB','dlB','daB','muB'];
  const state={status:'INITIALIZING',revision:0,error:null,params:null,baseModel:'lcdm',bridgeModel:'bridge',series:{base:[],bridge:[]},metrics:null,distance:null};
  let timer=0;

  function readParams(){
    if(!C) throw new Error('CANONICAL_COSMOLOGY_ENGINE_MISSING');
    return C.normalizeParams({
      H0:Number($('H0')?.value),
      Om:Number($('Om')?.value),
      Ol:Number($('Ol')?.value),
      Or:C.DEFAULT_OR,
      w:-1,
      s8:Number($('s8')?.value),
      beta:Number($('beta')?.value),
      ib:Number($('ib')?.value),
      rchi:Number($('rchi')?.value)
    });
  }

  function fmt(value,digits=3){
    return Number.isFinite(value)
      ? value.toLocaleString('de-DE',{minimumFractionDigits:digits,maximumFractionDigits:digits})
      : '–';
  }
  function fmtSigned(value,digits=3){
    return Number.isFinite(value)
      ? value.toFixed(digits).replace('-','−').replace('.',',')
      : '–';
  }
  function setText(id,value){const node=$(id);if(node)node.textContent=value;}

  function updateReadouts(p){
    setText('oH0',fmt(p.H0,1));
    setText('oOm',fmt(p.Om,3));
    setText('oOl',fmt(p.Ode,3));
    setText('ow','−1,000');
    setText('os8',fmt(p.sigma8,3));
    setText('obeta',fmtSigned(p.betaTau,3));
    setText('oib',fmt(p.IB,3));
    setText('orchi',fmt(p.Rchi,2));
    setText('oz',fmt(Number($('z')?.value),3));
  }

  function validateScaleFactorDomain(p,model,aMin=1e-8,samples=8192){
    const logMin=Math.log(aMin);
    let minE2=Infinity,minA=1;
    for(let i=0;i<=samples;i++){
      const a=Math.exp(logMin*(1-i/samples));
      const value=C.e2FromA(a,p,model);
      if(value<minE2){minE2=value;minA=a;}
      if(!Number.isFinite(value)||value<=0){
        const code=model==='bridge'?'INVALID_BRIDGE_DOMAIN':'INVALID_BACKGROUND_DOMAIN';
        return {ok:false,code,model,a,e2:value,minE2,minA,samples};
      }
    }
    return {ok:true,code:'PASS',model,aMin,minE2,minA,samples};
  }

  function preflight(p){
    const checks=[
      C.validateBackgroundDomain(p,'lcdm',{zMin:0,zMax:8,samples:12288}),
      C.validateBackgroundDomain(p,'bridge',{zMin:0,zMax:8,samples:12288}),
      validateScaleFactorDomain(p,'lcdm'),
      validateScaleFactorDomain(p,'bridge')
    ];
    const failed=checks.find(check=>!check.ok);
    if(failed) throw new C.CosmologyError(failed.code,'Invalid Compare SAFE model domain',failed);
    return checks;
  }

  function computeDistance(p,z){
    const options={n:1024,domainSamples:1536};
    const one=model=>({
      DC:C.radialComovingDistance(z,p,model,options),
      DM:C.transverseComovingDistance(z,p,model,options),
      DL:C.luminosityDistance(z,p,model,options),
      DA:C.angularDiameterDistance(z,p,model,options),
      mu:C.distanceModulus(z,p,model,options),
      etherington:C.etheringtonRatio(z,p,model,options)
    });
    return {z,base:one('lcdm'),bridge:one('bridge')};
  }

  function compute(){
    const p=readParams();
    const domains=preflight(p);
    const base=[];
    const bridge=[];
    for(let i=0;i<=100;i++){
      const z=5*i/100;
      base.push([z,p.H0*C.E(z,p,'lcdm')]);
      bridge.push([z,p.H0*C.E(z,p,'bridge')]);
    }
    const ageL=C.ageGyr(p,'lcdm',{aMin:1e-8,n:4096,domainSamples:8192});
    const ageB=C.ageGyr(p,'bridge',{aMin:1e-8,n:4096,domainSamples:8192});
    const dev1=100*(C.E(1,p,'bridge')/C.E(1,p,'lcdm')-1);
    const distance=computeDistance(p,Number($('z')?.value));
    return {
      p,domains,series:{base,bridge},
      metrics:{ageL,ageB,dev1,S8:C.S8(p),amplitude:p.betaTau*p.IB,ac:C.bridgeScale(p)},
      distance
    };
  }

  function resizeCanvas(){
    if(!canvas||!ctx)return {width:0,height:0};
    const density=Math.min(2,globalThis.devicePixelRatio||1);
    const rect=canvas.getBoundingClientRect();
    const width=Math.max(280,rect.width||280);
    const height=Math.max(250,rect.height||250);
    canvas.width=Math.round(width*density);
    canvas.height=Math.round(height*density);
    ctx.setTransform(density,0,0,density,0,0);
    return {width,height};
  }

  function drawCurve(points,geometry,color){
    if(!points.length)return;
    const {left,top,plotWidth,plotHeight,maxY}=geometry;
    ctx.strokeStyle=color;
    ctx.lineWidth=2.3;
    ctx.beginPath();
    points.forEach(([z,H],index)=>{
      const x=left+z/5*plotWidth;
      const y=top+(1-H/maxY)*plotHeight;
      if(index)ctx.lineTo(x,y);else ctx.moveTo(x,y);
    });
    ctx.stroke();
  }

  function drawValid(){
    const {width,height}=resizeCanvas();
    ctx.clearRect(0,0,width,height);
    const left=48,right=14,top=16,bottom=31;
    const plotWidth=width-left-right,plotHeight=height-top-bottom;
    const maxY=Math.max(...state.series.base.map(row=>row[1]),...state.series.bridge.map(row=>row[1]))*1.05;
    ctx.strokeStyle='#27334f';ctx.fillStyle='#9ca8c8';ctx.font='10px system-ui';ctx.lineWidth=1;
    for(let i=0;i<=5;i++){
      const x=left+plotWidth*i/5;
      ctx.beginPath();ctx.moveTo(x,top);ctx.lineTo(x,top+plotHeight);ctx.stroke();ctx.fillText(String(i),x-2,height-9);
    }
    for(let i=0;i<=4;i++){
      const y=top+plotHeight*i/4;
      ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(width-right,y);ctx.stroke();ctx.fillText(fmt(maxY*(1-i/4),0),3,y+3);
    }
    const geometry={left,top,plotWidth,plotHeight,maxY};
    drawCurve(state.series.base,geometry,'#8d7cff');
    drawCurve(state.series.bridge,geometry,'#ff9f67');

    setText('ageL',`${fmt(state.metrics.ageL,2)} Gyr`);
    setText('ageB',`${fmt(state.metrics.ageB,2)} Gyr`);
    setText('dev1',`${fmtSigned(state.metrics.dev1,3)} %`);
    setText('S8',fmt(state.metrics.S8,3));
    renderDistance();

    const status=$('compareStatus');
    status.classList.remove('invalid');
    status.innerHTML=`<strong>PASS:</strong> Engine ${C.VERSION} · ΛCDM gegen effektive Brücke · E²&gt;0 und 1+Δ&gt;0 im geprüften Bereich · βτ𝓘B=${fmt(state.metrics.amplitude,4)} · a_c=${fmt(state.metrics.ac,4)}.`;
    const badge=$('safeBadge');
    badge.classList.remove('invalid');
    badge.textContent='SAFE 2.0 · kanonischer Rechenkern';
    $('csv').disabled=false;
  }

  function renderDistance(){
    const d=state.distance;
    setText('oz',fmt(d.z,3));
    setText('dc',`${fmt(d.base.DC,1)} Mpc`);
    setText('dm',`${fmt(d.base.DM,1)} Mpc`);
    setText('dl',`${fmt(d.base.DL,1)} Mpc`);
    setText('da',`${fmt(d.base.DA,1)} Mpc`);
    setText('mu',fmt(d.base.mu,3));
    setText('dcB',`${fmt(d.bridge.DC,1)} Mpc`);
    setText('dmB',`${fmt(d.bridge.DM,1)} Mpc`);
    setText('dlB',`${fmt(d.bridge.DL,1)} Mpc`);
    setText('daB',`${fmt(d.bridge.DA,1)} Mpc`);
    setText('muB',fmt(d.bridge.mu,3));
  }

  function drawInvalid(error){
    const {width,height}=resizeCanvas();
    ctx.clearRect(0,0,width,height);
    ctx.fillStyle='#ff9ab0';ctx.font='700 13px system-ui';
    ctx.fillText(error.code||'INVALID_MODEL_DOMAIN',24,42);
    ctx.fillStyle='#a9b3cf';ctx.font='11px system-ui';
    ctx.fillText('Keine Vergleichskurve aus einer ungültigen reellen Domäne erzeugt.',24,65);
    for(const id of outputIds)setText(id,'–');
    const status=$('compareStatus');
    status.classList.add('invalid');
    const coordinate=Number.isFinite(error?.detail?.z)?` bei z≈${fmt(error.detail.z,3)}`:Number.isFinite(error?.detail?.a)?` bei a≈${Number(error.detail.a).toExponential(3)}`:'';
    status.innerHTML=`<strong>${error.code||'INVALID_MODEL_DOMAIN'}:</strong> Der Parametersatz verletzt die reelle Modell-Domäne${coordinate}. Es wird weder ein positiver Floor noch eine scheinbar endliche Kurve oder CSV-Datei erzeugt.`;
    const badge=$('safeBadge');
    badge.classList.add('invalid');
    badge.textContent='ungültige Domäne';
    $('csv').disabled=true;
  }

  function performUpdate(){
    clearTimeout(timer);timer=0;
    try{
      const result=compute();
      Object.assign(state,{status:'PASS',revision:state.revision+1,error:null,params:result.p,series:result.series,metrics:result.metrics,distance:result.distance});
      updateReadouts(result.p);
      drawValid();
    }catch(error){
      const p=(()=>{try{return readParams();}catch{return null;}})();
      Object.assign(state,{status:error?.code||'ERROR',revision:state.revision+1,error:{code:error?.code||'ERROR',message:error?.message||String(error),detail:error?.detail||{}},params:p,series:{base:[],bridge:[]},metrics:null,distance:null});
      if(p)updateReadouts(p);
      drawInvalid(error);
    }
    globalThis.dispatchEvent(new CustomEvent('universelab:compare-safe-update',{detail:snapshot()}));
    return snapshot();
  }

  function schedule(){
    clearTimeout(timer);
    try{updateReadouts(readParams());}catch{}
    timer=setTimeout(performUpdate,70);
  }

  const formulas={
    az:{eq:'a=1/(1+z)',desc:'Übersetzt Rotverschiebung in den Skalenfaktor.',unit:'dimensionslos',hint:'Heute gilt z=0 und a=1.',input:[['z',1,'Rotverschiebung']],calc:v=>C.aOfZ(v.z)},
    H:{eq:'H(z)=H₀E(z)',desc:'Expansionsrate für einen vorgegebenen dimensionslosen E-Wert.',unit:'km s⁻¹ Mpc⁻¹',hint:'Bei z=0 gilt E(0)=1.',input:[['H0',67.4,'heutige Hubble-Rate'],['E',1.79,'dimensionslose Friedmann-Funktion']],calc:v=>v.H0*v.E},
    S8:{eq:'S₈=σ₈√(Ωₘ/0,3)',desc:'Kombination aus Materiedichte und Strukturamplitude.',unit:'dimensionslos',hint:'Algebraische Observable; kein Lensing-Fit.',input:[['s8',.811,'σ₈'],['Om',.315,'Ωₘ']],calc:v=>v.s8*Math.sqrt(v.Om/.3)},
    dh:{eq:'ΔH/H=E_bridge/E_ΛCDM−1',desc:'Effektive Hintergrundabweichung der implementierten Brücke.',unit:'dimensionslos',hint:'Der Brückenhintergrund ist ein effektiver Proxy, keine 6D-Parent-Herleitung.',input:[['z',1,'Rotverschiebung']],calc:v=>{const p=state.params||readParams();return C.E(v.z,p,'bridge')/C.E(v.z,p,'lcdm')-1;}},
    qeff:{eq:'q(z)=−1−d ln E/d ln a',desc:'Verzögerungsparameter des aktiven effektiven Brückenhintergrunds.',unit:'dimensionslos',hint:'Hintergrundableitung; keine Perturbations- oder Stabilitätsaussage.',input:[['z',0,'Rotverschiebung']],calc:v=>C.q(v.z,state.params||readParams(),'bridge')},
    Sigma:{eq:'Σ(a,k): nicht konstruiert',desc:'Eine HZT-Lensing-Map ist nicht freigegeben.',unit:'',hint:'UNRELEASED_LENSING_MAP — die GR-Identität Σ=1 ist kein abgeleitetes Brückenresultat.',input:[],calc:()=> 'UNRELEASED_LENSING_MAP'}
  };

  function renderFormula(){
    const formula=formulas[$('formula').value];
    setText('fEq',formula.eq);setText('fDesc',formula.desc);setText('fUnit',formula.unit);setText('fHint',formula.hint);
    $('fInputs').innerHTML=formula.input.map(([key,value,label])=>`<label><span>${key}</span><small>${label}</small><input type="number" step="any" data-k="${key}" value="${value}"></label>`).join('');
    $('fInputs').querySelectorAll('input').forEach(input=>input.addEventListener('input',calculateFormula));
    calculateFormula();
  }

  function calculateFormula(){
    const formula=formulas[$('formula').value];
    const values={};
    $('fInputs').querySelectorAll('input').forEach(input=>{values[input.dataset.k]=Number(input.value);});
    try{
      const result=formula.calc(values);
      setText('fResult',typeof result==='string'?result:fmt(result,6));
    }catch(error){
      setText('fResult',error?.code||'INVALID_INPUT');
    }
  }

  function setView(view){
    document.querySelectorAll('.tabs button').forEach(button=>button.classList.toggle('active',button.dataset.view===view));
    document.querySelectorAll('.view').forEach(node=>node.classList.toggle('active',node.id===`view-${view}`));
    if(view==='compare')setTimeout(()=>{if(state.status==='PASS')drawValid();else if(state.error)drawInvalid(state.error);},10);
    if(view==='distance'&&state.status==='PASS')renderDistance();
    if(view==='formulas')renderFormula();
  }

  function reset(){
    for(const [id,value] of Object.entries(reference)){
      const node=$(id);if(node){node.value=String(value);node.dispatchEvent(new Event('input',{bubbles:true}));}
    }
    return performUpdate();
  }

  function csvText(){
    if(state.status!=='PASS')throw new C.CosmologyError('CSV_BLOCKED_INVALID_DOMAIN','CSV export requires a valid model domain',{status:state.status});
    const lines=['z,H_LCDM_km_s_Mpc,H_bridge_km_s_Mpc,delta_H_over_H'];
    for(let i=0;i<=100;i++){
      const z=5*i/100;
      const base=state.params.H0*C.E(z,state.params,'lcdm');
      const bridge=state.params.H0*C.E(z,state.params,'bridge');
      lines.push([z,base,bridge,bridge/base-1].join(','));
    }
    return `${lines.join('\n')}\n`;
  }

  function downloadCsv(){
    try{
      const blob=new Blob([csvText()],{type:'text/csv;charset=utf-8'});
      const url=URL.createObjectURL(blob);
      const link=document.createElement('a');
      link.href=url;link.download='universelab-vergleich-safe-v2.csv';link.click();
      setTimeout(()=>URL.revokeObjectURL(url),1000);
    }catch(error){drawInvalid(error);}
  }

  function probe(z,model='lcdm',quantity='H'){
    const p=state.params||readParams();
    const zz=Number(z);
    if(quantity==='E')return C.E(zz,p,model);
    if(quantity==='H')return p.H0*C.E(zz,p,model);
    if(quantity==='mu')return C.distanceModulus(zz,p,model,{n:1024,domainSamples:1024});
    if(quantity==='DM')return C.transverseComovingDistance(zz,p,model,{n:1024,domainSamples:1024});
    throw new Error(`UNSUPPORTED_COMPARE_PROBE:${quantity}`);
  }

  function snapshot(){
    return JSON.parse(JSON.stringify({
      version:VERSION,engineVersion:C?.VERSION||null,status:state.status,revision:state.revision,error:state.error,
      params:state.params,baseModel:state.baseModel,bridgeModel:state.bridgeModel,metrics:state.metrics,distance:state.distance,
      seriesCounts:{base:state.series.base.length,bridge:state.series.bridge.length}
    }));
  }

  function init(){
    if(!C){drawInvalid({code:'CANONICAL_COSMOLOGY_ENGINE_MISSING',detail:{}});return;}
    const w=$('w');if(w){w.value='-1';w.disabled=true;w.setAttribute('aria-disabled','true');}
    for(const id of inputIds.concat(['z']))$(id)?.addEventListener('input',schedule,{passive:true});
    document.querySelectorAll('.tabs button').forEach(button=>button.addEventListener('click',()=>setView(button.dataset.view)));
    $('reset')?.addEventListener('click',event=>{event.preventDefault();reset();});
    $('csv')?.addEventListener('click',event=>{event.preventDefault();downloadCsv();});
    $('formula')?.addEventListener('change',renderFormula);
    globalThis.addEventListener('resize',schedule,{passive:true});
    globalThis.addEventListener('universelab:modelchange',schedule);
    renderFormula();performUpdate();
  }

  globalThis.UniverseLabCompareSafe=Object.freeze({VERSION,get status(){return state.status;},update:performUpdate,reset,probe,csvText,snapshot,setView});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
