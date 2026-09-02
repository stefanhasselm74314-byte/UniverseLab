#!/usr/bin/env python3
"""Static and independent numerical checks for Observatory v1.5 migration."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'observatory.html'
ADAPTER = ROOT / 'assets/2026-09-01_UniverseLab_ObservatoryAdapter_v1.5.js'
ENGINE = ROOT / 'assets/2026-09-01_UniverseLab_CosmologyEngine_v1.0.js'
CONTRACT = ROOT / 'registry/2026-09-01_UniverseLab_ObservatoryMigrationContract_v1.5.json'
LEDGER = ROOT / 'science/cosmology/2026-09-01_UniverseLab_ObservatoryMigration_v1.5.md'
OR = 9.2e-5
C_KM_S = 299792.458


def simpson(fn, a: float, b: float, n: int = 8000) -> float:
    if n % 2:
        n += 1
    h = (b - a) / n
    total = fn(a) + fn(b)
    for i in range(1, n):
        total += (4 if i % 2 else 2) * fn(a + i * h)
    return total * h / 3


def e2(z: float, *, om: float, ode: float, w: float = -1.0) -> float:
    x = 1.0 + z
    ok = 1.0 - OR - om - ode
    return OR * x**4 + om * x**3 + ok * x**2 + ode * x ** (3 * (1 + w))


def dc(z: float, *, h0: float, om: float, ode: float, w: float = -1.0) -> float:
    return C_KM_S / h0 * simpson(lambda x: 1 / math.sqrt(e2(x, om=om, ode=ode, w=w)), 0, z)


def dm(z: float, *, h0: float, om: float, ode: float, w: float = -1.0) -> float:
    radial = dc(z, h0=h0, om=om, ode=ode, w=w)
    ok = 1.0 - OR - om - ode
    if abs(ok) < 1e-14:
        return radial
    dh = C_KM_S / h0
    chi = math.sqrt(abs(ok)) * radial / dh
    if ok > 0:
        return dh / math.sqrt(ok) * math.sinh(chi)
    return dh / math.sqrt(-ok) * math.sin(chi)


def growth_d_z1(*, om: float = .315, ode: float = .684908, w: float = -1.0, steps: int = 16000) -> float:
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
    html = HTML.read_text(encoding='utf-8')
    adapter = ADAPTER.read_text(encoding='utf-8')
    engine = ENGINE.read_text(encoding='utf-8')
    contract = json.loads(CONTRACT.read_text(encoding='utf-8'))
    ledger = LEDGER.read_text(encoding='utf-8')

    assert '<title>UniverseLab 1.5 · Observatory</title>' in html
    assert '2026-09-01_UniverseLab_CosmologyEngine_v1.0.js' in html
    assert '2026-09-01_UniverseLab_ObservatoryAdapter_v1.5.js' in html
    assert '<script>\n\'use strict\'' not in html
    assert 'id="Ol" type="range" min="0" max="1.2" step="0.000001" value="0.684908"' in html
    assert 'id="Ol" type="range" min="0" max="1.2" step="0.001" value="0.684908"' not in html
    for element_id in ('H0','Om','Ol','w','s8','age','q0','s80','curv','chart','legend','domainStatus','observatoryBadge'):
        assert f'id="{element_id}"' in html, element_id

    required_calls = (
        'C.validateBackgroundDomain', 'C.e2FromA', 'C.ageGyr', 'C.q', 'C.S8', 'C.E',
        'C.distanceModulus', 'C.baoDMOverRd', 'C.solveGrowth', 'C.growthAtZ',
        'INVALID_BACKGROUND_DOMAIN', 'D_C→D_M'
    )
    for token in required_calls:
        assert token in adapter, token
    for forbidden in ('Math.sqrt(Math.max(', 'Omz**0.55', 'P.s8*f/(1+z)', 'dc(z,P)/147.1'):
        assert forbidden not in adapter, forbidden
    assert 'UNRELEASED_GROWTH_MAP' in engine

    assert contract['version'] == '1.5.1'
    assert contract['status'] == 'ACTIVE_MERGED_QA_RECONCILED'
    assert contract['merged_pull_request'] == 198
    reference = contract['background_contract']['reference_state']
    assert reference == {
        'H0': 67.4,
        'Omega_r': .000092,
        'Omega_m': .315,
        'Omega_DE': .684908,
        'Omega_k': 0.0,
        'w': -1.0,
        'closure': 'Omega_r + Omega_m + Omega_DE + Omega_k = 1',
    }
    assert contract['background_contract']['reference_density_slider_resolution'] == .000001
    assert abs(reference['Omega_r'] + reference['Omega_m'] + reference['Omega_DE'] + reference['Omega_k'] - 1) < 1e-15
    assert contract['distance_contract']['bao'] == 'D_M/r_d'
    assert contract['growth_contract']['bridge_growth'] == 'UNRELEASED_GROWTH_MAP'
    assert contract['didactic_data_policy']['likelihood_fit'] is False
    assert contract['physical_gate_effect'] == 'NONE'
    assert contract['physical_evidence_effect'] == 'NONE'
    assert 'visueller Kurvenvergleich ≠ Datenfit ≠ Theoriebestätigung' in ledger

    z = 2.33
    dc_open = dc(z, h0=67.4, om=.2, ode=.5)
    dm_open = dm(z, h0=67.4, om=.2, ode=.5)
    dc_closed = dc(z, h0=67.4, om=.5, ode=.8)
    dm_closed = dm(z, h0=67.4, om=.5, ode=.8)
    assert dm_open > dc_open
    assert dm_closed < dc_closed
    assert abs(dm_open / dc_open - 1) > .01
    assert abs(dm_closed / dc_closed - 1) > .01

    values = [e2(5*i/20000, om=.1, ode=1.2, w=-1.5) for i in range(20001)]
    assert min(values) < -0.02

    d1 = growth_d_z1()
    assert abs(d1 - .6068047406) < 2e-7
    old_d_equal_a = .5
    assert abs(d1 - old_d_equal_a) > .1

    print('UniverseLab Observatory migration v1.5.1 static/numerical contract: PASS')


if __name__ == '__main__':
    main()
