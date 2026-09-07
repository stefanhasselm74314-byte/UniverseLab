#!/usr/bin/env python3
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

READINESS = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1_QuadraticActionReadiness_v0.1.json"
PARENT = ROOT / "hzt-s6-parent-action-v0.1.json"
FREEZE = ROOT / "registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json"
G01 = ROOT / "registry/2026-09-07_UniverseLab_BandVC_G01_PerturbationObservableInventory_v1.0.json"
ROADMAP = ROOT / "science/solver-hub/2026-08-07_ULSH-05_SVT-Perturbation_Roadmap_v1.0.md"
NOTE = ROOT / "science/solver-hub/2026-09-07_UniverseLab_ULSH05_WP1_QuadraticActionReadiness_v0.1.md"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def inventory_status(g01, item):
    matches = [row for row in g01["inventory"] if row["item"] == item]
    assert len(matches) == 1, f"missing/duplicate G01 inventory item: {item}"
    return matches[0]["status"]


def finite_difference_first(fn, x, h=1e-6):
    return (fn(x + h) - fn(x - h)) / (2.0 * h)


def finite_difference_second(fn, x, h=1e-4):
    return (fn(x + h) - 2.0 * fn(x) + fn(x - h)) / (h * h)


def main():
    r = load(READINESS)
    p = load(PARENT)
    f = load(FREEZE)
    g = load(G01)
    roadmap = ROADMAP.read_text(encoding="utf-8")
    note = NOTE.read_text(encoding="utf-8")

    # Identity and scope stay on the one-time controlled C-PHYS-M1 branch.
    assert r["model_id"] == "HZT-M0-S6-C-PHYS-M1"
    assert p["branch"] == "HZT-M0-S6"
    assert p["signature"] == "(-,+,+,+,+,+)"
    assert f["model_id"] == "HZT-M0-S6-C-PHYS-M1"
    assert r["classification"] == "NONOPERATIVE_ANALYTIC_READINESS_FREEZE"
    assert r["physical_gate_effect"] == "NONE"
    assert r["physical_evidence_effect"] == "NONE"
    assert r["solver_authorized"] is False

    # Parent/action functions needed for an off-shell Hessian are actually frozen.
    sectors = p["action_sectors"]
    assert sectors["bulk_Einstein_Hilbert"] == "included"
    assert sectors["bulk_scalar"] == "included"
    assert sectors["bulk_Maxwell_flux"] == "included"
    assert sectors["GHY_each_region"] == "included"
    assert sectors["cap_tension"] == "included"
    assert sectors["cap_winding_phase"] == "conditional"

    assert f["gate_state"]["MF_001_BULK_FUNCTIONS"] == "FROZEN_FOR_C_PHYS_M1"
    assert f["gate_state"]["MF_002_CAP_FUNCTIONS"] == "FROZEN_FOR_C_PHYS_M1"
    assert f["field_and_unit_conventions"]["scalar_domain"] == "R"
    assert f["exact_functions"]["U"]["formula"] == "U(phi)=0.5*mhat_phi_sq*M6^6*varphi^2"
    assert f["exact_functions"]["Z_F"]["formula"] == "Z_F(phi)=exp(-2*a_F*varphi)"
    assert f["exact_functions"]["lambda"]["formula"] == "lambda(phi)=lambda_hat*M6^5"
    assert f["exact_functions"]["Z_sigma"]["formula"] == "Z_sigma(phi)=z_sigma_hat*M6^3"

    # Independent numerical check of the algebraic M1 derivative kernels.
    M6 = 2.3
    m2 = 1.7
    aF = 0.41
    phi0 = 0.83

    def U(phi):
        varphi = phi / (M6 * M6)
        return 0.5 * m2 * M6**6 * varphi**2

    def ZF(phi):
        return math.exp(-2.0 * aF * phi / (M6 * M6))

    U1 = m2 * M6**2 * phi0
    U2 = m2 * M6**2
    Z1 = (-2.0 * aF / M6**2) * ZF(phi0)
    Z2 = (4.0 * aF**2 / M6**4) * ZF(phi0)

    assert math.isclose(finite_difference_first(U, phi0), U1, rel_tol=2e-9, abs_tol=2e-9)
    assert math.isclose(finite_difference_second(U, phi0), U2, rel_tol=2e-7, abs_tol=2e-7)
    assert math.isclose(finite_difference_first(ZF, phi0), Z1, rel_tol=2e-9, abs_tol=2e-9)
    assert math.isclose(finite_difference_second(ZF, phi0), Z2, rel_tol=2e-7, abs_tol=2e-7)

    # Readiness must not be mislabeled as a derived physical quadratic system.
    state = r["readiness_state"]
    assert state["action_data_for_offshell_second_variation"] == "READY_TO_DERIVE"
    assert state["full_S_quad_2"] == "NOT_DERIVED"
    assert state["EH_plus_GHY_second_variation"] == "NOT_DERIVED"
    assert state["bulk_scalar_Maxwell_second_variation"] == "NOT_DERIVED"
    assert state["cap_and_perturbed_junction_second_variation"] == "NOT_DERIVED"
    assert state["cap_bending_or_interface_gauge"] == "MISSING_REQUIRED_LINK"
    assert state["released_physical_background"] == "NOT_ESTABLISHED"
    assert state["on_shell_quadratic_action"] == "BLOCKED_BY_PHYSICAL_BACKGROUND_NOT_ESTABLISHED"
    assert state["matter_Delta_m_definition_and_coupling"] == "MISSING_REQUIRED_LINK"
    assert state["sixD_to_fourD_perturbative_reduction"] == "MISSING_REQUIRED_LINK"
    assert state["mu_eta_Sigma_growth_lensing_map"] == "UNRELEASED"

    # G01 remains the authoritative missing-link statement for matter/observable coupling.
    assert inventory_status(g, "matter_perturbation_Delta_m_definition_and_coupling_for_HZT") == "MISSING_REQUIRED_LINK"
    assert inventory_status(g, "sixD_to_4d_perturbative_reduction".replace("4d", "4d")) == "MISSING_REQUIRED_LINK"
    assert inventory_status(g, "effective_poisson_mu_k_a") == "MISSING_REQUIRED_LINK"
    assert inventory_status(g, "gravitational_slip_eta_k_a") == "MISSING_REQUIRED_LINK"
    assert inventory_status(g, "lensing_Sigma_k_a") == "MISSING_REQUIRED_LINK"

    # ULSH-05 itself still says the quadratic structure is not closed.
    assert "`PLANNED`" in roadmap
    assert "quadratische Wirkungsstruktur ist noch nicht vollständig geschlossen" in roadmap
    assert "Zweite Variation `S^(2)`" in roadmap

    # The scientific note must explicitly retain the boundary and observable blockers.
    assert "PREPARATORY_READY_TO_DERIVE_NOT_CLOSED" in note
    assert "Cap-Bending" in note
    assert "UNRELEASED_GROWTH_MAP" in note
    assert "UNRELEASED_LENSING_MAP" in note

    # Global safety firewalls are unchanged.
    fw = r["unchanged_firewalls"]
    assert fw["FM-G0"] == "OPEN"
    assert fw["AuthorizationDecision"] == "NOT_CREATED"
    assert fw["SingleUseGrant"] == "NOT_CREATED"
    assert fw["BACKEND_IMPORT"] == "NOT_EXECUTED"
    assert fw["SOLVER_EXECUTION"] == "NOT_EXECUTED"
    assert fw["PHYSICAL_BACKGROUND"] == "NOT_ESTABLISHED"
    assert fw["PHYSICAL_RESPONSE_RANK"] == "NOT_EXECUTED"
    assert fw["K1-D"] == "NOT_RELEASED"
    assert fw["K1-E"] == "NOT_ADMISSIBLE"

    # The frozen perturbative action must retain the same project-level physical non-release.
    assert f["gate_state"]["physical_background"] == "NOT_ESTABLISHED"
    assert f["gate_state"]["perturbative_stability"] == "OPEN"
    assert f["gate_state"]["ghost_freedom"] == "OPEN"
    assert f["gate_state"]["official_MD2S_solver"] == "NOT_AUTHORIZED"
    assert f["gate_state"]["K1-D"] == "NOT_RELEASED"
    assert f["gate_state"]["K1-E"] == "NOT_ADMISSIBLE"

    print("PASS: ULSH-05/WP1 action-side readiness frozen without quadratic/physical release")


if __name__ == "__main__":
    main()
