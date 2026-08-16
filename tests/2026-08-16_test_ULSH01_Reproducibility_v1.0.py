#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-08-16_ULSH01_ReproducibilityContract_v1.0.json"
INPUT = ROOT / "reproducibility/ulsh-01/2026-08-16_ULSH01_ControlReferenceInput_v1.0.json"
OUTPUT = ROOT / "reproducibility/ulsh-01/2026-08-16_ULSH01_ControlReferenceOutput_v1.0.json"
TOLERANCE = ROOT / "reproducibility/ulsh-01/2026-08-16_ULSH01_ToleranceContract_v1.0.json"
PROVENANCE = ROOT / "reproducibility/ulsh-01/2026-08-16_ULSH01_RunProvenance_v1.0.json"
CHECKSUMS = ROOT / "reproducibility/ulsh-01/2026-08-16_ULSH01_SHA256SUMS_v1.0.txt"
SOURCE_CONTRACT = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlContract_v0.3.json"
SOURCE_AUDIT = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlAuditResult_v0.3.json"
SOURCE_RUN_INPUT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"
SITE_STATE = ROOT / "registry/2026-08-16_UniverseLab_SiteState_v1.0.json"

PAYLOADS = (INPUT, OUTPUT, PROVENANCE, TOLERANCE)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"object required: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_checksums(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split("  ", 1)
        assert len(digest) == 64
        result[name] = digest
    return result


