#!/usr/bin/env python3
"""Static contract for retiring duplicate UniverseLab comparison engines."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERIC = ROOT / 'compare.html'
DIRECT = ROOT / 'compare-direct.html'
LEGACY_APP = ROOT / 'compare-app.js'
SAFE = ROOT / 'compare-safe.html'
CONTRACT = ROOT / 'registry/2026-09-01_UniverseLab_CompareRouteConsolidationContract_v1.0.json'


def main() -> None:
    generic = GENERIC.read_text(encoding='utf-8')
    direct = DIRECT.read_text(encoding='utf-8')
    legacy = LEGACY_APP.read_text(encoding='utf-8')
    safe = SAFE.read_text(encoding='utf-8')
    contract = json.loads(CONTRACT.read_text(encoding='utf-8'))

    for page in (generic, direct):
        assert './compare-safe.html' in page
        assert 'location.replace(target.href)' in page
        assert 'target.search=location.search' in page
        assert 'target.hash=location.hash' in page
        assert 'compare-direct.html?v=23' not in page
        for forbidden in ('Math.sqrt(', 'function e0(', 'function ew(', 'function eb(', 'function dc(', 'function age(', 'function sweep('):
            assert forbidden not in page, forbidden

    assert "status:'RETIRED_DUPLICATE_ENGINE'" in legacy
    assert "canonicalUrl:CANONICAL_URL" in legacy
    assert 'UniverseLabCompareLegacy' in legacy
    for forbidden in (
        'Math.sqrt(', 'Math.sinh(', 'Math.sin(', 'function eL(', 'function eW(', 'function eB(',
        'function simpson(', 'function dc(', 'function fs8(', 'Math.max(1e-12', 'Math.max(.02'
    ):
        assert forbidden not in legacy, forbidden

    assert '2026-09-01_UniverseLab_CosmologyEngine_v1.0.js' in safe
    assert '2026-09-01_UniverseLab_CompareSafeAdapter_v2.0.js' in safe
    assert 'UNRELEASED_GROWTH_MAP' in safe
    assert 'UNRELEASED_LENSING_MAP' in safe

    assert contract['status'] == 'IMPLEMENTED_REVIEW_PENDING'
    assert contract['canonical_executable_route'] == 'compare-safe.html'
    assert contract['legacy_routes']['compare-direct.html'] == 'REDIRECT_TO_COMPARE_SAFE'
    assert contract['legacy_routes']['compare-app.js'] == 'RETIRED_DUPLICATE_ENGINE_METADATA_ONLY'
    assert contract['compatibility_api']['numerical_functions'] == 0
    assert contract['physical_gate_effect'] == 'NONE'
    assert contract['physical_evidence_effect'] == 'NONE'

    print('UniverseLab comparison route consolidation v1.0 static contract: PASS')


if __name__ == '__main__':
    main()
