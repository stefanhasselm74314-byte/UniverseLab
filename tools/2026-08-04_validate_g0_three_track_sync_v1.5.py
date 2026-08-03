#!/usr/bin/env python3
"""G0 validator v1.5 for the C-PHYS-M1 Operator-2A canonical state."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_TOOL = ROOT / "tools/2026-08-03_validate_g0_three_track_sync_v1.0.py"
SPEC = importlib.util.spec_from_file_location("g0_base_for_v1_5", BASE_TOOL)
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
            decisions.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ContractError(f"invalid decision-log JSON at line {line_number}: {exc}") from exc
    ids = [entry.get("decision_id") for entry in decisions]
    require(len(ids) == len(set(ids)), "duplicate decision ids")
    numeric: list[int] = []
    for decision_id in ids:
        match = re.fullmatch(r"UL-DEC-(\d{4})", str(decision_id))
        require(match is not None, f"invalid decision id: {decision_id}")
        numeric.append(int(match.group(1)))
    require(numeric == sorted(numeric), "decision log must be monotonically append-only")
    require(ids[-1] == "UL-DEC-0021", "Operator-2A decision must be latest")
    latest = decisions[-1]
    require(latest["status"] == "ACTIVE", "UL-DEC-0021 must be active")
    require(latest["evidence_effect"] == "FORMAL_OPERATOR_STRUCTURE_ONLY", "Operator-2A evidence drift")
    require(latest["supersedes"] is None, "Operator-2A decision must not rewrite earlier decisions")


def validate_project_manifest_and_checkpoint() -> dict[str, Any]:
    project = load_json("project-manifest.json")
    require(project["release"] == "2.6-c-phys-m1-operator-2a-v0.1", "manifest release drift")
    require(project["architecture"]["program_chain"] == ["HPVS", "HZT-M0", "HZT-Full"], "program chain drift")
    tracks = project["architecture"]["research_tracks"]
    require([item["id"] for item in tracks] == ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"], "track order drift")
    require(tracks[1]["active_model"] == "HZT-M0-S6-C-PHYS-M1", "active model drift")
    require(tracks[1]["status"] == "ACTIVE_BOUNDARY_TRACE_AND_FUNCTION_SPACE_CLOSURE_REMAINING", "track status drift")

    gates = project["gates"]
    expected = {
        "R1.0": "ACTIVE_BOUNDARY_TRACE_AND_FUNCTION_SPACE_CLOSURE_REMAINING",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "CONTINUUM_BVP_OPERATOR": "SPECIALIZED_FORMAL_OPERATOR_DEFINED",
        "CONSTRAINT_PROPAGATION": "PROVEN_SYMBOLIC_CONDITIONAL",
        "INTERIOR_PRINCIPAL_RANK": "PASS_FOR_ELL_POSITIVE",
        "HIGHER_POLE_SERIES": "DERIVED_TO_A4_F4_G4_L5",
        "BOUNDARY_TRACE_MAP": "NOT_CONSTRUCTED",
        "COMPLEMENTING_BOUNDARY_CONDITION": "NOT_PROVEN",
        "CONTINUUM_BVP_JACOBIAN": "NOT_PROVEN",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected.items():
        require(gates.get(key) == value, f"manifest gate drift: {key}")

    entry = project["c_phys_operator_entry"]
    require(entry["status"] == "M1_DIFFERENTIAL_OPERATOR_CLOSED_BOUNDARY_TRACE_INVERTIBILITY_OPEN", "operator status drift")
    require(entry["constraint_dependency_proof"] == "PROVEN_SYMBOLIC_CONDITIONAL", "constraint status drift")
    require(entry["continuum_operator"] == "SPECIALIZED_FORMAL_OPERATOR_DEFINED", "continuum operator drift")
    require(entry["next_block"] == "C-PHYS-R1.0-OPERATOR-2B", "next block drift")
    require(entry["C1_V_source_migration"] == "FORBIDDEN", "track firewall drift")

    contract = load_json("registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2AContract_v0.1.json")
    status = load_json("registry/2026-08-04_UniverseLab_C_PHYS_M1_Operator2A_Status_v0.1.json")
    require(contract["model_id"] == "HZT-M0-S6-C-PHYS-M1", "Operator-2A model identity drift")
    require(contract["radial_constraint"]["off_shell_identity"] == "C_rr_x+4*A_x*C_rr=ell_x*E_A+4*A_x*E_ell-varphi_x*E_varphi", "constraint identity drift")
    require(contract["principal_part"]["determinant"] == "4*ell", "principal determinant drift")
    require(contract["boundary_operator_audit"]["linearized_trace_map_constructed"] is False, "trace map silently constructed")
    require(contract["operator_status"]["Fredholm_property"] == "NOT_PROVEN", "Fredholm evidence drift")
    require(status["status"] == "PASS_FORMAL_OPERATOR_STRUCTURE", "Operator-2A status artifact drift")
    require(status["results"]["physical_background"] == "NOT_ESTABLISHED", "background status drift")

    latest = load_json("registry/session-checkpoint-latest.json")
    snapshot_path = latest.get("canonical_snapshot")
    require(isinstance(snapshot_path, str) and snapshot_path, "checkpoint snapshot required")
    candidate = PurePosixPath(snapshot_path)
    require(not candidate.is_absolute() and ".." not in candidate.parts, "checkpoint path escape")
    dated = load_json(snapshot_path)
    require(dated == latest, "checkpoint alias mismatch")
    require(latest["checkpoint_id"] == "UL-CHK-20260804-012", "checkpoint id drift")
    require(latest["gate_state"]["CONSTRAINT_PROPAGATION"] == "PROVEN_SYMBOLIC_CONDITIONAL", "checkpoint constraint drift")
    require(latest["gate_state"]["BOUNDARY_TRACE_MAP"] == "NOT_CONSTRUCTED", "checkpoint trace drift")
    require(latest["gate_state"]["FREDHOLM_PROPERTY"] == "NOT_PROVEN", "checkpoint Fredholm drift")
    require(latest["gate_state"]["R1.1"] == "BLOCKED", "checkpoint R1.1 drift")
    require(latest["gate_state"]["OFFICIAL_MD2S_SOLVER"] == "NOT_AUTHORIZED", "checkpoint solver drift")
    require(latest["gate_state"]["K1-D"] == "NOT_RELEASED", "checkpoint K1-D drift")
    require(latest["gate_state"]["K1-E"] == "NOT_ADMISSIBLE", "checkpoint K1-E drift")
    workstreams = {item["track_id"]: item for item in latest["current_workstreams"]}
    require(workstreams["MD2S-R1-C-PHYS"]["next_block"] == "C-PHYS-R1.0-OPERATOR-2B", "primary next block drift")
    require(workstreams["HZT-M0-S6-C1-V"]["priority"] == "PARALLEL_DIAGNOSTIC_ONLY", "C1-V priority drift")

    return {"project": project, "checkpoint": latest}


BASE.validate_decision_log = validate_decision_log
BASE.validate_project_manifest_and_checkpoint = validate_project_manifest_and_checkpoint
validate = BASE.validate
main = BASE.main

if __name__ == "__main__":
    raise SystemExit(main())
