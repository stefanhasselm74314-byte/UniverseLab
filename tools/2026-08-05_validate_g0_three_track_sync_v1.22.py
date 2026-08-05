#!/usr/bin/env python3
"""Canonical G0 v1.22 validator after Background-3C11 denial."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RELEASE = "2.22-c-phys-m1-background-3c11-authorization-denied-v0.1"
DECISION = "UL-DEC-0037"
CHECKPOINT = "UL-CHK-20260805-030"
BASIS_COMMIT = "a5dcb30fd74afa6ccde92c140e67b71f77fbdaf2"
NEXT = "C-PHYS-R1.0-BACKGROUND-3C12_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE_IMPLEMENTATION_ONLY"
OLD_NEXT = "C-PHYS-R1.0-BACKGROUND-3C11_REAL_BACKEND_CONTROL_RELEASE_AUTHORIZATION_REVIEW_ONLY"
OLD_ACTIVE = "ACTIVE_REAL_BACKEND_CONTROL_RELEASE_AUTHORIZATION_REVIEW_REMAINING"
ACTIVE = "ACTIVE_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE_IMPLEMENTATION_REMAINING"
DENIAL = "DENIED_OPERATIVE_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE_ABSENT"
R1_STATUS = "FAIL_CLOSED_PRIMARY_UNIFORM_BULK_THRESHOLD_AT_N96"
R2_STATUS = "FAIL_CLOSED_CANDIDATE_JSON_KEY_ORDER_MISTAKEN_FOR_VECTOR_ORDER"
R3_STATUS = "PASS_REAL_BACKEND_AF0_CONTROL_RELEASE_NO_TARGET_SOLVE"
R3_GATE = "PASS_AUDITED_AF0_CONTROL_ONLY"
PACKAGE_DIGEST = "a7b48c88061e00cc3dc44dd00a2a17855a7f8c65dd228f725101fde9a1839eb4"
SNAPSHOT = ROOT / "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.30.json"
LATEST = ROOT / "registry/session-checkpoint-latest.json"
MANIFEST = ROOT / "project-manifest.json"
DECISIONS = ROOT / "registry/decision-log.jsonl"
REVIEW = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C11RealBackendControlAuthorizationReview_v0.1.json"
REVIEW_VALIDATOR = ROOT / "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c11_v0.1.py"
AUDIT_R3 = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlAuditResult_v0.3.json"
FAILURE_R1 = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlFailureResult_v0.1.json"
FAILURE_R2 = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlFailureResult_v0.2.json"
TARGET_RELEASE = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c12_target_path_release_v0.1.py"
GRANT_SCHEMA = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C12SingleUseGrantContract_v0.1.json"
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


def load_review_validator():
    spec = importlib.util.spec_from_file_location("background3c11_g0_validator", REVIEW_VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("3C11 validator import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate() -> dict[str, Any]:
    manifest = load(MANIFEST)
    latest = load(LATEST)
    snapshot = load(SNAPSHOT)
    review = load(REVIEW)
    audit_r3 = load(AUDIT_R3)
    failure_r1 = load(FAILURE_R1)
    failure_r2 = load(FAILURE_R2)
    decisions = [json.loads(line) for line in DECISIONS.read_text(encoding="utf-8").splitlines() if line.strip()]

    assert manifest["release"] == RELEASE
    assert manifest["release_date"] == "2026-08-05"
    assert LATEST.read_bytes() == SNAPSHOT.read_bytes()
    assert latest == snapshot
    assert latest["checkpoint_id"] == CHECKPOINT
    assert latest["basis_commit"] == BASIS_COMMIT
    assert latest["canonical_snapshot"] == "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.30.json"
    assert latest["current_workstreams"][0]["next_block"] == NEXT

    selected = [item for item in decisions if item.get("decision_id") == DECISION]
    assert len(selected) == 1
    assert selected[0]["evidence_effect"] == "GOVERNANCE_AND_TARGET_PATH_EXECUTION_SAFETY_REVIEW_ONLY"
    assert selected[0]["physical_evidence_effect"] == "NONE"

    expected = {
        "R1.0": ACTIVE,
        "BACKGROUND_SOLVER_IMPLEMENTATION": "REAL_BACKEND_AF0_CONTROL_AUDITED_TARGET_PATH_AND_GRANT_RELEASE_MISSING",
        "BACKGROUND_3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE": R3_GATE,
        "BACKGROUND_3C10_R1": R1_STATUS,
        "BACKGROUND_3C10_R2": R2_STATUS,
        "BACKGROUND_3C10_R3": R3_STATUS,
        "BACKGROUND_3C11_AUTHORIZATION_REVIEW": DENIAL,
        "BACKGROUND_3C12_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE": "NOT_STARTED",
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
        assert manifest["gates"].get(key) == value, (key, manifest["gates"].get(key), value)

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

    background = manifest["background_3c11"]
    assert background["status"] == DENIAL
    assert background["reviewed_control_release"] == "BACKGROUND_3C10_R3_PASS_AUDITED_AF0_CONTROL_ONLY"
    assert background["package_manifest_sha256"] == PACKAGE_DIGEST
    assert background["review_imported_backend"] is False
    assert background["physical_solver_calls"] == 0
    assert background["cp01r1_attempts"] == 0
    assert background["target_a_F_one_quarter_solves"] == 0
    assert background["operative_grants"] == 0
    assert background["physical_result_artifacts"] == 0
    assert background["physical_evidence_effect"] == "NONE"
    assert background["next_block"] == NEXT

    assert review["status"] == DENIAL
    assert review["authorization_decision"]["authorized"] is False
    assert review["authorization_decision"]["physical_backend_imported"] is False
    assert review["authorization_decision"]["cp01r1_attempted"] is False
    assert review["authorization_decision"]["target_a_F_one_quarter_solve_attempted"] is False
    assert review["authorization_decision"]["grant_created"] is False
    assert review["authorization_decision"]["result_artifact_created"] is False
    assert review["future_implementation_constraints"]["next_block"] == NEXT
    assert review["future_implementation_constraints"]["physical_backend_import_forbidden"] is True
    assert review["future_implementation_constraints"]["cp01r1_execution_forbidden"] is True
    assert review["future_implementation_constraints"]["operative_grant_creation_forbidden"] is True
    assert review["physical_evidence_effect"] == "NONE"

    assert failure_r1["status"] == R1_STATUS
    assert failure_r2["status"] == R2_STATUS
    assert audit_r3["status"] == R3_STATUS
    assert audit_r3["closed_package"]["package_manifest_sha256"] == PACKAGE_DIGEST
    assert audit_r3["execution_firewall"]["cp01r1_attempts"] == 0
    assert audit_r3["execution_firewall"]["target_a_F_one_quarter_solves"] == 0
    assert audit_r3["execution_firewall"]["operative_grants_created"] == 0
    assert audit_r3["execution_firewall"]["physical_result_artifacts_created"] == 0

    review_result = load_review_validator().validate()
    assert review_result["status"] == "PASS"
    assert review_result["review_status"] == DENIAL
    assert review_result["review_imports_numerical_backend"] is False
    assert review_result["physical_backend_imported"] is False
    assert review_result["physical_solver_calls"] == 0
    assert review_result["cp01r1_attempts"] == 0
    assert review_result["target_a_F_one_quarter_solves"] == 0
    assert review_result["operative_grants"] == 0
    assert review_result["physical_result_artifacts"] == 0
    assert review_result["physical_evidence_effect"] == "NONE"

    blockers = {item["blocker_id"] for item in latest["open_blockers"] if isinstance(item, dict) and "blocker_id" in item}
    assert "UL-BLK-C-PHYS-BACKGROUND-3C11-001" not in blockers
    assert "UL-BLK-C-PHYS-BACKGROUND-3C12-001" in blockers
    verified = {item["result_id"]: item for item in latest["verified_results"] if isinstance(item, dict) and "result_id" in item}
    result_record = verified["UL-RES-C-PHYS-M1-BG3C11-001"]
    assert result_record["status"] == DENIAL
    assert result_record["package_manifest_sha256"] == PACKAGE_DIGEST
    assert result_record["physical_evidence_effect"] == "NONE"

    assert not TARGET_RELEASE.exists()
    assert not GRANT_SCHEMA.exists()
    assert all(not path.exists() for path in GRANTS)
    assert not PHYSICAL_ARTIFACT.exists()

    return {
        "status": "PASS",
        "release": RELEASE,
        "decision": DECISION,
        "checkpoint": CHECKPOINT,
        "review_status": DENIAL,
        "r1_status": R1_STATUS,
        "r2_status": R2_STATUS,
        "r3_status": R3_STATUS,
        "package_manifest_sha256": PACKAGE_DIGEST,
        "execution_authorized": False,
        "review_imports_numerical_backend": False,
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
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else "PASS: G0 v1.22")


if __name__ == "__main__":
    main()
