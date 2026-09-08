from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry/2026-09-08_UniverseLab_ULSH05_WP1D_ConditionalSVTGaugeConstraintReduction_v0.1.json"
DOC = ROOT / "science/solver-hub/2026-09-08_UniverseLab_ULSH05_WP1D_ConditionalSVTGaugeConstraintReduction_v0.1.md"


def load() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_successor_id_is_assigned_only_here() -> None:
    d = load()
    s = d["successor_assignment"]
    assert d["work_package"] == "ULSH-05/WP1D"
    assert s["predecessor"] == "ULSH-05/WP1C4B2C"
    assert s["assigned_id"] == "ULSH-05/WP1D"
    assert s["status"] == "FROZEN_BY_THIS_SUCCESSOR_CONTRACT"
    assert "not claimed" in s["semantics"].lower()


def test_conditional_domain_is_not_physical_release() -> None:
    d = load()
    dom = d["conditional_domain"]
    assert dom["physical_release"] is False
    assert "int(M4)" in dom["tangential_support_finite_boundary_M4"]
    assert "2pi" in dom["chi_periodicity"]
    assert "smooth Cartesian" in dom["pole_regularity"]
    assert "O(r^abs(n))" in dom["scalar_fourier_control"]


def test_u1_cap_combination_is_invariant() -> None:
    # For d = D s - q A and delta s = q lambda, delta A = D lambda:
    q = 2.75
    d_lambda = -1.3
    delta_Ds = q * d_lambda
    delta_qA = q * d_lambda
    assert math.isclose(delta_Ds - delta_qA, 0.0, abs_tol=1e-15)


def test_moving_interface_induced_metric_is_invariant() -> None:
    # Scalarized component control of
    # delta p = 2 D zeta_parallel + 2 K zeta_perp,
    # delta xi = -zeta_perp, delta(D tau) = -D zeta_parallel.
    D_zeta_parallel = 0.73
    K = -1.9
    zeta_perp = 0.41
    delta_p = 2.0 * D_zeta_parallel + 2.0 * K * zeta_perp
    delta_xi = -zeta_perp
    delta_Dtau = -D_zeta_parallel
    delta_H = delta_p + 2.0 * K * delta_xi + 2.0 * delta_Dtau
    assert math.isclose(delta_H, 0.0, abs_tol=1e-15)


def test_schur_complement_control() -> None:
    # S = 1/2 A q^2 + B q n + 1/2 C n^2
    A = 4.0
    B = 2.0
    C = 5.0
    q = 1.7
    n_star = -(B / C) * q
    direct = 0.5 * A * q * q + B * q * n_star + 0.5 * C * n_star * n_star
    A_red = A - B * B / C
    reduced = 0.5 * A_red * q * q
    assert math.isclose(direct, reduced, rel_tol=0.0, abs_tol=1e-14)


def test_singular_auxiliary_block_fails_closed() -> None:
    d = load()
    ce = d["constraint_elimination"]
    assert ce["singular_C"] == "DIRECT_ELIMINATION_FORBIDDEN"
    assert ce["status"] == "BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING"
    assert ce["physical_kinetic_matrix"] == "NOT_IDENTIFIED"


def test_svt_semantics_are_conditional_not_physical_3plus1() -> None:
    d = load()
    s = d["svt_semantics"]
    assert s["physical_3plus1_svt"] == "NOT_RELEASED"
    assert s["projector_status"] == "CONDITIONAL_PROJECTOR_KERNELS_OPEN"
    for forbidden in ("global inverse D2", "retarded Green operator", "physical mode projector"):
        assert forbidden in s["not_frozen"]


def test_internal_zero_mode_is_not_divided_away() -> None:
    d = load()
    assert "no division by n" in d["regime_checks"]["internal_n_zero"]


def test_firewalls_remain_closed() -> None:
    d = load()
    g = d["gate_state"]
    assert d["solver_authorized"] is False
    assert d["physical_gate_effect"] == "NONE"
    assert d["physical_evidence_effect"] == "NONE"
    assert g["WP1D_successor_identifier"] == "FROZEN_BY_THIS_SUCCESSOR_CONTRACT"
    assert g["WP1D_analytic_field_domain"] == "FROZEN_CONDITIONAL"
    assert g["WP1D_gauge_action"] == "DEFINED_KINEMATICALLY"
    assert g["WP1D_constraint_elimination"] == "BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING"
    assert g["WP1D_physical_3plus1_SVT"] == "NOT_RELEASED"
    assert g["WP1D_physical_DOF_count"] == "NOT_RELEASED"
    assert g["WP1_full_quadratic_action"] == "NOT_CLOSED"
    assert g["PERTURBED_JUNCTION_SYSTEM"] == "NOT_RELEASED"
    assert g["PHYSICAL_BACKGROUND"] == "NOT_ESTABLISHED"
    assert g["FM-G0"] == "OPEN"
    assert g["AuthorizationDecision"] == "NOT_CREATED"
    assert g["SingleUseGrant"] == "NOT_CREATED"
    assert g["BACKEND_IMPORT"] == "NOT_EXECUTED"
    assert g["SOLVER_EXECUTION"] == "NOT_EXECUTED"
    assert g["PHYSICAL_RESPONSE_RANK"] == "NOT_EXECUTED"
    assert g["K1-D"] == "NOT_RELEASED"
    assert g["K1-E"] == "NOT_ADMISSIBLE"


def test_document_contains_core_no_go_statements() -> None:
    text = DOC.read_text(encoding="utf-8")
    required = [
        "ULSH-05/WP1D",
        "Kinematischer Quotient versus physischer Phasenraum",
        "singulärer Auxiliary-Block",
        "formales Schur-Komplement",
        "WP1D_constraint_elimination = BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING",
        "physische 3+1-S/V/T-Zerlegung",
        "SOLVER_EXECUTION          NOT_EXECUTED",
    ]
    for token in required:
        assert token in text


def main() -> None:
    test_successor_id_is_assigned_only_here()
    test_conditional_domain_is_not_physical_release()
    test_u1_cap_combination_is_invariant()
    test_moving_interface_induced_metric_is_invariant()
    test_schur_complement_control()
    test_singular_auxiliary_block_fails_closed()
    test_svt_semantics_are_conditional_not_physical_3plus1()
    test_internal_zero_mode_is_not_divided_away()
    test_firewalls_remain_closed()
    test_document_contains_core_no_go_statements()
    print("WP1D conditional SVT gauge-constraint reduction controls: PASS")


if __name__ == "__main__":
    main()
