(()=>{
  'use strict';

  const VERSION='2.0.0';
  const WCDM_BACKGROUND_E_Z1=1.8866898001885484;
  const WCDM_GROWTH_D_Z1=0.6221646187388952;
  const root=window;
  const C=root.UniverseLabCosmology;
  const lang=(document.documentElement.lang||'de').toLowerCase().startsWith('en')?'en':'de';

  const ui={
    de:{
      missingEngine:'Kanonischer Kosmologie-Kern nicht geladen',
      blocked:'BLOCKIERT',
      pass:'INTERN PASS',
      enginePrefix:'Engine',
      maxRelative:'max. normierter Fehler',
      tests:{
        normalization_E0:['Normierung E(0)=1','|E(0)−1| ≤ 10⁻¹²'],
        density_closure:['Dichteabschluss inklusive Ωₖ','Ωᵣ+Ωₘ+ΩDE+Ωₖ = 1'],
        wcdm_background_reference:['Gültige wCDM-Hintergrundreferenz','w=−0,8, z=1: E(z) gegen unabhängigen Anker'],
        eds_age:['Einstein–de-Sitter-Alter','t₀ = 2/(3H₀)'],
        small_z_hubble_law:['Kleine-z-Hubble-Grenze','D_C/(D_H z) → 1'],
        radial_distance_monotonic:['Radiale komovierende Distanz monoton','D_C(1) > D_C(0,5)'],
        flat_transverse_identity:['Flache Distanzidentität','Ωₖ=0 ⇒ D_M=D_C'],
        open_curvature_mapping:['Offene Krümmungsabbildung','Ωₖ>0 ⇒ D_M>D_C'],
        closed_curvature_mapping:['Geschlossene Krümmungsabbildung','Ωₖ<0 ⇒ D_M<D_C'],
        etherington_reciprocity:['Etherington-Reziprozität','D_L/[(1+z)²D_A] = 1'],
        invalid_background_fail_closed:['Ungültige E²-Domäne fail-closed','E²≤0 ⇒ INVALID_BACKGROUND_DOMAIN'],
        invalid_bridge_fail_closed:['Ungültige Brückendomäne fail-closed','1+Δ≤0 ⇒ INVALID_BRIDGE_DOMAIN'],
        bridge_product_degeneracy:['βτ·𝓘B-Produktdegeneration','gleiches Produkt ⇒ gleiche Hintergrundkurve'],
        lcdm_growth_reference:['ΛCDM-Wachstumsreferenz','max. relativer D-Fehler ≤ 3×10⁻⁹'],
        wcdm_growth_reference:['Gültige wCDM-Wachstumsreferenz','w=−0,8, z=1: relativer D-Fehler ≤ 5×10⁻⁸'],
        eds_growth_limit:['Einstein–de-Sitter-Wachstumsgrenze','D=a und f=1'],
        bridge_growth_firewall:['Brücken-Wachstumsfirewall','UNRELEASED_GROWTH_MAP']
      }
    },
    en:{
      missingEngine:'Canonical cosmology engine not loaded',
      blocked:'BLOCKED',
      pass:'INTERNAL PASS',
      enginePrefix:'Engine',
      maxRelative:'maximum normalized error',
      tests:{
        normalization_E0:['Normalization E(0)=1','|E(0)−1| ≤ 10⁻¹²'],
        density_closure:['Density closure including Ωₖ','Ωᵣ+Ωₘ+ΩDE+Ωₖ = 1'],
        wcdm_background_reference:['Valid wCDM background reference','w=−0.8, z=1: E(z) against independent anchor'],
        eds_age:['Einstein–de Sitter age','t₀ = 2/(3H₀)'],
        small_z_hubble_law:['Small-z Hubble limit','D_C/(D_H z) → 1'],
        radial_distance_monotonic:['Radial comoving distance monotonic','D_C(1) > D_C(0.5)'],
        flat_transverse_identity:['Flat distance identity','Ωₖ=0 ⇒ D_M=D_C'],
        open_curvature_mapping:['Open-curvature mapping','Ωₖ>0 ⇒ D_M>D_C'],
        closed_curvature_mapping:['Closed-curvature mapping','Ωₖ<0 ⇒ D_M<D_C'],
        etherington_reciprocity:['Etherington reciprocity','D_L/[(1+z)²D_A] = 1'],
        invalid_background_fail_closed:['Invalid E² domain fails closed','E²≤0 ⇒ INVALID_BACKGROUND_DOMAIN'],
        invalid_bridge_fail_closed:['Invalid bridge domain fails closed','1+Δ≤0 ⇒ INVALID_BRIDGE_DOMAIN'],
        bridge_product_degeneracy:['βτ·𝓘B product degeneracy','same product ⇒ same background curve'],
        lcdm_growth_reference:['ΛCDM growth reference','maximum relative D error ≤ 3×10⁻⁹'],
        wcdm_growth_reference:['Valid wCDM growth reference','w=−0.8, z=1: relative D error ≤ 5×10⁻⁸'],
        eds_growth_limit:['Einstein–de Sitter growth limit','D=a and f=1'],
        bridge_growth_firewall:['Bridge growth firewall','UNRELEASED_GROWTH_MAP']
      }
    }
  }[lang];

  const state={status:'idle',results:[],maxError:0,failed:0,passed:0,engineVersion:C?.VERSION||null};
  const byId=id=>document.getElementById(id);
  const finite=x=>Number.isFinite(Number(x));
  const fmt=x=>{
    if(typeof x==='string')return x;
    if(!Number.isFinite(x))return String(x);
    const ax=Math.abs(x);
    if(ax!==0&&(ax<1e-4||ax>=1e6))return x.toExponential(6);
    return x.toLocaleString(lang==='de'?'de-DE':'en-US',{maximumSignificantDigits:10});
  };
  const errorOf=(value,target,mode)=>mode==='absolute'||target===0?Math.abs(value-target):Math.abs((value-target)/target);

  function numeric(id,value,target,tolerance,{mode='relative',display=value,detail={}}={}){
    const error=errorOf(value,target,mode);
    return {id,kind:'numeric',ok:finite(value)&&finite(target)&&error<=tolerance,value,target,error,tolerance,display,code:null,detail};
  }
  function predicate(id,ok,value,{display=value,detail={}}={}){
    return {id,kind:'predicate',ok:Boolean(ok),value,error:ok?0:Infinity,tolerance:0,display,code:typeof value==='string'?value:null,detail};
  }
  function caughtCode(fn){
    try{fn();return null;}catch(error){return error?.code||error?.name||String(error);}
  }

  function execute(){
    if(!C)throw new Error(ui.missingEngine);
    const ref={H0:67.4,Om:.315,Ode:.684908,Or:9.2e-5,w:-1,sigma8:.811};
    const p=C.normalizeParams(ref);
    const results=[];

    results.push(numeric('normalization_E0',C.E(0,p,'lcdm'),1,1e-12));
    results.push(numeric('density_closure',p.Or+p.Om+p.Ode+p.Ok,1,1e-14,{mode:'absolute'}));

    const wRef={...ref,w:-.8};
    const wE1=C.E(1,wRef,'wcdm');
    results.push(numeric('wcdm_background_reference',wE1,WCDM_BACKGROUND_E_Z1,1e-12,{detail:{z:1,w:-.8}}));

    const eds={H0:70,Om:1,Ode:0,Or:0,w:-1,sigma8:.8};
    const edsAge=C.ageGyr(eds,'lcdm',{aMin:1e-10,n:8192});
    const edsExpected=C.hubbleTimeGyr(eds)*2/3;
    results.push(numeric('eds_age',edsAge,edsExpected,2e-8,{detail:{expected:edsExpected}}));

    const zSmall=1e-5;
    const dcSmall=C.radialComovingDistance(zSmall,p,'lcdm');
    const hubbleApprox=C.hubbleDistance(p)*zSmall;
    results.push(numeric('small_z_hubble_law',dcSmall,hubbleApprox,1e-5,{detail:{z:zSmall}}));

    const dc05=C.radialComovingDistance(.5,p,'lcdm');
    const dc1=C.radialComovingDistance(1,p,'lcdm');
    results.push(predicate('radial_distance_monotonic',dc1>dc05,dc1/dc05,{detail:{dc05,dc1}}));

    const dmFlat=C.transverseComovingDistance(1,p,'lcdm');
    results.push(numeric('flat_transverse_identity',dmFlat,dc1,1e-12));

    const open=C.normalizeParams({...ref,Om:.2,Ode:.5});
    const dcOpen=C.radialComovingDistance(2.33,open,'lcdm');
    const dmOpen=C.transverseComovingDistance(2.33,open,'lcdm');
    results.push(predicate('open_curvature_mapping',dmOpen>dcOpen,dmOpen/dcOpen-1,{detail:{Ok:open.Ok,dc:dcOpen,dm:dmOpen}}));

    const closed=C.normalizeParams({...ref,Om:.5,Ode:.8});
    const dcClosed=C.radialComovingDistance(2.33,closed,'lcdm');
    const dmClosed=C.transverseComovingDistance(2.33,closed,'lcdm');
    results.push(predicate('closed_curvature_mapping',dmClosed<dcClosed,dmClosed/dcClosed-1,{detail:{Ok:closed.Ok,dc:dcClosed,dm:dmClosed}}));

    let etherMax=0;
    for(const z of [.01,.5,1,2.33])etherMax=Math.max(etherMax,Math.abs(C.etheringtonRatio(z,p,'lcdm')-1));
    results.push(numeric('etherington_reciprocity',etherMax,0,1e-12,{mode:'absolute',display:etherMax}));

    const badW={H0:67.4,Om:.1,Ode:1.2,Or:9.2e-5,w:-1.5,sigma8:.811};
    const badWDomain=C.validateBackgroundDomain(badW,'wcdm',{zMax:5,samples:20000});
    const badWCode=caughtCode(()=>C.E(badWDomain.z??1.3,badW,'wcdm'));
    results.push(predicate('invalid_background_fail_closed',!badWDomain.ok&&badWDomain.code==='INVALID_BACKGROUND_DOMAIN'&&badWCode==='INVALID_BACKGROUND_DOMAIN',badWCode||badWDomain.code,{detail:badWDomain}));

    const badBridge={...ref,betaTau:-3,IB:1,Rchi:1};
    const badBridgeDomain=C.validateBackgroundDomain(badBridge,'bridge',{zMax:5,samples:8192});
    const badBridgeCode=caughtCode(()=>C.E(badBridgeDomain.z??5,badBridge,'bridge'));
    results.push(predicate('invalid_bridge_fail_closed',!badBridgeDomain.ok&&badBridgeDomain.code==='INVALID_BRIDGE_DOMAIN'&&badBridgeCode==='INVALID_BRIDGE_DOMAIN',badBridgeCode||badBridgeDomain.code,{detail:badBridgeDomain}));

    const b1={...ref,betaTau:.05,IB:.4,Rchi:1};
    const b2={...ref,betaTau:.1,IB:.2,Rchi:1};
    let bridgeMax=0;
    for(const z of [0,.5,1,3]){
      const a=C.E(z,b1,'bridge'),b=C.E(z,b2,'bridge');
      bridgeMax=Math.max(bridgeMax,Math.abs((a-b)/a));
    }
    results.push(numeric('bridge_product_degeneracy',bridgeMax,0,1e-13,{mode:'absolute'}));

    const growth=C.solveGrowth(p,'lcdm',{steps:4000});
    const expected=new Map([[.5,.7689433284179076],[1,.6068047406056298],[2,.4172414795427676],[3,.31553801878444504]]);
    let growthMax=0;
    const growthRows=[];
    for(const [z,target] of expected){
      const got=C.growthAtZ(z,growth).D;
      growthMax=Math.max(growthMax,Math.abs((got-target)/target));
      growthRows.push({z,got,target});
    }
    results.push(numeric('lcdm_growth_reference',growthMax,0,3e-9,{mode:'absolute',detail:{rows:growthRows}}));

    const wGrowth=C.solveGrowth(wRef,'wcdm',{steps:4000});
    const wGrowthD1=C.growthAtZ(1,wGrowth).D;
    results.push(numeric('wcdm_growth_reference',wGrowthD1,WCDM_GROWTH_D_Z1,5e-8,{detail:{z:1,w:-.8,reference:WCDM_GROWTH_D_Z1}}));

    const edsGrowth=C.solveGrowth(eds,'lcdm',{steps:2500,aInit:1e-3});
    let edsGrowthMax=0;
    const edsRows=[];
    for(const z of [0,.5,1,3,9]){
      const got=C.growthAtZ(z,edsGrowth),a=1/(1+z);
      const err=Math.max(Math.abs(got.D-a),Math.abs(got.f-1));
      edsGrowthMax=Math.max(edsGrowthMax,err);
      edsRows.push({z,D:got.D,f:got.f,a});
    }
    results.push(numeric('eds_growth_limit',edsGrowthMax,0,2e-6,{mode:'absolute',detail:{rows:edsRows}}));

    const growthFirewall=caughtCode(()=>C.solveGrowth({...ref,betaTau:.05,IB:.4},'bridge'));
    results.push(predicate('bridge_growth_firewall',growthFirewall==='UNRELEASED_GROWTH_MAP',growthFirewall));
    return results;
  }

  function render(){
    const body=byId('rows');
    if(!body)return;
    body.textContent='';
    for(const result of state.results){
      const [name,criterion]=ui.tests[result.id]||[result.id,''];
      const tr=document.createElement('tr');
      tr.dataset.testId=result.id;
      tr.dataset.testStatus=result.ok?'PASS':'FAIL';
      const nameCell=document.createElement('td');
      const strong=document.createElement('strong');strong.textContent=name;nameCell.appendChild(strong);
      const statusCell=document.createElement('td');
      const badge=document.createElement('span');badge.className=`state ${result.ok?'pass':'fail'}`;badge.textContent=result.ok?'PASS':'FAIL';statusCell.appendChild(badge);
      const valueCell=document.createElement('td');
      const code=document.createElement('code');code.textContent=fmt(result.display);valueCell.appendChild(code);
      const criterionCell=document.createElement('td');criterionCell.textContent=criterion;
      tr.append(nameCell,statusCell,valueCell,criterionCell);body.appendChild(tr);
    }
    byId('passed').textContent=`${state.passed}/${state.results.length}`;
    byId('failed').textContent=String(state.failed);
    byId('maxerr').textContent=Number.isFinite(state.maxError)?state.maxError.toExponential(2):'∞';
    byId('release').textContent=state.failed?ui.blocked:ui.pass;
    byId('release').style.color=state.failed?'var(--bad)':'var(--good)';
    const engine=byId('engine');if(engine)engine.textContent=`${ui.enginePrefix} ${state.engineVersion||'MISSING'}`;
  }

  function run(){
    state.status='running';
    try{
      state.results=execute();
    }catch(error){
      state.results=[predicate('engine_fatal',false,error?.code||error?.message||String(error),{detail:{stack:String(error?.stack||error)}})];
      ui.tests.engine_fatal=[ui.missingEngine,ui.missingEngine];
    }
    state.failed=state.results.filter(x=>!x.ok).length;
    state.passed=state.results.length-state.failed;
    state.maxError=state.results.reduce((m,x)=>Number.isFinite(x.error)?Math.max(m,x.error):m,0);
    state.status='complete';
    render();
    root.dispatchEvent(new CustomEvent('universelab:validation-complete',{detail:snapshot()}));
    return snapshot();
  }

  function snapshot(){
    return {
      version:VERSION,
      engineVersion:state.engineVersion,
      status:state.status,
      passed:state.passed,
      failed:state.failed,
      maxError:state.maxError,
      results:state.results.map(({id,kind,ok,value,target,error,tolerance,code,detail})=>({id,kind,ok,value,target,error:Number.isFinite(error)?error:null,tolerance,code,detail}))
    };
  }

  const api={VERSION,get status(){return state.status;},get results(){return snapshot().results;},run,snapshot};
  root.UniverseLabValidation=api;
  const init=()=>{const button=byId('run');if(button)button.addEventListener('click',run);run();};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
