#!/usr/bin/env python3
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1B_EHGHYHessianMaster_v0.1.json"
PARENT_MD = ROOT / "SCI-001-002_v0.1_Canonical_6D_Parent_Action_and_Boundary_Closure.md"
READINESS = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1_QuadraticActionReadiness_v0.1.json"
WP1A = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1A_FixedMetricScalarMaxwellHessian_v0.1.json"
G01 = ROOT / "registry/2026-09-07_UniverseLab_BandVC_G01_PerturbationObservableInventory_v1.0.json"
NOTE = ROOT / "science/solver-hub/2026-09-07_UniverseLab_ULSH05_WP1B_EHGHYHessianMaster_v0.1.md"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def assert_close(a, b, tol=1e-12):
    assert math.isclose(a, b, rel_tol=tol, abs_tol=tol), (a, b)


def exact_conformal_bulk_squad_D6(Rbar, Lambda, c, M4):
    # g_AB(eps)=s*gbar_AB, s=1+eps*c.
    # In D=6: sqrt(-g)R = sqrt(-gbar)*s^2*Rbar,
    # and sqrt(-g)(-2 Lambda) = sqrt(-gbar)*(-2 Lambda)*s^3.
    epsilon2_density = (Rbar - 6.0 * Lambda) * c * c
    return 0.5 * M4 * epsilon2_density


def master_conformal_bulk_squad_D6(Rbar, Lambda, c, M4):
    D = 6.0
    # Constant-curvature/Einstein local control background:
    # E_AB=e*g_AB with e=Lambda-(D-2)R/(2D).
    e = Lambda - ((D - 2.0) / (2.0 * D)) * Rbar
    # Under constant metric scaling, G_AB is unchanged as a covariant tensor;
    # delta E_AB = Lambda*c*g_AB.
    term_delta_E = -D * Lambda * c * c
    term_measure_inverse = -0.5 * D * D * e * c * c
    term_inverse_second = 2.0 * D * e * c * c
    bracket = term_delta_E + term_measure_inverse + term_inverse_second
    return 0.25 * M4 * bracket


