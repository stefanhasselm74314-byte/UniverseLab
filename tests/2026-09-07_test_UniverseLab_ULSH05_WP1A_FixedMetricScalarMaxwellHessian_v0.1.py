#!/usr/bin/env python3
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1A_FixedMetricScalarMaxwellHessian_v0.1.json"
FREEZE = ROOT / "registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json"
READINESS = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1_QuadraticActionReadiness_v0.1.json"
G01 = ROOT / "registry/2026-09-07_UniverseLab_BandVC_G01_PerturbationObservableInventory_v1.0.json"
NOTE = ROOT / "science/solver-hub/2026-09-07_UniverseLab_ULSH05_WP1A_FixedMetricScalarMaxwellHessian_v0.1.md"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def local_exact_lagrangian(eps, M6, m2, aF, phi0, v, X0, X1, X2, Y0, Y1, Y2):
    phi = phi0 + eps * v
    grad_sq = X0 + 2.0 * eps * X1 + eps * eps * X2
    F_sq = Y0 + 2.0 * eps * Y1 + eps * eps * Y2
    varphi_bg = phi / (M6 * M6)
    U = 0.5 * m2 * M6**6 * varphi_bg**2
    Z = math.exp(-2.0 * aF * phi / (M6 * M6))
    return -0.5 * grad_sq - U - 0.25 * Z * F_sq


def derived_quadratic_coefficient(M6, m2, aF, phi0, v, X2, Y0, Y1, Y2):
    Z0 = math.exp(-2.0 * aF * phi0 / (M6 * M6))
    Mvv = m2 * M6**2 + (aF * aF / M6**4) * Z0 * Y0
    Cvf = (aF / M6**2) * Z0
    return -0.5 * X2 - 0.5 * Mvv * v * v - 0.25 * Z0 * Y2 + Cvf * v * Y1


def central_quadratic_coefficient(fn, eps=1e-4):
    # If L(e)=L0+e L1+e^2 L2+..., then this returns L2+O(e^2).
    return (fn(eps) + fn(-eps) - 2.0 * fn(0.0)) / (2.0 * eps * eps)


def inventory_status(g01, item):
    rows = [row for row in g01["inventory"] if row["item"] == item]
    assert len(rows) == 1, f"missing/duplicate G01 item: {item}"
    return rows[0]["status"]


