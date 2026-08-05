#!/usr/bin/env python3
"""Fail-closed validator for the Background-3C6 integrated control release."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ENTRY_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c6_integrated_release_v0.2.py"
CONTRACT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C6IntegratedExecutionReleaseContract_v0.1.json"
AUDIT_RESULT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C6IntegratedExecutionReleaseAuditResult_v0.1.json"
PHYSICAL_GRANT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
PHYSICAL_ARTIFACT_ROOT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"


def load_entry():
    spec = importlib.util.spec_from_file_location("background3c6_canonical_entry", ENTRY_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to import Background-3C6 canonical entry point")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate() -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    recorded = json.loads(AUDIT_RESULT_PATH.read_text(encoding="utf-8"))
    entry = load_entry()
    audit = entry.audit_release()
    self_test = entry.BASE.self_test()

    assert contract["status"] == "IMPLEMENTED_PENDING_AUDIT_EXECUTION_NOT_AUTHORIZED"
    assert contract["canonical_entry_point"] == str(ENTRY_PATH.relative_to(ROOT))
    assert contract["physical_execution_authorized"] is False
    assert contract["cp01r1_execution_authorized"] is False
    assert contract["physical_evidence_effect"] == "NONE"
    assert contract["control_scope"]["primary_backend_import_allowed"] is False
    assert contract["control_scope"]["independent_backend_import_allowed"] is False
    assert contract["control_scope"]["newton_allowed"] is False
    assert contract["control_scope"]["shooting_jacobian_allowed"] is False
    assert contract["control_scope"]["shooting_root_allowed"] is False
    assert contract["control_scope"]["target_a_F_one_quarter_allowed"] is False

    assert recorded["status"] == "PASS_INTEGRATED_CONTROL_RELEASE_AUDIT_NO_PHYSICAL_EXECUTION"
    assert recorded["physical_evidence_effect"] == "NONE"
    assert recorded["source_count"] == len(contract["package_source_paths"])
    assert recorded["control_results"] == contract["expected_control_classifications"]
    assert recorded["transaction_counts"]["registered_control_subprocess_launches"] == 4
    assert recorded["transaction_counts"]["committed_control_artifacts_in_temporary_storage"] == 2
    assert recorded["transaction_counts"]["clean_abort_controls_without_final_artifact"] == 2
    assert recorded["transaction_counts"]["primary_root_calls"] == 0
    assert recorded["transaction_counts"]["independent_root_calls"] == 0
    assert recorded["transaction_counts"]["shooting_jacobian_calls"] == 0
    assert recorded["transaction_counts"]["cp01r1_attempts"] == 0
    assert recorded["authorization_state"]["physical_execution_authorized"] is False
    assert recorded["authorization_state"]["cp01r1_execution_authorized"] is False
    assert recorded["authorization_state"]["append_only_physical_grant_present"] is False

    assert audit["status"] == "PASS_INTEGRATED_CONTROL_RELEASE_AUDIT_NO_PHYSICAL_EXECUTION"
    assert re.fullmatch(r"[0-9a-f]{64}", audit["package_manifest_sha256"])
    assert audit["package_manifest_sha256"] == recorded["package_manifest_sha256"]
    assert audit["source_count"] == recorded["source_count"]
    assert audit["inspected_modules"] == recorded["static_audit"]["inspected_modules"]
    assert audit["inspected_call_names"] == recorded["static_audit"]["inspected_call_names"]
    assert audit["forbidden_modules"] == recorded["static_audit"]["forbidden_modules"] == []
    assert audit["forbidden_calls"] == recorded["static_audit"]["forbidden_calls"] == []
    assert audit["subprocess_launch_count"] == 0
    assert audit["primary_root_calls"] == 0
    assert audit["independent_root_calls"] == 0
    assert audit["shooting_jacobian_calls"] == 0
    assert audit["cp01r1_attempts"] == 0
    assert audit["physical_grant_present"] is False
    assert audit["physical_result_artifact_present"] is False

    expected = contract["expected_control_classifications"]
    assert self_test["status"] == "PASS_INTEGRATED_CONTROL_RELEASE_SELF_TEST"
    assert self_test["classifications"] == expected == recorded["control_results"]
    assert self_test["committed_control_artifacts"] == 2
    assert self_test["clean_abort_controls"] == 2
    assert self_test["subprocess_launches"] == 4
    assert self_test["primary_root_calls"] == 0
    assert self_test["independent_root_calls"] == 0
    assert self_test["shooting_jacobian_calls"] == 0
    assert self_test["cp01r1_attempts"] == 0
    assert self_test["repository_artifact_created"] is False
    assert self_test["physical_evidence_effect"] == "NONE"

    assert not PHYSICAL_GRANT_PATH.exists()
    assert not PHYSICAL_ARTIFACT_ROOT.exists()
    assert entry.BASE.PRIMARY_ROOT_CALL_COUNT == 0
    assert entry.BASE.INDEPENDENT_ROOT_CALL_COUNT == 0
    assert entry.BASE.SHOOTING_JACOBIAN_CALL_COUNT == 0
    assert entry.BASE.CP01R1_ATTEMPT_COUNT == 0

    return {
        "status": "PASS",
        "audit_status": audit["status"],
        "self_test_status": self_test["status"],
        "recorded_result_status": recorded["status"],
        "package_manifest_sha256": audit["package_manifest_sha256"],
        "control_classifications": self_test["classifications"],
        "subprocess_launches": self_test["subprocess_launches"],
        "physical_solver_calls": 0,
        "cp01r1_attempts": 0,
        "physical_grant_present": False,
        "physical_result_artifact_present": False,
        "physical_evidence_effect": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS: Background-3C6 integrated control release audited without physical execution")


if __name__ == "__main__":
    main()
