#!/usr/bin/env python3
"""Regression tests for fail-closed Background-3C3 authorization review."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3c3_v0.1.py"
SPEC = importlib.util.spec_from_file_location("background3c3_validator_test", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import Background-3C3 validator")
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


def test_repository_review_passes() -> None:
    result = MOD.validate()
    assert result["status"] == "PASS"
    assert result["review_outcome"] == "DENIED_MISSING_EXECUTION_PACKAGE"
    assert result["execution_authorized"] is False
    assert result["solver_executed"] is False
    assert result["result_artifact_created"] is False
    assert result["physical_evidence_effect"] == "NONE"
    assert result["next_block"] == "C-PHYS-R1.0-BACKGROUND-3C4_EXECUTION_RUNNER_IMPLEMENTATION_ONLY"


def test_authorization_opening_is_rejected() -> None:
    review = MOD.load_json(MOD.REVIEW)
    changed = copy.deepcopy(review)
    changed["authorized"] = True
    expect_failure(lambda: MOD.validate_review(changed), "authorization opened")


def test_missing_runner_cannot_be_marked_pass() -> None:
    review = MOD.load_json(MOD.REVIEW)
    changed = copy.deepcopy(review)
    changed["blocking_prerequisites"]["source_hash_bound_execution_runner"]["status"] = "PASS"
    expect_failure(lambda: MOD.validate_review(changed), "source_hash_bound_execution_runner")


def test_review_cannot_execute_solver() -> None:
    review = MOD.load_json(MOD.REVIEW)
    changed = copy.deepcopy(review)
    changed["review_logic"]["review_may_execute_solver"] = True
    expect_failure(lambda: MOD.validate_review(changed), "review execution opened")


def test_result_creation_is_rejected() -> None:
    review = MOD.load_json(MOD.REVIEW)
    changed = copy.deepcopy(review)
    changed["execution_effect"]["result_artifact_creation_allowed"] = True
    expect_failure(lambda: MOD.validate_review(changed), "execution effect opened")


def test_physical_and_release_overclaims_are_rejected() -> None:
    review = MOD.load_json(MOD.REVIEW)
    changed = copy.deepcopy(review)
    changed["gate_state"]["physical_background"] = "ESTABLISHED"
    expect_failure(lambda: MOD.validate_review(changed), "physical_background")

    changed = copy.deepcopy(review)
    changed["gate_state"]["K1-D"] = "RELEASED"
    expect_failure(lambda: MOD.validate_review(changed), "K1-D")


def main() -> int:
    test_repository_review_passes()
    test_authorization_opening_is_rejected()
    test_missing_runner_cannot_be_marked_pass()
    test_review_cannot_execute_solver()
    test_result_creation_is_rejected()
    test_physical_and_release_overclaims_are_rejected()
    print("PASS: Background-3C3 authorization review regression tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
