#!/usr/bin/env python3
"""Regression and negative tests for Background-3A preregistration."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3a_v0.1.py"

SPEC = importlib.util.spec_from_file_location("background_3a_validator", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import Background-3A validator")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def expect_failure(payload: dict, phrase: str) -> None:
    try:
        MOD.validate_payload(payload)
    except MOD.ContractError as exc:
        assert phrase in str(exc), (phrase, str(exc))
        return
    raise AssertionError(f"expected ContractError containing: {phrase}")


def test_repository_contract_passes() -> None:
    result = MOD.validate()
    assert result["status"] == "PASS"
    assert result["block"] == "C-PHYS-R1.0-BACKGROUND-3A"
    assert result["execution"] == "NOT_EXECUTED"
    assert result["solver_authorized"] is False
    assert result["next_block"] == "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY"
    assert result["physical_evidence_effect"] == "NONE"


def test_solver_execution_is_blocked() -> None:
    payload = copy.deepcopy(MOD.load_contract())
    payload["execution_firewall"]["nonlinear_solver_run"] = True
    expect_failure(payload, "nonlinear_solver_run")


def test_post_hoc_parameter_change_is_blocked() -> None:
    payload = copy.deepcopy(MOD.load_contract())
    payload["future_run_input_contract"]["post_hoc_parameter_change_under_same_run_id"] = True
    expect_failure(payload, "post-hoc parameter change")


def test_adaptive_mesh_tuning_is_blocked() -> None:
    payload = copy.deepcopy(MOD.load_contract())
    payload["primary_discretization"]["adaptive_mesh_or_order_selection"] = True
    expect_failure(payload, "adaptive post-hoc mesh")


def test_random_seed_drift_is_blocked() -> None:
    payload = copy.deepcopy(MOD.load_contract())
    payload["deterministic_seed_protocol"]["random_seed_use"] = True
    expect_failure(payload, "random seeds")


def test_single_mesh_acceptance_is_blocked() -> None:
    payload = copy.deepcopy(MOD.load_contract())
    payload["convergence_requirements"]["single_mesh_acceptance_forbidden"] = False
    expect_failure(payload, "single-mesh acceptance")


def test_backend_source_sharing_is_blocked() -> None:
    payload = copy.deepcopy(MOD.load_contract())
    payload["independent_backend_requirement"]["shared_source_code_for_residual_assembly"] = True
    expect_failure(payload, "backend source independence")


def test_physical_evidence_upgrade_is_blocked() -> None:
    payload = copy.deepcopy(MOD.load_contract())
    payload["physical_evidence_effect"] = "CONFIRMATION"
    expect_failure(payload, "physical evidence")


def test_release_gate_opening_is_blocked() -> None:
    payload = copy.deepcopy(MOD.load_contract())
    payload["gate_state"]["K1-D"] = "RELEASED"
    expect_failure(payload, "K1-D")


def main() -> int:
    test_repository_contract_passes()
    test_solver_execution_is_blocked()
    test_post_hoc_parameter_change_is_blocked()
    test_adaptive_mesh_tuning_is_blocked()
    test_random_seed_drift_is_blocked()
    test_single_mesh_acceptance_is_blocked()
    test_backend_source_sharing_is_blocked()
    test_physical_evidence_upgrade_is_blocked()
    test_release_gate_opening_is_blocked()
    print("PASS: Background-3A preregistration regression tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
