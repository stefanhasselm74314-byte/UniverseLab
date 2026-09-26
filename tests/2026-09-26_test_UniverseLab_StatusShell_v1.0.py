#!/usr/bin/env python3
"""WEB50-RUN-005: bounded CSS dependency/overflow repair, never adjudication.

Default runs stdlib source guards. --browser runs Chromium over HTTP.
--offline-layout inlines audited CSS and renders only shell DOM with a fixture
state; it is deliberately not HTTP, service-worker or live-deployment QA.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import subprocess
import unittest
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = '9e34903a09db17fb6d3c338be13ab934f16f09f1'
SHELL_CSS = 'assets/2026-08-16_UniverseLab_GlobalShell_v1.1.css'
SHELL_JS = 'assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js'
LINK = '<link rel="stylesheet" href="./assets/2026-08-16_UniverseLab_GlobalShell_v1.1.css?v=20260926-status">'
RULE = 'body[data-ul-page-id="UL-PAGE-RESEARCH-STATUS"] main{min-width:0;overflow-wrap:anywhere}body[data-ul-page-id="UL-PAGE-RESEARCH-STATUS"] .grid{grid-template-columns:repeat(12,minmax(0,1fr))}body[data-ul-page-id="UL-PAGE-RESEARCH-STATUS"] .card{min-width:0}'
BASE_BLOBS = {'research-status.html': '3fff2ef8b763e1bb26a79c2279c51592c009b39f', 'research-status-en.html': 'ff61b2091014ea9945e21a5948702c02d0b164a9'}
ASSET_BLOBS = {SHELL_CSS: 'fd85add76eea41f48853aa8b16279631da5c5299', SHELL_JS: '5ce99b21ff6d5a8876f90d7c34f4f4073d80a357'}
VIEWPORTS = [(320,740),(360,800),(390,844),(412,915),(720,900),(760,900),(761,900),(844,390),(1280,720),(1920,1080)]

def blob_id(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def check_source(name: str, text: str) -> None:
    assert text.count(LINK) == 1, 'exactly one explicit shell stylesheet'
    assert text.count(RULE) == 1, 'bounded containment rules required'
    assert text.index(LINK) < text.index('<script src="./' + SHELL_JS)
    restored = text.replace(LINK, '', 1).replace(RULE, '', 1)
    assert blob_id(restored.encode()) == BASE_BLOBS[name], 'out-of-scope source change'
    assert text.count('\n') == restored.count('\n'), 'claim source lines shifted'

class SourceGuards(unittest.TestCase):
    def test_exact_bounded_delta(self):
        for name in BASE_BLOBS:
            check_source(name, (ROOT/name).read_text())
    def test_missing_stylesheet_rejected(self):
        for name in BASE_BLOBS:
            with self.assertRaises(AssertionError):
                check_source(name, (ROOT/name).read_text().replace(LINK, ''))
    def test_duplicate_stylesheet_rejected(self):
        for name in BASE_BLOBS:
            with self.assertRaises(AssertionError):
                check_source(name, (ROOT/name).read_text().replace(LINK, LINK+LINK))
    def test_removed_containment_rejected(self):
        for name in BASE_BLOBS:
            with self.assertRaises(AssertionError):
                check_source(name, (ROOT/name).read_text().replace(RULE, ''))
    def test_changed_scientific_copy_rejected(self):
        for name in BASE_BLOBS:
            with self.assertRaises(AssertionError):
                check_source(name, (ROOT/name).read_text().replace('<p class="lead">','<p class="lead">MUTATED ',1))
    def test_changed_source_lines_rejected(self):
        for name in BASE_BLOBS:
            with self.assertRaises(AssertionError):
                check_source(name, '\n'+(ROOT/name).read_text())
    def test_existing_shell_assets_unchanged(self):
        for path, expected in ASSET_BLOBS.items():
            self.assertEqual(blob_id((ROOT/path).read_bytes()), expected)

def inline_css(path: Path) -> str:
    return re.sub(r'@import\s+url\(["\']?([^"\')]+)["\']?\);',
                  lambda m:inline_css((path.parent/m[1]).resolve()),path.read_text())

def offline_page(page, name: str) -> None:
    text = re.sub(r'<script\b[^>]*>[\s\S]*?</script>', '', (ROOT/name).read_text(), flags=re.I)
    def embed(match):
        href = re.search(r'href="([^"]+)"', match[0])[1]
        return '<style>'+inline_css(ROOT/urlparse(href).path)+'</style>'
    text = re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>', embed, text)
    page.set_content(text)
    state=json.loads((ROOT/'registry/2026-09-04_UniverseLab_SiteState_v1.4.json').read_text())
    page.evaluate('(s)=>{window.fetch=async()=>({ok:true,json:async()=>s})}',state)
    shell=(ROOT/SHELL_JS).read_text().split("\n(()=>{'use strict';if(new URLSearchParams")[0]
    page.add_script_tag(content=shell)

MEASURE = '''() => {
  const q = s => document.querySelector(s);
  const rect = e => { const r=e.getBoundingClientRect(); return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right}; };
  const css = [...document.querySelectorAll('link[rel~="stylesheet"]')].filter(l=>l.href.includes('GlobalShell_v1.1.css'));
  const shell=q('.ul-shell');
  return {viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,
    shell:shell?rect(shell):null,position:shell?getComputedStyle(shell).position:null,
    rowDisplay:q('.ul-shell__row')?getComputedStyle(q('.ul-shell__row')).display:null,
    navDisplay:q('.ul-shell__nav')?getComputedStyle(q('.ul-shell__nav')).display:null,
    stylesheetLinks:css.length,stylesheetLoaded:css.length===1&&!!css[0].sheet,
    boxes:[...document.querySelectorAll('main h1, main .hero, main .card, main code')].map(rect)};
}'''

def check_layout(page, *, shell=True, http=True):
    if shell: page.locator('.ul-shell').wait_for()
    m=page.evaluate(MEASURE)
    assert m['scrollWidth'] <= m['viewport']+1, m
    assert all(b['x']>=-1 and b['right']<=m['viewport']+1 for b in m['boxes']), m
    if shell:
        assert m['position']=='sticky' and m['rowDisplay']=='flex' and m['navDisplay']=='flex', m
        assert page.locator('.ul-shell').count()==1
        if http:
            assert m['stylesheetLinks']==1 and m['stylesheetLoaded'], m
            assert page.locator('[data-ul-language-switcher]').count()==1
    assert page.locator('main h1').is_visible()
    return m

def browser_checks(base, out, offline=False):
    from playwright.sync_api import sync_playwright
    results=[];out.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        opts={'headless':True}
        if os.getenv('WEB50_CHROMIUM'): opts['executable_path']=os.environ['WEB50_CHROMIUM']
        browser=p.chromium.launch(**opts)
        for name in BASE_BLOBS:
            for width,height in VIEWPORTS:
                ctx=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce',service_workers='block')
                page=ctx.new_page();errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                if offline: offline_page(page,name)
                else:
                    response=page.goto(urljoin(base,name),wait_until='networkidle')
                    assert response and response.status==200
                    page.locator('[data-ul-language-switcher] select').wait_for(state='visible')
                m=check_layout(page,http=not offline)
                assert not errors, errors
                page.screenshot(path=str(out/f'{name}-{width}x{height}.png'))
                results.append({'page':name,'viewport':[width,height],'case':'layout','result':'PASS','metrics':m})
                if width==390:
                    page.add_style_tag(content='html{font-size:200% !important}')
                    z=check_layout(page,http=not offline)
                    results.append({'page':name,'case':'CSS-root-text-scale-200-percent','result':'PASS','metrics':z})
                ctx.close()
        if not offline:
            for name in BASE_BLOBS:
                for width,height in [(390,844),(1280,720)]:
                    ctx=browser.new_context(viewport={'width':width,'height':height},java_script_enabled=False)
                    page=ctx.new_page();response=page.goto(urljoin(base,name),wait_until='networkidle')
                    assert response and response.status==200
                    m=check_layout(page,shell=False)
                    page.locator('main .top a').focus()
                    assert page.locator('main .top a').evaluate('(e)=>e===document.activeElement')
                    results.append({'page':name,'viewport':[width,height],'case':'no-JavaScript','result':'PASS','metrics':m});ctx.close()
            for name in BASE_BLOBS:
                ctx=browser.new_context(viewport={'width':390,'height':844},service_workers='allow')
                page=ctx.new_page();page.goto(urljoin(base,name),wait_until='networkidle')
                page.wait_for_function('navigator.serviceWorker.controller !== null')
                page.reload(wait_until='networkidle')
                m=check_layout(page)
                results.append({'page':name,'case':'controlled-client-reload','result':'PASS','metrics':m})
                session=ctx.new_cdp_session(page)
                session.send('Network.enable');session.send('Network.setCacheDisabled',{'cacheDisabled':True})
                page.reload(wait_until='networkidle');m=check_layout(page)
                results.append({'page':name,'case':'controlled-client-cache-disabled-reload','result':'PASS','metrics':m});ctx.close()
        browser.close()
    return results

def main():
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group();mode.add_argument('--browser',action='store_true');mode.add_argument('--offline-layout',action='store_true')
    parser.add_argument('--base-url',default='http://127.0.0.1:4173/UniverseLab/')
    parser.add_argument('--output',type=Path,default=ROOT/'web50-status-report')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    run=subprocess.run(['git','-C',str(ROOT),'rev-parse','HEAD'],capture_output=True,text=True)
    report={'base_sha':BASE_SHA,'tested_sha':run.stdout.strip() if run.returncode==0 else None,
            'mode':'HTTP-browser' if args.browser else 'offline-inlined-layout' if args.offline_layout else 'static',
            'physical_gate_effect':'NONE','physical_evidence_effect':'NONE','overall_release_approval':False}
    tests=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceGuards))
    report['source_tests']={'run':tests.testsRun,'failures':len(tests.failures),'errors':len(tests.errors)}
    try:
        assert tests.wasSuccessful(), 'source guards failed'
        if args.browser or args.offline_layout:
            report['browser_cases']=browser_checks(args.base_url,args.output,args.offline_layout)
        report['result']='PASS'
    except Exception as exc:
        report.update(result='FAIL',error=str(exc));raise
    finally:
        (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'result':report['result'],'source_tests':report['source_tests'],'browser_cases':len(report.get('browser_cases',[]))},indent=2))

if __name__=='__main__':main()
