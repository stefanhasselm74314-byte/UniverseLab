#!/usr/bin/env python3
"""Regression and negative tests for the Background-3B run-input freeze."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3b_v0.1.py"

SPEC = importlib.util.spec_from_file_location("background3b_validator", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import Background-3B validator")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def base_payloads():
    return (
        MOD.load_json(MOD.CONTRACT),
        MOD.load_json(MOD.SEEDS),
        MOD.load_json(MOD.METHOD),
        MOD.load_json(MOD.TOPOLOGY),
    )


def expect_failure(function, phrase: str) -> None:
    try:
        function()
    except MOD.ContractError as exc:
        assert phrase in str(exc), (phrase, str(exc))
        return
    raise AssertionError(f"expected ContractError containing: {phrase}")


def test_repository_contract_passes() -> None:
    result = MOD.validate()
    assert result["status"] == "PASS"
    assert result["run_payload"]["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01"
    assert result["run_payload"]["sha256"] == MOD.EXPECTED_RUN_SHA256
    assert result["seed_spec"]["sha256"] == MOD.EXPECTED_SEED_SHA256
    assert result["dependency_lock"]["sha256"] == MOD.EXPECTED_LOCK_SHA256
    assert result["source_consistency"]["topology_vector"] == ["N_F", "N_sigma", "m_sigma"]
    assert result["source_consistency"]["topology_values"] == [1, 1, 1]
    assert result["control_seed"]["classification"] == "EXACT_BULK_AND_PATCH_SEED_BOUNDARY_INEXACT"
    assert result["control_seed"]["cap_defects"] == "NONZERO_AS_PREREGISTERED"
    assert result["firewall"]["execution"] == "NOT_EXECUTED"
    assert result["firewall"]["solver_authorized"] is False
    assert result["physical_evidence_effect"] == "NONE"


def test_parameter_change_breaks_run_hash() -> None:
    contract, _, _, _ = base_payloads()
    changed = copy.deepcopy(contract)
    changed["frozen_run_payload"]["model_parameters_ordered"]["a_F"] = "1/3"
    expect_failure(lambda: MOD.verify_run_payload(changed), "recomputed run payload hash")


def test_topology_change_breaks_run_hash() -> None:
    contract, _, _, _ = base_payloads()
    changed = copy.deepcopy(contract)
    changed["frozen_run_payload"]["topological_sector_ordered"]["N_sigma"] = 2
    expect_failure(lambda: MOD.verify_run_payload(changed), "recomputed run payload hash")


def test_regional_topology_labels_are_rejected() -> None:
    contract, _, _, _ = base_payloads()
    changed = copy.deepcopy(contract)
    run = changed["frozen_run_payload"]
    run["topological_sector_ordered"] = {"N_F": 1, "m_N": 1, "m_S": 1, "n_N": 1, "n_S": 1}
    changed["frozen_run_payload_sha256"] = MOD.canonical_json_sha256(run)
    expect_failure(lambda: MOD.verify_run_payload(changed), "single-cap topology sector")


def test_dependency_hash_drift_is_rejected() -> None:
    contract, _, _, _ = base_payloads()
    changed = copy.deepcopy(contract)
    changed["frozen_run_payload"]["dependency_lock_sha256"] = "0" * 64
    expect_failure(lambda: MOD.verify_dependency_lock(changed), "run payload dependency hash")


def test_seed_hash_drift_is_rejected() -> None:
    contract, seeds, _, _ = base_payloads()
    changed = copy.deepcopy(seeds)
    changed["seed_generation"]["amplitude_scale"] = "1/10"
    expect_failure(lambda: MOD.verify_seed_hash(contract, changed), "recomputed seed payload hash")


def test_seed_solution_overclaim_is_rejected() -> None:
    _, seeds, _, _ = base_payloads()
    changed = copy.deepcopy(seeds)
    changed["base_control_seed"]["not_a_solution"] = False
    expect_failure(lambda: MOD.verify_exact_control_seed(changed), "solution overclaim")


def test_hidden_cap_defect_closure_is_rejected() -> None:
    _, seeds, _, _ = base_payloads()
    changed = copy.deepcopy(seeds)
    changed["base_control_seed"]["deliberately_nonzero_cap_defects"]["R_4d"] = "0"
    expect_failure(lambda: MOD.verify_exact_control_seed(changed), "recorded cap defects")


def test_c1_and_a0_migration_are_rejected() -> None:
    contract, _, _, _ = base_payloads()
    changed = copy.deepcopy(contract)
    changed["selection_firewall"]["C1_V_values_used"] = True
    expect_failure(lambda: MOD.verify_firewalls(changed), "C1_V_values_used")

    changed = copy.deepcopy(contract)
    changed["selection_firewall"]["historical_A0_values_used"] = True
    expect_failure(lambda: MOD.verify_firewalls(changed), "historical_A0_values_used")


def test_solver_and_execution_opening_are_rejected() -> None:
    contract, _, _, _ = base_payloads()
    changed = copy.deepcopy(contract)
    changed["solver_authorized"] = True
    expect_failure(lambda: MOD.verify_firewalls(changed), "solver authorization")

    changed = copy.deepcopy(contract)
    changed["execution_firewall"]["nonlinear_solver_run"] = True
    expect_failure(lambda: MOD.verify_firewalls(changed), "nonlinear_solver_run")

    changed = copy.deepcopy(contract)
    changed["execution_firewall"]["background_candidate_created"] = True
    expect_failure(lambda: MOD.verify_firewalls(changed), "background_candidate_created")


def test_release_gate_opening_is_rejected() -> None:
    contract, _, _, _ = base_payloads()
    changed = copy.deepcopy(contract)
    changed["gate_state"]["K1-D"] = "RELEASED"
    expect_failure(lambda: MOD.verify_firewalls(changed), "K1-D")


def main() -> int:
    test_repository_contract_passes()
    test_parameter_change_breaks_run_hash()
    test_topology_change_breaks_run_hash()
    test_regional_topology_labels_are_rejected()
    test_dependency_hash_drift_is_rejected()
    test_seed_hash_drift_is_rejected()
    test_seed_solution_overclaim_is_rejected()
    test_hidden_cap_defect_closure_is_rejected()
    test_c1_and_a0_migration_are_rejected()
    test_solver_and_execution_opening_are_rejected()
    test_release_gate_opening_is_rejected()
    print("PASS: Background-3B exact run-input regression tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
