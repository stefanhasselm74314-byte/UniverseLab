#!/usr/bin/env python3
"""Algebraic H4R1 preflight tests. No physical solver or backend is imported."""

from __future__ import annotations

import math


def det3(m):
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def test_dimensionless_roundtrip():
    M6 = 2.75
    t, r, phi, L, A_chi = 0.37, 1.21, 4.4, 0.83, -1.7
    tau = M6 * t
    x = M6 * r
    varphi = phi / M6**2
    ell = M6 * L
    a_chi = A_chi / M6
    assert math.isclose(tau / M6, t, rel_tol=1e-15)
    assert math.isclose(x / M6, r, rel_tol=1e-15)
    assert math.isclose(varphi * M6**2, phi, rel_tol=1e-15)
    assert math.isclose(ell / M6, L, rel_tol=1e-15)
    assert math.isclose(a_chi * M6, A_chi, rel_tol=1e-15)


def test_h4_principal_nondegeneracy_and_characteristics():
    a, L, a_F, varphi = 1.4, 0.9, 0.25, -0.3
    Z_F = math.exp(-2.0 * a_F * varphi)
    Kg = [
        [0.0, 3.0 * a**2 * L, a**3],
        [3.0 * a**2 * L, 6.0 * a * L, 3.0 * a**2],
        [a**3, 3.0 * a**2, 0.0],
    ]
    det_g = det3(Kg)
    scalar = -0.5 * a**3 * L
    gauge = -0.5 * a**3 * Z_F / L
    det_field = det_g * scalar * gauge
    assert math.isclose(det_g, 12.0 * a**7 * L, rel_tol=1e-12)
    assert Z_F > 0.0 and det_field != 0.0
    q = -(0.4**2) + 1.1**2
    assert q != 0.0 and det_field * q**5 != 0.0
    assert math.isclose(-(1.0**2) + 1.0**2, 0.0, abs_tol=1e-15)


def test_metric_boundary_normal_rank():
    B = [[0.0, -3.0, -1.0], [-1.0, -2.0, -1.0], [-1.0, -3.0, 0.0]]
    assert math.isclose(det3(B), -4.0, abs_tol=1e-15)


def test_full_boundary_normal_determinant_nonzero():
    ell, a_F, varphi = 1.7, 0.25, 0.4
    Z_F = math.exp(-2.0 * a_F * varphi)
    determinant = -4.0 * Z_F / ell**2
    assert Z_F > 0.0 and ell > 0.0 and determinant != 0.0


def test_patch_flux_propagation_condition():
    N_F, q_hat, a_s = 3, 1.25, -0.8
    a_n = a_s + N_F / q_hat
    assert math.isclose(a_n - a_s - N_F / q_hat, 0.0, abs_tol=1e-15)
    da_n = da_s = 0.037
    assert math.isclose(da_n - da_s, 0.0, abs_tol=1e-15)
    assert not math.isclose(da_n - (da_s + 0.01), 0.0, abs_tol=1e-15)


def main():
    tests = [
        test_dimensionless_roundtrip,
        test_h4_principal_nondegeneracy_and_characteristics,
        test_metric_boundary_normal_rank,
        test_full_boundary_normal_determinant_nonzero,
        test_patch_flux_propagation_condition,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS {len(tests)} H4R1 algebraic preflight tests; no physical solver executed")


if __name__ == "__main__":
    main()
