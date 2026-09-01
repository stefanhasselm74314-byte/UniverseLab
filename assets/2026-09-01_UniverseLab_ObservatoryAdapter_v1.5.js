(()=>{
  'use strict';

  const VERSION='1.5.0';
  const C=globalThis.UniverseLabCosmology;
  const $=selector=>document.querySelector(selector);
  const canvas=$('#chart');
  const ctx=canvas?.getContext('2d')||null;
  const inputIds=['H0','Om','Ol','w','s8'];
  const reference=Object.freeze({H0:67.4,Om:0.315,Ol:0.684908,w:-1,s8:0.811});
  const observations=Object.freeze({
    hz:[[0.15,75],[0.38,83],[0.61,97],[1.48,160],[2.34,222]],
    mu:[[0.08,37.8],[0.25,40.5],[0.55,42.6],[1.0,44.1],[1.7,45.7]],
    growth:[[0.15,0.49],[0.38,0.48],[0.61,0.44],[1.0,0.39],[1.5,0.33]],
    bao:[[0.38,10.2],[0.51,13.4],[0.70,17.6],[1.48,25.8],[2.33,36.0]],
    gw:[]
  });
  const labels=Object.freeze({
    hz:'Modell H(z) · didaktische Beispielwerte',
    mu:'Distanzmodul μ(z) mit D_C → D_M → D_L · didaktische Supernovae',
    growth:'Lineare GR-Referenz fσ₈(z) aus der Growth-ODE · didaktische RSD-Werte',
    bao:'D_M/r_d mit Krümmungsabbildung · didaktische BAO-Werte',
    gw:'Illustratives Frequenzfenster: PTA · LISA · ET/CE'
  });

  const state={
    status:'INITIALIZING',
    mode:'hz',
    revision:0,
    error:null,
    params:null,
    model:'wcdm',
    metrics:null,
    series:[],
    observations:[],
    label:'',
    bounds:{xmin:0,xmax:5,ymin:0,ymax:600},
    growth:null
  };
  let timer=0;

  function readParams(){
    if(!C) throw new Error('CANONICAL_COSMOLOGY_ENGINE_MISSING');
    return C.normalizeParams({
      H0:Number($('#H0')?.value),
      Om:Number($('#Om')?.value),
      Ol:Number($('#Ol')?.value),
      Or:C.DEFAULT_OR,
      w:Number($('#w')?.value),
      s8:Number($('#s8')?.value)
    });
  }

  function setText(id,value){
    const node=document.getElementById(id);
    if(node) node.textContent=value;
  }

  function format(value,digits=3){
    return Number.isFinite(value)
      ? value.toLocaleString('de-DE',{minimumFractionDigits:digits,maximumFractionDigits:digits})
      : '–';
  }

  function formatSigned(value,digits=3){
    return Number.isFinite(value)
      ? value.toFixed(digits).replace('-','−').replace('.',',')
      : '–';
  }

  function updateReadouts(p){
    setText('vH0',format(p.H0,1));
    setText('vOm',format(p.Om,3));
    setText('vOl',format(p.Ode,3));
    setText('vw',formatSigned(p.w,3));
    setText('vs8',format(p.sigma8,3));
  }

  function validateAgeDomain(p,model,aMin=1e-8,samples=4096){
    let minE2=Infinity,minA=1;
    const lo=Math.log(aMin);
    for(let i=0;i<=samples;i++){
      const a=Math.exp(lo*(1-i/samples));
      const value=C.e2FromA(a,p,model);
      if(value<minE2){minE2=value;minA=a;}
      if(!Number.isFinite(value)||value<=0){
        return {ok:false,code:'INVALID_BACKGROUND_DOMAIN',a,minE2,minA,e2:value,samples};
      }
    }
    return {ok:true,code:'PASS',aMin,minE2,minA,samples};
  }

  function preflight(p,model){
    const chart=C.validateBackgroundDomain(p,model,{zMin:0,zMax:5,samples:8192});
    if(!chart.ok) throw new C.CosmologyError(chart.code,'Invalid Observatory chart domain',chart);
    const age=validateAgeDomain(p,model,1e-8,4096);
    if(!age.ok) throw new C.CosmologyError(age.code,'Invalid Observatory age domain',age);
    return {chart,age};
  }

  function computeSeries(p,model,mode){
    const series=[];
    let bounds={xmin:0,xmax:5,ymin:0,ymax:600};
    let growth=null;

    if(mode==='hz'){
      for(let i=0;i<=125;i++){
        const z=5*i/125;
        series.push([z,p.H0*C.E(z,p,model)]);
      }
      bounds={xmin:0,xmax:5,ymin:0,ymax:Math.max(600,Math.max(...series.map(row=>row[1]))*1.05)};
    }else if(mode==='mu'){
      bounds={xmin:0.01,xmax:2.2,ymin:32,ymax:48};
      for(let i=0;i<=90;i++){
        const z=bounds.xmin+(bounds.xmax-bounds.xmin)*i/90;
        series.push([z,C.distanceModulus(z,p,model,{n:256,domainSamples:384})]);
      }
    }else if(mode==='growth'){
      bounds={xmin:0,xmax:3,ymin:0,ymax:1.1};
      growth=C.solveGrowth(p,model,{steps:4000});
      for(let i=0;i<=100;i++){
        const z=bounds.xmax*i/100;
        series.push([z,C.growthAtZ(z,growth).fsigma8]);
      }
    }else if(mode==='bao'){
      bounds={xmin:0.02,xmax:3,ymin:0,ymax:40};
      for(let i=0;i<=90;i++){
        const z=bounds.xmin+(bounds.xmax-bounds.xmin)*i/90;
        series.push([z,C.baoDMOverRd(z,p,model,{n:256,domainSamples:384,rdMpc:C.DEFAULT_RD_MPC})]);
      }
      bounds.ymax=Math.max(40,Math.max(...series.map(row=>row[1]),...observations.bao.map(row=>row[1]))*1.06);
    }else if(mode==='gw'){
      bounds={xmin:-10,xmax:4,ymin:0,ymax:1};
      series.push([-9,0.2],[-7,0.5],[-4,0.8],[-1,0.5],[2,0.3]);
    }else{
      throw new Error(`UNKNOWN_OBSERVATORY_MODE:${mode}`);
    }
    return {series,bounds,growth};
  }

  function compute(){
    const p=readParams();
    const model='wcdm';
    const domain=preflight(p,model);
    const metrics={
      age:C.ageGyr(p,model,{aMin:1e-8,n:4096,domainSamples:8192}),
      q0:C.q(0,p,model),
      S8:C.S8(p),
      Ok:p.Ok,
      domain
    };
    const curve=computeSeries(p,model,state.mode);
    return {
      p,model,metrics,
      series:curve.series,
      observations:observations[state.mode],
      label:labels[state.mode],
      bounds:curve.bounds,
      growth:curve.growth
    };
  }

  function resizeCanvas(){
    if(!canvas||!ctx) return {width:0,height:0};
    const density=Math.min(2,globalThis.devicePixelRatio||1);
    const rect=canvas.getBoundingClientRect();
    const width=Math.max(280,rect.width||280);
    const height=Math.max(220,rect.height||220);
    canvas.width=Math.round(width*density);
    canvas.height=Math.round(height*density);
    ctx.setTransform(density,0,0,density,0,0);
    return {width,height};
  }

  function coordinate(point,bounds,plot){
    const [px,py]=point;
    const x=plot.left+(px-bounds.xmin)/(bounds.xmax-bounds.xmin)*plot.width;
    const y=plot.top+(1-(py-bounds.ymin)/(bounds.ymax-bounds.ymin))*plot.height;
    return [x,y];
  }

  function drawGrid(width,height,bounds){
    const plot={left:48,right:20,top:15,bottom:31};
    plot.width=width-plot.left-plot.right;
    plot.height=height-plot.top-plot.bottom;
    ctx.strokeStyle='#232b47';
    ctx.fillStyle='#8f9bbb';
    ctx.font='10px system-ui';
    ctx.lineWidth=1;
    for(let i=0;i<=5;i++){
      const y=plot.top+i*plot.height/5;
      const value=bounds.ymax-(bounds.ymax-bounds.ymin)*i/5;
      ctx.beginPath();ctx.moveTo(plot.left,y);ctx.lineTo(width-plot.right,y);ctx.stroke();
      ctx.fillText(format(value,Math.abs(bounds.ymax-bounds.ymin)<5?2:0),3,y+3);
    }
    for(let i=0;i<=5;i++){
      const x=plot.left+i*plot.width/5;
      const value=bounds.xmin+(bounds.xmax-bounds.xmin)*i/5;
      ctx.fillText(format(value,Math.abs(bounds.xmax-bounds.xmin)<5?1:0),x-8,height-8);
    }
    return plot;
  }

  function drawValid(){
    const {width,height}=resizeCanvas();
    ctx.clearRect(0,0,width,height);
    const plot=drawGrid(width,height,state.bounds);
    ctx.strokeStyle='#8d7cff';
    ctx.lineWidth=2.5;
    ctx.beginPath();
    state.series.forEach((point,index)=>{
      const [x,y]=coordinate(point,state.bounds,plot);
      if(index===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    });
    ctx.stroke();
    ctx.fillStyle='#79e3bc';
    for(const point of state.observations){
      const [x,y]=coordinate(point,state.bounds,plot);
      ctx.beginPath();ctx.arc(x,y,4,0,Math.PI*2);ctx.fill();
    }
    ctx.fillStyle='#a8b0cf';
    ctx.font='11px system-ui';
    ctx.fillText(state.label,52,height-10);

    $('#legend').innerHTML='<span><i class="dot" style="background:#8d7cff"></i>kanonischer Modellpfad</span><span><i class="dot" style="background:#79e3bc"></i>didaktische Beispielwerte</span>';
    setText('age',`${format(state.metrics.age,2)} Gyr`);
    setText('q0',formatSigned(state.metrics.q0,3));
    setText('s80',format(state.metrics.S8,3));
    setText('curv',state.metrics.Ok.toExponential(2).replace('.',','));

    const status=$('#domainStatus');
    status.classList.remove('invalid');
    status.innerHTML=`<strong>PASS:</strong> Engine ${C.VERSION} · ${state.model} · E²(z)&gt;0 im geprüften Chart- und Altersbereich · D_C→D_M aktiv${state.mode==='growth'?' · Growth-ODE aktiv':''}.`;
    const badge=$('#observatoryBadge');
    badge.classList.remove('invalid');
    badge.textContent='kanonischer Rechenkern';
  }

  function drawInvalid(error){
    const {width,height}=resizeCanvas();
    ctx.clearRect(0,0,width,height);
    ctx.fillStyle='#ff9ab0';
    ctx.font='700 13px system-ui';
    ctx.fillText(error.code||'INVALID_BACKGROUND_DOMAIN',24,42);
    ctx.fillStyle='#a8b0cf';
    ctx.font='11px system-ui';
    ctx.fillText('Keine Kurve aus einer ungültigen reellen Hintergrunddomäne erzeugt.',24,65);
    $('#legend').innerHTML='<span><i class="dot" style="background:#ff7b98"></i>fail-closed: keine numerische Regularisierung</span>';
    for(const id of ['age','q0','s80','curv']) setText(id,'–');

    const status=$('#domainStatus');
    status.classList.add('invalid');
    const z=Number.isFinite(error?.detail?.z)?` bei z≈${format(error.detail.z,3)}`:'';
    status.innerHTML=`<strong>${error.code||'INVALID_BACKGROUND_DOMAIN'}:</strong> Der Parametersatz verletzt die reelle Hintergrunddomäne${z}. Es wird kein positiver Floor und keine scheinbar endliche Kurve erzeugt.`;
    const badge=$('#observatoryBadge');
    badge.classList.add('invalid');
    badge.textContent='ungültige Domäne';
  }

  function updateReadoutsFromInputs(){
    try{updateReadouts(readParams());}catch{}
  }

  function performUpdate(){
    clearTimeout(timer);timer=0;
    try{
      const result=compute();
      Object.assign(state,{
        status:'PASS',revision:state.revision+1,error:null,params:result.p,model:result.model,
        metrics:result.metrics,series:result.series,observations:result.observations,label:result.label,
        bounds:result.bounds,growth:result.growth
      });
      updateReadouts(result.p);
      drawValid();
    }catch(error){
      const p=(()=>{try{return readParams();}catch{return null;}})();
      Object.assign(state,{
        status:error?.code||'ERROR',revision:state.revision+1,
        error:{code:error?.code||'ERROR',message:error?.message||String(error),detail:error?.detail||{}},
        params:p,model:'wcdm',metrics:null,series:[],observations:[],label:'',growth:null,
        bounds:{xmin:0,xmax:1,ymin:0,ymax:1}
      });
      if(p) updateReadouts(p); else updateReadoutsFromInputs();
      drawInvalid(error);
    }
    globalThis.dispatchEvent(new CustomEvent('universelab:observatory-update',{detail:snapshot()}));
    return snapshot();
  }

  function schedule(){
    clearTimeout(timer);
    updateReadoutsFromInputs();
    timer=setTimeout(performUpdate,70);
  }

  function setMode(mode){
    if(!Object.prototype.hasOwnProperty.call(labels,mode)) throw new Error(`UNKNOWN_OBSERVATORY_MODE:${mode}`);
    state.mode=mode;
    document.querySelectorAll('.tabs button').forEach(button=>button.classList.toggle('active',button.dataset.mode===mode));
    return performUpdate();
  }

  function reset(){
    for(const [id,value] of Object.entries(reference)){
      const node=document.getElementById(id);
      if(node){node.value=String(value);node.dispatchEvent(new Event('input',{bubbles:true}));}
    }
    return performUpdate();
  }

  function probe(z,mode=state.mode){
    const p=state.params||readParams();
    const model=state.model||'wcdm';
    const zz=Number(z);
    if(mode==='hz') return p.H0*C.E(zz,p,model);
    if(mode==='mu') return C.distanceModulus(zz,p,model,{n:1024,domainSamples:1024});
    if(mode==='bao') return C.baoDMOverRd(zz,p,model,{n:1024,domainSamples:1024,rdMpc:C.DEFAULT_RD_MPC});
    if(mode==='growth'){
      const solution=state.growth||C.solveGrowth(p,model,{steps:4000});
      return C.growthAtZ(zz,solution).fsigma8;
    }
    throw new Error(`UNSUPPORTED_PROBE_MODE:${mode}`);
  }

  function snapshot(){
    return JSON.parse(JSON.stringify({
      version:VERSION,engineVersion:C?.VERSION||null,status:state.status,mode:state.mode,revision:state.revision,
      error:state.error,params:state.params,model:state.model,metrics:state.metrics,
      series:state.series,observations:state.observations,label:state.label,growth:state.growth
        ? {model:state.growth.model,aInit:state.growth.aInit,steps:state.growth.steps}
        : null
    }));
  }

  function init(){
    if(!C){
      state.status='CANONICAL_COSMOLOGY_ENGINE_MISSING';
      drawInvalid({code:state.status,message:state.status,detail:{}});
      return;
    }
    for(const id of inputIds) document.getElementById(id)?.addEventListener('input',schedule,{passive:true});
    document.querySelectorAll('.tabs button').forEach(button=>button.addEventListener('click',()=>setMode(button.dataset.mode)));
    $('#reset')?.addEventListener('click',event=>{event.preventDefault();reset();});
    globalThis.addEventListener('resize',schedule,{passive:true});
    globalThis.addEventListener('universelab:modelchange',schedule);
    performUpdate();
  }

  globalThis.UniverseLabObservatory=Object.freeze({
    VERSION,
    get status(){return state.status;},
    get mode(){return state.mode;},
    update:performUpdate,setMode,reset,probe,snapshot
  });

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
