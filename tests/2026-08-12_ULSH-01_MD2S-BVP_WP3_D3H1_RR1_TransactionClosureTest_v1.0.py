#!/usr/bin/env python3
"""Regression test for ULSH-01 WP3-D3H1-RR1, strictly no physical execution."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REVIEW_TOOL = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3h1_rr1_review_v1.0.py"
REVIEW_JSON = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_RR1_IndependentReview_v1.0.json"
CONTRACT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2TransactionHardeningContract_v1.0.json"
SCHEMA = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2ResultSchema_v1.0.json"

spec = importlib.util.spec_from_file_location("ulsh_d3h1_rr1_test_review", REVIEW_TOOL)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

result = module.review()
assert result["status"] == "PASS_WP3_D3H1_RR1_D3_BLOCKERS_VERIFIED_CLOSED_NO_EXECUTION"
assert result["D3-B01"] == "VERIFIED_CLOSED"
assert result["D3-B02"] == "VERIFIED_CLOSED"
assert result["new_release_blockers"] == []
assert result["synthetic_result_package"] == "PASS"
assert result["synthetic_replay_denial"] == "PASS"
assert result["synthetic_collision_guard"] == "PASS"
assert result["solver_calls"] == 0
assert result["physical_solve_authorized"] is False
assert result["physical_solve_executed"] is False
assert result["physical_evidence_effect"] == "NONE"
assert result["K1-D"] == "NOT_RELEASED"
assert result["K1-E"] == "NOT_ADMISSIBLE"
assert result["WP4"] == "BLOCKED"

review = json.loads(REVIEW_JSON.read_text(encoding="utf-8"))
contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
assert review["review_status"] == result["status"]
assert review["D3_blocker_disposition"]["D3-B01"]["status"] == "VERIFIED_CLOSED"
assert review["D3_blocker_disposition"]["D3-B02"]["status"] == "VERIFIED_CLOSED"
assert review["new_release_blockers"] == []
assert review["governance"]["release_authorization_present"] is False
assert review["governance"]["single_use_grant_present"] is False
assert review["governance"]["physical_solve_executed"] is False
assert review["next_allowed_action"] == "ULSH-01_WP3_D4_CP01R2_SINGLE_USE_RELEASE_DECISION_NO_EXECUTION"
assert contract["next_if_independent_review_passes"] == review["next_allowed_action"]
assert contract["D3_blocker_closure_claims"]["D3-B01"] == "IMPLEMENTED_PENDING_INDEPENDENT_REVIEW"
assert contract["D3_blocker_closure_claims"]["D3-B02"] == "IMPLEMENTED_PENDING_INDEPENDENT_REVIEW"
assert set(schema["cp01r2_etrn01_required_fields"]) == {
    "raw_rank_condition_history",
    "scaled_rank_condition_history",
    "trust_radius_rho_history",
    "progress_continuation_provenance",
}

# The no-execution repository state must contain no future release/grant artifacts.
assert not list(ROOT.glob("registry/*CP01R2*PhysicalSolveReleaseAuthorization*.json"))
assert not list(ROOT.glob("registry/*CP01R2*SingleUseExecutionGrant*.json"))

print("PASS_WP3_D3H1_RR1_TRANSACTION_RESULT_CLOSURE_TEST_NO_EXECUTION")
