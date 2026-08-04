#!/usr/bin/env python3
"""Canonical G0 validator v1.9 for corrected Background-3A topology."""

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
CHECKPOINT = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.17.json"
METHOD_TOOL = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3a_v0.1.py"
TOPOLOGY_TOOL = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3a_topology_v0.2.py"


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


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ContractError(f"unable to import {path.relative_to(ROOT)}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_manifest() -> dict[str, Any]:
    m = load_json("project-manifest.json")
    require(m["release"] == "2.9-c-phys-m1-background-3a-topology-corrected-v0.2", "release drift")
    tracks = m["architecture"]["research_tracks"]
    require([item["id"] for item in tracks] == ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"], "track drift")
    require(tracks[1]["active_model"] == "HZT-M0-S6-C-PHYS-M1", "active model drift")
    require(tracks[1]["status"] == "ACTIVE_RUN_INPUT_FREEZE_AND_FREDHOLM_ANALYSIS_REMAINING", "track status drift")

    gates = m["gates"]
    expected = {
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED_CORRECTED_TO_SINGLE_CAP_PHASE",
        "BACKGROUND_METHOD": "FROZEN_PREREGISTERED",
        "BACKGROUND_TOPOLOGY_SCHEMA": "FROZEN_SINGLE_CAP_PHASE",
        "BACKGROUND_RUN_INPUT": "NOT_FROZEN",
        "BACKGROUND_SOLVER_EXECUTION": "FORBIDDEN_PENDING_BACKGROUND_3B_AND_LATER_GATE",
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

    bg = m["c_phys_background_3a"]
    require(bg["status"] == "PREREGISTERED_NOT_EXECUTED_CORRECTED_TO_SINGLE_CAP_PHASE", "Background status drift")
    require(bg["topological_input_order"] == ["N_F", "N_sigma", "m_sigma"], "topology vector drift")
    require(bg["topological_input_count"] == 3, "topology count drift")
    require(set(bg["forbidden_regional_labels"]) == {"m_N", "m_S", "n_N", "n_S"}, "forbidden labels drift")
    require(bg["topology_schema"] == "FROZEN_SINGLE_CAP_PHASE", "topology schema drift")
    require(bg["run_input"] == "NOT_FROZEN", "run input overclaim")
    require(bg["current_execution"] == "NOT_EXECUTED", "execution overclaim")
    require(bg["physical_background"] == "NOT_ESTABLISHED", "background overclaim")
    require(bg["physical_evidence_effect"] == "NONE", "physical evidence drift")
    require(bg["next_block"] == "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY", "next block drift")

    require(m["central_registries"]["session_checkpoint_snapshot"] == CHECKPOINT, "checkpoint pointer drift")
    require(m["workstream_priority"] == [
        "MD2S-R1-C-PHYS:C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY",
        "HZT-M0-S6-C1-V:G1.2_PARALLEL_DIAGNOSTIC_ONLY",
    ], "workstream drift")
    return {"manifest": m, "gates": expected}


def validate_checkpoint() -> dict[str, Any]:
    latest = load_json("registry/session-checkpoint-latest.json")
    snapshot = latest.get("canonical_snapshot")
    require(snapshot == CHECKPOINT, "checkpoint snapshot drift")
    candidate = PurePosixPath(str(snapshot))
    require(not candidate.is_absolute() and ".." not in candidate.parts, "checkpoint path escape")
    require(load_json(CHECKPOINT) == latest, "checkpoint alias mismatch")
    require(latest["checkpoint_id"] == "UL-CHK-20260804-017", "checkpoint id drift")
    require(latest["supersedes"] == "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.16.json", "supersedes drift")
    basis = latest.get("basis_commit")
    require(isinstance(basis, str) and re.fullmatch(r"[0-9a-f]{40}", basis), "basis format drift")
    if (ROOT / ".git").exists():
        result = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{basis}^{{commit}}"], capture_output=True, text=True, check=False)
        require(result.returncode == 0, f"basis commit absent: {basis}")

    gates = latest["gate_state"]
    expected = {
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED_CORRECTED_TO_SINGLE_CAP_PHASE",
        "BACKGROUND_METHOD": "FROZEN_PREREGISTERED",
        "BACKGROUND_TOPOLOGY_SCHEMA": "FROZEN_SINGLE_CAP_PHASE",
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
    require(workstreams["MD2S-R1-C-PHYS"]["next_block"] == "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY", "checkpoint next block drift")
    return {"checkpoint_id": latest["checkpoint_id"], "basis_commit": basis, "gates": expected}


def validate_decision() -> str:
    path = ROOT / "registry/decision-log.jsonl"
    decisions = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [item["decision_id"] for item in decisions]
    require(len(ids) == len(set(ids)), "duplicate decisions")
    numeric = [int(re.fullmatch(r"UL-DEC-(\d{4})", item).group(1)) for item in ids]
    require(numeric == sorted(numeric), "decision order drift")
    require(ids[-1] == "UL-DEC-0024", "topology correction decision must be latest")
    latest = decisions[-1]
    require(latest["status"] == "ACTIVE", "decision status drift")
    require(latest["evidence_effect"] == "NUMERICAL_PROTOCOL_AND_MODEL_IDENTITY_CORRECTION_ONLY", "decision evidence drift")
    require(latest["supersedes"] is None, "decision must be additive")
    return latest["decision_id"]


def validate() -> dict[str, Any]:
    method = load_module(METHOD_TOOL, "background3a_method_v01").validate()
    topology = load_module(TOPOLOGY_TOOL, "background3a_topology_v02").validate()
    manifest = validate_manifest()
    return {
        "contract": "G0_BACKGROUND_3A_SINGLE_CAP_TOPOLOGY_V1_9",
        "status": "PASS",
        "method_status": method["status"],
        "topology_status": topology["status"],
        "topology_vector": topology["canonical_v0_2_vector"],
        "checkpoint": validate_checkpoint(),
        "decision": validate_decision(),
        "gate_state": manifest["gates"],
        "next_block": "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY",
        "solver_authorized": False,
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = validate()
    except (ContractError, ValueError, AttributeError) as exc:
        if args.json:
            print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"FAIL: {exc}")
        return 1
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("PASS: G0 synchronized through corrected single-cap Background-3A topology")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
