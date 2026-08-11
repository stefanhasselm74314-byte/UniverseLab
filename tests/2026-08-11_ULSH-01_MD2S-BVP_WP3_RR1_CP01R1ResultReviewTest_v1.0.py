#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP3_RR1_CP01R1ResultReview_v1.0.json"


def main() -> int:
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    assert review["review_status"] == "PASS_TRANSACTION_COMPLETE_NEGATIVE_NUMERICAL_OUTCOME_NO_CANDIDATE_UNDER_PREREGISTERED_PROTOCOL"
    assert review["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
    assert review["workflow_run"]["id"] == 31495350499
    assert review["workflow_run"]["attempt"] == 1
    assert review["workflow_run"]["workflow_conclusion"] == "success"
    assert review["grant_state"]["grant_spent"] is True
    assert review["grant_state"]["replay_permitted"] is False
    execution = review["execution_summary"]
    assert execution["planned_entries"] == execution["completed_entries"] == 35
    assert execution["stage_timeout_count"] == 0
    assert execution["total_budget_exhausted"] is False
    assert execution["candidate_count"] == 0
    assert execution["final_classification"] == "NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL"
    assert execution["independent_backend_candidate_comparisons"] == 0
    assert execution["higher_precision_candidate_audits"] == 0
    failures = review["failure_inventory"]
    assert sum(failures.values()) == 35
    assert failures == {"MAXIMUM_ITERATIONS": 30, "TRUST_RADIUS_BELOW_MINIMUM": 4, "RRQR_RANK_DEFICIENT": 1}
    n96 = review["n96_review"]
    assert n96["n96_local_root_count"] == 0
    assert n96["dominant_boundary_residual_all_seeds"] == "R_4D"
    assert min(n96["R_4D_abs_range"]) > 1.0
    assert min(n96["bulk_residual_max_range"]) > 1e-3
    assert min(n96["rr_constraint_max_range"]) > 1e-3
    assert review["gate_comparison"]["fine_mesh_gate_reached"] is False
    assert review["gate_comparison"]["independent_backend_gate_reached"] is False
    governance = review["governance_state"]
    assert governance["WP3"].startswith("NOT_CLOSED")
    assert governance["WP4"].startswith("BLOCKED")
    assert governance["K1-D"] == "NOT_RELEASED"
    assert governance["K1-E"] == "NOT_ADMISSIBLE"
    assert governance["physical_evidence_effect"] == "NONE"
    forbidden = set(review["forbidden_next_actions"])
    assert "DO_NOT_RERUN_CP01R1_WITH_THE_SPENT_GRANT" in forbidden
    assert "DO_NOT_TREAT_NO_CANDIDATE_AS_CONTINUUM_NONEXISTENCE_OR_MODEL_FALSIFICATION" in forbidden
    print("PASS_WP3_RR1_CP01R1_RESULT_REVIEW_NO_RERUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
