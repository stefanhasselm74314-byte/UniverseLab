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
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = '9e34903a09db17fb6d3c338be13ab934f16f09f1'
SHELL_CSS = 'assets/2026-08-16_UniverseLab_GlobalShell_v1.1.css'
SHELL_JS = 'assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js'
LINK = '<link rel="stylesheet" href="./assets/2026-08-16_UniverseLab_GlobalShell_v1.1.css?v=20260926-status">'
RULE = 'body[data-ul-page-id="UL-PAGE-RESEARCH-STATUS"] main{min-width:0;overflow-wrap:anywhere}body[data-ul-page-id="UL-PAGE-RESEARCH-STATUS"] .grid{grid-template-columns:repeat(12,minmax(0,1fr))}body[data-ul-page-id="UL-PAGE-RESEARCH-STATUS"] .card{min-width:0}'
BASE_BLOBS = {'research-status.html': '3fff2ef8b763e1bb26a79c2279c51592c009b39f', 'research-status-en.html': 'ff61b2091014ea9945e21a5948702c02d0b164a9'}
# Reviewed runtime asset boundary at BASE_SHA, not functional certification.
# Includes CSS imports and dynamically loaded utilities, including the worker.
# A legitimate dependency update requires an explicit reviewed manifest refresh
# and that dependency's own QA, not a silent re-baseline by this test.
ASSET_BLOBS = {'assets/2026-08-16_UniverseLab_GlobalShell_v1.1.css': 'fd85add76eea41f48853aa8b16279631da5c5299', 'assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js': '5ce99b21ff6d5a8876f90d7c34f4f4073d80a357', 'assets/2026-08-01_UniverseLab_MobileTypography_v1.1.css': '65bcba803086808839b830a9e70451eb19b12b69', 'assets/2026-08-05_UniverseLab_DesktopCompact_v1.0.css': '16a1323b169fe50bce7094d9a57024e67c1e6598', 'assets/2026-08-05_UniverseLab_Export_v1.0.css': '87c2f99b3f6791853f4e67203d6a0a9ef062f055', 'assets/2026-08-05_UniverseLab_Export_v1.0.js': '3e532fbce047b96562f6046336964a6846bae81e', 'assets/2026-08-19_UniverseLab_SitePrintExportBootstrap_v1.0.js': '47682cfe71483040d50de16a5a9c7737f0194ce1', 'assets/2026-08-19_UniverseLab_SitePrintExport_v1.0.js': '6ea788f98a53d243ff3a949ea8a2e78d361f4331', 'assets/2026-08-27_UniverseLab_DocumentLinkRouter_v1.0.js': '58bd538927c94f69ad2d20370b3d4e8e7efb117d', 'assets/2026-08-30_UniverseLab_SiteLanguageSwitcher_v1.0.js': '4890f2cd50a045e4bfc1bb5e11ea3fe9f51f4821', '2026-08-19_UniverseLab_SitePrintExportServiceWorker_v1.0.js': '57023b4c646e921ed15ad7c1b2721bdb44175f0c'}
MOBILE_CSS = 'assets/2026-08-01_UniverseLab_MobileTypography_v1.1.css'
EXPORT_CSS = 'assets/2026-08-05_UniverseLab_Export_v1.0.css'

VIEWPORTS = [(320,740),(360,800),(390,844),(412,915),(720,900),(760,900),(761,900),(844,390),(1280,720),(1920,1080)]

