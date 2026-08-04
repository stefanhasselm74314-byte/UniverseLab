#!/usr/bin/env python3
"""G0 synchronization validator v1.7 for provenance-safe Operator-2B state.

This additive wrapper preserves every Operator-2B invariant from v1.6 and
advances only the canonical checkpoint pointer from v1.14 to v1.15. The new
checkpoint corrects an invalid historical basis_commit; it changes no
scientific state, gate or evidence effect.
"""

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
BASE_TOOL = ROOT / "tools/2026-08-04_validate_g0_three_track_sync_v1.6.py"

SPEC = importlib.util.spec_from_file_location("g0_sync_v1_6_for_v1_7", BASE_TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import G0 v1.6 validator")
BASE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)

ContractError = BASE.ContractError
load_json = BASE.load_json
require = BASE.require

CHECKPOINT_PATH = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.15.json"
CHECKPOINT_ID = "UL-CHK-20260804-015"


def validate_manifest() -> dict[str, Any]:
    result = BASE._validate_manifest_v1_6()
    manifest = result["manifest"]
    registries = manifest.get("central_registries")
    require(isinstance(registries, dict), "manifest central_registries missing")
    require(
        registries.get("session_checkpoint_snapshot") == CHECKPOINT_PATH,
        "manifest checkpoint snapshot must point to v1.15",
    )
    return result


def validate_checkpoint() -> dict[str, Any]:
    latest = load_json("registry/session-checkpoint-latest.json")
    snapshot = latest.get("canonical_snapshot")
    require(isinstance(snapshot, str) and snapshot, "checkpoint snapshot missing")
    candidate = PurePosixPath(snapshot)
    require(not candidate.is_absolute() and ".." not in candidate.parts, "checkpoint path escape")
    require(snapshot == CHECKPOINT_PATH, "checkpoint alias must point to v1.15")
    dated = load_json(snapshot)
    require(dated == latest, "checkpoint alias mismatch")
    require(latest.get("checkpoint_id") == CHECKPOINT_ID, "checkpoint v1.15 id drift")
    require(
        latest.get("supersedes")
        == "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.14.json",
        "checkpoint v1.15 supersedes drift",
    )

    basis = latest.get("basis_commit")
    require(
        isinstance(basis, str) and re.fullmatch(r"[0-9a-f]{40}", basis) is not None,
        "checkpoint basis_commit format drift",
    )
    if (ROOT / ".git").exists():
        result = subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "-e", f"{basis}^{{commit}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        require(result.returncode == 0, f"checkpoint basis_commit absent from Git history: {basis}")

    correction = latest.get("provenance_correction")
    require(isinstance(correction, dict), "checkpoint provenance correction missing")
    require(correction.get("scientific_state_changed") is False, "scientific state changed in correction")
    require(correction.get("gate_state_changed") is False, "gate state changed in correction")
    require(
        correction.get("evidence_effect") == "GOVERNANCE_PROVENANCE_ONLY",
        "provenance correction evidence drift",
    )

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
        require(gates.get(key) == value, f"checkpoint v1.15 gate drift: {key}")

    workstreams = {item["track_id"]: item for item in latest["current_workstreams"]}
    require(
        workstreams["MD2S-R1-C-PHYS"]["next_block"] == "C-PHYS-R1.0-BACKGROUND-3A",
        "checkpoint primary next block drift",
    )
    require(
        workstreams["HZT-M0-S6-C1-V"]["priority"] == "PARALLEL_DIAGNOSTIC_ONLY",
        "checkpoint C1-V priority drift",
    )
    return {
        "checkpoint_id": CHECKPOINT_ID,
        "basis_commit": basis,
        "provenance_correction": "PASS_GOVERNANCE_ONLY",
        "gates": expected,
    }


# Preserve the original v1.6 manifest validator before monkeypatching.
BASE._validate_manifest_v1_6 = BASE.validate_manifest
BASE.validate_manifest = validate_manifest
BASE.validate_checkpoint = validate_checkpoint


def validate() -> dict[str, Any]:
    payload = BASE.validate()
    payload["contract"] = "G0_THREE_TRACK_SYNCHRONIZATION_OPERATOR_2B_PROVENANCE_V1_15"
    payload["checkpoint"] = validate_checkpoint()
    payload["provenance_effect"] = "GOVERNANCE_PROVENANCE_ONLY"
    payload["scientific_state_changed"] = False
    payload["gate_state_changed"] = False
    return payload


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
        print("PASS: G0 synchronized through Operator-2B with checkpoint v1.15")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
