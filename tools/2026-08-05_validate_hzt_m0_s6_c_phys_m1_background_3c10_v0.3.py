#!/usr/bin/env python3
"""Fail-closed validator for Background-3C10 R3 controls."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import signal
import sys

ROOT = Path(__file__).resolve().parents[1]
RELEASE_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_control_release_v0.3.py"
CONTRACT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlContract_v0.3.json"
FAILURE_R1_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlFailureResult_v0.1.json"
FAILURE_R2_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlFailureResult_v0.2.json"
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
    spec = importlib.util.spec_from_file_location("background3c10_release_v03", RELEASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to import Background-3C10 release v0.3")
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
    failure_r1 = load_json(FAILURE_R1_PATH)
    failure_r2 = load_json(FAILURE_R2_PATH)
    review = load_json(REVIEW_PATH)
    audit_3c8 = load_json(AUDIT_3C8_PATH)
    release = load_release()

    assert failure_r1["status"] == release.R1_FAILURE_STATUS
    assert failure_r2["status"] == release.R2_FAILURE_STATUS
    assert failure_r2["disposition"]["next_control_run_id"] == release.CONTROL_RUN_ID
    assert contract["control_run_id"] == release.CONTROL_RUN_ID
    assert contract["previous_control_runs"][0]["run_id"] == failure_r1["control_run_id"]
    assert contract["previous_control_runs"][1]["run_id"] == failure_r2["control_run_id"]
    assert all(item["may_be_reclassified_as_pass"] is False for item in contract["previous_control_runs"])
    assert all(item["may_be_reused"] is False for item in contract["previous_control_runs"])
    assert contract["correction_reason"]["acceptance_threshold_changed_from_r2"] is False
    assert contract["correction_reason"]["model_parameters_changed"] is False
    assert contract["correction_reason"]["topological_sector_changed"] is False
    assert contract["correction_reason"]["mesh_schedule_changed"] is False
    assert contract["correction_reason"]["independent_cutoff_schedule_changed"] is False
    assert contract["handoff_contract"]["json_object_key_order_semantic"] is False
    assert contract["handoff_contract"]["decoded_field_set_must_match_exactly"] is True
    assert contract["handoff_contract"]["vector_reconstruction_order"] == "candidate_fields"
    assert contract["handoff_contract"]["canonical_json_sort_keys"] is True
    assert contract["primary_control"]["acceptance"]["bulk_residual_inf_max_by_node_count"] == {
        "24": 1e-9, "48": 1e-9, "96": 3e-8
    }
    assert contract["primary_control"]["acceptance"]["continuum_convergence_inference_allowed"] is False
    assert contract["control_override"]["a_F"] == 0.0
    for key in (
        "cp01r1_execution_authorized",
        "target_a_F_one_quarter_solve_authorized",
        "primary_newton_target_solve_authorized",
        "independent_shooting_root_solve_authorized",
        "shooting_jacobian_authorized",
        "operative_grant_creation_authorized",
        "physical_result_artifact_authorized",
        "parameter_scan_authorized",
        "topology_scan_authorized",
    ):
        assert contract["hard_firewalls"][key] is False
    assert contract["physical_evidence_effect"] == "NONE"

    assert review["status"] == release.BASE.DENIAL_3C9
    assert review["authorization_decision"]["authorized"] is False
    assert review["future_control_release_constraints"]["next_block"] == contract["block"]

    audit = release.static_audit()
    assert audit["status"] == "PASS_REAL_BACKEND_CONTROL_STATIC_AUDIT_NO_BACKEND_IMPORT"
    assert audit["source_count"] == 24
    assert re.fullmatch(r"[0-9a-f]{64}", audit["package_manifest_sha256"])
    assert audit["worker_forbidden_calls"] == []
    assert audit["parent_imports_numerical_backend"] is False
    assert audit["worker_launches"] == 0
    assert audit["cp01r1_attempts"] == 0
    assert audit["target_root_solves"] == 0
    assert audit["operative_grants"] == 0
    assert audit["physical_results"] == 0
    assert audit["r1_failure_status"] == failure_r1["status"]
    assert audit["r2_failure_status"] == failure_r2["status"]
    assert audit["r3_control_run_id"] == release.CONTROL_RUN_ID
    assert audit["json_mapping_key_order_semantic"] is False
    assert audit["handoff_vector_order_source"] == "EXPLICIT_CANDIDATE_FIELDS_CONTRACT"
    assert audit["continuum_convergence_inference_allowed"] is False
    assert audit["primary_source_sha256"] == audit_3c8["real_backend_source_binding"]["primary_source_sha256"]
    assert audit["primary_base_source_sha256"] == audit_3c8["real_backend_source_binding"]["primary_base_source_sha256"]
    assert audit["independent_source_sha256"] == audit_3c8["real_backend_source_binding"]["independent_source_sha256"]

    result = release.self_test()
    assert result["status"] == "PASS_REAL_BACKEND_AF0_CONTROL_RELEASE_NO_TARGET_SOLVE"
    assert result["control_run_id"] == release.CONTROL_RUN_ID
    assert result["frozen_physical_run_id"] == release.BASE.FROZEN_RUN_ID
    assert result["package_manifest_sha256"] == audit["package_manifest_sha256"]
    assert result["worker_launch_count"] == 5
    assert result["real_backend_control_processes"] == 4
    assert result["r1_failure_preserved"] is True
    assert result["r2_failure_preserved"] is True
    assert result["json_mapping_key_order_semantic"] is False
    assert result["handoff_vector_order_source"] == "EXPLICIT_CANDIDATE_FIELDS_CONTRACT"
    assert result["bulk_monotonic_convergence_required"] is False
    assert result["continuum_convergence_inference_allowed"] is False
    assert result["primary_bulk_roundoff_classification"]["96"] == "HIGH_ORDER_DIFFERENTIATION_ROUNDOFF_ENVELOPE_CONTROL_ONLY"

    primary = result["primary"]
    assert primary["status"] == "PASS_REAL_PRIMARY_AF0_CONTROL_NO_NEWTON"
    assert primary["model_a_F"] == 0.0
    assert primary["newton_call_count"] == 0
    assert [record["node_count"] for record in primary["node_records"]] == [24, 48, 96]
    limits = contract["primary_control"]["acceptance"]["bulk_residual_inf_max_by_node_count"]
    for record in primary["node_records"]:
        assert record["bulk_residual_inf"] <= limits[str(record["node_count"])]
        assert record["constraint_inf"] <= contract["primary_control"]["acceptance"]["constraint_inf_max"]
        assert record["boundary_exact_distance"] <= contract["primary_control"]["acceptance"]["boundary_exact_distance_max"]
    assert primary["candidate_cross_mesh_distance"] == 0.0
    assert primary["candidate_sha256"] == "6a00f71f4904574841d17eaebba7f8318fc136d477ab6fd324f3354f1b33e400"

    independent = result["independent"]
    assert independent["status"] == "PASS_REAL_INDEPENDENT_AF0_CONTROL_NO_ROOT"
    assert independent["model_a_F"] == 0.0
    assert independent["integration_call_count"] == 6
    assert independent["shooting_jacobian_call_count"] == 0
    assert independent["nonlinear_root_calls"] == 0
    assert independent["json_mapping_key_order_semantic"] is False
    assert independent["handoff_vector_order_source"] == "EXPLICIT_CANDIDATE_FIELDS_CONTRACT"
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
    assert denial["control_run_id"] == release.CONTROL_RUN_ID
    assert denial["r1_failure_preserved"] is True
    assert denial["r2_failure_preserved"] is True
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
        "r1_status": failure_r1["status"],
        "r2_status": failure_r2["status"],
        "r3_control_run_id": release.CONTROL_RUN_ID,
        "package_manifest_sha256": audit["package_manifest_sha256"],
        "primary_source_sha256": audit["primary_source_sha256"],
        "independent_source_sha256": audit["independent_source_sha256"],
        "candidate_sha256": primary["candidate_sha256"],
        "primary_bulk_residuals_by_node_count": result["primary_bulk_residuals_by_node_count"],
        "independent_cutoff_table": result["cutoff_table"],
        "worker_launch_count": result["worker_launch_count"],
        "real_backend_control_processes": result["real_backend_control_processes"],
        "independent_integration_call_count": independent["integration_call_count"],
        "primary_timeout_import_attested": import_probes["primary_timeout_import_attested"],
        "independent_signal_import_attested": import_probes["independent_signal_import_attested"],
        "additional_probe_worker_launches": import_probes["probe_worker_launches"],
        "json_mapping_key_order_semantic": False,
        "handoff_vector_order_source": "EXPLICIT_CANDIDATE_FIELDS_CONTRACT",
        "primary_newton_calls": 0,
        "shooting_jacobian_calls": 0,
        "nonlinear_root_calls": 0,
        "cp01r1_attempts": 0,
        "target_a_F_one_quarter_solves": 0,
        "operative_grants": 0,
        "physical_result_artifacts": 0,
        "continuum_convergence_inference_allowed": False,
        "physical_evidence_effect": "NONE",
        "next_block": contract["next_block_if_pass"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else "PASS: Background-3C10 R3 real-backend controls")


if __name__ == "__main__":
    main()
