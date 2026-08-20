import { chromium } from 'playwright';
import fs from 'node:fs';

const BASE=process.env.UNIVERSELAB_BASE_URL||'https://stefanhasselm74314-byte.github.io/UniverseLab/';
const report={schema_version:'1.0',base_url:BASE,timestamp_utc:new Date().toISOString(),status:'PASS',checks:[],errors:[]};
function push(name,ok,detail={}){report.checks.push({name,ok,...detail});if(!ok)report.status='FAIL';}
function finite(x){return Number.isFinite(x);}
function parseDE(text){const m=String(text??'').replace(/−/g,'-').match(/[-+]?\d+(?:[.,]\d+)?(?:[eE][-+]?\d+)?/);return m?Number(m[0].replace(',','.')):NaN;}
async function open(context,path){const errors=[];const failed=[];const page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(`console: ${m.text()}`)});page.on('response',r=>{if(r.status()>=400)failed.push({status:r.status(),url:r.url()})});const u=new URL(path,BASE);u.searchParams.set('ul_numcov',Date.now());const r=await page.goto(u.href,{waitUntil:'networkidle',timeout:45000});if(!r?.ok())throw new Error(`HTTP ${r?.status()} ${u.href}`);return{page,errors,failed};}
async function setValue(page,id,value){await page.locator(`#${id}`).evaluate((el,v)=>{el.value=String(v);el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));},value);await page.waitForTimeout(80);}

