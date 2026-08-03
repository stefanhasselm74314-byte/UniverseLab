#!/usr/bin/env python3
"""Symbolic and contract QA for M1 Operator-2B function spaces and traces.

The verifier checks the fixed-domain pole chart, regularized derivatives,
endpoint traces and evidence firewalls. It does not construct a background,
linearized rank, kernel, cokernel, Fredholm index or solver.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceContract_v0.1.json"
LEDGER_PATH = ROOT / "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceLedger_v0.1.md"


class ContractError(ValueError):
    """Raised when an Operator-2B invariant fails closed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def load_contract() -> dict[str, Any]:
    require(CONTRACT_PATH.is_file(), "missing Operator-2B contract")
    try:
        value = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid Operator-2B JSON: {exc}") from exc
    require(isinstance(value, dict), "Operator-2B contract must be an object")
    return value


def verify_chart_derivatives() -> dict[str, str]:
    tau = sp.symbols("tau", positive=True)
    rho = sp.symbols("rho", positive=True)
    A0, phi0 = sp.symbols("A0 phi0")
    uA = sp.Function("uA")(tau)
    uL = sp.Function("uL")(tau)
    uP = sp.Function("uP")(tau)
    uG = sp.Function("uG")(tau)
    Lhat = 1 + tau * uL

    A = A0 + tau * uA
    ell = rho * sp.sqrt(tau) * Lhat
    phi = phi0 + tau * uP
    gauge = tau * uG

    def dx(expr: sp.Expr) -> sp.Expr:
        return sp.simplify(2 * sp.sqrt(tau) / rho * sp.diff(expr, tau))

    A_x = dx(A)
    A_xx = dx(A_x)
    phi_x = dx(phi)
    phi_xx = dx(phi_x)
    ell_x = dx(ell)
    ell_xx_over_ell = sp.simplify(dx(ell_x) / ell)
    mixed_A = sp.simplify(A_x * ell_x / ell)
    mixed_phi = sp.simplify(phi_x * ell_x / ell)
    gauge_x_over_sqrt = sp.simplify(dx(gauge) / sp.sqrt(tau))

    expected_A_x = 2 * sp.sqrt(tau) / rho * (uA + tau * sp.diff(uA, tau))
    expected_A_xx = 2 / rho**2 * (
        uA + 5 * tau * sp.diff(uA, tau) + 2 * tau**2 * sp.diff(uA, tau, 2)
    )
    expected_phi_x = 2 * sp.sqrt(tau) / rho * (uP + tau * sp.diff(uP, tau))
    expected_phi_xx = 2 / rho**2 * (
        uP + 5 * tau * sp.diff(uP, tau) + 2 * tau**2 * sp.diff(uP, tau, 2)
    )
    expected_ell_x = Lhat + 2 * tau * sp.diff(Lhat, tau)
    expected_ell_xx_over_ell = 2 / rho**2 * (
        3 * sp.diff(Lhat, tau) + 2 * tau * sp.diff(Lhat, tau, 2)
    ) / Lhat
    expected_mixed_A = 2 / rho**2 * (
        uA + tau * sp.diff(uA, tau)
    ) * (Lhat + 2 * tau * sp.diff(Lhat, tau)) / Lhat
    expected_mixed_phi = 2 / rho**2 * (
        uP + tau * sp.diff(uP, tau)
    ) * (Lhat + 2 * tau * sp.diff(Lhat, tau)) / Lhat
    expected_gauge = 2 / rho * (uG + tau * sp.diff(uG, tau))

    checks = {
        "A_x": sp.simplify(A_x - expected_A_x),
        "A_xx": sp.simplify(A_xx - expected_A_xx),
        "varphi_x": sp.simplify(phi_x - expected_phi_x),
        "varphi_xx": sp.simplify(phi_xx - expected_phi_xx),
        "ell_x": sp.simplify(ell_x - expected_ell_x),
        "ell_xx_over_ell": sp.simplify(ell_xx_over_ell - expected_ell_xx_over_ell),
        "A_x_ell_x_over_ell": sp.simplify(mixed_A - expected_mixed_A),
        "varphi_x_ell_x_over_ell": sp.simplify(mixed_phi - expected_mixed_phi),
        "gauge_x_over_sqrt_tau": sp.simplify(gauge_x_over_sqrt - expected_gauge),
    }
    for name, residual in checks.items():
        require(residual == 0, f"chart derivative identity failed: {name}: {residual}")

    return {
        "coordinate": "tau=y^2",
        "derivative_rule": "d/dx=(2*sqrt(tau)/rho)*d/dtau",
        "identities_checked": str(len(checks)),
        "status": "PASS_EXACT_SYMBOLIC",
    }


