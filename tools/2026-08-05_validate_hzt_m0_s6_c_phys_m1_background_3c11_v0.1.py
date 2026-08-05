#!/usr/bin/env python3
"""Fail-closed validator for Background-3C11 authorization review."""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C11RealBackendControlAuthorizationReview_v0.1.json"
CONTRACT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlContract_v0.3.json"
AUDIT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlAuditResult_v0.3.json"
FAILURE_R1_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlFailureResult_v0.1.json"
FAILURE_R2_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlFailureResult_v0.2.json"
RUN_INPUT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"
MANIFEST_PATH = ROOT / "project-manifest.json"
CHECKPOINT_PATH = ROOT / "registry/session-checkpoint-latest.json"
RELEASE_R3_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_control_release_v0.3.py"
OPERATIVE_GRANTS = (
    ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",
    ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",
)
TARGET_RELEASE_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c12_target_path_release_v0.1.py"
GRANT_SCHEMA_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C12SingleUseGrantContract_v0.1.json"
PHYSICAL_ARTIFACT_ROOT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
DENIAL = "DENIED_OPERATIVE_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE_ABSENT"
NEXT = "C-PHYS-R1.0-BACKGROUND-3C12_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE_IMPLEMENTATION_ONLY"
PACKAGE_DIGEST = "a7b48c88061e00cc3dc44dd00a2a17855a7f8c65dd228f725101fde9a1839eb4"


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"object required: {path}")
    return value


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modules.add(node.module or "")
    return modules


def called_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                names.add(node.func.attr)
    return names


