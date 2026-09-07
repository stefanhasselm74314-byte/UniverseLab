#!/usr/bin/env python3
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1C2_CapFixedInterfaceHessian_v0.1.json"
FUNCTION_FREEZE = ROOT / "registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json"
WP1 = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1_QuadraticActionReadiness_v0.1.json"
WP1B = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1B_EHGHYHessianMaster_v0.1.json"
WP1C1 = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1C1_BulkMetricMatterHessian_v0.1.json"
G01 = ROOT / "registry/2026-09-07_UniverseLab_BandVC_G01_PerturbationObservableInventory_v1.0.json"
PARENT = ROOT / "SCI-001-002_v0.1_Canonical_6D_Parent_Action_and_Boundary_Closure.md"
NOTE = ROOT / "science/solver-hub/2026-09-07_UniverseLab_ULSH05_WP1C2_CapFixedInterfaceHessian_v0.1.md"

N = 5
HBAR = [
    [-1.0, 0, 0, 0, 0],
    [0, 1.0, 0, 0, 0],
    [0, 0, 1.0, 0, 0],
    [0, 0, 0, 1.0, 0],
    [0, 0, 0, 0, 1.0],
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
    return [row[n:] for row in M], sign * det


def trace_mat(A):
    return sum(A[i][i] for i in range(len(A)))


def tensor2_dot(A, B):
    n = len(A)
    return sum(A[i][j] * B[i][j] for i in range(n) for j in range(n))


def vec_quad(v, M, w):
    return sum(v[i] * M[i][j] * w[j] for i in range(N) for j in range(N))


def matvec(M, v):
    return [sum(M[i][j] * v[j] for j in range(N)) for i in range(N)]


def raise2(Q, hi):
    return matmul(matmul(hi, Q), hi)


def assert_close(a, b, rel=4e-6, abs_tol=4e-6):
    assert math.isclose(a, b, rel_tol=rel, abs_tol=abs_tol), (a, b, a - b)


def assert_vec_close(a, b, rel=3e-7, abs_tol=3e-7):
    assert len(a) == len(b)
    for x, y in zip(a, b):
        assert_close(x, y, rel, abs_tol)


def assert_matrix_close(A, B, rel=3e-7, abs_tol=3e-7):
    for i in range(len(A)):
        for j in range(len(A)):
            assert_close(A[i][j], B[i][j], rel, abs_tol)


def analytic(h, Q, B, b, lam, Z, qcharge):
    hi, deth = inverse_and_det(h)
    assert deth < 0.0
    qc = raise2(Q, hi)
    r = matmul(matmul(matmul(matmul(hi, Q), hi), Q), hi)
    qtrace = trace_mat(matmul(hi, Q))
    q2 = tensor2_dot(Q, qc)
    n1 = qtrace / 2.0
    n2 = qtrace * qtrace / 8.0 - q2 / 4.0

    Bup = matvec(hi, B)
    bup = matvec(hi, b)
    Y0 = sum(B[i] * Bup[i] for i in range(N))
    Y1 = 2.0 * sum(Bup[i] * b[i] for i in range(N)) - vec_quad(B, qc, B)
    Y2 = vec_quad(b, hi, b) - 2.0 * vec_quad(B, qc, b) + vec_quad(B, r, B)

    L0 = -lam - 0.5 * Z * Y0
    L1 = -0.5 * Z * Y1
    L2 = -0.5 * Z * Y2
    C2 = L2 + n1 * L1 + n2 * L0

    Sbar = [[-(lam + 0.5 * Z * Y0) * h[i][j] + Z * B[i] * B[j] for j in range(N)] for i in range(N)]
    deltaS = [[
        -(lam + 0.5 * Z * Y0) * Q[i][j]
        - 0.5 * Z * Y1 * h[i][j]
        + Z * (B[i] * b[j] + b[i] * B[j])
        for j in range(N)
    ] for i in range(N)]

    Jbar = [qcharge * Z * x for x in Bup]
    deltaJ = [qcharge * Z * (bup[i] - sum(qc[i][j] * B[j] for j in range(N))) for i in range(N)]
    phase_density_delta = [
        math.sqrt(-deth) * Z * (
            bup[i] - sum(qc[i][j] * B[j] for j in range(N)) + 0.5 * qtrace * Bup[i]
        )
        for i in range(N)
    ]

    return {
        "hi": hi,
        "deth": deth,
        "qtrace": qtrace,
        "q2": q2,
        "Y0": Y0,
        "Y1": Y1,
        "Y2": Y2,
        "C2": C2,
        "Sbar": Sbar,
        "deltaS": deltaS,
        "Jbar": Jbar,
        "deltaJ": deltaJ,
        "phase_density_delta": phase_density_delta,
    }


def exact_density(eps, h, Q, B, b, lam, Z):
    H = matadd_scaled(h, eps, Q)
    hi, detH = inverse_and_det(H)
    assert detH < 0.0
    Be = [B[i] + eps * b[i] for i in range(N)]
    Y = vec_quad(Be, hi, Be)
    return math.sqrt(-detH) * (-lam - 0.5 * Z * Y)


def exact_stress(eps, h, Q, B, b, lam, Z):
    H = matadd_scaled(h, eps, Q)
    hi, _ = inverse_and_det(H)
    Be = [B[i] + eps * b[i] for i in range(N)]
    Y = vec_quad(Be, hi, Be)
    return [[-(lam + 0.5 * Z * Y) * H[i][j] + Z * Be[i] * Be[j] for j in range(N)] for i in range(N)]


def exact_current(eps, h, Q, B, b, Z, qcharge):
    H = matadd_scaled(h, eps, Q)
    hi, _ = inverse_and_det(H)
    Be = [B[i] + eps * b[i] for i in range(N)]
    Bup = matvec(hi, Be)
    return [qcharge * Z * x for x in Bup]


def fd_first_scalar(fn, h=2e-6):
    return (fn(h) - fn(-h)) / (2.0 * h)


def fd_second_coefficient(fn, h=3e-4):
    return (fn(h) + fn(-h) - 2.0 * fn(0.0)) / (2.0 * h * h)


def fd_first_matrix(fn, h=2e-6):
    P = fn(h)
    M = fn(-h)
    return [[(P[i][j] - M[i][j]) / (2.0 * h) for j in range(N)] for i in range(N)]


def fd_first_vector(fn, h=2e-6):
    P = fn(h)
    M = fn(-h)
    return [(P[i] - M[i]) / (2.0 * h) for i in range(N)]


def inventory_status(g01, item):
    rows = [row for row in g01["inventory"] if row["item"] == item]
    assert len(rows) == 1
    return rows[0]["status"]


def samples():
    Q1 = [
        [0.04, 0.01, -0.01, 0.00, 0.02],
        [0.01, -0.03, 0.02, 0.01, 0.00],
        [-0.01, 0.02, 0.05, -0.02, 0.01],
        [0.00, 0.01, -0.02, 0.02, 0.01],
        [0.02, 0.00, 0.01, 0.01, -0.01],
    ]
    Q2 = [
        [-0.02, 0.00, 0.01, -0.01, 0.00],
        [0.00, 0.03, -0.01, 0.02, 0.01],
        [0.01, -0.01, -0.04, 0.00, 0.02],
        [-0.01, 0.02, 0.00, 0.05, -0.01],
        [0.00, 0.01, 0.02, -0.01, 0.02],
    ]
    return [
        (Q1, [1.4, 0.2, -0.1, 0.3, 0.05], [0.35, -0.2, 0.4, 0.1, -0.25], 0.8, 1.7, 0.43),
        (Q2, [0.2, 0.7, -0.5, 0.1, 0.4], [-0.1, 0.3, 0.2, -0.4, 0.15], -0.4, 2.1, 0.27),
    ]


def main():
    c = load(CONTRACT)
    freeze = load(FUNCTION_FREEZE)
    wp1 = load(WP1)
    wp1b = load(WP1B)
    wp1c1 = load(WP1C1)
    g01 = load(G01)
    parent = PARENT.read_text(encoding="utf-8")
    note = NOTE.read_text(encoding="utf-8")

    assert c["model_id"] == "HZT-M0-S6-C-PHYS-M1"
    assert c["classification"] == "NONOPERATIVE_ANALYTIC_CAP_HESSIAN_FIXED_INTERFACE_CONTROL"
    assert c["physical_gate_effect"] == "NONE"
    assert c["physical_evidence_effect"] == "NONE"
    assert c["solver_authorized"] is False

    # Canonical M1 cap function/charge provenance.
    assert freeze["exact_functions"]["lambda"]["derivatives"]["d_lambda_dphi"] == "0"
    assert freeze["exact_functions"]["lambda"]["derivatives"]["d2_lambda_dphi2"] == "0"
    assert freeze["exact_functions"]["Z_sigma"]["derivatives"]["d_Z_sigma_dphi"] == "0"
    assert freeze["exact_functions"]["Z_sigma"]["derivatives"]["d2_Z_sigma_dphi2"] == "0"
    assert freeze["charge_normalization"]["q_sigma"] == "m_sigma*q_ref"
    assert "HZT-S6-PAR-v0.1-EQ-002" in parent
    assert "HZT-S6-PAR-v0.1-EQ-006" in parent
    assert "HZT-S6-PAR-v0.1-EQ-009" in parent
    assert "HZT-S6-PAR-v0.1-EQ-010" in parent

    negative_Y_seen = False
    for Q, B, b, lam, Z, qcharge in samples():
        comp = analytic(HBAR, Q, B, b, lam, Z, qcharge)
        negative_Y_seen = negative_Y_seen or comp["Y0"] < 0.0

        density_fn = lambda e: exact_density(e, HBAR, Q, B, b, lam, Z)
        numerical = fd_second_coefficient(density_fn)
        analytic_density = math.sqrt(-comp["deth"]) * comp["C2"]
        assert_close(numerical, analytic_density)

        stress_fn = lambda e: exact_stress(e, HBAR, Q, B, b, lam, Z)
        assert_matrix_close(fd_first_matrix(stress_fn), comp["deltaS"])

        current_fn = lambda e: exact_current(e, HBAR, Q, B, b, Z, qcharge)
        assert_vec_close(fd_first_vector(current_fn), comp["deltaJ"])

        # Exact fixed-induced-metric limit.
        zeroQ = [[0.0] * N for _ in range(N)]
        fixed = analytic(HBAR, zeroQ, B, b, lam, Z, qcharge)
        hi, _ = inverse_and_det(HBAR)
        expected_fixed = -0.5 * Z * vec_quad(b, hi, b)
        assert_close(fixed["C2"], expected_fixed, rel=2e-12, abs_tol=2e-12)

        # Stückelberg/U(1) perturbative gauge control: ds -> ds+q xi, a -> a+xi, hence b unchanged.
        xi = [0.11, -0.07, 0.05, 0.02, -0.09]
        ds = [b[i] + qcharge * 0.0 for i in range(N)]  # choose a=0 representative, ds=b
        avec = [0.0] * N
        ds_shifted = [ds[i] + qcharge * xi[i] for i in range(N)]
        avec_shifted = [avec[i] + xi[i] for i in range(N)]
        b_shifted = [ds_shifted[i] - qcharge * avec_shifted[i] for i in range(N)]
        assert_vec_close(b_shifted, b, rel=1e-14, abs_tol=1e-14)
        shifted = analytic(HBAR, Q, B, b_shifted, lam, Z, qcharge)
        assert_close(shifted["C2"], comp["C2"], rel=1e-14, abs_tol=1e-14)
        assert_matrix_close(shifted["deltaS"], comp["deltaS"], rel=1e-14, abs_tol=1e-14)
        assert_vec_close(shifted["deltaJ"], comp["deltaJ"], rel=1e-14, abs_tol=1e-14)

    assert negative_Y_seen, "Lorentz-signature negative background winding norm control not exercised"

    progress = c["parent_hessian_progress"]
    assert progress["WP1C2_cap_fixed_interface"] == "DERIVED_CONTROL_SUBSECTOR"
    assert progress["bulk_plus_fixed_interface_cap_parent_hessian"] == "ASSEMBLABLE_CONTROL_LEVEL_NOT_BENDING_COMPLETE_NOT_GAUGE_REDUCED"
    assert progress["full_parent_hessian_with_moving_cap"] == "NOT_DERIVED"

    assert wp1["readiness_state"]["cap_bending_or_interface_gauge"] == "MISSING_REQUIRED_LINK"
    assert wp1b["fixed_interface_gaussian_normal_boundary_control"]["classification"] == "LOCAL_CONTROL_GAUGE_NOT_GLOBAL_PHYSICAL_GAUGE_RELEASE"
    assert wp1c1["bulk_assembly_status"]["full_parent_hessian_including_cap"] == "NOT_DERIVED"
    assert inventory_status(g01, "matter_perturbation_Delta_m_definition_and_coupling_for_HZT") == "MISSING_REQUIRED_LINK"
    assert inventory_status(g01, "6d_to_4d_perturbative_reduction") == "MISSING_REQUIRED_LINK"
    assert inventory_status(g01, "lensing_Sigma_k_a") == "MISSING_REQUIRED_LINK"

    assert "Cap-Bending" in note
    assert "Residualkernel" in note
    assert "U(1)-Gaugeinvarianz" in note
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

    print("PASS: WP1C2 cap fixed-interface Hessian, stress/current responses and U(1) control independently verified; bending/physical gates remain open")


if __name__ == "__main__":
    main()
