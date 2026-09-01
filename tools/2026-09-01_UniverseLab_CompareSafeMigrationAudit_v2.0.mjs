import { chromium } from 'playwright';
import fs from 'node:fs';

const BASE=process.env.UNIVERSELAB_BASE_URL||'http://127.0.0.1:8000/';
const report={schema:'universelab.compare-safe-migration-audit.v1',timestamp_utc:new Date().toISOString(),base_url:BASE,status:'PASS',checks:[],errors:[]};
const add=(name,ok,detail={})=>{report.checks.push({name,ok,...detail});if(!ok)report.status='FAIL';};
const close=(a,b,rtol=1e-9,atol=1e-10)=>Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=atol+rtol*Math.max(Math.abs(a),Math.abs(b));

const browser=await chromium.launch({headless:true});
try{
  const context=await browser.newContext({viewport:{width:1280,height:900},locale:'de-DE',acceptDownloads:true});
  const page=await context.newPage();
  const browserErrors=[];
  const httpErrors=[];
  page.on('pageerror',error=>browserErrors.push(String(error)));
  page.on('console',message=>{if(message.type()==='error')browserErrors.push(`console: ${message.text()}`);});
  page.on('response',response=>{if(response.status()>=400)httpErrors.push({status:response.status(),url:response.url()});});

  const url=new URL('compare-safe.html',BASE);
  url.searchParams.set('ul_compare_safe_audit',String(Date.now()));
  const response=await page.goto(url.href,{waitUntil:'networkidle',timeout:45000});
  if(!response?.ok())throw new Error(`HTTP ${response?.status()} ${url.href}`);
  await page.waitForFunction(()=>window.UniverseLabCompareSafe?.snapshot().revision>=1,{timeout:20000});

  async function setInputs(values,extend={}){
    const before=await page.evaluate(()=>window.UniverseLabCompareSafe.snapshot().revision);
    await page.evaluate(({values,extend})=>{
      for(const [id,bounds] of Object.entries(extend)){
        const node=document.getElementById(id);
        for(const [key,value] of Object.entries(bounds))node.setAttribute(key,String(value));
      }
      for(const [id,value] of Object.entries(values)){
        const node=document.getElementById(id);
        if(!node)throw new Error(`missing input ${id}`);
        node.value=String(value);
        node.dispatchEvent(new Event('input',{bubbles:true}));
      }
      window.UniverseLabCompareSafe.update();
    },{values,extend});
    await page.waitForFunction(revision=>window.UniverseLabCompareSafe.snapshot().revision>revision,before,{timeout:15000});
    return page.evaluate(()=>window.UniverseLabCompareSafe.snapshot());
  }

  const initial=await page.evaluate(()=>({
    snapshot:window.UniverseLabCompareSafe.snapshot(),
    outputs:Object.fromEntries(['ageL','ageB','dev1','S8','dc','dm','dl','da','mu'].map(id=>[id,document.getElementById(id)?.textContent?.trim()])),
    growth:document.getElementById('growthStatus')?.textContent?.trim(),
    lensing:document.getElementById('lensingStatus')?.textContent?.trim(),
    status:document.getElementById('compareStatus')?.textContent||'',
    w:{value:document.getElementById('w')?.value,disabled:document.getElementById('w')?.disabled}
  }));
  add('default_runtime_pass',initial.snapshot.status==='PASS'&&initial.snapshot.engineVersion==='1.0.0'&&Object.values(initial.outputs).every(value=>value&&value!=='–')&&/PASS/.test(initial.status),initial);
  add('bridge_model_identity',initial.snapshot.baseModel==='lcdm'&&initial.snapshot.bridgeModel==='bridge'&&initial.w.disabled&&Number(initial.w.value)===-1,initial);
  add('growth_and_lensing_firewalls_visible',initial.growth==='UNRELEASED_GROWTH_MAP'&&initial.lensing==='UNRELEASED_LENSING_MAP',{growth:initial.growth,lensing:initial.lensing});

  const open=await setInputs({Om:.2,Ol:.5,z:2.33});
  const openProbe=await page.evaluate(()=>{
    const A=window.UniverseLabCompareSafe,C=window.UniverseLabCosmology,s=A.snapshot(),z=2.33;
    const dc=C.radialComovingDistance(z,s.params,'lcdm',{n:1024,domainSamples:1024});
    const dm=C.transverseComovingDistance(z,s.params,'lcdm',{n:1024,domainSamples:1024});
    const mu=A.probe(z,'lcdm','mu');
    const muOld=5*Math.log10((1+z)*dc)+25;
    return {dc,dm,mu,muOld,displayDm:document.getElementById('dm')?.textContent};
  });
  add('curved_distance_uses_D_M',open.status==='PASS'&&open.params.Ok>0&&openProbe.dm>openProbe.dc&&Math.abs(openProbe.mu-openProbe.muOld)>.05&&openProbe.displayDm&&!openProbe.displayDm.startsWith('–'),{snapshot:open,probe:openProbe});

  const curve1=await setInputs({beta:.05,ib:.4,rchi:1});
  const e1=await page.evaluate(()=>[0,.5,1,3,8].map(z=>window.UniverseLabCompareSafe.probe(z,'bridge','E')));
  const curve2=await setInputs({beta:.1,ib:.2,rchi:1});
  const e2=await page.evaluate(()=>[0,.5,1,3,8].map(z=>window.UniverseLabCompareSafe.probe(z,'bridge','E')));
  add('bridge_product_degeneracy',curve1.status==='PASS'&&curve2.status==='PASS'&&e1.every((value,index)=>close(value,e2[index],1e-13,1e-14)),{e1,e2,product1:.05*.4,product2:.1*.2});

  const csv=await page.evaluate(()=>window.UniverseLabCompareSafe.csvText());
  const rows=csv.trim().split('\n');
  add('valid_csv_contract',rows.length===102&&rows[0]==='z,H_LCDM_km_s_Mpc,H_bridge_km_s_Mpc,delta_H_over_H'&&!/(?:NaN|Infinity)/.test(csv),{row_count:rows.length,header:rows[0]});

  const invalidBase=await setInputs({Om:-1,Ol:0},{Om:{min:-1}});
  const baseUi=await page.evaluate(()=>({
    outputs:Object.fromEntries(['ageL','ageB','dev1','S8','dc','dm','dl','da','mu'].map(id=>[id,document.getElementById(id)?.textContent?.trim()])),
    status:document.getElementById('compareStatus')?.textContent||'',body:document.body.innerText,
    csvDisabled:document.getElementById('csv')?.disabled,
    csvCode:(()=>{try{window.UniverseLabCompareSafe.csvText();return null;}catch(error){return error?.code||error?.name;}})()
  }));
  add('invalid_background_fails_closed',invalidBase.status==='INVALID_BACKGROUND_DOMAIN'&&invalidBase.seriesCounts.base===0&&Object.values(baseUi.outputs).every(value=>value==='–')&&baseUi.csvDisabled&&baseUi.csvCode==='CSV_BLOCKED_INVALID_DOMAIN'&&!/(?:NaN|Infinity)/.test(baseUi.body),{snapshot:invalidBase,ui:baseUi});

  await page.evaluate(()=>window.UniverseLabCompareSafe.reset());
  const invalidBridge=await setInputs({beta:-3,ib:1,rchi:1},{beta:{min:-3}});
  const bridgeUi=await page.evaluate(()=>({status:document.getElementById('compareStatus')?.textContent||'',csvDisabled:document.getElementById('csv')?.disabled,body:document.body.innerText}));
  add('invalid_bridge_fails_closed',invalidBridge.status==='INVALID_BRIDGE_DOMAIN'&&invalidBridge.seriesCounts.bridge===0&&bridgeUi.csvDisabled&&!/(?:NaN|Infinity)/.test(bridgeUi.body),{snapshot:invalidBridge,ui:bridgeUi});

  const recovered=await page.evaluate(()=>window.UniverseLabCompareSafe.reset());
  add('reset_recovers_reference_state',recovered.status==='PASS'&&Math.abs(recovered.params.Om-.315)<1e-12&&Math.abs(recovered.params.Ode-.685)<1e-12&&Math.abs(recovered.params.betaTau-.05)<1e-12&&Math.abs(recovered.params.IB-.4)<1e-12&&Math.abs(recovered.params.Rchi-1)<1e-12,recovered);

  add('no_browser_or_http_errors',browserErrors.length===0&&httpErrors.length===0,{browser_errors:browserErrors,http_errors:httpErrors});
  await context.close();
}catch(error){
  report.status='FAIL';
  report.errors.push(String(error?.stack||error));
}finally{
  await browser.close();
}

fs.writeFileSync('compare-safe-migration-report.json',JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
if(report.status!=='PASS')process.exit(1);
