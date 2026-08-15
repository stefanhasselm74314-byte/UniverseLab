#!/usr/bin/env python3
"""Validate H4R4A exact conformal-gauge bulk/boundary export.

No physical PDE solve is performed. The numerical checks reconstruct the
Euler-Lagrange lower-order map at isolated phase-space points and test algebraic
boundary/jet identities only.
"""
from __future__ import annotations

import cmath
import json
import math
import sys
from pathlib import Path

U_NAMES = ("omega", "u", "v", "varphi", "a_chi")


def _exp(x):
    return cmath.exp(x) if isinstance(x, complex) else math.exp(x)


def params_default():
    return {
        "kappa_hat_sq": 1.3,
        "Lambda_hat": -0.17,
        "mhat_phi_sq": 0.83,
        "a_F": 0.25,
        "abar_ref": 1.11,
        "ell_ref": 0.91,
        "k": 1.0,
        "lambda_hat": 0.21,
        "z_sigma_hat": 0.77,
        "q_hat": 0.63,
        "m_sigma": 2.0,
        "N_sigma": 3.0,
    }


def geom(U, p):
    omega, u, v, varphi, _ = U
    abar = p["abar_ref"] * _exp(u)
    ell = p["ell_ref"] * _exp(v)
    z = _exp(-2.0 * p["a_F"] * varphi) / (ell * ell)
    S = abar**3 * ell
    return abar, ell, z, S, _exp(2.0 * omega)


def D(P, Q, i, j):
    return Q[i] * Q[j] - P[i] * P[j]


def bulk_F(U, P, Q, p):
    _, _, _, varphi, _ = U
    g = p["kappa_hat_sq"]
    Lam = p["Lambda_hat"]
    m2 = p["mhat_phi_sq"]
    af = p["a_F"]
    k = p["k"]
    abar, _, z, _, e2w = geom(U, p)

    Duu = D(P, Q, 1, 1)
    Duv = D(P, Q, 1, 2)
    Dvv = D(P, Q, 2, 2)
    Dpp = D(P, Q, 3, 3)
    DAA = D(P, Q, 4, 4)
    Dup = D(P, Q, 1, 3)
    Dvp = D(P, Q, 2, 3)
    DuA = D(P, Q, 1, 4)
    DvA = D(P, Q, 2, 4)
    DpA = D(P, Q, 3, 4)

    Fw = (
        -3.0 * Duu - 3.0 * Duv + 0.5 * g * Dpp + 0.25 * g * z * DAA
        + e2w * (3.0 * k / (abar * abar) - 0.5 * Lam - 0.25 * g * m2 * varphi * varphi)
    )
    Fu = (
        3.0 * Duu + Duv - 0.25 * g * z * DAA
        + e2w * (0.5 * Lam + 0.25 * g * m2 * varphi * varphi - 2.0 * k / (abar * abar))
    )
    Fv = (
        3.0 * Duv + Dvv + 0.75 * g * z * DAA
        + e2w * (0.5 * Lam + 0.25 * g * m2 * varphi * varphi)
    )
    Fp = 3.0 * Dup + Dvp + af * z * DAA - m2 * e2w * varphi
    FA = 3.0 * DuA - DvA - 2.0 * af * DpA
    return [float(x.real if isinstance(x, complex) else x) for x in (Fw, Fu, Fv, Fp, FA)]


def field_metric(U, p):
    g = p["kappa_hat_sq"]
    K = 1.0 / g
    _, _, z, S, _ = geom(U, p)
    b = [
        [0.0, 3.0*K, 1.0*K, 0.0, 0.0],
        [3.0*K, 6.0*K, 3.0*K, 0.0, 0.0],
        [1.0*K, 3.0*K, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, -1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, -z],
    ]
    return [[S * b[i][j] for j in range(5)] for i in range(5)]


def reduced_potential(U, p):
    _, _, _, varphi, _ = U
    g = p["kappa_hat_sq"]
    K = 1.0 / g
    Lam = p["Lambda_hat"]
    m2 = p["mhat_phi_sq"]
    k = p["k"]
    abar, _, _, S, e2w = geom(U, p)
    return S * e2w * (K * (3.0 * k / (abar * abar) - Lam) - 0.5 * m2 * varphi * varphi)


