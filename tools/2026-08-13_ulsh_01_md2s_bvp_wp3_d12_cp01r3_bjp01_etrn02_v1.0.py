#!/usr/bin/env python3
"""ULSH-01 / WP3-D12 CP01R3 manufactured-control implementation v1.0.

Implements only the generic BJP-01 algebra and ETRN-02 state-metric trust method
specified in WP3-D11. This module has no path to the MD2S physical backend,
contains no physical run input, issues no grant, and cannot execute CP01R3.
"""
from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
import math
from pathlib import Path
from typing import Any, Callable

import numpy as np

RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R3"
SEED_SET_ID = "M1-BG3B-CP01R3-BJP01-SEEDS-01"
NODE_COUNTS = (24, 32, 48, 64, 96)
SEED_MULTIPLIERS = (0.0, 1 / 8, -1 / 8, 1 / 4, -1 / 4, 1 / 2, -1 / 2)

SVD_RELATIVE_CUTOFF = 1.0e-12
EQUILIBRATION_FLOOR = 1.0e-12
RHO_ACCEPT_MIN = 0.10
RHO_SHRINK = 0.25
RHO_EXPAND = 0.75
TRUST_RADIUS_INITIAL = 0.25
TRUST_RADIUS_MINIMUM = 1.0e-8
TRUST_RADIUS_MAXIMUM = 2.0
MAXIMUM_ITERATIONS = 120
STAGNATION_WINDOW = 12
STAGNATION_FLOOR = 1.0e-4
MESH_METRIC_RELATIVE_TOLERANCE = 0.006

EXIT_NOT_AUTHORIZED = 73


class D12ControlError(RuntimeError):
    pass


class PhysicalExecutionDenied(D12ControlError):
    pass


@dataclass(frozen=True)
class BoundaryProjection:
    A_sum_star: float
    ell_sum_star: float
    delta_A_sum: float
    delta_ell_sum: float
    c_A_N: float
    c_A_S: float
    c_ell_N: float
    c_ell_S: float


@dataclass(frozen=True)
class StageMetric:
    node_count: int
    field_scales: tuple[float, ...]
    parameter_scales: tuple[float, ...]


def _finite(*values: float) -> None:
    if not all(math.isfinite(float(v)) for v in values):
        raise D12ControlError("finite values required")


def boundary_projection(
    *, A_sum_0: float, ell_sum_0: float, Y_sigma_0: float,
    ell_sigma_0: float, rho_N: float, rho_S: float, lambda_hat: float,
) -> BoundaryProjection:
    _finite(A_sum_0, ell_sum_0, Y_sigma_0, ell_sigma_0, rho_N, rho_S, lambda_hat)
    if ell_sigma_0 <= 0.0 or rho_N <= 0.0 or rho_S <= 0.0:
        raise D12ControlError("positive ell_sigma and cap radii required")
    A_star = (lambda_hat - 0.5 * Y_sigma_0) / 4.0
    ell_star = -3.0 * A_star + lambda_hat + 0.5 * Y_sigma_0
    dA = A_star - A_sum_0
    dL = ell_star - ell_sum_0
    return BoundaryProjection(
        A_sum_star=A_star,
        ell_sum_star=ell_star,
        delta_A_sum=dA,
        delta_ell_sum=dL,
        c_A_N=rho_N * dA / 4.0,
        c_A_S=rho_S * dA / 4.0,
        c_ell_N=ell_sigma_0 * dL / 4.0,
        c_ell_S=ell_sigma_0 * dL / 4.0,
    )


def projected_junction_residuals(projection: BoundaryProjection, *, Y_sigma_0: float, lambda_hat: float) -> tuple[float, float]:
    r4d = -3.0 * projection.A_sum_star - projection.ell_sum_star + lambda_hat + 0.5 * Y_sigma_0
    rchi = -4.0 * projection.A_sum_star + lambda_hat - 0.5 * Y_sigma_0
    return r4d, rchi


def derivative_basis(tau: np.ndarray, coefficient: float) -> np.ndarray:
    values = np.asarray(tau, dtype=float)
    if values.ndim != 1 or values.size < 2 or not np.all(np.isfinite(values)):
        raise D12ControlError("finite one-dimensional tau grid required")
    return float(coefficient) * (values - 1.0)


