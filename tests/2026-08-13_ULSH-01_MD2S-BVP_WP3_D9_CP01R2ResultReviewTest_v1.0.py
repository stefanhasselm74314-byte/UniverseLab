#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "registry/2026-08-13_ULSH-01_MD2S-BVP_WP3_D9_CP01R2ResultReview_v1.0.json"
D8_TRIGGER = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D8_CP01R2ImmediateExecutionTrigger_v2.0.json"
CP01R1_REVIEW = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP3_RR1_CP01R1ResultReview_v1.0.json"


def main() -> int:
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    assert review["classification"] == "INDEPENDENT_POST_EXECUTION_RESULT_REVIEW_NO_RERUN"
    assert review["review_status"] == "PASS_TRANSACTION_COMPLETE_NEGATIVE_NUMERICAL_OUTCOME_NO_CANDIDATE_UNDER_PREREGISTERED_CP01R2_PROTOCOL"
    assert review["reviewed_main_commit"] == "e718cff2613a00810f9edb6183e5fccd413370f9"
    assert review["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2"

    workflow = review["workflow_run"]
    assert workflow["id"] == 31595841858
    assert workflow["attempt"] == 1
    assert workflow["job_id"] == 94111018415
    assert workflow["workflow_conclusion"] == "success"
    assert workflow["transaction_step_conclusion"] == "success"
    assert workflow["artifact_preservation_conclusion"] == "success"

    artifact = review["artifact_binding"]
    assert artifact["artifact_id"] == 9141488748
    assert artifact["artifact_zip_sha256"] == "57548e8352b128a084d356b0f61ac1055092bcd831c2752e0ad542c56293268e"
    assert artifact["result_sha256"] == "08afdedfea172209ef03228dd3313e07cdce54b9a1491b29a10ef54315c544d1"
    assert artifact["artifact_manifest_sha256"] == "c35ad437d58c32a39ff49112b9572a66cc2c56f1282acd7797bc7fb0e0c876ea"
    assert artifact["result_commit_marker_sha256"] == "1ac40f0e1d908e6aa82c49531d216e4a82b71fdb48fe3c2a3b034f0226294d25"

    grant = review["grant_state"]
    assert grant["grant_spent"] is True
    assert grant["replay_permitted"] is False
    assert grant["durable_transaction_state"] == "SUCCEEDED"
    assert grant["result_package_committed"] is True

    execution = review["execution_summary"]
    assert execution["planned_entries"] == execution["completed_entries"] == 35
    assert execution["durable_checkpoint_count"] == 35
    assert execution["stage_timeout_count"] == 0
    assert execution["candidate_count"] == 0
    assert execution["final_classification"] == "NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL"
    assert execution["independent_backend_candidate_comparisons"] == 0
    assert execution["higher_precision_candidate_audits"] == 0

    failures = review["failure_inventory"]
    assert failures == {"STAGNATION": 24, "MAXIMUM_ITERATIONS": 11}
    assert sum(failures.values()) == 35
    assert review["mesh_failure_inventory"]["N96"] == {"STAGNATION": 7}

    n96 = review["n96_review"]
    assert n96["n96_local_root_count"] == 0
    assert n96["all_n96_terminal_failures"] == "STAGNATION"
    assert n96["dominant_boundary_residual_all_seeds"] == "R_4D"
    assert n96["discrete_rank_all_seeds"] == "776_OF_776"
    assert n96["condition_number_above_1e12_seed_count"] == 0
    assert min(n96["R_4D_abs_range"]) > 1.0
    assert min(n96["bulk_residual_max_range"]) > 1e-3
    assert max(n96["discrete_condition_number_range"]) < 1e12

    gates = review["gate_comparison"]
    assert gates["fine_mesh_candidate_gate_reached"] is False
    assert gates["spectral_tail_candidate_gate_reached"] is False
    assert gates["independent_backend_gate_reached"] is False
    assert gates["higher_precision_acceptance_gate_reached"] is False

    governance = review["governance_state"]
    assert governance["WP3"].startswith("NOT_CLOSED")
    assert governance["WP4"].startswith("BLOCKED")
    assert governance["ULSH-02"].startswith("BLOCKED")
    assert governance["K1-D"] == "NOT_RELEASED"
    assert governance["K1-E"] == "NOT_ADMISSIBLE"
    assert governance["physical_evidence_effect"] == "NONE"

    assert review["next_allowed_action"] == "ULSH-01_WP3_D10_CP01R2_FAILURE_MODE_DIAGNOSIS_NO_EXECUTION"
    forbidden = set(review["forbidden_next_actions"])
    assert "DO_NOT_RERUN_OR_REPLAY_THE_SPENT_CP01R2_D8_GRANT" in forbidden
    assert "DO_NOT_ADVANCE_TO_WP4_OR_ULSH-02" in forbidden
    assert "DO_NOT_PROMOTE_DISCRETE_FULL_RANK_TO_CONTINUUM_INVERTIBILITY" in forbidden

    assert D8_TRIGGER.exists()
    assert CP01R1_REVIEW.exists()

    print("PASS_WP3_D9_CP01R2_POST_EXECUTION_RESULT_REVIEW_NO_RERUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
