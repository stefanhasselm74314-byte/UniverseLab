#!/usr/bin/env python3
"""Static/adversarial contract for the Validation Console v2.0 migration."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / 'assets/2026-09-01_UniverseLab_CosmologyEngine_v1.0.js'
ADAPTER = ROOT / 'assets/2026-09-01_UniverseLab_ValidationConsole_v2.0.js'
DE = ROOT / 'validation.html'
EN = ROOT / 'validation-en.html'
PARITY = ROOT / 'tools/2026-08-20_UniverseLab_BrowserParityAudit_v1.0.mjs'
CONTRACT = ROOT / 'registry/2026-09-01_UniverseLab_ValidationConsoleContract_v2.0.json'



def independent_wcdm_growth_d_z1(*, steps: int = 20000) -> float:
    orad, om, ode, w = 9.2e-5, 0.315, 0.684908, -0.8
    ok = 1.0 - orad - om - ode
    a_init = max(1e-3, 10.0 * orad / om)
    x0 = math.log(a_init)
    h = -x0 / steps
    x, D, V = x0, a_init, a_init
    rows: list[tuple[float, float, float]] = []

    def rhs(X: float, Y: float, W: float) -> tuple[float, float]:
        a = math.exp(X)
        r, m, k = orad / a**4, om / a**3, ok / a**2
        de = ode * a ** (-3.0 * (1.0 + w))
        e2 = r + m + k + de
        dlnh = 0.5 * (-4.0*r - 3.0*m - 2.0*k - 3.0*(1.0+w)*de) / e2
        return W, -(2.0 + dlnh) * W + 1.5 * (m / e2) * Y

    for i in range(steps + 1):
        rows.append((x, D, V))
        if i == steps:
            break
        k1 = rhs(x, D, V)
        k2 = rhs(x+h/2, D+h*k1[0]/2, V+h*k1[1]/2)
        k3 = rhs(x+h/2, D+h*k2[0]/2, V+h*k2[1]/2)
        k4 = rhs(x+h, D+h*k3[0], V+h*k3[1])
        D += h * (k1[0] + 2*k2[0] + 2*k3[0] + k4[0]) / 6
        V += h * (k1[1] + 2*k2[1] + 2*k3[1] + k4[1]) / 6
        x += h

    norm = rows[-1][1]
    target_x = math.log(0.5)
    fractional = (target_x - x0) / h
    lo = max(0, min(steps - 1, int(fractional)))
    u = (target_x - rows[lo][0]) / h
    return (rows[lo][1] * (1-u) + rows[lo+1][1] * u) / norm

def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding='utf-8'))
    assert contract['status'] == 'VALIDATION_PAGE_MIGRATED_TO_CANONICAL_ENGINE'
    assert contract['physical_gate_effect'] == 'NONE'
    assert contract['physical_evidence_effect'] == 'NONE'
    test_ids = contract['stable_test_ids']
    assert len(test_ids) == 17
    assert 'wcdm_background_reference' in test_ids
    assert 'wcdm_growth_reference' in test_ids
    assert len(test_ids) == len(set(test_ids))

    wref = contract['constant_w_reference']
    a = 1.0 / (1.0 + wref['z'])
    orad, om, ode, w = 9.2e-5, 0.315, 0.684908, wref['w']
    ok = 1.0 - orad - om - ode
    e_expected = math.sqrt(orad/a**4 + om/a**3 + ok/a**2 + ode*a**(-3*(1+w)))
    assert abs(e_expected - wref['E_z1']) < 1e-15
    d_expected = independent_wcdm_growth_d_z1()
    assert abs(d_expected - wref['growth_D_z1']) / wref['growth_D_z1'] < 2e-8

    assert ENGINE.exists()
    adapter = ADAPTER.read_text(encoding='utf-8')
    assert "const VERSION='2.0.0'" in adapter
    assert 'const WCDM_BACKGROUND_E_Z1=1.8866898001885484' in adapter
    assert 'const WCDM_GROWTH_D_Z1=0.6221646187388952' in adapter
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
