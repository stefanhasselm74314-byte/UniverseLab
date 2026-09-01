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
  add('default_runtime_pass',initial.snapshot.status==='PASS'&&initial.snapshot.engineVersion==='1.0.0'&&initial.snapshot.version==='1.0.1'&&initial.snapshot.cellularDynamicsIndependent===true&&initial.snapshot.gridResamplingVisualOnly===true&&initial.canvases===2&&Object.values(initial.outputs).every(value=>value&&value!=='–')&&initial.eraBars.length>0&&/PASS/.test(initial.statusText),initial);
  add('exact_flat_reference_state',close(initial.snapshot.params.Om,.315,0,1e-12)&&close(initial.snapshot.params.Or,.000092,0,1e-12)&&close(initial.snapshot.params.Ode,.684908,0,1e-12)&&close(initial.snapshot.params.Ok,0,0,1e-12),{params:initial.snapshot.params});

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
  add('cellular_step_does_not_modify_static_cosmology',staticStep.after.generation===staticStep.before.generation+1&&close(staticStep.after.a,staticStep.before.a,0,0)&&close(staticStep.after.tau,staticStep.before.tau,0,0)&&staticStep.after.status==='PASS',staticStep);

  const physicalStep=await de.page.evaluate(()=>{
    const A=window.UniverseLabEmergence,C=window.UniverseLabCosmology,mode=document.getElementById('expMode'),timeScale=document.getElementById('timeScale');
    mode.value='lcdm';mode.dispatchEvent(new Event('change',{bubbles:true}));timeScale.value='100';timeScale.dispatchEvent(new Event('input',{bubbles:true}));
    const before=A.snapshot(),after=A.step(),x0=Math.log(before.a),x1=Math.log(after.a),n=8192,h=(x1-x0)/n;
    const integrand=x=>1/C.E(Math.exp(-x)-1,before.params,'lcdm');
    let sum=integrand(x0)+integrand(x1);for(let i=1;i<n;i++)sum+=(i%2?4:2)*integrand(x0+i*h);
    return{before,after,expectedDeltaTau:.002,integratedDeltaTau:sum*h/3};
  });
  add('lcdm_display_time_advances_scale_factor',physicalStep.after.generation===physicalStep.before.generation+1&&physicalStep.after.a>physicalStep.before.a&&physicalStep.after.a<=1&&physicalStep.after.status==='PASS',physicalStep);
  add('maximum_time_amplification_stays_in_domain',close(physicalStep.after.tau-physicalStep.before.tau,.002,0,1e-15)&&close(physicalStep.integratedDeltaTau,.002,2e-6,1e-10)&&physicalStep.after.error===null,physicalStep);

  await de.page.evaluate(()=>{document.getElementById('ol').max='5';});
  const invalid=await de.page.evaluate(()=>{
    const A=window.UniverseLabEmergence,before=A.snapshot(),blocked=A.setInputs({om:.05,or:0,ol:4},{resetScale:true}),generationBefore=blocked.generation,aBefore=blocked.a,afterCellStep=A.step();
    return{before,blocked,afterCellStep,generationBefore,aBefore,
      outputs:Object.fromEntries(['radMetric','matMetric','vacMetric','curvMetric','growthD','growthF','growthApprox','growthErr','epochNow','accelNow','eqRM','eqML','accA','qNow'].map(id=>[id,document.getElementById(id)?.textContent?.trim()])),
      eraBarsText:document.getElementById('eraBars')?.textContent?.trim()||'',statusText:document.getElementById('domainStatus')?.textContent||'',bodyText:document.body.innerText};
  });
  add('invalid_background_fails_closed',invalid.blocked.status==='INVALID_BACKGROUND_DOMAIN'&&invalid.blocked.error?.code==='INVALID_BACKGROUND_DOMAIN'&&invalid.blocked.growth===null&&invalid.blocked.domain===null&&Object.values(invalid.outputs).every(value=>value==='–')&&invalid.eraBarsText===''&&/INVALID_BACKGROUND_DOMAIN/.test(invalid.statusText)&&!/(?:NaN|Infinity)/.test(invalid.bodyText),invalid);
  add('cellular_automaton_remains_independent_under_invalid_cosmology',invalid.afterCellStep.generation===invalid.generationBefore+1&&close(invalid.afterCellStep.a,invalid.aBefore,0,0)&&invalid.afterCellStep.status==='INVALID_BACKGROUND_DOMAIN',{generationBefore:invalid.generationBefore,generationAfter:invalid.afterCellStep.generation,aBefore:invalid.aBefore,aAfter:invalid.afterCellStep.a,status:invalid.afterCellStep.status});

  const recovered=await de.page.evaluate(()=>window.UniverseLabEmergence.resetCosmology());
  add('reset_recovers_reference_state',recovered.status==='PASS'&&close(recovered.params.Om,.315,0,1e-12)&&close(recovered.params.Or,.000092,0,1e-12)&&close(recovered.params.Ode,.684908,0,1e-12)&&close(recovered.params.Ok,0,0,1e-12)&&recovered.growth?.model==='lcdm'&&recovered.tau===0,recovered);

  const en=await openPage(context,'emergence-en.html','en');
  const parity=await en.page.evaluate(()=>({snapshot:window.UniverseLabEmergence.snapshot(),probe:window.UniverseLabEmergence.probeScaleFactor(.5),lang:document.documentElement.lang,title:document.title,canvases:document.querySelectorAll('canvas').length,separation:document.getElementById('separationNote')?.textContent||''}));
  add('de_en_runtime_parity',parity.snapshot.status==='PASS'&&parity.snapshot.engineVersion==='1.0.0'&&parity.snapshot.version==='1.0.1'&&parity.lang==='en'&&/Emergence/.test(parity.title)&&parity.canvases===2&&close(parity.probe.E,probe.adapter.E)&&close(parity.probe.q,probe.adapter.q)&&close(parity.probe.growth.D,probe.adapter.D)&&close(parity.probe.growth.f,probe.adapter.f)&&/cellular automaton/i.test(parity.separation),parity);

  add('no_browser_or_http_errors',de.errors.length===0&&de.httpErrors.length===0&&en.errors.length===0&&en.httpErrors.length===0,{de_errors:de.errors,de_http_errors:de.httpErrors,en_errors:en.errors,en_http_errors:en.httpErrors});
  await de.page.close();await en.page.close();await context.close();
}catch(error){report.status='FAIL';report.errors.push(String(error?.stack||error));}
finally{await browser.close();}

fs.writeFileSync('emergence-canonical-growth-adapter-report.json',JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
if(report.status!=='PASS')process.exit(1);
