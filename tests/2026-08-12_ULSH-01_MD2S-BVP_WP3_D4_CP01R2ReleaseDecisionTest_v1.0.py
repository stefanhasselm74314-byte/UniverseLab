#!/usr/bin/env python3
"""Regression tests for ULSH-01 / WP3-D4 CP01R2 release decision.

No physical target or numerical backend is imported or executed.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d4_cp01r2_release_decision_v1.0.py"
DECISION_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D4_CP01R2ReleaseDecision_v1.0.json"
RELEASE_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2_PhysicalSolveReleaseAuthorization_v1.0.json"
GRANT_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2_SingleUseExecutionGrant_v1.0.json"

SPEC = importlib.util.spec_from_file_location("wp3_d4_release_decision", TOOL_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import D4 release-decision auditor")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
    audit = MOD.audit()

    require(audit["status"] == "PASS_WP3_D4_CP01R2_SINGLE_USE_RELEASE_AUTHORIZED_NO_EXECUTION", "audit did not pass")
    require(audit["predecessor_blob_bindings_verified"] == 8, "unexpected predecessor binding count")
    require(audit["rr1_review_gates"] == "8/8_PASS", "RR1 gate closure missing")
    require(audit["d3_blockers"] == {"D3-B01": "VERIFIED_CLOSED", "D3-B02": "VERIFIED_CLOSED"}, "D3 blockers not closed")

    d = decision["decision"]
    require(d["release_physical_solve"] is True, "release decision must be positive")
    require(d["authorization_scope"] == "SINGLE_USE_CP01R2_ONLY", "release scope is not CP01R2-only")
    require(d["execution_in_this_work_package"] is False, "D4 must not execute")
    require(d["execution_requires_fresh_single_use_grant"] is True, "fresh grant requirement missing")
    require(d["grant_must_bind_exactly_to_this_decision_id"] is True, "decision binding missing")
    require(d["grant_must_bind_exactly_to_authorization_decision_id"] is True, "authorization binding missing")
    require(d["grant_validity_seconds"] == 3600, "grant validity changed")
    require(d["grant_nonce_requirement"] == "128-256_BIT_LOWERCASE_HEX", "nonce requirement changed")
    require(d["grant_replay_permitted"] is False, "grant replay enabled")

    auth = decision["single_use_authorization_template"]
    grant = decision["single_use_execution_grant_template"]
    require(auth["issued"] is False, "D4 must not issue authorization artifact")
    require(grant["issued"] is False, "D4 must not issue grant")
    require(grant["grant_nonce"] is None and grant["issued_utc"] is None and grant["expires_utc"] is None, "D4 must not materialize grant state")
    require(not RELEASE_PATH.exists(), "release authorization artifact exists during D4")
    require(not GRANT_PATH.exists(), "single-use grant artifact exists during D4")

    firewall = decision["no_execution_firewall"]
    require(firewall["physical_solve_authorized_by_runtime_artifact"] is False, "runtime authorization changed")
    require(firewall["physical_solve_executed"] is False, "physical solve executed")
    require(firewall["result_directory_created_by_d4"] is False, "D4 created result directory")
    require(firewall["audit_solver_calls"] == 0, "solver call occurred")
    require(firewall["physical_evidence_effect"] == "NONE", "physical evidence status changed")

    governance = decision["governance_after_decision"]
    require(governance["WP3"] == "RELEASE_DECIDED_SINGLE_USE_CP01R2_EXECUTION_PENDING", "WP3 state mismatch")
    require(governance["WP4"] == "BLOCKED", "WP4 must remain blocked")
    require(governance["K1-D"] == "NOT_RELEASED", "K1-D changed")
    require(governance["K1-E"] == "NOT_ADMISSIBLE", "K1-E changed")
    require(governance["physical_evidence_effect"] == "NONE", "governance evidence status changed")

    print("PASS_WP3_D4_CP01R2_RELEASE_DECISION_TEST_NO_EXECUTION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
