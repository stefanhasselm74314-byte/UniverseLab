import { chromium } from 'playwright';
import fs from 'node:fs';

const BASE=process.env.UNIVERSELAB_BASE_URL||'http://127.0.0.1:8000/';
const report={schema:'universelab.emergence-canonical-growth-adapter-audit.v1',timestamp_utc:new Date().toISOString(),base_url:BASE,status:'PASS',checks:[],errors:[]};
function add(name,ok,detail={}){report.checks.push({name,ok:Boolean(ok),...detail});if(!ok)report.status='FAIL';}
function close(a,b,rtol=1e-10,atol=1e-12){return Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=atol+rtol*Math.max(Math.abs(a),Math.abs(b));}
async function openPage(context,path,label){
  const page=await context.newPage(),errors=[],httpErrors=[];
  page.on('pageerror',error=>errors.push(String(error)));
  page.on('console',message=>{if(message.type()==='error')errors.push(`console: ${message.text()}`);});
  page.on('response',response=>{if(response.status()>=400)httpErrors.push({status:response.status(),url:response.url()});});
  const url=new URL(path,BASE);url.searchParams.set('ul_emergence_audit',String(Date.now()));
  const response=await page.goto(url.href,{waitUntil:'networkidle',timeout:45000});
  if(!response?.ok())throw new Error(`${label}: HTTP ${response?.status()} ${url.href}`);
  await page.waitForFunction(()=>window.UniverseLabEmergence?.snapshot().revision>=1,{timeout:20000});
  return{page,errors,httpErrors,label};
}

