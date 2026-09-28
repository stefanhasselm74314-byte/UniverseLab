#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'registry/2026-09-08_UniverseLab_ULSH05_WP1C4B1D_DirectMovingActionShape_v0.1.json'
DOC = ROOT / 'science/solver-hub/2026-09-08_UniverseLab_ULSH05_WP1C4B1D_DirectMovingActionShape_v0.1.md'
FUNCTION_FREEZE = ROOT / 'registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json'


def central_diff(fn, x: float, h: float = 1e-6) -> float:
    return (fn(x + h) - fn(x - h)) / (2.0 * h)


def gravity_interval_action(rho: float, c: float, Lambda: float) -> float:
    # Per unit tangential coordinate volume. Lower-boundary GHY is constant in rho.
    e = math.exp(5.0 * c * rho)
    if abs(c) < 1e-14:
        integral = rho
    else:
        integral = (e - 1.0) / (5.0 * c)
    bulk = 0.5 * (-30.0 * c * c - 2.0 * Lambda) * integral
    upper_ghy = 5.0 * c * e
    lower_ghy = -5.0 * c
    return bulk + upper_ghy + lower_ghy


def passive_from_israel(aN: float, aS: float, lN: float, lS: float):
    A_sum = aN + aS
    L_sum = lN + lS
    Y = L_sum - A_sum
    lam = 0.5 * (7.0 * A_sum + L_sum)
    Abar = 0.5 * (aN - aS)
    Lbar = 0.5 * (lN - lS)
    surface = 4.0 * (-lam - 0.5 * Y) * Abar + (-lam + 0.5 * Y) * Lbar
    geom_jump = (6.0 * aS * aS + 4.0 * aS * lS) - (6.0 * aN * aN + 4.0 * aN * lN)
    return surface, geom_jump


