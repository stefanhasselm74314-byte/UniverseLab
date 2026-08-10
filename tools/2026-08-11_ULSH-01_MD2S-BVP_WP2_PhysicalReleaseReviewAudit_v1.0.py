#!/usr/bin/env python3
"""Reproduce the ULSH-01 WP2 physical release review without solver execution."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = "437b4e14edb65ae6abf7362d6247fe285026bf6b"
RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
PAYLOAD_SHA256 = "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302"

REVIEW_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_PhysicalReleaseReview_v1.0.json"
CONTRACT_PATH = ROOT / "registry/2026-08-10_ULSH-01_MD2S-BVP_WP2_PhysicalTransactionContract_v1.0.json"
TARGET_PATH = ROOT / "tools/2026-08-10_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.0.py"
TRANSACTION_PATH = ROOT / "tools/2026-08-10_ulsh_01_md2s_bvp_wp2_transaction_v1.0.py"
WP2_TEST_PATH = ROOT / "tests/2026-08-10_ULSH-01_MD2S-BVP_WP2_PhysicalTransactionTest_v1.0.py"
WP2_WORKFLOW_PATH = ROOT / ".github/workflows/2026-08-10_ULSH-01_MD2S-BVP_WP2_PhysicalTransactionContract_v1.0.yml"
WP2_LEDGER_PATH = ROOT / "science/hzt-m0/md2s/2026-08-10_ULSH-01_MD2S-BVP_WP2_PhysicalTransactionLedger_v1.0.md"
RESOURCE_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
RESULT_SCHEMA_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResultSchema_v0.1.json"
PREREG_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"
LOCK_B_PATH = ROOT / "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3B_v0.1.txt"
LOCK_C_PATH = ROOT / "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C_v0.1.txt"
RELEASE_PATH = ROOT / "registry/2026-08-10_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.0.json"
GRANT_PATH = ROOT / "registry/2026-08-10_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.0.json"

EXPECTED_SOURCE_BLOBS = {
    "wp2_contract": (CONTRACT_PATH, "f384801d5693c35a93863c59fa413121061dfdb0"),
    "target_entrypoint": (TARGET_PATH, "ea02d02f61e8c072c1191577c1bf7660038ad516"),
    "transaction_guard": (TRANSACTION_PATH, "110ca418cfed89f9661018c499342a0cd3bc6821"),
    "wp2_test": (WP2_TEST_PATH, "e5e572b1658233c9cf035d04c630013c9523648a"),
    "wp2_workflow": (WP2_WORKFLOW_PATH, "de270bb88d5490f6510d6afc6b0919e8a4a267c6"),
    "wp2_ledger": (WP2_LEDGER_PATH, "b9f9129accd598e6d4c5cdc92ff4c47ec5831b0b"),
    "resource_policy": (RESOURCE_PATH, "954a9730d3fa34864df7168555912ebba2dd6c3d"),
    "result_schema": (RESULT_SCHEMA_PATH, "b1fdf45aa9fb3d585e73795e9294dfa0c185fc39"),
    "preregistration": (PREREG_PATH, "9789101e0a168580b6906eb21edad5a5db2b64ce"),
}


class ReviewFailure(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReviewFailure(f"top-level JSON object required: {path}")
    return value


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_baseline_bindings(review: dict[str, Any]) -> dict[str, str]:
    if review.get("reviewed_baseline_commit") != BASELINE_COMMIT:
        raise ReviewFailure("reviewed baseline commit drift")
    if review.get("reviewed_run_id") != RUN_ID or review.get("reviewed_payload_sha256") != PAYLOAD_SHA256:
        raise ReviewFailure("review run/payload binding drift")
    observed: dict[str, str] = {}
    declared = review.get("reviewed_source_blobs", {})
    for key, (path, expected) in EXPECTED_SOURCE_BLOBS.items():
        actual = git_blob_sha1(path)
        if actual != expected or declared.get(key) != expected:
            raise ReviewFailure(f"reviewed source drift: {key}: {actual} != {expected}")
        observed[key] = actual
    return observed


def reproduce_findings() -> dict[str, Any]:
    review = load_json(REVIEW_PATH)
    contract = load_json(CONTRACT_PATH)
    resource = load_json(RESOURCE_PATH)
    result_schema = load_json(RESULT_SCHEMA_PATH)
    prereg = load_json(PREREG_PATH)
    source_blobs = verify_baseline_bindings(review)

    if contract.get("status") != "PASS_WP2_TRANSACTION_IMPLEMENTED_RELEASE_READY_NO_SOLVE":
        raise ReviewFailure("unexpected WP2 contract status")
    if contract.get("physical_solve_authorized") is not False or contract.get("physical_solve_executed") is not False:
        raise ReviewFailure("WP2 baseline is not in no-solve state")
    if RELEASE_PATH.exists() or GRANT_PATH.exists():
        raise ReviewFailure("release/grant artifact exists during blocked release review")

    transaction_source = TRANSACTION_PATH.read_text(encoding="utf-8")
    target_source = TARGET_PATH.read_text(encoding="utf-8")

    # RR-B01: frozen per-seed/per-level timeout exists in policy but is not consumed by WP2 execution code.
    per_stage_limit = int(resource["resource_limits"]["maximum_wall_clock_seconds_per_seed_per_level"])
    b01 = (
        per_stage_limit == 1800
        and "maximum_wall_clock_seconds_per_seed_per_level" not in transaction_source
        and "maximum_wall_clock_seconds_per_seed_per_level" not in target_source
    )

    # RR-B02: frozen output byte budget exists but current transaction source never consumes it.
    result_limit = int(resource["resource_limits"]["maximum_result_bytes"])
    b02 = result_limit == 1073741824 and "maximum_result_bytes" not in transaction_source

    # RR-B03: the execution return does not instantiate the frozen result schema and does not preserve all mandatory channels.
    required_top = list(result_schema["required_top_level_fields"])
    missing_top_literals = [field for field in required_top if f'"{field}"' not in target_source]
    mandatory_markers = {
        "all_eight_boundary_residuals": "all_eight_boundary_residuals",
        "rr_constraint_profile": "rr-constraint profile",
        "spectral_tail_table": "spectral_tail_table",
        "candidate_inventory": "candidate_inventory",
        "acceptance_audit": "acceptance_audit",
        "profile_artifact_sha256": "profile_artifact_sha256",
    }
    missing_mandatory = [name for name, marker in mandatory_markers.items() if marker not in target_source]
    b03 = bool(missing_top_literals) and bool(missing_mandatory)

    # RR-B04: frozen resource policy requires CPU and BLAS metadata, absent from WP2 runtime attestation.
    reproducibility = resource["reproducibility"]
    cpu_blas_required = reproducibility.get("cpu_and_blas_metadata_required") is True
    cpu_identity_present = any(token in transaction_source for token in ("platform.processor", "cpu_model", "/proc/cpuinfo"))
    blas_identity_present = any(token in transaction_source for token in ("show_config", "__config__", "blas", "lapack"))
    b04 = cpu_blas_required and not cpu_identity_present and not blas_identity_present

    # Nonblocking path alias: the two named locks are byte-identical today.
    lock_b_blob = git_blob_sha1(LOCK_B_PATH)
    lock_c_blob = git_blob_sha1(LOCK_C_PATH)
    w01 = lock_b_blob == lock_c_blob == "2c3a8126fc5ec23bd82f0e99d6922610d9250bfc"

    # Raw quarantine path does not yet mirror the canonical result-schema path.
    canonical_directory = str(result_schema["immutable_output_policy"]["directory"])
    w02 = canonical_directory not in transaction_source and 'external_root / "results"' in transaction_source

    reproduced = {
        "RR-B01": b01,
        "RR-B02": b02,
        "RR-B03": b03,
        "RR-B04": b04,
        "RR-W01": w01,
        "RR-W02": w02,
    }
    if not all(reproduced.values()):
        failed = [key for key, value in reproduced.items() if not value]
        raise ReviewFailure(f"review finding no longer reproduces: {failed}")

    declared_blockers = {item["id"] for item in review.get("blocking_findings", [])}
    if declared_blockers != {"RR-B01", "RR-B02", "RR-B03", "RR-B04"}:
        raise ReviewFailure("declared blocker set drift")
    if review.get("release_decision") != "DO_NOT_CREATE_PHYSICAL_SOLVE_RELEASE_OR_SINGLE_USE_GRANT":
        raise ReviewFailure("release decision drift")

    return {
        "status": "PASS_RELEASE_REVIEW_BLOCKERS_REPRODUCED_NO_SOLVE",
        "review_status": review["review_status"],
        "reviewed_baseline_commit": BASELINE_COMMIT,
        "run_id": RUN_ID,
        "frozen_payload_sha256": PAYLOAD_SHA256,
        "source_git_blob_sha1": source_blobs,
        "blocking_findings": ["RR-B01", "RR-B02", "RR-B03", "RR-B04"],
        "nonblocking_findings": ["RR-W01", "RR-W02"],
        "per_stage_wall_clock_seconds": per_stage_limit,
        "maximum_result_bytes": result_limit,
        "missing_result_top_level_literals": missing_top_literals,
        "missing_mandatory_markers": missing_mandatory,
        "dependency_lock_b_sha256": sha256_file(LOCK_B_PATH),
        "dependency_lock_c_sha256": sha256_file(LOCK_C_PATH),
        "release_authorization_present": False,
        "single_use_grant_present": False,
        "physical_solve_authorized": False,
        "solver_calls": 0,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
        "next_allowed_action": review["next_allowed_action"],
    }


def main() -> int:
    print(json.dumps(reproduce_findings(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
