#!/usr/bin/env python3
"""Independent pure-Python algebra tests for H4R2. No physical backend."""

from __future__ import annotations

import json
from pathlib import Path

REGISTRY = Path("registry/2026-08-14_HZT-M0_S6_C-PHYS_H4R2_BoundaryConstraintComplementingEnergyPreflight_v0.1.json")


def det(matrix):
    a = [[complex(x) for x in row] for row in matrix]
    n = len(a)
    out = 1.0 + 0.0j
    for i in range(n):
        pivot = max(range(i, n), key=lambda r: abs(a[r][i]))
        if abs(a[pivot][i]) == 0.0:
            return 0.0 + 0.0j
        if pivot != i:
            a[i], a[pivot] = a[pivot], a[i]
            out *= -1.0
        piv = a[i][i]
        out *= piv
        for r in range(i + 1, n):
            factor = a[r][i] / piv
            for c in range(i + 1, n):
                a[r][c] -= factor * a[i][c]
    return out


def block_matrix(k_n, k_s, z_n, z_s):
    b = [
        [0.0, -3.0, -1.0],
        [-1.0, -2.0, -1.0],
        [-1.0, -3.0, 0.0],
    ]
    ksum = k_n + k_s
    m = [[0.0j for _ in range(5)] for _ in range(5)]
    for i in range(3):
        for j in range(3):
            m[i][j] = ksum * b[i][j]
    m[3][3] = ksum
    m[4][4] = k_n * z_n + k_s * z_s
    return m


def closed_form(k_n, k_s, z_n, z_s):
    return -4.0 * (k_n + k_s) ** 4 * (k_n * z_n + k_s * z_s)


def main():
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert reg["solver_execution"] is False
    assert reg["physical_backend_imported"] is False

    # Independent determinant of the H4R1 metric block.
    bg = reg["two_sided_interface_symbol"]["metric_block"]
    assert abs(det(bg).real + 4.0) < 1e-12

    samples = [
        (1.0 + 0.0j, 1.0, 1.0, 1.0, 1.0),
        (1.0 + 0.3j, 0.5, 1.7, 0.2, 2.0),
        (0.2 + 1.1j, 2.2, 0.6, 3.0, 0.4),
    ]
    for zeta, c_n, c_s, z_n, z_s in samples:
        k_n = c_n * zeta
        k_s = c_s * zeta
        numeric = det(block_matrix(k_n, k_s, z_n, z_s))
        exact = closed_form(k_n, k_s, z_n, z_s)
        scale = max(1.0, abs(exact))
        assert abs(numeric - exact) / scale < 1e-11
        assert abs(numeric) > 0.0

    # Uniform lower-bound corner: equality at the minimal positive coefficients.
    c_min = 0.25
    z_min = 0.125
    numeric_corner = abs(det(block_matrix(c_min, c_min, z_min, z_min)))
    bound = 128.0 * c_min**5 * z_min
    assert abs(numeric_corner - bound) < 1e-13

    # Constraint principal matrix [[0,1],[1,0]] has characteristic speeds +/-1.
    constraint_principal = [[0.0, 1.0], [1.0, 0.0]]
    tr = constraint_principal[0][0] + constraint_principal[1][1]
    determinant = constraint_principal[0][0] * constraint_principal[1][1] - constraint_principal[0][1] * constraint_principal[1][0]
    discriminant = tr * tr - 4.0 * determinant
    lam_plus = 0.5 * (tr + discriminant ** 0.5)
    lam_minus = 0.5 * (tr - discriminant ** 0.5)
    assert {round(lam_plus, 12), round(lam_minus, 12)} == {1.0, -1.0}

    gate = reg["gate_disposition"]
    assert gate["physical_parent_solve_authorized"] is False
    assert gate["variable_coefficient_kreiss_estimate"] == "OPEN"
    assert gate["nonlinear_energy_estimate"] == "OPEN"
    assert gate["global_IBVP_existence_uniqueness"] == "OPEN"
    assert gate["K1-D"] == "NOT_RELEASED"
    assert gate["K1-E"] == "NOT_ADMISSIBLE"
    assert gate["WP4"] == "BLOCKED"
    assert gate["physical_evidence_effect"] == "NONE"

    print("PASS H4R2 independent determinant, Lopatinskii and constraint-principal tests")


if __name__ == "__main__":
    main()
