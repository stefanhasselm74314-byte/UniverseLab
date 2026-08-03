#!/usr/bin/env python3
"""Fail-closed G0 synchronization validator for C-PHYS-M1 Operator-2B.

The validator preserves the three-track firewall, M1 function selection and
Operator-2A results while accepting only the formal function-space and trace
state of Operator-2B. It authorizes no background solve or release gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class ContractError(ValueError):
    """Raised when a canonical synchronization invariant fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def load_json(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    require(path.is_file(), f"missing required JSON: {relative}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {relative}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root must be an object: {relative}")
    return value


def validate_tracks(manifest: dict[str, Any]) -> list[str]:
    require(
        manifest["architecture"]["program_chain"] == ["HPVS", "HZT-M0", "HZT-Full"],
        "program-chain drift",
    )
    tracks = manifest["architecture"]["research_tracks"]
    ids = [item["id"] for item in tracks]
    require(
        ids == ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"],
        "three-track ordering drift",
    )
    physical = tracks[1]
    require(physical["active_model"] == "HZT-M0-S6-C-PHYS-M1", "active model drift")
    require(
        physical["status"]
        == "ACTIVE_BACKGROUND_PREREQUISITE_AND_FREDHOLM_ANALYSIS_REMAINING",
        "physical-track status drift",
    )
    return ids


def validate_manifest() -> dict[str, Any]:
    manifest = load_json("project-manifest.json")
    require(
        manifest["release"] == "2.7-c-phys-m1-operator-2b-v0.1",
        "manifest release drift",
    )
    tracks = validate_tracks(manifest)

    gates = manifest["gates"]
    expected = {
        "FUNCTION_SELECTION": "PASS_POSTULATED_MODEL_FAMILY",
        "MF_001_BULK_FUNCTIONS": "FROZEN_FOR_C_PHYS_M1",
        "MF_002_CAP_FUNCTIONS": "FROZEN_FOR_C_PHYS_M1",
        "OPERATOR_2A": "PASS_FORMAL_OPERATOR_STRUCTURE",
        "OPERATOR_2B": "PASS_FORMAL_FUNCTION_SPACE_AND_TRACE_TEMPLATE",
        "R1.0": "ACTIVE_BACKGROUND_PREREQUISITE_AND_FREDHOLM_ANALYSIS_REMAINING",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "CONTINUUM_BVP_OPERATOR": "FUNCTION_SPACE_AND_TRACE_TEMPLATE_DEFINED",
        "WEIGHTED_FUNCTION_SPACES": "FROZEN",
        "FULL_LINEARIZED_BOUNDARY_TRACE_TEMPLATE": "DEFINED_NOT_EVALUATED",
        "FULL_LINEARIZED_BOUNDARY_TRACE_RANK": "NOT_PROVEN",
        "FREDHOLM_PROPERTY": "NOT_PROVEN",
        "CONTINUUM_BVP_JACOBIAN": "NOT_PROVEN",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected.items():
        require(gates.get(key) == value, f"manifest gate drift: {key}")

    entry = manifest["c_phys_operator_entry"]
    require(entry["model_id"] == "HZT-M0-S6-C-PHYS-M1", "operator model drift")
    require(
        entry["continuum_operator"] == "FUNCTION_SPACE_AND_TRACE_TEMPLATE_DEFINED",
        "operator status drift",
    )
    require(entry["weighted_function_spaces"] == "FROZEN", "function spaces drift")
    require(
        entry["full_linearized_boundary_trace_template"] == "DEFINED_NOT_EVALUATED",
        "trace-template drift",
    )
    require(entry["full_linearized_boundary_trace_rank"] == "NOT_PROVEN", "trace-rank overclaim")
    require(entry["Fredholm_property"] == "NOT_PROVEN", "Fredholm overclaim")
    require(entry["physical_background"] == "NOT_ESTABLISHED", "background overclaim")
    require(entry["solver_authorized"] is False, "solver authorization drift")
    require(entry["augmented_boundary_template_shape"] == "8 x 22", "trace shape drift")
    require(entry["next_block"] == "C-PHYS-R1.0-BACKGROUND-3A", "next block drift")

    require(
        manifest["workstream_priority"]
        == [
            "MD2S-R1-C-PHYS:C-PHYS-R1.0-BACKGROUND-3A",
            "HZT-M0-S6-C1-V:G1.2_PARALLEL_DIAGNOSTIC_ONLY",
        ],
        "workstream priority drift",
    )
    return {"manifest": manifest, "tracks": tracks, "gates": expected}


def validate_operator_chain() -> dict[str, Any]:
    function_contract = load_json(
        "registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json"
    )
    op2a = load_json(
        "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2AContract_v0.1.json"
    )
    op2a_trace = load_json(
        "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2ARegularityTracePreflight_v0.1.json"
    )
    op2b = load_json(
        "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceContract_v0.1.json"
    )
    status = load_json("registry/2026-08-04_UniverseLab_C_PHYS_M1_Operator2B_Status_v0.1.json")
    claims = load_json(
        "registry/2026-08-04_UniverseLab_ClaimRegister_C_PHYS_M1_Operator2B_v0.1.json"
    )

    require(function_contract["model_id"] == "HZT-M0-S6-C-PHYS-M1", "M1 function identity drift")
    require(op2a["model_id"] == "HZT-M0-S6-C-PHYS-M1", "Operator-2A identity drift")
    require(op2a["radial_constraint"]["status"] == "PROVEN_SYMBOLIC_CONDITIONAL_ON_INDEPENDENT_SYSTEM", "constraint proof drift")
    require(op2a_trace["gate_state"]["Fredholm_property"] == "NOT_PROVEN", "Operator-2A Fredholm overclaim")

    require(op2b["block"] == "C-PHYS-R1.0-OPERATOR-2B", "Operator-2B block drift")
    require(
        op2b["classification"]
        == "FORMAL_FUNCTION_SPACE_AND_TRACE_CONTRACT_NO_BACKGROUND_SOLVE",
        "Operator-2B classification drift",
    )
    require(op2b["solver_authorized"] is False, "Operator-2B solver authorization")
    require(op2b["physical_evidence_effect"] == "NONE", "Operator-2B physical evidence drift")
    require(
        op2b["little_holder_spaces"]["regional_profile_domain"]
        == "X_s=h^{2,alpha_H}^3 x h^{1,alpha_H}",
        "profile-space drift",
    )
    require(
        op2b["little_holder_spaces"]["regional_bulk_target"] == "Y_s=h^{0,alpha_H}^4",
        "bulk-target drift",
    )
    require(op2b["augmented_parameter_space"]["dimension"] == 8, "augmented dimension drift")
    require(
        op2b["regularized_bulk_operator"]["negative_tau_powers_after_regularization"] is False,
        "negative tau powers admitted",
    )
    trace = op2b["linearized_boundary_trace_template"]
    require(trace["matrix_shape"] == "8 x 22", "trace template shape drift")
    require(trace["numeric_matrix_constructed"] is False, "numeric trace overclaim")
    require(trace["rank_claim"] == "NOT_ADMISSIBLE_WITHOUT_W_star", "trace-rank firewall drift")
    require(op2b["future_kernel_cokernel_protocol"]["current_execution"] == "NOT_EXECUTED", "kernel protocol execution drift")

    require(status["status"] == "PASS_FORMAL_FUNCTION_SPACE_AND_TRACE_TEMPLATE", "status drift")
    require(status["physical_evidence_effect"] == "NONE", "status physical evidence drift")
    require(status["solver_authorized"] is False, "status solver drift")

    claim_ids = [item["claim_id"] for item in claims["claims"]]
    require(
        claim_ids
        == [
            "C-PHYS-M1-OP2B-CLAIM-001",
            "C-PHYS-M1-OP2B-CLAIM-002",
            "C-PHYS-M1-OP2B-CLAIM-003",
            "C-PHYS-M1-OP2B-CLAIM-004",
        ],
        "Operator-2B claim ordering drift",
    )
    require(all(item["physical_evidence_effect"] == "NONE" for item in claims["claims"]), "claim physical evidence overclaim")

    return {
        "profile_space": op2b["little_holder_spaces"]["regional_profile_domain"],
        "bulk_target": op2b["little_holder_spaces"]["regional_bulk_target"],
        "trace_shape": trace["matrix_shape"],
        "claim_ids": claim_ids,
    }


def validate_checkpoint() -> dict[str, Any]:
    latest = load_json("registry/session-checkpoint-latest.json")
    snapshot = latest.get("canonical_snapshot")
    require(isinstance(snapshot, str) and snapshot, "checkpoint snapshot missing")
    candidate = PurePosixPath(snapshot)
    require(not candidate.is_absolute() and ".." not in candidate.parts, "checkpoint path escape")
    dated = load_json(snapshot)
    require(dated == latest, "checkpoint alias mismatch")
    require(latest["checkpoint_id"] == "UL-CHK-20260804-014", "checkpoint id drift")
    require(snapshot == "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.14.json", "checkpoint snapshot drift")

    gates = latest["gate_state"]
    expected = {
        "OPERATOR_2B": "PASS_FORMAL_FUNCTION_SPACE_AND_TRACE_TEMPLATE",
        "R1.0": "ACTIVE_BACKGROUND_PREREQUISITE_AND_FREDHOLM_ANALYSIS_REMAINING",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "CONTINUUM_BVP_OPERATOR": "FUNCTION_SPACE_AND_TRACE_TEMPLATE_DEFINED",
        "WEIGHTED_FUNCTION_SPACES": "FROZEN",
        "FULL_LINEARIZED_BOUNDARY_TRACE_TEMPLATE": "DEFINED_NOT_EVALUATED",
        "FULL_LINEARIZED_BOUNDARY_TRACE_RANK": "NOT_PROVEN",
        "FREDHOLM_PROPERTY": "NOT_PROVEN",
        "CONTINUUM_BVP_JACOBIAN": "NOT_PROVEN",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "OFFICIAL_MD2S_SOLVER": "NOT_AUTHORIZED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "PHYSICAL_EVIDENCE_EFFECT": "NONE",
    }
    for key, value in expected.items():
        require(gates.get(key) == value, f"checkpoint gate drift: {key}")

    workstreams = {item["track_id"]: item for item in latest["current_workstreams"]}
    require(
        workstreams["MD2S-R1-C-PHYS"]["next_block"] == "C-PHYS-R1.0-BACKGROUND-3A",
        "checkpoint primary next block drift",
    )
    require(
        workstreams["HZT-M0-S6-C1-V"]["priority"] == "PARALLEL_DIAGNOSTIC_ONLY",
        "checkpoint C1 priority drift",
    )
    return {"checkpoint_id": latest["checkpoint_id"], "gates": expected}


def validate_decision_log() -> str:
    path = ROOT / "registry/decision-log.jsonl"
    require(path.is_file(), "missing decision log")
    decisions: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ContractError(f"invalid decision JSON at line {line_number}: {exc}") from exc
        require(isinstance(item, dict), f"decision line {line_number} must be an object")
        decisions.append(item)

    ids = [item.get("decision_id") for item in decisions]
    require(len(ids) == len(set(ids)), "duplicate decision ids")
    numeric: list[int] = []
    for decision_id in ids:
        match = re.fullmatch(r"UL-DEC-(\d{4})", str(decision_id))
        require(match is not None, f"invalid decision id: {decision_id}")
        numeric.append(int(match.group(1)))
    require(numeric == sorted(numeric), "decision log must remain append-only")
    require(ids[-1] == "UL-DEC-0022", "Operator-2B decision must be latest")
    decision = decisions[-1]
    require(decision["status"] == "ACTIVE", "UL-DEC-0022 must be active")
    require(
        decision["evidence_effect"] == "FORMAL_FUNCTIONAL_ANALYTIC_STRUCTURE_ONLY",
        "UL-DEC-0022 evidence drift",
    )
    require(decision["supersedes"] is None, "UL-DEC-0022 must be additive")
    return decision["decision_id"]


def validate() -> dict[str, Any]:
    manifest_result = validate_manifest()
    return {
        "contract": "G0_THREE_TRACK_SYNCHRONIZATION_OPERATOR_2B",
        "status": "PASS",
        "tracks": manifest_result["tracks"],
        "operator_chain": validate_operator_chain(),
        "checkpoint": validate_checkpoint(),
        "decision": validate_decision_log(),
        "gate_state": manifest_result["gates"],
        "next_recommended_block": {
            "track_id": "MD2S-R1-C-PHYS",
            "gate": "C-PHYS-R1.0-BACKGROUND-3A",
            "execution": "METHOD_PREREGISTRATION_ONLY",
        },
        "solver_authorized": False,
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = validate()
    except ContractError as exc:
        if args.json:
            print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"FAIL: {exc}")
        return 1
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("PASS: G0 three-track state synchronized through C-PHYS-M1 Operator-2B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