const browser=await chromium.launch({headless:true});
try{
  const context=await browser.newContext({viewport:{width:1280,height:900},locale:'de-DE'});
  const de=await openPage(context,'emergence.html','de');

  const initial=await de.page.evaluate(()=>({
    snapshot:window.UniverseLabEmergence.snapshot(),title:document.title,canvases:document.querySelectorAll('canvas').length,
    outputs:Object.fromEntries(['radMetric','matMetric','vacMetric','curvMetric','growthD','growthF','growthApprox','growthErr','epochNow','accelNow','eqRM','eqML','accA','qNow'].map(id=>[id,document.getElementById(id)?.textContent?.trim()])),
    eraBars:document.getElementById('eraBars')?.textContent?.trim()||'',statusText:document.getElementById('domainStatus')?.textContent||''
  }));
  add('default_runtime_pass',initial.snapshot.status==='PASS'&&initial.snapshot.engineVersion==='1.0.0'&&initial.snapshot.version==='1.0.3'&&initial.snapshot.cellularDynamicsIndependent===true&&initial.snapshot.gridResamplingVisualOnly===true&&initial.canvases===2&&Object.values(initial.outputs).every(value=>value&&value!=='–')&&initial.eraBars.length>0&&/PASS/.test(initial.statusText),initial);
  add('exact_flat_reference_state',close(initial.snapshot.params.Om,.315,0,1e-12)&&close(initial.snapshot.params.Or,.000092,0,1e-12)&&close(initial.snapshot.params.Ode,.684908,0,1e-12)&&close(initial.snapshot.params.Ok,0,0,1e-12),{params:initial.snapshot.params});
  add('exact_present_endpoint',initial.snapshot.domain?.displayTime?.endpoint?.x===0&&initial.snapshot.domain?.displayTime?.endpoint?.a===1,{endpoint:initial.snapshot.domain?.displayTime?.endpoint});

  const beforeSliderRevision=initial.snapshot.revision;
  await de.page.evaluate(()=>{const node=document.getElementById('h0');node.value='68.2';node.dispatchEvent(new Event('input',{bubbles:true}));});
  await de.page.waitForFunction(rev=>window.UniverseLabEmergence.snapshot().revision>rev,beforeSliderRevision,{timeout:5000});
  const sliderResult=await de.page.evaluate(()=>({snapshot:window.UniverseLabEmergence.snapshot(),value:document.getElementById('h0').value,output:document.getElementById('h0Out').textContent}));
  add('parameter_slider_event_rebuilds_cosmology',sliderResult.snapshot.status==='PASS'&&close(sliderResult.snapshot.params.H0,68.2,0,1e-12)&&sliderResult.snapshot.revision>beforeSliderRevision&&/68[,.]2/.test(sliderResult.output),sliderResult);
  await de.page.evaluate(()=>window.UniverseLabEmergence.resetCosmology());

  const probe=await de.page.evaluate(()=>{
    const A=window.UniverseLabEmergence,C=window.UniverseLabCosmology,s=A.snapshot(),a=.5,z=1/a-1,p=s.params;
    const directGrowth=C.growthAtZ(z,C.solveGrowth(p,'lcdm',{steps:4000})),d=A.probeScaleFactor(a);
    return{adapter:{E:d.E,q:d.q,D:d.growth.D,f:d.growth.f,a:d.a,z:d.z},direct:{E:C.E(z,p,'lcdm'),q:C.q(z,p,'lcdm'),D:directGrowth.D,f:directGrowth.f},closure:d.components.fractions.radiation+d.components.fractions.matter+d.components.fractions.curvature+d.components.fractions.vacuum};
  });
  add('canonical_probe_identity',close(probe.adapter.E,probe.direct.E)&&close(probe.adapter.q,probe.direct.q)&&close(probe.adapter.D,probe.direct.D)&&close(probe.adapter.f,probe.direct.f)&&close(probe.closure,1,1e-12,1e-12),probe);

  const staticStep=await de.page.evaluate(()=>{
    const mode=document.getElementById('expMode');mode.value='off';mode.dispatchEvent(new Event('change',{bubbles:true}));
    const before=window.UniverseLabEmergence.snapshot(),after=window.UniverseLabEmergence.step();return{before,after};
  });
  add('cellular_step_does_not_modify_static_cosmology',staticStep.after.generation===staticStep.before.generation+1&&close(staticStep.after.a,staticStep.before.a,0,0)&&close(staticStep.after.tau,staticStep.before.tau,0,0)&&staticStep.after.N===staticStep.before.N&&staticStep.after.status==='PASS',staticStep);

  const independence=await de.page.evaluate(()=>{
    const A=window.UniverseLabEmergence;
    const N=40,cells=Array(N*N).fill(0);
    for(const [x,y] of [[2,1],[3,2],[1,3],[2,3],[3,3],[12,12],[13,12],[14,12]])cells[y*N+x]=1;
    const baseInputs={h0:'67.4',om:'0.315',or:'0.000092',ol:'0.684908',speed:'10',density:'22',noise:'0',timeScale:'100',expand:'100',preset:'random',rule:'B3/S23'};
    const run=mode=>{
      localStorage.setItem('universelab',JSON.stringify({schema:'universelab.emergence-state.v2',N,generation:0,a:.05,tau:0,cells,inputs:{...baseInputs,expMode:mode}}));
      const loaded=A.load();
      const after=A.step();
      return{loaded,after};
    };
    return{off:run('off'),lcdm:run('lcdm')};
  });
  add('deterministic_cell_update_independent_of_cosmology_mode',independence.off.after.N===40&&independence.lcdm.after.N===40&&independence.off.after.cellHash===independence.lcdm.after.cellHash&&independence.off.after.generation===1&&independence.lcdm.after.generation===1&&close(independence.off.after.a,.05,0,1e-12)&&independence.lcdm.after.a>.05,independence);
  add('display_resampling_does_not_mutate_simulation_grid',independence.lcdm.after.displayN>independence.lcdm.after.N&&independence.lcdm.after.N===independence.lcdm.loaded.N&&independence.off.after.displayN===independence.off.after.N,{off:{N:independence.off.after.N,displayN:independence.off.after.displayN},lcdm:{N:independence.lcdm.after.N,displayN:independence.lcdm.after.displayN}});

  await de.page.evaluate(()=>window.UniverseLabEmergence.resetCosmology());
  const physicalStep=await de.page.evaluate(()=>{
    const A=window.UniverseLabEmergence,C=window.UniverseLabCosmology,mode=document.getElementById('expMode'),timeScale=document.getElementById('timeScale');
    mode.value='lcdm';mode.dispatchEvent(new Event('change',{bubbles:true}));timeScale.value='100';timeScale.dispatchEvent(new Event('input',{bubbles:true}));
    const before=A.snapshot(),after=A.step(),x0=Math.log(before.a),x1=Math.log(after.a),n=8192,h=(x1-x0)/n;
    const integrand=x=>1/C.E(Math.max(0,Math.exp(-Math.min(0,x))-1),before.params,'lcdm');
    let sum=integrand(x0)+integrand(x1);for(let i=1;i<n;i++)sum+=(i%2?4:2)*integrand(x0+i*h);
    return{before,after,expectedDeltaTau:.002,integratedDeltaTau:sum*h/3};
  });
  add('lcdm_display_time_advances_scale_factor',physicalStep.after.generation===physicalStep.before.generation+1&&physicalStep.after.a>physicalStep.before.a&&physicalStep.after.a<=1&&physicalStep.after.N===physicalStep.before.N&&physicalStep.after.status==='PASS',physicalStep);
  add('maximum_time_amplification_stays_in_domain',close(physicalStep.after.tau-physicalStep.before.tau,.002,0,1e-15)&&close(physicalStep.integratedDeltaTau,.002,2e-6,1e-10)&&physicalStep.after.error===null,physicalStep);

  await de.page.evaluate(()=>{document.getElementById('ol').max='5';});
  const invalid=await de.page.evaluate(()=>{
    const A=window.UniverseLabEmergence,before=A.snapshot(),blocked=A.setInputs({om:.05,or:0,ol:4},{resetScale:true}),generationBefore=blocked.generation,aBefore=blocked.a,NBefore=blocked.N,afterCellStep=A.step();
    return{before,blocked,afterCellStep,generationBefore,aBefore,NBefore,
      outputs:Object.fromEntries(['radMetric','matMetric','vacMetric','curvMetric','growthD','growthF','growthApprox','growthErr','epochNow','accelNow','eqRM','eqML','accA','qNow'].map(id=>[id,document.getElementById(id)?.textContent?.trim()])),
      eraBarsText:document.getElementById('eraBars')?.textContent?.trim()||'',statusText:document.getElementById('domainStatus')?.textContent||'',bodyText:document.body.innerText};
  });
  add('invalid_background_fails_closed',invalid.blocked.status==='INVALID_BACKGROUND_DOMAIN'&&invalid.blocked.error?.code==='INVALID_BACKGROUND_DOMAIN'&&invalid.blocked.growth===null&&invalid.blocked.domain===null&&Object.values(invalid.outputs).every(value=>value==='–')&&invalid.eraBarsText===''&&/INVALID_BACKGROUND_DOMAIN/.test(invalid.statusText)&&!/(?:NaN|Infinity)/.test(invalid.bodyText),invalid);
  add('cellular_automaton_remains_independent_under_invalid_cosmology',invalid.afterCellStep.generation===invalid.generationBefore+1&&invalid.afterCellStep.N===invalid.NBefore&&close(invalid.afterCellStep.a,invalid.aBefore,0,0)&&invalid.afterCellStep.status==='INVALID_BACKGROUND_DOMAIN',{generationBefore:invalid.generationBefore,generationAfter:invalid.afterCellStep.generation,NBefore:invalid.NBefore,NAfter:invalid.afterCellStep.N,aBefore:invalid.aBefore,aAfter:invalid.afterCellStep.a,status:invalid.afterCellStep.status});

  const legacy=await de.page.evaluate(()=>{
    const A=window.UniverseLabEmergence,N=40,cells=Array(N*N).fill(0);for(const [x,y] of [[1,0],[2,1],[0,2],[1,2],[2,2]])cells[y*N+x]=1;
    localStorage.setItem('universelab',JSON.stringify({N,generation:7,cells,a:.1,tau:.03,history:[[0,40,5]],settings:{h0:'70',om:'0.3',or:'0.000092',ol:'0.699908',speed:'7',density:'17',noise:'0',timeScale:'12',expand:'22',expMode:'off',preset:'glider',rule:'B3/S23'}}));
    const loaded=A.load();
    return{loaded,controls:Object.fromEntries(['h0','om','or','ol','speed','density','noise','timeScale','expand','expMode','preset','rule'].map(id=>[id,document.getElementById(id).value]))};
  });
  add('legacy_settings_payload_migrates_explicitly',legacy.loaded.status==='PASS'&&legacy.loaded.lastLoad?.sourceSchema==='legacy-pre-schema'&&legacy.loaded.lastLoad?.migration==='LEGACY_SETTINGS_TO_INPUTS'&&legacy.loaded.lastLoad?.legacyHistoryDiscarded===true&&legacy.loaded.N===40&&legacy.loaded.generation===7&&close(legacy.loaded.params.H0,70,0,1e-12)&&close(legacy.loaded.params.Om,.3,0,1e-12)&&close(legacy.loaded.params.Ode,.699908,0,1e-12)&&legacy.controls.speed==='7'&&legacy.controls.density==='17'&&legacy.controls.expMode==='off'&&legacy.controls.preset==='glider',legacy);

  const recovered=await de.page.evaluate(()=>window.UniverseLabEmergence.resetCosmology());
  add('reset_recovers_reference_state',recovered.status==='PASS'&&close(recovered.params.Om,.315,0,1e-12)&&close(recovered.params.Or,.000092,0,1e-12)&&close(recovered.params.Ode,.684908,0,1e-12)&&close(recovered.params.Ok,0,0,1e-12)&&recovered.domain?.displayTime?.endpoint?.x===0&&recovered.domain?.displayTime?.endpoint?.a===1&&recovered.growth?.model==='lcdm'&&recovered.tau===0,recovered);

  const en=await openPage(context,'emergence-en.html','en');
  const parity=await en.page.evaluate(()=>({snapshot:window.UniverseLabEmergence.snapshot(),probe:window.UniverseLabEmergence.probeScaleFactor(.5),lang:document.documentElement.lang,title:document.title,canvases:document.querySelectorAll('canvas').length,separation:document.getElementById('separationNote')?.textContent||''}));
  add('de_en_runtime_parity',parity.snapshot.status==='PASS'&&parity.snapshot.engineVersion==='1.0.0'&&parity.snapshot.version==='1.0.3'&&parity.lang==='en'&&/Emergence/.test(parity.title)&&parity.canvases===2&&close(parity.probe.E,probe.adapter.E)&&close(parity.probe.q,probe.adapter.q)&&close(parity.probe.growth.D,probe.adapter.D)&&close(parity.probe.growth.f,probe.adapter.f)&&/cellular automaton/i.test(parity.separation),parity);

  add('no_browser_or_http_errors',de.errors.length===0&&de.httpErrors.length===0&&en.errors.length===0&&en.httpErrors.length===0,{de_errors:de.errors,de_http_errors:de.httpErrors,en_errors:en.errors,en_http_errors:en.httpErrors});
  await de.page.close();await en.page.close();await context.close();
}catch(error){report.status='FAIL';report.errors.push(String(error?.stack||error));}
finally{await browser.close();}

fs.writeFileSync('emergence-canonical-growth-adapter-report.json',JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
if(report.status!=='PASS')process.exit(1);
