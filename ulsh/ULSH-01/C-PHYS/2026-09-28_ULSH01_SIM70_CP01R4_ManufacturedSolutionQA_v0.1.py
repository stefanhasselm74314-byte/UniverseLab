#!/usr/bin/env python3
"""SIM-70 manufactured-solution/reference QA for the frozen CP01R4 operator.

QA_ONLY / NO_PHYSICAL_EVIDENCE.

This module does not solve the BVP.  It evaluates manufactured regularized
profiles against an independently assembled analytic residual reference and
therefore tests the collocation differentiation and residual implementation.
"""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
BACKEND_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py"
RUN_INPUT_PATH = ROOT / "registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_RunInputRebind_v0.3.json"

SPEC = importlib.util.spec_from_file_location("sim70_cp01r4_backend", BACKEND_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load frozen CP01R4 primary backend")
BACKEND = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BACKEND
SPEC.loader.exec_module(BACKEND)

PHYSICAL_INTERPRETATION = "NONE"
CANONICAL_EFFECT = "NONE"
PHYSICAL_EVIDENCE_EFFECT = "NONE_QA_ONLY"


def _cheb_series(tau: np.ndarray, terms: dict[int, float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return value, d/dtau and d2/dtau2 for a Chebyshev series in x=2*tau-1."""
    degree = max(terms) if terms else 0
    coeff = np.zeros(degree + 1, dtype=float)
    for n, amplitude in terms.items():
        coeff[int(n)] = float(amplitude)
    x = 2.0 * np.asarray(tau, dtype=float) - 1.0
    d1 = np.polynomial.chebyshev.chebder(coeff, m=1)
    d2 = np.polynomial.chebyshev.chebder(coeff, m=2)
    value = np.polynomial.chebyshev.chebval(x, coeff)
    dtau = 2.0 * np.polynomial.chebyshev.chebval(x, d1)
    d2tau = 4.0 * np.polynomial.chebyshev.chebval(x, d2)
    return value, dtau, d2tau


def _profile_case(tau: np.ndarray, *, high_order: bool) -> dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    if high_order:
        specs = {
            "u_A": {0: 0.020, 2: 0.004, 40: 1.0e-7},
            "u_ell": {0: -0.040, 3: 0.003, 30: 1.0e-7},
            "u_varphi": {0: 0.030, 1: 0.004, 35: 1.0e-7},
            "u_g": {0: 0.060, 2: 0.003, 25: 1.0e-7},
        }
    else:
        specs = {
            "u_A": {0: 0.020, 1: -0.003, 4: 0.002},
            "u_ell": {0: -0.040, 2: 0.004, 5: 0.001},
            "u_varphi": {0: 0.030, 1: 0.005, 6: -0.001},
            "u_g": {0: 0.060, 3: -0.003, 6: 0.001},
        }
    return {name: _cheb_series(tau, terms) for name, terms in specs.items()}


def _reference_region(
    profile: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]],
    *,
    A0: float,
    varphi0: float,
    rho: float,
    q: float,
    k4: float,
    model: Any,
) -> dict[str, Any]:
    uA, uA_t, uA_tt = profile["u_A"]
    ul, ul_t, ul_tt = profile["u_ell"]
    uv, uv_t, uv_tt = profile["u_varphi"]
    ug, ug_t, _ = profile["u_g"]

    # All arrays share the same Chebyshev-Lobatto tau nodes.
    # Infer tau from T1 when possible; the caller attaches it explicitly below.
    tau = profile["_tau"][0]
    sqrt_tau = np.sqrt(tau)

    Lhat = 1.0 + tau * ul
    Lhat_t = ul + tau * ul_t
    Lhat_tt = 2.0 * ul_t + tau * ul_tt

    A = A0 + tau * uA
    varphi = varphi0 + tau * uv
    a_chi = tau * ug

    A_x = 2.0 * sqrt_tau / rho * (uA + tau * uA_t)
    A_xx = 2.0 / rho**2 * (uA + 5.0 * tau * uA_t + 2.0 * tau**2 * uA_tt)
    varphi_x = 2.0 * sqrt_tau / rho * (uv + tau * uv_t)
    varphi_xx = 2.0 / rho**2 * (uv + 5.0 * tau * uv_t + 2.0 * tau**2 * uv_tt)

    ell = rho * sqrt_tau * Lhat
    ell_x = Lhat + 2.0 * tau * Lhat_t
    ell_xx_over_ell = 2.0 / rho**2 * (3.0 * Lhat_t + 2.0 * tau * Lhat_tt) / Lhat
    A_x_ell_x_over_ell = 2.0 / rho**2 * (
        (uA + tau * uA_t) * (Lhat + 2.0 * tau * Lhat_t) / Lhat
    )
    varphi_x_ell_x_over_ell = 2.0 / rho**2 * (
        (uv + tau * uv_t) * (Lhat + 2.0 * tau * Lhat_t) / Lhat
    )

    rho_F = 0.5 * q**2 * np.exp(-8.0 * A + 2.0 * model.a_F * varphi)
    exp_minus_2A = np.exp(-2.0 * A)

    F_A = (
        4.0 * A_xx + 10.0 * A_x**2 - 6.0 * k4 * exp_minus_2A
        + model.Lambda_hat + 0.5 * varphi_x**2
        + 0.5 * model.mhat_phi_sq * varphi**2 - rho_F
    )
    F_ell = (
        ell_xx_over_ell + 3.0 * A_xx + 6.0 * A_x**2
        + 3.0 * A_x_ell_x_over_ell - 3.0 * k4 * exp_minus_2A
        + model.Lambda_hat + 0.5 * varphi_x**2
        + 0.5 * model.mhat_phi_sq * varphi**2 + rho_F
    )
    F_varphi = (
        varphi_xx + 4.0 * A_x * varphi_x + varphi_x_ell_x_over_ell
        - model.mhat_phi_sq * varphi + 2.0 * model.a_F * rho_F
    )
    F_gauge = (
        2.0 / rho * (ug + tau * ug_t)
        - q * rho * Lhat * np.exp(-4.0 * A + 2.0 * model.a_F * varphi)
    )
    constraint = (
        -6.0 * k4 * exp_minus_2A + 6.0 * A_x**2 + model.Lambda_hat
        + 4.0 * A_x_ell_x_over_ell - 0.5 * varphi_x**2
        + 0.5 * model.mhat_phi_sq * varphi**2 - rho_F
    )
    return {
        "A": A,
        "ell": ell,
        "varphi": varphi,
        "a_chi": a_chi,
        "A_x": A_x,
        "ell_x": ell_x,
        "varphi_x": varphi_x,
        "residual_blocks": (F_A, F_ell, F_varphi, F_gauge),
        "constraint": constraint,
    }


def _reference_boundary(north: dict[str, Any], south: dict[str, Any], parameters: np.ndarray, model: Any, sector: Any) -> np.ndarray:
    _, q_N, _, _, q_S, _, _, _ = parameters
    i = -1
    ell_sigma = 0.5 * (north["ell"][i] + south["ell"][i])
    A_sum = north["A_x"][i] + south["A_x"][i]
    ell_sum = (north["ell_x"][i] + south["ell_x"][i]) / ell_sigma
    d_chi = sector.N_sigma - sector.m_sigma * model.q_hat * south["a_chi"][i]
    Y_sigma = model.z_sigma_hat * d_chi**2 / ell_sigma**2
    return np.asarray(
        (
            north["A"][i] - south["A"][i],
            north["ell"][i] - south["ell"][i],
            north["varphi"][i] - south["varphi"][i],
            north["a_chi"][i] - south["a_chi"][i] - sector.N_F / model.q_hat,
            -3.0 * A_sum - ell_sum + model.lambda_hat + 0.5 * Y_sigma,
            -4.0 * A_sum + model.lambda_hat - 0.5 * Y_sigma,
            north["varphi_x"][i] + south["varphi_x"][i],
            q_N * np.exp(-4.0 * north["A"][i]) / ell_sigma
            + q_S * np.exp(-4.0 * south["A"][i]) / ell_sigma
            - sector.m_sigma * model.q_hat * model.z_sigma_hat * d_chi / ell_sigma**2,
        ),
        dtype=float,
    )


def manufactured_case(node_count: int, *, high_order: bool) -> dict[str, Any]:
    run_input = json.loads(RUN_INPUT_PATH.read_text(encoding="utf-8"))
    payload = run_input["frozen_run_payload"]
    model = BACKEND.model_from_payload(payload, control_a_F=False)
    sector = BACKEND.sector_from_payload(payload)

    grid = BACKEND.chebyshev_lobatto(node_count)
    tau = np.asarray(grid.tau, dtype=float)

    north_profile = _profile_case(tau, high_order=high_order)
    south_profile = _profile_case(tau, high_order=high_order)
    north_profile["_tau"] = (tau, tau, tau)
    south_profile["_tau"] = (tau, tau, tau)

    # Deliberately different regional signs/amplitudes while preserving regularity.
    south_profile["u_A"] = tuple(-0.8 * x for x in south_profile["u_A"])
    south_profile["u_varphi"] = tuple(-0.7 * x for x in south_profile["u_varphi"])
    south_profile["u_g"] = tuple(-0.9 * x for x in south_profile["u_g"])

    parameters = np.asarray([0.12, 0.31, -0.04, -0.08, -0.27, 1.30, 1.15, 0.025], dtype=float)
    varphi_N_0, q_N, A_S_0, varphi_S_0, q_S, rho_N, rho_S, k4 = parameters

    north_fields = [north_profile[name][0] for name in ("u_A", "u_ell", "u_varphi", "u_g")]
    south_fields = [south_profile[name][0] for name in ("u_A", "u_ell", "u_varphi", "u_g")]
    state = BACKEND.pack_state([north_fields, south_fields], parameters)

    numeric_vector, numeric_info = BACKEND.residual(state, node_count, model, sector)
    ref_n = _reference_region(
        north_profile,
        A0=0.0,
        varphi0=varphi_N_0,
        rho=rho_N,
        q=q_N,
        k4=k4,
        model=model,
    )
    ref_s = _reference_region(
        south_profile,
        A0=A_S_0,
        varphi0=varphi_S_0,
        rho=rho_S,
        q=q_S,
        k4=k4,
        model=model,
    )
    ref_boundary = _reference_boundary(ref_n, ref_s, parameters, model, sector)
    reference_vector = np.concatenate([*ref_n["residual_blocks"], *ref_s["residual_blocks"], ref_boundary])

    derivative_errors = []
    for numeric_region, ref in ((numeric_info["north"], ref_n), (numeric_info["south"], ref_s)):
        for name in ("A_x", "ell_x", "varphi_x"):
            derivative_errors.append(float(np.max(np.abs(np.asarray(getattr(numeric_region, name)) - ref[name]))))
        derivative_errors.append(float(np.max(np.abs(np.asarray(numeric_region.constraint) - ref["constraint"]))))

    absolute_error = float(np.max(np.abs(np.asarray(numeric_vector) - reference_vector)))
    reference_scale = max(1.0, float(np.max(np.abs(reference_vector))))
    relative_error = absolute_error / reference_scale

    return {
        "node_count": int(node_count),
        "high_order": bool(high_order),
        "absolute_residual_reference_error_inf": absolute_error,
        "relative_residual_reference_error_inf": relative_error,
        "max_derivative_or_constraint_error_inf": max(derivative_errors),
        "finite": bool(np.all(np.isfinite(numeric_vector)) and np.all(np.isfinite(reference_vector))),
    }


def run_mms() -> dict[str, Any]:
    before = int(getattr(BACKEND, "NEWTON_CALL_COUNT"))
    production_nodes = (24, 32, 48, 64, 96)

    low = [manufactured_case(n, high_order=False) for n in production_nodes]
    high = [manufactured_case(n, high_order=True) for n in production_nodes]

    after = int(getattr(BACKEND, "NEWTON_CALL_COUNT"))
    if after != before:
        raise AssertionError("manufactured QA must not execute Newton")

    low_max = max(item["absolute_residual_reference_error_inf"] for item in low)
    high_map = {item["node_count"]: item["absolute_residual_reference_error_inf"] for item in high}
    fine_min = min(high_map[48], high_map[64], high_map[96])

    # Low-degree manufactured profiles are exactly representable on every production grid.
    low_pass = all(item["finite"] for item in low) and low_max <= 5.0e-8

    # The high-order case is intentionally under-resolved at N=24/32 and representable
    # from N=48 onward. Require a clear resolution transition, not monotonic roundoff.
    high_pass = (
        all(item["finite"] for item in high)
        and fine_min <= 5.0e-7
        and high_map[48] <= max(1.0e-12, high_map[24] * 1.0e-3)
    )

    return {
        "schema": "universelab.ulsh01.sim70.cp01r4.manufactured-solution-qa.v0.1",
        "status": "PASS_QA_ONLY" if low_pass and high_pass else "FAIL_QA_ONLY",
        "run_id": "HZT-M0-S6-C-PHYS-M1-ULSH01-WP2-CP01R4",
        "model_spec_id": "HZT-M0-S6-C-PHYS-M1",
        "method": "ANALYTIC_MANUFACTURED_RESIDUAL_REFERENCE_NO_BVP_SOLVE",
        "production_node_counts": list(production_nodes),
        "low_order_case": low,
        "high_order_resolution_case": high,
        "low_order_max_abs_error": low_max,
        "high_order_fine_min_abs_error": fine_min,
        "newton_call_count_delta": after - before,
        "manufactured_solution_result": bool(low_pass and high_pass),
        "physical_interpretation": PHYSICAL_INTERPRETATION,
        "canonical_effect": CANONICAL_EFFECT,
        "physical_evidence_effect": PHYSICAL_EVIDENCE_EFFECT,
        "limitations": [
            "This verifies implementation against an analytic manufactured residual reference.",
            "It does not prove the formal equations; that remains SCI-31 scope.",
            "It does not establish a physical background, continuum existence, uniqueness, stability, or ghost freedom.",
        ],
    }


def main() -> int:
    result = run_mms()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["manufactured_solution_result"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
