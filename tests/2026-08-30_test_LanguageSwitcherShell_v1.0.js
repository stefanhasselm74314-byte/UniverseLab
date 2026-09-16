const { chromium } = require('playwright');
const assert = require('assert');
(async()=>{
  const browser=await chromium.launch({headless:true});
  const page=await browser.newPage({viewport:{width:412,height:915}});
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.addInitScript(()=>{
    if(!location.pathname.endsWith('2026-08-29_UniverseLab_Hyperzeit_10M_ResearchProgram_v1.0.html'))return;
    const observer=new MutationObserver(()=>{
      if(!document.body)return;
      const legacy=document.createElement('div');
      legacy.id='ul-test-legacy-switcher';
      legacy.dataset.ulLanguageSwitcher='legacy-test';
      legacy.textContent='legacy';
      document.body.appendChild(legacy);
      observer.disconnect();
    });
    observer.observe(document.documentElement,{childList:true,subtree:true});
  });
  await page.goto('http://127.0.0.1:4173/UniverseLab/2026-08-29_UniverseLab_Hyperzeit_10M_ResearchProgram_v1.0.html',{waitUntil:'networkidle'});
  const shellSrc=await page.locator('script[src*="2026-08-16_UniverseLab_GlobalShell_v1.1.js"]').getAttribute('src');
  assert(shellSrc && /\?v=20260916-1$/.test(shellSrc),'10M page must cache-bust the repaired GlobalShell asset');
  const wrap=page.locator('[data-ul-language-switcher]');
  const select=wrap.locator('select');
  const gates=page.locator('.ul-shell__gates');
  await select.waitFor({state:'visible',timeout:10000});
  assert.strictEqual(await select.locator('option').count(),11,'expected 11 languages');
  const box=await wrap.boundingBox();
  const gatesBox=await gates.boundingBox();
  assert(box && box.x>=0 && box.x+box.width<=412.5,'language selector must stay inside mobile viewport');
  assert(gatesBox && box.y>=gatesBox.y-1 && box.y+box.height<=gatesBox.y+gatesBox.height+1,'language selector must remain inside shell gate row');
  const parentClass=await wrap.evaluate(el=>el.parentElement?.className||'');
  assert(String(parentClass).includes('ul-shell__gates'),'language selector must be a child of shell gates');
  const pos=await wrap.evaluate(el=>getComputedStyle(el).position);
  assert.strictEqual(pos,'static','language selector must not be floating/fixed');
  assert.strictEqual(await select.inputValue(),'de');
  assert.strictEqual(await page.locator('#ul-test-legacy-switcher').count(),0,'legacy switcher outside the gate row must be replaced');
  assert.deepStrictEqual(errors,[],'page must have no JS errors');

  await page.goto('http://127.0.0.1:4173/UniverseLab/navigator.html',{waitUntil:'networkidle'});
  const navWrap=page.locator('[data-ul-language-switcher]');
  const navSelect=navWrap.locator('select');
  const navGates=page.locator('.ul-shell__gates');
  await navSelect.waitFor({state:'visible',timeout:10000});
  const navBox=await navWrap.boundingBox();
  const navGatesBox=await navGates.boundingBox();
  assert(navBox && navGatesBox && navBox.y>=navGatesBox.y-1 && navBox.y+navBox.height<=navGatesBox.y+navGatesBox.height+1,'navigator language selector must stay in top shell gate row');
  await Promise.all([page.waitForURL(/navigator-en\.html/,{timeout:10000}),navSelect.selectOption('en')]);
  assert(/navigator-en\.html$/.test(new URL(page.url()).pathname),'English must use curated navigator route');

  await page.goto('http://127.0.0.1:4173/UniverseLab/2026-08-29_UniverseLab_Hyperzeit_10M_ResearchProgram_v1.0.html',{waitUntil:'networkidle'});
  await page.evaluate(async()=>{
    const registrations=await navigator.serviceWorker.getRegistrations();
    await Promise.all(registrations.map(reg=>reg.unregister()));
    const reg=await navigator.serviceWorker.register('/UniverseLab/2026-08-19_UniverseLab_SitePrintExportServiceWorker_v1.0.js',{scope:'/UniverseLab/'});
    await navigator.serviceWorker.ready;
    const worker=reg.installing||reg.waiting||reg.active;
    if(worker&&worker.state!=='activated')await new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>reject(new Error('service worker activation timeout')),10000);
      worker.addEventListener('statechange',()=>{if(worker.state==='activated'){clearTimeout(timer);resolve()}});
    });
  });
  await page.reload({waitUntil:'networkidle'});
  await page.waitForFunction(()=>!!navigator.serviceWorker.controller,null,{timeout:10000});

  async function assertControlledShell(label){
    const controlled=await page.evaluate(()=>navigator.serviceWorker.controller?.scriptURL||'');
    assert(controlled.endsWith('/UniverseLab/2026-08-19_UniverseLab_SitePrintExportServiceWorker_v1.0.js'),label+': expected presentation worker control');
    const switches=page.locator('[data-ul-language-switcher]');
    await switches.locator('select').waitFor({state:'visible',timeout:10000});
    assert.strictEqual(await switches.count(),1,label+': expected exactly one language switcher');
    const parent=await switches.evaluate(el=>el.parentElement?.className||'');
    assert(String(parent).includes('ul-shell__gates'),label+': switcher must remain in gate row');
    assert.strictEqual(await page.locator('script[src*="2026-08-18_UniverseLab_SiteLanguageSwitcher_v1.1.js"]').count(),0,label+': legacy switcher asset must not be injected');
    assert.strictEqual(await page.locator('script[src*="2026-08-30_UniverseLab_SiteLanguageSwitcher_v1.0.js"]').count(),1,label+': current switcher asset must load once');
    assert.strictEqual(await page.locator('script[src*="2026-08-27_UniverseLab_DocumentLinkRouter_v1.0.js"]').count(),1,label+': document router parity');
    assert.strictEqual(await page.locator('script[src*="2026-08-19_UniverseLab_SitePrintExport_v1.0.js"]').count(),1,label+': print/export parity');
  }

  await assertControlledShell('controlled navigation 1');
  await page.goto('http://127.0.0.1:4173/UniverseLab/navigator.html',{waitUntil:'networkidle'});
  await page.goto('http://127.0.0.1:4173/UniverseLab/2026-08-29_UniverseLab_Hyperzeit_10M_ResearchProgram_v1.0.html',{waitUntil:'networkidle'});
  await assertControlledShell('controlled navigation 2');
  await page.evaluate(async()=>{const registrations=await navigator.serviceWorker.getRegistrations();await Promise.all(registrations.map(reg=>reg.unregister()))});
  assert.deepStrictEqual(errors,[],'controlled navigation must have no JS errors');
  await browser.close();
  console.log('Language switcher shell placement + controlled two-navigation parity: PASS');
})().catch(e=>{console.error(e);process.exit(1)});
