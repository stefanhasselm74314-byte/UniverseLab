#!/usr/bin/env python3
"""Canonical G0 v1.21 validator after Background-3C10 R3 audit."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RELEASE = "2.21-c-phys-m1-background-3c10-real-backend-control-audited-v0.1"
DECISION = "UL-DEC-0036"
CHECKPOINT = "UL-CHK-20260805-029"
BASIS_COMMIT = "e8c6e78d7dddd60d92a83bc8fbe82c3ef79e5e98"
NEXT = "C-PHYS-R1.0-BACKGROUND-3C11_REAL_BACKEND_CONTROL_RELEASE_AUTHORIZATION_REVIEW_ONLY"
OLD_NEXT = "C-PHYS-R1.0-BACKGROUND-3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE_IMPLEMENTATION_ONLY"
OLD_ACTIVE = "ACTIVE_REAL_BACKEND_ADAPTER_CONTROL_RELEASE_IMPLEMENTATION_REMAINING"
ACTIVE = "ACTIVE_REAL_BACKEND_CONTROL_RELEASE_AUTHORIZATION_REVIEW_REMAINING"
R1_STATUS = "FAIL_CLOSED_PRIMARY_UNIFORM_BULK_THRESHOLD_AT_N96"
R2_STATUS = "FAIL_CLOSED_CANDIDATE_JSON_KEY_ORDER_MISTAKEN_FOR_VECTOR_ORDER"
R3_STATUS = "PASS_REAL_BACKEND_AF0_CONTROL_RELEASE_NO_TARGET_SOLVE"
R3_GATE = "PASS_AUDITED_AF0_CONTROL_ONLY"
PACKAGE_DIGEST = "a7b48c88061e00cc3dc44dd00a2a17855a7f8c65dd228f725101fde9a1839eb4"
CANDIDATE_DIGEST = "6a00f71f4904574841d17eaebba7f8318fc136d477ab6fd324f3354f1b33e400"
SNAPSHOT = ROOT / "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.29.json"
LATEST = ROOT / "registry/session-checkpoint-latest.json"
MANIFEST = ROOT / "project-manifest.json"
DECISIONS = ROOT / "registry/decision-log.jsonl"
CONTRACT_R3 = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlContract_v0.3.json"
FAILURE_R1 = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlFailureResult_v0.1.json"
FAILURE_R2 = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlFailureResult_v0.2.json"
AUDIT_R3 = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlAuditResult_v0.3.json"
RELEASE_R3 = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_control_release_v0.3.py"
GRANTS = [
    ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",
    ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",
]
PHYSICAL_ARTIFACT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"object required: {path}")
    return value


def find_exact(value: Any, target: str, path: str = "$") -> list[str]:
    if isinstance(value, dict):
        return sum((find_exact(item, target, f"{path}.{key}") for key, item in value.items()), [])
    if isinstance(value, list):
        return sum((find_exact(item, target, f"{path}[{index}]") for index, item in enumerate(value)), [])
    return [path] if value == target else []


def load_release():
    spec = importlib.util.spec_from_file_location("background3c10_g0_release", RELEASE_R3)
    if spec is None or spec.loader is None:
        raise RuntimeError("R3 release import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate() -> dict[str, Any]:
    manifest = load(MANIFEST)
    latest = load(LATEST)
    snapshot = load(SNAPSHOT)
    contract = load(CONTRACT_R3)
    failure_r1 = load(FAILURE_R1)
    failure_r2 = load(FAILURE_R2)
    frozen_audit = load(AUDIT_R3)
    decisions = [
        json.loads(line) for line in DECISIONS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert manifest["release"] == RELEASE
    assert manifest["release_date"] == "2026-08-05"
    assert LATEST.read_bytes() == SNAPSHOT.read_bytes()
    assert latest == snapshot
    assert latest["checkpoint_id"] == CHECKPOINT
    assert latest["basis_commit"] == BASIS_COMMIT
    assert latest["canonical_snapshot"] == "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.29.json"
    assert latest["current_workstreams"][0]["next_block"] == NEXT

    selected = [item for item in decisions if item.get("decision_id") == DECISION]
    assert len(selected) == 1
    assert selected[0]["evidence_effect"] == "SOFTWARE_REAL_BACKEND_ANALYTIC_CONTROL_TRANSACTION_QA_ONLY"
    assert selected[0]["physical_evidence_effect"] == "NONE"

    gates = manifest["gates"]
    expected = {
        "R1.0": ACTIVE,
        "BACKGROUND_SOLVER_IMPLEMENTATION": "REAL_BACKEND_AF0_CONTROL_RELEASE_AUDITED_AUTHORIZATION_REVIEW_REMAINING",
        "BACKGROUND_3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE": R3_GATE,
        "BACKGROUND_3C10_R1": R1_STATUS,
        "BACKGROUND_3C10_R2": R2_STATUS,
        "BACKGROUND_3C10_R3": R3_STATUS,
        "BACKGROUND_3C11_AUTHORIZATION_REVIEW": "NOT_STARTED",
        "BACKGROUND_3C_EXECUTION": "NOT_AUTHORIZED",
        "BACKGROUND_SOLVER_EXECUTION": "NOT_AUTHORIZED",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "FULL_LINEARIZED_BOUNDARY_TRACE_RANK": "NOT_PROVEN",
        "FREDHOLM_PROPERTY": "NOT_PROVEN",
        "CONTINUUM_BVP_JACOBIAN": "NOT_PROVEN",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected.items():
        assert gates.get(key) == value, (key, gates.get(key), value)

    assert manifest["next_block"] == NEXT
    assert manifest["parent_action_v0_1"]["next_block"] == NEXT
    assert manifest["c_phys_operator_entry"]["next_block"] == NEXT
    assert manifest["c_phys_operator_entry"]["solver_authorized"] is False
    assert manifest["c_phys_operator_entry"]["physical_background"] == "NOT_ESTABLISHED"
    assert manifest["c_phys_m1"]["next_block"] == NEXT
    assert find_exact(manifest, OLD_NEXT) == []
    assert find_exact(manifest, OLD_ACTIVE) == []
    assert find_exact(latest, OLD_NEXT) == []
    assert find_exact(latest, OLD_ACTIVE) == []

    background = manifest["background_3c10"]
    assert background["status"] == R3_GATE
    assert background["append_only_failures"] == {"R1": R1_STATUS, "R2": R2_STATUS}
    assert background["package_manifest_sha256"] == PACKAGE_DIGEST
    assert background["source_count"] == 24
    assert background["candidate_sha256"] == CANDIDATE_DIGEST
    assert background["model_a_F"] == 0.0
    assert background["frozen_target_a_F"] == "1/4_NOT_EXECUTED"
    assert background["independent_integration_call_count"] == 6
    assert background["json_mapping_key_order_semantic"] is False
    assert background["handoff_vector_order_source"] == "EXPLICIT_CANDIDATE_FIELDS_CONTRACT"
    assert background["primary_newton_calls"] == 0
    assert background["shooting_jacobian_calls"] == 0
    assert background["nonlinear_root_calls"] == 0
    assert background["cp01r1_attempts"] == 0
    assert background["target_a_F_one_quarter_solves"] == 0
    assert background["operative_grants"] == 0
    assert background["physical_result_artifacts"] == 0
    assert background["continuum_convergence_inference_allowed"] is False
    assert background["physical_evidence_effect"] == "NONE"

    assert failure_r1["status"] == R1_STATUS
    assert failure_r1["disposition"]["r1_reuse_for_acceptance_forbidden"] is True
    assert failure_r2["status"] == R2_STATUS
    assert failure_r2["disposition"]["r2_reuse_for_acceptance_forbidden"] is True
    assert contract["previous_control_runs"][0]["may_be_reclassified_as_pass"] is False
    assert contract["previous_control_runs"][1]["may_be_reclassified_as_pass"] is False
    assert contract["handoff_contract"]["json_object_key_order_semantic"] is False
    assert contract["handoff_contract"]["vector_reconstruction_order"] == "candidate_fields"
    assert contract["primary_control"]["acceptance"]["continuum_convergence_inference_allowed"] is False

    assert frozen_audit["status"] == R3_STATUS
    assert frozen_audit["physical_evidence_effect"] == "NONE"
    assert frozen_audit["closed_package"]["package_manifest_sha256"] == PACKAGE_DIGEST
    assert frozen_audit["closed_package"]["source_count"] == 24
    assert frozen_audit["primary_control"]["candidate_sha256"] == CANDIDATE_DIGEST
    assert frozen_audit["primary_control"]["newton_call_count"] == 0
    assert frozen_audit["independent_control"]["integration_call_count"] == 6
    assert frozen_audit["independent_control"]["shooting_jacobian_call_count"] == 0
    assert frozen_audit["independent_control"]["nonlinear_root_call_count"] == 0
    assert frozen_audit["handoff_control"]["json_mapping_key_order_semantic"] is False
    assert frozen_audit["execution_firewall"]["cp01r1_attempts"] == 0
    assert frozen_audit["execution_firewall"]["target_a_F_one_quarter_solves"] == 0
    assert frozen_audit["execution_firewall"]["operative_grants_created"] == 0
    assert frozen_audit["execution_firewall"]["physical_result_artifacts_created"] == 0

    live_audit = load_release().static_audit()
    assert live_audit["status"] == "PASS_REAL_BACKEND_CONTROL_STATIC_AUDIT_NO_BACKEND_IMPORT"
    assert live_audit["package_manifest_sha256"] == PACKAGE_DIGEST
    assert live_audit["source_count"] == 24
    assert live_audit["r1_failure_status"] == R1_STATUS
    assert live_audit["r2_failure_status"] == R2_STATUS
    assert live_audit["r3_control_run_id"] == frozen_audit["control_run_id"]
    assert live_audit["parent_imports_numerical_backend"] is False
    assert live_audit["worker_launches"] == 0
    assert live_audit["cp01r1_attempts"] == 0
    assert live_audit["target_root_solves"] == 0
    assert live_audit["operative_grants"] == 0
    assert live_audit["physical_results"] == 0
    assert live_audit["continuum_convergence_inference_allowed"] is False

    blockers = {
        item["blocker_id"] for item in latest["open_blockers"]
        if isinstance(item, dict) and "blocker_id" in item
    }
    assert "UL-BLK-C-PHYS-BACKGROUND-3C10-001" not in blockers
    assert "UL-BLK-C-PHYS-BACKGROUND-3C11-001" in blockers
    verified = {
        item["result_id"]: item for item in latest["verified_results"]
        if isinstance(item, dict) and "result_id" in item
    }
    result_record = verified["UL-RES-C-PHYS-M1-BG3C10-001"]
    assert result_record["status"] == R3_GATE
    assert result_record["package_manifest_sha256"] == PACKAGE_DIGEST
    assert result_record["candidate_sha256"] == CANDIDATE_DIGEST
    assert result_record["physical_evidence_effect"] == "NONE"

    assert all(not path.exists() for path in GRANTS)
    assert not PHYSICAL_ARTIFACT.exists()

    return {
        "status": "PASS",
        "release": RELEASE,
        "decision": DECISION,
        "checkpoint": CHECKPOINT,
        "r1_status": R1_STATUS,
        "r2_status": R2_STATUS,
        "r3_status": R3_STATUS,
        "package_manifest_sha256": PACKAGE_DIGEST,
        "candidate_sha256": CANDIDATE_DIGEST,
        "source_count": 24,
        "real_backend_control_status": R3_GATE,
        "execution_authorized": False,
        "physical_solver_calls": 0,
        "cp01r1_attempts": 0,
        "operative_grants": 0,
        "physical_result_artifacts": 0,
        "continuum_convergence_inference_allowed": False,
        "physical_evidence_effect": "NONE",
        "next_block": NEXT,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else "PASS: G0 v1.21")


if __name__ == "__main__":
    main()
