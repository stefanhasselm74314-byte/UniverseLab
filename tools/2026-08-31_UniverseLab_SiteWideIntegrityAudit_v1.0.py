#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, re, sys
from collections import Counter, defaultdict, deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path('.').resolve()
REPORT_JSON = Path('2026-08-31_UniverseLab_SiteWideIntegrityAudit_Report_v1.0.json')
REPORT_MD = Path('2026-08-31_UniverseLab_SiteWideIntegrityAudit_Report_v1.0.md')
BASE_PREFIX = '/UniverseLab/'
ARCHIVE_RE = re.compile(r'(legacy|archive|archiv|audit-2026-07-31|2026-07-31)', re.I)
VERSION_RE = re.compile(r'(?P<stem>.*?)(?:_v\d+(?:\.\d+)*)?(?:-en)?\.html$', re.I)

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs=[]; self.title=''; self._title=False; self.lang=''; self.viewport=False; self.canonicals=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag=='html': self.lang=d.get('lang','')
        if tag=='meta' and d.get('name','').lower()=='viewport': self.viewport=True
        if tag=='link' and 'canonical' in d.get('rel','').lower().split():
            if d.get('href'): self.canonicals.append(d['href'])
        for key in ('href','src','action','poster','data-src'):
            if d.get(key): self.refs.append((tag,key,d[key]))
        if tag=='title': self._title=True
    def handle_endtag(self, tag):
        if tag=='title': self._title=False
    def handle_data(self, data):
        if self._title: self.title += data

def is_archive(path: Path) -> bool:
    return bool(ARCHIVE_RE.search(path.as_posix()))

def normalize_local(src: Path, ref: str):
    ref=ref.strip()
    if not ref or ref.startswith('#') or ref.startswith('//'): return None
    u=urlsplit(ref)
    if u.scheme in {'http','https','mailto','tel','javascript','data','blob'}: return None
    p=unquote(u.path)
    if not p: return None
    if p.startswith(BASE_PREFIX):
        p=p[len(BASE_PREFIX):]
        target=ROOT/p
    elif p.startswith('/'):
        # Other absolute site paths are not UniverseLab-local.
        return None
    else:
        target=(src.parent/p).resolve()
    try: target.relative_to(ROOT)
    except ValueError: return ('ESCAPES_ROOT', p)
    if p.endswith('/') or target.is_dir(): target=target/'index.html'
    return target

def family_key(p: Path):
    name=p.name
    m=VERSION_RE.match(name)
    return m.group('stem').lower() if m else name.lower()

