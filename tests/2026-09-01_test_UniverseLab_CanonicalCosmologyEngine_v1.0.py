#!/usr/bin/env python3
"""Independent regression checks for the canonical UniverseLab cosmology engine."""
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / 'assets/2026-09-01_UniverseLab_CosmologyEngine_v1.0.js'
VALIDATOR = ROOT / 'tools/2026-09-01_validate_UniverseLab_CanonicalCosmologyEngine_v1.0.mjs'
REPORT = ROOT / 'canonical-cosmology-engine-report.json'
OR = 9.2e-5


def simpson(fn, a: float, b: float, n: int = 4000) -> float:
    if n % 2:
        n += 1
    h = (b - a) / n
    total = fn(a) + fn(b)
    for i in range(1, n):
        total += (4 if i % 2 else 2) * fn(a + i * h)
    return total * h / 3


def e2(z: float, om: float, ode: float, w: float = -1.0, orad: float = OR) -> float:
    zp1 = 1.0 + z
    ok = 1.0 - orad - om - ode
    return orad * zp1**4 + om * zp1**3 + ok * zp1**2 + ode * zp1 ** (3.0 * (1.0 + w))


def bridge_scale(rchi: float) -> float:
    if not rchi > 0:
        raise ValueError('Rchi must be positive')
    return rchi / (rchi + 2.5)


def growth_reference(
    om: float = .315,
    ode: float = .684908,
    orad: float = OR,
    z_values: tuple[float, ...] = (.5, 1.0, 2.0, 3.0),
    steps: int = 16000,
) -> tuple[dict[float, float], tuple[float, float]]:
    aeq = orad / om
    a0 = max(1e-3, 10 * aeq)
    x0 = math.log(a0)
    nominal_h = -x0 / steps
    x = x0
    d = a0
    v = a0

    def rhs(X: float, D: float, V: float) -> tuple[float, float]:
        a = math.exp(X)
        r = orad / a**4
        m = om / a**3
        k = (1 - orad - om - ode) / a**2
        de = ode
        total = r + m + k + de
        dlnh = -0.5 * (4 * r + 3 * m + 2 * k) / total
        return V, -(2 + dlnh) * V + 1.5 * (m / total) * D

    rows: list[tuple[float, float, float]] = []
    for i in range(steps + 1):
        if i == steps:
            x = 0.0
        rows.append((x, math.exp(x) if i < steps else 1.0, d))
        if i == steps:
            break
        next_x = 0.0 if i == steps - 1 else x + nominal_h
        h = next_x - x
        k1 = rhs(x, d, v)
        k2 = rhs(x + h / 2, d + h * k1[0] / 2, v + h * k1[1] / 2)
        k3 = rhs(x + h / 2, d + h * k2[0] / 2, v + h * k2[1] / 2)
        k4 = rhs(next_x, d + h * k3[0], v + h * k3[1])
        d += h * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]) / 6
        v += h * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]) / 6
        x = next_x

    endpoint = (rows[-1][0], rows[-1][1])
    norm = rows[-1][2]
    result: dict[float, float] = {}
    for z in z_values:
        target = math.log(1 / (1 + z))
        hi = next(i for i, row in enumerate(rows) if row[0] >= target)
        lo = max(0, hi - 1)
        xa, _, da = rows[lo]
        xb, _, db = rows[hi]
        u = (target - xa) / (xb - xa)
        result[z] = (da * (1 - u) + db * u) / norm
    return result, endpoint


def main() -> None:
    text = ENGINE.read_text(encoding='utf-8')
    required = [
        "const VERSION='1.0.0'",
        "const REVISION='1.0.2'",
        'INVALID_BACKGROUND_DOMAIN',
        'INVALID_BRIDGE_DOMAIN',
        'UNRELEASED_GROWTH_MAP',
        'transverseComovingDistance',
        'solveGrowth',
        'etheringtonRatio',
        'function bridgeScale(p){return p.ac??p.Rchi/(p.Rchi+2.5);}',
        'const nextX=i===steps-1?0:x+nominalH',
        'rows.push({x,a:i===steps?1:Math.exp(x),D,V})',
    ]
    for token in required:
        assert token in text, token
    assert 'Math.sqrt(Math.max(1e-12' not in text
    assert 'Math.sqrt(Math.max(.02' not in text
    assert 'Math.max(0.02,p.Rchi)' not in text

    subprocess.run(['node', str(VALIDATOR)], cwd=ROOT, check=True)
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    assert report['status'] == 'PASS'
    assert report['engine_version'] == '1.0.0'
    assert report['engine_revision'] == '1.0.2'
    assert len(report['checks']) >= 15
    assert all(row['status'] == 'PASS' for row in report['checks'])

    # Independent flat LCDM distance reference.
    h0, om, ode = 67.4, .315, .684908
    dc = 299792.458 / h0 * simpson(lambda z: 1 / math.sqrt(e2(z, om, ode)), 0, 1, 6000)
    flat_row = next(row for row in report['checks'] if row['name'] == 'flat_distance_identity')
    node_dc = flat_row['detail']['dc']
    assert abs(node_dc - dc) / dc < 2e-10, (node_dc, dc)

    # Independent small-Rchi asymptotic and removal of the historical floor.
    small_row = next(row for row in report['checks'] if row['name'] == 'bridge_scale_small_rchi_asymptotic_no_hidden_floor')
    node_scales = {float(row['Rchi']): float(row['scale']) for row in small_row['detail']['samples']}
    for rchi in (1.0, .1, .02, .01, 1e-3, 1e-6):
        assert abs(node_scales[rchi] - bridge_scale(rchi)) < 1e-15
    historical_floor = 1 / (1 + 2.5 / .02)
    assert abs(node_scales[.01] - historical_floor) > 1e-3
    assert abs(node_scales[1e-6] / 1e-6 - .4) < 2e-7

    # Independent invalid-domain witness.
    vals = [e2(5 * i / 20000, .1, 1.2, -1.5) for i in range(20001)]
    assert min(vals) < -0.02

    # Independent default ODE reconstruction.
    expected, endpoint = growth_reference()
    assert endpoint == (0.0, 1.0)
    growth_row = next(row for row in report['checks'] if row['name'] == 'lcdm_growth_reference')
    got = {float(row['z']): float(row['D']) for row in growth_row['detail']['rows']}
    assert growth_row['detail']['endpoint']['x'] == 0
    assert growth_row['detail']['endpoint']['a'] == 1
    for z, value in expected.items():
        assert abs(got[z] - value) < 2e-7, (z, got[z], value)

    # Independent non-default initial-epoch/end-point reconstruction.
    legacy_expected, legacy_endpoint = growth_reference(.3, .699908, OR, (1.0,), 20000)
    assert legacy_endpoint == (0.0, 1.0)
    legacy_row = next(row for row in report['checks'] if row['name'] == 'growth_endpoint_nondefault_initial_epoch')
    assert legacy_row['detail']['endpoint']['x'] == 0
    assert legacy_row['detail']['endpoint']['a'] == 1
    node_legacy_d = float(legacy_row['detail']['z1']['D'])
    assert abs(node_legacy_d - legacy_expected[1.0]) < 2e-7, (node_legacy_d, legacy_expected[1.0])

    print('UniverseLab canonical cosmology engine independent tests: PASS')


if __name__ == '__main__':
    main()
