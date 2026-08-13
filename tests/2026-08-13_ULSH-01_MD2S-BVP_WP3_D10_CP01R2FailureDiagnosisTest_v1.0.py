#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D10 = ROOT / "registry/2026-08-13_ULSH-01_MD2S-BVP_WP3_D10_CP01R2FailureDiagnosis_v1.0.json"
D9 = ROOT / "registry/2026-08-13_ULSH-01_MD2S-BVP_WP3_D9_CP01R2ResultReview_v1.0.json"
KERNEL = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.1.py"
ETRN = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d2_cp01r2_etrn_v1.0.py"
RUN_INPUT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3_CP01R2RunInputFreeze_v1.0.json"


def main() -> int:
    diagnosis = json.loads(D10.read_text(encoding="utf-8"))
    review = json.loads(D9.read_text(encoding="utf-8"))
    run_input = json.loads(RUN_INPUT.read_text(encoding="utf-8"))
    kernel = KERNEL.read_text(encoding="utf-8")
    etrn = ETRN.read_text(encoding="utf-8")

    assert diagnosis["classification"] == "POST_RESULT_FAILURE_MODE_DIAGNOSIS_NO_EXECUTION"
    assert diagnosis["status"] == "PASS_CP01R2_FAILURE_MODE_DIAGNOSIS_BOUNDARY_MANIFOLD_AND_TRUST_GEOMETRY_IDENTIFIED_NO_EXECUTION"
    assert review["review_status"] == "PASS_TRANSACTION_COMPLETE_NEGATIVE_NUMERICAL_OUTCOME_NO_CANDIDATE_UNDER_PREREGISTERED_CP01R2_PROTOCOL"
    assert review["execution_summary"]["candidate_count"] == 0
    assert review["execution_summary"]["completed_entries"] == 35

    effect = diagnosis["execution_effect"]
    assert set(effect.values()) == {0}

    confirmed = diagnosis["confirmed_diagnostics"]
    assert confirmed["all_35_entries_initialized_from_fresh_frozen_seed_same_index"] is True
    assert confirmed["mesh_continuation_source_entry_count"] == 0
    assert confirmed["entries_meeting_10_percent_progress_continuation_threshold"] == 0
    assert confirmed["maximum_relative_stage_residual_improvement"] < 0.01
    assert confirmed["total_recorded_etrn_iterations"] == 1785
    assert confirmed["accepted_etrn_iterations"] == 1785
    assert confirmed["rejected_etrn_iterations"] == 0
    assert confirmed["n96_recorded_iterations"] == 84
    assert confirmed["n96_accepted_iterations"] == 84
    assert confirmed["n96_rejected_iterations"] == 0
    assert confirmed["n96_final_trust_radius_all_seeds"] == 64.0
    assert min(confirmed["n96_unclipped_scaled_step_norm_range"]) > 1e8
    assert max(confirmed["n96_max_trust_to_unclipped_step_ratio_range"]) < 1e-6
    assert max(confirmed["n96_relative_terminal_state_displacement_from_frozen_seed_range"]) < 2e-5
    assert confirmed["n96_full_discrete_rank_all_seeds"] == "776_OF_776"
    assert max(confirmed["n96_condition_estimate_range"]) < 1e12
    assert confirmed["n96_candidate_count"] == 0

    junction = diagnosis["junction_identity"]
    assert junction["Y_sigma_cancels_from_sum_identity"] is True
    assert junction["frozen_lambda_hat"] == 1.0
    assert junction["simultaneous_zero_necessary_condition"] == "7*A_sum + ell_sum = 2"
    assert max(junction["n96_observed_7A_sum_plus_ell_sum_range"]) < 0.0041
    assert min(junction["n96_observed_R4D_plus_Rchi_range"]) > 1.99

    # Source-bound static derivation: no numerical backend is imported or evaluated here.
    assert "-3.0 * A_sum - ell_sum + model.lambda_hat + 0.5 * Y_sigma" in kernel
    assert "-4.0 * A_sum + model.lambda_hat - 0.5 * Y_sigma" in kernel
    assert "TRUST_RADIUS_MAXIMUM = 64.0" in etrn
    assert "final <= 0.90 * initial" in etrn
    assert "STAGNATION_WINDOW = 12" in etrn
    assert "STAGNATION_FLOOR = 1.0e-4" in etrn

    payload = run_input["frozen_run_payload"]
    assert payload["model_parameters_ordered"]["lambda_hat"] == "1"
    assert payload["physical_equation_source_path"] == diagnosis["frozen_sources"]["physical_kernel"]
    assert payload["primary_method_id"] == "ETRN-01_EQUILIBRATED_TRUST_REGION_NEWTON"

    hypotheses = {row["id"]: row for row in diagnosis["ranked_failure_modes"]}
    assert set(hypotheses) == {"D10-H1", "D10-H2", "D10-H3", "D10-H4"}
    assert hypotheses["D10-H1"]["strength"] == "STRONG_DIAGNOSTIC"
    assert hypotheses["D10-H3"]["strength"] == "CONFIRMED_PROTOCOL_PATH"

    governance = diagnosis["governance_state"]
    assert governance["WP3"].startswith("NOT_CLOSED")
    assert governance["WP4"].startswith("BLOCKED")
    assert governance["ULSH-02"].startswith("BLOCKED")
    assert governance["K1-D"] == "NOT_RELEASED"
    assert governance["K1-E"] == "NOT_ADMISSIBLE"
    assert governance["physical_evidence_effect"] == "NONE"

    assert diagnosis["next_allowed_action"] == "ULSH-01_WP3_D11_BOUNDARY_AWARE_INITIALIZATION_AND_TRUST_SCALING_PROTOCOL_DESIGN_NO_EXECUTION"
    forbidden = set(diagnosis["forbidden_next_actions"])
    assert "DO_NOT_RERUN_OR_REPLAY_CP01R2_D8" in forbidden
    assert "DO_NOT_ADVANCE_TO_WP4_OR_ULSH-02" in forbidden
    assert "DO_NOT_PROMOTE_DISCRETE_FULL_RANK_TO_CONTINUUM_INVERTIBILITY" in forbidden

    print("PASS_WP3_D10_CP01R2_FAILURE_MODE_DIAGNOSIS_NO_EXECUTION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
