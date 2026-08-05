#!/usr/bin/env python3
"""Fail-closed validator for the Background-3C7 authorization review."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C7IntegratedReleaseAuthorizationReview_v0.1.json"
BG3C6_VALIDATOR_PATH = ROOT / "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c6_v0.1.py"
BG3C6_ENTRY_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c6_integrated_release_v0.2.py"
PHYSICAL_ADAPTER_CONTRACT = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C8PhysicalExecutionAdapterContract_v0.1.json"
PHYSICAL_ADAPTER_ENTRY = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c8_physical_execution_adapter_v0.1.py"
PHYSICAL_ADAPTER_AUDIT = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C8PhysicalExecutionAdapterAuditResult_v0.1.json"
GRANT = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
LEGACY_GRANT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
PHYSICAL_ARTIFACT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
EXPECTED_STATUS = "DENIED_PHYSICAL_BACKEND_ADAPTER_AND_SINGLE_USE_GRANT_RELEASE_ABSENT"
NEXT = "C-PHYS-R1.0-BACKGROUND-3C8_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_ONLY"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate() -> dict:
    review = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    assert review["status"] == EXPECTED_STATUS
    assert review["classification"] == "APPEND_ONLY_FAIL_CLOSED_PHYSICAL_EXECUTION_ELIGIBILITY_REVIEW"
    assert review["physical_evidence_effect"] == "NONE"
    decision = review["authorization_decision"]
    for key in (
        "authorized",
        "grant_created",
        "physical_backend_imported",
        "primary_newton_called",
        "independent_shooting_called",
        "shooting_jacobian_called",
        "cp01r1_attempted",
        "result_artifact_created",
    ):
        assert decision[key] is False, (key, decision[key])

    passed = review["passed_prerequisites"]
    assert passed and all(value is True for value in passed.values())
    blockers = review["blocking_findings"]
    expected_missing = {
        "physical_execution_adapter_contract": "NOT_PRESENT",
        "source_hash_bound_physical_adapter": "NOT_PRESENT",
        "frozen_seed_mesh_orchestration_wired_to_primary_backend": "NOT_PRESENT",
        "primary_candidate_to_independent_backend_handoff": "NOT_PRESENT",
        "physical_backend_subprocess_resource_binding": "NOT_PRESENT",
        "physical_backend_output_to_result_schema_translation": "NOT_PRESENT",
        "joint_primary_independent_candidate_classification_transaction": "NOT_PRESENT",
        "single_use_grant_schema_bound_to_run_payload_adapter_digest_and_commit": "NOT_PRESENT",
        "grant_consumption_and_replay_prevention": "NOT_IMPLEMENTED",
        "authorizable_physical_runner_release": "NOT_PRESENT",
    }
    for key, value in expected_missing.items():
        assert blockers[key] == value, (key, blockers.get(key), value)
    assert blockers["physical_backend_interruption_test_across_real_adapter_boundary"] == "NOT_PERFORMED"
    assert blockers["canonical_control_entry_point_allows_physical_backend_import"] is False
    assert blockers["canonical_control_entry_point_allows_cp01r1_run"] is False

    assert review["future_adapter_constraints"]["implementation_block_only"] is True
    assert review["future_adapter_constraints"]["cp01r1_execution_forbidden"] is True
    assert review["future_adapter_constraints"]["grant_creation_forbidden"] is True
    assert review["future_adapter_constraints"]["physical_target_root_solve_forbidden"] is True
    assert review["future_adapter_constraints"]["may_reuse_background_3c6_as_physical_grant"] is False
    assert review["next_allowed_block"] == NEXT

    gates = review["gate_state"]
    assert gates["BACKGROUND_3C6_INTEGRATED_CONTROL_RELEASE"] == "PASS_AUDITED_CONTROL_ONLY"
    assert gates["BACKGROUND_3C7_AUTHORIZATION_REVIEW"] == EXPECTED_STATUS
    assert gates["BACKGROUND_3C_EXECUTION"] == "NOT_AUTHORIZED"
    assert gates["BACKGROUND_SOLVER_EXECUTION"] == "NOT_AUTHORIZED"
    assert gates["physical_background"] == "NOT_ESTABLISHED"
    assert gates["R1.1"] == "BLOCKED"
    assert gates["R1.2"] == "BLOCKED"
    assert gates["official_MD2S_solver"] == "NOT_AUTHORIZED"
    assert gates["K1-D"] == "NOT_RELEASED"
    assert gates["K1-E"] == "NOT_ADMISSIBLE"
    assert gates["physical_evidence_effect"] == "NONE"

    bg3c6 = load_module(BG3C6_VALIDATOR_PATH, "bg3c6_from_bg3c7")
    bg3c6_result = bg3c6.validate()
    assert bg3c6_result["status"] == "PASS"
    assert bg3c6_result["physical_solver_calls"] == 0
    assert bg3c6_result["cp01r1_attempts"] == 0

    entry = load_module(BG3C6_ENTRY_PATH, "bg3c6_entry_from_bg3c7")
    denial = entry.BASE.denied_physical_run("HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1")
    assert denial["status"] == "NOT_AUTHORIZED"
    assert denial["exit_code"] == 73
    assert denial["subprocess_launches"] == 0
    assert denial["solver_calls"] == 0
    assert denial["result_artifact_created"] is False

    for path in (
        PHYSICAL_ADAPTER_CONTRACT,
        PHYSICAL_ADAPTER_ENTRY,
        PHYSICAL_ADAPTER_AUDIT,
        GRANT,
        LEGACY_GRANT,
        PHYSICAL_ARTIFACT,
    ):
        assert not path.exists(), str(path)

    return {
        "status": "PASS",
        "review_status": EXPECTED_STATUS,
        "background_3c6_revalidated": True,
        "physical_adapter_present": False,
        "grant_present": False,
        "physical_backend_imported": False,
        "physical_solver_calls": 0,
        "cp01r1_attempts": 0,
        "result_artifact_created": False,
        "physical_evidence_effect": "NONE",
        "next_block": NEXT,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS: Background-3C7 authorization denied without physical execution")


if __name__ == "__main__":
    main()
