#!/usr/bin/env python3
"""Fail-closed validator for HZT-M0-S6-C-PHYS-M1 Freeze-1B."""

from __future__ import annotations

import argparse
import copy
import json
import math
import pathlib
import sys
from dataclasses import dataclass
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT_PATH = pathlib.Path(
    "registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json"
)


@dataclass(frozen=True)
class ContractIssue:
    category: str
    message: str

    def render(self) -> str:
        return f"[{self.category}] {self.message}"


def load_contract(root: pathlib.Path = ROOT) -> dict[str, Any]:
    return json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))


def require(condition: bool, category: str, message: str, issues: list[ContractIssue]) -> None:
    if not condition:
        issues.append(ContractIssue(category, message))


def u(varphi: float, mhat_phi_sq: float) -> float:
    return 0.5 * mhat_phi_sq * varphi * varphi


def z_f(varphi: float, a_f: float) -> float:
    return math.exp(-2.0 * a_f * varphi)


def rho_f(q_s: float, warp: float, varphi: float, a_f: float) -> float:
    return 0.5 * q_s * q_s * math.exp(-8.0 * warp + 2.0 * a_f * varphi)


def validate_parameter_point(
    *,
    lambda_hat: float,
    lambda6_hat: float,
    mhat_phi_sq: float,
    a_f: float,
    z_sigma_hat: float,
    q_hat: float,
) -> list[ContractIssue]:
    issues: list[ContractIssue] = []
    for name, value in {
        "lambda_hat": lambda_hat,
        "Lambda_hat": lambda6_hat,
        "mhat_phi_sq": mhat_phi_sq,
        "a_F": a_f,
        "z_sigma_hat": z_sigma_hat,
        "q_hat": q_hat,
    }.items():
        require(math.isfinite(value), "DOMAIN", f"{name} must be finite", issues)
    require(mhat_phi_sq > 0.0, "DOMAIN", "mhat_phi_sq must be strictly positive", issues)
    require(a_f > 0.0, "DOMAIN", "a_F must be strictly positive in active M1", issues)
    require(z_sigma_hat > 0.0, "DOMAIN", "z_sigma_hat must be strictly positive", issues)
    require(q_hat > 0.0, "DOMAIN", "q_hat must be strictly positive", issues)
    return issues