def main():
    htmls=sorted(p for p in ROOT.rglob('*.html') if '.git' not in p.parts)
    files=set(p.resolve() for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts)
    records={}; broken=[]; escaped=[]; warnings=[]; graph=defaultdict(set); inbound=Counter(); families=defaultdict(list)
    stale_tokens=[]; contradictory=[]

    for p in htmls:
        rel=p.relative_to(ROOT).as_posix(); text=p.read_text(encoding='utf-8',errors='replace'); parser=P()
        try: parser.feed(text)
        except Exception as e: warnings.append({'type':'parse_error','page':rel,'detail':str(e)})
        archive=is_archive(p)
        shell_js='2026-08-16_UniverseLab_GlobalShell_v1.1.js' in text
        shell_css='2026-08-16_UniverseLab_GlobalShell_v1.1.css' in text
        shell_js_versioned=bool(re.search(r'2026-08-16_UniverseLab_GlobalShell_v1\.1\.js\?[^\"\']+',text))
        shell_css_versioned=bool(re.search(r'2026-08-16_UniverseLab_GlobalShell_v1\.1\.css\?[^\"\']+',text))
        if shell_js and not shell_js_versioned and not archive: stale_tokens.append({'page':rel,'asset':'GlobalShell JS','severity':'warning'})
        if shell_css and not shell_css_versioned and not archive: stale_tokens.append({'page':rel,'asset':'GlobalShell CSS','severity':'warning'})
        if not parser.title.strip(): warnings.append({'type':'missing_title','page':rel})
        if not parser.lang.strip(): warnings.append({'type':'missing_lang','page':rel})
        if not parser.viewport: warnings.append({'type':'missing_viewport','page':rel})
        if 'navigator-app.html' in text: warnings.append({'type':'legacy_route_reference','page':rel,'detail':'navigator-app.html'})
        if re.search(r'\bK1-D\b.{0,30}(?<!NOT_)RELEASED\b',text,re.I|re.S): contradictory.append({'page':rel,'claim':'K1-D RELEASED token present'})
        if re.search(r'\bK1-E\b.{0,30}(?<!NOT_)ADMISSIBLE\b',text,re.I|re.S): contradictory.append({'page':rel,'claim':'K1-E ADMISSIBLE token present'})
        local_count=0
        for tag,key,ref in parser.refs:
            n=normalize_local(p,ref)
            if n is None: continue
            if isinstance(n,tuple): escaped.append({'page':rel,'ref':ref}); continue
            local_count+=1
            if n.exists() and n.is_file():
                if n.suffix.lower()=='.html':
                    dst=n.relative_to(ROOT).as_posix(); graph[rel].add(dst); inbound[dst]+=1
            else:
                item={'page':rel,'ref':ref,'target':n.relative_to(ROOT).as_posix() if str(n).startswith(str(ROOT)) else str(n),'archive':archive}
                broken.append(item)
        digest=hashlib.sha256(re.sub(r'\s+',' ',text).strip().encode()).hexdigest()[:16]
        records[rel]={'archive':archive,'title':parser.title.strip(),'lang':parser.lang,'viewport':parser.viewport,'canonical':parser.canonicals,'local_refs':local_count,'shell_js':shell_js,'shell_css':shell_css,'shell_js_versioned':shell_js_versioned,'shell_css_versioned':shell_css_versioned,'digest16':digest}
        families[family_key(p)].append(rel)

    seeds=[x for x in ('index.html','navigator.html','links.html','research-status.html','solver-hub.html','hyperlab.html') if x in records]
    reachable=set(seeds); q=deque(seeds)
    while q:
        a=q.popleft()
        for b in graph.get(a,()):
            if b not in reachable: reachable.add(b); q.append(b)
    active_orphans=[p for p,r in records.items() if not r['archive'] and p not in reachable and inbound[p]==0]
    version_families={k:v for k,v in families.items() if len(v)>1}
    active_broken=[x for x in broken if not x['archive']]
    archive_broken=[x for x in broken if x['archive']]

    summary={
      'html_pages':len(htmls),'active_pages':sum(not r['archive'] for r in records.values()),'archive_pages':sum(r['archive'] for r in records.values()),
      'broken_internal_active':len(active_broken),'broken_internal_archive':len(archive_broken),'metadata_warnings':len(warnings),
      'unversioned_globalshell_refs':len(stale_tokens),'status_contradiction_candidates':len(contradictory),'active_orphans':len(active_orphans),
      'version_families':len(version_families),'reachable_from_primary_seeds':len(reachable)
    }
    report={'schema':'UniverseLab.SiteWideIntegrityAudit.v1','summary':summary,'primary_seeds':seeds,'active_broken':active_broken,'archive_broken':archive_broken,'metadata_warnings':warnings,'unversioned_globalshell_refs':stale_tokens,'status_contradiction_candidates':contradictory,'active_orphans':active_orphans,'version_families':version_families,'records':records}
    REPORT_JSON.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')
    lines=['# UniverseLab Site-Wide Integrity Audit v1.0','',f'**HTML-Seiten gesamt:** {summary["html_pages"]}',f'**Aktive/unklassifizierte Seiten:** {summary["active_pages"]}',f'**Archiv/Legacy:** {summary["archive_pages"]}',f'**Defekte interne Links (aktiv):** {summary["broken_internal_active"]}',f'**Defekte interne Links (Archiv):** {summary["broken_internal_archive"]}',f'**Metadatenwarnungen:** {summary["metadata_warnings"]}',f'**Unversionierte GlobalShell-Referenzen:** {summary["unversioned_globalshell_refs"]}',f'**Status-Widerspruchskandidaten:** {summary["status_contradiction_candidates"]}',f'**Aktive Orphans ohne eingehenden Link:** {summary["active_orphans"]}','']
    def sec(title,items,fmt):
        lines.extend([f'## {title}',''])
        if not items: lines.append('Keine.'); lines.append(''); return
        for x in items[:250]: lines.append('- '+fmt(x))
        if len(items)>250: lines.append(f'- … {len(items)-250} weitere im JSON-Report')
        lines.append('')
    sec('Defekte interne Links — aktive Seiten',active_broken,lambda x:f'`{x["page"]}` → `{x["ref"]}` (Ziel `{x["target"]}` fehlt)')
    sec('Unversionierte GlobalShell-Referenzen',stale_tokens,lambda x:f'`{x["page"]}` → {x["asset"]}')
    sec('Metadaten / Legacy-Routen',warnings,lambda x:f'`{x["page"]}` — {x["type"]}'+(f': {x.get("detail")}' if x.get('detail') else ''))
    sec('Status-Widerspruchskandidaten — manuell prüfen',contradictory,lambda x:f'`{x["page"]}` — {x["claim"]}')
    sec('Aktive Orphan-Seiten',active_orphans,lambda x:f'`{x}`')
    lines += ['## Bewertungsgrenze','', 'Dieser Audit prüft Struktur, interne Referenzen, Metadaten, Navigations-/Shell-Hygiene und Token-Konsistenz. Er ist **keine physikalische Validierung** und ändert keine Solver-, Gate- oder Evidenzzustände.','']
    REPORT_MD.write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))
    # Fail only on broken internal references on non-archive pages or path escapes.
    if active_broken or escaped:
        print(f'FAIL: active broken={len(active_broken)}, escapes={len(escaped)}',file=sys.stderr); return 2
    return 0
if __name__=='__main__': sys.exit(main())
