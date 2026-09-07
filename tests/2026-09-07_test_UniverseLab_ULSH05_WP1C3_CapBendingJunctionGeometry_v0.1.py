#!/usr/bin/env python3
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1C3_CapBendingJunctionGeometry_v0.1.json"
WP1C2 = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1C2_FixedInterfaceCapHessian_v0.1.json"
G01 = ROOT / "registry/2026-09-07_UniverseLab_BandVC_G01_PerturbationObservableInventory_v1.0.json"
D = 5


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def zeros():
    return [[0.0] * D for _ in range(D)]


def madd(A, B, a=1.0, b=1.0):
    return [[a*A[i][j] + b*B[i][j] for j in range(D)] for i in range(D)]


def scale(a, A):
    return [[a*x for x in row] for row in A]


def mm(A, B):
    return [[sum(A[i][k]*B[k][j] for k in range(D)) for j in range(D)] for i in range(D)]


def inv(A):
    M = [list(map(float, row)) + [1.0 if i == j else 0.0 for j in range(D)] for i, row in enumerate(A)]
    for c in range(D):
        p = max(range(c, D), key=lambda r: abs(M[r][c]))
        assert abs(M[p][c]) > 1e-14
        if p != c:
            M[c], M[p] = M[p], M[c]
        q = M[c][c]
        M[c] = [x/q for x in M[c]]
        for r in range(D):
            if r == c:
                continue
            f = M[r][c]
            M[r] = [M[r][j] - f*M[c][j] for j in range(2*D)]
    return [row[D:] for row in M]


def raise2(T, hi):
    return mm(mm(hi, T), hi)


def contract(A, B):
    return sum(A[i][j]*B[i][j] for i in range(D) for j in range(D))


def trace_with_inverse(hi, T):
    return sum(hi[i][j]*T[j][i] for i in range(D) for j in range(D))


def maxdiff(A, B):
    return max(abs(A[i][j]-B[i][j]) for i in range(D) for j in range(D))


def fd_matrix(fn, eps=1e-6):
    P, M = fn(+eps), fn(-eps)
    return [[(P[i][j]-M[i][j])/(2*eps) for j in range(D)] for i in range(D)]


def test_contract_scope():
    c = load(REG)
    assert c["model_id"] == "HZT-M0-S6-C-PHYS-M1"
    assert c["work_package"] == "ULSH-05/WP1C3"
    assert c["classification"] == "NONOPERATIVE_ANALYTIC_GEOMETRY_PREFLIGHT"
    assert c["status"] == "DERIVED_DOUBLY_COVARIANT_LINEAR_MOVING_INTERFACE_GEOMETRY_PREFLIGHT_FULL_PERTURBED_JUNCTION_AND_BOUNDARY_HESSIAN_OPEN"
    assert c["external_mathematical_crosscheck"]["status"] == "REFERENCE_ONLY_NOT_PROJECT_AUTHORITY"
    assert c["physical_gate_effect"] == "NONE"
    assert c["physical_evidence_effect"] == "NONE"
    assert c["solver_authorized"] is False


def test_induced_metric_D_gauge_invariance():
    K = [[0.12,0.01,0,0.02,-0.01],[0.01,-0.08,0.03,0,0.01],[0,0.03,0.05,-0.02,0],[0.02,0,-0.02,0.09,0.04],[-0.01,0.01,0,0.04,0.07]]
    p = [[0.07,-0.02,0.01,0,0.03],[-0.02,0.05,0,0.01,-0.01],[0.01,0,-0.04,0.02,0],[0,0.01,0.02,0.03,-0.02],[0.03,-0.01,0,-0.02,0.06]]
    S = [[0.03,0.01,-0.02,0,0.01],[0.01,-0.02,0,0.02,0],[-0.02,0,0.04,0.01,-0.01],[0,0.02,0.01,-0.01,0.03],[0.01,0,-0.01,0.03,0.02]]
    G = [[-0.02,0.03,0,-0.01,0.02],[0.03,0.01,-0.02,0,0],[0,-0.02,0.02,0.01,0.03],[-0.01,0,0.01,-0.03,0.01],[0.02,0,0.03,0.01,0]]
    xi, zn = 0.37, -0.21
    H = madd(madd(p, scale(2*xi, K)), S)
    p2 = madd(p, madd(G, scale(2*zn, K)), 1, -1)
    H2 = madd(madd(p2, scale(2*(xi+zn), K)), madd(S, G))
    assert maxdiff(H, H2) < 2e-15


