#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'registry/2026-09-08_UniverseLab_ULSH05_WP1C4B1C_PassiveShapeConstraint_v0.1.json'
DOC = ROOT / 'science/solver-hub/2026-09-08_UniverseLab_ULSH05_WP1C4B1C_PassiveShapeConstraint_v0.1.md'


def metric_and_derivative(r: float, c: float):
    signs = [1.0, -1.0, 1.0, 1.0, 1.0, 1.0]
    g = [[0.0] * 6 for _ in range(6)]
    dg = [[[0.0] * 6 for _ in range(6)] for _ in range(6)]
    g[0][0] = 1.0
    for i in range(1, 6):
        g[i][i] = signs[i] * math.exp(2.0 * c * r)
        dg[0][i][i] = 2.0 * c * g[i][i]
    inv = [[0.0] * 6 for _ in range(6)]
    for i in range(6):
        inv[i][i] = 1.0 / g[i][i]
    return g, inv, dg


def christoffel(r: float, c: float):
    _, inv, dg = metric_and_derivative(r, c)
    gamma = [[[0.0] * 6 for _ in range(6)] for _ in range(6)]
    for k in range(6):
        for i in range(6):
            for j in range(6):
                total = 0.0
                for l in range(6):
                    total += inv[k][l] * (dg[i][l][j] + dg[j][l][i] - dg[l][i][j])
                gamma[k][i][j] = 0.5 * total
    return gamma


def direct_warped_einstein_rr(c: float, h: float = 1e-6) -> float:
    g, inv, _ = metric_and_derivative(0.0, c)
    gam = christoffel(0.0, c)
    gp = christoffel(h, c)
    gm = christoffel(-h, c)

    def dgamma(coord: int, k: int, i: int, j: int) -> float:
        if coord != 0:
            return 0.0
        return (gp[k][i][j] - gm[k][i][j]) / (2.0 * h)

    ric = [[0.0] * 6 for _ in range(6)]
    for i in range(6):
        for j in range(6):
            value = 0.0
            for k in range(6):
                value += dgamma(k, k, i, j) - dgamma(j, k, i, k)
                for l in range(6):
                    value += gam[k][i][j] * gam[l][k][l] - gam[l][i][k] * gam[k][j][l]
            ric[i][j] = value
    scalar = sum(inv[i][j] * ric[i][j] for i in range(6) for j in range(6))
    return ric[0][0] - 0.5 * g[0][0] * scalar


def passive_from_israel(aN: float, aS: float, lN: float, lS: float):
    A_sum = aN + aS
    L_sum = lN + lS
    Y = L_sum - A_sum
    lam = 0.5 * (7.0 * A_sum + L_sum)
    Abar = 0.5 * (aN - aS)
    Lbar = 0.5 * (lN - lS)
    surface = 4.0 * (-lam - 0.5 * Y) * Abar + (-lam + 0.5 * Y) * Lbar
    geom_jump = (6.0 * aS * aS + 4.0 * aS * lS) - (6.0 * aN * aN + 4.0 * aN * lN)
    return lam, Y, surface, geom_jump


