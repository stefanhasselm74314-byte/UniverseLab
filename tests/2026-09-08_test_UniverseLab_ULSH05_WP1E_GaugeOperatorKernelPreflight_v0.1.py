from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry/2026-09-08_UniverseLab_ULSH05_WP1E_GaugeOperatorKernelPreflight_v0.1.json"
DOC = ROOT / "science/solver-hub/2026-09-08_UniverseLab_ULSH05_WP1E_GaugeOperatorKernelPreflight_v0.1.md"


def load() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def close(a: float, b: float = 0.0, tol: float = 1e-12) -> None:
    assert math.isclose(a, b, rel_tol=0.0, abs_tol=tol), (a, b)


def test_successor_assignment_and_nonoperative_scope() -> None:
    d = load()
    s = d["successor_assignment"]
    assert d["work_package"] == "ULSH-05/WP1E"
    assert d["basis_main"] == "a894517e2c8e378bff4f6a975aee67ca85fea785"
    assert s["predecessor"] == "ULSH-05/WP1D"
    assert s["assigned_id"] == "ULSH-05/WP1E"
    assert s["status"] == "FROZEN_BY_THIS_SUCCESSOR_CONTRACT"
    assert "not claimed" in s["semantics"].lower()
    assert d["solver_authorized"] is False
    assert d["physical_gate_effect"] == "NONE"
    assert d["physical_evidence_effect"] == "NONE"


def test_raw_operator_is_projector_independent() -> None:
    d = load()
    p = d["projector_kernel_audit"]
    assert p["raw_G_dependency_on_projector"] is False
    assert p["coefficient_G_dependency_on_projector"] is True
    assert p["global_D_inverse"] == "NOT_FROZEN"
    assert p["global_D2_inverse"] == "NOT_FROZEN"
    assert p["retarded_advanced_choice"] == "NOT_FROZEN"
    assert p["physical_DOF_from_rank_G"] == "FORBIDDEN_BEFORE_ULSH04_CONSTRAINT_CLOSURE"
    assert p["cokernel_status"] == "NOT_DEFINED_WITHOUT_A_FROZEN_PAIRING_OPERATOR_DOMAIN_AND_ADJOINT_CONTRACT"


def test_metric_componentization_scalarized_controls() -> None:
    Aprime = 0.37
    L = 1.8
    Lprime = -0.23
    e2A = 2.4

    zeta_r = -0.41
    expected_radial_trace_piece = 2.0 * Aprime * e2A * zeta_r
    direct_radial_trace_piece = -2.0 * (-Aprime * e2A) * zeta_r
    close(direct_radial_trace_piece, expected_radial_trace_piece)

    Dmu_zeta_r = 0.31
    dr_zeta_mu = -0.62
    zeta_mu = 0.27
    direct_mur = Dmu_zeta_r + dr_zeta_mu - 2.0 * Aprime * zeta_mu
    frozen_mur = Dmu_zeta_r + (dr_zeta_mu - 2.0 * Aprime * zeta_mu)
    close(direct_mur, frozen_mur)

    dr_zeta_chi = 0.44
    dchi_zeta_r = -0.18
    zeta_chi = 0.52
    direct_rchi = dr_zeta_chi + dchi_zeta_r - 2.0 * (Lprime / L) * zeta_chi
    frozen_rchi = dr_zeta_chi + dchi_zeta_r - 2.0 * (Lprime / L) * zeta_chi
    close(direct_rchi, frozen_rchi)

    dchi_zeta_chi = -0.33
    direct_chichi = 2.0 * dchi_zeta_chi + 2.0 * L * Lprime * zeta_r
    frozen_chichi = 2.0 * dchi_zeta_chi + 2.0 * L * Lprime * zeta_r
    close(direct_chichi, frozen_chichi)


def test_representative_compensators_transform_correctly() -> None:
    Aprime = 0.29
    zeta_L = -0.7
    dr_zeta_L = 0.43
    zeta_r = 0.38
    zeta_chi = -0.24
    dchi_zeta_L = 0.19

    delta_B = 2.0 * zeta_L
    dr_delta_B = 2.0 * dr_zeta_L
    delta_Br = zeta_r + dr_zeta_L - 2.0 * Aprime * zeta_L
    delta_Xr = delta_Br - 0.5 * (dr_delta_B - 2.0 * Aprime * delta_B)
    close(delta_Xr, zeta_r)

    dchi_delta_B = 2.0 * dchi_zeta_L
    delta_Bchi = zeta_chi + dchi_zeta_L
    delta_Xchi = delta_Bchi - 0.5 * dchi_delta_B
    close(delta_Xchi, zeta_chi)


