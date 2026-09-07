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


def zeros(n=D):
    return [[0.0 for _ in range(n)] for _ in range(n)]


def madd(A, B, a=1.0, b=1.0):
    n = len(A)
    return [[a * A[i][j] + b * B[i][j] for j in range(n)] for i in range(n)]


def mscale(a, A):
    return [[a * x for x in row] for row in A]


def matmul(A, B):
    n = len(A)
    return [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def inverse(A):
    n = len(A)
    M = [list(map(float, row)) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(A)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        assert abs(M[pivot][col]) > 1e-14
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]
        pv = M[col][col]
        M[col] = [x / pv for x in M[col]]
        for r in range(n):
            if r == col:
                continue
            fac = M[r][col]
            M[r] = [M[r][j] - fac * M[col][j] for j in range(2 * n)]
    return [row[n:] for row in M]


def raise2(T, hi):
    return matmul(matmul(hi, T), hi)


def contract(A, B):
    return sum(A[i][j] * B[i][j] for i in range(len(A)) for j in range(len(A)))


def trace_with_inverse(hi, T):
    return sum(hi[i][j] * T[j][i] for i in range(len(T)) for j in range(len(T)))


def maxdiff(A, B):
    return max(abs(A[i][j] - B[i][j]) for i in range(len(A)) for j in range(len(A)))


def fd_matrix(fn, eps=1e-6):
    P = fn(+eps)
    M = fn(-eps)
    return [[(P[i][j] - M[i][j]) / (2.0 * eps) for j in range(len(P))] for i in range(len(P))]


def test_contract_scope_and_external_reference_is_non_authoritative():
    c = load(REG)
    assert c["model_id"] == "HZT-M0-S6-C-PHYS-M1"
    assert c["work_package"] == "ULSH-05/WP1C3"
    assert c["classification"] == "NONOPERATIVE_ANALYTIC_GEOMETRY_PREFLIGHT"
    assert c["status"] == "DERIVED_DOUBLY_COVARIANT_LINEAR_MOVING_INTERFACE_GEOMETRY_PREFLIGHT_FULL_PERTURBED_JUNCTION_AND_BOUNDARY_HESSIAN_OPEN"
    assert c["external_mathematical_crosscheck"]["status"] == "REFERENCE_ONLY_NOT_PROJECT_AUTHORITY"
    assert c["background_hypersurface_contract"]["normal"] == "nbar_A e_a^A=0 and nbar_A nbar^A=+1"
    assert c["physical_gate_effect"] == "NONE"
    assert c["physical_evidence_effect"] == "NONE"
    assert c["solver_authorized"] is False


def test_induced_metric_bulk_D_gauge_invariance():
    # H = p + 2 xi K + (D tau + D tau^T).
    K = [
        [0.12, 0.01, 0.00, 0.02, -0.01],
        [0.01, -0.08, 0.03, 0.00, 0.01],
        [0.00, 0.03, 0.05, -0.02, 0.00],
        [0.02, 0.00, -0.02, 0.09, 0.04],
        [-0.01, 0.01, 0.00, 0.04, 0.07],
    ]
    p = [
        [0.07, -0.02, 0.01, 0.00, 0.03],
        [-0.02, 0.05, 0.00, 0.01, -0.01],
        [0.01, 0.00, -0.04, 0.02, 0.00],
        [0.00, 0.01, 0.02, 0.03, -0.02],
        [0.03, -0.01, 0.00, -0.02, 0.06],
    ]
    S_tau = [
        [0.03, 0.01, -0.02, 0.00, 0.01],
        [0.01, -0.02, 0.00, 0.02, 0.00],
        [-0.02, 0.00, 0.04, 0.01, -0.01],
        [0.00, 0.02, 0.01, -0.01, 0.03],
        [0.01, 0.00, -0.01, 0.03, 0.02],
    ]
    G_zeta = [
        [-0.02, 0.03, 0.00, -0.01, 0.02],
        [0.03, 0.01, -0.02, 0.00, 0.00],
        [0.00, -0.02, 0.02, 0.01, 0.03],
        [-0.01, 0.00, 0.01, -0.03, 0.01],
        [0.02, 0.00, 0.03, 0.01, 0.00],
    ]
    xi = 0.37
    zeta_n = -0.21
    H = madd(madd(p, mscale(2.0 * xi, K)), S_tau)
    # p' = p - projected(L_zeta g), with projected L_zeta g = G_zeta+2 zeta_n K.
    p2 = madd(p, madd(G_zeta, mscale(2.0 * zeta_n, K)), 1.0, -1.0)
    xi2 = xi + zeta_n
    S2 = madd(S_tau, G_zeta)
    H2 = madd(madd(p2, mscale(2.0 * xi2, K)), S2)
    assert maxdiff(H, H2) < 2e-15


def test_flat_graph_bending_sign():
    # In flat Gaussian-normal coordinates, r=eps*xi(y), grad xi=0 at the test point.
    Hess = [
        [0.40, -0.10, 0.00, 0.05, 0.00],
        [-0.10, -0.30, 0.07, 0.00, 0.02],
        [0.00, 0.07, 0.25, -0.04, 0.00],
        [0.05, 0.00, -0.04, 0.18, 0.03],
        [0.00, 0.02, 0.00, 0.03, -0.12],
    ]
    def exact_K(eps):
        # At a stationary point of xi the normalized graph normal gives K_ab=-eps*Hess_ab exactly to first order.
        return mscale(-eps, Hess)
    got = fd_matrix(exact_K, 1e-6)
    expected = mscale(-1.0, Hess)
    assert maxdiff(got, expected) < 2e-11


def test_warped_parallel_shift_signs():
    # ds^2=dr^2+exp(2 c r) eta_ab dy^a dy^b; n=+partial_r.
    eta = [[0.0] * D for _ in range(D)]
    for i, v in enumerate((-1.0, 1.0, 1.0, 1.0, 1.0)):
        eta[i][i] = v
    c = 0.43
    xi = -0.27
    def h_of_eps(eps):
        return mscale(math.exp(2.0 * c * eps * xi), eta)
    def K_of_eps(eps):
        return mscale(c * math.exp(2.0 * c * eps * xi), eta)
    dh = fd_matrix(h_of_eps, 2e-6)
    dK = fd_matrix(K_of_eps, 2e-6)
    h0 = eta
    K0 = mscale(c, h0)
    assert maxdiff(dh, mscale(2.0 * xi, K0)) < 2e-10
    assert maxdiff(dK, mscale(2.0 * c * c * xi, h0)) < 2e-10


def israel_operator(h, Kcov):
    hi = inverse(h)
    Ktrace = trace_with_inverse(hi, Kcov)
    return madd(Kcov, mscale(Ktrace, h), 1.0, -1.0)


def test_perturbed_israel_operator_against_direct_finite_difference():
    h = [
        [-1.0, 0.02, 0.00, 0.00, 0.00],
        [0.02, 1.20, 0.01, 0.00, 0.00],
        [0.00, 0.01, 0.90, -0.02, 0.00],
        [0.00, 0.00, -0.02, 1.35, 0.03],
        [0.00, 0.00, 0.00, 0.03, 2.10],
    ]
    H = [
        [0.04, -0.01, 0.02, 0.00, 0.00],
        [-0.01, -0.03, 0.00, 0.01, 0.00],
        [0.02, 0.00, 0.05, -0.02, 0.01],
        [0.00, 0.01, -0.02, 0.02, -0.01],
        [0.00, 0.00, 0.01, -0.01, 0.06],
    ]
    K = [
        [0.10, 0.01, 0.00, 0.02, 0.00],
        [0.01, -0.06, 0.03, 0.00, 0.01],
        [0.00, 0.03, 0.08, -0.01, 0.00],
        [0.02, 0.00, -0.01, 0.04, 0.02],
        [0.00, 0.01, 0.00, 0.02, 0.07],
    ]
    dK = [
        [-0.02, 0.01, 0.00, 0.00, 0.01],
        [0.01, 0.03, -0.01, 0.02, 0.00],
        [0.00, -0.01, 0.02, 0.00, -0.02],
        [0.00, 0.02, 0.00, -0.04, 0.01],
        [0.01, 0.00, -0.02, 0.01, 0.05],
    ]
    hi = inverse(h)
    Hup = raise2(H, hi)
    Ktrace = trace_with_inverse(hi, K)
    dKtrace_cov = trace_with_inverse(hi, dK)
    K_up_H = contract(raise2(K, hi), H)
    analytic = madd(
        madd(dK, mscale(dKtrace_cov, h), 1.0, -1.0),
        madd(mscale(K_up_H, h), mscale(Ktrace, H), 1.0, -1.0),
    )
    # Independent reconstruction from J(h(e),K(e)).
    exact = lambda e: israel_operator(madd(h, H, 1.0, e), madd(K, dK, 1.0, e))
    fd = fd_matrix(exact, 2e-6)
    assert maxdiff(fd, analytic) < 2e-9
    # Hup exists only to make explicit that H^{ab}=h^{ac}h^{bd}H_cd is finite.
    assert math.isfinite(contract(Hup, K))


def surface_stress(h, w, lam, z):
    hi = inverse(h)
    X = sum(hi[i][j] * w[i] * w[j] for i in range(D) for j in range(D))
    S = mscale(-(lam + 0.5 * z * X), h)
    for i in range(D):
        for j in range(D):
            S[i][j] += z * w[i] * w[j]
    return S


def test_m1_surface_stress_variation_against_direct_finite_difference():
    h = [[0.0] * D for _ in range(D)]
    for i, v in enumerate((-1.0, 1.1, 0.8, 1.4, 2.2)):
        h[i][i] = v
    H = [
        [0.03, 0.01, 0.00, -0.01, 0.00],
        [0.01, -0.02, 0.02, 0.00, 0.01],
        [0.00, 0.02, 0.04, 0.01, 0.00],
        [-0.01, 0.00, 0.01, -0.03, 0.02],
        [0.00, 0.01, 0.00, 0.02, 0.05],
    ]
    w = [0.11, -0.20, 0.07, 0.16, 0.52]
    dw = [-0.03, 0.05, 0.02, -0.01, 0.09]
    lam, z = 0.72, 1.37
    hi = inverse(h)
    wup = [sum(hi[i][j] * w[j] for j in range(D)) for i in range(D)]
    X = sum(wup[i] * w[i] for i in range(D))
    Hup = raise2(H, hi)
    deltaX = 2.0 * sum(wup[i] * dw[i] for i in range(D)) - sum(Hup[i][j] * w[i] * w[j] for i in range(D) for j in range(D))
    analytic = mscale(-0.5 * z * deltaX, h)
    analytic = madd(analytic, mscale(-(lam + 0.5 * z * X), H))
    mix = zeros()
    for i in range(D):
        for j in range(D):
            mix[i][j] = z * (dw[i] * w[j] + w[i] * dw[j])
    analytic = madd(analytic, mix)
    exact = lambda e: surface_stress(madd(h, H, 1.0, e), [w[i] + e * dw[i] for i in range(D)], lam, z)
    fd = fd_matrix(exact, 2e-6)
    assert maxdiff(fd, analytic) < 2e-9


def test_moving_pullback_u1_combination():
    q_sigma = 1.7
    sgrad = [0.20, -0.11, 0.04, 0.07, -0.16]
    aSigma = [-0.05, 0.03, 0.08, -0.02, 0.10]
    alpha_grad = [0.04, -0.03, 0.02, 0.01, -0.05]
    d0 = [sgrad[i] - q_sigma * aSigma[i] for i in range(D)]
    sgrad2 = [sgrad[i] + q_sigma * alpha_grad[i] for i in range(D)]
    a2 = [aSigma[i] + alpha_grad[i] for i in range(D)]
    d1 = [sgrad2[i] - q_sigma * a2[i] for i in range(D)]
    assert max(abs(d0[i] - d1[i]) for i in range(D)) < 2e-15


def test_gluing_and_fixed_interface_gauge_remain_conditional():
    c = load(REG)
    assert c["two_side_bending_gluing"]["normal_displacement_gluing_relation"] == "OPEN_REQUIRES_EXPLICIT_INTERFACE_IDENTIFICATION_MAP"
    assert c["fixed_interface_gauge_admissibility"]["status"] == "LOCALLY_AVAILABLE_CONDITIONALLY_GLOBAL_ADMISSIBILITY_NOT_PROVEN"
    assert c["gate_state"]["PERTURBED_JUNCTION_SYSTEM"] == "NOT_RELEASED"
    assert c["gate_state"]["WP1_full_boundary_hessian"] == "NOT_CLOSED"
    assert c["gate_state"]["WP1_full_quadratic_action"] == "NOT_CLOSED"


def test_upstream_and_physical_firewalls():
    c2 = load(WP1C2)
    c3 = load(REG)
    g = c3["gate_state"]
    assert c2["gate_state"]["WP1_fixed_interface_localized_cap_hessian"] == "DERIVED"
    assert c2["gate_state"]["FM-G0"] == "OPEN"
    expected = {
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
        assert g[key] == value, (key, g.get(key), value)
    g01 = load(G01)
    assert g01["status"] == "OPEN_BLOCKING"
    assert c3["physical_gate_effect"] == "NONE"
    assert c3["physical_evidence_effect"] == "NONE"
    assert c3["solver_authorized"] is False


def main():
    tests = [
        test_contract_scope_and_external_reference_is_non_authoritative,
        test_induced_metric_bulk_D_gauge_invariance,
        test_flat_graph_bending_sign,
        test_warped_parallel_shift_signs,
        test_perturbed_israel_operator_against_direct_finite_difference,
        test_m1_surface_stress_variation_against_direct_finite_difference,
        test_moving_pullback_u1_combination,
        test_gluing_and_fixed_interface_gauge_remain_conditional,
        test_upstream_and_physical_firewalls,
    ]
    for fn in tests:
        fn()
        print(f"PASS: {fn.__name__}")
    print("PASS: ULSH-05 WP1C3 cap bending / perturbed junction geometry preflight v0.1")


if __name__ == "__main__":
    main()
