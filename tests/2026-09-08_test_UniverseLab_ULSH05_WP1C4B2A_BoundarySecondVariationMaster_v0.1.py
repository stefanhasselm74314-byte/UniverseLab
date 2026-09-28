#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'registry/2026-09-08_UniverseLab_ULSH05_WP1C4B2A_BoundarySecondVariationMaster_v0.1.json'
DOC = ROOT / 'science/solver-hub/2026-09-08_UniverseLab_ULSH05_WP1C4B2A_BoundarySecondVariationMaster_v0.1.md'


def gravity_action(rho: float, c: float, Lambda: float) -> float:
    e = math.exp(5.0 * c * rho)
    integral = (e - 1.0) / (5.0 * c) if abs(c) > 1e-14 else rho
    bulk = 0.5 * (-30.0 * c * c - 2.0 * Lambda) * integral
    return bulk + 5.0 * c * e - 5.0 * c


def central_epsilon2_coeff(fn, h: float) -> float:
    return (fn(h) - 2.0 * fn(0.0) + fn(-h)) / (2.0 * h * h)


def cap_density(hdiag, B, lam: float, Z: float) -> float:
    det = math.prod(hdiag)
    assert det < 0.0
    X = sum(B[i] * B[i] / hdiag[i] for i in range(5))
    return math.sqrt(-det) * (-lam - 0.5 * Z * X)


def cap_C2(h, w, q, d, lam: float, Z: float) -> float:
    qtrace = sum(q[i] / h[i] for i in range(5))
    qnorm = sum(q[i] * q[i] / (h[i] * h[i]) for i in range(5))
    n1 = 0.5 * qtrace
    n2 = qtrace * qtrace / 8.0 - qnorm / 4.0
    X0 = sum(w[i] * w[i] / h[i] for i in range(5))
    X1 = 2.0 * sum(w[i] * d[i] / h[i] for i in range(5)) - sum(
        q[i] * w[i] * w[i] / (h[i] * h[i]) for i in range(5)
    )
    X2 = (
        sum(d[i] * d[i] / h[i] for i in range(5))
        - 2.0 * sum(q[i] * w[i] * d[i] / (h[i] * h[i]) for i in range(5))
        + sum(q[i] * q[i] * w[i] * w[i] / (h[i] ** 3) for i in range(5))
    )
    l0 = -lam - 0.5 * Z * X0
    l1 = -0.5 * Z * X1
    l2 = -0.5 * Z * X2
    return l2 + n1 * l1 + n2 * l0


def cap_D1(h, w, r, e, lam: float, Z: float) -> float:
    rtrace = sum(r[i] / h[i] for i in range(5))
    n1 = 0.5 * rtrace
    X0 = sum(w[i] * w[i] / h[i] for i in range(5))
    X1 = 2.0 * sum(w[i] * e[i] / h[i] for i in range(5)) - sum(
        r[i] * w[i] * w[i] / (h[i] * h[i]) for i in range(5)
    )
    l0 = -lam - 0.5 * Z * X0
    l1 = -0.5 * Z * X1
    return l1 + n1 * l0


