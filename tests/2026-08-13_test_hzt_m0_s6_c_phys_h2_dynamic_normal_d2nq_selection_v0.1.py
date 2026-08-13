#!/usr/bin/env python3
"""Algebraic regression tests for H2 Codazzi degeneracy and D2N-Q profile."""

from __future__ import annotations

from fractions import Fraction
import math


def w_for_power(n: int) -> Fraction:
    # B^2 ~ a^-n => d ln(B^2)/d ln(a) = -n.
    return Fraction(-1, 1) + Fraction(n, 3)


def test_power_law_family() -> None:
    expected = {
        0: Fraction(-1, 1),
        1: Fraction(-2, 3),
        2: Fraction(-1, 3),
        3: Fraction(0, 1),
        4: Fraction(1, 3),
    }
    got = {n: w_for_power(n) for n in expected}
    assert got == expected
    # Explicitly prove non-uniqueness: source-free Codazzi admits more than n=0,3.
    assert got[1] != got[0] and got[1] != got[3]
    assert got[2] != got[0] and got[2] != got[3]
    assert got[4] != got[0] and got[4] != got[3]


def test_target_lambda_plus_dust_profile() -> None:
    # Units M4^2=1. Pick positive constants and a,H away from zero.
    BL2 = 5.0
    Bm2 = 7.0
    a = 2.0
    H = 0.25

    B2 = BL2 + Bm2 * a ** -3
    dB2_dt = -3.0 * H * Bm2 * a ** -3

    rho = 3.0 * B2
    p_from_codazzi = -(3.0 * B2 + dB2_dt / H)
    p_target = -3.0 * BL2

    assert math.isclose(p_from_codazzi, p_target, rel_tol=0.0, abs_tol=1e-12)

    drho_dt = 3.0 * dB2_dt
    conservation = drho_dt + 3.0 * H * (rho + p_from_codazzi)
    assert math.isclose(conservation, 0.0, rel_tol=0.0, abs_tol=1e-12)


def test_general_source_exchange_identity() -> None:
    # Units M4^2=1. Use arbitrary nonzero source contraction beta.S.
    H = 0.7
    B2 = 1.9
    dB2_dt = -0.31
    beta_dot_S = 0.23

    alpha_dot_beta = -B2 - dB2_dt / (2.0 * H) + beta_dot_S / (3.0 * H)
    rho = 3.0 * B2
    p = 2.0 * alpha_dot_beta - B2
    drho_dt = 3.0 * dB2_dt

    lhs = drho_dt + 3.0 * H * (rho + p)
    rhs = 2.0 * beta_dot_S
    assert math.isclose(lhs, rhs, rel_tol=0.0, abs_tol=1e-12)


def test_source_free_codazzi_does_not_fix_B2() -> None:
    # For arbitrary positive differentiable B2 histories, Codazzi only fixes alpha.beta.
    H = 0.9
    samples = [
        (2.0, 0.0),
        (2.0, -0.4),
        (2.0, 0.7),
    ]
    alpha_beta_values = []
    for B2, dB2_dt in samples:
        alpha_beta = -B2 - dB2_dt / (2.0 * H)
        alpha_beta_values.append(alpha_beta)
        residual = 0.5 * dB2_dt + H * (alpha_beta + B2)
        assert math.isclose(residual, 0.0, rel_tol=0.0, abs_tol=1e-12)

    # Distinct histories all satisfy source-free Codazzi after alpha.beta is adjusted.
    assert len({round(x, 12) for x in alpha_beta_values}) == len(samples)


def main() -> None:
    test_power_law_family()
    test_target_lambda_plus_dust_profile()
    test_general_source_exchange_identity()
    test_source_free_codazzi_does_not_fix_B2()
    print("PASS: H2 Codazzi degeneracy algebra")


if __name__ == "__main__":
    main()
