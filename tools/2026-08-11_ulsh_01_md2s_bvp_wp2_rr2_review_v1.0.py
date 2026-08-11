#!/usr/bin/env python3
"""ULSH-01 / WP2-RR2 independent hardening re-review, strictly no-solve.

This reviewer performs source/contract inspection only. It never imports either
numerical backend and never calls a target execution function. Its purpose is to
verify the original RR blocker closures and independently search for additional
release-readiness defects before any release authorization or single-use grant.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_HardeningReReview_v1.0.json"
HARDENING_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_HardeningContract_v1.0.json"
TARGET_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.1.py"
TRANSACTION_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.1.py"
RESOURCE_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
RESULT_SCHEMA_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResultSchema_v0.1.json"
PREREG_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"
RELEASE_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.1.json"
GRANT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.1.json"

EXPECTED_BLOBS = {
    "hardening_contract": "ddbe12afbb6e06bfe7f3fbccb250ef1d45246236",
    "hardened_target_entrypoint": "304592405f843822e142110ba6a65fc845579489",
    "hardened_transaction": "a181056cb93b69c0c6c436a05b2bea838de25bda",
    "resource_policy": "954a9730d3fa34864df7168555912ebba2dd6c3d",
    "result_schema": "b1fdf45aa9fb3d585e73795e9294dfa0c185fc39",
    "preregistration": "9789101e0a168580b6906eb21edad5a5db2b64ce",
}


class ReviewFailure(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReviewFailure(f"top-level object required: {path}")
    return value


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def verify_review_basis() -> dict[str, str]:
    paths = {
        "hardening_contract": HARDENING_PATH,
        "hardened_target_entrypoint": TARGET_PATH,
        "hardened_transaction": TRANSACTION_PATH,
        "resource_policy": RESOURCE_PATH,
        "result_schema": RESULT_SCHEMA_PATH,
        "preregistration": PREREG_PATH,
    }
    observed = {key: git_blob_sha1(path) for key, path in paths.items()}
    if observed != EXPECTED_BLOBS:
        raise ReviewFailure(f"review basis drift: {observed}")
    return observed


def verify_original_closures(target: str, transaction: str) -> dict[str, bool]:
    checks = {
        "RR-B01_stage_timeout": (
            "def stage_wall_clock_limit" in target
            and "signal.setitimer(signal.ITIMER_REAL" in target
            and "STAGE_TIMEOUT_NO_RETRY" in target
        ),
        "RR-B02_result_budget": (
            "class BoundedStagingWriter" in transaction
            and "maximum_result_bytes" in transaction
            and "final staged package exceeds result byte budget" in transaction
        ),
        "RR-B03_schema_capture": (
            "schema_complete_capture" in target
            and "spectral_tail_table" in target
            and "all_eight_boundary_residuals" in target
            and "profile_artifacts" in target
            and "_validate_result_payload(result_payload)" in transaction
        ),
        "RR-B04_machine_metadata": (
            "def _cpu_identity" in transaction
            and "def _blas_lapack_metadata" in transaction
            and '"cpu_identity": _cpu_identity()' in transaction
            and '"blas_lapack": _blas_lapack_metadata()' in transaction
        ),
    }
    if not all(checks.values()):
        raise ReviewFailure(f"one or more original RR closures are not present: {checks}")
    return checks


def identify_new_blockers(target: str, transaction: str, prereg: dict[str, Any], result_schema: dict[str, Any]) -> dict[str, bool]:
    # RR2-B01: frozen schema requires output collision abort before solver init.
    solve_marker = "raw_result = target.execute_physical_schedule(capability)"
    collision_marker = "if result_dir.exists():"
    if solve_marker not in transaction or collision_marker not in transaction:
        raise ReviewFailure("cannot locate solve/output-collision ordering markers")
    b01 = transaction.index(collision_marker) > transaction.index(solve_marker)
    if result_schema["immutable_output_policy"]["existing_path_action"] != "ABORT_BEFORE_SOLVER_INITIALIZATION":
        raise ReviewFailure("frozen immutable-output policy drift")

    # RR2-B02: NumPy/SciPy BLAS metadata import happens in validate_runtime before
    # enforce_process_limits; UNSET thread-control variables are accepted.
    b02 = (
        transaction.index("runtime = validate_runtime()") < transaction.index("enforce_process_limits()")
        and 'if value not in {"UNSET", "1"}' in transaction
        and '"blas_lapack": _blas_lapack_metadata()' in transaction
    )

    # RR2-B03: target finalization is outside per-entry timer and the total elapsed
    # time is only measured after _finalize returns.
    final_marker = "finalized = _finalize("
    elapsed_marker = "execution_elapsed = time.monotonic() - start_monotonic"
    b03 = (
        final_marker in target
        and elapsed_marker in target
        and target.index(final_marker) < target.index(elapsed_marker)
        and "with total_wall_clock_limit" not in target
    )

    # RR2-B04: preregistration requires >=80-bit audit for borderline acceptance;
    # hardened target contains no such path or fail-closed precision classification.
    requirement = prereg["primary_discretization"]["higher_precision_audit"]
    if requirement != "80_BIT_OR_GREATER_REQUIRED_FOR_ANY_BORDERLINE_ACCEPTANCE":
        raise ReviewFailure("higher-precision preregistration requirement drift")
    lower_target = target.lower()
    b04 = not any(token in lower_target for token in (
        "higher_precision", "longdouble", "float128", "mpmath", "decimal", "80_bit", "80-bit"
    ))

    findings = {"RR2-B01": b01, "RR2-B02": b02, "RR2-B03": b03, "RR2-B04": b04}
    if not all(findings.values()):
        raise ReviewFailure(f"expected RR2 blockers are not reproducible: {findings}")
    return findings


def audit() -> dict[str, Any]:
    review = load_json(REVIEW_PATH)
    hardening = load_json(HARDENING_PATH)
    resource = load_json(RESOURCE_PATH)
    result_schema = load_json(RESULT_SCHEMA_PATH)
    prereg = load_json(PREREG_PATH)
    target = TARGET_PATH.read_text(encoding="utf-8")
    transaction = TRANSACTION_PATH.read_text(encoding="utf-8")

    if review["review_status"] != "BLOCKED_WP2_RR2_NEW_RELEASE_BLOCKERS_FOUND_NO_SOLVE":
        raise ReviewFailure("RR2 review status drift")
    if hardening["status"] != "PASS_WP2_HARDENING_IMPLEMENTED_NO_SOLVE_PENDING_REREVIEW":
        raise ReviewFailure("review is not based on the expected hardening state")
    if resource["resource_limits"]["maximum_wall_clock_seconds_total"] != 21600:
        raise ReviewFailure("total resource limit drift")
    if resource["resource_limits"]["maximum_cpu_threads"] != 1:
        raise ReviewFailure("CPU-thread resource limit drift")
    if RELEASE_PATH.exists() or GRANT_PATH.exists():
        raise ReviewFailure("release/grant must remain absent during RR2")

    basis = verify_review_basis()
    original = verify_original_closures(target, transaction)
    new_blockers = identify_new_blockers(target, transaction, prereg, result_schema)
    return {
        "status": "PASS_RR2_REVIEW_REPRODUCED_BLOCKED_NO_SOLVE",
        "review_status": review["review_status"],
        "original_RR_closures_verified": original,
        "new_release_blockers_reproduced": new_blockers,
        "reviewed_source_git_blob_sha1": basis,
        "release_authorization_present": False,
        "single_use_grant_present": False,
        "solver_imported": False,
        "solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    print(json.dumps(audit(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