def main() -> None:
    d = json.loads(CONTRACT.read_text())
    text = DOC.read_text()

    assert d['model_id'] == 'HZT-M0-S6-C-PHYS-M1'
    assert d['work_package'] == 'ULSH-05/WP1C4B1C'
    assert d['passive_shape_constraint']['master'] == 'S^ab*<K_ab>_c=[T_NN]_c=T_NN,S-T_NN,N'
    assert d['passive_shape_constraint']['israel_only_sufficiency'] is False

    deps = d['dependencies']
    assert len(deps) == len(set(deps)) == 5
    for rel in deps:
        assert (ROOT / rel).is_file(), rel

    # 1) Independent sign control from the six-dimensional warped metric.
    for c in (0.07, -0.13, 0.31):
        Grr = direct_warped_einstein_rr(c)
        expected = 10.0 * c * c
        assert abs(Grr - expected) < 2e-8, (c, Grr, expected)
        # K_ab=c h_ab: 1/2(K^2-K_ab K^ab)=10 c^2 for five tangent dimensions.
        gauss = 0.5 * ((5.0 * c) ** 2 - 5.0 * c * c)
        assert abs(gauss - expected) < 1e-15

    # 2) Direct anisotropic 4+1 Israel algebra.
    cases = [
        (0.12, -0.04, 0.08, 0.03),
        (-0.21, 0.17, 0.11, -0.09),
        (0.035, 0.061, -0.044, 0.072),
        (0.4, -0.15, -0.2, 0.31),
    ]
    for vals in cases:
        lam, Y, surface, geom_jump = passive_from_israel(*vals)
        assert math.isfinite(lam) and math.isfinite(Y)
        assert abs(surface - geom_jump) < 2e-14, (vals, surface, geom_jump)

    # 3) Concrete M1 rr-constraint control. Shared intrinsic/Lambda terms cancel in the jump.
    # Impose the scalar junction phix_N + phix_S = 0 so scalar squares also cancel.
    for vals in cases:
        _, _, surface, geom_jump = passive_from_israel(*vals)
        aN, aS, lN, lS = vals
        phixN = 0.19
        phixS = -phixN
        m2 = 0.7
        phi = -0.23
        common_intrinsic = -0.41  # represents -6*k4*e^-2A + Lambda_hat
        geomN = 6*aN*aN + 4*aN*lN + common_intrinsic
        geomS = 6*aS*aS + 4*aS*lS + common_intrinsic
        # Choose positive flux energies so each frozen rr constraint is satisfied exactly.
        rhoN = geomN - 0.5*phixN*phixN + 0.5*m2*phi*phi + 5.0
        # Add the same harmless constant to both t_NN channels; it cancels in the jump.
        tN = 0.5*phixN*phixN - 0.5*m2*phi*phi + rhoN
        rhoS = rhoN + (geomS - geomN)
        tS = 0.5*phixS*phixS - 0.5*m2*phi*phi + rhoS
        assert rhoN > 0 and rhoS > 0
        assert abs((tS - tN) - geom_jump) < 2e-14
        assert abs(surface - (tS - tN)) < 2e-14
        # With the scalar junction, only the flux-energy difference remains.
        assert abs((tS - tN) - (rhoS - rhoN)) < 2e-14

    # 4) Israel alone is insufficient: modify the south normal stress while keeping geometry/Israel fixed.
    _, _, surface, _ = passive_from_israel(*cases[0])
    tN = 0.3
    tS = tN + surface + 0.271
    passive_residual = surface - (tS - tN)
    assert abs(passive_residual) > 0.2

    # 5) Z2 control: identical outward slopes map to opposite common-normal K and zero average.
    lam, Y, surface, geom_jump = passive_from_israel(0.14, 0.14, -0.03, -0.03)
    assert abs(surface) < 1e-15
    assert abs(geom_jump) < 1e-15

    g = d['gate_state']
    expected_gates = {
        'WP1_shape_Ward_identity': 'DERIVED_CONDITIONAL_REDUNDANCY',
        'WP1_passive_shape_constraint': 'DERIVED_FROM_NN_CONSTRAINTS_AND_ISRAEL',
        'WP1_israel_only_shape_closure': 'FALSE',
        'WP1_full_shape_residual': 'NOT_ASSEMBLED_FROM_DIRECT_MOVING_ACTION',
        'WP1_full_boundary_hessian': 'NOT_CLOSED',
        'WP1_full_quadratic_action': 'NOT_CLOSED',
        'PERTURBED_JUNCTION_SYSTEM': 'NOT_RELEASED',
        'PHYSICAL_BACKGROUND': 'NOT_ESTABLISHED',
        'FM-G0': 'OPEN',
        'AuthorizationDecision': 'NOT_CREATED',
        'SingleUseGrant': 'NOT_CREATED',
        'BACKEND_IMPORT': 'NOT_EXECUTED',
        'SOLVER_EXECUTION': 'NOT_EXECUTED',
        'PHYSICAL_RESPONSE_RANK': 'NOT_EXECUTED',
        'K1-D': 'NOT_RELEASED',
        'K1-E': 'NOT_ADMISSIBLE',
    }
    for key, value in expected_gates.items():
        assert g[key] == value, (key, g[key], value)

    assert d['physical_gate_effect'] == 'NONE'
    assert d['physical_evidence_effect'] == 'NONE'
    assert d['solver_authorized'] is False
    assert 'Israel allein reicht nicht' in text
    assert 'PHYSICAL_BACKGROUND           NOT_ESTABLISHED' in text

    print('ULSH-05 WP1C4B1C passive shape constraint: PASS')


if __name__ == '__main__':
    main()
