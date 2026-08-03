#!/usr/bin/env python3
"""Fail-closed validator for MD2S-R1-C-PHYS Freeze-1B.

This validator checks model-definition consistency only. It does not solve the
boundary-value problem, evaluate a physical background, or authorize any
release gate.
"""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registry/2026-08-03_MD2S_R1_C_PHYS_MinimalEFTFunctionFreezeContract_v0.1.json"
STATUS_PATH = ROOT / "registry/2026-08-03_UniverseLab_C_PHYS_Freeze1B_Status_v0.1.json"
CLAIMS_PATH = ROOT / "registry/2026-08-03_UniverseLab_ClaimRegister_C_PHYS_Freeze1B_v0.1.json"
CHECKPOINT_PATH = ROOT / "registry/2026-08-03_UniverseLab_SessionCheckpoint_v1.11.json"
CHECKPOINT_ALIAS_PATH = ROOT / "registry/session-checkpoint-latest.json"
MANIFEST_PATH = ROOT / "project-manifest.json"
DECISION_LOG_PATH = ROOT / "registry/decision-log.jsonl"
LEDGER_PATH = ROOT / "science/hzt-m0/md2s/2026-08-03_MD2S_R1_C_PHYS_MinimalEFTFunctionFreezeLedger_v0.1.md"


