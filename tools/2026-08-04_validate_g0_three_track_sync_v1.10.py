#!/usr/bin/env python3
"""Canonical G0 validator v1.10 for the frozen CP01 Background-3B input."""

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
CHECKPOINT = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.18.json"
BG3B_TOOL = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3b_v0.1.py"


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


def load_bg3b_module():
    spec = importlib.util.spec_from_file_location("background3b_contract_v01", BG3B_TOOL)
    if spec is None or spec.loader is None:
        raise ContractError("unable to import Background-3B validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_manifest() -> dict[str, Any]:
    m = load_json("project-manifest.json")
    require(m["release"] == "2.10-c-phys-m1-background-3b-run-input-frozen-v0.1", "release drift")
    tracks = m["architecture"]["research_tracks"]
    require([item["id"] for item in tracks] == ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"], "track drift")
    require(tracks[1]["active_model"] == "HZT-M0-S6-C-PHYS-M1", "active model drift")
    require(tracks[1]["status"] == "ACTIVE_EXECUTION_IMPLEMENTATION_AND_AUTHORIZATION_GATE_REMAINING", "track status drift")

    gates = m["gates"]
    expected = {
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED_CORRECTED_TO_SINGLE_CAP_PHASE",
        "BACKGROUND_3B": "RUN_INPUT_FROZEN_EXECUTION_NOT_AUTHORIZED",
        "BACKGROUND_METHOD": "FROZEN_PREREGISTERED",
        "BACKGROUND_TOPOLOGY_SCHEMA": "FROZEN_SINGLE_CAP_PHASE",
        "BACKGROUND_RUN_INPUT": "FROZEN_CP01",
        "BACKGROUND_SOLVER_IMPLEMENTATION": "NOT_PRESENT",
        "BACKGROUND_SOLVER_EXECUTION": "NOT_AUTHORIZED",
        "R1.0": "ACTIVE_EXECUTION_IMPLEMENTATION_AND_AUTHORIZATION_GATE_REMAINING",
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

    bg = m["c_phys_background_3b"]
    require(bg["classification"] == "EXACT_RUN_INPUT_FREEZE_NO_SOLVER_EXECUTION", "Background-3B classification drift")
    require(bg["status"] == "RUN_INPUT_FROZEN_EXECUTION_NOT_AUTHORIZED", "Background-3B status drift")
    require(bg["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01", "run id drift")
    require(bg["model_parameters_ordered"] == {
        "Lambda_hat": "1", "mhat_phi_sq": "1", "a_F": "1/4",
        "lambda_hat": "1", "z_sigma_hat": "1", "q_hat": "1"
    }, "parameter vector drift")
    require(bg["topological_sector_ordered"] == {"N_F": 1, "N_sigma": 1, "m_sigma": 1}, "topology drift")
    require(bg["alpha_H"] == "1/2", "Holder exponent drift")
    require(bg["seed_set_id"] == "M1-BG3B-CP01-SEEDS-01", "seed-set drift")
    require(bg["dependency_lock_sha256"] == "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f", "dependency hash drift")
    require(bg["seed_payload_sha256"] == "b6e4319cc29736799a0b46320002e51cd17b70b724a6b4c6e86567a316996161", "seed hash drift")
    require(bg["run_payload_sha256"] == "625118d21d70fb563c310e985ba83126a18b8680278b7b11908c1bc550f79536", "run hash drift")
    require(bg["base_seed_classification"] == "EXACT_BULK_AND_PATCH_SEED_BOUNDARY_INEXACT", "base seed classification drift")
    require(bg["base_seed_is_solution"] is False, "base seed solution overclaim")
    require(bg["solver_implementation"] == "NOT_PRESENT", "solver implementation drift")
    require(bg["current_execution"] == "NOT_EXECUTED", "execution drift")
    require(bg["physical_background"] == "NOT_ESTABLISHED", "background overclaim")
    require(bg["physical_evidence_effect"] == "NONE", "physical evidence drift")
    require(bg["next_block"] == "C-PHYS-R1.0-BACKGROUND-3C_EXECUTION_IMPLEMENTATION_AND_AUTHORIZATION_GATE", "next block drift")
    require(m["central_registries"]["session_checkpoint_snapshot"] == CHECKPOINT, "checkpoint pointer drift")
    require(m["workstream_priority"] == [
        "MD2S-R1-C-PHYS:C-PHYS-R1.0-BACKGROUND-3C_EXECUTION_IMPLEMENTATION_AND_AUTHORIZATION_GATE",
        "HZT-M0-S6-C1-V:G1.2_PARALLEL_DIAGNOSTIC_ONLY",
    ], "workstream drift")
    return {"manifest": m, "gates": expected, "background_3b": bg}


def validate_checkpoint() -> dict[str, Any]:
    latest = load_json("registry/session-checkpoint-latest.json")
    snapshot = latest.get("canonical_snapshot")
    require(snapshot == CHECKPOINT, "checkpoint snapshot drift")
    candidate = PurePosixPath(str(snapshot))
    require(not candidate.is_absolute() and ".." not in candidate.parts, "checkpoint path escape")
    require(load_json(CHECKPOINT) == latest, "checkpoint alias mismatch")
    require(latest["checkpoint_id"] == "UL-CHK-20260804-018", "checkpoint id drift")
    require(latest["supersedes"] == "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.17.json", "supersedes drift")
    basis = latest.get("basis_commit")
    require(isinstance(basis, str) and re.fullmatch(r"[0-9a-f]{40}", basis), "basis format drift")
    if (ROOT / ".git").exists():
        result = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{basis}^{{commit}}"], capture_output=True, text=True, check=False)
        require(result.returncode == 0, f"basis commit absent: {basis}")

    gates = latest["gate_state"]
    expected = {
        "BACKGROUND_3B": "RUN_INPUT_FROZEN_EXECUTION_NOT_AUTHORIZED",
        "BACKGROUND_RUN_INPUT": "FROZEN_CP01",
        "BACKGROUND_SOLVER_IMPLEMENTATION": "NOT_PRESENT",
        "BACKGROUND_SOLVER_EXECUTION": "NOT_AUTHORIZED",
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
    require(workstreams["MD2S-R1-C-PHYS"]["next_block"] == "C-PHYS-R1.0-BACKGROUND-3C_EXECUTION_IMPLEMENTATION_AND_AUTHORIZATION_GATE", "checkpoint next block drift")
    return {"checkpoint_id": latest["checkpoint_id"], "basis_commit": basis, "gates": expected}


def validate_decision() -> str:
    path = ROOT / "registry/decision-log.jsonl"
    decisions = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [item["decision_id"] for item in decisions]
    require(len(ids) == len(set(ids)), "duplicate decisions")
    numeric = [int(re.fullmatch(r"UL-DEC-(\d{4})", item).group(1)) for item in ids]
    require(numeric == sorted(numeric), "decision order drift")
    require(ids[-1] == "UL-DEC-0025", "Background-3B decision must be latest")
    latest = decisions[-1]
    require(latest["status"] == "ACTIVE", "decision status drift")
    require(latest["evidence_effect"] == "NUMERICAL_RUN_INPUT_DEFINITION_ONLY", "decision evidence drift")
    require(latest["supersedes"] is None, "decision must be additive")
    return latest["decision_id"]


def validate() -> dict[str, Any]:
    bg3b = load_bg3b_module().validate()
    manifest = validate_manifest()
    return {
        "contract": "G0_BACKGROUND_3B_CP01_RUN_INPUT_V1_10",
        "status": "PASS",
        "background_3b_contract_status": bg3b["status"],
        "run_payload_sha256": bg3b["run_payload"]["sha256"],
        "seed_payload_sha256": bg3b["seed_spec"]["sha256"],
        "dependency_lock_sha256": bg3b["dependency_lock"]["sha256"],
        "checkpoint": validate_checkpoint(),
        "decision": validate_decision(),
        "gate_state": manifest["gates"],
        "next_block": "C-PHYS-R1.0-BACKGROUND-3C_EXECUTION_IMPLEMENTATION_AND_AUTHORIZATION_GATE",
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
    except (ContractError, ValueError, AttributeError) as exc:
        if args.json:
            print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"FAIL: {exc}")
        return 1
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("PASS: G0 synchronized through frozen CP01 Background-3B run input")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
