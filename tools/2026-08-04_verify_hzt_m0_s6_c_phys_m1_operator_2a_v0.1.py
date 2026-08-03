#!/usr/bin/env python3
"""Exact symbolic QA for HZT-M0-S6-C-PHYS-M1 operator block 2A."""

from __future__ import annotations

import json
import sympy as sp


def derive_constraint_identity() -> dict[str, str]:
    A, ell, varphi = sp.symbols("A ell varphi")
    Ap, ep, vp = sp.symbols("Ap ep vp")
    App, epp, vpp = sp.symbols("App epp vpp")
    k4, Lam, m2, aF, rho = sp.symbols("k4 Lam m2 aF rho")

    E_A = (
        4 * App
        + 10 * Ap**2
        - 6 * k4 * sp.exp(-2 * A)
        + Lam
        + sp.Rational(1, 2) * vp**2
        + sp.Rational(1, 2) * m2 * varphi**2
        - rho
    )
    E_ell = (
        epp
        + 3 * App * ell
        + 6 * Ap**2 * ell
        + 3 * Ap * ep
        - 3 * k4 * sp.exp(-2 * A) * ell
        + Lam * ell
        + ell
        * (
            sp.Rational(1, 2) * vp**2
            + sp.Rational(1, 2) * m2 * varphi**2
            + rho
        )
    )
    E_varphi = (
        ell * vpp
        + (4 * Ap * ell + ep) * vp
        - ell * m2 * varphi
        + 2 * aF * ell * rho
    )
    C = (
        ell * (-6 * k4 * sp.exp(-2 * A) + 6 * Ap**2 + Lam)
        + 4 * Ap * ep
        - ell
        * (
            sp.Rational(1, 2) * vp**2
            - sp.Rational(1, 2) * m2 * varphi**2
            + rho
        )
    )
    rho_p = rho * (-8 * Ap + 2 * aF * vp)
    C_p = (
        ep * (-6 * k4 * sp.exp(-2 * A) + 6 * Ap**2 + Lam)
        + ell * (12 * k4 * sp.exp(-2 * A) * Ap + 12 * Ap * App)
        + 4 * App * ep
        + 4 * Ap * epp
        - ep
        * (
            sp.Rational(1, 2) * vp**2
            - sp.Rational(1, 2) * m2 * varphi**2
            + rho
        )
        - ell * (vp * vpp - m2 * varphi * vp + rho_p)
    )
    identity = sp.simplify(
        C_p + 4 * Ap * C - (ep * E_A + 4 * Ap * E_ell - vp * E_varphi)
    )
    if identity != 0:
        raise AssertionError(f"constraint identity failed: {sp.factor(identity)}")
    return {
        "off_shell_identity": "C_x+4*A_x*C=ell_x*E_A+4*A_x*E_ell-varphi_x*E_varphi",
        "on_shell_propagation": "C_x=-4*A_x*C",
        "solution": "C(x)=C(x0)*exp[-4(A(x)-A(x0))]",
        "maxwell_condition": "rho_F_x=rho_F*(-8*A_x+2*a_F*varphi_x)",
    }


