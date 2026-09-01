import { chromium } from 'playwright';
import fs from 'node:fs';

const BASE = process.env.UNIVERSELAB_BASE_URL || 'https://stefanhasselm74314-byte.github.io/UniverseLab/';
const EPS = Number(process.env.UNIVERSELAB_PARITY_EPS || '1e-12');
const report = { schema_version:'1.2', base_url:BASE, timestamp_utc:new Date().toISOString(), status:'PASS', checks:[], errors:[] };

function push(name, ok, detail={}) {
  report.checks.push({name, ok, ...detail});
  if (!ok) report.status='FAIL';
}
function close(a,b,eps=EPS){
  if (!Number.isFinite(a)||!Number.isFinite(b)) return false;
  return Math.abs(a-b) <= eps*Math.max(1,Math.abs(a),Math.abs(b));
}
function sameValue(a,b){
  if(a===null||b===null)return a===b;
  if(typeof a==='number'||typeof b==='number')return close(Number(a),Number(b));
  return JSON.stringify(a)===JSON.stringify(b);
}
function parseLocaleNumber(text){
  const s=String(text??'').replace(/\s*Gyr/i,'').replace(/%/g,'').replace(/,/g,'.').replace(/[^0-9eE+\-.]/g,'');
  const x=Number(s); return Number.isFinite(x)?x:NaN;
}
async function goto(page,path){
  const url=new URL(path,BASE).href + (path.includes('?')?'&':'?') + 'ul_parity=' + Date.now();
  let last;
  for(let i=0;i<4;i++){
    try{
      const r=await page.goto(url,{waitUntil:'networkidle',timeout:45000});
      if(r && r.ok()) return r;
      last=new Error(`HTTP ${r?.status()} for ${url}`);
    }catch(e){last=e;}
    await page.waitForTimeout(1500*(i+1));
  }
  throw last;
}
async function pageErrors(context,label){
  const errors=[]; const page=await context.newPage();
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{ if(m.type()==='error') errors.push(`console: ${m.text()}`); });
  return {page,errors,label};
}

