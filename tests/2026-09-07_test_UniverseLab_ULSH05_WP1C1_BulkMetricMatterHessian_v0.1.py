#!/usr/bin/env python3
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1C1_BulkMetricMatterHessian_v0.1.json"
WP1 = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1_QuadraticActionReadiness_v0.1.json"
WP1A = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1A_FixedMetricScalarMaxwellHessian_v0.1.json"
WP1B = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1B_EHGHYHessianMaster_v0.1.json"
G01 = ROOT / "registry/2026-09-07_UniverseLab_BandVC_G01_PerturbationObservableInventory_v1.0.json"
NOTE = ROOT / "science/solver-hub/2026-09-07_UniverseLab_ULSH05_WP1C1_BulkMetricMatterHessian_v0.1.md"

D = 6
GBAR = [
    [-1.0, 0, 0, 0, 0, 0],
    [0, 1.0, 0, 0, 0, 0],
    [0, 0, 1.0, 0, 0, 0],
    [0, 0, 0, 1.0, 0, 0],
    [0, 0, 0, 0, 1.0, 0],
    [0, 0, 0, 0, 0, 1.0],
]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def matmul(A, B):
    n = len(A)
    return [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def matadd_scaled(A, scale, B):
    n = len(A)
    return [[A[i][j] + scale * B[i][j] for j in range(n)] for i in range(n)]


def inverse_and_det(A):
    n = len(A)
    M = [list(map(float, row)) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(A)]
    det = 1.0
    sign = 1.0
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        assert abs(M[pivot][col]) > 1e-14, "singular matrix"
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]
            sign *= -1.0
        pv = M[col][col]
        det *= pv
        invpv = 1.0 / pv
        M[col] = [x * invpv for x in M[col]]
        for r in range(n):
            if r == col:
                continue
            fac = M[r][col]
            if fac:
                M[r] = [M[r][j] - fac * M[col][j] for j in range(2 * n)]
    inv = [row[n:] for row in M]
    return inv, sign * det


def trace_mat(A):
    return sum(A[i][i] for i in range(len(A)))


def vec_quad(v, M, w):
    return sum(v[i] * M[i][j] * w[j] for i in range(D) for j in range(D))


def tensor2_dot(A, B):
    return sum(A[i][j] * B[i][j] for i in range(D) for j in range(D))


def raise2(P, gi):
    return matmul(matmul(gi, P), gi)


def field_contraction(gi, F, G):
    return sum(
        gi[a][c] * gi[b][d] * F[a][b] * G[c][d]
        for a in range(D) for b in range(D) for c in range(D) for d in range(D)
    )


def antisym(entries):
    A = [[0.0] * D for _ in range(D)]
    for i, j, value in entries:
        A[i][j] = value
        A[j][i] = -value
    return A


def analytic_components(g, P, phi0, varphi0, u, vgrad, F, f, M6, mhat2, aF):
    gi, detg = inverse_and_det(g)
    assert detg < 0.0
    pc = raise2(P, gi)
    r = matmul(matmul(matmul(matmul(gi, P), gi), P), gi)

    p = trace_mat(matmul(gi, P))
    p2 = tensor2_dot(P, pc)
    measure1 = 0.5 * p
    measure2 = p * p / 8.0 - p2 / 4.0

    X0 = vec_quad(u, gi, u)
    X1 = 2.0 * vec_quad(u, gi, vgrad) - vec_quad(u, pc, u)
    X2 = vec_quad(vgrad, gi, vgrad) - 2.0 * vec_quad(u, pc, vgrad) + vec_quad(u, r, u)

    Fmix = matmul(F, gi)  # F_A^B
    W0 = field_contraction(gi, F, F)
    Fdotf = field_contraction(gi, F, f)
    M_ac = [[sum(Fmix[a][b] * F[c][b] for b in range(D)) for c in range(D)] for a in range(D)]
    metric_FF = tensor2_dot(pc, M_ac)
    W1 = 2.0 * Fdotf - 2.0 * metric_FF

    pFf = sum(pc[a][c] * Fmix[a][b] * f[c][b] for a in range(D) for c in range(D) for b in range(D))
    rFF = tensor2_dot(r, M_ac)
    ppFF = sum(
        pc[a][c] * pc[b][d] * F[a][b] * F[c][d]
        for a in range(D) for b in range(D) for c in range(D) for d in range(D)
    )
    f2 = field_contraction(gi, f, f)
    W2 = f2 - 4.0 * pFf + 2.0 * rFF + ppFF

    U0 = 0.5 * mhat2 * M6**2 * phi0**2
    Up = mhat2 * M6**2 * phi0
    Upp = mhat2 * M6**2
    Z0 = math.exp(-2.0 * aF * phi0 / M6**2)
    Zp = -2.0 * aF * Z0 / M6**2
    Zpp = 4.0 * aF * aF * Z0 / M6**4

    L0 = -0.5 * X0 - U0 - 0.25 * Z0 * W0
    L1 = -0.5 * X1 - Up * varphi0 - 0.25 * (Z0 * W1 + Zp * varphi0 * W0)
    L2 = -0.5 * X2 - 0.5 * Upp * varphi0**2 - 0.25 * (
        Z0 * W2 + Zp * varphi0 * W1 + 0.5 * Zpp * varphi0**2 * W0
    )
    D2 = L2 + measure1 * L1 + measure2 * L0

    return {
        "detg": detg,
        "m1": measure1,
        "m2": measure2,
        "X0": X0,
        "X1": X1,
        "X2": X2,
        "W0": W0,
        "W1": W1,
        "W2": W2,
        "L0": L0,
        "L1": L1,
        "L2": L2,
        "D2": D2,
        "Z0": Z0,
        "Zp": Zp,
        "Zpp": Zpp,
        "Upp": Upp,
        "Fdotf": Fdotf,
        "f2": f2,
    }