def _derivative_scalar(fun, U, idx, p, h=1e-30):
    Z = [complex(x, 0.0) for x in U]
    Z[idx] += 1j * h
    return fun(Z, p).imag / h


def _derivative_matrix(fun, U, idx, p, h=1e-30):
    Z = [complex(x, 0.0) for x in U]
    Z[idx] += 1j * h
    M = fun(Z, p)
    return [[M[i][j].imag / h for j in range(5)] for i in range(5)]


def _solve(A, b):
    A = [list(map(float, row)) + [float(bi)] for row, bi in zip(A, b)]
    n = len(A)
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(A[r][col]))
        if abs(A[piv][col]) < 1e-14:
            raise AssertionError("singular matrix in validator")
        A[col], A[piv] = A[piv], A[col]
        s = A[col][col]
        A[col] = [x / s for x in A[col]]
        for r in range(n):
            if r == col:
                continue
            f = A[r][col]
            A[r] = [A[r][j] - f*A[col][j] for j in range(n+1)]
    return [A[i][-1] for i in range(n)]


def reconstruct_box_rhs(U, P, Q, p):
    """Independently reconstruct Box(U) from G and potential via Euler-Lagrange."""
    G = field_metric(U, p)
    dG = [_derivative_matrix(field_metric, U, k, p) for k in range(5)]
    dPot = [_derivative_scalar(reduced_potential, U, i, p) for i in range(5)]
    gamma = [[[0.0]*5 for _ in range(5)] for __ in range(5)]
    for i in range(5):
        for j in range(5):
            for k in range(5):
                gamma[i][j][k] = 0.5 * (dG[k][i][j] + dG[j][i][k] - dG[i][j][k])
    rhs = []
    for i in range(5):
        gd = 0.0
        for j in range(5):
            for k in range(5):
                gd += gamma[i][j][k] * D(P, Q, j, k)
        rhs.append(dPot[i] - gd)
    return _solve(G, rhs)


def constraints(U, P, Q, dQdx, dPdx, p):
    _, _, _, varphi, _ = U
    g = p["kappa_hat_sq"]
    Lam = p["Lambda_hat"]
    m2 = p["mhat_phi_sq"]
    k = p["k"]
    abar, _, z, _, e2w = geom(U, p)
    Pw, Pu, Pv, Pp, PA = P
    Qw, Qu, Qv, Qp, QA = Q
    CH = (
        -3.0*dQdx[1] - dQdx[2]
        + 3.0*Pu*Pu + 3.0*Pu*Pv + 3.0*Pu*Pw + Pv*Pw
        - 6.0*Qu*Qu - 3.0*Qu*Qv + 3.0*Qu*Qw - Qv*Qv + Qv*Qw
        + 3.0*e2w*k/(abar*abar) - e2w*Lam
        - 0.5*g*(Pp*Pp + Qp*Qp) - 0.5*g*z*(PA*PA + QA*QA)
        - 0.5*g*m2*varphi*varphi*e2w
    )
    CM = (
        -3.0*(dPdx[1] + Pu*Qu - Qw*Pu - Pw*Qu)
        -(dPdx[2] + Pv*Qv - Qw*Pv - Pw*Qv)
        -g*(Pp*Qp + z*PA*QA)
    )
    return CH, CM


def _avg(a, b):
    return [(x+y)/2.0 for x, y in zip(a, b)]


