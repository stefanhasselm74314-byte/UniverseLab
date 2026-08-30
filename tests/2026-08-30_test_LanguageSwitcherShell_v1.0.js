const { chromium } = require('playwright');
const assert = require('assert');
(async()=>{
  const browser=await chromium.launch({headless:true});
  const page=await browser.newPage({viewport:{width:412,height:915}});
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto('http://127.0.0.1:4173/UniverseLab/2026-08-29_UniverseLab_Hyperzeit_10M_ResearchProgram_v1.0.html',{waitUntil:'networkidle'});
  const select=page.locator('[data-ul-language-switcher] select');
  await select.waitFor({state:'visible',timeout:10000});
  assert.strictEqual(await select.locator('option').count(),11,'expected 11 languages');
  const box=await select.boundingBox();
  assert(box && box.x>=0 && box.x+box.width<=412.5,'language selector must stay inside mobile viewport');
  assert.strictEqual(await select.inputValue(),'de');
  assert.deepStrictEqual(errors,[],'page must have no JS errors');

  await page.goto('http://127.0.0.1:4173/UniverseLab/navigator.html',{waitUntil:'networkidle'});
  const navSelect=page.locator('[data-ul-language-switcher] select');
  await navSelect.waitFor({state:'visible',timeout:10000});
  await Promise.all([page.waitForURL(/navigator-en\.html/,{timeout:10000}),navSelect.selectOption('en')]);
  assert(/navigator-en\.html$/.test(new URL(page.url()).pathname),'English must use curated navigator route');
  await browser.close();
  console.log('Language switcher shell contract: PASS');
})().catch(e=>{console.error(e);process.exit(1)});
