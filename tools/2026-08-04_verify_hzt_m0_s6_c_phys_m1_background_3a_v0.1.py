#!/usr/bin/env python3
"""Exact QA for C-PHYS-M1 BACKGROUND-3A preregistration.

The verifier checks only the registered model point, exact h=0 bulk seed,
patch quantization, tau-chart limits, method freeze and evidence firewall.
It never runs Newton, continuation, collocation, shooting or any BVP solver.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"
LEDGER_PATH = ROOT / "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationLedger_v0.1.md"


class ContractError(ValueError):
    """Raised when a fail-closed preregistration invariant fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def load_contract() -> dict[str, Any]:
    require(CONTRACT_PATH.is_file(), "missing BACKGROUND-3A contract")
    try:
        value = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid BACKGROUND-3A JSON: {exc}") from exc
    require(isinstance(value, dict), "BACKGROUND-3A contract root must be an object")
    return value


def verify_exact_bulk_seed() -> dict[str, str]:
    x = sp.symbols("x", real=True)
    y = (sp.Integer(8) - 2 * sp.sqrt(10)) / 3
    q = y / 2
    R = 1 / sp.sqrt(y)
    rho = sp.pi * R / 2
    k4 = (1 - q**2 / 2) / 6
    Lambda = sp.Integer(1)
    rho_F = q**2 / 2

    require(sp.simplify(3 * y**2 - 16 * y + 8) == 0, "y0 polynomial identity failed")
    require(sp.simplify(y - (sp.Rational(1, 2) + 3 * q**2 / 4)) == 0, "bulk radius identity failed")
    require(sp.simplify(2 * q * R**2 - 1) == 0, "patch normalization identity failed")

    ell = R * sp.sin(x / R)
    ell_xx = sp.diff(ell, x, 2)
    A_x = sp.Integer(0)
    phi = sp.Integer(0)
    phi_x = sp.Integer(0)

    E_A = -6 * k4 + Lambda + sp.Rational(1, 2) * phi_x**2 + sp.Rational(1, 2) * phi**2 - rho_F
    E_ell = ell_xx - 3 * k4 * ell + Lambda * ell + rho_F * ell
    E_phi = sp.Integer(0)
    constraint = ell * (-6 * k4 + Lambda) - ell * rho_F

    a_plus = q * R**2 * (1 - sp.cos(x / R))
    a_minus = -a_plus
    E_gauge_plus = sp.diff(a_plus, x) - q * ell
    E_gauge_minus = sp.diff(a_minus, x) - (-q) * ell

    residuals = {
        "E_A": E_A,
        "E_ell": E_ell,
        "E_varphi": E_phi,
        "E_gauge_N": E_gauge_plus,
        "E_gauge_S": E_gauge_minus,
        "C_rr": constraint,
    }
    for name, residual in residuals.items():
        require(sp.simplify(sp.trigsimp(residual)) == 0, f"exact seed residual failed: {name}")

    aN_cap = sp.simplify(a_plus.subs(x, rho))
    aS_cap = sp.simplify(a_minus.subs(x, rho))
    require(aN_cap == sp.Rational(1, 2), "north cap potential drift")
    require(aS_cap == -sp.Rational(1, 2), "south cap potential drift")
    require(sp.simplify(aN_cap - aS_cap - 1) == 0, "patch residual is not exact")

    d_chi = 1 - aS_cap
    Y_sigma = sp.simplify(d_chi**2 / R**2)
    R_4d = sp.simplify(1 + Y_sigma / 2)
    R_chi = sp.simplify(1 - Y_sigma / 2)
    R_gauge = sp.simplify(-d_chi / R**2)
    require(d_chi == sp.Rational(3, 2), "seed winding drift")
    require(sp.simplify(Y_sigma - 9 * y / 4) == 0, "seed anisotropy drift")
    require(sp.simplify(R_4d - (1 + 9 * y / 8)) == 0, "R_4d defect drift")
    require(sp.simplify(R_chi - (1 - 9 * y / 8)) == 0, "R_chi defect drift")
    require(sp.simplify(R_gauge + 3 * y / 2) == 0, "R_gauge defect drift")
    require(all(sp.simplify(value) != 0 for value in (R_4d, R_chi, R_gauge)), "cap defects must remain visibly nonzero")

    return {
        "y0": str(y),
        "q0": str(sp.simplify(q)),
        "R0": str(R),
        "rho0": str(rho),
        "k4_0": str(sp.simplify(k4)),
        "bulk_residuals": "PASS_EXACT",
        "constraint": "PASS_EXACT",
        "patch_residual": "PASS_EXACT",
        "nonzero_cap_defects": "PASS_EXPLICIT",
    }


def verify_tau_chart_limits() -> dict[str, str]:
    tau = sp.symbols("tau", positive=True)
    root = sp.sqrt(tau)
    Lhat = 2 * sp.sin(sp.pi * root / 2) / (sp.pi * root)
    u_ell = (Lhat - 1) / tau
    u_g = (1 - sp.cos(sp.pi * root / 2)) / (2 * tau)

    require(sp.limit(Lhat, tau, 0, dir="+") == 1, "Lhat pole limit failed")
    require(sp.limit(u_ell, tau, 0, dir="+") == -sp.pi**2 / 24, "u_ell pole limit failed")
    require(sp.limit(u_g, tau, 0, dir="+") == sp.pi**2 / 16, "u_g pole limit failed")

    return {
        "Lhat_0": "1",
        "u_ell_0": "-pi**2/24",
        "u_g_N_0": "+pi**2/16",
        "u_g_S_0": "-pi**2/16",
        "status": "PASS_EXACT_LIMITS",
    }