def blob_id(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

class ResourceTags(HTMLParser):
    """Parse actual links/scripts; comments and script strings are not links."""
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.resources = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        if tag in ('link', 'script'):
            self.resources.append((tag, dict(attrs)))


def resource_path(href: str) -> str:
    parsed = urlparse(href)
    assert not parsed.scheme and not parsed.netloc, 'dependency must be local'
    path = parsed.path
    if path.startswith('/UniverseLab/'):
        return path[len('/UniverseLab/'):]
    assert not path.startswith('/'), 'dependency must stay under Pages base'
    return path.removeprefix('./')


def check_stylesheet_order(name: str, text: str) -> None:
    resources = ResourceTags(text).resources
    styles = []
    for index, (tag, attrs) in enumerate(resources):
        if tag != 'link' or 'stylesheet' not in attrs.get('rel', '').lower().split():
            continue
        assert 'disabled' not in attrs, 'disabled stylesheet'
        assert attrs.get('media', 'all').strip().lower() in ('', 'all', 'screen'), 'inactive stylesheet'
        styles.append((index, resource_path(attrs.get('href', ''))))
    expected = [SHELL_CSS, MOBILE_CSS] + ([EXPORT_CSS] if name == 'research-status.html' else [])
    assert [path for _, path in styles] == expected, 'stylesheet cascade order changed'
    scripts = [i for i, (tag, a) in enumerate(resources) if tag == 'script'
               and a.get('src') and resource_path(a['src']) == SHELL_JS]
    assert len(scripts) == 1 and styles[-1][0] < scripts[0], 'styles must precede shell script'


def check_assets(reader=None) -> None:
    reader = reader or (lambda path: (ROOT/path).read_bytes())
    for path, expected in ASSET_BLOBS.items():
        assert blob_id(reader(path)) == expected, f'Unreviewed runtime dependency: {path}'


def font_ratios(before, after, *, require_double=False):
    assert before and len(before) == len(after), 'missing font samples'
    rows = []
    for left, right in zip(before, after):
        assert left['key'] == right['key'], 'font sample identity changed'
        b, a = left['px'], right['px']
        assert b > 0 and a > 0, 'invalid font size'
        ratio = a/b
        rows.append({'key':left['key'], 'before_px':b, 'after_px':a, 'ratio':ratio})
    if require_double:
        bad = [row for row in rows if not 1.98 <= row['ratio'] <= 2.02]
        assert not bad, f'text not doubled: {bad[:12]}'
    return rows


def check_source(name: str, text: str) -> None:
    assert text.count(LINK) == 1, 'exactly one explicit shell stylesheet'
    assert text.count(RULE) == 1, 'bounded containment rules required'
    check_stylesheet_order(name, text)
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
    def test_runtime_assets_unchanged(self):
        check_assets()

    def test_each_runtime_dependency_mutation_rejected(self):
        for target in ASSET_BLOBS:
            with self.subTest(path=target), self.assertRaisesRegex(AssertionError, 'Unreviewed runtime dependency'):
                check_assets(lambda path: b'/* valid empty control stub */' if path == target else (ROOT/path).read_bytes())

    def test_each_runtime_dependency_missing_rejected(self):
        for target in ASSET_BLOBS:
            def read(path):
                if path == target:
                    raise FileNotFoundError(path)
                return (ROOT/path).read_bytes()
            with self.subTest(path=target), self.assertRaises(FileNotFoundError):
                check_assets(read)

    def test_late_stylesheet_insertions_rejected(self):
        for name in BASE_BLOBS:
            text = (ROOT/name).read_text()
            for other in [MOBILE_CSS] + ([EXPORT_CSS] if name == 'research-status.html' else []):
                link = f'<link rel="stylesheet" href="./{other}">'
                changed = text.replace(LINK, '', 1).replace(link, link+LINK, 1)
                # This was a real blind spot: restoration still matches the baseline.
                restored = changed.replace(LINK, '', 1).replace(RULE, '', 1)
                self.assertEqual(blob_id(restored.encode()), BASE_BLOBS[name])
                with self.subTest(page=name, after=other), self.assertRaisesRegex(AssertionError, 'cascade order'):
                    check_source(name, changed)

    def test_stylesheet_comment_and_disabled_rejected(self):
        for name in BASE_BLOBS:
            text = (ROOT/name).read_text()
            for replacement in ['<!--'+LINK+'-->', LINK.replace('rel=', 'disabled rel='),
                                LINK.replace('rel=', 'media="print" rel='), LINK.replace('rel=', 'rel="preload" data-old-rel=')]:
                with self.subTest(page=name, replacement=replacement), self.assertRaises(AssertionError):
                    check_stylesheet_order(name, text.replace(LINK, replacement))

    def test_workflow_covers_exact_runtime_dependencies(self):
        workflow = (ROOT/'.github/workflows/2026-09-26_UniverseLab_StatusShell_QA_v1.0.yml').read_text()
        paths = re.findall(r"^      - '([^']+)'$", workflow, re.M)
        expected = set(ASSET_BLOBS) | set(BASE_BLOBS) | {
            'tests/2026-09-26_test_UniverseLab_StatusShell_v1.0.py',
            '.github/workflows/2026-09-26_UniverseLab_StatusShell_QA_v1.0.yml'}
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(set(paths), expected)

    def test_font_ratio_contract(self):
        before = [{'key':'body', 'px':17}, {'key':'control', 'px':10}]
        self.assertEqual(len(font_ratios(before,[{'key':'body','px':34},{'key':'control','px':20}],require_double=True)),2)
        for after in [before, [{'key':'body','px':34},{'key':'control','px':10}],
                      [{'key':'body','px':25.5},{'key':'control','px':15}], [],
                      [{'key':'other','px':34},{'key':'control','px':20}],
                      [{'key':'body','px':34},{'key':'control','px':0}]]:
            with self.subTest(after=after), self.assertRaises(AssertionError):
                font_ratios(before,after,require_double=True)


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

# Test-only font intervention. Snapshot every rendered element in the document
# and OPEN shadow roots before changing any size. Explicit px sizes (including
# controls) are doubled too; no production CSS/HTML is edited. This synthetic
# stress test is NOT native browser zoom or a WCAG conformance attestation.
CAPTURE_FONTS = r"""() => {
  const nodes=[];
  function visit(root){
    for(const e of root.querySelectorAll('*')){
      if(e.tagName==='SCRIPT'||e.tagName==='STYLE') continue;
      const s=getComputedStyle(e);
      if(e.getClientRects().length && s.visibility!=='hidden' && parseFloat(s.fontSize)>0)
        nodes.push({e,key:`${nodes.length}:${e.tagName}:${e.id||e.className||''}`,px:parseFloat(s.fontSize)});
      if(e.shadowRoot) visit(e.shadowRoot);
    }
  }
  visit(document);
  for(const selector of ['body','main h1','main .lead','main code','.ul-shell__nav a','#k1d']){
    const el=document.querySelector(selector);
    if(!el||!nodes.some(n=>n.e===el)) throw Error('Missing resize probe: '+selector);
  }
  window.__web50FontSnapshot=nodes;
  return nodes.map(({key,px})=>({key,px}));
}"""
READ_FONTS = "() => window.__web50FontSnapshot.map(({e,key})=>({key,px:parseFloat(getComputedStyle(e).fontSize)}))"
SCALE_FONTS = "() => window.__web50FontSnapshot.forEach(({e,px})=>e.style.setProperty('font-size', `${px*2}px`, 'important'))"


def resize_checks(page, name, out, *, http):
    before=page.evaluate(CAPTURE_FONTS)
    root_style=page.add_style_tag(content='html{font-size:200% !important}')
    after=page.evaluate(READ_FONTS)
    ratios=font_ratios(before,after)
    metrics=check_layout(page,http=http)
    # The old root-only probe is retained, but explicitly cannot count as a
    # successful full-resize scenario. Its partial scaling is negative evidence.
    try:
        font_ratios(before,after,require_double=True)
    except AssertionError:
        rejects_partial=True
    else:
        rejects_partial=False
    diagnostic={'page':name,'case':'root-font-only-diagnostic','result':'DIAGNOSTIC',
                'full_resize_claim':False,'partial_scaling_rejected':rejects_partial,
                'fonts':ratios,'metrics':metrics}
    root_style.evaluate('(e)=>e.remove()')
    before=page.evaluate(CAPTURE_FONTS)
    page.evaluate(SCALE_FONTS)
    after=page.evaluate(READ_FONTS)
    rows=font_ratios(before,after)
    (out/f'{name}-font-resize-evidence.json').write_text(
        json.dumps({'root_font_diagnostic':diagnostic, 'synthetic_fonts':rows},indent=2)+'\n')
    font_ratios(before,after,require_double=True)
    metrics=check_layout(page,http=http)
    page.screenshot(path=str(out/f'{name}-390x844-synthetic-text-200.png'))
    resized={'page':name,'case':'synthetic-all-rendered-fonts-200-percent','result':'PASS',
             'native_browser_zoom':False,'wcag_conformance_claim':False,
             'fonts':rows,'metrics':metrics}
    return [diagnostic,resized]


def browser_checks(base, out, offline=False):
    from playwright.sync_api import sync_playwright
    results=[];out.mkdir(parents=True,exist_ok=True)
    def record(value):
        results.append(value)
        (out/'browser-progress.json').write_text(json.dumps(results,indent=2)+'\n')
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
                record({'page':name,'viewport':[width,height],'case':'layout','result':'PASS','metrics':m})
                if width==390:
                    for item in resize_checks(page,name,out,http=not offline):
                        record(item)
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
                    record({'page':name,'viewport':[width,height],'case':'no-JavaScript','result':'PASS','metrics':m});ctx.close()
            for name in BASE_BLOBS:
                ctx=browser.new_context(viewport={'width':390,'height':844},service_workers='allow')
                page=ctx.new_page();page.goto(urljoin(base,name),wait_until='networkidle')
                # Production bootstrap intentionally registers on HTTPS only.
                # Seed the unchanged worker ONLY in this trusted loopback fixture
                # to exercise an already-controlled client, not auto-registration.
                assert page.evaluate('isSecureContext'), 'worker fixture needs a secure context'
                parsed=urlparse(base)
                if parsed.scheme=='http':
                    assert parsed.hostname in ('127.0.0.1','localhost','::1'), 'loopback fixture only'
                    assert page.evaluate('navigator.serviceWorker.controller === null')
                    page.evaluate('''async () => {
                      const reg=await navigator.serviceWorker.register(
                        '/UniverseLab/2026-08-19_UniverseLab_SitePrintExportServiceWorker_v1.0.js',
                        {scope:'/UniverseLab/'});
                      await navigator.serviceWorker.ready;
                      return reg.scope;
                    }''')
                page.wait_for_function('navigator.serviceWorker.controller !== null')
                assert page.evaluate("navigator.serviceWorker.controller.scriptURL.endsWith('/2026-08-19_UniverseLab_SitePrintExportServiceWorker_v1.0.js')")
                page.reload(wait_until='networkidle')
                m=check_layout(page)
                record({'page':name,'case':'explicit-worker-fixture-controlled-reload','result':'PASS','metrics':m})
                session=ctx.new_cdp_session(page)
                session.send('Network.enable');session.send('Network.setCacheDisabled',{'cacheDisabled':True})
                page.reload(wait_until='networkidle');m=check_layout(page)
                record({'page':name,'case':'explicit-worker-fixture-cache-disabled-reload','result':'PASS','metrics':m});ctx.close()
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
            'physical_gate_effect':'NONE','physical_evidence_effect':'NONE','overall_release_approval':False,
            'dependency_basis_sha':BASE_SHA,'runtime_asset_blobs':ASSET_BLOBS,
            'text_resize_scope':'synthetic computed-font intervention; not native zoom or WCAG conformance'}
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
