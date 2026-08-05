#!/usr/bin/env python3
"""Fail-closed validator for Background-3C8 physical adapter controls."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c8_physical_execution_adapter_v0.1.py"
CONTRACT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C8PhysicalExecutionAdapterContract_v0.1.json"
REVIEW_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C7IntegratedReleaseAuthorizationReview_v0.1.json"
OPERATIVE_GRANT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
PHYSICAL_ARTIFACT_ROOT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_adapter():
    spec = importlib.util.spec_from_file_location("background3c8_adapter", ADAPTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to import Background-3C8 adapter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate() -> dict:
    contract = load_json(CONTRACT_PATH)
    review = load_json(REVIEW_PATH)
    adapter = load_adapter()
    audit = adapter.audit_release()
    self_test = adapter.self_test()

    assert contract["status"] == "IMPLEMENTED_PENDING_AUDIT_PHYSICAL_EXECUTION_NOT_AUTHORIZED"
    assert contract["physical_execution_authorized"] is False
    assert contract["cp01r1_execution_authorized"] is False
    assert contract["operative_grant_creation_allowed"] is False
    assert contract["physical_evidence_effect"] == "NONE"
    assert contract["canonical_entry_point"] == str(ADAPTER_PATH.relative_to(ROOT))
    assert contract["immutable_run_binding"]["expected_schedule_entries"] == 35
    assert contract["immutable_run_binding"]["seed_count"] == 7
    assert contract["immutable_run_binding"]["node_counts_ordered"] == [24, 32, 48, 64, 96]
    assert contract["manufactured_capability"]["physical_authorized"] is False
    assert contract["manufactured_capability"]["replay_rejected"] is True
    assert contract["artifact_policy"]["repository_artifact_creation_allowed"] is False
    assert contract["artifact_policy"]["physical_result_path_creation_allowed"] is False

    assert review["status"] == "DENIED_PHYSICAL_BACKEND_ADAPTER_AND_SINGLE_USE_GRANT_RELEASE_ABSENT"
    assert review["authorization_decision"]["authorized"] is False

    assert audit["status"] == "PASS_PHYSICAL_ADAPTER_STATIC_AUDIT_NO_PHYSICAL_EXECUTION"
    assert re.fullmatch(r"[0-9a-f]{64}", audit["package_manifest_sha256"])
    assert audit["source_count"] == len(contract["package_source_paths"])
    assert audit["run_binding"]["schedule_entry_count"] == 35
    assert re.fullmatch(r"[0-9a-f]{64}", audit["run_binding"]["schedule_sha256"])
    assert audit["forbidden_modules"] == []
    assert audit["forbidden_calls"] == []
    assert audit["stub_subprocess_launches"] == 0
    assert audit["primary_physical_root_calls"] == 0
    assert audit["independent_physical_root_calls"] == 0
    assert audit["shooting_jacobian_calls"] == 0
    assert audit["cp01r1_attempts"] == 0
    assert audit["operative_grant_present"] is False
    assert audit["physical_result_artifact_present"] is False
    assert audit["backend_binding"]["physical_backend_imported"] is False

    assert self_test["status"] == "PASS_PHYSICAL_ADAPTER_MANUFACTURED_END_TO_END_CONTROLS"
    assert self_test["classifications"] == contract["expected_control_classifications"]
    assert self_test["manufactured_subprocess_launches"] == 6
    assert self_test["committed_external_control_artifacts"] == 2
    assert self_test["clean_abort_controls"] == 2
    assert self_test["capability_replay_rejected"] is True
    assert self_test["primary_physical_root_calls"] == 0
    assert self_test["independent_physical_root_calls"] == 0
    assert self_test["shooting_jacobian_calls"] == 0
    assert self_test["cp01r1_attempts"] == 0
    assert self_test["operative_grant_present"] is False
    assert self_test["repository_physical_result_present"] is False
    assert self_test["physical_evidence_effect"] == "NONE"

    denial = adapter.denied_physical_run(adapter.RUN_ID)
    assert denial["status"] == "NOT_AUTHORIZED"
    assert denial["physical_backend_imported"] is False
    assert denial["solver_calls"] == 0
    assert denial["cp01r1_attempted"] is False
    assert denial["operative_grant_created"] is False
    assert denial["result_artifact_created"] is False

    assert adapter.PRIMARY_PHYSICAL_ROOT_CALL_COUNT == 0
    assert adapter.INDEPENDENT_PHYSICAL_ROOT_CALL_COUNT == 0
    assert adapter.SHOOTING_JACOBIAN_CALL_COUNT == 0
    assert adapter.CP01R1_ATTEMPT_COUNT == 0
    assert not OPERATIVE_GRANT_PATH.exists()
    assert not PHYSICAL_ARTIFACT_ROOT.exists()

    return {
        "status": "PASS",
        "audit_status": audit["status"],
        "self_test_status": self_test["status"],
        "package_manifest_sha256": audit["package_manifest_sha256"],
        "schedule_sha256": audit["run_binding"]["schedule_sha256"],
        "control_classifications": self_test["classifications"],
        "manufactured_subprocess_launches": self_test["manufactured_subprocess_launches"],
        "physical_backend_imported": False,
        "physical_solver_calls": 0,
        "cp01r1_attempts": 0,
        "operative_grant_present": False,
        "physical_result_artifact_present": False,
        "physical_evidence_effect": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else "PASS: Background-3C8 adapter controls")


if __name__ == "__main__":
    main()