def matmul(A, B):
    n = len(A)
    return [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def matadd(A, B):
    n = len(A)
    return [[A[i][j] + B[i][j] for j in range(n)] for i in range(n)]


def matsub(A, B):
    n = len(A)
    return [[A[i][j] - B[i][j] for j in range(n)] for i in range(n)]


def matscale(s, A):
    return [[s * x for x in row] for row in A]


def trace(A):
    return sum(A[i][i] for i in range(len(A)))


def frobenius(A, B):
    n = len(A)
    return sum(A[i][j] * B[i][j] for i in range(n) for j in range(n))


def identity(n):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def assert_matrix_close(A, B, tol=1e-12):
    n = len(A)
    for i in range(n):
        for j in range(n):
            assert_close(A[i][j], B[i][j], tol)


def boundary_gaussian_normal_check():
    # Local orthonormal five-dimensional boundary frame.
    d = 5
    I = identity(d)
    K = [
        [0.7, 0.1, 0.0, -0.2, 0.05],
        [0.1, -0.4, 0.03, 0.0, 0.08],
        [0.0, 0.03, 0.2, 0.06, -0.01],
        [-0.2, 0.0, 0.06, 0.5, 0.04],
        [0.05, 0.08, -0.01, 0.04, -0.1],
    ]
    q = [
        [0.2, -0.03, 0.01, 0.0, 0.02],
        [-0.03, -0.1, 0.04, 0.01, 0.0],
        [0.01, 0.04, 0.15, -0.02, 0.03],
        [0.0, 0.01, -0.02, 0.05, -0.01],
        [0.02, 0.0, 0.03, -0.01, -0.08],
    ]
    dq = [
        [0.11, 0.02, -0.01, 0.03, 0.0],
        [0.02, -0.07, 0.05, 0.0, 0.01],
        [-0.01, 0.05, 0.09, -0.04, 0.02],
        [0.03, 0.0, -0.04, 0.13, 0.06],
        [0.0, 0.01, 0.02, 0.06, -0.05],
    ]

    Ktrace = trace(K)
    Kdotq = frobenius(K, q)
    deltaK_direct = -Kdotq + 0.5 * trace(dq)
    deltaKab_direct = matscale(0.5, dq)
    deltaPi_direct = matsub(
        matsub(deltaKab_direct, matscale(deltaK_direct, I)),
        matscale(Ktrace, q),
    )

    # Covariant normal derivative in Gaussian normal coordinates:
    # nabla_n q = partial_n q - K q - q K.
    Kq = matmul(K, q)
    qK = matmul(q, K)
    cov_n_q = matsub(matsub(dq, Kq), qK)
    sym_Kq = matscale(0.5, matadd(Kq, qK))
    deltaKab_cov = matadd(matscale(0.5, cov_n_q), sym_Kq)
    q_normal_scalar = trace(dq) - 2.0 * Kdotq
    deltaK_cov = 0.5 * q_normal_scalar
    deltaPi_cov = matsub(
        matsub(deltaKab_cov, matscale(deltaK_cov, I)),
        matscale(Ktrace, q),
    )

    assert_matrix_close(deltaKab_direct, deltaKab_cov)
    assert_close(deltaK_direct, deltaK_cov)
    assert_matrix_close(deltaPi_direct, deltaPi_cov)


def conformal_ricci_local_check():
    # Independent local flat-frame contraction of the generic delta R_AB formula
    # for p_AB=2*sigma*delta_AB, evaluated from an arbitrary symmetric Hessian H_AB.
    D = 6
    H = [
        [0.3, 0.02, -0.01, 0.04, 0.0, 0.01],
        [0.02, -0.2, 0.03, 0.0, 0.05, -0.02],
        [-0.01, 0.03, 0.1, 0.01, -0.04, 0.02],
        [0.04, 0.0, 0.01, -0.05, 0.03, 0.06],
        [0.0, 0.05, -0.04, 0.03, 0.12, -0.01],
        [0.01, -0.02, 0.02, 0.06, -0.01, 0.08],
    ]
    trH = trace(H)
    for A in range(D):
        for B in range(D):
            delta = 1.0 if A == B else 0.0
            term1 = 2.0 * H[A][B]
            term2 = 2.0 * H[A][B]
            term3 = -2.0 * delta * trH
            term4 = -2.0 * D * H[A][B]
            generic = 0.5 * (term1 + term2 + term3 + term4)
            expected = -(D - 2.0) * H[A][B] - delta * trH
            assert_close(generic, expected)


def inventory_status(g01, item):
    rows = [row for row in g01["inventory"] if row["item"] == item]
    assert len(rows) == 1, f"missing/duplicate G01 item: {item}"
    return rows[0]["status"]


def main():
    c = load(CONTRACT)
    r = load(READINESS)
    a = load(WP1A)
    g = load(G01)
    parent = PARENT_MD.read_text(encoding="utf-8")
    note = NOTE.read_text(encoding="utf-8")

    assert c["model_id"] == "HZT-M0-S6-C-PHYS-M1"
    assert c["classification"] == "NONOPERATIVE_ANALYTIC_GRAVITY_HESSIAN_CONTROL"
    assert c["status"] == "DERIVED_VARIATIONAL_HESSIAN_MASTER_FIXED_INTERFACE_GN_BOUNDARY_CONTROL_FULL_COUPLED_SYSTEM_NOT_CLOSED"
    assert c["physical_gate_effect"] == "NONE"
    assert c["physical_evidence_effect"] == "NONE"
    assert c["solver_authorized"] is False

    # Project parent-action and Israel-sign provenance.
    compact = "".join(parent.split())
    assert "M_6^4\sum_{s=\pm}\int_{\Sigma_5}d^5x\sqrt{-h}\,K_s" in compact
    assert "M_6^4\sum_{s=\pm}\left(K_{ab}^{(s)}-K^{(s)}h_{ab}\right)=S_{ab}" in compact
    assert "Outward-normal-Konvention" in parent

    # Independent 6D constant conformal-scaling check of the off-shell master factors.
    samples = [
        (12.0, 0.7, 0.13, 2.4),
        (-8.5, -0.2, -0.31, 0.9),
        (3.2, 1.1, 0.47, 5.0),
    ]
    for Rbar, Lambda, cscale, M4 in samples:
        direct = exact_conformal_bulk_squad_D6(Rbar, Lambda, cscale, M4)
        master = master_conformal_bulk_squad_D6(Rbar, Lambda, cscale, M4)
        assert_close(direct, master)

    # Independent local checks of the derivative kernel and boundary momentum variation.
    conformal_ricci_local_check()
    boundary_gaussian_normal_check()

    # Scope remains a control/master block, not the complete coupled Hessian.
    progress = c["wp1_progress_effect"]
    assert progress["WP1A_fixed_metric_scalar_Maxwell"] == "DERIVED_CONTROL_SUBSECTOR"
    assert progress["WP1B_EH_GHY_master"] == "DERIVED_CONTROL_TEMPLATE"
    assert progress["full_coupled_S_quad_2"] == "NOT_DERIVED"
    assert progress["ULSH05_WP1"] == "PREPARATORY_IN_PROGRESS_NOT_CLOSED"
    assert progress["G01"] == "OPEN_BLOCKING"

    gn = c["fixed_interface_gaussian_normal_boundary_control"]
    assert gn["classification"] == "LOCAL_CONTROL_GAUGE_NOT_GLOBAL_PHYSICAL_GAUGE_RELEASE"
    assert "p_nn=0 and p_na=0" in " ".join(gn["assumptions"])
    assert "does not prove" in gn["gauge_firewall"]

    # Prior WP1/WP1A and G01 non-release remains intact.
    assert r["readiness_state"]["released_physical_background"] == "NOT_ESTABLISHED"
    assert r["readiness_state"]["cap_bending_or_interface_gauge"] == "MISSING_REQUIRED_LINK"
    assert a["wp1_progress_effect"]["full_S_quad_2"] == "NOT_DERIVED"
    assert inventory_status(g, "matter_perturbation_Delta_m_definition_and_coupling_for_HZT") == "MISSING_REQUIRED_LINK"
    assert inventory_status(g, "6d_to_4d_perturbative_reduction") == "MISSING_REQUIRED_LINK"
    assert inventory_status(g, "effective_poisson_mu_k_a") == "MISSING_REQUIRED_LINK"
    assert inventory_status(g, "lensing_Sigma_k_a") == "MISSING_REQUIRED_LINK"

    # Scientific note must retain the main methodological firewalls.
    assert "Ebar_AB -> 0" in note
    assert "Cap-Bending" in note
    assert "PREPARATORY_IN_PROGRESS_NOT_CLOSED" in note
    assert "NOT_ESTABLISHED" in note

    expected_fw = {
        "FM-G0": "OPEN",
        "AuthorizationDecision": "NOT_CREATED",
        "SingleUseGrant": "NOT_CREATED",
        "BACKEND_IMPORT": "NOT_EXECUTED",
        "SOLVER_EXECUTION": "NOT_EXECUTED",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "PHYSICAL_RESPONSE_RANK": "NOT_EXECUTED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
    }
    assert c["unchanged_firewalls"] == expected_fw

    print("PASS: WP1B EH+GHY Hessian master and boundary kernel independently checked; coupled/physical gates remain closed")


if __name__ == "__main__":
    main()
