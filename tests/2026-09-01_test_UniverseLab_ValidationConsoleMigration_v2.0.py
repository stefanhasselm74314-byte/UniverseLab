#!/usr/bin/env python3
"""Static/adversarial contract for the Validation Console v2.0 migration."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / 'assets/2026-09-01_UniverseLab_CosmologyEngine_v1.0.js'
ADAPTER = ROOT / 'assets/2026-09-01_UniverseLab_ValidationConsole_v2.0.js'
DE = ROOT / 'validation.html'
EN = ROOT / 'validation-en.html'
PARITY = ROOT / 'tools/2026-08-20_UniverseLab_BrowserParityAudit_v1.0.mjs'
CONTRACT = ROOT / 'registry/2026-09-01_UniverseLab_ValidationConsoleContract_v2.0.json'


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding='utf-8'))
    assert contract['status'] == 'VALIDATION_PAGE_MIGRATED_TO_CANONICAL_ENGINE'
    assert contract['physical_gate_effect'] == 'NONE'
    assert contract['physical_evidence_effect'] == 'NONE'
    test_ids = contract['stable_test_ids']
    assert len(test_ids) == 15
    assert len(test_ids) == len(set(test_ids))

    assert ENGINE.exists()
    adapter = ADAPTER.read_text(encoding='utf-8')
    assert "const VERSION='2.0.0'" in adapter
    assert 'window' in adapter and 'UniverseLabValidation' in adapter
    assert 'UniverseLabCosmology' in adapter
    for test_id in test_ids:
        assert test_id in adapter, test_id
    for required in [
        'INVALID_BACKGROUND_DOMAIN',
        'INVALID_BRIDGE_DOMAIN',
        'UNRELEASED_GROWTH_MAP',
        'transverseComovingDistance',
        'etheringtonRatio',
        'solveGrowth',
        'growthAtZ',
    ]:
        assert required in adapter, required
    assert 'Math.sqrt(Math.max(1e-12' not in adapter
    assert 'Math.sqrt(Math.max(.02' not in adapter

    html_texts = []
    for page, lang in [(DE, 'de'), (EN, 'en')]:
        html = page.read_text(encoding='utf-8')
        html_texts.append(html)
        assert f'<html lang="{lang}">' in html
        assert 'UniverseLab 2.0 · Validation Console' in html
        assert './assets/2026-09-01_UniverseLab_CosmologyEngine_v1.0.js' in html
        assert './assets/2026-09-01_UniverseLab_ValidationConsole_v2.0.js' in html
        assert 'id="rows"' in html
        assert 'id="passed"' in html
        assert 'id="failed"' in html
        assert 'id="maxerr"' in html
        assert 'id="release"' in html
        assert 'id="engine"' in html
        # No page-local duplicate numerical engine remains.
        for forbidden in [
            'function E(',
            'function simpson(',
            'function ageGyr(',
            'function dc(',
            "const tests=[]",
        ]:
            assert forbidden not in html, (page.name, forbidden)
        assert 'K1-D' not in html or 'not' in html.lower() or 'nicht' in html.lower()

    parity = PARITY.read_text(encoding='utf-8')
    assert "schema_version:'1.2'" in parity
    assert "window.UniverseLabValidation?.status==='complete'" in parity
    assert 'validation_test_id_parity' in parity
    assert 'validation_engine_identity' in parity
    assert "length===6" not in parity
    assert 'data-test-id' in parity
    assert 'validation_numeric_parity' in parity

    # Both pages expose exactly the same structural IDs and script contract.
    structural = ['passed', 'failed', 'maxerr', 'release', 'run', 'rows', 'engine']
    for element_id in structural:
        assert all(f'id="{element_id}"' in html for html in html_texts)

    print('UniverseLab Validation Console migration v2.0 static contract: PASS')


if __name__ == '__main__':
    main()
