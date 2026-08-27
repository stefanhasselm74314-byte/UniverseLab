#!/usr/bin/env python3
"""ULSH-01 M1/C1 canonical 8x8 backend interface v0.1.

Schema/patch binding only. This module MUST NOT execute a physical solver.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

TARGET_DIGEST = "237c4b5e08a2106e13e985c4af7925f1899e2ae2e4b7253c7ab73cc2db5f1823"
MODEL_ID = "HZT-M0-S6-C-PHYS-M1"
PROFILE_ORDER = ("A_s", "ell_s", "varphi_s", "a_chi_s")
FIXED_SECTOR_ORDER = ("N_F", "N_sigma", "m_sigma")
M1_PARAMETER_ORDER = ("Lambda_hat", "mhat_phi_sq", "a_F", "lambda_hat", "z_sigma_hat", "q_hat")
UNKNOWN_ORDER = ("varphi_N_0", "q_N", "A_S_0", "varphi_S_0", "q_S", "rho_N", "rho_S", "k4")
BULK_RESIDUAL_ORDER = ("E_A", "E_ell", "E_varphi", "E_gauge")
BOUNDARY_RESIDUAL_ORDER = ("R_A", "R_ell", "R_varphi", "R_patch", "R_4d", "R_chi", "R_scalar", "R_gauge_local")
INTERFACE_TRACE_ORDER = ("A_N_x_cap", "A_S_x_cap", "ell_N_x_over_ellSigma_cap", "ell_S_x_over_ellSigma_cap")
FORBIDDEN_CANONICAL_KEYS = {
    "Sigma_FT",
    "s_hat",
    "c_N",
    "c_S",
    "Lambda_layer_over_Lambda_ref",
    "mSigma2_over_mref2",
    "lambdaSigma",
    "gSigma",
}

PHYSICAL_EXECUTION_AUTHORIZED = False
PHYSICAL_BACKEND_IMPORT_ALLOWED = False
TARGET_SOLVE_ALLOWED = False
RANK_R_CLAIM_ALLOWED = False
PHYSICAL_EVIDENCE_EFFECT = "NONE"


class ContractError(ValueError):
    pass


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def canonical_target_digest(target: dict[str, Any]) -> str:
    semantics = target.get("target_semantics")
    if not isinstance(semantics, dict):
        raise ContractError("target_semantics missing")
    canonical = json.dumps(
        semantics,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def verify_target(target: dict[str, Any]) -> None:
    actual = canonical_target_digest(target)
    recorded = target.get("target_contract_digest", {}).get("sha256")
    if actual != TARGET_DIGEST or recorded != TARGET_DIGEST:
        raise ContractError(f"target digest mismatch: actual={actual} recorded={recorded}")

    sem = target["target_semantics"]
    if sem.get("model_id") != MODEL_ID:
        raise ContractError("model_id mismatch")
    if tuple(sem.get("field_content", {}).get("regional_background_profiles", [])) != PROFILE_ORDER:
        raise ContractError("regional profile order mismatch")
    if tuple(sem.get("fixed_sector", {}).get("ordered", [])) != FIXED_SECTOR_ORDER:
        raise ContractError("fixed discrete-sector order mismatch")
    if tuple(sem.get("m1_model", {}).get("parameter_order", [])) != M1_PARAMETER_ORDER:
        raise ContractError("M1 parameter order mismatch")
    if tuple(sem.get("continuous_unknown_vector", [])) != UNKNOWN_ORDER:
        raise ContractError("continuous unknown order mismatch")
    if tuple(sem.get("bulk_operator", {}).get("residual_order", [])) != BULK_RESIDUAL_ORDER:
        raise ContractError("bulk residual order mismatch")
    if tuple(sem.get("boundary_operator", {}).get("residual_order", [])) != BOUNDARY_RESIDUAL_ORDER:
        raise ContractError("boundary residual order mismatch")

    excluded = set(sem.get("field_content", {}).get("noncanonical_excluded_from_target", []))
    if not {"Sigma_FT", "c_N", "c_S"}.issubset(excluded):
        raise ContractError("noncanonical field firewall incomplete")
    if sem.get("rr_constraint", {}).get("role") != "PROPAGATED_QA_CHANNEL_NOT_ADDITIONAL_NONLINEAR_OR_ENDPOINT_RESIDUAL":
        raise ContractError("C_rr role mismatch")
    if sem.get("boundary_operator", {}).get("not_additional_residuals", {}).get("R_flux") != "equivalent_to_R_patch":
        raise ContractError("R_flux/R_patch counting contract mismatch")


def verify_interface_contract(contract: dict[str, Any]) -> None:
    authority = contract.get("authority", {})
    interface = contract.get("interface", {})
    patch = contract.get("patch_binding", {})
    firewall = contract.get("firewall", {})

    if authority.get("target_digest_sha256") != TARGET_DIGEST:
        raise ContractError("interface target digest mismatch")
    if tuple(interface.get("profile_order_per_region", [])) != PROFILE_ORDER:
        raise ContractError("interface profile order mismatch")
    if tuple(interface.get("fixed_discrete_sector_order", [])) != FIXED_SECTOR_ORDER:
        raise ContractError("interface fixed sector mismatch")
    if tuple(interface.get("m1_parameter_order", [])) != M1_PARAMETER_ORDER:
        raise ContractError("interface M1 parameter order mismatch")
    if tuple(interface.get("continuous_unknown_order", [])) != UNKNOWN_ORDER:
        raise ContractError("interface unknown order mismatch")
    if tuple(interface.get("boundary_residual_order", [])) != BOUNDARY_RESIDUAL_ORDER:
        raise ContractError("interface boundary order mismatch")
    if patch.get("representation") != "a_chi_Sigma := a_chi_S(cap)":
        raise ContractError("a_chi_Sigma patch representation mismatch")
    if patch.get("R_patch_count") != 1 or patch.get("R_flux_additional_residual_allowed") is not False:
        raise ContractError("patch residual counting mismatch")
    if firewall.get("solver_authorized") is not False or firewall.get("physical_evidence_effect") != "NONE":
        raise ContractError("execution firewall mismatch")


def _finite(value: Any, name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
        raise ContractError(f"{name} must be finite numeric")
    return float(value)


def patch_binding(
    *,
    a_chi_N_cap: float,
    a_chi_S_cap: float,
    N_F: int,
    q_hat: float,
    N_sigma: int,
    m_sigma: int,
) -> dict[str, float]:
    """Evaluate only the frozen patch representation; no physical solve occurs."""
    a_n = _finite(a_chi_N_cap, "a_chi_N_cap")
    a_s = _finite(a_chi_S_cap, "a_chi_S_cap")
    q = _finite(q_hat, "q_hat")
    if q <= 0:
        raise ContractError("q_hat must be strictly positive")
    if not isinstance(N_F, int) or isinstance(N_F, bool):
        raise ContractError("N_F must be integer")
    if not isinstance(N_sigma, int) or isinstance(N_sigma, bool):
        raise ContractError("N_sigma must be integer")
    if not isinstance(m_sigma, int) or isinstance(m_sigma, bool) or m_sigma <= 0:
        raise ContractError("m_sigma must be positive integer")

    a_chi_sigma = a_s
    r_patch = a_n - a_s - N_F / q
    d_chi = N_sigma - m_sigma * q * a_chi_sigma
    return {
        "a_chi_Sigma": a_chi_sigma,
        "R_patch": r_patch,
        "d_chi": d_chi,
    }


def _walk_keys(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def reject_noncanonical_keys(payload: dict[str, Any]) -> None:
    found = sorted(FORBIDDEN_CANONICAL_KEYS.intersection(_walk_keys(payload)))
    if found:
        raise ContractError(f"noncanonical keys forbidden in M1/C1 8x8 payload: {found}")


def verify_result_schema(schema: dict[str, Any]) -> None:
    if schema.get("target_contract_digest_sha256") != TARGET_DIGEST:
        raise ContractError("result schema target digest mismatch")
    solution = schema.get("solution", {})
    if tuple(solution.get("continuous_unknown_order", [])) != UNKNOWN_ORDER:
        raise ContractError("result unknown order mismatch")
    if tuple(solution.get("boundary_residual_order", [])) != BOUNDARY_RESIDUAL_ORDER:
        raise ContractError("result boundary order mismatch")
    traces = schema.get("interface_traces", {})
    if any(name not in traces for name in INTERFACE_TRACE_ORDER):
        raise ContractError("one-sided cap trace coverage incomplete")
    patch = schema.get("patch_binding", {})
    if patch.get("a_chi_Sigma_representation") != "a_chi_S(cap)":
        raise ContractError("result patch representation mismatch")
    if patch.get("R_patch_counted_once") is not True or patch.get("R_flux_additional_residual") is not False:
        raise ContractError("result patch counting mismatch")
    governance = schema.get("governance", {})
    if governance.get("solver_authorized") is not False:
        raise ContractError("result schema must remain non-authorized")
    if governance.get("physical_evidence_effect") != "NONE":
        raise ContractError("result schema physical evidence firewall mismatch")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ULSH-01 M1/C1 8x8 interface contracts without solver execution")
    parser.add_argument("--target", required=True)
    parser.add_argument("--interface-contract", required=True)
    parser.add_argument("--result-schema", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    verify_target(load_json(args.target))
    verify_interface_contract(load_json(args.interface_contract))
    verify_result_schema(load_json(args.result_schema))

    out = {
        "status": "PASS_TARGET_BOUND_INTERFACE_SCHEMA_QA",
        "target_digest_sha256": TARGET_DIGEST,
        "solver_executed": False,
        "physical_execution_authorized": False,
        "rank_R_claim_allowed": False,
        "physical_evidence_effect": "NONE",
    }
    print(json.dumps(out, indent=2) if args.json else out["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
