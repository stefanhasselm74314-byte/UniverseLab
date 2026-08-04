#!/usr/bin/env python3
"""Regression tests for G0 v1.12 audited Background-3C primary state."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_validate_g0_three_track_sync_v1.12.py"
SPEC = importlib.util.spec_from_file_location("g0_v1_12", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import G0 v1.12 validator")
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
    assert result["primary_implementation"] == "PASS_PRIMARY_IMPLEMENTATION_AUDIT_NO_SOLVER_EXECUTION"
    assert result["newton_call_count"] == 0
    assert result["decision"] == "UL-DEC-0027"
    assert result["independent_backend"] == "NOT_PRESENT_BLOCKING"
    assert result["execution_authorized"] is False
    assert result["result_artifact_created"] is False
    assert result["physical_evidence_effect"] == "NONE"


def test_manifest_rejects_execution_opening() -> None:
    manifest = MOD.load_json("project-manifest.json")
    changed = copy.deepcopy(manifest)
    changed["gates"]["BACKGROUND_3C_EXECUTION"] = "AUTHORIZED"
    expect_failure(lambda: MOD.validate_manifest(changed), "BACKGROUND_3C_EXECUTION")


def test_manifest_rejects_independent_backend_overclaim() -> None:
    manifest = MOD.load_json("project-manifest.json")
    changed = copy.deepcopy(manifest)
    changed["gates"]["BACKGROUND_3C_INDEPENDENT_BACKEND"] = "PASS"
    expect_failure(lambda: MOD.validate_manifest(changed), "BACKGROUND_3C_INDEPENDENT_BACKEND")


def test_manifest_rejects_newton_overclaim() -> None:
    manifest = MOD.load_json("project-manifest.json")
    changed = copy.deepcopy(manifest)
    changed["c_phys_background_3c"]["audit_newton_call_count"] = 1
    expect_failure(lambda: MOD.validate_manifest(changed), "Newton execution")


def test_checkpoint_rejects_background_overclaim() -> None:
    checkpoint = MOD.load_json(MOD.CHECKPOINT)
    changed = copy.deepcopy(checkpoint)
    changed["gate_state"]["PHYSICAL_BACKGROUND"] = "ESTABLISHED"
    expect_failure(lambda: MOD.validate_checkpoint(changed), "PHYSICAL_BACKGROUND")


def test_manifest_rejects_next_block_drift() -> None:
    manifest = MOD.load_json("project-manifest.json")
    changed = copy.deepcopy(manifest)
    changed["c_phys_background_3c"]["next_block"] = "EXECUTE_NOW"
    expect_failure(lambda: MOD.validate_manifest(changed), "next block")


def main() -> int:
    test_repository_state_passes()
    test_manifest_rejects_execution_opening()
    test_manifest_rejects_independent_backend_overclaim()
    test_manifest_rejects_newton_overclaim()
    test_checkpoint_rejects_background_overclaim()
    test_manifest_rejects_next_block_drift()
    print("PASS: G0 v1.12 canonical regression tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
