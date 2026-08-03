#!/usr/bin/env python3
"""G0 validator v1.2 for consolidated C-PHYS and C1-V post-merge state."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_TOOL = ROOT / "tools" / "2026-08-03_validate_g0_three_track_sync_v1.0.py"

SPEC = importlib.util.spec_from_file_location("g0_three_track_validator_v1_0_for_v1_2", BASE_TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import G0 v1.0 validator")
BASE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)

ContractError = BASE.ContractError
load_json = BASE.load_json
require = BASE.require


def validate_decision_log() -> None:
    path = ROOT / "registry" / "decision-log.jsonl"
    require(path.is_file(), "missing decision log")
    decisions: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ContractError(f"invalid decision-log JSON at line {line_number}: {exc}") from exc
        require(isinstance(entry, dict), f"decision-log line {line_number} must be an object")
        decisions.append(entry)

    ids = [entry.get("decision_id") for entry in decisions]
    require(all(isinstance(item, str) for item in ids), "every decision requires a string id")
    require(len(ids) == len(set(ids)), "duplicate decision ids")
    numeric: list[int] = []
    for decision_id in ids:
        match = re.fullmatch(r"UL-DEC-(\d{4})", str(decision_id))
        require(match is not None, f"invalid decision id: {decision_id}")
        numeric.append(int(match.group(1)))
    require(numeric == sorted(numeric), "decision log must be monotonically append-only")
    require(ids[-2:] == ["UL-DEC-0017", "UL-DEC-0018"], "post-merge decisions must be latest")

    by_id = {entry["decision_id"]: entry for entry in decisions}
    require(by_id["UL-DEC-0014"]["evidence_effect"] == "GOVERNANCE_ONLY", "G0 decision drift")
    require(
        by_id["UL-DEC-0017"]["evidence_effect"]
        == "GOVERNANCE_AND_DIAGNOSTIC_LABEL_CORRECTION_ONLY",
        "atomic diagnostic decision drift",
    )
    require(
        by_id["UL-DEC-0018"]["evidence_effect"]
        == "FORMAL_PARENT_ACTION_AND_OPERATOR_STRUCTURE_ONLY",
        "C-PHYS decision drift",
    )


def validate_project_manifest_and_checkpoint() -> dict[str, Any]:
    project = load_json("project-manifest.json")
    require(project["architecture"]["program_chain"] == ["HPVS", "HZT-M0", "HZT-Full"], "program chain drift")
    tracks = project["architecture"]["research_tracks"]
    require(
        [track["id"] for track in tracks]
        == ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"],
        "research track drift",
    )
    track_status = {track["id"]: track["status"] for track in tracks}
    require(
        track_status["MD2S-R1-C-PHYS"] == "ACTIVE_MODEL_FREEZE_INCOMPLETE",
        "C-PHYS manifest status drift",
    )

    gates = project["gates"]
    required_gates = {
        "R1.0": "ACTIVE_MODEL_FREEZE_INCOMPLETE",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "CONTINUUM_BVP_OPERATOR": "SCAFFOLD_ONLY",
        "CONTINUUM_BVP_JACOBIAN": "NOT_PROVEN",
        "G1.1": "PASS_DIAGNOSTIC",
        "C1-V3": "PARTIAL",
        "C1-V4": "NOT_STARTED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    for key, value in required_gates.items():
        require(gates.get(key) == value, f"manifest gate drift: {key}")

    c_phys = project["c_phys_operator_entry"]
    require(c_phys["radial_system"] == "DERIVED_CONDITIONAL", "C-PHYS radial status drift")
    require(c_phys["continuum_operator"] == "SCAFFOLD_ONLY", "C-PHYS operator drift")
    require(c_phys["solver_authorized"] is False, "C-PHYS solver authorization drift")
    require(c_phys["C1_V_source_migration"] == "FORBIDDEN", "track migration firewall drift")

    c1 = project["c1_verification"]
    require(c1["g1_1_primary_status"] == "NUMERICALLY_CONFIRMED_DIAGNOSTIC", "G1.1 manifest status is not atomic")

    latest = load_json("registry/session-checkpoint-latest.json")
    snapshot = latest.get("canonical_snapshot")
    require(isinstance(snapshot, str) and snapshot, "checkpoint canonical snapshot required")
    candidate = PurePosixPath(snapshot)
    require(not candidate.is_absolute() and ".." not in candidate.parts, "checkpoint path escapes repository")
    require(candidate.parts[:1] == ("registry",), "checkpoint snapshot must be in registry")
    dated = load_json(snapshot)
    require(dated == latest, "stable checkpoint alias must equal canonical snapshot")
    require(latest["checkpoint_id"] == "UL-CHK-20260803-009", "unexpected checkpoint id")

    workstreams = latest.get("current_workstreams")
    require(isinstance(workstreams, list) and len(workstreams) == 2, "two current workstreams required")
    priorities = {item["track_id"]: item["priority"] for item in workstreams}
    require(priorities["MD2S-R1-C-PHYS"] == "PRIMARY", "C-PHYS must be primary")
    require(priorities["HZT-M0-S6-C1-V"] == "PARALLEL_DIAGNOSTIC_ONLY", "C1-V priority drift")

    checkpoint_gate = latest["gate_state"]
    require(checkpoint_gate["MD2S-R1-C-PHYS"] == "ACTIVE_MODEL_FREEZE_INCOMPLETE", "checkpoint C-PHYS drift")
    require(checkpoint_gate["CONTINUUM_BVP_OPERATOR"] == "SCAFFOLD_ONLY", "checkpoint operator drift")
    require(checkpoint_gate["G1.1"] == "PASS_DIAGNOSTIC", "checkpoint G1.1 drift")
    require(checkpoint_gate["R1.1"] == "BLOCKED", "checkpoint R1.1 drift")
    require(checkpoint_gate["OFFICIAL_MD2S_SOLVER"] == "NOT_AUTHORIZED", "checkpoint solver drift")
    require(checkpoint_gate["K1-D"] == "NOT_RELEASED", "checkpoint K1-D drift")
    require(checkpoint_gate["K1-E"] == "NOT_ADMISSIBLE", "checkpoint K1-E drift")
    require(checkpoint_gate["PHYSICAL_EVIDENCE_EFFECT"] == "NONE", "checkpoint evidence drift")

    result = load_json("registry/2026-08-03_HZT_M0_S6_C1_V_G1_1_SymmetricPredictorResult_v0.2.json")
    claim_register = load_json("registry/2026-08-03_UniverseLab_ClaimRegister_G1_1_v0.2.json")
    require(result["status"] == "NUMERICALLY_CONFIRMED_DIAGNOSTIC", "result status not atomic")
    claim = claim_register["claims"][0]
    require(claim["claim_id"] == "C1-V-CLAIM-005", "unexpected G1.1 claim")
    require(claim["status"] == "NUMERICALLY_CONFIRMED_DIAGNOSTIC", "claim status not atomic")
    require(result["physical_evidence_effect"] == "NONE", "result physical evidence drift")
    require(claim["physical_evidence_effect"] == "NONE", "claim physical evidence drift")

    return {"project": project, "checkpoint": latest}


BASE.validate_decision_log = validate_decision_log
BASE.validate_project_manifest_and_checkpoint = validate_project_manifest_and_checkpoint
validate = BASE.validate
main = BASE.main


if __name__ == "__main__":
    raise SystemExit(main())
