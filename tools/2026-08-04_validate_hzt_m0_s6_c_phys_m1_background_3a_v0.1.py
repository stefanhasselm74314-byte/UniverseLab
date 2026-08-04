#!/usr/bin/env python3
"""Validate the C-PHYS-M1 Background-3A preregistration contract.

This validator is read-only and fail-closed. It verifies method
preregistration and evidence firewalls; it never runs a nonlinear solver.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"


class ContractError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def load_contract() -> dict[str, Any]:
    require(CONTRACT.is_file(), "missing Background-3A contract")
    try:
        payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid Background-3A JSON: {exc}") from exc
    require(isinstance(payload, dict), "Background-3A contract must be an object")
    return payload


def validate_payload(c: dict[str, Any]) -> dict[str, Any]:
    require(c["model_id"] == "HZT-M0-S6-C-PHYS-M1", "model identity drift")
    require(c["track_id"] == "MD2S-R1-C-PHYS", "track identity drift")
    require(c["block"] == "C-PHYS-R1.0-BACKGROUND-3A", "block identity drift")
    require(c["classification"] == "NUMERICAL_METHOD_PREREGISTRATION_NO_SOLVER_EXECUTION", "classification drift")
    require(c["status"] == "PREREGISTERED_NOT_EXECUTED", "status drift")
    require(c["evidence_effect"] == "NUMERICAL_PROTOCOL_DEFINITION_ONLY", "evidence effect drift")
    require(c["physical_evidence_effect"] == "NONE", "physical evidence drift")
    require(c["solver_authorized"] is False, "solver authorization drift")

    problem = c["frozen_mathematical_problem"]
    require(problem["regional_coordinate"] == "tau in [0,1] for each of N and S", "coordinate drift")
    require(problem["regional_profile_variables"] == [
        "u_A_s(tau)", "u_ell_s(tau)", "u_varphi_s(tau)", "u_g_s(tau)"
    ], "profile variable order drift")
    require(problem["augmented_unknown_vector"] == [
        "varphi_N_0", "q_N", "A_S_0", "varphi_S_0", "q_S", "rho_N", "rho_S", "k4"
    ], "augmented unknown order drift")
    require(len(problem["external_model_coefficients"]) == 6, "M1 parameter budget drift")
    require(len(problem["topological_inputs"]) == 5, "topological input budget drift")
    require(problem["rr_constraint_role"] == "INDEPENDENT_PROPAGATED_QA_CHANNEL_NOT_NONLINEAR_RESIDUAL", "constraint role drift")
    require(problem["model_parameters_are_shooting_variables"] is False, "parameter/shooting role drift")

    inputs = c["future_run_input_contract"]
    require(len(inputs["required_before_execution"]) >= 6, "run-input prerequisites incomplete")
    require("DERIVED_FROM_C1_V" in inputs["parameter_source_labels_forbidden"], "C1-V migration firewall missing")
    require("HISTORICAL_A0_RECONSTRUCTION" in inputs["parameter_source_labels_forbidden"], "historical migration firewall missing")
    require(inputs["post_hoc_parameter_change_under_same_run_id"] is False, "post-hoc parameter change enabled")
    require(inputs["missing_input_action"] == "ABORT_BEFORE_SOLVER_INITIALIZATION", "missing-input action drift")

    disc = c["primary_discretization"]
    require(disc["method"] == "CHEBYSHEV_LOBATTO_COLLOCATION_IN_TAU", "primary discretization drift")
    require(disc["regional_node_counts"] == [24, 32, 48, 64, 96], "mesh preregistration drift")
    require(disc["adaptive_mesh_or_order_selection"] is False, "adaptive post-hoc mesh selection enabled")
    require(disc["floating_point"] == "IEEE_754_BINARY64_PRIMARY", "primary precision drift")

    nonlinear = c["nonlinear_method"]
    require(nonlinear["classification"] == "FUTURE_CANDIDATE_METHOD_NOT_CURRENTLY_AUTHORIZED", "method authorization drift")
    require(nonlinear["method"] == "DAMPED_NEWTON_TRUST_REGION", "nonlinear method drift")
    require(nonlinear["maximum_newton_iterations_per_mesh"] == 60, "iteration cap drift")
    require(nonlinear["maximum_backtracking_steps"] == 20, "backtracking cap drift")
    require(nonlinear["failure_action"] == "RETURN_NO_CANDIDATE_UNDER_PREREGISTERED_PROTOCOL", "failure semantics drift")

    seeds = c["deterministic_seed_protocol"]
    require(seeds["seed_set_size"] == 7, "seed-set size drift")
    require(seeds["seed_amplitude_multipliers"] == [0.0, 0.125, -0.125, 0.25, -0.25, 0.5, -0.5], "seed amplitudes drift")
    require(seeds["random_seed_use"] is False, "random seeds enabled")
    require(seeds["warm_start_across_parameter_points"] is False, "cross-point warm start enabled")
    require("retain and report every distinct candidate" in seeds["multiple_converged_candidates"], "candidate cherry-pick firewall missing")

    tolerances = c["acceptance_thresholds"]
    expected_tolerances = {
        "bulk_residual_max": 1e-10,
        "boundary_residual_max": 1e-10,
        "rr_constraint_max": 1e-9,
        "fine_mesh_profile_difference_max": 1e-8,
        "fine_mesh_augmented_difference_max": 1e-9,
        "independent_backend_candidate_distance_max": 1e-7,
    }
    for key, value in expected_tolerances.items():
        require(tolerances[key] == value, f"acceptance threshold drift: {key}")
    require(tolerances["all_thresholds_must_pass_simultaneously"] is True, "partial acceptance enabled")
    require(tolerances["minimum_rho_N"] > 0 and tolerances["minimum_rho_S"] > 0, "radius positivity margin lost")
    require(tolerances["minimum_interior_ell_margin"] > 0, "interior ell margin lost")
    require(tolerances["minimum_cap_ell_margin"] > 0, "cap ell margin lost")

    convergence = c["convergence_requirements"]
    require(convergence["required_successful_levels"] == [48, 64, 96], "required mesh levels drift")
    require(convergence["fine_pair"] == [64, 96], "fine mesh pair drift")
    require(convergence["single_mesh_acceptance_forbidden"] is True, "single-mesh acceptance enabled")

    backend = c["independent_backend_requirement"]
    require(backend["required_for_candidate_status"] is True, "independent backend no longer required")
    require(backend["shared_source_code_for_residual_assembly"] is False, "backend source independence lost")
    require(backend["candidate_distance_threshold"] == 1e-7, "backend distance threshold drift")
    require(backend["agreement_interpretation"] == "NUMERICAL_CROSSCHECK_ONLY_NOT_INDEPENDENT_PHYSICAL_CONFIRMATION", "backend evidence firewall drift")

    classes = c["predeclared_result_classes"]
    expected_classes = {
        "all_acceptance_gates_pass": "NUMERICAL_CANDIDATE_BACKGROUND_DIAGNOSTIC",
        "solver_converges_but_one_or_more_acceptance_gates_fail": "NUMERICAL_ROOT_REJECTED_BY_QA",
        "no_seed_converges": "NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL",
        "multiple_distinct_candidates_pass": "MULTIPLE_NUMERICAL_CANDIDATE_BACKGROUNDS_DIAGNOSTIC",
        "input_contract_incomplete": "NOT_EXECUTED_INPUT_CONTRACT_FAILURE",
    }
    for key, value in expected_classes.items():
        require(classes[key] == value, f"result class drift: {key}")

    firewall = c["execution_firewall"]
    require(firewall["current_execution"] == "NOT_EXECUTED", "execution status drift")
    for key in [
        "nonlinear_solver_run", "parameter_scan", "observational_fit", "trace_matrix_evaluated",
        "trace_rank_claimed", "Fredholm_claimed", "continuum_Jacobian_claimed",
        "existence_or_uniqueness_claimed", "stability_claimed", "physical_confirmation_claimed"
    ]:
        require(firewall[key] is False, f"execution/evidence firewall opened: {key}")

    gates = c["gate_state"]
    expected_gates = {
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "full_linearized_boundary_trace_rank": "NOT_PROVEN",
        "Fredholm_property": "NOT_PROVEN",
        "continuum_BVP_Jacobian": "NOT_PROVEN",
        "physical_background": "NOT_ESTABLISHED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected_gates.items():
        require(gates[key] == value, f"gate drift: {key}")

    require(c["next_allowed_block_after_merge"] == "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY", "next block drift")
    require("Do not execute the solver" in c["forbidden_next_action"], "solver execution prohibition missing")

    return {
        "status": "PASS",
        "contract": c["schema"],
        "block": c["block"],
        "method": disc["method"],
        "mesh_levels": disc["regional_node_counts"],
        "seed_count": seeds["seed_set_size"],
        "execution": firewall["current_execution"],
        "solver_authorized": c["solver_authorized"],
        "next_block": c["next_allowed_block_after_merge"],
        "physical_evidence_effect": c["physical_evidence_effect"],
        "gate_state": gates,
    }


def validate() -> dict[str, Any]:
    return validate_payload(load_contract())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = validate()
    except ContractError as exc:
        if args.json:
            print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"FAIL: {exc}")
        return 1
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("PASS: C-PHYS-M1 Background-3A preregistration contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
