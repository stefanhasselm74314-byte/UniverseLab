from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINKS = ROOT / 'links.html'
ACTIVE = ROOT / 'ACTIVE_LINKS.md'
BOOTSTRAP = ROOT / 'assets/2026-08-19_UniverseLab_SitePrintExportBootstrap_v1.0.js'
PRESENTATION_SW = ROOT / '2026-08-19_UniverseLab_SitePrintExportServiceWorker_v1.0.js'
SHELL = ROOT / 'assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js'

DEAD_GSRA_REPO = 'stefanhasselm74314-byte/gsra-orion-pulse'
DEAD_TELEMETRY_ID = '1EUwZhP8MEMfLz1Ocb_r7UxIA5doTiSCM59PCqiLHcco'
DEAD_RELEASE_ID = '1CCKgG5dmBkjHNiiVLm7RoKM8nfzmlhDpTTqiVpJsytM'


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag.lower() != 'a':
            return
        d = dict(attrs)
        if d.get('href'):
            self.hrefs.append(d['href'])


def hrefs() -> list[str]:
    p = AnchorParser()
    p.feed(LINKS.read_text(encoding='utf-8'))
    return p.hrefs


def local_repo_path(href: str) -> Path | None:
    u = urlsplit(href)
    if u.scheme or u.netloc or not u.path.startswith('/UniverseLab/'):
        return None
    rel = u.path[len('/UniverseLab/'):]
    if rel == '':
        rel = 'index.html'
    return ROOT / rel


def test_active_local_links_resolve_in_repository():
    missing = []
    for h in hrefs():
        p = local_repo_path(h)
        if p is not None and not p.exists():
            missing.append((h, str(p.relative_to(ROOT))))
    assert not missing, f'missing same-origin targets: {missing}'


def test_archive_links_are_explicit_and_present():
    hs = set(hrefs())
    assert '/UniverseLab/universelab-audit-2026-07-31.html' in hs
    assert '/UniverseLab/legacy.html' in hs
    assert (ROOT / 'universelab-audit-2026-07-31.html').exists()
    assert (ROOT / 'legacy.html').exists()


def test_unverifiable_gsra_targets_are_not_clickable():
    html = LINKS.read_text(encoding='utf-8')
    hs = '\n'.join(hrefs())
    assert DEAD_GSRA_REPO not in hs
    assert DEAD_TELEMETRY_ID not in hs
    assert DEAD_RELEASE_ID not in hs
    # Preserve the original visible card text so the scientific claim census is unaffected;
    # only the link semantics are disabled.
    assert html.count('aria-disabled="true"') == 3
    assert '<h3>Source Brief</h3><span class="link" aria-disabled="true"><span>Öffnen</span><span>↗</span></span>' in html
    assert '<h3>Telemetry Contract</h3><span class="link" aria-disabled="true"><span>Öffnen</span><span>↗</span></span>' in html
    assert '<h3>Release Notes</h3><span class="link" aria-disabled="true"><span>Öffnen</span><span>↗</span></span>' in html


def test_active_registry_marks_old_gsra_targets_inactive():
    text = ACTIVE.read_text(encoding='utf-8')
    assert '**Stand:** 09.09.2026' in text
    assert 'derzeit nicht aktiv verlinkt' in text
    assert 'nicht als aktive Links verwenden' in text
    # IDs may remain as historical provenance, but not as active https:// links.
    assert f'https://docs.google.com/document/d/{DEAD_TELEMETRY_ID}' not in text
    assert f'https://docs.google.com/document/d/{DEAD_RELEASE_ID}' not in text
    assert f'https://github.com/{DEAD_GSRA_REPO}' not in text


def test_navigation_service_worker_is_retired():
    bootstrap = BOOTSTRAP.read_text(encoding='utf-8')
    sw = PRESENTATION_SW.read_text(encoding='utf-8')
    shell = SHELL.read_text(encoding='utf-8')
    assert 'navigator.serviceWorker.register' not in bootstrap
    assert 'navigator.serviceWorker.getRegistrations' in bootstrap
    assert 'reg.unregister()' in bootstrap
    assert "addEventListener('fetch'" not in sw
    assert 'respondWith' not in sw
    assert 'self.registration.unregister()' in sw
    assert "const VERSION='1.1.6'" in shell
    assert 'SitePrintExportBootstrap_v1.0.js?v=1.0.9' in shell


def test_scientific_firewall_unchanged():
    text = LINKS.read_text(encoding='utf-8')
    assert 'K1-D = NOT_RELEASED' in text
    assert 'K1-E = NOT_ADMISSIBLE' in text


if __name__ == '__main__':
    test_active_local_links_resolve_in_repository()
    test_archive_links_are_explicit_and_present()
    test_unverifiable_gsra_targets_are_not_clickable()
    test_active_registry_marks_old_gsra_targets_inactive()
    test_navigation_service_worker_is_retired()
    test_scientific_firewall_unchanged()
    print('UniverseLab link/navigation recovery controls: PASS')
