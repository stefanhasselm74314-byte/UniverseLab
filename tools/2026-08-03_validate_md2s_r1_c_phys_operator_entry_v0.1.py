#!/usr/bin/env python3
"""Fail-closed validator for the MD2S-R1-C-PHYS operator-entry contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registry" / "2026-08-03_MD2S_R1_C_PHYS_ParentActionOperatorEntryContract_v0.1.json"
LEDGER_PATH = ROOT / "science" / "hzt-m0" / "md2s" / "2026-08-03_MD2S_R1_C_PHYS_ParentActionOperatorEntryLedger_v0.1.md"


class ContractError(RuntimeError):
    """Raised when a C-PHYS entry invariant is violated."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing required artifact: {path.relative_to(ROOT)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON: {exc}") from exc
    require(isinstance(payload, dict), "top-level JSON object required")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_pole_coefficients() -> dict[str, float]:
    """Numerically regress the declared leading pole coefficients.

    This is an algebraic consistency check of the generic formulas only. It is
    not a physical background solve and does not use C1-V as a source.
    """

    m6_four = 2.3
    k4 = 0.071
    a0 = 0.13
    lambda6 = 0.019
    potential = 0.41
    rho_flux = 0.083
    potential_phi = -0.037
    dlog_zf = 0.24
    alpha = 0.92
    q = 0.31
    zf = 1.17

    curvature = k4 * math.exp(-2.0 * a0)
    a2 = (
        6.0 * curvature
        - lambda6
        + (-potential + rho_flux) / m6_four
    ) / 8.0
    f2 = (potential_phi + rho_flux * dlog_zf) / 4.0
    g2 = q * alpha * math.exp(-4.0 * a0) / (2.0 * zf)
    l3 = alpha * (
        3.0 * curvature
        - 12.0 * a2
        - lambda6
        + (-potential - rho_flux) / m6_four
    ) / 6.0

    chi_residual = m6_four * (
        -6.0 * curvature + 8.0 * a2 + lambda6
    ) - (-potential + rho_flux)
    scalar_residual = 4.0 * f2 - potential_phi - rho_flux * dlog_zf
    gauge_residual = 2.0 * g2 - q * alpha * math.exp(-4.0 * a0) / zf
    external_residual = m6_four * (
        -3.0 * curvature + 12.0 * a2 + 6.0 * l3 / alpha + lambda6
    ) - (-potential - rho_flux)

    tolerance = 1.0e-12
    require(abs(chi_residual) <= tolerance, "pole a2 coefficient fails chi-chi equation")
    require(abs(scalar_residual) <= tolerance, "pole f2 coefficient fails scalar equation")
    require(abs(gauge_residual) <= tolerance, "pole g2 coefficient fails Maxwell equation")
    require(abs(external_residual) <= tolerance, "pole l3 coefficient fails mu-nu equation")

    return {
        "chi_residual": chi_residual,
        "scalar_residual": scalar_residual,
        "gauge_residual": gauge_residual,
        "external_residual": external_residual,
    }


def validate_anisotropy_identity() -> float:
    """Check the algebraic difference of the two metric junctions."""

    m6_four = 1.9
    a_sum = 0.14
    l_sum = -0.06
    y_sigma = m6_four * (l_sum - a_sum)
    tension = 4.0 * m6_four * a_sum + 0.5 * y_sigma

    r_4d = m6_four * (-3.0 * a_sum - l_sum) + tension + 0.5 * y_sigma
    r_chi = -4.0 * m6_four * a_sum + tension - 0.5 * y_sigma
    require(abs(r_4d) <= 1.0e-12, "4D junction does not close under anisotropy identity")
    require(abs(r_chi) <= 1.0e-12, "chi junction does not close under anisotropy identity")
    return max(abs(r_4d), abs(r_chi))