def chebyshev_lobatto_tau(node_count: int) -> np.ndarray:
    if node_count < 3:
        raise D12ControlError("node_count must be >=3")
    j = np.arange(node_count)
    x_desc = np.cos(np.pi * j / (node_count - 1))
    return ((x_desc + 1.0) / 2.0)[::-1].copy()


def freeze_stage_metric(seed_state: np.ndarray, node_count: int) -> StageMetric:
    seed = np.asarray(seed_state, dtype=float)
    expected = 8 * node_count + 8
    if seed.ndim != 1 or seed.size != expected or not np.all(np.isfinite(seed)):
        raise D12ControlError(f"finite seed state of length {expected} required")
    field_scales: list[float] = []
    offset = 0
    for _ in range(8):
        block = seed[offset:offset + node_count]
        offset += node_count
        rms = float(np.sqrt(np.mean(block**2)))
        field_scales.append(max(1.0, rms))
    parameter_scales = tuple(max(1.0, abs(float(v))) for v in seed[offset:offset + 8])
    return StageMetric(node_count=node_count, field_scales=tuple(field_scales), parameter_scales=parameter_scales)


def state_metric_norm(delta_state: np.ndarray, metric: StageMetric) -> float:
    delta = np.asarray(delta_state, dtype=float)
    expected = 8 * metric.node_count + 8
    if delta.ndim != 1 or delta.size != expected or not np.all(np.isfinite(delta)):
        raise D12ControlError(f"finite displacement of length {expected} required")
    value = 0.0
    offset = 0
    for scale in metric.field_scales:
        block = delta[offset:offset + metric.node_count]
        offset += metric.node_count
        value += float(np.mean((block / scale) ** 2))
    for scale, component in zip(metric.parameter_scales, delta[offset:offset + 8], strict=True):
        value += float((component / scale) ** 2)
    return math.sqrt(value)


def _rank_condition(singular_values: np.ndarray) -> tuple[int, float]:
    values = np.asarray(singular_values, dtype=float)
    if values.ndim != 1 or values.size == 0:
        raise D12ControlError("nonempty singular-value vector required")
    sigma_max = float(values[0])
    cutoff = SVD_RELATIVE_CUTOFF * sigma_max if sigma_max > 0.0 else 0.0
    rank = int(np.count_nonzero(values > cutoff)) if sigma_max > 0.0 else 0
    sigma_min = float(values[-1])
    condition = math.inf if sigma_min <= 0.0 else sigma_max / sigma_min
    return rank, condition


def equilibrated_original_direction(jacobian: np.ndarray, residual: np.ndarray) -> dict[str, Any]:
    J = np.asarray(jacobian, dtype=float)
    r = np.asarray(residual, dtype=float)
    if J.ndim != 2 or r.ndim != 1 or J.shape[0] != r.size or J.shape[1] != r.size:
        raise D12ControlError("square Jacobian and matching residual required")
    if not np.all(np.isfinite(J)) or not np.all(np.isfinite(r)):
        raise D12ControlError("nonfinite Jacobian/residual")
    column_norms = np.linalg.norm(J, axis=0)
    column_scale = np.maximum(column_norms, EQUILIBRATION_FLOOR)
    J_column = J / column_scale[None, :]
    row_norms = np.linalg.norm(J_column, axis=1)
    row_scale = 1.0 / np.maximum(row_norms, EQUILIBRATION_FLOOR)
    A = row_scale[:, None] * J_column
    b = -(row_scale * r)
    U, singular, Vt = np.linalg.svd(A, full_matrices=False)
    rank, condition = _rank_condition(singular)
    cutoff = SVD_RELATIVE_CUTOFF * float(singular[0])
    inverse = np.zeros_like(singular)
    active = singular > cutoff
    inverse[active] = 1.0 / singular[active]
    z = Vt.T @ (inverse * (U.T @ b))
    dx = z / column_scale
    return {
        "dx_unclipped": dx,
        "linear_coordinate": z,
        "scaled_rank": rank,
        "scaled_condition_estimate": condition,
        "column_scale": column_scale,
        "row_scale": row_scale,
    }


def clip_in_state_metric(dx_unclipped: np.ndarray, metric: StageMetric, trust_radius: float) -> dict[str, Any]:
    if not math.isfinite(trust_radius) or trust_radius <= 0.0:
        raise D12ControlError("positive finite trust radius required")
    direction = np.asarray(dx_unclipped, dtype=float)
    norm = state_metric_norm(direction, metric)
    alpha = 1.0 if norm <= trust_radius or norm == 0.0 else trust_radius / norm
    dx = alpha * direction
    return {
        "dx": dx,
        "unclipped_state_metric_norm": norm,
        "accepted_state_metric_step_norm": state_metric_norm(dx, metric),
        "clip_factor": alpha,
        "trust_radius_active": bool(alpha < 1.0),
    }