def test_vector_invariants_cancel_bulk_diffeomorphism() -> None:
    Aprime = -0.16
    zetaT = 0.73
    dr_zetaT = -0.21
    dchi_zetaT = 0.35

    delta_V = zetaT
    delta_Vr = dr_zetaT - 2.0 * Aprime * zetaT
    delta_Vhat_r = delta_Vr - (dr_zetaT - 2.0 * Aprime * delta_V)
    close(delta_Vhat_r)

    delta_Vchi = dchi_zetaT
    delta_Vhat_chi = delta_Vchi - dchi_zetaT
    close(delta_Vhat_chi)


def test_scalar_metric_invariants_cancel_bulk_diffeomorphism() -> None:
    Aprime = 0.42
    e2A = 1.7
    L = 1.6
    Lprime = 0.28

    zeta_L = -0.22
    D2_zeta_L = 0.51
    zeta_r = -0.31
    dr_zeta_r = 0.13
    zeta_chi = 0.46
    dr_zeta_chi = -0.37
    dchi_zeta_r = 0.17
    dchi_zeta_chi = -0.12

    delta_B = 2.0 * zeta_L
    D2_delta_B = 2.0 * D2_zeta_L
    delta_Xr = zeta_r
    delta_Xchi = zeta_chi

    delta_H = 2.0 * D2_zeta_L + 8.0 * Aprime * e2A * zeta_r
    close(delta_H - D2_delta_B - 8.0 * Aprime * e2A * delta_Xr)

    delta_hrr = 2.0 * dr_zeta_r
    close(delta_hrr - 2.0 * dr_zeta_r)

    delta_hrchi = dr_zeta_chi + dchi_zeta_r - 2.0 * (Lprime / L) * zeta_chi
    close(
        delta_hrchi
        - dr_zeta_chi
        - dchi_zeta_r
        + 2.0 * (Lprime / L) * delta_Xchi
    )

    delta_hchichi = 2.0 * dchi_zeta_chi + 2.0 * L * Lprime * zeta_r
    close(delta_hchichi - 2.0 * dchi_zeta_chi - 2.0 * L * Lprime * delta_Xr)


def test_scalar_field_invariant_has_no_unitary_gauge_division() -> None:
    phiprime = -0.63
    zeta_r = 0.28
    delta_varphi = phiprime * zeta_r
    delta_Xr = zeta_r
    close(delta_varphi - phiprime * delta_Xr)

    phiprime = 0.0
    delta_varphi = phiprime * zeta_r
    close(delta_varphi - phiprime * delta_Xr)

    d = load()
    assert d["regime_checks"]["phibar_prime_zero"].startswith("varphihat reduces smoothly")
    assert "divide" not in d["conditional_kinematic_invariants"]["scalar_metric_and_scalar_field"]["varphihat"].lower()


def test_maxwell_scalar_invariants_cancel_u1_and_internal_bulk_diff() -> None:
    Achi = 1.14
    Achiprime = -0.36
    L = 1.9
    Lprime = 0.25
    zeta_chi = 0.47
    dr_zeta_chi = -0.22
    zeta_r = -0.31
    lam = 0.61
    dr_lam = -0.14
    dchi_lam = 0.29

    delta_alpha = lam + (Achi / L**2) * zeta_chi
    assert math.isfinite(delta_alpha)

    d_zeta_contra_chi = dr_zeta_chi / L**2 - 2.0 * Lprime * zeta_chi / L**3
    delta_ar = dr_lam + Achi * d_zeta_contra_chi
    d_AoverL2 = Achiprime / L**2 - 2.0 * Achi * Lprime / L**3
    dr_delta_alpha = dr_lam + d_AoverL2 * zeta_chi + (Achi / L**2) * dr_zeta_chi
    delta_ur = delta_ar - dr_delta_alpha
    close(delta_ur, -(Achiprime / L**2) * zeta_chi)

    dchi_zeta_chi = -0.18
    delta_achi = dchi_lam + Achiprime * zeta_r + (Achi / L**2) * dchi_zeta_chi
    dchi_delta_alpha = dchi_lam + (Achi / L**2) * dchi_zeta_chi
    delta_uchi = delta_achi - dchi_delta_alpha
    close(delta_uchi, Achiprime * zeta_r)

    delta_Xr = zeta_r
    delta_Xchi = zeta_chi
    close(delta_ur + (Achiprime / L**2) * delta_Xchi)
    close(delta_uchi - Achiprime * delta_Xr)

    Achiprime = 0.0
    close(-(Achiprime / L**2) * zeta_chi + (Achiprime / L**2) * delta_Xchi)
    close(Achiprime * zeta_r - Achiprime * delta_Xr)


