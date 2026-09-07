#!/usr/bin/env python3
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1C4A_SignedCollarBendingGluing_v0.1.json"
WP1C3 = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1C3_CapBendingJunctionGeometry_v0.1.json"
G01 = ROOT / "registry/2026-09-07_UniverseLab_BandVC_G01_PerturbationObservableInventory_v1.0.json"
D = 5


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def zeros():
    return [[0.0]*D for _ in range(D)]


def madd(A, B, a=1.0, b=1.0):
    return [[a*A[i][j] + b*B[i][j] for j in range(D)] for i in range(D)]


def scale(a, A):
    return [[a*x for x in row] for row in A]


def maxdiff(A, B):
    return max(abs(A[i][j]-B[i][j]) for i in range(D) for j in range(D))


def fd_scalar(fn, eps=2e-6):
    return (fn(+eps)-fn(-eps))/(2*eps)


def fd_matrix(fn, eps=2e-6):
    P, M = fn(+eps), fn(-eps)
    return [[(P[i][j]-M[i][j])/(2*eps) for j in range(D)] for i in range(D)]


def test_contract_scope_and_firewall():
    c = load(REG)
    assert c["model_id"] == "HZT-M0-S6-C-PHYS-M1"
    assert c["work_package"] == "ULSH-05/WP1C4A"
    assert c["classification"] == "NONOPERATIVE_GEOMETRIC_GLUING_PREFLIGHT"
    assert c["status"] == "DERIVED_EXPLICIT_SIGNED_COLLAR_TWO_SIDE_BENDING_GLUING_FULL_MOVING_BOUNDARY_DYNAMICS_OPEN"
    assert c["common_signed_collar_map"]["classification"] == "EXPLICIT_INTERFACE_IDENTIFICATION_CONVENTION_NOT_PHYSICAL_BACKGROUND"
    assert c["single_interface_graph"]["interpretation"].endswith("not a gauge-invariant observable")
    assert c["physical_gate_effect"] == "NONE"
    assert c["physical_evidence_effect"] == "NONE"
    assert c["solver_authorized"] is False


def test_collar_coordinate_jacobians_and_local_normals():
    rhoN, rhoS = 2.7, 4.1
    rN = lambda u: rhoN + u
    rS = lambda u: rhoS - u
    assert math.isclose(fd_scalar(rN), +1.0, rel_tol=0.0, abs_tol=2e-10)
    assert math.isclose(fd_scalar(rS), -1.0, rel_tol=0.0, abs_tol=2e-10)
    # If nu=+partial_u, then local frozen outward normals are +nu on N and -nu on S.
    assert load(REG)["common_signed_collar_map"]["local_outward_normals_in_collar"] == {"n_N":"+nu","n_S":"-nu"}


def test_single_interface_graph_reconstructs_opposite_regional_bending():
    rhoN, rhoS, zeta = 3.2, 5.4, -0.37
    rN = lambda eps: rhoN + eps*zeta
    rS = lambda eps: rhoS - eps*zeta
    drN = fd_scalar(rN)
    drS = fd_scalar(rS)
    assert math.isclose(drN, zeta, rel_tol=0.0, abs_tol=2e-10)
    assert math.isclose(drS, -zeta, rel_tol=0.0, abs_tol=2e-10)
    xiN, xiS = drN, drS  # local outward normals are +partial_rN and +partial_rS
    assert abs(xiN + xiS) < 3e-10


def test_common_D_gauge_preserves_gluing_and_can_fix_both_locally():
    zeta, beta = 0.43, -0.18
    xiN, xiS = zeta, -zeta
    betaN, betaS = beta, -beta
    assert abs((xiN+betaN)+(xiS+betaS)) < 1e-15

    # One common collar generator beta=-zeta fixes both regional representations locally.
    beta = -zeta
    xiN2 = xiN + beta
    xiS2 = xiS - beta
    assert abs(xiN2) < 1e-15 and abs(xiS2) < 1e-15

    # Two unrelated regional gauges do not preserve one-interface gluing unless beta_N+beta_S=0.
    bad_betaN, bad_betaS = 0.11, 0.07
    assert abs((xiN+bad_betaN)+(xiS+bad_betaS)) > 1e-3