def test_flat_graph_bending_sign():
    Hess = [[0.40,-0.10,0,0.05,0],[-0.10,-0.30,0.07,0,0.02],[0,0.07,0.25,-0.04,0],[0.05,0,-0.04,0.18,0.03],[0,0.02,0,0.03,-0.12]]
    got = fd_matrix(lambda e: scale(-e, Hess), 1e-6)
    assert maxdiff(got, scale(-1, Hess)) < 2e-11


def test_warped_parallel_shift_signs():
    eta = zeros()
    for i, v in enumerate((-1.0,1.0,1.0,1.0,1.0)):
        eta[i][i] = v
    c, xi = 0.43, -0.27
    h = lambda e: scale(math.exp(2*c*e*xi), eta)
    K = lambda e: scale(c*math.exp(2*c*e*xi), eta)
    assert maxdiff(fd_matrix(h,2e-6), scale(2*xi*c, eta)) < 2e-10
    assert maxdiff(fd_matrix(K,2e-6), scale(2*c*c*xi, eta)) < 2e-10


def israel_operator(h, K):
    hi = inv(h)
    return madd(K, scale(trace_with_inverse(hi, K), h), 1, -1)


def test_perturbed_israel_operator_finite_difference():
    h = [[-1,0.02,0,0,0],[0.02,1.2,0.01,0,0],[0,0.01,0.9,-0.02,0],[0,0,-0.02,1.35,0.03],[0,0,0,0.03,2.1]]
    H = [[0.04,-0.01,0.02,0,0],[-0.01,-0.03,0,0.01,0],[0.02,0,0.05,-0.02,0.01],[0,0.01,-0.02,0.02,-0.01],[0,0,0.01,-0.01,0.06]]
    K = [[0.10,0.01,0,0.02,0],[0.01,-0.06,0.03,0,0.01],[0,0.03,0.08,-0.01,0],[0.02,0,-0.01,0.04,0.02],[0,0.01,0,0.02,0.07]]
    dK = [[-0.02,0.01,0,0,0.01],[0.01,0.03,-0.01,0.02,0],[0,-0.01,0.02,0,-0.02],[0,0.02,0,-0.04,0.01],[0.01,0,-0.02,0.01,0.05]]
    hi = inv(h)
    Ktr = trace_with_inverse(hi, K)
    dKtr = trace_with_inverse(hi, dK)
    KupH = contract(raise2(K, hi), H)
    analytic = madd(madd(dK, scale(dKtr, h), 1, -1), madd(scale(KupH, h), scale(Ktr, H), 1, -1))
    exact = lambda e: israel_operator(madd(h,H,1,e), madd(K,dK,1,e))
    assert maxdiff(fd_matrix(exact,2e-6), analytic) < 2e-9


def surface_stress(h, w, lam, z):
    hi = inv(h)
    X = sum(hi[i][j]*w[i]*w[j] for i in range(D) for j in range(D))
    S = scale(-(lam+0.5*z*X), h)
    for i in range(D):
        for j in range(D):
            S[i][j] += z*w[i]*w[j]
    return S


def test_surface_stress_variation_finite_difference():
    h = zeros()
    for i, v in enumerate((-1.0,1.1,0.8,1.4,2.2)):
        h[i][i] = v
    H = [[0.03,0.01,0,-0.01,0],[0.01,-0.02,0.02,0,0.01],[0,0.02,0.04,0.01,0],[-0.01,0,0.01,-0.03,0.02],[0,0.01,0,0.02,0.05]]
    w, dw = [0.11,-0.20,0.07,0.16,0.52], [-0.03,0.05,0.02,-0.01,0.09]
    lam, z = 0.72, 1.37
    hi = inv(h)
    wup = [sum(hi[i][j]*w[j] for j in range(D)) for i in range(D)]
    X = sum(wup[i]*w[i] for i in range(D))
    Hup = raise2(H, hi)
    dX = 2*sum(wup[i]*dw[i] for i in range(D))-sum(Hup[i][j]*w[i]*w[j] for i in range(D) for j in range(D))
    analytic = madd(scale(-0.5*z*dX,h), scale(-(lam+0.5*z*X),H))
    mix = zeros()
    for i in range(D):
        for j in range(D):
            mix[i][j] = z*(dw[i]*w[j]+w[i]*dw[j])
    analytic = madd(analytic, mix)
    exact = lambda e: surface_stress(madd(h,H,1,e), [w[i]+e*dw[i] for i in range(D)], lam, z)
    assert maxdiff(fd_matrix(exact,2e-6), analytic) < 2e-9


