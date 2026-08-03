#!/usr/bin/env python3
"""Fail-closed validator for the C-PHYS global convention freeze."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-08-03_MD2S_R1_C_PHYS_GlobalConventionFreezeContract_v0.1.json"
LEDGER = ROOT / "science/hzt-m0/md2s/2026-08-03_MD2S_R1_C_PHYS_GlobalConventionFreezeLedger_v0.1.md"


class ContractError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def load() -> dict[str, Any]:
    require(CONTRACT.is_file(), "missing convention contract")
    require(LEDGER.is_file(), "missing convention ledger")
    payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(isinstance(payload, dict), "contract root must be an object")
    return payload


def flux_patch_regression() -> dict[str, float]:
    q_ref = 0.37
    n_flux = 3
    a_n_cap = 1.21
    a_s_cap = a_n_cap - n_flux / q_ref
    delta_chi = 2.0 * math.pi

    flux_oriented = delta_chi * (a_n_cap - a_s_cap)
    flux_residual = q_ref * flux_oriented - 2.0 * math.pi * n_flux
    patch_residual = a_n_cap - a_s_cap - n_flux / q_ref

    require(abs(flux_residual) <= 1.0e-12, "oriented flux does not reproduce quantization")
    require(abs(patch_residual) <= 1.0e-12, "patch transition does not reproduce bundle condition")
    return {
        "oriented_flux": flux_oriented,
        "flux_residual": flux_residual,
        "patch_residual": patch_residual,
    }


def charge_lattice_regression() -> dict[str, float]:
    q_ref = 0.23
    m_sigma = 4
    n_flux = 5
    q_sigma = m_sigma * q_ref
    delta_lambda = 2.0 * math.pi * n_flux / q_ref
    phase_increment = q_sigma * delta_lambda
    winding_integer = phase_increment / (2.0 * math.pi)
    require(abs(winding_integer - m_sigma * n_flux) <= 1.0e-12, "charge lattice is not single-valued")
    return {
        "q_sigma": q_sigma,
        "phase_increment_over_2pi": winding_integer,
    }


def validate() -> dict[str, Any]:
    data = load()
    require(data["track_id"] == "MD2S-R1-C-PHYS", "wrong track")
    require(data["block"] == "C-PHYS-R1.0-FREEZE-1A", "wrong block")
    require(
        data["status"] == "GLOBAL_CONVENTIONS_AND_PARAMETER_ROLES_FROZEN_FUNCTIONS_OPEN",
        "status drift",
    )
    require(data["physical_evidence_effect"] == "NONE", "physical evidence drift")
    require(data["solver_authorized"] is False, "solver authorization forbidden")

    firewall = data["track_firewall"]
    require(firewall["C1_V_parameter_values_migrated"] is False, "C1-V parameter migration")
    require(firewall["C1_V_functional_forms_migrated"] is False, "C1-V function migration")

    angular = data["angular_convention"]
    require(angular["Delta_chi"] == "2*pi", "angular convention drift")
    require(angular["conical_defect_at_poles"] == "FORBIDDEN", "conical defect leakage")

    orientation = data["regional_coordinates_and_orientations"]
    require(orientation["outward_boundary_normals_in_local_coordinates"] == {"n_N^r": 1, "n_S^r": 1}, "normal table drift")
    require(orientation["global_two_form_orientation_signs"] == {"epsilon_N": 1, "epsilon_S": -1}, "global orientation drift")

    patch = data["regular_gauge_and_patch_contract"]
    require(patch["patch_residual"].endswith("N_F/q_ref=0"), "patch residual drift")
    require(patch["status"] == "FROZEN_BY_U1_BUNDLE_CONSISTENCY", "patch status drift")

    flux = data["global_flux_contract"]
    require("-integral_0^rho_S" in flux["oriented_flux"], "south orientation sign missing")
    require("counted once" in flux["equivalence"], "patch/flux deduplication missing")

    charges = data["charge_lattice"]
    require(charges["cap_charge"] == "q_sigma=m_sigma*q_ref", "charge lattice drift")
    require(charges["m_sigma_domain"] == "positive_integer", "charge integer domain drift")
    require(charges["q_ref_equals_q_sigma"] == "ONLY_IF_m_sigma_EQUALS_1", "charge identity overclaim")

    frame = data["four_dimensional_frame"]
    require(frame["condition"] == "A_N(0)=0", "frame drift")
    require(frame["A_S(0)"] == "CONTINUOUS_SHOOTING_UNKNOWN", "south warp overfixing")
    require(frame["must_not_also_fix_A_S_0"] is True, "double frame fixing allowed")

    unknowns = data["continuous_unknown_roles"]
    require(unknowns["count"] == 8, "continuous unknown count drift")
    require(len(unknowns["shooting_or_eigen_unknowns"]) == 8, "unknown list size drift")
    require(len(data["independent_boundary_residuals"]) == 8, "residual count drift")

    bvp = data["structural_BVP_count"]
    require(bvp["continuous_unknowns"] == bvp["independent_boundary_residuals"] == 8, "BVP is not square")
    require(bvp["status"] == "SQUARE_COUNT_STRUCTURALLY_CLOSED_CONDITIONAL_ON_FUNCTION_FREEZE", "BVP status overclaim")

    function_class = data["admissible_function_class"]
    require(function_class["exact_forms"] == "OPEN_REQUIRES_VERSIONED_MODEL_SELECTION", "functions silently frozen")
    require("strictly positive" in function_class["Z_F"], "Z_F positivity missing")
    require("strictly positive" in function_class["Z_sigma"], "Z_sigma positivity missing")

    gates = data["gate_state"]
    expected = {
        "R1.0": "ACTIVE_FUNCTION_FREEZE_REMAINING",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "structural_BVP_count": "SQUARE_CONDITIONAL",
        "continuum_BVP_operator": "SCAFFOLD_ONLY",
        "continuum_BVP_Jacobian": "NOT_PROVEN",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    require(gates == expected, "gate state drift")
    require(data["next_block"]["id"] == "C-PHYS-R1.0-FREEZE-1B", "wrong next block")
    require(data["next_block"]["execution_type"] == "VERSIONED_MODEL_SELECTION_NOT_DERIVATION", "model-selection scope drift")

    return {
        "status": "PASS",
        "contract": "MD2S_R1_C_PHYS_GLOBAL_CONVENTION_FREEZE_V0_1",
        "track_id": data["track_id"],
        "block": data["block"],
        "flux_patch_regression": flux_patch_regression(),
        "charge_lattice_regression": charge_lattice_regression(),
        "gate_state": gates,
        "next_block": data["next_block"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = validate()
    except ContractError as exc:
        if args.json:
            print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2))
        else:
            print(f"C_PHYS_GLOBAL_CONVENTION_FREEZE = FAIL: {exc}")
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("C_PHYS_GLOBAL_CONVENTION_FREEZE = PASS")
        print("R1.1 = BLOCKED")
        print("OFFICIAL_MD2S_SOLVER = NOT_AUTHORIZED")
        print("K1-D = NOT_RELEASED")
        print("K1-E = NOT_ADMISSIBLE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
