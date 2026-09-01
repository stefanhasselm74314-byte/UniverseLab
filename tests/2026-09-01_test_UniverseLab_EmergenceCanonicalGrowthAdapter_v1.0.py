#!/usr/bin/env python3
"""Static and independent numerical contract for the Emergence canonical growth adapter."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'emergence.html'
ADAPTER = ROOT / 'assets/2026-09-01_UniverseLab_EmergenceAdapter_v1.0.js'
ENGINE = ROOT / 'assets/2026-09-01_UniverseLab_CosmologyEngine_v1.0.js'
CONTRACT = ROOT / 'registry/2026-09-01_UniverseLab_EmergenceCanonicalGrowthAdapterContract_v1.0.json'
LEDGER = ROOT / 'science/cosmology/2026-09-01_UniverseLab_EmergenceCanonicalGrowthAdapter_v1.0.md'
OR = 9.2e-5


def independent_growth_d_z1(steps: int = 20000) -> float:
    om, ode, w = .315, .684908, -1.0
    ok = 1.0 - OR - om - ode
    a0 = max(1e-3, 10 * OR / om)
    x = math.log(a0)
    h = -x / steps
    D = V = a0
    rows: list[tuple[float, float]] = []

    def rhs(X: float, Y: float, W: float) -> tuple[float, float]:
        a = math.exp(X)
        r = OR / a**4
        m = om / a**3
        k = ok / a**2
        de = ode * a ** (-3 * (1 + w))
        total = r + m + k + de
        dlnh = .5 * (-4*r - 3*m - 2*k - 3*(1+w)*de) / total
        return W, -(2 + dlnh) * W + 1.5 * (m / total) * Y

    for i in range(steps + 1):
        rows.append((x, D))
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
    target = math.log(.5)
    hi = next(i for i, row in enumerate(rows) if row[0] >= target)
    lo = hi - 1
    xa, da = rows[lo]
    xb, db = rows[hi]
    u = (target - xa) / (xb - xa)
    return (da * (1-u) + db * u) / norm


def main() -> None:
    for path in (HTML, ADAPTER, ENGINE, CONTRACT, LEDGER):
        assert path.is_file(), path

    html = HTML.read_text(encoding='utf-8')
    adapter = ADAPTER.read_text(encoding='utf-8')
    engine = ENGINE.read_text(encoding='utf-8')
    contract = json.loads(CONTRACT.read_text(encoding='utf-8'))
    ledger = LEDGER.read_text(encoding='utf-8')

    assert '<title>UniverseLab 1.0 · Emergenz</title>' in html
    assert '2026-09-01_UniverseLab_CosmologyEngine_v1.0.js' in html
    assert '2026-09-01_UniverseLab_EmergenceAdapter_v1.0.js' in html
    assert html.index('CosmologyEngine_v1.0.js') < html.index('EmergenceAdapter_v1.0.js')
    for element_id in contract['preserved_runtime_ids']:
        assert f'id="{element_id}"' in html, element_id
    assert html.count('<canvas') == 2
    assert '<script>\'use strict\'' not in html

    for token in (
        'C.e2FromA', 'C.solveGrowth', 'C.growthAtZ', 'C.q', 'C.E', 'C.ageGyr',
        'INVALID_BACKGROUND_DOMAIN', 'cellularDynamicsIndependent:true',
        'gridResamplingVisualOnly:true', 'omegaMatter**.55'
    ):
        assert token in adapter, token
    for forbidden in (
        'Math.sqrt(Math.max(0', 'Math.sqrt(Math.max(1e-12',
        'function buildGrowth', 'function dlnH', 'function terms('
    ):
        assert forbidden not in adapter, forbidden
    assert 'UNRELEASED_GROWTH_MAP' in engine

    assert contract['status'] == 'IMPLEMENTED_REVIEW_PENDING'
    assert contract['architecture']['dynamical_coupling_between_automaton_and_cosmology'] is False
    assert contract['architecture']['grid_resampling_is_structure_formation_model'] is False
    assert contract['architecture']['cellular_automaton_continues_when_cosmology_is_invalid'] is True
    assert contract['background_contract']['invalid_policy'] == 'FAIL_CLOSED_NO_POSITIVE_FLOOR'
    assert contract['growth_contract']['approximation_role'] == 'DISPLAY_ONLY_DIAGNOSTIC_NOT_DYNAMICS'
    assert contract['growth_contract']['bridge_growth'] == 'UNRELEASED_GROWTH_MAP'
    assert contract['K1-D'] == 'NOT_RELEASED'
    assert contract['K1-E'] == 'NOT_ADMISSIBLE'
    assert contract['physical_gate_effect'] == 'NONE'
    assert contract['physical_evidence_effect'] == 'NONE'
    assert 'zelluläres Muster ≠ kosmische Dichteperturbation ≠ 6D-Strukturbildungsherleitung' in ledger

    a = .2
    invalid_e2 = .05/a**3 - 3.05/a**2 + 4
    assert invalid_e2 < -60

    d_z1 = independent_growth_d_z1()
    assert abs(d_z1 - .6068047406056298) < 2e-7
    assert abs(d_z1 - .5) > .1

    om, ode, orad = .315, .684908, OR
    ok = 1 - om - ode - orad
    total = orad/a**4 + om/a**3 + ok/a**2 + ode
    closure = (orad/a**4 + om/a**3 + ok/a**2 + ode) / total
    assert abs(closure - 1) < 1e-15

    print('UniverseLab Emergence canonical growth adapter static/numerical contract: PASS')


if __name__ == '__main__':
    main()