class ContractError(ValueError):
    """Raised when a fail-closed invariant is violated."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def load_json(path: pathlib.Path) -> Any:
    require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def load_decisions() -> list[dict[str, Any]]:
    require(DECISION_LOG_PATH.is_file(), "missing decision log")
    result: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        DECISION_LOG_PATH.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ContractError(
                f"invalid decision JSON at line {line_number}: {exc}"
            ) from exc
        require(isinstance(item, dict), f"decision line {line_number} must be an object")
        result.append(item)
    return result


def validate_function_selection(contract: dict[str, Any]) -> dict[str, Any]:
    require(contract["track_id"] == "MD2S-R1-C-PHYS", "wrong track")
    require(contract["block"] == "C-PHYS-R1.0-FREEZE-1B", "wrong block")
    require(contract["model_family_id"] == "C-PHYS-ME1", "wrong model family")
    require(
        contract["classification"] == "VERSIONED_MODEL_SELECTION_NOT_DERIVATION",
        "classification firewall missing",
    )
    require(contract["evidence_effect"] == "MODEL_DEFINITION_ONLY", "wrong evidence effect")
    require(contract["physical_evidence_effect"] == "NONE", "physical evidence must remain none")
    require(contract["solver_authorized"] is False, "solver must remain unauthorized")

    functions = contract["exact_functions"]
    require(functions["U"]["formula"] == "U(phi)=1/2*m_phi^2*phi^2", "U formula drift")
    require(functions["U"]["coefficient_domain"] == "mu_phi_sq>0", "U mass domain drift")
    require(functions["Z_F"]["formula"] == "Z_F(phi)=1", "Z_F formula drift")
    require(
        functions["lambda"]["formula"] == "lambda(phi)=M6^5*tau*exp(alpha*varphi)",
        "lambda formula drift",
    )
    require(functions["lambda"]["coefficient_domains"]["tau"] == "tau>0", "tau domain drift")
    require(functions["lambda"]["coefficient_domains"]["alpha"] == "alpha>0", "alpha domain drift")
    require(
        functions["Z_sigma"]["formula"] == "Z_sigma(phi)=M6^3*z_sigma",
        "Z_sigma formula drift",
    )
    require(functions["Z_sigma"]["coefficient_domain"] == "z_sigma>0", "z_sigma domain drift")

    domain = contract["field_normalization_and_domain"]
    require(domain["phi_dimension"] == "M^2", "scalar dimension drift")
    require(domain["dimensionless_scalar"] == "varphi=phi/M6^2", "scalar normalization drift")
    require(domain["scalar_domain_varphi"] == "R", "scalar domain must remain R")

    charge = contract["charge_normalization"]
    require(charge["q_ref"] == "1/M6", "q_ref normalization drift")
    require(charge["dimensionless_q_ref"] == "M6*q_ref=1", "dimensionless q_ref drift")
    require(charge["not_a_coordinate_convention"] is True, "q_ref must be labeled physical model normalization")

    # Independent numerical sanity check of the exact selected functions.
    M6 = 2.5
    mu_phi_sq = 0.7
    m_phi_sq = mu_phi_sq * M6 * M6
    tau = 0.4
    alpha = 1.3
    z_sigma = 0.8
    samples = (-4.0, -1.0, 0.0, 0.5, 3.0)
    for varphi in samples:
        phi = varphi * M6 * M6
        U = 0.5 * m_phi_sq * phi * phi
        Z_F = 1.0
        cap_lambda = M6**5 * tau * math.exp(alpha * varphi)
        Z_sigma = M6**3 * z_sigma
        require(math.isfinite(U) and U >= 0.0, "U positivity sample failed")
        require(Z_F > 0.0, "Z_F positivity sample failed")
        require(math.isfinite(cap_lambda) and cap_lambda > 0.0, "lambda positivity sample failed")
        require(Z_sigma > 0.0, "Z_sigma positivity sample failed")

    return {
        "model_family_id": contract["model_family_id"],
        "scalar_domain": domain["scalar_domain_varphi"],
        "q_ref": charge["q_ref"],
    }


def validate_parameter_budget(contract: dict[str, Any]) -> dict[str, Any]:
    budget = contract["parameter_identifiability_budget"]
    expected = [
        "Lambda6_hat=Lambda6/M6^2",
        "mu_phi_sq=m_phi^2/M6^2",
        "tau",
        "alpha",
        "z_sigma",
    ]
    require(
        budget["continuous_dimensionless_model_parameters"] == expected,
        "continuous model parameter list drift",
    )
    require(budget["continuous_model_parameter_count"] == 5, "model parameter count must be five")
    require(budget["continuous_shooting_unknown_count"] == 8, "shooting count must remain eight")
    require(budget["independent_boundary_residual_count"] == 8, "boundary residual count must remain eight")
    require(
        budget["structural_count"] == "SQUARE_FUNCTIONALLY_SPECIALIZED_CONDITIONAL",
        "structural count label drift",
    )
    require(budget["fit_authorized"] is False, "parameter fitting must remain unauthorized")

    redundancy = contract["minimality_and_redundancy_audit"]
    removed = " ".join(redundancy["removed_exact_redundancies"])
    require("U0" in removed and "Lambda6" in removed, "U0-Lambda6 redundancy not recorded")
    require("alpha" in removed and "phi->-phi" in removed, "alpha sign redundancy not recorded")
    require(
        "Patch and flux residuals are counted once." in redundancy["removed_exact_redundancies"],
        "patch-flux single counting missing",
    )
    return {
        "continuous_model_parameters": 5,
        "shooting_unknowns": 8,
        "boundary_residuals": 8,
    }


def validate_firewalls(contract: dict[str, Any], status: dict[str, Any]) -> dict[str, str]:
    firewall = contract["track_firewall"]
    require(firewall["historical_A0_identity"] == "NOT_CLAIMED", "historical firewall failed")
    require(firewall["C1_V_parameter_values_migrated"] is False, "C1-V parameter migration")
    require(firewall["C1_V_functional_forms_migrated"] is False, "C1-V function migration")
    require(firewall["observational_fit_used_to_select_functions"] is False, "observational fit migration")

    gates = contract["gate_state"]
    expected = {
        "R1.0": "ACTIVE_MODEL_FREEZE_INCOMPLETE",
        "R1.0_substate": "FUNCTION_FAMILY_FROZEN_BENCHMARK_INSTANCE_OPEN",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "continuum_BVP_operator": "SCAFFOLD_ONLY",
        "continuum_BVP_Jacobian": "NOT_PROVEN",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected.items():
        require(gates[key] == value, f"gate drift in contract: {key}")
        require(status["gate_state"][key] == value, f"gate drift in status: {key}")

    positivity = contract["positivity_and_boundedness_audit"]
    require(positivity["U_bounded_below"] is True, "U boundedness audit failed")
    require(positivity["Z_F_strictly_positive"] is True, "Z_F positivity audit failed")
    require(positivity["lambda_strictly_positive"] is True, "lambda positivity audit failed")
    require(positivity["Z_sigma_strictly_positive"] is True, "Z_sigma positivity audit failed")
    require(positivity["background_ghost_freedom_proven"] is False, "ghost freedom overclaim")
    require(positivity["perturbative_stability_proven"] is False, "stability overclaim")
    return expected


def validate_claims(claims: dict[str, Any]) -> list[str]:
    require(claims["track_id"] == "MD2S-R1-C-PHYS", "claim register track drift")
    items = claims["claims"]
    ids = [item["claim_id"] for item in items]
    require(ids == [
        "C-PHYS-F1B-CLAIM-001",
        "C-PHYS-F1B-CLAIM-002",
        "C-PHYS-F1B-CLAIM-003",
    ], "claim IDs or ordering drift")
    require(items[0]["status"] == "CONDITIONAL", "model definition claim must remain conditional")
    require(items[0]["evidence_effect"] == "MODEL_DEFINITION_ONLY", "claim evidence drift")
    require(items[1]["evidence_effect"] == "FORMAL_MODEL_ACCOUNTING_ONLY", "budget evidence drift")
    require(items[2]["evidence_effect"] == "INPUT_HYGIENE_ONLY", "positivity evidence drift")
    require(all(item["physical_evidence_effect"] == "NONE" for item in items), "claim physical evidence overclaim")
    return ids


def validate_checkpoint_and_manifest() -> dict[str, str]:
    checkpoint = load_json(CHECKPOINT_PATH)
    alias = load_json(CHECKPOINT_ALIAS_PATH)
    require(checkpoint == alias, "stable checkpoint alias must be semantically identical to v1.11")
    require(checkpoint["checkpoint_id"] == "UL-CHK-20260803-011", "checkpoint ID drift")
    require(
        checkpoint["gate_state"]["R1.0_SUBSTATE"]
        == "FUNCTION_FAMILY_FROZEN_BENCHMARK_INSTANCE_OPEN",
        "checkpoint R1.0 substate drift",
    )
    require(
        checkpoint["current_workstreams"][0]["next_block"] == "C-PHYS-R1.0-FREEZE-1C",
        "wrong primary next block",
    )
    require(
        checkpoint["current_workstreams"][1]["priority"] == "PARALLEL_DIAGNOSTIC_ONLY",
        "G1.2 priority firewall drift",
    )

    manifest = load_json(MANIFEST_PATH)
    require(manifest["release"] == "2.5-c-phys-freeze-1b-v0.1", "manifest release drift")
    require(
        manifest["gates"]["R1.0_SUBSTATE"]
        == "FUNCTION_FAMILY_FROZEN_BENCHMARK_INSTANCE_OPEN",
        "manifest R1.0 substate drift",
    )
    require(
        manifest["gates"]["STRUCTURAL_BVP_COUNT"]
        == "SQUARE_FUNCTIONALLY_SPECIALIZED_CONDITIONAL",
        "manifest structural count drift",
    )
    require(
        manifest["c_phys_operator_entry"]["minimal_eft_contract"]
        == "registry/2026-08-03_MD2S_R1_C_PHYS_MinimalEFTFunctionFreezeContract_v0.1.json",
        "manifest contract pointer drift",
    )
    require(
        manifest["workstream_priority"][0]
        == "MD2S-R1-C-PHYS:C-PHYS-R1.0-FREEZE-1C",
        "manifest primary workstream drift",
    )
    return {
        "checkpoint": checkpoint["checkpoint_id"],
        "manifest_release": manifest["release"],
    }


def validate_decision_log() -> str:
    decisions = load_decisions()
    ids = [item.get("decision_id") for item in decisions]
    require(len(ids) == len(set(ids)), "duplicate decision IDs")
    numeric: list[int] = []
    for decision_id in ids:
        require(isinstance(decision_id, str), "decision ID must be a string")
        match = re.fullmatch(r"UL-DEC-(\d{4})", decision_id)
        require(match is not None, f"invalid decision ID: {decision_id}")
        numeric.append(int(match.group(1)))
    require(numeric == sorted(numeric), "decision log must remain append-only and ordered")
    require(ids[-1] == "UL-DEC-0020", "UL-DEC-0020 must be the current appended decision")
    decision = decisions[-1]
    require(decision["status"] == "ACTIVE", "UL-DEC-0020 must be active")
    require(decision["evidence_effect"] == "MODEL_DEFINITION_ONLY", "UL-DEC-0020 evidence drift")
    require(decision["supersedes"] is None, "UL-DEC-0020 must not silently supersede prior decisions")
    return decision["decision_id"]


def validate_ledger() -> None:
    require(LEDGER_PATH.is_file(), "missing Freeze-1B ledger")
    text = LEDGER_PATH.read_text(encoding="utf-8")
    required_fragments = [
        "VERSIONED_MODEL_SELECTION_NOT_DERIVATION",
        "C-PHYS-ME1",
        "U(\\phi)=\\frac12 m_\\phi^2\\phi^2",
        "Z_F(\\phi)=1",
        "q_{\\rm ref}=\\frac1{M_6}",
        "FUNCTION_FAMILY_FROZEN_BENCHMARK_INSTANCE_OPEN",
        "C-PHYS-R1.0-FREEZE-1C",
    ]
    for fragment in required_fragments:
        require(fragment in text, f"ledger missing required fragment: {fragment}")


def validate() -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    status = load_json(STATUS_PATH)
    claims = load_json(CLAIMS_PATH)
    validate_ledger()
    result = {
        "contract": "MD2S_R1_C_PHYS_MINIMAL_EFT_FUNCTION_FREEZE",
        "status": "PASS",
        "function_selection": validate_function_selection(contract),
        "parameter_budget": validate_parameter_budget(contract),
        "gate_state": validate_firewalls(contract, status),
        "claims": validate_claims(claims),
        "synchronization": validate_checkpoint_and_manifest(),
        "decision": validate_decision_log(),
        "solver_authorized": False,
        "physical_evidence_effect": "NONE",
        "next_block": "C-PHYS-R1.0-FREEZE-1C",
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    try:
        result = validate()
    except ContractError as exc:
        if args.json:
            print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"FAIL: {exc}")
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS: MD2S-R1-C-PHYS Freeze-1B contract is internally synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