def main():
    c = load(CONTRACT)
    f = load(FREEZE)
    r = load(READINESS)
    g = load(G01)
    note = NOTE.read_text(encoding="utf-8")

    assert c["model_id"] == "HZT-M0-S6-C-PHYS-M1"
    assert c["classification"] == "NONOPERATIVE_ANALYTIC_CONTROL_SUBSECTOR"
    assert c["status"] == "DERIVED_CONTROL_SUBSECTOR_OFFSHELL_FIXED_METRIC_BULK_INTERIOR"
    assert c["physical_gate_effect"] == "NONE"
    assert c["physical_evidence_effect"] == "NONE"
    assert c["solver_authorized"] is False

    scope = c["scope_contract"]
    assert "h_AB=0" in scope["metric"]
    assert scope["cap_and_junction_terms"] == "excluded_from_WP1A"
    assert scope["GHY"] == "excluded_from_WP1A_because_metric_is_fixed"
    assert "compactly supported" in scope["test_perturbations"]
    assert scope["U1_gauge"].startswith("retained")

    # The source function family used by the derivation must be exactly the frozen M1 family.
    assert f["exact_functions"]["U"]["formula"] == "U(phi)=0.5*mhat_phi_sq*M6^6*varphi^2"
    assert f["exact_functions"]["Z_F"]["formula"] == "Z_F(phi)=exp(-2*a_F*varphi)"

    # Independent coefficient extraction from the original local Lagrangian.
    samples = [
        # Includes positive Fbar^2.
        (2.3, 1.7, 0.41, 0.83, 0.67, 1.2, -0.7, 0.9, 2.4, 0.6, 1.1),
        # Includes negative Fbar^2 to ensure no hidden positivity assumption.
        (1.8, 0.9, 0.20, -0.5, -0.4, -2.0, 0.3, 1.5, -3.2, -0.8, 2.1),
        (3.1, 2.2, 0.70, 1.1, 1.3, 0.2, 1.4, -0.9, 0.4, 2.3, -1.7),
    ]

    for sample in samples:
        M6, m2, aF, phi0, v, X0, X1, X2, Y0, Y1, Y2 = sample
        fn = lambda eps: local_exact_lagrangian(
            eps, M6, m2, aF, phi0, v, X0, X1, X2, Y0, Y1, Y2
        )
        numerical = central_quadratic_coefficient(fn)
        analytic = derived_quadratic_coefficient(M6, m2, aF, phi0, v, X2, Y0, Y1, Y2)
        assert math.isclose(numerical, analytic, rel_tol=2e-7, abs_tol=2e-7), (numerical, analytic, sample)

        # Direct-linearization coefficients must agree with Hessian coefficients.
        Z0 = math.exp(-2.0 * aF * phi0 / (M6 * M6))
        Z1 = (-2.0 * aF / M6**2) * Z0
        Z2 = (4.0 * aF * aF / M6**4) * Z0
        U2 = m2 * M6**2
        scalar_mass_from_parent_linearization = U2 + 0.25 * Z2 * Y0
        scalar_mass_from_hessian = m2 * M6**2 + (aF * aF / M6**4) * Z0 * Y0
        scalar_mix_from_parent_linearization = -0.5 * Z1
        scalar_mix_from_hessian = (aF / M6**2) * Z0
        maxwell_mix_from_parent_linearization = Z1
        maxwell_mix_from_hessian = -(2.0 * aF / M6**2) * Z0
        assert math.isclose(scalar_mass_from_parent_linearization, scalar_mass_from_hessian, rel_tol=1e-14, abs_tol=1e-14)
        assert math.isclose(scalar_mix_from_parent_linearization, scalar_mix_from_hessian, rel_tol=1e-14, abs_tol=1e-14)
        assert math.isclose(maxwell_mix_from_parent_linearization, maxwell_mix_from_hessian, rel_tol=1e-14, abs_tol=1e-14)

    # WP1A advances only the declared control subsector, not the full perturbation package.
    progress = c["wp1_progress_effect"]
    assert progress["bulk_scalar_Maxwell_fixed_metric_control"] == "DERIVED"
    assert progress["full_S_quad_2"] == "NOT_DERIVED"
    assert progress["ULSH05_WP1"] == "PREPARATORY_IN_PROGRESS_NOT_CLOSED"
    assert progress["G01"] == "OPEN_BLOCKING"

    # The prior readiness freeze and G01 missing links must remain intact.
    assert r["readiness_state"]["released_physical_background"] == "NOT_ESTABLISHED"
    assert r["readiness_state"]["EH_plus_GHY_second_variation"] == "NOT_DERIVED"
    assert r["readiness_state"]["cap_and_perturbed_junction_second_variation"] == "NOT_DERIVED"
    assert inventory_status(g, "matter_perturbation_Delta_m_definition_and_coupling_for_HZT") == "MISSING_REQUIRED_LINK"
    assert inventory_status(g, "6d_to_4d_perturbative_reduction") == "MISSING_REQUIRED_LINK"
    assert inventory_status(g, "effective_poisson_mu_k_a") == "MISSING_REQUIRED_LINK"
    assert inventory_status(g, "lensing_Sigma_k_a") == "MISSING_REQUIRED_LINK"

    # Textual firewalls and U(1) statement are part of the scientific artifact.
    assert "U(1)-Gaugeinvarianz" in note
    assert "h_{AB}=0" in note
    assert "NOT_DERIVED" in note
    assert "NOT_ESTABLISHED" in note

    fw = c["unchanged_firewalls"]
    expected = {
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
    assert fw == expected

    print("PASS: WP1A fixed-metric scalar-Maxwell Hessian independently reconstructed and firewalls preserved")


if __name__ == "__main__":
    main()
