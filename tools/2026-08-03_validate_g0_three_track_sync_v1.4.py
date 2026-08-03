#!/usr/bin/env python3
"""G0 validator v1.4 for the C-PHYS-M1 function-freeze canonical state."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_TOOL = ROOT / "tools/2026-08-03_validate_g0_three_track_sync_v1.0.py"

SPEC = importlib.util.spec_from_file_location("g0_base_for_v1_4", BASE_TOOL)
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
    require(ids[-1] == "UL-DEC-0020", "C-PHYS-M1 function-freeze decision must be latest")
    latest = decisions[-1]
    require(latest["status"] == "ACTIVE", "UL-DEC-0020 must be active")
    require(latest["evidence_effect"] == "MODEL_DEFINITION_ONLY", "M1 decision evidence drift")
    require(latest["supersedes"] is None, "M1 decision must not rewrite earlier scientific decisions")


def validate_project_manifest_and_checkpoint() -> dict[str, Any]:
    project = load_json("project-manifest.json")
    require(project["release"] == "2.5-c-phys-m1-function-freeze-v0.1", "manifest release drift")
    require(project["architecture"]["program_chain"] == ["HPVS", "HZT-M0", "HZT-Full"], "program chain drift")
    tracks = project["architecture"]["research_tracks"]
    require([item["id"] for item in tracks] == ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"], "track order drift")
    require(tracks[1]["active_model"] == "HZT-M0-S6-C-PHYS-M1", "active C-PHYS model drift")
    require(tracks[1]["status"] == "ACTIVE_OPERATOR_CLOSURE_REMAINING", "C-PHYS track status drift")

    gates = project["gates"]
    expected = {
        "FUNCTION_SELECTION": "PASS_POSTULATED_MODEL_FAMILY",
        "MF_001_BULK_FUNCTIONS": "FROZEN_FOR_C_PHYS_M1",
        "MF_002_CAP_FUNCTIONS": "FROZEN_FOR_C_PHYS_M1",
        "R1.0": "ACTIVE_OPERATOR_CLOSURE_REMAINING",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "STRUCTURAL_BVP_COUNT": "SQUARE_CONDITIONAL",
        "CONTINUUM_BVP_OPERATOR": "SCAFFOLD_ONLY",
        "CONTINUUM_BVP_JACOBIAN": "NOT_PROVEN",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected.items():
        require(gates.get(key) == value, f"manifest gate drift: {key}")

    c_phys = project["c_phys_operator_entry"]
    require(c_phys["model_id"] == "HZT-M0-S6-C-PHYS-M1", "C-PHYS model identity drift")
    require(c_phys["status"] == "EXACT_M1_FUNCTIONS_SELECTED_OPERATOR_CLOSURE_REMAINING", "C-PHYS status drift")
    require(c_phys["next_block"] == "C-PHYS-R1.0-OPERATOR-2A", "C-PHYS next block drift")
    require(c_phys["C1_V_source_migration"] == "FORBIDDEN", "track firewall drift")
    require(c_phys["open_model_freeze_items"] == [], "function-freeze items must be closed")
    require("symbolic rr-constraint propagation identity" in c_phys["remaining_operator_items"], "operator blocker missing")

    model = project["c_phys_m1"]
    require(model["status"] == "PASS_POSTULATED_MODEL_FAMILY", "M1 manifest status drift")
    require(model["classification"] == "VERSIONED_PHYSICAL_CANDIDATE_MODEL_SELECTION_NOT_DERIVATION", "M1 classification drift")
    require(model["scalar_domain"] == "R", "M1 scalar domain drift")
    require(model["parameter_count"] == 6, "M1 information budget drift")
    require(model["localized_scalar_source"] == "ABSENT_BY_MODEL_SELECTION", "M1 cap-source drift")
    require(model["background_existence"] == "NOT_ESTABLISHED", "M1 background status drift")
    require(model["physical_evidence_effect"] == "NONE", "M1 physical evidence drift")

    contract = load_json("registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json")
    status = load_json("registry/2026-08-03_UniverseLab_C_PHYS_M1_FunctionFreezeStatus_v0.1.json")
    require(contract["model_id"] == "HZT-M0-S6-C-PHYS-M1", "function contract identity drift")
    require(contract["classification"] == "VERSIONED_PHYSICAL_CANDIDATE_MODEL_SELECTION_NOT_DERIVATION", "function contract classification drift")
    require(contract["dimensionless_model_parameter_vector"]["count"] == 6, "function contract parameter count drift")
    require(contract["track_firewall"]["C1_V_parameter_values_migrated"] is False, "C1-V parameter migration")
    require(contract["gate_state"]["R1.1"] == "BLOCKED", "function contract R1.1 drift")
    require(contract["gate_state"]["official_MD2S_solver"] == "NOT_AUTHORIZED", "function contract solver drift")
    require(status["status"] == "PASS_POSTULATED_MODEL_FAMILY", "M1 status artifact drift")
    require(status["overall_track_status"] == "ACTIVE_OPERATOR_CLOSURE_REMAINING", "M1 track status artifact drift")
    require(status["physical_evidence_effect"] == "NONE", "M1 status evidence drift")

    latest = load_json("registry/session-checkpoint-latest.json")
    snapshot_path = latest.get("canonical_snapshot")
    require(isinstance(snapshot_path, str) and snapshot_path, "checkpoint snapshot required")
    candidate = PurePosixPath(snapshot_path)
    require(not candidate.is_absolute() and ".." not in candidate.parts, "checkpoint path escape")
    dated = load_json(snapshot_path)
    require(dated == latest, "checkpoint alias mismatch")
    require(latest["checkpoint_id"] == "UL-CHK-20260803-011", "checkpoint id drift")
    require(latest["gate_state"]["C_PHYS_MODEL_ID"] == "HZT-M0-S6-C-PHYS-M1", "checkpoint model drift")
    require(latest["gate_state"]["FUNCTION_SELECTION"] == "PASS_POSTULATED_MODEL_FAMILY", "checkpoint function status drift")
    require(latest["gate_state"]["R1.0"] == "ACTIVE_OPERATOR_CLOSURE_REMAINING", "checkpoint R1.0 drift")
    require(latest["gate_state"]["PHYSICAL_BACKGROUND"] == "NOT_ESTABLISHED", "checkpoint background drift")
    require(latest["gate_state"]["R1.1"] == "BLOCKED", "checkpoint R1.1 drift")
    require(latest["gate_state"]["OFFICIAL_MD2S_SOLVER"] == "NOT_AUTHORIZED", "checkpoint solver drift")
    require(latest["gate_state"]["K1-D"] == "NOT_RELEASED", "checkpoint K1-D drift")
    require(latest["gate_state"]["K1-E"] == "NOT_ADMISSIBLE", "checkpoint K1-E drift")
    workstreams = {item["track_id"]: item for item in latest["current_workstreams"]}
    require(workstreams["MD2S-R1-C-PHYS"]["model_id"] == "HZT-M0-S6-C-PHYS-M1", "primary model workstream drift")
    require(workstreams["MD2S-R1-C-PHYS"]["next_block"] == "C-PHYS-R1.0-OPERATOR-2A", "primary next block drift")
    require(workstreams["HZT-M0-S6-C1-V"]["priority"] == "PARALLEL_DIAGNOSTIC_ONLY", "C1-V priority drift")

    return {"project": project, "checkpoint": latest}


BASE.validate_decision_log = validate_decision_log
BASE.validate_project_manifest_and_checkpoint = validate_project_manifest_and_checkpoint
validate = BASE.validate
main = BASE.main


if __name__ == "__main__":
    raise SystemExit(main())