def main() -> None:
    d = json.loads(CONTRACT.read_text())
    text = DOC.read_text()
    freeze = json.loads(FUNCTION_FREEZE.read_text())

    assert d['model_id'] == 'HZT-M0-S6-C-PHYS-M1'
    assert d['work_package'] == 'ULSH-05/WP1C4B1D'
    assert d['assembled_interface_first_variation']['direct_shape_residual'] == 'R_perp_direct=M6^4*[(G_NN+Lambda6)]_c-[T_NN]_c'
    assert d['equivalence_to_wp1c4b1c']['classification'] == 'DERIVED_DIRECT_ACTION_EQUIVALENCE_AND_REDUNDANCY'

    deps = d['dependencies']
    assert len(deps) == len(set(deps)) == 8
    for rel in deps:
        assert (ROOT / rel).is_file(), rel

    # M1 cap has no local scalar source from lambda or Z_sigma.
    exact = freeze['exact_functions']
    assert exact['lambda']['derivatives']['d_lambda_dphi'] == '0'
    assert exact['Z_sigma']['derivatives']['d_Z_sigma_dphi'] == '0'

    # 1) Direct EH+GHY moving-boundary finite difference.
    gravity_cases = [
        (0.07, 0.21, 0.43),
        (-0.13, -0.37, 0.31),
        (0.31, 0.11, 0.22),
    ]
    for c, Lambda, rho in gravity_cases:
        direct = central_diff(lambda r: gravity_interval_action(r, c, Lambda), rho, 2e-6)
        sqrt_h = math.exp(5.0 * c * rho)
        expected = sqrt_h * (10.0 * c * c - Lambda)
        assert abs(direct - expected) < 2e-8 + 2e-8 * abs(expected), (c, Lambda, rho, direct, expected)

        # Independent decomposition on the moving upper boundary, xi=1.
        # Pi_ab=-4c h_ab, H_ab=2c h_ab, five tangential dimensions.
        pi_dot_H = -40.0 * c * c
        brown_york_channel = -0.5 * pi_dot_H
        G_NN = 10.0 * c * c
        shape_channel = -(G_NN + Lambda)
        decomposed = sqrt_h * (brown_york_channel + shape_channel)
        assert abs(decomposed - expected) < 1e-13

    # 2) Direct scalar moving-interval finite difference.
    for v, U, rho in [(0.8, 0.3, 0.7), (-1.1, 0.12, 0.4), (0.25, -0.08, 1.2)]:
        L = -0.5 * v * v - U
        direct = central_diff(lambda r: r * L, rho)
        Qphi = v
        Phi = v  # fixed ambient phi=v*r, unit boundary displacement
        T_NN = 0.5 * v * v - U
        decomposed = -Qphi * Phi + T_NN
        assert abs(direct - L) < 1e-10
        assert abs(decomposed - L) < 1e-15

    # 3) Direct Maxwell moving-interval finite difference, flat r-chi control.
    for Z, f, rho in [(1.3, 0.7, 0.8), (0.6, -1.1, 0.5), (2.0, 0.22, 1.4)]:
        L = -0.5 * Z * f * f  # F^2=2 f^2
        direct = central_diff(lambda r: r * L, rho)
        QF = Z * f
        Acal = f  # A_chi=f*r, unit boundary displacement
        T_NN = 0.5 * Z * f * f
        decomposed = -QF * Acal + T_NN
        assert abs(direct - L) < 1e-10
        assert abs(decomposed - L) < 1e-15

    # 4) Two-side common-normal assembly, xi_N=+xi, xi_S=-xi.
    for EN, ES, TN, TS in [(0.4, -0.2, 0.1, 0.7), (-1.0, 0.8, -0.3, 0.2), (0.03, 0.11, 0.7, 0.65)]:
        regional = (TN - EN) - (TS - ES)  # M6^4=1 control
        master = (ES - EN) - (TS - TN)
        assert abs(regional - master) < 1e-15

    # 5) Israel/Gauss equivalence to C4B1C passive residual.
    cases = [
        (0.12, -0.04, 0.08, 0.03),
        (-0.21, 0.17, 0.11, -0.09),
        (0.035, 0.061, -0.044, 0.072),
    ]
    for vals in cases:
        surface, geom_jump = passive_from_israel(*vals)
        assert abs(surface - geom_jump) < 2e-14
        tN = -0.17
        tS = 0.29
        direct_residual = geom_jump - (tS - tN)
        passive_residual = surface - (tS - tN)
        assert abs(direct_residual - passive_residual) < 2e-14

    # 6) Both regional NN constraints make the direct shape residual redundant.
    for EN, ES in [(0.5, -0.2), (-1.1, 0.9), (0.0, 0.37)]:
        TN = EN  # M6^4=1 and E includes G_NN+Lambda
        TS = ES
        direct_residual = (ES - EN) - (TS - TN)
        assert abs(direct_residual) < 1e-15

    # 7) Israel alone does not close the direct residual.
    surface, geom_jump = passive_from_israel(*cases[0])
    tN = 0.2
    tS = tN + surface + 0.31
    assert abs(geom_jump - surface) < 2e-14
    direct_residual = geom_jump - (tS - tN)
    assert abs(direct_residual) > 0.3

    # 8) Boundary residual basis and governance firewalls.
    basis = d['off_shell_ward_basis']
    assert basis['independent_interface_channels'] == ['H_ab', 'Phi_Sigma', 'Acal_a modulo intrinsic U(1)', 's', 'xi']
    assert basis['residual_channels'] == ['R_h^ab', 'R_phi', 'R_A^a', 'R_sigma', 'R_perp_direct']

    g = d['gate_state']
    expected = {
        'WP1_shape_Ward_identity': 'DERIVED_CONDITIONAL_REDUNDANCY',
        'WP1_passive_shape_constraint': 'DERIVED_FROM_NN_CONSTRAINTS_AND_ISRAEL',
        'WP1_direct_moving_action_first_variation': 'DERIVED_INTERFACE_DECOMPOSITION',
        'WP1_direct_shape_residual': 'DERIVED_AS_NN_CONSTRAINT_JUMP',
        'WP1_first_shape_equivalence': 'DERIVED_DIRECT_ACTION_TO_PASSIVE_CONSTRAINT',
        'WP1_first_shape_level': 'CLOSED_ANALYTICALLY_AS_REDUNDANT_CONSTRAINT_CHANNEL',
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
    for key, value in expected.items():
        assert g[key] == value, (key, g[key], value)

    assert d['physical_gate_effect'] == 'NONE'
    assert d['physical_evidence_effect'] == 'NONE'
    assert d['solver_authorized'] is False
    assert 'reiner Koordinatenshift nicht genügt' in text
    assert 'PHYSICAL_BACKGROUND            NOT_ESTABLISHED' in text

    print('ULSH-05 WP1C4B1D direct moving-action shape: PASS')


if __name__ == '__main__':
    main()
