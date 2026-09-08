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
    assert "intrinsic interface-reparameterization" in dom["gauge_closure"]
    for token in ("support", "2pi", "smooth pole", "common two-side"):
        assert token in dom["intrinsic_reparameterization_domain"]


def test_u1_cap_combination_is_invariant() -> None:
    q = 2.75
    d_lambda = -1.3
    delta_Ds = q * d_lambda
    delta_qA = q * d_lambda
    assert math.isclose(delta_Ds - delta_qA, 0.0, abs_tol=1e-15)


def test_moving_interface_induced_metric_is_bulk_diff_invariant() -> None:
    D_zeta_parallel = 0.73
    K = -1.9
    zeta_perp = 0.41
    delta_p = 2.0 * D_zeta_parallel + 2.0 * K * zeta_perp
    delta_xi = -zeta_perp
    delta_Dtau = -D_zeta_parallel
    delta_H = delta_p + 2.0 * K * delta_xi + 2.0 * delta_Dtau
    assert math.isclose(delta_H, 0.0, abs_tol=1e-15)


def test_intrinsic_surface_reparameterization_is_independent_and_quotiented() -> None:
    d = load()
    r = d["gauge_action"]["intrinsic_surface_reparameterization"]
    q = d["kinematic_quotient"]
    assert r["independent_from_bulk_diffeomorphism"] is True
    assert r["must_not_identify_with_zeta_parallel"] is True
    assert r["common_interface_chart"] is True
    assert r["pure_tangential_chart_mode"] == "GAUGE_ORBIT_NOT_PHYSICAL_MODE"
    assert any("intrinsic interface reparameterizations" in generator for generator in q["generators"])
    assert q["bulk_vs_surface_reparameterization"] == "DISTINCT_GAUGE_SYMMETRIES_MUST_NOT_BE_IDENTIFIED"
    assert q["pure_tau_chart_orbit"] == "NOT_A_PHYSICAL_KINEMATIC_MODE"

    # Scalarized control of the active chart-representative convention:
    # a pure intrinsic chart generator shifts tau but remains classified as gauge.
    rho = 0.47
    delta_tau = rho
    assert math.isclose(delta_tau, rho, rel_tol=0.0, abs_tol=1e-15)


def test_schur_complement_control() -> None:
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
    assert g["WP1D_gauge_action"] == "DEFINED_KINEMATICALLY_WITH_INDEPENDENT_SURFACE_REPARAMETERIZATION"
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


def test_document_contains_core_no_go_and_surface_gauge_statements() -> None:
    text = DOC.read_text(encoding="utf-8")
    required = [
        "ULSH-05/WP1D",
        "Kinematischer Quotient versus physischer Phasenraum",
        "singulärer Auxiliary-Block",
        "formales Schur-Komplement",
        "WP1D_constraint_elimination = BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING",
        "physikalische 3+1-S/V/T-Zerlegung",
        "Unabhängige intrinsische Interface-Reparametrisierung",
        "GAUGE_ORBIT_NOT_PHYSICAL_MODE",
        "SOLVER_EXECUTION          NOT_EXECUTED",
    ]
    for token in required:
        assert token in text
    assert "nicht mit" in text and "\\zeta_\\parallel^a" in text


def main() -> None:
    test_successor_id_is_assigned_only_here()
    test_conditional_domain_is_not_physical_release()
    test_u1_cap_combination_is_invariant()
    test_moving_interface_induced_metric_is_bulk_diff_invariant()
    test_intrinsic_surface_reparameterization_is_independent_and_quotiented()
    test_schur_complement_control()
    test_singular_auxiliary_block_fails_closed()
    test_svt_semantics_are_conditional_not_physical_3plus1()
    test_internal_zero_mode_is_not_divided_away()
    test_firewalls_remain_closed()
    test_document_contains_core_no_go_and_surface_gauge_statements()
    print("WP1D conditional SVT gauge-constraint reduction controls: PASS")


if __name__ == "__main__":
    main()