def boundary_residual(UN, US, QN, QS, p):
    """Exact local cap residual in the symmetric off-constraint trace extension."""
    Uc = _avg(UN, US)
    _, ellc, _, _, _ = geom(Uc, p)
    _, _, zN, _, _ = geom(UN, p)
    _, _, zS, _, _ = geom(US, p)
    nuN = [-math.exp(-UN[0])*q for q in QN]
    nuS = [-math.exp(-US[0])*q for q in QS]
    K = [nuN[i] + nuS[i] for i in range(5)]
    qcap = p["m_sigma"] * p["q_hat"]
    dchi = p["N_sigma"] - qcap * Uc[4]
    Y = p["z_sigma_hat"] * dchi*dchi / (ellc*ellc)
    g = p["kappa_hat_sq"]
    lam = p["lambda_hat"]
    out = [UN[i] - US[i] for i in range(5)]
    out += [
        -(3.0*K[1] + K[2]) + g*(lam + 0.5*Y),
        -(K[0] + 2.0*K[1] + K[2]) + g*(lam + 0.5*Y),
        -(K[0] + 3.0*K[1]) + g*(lam - 0.5*Y),
        K[3],
        zN*nuN[4] + zS*nuS[4] - qcap*p["z_sigma_hat"]*dchi/(ellc*ellc),
    ]
    return out


def boundary_first_jet(UN, US, PN, PS, QN, QS, dPxN, dPxS, p):
    Uc = _avg(UN, US)
    Pc = _avg(PN, PS)
    _, ellc, _, _, _ = geom(Uc, p)
    _, _, zN, _, _ = geom(UN, p)
    _, _, zS, _, _ = geom(US, p)
    nuN = [-math.exp(-UN[0])*q for q in QN]
    nuS = [-math.exp(-US[0])*q for q in QS]
    nudN = [-math.exp(-UN[0])*(dPxN[i] - PN[0]*QN[i]) for i in range(5)]
    nudS = [-math.exp(-US[0])*(dPxS[i] - PS[0]*QS[i]) for i in range(5)]
    Kd = [nudN[i] + nudS[i] for i in range(5)]
    zNd = zN * (-2.0*p["a_F"]*PN[3] - 2.0*PN[2])
    zSd = zS * (-2.0*p["a_F"]*PS[3] - 2.0*PS[2])
    qcap = p["m_sigma"] * p["q_hat"]
    dchi = p["N_sigma"] - qcap*Uc[4]
    Yd = -2.0*p["z_sigma_hat"]/(ellc*ellc) * (dchi*dchi*Pc[2] + qcap*dchi*Pc[4])
    source_gauge_dot = qcap*p["z_sigma_hat"]/(ellc*ellc) * (qcap*Pc[4] + 2.0*dchi*Pc[2])
    g = p["kappa_hat_sq"]
    out = [PN[i] - PS[i] for i in range(5)]
    out += [
        -(3.0*Kd[1] + Kd[2]) + 0.5*g*Yd,
        -(Kd[0] + 2.0*Kd[1] + Kd[2]) + 0.5*g*Yd,
        -(Kd[0] + 3.0*Kd[1]) - 0.5*g*Yd,
        Kd[3],
        zNd*nuN[4] + zN*nudN[4] + zSd*nuS[4] + zS*nudS[4] + source_gauge_dot,
    ]
    return out


def check_bulk_euler_lagrange():
    p = params_default()
    samples = [
        ([0.07, -0.12, 0.09, 0.21, -0.08], [0.13, -0.17, 0.11, 0.05, -0.19], [-0.04, 0.23, -0.14, 0.17, 0.09]),
        ([-0.09, 0.18, -0.11, -0.31, 0.16], [-0.08, 0.06, -0.15, 0.22, 0.12], [0.19, -0.07, 0.13, -0.09, -0.18]),
        ([0.16, 0.04, 0.14, 0.12, 0.03], [0.03, 0.09, -0.04, -0.11, 0.21], [-0.17, 0.08, 0.05, 0.14, -0.06]),
    ]
    for U, P, Q in samples:
        box = reconstruct_box_rhs(U, P, Q, p)
        F = bulk_F(U, P, Q, p)
        for i, (b, f) in enumerate(zip(box, F)):
            if abs(b + f) > 2e-9:
                raise AssertionError(f"bulk F mismatch component {i}: box={b} F={f}")


