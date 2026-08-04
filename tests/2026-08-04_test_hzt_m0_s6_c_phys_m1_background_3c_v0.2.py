#!/usr/bin/env python3
"""Regression and fail-closed tests for Background-3C primary implementation."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3c_v0.2.py"
GATE_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_gate_v0.2.py"
KERNEL_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module("background3c_validator_test", VALIDATOR_PATH)
GATE = load_module("background3c_gate_test", GATE_PATH)
KERNEL = load_module("background3c_kernel_test", KERNEL_PATH)


def expect_failure(function, phrase: str) -> None:
    try:
        function()
    except (VALIDATOR.ContractError, RuntimeError, ValueError) as exc:
        assert phrase in str(exc), (phrase, str(exc))
        return
    raise AssertionError(f"expected failure containing: {phrase}")


def test_repository_contract_passes_without_newton() -> None:
    before = KERNEL.NEWTON_CALL_COUNT
    result = VALIDATOR.validate()
    assert result["status"] == "PASS"
    assert result["audit"]["status"] == "PASS_PRIMARY_IMPLEMENTATION_AUDIT_NO_SOLVER_EXECUTION"
    assert result["audit"]["newton_call_count"] == 0
    assert KERNEL.NEWTON_CALL_COUNT == before == 0
    assert result["solver_executed"] is False
    assert result["physical_evidence_effect"] == "NONE"
    assert result["next_block"] == "C-PHYS-R1.0-BACKGROUND-3C2_INDEPENDENT_BACKEND_AND_EXECUTION_PACKAGE"


def test_seed_adapter_matches_frozen_formula() -> None:
    node_count = 24
    base = KERNEL.control_seed_state(node_count)
    direction = KERNEL.seed_direction(node_count)
    seeds = KERNEL.seven_seeds(node_count)
    assert len(seeds) == 7
    assert KERNEL.SEED_AMPLITUDE_SCALE == 1.0 / 20.0
    expected_multipliers = (0.0, 1/8, -1/8, 1/4, -1/4, 1/2, -1/2)
    assert KERNEL.SEED_MULTIPLIERS == expected_multipliers
    for seed, multiplier in zip(seeds, expected_multipliers):
        np.testing.assert_allclose(seed, base + (1.0 / 20.0) * multiplier * direction, rtol=0.0, atol=0.0)


def test_run_command_is_denied_before_newton_and_writes_nothing() -> None:
    output_root = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
    assert not output_root.exists()
    before = KERNEL.NEWTON_CALL_COUNT
    process = subprocess.run(
        [sys.executable, str(GATE_PATH), "run", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert process.returncode == 73, process.stdout + process.stderr
    payload = json.loads(process.stdout)
    assert payload["status"] == "NOT_AUTHORIZED"
    assert payload["solver_executed"] is False
    assert payload["result_artifact_created"] is False
    assert KERNEL.NEWTON_CALL_COUNT == before == 0
    assert not output_root.exists()


def test_direct_kernel_invocation_is_denied() -> None:
    process = subprocess.run(
        [sys.executable, str(KERNEL_PATH)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert process.returncode == 73
    assert "NOT_AUTHORIZED" in process.stdout


def test_rrqr_rank_deficiency_is_rejected() -> None:
    singular = np.asarray([[1.0, 2.0], [2.0, 4.0]])
    expect_failure(lambda: KERNEL.rrqr_step(singular, np.asarray([1.0, 2.0])), "RRQR rank deficient")


def test_source_hash_drift_is_rejected() -> None:
    contract = VALIDATOR.load_json(VALIDATOR.CONTRACT)
    changed = copy.deepcopy(contract)
    changed["implementation_source"]["canonical_primary_kernel_git_blob_sha"] = "0" * 40
    expect_failure(lambda: VALIDATOR.validate_source_identity(changed), "source blob hash drift")


def test_execution_and_evidence_overclaims_are_rejected() -> None:
    contract = VALIDATOR.load_json(VALIDATOR.CONTRACT)
    changed = copy.deepcopy(contract)
    changed["current_execution_state"]["newton_executed"] = True
    expect_failure(lambda: VALIDATOR.validate_contract(changed), "execution-state overclaim")

    changed = copy.deepcopy(contract)
    changed["gate_state"]["physical_evidence_effect"] = "SUPPORT"
    expect_failure(lambda: VALIDATOR.validate_contract(changed), "physical_evidence_effect")


def test_result_overwrite_and_network_opening_are_rejected() -> None:
    result = VALIDATOR.load_json(VALIDATOR.RESULT_SCHEMA)
    resources = VALIDATOR.load_json(VALIDATOR.RESOURCE_POLICY)
    changed_result = copy.deepcopy(result)
    changed_result["immutable_output_policy"]["overwrite_existing_path"] = True
    original_result_loader = VALIDATOR.load_json

    def load_result_override(path: Path):
        if path == VALIDATOR.RESULT_SCHEMA:
            return changed_result
        if path == VALIDATOR.RESOURCE_POLICY:
            return resources
        return original_result_loader(path)

    VALIDATOR.load_json = load_result_override
    try:
        expect_failure(VALIDATOR.validate_result_and_resource_contracts, "output overwrite")
    finally:
        VALIDATOR.load_json = original_result_loader

    changed_resources = copy.deepcopy(resources)
    changed_resources["execution_environment"]["network_access"] = True

    def load_resource_override(path: Path):
        if path == VALIDATOR.RESULT_SCHEMA:
            return result
        if path == VALIDATOR.RESOURCE_POLICY:
            return changed_resources
        return original_result_loader(path)

    VALIDATOR.load_json = load_resource_override
    try:
        expect_failure(VALIDATOR.validate_result_and_resource_contracts, "network access")
    finally:
        VALIDATOR.load_json = original_result_loader


def test_future_grant_is_absent() -> None:
    assert not VALIDATOR.FUTURE_GRANT.exists()
    result = VALIDATOR.validate_authorization()
    assert result == {"status": "NOT_GRANTED", "future_grant_present": False}


def main() -> int:
    test_repository_contract_passes_without_newton()
    test_seed_adapter_matches_frozen_formula()
    test_run_command_is_denied_before_newton_and_writes_nothing()
    test_direct_kernel_invocation_is_denied()
    test_rrqr_rank_deficiency_is_rejected()
    test_source_hash_drift_is_rejected()
    test_execution_and_evidence_overclaims_are_rejected()
    test_result_overwrite_and_network_opening_are_rejected()
    test_future_grant_is_absent()
    print("PASS: Background-3C primary implementation regression tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