def test_moving_pullback_u1_invariance():
    q = 1.7
    s = [0.20,-0.11,0.04,0.07,-0.16]
    a = [-0.05,0.03,0.08,-0.02,0.10]
    alpha = [0.04,-0.03,0.02,0.01,-0.05]
    d0 = [s[i]-q*a[i] for i in range(D)]
    d1 = [(s[i]+q*alpha[i])-q*(a[i]+alpha[i]) for i in range(D)]
    assert max(abs(d0[i]-d1[i]) for i in range(D)) < 2e-15


def test_gluing_and_global_fixed_interface_gauge_remain_open():
    c = load(REG)
    assert c["two_side_bending_gluing"]["normal_displacement_gluing_relation"] == "OPEN_REQUIRES_EXPLICIT_INTERFACE_IDENTIFICATION_MAP"
    assert c["fixed_interface_gauge_admissibility"]["status"] == "LOCALLY_AVAILABLE_CONDITIONALLY_GLOBAL_ADMISSIBILITY_NOT_PROVEN"
    assert c["gate_state"]["PERTURBED_JUNCTION_SYSTEM"] == "NOT_RELEASED"
    assert c["gate_state"]["WP1_full_boundary_hessian"] == "NOT_CLOSED"
    assert c["gate_state"]["WP1_full_quadratic_action"] == "NOT_CLOSED"


def test_upstream_G01_and_physical_firewalls():
    c2, c3, g01 = load(WP1C2), load(REG), load(G01)
    assert c2["gate_state"]["WP1_fixed_interface_localized_cap_hessian"] == "DERIVED"
    assert c2["gate_state"]["FM-G0"] == "OPEN"
    assert g01["gap_status_after_inventory"].startswith("OPEN_BLOCKING")
    assert g01["crosswalk_state"]["equation_or_derivation"] == "MISSING_REQUIRED_LINK"
    assert g01["unchanged_firewalls"]["FM-G0"] == "OPEN"
    expected = {
        "PHYSICAL_BACKGROUND":"NOT_ESTABLISHED",
        "FM-G0":"OPEN",
        "AuthorizationDecision":"NOT_CREATED",
        "SingleUseGrant":"NOT_CREATED",
        "BACKEND_IMPORT":"NOT_EXECUTED",
        "SOLVER_EXECUTION":"NOT_EXECUTED",
        "PHYSICAL_RESPONSE_RANK":"NOT_EXECUTED",
        "K1-D":"NOT_RELEASED",
        "K1-E":"NOT_ADMISSIBLE",
    }
    for k, v in expected.items():
        assert c3["gate_state"][k] == v, (k,c3["gate_state"].get(k),v)
    assert c3["physical_gate_effect"] == "NONE"
    assert c3["physical_evidence_effect"] == "NONE"
    assert c3["solver_authorized"] is False


def main():
    tests = [
        test_contract_scope,
        test_induced_metric_D_gauge_invariance,
        test_flat_graph_bending_sign,
        test_warped_parallel_shift_signs,
        test_perturbed_israel_operator_finite_difference,
        test_surface_stress_variation_finite_difference,
        test_moving_pullback_u1_invariance,
        test_gluing_and_global_fixed_interface_gauge_remain_open,
        test_upstream_G01_and_physical_firewalls,
    ]
    for fn in tests:
        fn()
        print(f"PASS: {fn.__name__}")
    print("PASS: ULSH-05 WP1C3 cap bending / perturbed junction geometry preflight v0.1")


if __name__ == "__main__":
    main()
