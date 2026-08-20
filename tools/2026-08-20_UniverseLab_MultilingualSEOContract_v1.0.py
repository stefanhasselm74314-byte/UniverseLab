#!/usr/bin/env python3
"""Fail-closed consistency validator for UniverseLab multilingual routing and SEO.

Scope is presentation/navigation/SEO only. It does not inspect or interpret
scientific formulas, numerical results, solver states, evidence or release gates.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'2026-08-20_UniverseLab_MultilingualRouteRegistry_v1.1.json'
SITEMAP=ROOT/'sitemap.xml'
SWITCHER=ROOT/'assets/2026-08-18_UniverseLab_SiteLanguageSwitcher_v1.1.js'
ORIGIN='https://stefanhasselm74314-byte.github.io'
BASE='/UniverseLab/'
NS={'sm':'http://www.sitemaps.org/schemas/sitemap/0.9','x':'http://www.w3.org/1999/xhtml'}

class ContractError(RuntimeError): pass

def local_path(route:str)->Path:
    if not route.startswith(BASE): raise ContractError(f'route outside {BASE}: {route}')
    rel=route[len(BASE):]
    return ROOT/('index.html' if rel=='' else rel)

def abs_url(route:str)->str:
    return ORIGIN+route

def attr(html:str, rel:str, hreflang:str|None=None)->list[str]:
    tags=re.findall(r'<link\b[^>]*>',html,re.I)
    out=[]
    for tag in tags:
        if not re.search(r'\brel=["\']'+re.escape(rel)+r'["\']',tag,re.I): continue
        if hreflang is not None and not re.search(r'\bhreflang=["\']'+re.escape(hreflang)+r'["\']',tag,re.I): continue
        m=re.search(r'\bhref=["\']([^"\']+)["\']',tag,re.I)
        if m: out.append(m.group(1))
    return out

def normalize_href(href:str, page:Path)->str:
    if href.startswith('http://') or href.startswith('https://'):
        return href
    if href.startswith('/'):
        return ORIGIN+href
    # pages are at repository root for all currently governed pairs
    return ORIGIN+BASE+href.removeprefix('./')

def sitemap_records()->dict[str,dict[str,str]]:
    root=ET.parse(SITEMAP).getroot()
    records={}
    for node in root.findall('sm:url',NS):
        loc=node.findtext('sm:loc',default='',namespaces=NS)
        alts={}
        for link in node.findall('x:link',NS):
            if link.attrib.get('rel')=='alternate':
                alts[link.attrib.get('hreflang','')]=link.attrib.get('href','')
        records[loc]=alts
    return records

def main()->int:
    data=json.loads(REGISTRY.read_text(encoding='utf-8'))
    pairs=data.get('route_pairs',[])
    if data.get('unpaired_german_routes') not in ([],None):
        raise ContractError('unpaired_german_routes must be empty in v1.1')
    ids=set(); routes=set(); en_routes=set()
    sitemap=sitemap_records(); switcher=SWITCHER.read_text(encoding='utf-8')
    issues=[]
    for p in pairs:
        pid=p['id']; de=p['de']; en=p['en']; xd=p['x_default']
        if pid in ids: issues.append(f'duplicate id: {pid}')
        ids.add(pid)
        if de in routes: issues.append(f'duplicate DE route: {de}')
        if en in en_routes: issues.append(f'duplicate EN route: {en}')
        routes.add(de); en_routes.add(en)
        if xd!=de: issues.append(f'{pid}: x_default must equal canonical German route')
        de_path=local_path(de); en_path=local_path(en)
        if not de_path.is_file(): issues.append(f'{pid}: missing DE file {de_path.relative_to(ROOT)}')
        if not en_path.is_file(): issues.append(f'{pid}: missing EN file {en_path.relative_to(ROOT)}')
        for route in (de,en):
            if route not in switcher: issues.append(f'{pid}: switcher missing route {route}')
        expected={'de':abs_url(de),'en':abs_url(en),'x-default':abs_url(xd)}
        for loc_route in (de,en):
            loc=abs_url(loc_route)
            if loc not in sitemap:
                issues.append(f'{pid}: sitemap missing {loc}')
                continue
            if sitemap[loc]!=expected:
                issues.append(f'{pid}: sitemap alternates mismatch for {loc}: {sitemap[loc]} != {expected}')
        # Static page metadata are consistency-checked when present. Runtime-mirror
        # English editions must carry all metadata in their wrapper before JS runs.
        for route,path,lang in ((de,de_path,'de'),(en,en_path,'en')):
            if not path.is_file(): continue
            html=path.read_text(encoding='utf-8',errors='replace')
            html_lang=re.search(r'<html\b[^>]*\blang=["\']([^"\']+)',html,re.I)
            if lang=='en' and html_lang and not html_lang.group(1).lower().startswith('en'):
                issues.append(f'{pid}: EN page lang mismatch: {html_lang.group(1)}')
            canon=attr(html,'canonical')
            if canon:
                target=normalize_href(canon[0],path)
                own=abs_url(route)
                if target!=own: issues.append(f'{pid}: canonical mismatch on {route}: {target} != {own}')
            present={k:attr(html,'alternate',k) for k in ('de','en','x-default')}
            if any(present.values()):
                for k,vals in present.items():
                    if vals:
                        got=normalize_href(vals[0],path)
                        if got!=expected[k]: issues.append(f'{pid}: {k} page alternate mismatch on {route}: {got} != {expected[k]}')
            if p.get('edition')=='curated_runtime_mirror' and lang=='en':
                if not canon: issues.append(f'{pid}: runtime mirror EN wrapper missing canonical')
                for k,vals in present.items():
                    if not vals: issues.append(f'{pid}: runtime mirror EN wrapper missing hreflang={k}')
                if '2026-08-20_UniverseLab_CuratedEnglishLegacyAdapter_v1.0.js' not in html:
                    issues.append(f'{pid}: runtime mirror EN wrapper missing governed adapter')
    if len(pairs)!=17: issues.append(f'expected 17 curated pairs, found {len(pairs)}')
    if issues:
        print('UniverseLab multilingual SEO contract: FAIL')
        for i in issues: print(' -',i)
        return 1
    print(f'UniverseLab multilingual SEO contract: PASS ({len(pairs)} curated DE↔EN pairs)')
    return 0

if __name__=='__main__':
    try: raise SystemExit(main())
    except ContractError as exc:
        print('UniverseLab multilingual SEO contract: FAIL')
        print(' -',exc)
        raise SystemExit(1)
