#!/usr/bin/env python3
"""Regression tests for canonical G0 v1.11 Background-3A assembly state."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_validate_g0_three_track_sync_v1.11.py"
SPEC = importlib.util.spec_from_file_location("g0_v1_11", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import G0 v1.11 validator")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def expect_failure(function, phrase: str) -> None:
    try:
        function()
    except MOD.ContractError as exc:
        assert phrase in str(exc), (phrase, str(exc))
        return
    raise AssertionError(f"expected ContractError containing: {phrase}")


def test_repository_state_passes() -> None:
    result = MOD.validate()
    assert result["status"] == "PASS"
    assert result["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
    assert result["run_payload_sha256"] == "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302"
    assert result["decision"] == "UL-DEC-0026"
    assert result["solver_implementation"] == "NOT_PRESENT"
    assert result["solver_authorized"] is False
    assert result["physical_evidence_effect"] == "NONE"


def test_manifest_rejects_old_cp01() -> None:
    manifest = MOD.load_json("project-manifest.json")
    changed = copy.deepcopy(manifest)
    changed["gates"]["BACKGROUND_RUN_INPUT"] = "FROZEN_CP01"
    expect_failure(lambda: MOD.validate_manifest(changed), "BACKGROUND_RUN_INPUT")


def test_manifest_rejects_solver_opening() -> None:
    manifest = MOD.load_json("project-manifest.json")
    changed = copy.deepcopy(manifest)
    changed["gates"]["BACKGROUND_SOLVER_IMPLEMENTATION"] = "PRESENT"
    expect_failure(lambda: MOD.validate_manifest(changed), "BACKGROUND_SOLVER_IMPLEMENTATION")


def test_checkpoint_rejects_background_overclaim() -> None:
    checkpoint = MOD.load_json(MOD.CHECKPOINT)
    changed = copy.deepcopy(checkpoint)
    changed["gate_state"]["PHYSICAL_BACKGROUND"] = "ESTABLISHED"
    expect_failure(lambda: MOD.validate_checkpoint(changed), "PHYSICAL_BACKGROUND")


def test_manifest_rejects_run_hash_drift() -> None:
    manifest = MOD.load_json("project-manifest.json")
    changed = copy.deepcopy(manifest)
    changed["c_phys_background_3b"]["run_payload_sha256"] = "0" * 64
    expect_failure(lambda: MOD.validate_manifest(changed), "run hash")


def main() -> int:
    test_repository_state_passes()
    test_manifest_rejects_old_cp01()
    test_manifest_rejects_solver_opening()
    test_checkpoint_rejects_background_overclaim()
    test_manifest_rejects_run_hash_drift()
    print("PASS: G0 v1.11 canonical regression tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
