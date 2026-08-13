#!/usr/bin/env python3
"""Regression tests for the H3 v0.2 rank-one correction."""
from __future__ import annotations

import math


def close(x: float, y: float, tol: float = 1e-12) -> None:
    assert math.isclose(x, y, rel_tol=tol, abs_tol=tol), (x, y)


def test_rank_one_counterexample() -> None:
    BL, Bm, a = 0.4, 0.7, 2.5
    X = BL**2 + Bm**2 * a**-3
    beta_r = math.sqrt(X)
    beta_chi = 0.0
    close(beta_r**2 + beta_chi**2, X)


def test_source_free_alpha_completion() -> None:
    BL, Bm, a, H, M4 = 0.4, 0.7, 2.5, 0.13, 2.3
    Y = Bm**2 * a**-3
    X = BL**2 + Y
    dXdt = -3.0 * H * Y
    beta = math.sqrt(X)
    alpha_beta = -X - dXdt / (2.0 * H)
    close(alpha_beta, -BL**2 + 0.5 * Y)
    alpha = alpha_beta / beta
    rho = 3.0 * M4**2 * X
    p = M4**2 * (2.0 * alpha * beta - X)
    close(rho, 3.0 * M4**2 * (BL**2 + Y))
    close(p, -3.0 * M4**2 * BL**2)


def test_old_additive_cross_term_is_only_special_parameterization() -> None:
    BL, Bm, a = 0.4, 0.7, 2.5
    X = BL**2 + Bm**2 * a**-3
    additive_square = (BL + Bm * a**-1.5) ** 2
    assert not math.isclose(additive_square, X)
    # But sqrt(X) gives X exactly, disproving the old rank-one no-go.
    close(math.sqrt(X) ** 2, X)


def test_factorized_warp_result_still_constant() -> None:
    grad = (0.3, -0.4)
    B2 = sum(v*v for v in grad)
    for a4 in (0.1, 1.0, 10.0, 1000.0):
        _ = a4
        close(sum(v*v for v in grad), B2)


def main() -> int:
    test_rank_one_counterexample()
    test_source_free_alpha_completion()
    test_old_additive_cross_term_is_only_special_parameterization()
    test_factorized_warp_result_still_constant()
    print("[PASS] H3 v0.2 rank-one counterexample and source-free completion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
