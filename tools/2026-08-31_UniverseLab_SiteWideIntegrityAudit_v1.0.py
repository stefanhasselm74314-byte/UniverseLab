#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, sys
from collections import Counter, defaultdict, deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT=Path('.').resolve()
REPORT_JSON=Path('2026-08-31_UniverseLab_SiteWideIntegrityAudit_Report_v1.0.json')
REPORT_MD=Path('2026-08-31_UniverseLab_SiteWideIntegrityAudit_Report_v1.0.md')
BASE_PREFIX='/UniverseLab/'
ARCHIVE_RE=re.compile(r'(legacy|archive|archiv|audit-2026-07-31|2026-07-31)',re.I)

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.refs=[]; self.title=''; self._title=False; self.lang=''; self.viewport=False
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='html': self.lang=d.get('lang','')
        if tag=='meta' and d.get('name','').lower()=='viewport': self.viewport=True
        for k in ('href','src','action','poster','data-src'):
            if d.get(k): self.refs.append(d[k])
        if tag=='title': self._title=True
    def handle_endtag(self,tag):
        if tag=='title': self._title=False
    def handle_data(self,data):
        if self._title: self.title+=data

def archived(p:Path)->bool: return bool(ARCHIVE_RE.search(p.as_posix()))
def lang_mirror(rel:str)->bool: return rel.endswith('-en.html') or rel in {'index-en.html','navigator-en.html','compare-en.html','guide-en.html'}
def local_target(src:Path,ref:str):
    ref=ref.strip()
    if not ref or ref.startswith('#') or ref.startswith('//'): return None
    u=urlsplit(ref)
    if u.scheme in {'http','https','mailto','tel','javascript','data','blob'}: return None
    p=unquote(u.path)
    if not p: return None
    if p.startswith(BASE_PREFIX): target=ROOT/p[len(BASE_PREFIX):]
    elif p.startswith('/'): return None
    else: target=(src.parent/p).resolve()
    try: target.relative_to(ROOT)
    except ValueError: return ('escape',p)
    if p.endswith('/') or target.is_dir(): target=target/'index.html'
    return target

def main():
    pages=sorted(p for p in ROOT.rglob('*.html') if '.git' not in p.parts)
    records={}; graph=defaultdict(set); inbound=Counter(); broken=[]; escaped=[]; warnings=[]; shell=[]; contradictions=[]
    for p in pages:
        rel=p.relative_to(ROOT).as_posix(); text=p.read_text(encoding='utf-8',errors='replace'); par=Parser(); par.feed(text); arc=archived(p)
        if not par.title.strip(): warnings.append({'type':'missing_title','page':rel})
        if not par.lang.strip(): warnings.append({'type':'missing_lang','page':rel})
        if not par.viewport: warnings.append({'type':'missing_viewport','page':rel})
        if 'navigator-app.html' in text: warnings.append({'type':'legacy_route_reference','page':rel,'detail':'navigator-app.html'})
        for asset,pat in [('GlobalShell JS',r'2026-08-16_UniverseLab_GlobalShell_v1\.1\.js'),('GlobalShell CSS',r'2026-08-16_UniverseLab_GlobalShell_v1\.1\.css')]:
            if re.search(pat,text) and not re.search(pat+r'\?[^\"\']+',text) and not arc: shell.append({'page':rel,'asset':asset})
        # Exact positive status only; NOT_RELEASED / NOT_ADMISSIBLE must never match.
        if re.search(r'\bK1-D\b\s*(?:=|:)?\s*RELEASED\b',text,re.I): contradictions.append({'page':rel,'claim':'exact K1-D RELEASED token'})
        if re.search(r'\bK1-E\b\s*(?:=|:)?\s*ADMISSIBLE\b',text,re.I): contradictions.append({'page':rel,'claim':'exact K1-E ADMISSIBLE token'})
        for ref in par.refs:
            t=local_target(p,ref)
            if t is None: continue
            if isinstance(t,tuple): escaped.append({'page':rel,'ref':ref}); continue
            if t.exists() and t.is_file():
                if t.suffix.lower()=='.html':
                    dst=t.relative_to(ROOT).as_posix(); graph[rel].add(dst); inbound[dst]+=1
            else: broken.append({'page':rel,'ref':ref,'target':t.relative_to(ROOT).as_posix(),'archive':arc})
        records[rel]={'archive':arc,'language_mirror':lang_mirror(rel),'title':par.title.strip(),'lang':par.lang,'viewport':par.viewport,'digest16':hashlib.sha256(re.sub(r'\s+',' ',text).encode()).hexdigest()[:16]}
    seeds=[x for x in ('index.html','navigator.html','links.html','research-status.html','solver-hub.html','hyperlab.html') if x in records]
    reachable=set(seeds); q=deque(seeds)
    while q:
        a=q.popleft()
        for b in graph.get(a,()):
            if b not in reachable: reachable.add(b); q.append(b)
    orphans=[p for p,r in records.items() if not r['archive'] and not r['language_mirror'] and p not in reachable and inbound[p]==0]
    active_broken=[x for x in broken if not x['archive']]; archive_broken=[x for x in broken if x['archive']]
    summary={'html_pages':len(pages),'active_pages':sum(not r['archive'] for r in records.values()),'archive_pages':sum(r['archive'] for r in records.values()),'broken_internal_active':len(active_broken),'broken_internal_archive':len(archive_broken),'metadata_warnings':len(warnings),'unversioned_globalshell_refs':len(shell),'status_contradiction_candidates':len(contradictions),'active_orphans':len(orphans),'reachable_from_primary_seeds':len(reachable)}
    report={'schema':'UniverseLab.SiteWideIntegrityAudit.v1','summary':summary,'primary_seeds':seeds,'active_broken':active_broken,'archive_broken':archive_broken,'metadata_warnings':warnings,'unversioned_globalshell_refs':shell,'status_contradiction_candidates':contradictions,'active_orphans':orphans,'records':records}
    REPORT_JSON.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# UniverseLab Site-Wide Integrity Audit v1.0','']+[f'- **{k}:** {v}' for k,v in summary.items()]+['']
    for title,key in [('Defekte interne Links — aktiv','active_broken'),('Defekte interne Links — Archiv','archive_broken'),('Metadaten / Legacy-Routen','metadata_warnings'),('Unversionierte GlobalShell-Referenzen','unversioned_globalshell_refs'),('Status-Widerspruchskandidaten','status_contradiction_candidates'),('Aktive Orphan-Seiten','active_orphans')]:
        lines += ['## '+title,'']
        items=report[key]
        if not items: lines += ['Keine.','']; continue
        for x in items[:250]: lines.append('- `'+(x if isinstance(x,str) else x.get('page','?'))+'` — '+(' / '.join(f'{a}={b}' for a,b in x.items() if a!='page') if isinstance(x,dict) else ''))
        lines.append('')
    lines += ['## Bewertungsgrenze','','Struktur-, Link-, Metadaten-, Navigations- und Shell-QA. Keine physikalische Validierung; keine Änderung von Solver-, Gate- oder Evidenzzuständen.','']
    REPORT_MD.write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))
    if active_broken or escaped: return 2
    return 0
if __name__=='__main__': sys.exit(main())
