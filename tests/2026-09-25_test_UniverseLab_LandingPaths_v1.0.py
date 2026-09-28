#!/usr/bin/env python3
"""Read-only landing regression. UI checks do not confer scientific authority.

Default: standard-library static checks. --browser adds actual HTTP/Playwright
checks; --offline-render is a separate layout-only mode for offline review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = '11054f84a496497de3b9db3cd6db65f7bfaa3d86'
CSS = 'assets/2026-09-25_UniverseLab_LandingPaths_v1.0.css'
BASELINE = {'index.html': {'copy': '40c72926fdf69f7cc74dc907840ab7d56186639432c39d72af423ac088683827', 'scripts': '4f4473d83997c7e1f1a2ae4a995179d3764942421bb9394bbecab62ce5dc638b', 'metadata': '3d51cd346b1daa34b564cc14dcd2eea241a95990b7d0867452de23b211558ce4'}, 'index-en.html': {'copy': 'c56ee18ec2085da888ac3978444172c8638034e7755203f7a8bb918ca1b3d83b', 'scripts': '1cbf6925935355b4e0e6b4ba5ed12edb797f0db8a0a8f5cdde81ca8a16a41108', 'metadata': 'b452433eba9accf9b4ad5695d9992c850ea8c1a253c5cba59b571d65f8d0e856'}}  # Frozen BASE_SHA fingerprints.

class Node:
    def __init__(self, tag='', attrs=(), parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.parts = []
    @property
    def text(self):
        return ''.join(p.text if isinstance(p, Node) else p for p in self.parts)
    def has(self, name):
        return name in self.attrs.get('class', '').split()

class DOM(HTMLParser):
    VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Node(); self.current = self.root; self.nodes = []
        self.feed(html)
    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.parts.append(node); self.nodes.append(node)
        if tag not in self.VOID: self.current = node
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID: self.handle_endtag(tag)
    def handle_endtag(self, tag):
        n = self.current
        while n.parent is not None:
            if n.tag == tag:
                self.current = n.parent; return
            n = n.parent
    def handle_data(self, data): self.current.parts.append(data)
    def select(self, tag=None, cls=None):
        return [n for n in self.nodes if (tag is None or n.tag == tag) and (cls is None or n.has(cls))]

def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def protected(html):
    d = DOM(html)
    # Freeze science descriptions/status language, all existing code and metadata.
    copy = []
    for n in d.nodes:
        if any(n.has(c) for c in ('lead','facts','code','status','note')):
            copy.append(' '.join(n.text.split()))
        if n.tag in ('p','h2','h3') and n.parent and n.parent.has('card'):
            copy.append(' '.join(n.text.split()))
    scripts = re.findall(r'<script\b[^>]*>[\s\S]*?</script>', html, re.I)
    metas = re.findall(r'<meta\b[^>]*>|<title>[\s\S]*?</title>|<link\b[^>]*rel="(?:canonical|alternate)"[^>]*>', html, re.I)
    return {'copy': digest('\n'.join(copy)), 'scripts': digest('\n'.join(scripts)), 'metadata': digest('\n'.join(metas))}

def static_checks():
    pairs = json.loads((ROOT/'2026-08-20_UniverseLab_MultilingualRouteRegistry_v1.1.json').read_text())['route_pairs']
    route_map = {p['de'].split('/')[-1]:p['en'].split('/')[-1] for p in pairs}
    assertions = 0
    for name, lang in [('index.html','de'), ('index-en.html','en')]:
        html = (ROOT/name).read_text(); dom = DOM(html)
        assert protected(html) == BASELINE[name], f'{name}: protected scientific copy/code/metadata changed'
        assertions += 3
        assert len(dom.select('h1')) == 1
        ids = [n.attrs['id'] for n in dom.nodes if 'id' in n.attrs]
        assert len(ids) == len(set(ids)), f'{name}: duplicate id'
        assert 'ul-home-main' in ids and 'ul-home-modules' in ids
        assert len(dom.select('details','ul-home-menu')) == 1
        menu = dom.select('details','ul-home-menu')[0]
        assert 'open' not in menu.attrs
        assert any(isinstance(n,Node) and n.tag=='summary' for n in menu.parts)
        assert len(dom.select('nav','ul-home-nav')) == 1
        assert len(dom.select('nav','ul-home-paths')) == 1
        entries = [n for n in dom.select('a') if 'data-ul-entry' in n.attrs]
        assert [n.attrs['data-ul-entry'] for n in entries] == ['explore','research','solvers']
        expected = ['observatory.html','research-status.html','solver-hub.html']
        if lang=='en': expected = [route_map[p] for p in expected]
        assert [n.attrs['href'] for n in entries] == ['./'+p for p in expected]
        assert len([n for n in dom.select('link') if n.attrs.get('href')=='./'+CSS])==1
        assert dom.select('a','ul-home-skip')[0].attrs['href']=='#ul-home-main'
        assertions += 12
        for n in dom.select('a'):
            href=n.attrs.get('href',''); u=urlparse(href)
            assert u.scheme not in ('javascript','data'), f'{name}: unsafe navigation'
            if u.scheme or u.netloc: continue
            path=unquote(u.path).removeprefix('./')
            target=ROOT/(path or (name if u.fragment else 'index.html'))
            assert target.is_file(), f'{name}: missing target {href}'
            if u.fragment:
                target_ids={x.attrs.get('id') for x in DOM(target.read_text()).nodes}
                assert unquote(u.fragment) in target_ids, f'{name}: missing fragment {href}'
            if lang=='en' and path in route_map and path:
                raise AssertionError(f'{name}: bypasses curated English route: {href}')
            assertions += 1
    css=(ROOT/CSS).read_text()
    assert '@import' not in css and 'url(' not in css, 'No new remote assets'
    assert ':focus-visible' in css and '44px' in css
    assert all(x not in css for x in ('canvas','animation:','transition:')), 'Landing must not change renderer/motion'
    return assertions+3

def inline_css(path, seen=None):
    seen=set() if seen is None else seen
    if path in seen: return ''
    seen.add(path); s=path.read_text()
    return re.sub(r'@import\s+url\(["\']?([^"\')]+)["\']?\);', lambda m:inline_css((path.parent/m[1]).resolve(),seen),s)

def assert_brand_layout(page, name, width):
    """Check rendered geometry, not a CSS keyword: a block mark must not stack EN."""
    brand = page.locator('.ul-landing .shell .brand')
    mark = brand.locator('.mark')
    word = brand.locator('strong')
    assert brand.count() == mark.count() == word.count() == 1
    assert mark.is_visible(), f'{name}/{width}: brand mark missing'
    outer, icon = brand.bounding_box(), mark.bounding_box()
    assert outer and icon and outer['height'] >= 44
    assert outer['x'] >= -1 and outer['x'] + outer['width'] <= width + 1
    metrics = {'brand': outer, 'mark': icon, 'wordmark_visible': word.is_visible()}
    if width <= 760:
        assert not word.is_visible(), f'{name}/{width}: compact wordmark must stay hidden'
    else:
        assert word.is_visible(), f'{name}/{width}: desktop wordmark missing'
        label = word.bounding_box()
        assert label and label['width'] > 0 and label['height'] > 0
        delta = abs((icon['y'] + icon['height']/2) - (label['y'] + label['height']/2))
        metrics.update({'wordmark': label, 'center_y_delta': delta})
        assert delta <= 1, f'{name}/{width}: brand stacked or vertically misaligned: {metrics}'
        assert icon['x'] + icon['width'] <= label['x'] + 1, f'{name}/{width}: brand items overlap'
        assert label['x'] + label['width'] <= outer['x'] + outer['width'] + 1
    return metrics

def render_checks(base_url, out, offline=False):
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True,exist_ok=True)
    cases=[]
    with sync_playwright() as p:
        kwargs={'headless':True}
        if os.environ.get('WEB50_CHROMIUM'): kwargs['executable_path']=os.environ['WEB50_CHROMIUM']
        browser=p.chromium.launch(**kwargs)
        for name in ('index.html','index-en.html'):
            for width,height in ((320,740),(360,800),(390,844),(412,915),(844,390),(760,900),(761,900),(768,1024),(1280,720),(1920,1080)):
                ctx=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
                page=ctx.new_page();errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                if offline:
                    html=(ROOT/name).read_text()
                    html=re.sub(r'<script\b[^>]*>[\s\S]*?</script>','',html,flags=re.I)
                    def embed(m):
                        href=re.search(r'href="([^"]+)"',m[0])
                        return '<style>'+inline_css((ROOT/href[1]).resolve())+'</style>' if href else m[0]
                    html=re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>',embed,html)
                    page.set_content(html)
                    # Run the actual unmodified switcher only, for layout. No SW/network proof.
                    js='assets/2026-08-30_UniverseLab_SiteLanguageSwitcher_v1.0.js' if name=='index.html' else 'assets/2026-08-18_UniverseLab_SiteLanguageSwitcher_v1.1.js'
                    page.add_script_tag(content=(ROOT/js).read_text())
                else:
                    response=page.goto(urljoin(base_url,name),wait_until='networkidle')
                    assert response and response.status==200
                page.locator('[data-ul-language-switcher] select').wait_for(state='visible')
                assert page.locator('[data-ul-language-switcher]').count()==1
                brand_metrics = assert_brand_layout(page, name, width)
                menu=page.locator('.ul-home-menu'); summary=menu.locator('summary')
                assert menu.get_attribute('open') is None
                page.keyboard.press('Tab')
                assert page.locator('.ul-home-skip').evaluate('(e)=>e===document.activeElement')
                page.keyboard.press('Enter')
                assert page.locator('#ul-home-main').evaluate('(e)=>e===document.activeElement')
                page.evaluate('scrollTo(0,0)')
                summary.focus();page.keyboard.press('Enter')
                assert menu.get_attribute('open') is not None
                links=page.locator('.ul-home-nav a'); assert links.count()==5
                for a in links.all()+page.locator('[data-ul-entry]').all():
                    box=a.bounding_box()
                    assert box and box['width']>=44 and box['height']>=44, f'{name}/{width}: target size {a.inner_text()} {box}'
                    assert box['x']>=-1 and box['x']+box['width']<=width+1, f'{name}/{width}: clipped target'
                page.screenshot(path=str(out/f'{name}-{width}x{height}-menu.png'))
                page.keyboard.press('Enter')
                assert menu.get_attribute('open') is None
                page.evaluate('scrollTo(0,0)')
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), f'{name}/{width}: body overflow'
                page.screenshot(path=str(out/f'{name}-{width}x{height}.png'))
                assert not errors, errors
                cases.append({'page':name,'viewport':[width,height],'mode':'offline-layout' if offline else 'HTTP-browser','result':'PASS','brand_geometry':brand_metrics})
                ctx.close()
        if not offline:
            # Verify both curated language directions using the unchanged loaders.
            ctx=browser.new_context(viewport={'width':390,'height':844});page=ctx.new_page()
            page.goto(urljoin(base_url,'index.html'),wait_until='networkidle')
            page.locator('[data-ul-language-switcher] select').select_option('en')
            page.wait_for_url('**/index-en.html');page.wait_for_load_state('networkidle')
            page.locator('[data-ul-language-switcher] select').select_option('de')
            page.wait_for_url(re.compile(r'/UniverseLab/(?:index\.html)?$'))
            cases.append({'case':'DE-EN-DE','result':'PASS'})
            ctx.close()
            for name in ('index.html','index-en.html'):
                for width,height in ((390,844),(1280,720)):
                    ctx=browser.new_context(java_script_enabled=False,viewport={'width':width,'height':height})
                    page=ctx.new_page();response=page.goto(urljoin(base_url,name))
                    assert response and response.status==200
                    brand_metrics = assert_brand_layout(page, name, width)
                    page.locator('.ul-home-menu summary').click()
                    assert page.locator('.ul-home-nav a').first.is_visible()
                    assert page.locator('[data-ul-entry]').count()==3
                    cases.append({'case':'no-JavaScript-navigation','page':name,'viewport':[width,height],
                                  'result':'PASS','brand_geometry':brand_metrics});ctx.close()
        browser.close()
    return cases

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--browser',action='store_true');ap.add_argument('--offline-render',action='store_true')
    ap.add_argument('--base-url',default='http://127.0.0.1:4173/UniverseLab/');ap.add_argument('--output',type=Path,default=ROOT/'web50-landing-report')
    a=ap.parse_args();count=static_checks()
    result={'base_sha':BASE_SHA,'static_assertions':count,'physical_gate_effect':'NONE','physical_evidence_effect':'NONE'}
    if a.browser or a.offline_render: result['browser_cases']=render_checks(a.base_url,a.output,a.offline_render)
    a.output.mkdir(parents=True,exist_ok=True);(a.output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));return 0

if __name__=='__main__':
    sys.exit(main())