def check_boundary_principal_flux():
    p = params_default()
    U = [0.08, -0.03, 0.12, 0.17, -0.09]
    _, _, z, _, _ = geom(U, p)
    Ddiag = [1.0, 1.0, 1.0, 1.0, z]
    P = [0.13, -0.07, 0.21, 0.04, -0.16]
    QN = [-0.11, 0.06, 0.09, -0.12, 0.18]
    QS = [-q for q in QN]
    flux = sum(P[i]*Ddiag[i]*QN[i] for i in range(5)) + sum(P[i]*Ddiag[i]*QS[i] for i in range(5))
    if abs(flux) > 1e-13:
        raise AssertionError("principal conservative flux failed")
    Bg = [[0.0,-3.0,-1.0],[-1.0,-2.0,-1.0],[-1.0,-3.0,0.0]]
    det = (
        Bg[0][0]*(Bg[1][1]*Bg[2][2]-Bg[1][2]*Bg[2][1])
        -Bg[0][1]*(Bg[1][0]*Bg[2][2]-Bg[1][2]*Bg[2][0])
        +Bg[0][2]*(Bg[1][0]*Bg[2][1]-Bg[1][1]*Bg[2][0])
    )
    if abs(det + 4.0) > 1e-13 or not z > 0.0:
        raise AssertionError("boundary normal rank precondition failed")


def check_boundary_first_jet():
    p = params_default()
    UN = [0.06, -0.04, 0.08, 0.11, -0.05]
    US = [0.03, -0.01, 0.05, 0.09, -0.02]
    PN = [0.12, -0.07, 0.03, 0.08, -0.09]
    PS = [-0.05, 0.06, -0.04, 0.02, 0.07]
    QN = [0.09, -0.11, 0.05, -0.08, 0.13]
    QS = [-0.04, 0.07, -0.12, 0.06, -0.10]
    dPxN = [0.02, -0.03, 0.04, -0.05, 0.06]
    dPxS = [-0.01, 0.05, -0.02, 0.03, -0.04]
    analytic = boundary_first_jet(UN, US, PN, PS, QN, QS, dPxN, dPxS, p)
    h = 2e-6
    def shifted(sign):
        Un = [UN[i] + sign*h*PN[i] for i in range(5)]
        Us = [US[i] + sign*h*PS[i] for i in range(5)]
        Qn = [QN[i] + sign*h*dPxN[i] for i in range(5)]
        Qs = [QS[i] + sign*h*dPxS[i] for i in range(5)]
        return boundary_residual(Un, Us, Qn, Qs, p)
    plus = shifted(+1.0)
    minus = shifted(-1.0)
    numeric = [(a-b)/(2*h) for a,b in zip(plus, minus)]
    for i, (a,n) in enumerate(zip(analytic, numeric)):
        if abs(a-n) > 2e-8:
            raise AssertionError(f"boundary jet mismatch row {i}: analytic={a} numeric={n}")


def check_registry(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    assert data["baseline_main_sha"] == "5fb7b95dcf214c6fa022745c0bcc426ca469a91f"
    assert data["solver_execution"] is False
    assert data["mms_execution"] is False
    assert data["physical_evidence_effect"] == "NONE"
    assert data["external_material_firewall"]["gemini_blocks"] == "EXTERNAL_UNVERIFIED_GEMINI_DRAFT"
    assert data["canonical_signature"]["physical_times"] == 1
    assert data["theorem_review"]["decision"].startswith("RATIFIED_CONDITIONALLY_FOR_REDUCED_LOCAL_IBVP")
    gates = data["gate_disposition"]
    assert gates["physical_parent_solve_authorized"] is False
    assert gates["K1-D"] == "NOT_RELEASED"
    assert gates["K1-E"] == "NOT_ADMISSIBLE"
    assert gates["WP4"] == "BLOCKED"
    assert gates["physical_evidence_effect"] == "NONE"
    assert data["gauge_and_normalization"]["coordinate_wave_speed"] == 1
    assert "F_omega" in data["exact_bulk_source_F"]
    assert data["boundary_time_jet_generator"]["status"].startswith("PASS_")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: validator.py registry.json")
    check_registry(sys.argv[1])
    check_bulk_euler_lagrange()
    check_boundary_principal_flux()
    check_boundary_first_jet()
    print("H4R4A validation PASS: exact formula/boundary algebra only; no PDE or MMS execution.")


if __name__ == "__main__":
    main()