def exact_density(eps, g, P, phi0, varphi0, u, vgrad, F, f, M6, mhat2, aF):
    G = matadd_scaled(g, eps, P)
    gi, detG = inverse_and_det(G)
    assert detG < 0.0
    phi = phi0 + eps * varphi0
    grad = [u[i] + eps * vgrad[i] for i in range(D)]
    Ft = [[F[i][j] + eps * f[i][j] for j in range(D)] for i in range(D)]
    X = vec_quad(grad, gi, grad)
    W = field_contraction(gi, Ft, Ft)
    U = 0.5 * mhat2 * M6**2 * phi**2
    Z = math.exp(-2.0 * aF * phi / M6**2)
    return math.sqrt(-detG) * (-0.5 * X - U - 0.25 * Z * W)


def exact_W(eps, g, P, F, f):
    G = matadd_scaled(g, eps, P)
    gi, _ = inverse_and_det(G)
    Ft = [[F[i][j] + eps * f[i][j] for j in range(D)] for i in range(D)]
    return field_contraction(gi, Ft, Ft)


def fd_first(fn, h=2e-6):
    return (fn(h) - fn(-h)) / (2.0 * h)


def fd_second_coefficient(fn, h=3e-4):
    # For f=f0+e f1+e^2 f2+..., returns f2+O(h^2).
    return (fn(h) + fn(-h) - 2.0 * fn(0.0)) / (2.0 * h * h)


def assert_close(a, b, rel=4e-6, abs_tol=4e-6):
    assert math.isclose(a, b, rel_tol=rel, abs_tol=abs_tol), (a, b, a - b)


def inventory_status(g01, item):
    rows = [row for row in g01["inventory"] if row["item"] == item]
    assert len(rows) == 1
    return rows[0]["status"]


def sample_data():
    P1 = [
        [0.06, 0.01, -0.02, 0.00, 0.01, -0.01],
        [0.01, -0.04, 0.01, 0.02, 0.00, 0.01],
        [-0.02, 0.01, 0.03, -0.01, 0.02, 0.00],
        [0.00, 0.02, -0.01, 0.05, 0.01, -0.02],
        [0.01, 0.00, 0.02, 0.01, -0.02, 0.01],
        [-0.01, 0.01, 0.00, -0.02, 0.01, 0.04],
    ]
    F1 = antisym([(0, 1, 2.4), (0, 3, -0.7), (2, 3, 0.2), (4, 5, 0.3)])
    f1 = antisym([(0, 2, 0.4), (1, 3, -0.5), (2, 5, 0.7), (4, 5, -0.2)])

    P2 = [
        [-0.03, 0.02, 0.00, -0.01, 0.01, 0.00],
        [0.02, 0.05, -0.01, 0.00, 0.02, -0.01],
        [0.00, -0.01, -0.02, 0.02, 0.00, 0.01],
        [-0.01, 0.00, 0.02, 0.04, -0.02, 0.00],
        [0.01, 0.02, 0.00, -0.02, 0.03, 0.01],
        [0.00, -0.01, 0.01, 0.00, 0.01, -0.01],
    ]
    F2 = antisym([(0, 2, 0.3), (1, 2, 1.1), (3, 4, -0.8), (4, 5, 0.5)])
    f2 = antisym([(0, 5, -0.6), (1, 4, 0.2), (2, 3, 0.9), (3, 5, -0.4)])

    return [
        (P1, 0.83, 0.67, [0.3, -0.2, 0.4, 0.1, -0.5, 0.2], [0.2, 0.1, -0.3, 0.4, 0.15, -0.25], F1, f1, 2.3, 1.7, 0.41),
        (P2, -0.52, -0.38, [-0.4, 0.3, 0.1, -0.2, 0.25, 0.05], [0.1, -0.2, 0.35, 0.05, -0.1, 0.4], F2, f2, 1.8, 0.9, 0.20),
    ]


