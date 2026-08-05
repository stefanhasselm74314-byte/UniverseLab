#!/usr/bin/env python3
"""Fail-closed Background-3C9 authorization-review validator."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C9PhysicalAdapterAuthorizationReview_v0.1.json"
AUDIT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C8PhysicalExecutionAdapterAuditResult_v0.1.json"
CONTRACT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C8PhysicalExecutionAdapterContract_v0.1.json"
ADAPTER_VALIDATOR_PATH = ROOT / "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c8_v0.1.py"
GRANTS = [
    ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",
    ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",
]
PHYSICAL_ARTIFACT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
DENIAL = "DENIED_REAL_BACKEND_ADAPTER_TRANSACTION_AND_OPERATIVE_SINGLE_USE_GRANT_RELEASE_ABSENT"
NEXT = "C-PHYS-R1.0-BACKGROUND-3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE_IMPLEMENTATION_ONLY"
PACKAGE_DIGEST = "497d6da51d0d7f436ae7cf24d8c4acad93d5e2423ab9eb717ec016c776e27613"
SCHEDULE_DIGEST = "95001986dc93818f0fea3124cf9ddcd63eb136f8d206f6200a4e8c0cf6d54927"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_adapter_validator():
    spec = importlib.util.spec_from_file_location("bg3c8_basis", ADAPTER_VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Background-3C8 validator import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate() -> dict:
    review = load(REVIEW_PATH)
    audit = load(AUDIT_PATH)
    contract = load(CONTRACT_PATH)

    assert review["status"] == DENIAL
    assert review["classification"] == "APPEND_ONLY_FAIL_CLOSED_REAL_BACKEND_EXECUTION_ELIGIBILITY_REVIEW"
    decision = review["authorization_decision"]
    assert decision == {
        "authorized": False,
        "grant_created": False,
        "physical_backend_imported": False,
        "primary_newton_called": False,
        "independent_shooting_called": False,
        "shooting_jacobian_called": False,
        "cp01r1_attempted": False,
        "result_artifact_created": False,
    }
    assert review["physical_evidence_effect"] == "NONE"
    assert review["next_allowed_block"] == NEXT
    constraints = review["future_control_release_constraints"]
    assert constraints["next_block"] == NEXT
    assert constraints["implementation_only"] is True
    assert constraints["cp01r1_execution_forbidden"] is True
    assert constraints["target_a_F_one_quarter_solve_forbidden"] is True
    assert constraints["primary_newton_target_solve_forbidden"] is True
    assert constraints["independent_shooting_root_solve_forbidden"] is True
    assert constraints["operative_grant_creation_forbidden"] is True
    assert constraints["physical_result_artifact_forbidden"] is True

    blockers = review["blocking_findings"]
    required_absent = {
        "real_primary_backend_import_through_adapter": "NOT_PERFORMED",
        "real_independent_backend_import_through_adapter": "NOT_PERFORMED",
        "real_primary_analytic_control_transaction": "NOT_PERFORMED",
        "real_independent_analytic_control_transaction": "NOT_PERFORMED",
        "resource_limits_across_real_backend_process_boundary": "NOT_TESTED",
        "timeout_and_signal_cleanup_across_real_backend_process_boundary": "NOT_TESTED",
        "operative_single_use_grant_schema": "NOT_PRESENT",
        "authorizable_real_backend_execution_release": "NOT_PRESENT",
    }
    for key, value in required_absent.items():
        assert blockers[key] == value, (key, blockers.get(key), value)

    assert audit["status"] == "PASS_PHYSICAL_ADAPTER_AUDIT_MANUFACTURED_CONTROLS_ONLY"
    assert audit["package_manifest_sha256"] == PACKAGE_DIGEST
    assert audit["immutable_run_binding"]["schedule_sha256"] == SCHEDULE_DIGEST
    assert audit["real_backend_source_binding"]["physical_backend_imported"] is False
    assert audit["authorization_state"]["physical_execution_authorized"] is False
    assert audit["authorization_state"]["cp01r1_execution_authorized"] is False
    assert audit["authorization_state"]["operative_grant_present"] is False
    counts = audit["transaction_counts"]
    assert counts["primary_physical_root_calls"] == 0
    assert counts["independent_physical_root_calls"] == 0
    assert counts["shooting_jacobian_calls"] == 0
    assert counts["cp01r1_attempts"] == 0
    assert counts["operative_grants_created"] == 0
    assert counts["repository_physical_result_artifacts"] == 0

    assert contract["physical_execution_authorized"] is False
    assert contract["cp01r1_execution_authorized"] is False
    assert contract["operative_grant_creation_allowed"] is False
    assert contract["physical_backend_bindings"]["primary"]["import_during_3c8_controls"] is False
    assert contract["physical_backend_bindings"]["independent"]["import_during_3c8_controls"] is False

    basis = load_adapter_validator().validate()
    assert basis["status"] == "PASS"
    assert basis["package_manifest_sha256"] == PACKAGE_DIGEST
    assert basis["schedule_sha256"] == SCHEDULE_DIGEST
    assert basis["physical_backend_imported"] is False
    assert basis["physical_solver_calls"] == 0
    assert basis["cp01r1_attempts"] == 0
    assert basis["operative_grant_present"] is False
    assert basis["physical_result_artifact_present"] is False

    assert all(not path.exists() for path in GRANTS)
    assert not PHYSICAL_ARTIFACT.exists()

    return {
        "status": "PASS",
        "review_status": DENIAL,
        "package_manifest_sha256": PACKAGE_DIGEST,
        "schedule_sha256": SCHEDULE_DIGEST,
        "physical_backend_imported": False,
        "physical_solver_calls": 0,
        "cp01r1_attempts": 0,
        "grant_created": False,
        "result_artifact_created": False,
        "physical_evidence_effect": "NONE",
        "next_block": NEXT,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else "PASS: Background-3C9 review")


if __name__ == "__main__":
    main()
