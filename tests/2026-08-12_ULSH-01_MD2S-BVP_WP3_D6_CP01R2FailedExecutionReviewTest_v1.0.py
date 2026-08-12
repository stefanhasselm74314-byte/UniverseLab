#!/usr/bin/env python3
"""Regression test for ULSH-01 / WP3-D6 failed CP01R2 execution review."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d6_cp01r2_failed_execution_review_v1.0.py"
REVIEW = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6_CP01R2FailedExecutionReview_v1.0.json"

SPEC = importlib.util.spec_from_file_location("wp3_d6_failed_review", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load D6 review audit")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    result = MOD.audit()

    require(result["status"] == "BLOCKED_WP3_D6_CP01R2_RESULT_REVIEW_FINALIZATION_DEFECT_NO_REPLAY", "D6 audit status mismatch")
    require(result["exact_source_blobs_verified"] == 7, "source-binding count mismatch")
    require(result["grant"] == "SPENT_NON_REPLAYABLE", "spent-grant firewall missing")
    require(result["result_package"] == "NOT_COMMITTED", "result package must remain not committed")
    require(result["control_flow_35_entries"] == "REACHED_FINALIZER_NOT_DURABLY_PRESERVED", "control-flow classification mismatch")
    require(result["numerical_outcome"] == "INDETERMINATE_UNPRESERVED", "numerical outcome must remain indeterminate")
    require(result["release_blockers"] == ["D6-B01", "D6-B02"], "D6 blocker set mismatch")
    require(result["solver_calls_by_review"] == 0, "D6 review must not execute solver")
    require(result["physical_evidence_effect"] == "NONE", "D6 review cannot change physical evidence")

    findings = review["control_flow_findings"]
    require(findings["at_least_one_n96_terminal_state_without_local_root"] is True, "required N96 non-root inference missing")
    require(findings["candidate_count_recoverable"] is False, "candidate count must not be claimed recoverable")
    require(findings["residual_matrix_recoverable"] is False, "residual matrix must not be claimed recoverable")
    require(findings["independent_backend_records_recoverable"] is False, "independent-backend record must not be claimed recoverable")

    governance = review["grant_and_governance_disposition"]
    require(governance["d4_single_use_execution_permission_consumed"] is True, "D4 single-use permission consumption missing")
    require(governance["fresh_execution_grant_permitted_now"] is False, "fresh grant must remain forbidden")
    require(governance["WP4"] == "BLOCKED", "WP4 must remain blocked")
    require(governance["K1-D"] == "NOT_RELEASED", "K1-D changed")
    require(governance["K1-E"] == "NOT_ADMISSIBLE", "K1-E changed")

    print("PASS_WP3_D6_CP01R2_FAILED_EXECUTION_REVIEW_TEST_NO_RERUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
