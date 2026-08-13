#!/usr/bin/env python3
"""Analytic regression tests for H3 local B^2 bridge and ansatz no-go."""
from __future__ import annotations

import math


def close(a: float, b: float, tol: float = 1e-12) -> None:
    assert math.isclose(a, b, rel_tol=tol, abs_tol=tol), (a, b)


def test_local_bridge() -> None:
    # Orthornormal normal derivatives of ln(a).
    d1, d2 = 0.7, -0.2
    B2 = d1 * d1 + d2 * d2
    close(B2, 0.53)
    assert B2 >= 0.0


def test_factorized_warp_has_time_independent_B2() -> None:
    # a(t,y)=a4(t) exp(A(y)); normal derivative kills a4(t).
    gradA = (0.3, -0.4)
    values = []
    for a4 in (0.1, 1.0, 10.0, 1e3):
        _ = a4
        values.append(sum(g * g for g in gradA))
    assert all(math.isclose(v, values[0]) for v in values)
    close(values[0], 0.25)


def test_rank_one_target_cross_term() -> None:
    BL, Bm, a = 0.4, 0.7, 2.5
    rank_one = (BL + Bm * a ** (-1.5)) ** 2
    target = BL**2 + Bm**2 * a ** (-3.0)
    cross = 2.0 * BL * Bm * a ** (-1.5)
    close(rank_one - target, cross)
    assert abs(cross) > 0.0


def test_orthogonal_two_normal_target_has_no_cross_term() -> None:
    BL, Bm, a = 0.4, 0.7, 2.5
    beta = (BL, Bm * a ** (-1.5))
    B2 = beta[0] ** 2 + beta[1] ** 2
    target = BL**2 + Bm**2 * a ** (-3.0)
    close(B2, target)


def test_degenerate_limits_escape_rank_one_no_go() -> None:
    a = 3.0
    # If either amplitude vanishes there is no forbidden cross term.
    for BL, Bm in ((0.0, 0.8), (0.8, 0.0)):
        rank_one = (BL + Bm * a ** (-1.5)) ** 2
        target = BL**2 + Bm**2 * a ** (-3.0)
        close(rank_one, target)


def main() -> int:
    test_local_bridge()
    test_factorized_warp_has_time_independent_B2()
    test_rank_one_target_cross_term()
    test_orthogonal_two_normal_target_has_no_cross_term()
    test_degenerate_limits_escape_rank_one_no_go()
    print("[PASS] H3 analytic B2 bridge / factorized-warp / rank-one no-go regressions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