def test_first_fundamental_form_gluing_by_direct_finite_difference():
    K_N = [[0.10,0.01,0,0,0.02],[0.01,-0.05,0.02,0.01,0],[0,0.02,0.08,-0.01,0],[0,0.01,-0.01,0.06,0.03],[0.02,0,0,0.03,0.04]]
    K_S = [[-0.03,0.02,0.01,0,0],[0.02,0.07,0,-0.01,0.02],[0.01,0,0.04,0.02,0],[0,-0.01,0.02,-0.02,0.01],[0,0.02,0,0.01,0.05]]
    pN = [[0.04,-0.01,0,0.02,0],[-0.01,0.03,0.01,0,0],[0,0.01,-0.02,0.01,0.02],[0.02,0,0.01,0.05,-0.01],[0,0,0.02,-0.01,0.01]]
    zeta = 0.31
    # Choose pS so the reduced common-tangential-gauge continuity relation is satisfied.
    pS = madd(pN, scale(2*zeta, madd(K_N, K_S)))
    h0 = zeros()
    for i, value in enumerate((-1.0,1.1,0.9,1.3,2.0)):
        h0[i][i] = value

    hN = lambda eps: madd(h0, madd(pN, scale(2*zeta, K_N)), 1.0, eps)
    hS = lambda eps: madd(h0, madd(pS, scale(-2*zeta, K_S)), 1.0, eps)
    residual_fd = madd(fd_matrix(hN), fd_matrix(hS), 1.0, -1.0)
    assert maxdiff(residual_fd, zeros()) < 2e-9

    analytic = madd(madd(pN,pS,1,-1), scale(2*zeta,madd(K_N,K_S)))
    assert maxdiff(analytic, zeros()) < 2e-15


def test_scalar_pullback_gluing_offshell_without_junction_simplification():
    phi0 = 0.73
    aN, aS = 0.42, -0.17
    assert abs(aN+aS) > 0.2  # deliberately NOT an on-shell zero-sum control
    zeta = -0.36
    varphiN = 0.11
    # Choose varphiS only from the off-shell pullback continuity relation.
    varphiS = varphiN + zeta*(aN+aS)

    phiN = lambda eps: phi0 + aN*(eps*zeta) + eps*varphiN
    phiS = lambda eps: phi0 + aS*(-eps*zeta) + eps*varphiS
    assert abs(fd_scalar(lambda e: phiN(e)-phiS(e))) < 2e-10

    analytic = varphiN-varphiS+zeta*(aN+aS)
    assert abs(analytic) < 2e-15


def test_patch_and_full_boundary_dynamics_remain_open():
    c = load(REG)
    assert c["gauge_patch_gluing"]["status"] == "OPEN_FOR_WP1C4B"
    assert c["compatible_bulk_D_gauge"]["global_extension_to_poles_and_patch_structure"] == "NOT_PROVEN"
    g = c["gate_state"]
    assert g["WP1_signed_collar_interface_identification"] == "DERIVED"
    assert g["WP1_two_side_bending_gluing"] == "DERIVED_IN_DECLARED_COLLAR"
    assert g["WP1_local_simultaneous_fixed_interface_gauge"] == "DERIVED_COLLAR_LOCAL_ONLY"
    assert g["WP1_global_fixed_interface_gauge"] == "NOT_PROVEN"
    assert g["WP1_full_boundary_hessian"] == "NOT_CLOSED"
    assert g["WP1_full_quadratic_action"] == "NOT_CLOSED"
    assert g["PERTURBED_JUNCTION_SYSTEM"] == "NOT_RELEASED"


def test_upstream_and_physical_firewalls():
    c3, c4, g01 = load(WP1C3), load(REG), load(G01)
    assert c3["gate_state"]["WP1_moving_interface_linear_geometry"] == "DERIVED_PREFLIGHT"
    assert c3["gate_state"]["FM-G0"] == "OPEN"
    assert g01["gap_status_after_inventory"].startswith("OPEN_BLOCKING")
    expected = {
        "PHYSICAL_BACKGROUND":"NOT_ESTABLISHED",
        "FM-G0":"OPEN",
        "AuthorizationDecision":"NOT_CREATED",
        "SingleUseGrant":"NOT_CREATED",
        "BACKEND_IMPORT":"NOT_EXECUTED",
        "SOLVER_EXECUTION":"NOT_EXECUTED",
        "PHYSICAL_RESPONSE_RANK":"NOT_EXECUTED",
        "K1-D":"NOT_RELEASED",
        "K1-E":"NOT_ADMISSIBLE"
    }
    for key, value in expected.items():
        assert c4["gate_state"][key] == value, (key,c4["gate_state"].get(key),value)
    assert c4["physical_gate_effect"] == "NONE"
    assert c4["physical_evidence_effect"] == "NONE"
    assert c4["solver_authorized"] is False


def main():
    tests = [
        test_contract_scope_and_firewall,
        test_collar_coordinate_jacobians_and_local_normals,
        test_single_interface_graph_reconstructs_opposite_regional_bending,
        test_common_D_gauge_preserves_gluing_and_can_fix_both_locally,
        test_first_fundamental_form_gluing_by_direct_finite_difference,
        test_scalar_pullback_gluing_offshell_without_junction_simplification,
        test_patch_and_full_boundary_dynamics_remain_open,
        test_upstream_and_physical_firewalls,
    ]
    for fn in tests:
        fn()
        print(f"PASS: {fn.__name__}")
    print("PASS: ULSH-05 WP1C4A signed-collar bending gluing v0.1")


if __name__ == "__main__":
    main()
