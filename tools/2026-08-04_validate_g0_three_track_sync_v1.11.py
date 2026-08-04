#!/usr/bin/env python3
"""Canonical G0 validator v1.11 for Background-3A v0.3 and CP01R1."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.19.json"
ASSEMBLY_TOOL = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3a_assembly_v0.3.py"
NEXT = "C-PHYS-R1.0-BACKGROUND-3C_EXECUTION_IMPLEMENTATION_AND_AUTHORIZATION_GATE"


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
    require(isinstance(value, dict), f"JSON root must be object: {relative}")
    return value


def load_assembly_module():
    spec = importlib.util.spec_from_file_location("background3a_assembly_v03", ASSEMBLY_TOOL)
    if spec is None or spec.loader is None:
        raise ContractError("unable to import Background-3A assembly validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_manifest(m: dict[str, Any]) -> dict[str, str]:
    require(m["release"] == "2.11-c-phys-m1-background-3a-assembly-corrected-v0.3", "release drift")
    tracks = m["architecture"]["research_tracks"]
    require([item["id"] for item in tracks] == ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"], "track drift")
    require(tracks[1]["active_model"] == "HZT-M0-S6-C-PHYS-M1", "active model drift")
    require(tracks[1]["status"] == "ACTIVE_EXECUTION_IMPLEMENTATION_AND_AUTHORIZATION_GATE_REMAINING", "physical track status drift")
    expected = {
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED_SQUARE_ASSEMBLY_CORRECTED",
        "BACKGROUND_3B": "RUN_INPUT_FROZEN_CP01R1_EXECUTION_NOT_AUTHORIZED",
        "BACKGROUND_METHOD": "FROZEN_PREREGISTERED_WITH_ASSEMBLY_CORRECTION",
        "BACKGROUND_TOPOLOGY_SCHEMA": "FROZEN_SINGLE_CAP_PHASE",
        "BACKGROUND_RUN_INPUT": "FROZEN_CP01R1",
        "BACKGROUND_SOLVER_IMPLEMENTATION": "NOT_PRESENT",
        "BACKGROUND_SOLVER_EXECUTION": "NOT_AUTHORIZED",
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
        require(m["gates"].get(key) == value, f"manifest gate drift: {key}")
    bg = m["c_phys_background_3b"]
    require(bg["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1", "manifest run id drift")
    require(bg["previous_run_status"] == "SUPERSEDED_BEFORE_EXECUTION", "previous run status drift")
    require(bg["run_payload_sha256"] == "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302", "manifest run hash drift")
    require(bg["assembly"] == "8N_regularized_bulk_rows_plus_8_boundary_rows_for_8N_plus_8_unknowns", "manifest assembly drift")
    require(bg["solver_implementation"] == "NOT_PRESENT" and bg["current_execution"] == "NOT_EXECUTED", "manifest execution overclaim")
    require(bg["next_block"] == NEXT, "manifest next block drift")
    require(m["central_registries"]["session_checkpoint_snapshot"] == CHECKPOINT, "checkpoint pointer drift")
    require(m["workstream_priority"][0] == f"MD2S-R1-C-PHYS:{NEXT}", "workstream priority drift")
    return expected


def validate_checkpoint(cp: dict[str, Any]) -> dict[str, str]:
    require(cp["checkpoint_id"] == "UL-CHK-20260804-019", "checkpoint id drift")
    require(cp["canonical_snapshot"] == CHECKPOINT, "checkpoint snapshot drift")
    require(cp["supersedes"] == "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.18.json", "checkpoint supersedes drift")
    basis = cp.get("basis_commit")
    require(isinstance(basis, str) and re.fullmatch(r"[0-9a-f]{40}", basis), "checkpoint basis format drift")
    if (ROOT / ".git").exists():
        result = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{basis}^{{commit}}"], capture_output=True, text=True, check=False)
        require(result.returncode == 0, f"checkpoint basis commit absent: {basis}")
    expected = {
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED_SQUARE_ASSEMBLY_CORRECTED",
        "BACKGROUND_3B": "RUN_INPUT_FROZEN_CP01R1_EXECUTION_NOT_AUTHORIZED",
        "BACKGROUND_RUN_INPUT": "FROZEN_CP01R1",
        "BACKGROUND_SOLVER_IMPLEMENTATION": "NOT_PRESENT",
        "BACKGROUND_SOLVER_EXECUTION": "NOT_AUTHORIZED",
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
        require(cp["gate_state"].get(key) == value, f"checkpoint gate drift: {key}")
    require(cp["current_workstreams"][0]["next_block"] == NEXT, "checkpoint next block drift")
    return expected


def validate_alias() -> dict[str, Any]:
    latest = load_json("registry/session-checkpoint-latest.json")
    candidate = PurePosixPath(latest["canonical_snapshot"])
    require(not candidate.is_absolute() and ".." not in candidate.parts, "checkpoint path escape")
    dated = load_json(CHECKPOINT)
    require(latest == dated, "checkpoint alias mismatch")
    return latest


def validate_decision() -> str:
    lines = [line for line in (ROOT / "registry/decision-log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    decisions = [json.loads(line) for line in lines]
    ids = [item["decision_id"] for item in decisions]
    require(len(ids) == len(set(ids)), "duplicate decision ids")
    numeric = []
    for decision_id in ids:
        match = re.fullmatch(r"UL-DEC-(\d{4})", decision_id)
        require(match is not None, f"invalid decision id: {decision_id}")
        numeric.append(int(match.group(1)))
    require(numeric == sorted(numeric), "decision order drift")
    require(ids[-1] == "UL-DEC-0026", "assembly decision must be latest")
    latest = decisions[-1]
    require(latest["status"] == "ACTIVE", "decision status drift")
    require(latest["evidence_effect"] == "NUMERICAL_PROTOCOL_AND_RUN_IDENTITY_DEFINITION_ONLY", "decision evidence drift")
    require(latest["supersedes"] is None, "decision must remain additive")
    return latest["decision_id"]


def validate() -> dict[str, Any]:
    assembly = load_assembly_module().validate()
    manifest = load_json("project-manifest.json")
    checkpoint = validate_alias()
    return {
        "contract": "G0_BACKGROUND_3A_ASSEMBLY_CP01R1_V1_11",
        "status": "PASS",
        "assembly_contract_status": assembly["status"],
        "run_id": assembly["run_rebind"]["new_run_id"],
        "run_payload_sha256": assembly["run_rebind"]["run_hash"],
        "manifest_gates": validate_manifest(manifest),
        "checkpoint_gates": validate_checkpoint(checkpoint),
        "decision": validate_decision(),
        "next_block": NEXT,
        "solver_implementation": "NOT_PRESENT",
        "solver_authorized": False,
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = validate()
    except (ContractError, ValueError, KeyError, AttributeError) as exc:
        payload = {"status": "FAIL", "error": str(exc)}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"FAIL: {exc}")
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else "PASS: G0 synchronized through Background-3A v0.3 and CP01R1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
