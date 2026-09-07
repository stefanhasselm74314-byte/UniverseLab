#!/usr/bin/env python3
"""Independent controls for ULSH-05/WP1C4B1A moving-domain transport master."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1C4B1A_MovingDomainTransportMaster_v0.1.json"
C4B0 = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1C4B0_SecondOrderEmbeddingPathContract_v0.1.json"
C4A = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1C4A_GluingNormalFluxJunctions_v0.1.json"
DOC = ROOT / "science/solver-hub/2026-09-07_UniverseLab_ULSH05_WP1C4B1A_MovingDomainTransportMaster_v0.1.md"


def close(a: float, b: float, atol: float = 1e-7, rtol: float = 1e-7) -> None:
    assert math.isfinite(a) and math.isfinite(b), (a, b)
    assert abs(a - b) <= atol + rtol * max(abs(a), abs(b)), (a, b, abs(a-b))


def poly_int(c0: float, c1: float, c2: float, x: float) -> float:
    return c0*x + 0.5*c1*x*x + (c2/3.0)*x*x*x


def single_interval_transport_control() -> None:
    a0 = 0.83
    xi = -0.27
    chi = 0.36

    # f_j(x)=c0+c1*x+c2*x^2 for j=0,1,2.
    c0 = (1.1, 0.4, 0.2)
    c1 = (-0.3, 0.5, -0.1)
    c2 = (0.7, -0.2, 0.3)

    def val(c, x):
        return c[0] + c[1]*x + c[2]*x*x

    def deriv(c, x):
        return c[1] + 2*c[2]*x

    def integ(c, x):
        return poly_int(*c, x)

    def a(eps):
        return a0 + eps*xi + 0.5*eps*eps*chi

    def I(eps):
        aa = a(eps)
        return integ(c0, aa) + eps*integ(c1, aa) + 0.5*eps*eps*integ(c2, aa)

    expected1 = integ(c1, a0) + xi*val(c0, a0)
    expected2 = (
        integ(c2, a0)
        + 2*xi*val(c1, a0)
        + chi*val(c0, a0)
        + xi*xi*deriv(c0, a0)
    )

    errs = []
    for h in (4e-4, 2e-4, 1e-4):
        fd1 = (I(h)-I(-h))/(2*h)
        fd2 = (I(h)-2*I(0.0)+I(-h))/(h*h)
        errs.append((h, abs(fd1-expected1), abs(fd2-expected2)))
        close(fd1, expected1, atol=2e-6, rtol=2e-6)
        close(fd2, expected2, atol=3e-6, rtol=3e-6)
    assert min(e1 for _, e1, _ in errs) < 2e-7, errs
    assert min(e2 for _, _, e2 in errs) < 5e-7, errs


def two_region_interface_control() -> None:
    y0 = 0.72
    L = 1.91
    xi = 0.31
    chi = -0.22

    n0 = (0.8, 0.45, 0.12)
    n1 = (-0.15, 0.33, 0.04)
    n2 = (0.21, -0.18, 0.09)
    s0 = (1.25, -0.28, 0.07)
    s1 = (0.18, 0.14, -0.05)
    s2 = (-0.12, 0.26, 0.03)

    def val(c, x):
        return c[0] + c[1]*x + c[2]*x*x

    def deriv(c, x):
        return c[1] + 2*c[2]*x

    def integ(c, a, b):
        return poly_int(*c, b)-poly_int(*c, a)

    def y(eps):
        return y0 + eps*xi + 0.5*eps*eps*chi

    def I(eps):
        yy = y(eps)
        IN = integ(n0, 0.0, yy) + eps*integ(n1, 0.0, yy) + 0.5*eps*eps*integ(n2, 0.0, yy)
        IS = integ(s0, yy, L) + eps*integ(s1, yy, L) + 0.5*eps*eps*integ(s2, yy, L)
        return IN + IS

    expected1 = (
        integ(n1, 0.0, y0)
        + integ(s1, y0, L)
        + xi*(val(n0, y0)-val(s0, y0))
    )
    expected2 = (
        integ(n2, 0.0, y0)
        + integ(s2, y0, L)
        + 2*xi*(val(n1, y0)-val(s1, y0))
        + chi*(val(n0, y0)-val(s0, y0))
        + xi*xi*(deriv(n0, y0)-deriv(s0, y0))
    )

    errs = []
    for h in (4e-4, 2e-4, 1e-4):
        fd1 = (I(h)-I(-h))/(2*h)
        fd2 = (I(h)-2*I(0.0)+I(-h))/(h*h)
        errs.append((h, abs(fd1-expected1), abs(fd2-expected2)))
        close(fd1, expected1, atol=3e-6, rtol=3e-6)
        close(fd2, expected2, atol=4e-6, rtol=4e-6)
    assert min(e1 for _, e1, _ in errs) < 3e-7, errs
    assert min(e2 for _, _, e2 in errs) < 7e-7, errs


def tangential_top_form_flux_control() -> None:
    # In 2D let omega=f dx^dy and boundary x=a with tangent t=partial_y.
    # i_t omega=-f dx, whose pullback to x=a has dx/dy=0, hence vanishes.
    f = 1.73
    tau = -0.42
    alpha_x = -tau*f
    alpha_y = 0.0
    boundary_dx_ds = 0.0
    boundary_dy_ds = 1.0
    pullback = alpha_x*boundary_dx_ds + alpha_y*boundary_dy_ds
    close(pullback, 0.0, atol=0.0, rtol=0.0)


def fixed_domain_limit_control() -> None:
    a0 = 0.63
    c1 = (0.2, -0.4, 0.1)
    c2 = (-0.3, 0.6, 0.05)
    expected1 = poly_int(*c1, a0)
    expected2 = poly_int(*c2, a0)

    def I(eps):
        return (
            poly_int(1.0, 0.2, 0.3, a0)
            + eps*poly_int(*c1, a0)
            + 0.5*eps*eps*poly_int(*c2, a0)
        )

    h = 1e-4
    fd1 = (I(h)-I(-h))/(2*h)
    fd2 = (I(h)-2*I(0.0)+I(-h))/(h*h)
    close(fd1, expected1, atol=2e-9, rtol=2e-9)
    close(fd2, expected2, atol=2e-8, rtol=2e-8)


def contract_and_firewall_control() -> None:
    d = json.loads(CONTRACT.read_text(encoding="utf-8"))
    c4b0 = json.loads(C4B0.read_text(encoding="utf-8"))
    c4a = json.loads(C4A.read_text(encoding="utf-8"))
    doc = DOC.read_text(encoding="utf-8")

    assert d["model_id"] == "HZT-M0-S6-C-PHYS-M1"
    assert d["work_package"] == "ULSH-05/WP1C4B1A"
    assert d["basis_main"] == "2dec38781b453a6688f4f5ef0be08b57943ea012"
    assert d["physical_gate_effect"] == "NONE"
    assert d["physical_evidence_effect"] == "NONE"
    assert d["solver_authorized"] is False

    transport = d["moving_domain_transport"]
    assert "L1_s+L_zs Lbar_s" in transport["first_derivative"]
    assert "L2_s+2*L_zs L1_s+(L_ws+L_zs^2)Lbar_s" in transport["second_derivative"]
    assert "2*i_zs L1_s+i_ws Lbar_s+i_zs L_zs Lbar_s" in transport["stokes_second"]
    assert d["internal_cap_first_order"]["canonical_two_side_form"] == "sum_s Xbar_s^*(i_zs Lbar_s)"
    assert d["internal_cap_first_order"]["status"] == "ORIENTATION_SAFE_MASTER_FROZEN_SCALAR_JUMP_REDUCTION_CONDITIONAL"

    g = d["gate_state"]
    expected = {
        "WP1_second_order_embedding_path_contract": "DERIVED",
        "WP1_moving_domain_transport_master": "DERIVED",
        "WP1_full_shape_residual": "NOT_ASSEMBLED",
        "WP1_configuration_space_connection": "NOT_FROZEN",
        "WP1_full_boundary_hessian": "NOT_CLOSED",
        "WP1_full_quadratic_action": "NOT_CLOSED",
        "PERTURBED_JUNCTION_SYSTEM": "NOT_RELEASED",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "FM-G0": "OPEN",
        "AuthorizationDecision": "NOT_CREATED",
        "SingleUseGrant": "NOT_CREATED",
        "BACKEND_IMPORT": "NOT_EXECUTED",
        "SOLVER_EXECUTION": "NOT_EXECUTED",
        "PHYSICAL_RESPONSE_RANK": "NOT_EXECUTED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
    }
    for key, value in expected.items():
        assert g[key] == value, (key, g[key], value)

    assert c4b0["gate_state"]["WP1_second_order_embedding_path_contract"] == "DERIVED"
    assert c4b0["gate_state"]["WP1_configuration_space_connection"] == "NOT_FROZEN"
    assert c4a["gate_state"]["WP1_two_side_bending_glue"] == "DERIVED"
    assert c4a["gate_state"]["WP1_full_boundary_hessian"] == "NOT_CLOSED"

    for sentinel in (
        "I_{1,s}",
        "I_{2,s}",
        "regional transport term != physical brane force by itself",
        "WP1_full_shape_residual = NOT_ASSEMBLED",
        "PHYSICAL_BACKGROUND = NOT_ESTABLISHED",
    ):
        assert sentinel in doc, sentinel


if __name__ == "__main__":
    single_interval_transport_control()
    two_region_interface_control()
    tangential_top_form_flux_control()
    fixed_domain_limit_control()
    contract_and_firewall_control()
    print("ULSH-05 WP1C4B1A moving-domain transport master: PASS")
