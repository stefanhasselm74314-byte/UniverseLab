#!/usr/bin/env python3
"""Fail-closed regression controls for ULSH-05/WP1D2 v0.1.

Stdlib only. These tests establish algebraic/contract consistency, not a
physical background, physical projector, physical DOF count, or solver release.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry/2026-09-14_UniverseLab_ULSH05_WP1D2_KinematicInvariantProjectorSolvabilityPreflight_v0.1.json"
PREDECESSOR = ROOT / "registry/2026-09-08_UniverseLab_ULSH05_WP1D1_GaugeOperatorKernelPreflight_v0.1.json"
SCIENCE = ROOT / "science/solver-hub/2026-09-14_UniverseLab_ULSH05_WP1D2_KinematicInvariantProjectorSolvabilityPreflight_v0.1.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def close(a: float, b: float, tol: float = 1e-12) -> None:
    assert math.isclose(a, b, rel_tol=tol, abs_tol=tol), (a, b)


def test_contract_and_successor() -> None:
    r = load(REGISTRY)
    p = load(PREDECESSOR)

    assert r["work_package"] == "ULSH-05/WP1D2"
    assert r["basis_main"] == "e8fd2594b5ac86e243b278a339a13705be03b725"
    assert r["physical_gate_effect"] == "NONE"
    assert r["physical_evidence_effect"] == "NONE"
    assert r["solver_authorized"] is False

    assert p["continuation"]["next_candidate_id"] == "ULSH-05/WP1D2"
    assert p["continuation"]["title"] == "Kinematic invariant candidate ledger and projector solvability preflight"
    assert r["successor_assignment"]["predecessor"] == "ULSH-05/WP1D1"
    assert r["successor_assignment"]["assigned_id"] == p["continuation"]["next_candidate_id"]
    assert r["successor_assignment"]["predecessor_continuation_title"] == p["continuation"]["title"]
    assert r["continuation"]["next_exact_id"] == "NOT_ASSIGNED_BY_THIS_PREFLIGHT"


def test_inherited_domain_and_complete_interface_rows() -> None:
    r = load(REGISTRY)
    d = r["inherited_conditional_domain"]
    g = r["gauge_operator_extension"]

    assert d["name"] == "D_cond"
    assert d["status"] == "FROZEN_CONDITIONAL"
    assert d["physical_release"] is False
    assert "smooth Cartesian" in d["pole_regularity"]

    z = g["bulk_diffeomorphism_rows"]
    u = g["u1_rows"]
    rho = g["intrinsic_interface_rows"]

    # The two P1 omissions of the superseded WP1E branch must not recur.
    assert z["xi_shape"] == "delta xi_shape = -zeta_perp"
    assert z["tau_a"] == "delta tau_a = -zeta_parallel_a"
    assert z["H_ab"] == "delta H_ab = 0 under the paired bulk-field/embedding transformation"
    assert z["d_a"] == "delta d_a = 0 under the paired bulk-field/embedding transformation"
    assert u["s"] == "delta s = q_sigma lambda"
    assert u["Acal_a"] == "delta Acal_a = D_a lambda"
    assert u["d_a"] == "delta d_a = 0"
    assert rho["tau_a"] == "delta tau^a = rho^a"
    assert "2 D_(a rho_b)" in rho["H_ab"]


def test_compensator_cancellation() -> None:
    # Independent numerical instantiation of
    # X_r = B_r - 1/2 (d_r-2A')B and X_chi = B_chi - 1/2 d_chi B.
    Aprime = 0.37
    zeta_L = -0.41
    dr_zeta_L = 0.23
    dchi_zeta_L = -0.17
    zeta_r = 0.29
    zeta_chi = -0.31

    delta_B = 2.0 * zeta_L
    delta_Br = zeta_r + dr_zeta_L - 2.0 * Aprime * zeta_L
    delta_Bchi = zeta_chi + dchi_zeta_L

    delta_Xr = delta_Br - 0.5 * (2.0 * dr_zeta_L - 2.0 * Aprime * delta_B)
    delta_Xchi = delta_Bchi - 0.5 * (2.0 * dchi_zeta_L)

    close(delta_Xr, zeta_r)
    close(delta_Xchi, zeta_chi)


def test_scalar_and_maxwell_candidate_cancellations() -> None:
    phip = -0.72
    Achip = 0.44
    L = 1.7
    zeta_r = 0.36
    zeta_chi = -0.28

    # varphihat = varphi - phibar' X_r
    delta_varphi = phip * zeta_r
    delta_Xr = zeta_r
    close(delta_varphi - phip * delta_Xr, 0.0)

    # Ahat_r = u_r + (Achi'/L^2) X_chi
    # Ahat_chi = u_chi - Achi' X_r
    delta_Xchi = zeta_chi
    delta_u_r = -(Achip / (L * L)) * zeta_chi
    delta_u_chi = Achip * zeta_r
    close(delta_u_r + (Achip / (L * L)) * delta_Xchi, 0.0)
    close(delta_u_chi - Achip * delta_Xr, 0.0)

    # Zero-gradient regimes remain finite because no inverse gradients occur.
    phip = 0.0
    Achip = 0.0
    close(phip * zeta_r - phip * delta_Xr, 0.0)
    close(-(Achip / (L * L)) * zeta_chi + (Achip / (L * L)) * delta_Xchi, 0.0)
    close(Achip * zeta_r - Achip * delta_Xr, 0.0)


def test_no_forbidden_inverse_contract() -> None:
    r = load(REGISTRY)
    forbidden = set(r["kinematic_invariant_candidate_ledger"]["forbidden_denominators"])
    assert {
        "1/phibar_prime",
        "1/Abar_chi_prime",
        "1/n",
        "1/k",
        "D2_inverse",
        "retarded_Green_operator",
        "advanced_Green_operator",
    } <= forbidden
    assert r["regime_checks"]["internal_n_zero"].startswith("retained")


def test_polar_translation_counterexample() -> None:
    # In flat polar coordinates, partial_x = cos(chi) partial_r
    # - sin(chi)/r partial_chi. The angular component diverges as r->0,
    # while the geometric norm is exactly one for every r>0.
    chi = 0.91
    for r in (1.0, 1e-2, 1e-6, 1e-10):
        Vr = math.cos(chi)
        Vchi = -math.sin(chi) / r
        norm2 = Vr * Vr + r * r * Vchi * Vchi
        close(norm2, 1.0, tol=1e-10)
    reg = load(REGISTRY)["polar_coordinate_firewall"]
    assert reg["pole_extension_audit"] == "OPEN_NOT_PROVEN_COMPONENTWISE"
    assert "punctured chart L>0" in reg["component_formula_domain"]


def test_projector_closed_range_logic_control() -> None:
    # Finite-dimensional closed-range control: P=diag(1,0).
    # ker(P^T)=span(e2), Ran(P)=span(e1).
    def P(u: tuple[float, float]) -> tuple[float, float]:
        return (u[0], 0.0)

    f_good = (2.5, 0.0)
    f_bad = (2.5, 0.3)
    e2 = (0.0, 1.0)

    dot_good = f_good[0] * e2[0] + f_good[1] * e2[1]
    dot_bad = f_bad[0] * e2[0] + f_bad[1] * e2[1]
    close(dot_good, 0.0)
    assert abs(dot_bad) > 0.0
    assert P((f_good[0], 7.0)) == f_good  # nonunique modulo ker P
    assert P((f_good[0], -11.0)) == f_good

    pre = load(REGISTRY)["projector_solvability_preflight"]
    assert "necessary" in pre["orthogonality_condition"]
    assert "closure(Ran P)" in pre["orthogonality_condition"]
    assert "closed" in pre["closed_range_upgrade"]
    assert pre["closed_range_D2"] == "NOT_PROVEN"
    assert pre["closed_range_Delta_1"] == "NOT_PROVEN"
    assert pre["closed_range_Delta_L"] == "NOT_PROVEN"
    assert pre["physical_Green_operator"] == "NOT_FROZEN"


def test_full_g_invariance_firewall() -> None:
    r = load(REGISTRY)
    s = r["kinematic_invariant_candidate_ledger"]["interface_status"]
    assert "G_RHO_NONINVARIANT" in s["H_ab"]
    assert "G_RHO_NONINVARIANT" in s["d_a"]
    assert s["full_componentwise_rho_invariant_basis"] == "NOT_RELEASED"


def test_exact_gate_inheritance() -> None:
    r = load(REGISTRY)
    g = r["gate_state"]
    expected = {
        "WP1_physical_boundary_domain": "BLOCKED_UNESTABLISHED_BACKGROUND_AND_GLOBAL_CORNER_DATA",
        "WP1D_constraint_elimination": "BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING",
        "WP1D_physical_3plus1_SVT": "NOT_RELEASED",
        "WP1D_physical_DOF_count": "NOT_RELEASED",
        "WP1D1_closed_range_of_G": "NOT_PROVEN",
        "WP1D1_Fredholm_property_of_G": "NOT_PROVEN",
        "WP1D2_projector_solvability_preflight": "DERIVED_FAIL_CLOSED_CLOSED_RANGE_NOT_PROVEN",
        "WP1D2_pole_extension_audit": "OPEN_NOT_PROVEN_COMPONENTWISE",
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
        assert g[key] == value, (key, g.get(key), value)


def test_science_contract_contains_negative_results() -> None:
    text = SCIENCE.read_text(encoding="utf-8")
    for marker in (
        "columnwise invariance != full-G invariance",
        "f perpendicular ker(P^dagger) => exakte Lösbarkeit",
        "rank(G) => physikalischer DOF-Count",
        "grüne QA => physikalische Evidenz",
        "OPEN_NOT_PROVEN_COMPONENTWISE",
    ):
        assert marker in text


def main() -> None:
    tests = [name for name, obj in globals().items() if name.startswith("test_") and callable(obj)]
    for name in sorted(tests):
        globals()[name]()
        print(f"PASS {name}")
    print(f"PASS ULSH-05/WP1D2 controls: {len(tests)} tests")


if __name__ == "__main__":
    main()