def verify_endpoint_traces() -> dict[str, str]:
    tau = sp.symbols("tau", positive=True)
    rho = sp.symbols("rho", positive=True)
    A0, phi0 = sp.symbols("A0 phi0")
    uA = sp.Function("uA")(tau)
    uL = sp.Function("uL")(tau)
    uP = sp.Function("uP")(tau)
    uG = sp.Function("uG")(tau)
    Lhat = 1 + tau * uL

    A = A0 + tau * uA
    ell = rho * sp.sqrt(tau) * Lhat
    phi = phi0 + tau * uP
    gauge = tau * uG

    def dx(expr: sp.Expr) -> sp.Expr:
        return sp.simplify(2 * sp.sqrt(tau) / rho * sp.diff(expr, tau))

    at_one = {tau: sp.Integer(1)}
    traces = {
        "A": sp.simplify(A.subs(at_one)),
        "A_x": sp.simplify(dx(A).subs(at_one)),
        "ell": sp.simplify(ell.subs(at_one)),
        "ell_x": sp.simplify(dx(ell).subs(at_one)),
        "varphi": sp.simplify(phi.subs(at_one)),
        "varphi_x": sp.simplify(dx(phi).subs(at_one)),
        "a_chi": sp.simplify(gauge.subs(at_one)),
    }
    expected = {
        "A": A0 + uA.subs(at_one),
        "A_x": 2 / rho * (uA.subs(at_one) + sp.diff(uA, tau).subs(at_one)),
        "ell": rho * Lhat.subs(at_one),
        "ell_x": Lhat.subs(at_one) + 2 * sp.diff(Lhat, tau).subs(at_one),
        "varphi": phi0 + uP.subs(at_one),
        "varphi_x": 2 / rho * (uP.subs(at_one) + sp.diff(uP, tau).subs(at_one)),
        "a_chi": uG.subs(at_one),
    }
    for name in traces:
        require(sp.simplify(traces[name] - expected[name]) == 0, f"trace formula failed: {name}")

    ell_cap = sp.symbols("ell_cap", positive=True)
    metric_matrix = sp.Matrix([[-3, -1 / ell_cap], [-4, 0]])
    determinant = sp.factor(metric_matrix.det())
    require(determinant == -4 / ell_cap, "cap principal determinant drift")

    return {
        "regional_trace_dimension": "7",
        "combined_profile_trace_dimension": "14",
        "augmented_trace_dimension": "22",
        "cap_metric_derivative_determinant": "-4/ell_cap",
        "status": "PASS_EXACT_SYMBOLIC",
    }


