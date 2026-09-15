#!/usr/bin/env python3
"""Fail-closed validator for Background-3C12 v0.2 controls."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
RELEASE_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c12_target_path_release_v0.2.py"
GRANT_CONTRACT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C12SingleUseGrantContract_v0.1.json"
TARGET_CONTRACT_V01_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C12TargetPathReleaseContract_v0.1.json"
TARGET_CONTRACT_V02_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C12TargetPathReleaseContract_v0.2.json"
REVIEW_3C11_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C11RealBackendControlAuthorizationReview_v0.1.json"
RUN_INPUT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"
SEED_SPEC_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BSeedSpecification_v0.1.json"
OPERATIVE_GRANTS = (
    ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",
    ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",
)
PHYSICAL_ARTIFACT_ROOT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
EXPECTED_TERMINAL_STATES = {
    "success": "CONSUMED_SYNTHETIC_SUCCESS",
    "failure": "CONSUMED_SYNTHETIC_FAILURE",
    "timeout": "CONSUMED_SYNTHETIC_TIMEOUT",
    "signal": "CONSUMED_SYNTHETIC_SIGNAL",
    "crash": "CONSUMED_SYNTHETIC_CRASH",
}
EXPECTED_INVALID_REJECTIONS = [
    "binding", "control_override", "digest", "expired", "not_before", "operative",
]


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"object required: {path}")
    return value


def load_release():
    spec = importlib.util.spec_from_file_location("background3c12_release_v02", RELEASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to import Background-3C12 release v0.2")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate() -> dict:
    grant_contract = load_json(GRANT_CONTRACT_PATH)
    target_v01 = load_json(TARGET_CONTRACT_V01_PATH)
    target_v02 = load_json(TARGET_CONTRACT_V02_PATH)
    review = load_json(REVIEW_3C11_PATH)
    run_input = load_json(RUN_INPUT_PATH)
    seed_spec = load_json(SEED_SPEC_PATH)
    release = load_release()

    assert grant_contract["status"] == "IMPLEMENTED_PENDING_AUDIT_NOT_AN_AUTHORIZATION"
    assert grant_contract["classification"] == "NONOPERATIVE_SYNTHETIC_SINGLE_USE_GRANT_SCHEMA"
    assert grant_contract["operative"] is False
    assert grant_contract["physical_evidence_effect"] == "NONE"
    assert grant_contract["single_consumption_state_machine"]["atomic_reservation_required"] is True
    assert grant_contract["single_consumption_state_machine"]["replay_after_reservation_rejected"] is True
    assert grant_contract["single_consumption_state_machine"]["replay_after_any_terminal_state_rejected"] is True
    assert grant_contract["single_consumption_state_machine"]["reuse_after_crash_recovery_rejected"] is True
    for value in grant_contract["hard_firewalls"].values():
        assert value is False

    assert target_v02["status"] == "IMPLEMENTED_PENDING_AUDIT_EXECUTION_NOT_AUTHORIZED"
    assert target_v02["supersedes_for_audit"] == str(TARGET_CONTRACT_V01_PATH.relative_to(ROOT))
    correction = target_v02["pre_audit_correction"]
    assert correction["audit_or_control_run_executed_under_v0_1"] is False
    assert correction["scientific_acceptance_threshold_changed"] is False
    assert correction["model_or_topology_changed"] is False
    assert correction["target_identity_changed"] is False
    assert correction["schedule_changed"] is False
    assert correction["grant_binding_changed"] is False
    assert correction["corrected_item"] == "DEFAULT_SYNTHETIC_NOT_BEFORE_EQUALS_ISSUED_AT"
    assert target_v01["target_identity"] == target_v02["target_identity"]
    assert target_v02["source_bindings"]["target_path_entry_point"] == str(RELEASE_PATH.relative_to(ROOT))
    assert target_v02["target_identity"]["run_id"] == release.BASE.TARGET_RUN_ID
    assert target_v02["target_identity"]["a_F"] == release.BASE.TARGET_A_F
    assert target_v02["target_identity"]["seed_count"] == 7
    assert target_v02["target_identity"]["schedule_entry_count"] == 35
    assert target_v02["target_identity"]["schedule_sha256"] == release.BASE.SCHEDULE_SHA256
    for value in target_v02["hard_firewalls"].values():
        assert value is False

    assert review["status"] == release.BASE.DENIAL_3C11
    assert review["authorization_decision"]["authorized"] is False
    assert review["future_implementation_constraints"]["next_block"] == target_v02["block"]
    assert review["future_implementation_constraints"]["physical_backend_import_forbidden"] is True
    assert review["future_implementation_constraints"]["cp01r1_execution_forbidden"] is True
    assert review["future_implementation_constraints"]["operative_grant_creation_forbidden"] is True

    assert run_input["status"] == "RUN_INPUT_FROZEN_CP01R1_EXECUTION_NOT_AUTHORIZED"
    assert run_input["solver_authorized"] is False
    assert run_input["frozen_run_payload"]["run_id"] == release.BASE.TARGET_RUN_ID
    assert run_input["frozen_run_payload"]["model_parameters_ordered"]["a_F"] == release.BASE.TARGET_A_F
    assert run_input["execution_firewall"]["current_execution"] == "NOT_EXECUTED"
    assert run_input["execution_firewall"]["solver_initialization"] is False
    assert run_input["execution_firewall"]["nonlinear_solver_run"] is False
    assert run_input["execution_firewall"]["background_candidate_created"] is False
    assert seed_spec["seed_set_id"] == target_v02["target_identity"]["seed_set_id"]

    audit = release.static_audit()
    assert audit["status"] == "PASS_3C12_V02_STATIC_AUDIT_NO_BACKEND_IMPORT_NO_EXECUTION"
    assert audit["release_adapter"] == "v0.2"
    assert audit["source_count"] == 18
    assert re.fullmatch(r"[0-9a-f]{64}", audit["package_manifest_sha256"])
    assert re.fullmatch(r"[0-9a-f]{40}", audit["checkout_commit_sha"])
    assert audit["target_run_id"] == release.BASE.TARGET_RUN_ID
    assert audit["target_a_F"] == release.BASE.TARGET_A_F
    assert audit["schedule_entry_count"] == 35
    assert audit["schedule_sha256"] == release.BASE.SCHEDULE_SHA256
    assert re.fullmatch(r"[0-9a-f]{64}", audit["target_plan_sha256"])
    assert audit["pre_audit_correction"] == "DEFAULT_SYNTHETIC_NOT_BEFORE_EQUALS_ISSUED_AT"
    assert audit["default_not_before_equals_issued_at"] is True
    assert audit["physical_backend_imports"] == 0
    assert audit["physical_solver_calls"] == 0
    assert audit["cp01r1_attempts"] == 0
    assert audit["target_solves"] == 0
    assert audit["operative_grants"] == 0
    assert audit["physical_results"] == 0
    assert audit["physical_evidence_effect"] == "NONE"

    now = datetime.now(timezone.utc)
    immediate = release.issue_synthetic_grant(audit["binding"], now=now)
    assert immediate["issued_at_utc"] == immediate["not_before_utc"]
    release.BASE.validate_grant(immediate, audit["binding"], now=now)

    result = release.self_test()
    assert result["status"] == "PASS_3C12_V02_NONOPERATIVE_GRANT_AND_TARGET_PATH_CONTROLS"
    assert result["release_adapter"] == "v0.2"
    assert result["package_manifest_sha256"] == audit["package_manifest_sha256"]
    assert result["checkout_commit_sha"] == audit["checkout_commit_sha"]
    assert result["source_count"] == 18
    assert result["target_run_id"] == release.BASE.TARGET_RUN_ID
    assert result["target_a_F"] == release.BASE.TARGET_A_F
    assert result["schedule_entry_count"] == 35
    assert result["schedule_sha256"] == release.BASE.SCHEDULE_SHA256
    assert result["target_plan_sha256"] == audit["target_plan_sha256"]
    assert result["terminal_states"] == EXPECTED_TERMINAL_STATES
    assert result["worker_launch_count"] == 5
    assert result["replay_rejections"] == 6
    assert result["parallel_reservation_race"] == "PASS_EXACTLY_ONE_WINNER"
    assert result["invalid_rejections"] == EXPECTED_INVALID_REJECTIONS
    assert result["grant_instances_persisted_in_repository"] == 0
    assert result["operative_grants_created"] == 0
    assert result["physical_backend_imports"] == 0
    assert result["physical_solver_calls"] == 0
    assert result["cp01r1_attempts"] == 0
    assert result["target_solves"] == 0
    assert result["physical_result_artifacts"] == 0
    assert result["default_not_before_equals_issued_at"] is True
    assert result["physical_evidence_effect"] == "NONE"
    translation = result["result_schema_translation"]
    assert set(translation["mapped_fields"]) == set(translation["required_fields"])
    assert re.fullmatch(r"[0-9a-f]{64}", translation["preview_sha256"])
    assert translation["result_schema_preview_is_physical_result"] is False
    assert translation["result_artifact_created"] is False
    assert result["next_block"] == target_v02["next_block_if_pass"]

    denial = release.denied_physical_run()
    assert denial["status"] == "NOT_AUTHORIZED"
    assert denial["release_adapter"] == "v0.2"
    assert denial["physical_backend_imported"] is False
    assert denial["solver_calls"] == 0
    assert denial["cp01r1_attempted"] is False
    assert denial["target_a_F_one_quarter_solve"] is False
    assert denial["operative_grant_created"] is False
    assert denial["result_artifact_created"] is False
    assert denial["physical_evidence_effect"] == "NONE"

    assert all(not path.exists() for path in OPERATIVE_GRANTS)
    assert not PHYSICAL_ARTIFACT_ROOT.exists()

    return {
        "status": "PASS",
        "audit_status": audit["status"],
        "control_status": result["status"],
        "package_manifest_sha256": audit["package_manifest_sha256"],
        "checkout_commit_sha": audit["checkout_commit_sha"],
        "source_count": 18,
        "target_run_id": release.BASE.TARGET_RUN_ID,
        "target_a_F": release.BASE.TARGET_A_F,
        "schedule_entry_count": 35,
        "schedule_sha256": release.BASE.SCHEDULE_SHA256,
        "target_plan_sha256": audit["target_plan_sha256"],
        "terminal_states": result["terminal_states"],
        "worker_launch_count": result["worker_launch_count"],
        "replay_rejections": result["replay_rejections"],
        "parallel_reservation_race": result["parallel_reservation_race"],
        "invalid_rejections": result["invalid_rejections"],
        "physical_backend_imports": 0,
        "physical_solver_calls": 0,
        "cp01r1_attempts": 0,
        "target_solves": 0,
        "operative_grants": 0,
        "physical_result_artifacts": 0,
        "physical_evidence_effect": "NONE",
        "next_block": result["next_block"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else "PASS: Background-3C12 v0.2 controls")


if __name__ == "__main__":
    main()
