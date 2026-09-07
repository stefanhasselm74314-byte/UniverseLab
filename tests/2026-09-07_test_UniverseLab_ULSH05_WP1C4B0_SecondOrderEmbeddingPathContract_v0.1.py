#!/usr/bin/env python3
"""Independent controls for ULSH-05/WP1C4B0 second-order embedding path contract."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1C4B0_SecondOrderEmbeddingPathContract_v0.1.json"
C4A = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1C4A_GluingNormalFluxJunctions_v0.1.json"
C3 = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1C3_CapBendingJunctionGeometry_v0.1.json"
DOC = ROOT / "science/solver-hub/2026-09-07_UniverseLab_ULSH05_WP1C4B0_SecondOrderEmbeddingPathContract_v0.1.md"


def close(a: float, b: float, atol: float = 1e-7, rtol: float = 1e-7) -> None:
    assert math.isfinite(a) and math.isfinite(b), (a, b)
    assert abs(a - b) <= atol + rtol * max(abs(a), abs(b)), (a, b, abs(a-b))


def vadd(a, b):
    return [x + y for x, y in zip(a, b)]


def vsub(a, b):
    return [x - y for x, y in zip(a, b)]


def vscale(c, a):
    return [c * x for x in a]


def mmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def mvec(A, x):
    return [sum(A[i][j] * x[j] for j in range(len(x))) for i in range(len(A))]


def madd(A, B):
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


def msub(A, B):
    return [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


def vdot(A, x):
    return mvec(A, x)


def assert_vec_equal(a, b):
    assert a == b, (a, b)


def moving_scalar_pullback_control() -> None:
    x0 = 0.37
    z = -0.61
    w = 0.43

    def T0(x):
        return 1.2 + 0.7*x + 0.4*x*x + 0.1*x*x*x

    def T0p(x):
        return 0.7 + 0.8*x + 0.3*x*x

    def T0pp(x):
        return 0.8 + 0.6*x

    def T1(x):
        return -0.3 + 0.5*x - 0.2*x*x

    def T1p(x):
        return 0.5 - 0.4*x

    def T2(x):
        return 0.8 - 0.1*x

    def xeps(eps):
        return x0 + eps*z + 0.5*eps*eps*w

    def pulled(eps):
        x = xeps(eps)
        return T0(x) + eps*T1(x) + 0.5*eps*eps*T2(x)

    expected = T2(x0) + 2*z*T1p(x0) + w*T0p(x0) + z*z*T0pp(x0)
    values = []
    for h in (4e-4, 2e-4, 1e-4):
        fd2 = (pulled(h) - 2*pulled(0.0) + pulled(-h)) / (h*h)
        values.append((h, fd2, abs(fd2-expected)))
        close(fd2, expected, atol=3e-6, rtol=3e-6)
    assert min(err for _, _, err in values) < 3e-7, values


def noncommuting_second_order_gauge_control() -> None:
    # Finite-dimensional representations of Lie derivative operators.
    Z = [[0, 1, 0], [0, 0, 2], [0, 0, 0]]
    J = [[0, 0, 0], [1, 0, 0], [0, -1, 0]]
    L = [[1, 2, 0], [0, -1, 1], [2, 0, 1]]
    W = [[0, 1, -1], [2, 0, 0], [0, 1, 0]]
    T0 = [2, -1, 3]
    T1 = [1, 4, -2]
    T2 = [-3, 5, 2]

    C = msub(mmul(J, Z), mmul(Z, J))  # [L_zeta,L_z] = L_[zeta,z]
    assert C != [[0,0,0],[0,0,0],[0,0,0]]

    Q1 = vadd(T1, vdot(Z, T0))
    Q2 = vadd(vadd(T2, vscale(2, vdot(Z, T1))), vdot(madd(W, mmul(Z, Z)), T0))

    T1p = vsub(T1, vdot(J, T0))
    T2p = vadd(vsub(T2, vscale(2, vdot(J, T1))), vdot(msub(mmul(J, J), L), T0))
    Zp = madd(Z, J)
    Wp = msub(madd(W, L), C)

    Q1p = vadd(T1p, vdot(Zp, T0))
    Q2p = vadd(vadd(T2p, vscale(2, vdot(Zp, T1p))), vdot(madd(Wp, mmul(Zp, Zp)), T0))

    assert_vec_equal(Q1p, Q1)
    assert_vec_equal(Q2p, Q2)

    # Omitting the commutator must fail for this non-commuting control.
    Wwrong = madd(W, L)
    Q2wrong = vadd(vadd(T2p, vscale(2, vdot(Zp, T1p))), vdot(madd(Wwrong, mmul(Zp, Zp)), T0))
    assert Q2wrong != Q2


def off_shell_path_dependence_control() -> None:
    # This control is intentionally performed in one declared affine chart.
    x0 = 0.41
    u = -0.73
    v1 = 0.28
    v2 = -0.64

    def S(x):
        return 0.9 + 1.7*x + 0.5*2.3*x*x + (0.4/6.0)*x*x*x

    def DS(x):
        return 1.7 + 2.3*x + 0.2*x*x

    def D2S(x):
        return 2.3 + 0.4*x

    def path(eps, v):
        return x0 + eps*u + 0.5*eps*eps*v

    def fd2(v, h=1e-4):
        return (S(path(h, v)) - 2*S(path(0.0, v)) + S(path(-h, v))) / (h*h)

    d1 = fd2(v1)
    d2 = fd2(v2)
    expected1 = D2S(x0)*u*u + DS(x0)*v1
    expected2 = D2S(x0)*u*u + DS(x0)*v2
    close(d1, expected1, atol=3e-7, rtol=3e-7)
    close(d2, expected2, atol=3e-7, rtol=3e-7)
    close(d1-d2, DS(x0)*(v1-v2), atol=5e-7, rtol=5e-7)

    chart_hess1 = 0.5*(d1-DS(x0)*v1)
    chart_hess2 = 0.5*(d2-DS(x0)*v2)
    chart_hess_expected = 0.5*D2S(x0)*u*u
    close(chart_hess1, chart_hess_expected, atol=3e-7, rtol=3e-7)
    close(chart_hess2, chart_hess_expected, atol=3e-7, rtol=3e-7)
    assert abs(DS(x0)) > 0.1  # genuinely off shell control


def two_side_second_order_gluing_control() -> None:
    rhoN = 1.3
    rhoS = 2.1
    xi = 0.27
    chi = -0.44

    def y(eps):
        return eps*xi + 0.5*eps*eps*chi

    def rN(eps):
        return rhoN + y(eps)

    def rS(eps):
        return rhoS - y(eps)

    h = 2e-4
    dN = (rN(h)-rN(-h))/(2*h)
    dS = (rS(h)-rS(-h))/(2*h)
    ddN = (rN(h)-2*rN(0)+rN(-h))/(h*h)
    ddS = (rS(h)-2*rS(0)+rS(-h))/(h*h)
    close(dN, xi, atol=1e-9, rtol=1e-9)
    close(dS, -xi, atol=1e-9, rtol=1e-9)
    close(ddN, chi, atol=2e-8, rtol=2e-8)
    close(ddS, -chi, atol=2e-8, rtol=2e-8)
    close(dN+dS, 0.0, atol=1e-10, rtol=0.0)
    close(ddN+ddS, 0.0, atol=3e-8, rtol=0.0)


def contract_and_firewall_control() -> None:
    d = json.loads(CONTRACT.read_text(encoding="utf-8"))
    c4a = json.loads(C4A.read_text(encoding="utf-8"))
    c3 = json.loads(C3.read_text(encoding="utf-8"))
    doc = DOC.read_text(encoding="utf-8")

    assert d["model_id"] == "HZT-M0-S6-C-PHYS-M1"
    assert d["work_package"] == "ULSH-05/WP1C4B0"
    assert d["basis_main"] == "fa8749bb87351c7057fb37db6129c3819a4b6ad7"
    assert d["physical_gate_effect"] == "NONE"
    assert d["physical_evidence_effect"] == "NONE"
    assert d["solver_authorized"] is False
    assert d["second_order_field_path"]["configuration_chart"] == "DECLARED_LOCAL_AFFINE_PERTURBATION_CHART_FOR_THIS_PREFLIGHT"
    assert d["second_order_field_path"]["field_space_connection_status"] == "NOT_FROZEN"
    assert "T2+2*L_z T1+(L_w+L_z^2)Tbar" in d["moving_pullback_second_order"]["second_order"]
    assert "w+lambda-[zeta,z]" in d["second_order_bulk_D_gauge"]["embedding_second"]
    extraction = d["off_shell_hessian_extraction"]
    assert "DS[v]" in extraction["path_second_derivative"]
    assert extraction["field_space_connection_status"] == "NOT_FROZEN"
    assert "declared local affine perturbation chart" in extraction["chart_scope"]
    assert "nabla_cfg" in extraction["covariant_field_space_identity"]
    assert d["two_side_second_order_gluing"]["equivalent_second_constraint"] == "chi_N+chi_S=0"

    g = d["gate_state"]
    expected = {
        "WP1_second_order_embedding_path_contract": "DERIVED",
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

    assert c4a["gate_state"]["WP1_two_side_bending_glue"] == "DERIVED"
    assert c4a["gate_state"]["WP1_full_boundary_hessian"] == "NOT_CLOSED"
    assert c3["gate_state"]["WP1_moving_interface_linear_geometry"] == "DERIVED_PREFLIGHT"
    assert c3["gate_state"]["PERTURBED_JUNCTION_SYSTEM"] == "NOT_RELEASED"

    for sentinel in (
        "DS[v]",
        "Q_2'=Q_2",
        "Konfigurationsraum-Verbindung",
        "global feldraum-kovariante off-shell Hesse",
        "PHYSICAL_BACKGROUND = NOT_ESTABLISHED",
        "WP1_full_boundary_hessian = NOT_CLOSED",
    ):
        assert sentinel in doc, sentinel


if __name__ == "__main__":
    moving_scalar_pullback_control()
    noncommuting_second_order_gauge_control()
    off_shell_path_dependence_control()
    two_side_second_order_gluing_control()
    contract_and_firewall_control()
    print("ULSH-05 WP1C4B0 second-order embedding/path contract: PASS")
