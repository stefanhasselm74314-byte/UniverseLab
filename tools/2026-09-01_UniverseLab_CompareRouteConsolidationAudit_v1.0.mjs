import { chromium } from 'playwright';
import fs from 'node:fs';

const BASE=process.env.UNIVERSELAB_BASE_URL||'http://127.0.0.1:8000/';
const report={schema:'universelab.compare-route-consolidation-audit.v1',timestamp_utc:new Date().toISOString(),base_url:BASE,status:'PASS',checks:[],errors:[]};
const add=(name,ok,detail={})=>{report.checks.push({name,ok,...detail});if(!ok)report.status='FAIL';};
const browser=await chromium.launch({headless:true});
try{
  const context=await browser.newContext({viewport:{width:1280,height:900},locale:'de-DE'});
  for(const route of ['compare.html','compare-direct.html']){
    const page=await context.newPage();
    const errors=[];
    page.on('pageerror',error=>errors.push(String(error)));
    page.on('console',message=>{if(message.type()==='error')errors.push(`console: ${message.text()}`);});
    const source=new URL(route,BASE);
    source.searchParams.set('probe','route');
    source.hash='distance';
    await page.goto(source.href,{waitUntil:'networkidle',timeout:45000});
    await page.waitForFunction(()=>window.UniverseLabCompareSafe?.snapshot().revision>=1,{timeout:20000});
    const result=await page.evaluate(()=>({
      url:location.href,
      path:location.pathname,
      search:location.search,
      hash:location.hash,
      snapshot:window.UniverseLabCompareSafe.snapshot(),
      title:document.title
    }));
    add(`${route}_redirects_to_canonical_safe`,
      result.path.endsWith('/compare-safe.html')&&result.search.includes('probe=route')&&result.hash==='#distance'&&
      result.snapshot.status==='PASS'&&result.snapshot.engineVersion==='1.0.0'&&errors.length===0,
      {...result,browser_errors:errors});
    await page.close();
  }

  const page=await context.newPage();
  await page.goto(new URL('compare-safe.html',BASE).href,{waitUntil:'networkidle',timeout:45000});
  const legacy=await page.evaluate(async()=>{
    await new Promise((resolve,reject)=>{
      const script=document.createElement('script');
      script.src='./compare-app.js?retirement-audit='+Date.now();
      script.onload=resolve;script.onerror=reject;document.head.appendChild(script);
    });
    const api=window.UniverseLabCompareLegacy;
    const forbidden=['E','H','dc','mu','growth','sweep'];
    return {
      status:api?.status,
      canonicalUrl:api?.canonicalUrl,
      keys:Object.keys(api||{}),
      openCanonicalIsFunction:typeof api?.openCanonical==='function',
      hasNumericalAuthority:Object.keys(api||{}).some(key=>forbidden.includes(key)),
      provenance:api?.provenance||null,
      physicalGateEffect:api?.physicalGateEffect,
      physicalEvidenceEffect:api?.physicalEvidenceEffect
    };
  });
  add('legacy_app_has_no_numerical_authority',
    legacy.status==='RETIRED_DUPLICATE_ENGINE'&&legacy.canonicalUrl==='./compare-safe.html?v=safe2'&&
    legacy.openCanonicalIsFunction&&!legacy.hasNumericalAuthority&&legacy.physicalGateEffect==='NONE'&&
    legacy.physicalEvidenceEffect==='NONE'&&legacy.provenance?.unit==='dimensionslos',
    legacy);
  await page.close();
  await context.close();
}catch(error){
  report.status='FAIL';
  report.errors.push(String(error?.stack||error));
}finally{
  await browser.close();
}

fs.writeFileSync('compare-route-consolidation-report.json',JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
if(report.status!=='PASS')process.exit(1);
