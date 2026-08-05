#!/usr/bin/env python3
"""Canonical G0 v1.22.1 validator after Background-3C11 denial."""
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
GRANTS = (
    ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",
    ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",
)
PHYSICAL_ARTIFACT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"object required: {path}")
    return value


def expect_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise AssertionError(
            f"{label} drift: actual={actual!r} expected={expected!r} "
            f"actual_type={type(actual).__name__} expected_type={type(expected).__name__}"
        )


def expect_false(value: Any, label: str) -> None:
    if value is not False:
        raise AssertionError(f"{label} must be false, got {value!r}")


def expect_zero(value: Any, label: str) -> None:
    if value != 0:
        raise AssertionError(f"{label} must be zero, got {value!r}")


def find_exact(value: Any, target: str, path: str = "$") -> list[str]:
    if isinstance(value, dict):
        return sum((find_exact(item, target, f"{path}.{key}") for key, item in value.items()), [])
    if isinstance(value, list):
        return sum((find_exact(item, target, f"{path}[{index}]") for index, item in enumerate(value)), [])
    return [path] if value == target else []


def load_review_validator():
    spec = importlib.util.spec_from_file_location("background3c11_g0_validator_v1221", REVIEW_VALIDATOR)
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

    expect_equal(manifest.get("release"), RELEASE, "manifest release")
    expect_equal(manifest.get("release_date"), "2026-08-05", "manifest release date")
    if LATEST.read_bytes() != SNAPSHOT.read_bytes():
        raise AssertionError("checkpoint alias and snapshot are not byte-identical")
    expect_equal(latest, snapshot, "checkpoint object")
    expect_equal(latest.get("checkpoint_id"), CHECKPOINT, "checkpoint ID")
    expect_equal(latest.get("basis_commit"), BASIS_COMMIT, "checkpoint basis commit")
    expect_equal(latest.get("canonical_snapshot"), "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.30.json", "checkpoint snapshot path")
    expect_equal(latest["current_workstreams"][0].get("next_block"), NEXT, "checkpoint next block")

    selected = [item for item in decisions if item.get("decision_id") == DECISION]
    expect_equal(len(selected), 1, "decision count")
    expect_equal(selected[0].get("evidence_effect"), "GOVERNANCE_AND_TARGET_PATH_EXECUTION_SAFETY_REVIEW_ONLY", "decision evidence effect")
    expect_equal(selected[0].get("physical_evidence_effect"), "NONE", "decision physical effect")

    expected_gates = {
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
    for key, expected in expected_gates.items():
        expect_equal(manifest["gates"].get(key), expected, f"manifest gate {key}")

    expect_equal(manifest.get("next_block"), NEXT, "manifest next block")
    expect_equal(manifest["parent_action_v0_1"].get("next_block"), NEXT, "parent next block")
    expect_equal(manifest["c_phys_operator_entry"].get("next_block"), NEXT, "operator next block")
    expect_false(manifest["c_phys_operator_entry"].get("solver_authorized"), "operator solver authorization")
    expect_equal(manifest["c_phys_m1"].get("next_block"), NEXT, "M1 next block")
    expect_equal(find_exact(manifest, OLD_NEXT), [], "stale manifest next-block locations")
    expect_equal(find_exact(manifest, OLD_ACTIVE), [], "stale manifest active-status locations")
    expect_equal(find_exact(latest, OLD_NEXT), [], "stale checkpoint next-block locations")
    expect_equal(find_exact(latest, OLD_ACTIVE), [], "stale checkpoint active-status locations")

    background = manifest.get("background_3c11", {})
    expect_equal(background.get("status"), DENIAL, "manifest 3C11 status")
    expect_equal(background.get("reviewed_control_release"), "BACKGROUND_3C10_R3_PASS_AUDITED_AF0_CONTROL_ONLY", "reviewed release")
    expect_equal(background.get("package_manifest_sha256"), PACKAGE_DIGEST, "3C11 package digest")
    expect_false(background.get("review_imported_backend"), "3C11 backend import")
    for key in ("physical_solver_calls", "cp01r1_attempts", "target_a_F_one_quarter_solves", "operative_grants", "physical_result_artifacts"):
        expect_zero(background.get(key), f"3C11 {key}")
    expect_equal(background.get("physical_evidence_effect"), "NONE", "3C11 physical effect")
    expect_equal(background.get("next_block"), NEXT, "3C11 next block")

    expect_equal(review.get("status"), DENIAL, "review status")
    decision = review["authorization_decision"]
    for key in ("authorized", "physical_backend_imported", "cp01r1_attempted", "target_a_F_one_quarter_solve_attempted", "grant_created", "result_artifact_created"):
        expect_false(decision.get(key), f"review decision {key}")
    future = review["future_implementation_constraints"]
    expect_equal(future.get("next_block"), NEXT, "review next block")
    for key in ("physical_backend_import_forbidden", "cp01r1_execution_forbidden", "operative_grant_creation_forbidden"):
        expect_equal(future.get(key), True, f"review constraint {key}")
    expect_equal(review.get("physical_evidence_effect"), "NONE", "review physical effect")

    expect_equal(failure_r1.get("status"), R1_STATUS, "R1 status")
    expect_equal(failure_r2.get("status"), R2_STATUS, "R2 status")
    expect_equal(audit_r3.get("status"), R3_STATUS, "R3 status")
    expect_equal(audit_r3["closed_package"].get("package_manifest_sha256"), PACKAGE_DIGEST, "R3 package digest")
    for key in ("cp01r1_attempts", "target_a_F_one_quarter_solves", "operative_grants_created", "physical_result_artifacts_created"):
        expect_zero(audit_r3["execution_firewall"].get(key), f"R3 firewall {key}")

    review_result = load_review_validator().validate()
    expect_equal(review_result.get("status"), "PASS", "3C11 validator status")
    expect_equal(review_result.get("review_status"), DENIAL, "3C11 validator review status")
    expect_false(review_result.get("review_imports_numerical_backend"), "3C11 validator numerical import")
    expect_false(review_result.get("physical_backend_imported"), "3C11 validator backend import")
    for key in ("physical_solver_calls", "cp01r1_attempts", "target_a_F_one_quarter_solves", "operative_grants", "physical_result_artifacts"):
        expect_zero(review_result.get(key), f"3C11 validator {key}")
    expect_equal(review_result.get("physical_evidence_effect"), "NONE", "3C11 validator physical effect")

    blockers = {item["blocker_id"] for item in latest["open_blockers"] if isinstance(item, dict) and "blocker_id" in item}
    if "UL-BLK-C-PHYS-BACKGROUND-3C11-001" in blockers:
        raise AssertionError("completed 3C11 blocker remains")
    if "UL-BLK-C-PHYS-BACKGROUND-3C12-001" not in blockers:
        raise AssertionError("3C12 blocker missing")
    verified = {item["result_id"]: item for item in latest["verified_results"] if isinstance(item, dict) and "result_id" in item}
    result_record = verified["UL-RES-C-PHYS-M1-BG3C11-001"]
    expect_equal(result_record.get("status"), DENIAL, "checkpoint 3C11 result status")
    expect_equal(result_record.get("package_manifest_sha256"), PACKAGE_DIGEST, "checkpoint 3C11 package digest")
    expect_equal(result_record.get("physical_evidence_effect"), "NONE", "checkpoint 3C11 physical effect")

    if TARGET_RELEASE.exists():
        raise AssertionError("target-path release unexpectedly exists")
    if GRANT_SCHEMA.exists():
        raise AssertionError("single-use grant schema unexpectedly exists")
    if any(path.exists() for path in GRANTS):
        raise AssertionError("operative grant unexpectedly exists")
    if PHYSICAL_ARTIFACT.exists():
        raise AssertionError("physical result directory unexpectedly exists")

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
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else "PASS: G0 v1.22.1")


if __name__ == "__main__":
    main()
