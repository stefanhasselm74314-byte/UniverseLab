#!/usr/bin/env python3
"""Algebraic regression tests for H4. No physical solver is executed."""

from __future__ import annotations

import math


def det3(m):
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def test_gravitational_principal_determinant():
    for a, L in [(0.7, 0.9), (1.0, 2.0), (3.2, 1.4)]:
        m = [
            [0.0, 3 * a**2 * L, a**3],
            [3 * a**2 * L, 6 * a * L, 3 * a**2],
            [a**3, 3 * a**2, 0.0],
        ]
        expected = 12 * a**7 * L
        assert math.isclose(det3(m), expected, rel_tol=1e-12, abs_tol=1e-12)
        assert expected > 0.0


def test_lambda_dust_fit_free_identity_and_reconstruction():
    for N in [-2.0, -0.4, 0.0, 0.8, 1.7]:
        B_L2 = 0.31
        B_m2 = 1.27
        e = math.exp(-3 * N)
        X = B_L2 + B_m2 * e
        X_N = -3 * B_m2 * e
        X_NN = 9 * B_m2 * e
        residual = X_NN + 3 * X_N
        reconstructed_m2 = -(math.exp(3 * N) / 3.0) * X_N
        reconstructed_L2 = X + X_N / 3.0
        assert math.isclose(residual, 0.0, abs_tol=1e-12)
        assert math.isclose(reconstructed_m2, B_m2, rel_tol=1e-12)
        assert math.isclose(reconstructed_L2, B_L2, rel_tol=1e-12)


def test_source_free_rank_one_codazzi_completion():
    for N in [-1.0, 0.0, 0.6]:
        B_L2 = 0.41
        B_m2 = 0.83
        e = math.exp(-3 * N)
        X = B_L2 + B_m2 * e
        X_N = -3 * B_m2 * e
        alpha_beta = -X - 0.5 * X_N
        expected = -B_L2 + 0.5 * B_m2 * e
        assert math.isclose(alpha_beta, expected, rel_tol=1e-12, abs_tol=1e-12)


def test_dynamic_junction_static_limit():
    kappa2 = 0.37
    lam = 1.8
    Y = 0.4
    A = 0.2
    Ls = -0.1
    Kt = Ka = A
    Kchi = Ls
    dynamic_time = -(3 * Ka + Kchi) + kappa2 * (lam + Y / 2)
    static_4d = -(3 * A + Ls) + kappa2 * (lam + Y / 2)
    dynamic_chi = -(Kt + 3 * Ka) + kappa2 * (lam - Y / 2)
    static_chi = -4 * A + kappa2 * (lam - Y / 2)
    assert math.isclose(dynamic_time, static_4d, abs_tol=1e-15)
    assert math.isclose(dynamic_chi, static_chi, abs_tol=1e-15)
    assert math.isclose(Kt - Ka, 0.0, abs_tol=1e-15)


def test_mixed_flux_can_cancel_but_is_not_identity():
    Z = 2.0
    L = 4.0
    phi_t, phi_r = 3.0, 5.0
    A_t, A_r = 2.0, -60.0
    Ttr = phi_t * phi_r + Z * A_t * A_r / L**2
    assert math.isclose(Ttr, 0.0, abs_tol=1e-15)
    generic = phi_t * phi_r + Z * A_t * 1.0 / L**2
    assert not math.isclose(generic, 0.0, abs_tol=1e-12)


def main():
    tests = [
        test_gravitational_principal_determinant,
        test_lambda_dust_fit_free_identity_and_reconstruction,
        test_source_free_rank_one_codazzi_completion,
        test_dynamic_junction_static_limit,
        test_mixed_flux_can_cancel_but_is_not_identity,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS {len(tests)} H4 algebraic regression tests; no physical solver executed")


if __name__ == "__main__":
    main()