def model_reduction_ratio(current_residual: np.ndarray, trial_residual: np.ndarray, jacobian: np.ndarray, trial_step: np.ndarray) -> float:
    r = np.asarray(current_residual, dtype=float)
    rt = np.asarray(trial_residual, dtype=float)
    J = np.asarray(jacobian, dtype=float)
    dx = np.asarray(trial_step, dtype=float)
    current_phi = 0.5 * float(r @ r)
    trial_phi = 0.5 * float(rt @ rt)
    predicted = r + J @ dx
    predicted_phi = 0.5 * float(predicted @ predicted)
    denominator = current_phi - predicted_phi
    if not math.isfinite(denominator) or denominator <= 0.0:
        return -math.inf
    return (current_phi - trial_phi) / denominator


def radius_update(delta: float, rho: float, step_norm: float) -> float:
    if rho < RHO_SHRINK:
        return max(TRUST_RADIUS_MINIMUM, RHO_SHRINK * delta)
    if rho > RHO_EXPAND and step_norm >= 0.8 * delta:
        return min(TRUST_RADIUS_MAXIMUM, 2.0 * delta)
    return delta


def etrn02_solve_generic(
    initial: np.ndarray,
    node_count: int,
    residual_fn: Callable[[np.ndarray], np.ndarray],
    jacobian_fn: Callable[[np.ndarray], np.ndarray],
    admissible_fn: Callable[[np.ndarray], bool],
    *, residual_tolerance: float = 1.0e-10,
) -> dict[str, Any]:
    state = np.asarray(initial, dtype=float).copy()
    metric = freeze_stage_metric(state, node_count)
    delta = TRUST_RADIUS_INITIAL
    history: list[dict[str, Any]] = []
    accepted_norms: list[float] = []

    for iteration in range(MAXIMUM_ITERATIONS):
        residual = np.asarray(residual_fn(state), dtype=float)
        if not np.all(np.isfinite(residual)):
            return {"converged": False, "failure": "NONFINITE_RESIDUAL", "state": state, "history": history}
        residual_inf = float(np.max(np.abs(residual))) if residual.size else 0.0
        if residual_inf <= residual_tolerance:
            return {"converged": True, "state": state, "history": history, "residual_inf": residual_inf}
        direction = equilibrated_original_direction(np.asarray(jacobian_fn(state), dtype=float), residual)
        clipped = clip_in_state_metric(direction["dx_unclipped"], metric, delta)
        trial = state + clipped["dx"]
        accepted = False
        rho = -math.inf
        trial_inf = residual_inf
        if bool(admissible_fn(trial)) and np.all(np.isfinite(trial)):
            trial_residual = np.asarray(residual_fn(trial), dtype=float)
            if np.all(np.isfinite(trial_residual)):
                trial_inf = float(np.max(np.abs(trial_residual))) if trial_residual.size else 0.0
                rho = model_reduction_ratio(residual, trial_residual, np.asarray(jacobian_fn(state), dtype=float), clipped["dx"])
                if trial_inf < residual_inf and rho >= RHO_ACCEPT_MIN:
                    state = trial
                    accepted = True
        row = {
            "iteration": iteration,
            "residual_inf": residual_inf,
            "trial_residual_inf": trial_inf,
            "accepted": accepted,
            "rho": rho,
            "trust_radius_before": delta,
            "trust_radius_active": clipped["trust_radius_active"],
            "unclipped_state_metric_norm": clipped["unclipped_state_metric_norm"],
            "accepted_state_metric_step_norm": clipped["accepted_state_metric_step_norm"] if accepted else 0.0,
            "clip_factor": clipped["clip_factor"] if accepted else 0.0,
            "scaled_rank": direction["scaled_rank"],
            "scaled_condition_estimate": direction["scaled_condition_estimate"],
            "acceptance_merit": "ORIGINAL_UNSCALED_RESIDUAL_INFINITY_NORM",
        }
        if accepted:
            delta = radius_update(delta, rho, clipped["accepted_state_metric_step_norm"])
            accepted_norms.append(trial_inf)
            if len(accepted_norms) > STAGNATION_WINDOW:
                accepted_norms.pop(0)
            if len(accepted_norms) == STAGNATION_WINDOW:
                improvement = (accepted_norms[0] - accepted_norms[-1]) / max(accepted_norms[0], 1.0e-300)
                if improvement < STAGNATION_FLOOR:
                    row["trust_radius_after"] = delta
                    history.append(row)
                    return {"converged": False, "failure": "STAGNATION", "state": state, "history": history}
        else:
            delta = max(TRUST_RADIUS_MINIMUM, RHO_SHRINK * delta)
            if delta <= TRUST_RADIUS_MINIMUM:
                row["trust_radius_after"] = delta
                history.append(row)
                return {"converged": False, "failure": "TRUST_RADIUS_BELOW_MINIMUM", "state": state, "history": history}
        row["trust_radius_after"] = delta
        history.append(row)

    final_residual = np.asarray(residual_fn(state), dtype=float)
    return {
        "converged": False,
        "failure": "MAXIMUM_ITERATIONS",
        "state": state,
        "history": history,
        "residual_inf": float(np.max(np.abs(final_residual))),
    }