def validate_contract(data: dict[str, Any], root: pathlib.Path = ROOT) -> list[ContractIssue]:
    issues: list[ContractIssue] = []

    require(
        data.get("schema") == "universelab.hzt-m0-s6-c-phys-m1.function-freeze.v0.1",
        "SCHEMA",
        "unexpected schema",
        issues,
    )
    require(data.get("track_id") == "MD2S-R1-C-PHYS", "TRACK", "track drift", issues)
    require(data.get("model_id") == "HZT-M0-S6-C-PHYS-M1", "TRACK", "model identity drift", issues)
    require(
        data.get("classification") == "VERSIONED_PHYSICAL_CANDIDATE_MODEL_SELECTION_NOT_DERIVATION",
        "GOVERNANCE",
        "model-selection classification drift",
        issues,
    )
    require(data.get("physical_evidence_effect") == "NONE", "GOVERNANCE", "physical evidence drift", issues)
    require(data.get("solver_authorized") is False, "GOVERNANCE", "solver must remain unauthorized", issues)

    dependencies = data.get("dependencies")
    require(isinstance(dependencies, list) and bool(dependencies), "PROVENANCE", "dependencies required", issues)
    if isinstance(dependencies, list):
        for item in dependencies:
            require(isinstance(item, str) and bool(item), "PROVENANCE", "invalid dependency path", issues)
            if isinstance(item, str):
                require((root / item).is_file(), "PROVENANCE", f"missing dependency: {item}", issues)

    firewall = data.get("track_firewall", {})
    require(firewall.get("historical_A0_identity") == "NOT_CLAIMED", "FIREWALL", "A0 identity drift", issues)
    require(firewall.get("C1_V_identity") == "NOT_CLAIMED", "FIREWALL", "C1-V identity drift", issues)
    require(firewall.get("C1_V_parameter_values_migrated") is False, "FIREWALL", "C1-V parameter migration", issues)
    require(firewall.get("C1_V_numerical_results_used") is False, "FIREWALL", "C1-V numerical migration", issues)

    conventions = data.get("field_and_unit_conventions", {})
    require(conventions.get("varphi_definition") == "varphi=phi/M6^2", "DIMENSION", "varphi definition drift", issues)
    require(conventions.get("scalar_domain") == "R", "DOMAIN", "scalar domain must be R", issues)
    require(conventions.get("canonical_scalar_kinetic") == "Z_phi=1", "DIMENSION", "canonical kinetic drift", issues)

    functions = data.get("exact_functions", {})
    expected_formulas = {
        "U": "U(phi)=0.5*mhat_phi_sq*M6^6*varphi^2",
        "Z_F": "Z_F(phi)=exp(-2*a_F*varphi)",
        "lambda": "lambda(phi)=lambda_hat*M6^5",
        "Z_sigma": "Z_sigma(phi)=z_sigma_hat*M6^3",
    }
    expected_dimensions = {"U": "M^6", "Z_F": "1", "lambda": "M^5", "Z_sigma": "M^3"}
    for name, formula in expected_formulas.items():
        require(name in functions, "SCHEMA", f"missing exact function {name}", issues)
        entry = functions.get(name, {})
        require(entry.get("formula") == formula, "MODEL", f"{name} formula drift", issues)
        require(entry.get("dimension") == expected_dimensions[name], "DIMENSION", f"{name} dimension drift", issues)

    u_entry = functions.get("U", {})
    require(u_entry.get("derivatives", {}).get("U_at_0") == "0", "REDUNDANCY", "U(0) must vanish", issues)
    require(
        "no_constant_term_to_avoid_double_counting_Lambda6" in u_entry.get("properties", []),
        "REDUNDANCY",
        "vacuum-constant no-double-counting rule missing",
        issues,
    )
    require(functions.get("Z_F", {}).get("derivatives", {}).get("Z_F_at_0") == "1", "REDUNDANCY", "Z_F(0) normalization drift", issues)
    require(
        functions.get("Z_sigma", {}).get("parameters", {}).get("z_sigma_hat")
        == "strictly_positive_dimensionless",
        "DOMAIN",
        "Z_sigma positivity domain drift",
        issues,
    )
    require(
        functions.get("lambda", {}).get("derivatives", {}).get("d_lambda_dphi") == "0",
        "MODEL",
        "localized scalar source reintroduced through lambda",
        issues,
    )
    require(
        functions.get("Z_sigma", {}).get("derivatives", {}).get("d_Z_sigma_dphi") == "0",
        "MODEL",
        "localized scalar source reintroduced through Z_sigma",
        issues,
    )

    vector = data.get("dimensionless_model_parameter_vector", {})
    expected_vector = [
        "Lambda_hat",
        "mhat_phi_sq",
        "a_F",
        "lambda_hat",
        "z_sigma_hat",
        "q_hat",
    ]
    require(vector.get("ordered_parameters") == expected_vector, "P0", "parameter vector drift", issues)
    require(vector.get("count") == 6, "P0", "model-shape parameter count must remain six", issues)
    require(vector.get("silent_promotion_to_shooting_variables") is False, "P0", "model parameters promoted to shooting", issues)

    charge = data.get("charge_normalization", {})
    require(charge.get("q_ref") == "q_hat/M6", "CHARGE", "q_ref normalization drift", issues)
    require(charge.get("q_sigma") == "m_sigma*q_ref", "CHARGE", "charge lattice drift", issues)
    require(charge.get("q_hat_can_be_set_to_one_without_model_change") is False, "CHARGE", "q_hat incorrectly treated as gauge", issues)

    redundancy = data.get("redundancy_audit", {})
    require(
        redundancy.get("scalar_reflection")
        == "a_F_positive_selects_one_representative_of_phi_to_minus_phi_equivalence",
        "REDUNDANCY",
        "scalar reflection convention drift",
        issues,
    )
    require(
        redundancy.get("bulk_vacuum_constant")
        == "ASSIGNED_ONLY_TO_Lambda6_BECAUSE_U_AT_ZERO_EQUALS_ZERO",
        "REDUNDANCY",
        "vacuum allocation drift",
        issues,
    )

    # Functional and derivative checks at a representative valid parameter point.
    m2 = 2.75
    a_f = 0.41
    zsig = 1.3
    qhat = 0.7
    issues.extend(
        validate_parameter_point(
            lambda_hat=-0.2,
            lambda6_hat=0.15,
            mhat_phi_sq=m2,
            a_f=a_f,
            z_sigma_hat=zsig,
            q_hat=qhat,
        )
    )
    for value in (-4.0, -1.0, 0.0, 1.0, 4.0):
        require(u(value, m2) >= 0.0, "POSITIVITY", "U lost lower bound", issues)
        require(z_f(value, a_f) > 0.0, "POSITIVITY", "Z_F lost positivity", issues)
    require(abs(u(0.0, m2)) < 1e-15, "POSITIVITY", "U minimum not at zero", issues)
    require(abs(z_f(0.0, a_f) - 1.0) < 1e-15, "REDUNDANCY", "Z_F(0) != 1", issues)

    h = 1e-5
    du0 = (u(h, m2) - u(-h, m2)) / (2.0 * h)
    d2u0 = (u(h, m2) - 2.0 * u(0.0, m2) + u(-h, m2)) / (h * h)
    dlogzf = (math.log(z_f(h, a_f)) - math.log(z_f(-h, a_f))) / (2.0 * h)
    require(abs(du0) < 1e-10, "DERIVATIVE", "U'(0) mismatch", issues)
    require(abs(d2u0 - m2) < 1e-5, "DERIVATIVE", "U''(0) mismatch", issues)
    require(abs(dlogzf + 2.0 * a_f) < 1e-10, "DERIVATIVE", "d ln Z_F/dvarphi mismatch", issues)

    # Leading pole identities from the specialized equations.
    warp = -0.13
    varphi0 = 0.27
    q_s = 0.61
    k4 = 0.02
    lambda_hat_dimless = -0.19
    density = rho_f(q_s, warp, varphi0, a_f)
    a2 = (6.0 * k4 * math.exp(-2.0 * warp) - lambda_hat_dimless - u(varphi0, m2) + density) / 8.0
    f2 = (m2 * varphi0 - 2.0 * a_f * density) / 4.0
    g2 = 0.5 * q_s * math.exp(-4.0 * warp + 2.0 * a_f * varphi0)
    require(
        abs(8.0 * a2 - (6.0 * k4 * math.exp(-2.0 * warp) - lambda_hat_dimless - u(varphi0, m2) + density)) < 1e-12,
        "POLE",
        "warp pole coefficient identity failed",
        issues,
    )
    require(abs(4.0 * f2 - (m2 * varphi0 - 2.0 * a_f * density)) < 1e-12, "POLE", "scalar pole coefficient identity failed", issues)
    require(abs(2.0 * g2 - q_s * math.exp(-4.0 * warp + 2.0 * a_f * varphi0)) < 1e-12, "POLE", "gauge pole coefficient identity failed", issues)

    specialization = data.get("dimensionless_specialization", {})
    require(
        specialization.get("cap_quantities", {}).get("R_scalar")
        == "varphi_N_x_at_cap+varphi_S_x_at_cap=0",
        "BOUNDARY",
        "source-free scalar junction drift",
        issues,
    )
    require(
        specialization.get("cap_quantities", {}).get("R_patch")
        == "a_chi_N_at_cap-a_chi_S_at_cap-N_F/q_hat=0",
        "BOUNDARY",
        "patch residual drift",
        issues,
    )

    gates = data.get("gate_state", {})
    expected_gates = {
        "FUNCTION_SELECTION": "PASS_POSTULATED_MODEL_FAMILY",
        "MF_001_BULK_FUNCTIONS": "FROZEN_FOR_C_PHYS_M1",
        "MF_002_CAP_FUNCTIONS": "FROZEN_FOR_C_PHYS_M1",
        "R1.0": "ACTIVE_OPERATOR_CLOSURE_REMAINING",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "continuum_BVP_Jacobian": "NOT_PROVEN",
        "physical_background": "NOT_ESTABLISHED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    for gate, expected in expected_gates.items():
        require(gates.get(gate) == expected, "GATE", f"{gate} drift: expected {expected}", issues)

    next_block = data.get("next_block", {})
    require(next_block.get("id") == "C-PHYS-R1.0-OPERATOR-2A", "SEQUENCE", "next block drift", issues)

    return issues


def validate_repository(root: pathlib.Path = ROOT) -> list[ContractIssue]:
    path = root / CONTRACT_PATH
    if not path.is_file():
        return [ContractIssue("SCHEMA", f"missing contract: {CONTRACT_PATH}")]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [ContractIssue("SCHEMA", f"invalid JSON: {exc}")]
    return validate_contract(data, root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit machine-readable result")
    args = parser.parse_args(argv)
    issues = validate_repository(ROOT)
    if args.json:
        print(
            json.dumps(
                {
                    "schema": "universelab.c-phys-m1-function-freeze-validation.v0.1",
                    "status": "PASS" if not issues else "FAIL",
                    "issues": [issue.__dict__ for issue in issues],
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        if issues:
            for issue in issues:
                print(issue.render(), file=sys.stderr)
        else:
            print("C-PHYS-M1 function freeze contract: PASS")
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
