#!/usr/bin/env python3
"""Validate the exact C-PHYS-M1 Background-3B run-input freeze.

This validator is read-only and fail-closed. It recomputes the dependency,
seed and run-payload hashes, checks the exact control seed symbolically and
verifies that no solver implementation or execution is authorized.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.1.json"
SEEDS = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BSeedSpecification_v0.1.json"
LOCK = ROOT / "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3B_v0.1.txt"
METHOD = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"
TOPOLOGY = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3ATopologyCorrectionContract_v0.2.json"

EXPECTED_LOCK_TEXT = "numpy==2.1.3\nscipy==1.14.1\nsympy==1.13.3\nmpmath==1.3.0\n"
EXPECTED_LOCK_SHA256 = "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f"
EXPECTED_SEED_SHA256 = "b6e4319cc29736799a0b46320002e51cd17b70b724a6b4c6e86567a316996161"
EXPECTED_RUN_SHA256 = "625118d21d70fb563c310e985ba83126a18b8680278b7b11908c1bc550f79536"
EXPECTED_BASIS_COMMIT = "2e27fd5702e02bd0e7e2b096844aa56c070d9257"


class ContractError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing required artifact: {path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    require(isinstance(value, dict), f"artifact root must be an object: {path.relative_to(ROOT)}")
    return value


def canonical_json_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verify_dependency_lock(contract: dict[str, Any]) -> dict[str, str]:
    require(LOCK.is_file(), "missing dependency lock")
    text = LOCK.read_text(encoding="utf-8")
    require(text == EXPECTED_LOCK_TEXT, "dependency lock text drift")
    actual = hashlib.sha256(text.encode("utf-8")).hexdigest()
    require(actual == EXPECTED_LOCK_SHA256, "dependency lock SHA256 drift")
    payload = contract["frozen_run_payload"]
    require(payload["dependency_lock_path"] == str(LOCK.relative_to(ROOT)), "dependency lock path drift")
    require(payload["dependency_lock_sha256"] == actual, "run payload dependency hash drift")
    state = contract["dependency_and_software_state"]
    require(state["dependency_lock_frozen"] is True, "dependency lock not frozen")
    require(state["dependency_versions_are_method_pins_not_latest_version_claims"] is True, "latest-version overclaim")
    return {"path": str(LOCK.relative_to(ROOT)), "sha256": actual}


def verify_seed_hash(contract: dict[str, Any], seeds: dict[str, Any]) -> dict[str, Any]:
    require(seeds["model_id"] == "HZT-M0-S6-C-PHYS-M1", "seed model drift")
    require(seeds["seed_set_id"] == "M1-BG3B-CP01-SEEDS-01", "seed-set id drift")
    require(seeds["classification"] == "DETERMINISTIC_SEED_SET_FOR_FROZEN_RUN_INPUT_NOT_SOLUTION", "seed classification drift")
    require(seeds["target_a_F"] == "1/4", "target a_F drift")
    require(seeds["base_control_value_a_F"] == "0", "control a_F drift")

    payload = copy.deepcopy(seeds)
    recorded = payload.pop("canonical_payload_sha256", None)
    actual = canonical_json_sha256(payload)
    require(recorded == EXPECTED_SEED_SHA256, "recorded seed payload hash drift")
    require(actual == EXPECTED_SEED_SHA256, "recomputed seed payload hash drift")
    require(contract["frozen_run_payload"]["seed_spec_sha256"] == actual, "run payload seed hash drift")

    generation = seeds["seed_generation"]
    require(generation["seed_count"] == 7, "seed count drift")
    require(generation["amplitude_scale"] == "1/20", "seed amplitude scale drift")
    require(generation["multipliers_in_order"] == ["0", "1/8", "-1/8", "1/4", "-1/4", "1/2", "-1/2"], "seed multiplier order drift")
    require(generation["random_numbers"] is False, "random seeds enabled")
    require(generation["post_result_seed_addition"] is False, "post-result seed addition enabled")
    require(generation["all_distinct_converged_candidates_retained"] is True, "candidate retention firewall lost")
    require(generation["augmented_variable_order"] == [
        "varphi_N_0", "q_N", "A_S_0", "varphi_S_0", "q_S", "rho_N", "rho_S", "k4"
    ], "augmented seed order drift")

    scope = seeds["scope"]
    require(scope == {
        "run_input_only": True,
        "solver_execution": False,
        "background_result": False,
        "physical_evidence_effect": "NONE",
    }, "seed scope drift")
    return {"seed_set_id": seeds["seed_set_id"], "seed_count": generation["seed_count"], "sha256": actual}


def verify_run_payload(contract: dict[str, Any]) -> dict[str, Any]:
    run = contract["frozen_run_payload"]
    actual = canonical_json_sha256(run)
    require(contract["frozen_run_payload_sha256"] == EXPECTED_RUN_SHA256, "recorded run payload hash drift")
    require(actual == EXPECTED_RUN_SHA256, "recomputed run payload hash drift")
    require(run["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01", "run id drift")
    require(run["classification"] == "CONTROL_POINT_RUN_INPUT_FREEZE_ONLY", "run classification drift")
    require(run["model_parameters_ordered"] == {
        "Lambda_hat": "1",
        "mhat_phi_sq": "1",
        "a_F": "1/4",
        "lambda_hat": "1",
        "z_sigma_hat": "1",
        "q_hat": "1",
    }, "frozen M1 parameter vector drift")
    require(run["dimensional_anchor"] == {
        "M6": "1_as_dimensionless_computational_unit_only",
        "physical_value_assigned": False,
    }, "dimensional anchor drift")
    require(run["topological_sector_ordered"] == {
        "N_F": 1,
        "N_sigma": 1,
        "m_sigma": 1,
    }, "single-cap topology sector drift")
    require(run["alpha_H"] == "1/2", "Holder exponent drift")
    require(run["protocol_basis_commit"] == EXPECTED_BASIS_COMMIT, "protocol basis commit drift")
    require(run["solver_implementation_commit"] == "NOT_PRESENT_EXECUTION_FORBIDDEN", "solver implementation state drift")
    require(run["background_method_contract"] == str(METHOD.relative_to(ROOT)), "method contract pointer drift")
    require(run["topology_correction_contract"] == str(TOPOLOGY.relative_to(ROOT)), "topology contract pointer drift")

    run_text = json.dumps(run, sort_keys=True)
    for forbidden in ["m_N", "m_S", "n_N", "n_S"]:
        require(forbidden not in run_text, f"regional topology label entered frozen run payload: {forbidden}")

    if (ROOT / ".git").exists():
        require(re.fullmatch(r"[0-9a-f]{40}", run["protocol_basis_commit"]) is not None, "basis commit format drift")
        result = subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "-e", f"{run['protocol_basis_commit']}^{{commit}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        require(result.returncode == 0, "protocol basis commit absent from repository history")
    return {"run_id": run["run_id"], "sha256": actual, "basis_commit": run["protocol_basis_commit"]}


def verify_model_and_topology_sources(contract: dict[str, Any], method: dict[str, Any], topology: dict[str, Any]) -> dict[str, Any]:
    require(method["model_id"] == "HZT-M0-S6-C-PHYS-M1", "Background-3A method model drift")
    require(method["status"] == "PREREGISTERED_NOT_EXECUTED", "Background-3A method status drift")
    require(method["solver_authorized"] is False, "Background-3A solver authorization drift")
    require(topology["status"] == "ACTIVE_CANONICAL_CORRECTION", "topology correction status drift")
    require(topology["canonical_effective_topological_input"]["ordered_vector"] == ["N_F", "N_sigma", "m_sigma"], "canonical topology vector drift")
    require(topology["canonical_effective_topological_input"]["count"] == 3, "canonical topology count drift")
    require(topology["effective_background_3a_status"]["exact_run_input_frozen"] is False, "Background-3A incorrectly froze run input")

    require(contract["parameter_domain_audit"] == {
        "Lambda_hat": "finite_real_pass",
        "mhat_phi_sq": "1_strictly_positive_pass",
        "a_F": "1/4_strictly_positive_active_M1_pass",
        "lambda_hat": "finite_real_pass",
        "z_sigma_hat": "1_strictly_positive_pass",
        "q_hat": "1_strictly_positive_pass",
        "alpha_H": "1/2_in_open_interval_0_1_pass",
        "M6": "dimensionless_computational_unit_only_no_physical_scale_assignment",
    }, "parameter-domain audit drift")
    require(contract["topology_audit"]["ordered_sector"] == ["N_F", "N_sigma", "m_sigma"], "contract topology order drift")
    require(contract["topology_audit"]["values"] == [1, 1, 1], "contract topology values drift")
    require(contract["topology_audit"]["single_cap_phase"] is True, "single-cap identity lost")
    require(contract["topology_audit"]["sector_change_under_same_run_id"] is False, "sector mutation enabled")
    return {"parameter_count": 6, "topology_vector": ["N_F", "N_sigma", "m_sigma"], "topology_values": [1, 1, 1]}


def verify_exact_control_seed(seeds: dict[str, Any]) -> dict[str, str]:
    seed = seeds["base_control_seed"]
    require(seed["classification"] == "EXACT_BULK_AND_PATCH_SEED_BOUNDARY_INEXACT", "control seed classification drift")
    require(seed["not_a_solution"] is True, "control seed solution overclaim")

    y = (sp.Integer(8) - 2 * sp.sqrt(10)) / 3
    q = y / 2
    R2 = 1 / y
    k4 = (1 - q**2 / 2) / 6
    rho_F = q**2 / 2

    require(sp.simplify(3 * y**2 - 16 * y + 8) == 0, "seed polynomial identity failed")
    require(sp.simplify(y - (sp.Rational(1, 2) + sp.Rational(3, 4) * q**2)) == 0, "seed curvature-flux identity failed")
    require(sp.simplify(2 * q * R2 - 1) == 0, "seed patch identity failed")

    E_A = -6 * k4 + 1 - rho_F
    E_ell_coefficient = -y - 3 * k4 + 1 + rho_F
    C_rr_coefficient = -6 * k4 + 1 - rho_F
    require(sp.simplify(E_A) == 0, "control-seed E_A failed")
    require(sp.simplify(E_ell_coefficient) == 0, "control-seed E_ell failed")
    require(sp.simplify(C_rr_coefficient) == 0, "control-seed rr constraint failed")

    R4d = 1 + 9 * y / 8
    Rchi = 1 - 9 * y / 8
    Rgauge = -3 * y / 2
    require(sp.simplify(R4d) != 0, "R_4d defect was incorrectly closed")
    require(sp.simplify(Rchi) != 0, "R_chi defect was incorrectly closed")
    require(sp.simplify(Rgauge) != 0, "R_gauge defect was incorrectly closed")
    defects = seed["deliberately_nonzero_cap_defects"]
    require(defects == {
        "d_chi_using_south_patch": "3/2",
        "Y_hat_sigma": "9*y0/4",
        "R_4d": "1+9*y0/8",
        "R_chi": "1-9*y0/8",
        "R_gauge_local": "-3*y0/2",
    }, "recorded cap defects drift")
    return {
        "classification": seed["classification"],
        "bulk_and_constraint": "PASS_EXACT_SYMBOLIC",
        "patch": "PASS_EXACT_SYMBOLIC",
        "cap_defects": "NONZERO_AS_PREREGISTERED",
        "solution_claim": "FORBIDDEN",
    }


def verify_firewalls(contract: dict[str, Any]) -> dict[str, Any]:
    require(contract["classification"] == "EXACT_RUN_INPUT_FREEZE_NO_SOLVER_EXECUTION", "contract classification drift")
    require(contract["status"] == "RUN_INPUT_FROZEN_EXECUTION_NOT_AUTHORIZED", "contract status drift")
    require(contract["evidence_effect"] == "NUMERICAL_RUN_INPUT_DEFINITION_ONLY", "evidence effect drift")
    require(contract["physical_evidence_effect"] == "NONE", "physical evidence drift")
    require(contract["solver_authorized"] is False, "solver authorization drift")

    selection = contract["selection_firewall"]
    require(selection["parameter_source_label"] == "CONTROL_POINT", "parameter source drift")
    for key in [
        "observational_fit_used", "historical_A0_values_used", "C1_V_values_used",
        "random_search_used", "post_hoc_tuning_used", "physical_preference_claimed",
    ]:
        require(selection[key] is False, f"selection firewall opened: {key}")

    software = contract["dependency_and_software_state"]
    require(software["solver_entry_point"] == "NOT_PRESENT", "solver entry point appeared")
    require(software["solver_source_hash"] == "NOT_AVAILABLE_BECAUSE_IMPLEMENTATION_FORBIDDEN_IN_BACKGROUND_3B", "solver source state drift")
    require(software["execution_environment_hash"] == "NOT_AVAILABLE_BECAUSE_NO_EXECUTION_ENVIRONMENT_IS_BUILT", "execution environment overclaim")

    firewall = contract["execution_firewall"]
    require(firewall["current_execution"] == "NOT_EXECUTED", "execution status drift")
    for key in [
        "solver_implementation_present", "solver_initialization", "nonlinear_solver_run",
        "parameter_scan", "topology_scan", "continuation_run", "background_candidate_created",
        "trace_matrix_evaluated", "trace_rank_claimed", "Fredholm_claimed",
        "continuum_Jacobian_claimed", "existence_or_uniqueness_claimed",
        "stability_claimed", "physical_confirmation_claimed",
    ]:
        require(firewall[key] is False, f"execution/evidence firewall opened: {key}")

    gates = contract["gate_state"]
    expected = {
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED_CORRECTED_TO_SINGLE_CAP_PHASE",
        "BACKGROUND_3B": "RUN_INPUT_FROZEN_EXECUTION_NOT_AUTHORIZED",
        "BACKGROUND_RUN_INPUT": "FROZEN_CP01",
        "BACKGROUND_SOLVER_IMPLEMENTATION": "NOT_PRESENT",
        "BACKGROUND_SOLVER_EXECUTION": "NOT_AUTHORIZED",
        "physical_background": "NOT_ESTABLISHED",
        "full_linearized_boundary_trace_rank": "NOT_PROVEN",
        "Fredholm_property": "NOT_PROVEN",
        "continuum_BVP_Jacobian": "NOT_PROVEN",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected.items():
        require(gates.get(key) == value, f"gate drift: {key}")
    require(contract["next_allowed_block"] == "C-PHYS-R1.0-BACKGROUND-3C_EXECUTION_IMPLEMENTATION_AND_AUTHORIZATION_GATE", "next block drift")
    require("must not itself trigger execution" in contract["next_block_limits"], "automatic execution firewall missing")
    return {"execution": firewall["current_execution"], "solver_authorized": False, "gates": expected}


def validate_payloads(contract: dict[str, Any], seeds: dict[str, Any], method: dict[str, Any], topology: dict[str, Any]) -> dict[str, Any]:
    require(contract["track_id"] == "MD2S-R1-C-PHYS", "track identity drift")
    require(contract["model_id"] == "HZT-M0-S6-C-PHYS-M1", "model identity drift")
    require(contract["block"] == "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY", "block identity drift")
    return {
        "status": "PASS",
        "contract": contract["schema"],
        "dependency_lock": verify_dependency_lock(contract),
        "seed_spec": verify_seed_hash(contract, seeds),
        "run_payload": verify_run_payload(contract),
        "source_consistency": verify_model_and_topology_sources(contract, method, topology),
        "control_seed": verify_exact_control_seed(seeds),
        "firewall": verify_firewalls(contract),
        "next_block": contract["next_allowed_block"],
        "physical_evidence_effect": contract["physical_evidence_effect"],
    }


def validate() -> dict[str, Any]:
    return validate_payloads(load_json(CONTRACT), load_json(SEEDS), load_json(METHOD), load_json(TOPOLOGY))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = validate()
    except (ContractError, AssertionError) as exc:
        if args.json:
            print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"FAIL: {exc}")
        return 1
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("PASS: C-PHYS-M1 Background-3B exact run input frozen without execution")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
