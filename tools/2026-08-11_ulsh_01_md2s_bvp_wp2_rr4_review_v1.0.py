#!/usr/bin/env python3
"""Independent ULSH-01 WP2-RR4 H3 release-readiness review, strictly no-solve.

Stdlib-only source/contract review. It does not import the H3 transaction, NumPy,
SciPy, either numerical backend, or any physical execution entry point.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_RR4Review_v1.0.json"
H3_CONTRACT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_H3Contract_v1.0.json"
H3_TX_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.4.py"
RR3_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_RR3Review_v1.0.json"
H2_CONTRACT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_H2Contract_v1.0.json"
RELEASE_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.3.json"
GRANT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.3.json"

EXPECTED_BLOBS = {
    "h3_contract": "a09067d749493fa14c61fc8a7678ca353a005566",
    "h3_transaction": "2dd09d9ade6d6ae69c1949833e88b2af49c13710",
    "rr3_review": "9d3ccc1553e8484550d81a57f9248991b63a9c03",
    "h2_contract": "213cf0c67bb057835d8e680b4199393b2fe6b6cf",
}


class RR4ReviewFailure(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RR4ReviewFailure(f"top-level object required: {path}")
    return value


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def verify_basis() -> dict[str, str]:
    paths = {
        "h3_contract": H3_CONTRACT_PATH,
        "h3_transaction": H3_TX_PATH,
        "rr3_review": RR3_PATH,
        "h2_contract": H2_CONTRACT_PATH,
    }
    observed = {key: git_blob_sha1(path) for key, path in paths.items()}
    if observed != EXPECTED_BLOBS:
        raise RR4ReviewFailure(f"RR4 review basis drift: {observed}")
    return observed


def verify_rr3_b01(source: str) -> dict[str, bool]:
    strict_rejects_inf = False
    try:
        json.dumps({"x": math.inf}, allow_nan=False)
    except ValueError:
        strict_rejects_inf = True
    execute = source[source.index("def execute(transaction_root"):]
    checks = {
        "python_strict_json_rejects_nonfinite": strict_rejects_inf,
        "recursive_projection_present": "def json_safe_diagnostic_projection" in source,
        "nonfinite_detection_present": "not math.isfinite(value)" in source,
        "replacement_is_null_not_finite": "return None, replacements" in source,
        "path_reason_ledger_present": "json_safe_nonfinite_replacements" in source and "original_nonfinite_kind" in source,
        "finite_reinterpretation_forbidden": "NOT_A_FINITE_MEASUREMENT" in source,
        "second_recursive_nonfinite_check": "remaining = _walk_nonfinite(projected)" in source,
        "strict_serialization_recheck": "allow_nan=False" in source,
        "sanitizer_before_packaging": execute.index("sanitize_raw_result_for_immutable_json(raw_result)") < execute.index("package_schema_complete_result"),
    }
    if not all(checks.values()):
        raise RR4ReviewFailure(f"RR3-B01 closure not independently verified: {checks}")
    return checks


def verify_rr3_b02(source: str) -> dict[str, bool]:
    execute = source[source.index("def execute(transaction_root"):]
    before_except = execute[:execute.index("except BaseException as exc:")]
    after_except = execute[execute.index("except BaseException as exc:"):]
    order = [
        "with H2.total_transaction_wall_clock_limit",
        "H2.supervised_target_execution",
        "package_schema_complete_result",
        'mark_state(grant_dir, "COMMITTING_RESULT"',
        "os.replace(staging, result_dir)",
        "UTILS._fsync_directory(result_dir.parent)",
        'grant_dir / "result-commit.json"',
        'mark_state(grant_dir, "SUCCEEDED"',
    ]
    positions = [before_except.index(marker) for marker in order]
    checks = {
        "commit_sequence_ordered": positions == sorted(positions),
        "precommit_expected_hashes_recorded": "expected_result_sha256" in before_except and "expected_artifact_manifest_sha256" in before_except,
        "committed_result_inspected_on_any_baseexception": "inspect_committed_result(result_dir, package)" in after_except,
        "result_and_manifest_hashes_verified": "COMMITTED_HASHES_MATCH_PRECOMMIT_PACKAGE" in source and "artifact-manifest.json" in source and "result.json" in source,
        "committed_state_never_plain_failed": 'durable_state = "COMMITTED_INDETERMINATE" if committed else' in after_except,
        "commit_truth_written_to_failure_record": '"result_package_committed": committed' in after_except,
        "replay_forbidden": "replay_permitted=False" in after_except and '"replay_permitted": False' in after_except,
        "retry_requires_new_grant": '"retry_requires_new_grant": True' in after_except and "retry_requires_new_grant=True" in after_except,
        "hard_deadline_value_preserved_in_contract": load_json(H3_CONTRACT_PATH)["rr3_blocker_closure"]["RR3-B02"]["hard_total_deadline_seconds"] == 21600,
    }
    if not all(checks.values()):
        raise RR4ReviewFailure(f"RR3-B02 closure not independently verified: {checks}")
    return checks


def verify_future_release_binding(source: str, contract: dict[str, Any]) -> dict[str, bool]:
    checks = {
        "h3_release_and_grant_paths_are_new_exact_paths": contract["grant_protocol"]["release_path"].endswith("v1.3.json") and contract["grant_protocol"]["grant_path"].endswith("v1.3.json"),
        "exact_contract_binding_enforced": "transaction_contract_sha256" in source and "contract_sha" in source,
        "exact_source_bundle_binding_enforced": "source_bundle_sha256" in source and "bundle_sha" in source,
        "schedule_35_binding_enforced": 'grant.get("schedule_sha256") != schedule_sha' in source and 'grant.get("planned_entry_count") != 35' in source,
        "dependency_binding_enforced": "dependency_lock_sha256" in source,
        "resource_and_result_schema_binding_enforced": "resource_policy_git_blob_sha1" in source and "result_schema_git_blob_sha1" in source,
        "single_use_scope_enforced": 'for key in ("single_use", "physical_solve_authorized", "no_retry", "no_scan", "no_fallback")' in source,
        "nonce_and_time_window_enforced": "NONCE_RE.fullmatch" in source and "maximum_validity_seconds" in source,
        "source_blob_drift_fail_closed": "H3 source binding drift" in source,
        "inherited_h2_preflight_retained": "H2.static_preflight()" in source,
    }
    if not all(checks.values()):
        raise RR4ReviewFailure(f"future H3 release binding incomplete: {checks}")
    return checks


def audit() -> dict[str, Any]:
    review = load_json(REVIEW_PATH)
    contract = load_json(H3_CONTRACT_PATH)
    rr3 = load_json(RR3_PATH)
    source = H3_TX_PATH.read_text(encoding="utf-8")
    if review.get("review_status") != "PASS_WP2_RR4_H3_RELEASE_READINESS_VERIFIED_NO_SOLVE":
        raise RR4ReviewFailure("RR4 review-status drift")
    if contract.get("status") != "PASS_WP2_H3_IMPLEMENTED_NO_SOLVE_PENDING_RR4":
        raise RR4ReviewFailure("unexpected H3 contract status")
    if rr3.get("review_status") != "BLOCKED_WP2_RR3_NEW_RELEASE_BLOCKERS_FOUND_NO_SOLVE":
        raise RR4ReviewFailure("unexpected RR3 basis")
    if RELEASE_PATH.exists() or GRANT_PATH.exists():
        raise RR4ReviewFailure("H3 release/grant must remain absent during RR4")
    basis = verify_basis()
    b01 = verify_rr3_b01(source)
    b02 = verify_rr3_b02(source)
    bindings = verify_future_release_binding(source, contract)
    if review.get("new_release_blockers") != {}:
        raise RR4ReviewFailure("RR4 pass review must not hide listed release blockers")
    return {
        "status": "PASS_RR4_H3_RELEASE_READINESS_REPRODUCED_NO_SOLVE",
        "review_status": review["review_status"],
        "reviewed_source_git_blob_sha1": basis,
        "RR3-B01": b01,
        "RR3-B02": b02,
        "future_release_binding": bindings,
        "new_release_blockers": {},
        "wp2_status": "CLOSED_RELEASE_READY_NO_EXECUTION",
        "release_authorization_present": False,
        "single_use_grant_present": False,
        "solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "CP01R1": "NOT_EXECUTED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    print(json.dumps(audit(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
