#!/usr/bin/env python3
"""G0 validator v1.3 for the C-PHYS Freeze-1A canonical state."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_TOOL = ROOT / "tools/2026-08-03_validate_g0_three_track_sync_v1.0.py"

SPEC = importlib.util.spec_from_file_location("g0_base_for_v1_3", BASE_TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import G0 base validator")
BASE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)

ContractError = BASE.ContractError
load_json = BASE.load_json
require = BASE.require


def validate_decision_log() -> None:
    path = ROOT / "registry/decision-log.jsonl"
    require(path.is_file(), "missing decision log")
    decisions: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ContractError(f"invalid decision-log JSON at line {line_number}: {exc}") from exc
        decisions.append(entry)
    ids = [entry.get("decision_id") for entry in decisions]
    require(len(ids) == len(set(ids)), "duplicate decision ids")
    numeric: list[int] = []
    for decision_id in ids:
        match = re.fullmatch(r"UL-DEC-(\d{4})", str(decision_id))
        require(match is not None, f"invalid decision id: {decision_id}")
        numeric.append(int(match.group(1)))
    require(numeric == sorted(numeric), "decision log must be monotonically append-only")
    require(ids[-1] == "UL-DEC-0019", "Freeze-1A decision must be latest")
    latest = decisions[-1]
    require(latest["status"] == "ACTIVE", "UL-DEC-0019 must be active")
    require(latest["evidence_effect"] == "FORMAL_GLOBAL_STRUCTURE_ONLY", "Freeze-1A evidence drift")


def validate_project_manifest_and_checkpoint() -> dict[str, Any]:
    project = load_json("project-manifest.json")
    require(project["release"] == "2.4-c-phys-freeze-1a-v0.1", "manifest release drift")
    require(project["architecture"]["program_chain"] == ["HPVS", "HZT-M0", "HZT-Full"], "program chain drift")
    tracks = project["architecture"]["research_tracks"]
    require([item["id"] for item in tracks] == ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"], "track order drift")

    gates = project["gates"]
    expected = {
        "R1.0": "ACTIVE_MODEL_FREEZE_INCOMPLETE",
        "R1.0_SUBSTATE": "ACTIVE_FUNCTION_FREEZE_REMAINING",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "STRUCTURAL_BVP_COUNT": "SQUARE_CONDITIONAL",
        "CONTINUUM_BVP_OPERATOR": "SCAFFOLD_ONLY",
        "CONTINUUM_BVP_JACOBIAN": "NOT_PROVEN",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected.items():
        require(gates.get(key) == value, f"manifest gate drift: {key}")

    c_phys = project["c_phys_operator_entry"]
    require(c_phys["status"] == "GLOBAL_CONVENTIONS_FROZEN_FUNCTIONS_OPEN", "C-PHYS status drift")
    require(c_phys["next_block"] == "C-PHYS-R1.0-FREEZE-1B", "C-PHYS next block drift")
    require(c_phys["C1_V_source_migration"] == "FORBIDDEN", "track firewall drift")
    open_items = set(c_phys["open_model_freeze_items"])
    require("exact U(phi)" in open_items and "exact Z_F(phi)" in open_items, "bulk functions silently closed")
    require("gauge patch transition" not in open_items, "patch transition not removed from open list")
    require("normal orientation table" not in open_items, "orientation not removed from open list")

    freeze = load_json("registry/2026-08-03_MD2S_R1_C_PHYS_GlobalConventionFreezeContract_v0.1.json")
    status = load_json("registry/2026-08-03_UniverseLab_C_PHYS_Freeze1A_Status_v0.1.json")
    require(freeze["status"] == "GLOBAL_CONVENTIONS_AND_PARAMETER_ROLES_FROZEN_FUNCTIONS_OPEN", "freeze contract drift")
    require(freeze["structural_BVP_count"]["status"] == "SQUARE_COUNT_STRUCTURALLY_CLOSED_CONDITIONAL_ON_FUNCTION_FREEZE", "square count drift")
    require(status["status"] == "PASS_FORMAL_GLOBAL_STRUCTURE", "Freeze-1A status drift")
    require(status["R1_0_substate"] == "ACTIVE_FUNCTION_FREEZE_REMAINING", "Freeze-1A substate drift")

    latest = load_json("registry/session-checkpoint-latest.json")
    snapshot_path = latest.get("canonical_snapshot")
    require(isinstance(snapshot_path, str) and snapshot_path, "checkpoint snapshot required")
    candidate = PurePosixPath(snapshot_path)
    require(not candidate.is_absolute() and ".." not in candidate.parts, "checkpoint path escape")
    dated = load_json(snapshot_path)
    require(dated == latest, "checkpoint alias mismatch")
    require(latest["checkpoint_id"] == "UL-CHK-20260803-010", "checkpoint id drift")
    require(latest["gate_state"]["R1.0_SUBSTATE"] == "ACTIVE_FUNCTION_FREEZE_REMAINING", "checkpoint substate drift")
    require(latest["gate_state"]["STRUCTURAL_BVP_COUNT"] == "SQUARE_CONDITIONAL", "checkpoint count drift")
    require(latest["gate_state"]["R1.1"] == "BLOCKED", "checkpoint R1.1 drift")
    require(latest["gate_state"]["OFFICIAL_MD2S_SOLVER"] == "NOT_AUTHORIZED", "checkpoint solver drift")
    require(latest["gate_state"]["K1-D"] == "NOT_RELEASED", "checkpoint K1-D drift")
    require(latest["gate_state"]["K1-E"] == "NOT_ADMISSIBLE", "checkpoint K1-E drift")
    workstreams = {item["track_id"]: item for item in latest["current_workstreams"]}
    require(workstreams["MD2S-R1-C-PHYS"]["next_block"] == "C-PHYS-R1.0-FREEZE-1B", "primary next block drift")
    require(workstreams["HZT-M0-S6-C1-V"]["priority"] == "PARALLEL_DIAGNOSTIC_ONLY", "C1-V priority drift")

    return {"project": project, "checkpoint": latest}


BASE.validate_decision_log = validate_decision_log
BASE.validate_project_manifest_and_checkpoint = validate_project_manifest_and_checkpoint
validate = BASE.validate
main = BASE.main


if __name__ == "__main__":
    raise SystemExit(main())
