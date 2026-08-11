#!/usr/bin/env python3
"""ULSH-01 / WP2-H2 target hardening v1.2, no-solve audit by default.

This wrapper preserves the frozen WP2-H v1.1 numerical schedule and adds the
RR2-B04 fail-closed >=80-bit residual audit for every candidate that would
otherwise receive numerical-candidate status. Total wall-clock hard enforcement
is supplied by the v1.2 transaction process supervisor, which includes this
wrapper's post-solve finalization and precision audit.

Direct invocation performs audit only. No numerical backend is imported and no
physical solve is executed by audit/CI.
"""
from __future__ import annotations

from fractions import Fraction
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_TARGET_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.1.py"
PREREG_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"

_SPEC = importlib.util.spec_from_file_location("ulsh_wp2_h1_target", BASE_TARGET_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("unable to import WP2-H v1.1 target")
BASE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = BASE
_SPEC.loader.exec_module(BASE)

RUN_ID = BASE.RUN_ID
FROZEN_PAYLOAD_SHA256 = BASE.FROZEN_PAYLOAD_SHA256
NODE_COUNTS = BASE.NODE_COUNTS
PLANNED_ENTRY_COUNT = BASE.PLANNED_ENTRY_COUNT
TargetExecutionCapability = BASE.TargetExecutionCapability

PASS_CLASS = "NUMERICAL_CANDIDATE_BACKGROUND_DIAGNOSTIC"
REJECT_CLASS = "NUMERICAL_ROOT_REJECTED_BY_QA"
MULTI_CLASS = "MULTIPLE_NUMERICAL_CANDIDATE_BACKGROUNDS_DIAGNOSTIC"
NO_CANDIDATE_CLASS = "NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL"


class H2PrecisionAuditError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise H2PrecisionAuditError(f"top-level JSON object required: {path}")
    return value


def build_schedule() -> list[dict[str, Any]]:
    return BASE.build_schedule()


def schedule_sha256() -> str:
    return BASE.schedule_sha256()


def frozen_payload() -> dict[str, Any]:
    return BASE.frozen_payload()


def _ld(value: Any, np: Any) -> Any:
    if isinstance(value, str) and "/" in value:
        fraction = Fraction(value)
        return np.longdouble(fraction.numerator) / np.longdouble(fraction.denominator)
    return np.longdouble(str(value))


def _longdouble_grid(node_count: int, np: Any) -> tuple[Any, Any, Any]:
    if node_count < 3:
        raise H2PrecisionAuditError("node_count must be >=3")
    degree = node_count - 1
    j = np.arange(node_count, dtype=np.longdouble)
    pi = np.arccos(np.longdouble(-1))
    x_desc = np.cos(pi * j / np.longdouble(degree))
    tau_desc = (x_desc + np.longdouble(1)) / np.longdouble(2)
    weights_desc = np.where((np.arange(node_count) % 2) == 0, np.longdouble(1), np.longdouble(-1)).astype(np.longdouble)
    weights_desc[0] *= np.longdouble("0.5")
    weights_desc[-1] *= np.longdouble("0.5")
    tau = tau_desc[::-1].copy()
    weights = weights_desc[::-1].copy()
    D = np.zeros((node_count, node_count), dtype=np.longdouble)
    for i in range(node_count):
        for k in range(node_count):
            if i != k:
                D[i, k] = weights[k] / (weights[i] * (tau[i] - tau[k]))
        D[i, i] = -np.sum(D[i, :], dtype=np.longdouble)
    return tau, D, D @ D


def _evaluate_region(fields: list[Any], *, A0: Any, varphi0: Any, rho: Any, q: Any, k4: Any, tau: Any, D: Any, D2: Any, model: dict[str, Any], np: Any) -> dict[str, Any]:
    u_A, u_ell, u_varphi, u_g = fields
    u_A_t, u_A_tt = D @ u_A, D2 @ u_A
    u_ell_t, u_ell_tt = D @ u_ell, D2 @ u_ell
    u_varphi_t, u_varphi_tt = D @ u_varphi, D2 @ u_varphi
    u_g_t = D @ u_g
    one, two, three, four = map(np.longdouble, (1, 2, 3, 4))
    six, eight, ten = map(np.longdouble, (6, 8, 10))
    half = np.longdouble("0.5")
    Lhat = one + tau * u_ell
    Lhat_t = u_ell + tau * u_ell_t
    Lhat_tt = two * u_ell_t + tau * u_ell_tt
    A = A0 + tau * u_A
    varphi = varphi0 + tau * u_varphi
    sqrt_tau = np.sqrt(tau)
    A_x = two * sqrt_tau / rho * (u_A + tau * u_A_t)
    A_xx = two / rho**2 * (u_A + np.longdouble(5) * tau * u_A_t + two * tau**2 * u_A_tt)
    varphi_x = two * sqrt_tau / rho * (u_varphi + tau * u_varphi_t)
    varphi_xx = two / rho**2 * (u_varphi + np.longdouble(5) * tau * u_varphi_t + two * tau**2 * u_varphi_tt)
    ell = rho * sqrt_tau * Lhat
    ell_x = Lhat + two * tau * Lhat_t
    ell_xx_over_ell = two / rho**2 * (three * Lhat_t + two * tau * Lhat_tt) / Lhat
    A_x_ell_x_over_ell = two / rho**2 * ((u_A + tau * u_A_t) * (Lhat + two * tau * Lhat_t) / Lhat)
    varphi_x_ell_x_over_ell = two / rho**2 * ((u_varphi + tau * u_varphi_t) * (Lhat + two * tau * Lhat_t) / Lhat)
    a_chi = tau * u_g
    rho_F = half * q**2 * np.exp(-eight * A + two * model["a_F"] * varphi)
    exp_minus_2A = np.exp(-two * A)
    F_A = four * A_xx + ten * A_x**2 - six * k4 * exp_minus_2A + model["Lambda_hat"] + half * varphi_x**2 + half * model["mhat_phi_sq"] * varphi**2 - rho_F
    F_ell = ell_xx_over_ell + three * A_xx + six * A_x**2 + three * A_x_ell_x_over_ell - three * k4 * exp_minus_2A + model["Lambda_hat"] + half * varphi_x**2 + half * model["mhat_phi_sq"] * varphi**2 + rho_F
    F_varphi = varphi_xx + four * A_x * varphi_x + varphi_x_ell_x_over_ell - model["mhat_phi_sq"] * varphi + two * model["a_F"] * rho_F
    F_gauge = two / rho * (u_g + tau * u_g_t) - q * rho * Lhat * np.exp(-four * A + two * model["a_F"] * varphi)
    constraint = -six * k4 * exp_minus_2A + six * A_x**2 + model["Lambda_hat"] + four * A_x_ell_x_over_ell - half * varphi_x**2 + half * model["mhat_phi_sq"] * varphi**2 - rho_F
    return {"A": A, "ell": ell, "varphi": varphi, "a_chi": a_chi, "A_x": A_x, "ell_x": ell_x, "varphi_x": varphi_x, "Lhat": Lhat, "residual_blocks": (F_A, F_ell, F_varphi, F_gauge), "constraint": constraint}


def _longdouble_candidate_audit(profile: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    import numpy as np
    finfo = np.finfo(np.longdouble)
    mantissa_bits = int(finfo.nmant) + 1
    if mantissa_bits < 64:
        raise H2PrecisionAuditError(f">=80-bit extended precision unavailable: longdouble mantissa={mantissa_bits} bits")
    node_count = int(profile["node_count"])
    if node_count != 96:
        raise H2PrecisionAuditError("higher-precision acceptance audit requires N=96 candidate state")
    tau, D, D2 = _longdouble_grid(node_count, np)
    regularized = profile["regularized_profiles"]
    north_fields = [np.asarray(values, dtype=np.longdouble) for values in regularized["north"]]
    south_fields = [np.asarray(values, dtype=np.longdouble) for values in regularized["south"]]
    augmented = profile["augmented_variables"]
    p = payload["model_parameters_ordered"]
    t = payload["topological_sector_ordered"]
    model = {name: _ld(p[name], np) for name in ("Lambda_hat", "mhat_phi_sq", "a_F", "lambda_hat", "z_sigma_hat", "q_hat")}
    required_topology = ("N_F", "N_sigma", "m_sigma")
    if any(key not in t for key in required_topology):
        raise H2PrecisionAuditError(f"topological payload lacks primary-backend keys {required_topology}")
    N_F, N_sigma, m_sigma = int(t["N_F"]), int(t["N_sigma"]), int(t["m_sigma"])
    varphi_N_0 = _ld(augmented["varphi_N_0"], np)
    q_N = _ld(augmented["q_N"], np)
    A_S_0 = _ld(augmented["A_S_0"], np)
    varphi_S_0 = _ld(augmented["varphi_S_0"], np)
    q_S = _ld(augmented["q_S"], np)
    rho_N = _ld(augmented["rho_N"], np)
    rho_S = _ld(augmented["rho_S"], np)
    k4 = _ld(augmented["k4"], np)
    north = _evaluate_region(north_fields, A0=np.longdouble(0), varphi0=varphi_N_0, rho=rho_N, q=q_N, k4=k4, tau=tau, D=D, D2=D2, model=model, np=np)
    south = _evaluate_region(south_fields, A0=A_S_0, varphi0=varphi_S_0, rho=rho_S, q=q_S, k4=k4, tau=tau, D=D, D2=D2, model=model, np=np)
    i = -1
    two, three, four = map(np.longdouble, (2, 3, 4))
    half = np.longdouble("0.5")
    ell_sigma = half * (north["ell"][i] + south["ell"][i])
    A_sum = north["A_x"][i] + south["A_x"][i]
    ell_sum = (north["ell_x"][i] + south["ell_x"][i]) / ell_sigma
    d_chi = np.longdouble(N_sigma) - np.longdouble(m_sigma) * model["q_hat"] * south["a_chi"][i]
    Y_sigma = model["z_sigma_hat"] * d_chi**2 / ell_sigma**2
    boundary = np.asarray((north["A"][i] - south["A"][i], north["ell"][i] - south["ell"][i], north["varphi"][i] - south["varphi"][i], north["a_chi"][i] - south["a_chi"][i] - np.longdouble(N_F) / model["q_hat"], -three * A_sum - ell_sum + model["lambda_hat"] + half * Y_sigma, -four * A_sum + model["lambda_hat"] - half * Y_sigma, north["varphi_x"][i] + south["varphi_x"][i], q_N * np.exp(-four * north["A"][i]) / ell_sigma + q_S * np.exp(-four * south["A"][i]) / ell_sigma - np.longdouble(m_sigma) * model["q_hat"] * model["z_sigma_hat"] * d_chi / ell_sigma**2), dtype=np.longdouble)
    bulk = np.concatenate([*north["residual_blocks"], *south["residual_blocks"]])
    constraint = np.concatenate([north["constraint"], south["constraint"]])
    bulk_max = np.max(np.abs(bulk))
    boundary_max = np.max(np.abs(boundary))
    constraint_max = np.max(np.abs(constraint))
    thresholds = load_json(PREREG_PATH)["acceptance_thresholds"]
    bulk_limit = _ld(thresholds["bulk_residual_max"], np)
    boundary_limit = _ld(thresholds["boundary_residual_max"], np)
    constraint_limit = _ld(thresholds["rr_constraint_max"], np)
    passed = bool(np.isfinite(bulk_max) and np.isfinite(boundary_max) and np.isfinite(constraint_max) and bulk_max <= bulk_limit and boundary_max <= boundary_limit and constraint_max <= constraint_limit)
    return {"required_for_every_otherwise_passing_candidate": True, "precision_backend": "numpy.longdouble residual re-evaluation", "mantissa_bits": mantissa_bits, "epsilon": str(finfo.eps), "node_count": node_count, "bulk_residual_max": str(bulk_max), "boundary_residual_max": str(boundary_max), "constraint_max": str(constraint_max), "bulk_limit": str(bulk_limit), "boundary_limit": str(boundary_limit), "constraint_limit": str(constraint_limit), "passed": passed, "interpretation": "NUMERICAL_PRECISION_QA_ONLY_NOT_PHYSICAL_CONFIRMATION"}


def _apply_precision_gate(raw: dict[str, Any]) -> dict[str, Any]:
    payload = frozen_payload()
    audits: dict[str, dict[str, Any]] = {}
    passing_after_precision: set[str] = set()
    for candidate in raw.get("candidate_inventory", []):
        candidate_id = str(candidate.get("candidate_id", ""))
        if candidate.get("classification") != PASS_CLASS:
            candidate["higher_precision_audit"] = {"required": False, "reason": "candidate_not_otherwise_passing"}
            continue
        profile = raw.get("profile_artifacts", {}).get(candidate_id)
        if not isinstance(profile, dict):
            audit = {"required": True, "passed": False, "failure": "MISSING_N96_PROFILE_ARTIFACT", "interpretation": "FAIL_CLOSED_NO_BORDERLINE_ACCEPTANCE"}
        else:
            try:
                audit = _longdouble_candidate_audit(profile, payload)
                audit["required"] = True
            except Exception as exc:
                audit = {"required": True, "passed": False, "failure": f"{type(exc).__name__}: {exc}", "interpretation": "FAIL_CLOSED_NO_BORDERLINE_ACCEPTANCE"}
        audits[candidate_id] = audit
        candidate["higher_precision_audit"] = audit
        if audit.get("passed") is True:
            passing_after_precision.add(candidate_id)
        else:
            candidate["classification"] = REJECT_CLASS
    acceptance = raw.setdefault("acceptance_audit", {})
    original_passing = [str(item) for item in acceptance.get("passing_candidate_ids", [])]
    original_distinct = [str(item) for item in acceptance.get("distinct_passing_candidate_ids", [])]
    acceptance["pre_precision_passing_candidate_ids"] = original_passing
    acceptance["pre_precision_distinct_passing_candidate_ids"] = original_distinct
    acceptance["higher_precision_audits"] = audits
    acceptance["higher_precision_policy"] = "CONSERVATIVE_ALL_OTHERWISE_PASSING_CANDIDATES_REQUIRE_>=80BIT_RESIDUAL_REEVALUATION"
    acceptance["passing_candidate_ids"] = [item for item in original_passing if item in passing_after_precision]
    acceptance["distinct_passing_candidate_ids"] = [item for item in original_distinct if item in passing_after_precision]
    distinct_count = len(acceptance["distinct_passing_candidate_ids"])
    if distinct_count > 1:
        raw["final_classification"] = MULTI_CLASS
    elif distinct_count == 1:
        raw["final_classification"] = PASS_CLASS
    elif raw.get("candidate_inventory"):
        raw["final_classification"] = REJECT_CLASS
    else:
        raw["final_classification"] = NO_CANDIDATE_CLASS
    raw["higher_precision_audit"] = {"policy": acceptance["higher_precision_policy"], "candidate_audits": audits, "passing_after_precision": acceptance["passing_candidate_ids"], "physical_evidence_effect": "NONE"}
    return raw


def audit_target() -> dict[str, Any]:
    base = BASE.audit_target()
    prereg = load_json(PREREG_PATH)
    if prereg["primary_discretization"]["higher_precision_audit"] != "80_BIT_OR_GREATER_REQUIRED_FOR_ANY_BORDERLINE_ACCEPTANCE":
        raise H2PrecisionAuditError("preregistered higher-precision requirement drift")
    return {"status": "PASS_WP2_H2_TARGET_HARDENING_NO_SOLVE", "base_status": base["status"], "run_id": RUN_ID, "frozen_payload_sha256": FROZEN_PAYLOAD_SHA256, "schedule_sha256": schedule_sha256(), "planned_entry_count": PLANNED_ENTRY_COUNT, "a_F": base["a_F"], "higher_precision_audit_required": True, "higher_precision_audit_policy": "all otherwise-passing N=96 candidates are re-evaluated in numpy.longdouble; lack of >=64 significand bits or audit failure rejects candidate fail-closed", "total_wall_clock_enforcement_owner": "WP2-H2_TRANSACTION_PROCESS_SUPERVISOR", "solver_imported": False, "solver_calls": 0, "physical_solve_executed": False, "physical_evidence_effect": "NONE"}


def execute_physical_schedule(capability: TargetExecutionCapability) -> dict[str, Any]:
    started = time.monotonic()
    raw = BASE.execute_physical_schedule(capability)
    raw = _apply_precision_gate(raw)
    raw["execution_elapsed_wall_clock_seconds"] = time.monotonic() - started
    raw["wp2_h2_precision_gate_applied"] = True
    raw["physical_evidence_effect"] = "NONE"
    return raw


def main() -> int:
    print(json.dumps(audit_target(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
