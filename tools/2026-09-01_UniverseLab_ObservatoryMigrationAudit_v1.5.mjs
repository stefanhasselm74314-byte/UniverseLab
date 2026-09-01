import { chromium } from 'playwright';
import fs from 'node:fs';

const BASE=process.env.UNIVERSELAB_BASE_URL||'http://127.0.0.1:8000/';
const report={
  schema:'universelab.observatory-migration-audit.v1',
  timestamp_utc:new Date().toISOString(),
  base_url:BASE,
  status:'PASS',
  checks:[],
  errors:[]
};

function add(name,ok,detail={}){
  report.checks.push({name,ok,...detail});
  if(!ok) report.status='FAIL';
}
function close(a,b,rtol=1e-9,atol=1e-10){
  return Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=atol+rtol*Math.max(Math.abs(a),Math.abs(b));
}

const browser=await chromium.launch({headless:true});
try{
  const context=await browser.newContext({viewport:{width:1280,height:900},locale:'de-DE'});
  const page=await context.newPage();
  const browserErrors=[];
  const httpErrors=[];
  page.on('pageerror',error=>browserErrors.push(String(error)));
  page.on('console',message=>{if(message.type()==='error')browserErrors.push(`console: ${message.text()}`);});
  page.on('response',response=>{if(response.status()>=400)httpErrors.push({status:response.status(),url:response.url()});});

  const url=new URL('observatory.html',BASE);
  url.searchParams.set('ul_observatory_audit',String(Date.now()));
  const response=await page.goto(url.href,{waitUntil:'networkidle',timeout:45000});
  if(!response?.ok()) throw new Error(`HTTP ${response?.status()} ${url.href}`);
  await page.waitForFunction(()=>window.UniverseLabObservatory?.snapshot().revision>=1,{timeout:20000});

  const initial=await page.evaluate(()=>({
    snapshot:window.UniverseLabObservatory.snapshot(),
    outputs:Object.fromEntries(['age','q0','s80','curv'].map(id=>[id,document.getElementById(id)?.textContent?.trim()])),
    statusText:document.getElementById('domainStatus')?.textContent||''
  }));
  add('default_runtime_pass',
    initial.snapshot.status==='PASS'&&initial.snapshot.engineVersion==='1.0.0'&&
    Object.values(initial.outputs).every(value=>value&&value!=='–')&&/PASS/.test(initial.statusText),
    initial);
  add('default_age_sanity',initial.snapshot.metrics?.age>10&&initial.snapshot.metrics?.age<20,{age_gyr:initial.snapshot.metrics?.age});

  async function setInputs(values){
    return page.evaluate(values=>{
      for(const [id,value] of Object.entries(values)){
        const node=document.getElementById(id);
        if(!node) throw new Error(`missing input ${id}`);
        node.value=String(value);
        node.dispatchEvent(new Event('input',{bubbles:true}));
      }
      return window.UniverseLabObservatory.update();
    },values);
  }

  await setInputs({Om:.2,Ol:.5,w:-1});
  await page.evaluate(()=>window.UniverseLabObservatory.setMode('bao'));
  const open=await page.evaluate(()=>{
    const A=window.UniverseLabObservatory;
    const C=window.UniverseLabCosmology;
    const s=A.snapshot();
    const z=2.33;
    const dc=C.radialComovingDistance(z,s.params,s.model,{n:1024,domainSamples:1024});
    const dm=C.transverseComovingDistance(z,s.params,s.model,{n:1024,domainSamples:1024});
    return {status:s.status,Ok:s.params.Ok,probe:A.probe(z,'bao'),dc,dm,rd:C.DEFAULT_RD_MPC};
  });
  add('open_curvature_uses_D_M',
    open.status==='PASS'&&open.Ok>0&&open.dm>open.dc&&close(open.probe,open.dm/open.rd),
    open);

  await setInputs({Om:.5,Ol:.8,w:-1});
  await page.evaluate(()=>window.UniverseLabObservatory.setMode('bao'));
  const closed=await page.evaluate(()=>{
    const A=window.UniverseLabObservatory;
    const C=window.UniverseLabCosmology;
    const s=A.snapshot();
    const z=2.33;
    const dc=C.radialComovingDistance(z,s.params,s.model,{n:1024,domainSamples:1024});
    const dm=C.transverseComovingDistance(z,s.params,s.model,{n:1024,domainSamples:1024});
    return {status:s.status,Ok:s.params.Ok,probe:A.probe(z,'bao'),dc,dm,rd:C.DEFAULT_RD_MPC};
  });
  add('closed_curvature_uses_D_M',
    closed.status==='PASS'&&closed.Ok<0&&closed.dm<closed.dc&&close(closed.probe,closed.dm/closed.rd),
    closed);

  await page.evaluate(()=>window.UniverseLabObservatory.reset());
  await page.evaluate(()=>window.UniverseLabObservatory.setMode('growth'));
  const growth=await page.evaluate(()=>{
    const A=window.UniverseLabObservatory;
    const C=window.UniverseLabCosmology;
    const s=A.snapshot();
    const z=1;
    const direct=C.growthAtZ(z,C.solveGrowth(s.params,s.model,{steps:4000})).fsigma8;
    const oldApprox=C.omegaM(z,s.params,s.model)**.55*s.params.sigma8/(1+z);
    return {status:s.status,model:s.model,probe:A.probe(z,'growth'),direct,oldApprox,difference:A.probe(z,'growth')-oldApprox};
  });
  add('growth_uses_canonical_ODE',
    growth.status==='PASS'&&growth.model==='wcdm'&&close(growth.probe,growth.direct)&&Math.abs(growth.difference)>.01,
    growth);

  await setInputs({Om:.1,Ol:1.2,w:-1.5});
  const invalid=await page.evaluate(()=>({
    snapshot:window.UniverseLabObservatory.snapshot(),
    outputs:Object.fromEntries(['age','q0','s80','curv'].map(id=>[id,document.getElementById(id)?.textContent?.trim()])),
    statusText:document.getElementById('domainStatus')?.textContent||'',
    bodyText:document.body.innerText
  }));
  add('invalid_domain_fails_closed',
    invalid.snapshot.status==='INVALID_BACKGROUND_DOMAIN'&&invalid.snapshot.series.length===0&&
    Object.values(invalid.outputs).every(value=>value==='–')&&
    /INVALID_BACKGROUND_DOMAIN/.test(invalid.statusText)&&
    !/(?:NaN|Infinity)/.test(invalid.bodyText),
    invalid);

  const recovered=await page.evaluate(()=>window.UniverseLabObservatory.reset());
  add('reset_recovers_valid_state',
    recovered.status==='PASS'&&Math.abs(recovered.params.Om-.315)<1e-12&&
    Math.abs(recovered.params.Ode-.685)<1e-12&&Math.abs(recovered.params.w+1)<1e-12,
    recovered);

  add('no_browser_or_http_errors',browserErrors.length===0&&httpErrors.length===0,{browser_errors:browserErrors,http_errors:httpErrors});
  await context.close();
}catch(error){
  report.status='FAIL';
  report.errors.push(String(error?.stack||error));
}finally{
  await browser.close();
}

fs.writeFileSync('observatory-migration-report.json',JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
if(report.status!=='PASS') process.exit(1);