const browser=await chromium.launch({headless:true});
try{
  const context=await browser.newContext({viewport:{width:1280,height:900}, locale:'en-US'});

  // 1) Validation Console: DE and EN use one canonical engine and must expose identical stable test semantics.
  {
    const de=await pageErrors(context,'validation-de'); const en=await pageErrors(context,'validation-en');
    await goto(de.page,'validation.html'); await goto(en.page,'validation-en.html');
    await de.page.waitForFunction(()=>window.UniverseLabValidation?.status==='complete'&&document.querySelectorAll('#rows tr[data-test-id]').length>=10);
    await en.page.waitForFunction(()=>window.UniverseLabValidation?.status==='complete'&&document.querySelectorAll('#rows tr[data-test-id]').length>=10);
    const snap=async p=>p.evaluate(()=>({
      api:window.UniverseLabValidation.snapshot(),
      rowIds:[...document.querySelectorAll('#rows tr[data-test-id]')].map(x=>x.dataset.testId),
      rowStates:[...document.querySelectorAll('#rows tr[data-test-id]')].map(x=>x.dataset.testStatus),
      failedText:document.querySelector('#failed')?.textContent,
      releaseText:document.querySelector('#release')?.textContent
    }));
    const A=await snap(de.page), B=await snap(en.page);
    const idsA=A.api.results.map(x=>x.id), idsB=B.api.results.map(x=>x.id);
    const idParity=JSON.stringify(idsA)===JSON.stringify(idsB)&&JSON.stringify(A.rowIds)===JSON.stringify(idsA)&&JSON.stringify(B.rowIds)===JSON.stringify(idsB);
    const semanticParity=idParity&&A.api.results.every((x,i)=>{
      const y=B.api.results[i];
      return x.id===y.id&&x.kind===y.kind&&x.ok===y.ok&&x.code===y.code&&sameValue(x.value,y.value)&&sameValue(x.target,y.target)&&sameValue(x.error,y.error)&&sameValue(x.tolerance,y.tolerance);
    });
    push('validation_test_id_parity',idParity,{de_ids:idsA,en_ids:idsB,de_rows:A.rowIds,en_rows:B.rowIds});
    push('validation_numeric_parity',semanticParity,{de:A.api.results,en:B.api.results,epsilon:EPS});
    push('validation_engine_identity',A.api.engineVersion===B.api.engineVersion&&A.api.engineVersion==='1.0.0',{de:A.api.engineVersion,en:B.api.engineVersion});
    push('validation_internal_health',A.api.failed===0&&B.api.failed===0&&A.api.results.length>=10&&A.api.results.every(x=>x.ok)&&B.api.results.every(x=>x.ok)&&A.rowStates.every(x=>x==='PASS')&&B.rowStates.every(x=>x==='PASS'),{de:A,en:B});
    push('validation_no_browser_errors',de.errors.length===0&&en.errors.length===0,{de_errors:de.errors,en_errors:en.errors});
    await de.page.close(); await en.page.close();
  }

  // 2) Single-engine shells: English must route to the canonical German executable engine.
  for(const spec of [
    {id:'comparison', en:'compare-en.html', selector:'a[href*="compare-safe.html"]', expected:'compare-safe.html', engine:'compare-safe.html', outputs:['ageL','ageB','dev1','S8']},
    {id:'observatory', en:'observatory-en.html', selector:'a[href="./observatory.html"]', expected:'observatory.html', engine:'observatory.html', outputs:['age','q0','s80','curv']}
  ]){
    const sh=await pageErrors(context,`${spec.id}-en-shell`); await goto(sh.page,spec.en);
    const href=await sh.page.locator(spec.selector).first().getAttribute('href');
    push(`${spec.id}_single_engine_route`, !!href && href.includes(spec.expected), {href,expected:spec.expected});
    const eng=await pageErrors(context,`${spec.id}-engine`); await goto(eng.page,spec.engine);
    await eng.page.waitForTimeout(500);
    const out=await eng.page.evaluate(ids=>Object.fromEntries(ids.map(id=>[id,document.getElementById(id)?.textContent?.trim()])),spec.outputs);
    const present=Object.values(out).every(v=>v && v!=='–');
    push(`${spec.id}_engine_runtime`, present && eng.errors.length===0,{outputs:out,browser_errors:eng.errors});
    if(spec.id==='observatory'){
      const age=parseLocaleNumber(out.age);
      push('observatory_age_sanity', age>10 && age<20,{age_gyr:age,criterion:'10 < t0 < 20 Gyr'});
    }
    if(spec.id==='comparison'){
      const ageL=parseLocaleNumber(out.ageL), ageB=parseLocaleNumber(out.ageB);
      push('comparison_age_sanity', ageL>10&&ageL<20&&ageB>10&&ageB<20,{age_lcdm_gyr:ageL,age_bridge_gyr:ageB});
    }
    push(`${spec.id}_shell_no_browser_errors`, sh.errors.length===0,{browser_errors:sh.errors});
    await sh.page.close(); await eng.page.close();
  }

  // 3) Governed runtime mirrors: rendered EN must preserve executable input identity/default state.
  for(const id of ['about','journey','emergence','universe3d']){
    const de=await pageErrors(context,`${id}-de`); const en=await pageErrors(context,`${id}-en`);
    await goto(de.page,`${id}.html`); await goto(en.page,`${id}-en.html`);
    await en.page.waitForTimeout(1200);
    const collect=async p=>p.evaluate(()=>({
      fields:[...document.querySelectorAll('input,select,textarea')].map((e,i)=>({
        key:e.id||e.name||`${e.tagName.toLowerCase()}-${i}`,
        tag:e.tagName.toLowerCase(), type:e.type||'', value:e.value, min:e.min||'', max:e.max||'', step:e.step||''
      })),
      canvases:document.querySelectorAll('canvas').length
    }));
    const A=await collect(de.page), B=await collect(en.page);
    const sameFields=JSON.stringify(A.fields)===JSON.stringify(B.fields);
    push(`${id}_runtime_mirror_input_parity`, sameFields,{de_fields:A.fields,en_fields:B.fields,de_canvas:A.canvases,en_canvas:B.canvases});
    push(`${id}_runtime_mirror_canvas_parity`,A.canvases===B.canvases,{de:A.canvases,en:B.canvases});
    push(`${id}_runtime_mirror_no_browser_errors`, de.errors.length===0 && en.errors.length===0,{de_errors:de.errors,en_errors:en.errors});
    await de.page.close(); await en.page.close();
  }

  // 4) HyperLab evidence/gate semantics must survive translation.
  {
    const de=await pageErrors(context,'hyperlab-de'); const en=await pageErrors(context,'hyperlab-en');
    await goto(de.page,'hyperlab.html'); await goto(en.page,'hyperlab-en.html');
    const textA=(await de.page.textContent('body'))||''; const textB=(await en.page.textContent('body'))||'';
    const okA=/K1-D/i.test(textA)&&/not\s+released/i.test(textA)&&/K1-E/i.test(textA)&&/not\s+admissible/i.test(textA);
    const okB=/K1-D/i.test(textB)&&/not\s+released/i.test(textB)&&/K1-E/i.test(textB)&&/not\s+admissible/i.test(textB);
    push('hyperlab_gate_semantic_parity',okA&&okB,{de:okA,en:okB});
    push('hyperlab_no_browser_errors',de.errors.length===0&&en.errors.length===0,{de_errors:de.errors,en_errors:en.errors});
    await de.page.close(); await en.page.close();
  }

  await context.close();
}catch(e){ report.status='FAIL'; report.errors.push(String(e?.stack||e)); }
finally{ await browser.close(); }

fs.writeFileSync('browser-parity-report.json',JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
if(report.status!=='PASS') process.exit(1);
