(()=>{
  'use strict';

  const VERSION='1.0.3';
  const STORAGE_KEY='universelab';
  const STATE_SCHEMA='universelab.emergence-state.v2';
  const C=globalThis.UniverseLabCosmology;
  const $=selector=>document.querySelector(selector);
  const simCanvas=$('#c');
  const simCtx=simCanvas?.getContext('2d')||null;
  const chartCanvas=$('#chart');
  const chartCtx=chartCanvas?.getContext('2d')||null;
  const language=(document.documentElement.lang||'de').toLowerCase().startsWith('en')?'en':'de';

  const text={
    de:{start:'▶ Start',pause:'⏸ Pause',engine:'kanonischer Growth-Adapter',invalid:'ungültige Domäne',pass:'PASS',noCurve:'Keine kosmologische Kurve aus einer ungültigen reellen Hintergrunddomäne.',staticMode:'Kosmologische Anzeige statisch',physicalMode:'ΛCDM-Anzeigezeit aktiv',heuristicMode:'Heuristische Anzeigegröße aktiv',radiation:'Strahlungsära',matter:'Materieära',curvature:'Krümmungsära',vacuum:'Vakuumära',accelerated:'beschleunigt',decelerated:'gebremst',saved:'Zustand gespeichert',missingSave:'Kein gespeicherter Zustand',visualOnly:'Anzeigeresampling verändert das Simulationsgitter nicht',modelLine:'Zellautomat und Kosmologie sind dynamisch entkoppelt',separationLong:'Zentrale Trennung: Der Zellautomat beeinflusst weder E(a), D(a), f(a) noch kosmologische Epochen. Die optionale Anzeigevergrößerung wird aus einer getrennten Renderansicht erzeugt und verändert weder Gittergröße noch Zellzustand des Automaten.'},
    en:{start:'▶ Start',pause:'⏸ Pause',engine:'canonical growth adapter',invalid:'invalid domain',pass:'PASS',noCurve:'No cosmological curve is generated from an invalid real background domain.',staticMode:'Cosmology display held static',physicalMode:'ΛCDM display time active',heuristicMode:'Heuristic display size active',radiation:'radiation era',matter:'matter era',curvature:'curvature era',vacuum:'vacuum era',accelerated:'accelerating',decelerated:'decelerating',saved:'State saved',missingSave:'No saved state',visualOnly:'Display resampling does not modify the simulation lattice',modelLine:'Cellular automaton and cosmology are dynamically decoupled',separationLong:'Core separation: the cellular automaton affects neither E(a), D(a), f(a), nor the cosmological epochs. Optional display enlargement is generated in a separate render view and changes neither the automaton lattice size nor its cell state.'}
  }[language];

  const state={
    status:'INITIALIZING',running:false,generation:0,N:120,displayN:120,
    cells:new Uint8Array(120*120),next:new Uint8Array(120*120),
    lastFrame:0,accumulator:0,history:[],params:null,model:'lcdm',domain:null,
    growth:null,timeMap:null,a:1e-3,tau:0,revision:0,error:null,installPrompt:null,lastLoad:null,
    cellularDynamicsIndependent:true,gridResamplingVisualOnly:true
  };
  const parameterIds=['h0','om','or','ol'];
  const controlIds=['speed','density','noise','timeScale','expand'];
  let timer=0;

  function setText(id,value){const node=document.getElementById(id);if(node)node.textContent=String(value);}
  function fmt(value,digits=3){return Number.isFinite(value)?value.toLocaleString(language==='de'?'de-DE':'en-US',{minimumFractionDigits:digits,maximumFractionDigits:digits}):'–';}
  function fmtExp(value,digits=3){return Number.isFinite(value)?value.toExponential(digits).replace('.',language==='de'?',':'.'):'–';}
  function clamp(value,min,max){return Math.max(min,Math.min(max,value));}

  function readParams(){
    if(!C)throw new Error('CANONICAL_COSMOLOGY_ENGINE_MISSING');
    return C.normalizeParams({H0:Number($('#h0')?.value),Om:Number($('#om')?.value),Or:Number($('#or')?.value),Ol:Number($('#ol')?.value),w:-1,sigma8:.811});
  }

  function validateScaleFactorDomain(params,model,aMin=1e-8,samples=8192){
    if(!(aMin>0&&aMin<1))throw new Error('INVALID_A_MIN');
    const logMin=Math.log(aMin);
    let minE2=Infinity,minA=1;
    for(let i=0;i<=samples;i++){
      const a=Math.exp(logMin*(1-i/samples));
      const e2=C.e2FromA(a,params,model);
      if(e2<minE2){minE2=e2;minA=a;}
      if(!Number.isFinite(e2)||e2<=0)return{ok:false,code:'INVALID_BACKGROUND_DOMAIN',a,e2,minE2,minA,samples,aMin};
    }
    return{ok:true,code:'PASS',minE2,minA,samples,aMin};
  }

  function componentState(a,params){
    const radiation=params.Or/a**4,matter=params.Om/a**3,curvature=params.Ok/a**2,vacuum=params.Ode;
    const total=C.e2FromA(a,params,'lcdm');
    if(!(Number.isFinite(total)&&total>0))throw new C.CosmologyError('INVALID_BACKGROUND_DOMAIN','E^2 must remain strictly positive',{a,e2:total});
    return{radiation,matter,curvature,vacuum,total,fractions:{radiation:radiation/total,matter:matter/total,curvature:curvature/total,vacuum:vacuum/total}};
  }

  function dominantEra(c){return[[text.radiation,c.radiation],[text.matter,c.matter],[text.curvature,Math.abs(c.curvature)],[text.vacuum,c.vacuum]].sort((a,b)=>b[1]-a[1])[0][0];}

  function solveAccelerationOnset(params,aMin){
    const qAt=a=>C.q(Math.max(0,1/a-1),params,'lcdm');
    const samples=2048;
    let previousA=aMin,previousQ=qAt(aMin);
    for(let i=1;i<=samples;i++){
      const a=Math.exp(Math.log(aMin)*(1-i/samples)),q=qAt(a);
      if(Number.isFinite(previousQ)&&Number.isFinite(q)&&previousQ*q<=0){
        let lo=previousA,hi=a,qlo=previousQ;
        for(let j=0;j<80;j++){
          const mid=Math.sqrt(lo*hi),qm=qAt(mid);
          if(qlo*qm<=0)hi=mid;else{lo=mid;qlo=qm;}
        }
        return Math.sqrt(lo*hi);
      }
      previousA=a;previousQ=q;
    }
    return null;
  }

  function buildTimeMap(params,aMin,points=4096){
    const x0=Math.log(aMin),dx=-x0/points,rows=[];
    const invE=x=>1/C.E(Math.max(0,Math.exp(-Math.min(0,x))-1),params,'lcdm');
    let x=x0,tau=0;
    rows.push({x,a:aMin,tau});
    for(let i=0;i<points;i++){
      const x1=i===points-1?0:x+dx;
      const localDx=x1-x,mid=(x+x1)/2;
      tau+=localDx*(invE(x)+4*invE(mid)+invE(x1))/6;
      x=x1;
      rows.push({x,a:i===points-1?1:Math.exp(x),tau});
    }
    return{aMin,points,totalTau:tau,rows};
  }

  function lowerBracket(rows,value,key){
    let lo=0,hi=rows.length-1;
    while(hi-lo>1){const mid=(lo+hi)>>1;if(rows[mid][key]<=value)lo=mid;else hi=mid;}
    return[lo,hi];
  }

  function tauAtScaleFactor(a,map){
    const aa=clamp(Number(a),map.aMin,1);
    if(aa<=map.aMin)return 0;
    if(aa>=1)return map.totalTau;
    const[lo,hi]=lowerBracket(map.rows,aa,'a'),A=map.rows[lo],B=map.rows[hi];
    const u=(Math.log(aa)-A.x)/(B.x-A.x);
    return A.tau*(1-u)+B.tau*u;
  }

  function scaleFactorAtTau(tau,map){
    const tt=clamp(Number(tau),0,map.totalTau);
    if(tt<=0)return map.aMin;
    if(tt>=map.totalTau)return 1;
    const[lo,hi]=lowerBracket(map.rows,tt,'tau'),A=map.rows[lo],B=map.rows[hi];
    const u=(tt-A.tau)/(B.tau-A.tau);
    return Math.min(1,Math.exp(A.x*(1-u)+B.x*u));
  }

  function rebuildCosmology({resetScale=false}={}){
    const params=readParams(),model='lcdm';
    const scaleDomain=validateScaleFactorDomain(params,model,1e-8,8192);
    if(!scaleDomain.ok)throw new C.CosmologyError(scaleDomain.code,'Invalid Emergence background domain',scaleDomain);
    const growth=C.solveGrowth(params,model,{steps:4000});
    const timeMap=buildTimeMap(params,growth.aInit,4096);
    const age=C.ageGyr(params,model,{aMin:1e-8,n:4096,domainSamples:8192});
    const epochs={radiationMatter:params.Om>0?params.Or/params.Om:null,matterVacuum:params.Ode>0?Math.cbrt(params.Om/params.Ode):null,acceleration:solveAccelerationOnset(params,growth.aInit)};
    state.params=params;state.model=model;state.growth=growth;state.timeMap=timeMap;
    state.domain={scaleFactor:scaleDomain,ageGyr:age,epochs,displayTime:{aMin:timeMap.aMin,points:timeMap.points,totalTau:timeMap.totalTau,endpoint:{x:timeMap.rows.at(-1).x,a:timeMap.rows.at(-1).a}}};
    state.error=null;state.status='PASS';state.history=[];
    if(resetScale||!Number.isFinite(state.a)){state.a=growth.aInit;state.tau=0;}
    else{state.a=clamp(state.a,growth.aInit,1);state.tau=tauAtScaleFactor(state.a,timeMap);}
    state.revision++;
  }

  function diagnosticsAt(a=state.a){
    if(!state.params||!state.growth)throw new Error('COSMOLOGY_NOT_READY');
    const aa=clamp(Number(a),state.growth.aInit,1),z=Math.max(0,1/aa-1);
    const E=C.E(z,state.params,state.model),components=componentState(aa,state.params),growth=C.growthAtZ(z,state.growth),q=C.q(z,state.params,state.model);
    const omegaMatter=components.fractions.matter,approximation=omegaMatter>=0?omegaMatter**.55:NaN;
    const approximationError=Number.isFinite(approximation)&&growth.f!==0?(approximation-growth.f)/growth.f:NaN;
    return{a:aa,z,E,q,components,growth,approximation,approximationError,era:dominantEra(components),expansion:q<0?text.accelerated:text.decelerated};
  }

  function advanceCosmology(){
    if($('#expMode')?.value!=='lcdm'||state.a>=1||!state.timeMap)return;
    const deltaTau=2e-5*Number($('#timeScale')?.value||25);
    state.tau=Math.min(state.timeMap.totalTau,state.tau+deltaTau);
    state.a=scaleFactorAtTau(state.tau,state.timeMap);
  }

  function ruleSets(value){const[birth,survival]=String(value).split('/');return{birth:new Set([...birth.slice(1)].map(Number)),survival:new Set([...survival.slice(1)].map(Number))};}

  function restoreSimulationGrid(target,cells=null){
    const N=clamp(Math.round(Number(target)||120),40,260);
    state.N=N;
    state.cells=new Uint8Array(N*N);
    state.next=new Uint8Array(N*N);
    if(Array.isArray(cells)&&cells.length===N*N)state.cells=Uint8Array.from(cells,value=>value?1:0);
  }

  function displayGridSize(){
    const mode=$('#expMode')?.value||'lcdm';
    if(mode==='lcdm'&&state.status==='PASS'&&state.growth){
      const ratio=Math.max(1,state.a/state.growth.aInit);
      return clamp(Math.round(state.N+28*Math.log10(ratio)),state.N,260);
    }
    if(mode==='heuristic'){
      const strength=Number($('#expand')?.value||0),period=Math.max(8,Math.round(110-strength));
      return clamp(state.N+2*Math.floor(state.generation/period),state.N,260);
    }
    return state.N;
  }

  function seed(kind=$('#preset')?.value||'random'){
    state.cells.fill(0);state.generation=0;state.history=[];state.a=state.growth?.aInit||1e-3;state.tau=0;
    const density=Number($('#density')?.value||22)/100,N=state.N;
    if(kind==='random')for(let i=0;i<state.cells.length;i++)state.cells[i]=Math.random()<density?1:0;
    else if(kind==='bigbang'){
      const radius=N*.055;
      for(let y=0;y<N;y++)for(let x=0;x<N;x++)if((x-N/2)**2+(y-N/2)**2<radius**2)state.cells[y*N+x]=Math.random()<.58?1:0;
    }else if(kind==='symmetry'){
      for(let y=10;y<N/2;y++)for(let x=10;x<N/2;x++)if(Math.random()<density){state.cells[y*N+x]=1;state.cells[y*N+N-1-x]=1;state.cells[(N-1-y)*N+x]=1;state.cells[(N-1-y)*N+N-1-x]=1;}
    }else for(let k=0;k<36;k++){
      const x=5+Math.floor(Math.random()*(N-10)),y=5+Math.floor(Math.random()*(N-10));
      for(const[u,v]of[[1,0],[2,1],[0,2],[1,2],[2,2]])state.cells[(y+v)*N+x+u]=1;
    }
    recordHistory();draw();return snapshot();
  }

  function clearCells(){state.cells.fill(0);state.generation=0;state.history=[];state.a=state.growth?.aInit||1e-3;state.tau=0;recordHistory();draw();return snapshot();}

  function stepCells(){
    const rules=ruleSets($('#rule')?.value||'B3/S23'),noise=Number($('#noise')?.value||0)/100000,N=state.N;
    for(let y=0;y<N;y++)for(let x=0;x<N;x++){
      let neighbors=0;
      for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++)if(dx||dy)neighbors+=state.cells[((y+dy+N)%N)*N+(x+dx+N)%N];
      const index=y*N+x;
      state.next[index]=((state.cells[index]?rules.survival.has(neighbors):rules.birth.has(neighbors))||Math.random()<noise)?1:0;
    }
    [state.cells,state.next]=[state.next,state.cells];state.generation++;
    if($('#expMode')?.value==='lcdm'&&state.status==='PASS')advanceCosmology();
    if(state.status==='PASS')recordHistory();
    draw();return snapshot();
  }

  function liveCount(){let total=0;for(const value of state.cells)total+=value;return total;}
  function cellHash(){let hash=2166136261;for(const value of state.cells)hash=Math.imul(hash^value,16777619);return(hash>>>0).toString(16).padStart(8,'0');}

  function recordHistory(){
    if(state.status!=='PASS'||!state.params||!state.growth)return;
    const live=liveCount(),d=diagnosticsAt(state.a);
    state.history.push({generation:state.generation,N:state.N,displayN:displayGridSize(),live,density:live/(state.N*state.N),tau:state.tau,a:d.a,E:d.E,q:d.q,radiation:d.components.fractions.radiation,matter:d.components.fractions.matter,curvature:d.components.fractions.curvature,vacuum:d.components.fractions.vacuum,D:d.growth.D,f:d.growth.f,approximation:d.approximation,era:d.era});
    if(state.history.length>2500)state.history.shift();
  }

  function drawCells(){
    if(!simCtx||!simCanvas)return;
    simCtx.fillStyle='#02030a';simCtx.fillRect(0,0,simCanvas.width,simCanvas.height);
    const renderN=displayGridSize();state.displayN=renderN;
    const scale=simCanvas.width/renderN;
    for(let y=0;y<renderN;y++)for(let x=0;x<renderN;x++){
      const sx=Math.min(state.N-1,Math.floor(x*state.N/renderN)),sy=Math.min(state.N-1,Math.floor(y*state.N/renderN));
      if(!state.cells[sy*state.N+sx])continue;
      simCtx.fillStyle=`hsl(${235+55*((x+y+state.generation*.15)%renderN/renderN)} 90% 68%)`;
      simCtx.fillRect(x*scale,y*scale,Math.ceil(scale),Math.ceil(scale));
    }
  }

  function seriesRange(rows,keys){
    const values=[];for(const row of rows)for(const key of keys)if(Number.isFinite(row[key]))values.push(row[key]);
    if(!values.length)return{min:-1,max:1};
    let min=Math.min(...values),max=Math.max(...values);if(min===max){min-=1;max+=1;}
    const pad=(max-min)*.08;return{min:min-pad,max:max+pad};
  }

  function drawChart(){
    if(!chartCtx||!chartCanvas)return;
    chartCtx.fillStyle='#02030a';chartCtx.fillRect(0,0,chartCanvas.width,chartCanvas.height);
    if(state.status!=='PASS'||state.history.length===0){chartCtx.fillStyle='#ff9ab0';chartCtx.font='700 16px system-ui';chartCtx.fillText(state.error?.code||'NO_VALID_COSMOLOGY_HISTORY',24,42);return;}
    const rows=state.history,width=chartCanvas.width,height=chartCanvas.height,left=48,right=18,top=18,bottom=32;
    const plotWidth=width-left-right,plotHeight=height-top-bottom,range=seriesRange(rows,['radiation','matter','vacuum','D','f','approximation']);
    const xOf=index=>left+index/Math.max(1,rows.length-1)*plotWidth,yOf=value=>top+(1-(value-range.min)/(range.max-range.min))*plotHeight;
    chartCtx.strokeStyle='#26304e';chartCtx.lineWidth=1;chartCtx.fillStyle='#8f9bbb';chartCtx.font='11px system-ui';
    for(let i=0;i<=4;i++){
      const y=top+i*plotHeight/4,value=range.max-(range.max-range.min)*i/4;
      chartCtx.beginPath();chartCtx.moveTo(left,y);chartCtx.lineTo(width-right,y);chartCtx.stroke();chartCtx.fillText(fmt(value,2),3,y+4);
    }
    for(const[key,color]of[['radiation','#ffcf6e'],['matter','#6eb6ff'],['vacuum','#ff84c1'],['D','#ffffff'],['f','#b7ff70'],['approximation','#ff8f70']]){
      chartCtx.strokeStyle=color;chartCtx.fillStyle=color;chartCtx.lineWidth=key==='approximation'?1.2:2;chartCtx.setLineDash(key==='approximation'?[7,5]:[]);chartCtx.beginPath();
      rows.forEach((row,index)=>{const x=xOf(index),y=yOf(row[key]);if(index===0)chartCtx.moveTo(x,y);else chartCtx.lineTo(x,y);});chartCtx.stroke();
      if(rows.length===1){chartCtx.beginPath();chartCtx.arc(xOf(0),yOf(rows[0][key]),2.5,0,Math.PI*2);chartCtx.fill();}
    }
    chartCtx.setLineDash([]);chartCtx.fillStyle='#8f9bbb';chartCtx.fillText(`ln a: ${Math.log(state.a).toFixed(3)} · τ: ${state.tau.toExponential(2)}`,left,height-9);
  }

  function updateEraBars(d){
    const host=$('#eraBars');if(!host)return;
    const items=[[text.radiation,d.components.fractions.radiation,'#ffcf6e'],[text.matter,d.components.fractions.matter,'#6eb6ff'],[text.vacuum,d.components.fractions.vacuum,'#ff84c1'],[text.curvature,d.components.fractions.curvature,'#8d7cff']];
    host.innerHTML=items.map(([name,value,color])=>`<div class="eraBar"><span>${name}</span><div><i style="width:${Math.min(100,Math.max(0,Math.abs(value)*100))}%;background:${color}"></i></div><b>${fmt(value*100,2)} %</b></div>`).join('');
  }

  function draw(){
    drawCells();
    if(state.status!=='PASS'){
      drawChart();$('#hud').innerHTML=`<strong>${state.error?.code||state.status}</strong><br>${text.noCurve}`;
      for(const id of ['radMetric','matMetric','vacMetric','curvMetric','growthD','growthF','growthApprox','growthErr','epochNow','accelNow','eqRM','eqML','accA','qNow'])setText(id,'–');
      if($('#eraBars'))$('#eraBars').innerHTML='';
      $('#domainStatus').classList.add('invalid');$('#domainStatus').innerHTML=`<strong>${state.error?.code||state.status}</strong> · ${text.noCurve}`;
      $('#emergenceBadge').classList.add('invalid');$('#emergenceBadge').textContent=text.invalid;return;
    }
    const d=diagnosticsAt(state.a),live=liveCount();
    $('#hud').innerHTML=`Generation: ${state.generation}<br>Simulationsgitter: ${state.N}×${state.N}<br>Anzeigegitter: ${state.displayN}×${state.displayN}<br>Aktiv: ${live}<br>a: ${fmtExp(d.a,3)}<br>E: ${fmtExp(d.E,3)}<br>D: ${fmt(d.growth.D,4)}<br>f: ${fmt(d.growth.f,4)}`;
    setText('radMetric',`${fmt(100*d.components.fractions.radiation,2)} %`);setText('matMetric',`${fmt(100*d.components.fractions.matter,2)} %`);setText('vacMetric',`${fmt(100*d.components.fractions.vacuum,2)} %`);setText('curvMetric',`${fmt(100*d.components.fractions.curvature,2)} %`);
    setText('growthD',fmt(d.growth.D,5));setText('growthF',fmt(d.growth.f,5));setText('growthApprox',fmt(d.approximation,5));setText('growthErr',Number.isFinite(d.approximationError)?`${fmt(100*d.approximationError,2)} %`:'–');
    setText('epochNow',d.era);setText('accelNow',d.expansion);setText('eqRM',state.domain.epochs.radiationMatter?fmtExp(state.domain.epochs.radiationMatter,3):'–');setText('eqML',state.domain.epochs.matterVacuum?fmt(state.domain.epochs.matterVacuum,4):'–');setText('accA',state.domain.epochs.acceleration?fmt(state.domain.epochs.acceleration,4):'–');setText('qNow',fmt(d.q,4));
    updateEraBars(d);drawChart();
    const mode=$('#expMode')?.value||'lcdm',modeText=mode==='lcdm'?text.physicalMode:mode==='heuristic'?text.heuristicMode:text.staticMode;
    $('#domainStatus').classList.remove('invalid');$('#domainStatus').innerHTML=`<strong>${text.pass}</strong> · Engine ${C.VERSION} · ${text.modelLine} · ${modeText} · ${text.visualOnly}.`;
    $('#emergenceBadge').classList.remove('invalid');$('#emergenceBadge').textContent=text.engine;
  }

  function updateOutputs(){
    setText('speedOut',$('#speed')?.value||'–');setText('densityOut',`${$('#density')?.value||'–'} %`);setText('noiseOut',$('#noise')?.value||'–');setText('h0Out',fmt(Number($('#h0')?.value),1));setText('omOut',fmt(Number($('#om')?.value),3));setText('orOut',fmt(Number($('#or')?.value),6));setText('olOut',fmt(Number($('#ol')?.value),6));setText('timeOut',$('#timeScale')?.value||'–');setText('expandOut',$('#expand')?.value||'–');
    const mode=$('#expMode')?.value||'lcdm';$('#lcdmBox')?.classList.toggle('on',mode==='lcdm');$('#heurBox')?.classList.toggle('on',mode==='heuristic');
  }

  function cosmologyChanged({resetScale=false}={}){
    try{rebuildCosmology({resetScale});recordHistory();draw();}
    catch(error){
      state.status=error?.code||'ERROR';state.error={code:error?.code||'ERROR',message:error?.message||String(error),detail:error?.detail||{}};
      state.params=(()=>{try{return readParams();}catch{return null;}})();state.domain=null;state.growth=null;state.timeMap=null;state.history=[];state.revision++;draw();
    }
    globalThis.dispatchEvent(new CustomEvent('universelab:emergence-update',{detail:snapshot()}));return snapshot();
  }

  function scheduleCosmology(){clearTimeout(timer);updateOutputs();timer=setTimeout(()=>cosmologyChanged(),90);}
  function togglePlay(){state.running=!state.running;const button=$('#play');if(button)button.textContent=state.running?text.pause:text.start;return state.running;}
  function animationFrame(timestamp){
    if(!state.lastFrame)state.lastFrame=timestamp;
    const elapsed=Math.min(250,timestamp-state.lastFrame);state.lastFrame=timestamp;
    if(state.running){
      const rate=Math.max(1,Number($('#speed')?.value||10)),interval=1000/rate;state.accumulator+=elapsed;
      let guard=0;while(state.accumulator>=interval&&guard<8){stepCells();state.accumulator-=interval;guard++;}
    }
    requestAnimationFrame(animationFrame);
  }

  function cellFromPointer(event){
    const rect=simCanvas.getBoundingClientRect();
    const renderN=state.displayN||state.N,xDisplay=Math.floor((event.clientX-rect.left)/rect.width*renderN),yDisplay=Math.floor((event.clientY-rect.top)/rect.height*renderN);
    const x=Math.min(state.N-1,Math.floor(xDisplay*state.N/renderN)),y=Math.min(state.N-1,Math.floor(yDisplay*state.N/renderN));
    if(x>=0&&x<state.N&&y>=0&&y<state.N){state.cells[y*state.N+x]=1;drawCells();}
  }

  function applySavedInputs(payload){
    const source=payload&&typeof payload.inputs==='object'&&payload.inputs?payload.inputs:
      payload&&typeof payload.settings==='object'&&payload.settings?payload.settings:{};
    for(const[id,value]of Object.entries(source)){
      const node=document.getElementById(id);
      if(node&&value!=null)node.value=String(value);
    }
    return payload?.inputs?'CURRENT_INPUTS':payload?.settings?'LEGACY_SETTINGS_TO_INPUTS':'NO_SETTINGS';
  }

  function saveState(){
    const payload={schema:STATE_SCHEMA,savedAt:new Date().toISOString(),N:state.N,generation:state.generation,a:state.a,tau:state.tau,cells:Array.from(state.cells),inputs:Object.fromEntries([...parameterIds,...controlIds,'expMode','preset','rule'].map(id=>[id,document.getElementById(id)?.value]))};
    localStorage.setItem(STORAGE_KEY,JSON.stringify(payload));$('#domainStatus').dataset.notice=text.saved;return payload;
  }

  function loadState(){
    const raw=localStorage.getItem(STORAGE_KEY);if(!raw){$('#domainStatus').dataset.notice=text.missingSave;return null;}
    const payload=JSON.parse(raw),migration=applySavedInputs(payload);
    updateOutputs();cosmologyChanged();
    restoreSimulationGrid(payload.N,payload.cells);
    state.generation=Math.max(0,Number(payload.generation)||0);
    state.a=clamp(Number(payload.a)||state.growth?.aInit||1e-3,state.growth?.aInit||1e-3,1);
    state.tau=state.timeMap?tauAtScaleFactor(state.a,state.timeMap):0;
    state.history=[];state.lastLoad={sourceSchema:payload.schema||'legacy-pre-schema',migration,legacyHistoryDiscarded:Array.isArray(payload.history)};
    recordHistory();draw();return snapshot();
  }

  function exportCsv(){
    const columns=['generation','N','displayN','live','density','tau','a','E','q','radiation','matter','curvature','vacuum','D','f','approximation','era'];
    const lines=[columns.join(',')];for(const row of state.history)lines.push(columns.map(key=>JSON.stringify(row[key]??'')).join(','));
    const blob=new Blob([lines.join('\n')],{type:'text/csv;charset=utf-8'}),link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download='UniverseLab_Emergence_Diagnostics.csv';link.click();setTimeout(()=>URL.revokeObjectURL(link.href),1000);
  }

  function resetCosmology(){
    for(const[id,value]of Object.entries({h0:67.4,om:.315,or:.000092,ol:.684908,timeScale:25})){const node=document.getElementById(id);if(node)node.value=String(value);}
    updateOutputs();return cosmologyChanged({resetScale:true});
  }

  function setInputs(values,{resetScale=false}={}){
    for(const[id,value]of Object.entries(values)){const node=document.getElementById(id);if(!node)throw new Error(`MISSING_INPUT:${id}`);node.value=String(value);}
    updateOutputs();return cosmologyChanged({resetScale});
  }

  function probeScaleFactor(a){return diagnosticsAt(a);}
  function snapshot(){
    return JSON.parse(JSON.stringify({version:VERSION,engineVersion:C?.VERSION||null,status:state.status,running:state.running,generation:state.generation,N:state.N,displayN:state.displayN,live:liveCount(),cellHash:cellHash(),a:state.a,tau:state.tau,revision:state.revision,error:state.error,params:state.params,model:state.model,domain:state.domain,growth:state.growth?{model:state.growth.model,aInit:state.growth.aInit,steps:state.growth.steps}:null,lastLoad:state.lastLoad,cellularDynamicsIndependent:state.cellularDynamicsIndependent,gridResamplingVisualOnly:state.gridResamplingVisualOnly,expMode:$('#expMode')?.value||null}));
  }

  function bind(){
    for(const id of parameterIds)document.getElementById(id)?.addEventListener('input',scheduleCosmology,{passive:true});
    for(const id of controlIds)document.getElementById(id)?.addEventListener('input',()=>{updateOutputs();draw();},{passive:true});
    $('#expMode')?.addEventListener('change',()=>{updateOutputs();draw();});$('#play')?.addEventListener('click',togglePlay);$('#step')?.addEventListener('click',stepCells);$('#seed')?.addEventListener('click',()=>seed());$('#clear')?.addEventListener('click',clearCells);$('#save')?.addEventListener('click',saveState);$('#load')?.addEventListener('click',loadState);$('#export')?.addEventListener('click',exportCsv);
    $('#install')?.addEventListener('click',async()=>{if(!state.installPrompt)return;state.installPrompt.prompt();await state.installPrompt.userChoice;state.installPrompt=null;$('#install').hidden=true;});
    if(simCanvas)simCanvas.onpointerdown=event=>{if(event.button!=null&&event.button!==0)return;cellFromPointer(event);};
    globalThis.addEventListener('beforeinstallprompt',event=>{event.preventDefault();state.installPrompt=event;if($('#install'))$('#install').hidden=false;});globalThis.addEventListener('resize',draw);
  }

  function init(){
    updateOutputs();setText('separationNote',text.separationLong);bind();cosmologyChanged({resetScale:true});seed($('#preset')?.value||'random');requestAnimationFrame(animationFrame);
    setTimeout(()=>{document.title=language==='en'?'UniverseLab 1.0 · Emergence':'UniverseLab 1.0 · Emergenz';draw();},0);
    if('serviceWorker'in navigator)navigator.serviceWorker.register('./sw.js').catch(()=>{});
  }

  globalThis.UniverseLabEmergence=Object.freeze({VERSION,get status(){return state.status;},get running(){return state.running;},step:stepCells,seed,clear:clearCells,update:cosmologyChanged,resetCosmology,setInputs,probeScaleFactor,snapshot,save:saveState,load:loadState});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