def validate() -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    require(LEDGER_PATH.is_file(), "missing derivation ledger")

    require(contract["track_id"] == "MD2S-R1-C-PHYS", "wrong track")
    require(contract["phase"] == "R1.0", "operator entry must remain in R1.0")
    require(
        contract["status"] == "CONTINUUM_OPERATOR_SCAFFOLD_DEFINED_MODEL_FREEZE_INCOMPLETE",
        "unexpected primary status",
    )
    require(contract["evidence_effect"] == "NONE", "evidence effect must remain NONE")
    require(contract["physical_evidence_effect"] == "NONE", "physical evidence effect must remain NONE")
    require(contract["solver_authorized"] is False, "solver authorization is forbidden")

    firewall = contract["track_firewall"]
    require(firewall["historical_A0_identity"] == "NOT_CLAIMED", "historical identity drift")
    require(firewall["C1_V_equations_used_as_physical_source"] is False, "C1-V source migration forbidden")
    require(firewall["legacy_benchmarks_used_to_fix_parameters"] is False, "benchmark reverse fitting forbidden")
    require(firewall["verification_to_physics_bridge"] == "NOT_DEFINED", "unexpected verification bridge")

    action = contract["parent_action"]
    require(action["scalar_kinetic_function"] == "Z_phi=1_FROZEN_FOR_THIS_MINIMAL_BRANCH", "minimal scalar kinetic drift")
    require(action["Gauss_Bonnet"] == "EXCLUDED_FROM_THIS_CONTRACT", "Gauss-Bonnet leakage")

    equations = contract["regularized_bulk_equations"]
    require(set(equations) >= {"E_A", "E_L", "E_phi", "E_gauge", "status"}, "bulk equation set incomplete")
    require(equations["status"] == "DERIVED_GENERIC_NOT_MODEL_CLOSED", "bulk status drift")

    constraint = contract["radial_constraint"]
    require(constraint["dependency_proof"] == "OPEN", "constraint dependency cannot be silently closed")
    require(constraint["must_not_be_double_counted"] is True, "constraint double-count firewall missing")

    cap = contract["cap_and_global_system"]
    require(cap["gauge_patch_transition_rule"] == "OPEN", "patch rule must remain open")
    require(cap["q_ref_equals_q_sigma"] == "NOT_ASSUMED", "charge identity must not be assumed")

    operator = contract["continuum_operator_scaffold"]
    require(operator["square_count"].startswith("OPEN_"), "BVP square count must remain open")
    require(operator["Freholm_status"] == "NOT_PROVEN", "Fredholm status drift")
    require(operator["continuum_Jacobian"] == "NOT_CONSTRUCTED", "continuum Jacobian drift")
    require(operator["implicit_function_theorem"] == "NOT_ADMISSIBLE", "IFT must remain inadmissible")

    closure = contract["model_freeze_closure_matrix"]
    require(set(closure) == {f"MF-00{i}" for i in range(1, 8)}, "MF closure matrix incomplete")
    require(closure["MF-003"]["status"] == "PARTIAL_DERIVED_CONDITIONAL", "MF-003 overclaim")
    require(closure["MF-005"]["status"] == "PARTIAL_DERIVED_CONDITIONAL", "MF-005 overclaim")

    gates = contract["gate_state"]
    expected = {
        "R1.0": "ACTIVE_MODEL_FREEZE_INCOMPLETE",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "continuum_BVP_operator": "SCAFFOLD_ONLY",
        "continuum_BVP_Jacobian": "NOT_PROVEN",
        "perturbative_stability": "OPEN",
        "ghost_freedom": "OPEN",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    require(gates == expected, "immutable gate state drift")

    next_block = contract["next_block"]
    require(next_block["id"] == "C-PHYS-R1.0-FREEZE-1", "wrong next block")
    require(next_block["execution_type"] == "SOURCE_AND_GOVERNANCE_CLOSURE_ONLY", "next block scope drift")

    pole_check = validate_pole_coefficients()
    junction_check = validate_anisotropy_identity()

    return {
        "status": "PASS",
        "contract": "MD2S_R1_C_PHYS_PARENT_ACTION_OPERATOR_ENTRY_V0_1",
        "track_id": contract["track_id"],
        "phase": contract["phase"],
        "gate_state": gates,
        "pole_coefficient_regression": pole_check,
        "junction_identity_residual": junction_check,
        "contract_sha256": sha256(CONTRACT_PATH),
        "ledger_sha256": sha256(LEDGER_PATH),
        "next_block": next_block,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()
    try:
        result = validate()
    except ContractError as exc:
        if args.json:
            print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2))
        else:
            print(f"C_PHYS_OPERATOR_ENTRY = FAIL: {exc}")
        return 1

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("C_PHYS_OPERATOR_ENTRY = PASS")
        print("R1.1 = BLOCKED")
        print("OFFICIAL_MD2S_SOLVER = NOT_AUTHORIZED")
        print("K1-D = NOT_RELEASED")
        print("K1-E = NOT_ADMISSIBLE")
        print("PHYSICAL_EVIDENCE_EFFECT = NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