def validate() -> dict:
    review = load(REVIEW_PATH)
    contract = load(CONTRACT_PATH)
    audit = load(AUDIT_PATH)
    failure_r1 = load(FAILURE_R1_PATH)
    failure_r2 = load(FAILURE_R2_PATH)
    run_input = load(RUN_INPUT_PATH)
    manifest = load(MANIFEST_PATH)
    checkpoint = load(CHECKPOINT_PATH)

    assert review["status"] == DENIAL
    assert review["classification"] == "APPEND_ONLY_FAIL_CLOSED_TARGET_PATH_EXECUTION_ELIGIBILITY_REVIEW"
    assert review["physical_evidence_effect"] == "NONE"
    decision = review["authorization_decision"]
    assert decision == {
        "authorized": False,
        "grant_created": False,
        "physical_backend_imported": False,
        "primary_newton_called": False,
        "independent_shooting_called": False,
        "shooting_jacobian_called": False,
        "nonlinear_root_called": False,
        "cp01r1_attempted": False,
        "target_a_F_one_quarter_solve_attempted": False,
        "result_artifact_created": False,
    }

    passed = review["passed_prerequisites"]
    assert passed["closed_real_backend_control_package_bound"] is True
    assert passed["package_manifest_sha256"] == PACKAGE_DIGEST
    assert passed["source_count"] == 24
    assert passed["exact_a_F_zero_primary_control_passed"] is True
    assert passed["exact_a_F_zero_independent_control_passed"] is True
    assert passed["all_target_solver_grant_and_physical_result_counters_zero"] is True

    blocking = review["blocking_findings"]
    assert blocking["audited_release_scope"] == "ANALYTIC_A_F_ZERO_CONTROL_ONLY"
    assert blocking["frozen_target_scope"] == "A_F_ONE_QUARTER_CP01R1"
    required_absences = (
        "target_path_entry_point",
        "target_path_source_manifest",
        "operative_single_use_grant_schema",
        "grant_bound_to_main_commit",
        "grant_bound_to_frozen_payload_package_backends_and_dependency_lock",
        "grant_expiration_and_not_before_window",
        "grant_nonce_and_authorization_decision_identity",
        "grant_atomic_consumption_record",
        "authorizable_target_path_release",
    )
    for key in required_absences:
        assert blocking[key] == "NOT_PRESENT"
    assert blocking["grant_replay_prevention_after_success_failure_timeout_and_signal"] == "NOT_IMPLEMENTED"
    assert blocking["grant_crash_recovery_semantics"] == "NOT_IMPLEMENTED"
    assert blocking["grant_cannot_be_used_for_control_override"] == "NOT_PROVEN"

    future = review["future_implementation_constraints"]
    assert future["next_block"] == NEXT
    assert future["implementation_only"] is True
    for key in (
        "physical_backend_import_forbidden",
        "cp01r1_execution_forbidden",
        "target_a_F_one_quarter_solve_forbidden",
        "primary_newton_target_solve_forbidden",
        "independent_shooting_root_solve_forbidden",
        "operative_grant_creation_forbidden",
        "physical_result_artifact_forbidden",
        "automatic_authorization_forbidden",
    ):
        assert future[key] is True

    assert contract["status"] == "IMPLEMENTED_PENDING_AUDIT_REAL_BACKEND_ANALYTIC_CONTROLS_ONLY"
    assert contract["control_override"]["a_F"] == 0.0
    assert contract["control_override"]["target_a_F"] == "1/4_FORBIDDEN"
    assert contract["next_block_if_pass"] == review["block"]
    assert audit["status"] == "PASS_REAL_BACKEND_AF0_CONTROL_RELEASE_NO_TARGET_SOLVE"
    assert audit["closed_package"]["package_manifest_sha256"] == PACKAGE_DIGEST
    assert audit["closed_package"]["source_count"] == 24
    assert audit["primary_control"]["model_a_F"] == 0.0
    assert audit["primary_control"]["newton_call_count"] == 0
    assert audit["independent_control"]["integration_call_count"] == 6
    assert audit["independent_control"]["shooting_jacobian_call_count"] == 0
    assert audit["independent_control"]["nonlinear_root_call_count"] == 0
    for key, value in audit["execution_firewall"].items():
        if key != "physical_run_cli_exit_73":
            assert value == 0
    assert audit["physical_evidence_effect"] == "NONE"
    assert failure_r1["status"] == "FAIL_CLOSED_PRIMARY_UNIFORM_BULK_THRESHOLD_AT_N96"
    assert failure_r2["status"] == "FAIL_CLOSED_CANDIDATE_JSON_KEY_ORDER_MISTAKEN_FOR_VECTOR_ORDER"

    assert run_input["frozen_run_payload"]["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
    assert run_input["frozen_run_payload"]["model_parameters_ordered"]["a_F"] == "1/4"
    assert run_input["current_state"]["execution_authorized"] is False
    assert run_input["current_state"]["solver_executed"] is False

    assert manifest["release"] == "2.21-c-phys-m1-background-3c10-real-backend-control-audited-v0.1"
    assert manifest["gates"]["BACKGROUND_3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE"] == "PASS_AUDITED_AF0_CONTROL_ONLY"
    assert manifest["gates"]["BACKGROUND_3C11_AUTHORIZATION_REVIEW"] == "NOT_STARTED"
    assert manifest["gates"]["BACKGROUND_3C_EXECUTION"] == "NOT_AUTHORIZED"
    assert manifest["gates"]["BACKGROUND_SOLVER_EXECUTION"] == "NOT_AUTHORIZED"
    assert manifest["gates"]["PHYSICAL_BACKGROUND"] == "NOT_ESTABLISHED"
    assert manifest["next_block"] == review["block"]
    assert checkpoint["checkpoint_id"] == "UL-CHK-20260805-029"
    assert checkpoint["current_workstreams"][0]["next_block"] == review["block"]

    review_modules = imported_modules(Path(__file__).resolve())
    assert "numpy" not in review_modules
    assert "scipy" not in review_modules
    review_calls = called_names(Path(__file__).resolve())
    for forbidden in ("damped_newton", "shooting_residual", "centered_fd_jacobian", "least_squares", "root", "solve_ivp"):
        assert forbidden not in review_calls

    release_text = RELEASE_R3_PATH.read_text(encoding="utf-8")
    assert "def denied_physical_run" in release_text
    assert "EXIT_NOT_AUTHORIZED" in release_text
    assert all(not path.exists() for path in OPERATIVE_GRANTS)
    assert not TARGET_RELEASE_PATH.exists()
    assert not GRANT_SCHEMA_PATH.exists()
    assert not PHYSICAL_ARTIFACT_ROOT.exists()

    return {
        "status": "PASS",
        "review_status": DENIAL,
        "package_manifest_sha256": PACKAGE_DIGEST,
        "review_imports_numerical_backend": False,
        "physical_backend_imported": False,
        "physical_solver_calls": 0,
        "cp01r1_attempts": 0,
        "target_a_F_one_quarter_solves": 0,
        "operative_grants": 0,
        "physical_result_artifacts": 0,
        "physical_evidence_effect": "NONE",
        "next_block": NEXT,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else "PASS: Background-3C11 authorization denial")


if __name__ == "__main__":
    main()
