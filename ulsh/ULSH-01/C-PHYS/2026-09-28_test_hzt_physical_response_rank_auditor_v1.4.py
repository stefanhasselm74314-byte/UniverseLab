#!/usr/bin/env python3
"""SIM-70 adversarial QA for response-rank auditor v1.4.

Software/numerical QA only. No physical solver import and no physical evidence.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / "2026-09-28_hzt_physical_response_rank_auditor_v1.4.py"
spec = importlib.util.spec_from_file_location("rank_auditor_v14", TARGET)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def full_rank_matrix():
    return np.array(
        [
            [4.0, 0.0, 0.0, 0.0, 0.10],
            [0.0, 3.0, 0.0, 0.0, 0.10],
            [0.0, 0.0, 2.0, 0.0, 0.10],
            [0.0, 0.0, 0.0, 1.0, 0.10],
        ],
        dtype=float,
    )


def test_svd_rrqr_minor_agree_on_full_rank():
    A = full_rank_matrix()
    _, s, _, _ = m.svd_decomp(A)
    rr = m.rrqr_diagnostics(A, 1e-8)
    md = m.minor_diagnostics(A, 1e-8)
    assert np.sum(s > 1e-8 * s[0]) == 4
    assert rr["rank"] == 4
    assert md["rank4_support"] is True
    assert md["cauchy_binet_relative_mismatch"] < 1e-12


def test_svd_rrqr_minor_agree_on_exact_rank3():
    A = full_rank_matrix()
    A[3] = A[2]
    _, s, _, _ = m.svd_decomp(A)
    rr = m.rrqr_diagnostics(A, 1e-8)
    md = m.minor_diagnostics(A, 1e-8)
    assert np.sum(s > 1e-8 * s[0]) == 3
    assert rr["rank"] == 3
    assert md["rank4_support"] is False


def test_rrqr_rank_invariant_under_global_scaling_and_column_permutation():
    A = full_rank_matrix()
    perm = [4, 2, 0, 3, 1]
    for factor in (1e-12, 1.0, 1e12):
        rr = m.rrqr_diagnostics(factor * A[:, perm], 1e-8)
        assert rr["rank"] == 4


def test_minor_energy_matches_cauchy_binet_product():
    rng = np.random.default_rng(20260928)
    A = rng.normal(size=(4, 5))
    md = m.minor_diagnostics(A, 1e-8)
    assert md["cauchy_binet_relative_mismatch"] < 1e-12


def test_precision_ladder_supports_well_conditioned_rank4():
    A = full_rank_matrix()
    out = m.precision_ladder(A, 1e-8, mp_dps=80)
    assert out["status"] == "RECORDED_MATRIX_ANALYSIS_ONLY"
    assert out["float64"]["rank4_support"] is True
    assert out["longdouble"]["rank4_support"] is True
    assert out["mpmath"]["rank4_support"] is True


def test_observed_second_order():
    p = m.observed_order(4.0e-4, 1.0e-4)
    assert p is not None
    assert abs(p - 2.0) < 1e-14


def test_cluster_dimension_and_subspace_rotation_invariance():
    s = np.array([10.0, 5.0, 1.02, 1.0])
    assert m.weakest_cluster_dimension(s, 1.05) == 2

    V1 = np.zeros((4, 5))
    V1[0, 0] = 1.0
    V1[1, 1] = 1.0
    V1[2, 2] = 1.0
    V1[3, 3] = 1.0

    theta = 0.73
    V2 = V1.copy()
    V2[2] = np.cos(theta) * V1[2] + np.sin(theta) * V1[3]
    V2[3] = -np.sin(theta) * V1[2] + np.cos(theta) * V1[3]

    one_vector = m.principal_angle_max_deg(V1, V2, 1)
    subspace = m.principal_angle_max_deg(V1, V2, 2)
    assert one_vector > 10.0
    assert subspace < 1e-10


def test_longdouble_determinant_against_float_reference():
    A = np.array(
        [
            [3.0, 1.0, 0.0, 0.0],
            [0.0, 2.0, 1.0, 0.0],
            [0.0, 0.0, 5.0, 1.0],
            [1.0, 0.0, 0.0, 7.0],
        ]
    )
    got = float(m.det_longdouble(A))
    expected = float(np.linalg.det(A))
    assert abs(got - expected) < 1e-12


if __name__ == "__main__":
    test_svd_rrqr_minor_agree_on_full_rank()
    test_svd_rrqr_minor_agree_on_exact_rank3()
    test_rrqr_rank_invariant_under_global_scaling_and_column_permutation()
    test_minor_energy_matches_cauchy_binet_product()
    test_precision_ladder_supports_well_conditioned_rank4()
    test_observed_second_order()
    test_cluster_dimension_and_subspace_rotation_invariance()
    test_longdouble_determinant_against_float_reference()
    print("SIM-70 response-rank auditor v1.4 adversarial QA: PASS (NO PHYSICAL EXECUTION)")
