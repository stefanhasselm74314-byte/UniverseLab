#!/usr/bin/env python3
"""ULSH-01 / WP3-D4 CP01R2 single-use release decision audit.

This tool performs governance/source-binding checks only. It MUST NOT import or
invoke the physical target, transaction supervisor, NumPy/SciPy, or any solver.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D4_CP01R2ReleaseDecision_v1.0.json"
EXPECTED_STATUS = "PASS_WP3_D4_CP01R2_SINGLE_USE_RELEASE_AUTHORIZED_NO_EXECUTION"
EXPECTED_DECISION_ID = "ULSH-01-WP3-D4-CP01R2-RELEASE-DEC-20260812-A"
EXPECTED_RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2"
EXPECTED_PAYLOAD_SHA256 = "e8b8e82d2cb1472d91c387a40c8f84024c2549a3dcc2c897df5561f7bf721b36"
EXPECTED_SCHEDULE_SHA256 = "929f59d018cc511f36c98ef26a8614ed495fe699a067b1b33e6c5b53efaf8e0b"
EXPECTED_DEPENDENCY_SHA256 = "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f"
EXPECTED_BASELINE = "39c285f893c0c119fc5bc16d1966a5d9e7d7d2b9"

PREDECESSOR_BLOBS = {
    "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D2_CP01R2IndependentProtocolReview_v1.0.json": "2734b120ffa9a481a092f87190605df24d02bcb0",
    "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3_CP01R2RunInputFreeze_v1.0.json": "471f40a517140cc2a2d609f4828fd1004c4861e2",
    "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3_CP01R2PhysicalBindingReleaseReadinessReview_v1.0.json": "2e311f00d91dbd918401251052ba67bd23ab384a",
    "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2TransactionHardeningContract_v1.0.json": "ebe9193b6da50f6f352ac5397749d9caaceaf047",
    "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_RR1_IndependentReview_v1.0.json": "e240cb9b7fb4990575a99c3f436640b7fd91cb8b",
    "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2ResultSchema_v1.0.json": "54bf49acdfcca128e3b909d6e479b1178c77c276",
    "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3h1_cp01r2_target_v1.0.py": "199815ac9e4014cc0d68fde71d634cdac24516ce",
    "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3h1_cp01r2_transaction_v1.1.py": "07d1532be17e5d5d81c96ad4438c3195ca4653aa",
}

FUTURE_RELEASE = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2_PhysicalSolveReleaseAuthorization_v1.0.json"
FUTURE_GRANT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2_SingleUseExecutionGrant_v1.0.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha1(relative_path: str) -> str:
    completed = subprocess.run(
        ["git", "hash-object", relative_path],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def document_status(doc: dict[str, Any]) -> str | None:
    return doc.get("status") or doc.get("review_status")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def audit() -> dict[str, Any]:
    decision = load_json(DECISION_PATH)

    require(decision["status"] == EXPECTED_STATUS, "D4 decision status mismatch")
    require(decision["decision_id"] == EXPECTED_DECISION_ID, "D4 decision id mismatch")
    require(decision["baseline_main_commit"] == EXPECTED_BASELINE, "baseline commit mismatch")
    require(decision["run_id"] == EXPECTED_RUN_ID, "run id mismatch")
    require(decision["run_payload_sha256"] == EXPECTED_PAYLOAD_SHA256, "payload hash mismatch")
    require(decision["schedule_sha256"] == EXPECTED_SCHEDULE_SHA256, "schedule hash mismatch")
    require(decision["dependency_lock_sha256"] == EXPECTED_DEPENDENCY_SHA256, "dependency hash mismatch")

    subprocess.run(
        ["git", "cat-file", "-e", f"{EXPECTED_BASELINE}^{{commit}}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )

    observed_blobs: dict[str, str] = {}
    for relative_path, expected_blob in PREDECESSOR_BLOBS.items():
        actual = git_blob_sha1(relative_path)
        require(actual == expected_blob, f"source drift: {relative_path}: {actual} != {expected_blob}")
        observed_blobs[relative_path] = actual

    d2 = load_json(ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D2_CP01R2IndependentProtocolReview_v1.0.json")
    require(d2.get("review_status") == "PASS_WP3_D2_INDEPENDENT_PROTOCOL_REVIEW_NO_EXECUTION", "D2 independent protocol review is not PASS")
    require(all(v == "PASS" for v in d2.get("review_gates", {}).values()), "D2 review gates are not all PASS")

    d3_freeze = load_json(ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3_CP01R2RunInputFreeze_v1.0.json")
    require(d3_freeze.get("status") == "FROZEN_CP01R2_NOT_AUTHORIZED_NOT_EXECUTED", "D3 run input is not frozen")
    frozen = d3_freeze.get("frozen_run_payload", {})
    require(frozen.get("run_id") == EXPECTED_RUN_ID, "D3 frozen run id mismatch")
    require(d3_freeze.get("frozen_run_payload_sha256") == EXPECTED_PAYLOAD_SHA256, "D3 frozen payload hash mismatch")
    require(d3_freeze.get("schedule_sha256") == EXPECTED_SCHEDULE_SHA256, "D3 frozen schedule hash mismatch")
    identity = d3_freeze.get("physical_identity_check", {})
    require(identity and all(identity.values()), "D3 physical-identity freeze has a failed invariant")

    d3_review = load_json(ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3_CP01R2PhysicalBindingReleaseReadinessReview_v1.0.json")
    require(d3_review.get("physical_target_binding_status") == "PASS_SOURCE_CONTRACT_BOUND_NO_EXECUTION", "D3 physical target binding did not pass")
    require(d3_review.get("release_readiness_status") == "BLOCKED_CP01R2_TRANSACTION_SUPERVISOR_AND_IMMUTABLE_RESULT_CLOSURE_NOT_YET_REBOUND", "D3 historical readiness blocker state drifted")
    d3_gates = d3_review.get("review_gates", {})
    require(d3_gates.get("D3-RB09_EXACT_CP01R2_TRANSACTION_SUPERVISOR_BINDING") == "BLOCKED", "D3 historical B01 gate mismatch")
    require(d3_gates.get("D3-RB10_CP01R2_IMMUTABLE_RESULT_COMMIT_AND_ARTIFACT_CLOSURE") == "BLOCKED", "D3 historical B02 gate mismatch")

    h1 = load_json(ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2TransactionHardeningContract_v1.0.json")
    require(document_status(h1) == "PASS_D3H1_IMPLEMENTED_NO_EXECUTION_PENDING_INDEPENDENT_REVIEW", "D3H1 hardening status mismatch")

    rr1 = load_json(ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_RR1_IndependentReview_v1.0.json")
    require(rr1.get("review_status") == "PASS_WP3_D3H1_RR1_D3_BLOCKERS_VERIFIED_CLOSED_NO_EXECUTION", "D3H1 RR1 is not PASS")
    require(rr1.get("new_release_blockers") == [], "RR1 has unresolved/new release blockers")
    disposition = rr1.get("D3_blocker_disposition", {})
    require(disposition.get("D3-B01", {}).get("status") == "VERIFIED_CLOSED", "D3-B01 not independently closed")
    require(disposition.get("D3-B02", {}).get("status") == "VERIFIED_CLOSED", "D3-B02 not independently closed")
    gates = rr1.get("review_gates", {})
    require(len(gates) == 8 and all(v == "PASS" for v in gates.values()), "RR1 review gates are not 8/8 PASS")

    d = decision["decision"]
    require(d["release_physical_solve"] is True, "single-use release decision is not positive")
    require(d["authorization_scope"] == "SINGLE_USE_CP01R2_ONLY", "authorization scope mismatch")
    require(d["execution_in_this_work_package"] is False, "D4 must remain no-execution")
    require(d["execution_requires_fresh_single_use_grant"] is True, "fresh grant requirement missing")
    require(d["grant_validity_seconds"] == 3600, "grant validity mismatch")
    require(d["grant_replay_permitted"] is False, "grant replay must remain forbidden")
    for key in (
        "parallel_execution",
        "adaptive_retry",
        "parameter_or_topology_mutation",
        "method_or_threshold_relaxation",
        "branch_scan",
        "fallback_method",
    ):
        require(d[key] is False, f"forbidden D4 capability enabled: {key}")

    firewall = decision["no_execution_firewall"]
    require(firewall["release_authorization_artifact_present"] is False, "release artifact unexpectedly marked present")
    require(firewall["single_use_grant_artifact_present"] is False, "grant unexpectedly marked present")
    require(firewall["physical_solve_authorized_by_runtime_artifact"] is False, "runtime authorization must remain false")
    require(firewall["physical_solve_executed"] is False, "D4 executed a physical solve")
    require(firewall["audit_solver_calls"] == 0, "D4 solver call count must be zero")
    require(firewall["physical_evidence_effect"] == "NONE", "D4 cannot create physical evidence")

    require(not FUTURE_RELEASE.exists(), "future release authorization already exists; D4 firewall violated")
    require(not FUTURE_GRANT.exists(), "future single-use grant already exists; D4 firewall violated")

    governance = decision["governance_after_decision"]
    require(governance["WP4"] == "BLOCKED", "WP4 advanced during D4")
    require(governance["K1-D"] == "NOT_RELEASED", "K1-D advanced during D4")
    require(governance["K1-E"] == "NOT_ADMISSIBLE", "K1-E advanced during D4")
    require(governance["physical_evidence_effect"] == "NONE", "physical evidence status changed during D4")

    return {
        "status": EXPECTED_STATUS,
        "decision_id": EXPECTED_DECISION_ID,
        "run_id": EXPECTED_RUN_ID,
        "predecessor_blob_bindings_verified": len(observed_blobs),
        "d2_review": "PASS",
        "d3_run_input": "FROZEN",
        "d3_historical_blockers": "PRESERVED_AS_REVIEW_PROVENANCE",
        "rr1_review_gates": "8/8_PASS",
        "d3_blockers": {"D3-B01": "VERIFIED_CLOSED", "D3-B02": "VERIFIED_CLOSED"},
        "release_authorization_present": False,
        "single_use_grant_present": False,
        "physical_solve_executed": False,
        "audit_solver_calls": 0,
        "physical_evidence_effect": "NONE",
        "next_allowed_action": decision["next_allowed_action"],
    }


def main() -> int:
    try:
        result = audit()
    except Exception as exc:  # governance audit must fail closed
        print(json.dumps({"status": "BLOCKED_WP3_D4_CP01R2_RELEASE_DECISION_AUDIT", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