def main():
    c = load(CONTRACT)
    wp1 = load(WP1)
    a = load(WP1A)
    b = load(WP1B)
    g01 = load(G01)
    note = NOTE.read_text(encoding="utf-8")

    assert c["model_id"] == "HZT-M0-S6-C-PHYS-M1"
    assert c["classification"] == "NONOPERATIVE_ANALYTIC_BULK_MATTER_HESSIAN"
    assert c["physical_gate_effect"] == "NONE"
    assert c["physical_evidence_effect"] == "NONE"
    assert c["solver_authorized"] is False

    negative_F2_seen = False
    for sample in sample_data():
        P, phi0, varphi0, u, vgrad, F, f, M6, mhat2, aF = sample
        args = (GBAR, P, phi0, varphi0, u, vgrad, F, f, M6, mhat2, aF)
        comp = analytic_components(*args)
        negative_F2_seen = negative_F2_seen or comp["W0"] < 0.0

        # Independent F^2 expansion.
        Wfn = lambda e: exact_W(e, GBAR, P, F, f)
        assert_close(fd_first(Wfn), comp["W1"], rel=2e-7, abs_tol=2e-7)
        assert_close(fd_second_coefficient(Wfn), comp["W2"], rel=2e-6, abs_tol=2e-6)

        # Independent complete Lorentz-signature density reconstruction.
        density_fn = lambda e: exact_density(e, *args)
        numerical_D2_density = fd_second_coefficient(density_fn)
        analytic_D2_density = math.sqrt(-comp["detg"]) * comp["D2"]
        assert_close(numerical_D2_density, analytic_D2_density)

        # WP1A exact limit p_AB=0.
        zeroP = [[0.0] * D for _ in range(D)]
        fixed = analytic_components(GBAR, zeroP, phi0, varphi0, u, vgrad, F, f, M6, mhat2, aF)
        gi, _ = inverse_and_det(GBAR)
        v2 = vec_quad(vgrad, gi, vgrad)
        wp1a_expected = (
            -0.5 * v2
            -0.5 * fixed["Upp"] * varphi0**2
            -0.25 * fixed["Z0"] * fixed["f2"]
            -0.5 * fixed["Zp"] * varphi0 * fixed["Fdotf"]
            -0.125 * fixed["Zpp"] * fixed["W0"] * varphi0**2
        )
        assert_close(fixed["D2"], wp1a_expected, rel=2e-12, abs_tol=2e-12)

    assert negative_F2_seen, "negative Fbar^2 Lorentz control was not exercised"

    # Progress is real but deliberately not a full parent-Hessian or observable release.
    bulk = c["bulk_assembly_status"]
    assert bulk["WP1A_fixed_metric_scalar_Maxwell"] == "DERIVED_CONTROL_SUBSECTOR"
    assert bulk["WP1B_gravity_EH_GHY_master"] == "DERIVED_CONTROL_TEMPLATE"
    assert bulk["WP1C1_bulk_matter_metric_mixing"] == "DERIVED"
    assert bulk["full_bulk_interior_gravity_scalar_Maxwell_hessian"] == "ASSEMBLABLE_AS_WP1B_BULK_PLUS_WP1C1_NOT_GAUGE_REDUCED"
    assert bulk["full_parent_hessian_including_cap"] == "NOT_DERIVED"

    assert wp1["readiness_state"]["released_physical_background"] == "NOT_ESTABLISHED"
    assert a["wp1_progress_effect"]["full_S_quad_2"] == "NOT_DERIVED"
    assert b["wp1_progress_effect"]["full_coupled_S_quad_2"] == "NOT_DERIVED"
    assert inventory_status(g01, "matter_perturbation_Delta_m_definition_and_coupling_for_HZT") == "MISSING_REQUIRED_LINK"
    assert inventory_status(g01, "6d_to_4d_perturbative_reduction") == "MISSING_REQUIRED_LINK"
    assert inventory_status(g01, "effective_poisson_mu_k_a") == "MISSING_REQUIRED_LINK"
    assert inventory_status(g01, "gravitational_slip_eta_k_a") == "MISSING_REQUIRED_LINK"
    assert inventory_status(g01, "lensing_Sigma_k_a") == "MISSING_REQUIRED_LINK"

    assert "WP1A-Grenze" in note
    assert "F^2<0" in note
    assert "ASSEMBLABLE_NOT_GAUGE_REDUCED" in note
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

    print("PASS: WP1C1 full bulk metric-scalar-Maxwell epsilon^2 density independently reconstructed; WP1A limit and firewalls preserved")


if __name__ == "__main__":
    main()
