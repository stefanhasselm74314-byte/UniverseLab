#!/usr/bin/env python3
"""Regression and negative tests for Background-3A assembly correction v0.3."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3a_assembly_v0.3.py"
SPEC = importlib.util.spec_from_file_location("background3a_assembly_validator", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import assembly validator")
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


def payloads():
    return (
        MOD.load_json(MOD.METHOD),
        MOD.load_json(MOD.TOPOLOGY),
        MOD.load_json(MOD.ASSEMBLY),
        MOD.load_json(MOD.RUN_V1),
        MOD.load_json(MOD.RUN_V2),
    )


def test_repository_contract_passes() -> None:
    result = MOD.validate()
    assert result["status"] == "PASS"
    assert result["assembly"] == {"unknowns": "8*N+8", "residuals": "8*N+8"}
    assert result["run_rebind"]["new_run_id"].endswith("CP01R1")
    assert result["run_rebind"]["run_hash"] == MOD.EXPECTED_RUN_HASH
    assert result["solver_executed"] is False
    assert result["physical_evidence_effect"] == "NONE"


def test_strict_interior_count_is_rejected() -> None:
    method, topology, assembly, _, _ = payloads()
    changed = copy.deepcopy(assembly)
    changed["counting_audit"]["regularized_bulk_residuals_at_all_nodes"] = "8*(N-2)"
    expect_failure(lambda: MOD.validate_assembly(method, topology, changed), "bulk row count")


def test_degree_rule_drift_is_rejected() -> None:
    method, topology, assembly, _, _ = payloads()
    changed = copy.deepcopy(assembly)
    changed["canonical_assembly"]["degree_rule"] = "degree=node_count"
    expect_failure(lambda: MOD.validate_assembly(method, topology, changed), "degree rule")


def test_constraint_double_count_is_rejected() -> None:
    method, topology, assembly, _, _ = payloads()
    changed = copy.deepcopy(assembly)
    changed["canonical_assembly"]["constraint_role"] = "APPENDED_NONLINEAR_RESIDUAL"
    expect_failure(lambda: MOD.validate_assembly(method, topology, changed), "constraint role")


def test_reusing_old_run_id_is_rejected() -> None:
    _, _, _, old, new = payloads()
    changed = copy.deepcopy(new)
    changed["frozen_run_payload"]["run_id"] = old["frozen_run_payload"]["run_id"]
    expect_failure(lambda: MOD.validate_rebound(old, changed), "new run identity")


def test_parameter_or_topology_mutation_is_rejected() -> None:
    _, _, _, old, new = payloads()
    changed = copy.deepcopy(new)
    changed["frozen_run_payload"]["model_parameters_ordered"]["a_F"] = "1/3"
    expect_failure(lambda: MOD.validate_rebound(old, changed), "unexpected control-point change")

    changed = copy.deepcopy(new)
    changed["frozen_run_payload"]["topological_sector_ordered"]["N_sigma"] = 2
    expect_failure(lambda: MOD.validate_rebound(old, changed), "unexpected control-point change")


def test_hash_mutation_is_rejected() -> None:
    _, _, _, old, new = payloads()
    changed = copy.deepcopy(new)
    changed["frozen_run_payload_sha256"] = "0" * 64
    expect_failure(lambda: MOD.validate_rebound(old, changed), "recorded CP01R1 hash")


def test_solver_or_evidence_opening_is_rejected() -> None:
    _, _, _, old, new = payloads()
    changed = copy.deepcopy(new)
    changed["execution_firewall"]["nonlinear_solver_run"] = True
    expect_failure(lambda: MOD.validate_rebound(old, changed), "execution firewall")

    changed = copy.deepcopy(new)
    changed["gate_state"]["physical_evidence_effect"] = "SUPPORT"
    expect_failure(lambda: MOD.validate_rebound(old, changed), "physical evidence")


def main() -> int:
    test_repository_contract_passes()
    test_strict_interior_count_is_rejected()
    test_degree_rule_drift_is_rejected()
    test_constraint_double_count_is_rejected()
    test_reusing_old_run_id_is_rejected()
    test_parameter_or_topology_mutation_is_rejected()
    test_hash_mutation_is_rejected()
    test_solver_or_evidence_opening_is_rejected()
    print("PASS: Background-3A assembly correction regression tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
