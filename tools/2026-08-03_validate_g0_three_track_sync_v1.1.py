#!/usr/bin/env python3
"""G0 three-track validator v1.1 with append-only and checkpoint compatibility."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys
from pathlib import PurePosixPath
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_TOOL = ROOT / "tools" / "2026-08-03_validate_g0_three_track_sync_v1.0.py"

_spec = importlib.util.spec_from_file_location("g0_three_track_validator_v1_0", BASE_TOOL)
if _spec is None or _spec.loader is None:
    raise RuntimeError("unable to import G0 v1.0 validator")
_base = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _base
_spec.loader.exec_module(_base)

ContractError = _base.ContractError
load_json = _base.load_json
canonical_json_hash = _base.canonical_json_hash
require = _base.require


def validate_decision_log() -> None:
    """Preserve UL-DEC-0014 while allowing later append-only decisions."""
    path = ROOT / "registry/decision-log.jsonl"
    if not path.is_file():
        raise ContractError("missing decision log")

    decisions: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ContractError(f"invalid decision-log JSON at line {line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ContractError(f"decision-log entry at line {line_number} must be an object")
        decisions.append(value)

    ids = [entry.get("decision_id") for entry in decisions]
    require(all(isinstance(item, str) for item in ids), "every decision requires a string decision_id")
    require(len(ids) == len(set(ids)), "duplicate decision ids")
    require("UL-DEC-0014" in ids, "UL-DEC-0014 must remain in the append-only decision log")

    numeric_ids: list[int] = []
    for decision_id in ids:
        match = re.fullmatch(r"UL-DEC-(\d{4})", decision_id)
        require(match is not None, f"invalid decision id: {decision_id}")
        numeric_ids.append(int(match.group(1)))
    require(numeric_ids == sorted(numeric_ids), "decision log must remain monotonically append-only")

    decision = decisions[ids.index("UL-DEC-0014")]
    require(decision["status"] == "ACTIVE", "UL-DEC-0014 must remain active")
    require(
        decision["evidence_effect"] == "GOVERNANCE_ONLY",
        "UL-DEC-0014 must retain governance-only evidence effect",
    )


def validate_project_manifest_and_checkpoint() -> dict[str, Any]:
    """Validate immutable G0 gates while allowing versioned checkpoint progress."""
    project = load_json("project-manifest.json")
    require(
        project["architecture"]["program_chain"] == ["HPVS", "HZT-M0", "HZT-Full"],
        "project manifest program chain drift",
    )
    tracks = project["architecture"]["research_tracks"]
    require(
        [track["id"] for track in tracks]
        == ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"],
        "project manifest research tracks drift",
    )
    require(project["gates"]["K1-D"] == "NOT_RELEASED", "manifest K1-D drift")
    require(project["gates"]["K1-E"] == "NOT_ADMISSIBLE", "manifest K1-E drift")
    require(project["gates"]["R1.1"] == "BLOCKED", "manifest R1.1 drift")
    require(project["gates"]["official_MD2S_solver"] == "NOT_AUTHORIZED", "manifest solver drift")
    require(project["gates"]["physical_evidence_effect"] == "NONE", "manifest evidence drift")

    latest = load_json("registry/session-checkpoint-latest.json")
    snapshot = latest.get("canonical_snapshot")
    require(isinstance(snapshot, str) and bool(snapshot.strip()), "checkpoint canonical_snapshot is required")
    candidate = PurePosixPath(snapshot)
    require(not candidate.is_absolute() and ".." not in candidate.parts, "checkpoint snapshot path escapes repository")
    require(candidate.parts[:1] == ("registry",), "checkpoint snapshot must remain in registry")
    dated = load_json(snapshot)
    require(dated == latest, "stable checkpoint alias must match its declared canonical_snapshot")

    checkpoint_id = str(latest.get("checkpoint_id", ""))
    match = re.fullmatch(r"UL-CHK-20260803-(\d{3})", checkpoint_id)
    require(match is not None, "unexpected checkpoint identifier")
    require(int(match.group(1)) >= 7, "checkpoint must not regress before G0 v1.7")
    require(isinstance(latest.get("current_workstream"), str) and latest["current_workstream"], "checkpoint workstream required")

    gate = latest["gate_state"]
    require(gate["MD2S-R1-L"] == "BLOCKED_BY_MISSING_PRIMARY_SOURCES", "checkpoint legacy drift")
    require(gate["MD2S-R1-C-PHYS"] == "MODEL_FREEZE_INCOMPLETE", "checkpoint C-PHYS drift")
    require(gate["HZT-M0-S6-C1-V"] == "MANUFACTURED_VERIFICATION_MODEL", "checkpoint C1-V drift")
    require(gate["C1-V3"] == "PARTIAL", "checkpoint C1-V3 drift")
    require(gate["C1-V4"] == "NOT_STARTED", "checkpoint C1-V4 drift")
    if "G1.1" in gate:
        require(gate["G1.1"] == "PASS_DIAGNOSTIC", "checkpoint G1.1 drift")
    require(gate["R1.1"] == "BLOCKED", "checkpoint R1.1 drift")
    require(gate["OFFICIAL_MD2S_SOLVER"] == "NOT_AUTHORIZED", "checkpoint solver drift")
    require(gate["K1-D"] == "NOT_RELEASED", "checkpoint K1-D drift")
    require(gate["K1-E"] == "NOT_ADMISSIBLE", "checkpoint K1-E drift")
    require(gate["PHYSICAL_EVIDENCE_EFFECT"] == "NONE", "checkpoint evidence drift")
    return {"project": project, "checkpoint": latest}


_base.validate_decision_log = validate_decision_log
_base.validate_project_manifest_and_checkpoint = validate_project_manifest_and_checkpoint

validate = _base.validate
main = _base.main


if __name__ == "__main__":
    raise SystemExit(main())