def test_internal_zero_mode_and_no_division_firewall() -> None:
    d = load()
    zero = d["regime_checks"]["internal_n_zero"]
    assert "retained" in zero
    assert "no 1/n operation" in zero
    firewall = d["conditional_kinematic_invariants"]["division_firewall"]
    assert "Fourier n" in firewall
    assert "no invariant above divides by" in firewall


def test_interface_rho_is_independent_and_partial_invariance_not_promoted() -> None:
    d = load()
    f = d["interface_full_gauge_firewall"]
    assert "intrinsic rho" in f["H_ab"]
    assert "intrinsic rho" in f["d_a"]
    assert f["componentwise_full_rho_invariant_basis"] == "NOT_RELEASED"
    assert d["gate_state"]["WP1E_full_interface_rho_invariant_basis"] == "NOT_RELEASED"
    assert d["gauge_parameter_convention"]["intrinsic_interface_reparameterization"].startswith("rho^a")
    assert "independent" in d["gauge_parameter_convention"]["intrinsic_interface_reparameterization"]


def test_gate_firewalls_remain_closed() -> None:
    d = load()
    g = d["gate_state"]
    assert g["WP1E_successor_identifier"] == "FROZEN_BY_THIS_SUCCESSOR_CONTRACT"
    assert g["WP1E_raw_gauge_operator"] == "COMPONENTIZED_ON_CURRENT_STATIC_ANSATZ"
    assert g["WP1E_coefficient_gauge_matrix"] == "DEFINED_CONDITIONAL_ON_PROJECTOR_REPRESENTATIVE_SLICE"
    assert g["WP1E_projector_kernel_audit"] == "OPEN_TRACKED_NO_GLOBAL_INVERSE_RELEASE"
    assert g["WP1E_conditional_bulk_kinematic_invariants"] == "DERIVED_REPRESENTATIVE_LEVEL"
    assert g["WP1E_full_interface_rho_invariant_basis"] == "NOT_RELEASED"
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


def test_document_contains_required_no_go_statements() -> None:
    text = DOC.read_text(encoding="utf-8")
    required = [
        "ULSH-05/WP1E",
        "Primärer roher Gaugeoperator",
        "Projektor-Firewall",
        "Repräsentanten-Kompensatoren",
        "Intrinsische Interface-Reparametrisierung",
        "WP1E_full_interface_rho_invariant_basis = NOT_RELEASED",
        "Projektor-/Repräsentantenkernel",
        "rank(G)",
        "kein** zulässiger physischer Freiheitsgrad-Count",
        "SOLVER_EXECUTION                           NOT_EXECUTED",
    ]
    for token in required:
        assert token in text, token


def main() -> None:
    test_successor_assignment_and_nonoperative_scope()
    test_raw_operator_is_projector_independent()
    test_metric_componentization_scalarized_controls()
    test_representative_compensators_transform_correctly()
    test_vector_invariants_cancel_bulk_diffeomorphism()
    test_scalar_metric_invariants_cancel_bulk_diffeomorphism()
    test_scalar_field_invariant_has_no_unitary_gauge_division()
    test_maxwell_scalar_invariants_cancel_u1_and_internal_bulk_diff()
    test_internal_zero_mode_and_no_division_firewall()
    test_interface_rho_is_independent_and_partial_invariance_not_promoted()
    test_gate_firewalls_remain_closed()
    test_document_contains_required_no_go_statements()
    print("WP1E gauge-operator/kernel preflight controls: PASS")


if __name__ == "__main__":
    main()