def verify_contract_structure(contract: dict[str, Any]) -> dict[str, Any]:
    require(contract["track_id"] == "MD2S-R1-C-PHYS", "track drift")
    require(contract["model_id"] == "HZT-M0-S6-C-PHYS-M1", "model drift")
    require(contract["block"] == "C-PHYS-R1.0-OPERATOR-2B", "block drift")
    require(
        contract["classification"]
        == "FORMAL_FUNCTION_SPACE_AND_TRACE_CONTRACT_NO_BACKGROUND_SOLVE",
        "classification firewall drift",
    )
    require(
        contract["evidence_effect"] == "FORMAL_FUNCTIONAL_ANALYTIC_STRUCTURE_ONLY",
        "evidence effect drift",
    )
    require(contract["physical_evidence_effect"] == "NONE", "physical evidence overclaim")
    require(contract["solver_authorized"] is False, "solver authorization drift")

    spaces = contract["little_holder_spaces"]
    require(
        spaces["regional_profile_domain"] == "X_s=h^{2,alpha_H}^3 x h^{1,alpha_H}",
        "profile domain drift",
    )
    require(spaces["regional_bulk_target"] == "Y_s=h^{0,alpha_H}^4", "target drift")
    require("dense" in spaces["dense_embedding"], "dense-core statement missing")

    parameters = contract["augmented_parameter_space"]
    require(parameters["dimension"] == 8, "augmented parameter dimension drift")
    require(len(parameters["continuous_vector_order"]) == 8, "parameter ordering drift")

    bulk = contract["regularized_bulk_operator"]
    require(bulk["negative_tau_powers_after_regularization"] is False, "negative tau powers admitted")
    require(bulk["target"] == "F_bulk:U_adm->Y_bulk", "bulk target drift")

    trace = contract["linearized_boundary_trace_template"]
    require(trace["matrix_shape"] == "8 x 22", "boundary matrix template drift")
    require(trace["numeric_matrix_constructed"] is False, "numeric trace overclaim")
    require(trace["rank_claim"] == "NOT_ADMISSIBLE_WITHOUT_W_star", "trace rank firewall drift")

    linearized = contract["linearized_operator_template"]
    require(linearized["Fredholm_property"] == "NOT_PROVEN", "Fredholm overclaim")
    require(linearized["kernel"] == "NOT_COMPUTED", "kernel overclaim")
    require(linearized["cokernel"] == "NOT_COMPUTED", "cokernel overclaim")

    gate = contract["gate_state"]
    expected_gates = {
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "full_linearized_boundary_trace_template": "DEFINED_NOT_EVALUATED",
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
        require(gate[key] == value, f"gate drift: {key}")

    return {
        "alpha_H_domain": contract["fixed_exponent"]["domain"],
        "regional_profile_domain": spaces["regional_profile_domain"],
        "regional_bulk_target": spaces["regional_bulk_target"],
        "augmented_parameter_dimension": parameters["dimension"],
        "boundary_template_shape": trace["matrix_shape"],
        "next_block": contract["next_block"]["id"],
    }


def verify_ledger() -> None:
    require(LEDGER_PATH.is_file(), "missing Operator-2B ledger")
    text = LEDGER_PATH.read_text(encoding="utf-8")
    required = [
        "little-Hölder",
        "C-PHYS-R1.0-OPERATOR-2B",
        "tau=y^2",
        "DEFINED NOT EVALUATED",
        "Fredholm property",
        "C-PHYS-R1.0-BACKGROUND-3A",
    ]
    for fragment in required:
        require(fragment in text, f"ledger missing fragment: {fragment}")


def validate() -> dict[str, Any]:
    contract = load_contract()
    verify_ledger()
    return {
        "contract": "C_PHYS_M1_OPERATOR_2B_FUNCTION_SPACE_TRACE",
        "status": "PASS_FORMAL",
        "chart_derivatives": verify_chart_derivatives(),
        "endpoint_traces": verify_endpoint_traces(),
        "contract_structure": verify_contract_structure(contract),
        "solver_authorized": False,
        "physical_evidence_effect": "NONE",
        "forbidden_inference": [
            "No candidate background is constructed.",
            "No numerical trace rank is computed.",
            "No kernel, cokernel or Fredholm index is computed.",
            "No solver or release gate is authorized.",
        ],
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
        print("PASS: M1 Operator-2B function-space and trace contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