def verify_pole_series() -> dict[str, str]:
    x = sp.symbols("x")
    A0, v0 = sp.symbols("A0 v0")
    a2, a4, l3, l5, f2, f4, g2, g4 = sp.symbols(
        "a2 a4 l3 l5 f2 f4 g2 g4"
    )
    Lam, m2, aF = sp.symbols("Lam m2 aF")
    K0, R0 = sp.symbols("K0 R0")
    G2 = sp.symbols("G2")

    A = A0 + a2 * x**2 + a4 * x**4
    ell = x + l3 * x**3 + l5 * x**5
    v = v0 + f2 * x**2 + f4 * x**4
    achi = g2 * x**2 + g4 * x**4
    rho = R0 * sp.exp(-8 * (A - A0) + 2 * aF * (v - v0))

    E_A = (
        4 * sp.diff(A, x, 2)
        + 10 * sp.diff(A, x) ** 2
        - 6 * K0 * sp.exp(-2 * (A - A0))
        + Lam
        + sp.Rational(1, 2) * sp.diff(v, x) ** 2
        + sp.Rational(1, 2) * m2 * v**2
        - rho
    )
    E_ell = (
        sp.diff(ell, x, 2)
        + 3 * sp.diff(A, x, 2) * ell
        + 6 * sp.diff(A, x) ** 2 * ell
        + 3 * sp.diff(A, x) * sp.diff(ell, x)
        - 3 * K0 * sp.exp(-2 * (A - A0)) * ell
        + Lam * ell
        + ell
        * (
            sp.Rational(1, 2) * sp.diff(v, x) ** 2
            + sp.Rational(1, 2) * m2 * v**2
            + rho
        )
    )
    E_v = (
        ell * sp.diff(v, x, 2)
        + (4 * sp.diff(A, x) * ell + sp.diff(ell, x)) * sp.diff(v, x)
        - ell * m2 * v
        + 2 * aF * ell * rho
    )
    E_g = (
        sp.diff(achi, x)
        - 2 * G2 * ell * sp.exp(-4 * (A - A0) + 2 * aF * (v - v0))
    )

    leading = {
        a2: (6 * K0 - Lam - sp.Rational(1, 2) * m2 * v0**2 + R0) / 8,
        f2: (m2 * v0 - 2 * aF * R0) / 4,
    }
    leading[l3] = (
        3 * K0
        - 12 * leading[a2]
        - Lam
        - sp.Rational(1, 2) * m2 * v0**2
        - R0
    ) / 6
    leading[g2] = G2

    higher = {
        a4: -(
            40 * a2**2
            + 2 * f2**2
            + m2 * v0 * f2
            + 12 * K0 * a2
            + 8 * R0 * a2
            - 2 * aF * R0 * f2
        )
        / 48,
        f4: (
            16 * aF * R0 * a2
            - 4 * aF**2 * R0 * f2
            - 2 * aF * R0 * l3
            - 16 * a2 * f2
            - 8 * f2 * l3
            + m2 * f2
            + m2 * v0 * l3
        )
        / 16,
    }
    higher[g4] = G2 * (-2 * a2 + aF * f2 + sp.Rational(1, 2) * l3)
    higher[l5] = -(
        6 * K0 * (2 * a2 - l3)
        + 2 * R0 * (-8 * a2 + 2 * aF * f2 + l3)
        + 2 * Lam * l3
        + 48 * a2**2
        + 48 * a2 * l3
        + 96 * a4
        + 4 * f2**2
        + 2 * m2 * v0 * f2
        + m2 * v0**2 * l3
    ) / 40

    equations = [
        sp.series(E_A, x, 0, 5).removeO().expand().coeff(x, 0),
        sp.series(E_A, x, 0, 5).removeO().expand().coeff(x, 2),
        sp.series(E_ell, x, 0, 6).removeO().expand().coeff(x, 1),
        sp.series(E_ell, x, 0, 6).removeO().expand().coeff(x, 3),
        sp.series(E_v, x, 0, 6).removeO().expand().coeff(x, 1),
        sp.series(E_v, x, 0, 6).removeO().expand().coeff(x, 3),
        sp.series(E_g, x, 0, 6).removeO().expand().coeff(x, 1),
        sp.series(E_g, x, 0, 6).removeO().expand().coeff(x, 3),
    ]
    substitutions = {**leading, **higher}
    for idx, equation in enumerate(equations):
        reduced = sp.simplify(sp.expand(equation).subs(substitutions, simultaneous=True))
        reduced = sp.simplify(reduced.subs(higher, simultaneous=True))
        reduced = sp.simplify(reduced.subs(leading, simultaneous=True))
        reduced = sp.simplify(reduced.subs(higher, simultaneous=True))
        reduced = sp.simplify(reduced.subs(leading, simultaneous=True))
        if reduced != 0:
            raise AssertionError(
                f"pole coefficient equation {idx} failed: {sp.factor(reduced)}"
            )

    return {
        "series_order": "A,varphi,a_chi through x^4; ell through x^5",
        "rho_F0": "R0=0.5*q^2*exp(-8*A0+2*a_F*varphi0)",
        "K0": "K0=k4*exp(-2*A0)",
        "a4": str(higher[a4]),
        "f4": str(higher[f4]),
        "l5": str(higher[l5]),
        "g4": str(higher[g4]),
    }


def verify_principal_matrix() -> dict[str, str]:
    ell = sp.symbols("ell", positive=True)
    matrix = sp.Matrix(
        [
            [4, 0, 0, 0],
            [3 * ell, 1, 0, 0],
            [0, 0, ell, 0],
            [0, 0, 0, 1],
        ]
    )
    determinant = sp.factor(matrix.det())
    if determinant != 4 * ell:
        raise AssertionError(f"unexpected principal determinant: {determinant}")
    return {
        "variables": "(A,ell,varphi,a_chi)",
        "highest_derivatives": "(A_xx,ell_xx,varphi_xx,a_chi_x)",
        "principal_matrix": "[[4,0,0,0],[3*ell,1,0,0],[0,0,ell,0],[0,0,0,1]]",
        "determinant": "4*ell",
        "interior_status": "FULL_RANK_FOR_ELL_POSITIVE",
        "pole_status": "REGULAR_SINGULAR_REQUIRES_PARITY_FACTORIZATION",
        "complementing_boundary_status": "NOT_PROVEN",
    }


def main() -> int:
    payload = {
        "contract": "C_PHYS_M1_OPERATOR_2A_SYMBOLIC_QA",
        "status": "PASS_FORMAL",
        "constraint": derive_constraint_identity(),
        "pole_series": verify_pole_series(),
        "principal_part": verify_principal_matrix(),
        "forbidden_inference": [
            "No Fredholm property follows.",
            "No continuum Jacobian rank follows.",
            "No physical background solution follows.",
            "No R1.1 or solver authorization follows.",
        ],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