def main() -> None:
    d = json.loads(CONTRACT.read_text())
    text = DOC.read_text()

    assert d['model_id'] == 'HZT-M0-S6-C-PHYS-M1'
    assert d['work_package'] == 'ULSH-05/WP1C4B2A'
    assert d['status'] == 'DERIVED_SECOND_ORDER_BOUNDARY_CHAIN_RULE_CAP_MOVING_PATH_CLOSED_COMPONENT_RESIDUAL_OPERATOR_NOT_YET_ASSEMBLED'
    assert d['intrinsic_cap_chain_rule']['normalization'].startswith('C2, D1 and C_cap')

    deps = d['dependencies']
    assert len(deps) == len(set(deps)) == 8
    for rel in deps:
        assert (ROOT / rel).is_file(), rel

    # 1) Accelerated moving EH+GHY boundary: path coefficient vs chart coefficient.
    gravity_cases = [
        (0.07, 0.21, 0.43, 0.30, -0.40),
        (-0.13, -0.37, 0.31, -0.25, 0.20),
        (0.31, 0.11, 0.22, 0.12, 0.50),
    ]
    for c, Lambda, rho0, xi, chi in gravity_cases:
        def path(eps: float) -> float:
            rho = rho0 + eps * xi + 0.5 * eps * eps * chi
            return gravity_action(rho, c, Lambda)

        direct_path = central_epsilon2_coeff(path, 2e-4)
        Sprime = math.exp(5.0 * c * rho0) * (10.0 * c * c - Lambda)
        Ssecond = 5.0 * c * Sprime
        expected_path = 0.5 * xi * xi * Ssecond + 0.5 * chi * Sprime
        expected_chart = 0.5 * xi * xi * Ssecond
        direct_chart = direct_path - 0.5 * chi * Sprime
        assert abs(Sprime) > 1e-3  # explicitly off shell in this control
        assert abs(direct_path - expected_path) < 1e-8, (direct_path, expected_path)
        assert abs(direct_chart - expected_chart) < 1e-8, (direct_chart, expected_chart)

    # 2) Nonlinear intrinsic cap path on a Lorentz-signature five-metric.
    hbar = [-1.2, 1.1, 0.95, 1.3, 0.8]
    w = [0.31, -0.17, 0.22, 0.08, -0.11]
    q = [0.07, -0.04, 0.03, 0.05, -0.02]
    d1 = [-0.06, 0.09, 0.04, -0.05, 0.07]
    r_bil = [0.03, -0.02, 0.015, -0.01, 0.025]
    e_bil = [0.02, 0.03, -0.015, 0.04, -0.025]
    r_acc = [-0.012, 0.014, 0.011, -0.013, 0.009]
    e_acc = [0.013, -0.017, 0.01, 0.008, -0.012]
    r_total = [r_bil[i] + r_acc[i] for i in range(5)]
    e_total = [e_bil[i] + e_acc[i] for i in range(5)]
    lam = 0.73
    Z = 1.4
    sqrt_hbar = math.sqrt(-math.prod(hbar))

    def cap_path(eps: float, rvec, evec) -> float:
        h = [hbar[i] + eps * q[i] + 0.5 * eps * eps * rvec[i] for i in range(5)]
        B = [w[i] + eps * d1[i] + 0.5 * eps * eps * evec[i] for i in range(5)]
        return cap_density(h, B, lam, Z)

    direct_raw = central_epsilon2_coeff(lambda eps: cap_path(eps, r_total, e_total), 1e-3)
    direct_normalized = direct_raw / sqrt_hbar
    C2 = cap_C2(hbar, w, q, d1, lam, Z)
    D1_total = cap_D1(hbar, w, r_total, e_total, lam, Z)
    expected_normalized_path = C2 + 0.5 * D1_total
    assert abs(direct_normalized - expected_normalized_path) < 2e-8, (
        direct_normalized,
        expected_normalized_path,
    )

    # 3) Explicit chart subtraction: remove only the acceleration-linear D1 piece.
    D1_acc = cap_D1(hbar, w, r_acc, e_acc, lam, Z)
    D1_bil = cap_D1(hbar, w, r_bil, e_bil, lam, Z)
    direct_chart = direct_normalized - 0.5 * D1_acc
    expected_chart = C2 + 0.5 * D1_bil
    assert abs(direct_chart - expected_chart) < 2e-8
    # Linearity of D1 is itself required by the chain rule.
    assert abs(D1_total - D1_acc - D1_bil) < 1e-15

    # 4) Fixed-interface affine limit reproduces merged WP1C2 exactly.
    direct_fixed_raw = central_epsilon2_coeff(
        lambda eps: cap_path(eps, [0.0] * 5, [0.0] * 5),
        1e-3,
    )
    direct_fixed_normalized = direct_fixed_raw / sqrt_hbar
    assert abs(direct_fixed_normalized - C2) < 2e-8

    # 5) Off-shell residual x path-acceleration is real and may not be dropped wholesale.
    # Scalar toy action F(x)=a*x+0.5*b*x^2 along x=eps*u+0.5*eps^2*v.
    a = 1.7  # nonzero first residual
    b = -0.8
    u = 0.6
    v = -0.4
    path_coeff = 0.5 * b * u * u + 0.5 * a * v
    chart_coeff = path_coeff - 0.5 * a * v
    assert abs(path_coeff - chart_coeff) > 0.3
    assert abs(chart_coeff - 0.5 * b * u * u) < 1e-15

    # 6) Master/gate semantics.
    split = d['chart_acceleration_split']
    assert split['c4b0_identity'] == 'S_path,quad^(2)=0.5*D2S[u,u]+0.5*DS[v]'
    assert 'residual-proportional U2_bil terms may not be dropped' in split['critical_firewall']

    readiness = d['residual_linearization_readiness']
    assert readiness['DeltaR_sigma'] == 'NOT_YET_COMPONENTIZED_FOR_GENERAL_MOVING_INTERFACE'
    assert readiness['DeltaR_perp'].endswith('NOT_YET_COMPONENTIZED')

    g = d['gate_state']
    expected_gates = {
        'WP1_first_shape_level': 'CLOSED_ANALYTICALLY_AS_REDUNDANT_CONSTRAINT_CHANNEL',
        'WP1_boundary_second_variation_chain_rule': 'DERIVED',
        'WP1_intrinsic_cap_moving_second_variation': 'DERIVED_CHAIN_RULE_MASTER',
        'WP1_moving_GHY_second_variation': 'DERIVED_SHAPE_CONTROL_AND_RESIDUAL_CHAIN_RULE_MASTER',
        'WP1_boundary_residual_linearizations': 'PARTIAL_NOT_FULLY_COMPONENTIZED',
        'WP1_full_boundary_hessian': 'NOT_CLOSED_COMPONENT_OPERATOR_AND_SYMMETRY_TEST_OPEN',
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
    assert 'nur dieser' in text
    assert 'PHYSICAL_BACKGROUND             NOT_ESTABLISHED' in text

    print('ULSH-05 WP1C4B2A boundary second-variation master: PASS')


if __name__ == '__main__':
    main()