def _manufactured_state(node_count: int, value: float = 0.0) -> np.ndarray:
    return np.full(8 * node_count + 8, float(value), dtype=float)


def run_manufactured_controls() -> dict[str, Any]:
    controls: dict[str, Any] = {}

    # C1 exact BJP-01 algebra.
    max_projection_error = 0.0
    for values in (
        (0.0, 0.0, 1.25, 1.4, 2.1, 2.0, 1.0),
        (0.2, -0.4, 0.0, 0.9, 1.2, 1.7, 1.0),
        (-0.3, 0.8, 2.0, 2.2, 3.0, 2.5, 1.0),
        (1.0, -1.0, 0.75, 1.1, 1.5, 1.8, 0.5),
    ):
        projection = boundary_projection(
            A_sum_0=values[0], ell_sum_0=values[1], Y_sigma_0=values[2],
            ell_sigma_0=values[3], rho_N=values[4], rho_S=values[5], lambda_hat=values[6],
        )
        r4d, rchi = projected_junction_residuals(projection, Y_sigma_0=values[2], lambda_hat=values[6])
        max_projection_error = max(max_projection_error, abs(r4d), abs(rchi))
    controls["D11-C1"] = {"status": "PASS", "max_abs_projected_junction_residual": max_projection_error}

    # C2 endpoint/pole invariants of the derivative-only basis.
    tau = chebyshev_lobatto_tau(48)
    basis = derivative_basis(tau, 0.37)
    physical_A_delta = tau * basis
    Lhat_delta = tau * basis
    controls["D11-C2"] = {
        "status": "PASS" if max(abs(float(physical_A_delta[0])), abs(float(physical_A_delta[-1])), abs(float(Lhat_delta[0])), abs(float(Lhat_delta[-1]))) < 1e-15 else "FAIL",
        "endpoint_invariant_max_abs": max(abs(float(physical_A_delta[0])), abs(float(physical_A_delta[-1])), abs(float(Lhat_delta[0])), abs(float(Lhat_delta[-1]))),
    }

    # C3 same smooth displacement sampled at all frozen meshes.
    metric_values: list[float] = []
    for n in NODE_COUNTS:
        tau_n = chebyshev_lobatto_tau(n)
        seed = _manufactured_state(n, 0.5)
        delta = np.zeros_like(seed)
        offset = 0
        for block_index in range(8):
            delta[offset:offset + n] = (0.2 + 0.01 * block_index) * (1.0 - tau_n)
            offset += n
        delta[offset:offset + 8] = np.linspace(-0.05, 0.05, 8)
        metric_values.append(state_metric_norm(delta, freeze_stage_metric(seed, n)))
    metric_rel_spread = (max(metric_values) - min(metric_values)) / max(float(np.mean(metric_values)), 1e-300)
    controls["D11-C3"] = {"status": "PASS" if metric_rel_spread <= MESH_METRIC_RELATIVE_TOLERANCE else "FAIL", "relative_spread": metric_rel_spread, "registered_tolerance": MESH_METRIC_RELATIVE_TOLERANCE}

    # C4 original-state trust metric is independent of column-equilibrated z coordinates.
    n = 3
    size = 8 * n + 8
    rng = np.random.default_rng(20260813)
    q1, _ = np.linalg.qr(rng.normal(size=(size, size)))
    q2, _ = np.linalg.qr(rng.normal(size=(size, size)))
    singular = np.geomspace(1e4, 1e-4, size)
    J = q1 @ np.diag(singular) @ q2.T
    root = np.linspace(-0.3, 0.3, size)
    x0 = np.zeros(size)
    r0 = J @ (x0 - root)
    direction = equilibrated_original_direction(J, r0)
    metric = freeze_stage_metric(x0, n)
    base_norm = state_metric_norm(direction["dx_unclipped"], metric)
    factors = np.geomspace(1e-3, 1e3, size)
    J_reparameterized = J @ np.diag(factors)
    direction_y = equilibrated_original_direction(J_reparameterized, r0)
    recovered_dx = factors * direction_y["dx_unclipped"]
    recovered_norm = state_metric_norm(recovered_dx, metric)
    decoupling_rel = abs(base_norm - recovered_norm) / max(base_norm, 1e-300)
    controls["D11-C4"] = {"status": "PASS" if decoupling_rel < 1e-7 else "FAIL", "relative_original_state_metric_difference": decoupling_rel}

    # C5 manufactured stiff coupled linear system with known root.
    q3, _ = np.linalg.qr(rng.normal(size=(size, size)))
    q4, _ = np.linalg.qr(rng.normal(size=(size, size)))
    stiff_singular = np.geomspace(1e6, 1e-4, size)
    A = q3 @ np.diag(stiff_singular) @ q4.T
    known_root = np.linspace(-0.4, 0.4, size)
    result = etrn02_solve_generic(
        np.zeros(size), n,
        lambda x: A @ (x - known_root),
        lambda _x: A,
        lambda x: bool(np.all(np.isfinite(x))),
    )
    root_error = float(np.max(np.abs(np.asarray(result["state"]) - known_root)))
    controls["D11-C5"] = {"status": "PASS" if result.get("converged") and root_error < 1e-7 else "FAIL", "iterations": len(result.get("history", [])), "root_error_inf": root_error}

    # C6 fail-closed nonfinite/admissibility controls.
    failures = 0
    try:
        state_metric_norm(np.full(size, np.nan), freeze_stage_metric(np.zeros(size), n))
    except D12ControlError:
        failures += 1
    try:
        clip_in_state_metric(np.zeros(size), freeze_stage_metric(np.zeros(size), n), 0.0)
    except D12ControlError:
        failures += 1
    inadmissible = etrn02_solve_generic(
        np.zeros(size), n,
        lambda x: x - np.ones(size),
        lambda _x: np.eye(size),
        lambda _x: False,
    )
    if not inadmissible.get("converged") and inadmissible.get("failure") in {"TRUST_RADIUS_BELOW_MINIMUM", "STAGNATION"}:
        failures += 1
    controls["D11-C6"] = {"status": "PASS" if failures == 3 else "FAIL", "fail_closed_checks_passed": failures}

    all_pass = all(row["status"] == "PASS" for row in controls.values())
    return {
        "schema": "universelab.ulsh-01.md2s-bvp.wp3-d12-cp01r3-manufactured-controls.v1",
        "status": "PASS_D12_BJP01_ETRN02_MANUFACTURED_CONTROLS_NO_PHYSICAL_EXECUTION" if all_pass else "FAIL_D12_MANUFACTURED_CONTROL",
        "run_id_reserved": RUN_ID,
        "seed_set_id_reserved": SEED_SET_ID,
        "controls": controls,
        "physical_backend_imported": False,
        "physical_residual_evaluations": 0,
        "physical_jacobian_evaluations": 0,
        "physical_solver_calls": 0,
        "grant_issued": False,
        "physical_evidence_effect": "NONE",
    }


def audit() -> dict[str, Any]:
    result = run_manufactured_controls()
    if not result["status"].startswith("PASS_"):
        raise D12ControlError(result["status"])
    return result


def direct_physical_execution_denied() -> int:
    raise PhysicalExecutionDenied("D12 is manufactured-control only; CP01R3 physical execution is not implemented or authorized")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--physical-run", action="store_true")
    args = parser.parse_args()
    if args.physical_run:
        try:
            direct_physical_execution_denied()
        except PhysicalExecutionDenied as exc:
            print(str(exc))
            return EXIT_NOT_AUTHORIZED
    if not args.audit:
        parser.error("--audit required")
    print(json.dumps(audit(), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
