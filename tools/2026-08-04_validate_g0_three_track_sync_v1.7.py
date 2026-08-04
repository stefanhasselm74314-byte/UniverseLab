#!/usr/bin/env python3
"""Fail-closed G0 validator v1.7 for the canonical Operator-2B state.

This version preserves the Operator-2B scientific contract from v1.6 while
requiring the corrected alias-backed checkpoint v1.15. It authorizes no
background solve, Fredholm claim, continuum Jacobian, stability result or
physical release.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_TOOL = ROOT / "tools/2026-08-04_validate_g0_three_track_sync_v1.6.py"

SPEC = importlib.util.spec_from_file_location("g0_operator2b_v1_6_base", BASE_TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import G0 Operator-2B v1.6 validator")
BASE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)

ContractError = BASE.ContractError
load_json = BASE.load_json
require = BASE.require


def validate_checkpoint() -> dict[str, Any]:
    latest = load_json("registry/session-checkpoint-latest.json")
    snapshot = latest.get("canonical_snapshot")
    require(isinstance(snapshot, str) and snapshot, "checkpoint snapshot missing")
    candidate = PurePosixPath(snapshot)
    require(not candidate.is_absolute() and ".." not in candidate.parts, "checkpoint path escape")
    require(
        snapshot == "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.15.json",
        "checkpoint snapshot drift",
    )
    dated = load_json(snapshot)
    require(dated == latest, "checkpoint alias mismatch")
    require(latest["checkpoint_id"] == "UL-CHK-20260804-015", "checkpoint id drift")
    require(
        latest["supersedes"] == "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.14.json",
        "checkpoint supersession drift",
    )
    require("v1.14" in latest.get("correction_note", ""), "checkpoint correction note missing")
    require("v1.13" in latest.get("correction_note", ""), "missing v1.13 provenance correction")

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
    return {"checkpoint_id": latest["checkpoint_id"], "snapshot": snapshot, "gates": expected}


BASE.validate_checkpoint = validate_checkpoint
validate = BASE.validate


def main() -> int:
    import argparse

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
        print("PASS: G0 canonical state synchronized through Operator-2B checkpoint v1.15")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
