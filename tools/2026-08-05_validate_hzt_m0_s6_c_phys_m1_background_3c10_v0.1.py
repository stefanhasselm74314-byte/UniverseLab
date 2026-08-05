#!/usr/bin/env python3
"""Fail-closed validator for Background-3C10 real-backend controls."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import signal
import sys

ROOT = Path(__file__).resolve().parents[1]
RELEASE_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_control_release_v0.1.py"
CONTRACT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlContract_v0.1.json"
REVIEW_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C9PhysicalAdapterAuthorizationReview_v0.1.json"
AUDIT_3C8_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C8PhysicalExecutionAdapterAuditResult_v0.1.json"
RUN_INPUT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"
GRANT_PATHS = (
    ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",
    ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",
)
PHYSICAL_ARTIFACT_ROOT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"object required: {path}")
    return value


def load_release():
    spec = importlib.util.spec_from_file_location("background3c10_release", RELEASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to import Background-3C10 release")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_real_import_termination_probes(release) -> dict:
    payload = load_json(RUN_INPUT_PATH)["frozen_run_payload"]

    timeout_request = release.worker_envelope("timeout_probe", payload)
    timeout_request["sleep_seconds"] = 30.0
    timeout_result = release.launch_worker(timeout_request, timeout_seconds=7.0)
    assert timeout_result["timed_out"] is True
    assert timeout_result["returncode"] in (-signal.SIGTERM, -signal.SIGKILL)
    assert isinstance(timeout_result["stdout"], dict)
    assert timeout_result["stdout"]["status"] == "REAL_PRIMARY_IMPORTED_TIMEOUT_PROBE_READY"
    assert timeout_result["stdout"]["newton_call_count"] == 0

    signal_request = release.worker_envelope("signal_probe", payload)
    signal_result = release.launch_worker(signal_request)
    assert signal_result["timed_out"] is False
    assert signal_result["returncode"] == -signal.SIGTERM
    assert isinstance(signal_result["stdout"], dict)
    assert signal_result["stdout"]["status"] == "REAL_INDEPENDENT_IMPORTED_SIGNAL_PROBE_READY"
    assert signal_result["stdout"]["shooting_jacobian_call_count"] == 0

    return {
        "primary_timeout_import_attested": True,
        "independent_signal_import_attested": True,
        "probe_worker_launches": 2,
    }


def validate() -> dict:
    contract = load_json(CONTRACT_PATH)
    review = load_json(REVIEW_PATH)
    audit_3c8 = load_json(AUDIT_3C8_PATH)
    release = load_release()

    assert contract["status"] == "IMPLEMENTED_PENDING_AUDIT_REAL_BACKEND_ANALYTIC_CONTROLS_ONLY"
    assert contract["control_override"]["a_F"] == 0.0
    assert contract["hard_firewalls"]["cp01r1_execution_authorized"] is False
    assert contract["hard_firewalls"]["target_a_F_one_quarter_solve_authorized"] is False
    assert contract["hard_firewalls"]["primary_newton_target_solve_authorized"] is False
    assert contract["hard_firewalls"]["independent_shooting_root_solve_authorized"] is False
    assert contract["hard_firewalls"]["shooting_jacobian_authorized"] is False
    assert contract["hard_firewalls"]["operative_grant_creation_authorized"] is False
    assert contract["hard_firewalls"]["physical_result_artifact_authorized"] is False
    assert contract["physical_evidence_effect"] == "NONE"

    assert review["status"] == release.DENIAL_3C9
    assert review["authorization_decision"]["authorized"] is False
    assert review["future_control_release_constraints"]["next_block"] == contract["block"]

    audit = release.static_audit()
    assert audit["status"] == "PASS_REAL_BACKEND_CONTROL_STATIC_AUDIT_NO_BACKEND_IMPORT"
    assert audit["source_count"] == 13
    assert re.fullmatch(r"[0-9a-f]{64}", audit["package_manifest_sha256"])
    assert audit["worker_forbidden_calls"] == []
    assert audit["parent_imports_numerical_backend"] is False
    assert audit["worker_launches"] == 0
    assert audit["cp01r1_attempts"] == 0
    assert audit["target_root_solves"] == 0
    assert audit["operative_grants"] == 0
    assert audit["physical_results"] == 0
    assert audit["primary_source_sha256"] == audit_3c8["real_backend_source_binding"]["primary_source_sha256"]
    assert audit["primary_base_source_sha256"] == audit_3c8["real_backend_source_binding"]["primary_base_source_sha256"]
    assert audit["independent_source_sha256"] == audit_3c8["real_backend_source_binding"]["independent_source_sha256"]

    result = release.self_test()
    assert result["status"] == "PASS_REAL_BACKEND_AF0_CONTROL_RELEASE_NO_TARGET_SOLVE"
    assert result["control_run_id"] == release.CONTROL_RUN_ID
    assert result["frozen_physical_run_id"] == release.FROZEN_RUN_ID
    assert result["package_manifest_sha256"] == audit["package_manifest_sha256"]
    assert result["worker_launch_count"] == 5
    assert result["real_backend_control_processes"] == 4
    assert result["primary"]["status"] == "PASS_REAL_PRIMARY_AF0_CONTROL_NO_NEWTON"
    assert result["primary"]["model_a_F"] == 0.0
    assert result["primary"]["newton_call_count"] == 0
    assert [record["node_count"] for record in result["primary"]["node_records"]] == [24, 48, 96]
    assert result["independent"]["status"] == "PASS_REAL_INDEPENDENT_AF0_CONTROL_NO_ROOT"
    assert result["independent"]["model_a_F"] == 0.0
    assert result["independent"]["integration_call_count"] == 6
    assert result["independent"]["shooting_jacobian_call_count"] == 0
    assert result["independent"]["nonlinear_root_calls"] == 0
    assert result["handoff_digest_verified"] is True
    assert result["tampered_handoff_rejected"] is True
    assert result["timeout_probe"] == "PASS_REAL_PRIMARY_IMPORT_THEN_CLEAN_TERMINATION"
    assert result["signal_probe"] == "PASS_REAL_INDEPENDENT_IMPORT_THEN_SIGNAL_TERMINATION"
    assert result["result_schema_translation"]["result_schema_preview_is_physical_result"] is False
    assert result["result_schema_translation"]["result_artifact_created"] is False
    assert set(result["result_schema_translation"]["mapped_fields"]) == set(result["result_schema_translation"]["required_fields"])
    assert result["external_atomic_control_artifact"] == "PASS_TEMPORARY_EXTERNAL_DIRECTORY_ONLY"
    assert result["no_overwrite_firewall"] is True
    assert result["primary_newton_calls"] == 0
    assert result["independent_shooting_jacobian_calls"] == 0
    assert result["nonlinear_root_calls"] == 0
    assert result["cp01r1_attempts"] == 0
    assert result["target_a_F_one_quarter_solves"] == 0
    assert result["operative_grants_created"] == 0
    assert result["physical_result_artifacts_created"] == 0
    assert result["physical_evidence_effect"] == "NONE"

    import_probes = validate_real_import_termination_probes(release)

    denial = release.denied_physical_run()
    assert denial["status"] == "NOT_AUTHORIZED"
    assert denial["physical_backend_imported"] is False
    assert denial["solver_calls"] == 0
    assert denial["cp01r1_attempted"] is False
    assert denial["target_a_F_one_quarter_solve"] is False
    assert denial["operative_grant_created"] is False
    assert denial["result_artifact_created"] is False

    assert all(not path.exists() for path in GRANT_PATHS)
    assert not PHYSICAL_ARTIFACT_ROOT.exists()

    return {
        "status": "PASS",
        "audit_status": audit["status"],
        "control_status": result["status"],
        "package_manifest_sha256": audit["package_manifest_sha256"],
        "primary_source_sha256": audit["primary_source_sha256"],
        "independent_source_sha256": audit["independent_source_sha256"],
        "worker_launch_count": result["worker_launch_count"],
        "real_backend_control_processes": result["real_backend_control_processes"],
        "independent_integration_call_count": result["independent"]["integration_call_count"],
        "primary_timeout_import_attested": import_probes["primary_timeout_import_attested"],
        "independent_signal_import_attested": import_probes["independent_signal_import_attested"],
        "additional_probe_worker_launches": import_probes["probe_worker_launches"],
        "primary_newton_calls": 0,
        "shooting_jacobian_calls": 0,
        "nonlinear_root_calls": 0,
        "cp01r1_attempts": 0,
        "target_a_F_one_quarter_solves": 0,
        "operative_grants": 0,
        "physical_result_artifacts": 0,
        "physical_evidence_effect": "NONE",
        "next_block": contract["next_block_if_pass"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else "PASS: Background-3C10 real-backend controls")


if __name__ == "__main__":
    main()
