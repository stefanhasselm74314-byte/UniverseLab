#!/usr/bin/env python3
"""ULSH-01 / WP2-RR3 independent H2 release-readiness review, strictly no-solve.

The reviewer performs source/contract inspection with Python stdlib only. It
never imports NumPy, SciPy, either numerical backend, the target execution
module, or the physical transaction execute path.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_RR3Review_v1.0.json"
H2_CONTRACT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_H2Contract_v1.0.json"
H2_TARGET_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.2.py"
H2_TX_BASE_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.2.py"
H2_TX_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.3.py"
H1_TARGET_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.1.py"
H1_TX_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.1.py"
RESULT_SCHEMA_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResultSchema_v0.1.json"
PREREG_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"
RELEASE_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.2.json"
GRANT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.2.json"

EXPECTED_BLOBS = {
    "h2_contract": "213cf0c67bb057835d8e680b4199393b2fe6b6cf",
    "h2_target": "db2f4a0ea1ac374209e52b21fdc72de23e5f419d",
    "h2_transaction_base": "65a752b82a748aa8c73a322b7bdfd332951b47b2",
    "h2_transaction_supervisor": "bc8aa30d689997dd4002f9c4559885bcb0a56807",
    "h1_target": "304592405f843822e142110ba6a65fc845579489",
    "h1_transaction": "a181056cb93b69c0c6c436a05b2bea838de25bda",
    "result_schema": "b1fdf45aa9fb3d585e73795e9294dfa0c185fc39",
    "preregistration": "9789101e0a168580b6906eb21edad5a5db2b64ce",
}


class RR3ReviewFailure(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RR3ReviewFailure(f"top-level object required: {path}")
    return value


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def verify_review_basis() -> dict[str, str]:
    paths = {
        "h2_contract": H2_CONTRACT_PATH,
        "h2_target": H2_TARGET_PATH,
        "h2_transaction_base": H2_TX_BASE_PATH,
        "h2_transaction_supervisor": H2_TX_PATH,
        "h1_target": H1_TARGET_PATH,
        "h1_transaction": H1_TX_PATH,
        "result_schema": RESULT_SCHEMA_PATH,
        "preregistration": PREREG_PATH,
    }
    observed = {key: git_blob_sha1(path) for key, path in paths.items()}
    if observed != EXPECTED_BLOBS:
        raise RR3ReviewFailure(f"RR3 review basis drift: {observed}")
    return observed


def verify_h2_rr2_closures(h2_target: str, tx_base: str, tx: str, contract: dict[str, Any]) -> dict[str, bool]:
    closure = contract.get("rr2_blocker_closure", {})
    execute_marker = "def execute(transaction_root"
    if execute_marker not in tx:
        raise RR3ReviewFailure("cannot locate H2 transaction execute function")
    body = tx[tx.index(execute_marker):]
    checks = {
        "RR2-B01_pre_solver_output_collision": (
            set(closure) == {"RR2-B01", "RR2-B02", "RR2-B03", "RR2-B04"}
            and "pre_solver_output_collision_guard" in body
            and body.index("pre_solver_output_collision_guard") < body.index("strict_startup_environment")
            and body.index("pre_solver_output_collision_guard") < body.index("claim_single_use_grant")
        ),
        "RR2-B02_fail_closed_one_thread": (
            'if value != "1"' in tx_base
            and "effective_blas_thread_attestation" in tx
            and "reported_threads" in tx
            and 'runtime["effective_blas_threads"] = effective_blas_thread_attestation()' in body
            and body.index('runtime["effective_blas_threads"] = effective_blas_thread_attestation()') < body.index("claim_single_use_grant")
        ),
        "RR2-B03_continuous_total_deadline": (
            "def total_transaction_wall_clock_limit" in tx
            and "with total_transaction_wall_clock_limit" in body
            and body.index("with total_transaction_wall_clock_limit") < body.index("supervised_target_execution")
            and body.index("with total_transaction_wall_clock_limit") < body.index("package_schema_complete_result")
            and body.index("with total_transaction_wall_clock_limit") < body.index("os.replace(staging, result_dir)")
        ),
        "RR2-B04_high_precision_gate": (
            "ALL_OTHERWISE_PASSING_CANDIDATES" in h2_target
            and "np.longdouble" in h2_target
            and "mantissa_bits < 64" in h2_target
            and "pi = np.arccos(np.longdouble(-1))" in h2_target
            and 'candidate["classification"] = REJECT_CLASS' in h2_target
        ),
    }
    if not all(checks.values()):
        raise RR3ReviewFailure(f"one or more H2 RR2 closures are not independently reproducible: {checks}")
    return checks


def identify_new_release_blockers(h1_target: str, h1_tx: str, h2_tx: str, prereg: dict[str, Any]) -> dict[str, bool]:
    # RR3-B01: valid negative/partial outcome paths use +/- infinity sentinels,
    # while immutable JSON serialization is strict allow_nan=False. A no-candidate
    # or partial-seed run can therefore fail during result packaging instead of
    # producing its preregistered machine-readable classification.
    strict_json_rejects_inf = False
    try:
        json.dumps({"sentinel": math.inf}, allow_nan=False)
    except ValueError:
        strict_json_rejects_inf = True
    sentinel_markers = (
        'pair_values[key] = {"profile": math.inf, "augmented": math.inf}',
        "independent_distance = math.inf",
        "Y_sigma = float(model.z_sigma_hat) * d_chi**2 / ell_sigma**2 if ell_sigma > 0.0 else -math.inf",
    )
    b01 = (
        strict_json_rejects_inf
        and all(marker in h1_target for marker in sentinel_markers)
        and "allow_nan=False" in h1_tx
        and '"NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL"' in prereg["predeclared_result_classes"].values()
    )

    # RR3-B02: the hard total SIGALRM remains active during atomic staging->result
    # rename, but SUCCEEDED is recorded only after the timer context exits. If the
    # signal is delivered immediately after a successful rename, the exception
    # branch hardcodes result_package_committed=false and FAILED without checking
    # result_dir. That permits an immutable committed result and a contradictory
    # failed grant ledger.
    execute_marker = "def execute(transaction_root"
    body = h2_tx[h2_tx.index(execute_marker):]
    b02 = (
        "with total_transaction_wall_clock_limit" in body
        and body.index("with total_transaction_wall_clock_limit") < body.index("os.replace(staging, result_dir)")
        and body.index("os.replace(staging, result_dir)") < body.index('UTILS.mark_state(grant_dir, "SUCCEEDED"')
        and '"result_package_committed": False' in body
        and 'UTILS.mark_state(grant_dir, "FAILED"' in body
        and "result_dir.exists()" not in body[body.index("except BaseException as exc:"):]
    )

    findings = {"RR3-B01": b01, "RR3-B02": b02}
    if not all(findings.values()):
        raise RR3ReviewFailure(f"expected RR3 blockers are not reproducible: {findings}")
    return findings


def audit() -> dict[str, Any]:
    review = load_json(REVIEW_PATH)
    contract = load_json(H2_CONTRACT_PATH)
    prereg = load_json(PREREG_PATH)
    h2_target = H2_TARGET_PATH.read_text(encoding="utf-8")
    tx_base = H2_TX_BASE_PATH.read_text(encoding="utf-8")
    tx = H2_TX_PATH.read_text(encoding="utf-8")
    h1_target = H1_TARGET_PATH.read_text(encoding="utf-8")
    h1_tx = H1_TX_PATH.read_text(encoding="utf-8")

    if review.get("review_status") != "BLOCKED_WP2_RR3_NEW_RELEASE_BLOCKERS_FOUND_NO_SOLVE":
        raise RR3ReviewFailure("RR3 review status drift")
    if contract.get("status") != "PASS_WP2_H2_IMPLEMENTED_NO_SOLVE_PENDING_RR3":
        raise RR3ReviewFailure("RR3 is not reviewing the expected H2 state")
    if RELEASE_PATH.exists() or GRANT_PATH.exists():
        raise RR3ReviewFailure("release/grant must remain absent during RR3")
    basis = verify_review_basis()
    closures = verify_h2_rr2_closures(h2_target, tx_base, tx, contract)
    blockers = identify_new_release_blockers(h1_target, h1_tx, tx, prereg)
    return {
        "status": "PASS_RR3_REVIEW_REPRODUCED_BLOCKED_NO_SOLVE",
        "review_status": review["review_status"],
        "h2_rr2_closures_verified": closures,
        "new_release_blockers_reproduced": blockers,
        "reviewed_source_git_blob_sha1": basis,
        "release_authorization_present": False,
        "single_use_grant_present": False,
        "numerical_backend_imported": False,
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
