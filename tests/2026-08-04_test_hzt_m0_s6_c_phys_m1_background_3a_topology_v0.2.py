#!/usr/bin/env python3
"""Regression tests for the Background-3A topology correction v0.2."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3a_topology_v0.2.py"

SPEC = importlib.util.spec_from_file_location("background3a_topology_v02", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import Background-3A topology validator")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def load_all():
    return (
        MOD.load(MOD.V01),
        MOD.load(MOD.V02),
        MOD.load(MOD.PARENT),
        MOD.load(MOD.GLOBAL),
        MOD.load(MOD.M1),
        MOD.load(MOD.OP2B),
    )


def expect_failure(payloads, phrase: str) -> None:
    try:
        MOD.validate_payloads(*payloads)
    except MOD.ContractError as exc:
        assert phrase in str(exc), (phrase, str(exc))
        return
    raise AssertionError(f"expected ContractError containing: {phrase}")


def test_repository_contract_passes() -> None:
    result = MOD.validate()
    assert result["status"] == "PASS"
    assert result["historical_v0_1_vector"] == ["N_F", "m_N", "m_S", "n_N", "n_S"]
    assert result["canonical_v0_2_vector"] == ["N_F", "N_sigma", "m_sigma"]
    assert result["canonical_count"] == 3
    assert result["single_cap_phase"] is True
    assert result["solver_authorized"] is False
    assert result["current_execution"] == "NOT_EXECUTED"
    assert result["physical_evidence_effect"] == "NONE"


def test_regionalized_vector_is_rejected() -> None:
    payloads = list(load_all())
    payloads[1] = copy.deepcopy(payloads[1])
    payloads[1]["canonical_effective_topological_input"]["ordered_vector"] = [
        "N_F", "m_N", "m_S", "n_N", "n_S"
    ]
    expect_failure(tuple(payloads), "canonical topology vector")


def test_second_cap_phase_requires_new_model() -> None:
    payloads = list(load_all())
    payloads[1] = copy.deepcopy(payloads[1])
    payloads[1]["forbidden_regional_expansion"]["future_two_cap_phase_extension"] = "ALLOWED_IN_M1"
    expect_failure(tuple(payloads), "new-model firewall")


def test_parent_single_sigma_is_required() -> None:
    payloads = list(load_all())
    payloads[2] = copy.deepcopy(payloads[2])
    payloads[2]["parent_action"]["D_a_sigma"] = "regionalized"
    expect_failure(tuple(payloads), "single sigma")


def test_m1_discrete_sector_is_required() -> None:
    payloads = list(load_all())
    payloads[4] = copy.deepcopy(payloads[4])
    payloads[4]["discrete_sector"]["m_sigma"] = "integer"
    expect_failure(tuple(payloads), "M1 discrete sector")


def test_run_input_and_solver_stay_closed() -> None:
    payloads = list(load_all())
    payloads[1] = copy.deepcopy(payloads[1])
    payloads[1]["effective_background_3a_status"]["exact_run_input_frozen"] = True
    expect_failure(tuple(payloads), "run input overclaim")

    payloads = list(load_all())
    payloads[1] = copy.deepcopy(payloads[1])
    payloads[1]["solver_authorized"] = True
    expect_failure(tuple(payloads), "solver authorization")


def test_release_gate_opening_is_rejected() -> None:
    payloads = list(load_all())
    payloads[1] = copy.deepcopy(payloads[1])
    payloads[1]["gate_state"]["K1-D"] = "RELEASED"
    expect_failure(tuple(payloads), "K1-D")


def main() -> int:
    test_repository_contract_passes()
    test_regionalized_vector_is_rejected()
    test_second_cap_phase_requires_new_model()
    test_parent_single_sigma_is_required()
    test_m1_discrete_sector_is_required()
    test_run_input_and_solver_stay_closed()
    test_release_gate_opening_is_rejected()
    print("PASS: Background-3A topology correction regression tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
