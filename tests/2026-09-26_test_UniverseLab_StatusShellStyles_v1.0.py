#!/usr/bin/env python3
"""Status-page shell CSS dependency regression. No science or release authority.

--browser uses actual HTTP. --offline-render is layout-only: local CSS and the
unchanged shell script, with a recorded local SiteState response and no workers.
Do not equate these modes or infer overall page accessibility from these checks.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = ('research-status.html', 'research-status-en.html')
STYLE = 'assets/2026-08-16_UniverseLab_GlobalShell_v1.1.css'
SCRIPT = 'assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js'
STATE = 'registry/2026-09-04_UniverseLab_SiteState_v1.4.json'
LANGUAGE = 'assets/2026-08-30_UniverseLab_SiteLanguageSwitcher_v1.0.js'
LINK = f'<link rel="stylesheet" href="./{STYLE}">'
VIEWPORTS = ((320,740),(390,844),(412,915),(760,900),(761,900),(844,390),(1280,720),(1920,1080))


class Tags(HTMLParser):
    def __init__(self, html: str):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.feed(html)
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def local_path(href: str) -> str:
    return urlsplit(urljoin('https://fixture.invalid/UniverseLab/', href)).path


def dependency_check(html: str) -> None:
    tags = Tags(html).tags
    links = [(i,a) for i,(t,a) in enumerate(tags) if t == 'link' and
             local_path(a.get('href','')) == '/UniverseLab/' + STYLE]
    assert len(links) == 1, f'expected exactly one shell stylesheet, found {len(links)}'
    index, attrs = links[0]
    assert attrs.get('rel','').lower().split() == ['stylesheet'], 'not a stylesheet'
    assert 'disabled' not in attrs, 'disabled stylesheet'
    assert attrs.get('media','all').strip() in ('', 'all', 'screen'), 'print-only or conditional stylesheet'
    assert not urlsplit(attrs['href']).netloc, 'dependency must stay local'
    scripts = [i for i,(t,a) in enumerate(tags) if t == 'script' and
               local_path(a.get('src','')) == '/UniverseLab/' + SCRIPT]
    assert len(scripts) == 1 and index < scripts[0], 'CSS must precede shell script'


def static_checks():
    records = []
    assert (ROOT / STYLE).is_file()
    for name in PAGES:
        html = (ROOT / name).read_text(encoding='utf-8')
        dependency_check(html)
        records.append({'page':name,'case':'direct-stylesheet-dependency','result':'PASS'})
        mutations = {
            'missing': html.replace(LINK, '', 1),
            'duplicate': html.replace(LINK, LINK + LINK, 1),
            'disabled': html.replace(LINK, LINK.replace('rel=', 'disabled rel='), 1),
            'print-only': html.replace(LINK, LINK.replace('rel=', 'media="print" rel='), 1),
            'wrong-target': html.replace(LINK, LINK.replace('v1.1.css', 'missing.css'), 1),
        }
        assert LINK in html, 'mutation fixture must target the actual dependency'
        for case, changed in mutations.items():
            try:
                dependency_check(changed)
            except AssertionError:
                records.append({'page':name,'case':case,'result':'EXPECTED_REJECTION'})
            else:
                raise AssertionError(f'{name}: negative control accepted: {case}')
    return records


def inline_css(path: Path, stack=()) -> str:
    path = path.resolve()
    assert path not in stack, 'circular CSS import'
    text = path.read_text(encoding='utf-8')
    return re.sub(r'@import\s+url\(["\']?([^"\')]+)["\']?\);',
                  lambda m: inline_css(path.parent / m[1], (*stack,path)), text)


def offline_page(page, name):
    html = (ROOT/name).read_text(encoding='utf-8')
    html = re.sub(r'<script\b[^>]*>[\s\S]*?</script>', '', html, flags=re.I)
    def style(m):
        attrs = Tags(m[0]).tags[0][1]
        if attrs.get('rel') != 'stylesheet':
            return m[0]
        path = ROOT / urlsplit(attrs['href']).path.removeprefix('./')
        return '<style>' + inline_css(path) + '</style>'
    html = re.sub(r'<link\b[^>]*>', style, html)
    # Sentinels suppress external bootstrap requests only in this offline fixture.
    html = html.replace('</head>', '<script data-ul-print-export-bootstrap-v10 type="application/json">{}</script>'
                        '<script data-ul-language-switcher-v10 type="application/json">{}</script></head>')
    page.set_content(html)
    state = json.loads((ROOT/STATE).read_text(encoding='utf-8'))
    page.evaluate('(s)=>{window.fetch=async()=>({ok:true,json:async()=>s})}', state)
    page.add_script_tag(content=(ROOT/SCRIPT).read_text(encoding='utf-8'))
    page.locator('.ul-shell').wait_for(state='visible')
    page.add_script_tag(content=(ROOT/LANGUAGE).read_text(encoding='utf-8'))


def geometry(page, name, mode):
    page.locator('.ul-shell').wait_for(state='visible')
    page.locator('.ul-shell__gates [data-ul-language-switcher]').wait_for(state='visible')
    data = page.evaluate('''()=>{
      const q=s=>document.querySelector(s), css=s=>getComputedStyle(q(s));
      return {shellCount:document.querySelectorAll('.ul-shell').length,
        languageCount:document.querySelectorAll('[data-ul-language-switcher]').length,
        shellPosition:css('.ul-shell').position, rowDisplay:css('.ul-shell__row').display,
        navDisplay:css('.ul-shell__nav').display, metaDisplay:css('.ul-shell__meta').display,
        navGap:css('.ul-shell__nav').gap,
        shellWidth:q('.ul-shell').getBoundingClientRect().width,
        viewportWidth:innerWidth, documentWidth:document.documentElement.scrollWidth,
        controller:!!navigator.serviceWorker?.controller};}''')
    assert data['shellCount'] == data['languageCount'] == 1, data
    assert data['shellPosition'] == 'sticky', data
    assert data['rowDisplay'] == data['navDisplay'] == 'flex', data
    assert data['metaDisplay'] == 'grid' and float(data['navGap'].removesuffix('px')) > 0, data
    if mode == 'HTTP-browser':
        selector = f'link[rel="stylesheet"][href="./{STYLE}"]'
        assert page.locator(selector).count() == 1
        assert page.locator(selector).evaluate('(e)=>e.sheet!==null'), 'stylesheet not loaded'
    # Focusability remains testable even when the existing row scrolls horizontally.
    first = page.locator('.ul-shell__nav a').first
    first.focus()
    assert first.evaluate('(e)=>e===document.activeElement')
    # documentWidth is diagnostic only: this test does not claim whole-page containment.
    return {'page':name,'mode':mode,'result':'PASS','geometry':data}


def browser_checks(base_url, out, offline=False):
    from playwright.sync_api import sync_playwright
    records=[]
    out.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        kwargs={'headless':True}
        if os.environ.get('WEB50_CHROMIUM'):kwargs['executable_path']=os.environ['WEB50_CHROMIUM']
        browser=p.chromium.launch(**kwargs)
        try:
            for name in PAGES:
                for width,height in VIEWPORTS:
                    ctx=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
                    page=ctx.new_page()
                    try:
                        if offline:
                            offline_page(page,name)
                        else:
                            res=page.goto(urljoin(base_url,name),wait_until='networkidle')
                            assert res and res.status==200
                        item=geometry(page,name,'offline-layout' if offline else 'HTTP-browser')
                        item['viewport']=[width,height];item['case']='fresh-client'
                        records.append(item)
                        page.evaluate('scrollTo(0,0)')
                        page.screenshot(path=str(out/f'{name}-{width}x{height}.png'))
                        if not offline and width==390:
                            page.wait_for_function('!!navigator.serviceWorker.controller', timeout=15000)
                            for case in ('controlled-reload','controlled-return'):
                                if case=='controlled-return':
                                    page.goto(urljoin(base_url,'navigator.html'),wait_until='networkidle')
                                    page.goto(urljoin(base_url,name),wait_until='networkidle')
                                else:page.reload(wait_until='networkidle')
                                item=geometry(page,name,'HTTP-browser')
                                assert item['geometry']['controller'], 'controlled case was not controlled'
                                item.update({'viewport':[width,height],'case':case});records.append(item)
                    finally:ctx.close()
            if not offline:
                for name in PAGES:
                    ctx=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
                    try:
                        page=ctx.new_page();res=page.goto(urljoin(base_url,name),wait_until='networkidle')
                        assert res and res.status==200
                        assert page.locator('main .top a').is_visible()
                        assert page.locator(f'link[href="./{STYLE}"]').evaluate('(e)=>e.sheet!==null')
                        records.append({'page':name,'case':'no-JavaScript-content-and-return','result':'PASS'})
                    finally:ctx.close()
        finally:browser.close()
    return records


def main():
    ap=argparse.ArgumentParser()
    mode=ap.add_mutually_exclusive_group()
    mode.add_argument('--browser',action='store_true');mode.add_argument('--offline-render',action='store_true')
    ap.add_argument('--render-only',action='store_true',help='For negative layout controls; omit static precheck')
    ap.add_argument('--base-url',default='http://127.0.0.1:4173/UniverseLab/')
    ap.add_argument('--output',type=Path,default=ROOT/'web50-status-shell-report')
    args=ap.parse_args()
    result={'scope':'status shell stylesheet only','physical_gate_effect':'NONE','physical_evidence_effect':'NONE'}
    try:
        if not args.render_only:result['static_cases']=static_checks()
        if args.browser or args.offline_render:
            result['browser_cases']=browser_checks(args.base_url,args.output,args.offline_render)
        result['result']='PASS'
    except Exception as exc:
        result.update({'result':'FAIL','error':str(exc)})
        raise
    finally:
        args.output.mkdir(parents=True,exist_ok=True)
        (args.output/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result,indent=2))

if __name__=='__main__':main()