const browser=await chromium.launch({headless:true});
try{
 const context=await browser.newContext({viewport:{width:1280,height:900},locale:'de-DE'});

 // A. HyperLab: deterministic diagnostic calculators and adversarial response checks.
 {
  const h=await open(context,'hyperlab.html'); const p=h.page; await p.waitForTimeout(700);
  const text=id=>p.locator(`#${id}`).textContent();
  const eps=parseDE(await text('eftOut'));
  const d=await text('dOut'); const b2=parseDE(d); const wm=(d.match(/wQ=([-+0-9.,]+)/)||[])[1]; const wq=wm?Number(wm.replace(',','.')):NaN;
  const chir=parseDE(await text('fOut')); const mu=parseDE(await text('bOut')); const self=parseDE(await text('sOut')); const bounce=(await text('xOut')).trim();
  push('hyperlab_default_diagnostics',Math.abs(eps-.02)<1e-12&&Math.abs(b2-1)<1e-12&&Math.abs(wq+.7)<1e-12&&Math.abs(chir-1)<1e-6&&Math.abs(mu-.01)<1e-12&&Math.abs(self-.01)<1e-12&&/PASS/.test(bounce),{eps,b2,wq,chirality:chir,muB:mu,self_tuning:self,bounce});
  await setValue(p,'eftM',.01); const epsBad=parseDE(await text('eftOut')); const eftNote=await p.locator('#eftNote').textContent();
  push('hyperlab_eft_adversarial_response',Math.abs(epsBad-2)<1e-12&&/nicht abgesichert/i.test(eftNote),{epsilon:epsBad,note:eftNote});
  await setValue(p,'xH',.1); const bounceBad=(await text('xOut')).trim();
  push('hyperlab_bounce_adversarial_response',/FAIL|UNVOLLSTÄNDIG/.test(bounceBad),{output:bounceBad});
  push('hyperlab_runtime_health',h.errors.length===0&&h.failed.length===0,{browser_errors:h.errors,http_failures:h.failed});
  await p.close();
 }

 // B. Tafelwerk: exhaustive sweep of every entry declared numerically calculable.
 {
  const t=await open(context,'tafelwerk.html'); const p=t.page; await p.waitForTimeout(600);
  const declared=Number((await p.locator('#calcCount').textContent()).match(/\d+/)?.[0]||0);
  await p.locator('#calcOnly').check(); await p.locator('#calcOnly').dispatchEvent('change'); await p.waitForTimeout(150);
  const options=await p.locator('#formulaList option').evaluateAll(os=>os.map(o=>({value:o.value,label:o.textContent.trim()})));
  const rows=[];
  for(const o of options){
    await p.locator('#formulaList').selectOption(o.value); await p.locator('#formulaList').dispatchEvent('change'); await p.waitForTimeout(20);
    const result=(await p.locator('#formulaResult').textContent()).trim();
    const bad=/nicht definiert|NaN|Infinity|∞|undefined|null/i.test(result)||!result||result==='–';
    rows.push({id:o.value,label:o.label,result,ok:!bad});
  }
  const bad=rows.filter(x=>!x.ok);
  push('tafelwerk_declared_count_consistency',declared>0&&options.length===declared,{declared,enumerated:options.length});
  push('tafelwerk_all_calculable_defaults_defined',options.length>0&&bad.length===0,{tested:options.length,failures:bad});
  // Analytic anchor points independent of the library's displayed defaults.
  async function selectByLabel(fragment){const hit=options.find(x=>x.label.includes(fragment));if(!hit)throw new Error(`Tafelwerk formula not found: ${fragment}`);await p.locator('#formulaList').selectOption(hit.value);await p.locator('#formulaList').dispatchEvent('change');await p.waitForTimeout(30);return hit;}
  await selectByLabel('Skalenfaktor aus Rotverschiebung'); const zInput=p.locator('#formulaInputs input').first(); await zInput.fill('3'); await zInput.dispatchEvent('input'); const a=parseDE(await p.locator('#formulaResult').textContent());
  await selectByLabel('Hubble-Länge'); const hInput=p.locator('#formulaInputs input').first(); await hInput.fill('70'); await hInput.dispatchEvent('input'); const dh=parseDE(await p.locator('#formulaResult').textContent());
  push('tafelwerk_analytic_anchors',Math.abs(a-.25)<1e-12&&Math.abs(dh-(299792.458/70))<1e-5,{a_at_z3:a,dh_mpc_at_H0_70:dh,dh_expected:299792.458/70});
  push('tafelwerk_runtime_health',t.errors.length===0&&t.failed.length===0,{browser_errors:t.errors,http_failures:t.failed});
  await p.close();
 }

 // C. Observatory: response invariant under H0 change at fixed dimensionless densities.
 {
  const o=await open(context,'observatory.html');const p=o.page;await p.waitForTimeout(400);
  const age0=parseDE(await p.locator('#age').textContent()); const q0=await p.locator('#q0').textContent(); const s80=await p.locator('#s80').textContent();
  await setValue(p,'H0',80); const age1=parseDE(await p.locator('#age').textContent()); const q1=await p.locator('#q0').textContent(); const s81=await p.locator('#s80').textContent();
  const ratio=age1/age0,expected=67.4/80;
  push('observatory_h0_scaling_invariant',finite(age0)&&finite(age1)&&Math.abs(ratio-expected)<2e-3&&q0===q1&&s80===s81,{age67_4:age0,age80:age1,ratio,expected,q0_before:q0,q0_after:q1,s8_before:s80,s8_after:s81});
  push('observatory_runtime_health',o.errors.length===0&&o.failed.length===0,{browser_errors:o.errors,http_failures:o.failed}); await p.close();
 }

 // D. Generative/visual modules: numerical-health contract, not exact-state regression.
 for(const path of ['journey.html','emergence.html','universe3d.html','conway.html']){
  const x=await open(context,path);const p=x.page;await p.waitForTimeout(500);
  const health=await p.evaluate(()=>({badText:/\b(?:NaN|Infinity|undefined)\b/.test(document.body.innerText),canvases:[...document.querySelectorAll('canvas')].map(c=>({w:c.width,h:c.height}))}));
  const canvasOK=health.canvases.every(c=>c.w>0&&c.h>0);
  push(`${path.replace('.html','')}_numerical_runtime_health`,!health.badText&&canvasOK&&x.errors.length===0&&x.failed.length===0,{...health,browser_errors:x.errors,http_failures:x.failed});await p.close();
 }
 await context.close();
}catch(e){report.status='FAIL';report.errors.push(String(e?.stack||e));}
finally{await browser.close();}
fs.writeFileSync('numerical-coverage-report.json',JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
if(report.status!=='PASS')process.exit(1);
