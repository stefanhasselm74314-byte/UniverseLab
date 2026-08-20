#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys, time, urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'2026-08-20_UniverseLab_MultilingualRouteRegistry_v1.1.json'
BASE='https://stefanhasselm74314-byte.github.io'
RUNTIME={'about','journey','emergence','universe3d'}

class Meta(HTMLParser):
    def __init__(self): super().__init__(); self.lang=''; self.canonical=''; self.alts={}; self.scripts=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag=='html': self.lang=d.get('lang','')
        if tag=='link' and d.get('rel')=='canonical': self.canonical=d.get('href','')
        if tag=='link' and d.get('rel')=='alternate' and d.get('hreflang'): self.alts[d['hreflang']]=d.get('href','')
        if tag=='script' and d.get('src'): self.scripts.append(d['src'])

def absurl(path:str)->str: return BASE+path

def fetch(url:str, attempts=6):
    last=None
    for i in range(attempts):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'UniverseLab-ProductionSmoke/1.0','Cache-Control':'no-cache'})
            with urllib.request.urlopen(req,timeout=20) as r:
                return r.status, r.geturl(), r.read().decode('utf-8','replace')
        except Exception as e:
            last=e; time.sleep(min(2**i,15))
    raise RuntimeError(f'{url}: {last}')

def same(a,b):
    def n(x):
        if not x:return ''
        if x.startswith('./'): x='/UniverseLab/'+x[2:]
        if x.startswith('/'): x=BASE+x
        return x.rstrip('/')
    return n(a)==n(b)

def main()->int:
    reg=json.loads(REG.read_text(encoding='utf-8'))
    errors=[]; rows=[]
    for p in reg['route_pairs']:
        for side in ('de','en'):
            path=p[side]; url=absurl(path); status, final, body=fetch(url)
            meta=Meta(); meta.feed(body)
            ok=status==200
            if not ok: errors.append(f"{p['id']} {side}: HTTP {status}")
            # English pages must remain English; German root/index may be special.
            if side=='en' and not meta.lang.lower().startswith('en'):
                errors.append(f"{p['id']} en: html lang is {meta.lang!r}")
            # Where static canonical exists, it must be self-canonical.
            if meta.canonical and not same(meta.canonical,url):
                errors.append(f"{p['id']} {side}: canonical {meta.canonical} != {url}")
            # Static alternates, when present, must agree with registry.
            if meta.alts.get('de') and not same(meta.alts['de'],absurl(p['de'])):
                errors.append(f"{p['id']} {side}: de alternate mismatch")
            if meta.alts.get('en') and not same(meta.alts['en'],absurl(p['en'])):
                errors.append(f"{p['id']} {side}: en alternate mismatch")
            if meta.alts.get('x-default') and not same(meta.alts['x-default'],absurl(p['x_default'])):
                errors.append(f"{p['id']} {side}: x-default mismatch")
            if p['id'] in RUNTIME and side=='en':
                if 'CuratedEnglishLegacyAdapter' not in body:
                    errors.append(f"{p['id']} en: governed runtime adapter missing")
                if 'ul-curated-source' not in body:
                    errors.append(f"{p['id']} en: curated source metadata missing")
            rows.append({'id':p['id'],'side':side,'url':url,'status':status,'final':final,'lang':meta.lang,'canonical':meta.canonical})
    # Live language-switcher asset must be reachable and carry all four newly governed routes.
    asset=BASE+'/UniverseLab/assets/2026-08-18_UniverseLab_SiteLanguageSwitcher_v1.1.js'
    st,_,js=fetch(asset)
    if st!=200: errors.append(f'language switcher asset HTTP {st}')
    for slug in ('about','journey','emergence','universe3d','navigator'):
        if slug not in js: errors.append(f'language switcher live asset missing route token {slug}')
    report={'status':'PASS' if not errors else 'FAIL','base':BASE,'pairs':len(reg['route_pairs']),'checks':rows,'errors':errors,
            'scientific_firewall':'Runtime English mirrors execute the same canonical German page; this HTTP audit verifies deployment identity but does not claim independent numerical browser equivalence.'}
    out=ROOT/'production-smoke-report.json'; out.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 0 if not errors else 1

if __name__=='__main__': raise SystemExit(main())
