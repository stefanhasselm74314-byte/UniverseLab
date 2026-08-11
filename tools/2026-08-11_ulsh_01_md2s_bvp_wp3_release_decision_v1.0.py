#!/usr/bin/env python3
"""ULSH-01 / WP3 CP01R1 release-decision auditor.

Stdlib-only. This tool decides whether the frozen H3 transaction is eligible for
later exact single-use release/grant issuance. It never creates either artifact,
imports numerical backends, or executes CP01R1.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP3_CP01R1ReleaseDecision_v1.0.json"
RR4_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_RR4Review_v1.0.json"
H3_CONTRACT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_H3Contract_v1.0.json"
H3_TX_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.4.py"
RELEASE_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.3.json"
GRANT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.3.json"

RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
FROZEN_PAYLOAD_SHA256 = "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302"
EXPECTED_RR4_BLOB = "7d69a7187962f2b5be817d10dc9b2dac0d099b05"
EXPECTED_H3_CONTRACT_BLOB = "a09067d749493fa14c61fc8a7678ca353a005566"
EXPECTED_H3_TX_BLOB = "2dd09d9ade6d6ae69c1949833e88b2af49c13710"
EXPECTED_SOURCE_BUNDLE_SHA256 = "022b1ede18d217c3278445ea1cfd65fad475d28a6ebaa7327cc9c46904c877cd"


class ReleaseDecisionFailure(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReleaseDecisionFailure(f"top-level JSON object required: {path}")
    return value


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_bundle_sha256(contract: dict[str, Any]) -> str:
    bindings = contract.get("source_bindings")
    if not isinstance(bindings, dict):
        raise ReleaseDecisionFailure("H3 contract source_bindings missing")
    material: list[dict[str, str]] = []
    for key in sorted(bindings):
        binding = bindings[key]
        path = ROOT / binding["path"]
        observed = git_blob_sha1(path)
        expected = binding["git_blob_sha1"]
        if observed != expected:
            raise ReleaseDecisionFailure(f"source drift for {key}: observed={observed} expected={expected}")
        material.append({"key": key, "path": binding["path"], "git_blob_sha1": observed})
    canonical = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def audit() -> dict[str, Any]:
    decision = load_json(DECISION_PATH)
    rr4 = load_json(RR4_PATH)
    h3 = load_json(H3_CONTRACT_PATH)
    h3_source = H3_TX_PATH.read_text(encoding="utf-8")

    observed_blobs = {
        "rr4": git_blob_sha1(RR4_PATH),
        "h3_contract": git_blob_sha1(H3_CONTRACT_PATH),
        "h3_transaction": git_blob_sha1(H3_TX_PATH),
    }
    expected_blobs = {
        "rr4": EXPECTED_RR4_BLOB,
        "h3_contract": EXPECTED_H3_CONTRACT_BLOB,
        "h3_transaction": EXPECTED_H3_TX_BLOB,
    }
    if observed_blobs != expected_blobs:
        raise ReleaseDecisionFailure(f"review basis drift: {observed_blobs}")

    if rr4.get("review_status") != "PASS_WP2_RR4_H3_RELEASE_READINESS_VERIFIED_NO_SOLVE":
        raise ReleaseDecisionFailure("RR4 is not a release-readiness PASS")
    if rr4.get("new_release_blockers") != {}:
        raise ReleaseDecisionFailure("RR4 contains release blockers")
    if rr4.get("wp2_completion", {}).get("status") != "CLOSED_RELEASE_READY_NO_EXECUTION":
        raise ReleaseDecisionFailure("WP2 is not closed release-ready")
    if rr4.get("next_allowed_action") != "ULSH-01_WP3_SEPARATE_CP01R1_SINGLE_USE_RELEASE_DECISION":
        raise ReleaseDecisionFailure("RR4 next-action contract drift")

    if h3.get("run_id") != RUN_ID or h3.get("frozen_payload_sha256") != FROZEN_PAYLOAD_SHA256:
        raise ReleaseDecisionFailure("H3 run/payload binding drift")
    if h3.get("physical_solve_authorized") is not False or h3.get("physical_solve_executed") is not False:
        raise ReleaseDecisionFailure("H3 basis unexpectedly authorizes or records solve")
    protocol = h3.get("grant_protocol", {})
    if protocol.get("maximum_validity_seconds") != 3600:
        raise ReleaseDecisionFailure("H3 grant validity window drift")
    if protocol.get("single_use") is not True or protocol.get("replay_allowed") is not False:
        raise ReleaseDecisionFailure("H3 single-use/replay contract drift")

    bundle_sha = source_bundle_sha256(h3)
    if bundle_sha != EXPECTED_SOURCE_BUNDLE_SHA256:
        raise ReleaseDecisionFailure(f"H3 source bundle digest drift: {bundle_sha}")

    scope = decision.get("frozen_execution_scope", {})
    if scope.get("seed_count") != 7 or scope.get("node_counts") != [24, 32, 48, 64, 96] or scope.get("planned_primary_entries") != 35:
        raise ReleaseDecisionFailure("WP3 release decision schedule drift")
    if scope.get("target_a_F") != "1/4":
        raise ReleaseDecisionFailure("WP3 target a_F drift")
    for key in ("parameter_mutation_allowed", "topology_mutation_allowed", "random_restart_allowed", "adaptive_mesh_insertion_allowed", "surrogate_or_control_fallback_allowed"):
        if scope.get(key) is not False:
            raise ReleaseDecisionFailure(f"forbidden execution mutation enabled: {key}")

    release_decision = decision.get("release_decision", {})
    if release_decision.get("eligible_to_issue_exact_h3_release_authorization") is not True:
        raise ReleaseDecisionFailure("release authorization issuance not approved")
    if release_decision.get("eligible_to_issue_exact_h3_single_use_grant") is not True:
        raise ReleaseDecisionFailure("single-use grant issuance not approved")
    if release_decision.get("release_authorization_created_by_this_decision") is not False or release_decision.get("single_use_grant_created_by_this_decision") is not False:
        raise ReleaseDecisionFailure("decision improperly claims issuance")

    if RELEASE_PATH.exists() or GRANT_PATH.exists():
        raise ReleaseDecisionFailure("WP3 decision phase must not contain release/grant artifacts")

    boundary = decision.get("decision_boundary", {})
    if boundary.get("physical_solve_authorized") is not False or boundary.get("physical_solve_executed") is not False:
        raise ReleaseDecisionFailure("decision boundary improperly authorizes/records solve")
    if boundary.get("K1-D") != "NOT_RELEASED" or boundary.get("K1-E") != "NOT_ADMISSIBLE" or boundary.get("physical_evidence_effect") != "NONE":
        raise ReleaseDecisionFailure("scientific firewall drift")

    required_source_tokens = (
        "validate_h3_release_and_grant",
        "source_bundle_sha256",
        "planned_entry_count",
        "single_use",
        "no_retry",
        "no_scan",
        "no_fallback",
        "NONCE_RE.fullmatch",
        "maximum_validity_seconds",
        "H2.static_preflight()",
    )
    missing = [token for token in required_source_tokens if token not in h3_source]
    if missing:
        raise ReleaseDecisionFailure(f"H3 exact-release enforcement source tokens missing: {missing}")

    return {
        "status": "PASS_WP3_CP01R1_RELEASE_DECISION_ELIGIBLE_NO_GRANT_NO_SOLVE",
        "decision_status": decision["decision_status"],
        "reviewed_main_commit": decision["reviewed_main_commit"],
        "run_id": RUN_ID,
        "frozen_payload_sha256": FROZEN_PAYLOAD_SHA256,
        "h3_source_bundle_sha256": bundle_sha,
        "schedule": {"seed_count": 7, "node_counts": [24, 32, 48, 64, 96], "planned_entries": 35},
        "release_authorization_present": False,
        "single_use_grant_present": False,
        "solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "CP01R1": "NOT_EXECUTED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
        "next_allowed_action": decision["next_allowed_action"],
    }


def main() -> int:
    print(json.dumps(audit(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
