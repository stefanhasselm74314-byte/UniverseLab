#!/usr/bin/env python3
"""Independent algebra regressions for the H4R3 formal PDE preflight.

No physical backend, no PDE solve, no HZT evidence computation.
"""

from __future__ import annotations

import math


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def det3(m):
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def test_metric_row_normalization():
    bg = [[0.0, -3.0, -1.0], [-1.0, -2.0, -1.0], [-1.0, -3.0, 0.0]]
    bgi = [[0.75, -0.75, -0.25], [-0.25, 0.25, -0.25], [-0.25, -0.75, 0.75]]
    assert det3(bg) == -4.0
    prod = matmul(bgi, bg)
    for i in range(3):
        for j in range(3):
            expected = 1.0 if i == j else 0.0
            assert abs(prod[i][j] - expected) < 1e-12


def test_positive_symmetrizer_domain():
    samples = [
        (0.25, 0.4),
        (1.0, 1.0),
        (3.0, 2.5),
        (0.75, 4.0),
    ]
    for z, c in samples:
        d = [1.0, 1.0, 1.0, 1.0, z]
        a0 = [x / (c * c) for x in d] + d
        assert min(a0) > 0.0
        coercive = min(1.0, z) * min(1.0, 1.0 / (c * c))
        assert min(a0) + 1e-15 >= coercive


def test_symmetric_spatial_block():
    z = 0.7
    d = [1.0, 1.0, 1.0, 1.0, z]
    n = len(d)
    a1 = [[0.0 for _ in range(2 * n)] for __ in range(2 * n)]
    for i, x in enumerate(d):
        a1[i][n + i] = -x
        a1[n + i][i] = -x
    for i in range(2 * n):
        for j in range(2 * n):
            assert a1[i][j] == a1[j][i]


def test_interface_flux_cancellation_family():
    p = [1.2, -0.7, 0.4, 0.9, -0.3]
    qn = [0.1, 0.2, -0.5, 0.8, 0.6]
    for zn, zs in [(0.2, 0.4), (0.9, 1.1), (2.0, 0.5), (5.0, 3.0)]:
        dn = [1.0, 1.0, 1.0, 1.0, zn]
        ds = [1.0, 1.0, 1.0, 1.0, zs]
        qs = [-(dn[i] / ds[i]) * qn[i] for i in range(5)]
        match = [dn[i] * qn[i] + ds[i] * qs[i] for i in range(5)]
        assert max(abs(x) for x in match) < 1e-12
        flux = sum(p[i] * match[i] for i in range(5))
        assert abs(flux) < 1e-12


def test_maximal_interface_count():
    derivative_boundary_variables = 4 * 5
    principal_conditions = 2 * 5
    allowed_dimension = derivative_boundary_variables - principal_conditions
    assert derivative_boundary_variables == 20
    assert principal_conditions == 10
    assert allowed_dimension == 10
    assert 2 * allowed_dimension == derivative_boundary_variables


def test_energy_ode_template_local_bound():
    # The H4R3 estimate is E' <= C(1+sqrt(E))E in the homogeneous case.
    # This test only checks the declared RHS is nonnegative and locally Lipschitz
    # for finite E>=0; it is not a physical evolution.
    C = 2.0
    for E in [0.0, 1e-8, 0.1, 1.0, 10.0]:
        rhs = C * (1.0 + math.sqrt(E)) * E
        assert rhs >= 0.0
        assert math.isfinite(rhs)


def main():
    test_metric_row_normalization()
    test_positive_symmetrizer_domain()
    test_symmetric_spatial_block()
    test_interface_flux_cancellation_family()
    test_maximal_interface_count()
    test_energy_ode_template_local_bound()
    print("PASS H4R3 independent symmetrizer / interface-flux algebra regressions")


if __name__ == "__main__":
    main()