def verify_contract_firewall(contract: dict[str, Any]) -> dict[str, Any]:
    require(contract["track_id"] == "MD2S-R1-C-PHYS", "track drift")
    require(contract["model_id"] == "HZT-M0-S6-C-PHYS-M1", "model drift")
    require(contract["block"] == "C-PHYS-R1.0-BACKGROUND-3A", "block drift")
    require(
        contract["classification"] == "BACKGROUND_METHOD_PREREGISTRATION_NO_SOLVER_EXECUTION",
        "classification drift",
    )
    require(contract["status"] == "METHOD_PREREGISTERED_EXECUTION_NOT_AUTHORIZED", "status drift")
    require(contract["official_solver_authorized"] is False, "official solver overclaim")
    require(contract["diagnostic_execution_authorized_in_this_block"] is False, "diagnostic execution overclaim")
    require(contract["physical_evidence_effect"] == "NONE", "physical evidence overclaim")

    instance = contract["diagnostic_instance"]
    require(instance["instance_id"] == "HZT-M0-S6-C-PHYS-M1-BG3A-I1", "instance id drift")
    require(
        instance["dimensionless_model_parameters"]
        == {
            "Lambda_hat": 1,
            "mhat_phi_sq": 1,
            "a_F": "1/4",
            "lambda_hat": 1,
            "z_sigma_hat": 1,
            "q_hat": 1,
        },
        "diagnostic parameter tuple drift",
    )
    require(
        instance["discrete_sector"]
        == {
            "sector_id": "NF1-NS1-MS1",
            "N_F": 1,
            "N_sigma": 1,
            "m_sigma": 1,
            "q_sigma_over_q_ref": 1,
            "fixed_for_entire_attempt": True,
        },
        "discrete sector drift",
    )
    require(instance["parameter_scan"] == "FORBIDDEN_IN_BACKGROUND_3A_AND_3B", "parameter scan firewall drift")
    require(instance["sector_scan"] == "FORBIDDEN_IN_BACKGROUND_3A_AND_3B", "sector scan firewall drift")

    homotopy = contract["control_homotopy"]
    require(homotopy["only_varied_model_coefficient"] == "a_F(h)=h/4", "homotopy drift")
    require(homotopy["minimum_step"] == "1/256", "minimum homotopy step drift")
    require(homotopy["all_other_model_parameters_fixed"] is True, "parameter-freeze drift")
    require(homotopy["discrete_sector_fixed"] is True, "sector-freeze drift")

    primary = contract["primary_backend"]
    require(primary["continuation_degree"] == 32, "continuation degree drift")
    require(primary["target_refinement_degrees"] == [48, 64, 96], "refinement schedule drift")
    require(primary["jacobian"]["method"] == "complex_step_componentwise_on_analytic_residual_map", "primary Jacobian drift")
    require(primary["determinism"]["random_numbers"] == "FORBIDDEN", "randomness firewall drift")

    secondary = contract["independent_backend"]
    require(secondary["integrator"] == "DOP853", "independent integrator drift")
    require(secondary["pole_cutoff_sequence"] == ["1e-3", "5e-4", "2.5e-4"], "pole-cutoff schedule drift")

    execution = contract["execution_protocol"]
    require(execution["current_execution_state"] == "NOT_STARTED", "execution has started inside preregistration")
    require(execution["result_artifact_created"] is False, "result artifact overclaim")

    gates = contract["gate_state"]
    expected = {
        "BACKGROUND_3B": "NOT_STARTED",
        "diagnostic_candidate_execution": "NOT_AUTHORIZED_IN_THIS_BLOCK",
        "physical_background": "NOT_ESTABLISHED",
        "background_existence": "NOT_PROVEN",
        "background_uniqueness": "NOT_PROVEN",
        "full_linearized_boundary_trace_rank": "NOT_PROVEN",
        "Fredholm_property": "NOT_PROVEN",
        "continuum_BVP_Jacobian": "NOT_PROVEN",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected.items():
        require(gates[key] == value, f"gate drift: {key}")

    return {
        "instance_id": instance["instance_id"],
        "sector_id": instance["discrete_sector"]["sector_id"],
        "primary_backend": primary["backend_id"],
        "independent_backend": secondary["backend_id"],
        "next_block": contract["next_block"]["id"],
        "solver_authorized": False,
    }


def verify_ledger() -> None:
    require(LEDGER_PATH.is_file(), "missing BACKGROUND-3A ledger")
    text = LEDGER_PATH.read_text(encoding="utf-8")
    required_fragments = [
        "BACKGROUND-3A",
        "3y_0^2-16y_0+8=0",
        "EXACT_BULK_AND_PATCH_SEED_BOUNDARY_INEXACT",
        "NO_ACCEPTED_CANDIDATE",
        "METHOD_PREREGISTERED_EXECUTION_NOT_AUTHORIZED",
        "C-PHYS-R1.0-BACKGROUND-3B",
    ]
    for fragment in required_fragments:
        require(fragment in text, f"ledger missing fragment: {fragment}")


def validate() -> dict[str, Any]:
    contract = load_contract()
    verify_ledger()
    return {
        "contract": "C_PHYS_M1_BACKGROUND_3A_PREREGISTRATION",
        "status": "PASS_METHOD_PREREGISTRATION",
        "exact_bulk_seed": verify_exact_bulk_seed(),
        "tau_chart": verify_tau_chart_limits(),
        "firewall": verify_contract_firewall(contract),
        "solver_executed": False,
        "candidate_background_created": False,
        "physical_evidence_effect": "NONE",
    }


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
        print("PASS: C-PHYS-M1 BACKGROUND-3A preregistration and exact control seed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
