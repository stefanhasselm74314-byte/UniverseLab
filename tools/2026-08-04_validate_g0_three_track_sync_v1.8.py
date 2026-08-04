#!/usr/bin/env python3
"""Fail-closed canonical validator v1.8 for Background-3A preregistration.

The validator accepts only a method-preregistered, not-executed Background-3A
state. It does not authorize a run input, solver, numerical background,
continuum theorem, stability claim or physical release.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.16.json"
BACKGROUND_CONTRACT = (
    "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_"
    "Background3APreregistrationContract_v0.1.json"
)


class ContractError(ValueError):
    pass


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


def validate_manifest() -> dict[str, Any]:
    manifest = load_json("project-manifest.json")
    require(
        manifest.get("release") == "2.8-c-phys-m1-background-3a-preregistered-v0.1",
        "manifest release drift",
    )
    require(
        manifest["architecture"]["program_chain"] == ["HPVS", "HZT-M0", "HZT-Full"],
        "program-chain drift",
    )
    tracks = manifest["architecture"]["research_tracks"]
    require(
        [item["id"] for item in tracks]
        == ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"],
        "three-track ordering drift",
    )
    physical = tracks[1]
    require(physical["active_model"] == "HZT-M0-S6-C-PHYS-M1", "active model drift")
    require(
        physical["status"] == "ACTIVE_RUN_INPUT_FREEZE_AND_FREDHOLM_ANALYSIS_REMAINING",
        "physical-track status drift",
    )

    gates = manifest["gates"]
    expected = {
        "OPERATOR_2A": "PASS_FORMAL_OPERATOR_STRUCTURE",
        "OPERATOR_2B": "PASS_FORMAL_FUNCTION_SPACE_AND_TRACE_TEMPLATE",
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED",
        "BACKGROUND_METHOD": "FROZEN_PREREGISTERED",
        "BACKGROUND_RUN_INPUT": "NOT_FROZEN",
        "BACKGROUND_SOLVER_EXECUTION": "FORBIDDEN_PENDING_BACKGROUND_3B_AND_LATER_GATE",
        "R1.0": "ACTIVE_RUN_INPUT_FREEZE_AND_FREDHOLM_ANALYSIS_REMAINING",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
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
        entry["status"] == "BACKGROUND_3A_METHOD_PREREGISTERED_RUN_INPUT_REMAINING",
        "operator-entry status drift",
    )
    require(entry["solver_authorized"] is False, "solver authorization drift")
    require(entry["physical_background"] == "NOT_ESTABLISHED", "background overclaim")
    require(
        entry["next_block"] == "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY",
        "next block drift",
    )

    bg = manifest["c_phys_background_3a"]
    require(bg["status"] == "PREREGISTERED_NOT_EXECUTED", "Background-3A status drift")
    require(
        bg["classification"] == "NUMERICAL_METHOD_PREREGISTRATION_NO_SOLVER_EXECUTION",
        "Background-3A classification drift",
    )
    require(bg["primary_method"] == "CHEBYSHEV_LOBATTO_COLLOCATION_IN_TAU", "method drift")
    require(bg["node_levels"] == [24, 32, 48, 64, 96], "node-level drift")
    require(bg["deterministic_seed_count"] == 7, "seed-count drift")
    require(bg["independent_backend_required"] is True, "backend requirement drift")
    require(bg["run_input"] == "NOT_FROZEN", "run input overclaim")
    require(bg["current_execution"] == "NOT_EXECUTED", "execution overclaim")
    require(bg["physical_background"] == "NOT_ESTABLISHED", "background overclaim")
    require(bg["physical_evidence_effect"] == "NONE", "physical evidence drift")

    require(
        manifest["workstream_priority"]
        == [
            "MD2S-R1-C-PHYS:C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY",
            "HZT-M0-S6-C1-V:G1.2_PARALLEL_DIAGNOSTIC_ONLY",
        ],
        "workstream priority drift",
    )
    require(
        manifest["central_registries"]["session_checkpoint_snapshot"] == CHECKPOINT,
        "manifest checkpoint pointer drift",
    )
    return {"manifest": manifest, "gates": expected}


def validate_background_contract() -> dict[str, Any]:
    contract = load_json(BACKGROUND_CONTRACT)
    require(contract["track_id"] == "MD2S-R1-C-PHYS", "Background track drift")
    require(contract["model_id"] == "HZT-M0-S6-C-PHYS-M1", "Background model drift")
    require(contract["block"] == "C-PHYS-R1.0-BACKGROUND-3A", "Background block drift")
    require(contract["status"] == "PREREGISTERED_NOT_EXECUTED", "Background status drift")
    require(contract["solver_authorized"] is False, "Background solver authorization")
    require(contract["physical_evidence_effect"] == "NONE", "Background evidence drift")

    disc = contract["primary_discretization"]
    require(disc["method"] == "CHEBYSHEV_LOBATTO_COLLOCATION_IN_TAU", "discretization drift")
    require(disc["regional_node_counts"] == [24, 32, 48, 64, 96], "mesh drift")
    require(disc["adaptive_mesh_or_order_selection"] is False, "adaptive tuning enabled")

    seeds = contract["deterministic_seed_protocol"]
    require(seeds["seed_set_size"] == 7, "seed-set drift")
    require(seeds["random_seed_use"] is False, "random seed use enabled")
    require(seeds["warm_start_across_parameter_points"] is False, "cross-point warm start enabled")

    require(
        contract["independent_backend_requirement"]["required_for_candidate_status"] is True,
        "independent backend no longer required",
    )
    require(
        contract["convergence_requirements"]["single_mesh_acceptance_forbidden"] is True,
        "single-mesh acceptance enabled",
    )

    firewall = contract["execution_firewall"]
    require(firewall["current_execution"] == "NOT_EXECUTED", "Background execution drift")
    for key in [
        "nonlinear_solver_run",
        "parameter_scan",
        "observational_fit",
        "trace_matrix_evaluated",
        "trace_rank_claimed",
        "Fredholm_claimed",
        "continuum_Jacobian_claimed",
        "existence_or_uniqueness_claimed",
        "stability_claimed",
        "physical_confirmation_claimed",
    ]:
        require(firewall[key] is False, f"Background firewall opened: {key}")

    require(
        contract["next_allowed_block_after_merge"]
        == "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY",
        "Background next-block drift",
    )
    return {
        "method": disc["method"],
        "node_levels": disc["regional_node_counts"],
        "seed_count": seeds["seed_set_size"],
        "execution": firewall["current_execution"],
    }


def validate_checkpoint() -> dict[str, Any]:
    latest = load_json("registry/session-checkpoint-latest.json")
    snapshot = latest.get("canonical_snapshot")
    require(isinstance(snapshot, str) and snapshot, "checkpoint snapshot missing")
    path = PurePosixPath(snapshot)
    require(not path.is_absolute() and ".." not in path.parts, "checkpoint path escape")
    require(snapshot == CHECKPOINT, "checkpoint snapshot drift")
    require(load_json(snapshot) == latest, "checkpoint alias mismatch")
    require(latest["checkpoint_id"] == "UL-CHK-20260804-016", "checkpoint id drift")
    require(
        latest["supersedes"] == "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.15.json",
        "checkpoint supersedes drift",
    )

    basis = latest.get("basis_commit")
    require(isinstance(basis, str) and re.fullmatch(r"[0-9a-f]{40}", basis), "basis commit format drift")
    if (ROOT / ".git").exists():
        result = subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "-e", f"{basis}^{{commit}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        require(result.returncode == 0, f"basis commit absent from Git history: {basis}")

    gates = latest["gate_state"]
    expected = {
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED",
        "BACKGROUND_METHOD": "FROZEN_PREREGISTERED",
        "BACKGROUND_RUN_INPUT": "NOT_FROZEN",
        "BACKGROUND_SOLVER_EXECUTION": "FORBIDDEN_PENDING_BACKGROUND_3B_AND_LATER_GATE",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
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
        workstreams["MD2S-R1-C-PHYS"]["next_block"]
        == "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY",
        "checkpoint next block drift",
    )
    require(
        workstreams["HZT-M0-S6-C1-V"]["priority"] == "PARALLEL_DIAGNOSTIC_ONLY",
        "C1-V priority drift",
    )
    return {"checkpoint_id": latest["checkpoint_id"], "basis_commit": basis, "gates": expected}


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
    require(numeric == sorted(numeric), "decision log is not append-only")
    require(ids[-1] == "UL-DEC-0023", "Background-3A decision must be latest")
    latest = decisions[-1]
    require(latest["status"] == "ACTIVE", "UL-DEC-0023 must be active")
    require(
        latest["evidence_effect"] == "NUMERICAL_PROTOCOL_DEFINITION_ONLY",
        "UL-DEC-0023 evidence drift",
    )
    require(latest["supersedes"] is None, "UL-DEC-0023 must be additive")
    return latest["decision_id"]


def validate() -> dict[str, Any]:
    manifest = validate_manifest()
    return {
        "contract": "G0_THREE_TRACK_BACKGROUND_3A_PREREGISTRATION_V1_8",
        "status": "PASS",
        "background_3a": validate_background_contract(),
        "checkpoint": validate_checkpoint(),
        "decision": validate_decision_log(),
        "gate_state": manifest["gates"],
        "next_recommended_block": "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY",
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
        print("PASS: G0 canonical state synchronized through Background-3A preregistration")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
