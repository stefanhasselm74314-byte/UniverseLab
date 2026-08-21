#!/usr/bin/env python3
"""Pure QA for G3.9 preregistration. No BVP solver is imported or executed."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = HERE / "2026-08-19_Background3C5_G3_9_Functional_Jacobian_Evaluation_Preregistration_v0.1.json"


def main():
    x = json.loads(GATE.read_text(encoding="utf-8"))
    assert x["status"] == "PREREGISTERED_NOT_AUTHORIZED"
    assert x["operator"]["dimension"] == 10
    assert len(x["operator"]["residuals"]) == 10
    assert len(x["operator"]["coordinates"]) == 10
    assert x["branch_lock"]["constraint"] == "n_N-n_S=m_layer*N_F"
    assert x["finite_difference"]["scheme"] == "CENTRAL_ONLY"
    assert x["finite_difference"]["dimensionless_step_levels"] == [0.01, 0.005, 0.0025]
    assert x["finite_difference"]["one_sided_fallback"] == "FORBIDDEN"
    assert x["solver_settings"]["nominal"]["relative_tolerance"] == 1e-8
    assert x["solver_settings"]["refined_h3"]["relative_tolerance"] == 1e-10

    schedule = x["evaluation_schedule"]
    expected_nominal = 10 * 3 * 2
    expected_refined = 10 * 2
    expected_total = 1 + expected_nominal + expected_refined
    assert schedule["nominal_perturbations"] == expected_nominal == 60
    assert schedule["refined_h3_perturbations"] == expected_refined == 20
    assert schedule["total_bvp_evaluations"] == expected_total == 81
    assert schedule["execution_authorized"] is False

    cert = x["rank_certification"]
    assert cert["sigma_min_uncertainty_factor_q"] == 5.0
    assert cert["condition_number_max"] == 1e6
    assert cert["smallest_direction_angle_max_deg"] == 10.0
    assert cert["robust_rank10_criterion"] == "sigma_10 > 5*epsilon_J"

    fw = x["firewall"]
    assert fw["physical_execution_authorized"] is False
    assert fw["physical_background_established"] is False
    assert fw["physical_response_rank_R"] == "NOT_EXECUTED"
    assert fw["K1-D"] == "NOT_RELEASED"
    assert fw["K1-E"] == "NOT_ADMISSIBLE"

    print("G3.9 preregistration QA PASS: schedule=81, execution_authorized=false")


if __name__ == "__main__":
    main()