def validate() -> dict[str, Any]:
    contract = load(CONTRACT)
    ref_input = load(INPUT)
    ref_output = load(OUTPUT)
    tolerance = load(TOLERANCE)
    provenance = load(PROVENANCE)
    source_contract = load(SOURCE_CONTRACT)
    source_audit = load(SOURCE_AUDIT)
    source_run_input = load(SOURCE_RUN_INPUT)
    site_state = load(SITE_STATE)

    assert contract["schema"] == "universelab.solver-reference-package.v1"
    assert contract["module_id"] == "ULSH-01"
    assert contract["solver_id"] == "MD2S-BVP"
    assert contract["physical_gate_effect"] == "NONE"
    assert contract["physical_evidence_effect"] == "NONE"
    assert contract["reference_scope"]["control_reference"] == "AVAILABLE_AUDITED_AF0_R3"
    assert contract["reference_scope"]["control_replay"] == "NOT_RUN_BY_THIS_PACKAGE"
    assert contract["reference_scope"]["physical_target_reference"] == "NOT_AVAILABLE_NOT_AUTHORIZED"

    checksums = parse_checksums(CHECKSUMS)
    expected = contract["sha256"]
    assert set(checksums) == {path.name for path in PAYLOADS}
    assert set(expected) == set(checksums)
    for path in PAYLOADS:
        digest = sha256(path)
        assert digest == checksums[path.name], (path.name, digest, checksums[path.name])
        assert digest == expected[path.name], (path.name, digest, expected[path.name])
    assert sha256(CHECKSUMS) == contract["checksums_file_sha256"]

    assert ref_input["control_run_id"] == source_contract["control_run_id"]
    assert ref_input["control_override"] == source_contract["control_override"]
    assert ref_input["primary_control"]["node_counts"] == source_contract["primary_control"]["node_counts"]
    assert ref_input["independent_control"]["pole_cutoffs"] == source_contract["independent_control"]["pole_cutoffs"]
    assert ref_input["independent_control"]["sample_count"] == source_contract["independent_control"]["sample_count"]
    for key in ("python_hash_seed", "thread_count", "network_allowed", "randomness_allowed"):
        assert ref_input["process_controls"][key] == source_contract["process_controls"][key]
    target = source_run_input["frozen_run_payload"]
    assert ref_input["physical_target_context"]["run_id"] == target["run_id"]
    assert ref_input["physical_target_context"]["frozen_run_payload_sha256"] == source_run_input["frozen_run_payload_sha256"]
    assert ref_input["physical_target_context"]["a_F"] == target["model_parameters_ordered"]["a_F"]
    assert ref_input["physical_target_context"]["solver_authorized"] is False
    assert source_run_input["solver_authorized"] is False

    assert ref_output["status"] == source_audit["status"]
    assert ref_output["control_run_id"] == source_audit["control_run_id"]
    assert ref_output["primary_control"] == source_audit["primary_control"]
    assert ref_output["independent_control"] == source_audit["independent_control"]
    assert ref_output["execution_firewall"] == source_audit["execution_firewall"]
    assert ref_output["physical_evidence_effect"] == "NONE"

    primary_acceptance = source_contract["primary_control"]["acceptance"]
    assert tolerance["primary_acceptance"]["bulk_residual_inf_max_by_node_count"] == primary_acceptance["bulk_residual_inf_max_by_node_count"]
    for key in (
        "constraint_inf_max",
        "boundary_exact_distance_max",
        "candidate_parameter_cross_mesh_distance_max",
        "bulk_monotonic_convergence_required",
        "continuum_convergence_inference_allowed",
    ):
        assert tolerance["primary_acceptance"][key] == primary_acceptance[key]
    independent_acceptance = source_contract["independent_control"]["acceptance"]
    for key in (
        "profile_error_inf_max",
        "constraint_inf_max",
        "boundary_exact_distance_max",
        "primary_independent_boundary_distance_max",
        "integration_call_count",
        "shooting_jacobian_call_count",
    ):
        assert tolerance["independent_acceptance"][key] == independent_acceptance[key]
    assert tolerance["independent_acceptance"]["nonlinear_root_call_count"] == source_audit["independent_control"]["nonlinear_root_call_count"]

    assert provenance["scientific_artifact_commit"] == source_audit["audited_branch_head"]
    hist = provenance["historical_run"]
    assert hist["control_run_id"] == source_audit["control_run_id"]
    assert hist["workflow_run_id"] == source_audit["workflow_run_id"]
    assert hist["workflow_job_id"] == source_audit["workflow_job_id"]
    assert hist["workflow_artifact_id"] == source_audit["workflow_artifact"]["artifact_id"]
    assert hist["workflow_artifact_zip_sha256"] == source_audit["workflow_artifact"]["zip_sha256"]
    assert hist["package_manifest_sha256"] == source_audit["closed_package"]["package_manifest_sha256"]
    assert hist["dependency_lock_sha256"] == source_audit["closed_package"]["dependency_lock_sha256"]
    assert provenance["physical_target"]["authorized"] is False
    assert provenance["physical_target"]["executed"] is False
    assert provenance["physical_target"]["reference_output_exists"] is False

    modules = {item["module_id"]: item for item in site_state["modules"]}
    u = modules["ULSH-01"]
    assert u["governance"]["solver_release"] == "NOT_AUTHORIZED"
    assert u["scientific"]["physical_background"] == "NOT_ESTABLISHED"
    assert u["governance"]["K1-D"] == "NOT_RELEASED"
    assert u["governance"]["K1-E"] == "NOT_ADMISSIBLE"
    assert u["governance"]["physical_evidence_effect"] == "NONE"
    assert u["release_gate"]["status"] == "NOT_SATISFIED"

    return {
        "schema": "universelab.ulsh01.reproducibility-test-status.v1",
        "version": "1.0.0",
        "module_id": "ULSH-01",
        "package_id": contract["package_id"],
        "status": "PASS_PACKAGE_INTEGRITY_AND_STATIC_AUDIT_BINDING",
        "package_integrity": "BITWISE_MATCH",
        "static_audit_binding": "MATCH",
        "control_replay": "NOT_TESTED",
        "physical_target": "NOT_APPLICABLE_NOT_AUTHORIZED",
        "reference_package_commit": os.environ.get("UL_REFERENCE_COMMIT", os.environ.get("GITHUB_SHA", "LOCAL_WORKTREE")),
        "test_run_id": os.environ.get("GITHUB_RUN_ID", "LOCAL"),
        "solver_release": "NOT_AUTHORIZED",
        "physical_background": "NOT_ESTABLISHED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
        "physical_gate_effect": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
