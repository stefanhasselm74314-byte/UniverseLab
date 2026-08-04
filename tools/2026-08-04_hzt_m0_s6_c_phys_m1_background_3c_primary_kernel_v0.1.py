#!/usr/bin/env python3
"""Primary CP01R1 collocation kernel for Background-3C.

This module defines the preregistered primary numerical machinery. It is not an
execution entry point. Importing and auditing it does not run Newton iterations.
Direct invocation is denied with exit code 73.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Any

import numpy as np
import scipy.linalg as la

EXIT_NOT_AUTHORIZED = 73
FIELD_ORDER = ("u_A", "u_ell", "u_varphi", "u_g")
PARAMETER_ORDER = (
    "varphi_N_0", "q_N", "A_S_0", "varphi_S_0",
    "q_S", "rho_N", "rho_S", "k4",
)
BOUNDARY_ORDER = (
    "R_A", "R_ell", "R_varphi", "R_patch",
    "R_4D", "R_chi", "R_scalar", "R_gauge",
)
NEWTON_CALL_COUNT = 0


class ImplementationError(RuntimeError):
    pass


@dataclass(frozen=True)
class Model:
    Lambda_hat: float
    mhat_phi_sq: float
    a_F: float
    lambda_hat: float
    z_sigma_hat: float
    q_hat: float


@dataclass(frozen=True)
class Sector:
    N_F: int
    N_sigma: int
    m_sigma: int


@dataclass(frozen=True)
class Grid:
    node_count: int
    degree: int
    tau: np.ndarray
    D: np.ndarray
    D2: np.ndarray


@dataclass
class RegionEvaluation:
    A: np.ndarray
    ell: np.ndarray
    varphi: np.ndarray
    a_chi: np.ndarray
    A_x: np.ndarray
    ell_x: np.ndarray
    varphi_x: np.ndarray
    Lhat: np.ndarray
    residual_blocks: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
    constraint: np.ndarray


def as_float(value: Any) -> float:
    if isinstance(value, str) and "/" in value:
        return float(Fraction(value))
    return float(value)


def model_from_payload(payload: dict[str, Any], *, control_a_F: bool = False) -> Model:
    p = payload["model_parameters_ordered"]
    return Model(
        Lambda_hat=as_float(p["Lambda_hat"]),
        mhat_phi_sq=as_float(p["mhat_phi_sq"]),
        a_F=0.0 if control_a_F else as_float(p["a_F"]),
        lambda_hat=as_float(p["lambda_hat"]),
        z_sigma_hat=as_float(p["z_sigma_hat"]),
        q_hat=as_float(p["q_hat"]),
    )


def sector_from_payload(payload: dict[str, Any]) -> Sector:
    t = payload["topological_sector_ordered"]
    return Sector(N_F=int(t["N_F"]), N_sigma=int(t["N_sigma"]), m_sigma=int(t["m_sigma"]))


def chebyshev_lobatto(node_count: int) -> Grid:
    if node_count < 3:
        raise ValueError("node_count must be at least three")
    degree = node_count - 1
    j = np.arange(node_count)
    x_desc = np.cos(np.pi * j / degree)
    tau_desc = (x_desc + 1.0) / 2.0
    weights_desc = (-1.0) ** j
    weights_desc[[0, -1]] *= 0.5
    tau = tau_desc[::-1].copy()
    weights = weights_desc[::-1].copy()
    D = np.zeros((node_count, node_count), dtype=float)
    for i in range(node_count):
        for k in range(node_count):
            if i != k:
                D[i, k] = weights[k] / (weights[i] * (tau[i] - tau[k]))
        D[i, i] = -np.sum(D[i, :])
    return Grid(node_count=node_count, degree=degree, tau=tau, D=D, D2=D @ D)


def state_size(node_count: int) -> int:
    return 8 * node_count + 8


def unpack_state(state: np.ndarray, node_count: int) -> tuple[list[list[np.ndarray]], np.ndarray]:
    state = np.asarray(state)
    expected = state_size(node_count)
    if state.ndim != 1 or state.size != expected:
        raise ValueError(f"state must have shape ({expected},)")
    offset = 0
    regions: list[list[np.ndarray]] = []
    for _ in range(2):
        fields: list[np.ndarray] = []
        for _ in FIELD_ORDER:
            fields.append(state[offset:offset + node_count])
            offset += node_count
        regions.append(fields)
    return regions, state[offset:offset + 8]


def pack_state(regions: list[list[np.ndarray]], parameters: np.ndarray) -> np.ndarray:
    return np.concatenate([*regions[0], *regions[1], np.asarray(parameters)])


def evaluate_region(
    fields: list[np.ndarray], *, A0: complex, varphi0: complex,
    rho: complex, q: complex, k4: complex, grid: Grid, model: Model,
) -> RegionEvaluation:
    u_A, u_ell, u_varphi, u_g = fields
    tau, D, D2 = grid.tau, grid.D, grid.D2
    u_A_t, u_A_tt = D @ u_A, D2 @ u_A
    u_ell_t, u_ell_tt = D @ u_ell, D2 @ u_ell
    u_varphi_t, u_varphi_tt = D @ u_varphi, D2 @ u_varphi
    u_g_t = D @ u_g

    Lhat = 1.0 + tau * u_ell
    Lhat_t = u_ell + tau * u_ell_t
    Lhat_tt = 2.0 * u_ell_t + tau * u_ell_tt
    A = A0 + tau * u_A
    varphi = varphi0 + tau * u_varphi
    sqrt_tau = np.sqrt(tau)
    A_x = 2.0 * sqrt_tau / rho * (u_A + tau * u_A_t)
    A_xx = 2.0 / rho**2 * (u_A + 5.0 * tau * u_A_t + 2.0 * tau**2 * u_A_tt)
    varphi_x = 2.0 * sqrt_tau / rho * (u_varphi + tau * u_varphi_t)
    varphi_xx = 2.0 / rho**2 * (
        u_varphi + 5.0 * tau * u_varphi_t + 2.0 * tau**2 * u_varphi_tt
    )
    ell = rho * sqrt_tau * Lhat
    ell_x = Lhat + 2.0 * tau * Lhat_t
    ell_xx_over_ell = 2.0 / rho**2 * (
        3.0 * Lhat_t + 2.0 * tau * Lhat_tt
    ) / Lhat
    A_x_ell_x_over_ell = 2.0 / rho**2 * (
        (u_A + tau * u_A_t) * (Lhat + 2.0 * tau * Lhat_t) / Lhat
    )
    varphi_x_ell_x_over_ell = 2.0 / rho**2 * (
        (u_varphi + tau * u_varphi_t) * (Lhat + 2.0 * tau * Lhat_t) / Lhat
    )
    a_chi = tau * u_g

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
        2.0 / rho * (u_g + tau * u_g_t)
        - q * rho * Lhat * np.exp(-4.0 * A + 2.0 * model.a_F * varphi)
    )
    constraint = (
        -6.0 * k4 * exp_minus_2A + 6.0 * A_x**2 + model.Lambda_hat
        + 4.0 * A_x_ell_x_over_ell - 0.5 * varphi_x**2
        + 0.5 * model.mhat_phi_sq * varphi**2 - rho_F
    )
    return RegionEvaluation(
        A, ell, varphi, a_chi, A_x, ell_x, varphi_x, Lhat,
        (F_A, F_ell, F_varphi, F_gauge), constraint,
    )


def boundary_residual(
    north: RegionEvaluation, south: RegionEvaluation,
    parameters: np.ndarray, model: Model, sector: Sector,
) -> np.ndarray:
    _, q_N, _, _, q_S, _, _, _ = parameters
    i = -1
    ell_sigma = 0.5 * (north.ell[i] + south.ell[i])
    A_sum = north.A_x[i] + south.A_x[i]
    ell_sum = (north.ell_x[i] + south.ell_x[i]) / ell_sigma
    d_chi = sector.N_sigma - sector.m_sigma * model.q_hat * south.a_chi[i]
    Y_sigma = model.z_sigma_hat * d_chi**2 / ell_sigma**2
    rows = (
        north.A[i] - south.A[i],
        north.ell[i] - south.ell[i],
        north.varphi[i] - south.varphi[i],
        north.a_chi[i] - south.a_chi[i] - sector.N_F / model.q_hat,
        -3.0 * A_sum - ell_sum + model.lambda_hat + 0.5 * Y_sigma,
        -4.0 * A_sum + model.lambda_hat - 0.5 * Y_sigma,
        north.varphi_x[i] + south.varphi_x[i],
        q_N * np.exp(-4.0 * north.A[i]) / ell_sigma
        + q_S * np.exp(-4.0 * south.A[i]) / ell_sigma
        - sector.m_sigma * model.q_hat * model.z_sigma_hat * d_chi / ell_sigma**2,
    )
    return np.asarray(rows, dtype=np.result_type(parameters, north.A, float))


def residual(
    state: np.ndarray, node_count: int, model: Model, sector: Sector,
) -> tuple[np.ndarray, dict[str, Any]]:
    grid = chebyshev_lobatto(node_count)
    regions, parameters = unpack_state(state, node_count)
    varphi_N_0, q_N, A_S_0, varphi_S_0, q_S, rho_N, rho_S, k4 = parameters
    north = evaluate_region(
        regions[0], A0=0.0, varphi0=varphi_N_0, rho=rho_N,
        q=q_N, k4=k4, grid=grid, model=model,
    )
    south = evaluate_region(
        regions[1], A0=A_S_0, varphi0=varphi_S_0, rho=rho_S,
        q=q_S, k4=k4, grid=grid, model=model,
    )
    boundary = boundary_residual(north, south, parameters, model, sector)
    vector = np.concatenate([*north.residual_blocks, *south.residual_blocks, boundary])
    return vector, {"north": north, "south": south, "boundary": boundary}


def control_seed_state(node_count: int) -> np.ndarray:
    tau = chebyshev_lobatto(node_count).tau
    y0 = (8.0 - 2.0 * math.sqrt(10.0)) / 3.0
    q0 = y0 / 2.0
    R0 = 1.0 / math.sqrt(y0)
    rho0 = math.pi * R0 / 2.0
    k4_0 = (1.0 - q0**2 / 2.0) / 6.0
    root = np.sqrt(tau)
    angle = math.pi * root / 2.0
    positive = tau > 1.0e-14
    Lhat = np.ones_like(tau)
    Lhat[positive] = 2.0 * np.sin(angle[positive]) / (math.pi * root[positive])
    u_ell = np.empty_like(tau)
    u_ell[positive] = (Lhat[positive] - 1.0) / tau[positive]
    u_ell[~positive] = -math.pi**2 / 24.0
    u_g = np.empty_like(tau)
    u_g[positive] = (1.0 - np.cos(angle[positive])) / (2.0 * tau[positive])
    u_g[~positive] = math.pi**2 / 16.0
    zero = np.zeros_like(tau)
    regions = [
        [zero.copy(), u_ell.copy(), zero.copy(), u_g.copy()],
        [zero.copy(), u_ell.copy(), zero.copy(), -u_g.copy()],
    ]
    parameters = np.asarray([0.0, q0, 0.0, 0.0, -q0, rho0, rho0, k4_0])
    return pack_state(regions, parameters)


def seed_direction(node_count: int) -> np.ndarray:
    tau = chebyshev_lobatto(node_count).tau
    one_minus_tau = 1.0 - tau
    const = np.ones_like(tau)
    regions = [
        [const / 64.0, one_minus_tau / 64.0, one_minus_tau / 32.0, one_minus_tau / 64.0],
        [-const / 64.0, -one_minus_tau / 64.0, -one_minus_tau / 32.0, -one_minus_tau / 64.0],
    ]
    parameters = np.asarray([1 / 32, 1 / 64, 0.0, -1 / 32, -1 / 64, 1 / 64, -1 / 64, 1 / 128])
    return pack_state(regions, parameters)


def seven_seeds(node_count: int) -> list[np.ndarray]:
    base = control_seed_state(node_count)
    direction = seed_direction(node_count)
    return [base + multiplier * direction for multiplier in (0.0, 1 / 8, -1 / 8, 1 / 4, -1 / 4, 1 / 2, -1 / 2)]


def admissible(
    state: np.ndarray, node_count: int, *,
    rho_min: float = 1.0e-4, ell_margin: float = 1.0e-8,
) -> bool:
    if np.iscomplexobj(state):
        return True
    regions, parameters = unpack_state(state, node_count)
    if (
        not np.all(np.isfinite(state))
        or parameters[5] <= rho_min
        or parameters[6] <= rho_min
    ):
        return False
    tau = chebyshev_lobatto(node_count).tau
    return bool(
        np.min(1.0 + tau * regions[0][1]) > ell_margin
        and np.min(1.0 + tau * regions[1][1]) > ell_margin
    )


def complex_step_jacobian(
    state: np.ndarray, node_count: int, model: Model, sector: Sector,
    step: float = 1.0e-30,
) -> np.ndarray:
    state = np.asarray(state, dtype=float)
    jacobian = np.empty((state.size, state.size), dtype=float)
    for column in range(state.size):
        probe = state.astype(complex)
        probe[column] += 1j * step
        jacobian[:, column] = np.imag(residual(probe, node_count, model, sector)[0]) / step
    return jacobian


def rrqr_step(
    jacobian: np.ndarray, rhs: np.ndarray, *, rank_rtol: float = 1.0e-12,
) -> tuple[np.ndarray, dict[str, Any]]:
    Q, R, pivots = la.qr(jacobian, mode="economic", pivoting=True)
    diagonal = np.abs(np.diag(R))
    scale = float(diagonal[0]) if diagonal.size else 0.0
    rank = int(np.count_nonzero(diagonal > rank_rtol * scale)) if scale > 0.0 else 0
    singular_values = la.svdvals(jacobian)
    if rank != jacobian.shape[1]:
        raise ImplementationError(
            f"RRQR rank deficient: rank={rank}, columns={jacobian.shape[1]}"
        )
    transformed = Q.T @ rhs
    pivoted_step = la.solve_triangular(R, transformed, lower=False)
    step = np.empty_like(pivoted_step)
    step[pivots] = pivoted_step
    return step, {
        "rrqr_rank": rank,
        "pivot_order": pivots.tolist(),
        "singular_values": singular_values,
    }


def damped_newton(
    initial: np.ndarray, node_count: int, model: Model, sector: Sector, *,
    maximum_iterations: int = 60,
    maximum_backtracking_steps: int = 20,
    armijo_parameter: float = 1.0e-4,
    minimum_step_fraction: float = 2.0**-20,
    trust_radius_initial: float = 1.0,
    trust_radius_minimum: float = 1.0e-12,
    residual_tolerance: float = 1.0e-10,
    step_tolerance: float = 1.0e-11,
    stagnation_window_iterations: int = 6,
    stagnation_relative_improvement_floor: float = 1.0e-3,
) -> dict[str, Any]:
    global NEWTON_CALL_COUNT
    NEWTON_CALL_COUNT += 1
    state = np.asarray(initial, dtype=float).copy()
    trust_radius = trust_radius_initial
    history: list[dict[str, Any]] = []
    recent_norms: list[float] = []
    for iteration in range(maximum_iterations):
        current_residual, _ = residual(state, node_count, model, sector)
        current_norm = float(np.max(np.abs(current_residual)))
        jacobian = complex_step_jacobian(state, node_count, model, sector)
        try:
            delta, diagnostics = rrqr_step(jacobian, -current_residual)
        except ImplementationError as exc:
            return {
                "converged": False,
                "failure": "RRQR_RANK_DEFICIENT",
                "error": str(exc),
                "state": state,
                "history": history,
            }
        raw_step_norm = float(la.norm(delta))
        if raw_step_norm > trust_radius:
            delta *= trust_radius / raw_step_norm
        scaled_step_norm = float(la.norm(delta))
        accepted = False
        accepted_factor = 0.0
        candidate_norm = current_norm
        for backtrack in range(maximum_backtracking_steps + 1):
            factor = 0.5**backtrack
            if factor < minimum_step_fraction:
                break
            candidate = state + factor * delta
            if not admissible(candidate, node_count):
                continue
            candidate_residual, _ = residual(candidate, node_count, model, sector)
            candidate_norm = float(np.max(np.abs(candidate_residual)))
            if candidate_norm <= (1.0 - armijo_parameter * factor) * current_norm:
                state = candidate
                accepted = True
                accepted_factor = factor
                break
        singular_values = diagnostics["singular_values"]
        history.append({
            "iteration": iteration,
            "residual_inf": current_norm,
            "trial_residual_inf": candidate_norm,
            "step_2": scaled_step_norm,
            "accepted_factor": accepted_factor,
            "trust_radius": trust_radius,
            "rrqr_rank": diagnostics["rrqr_rank"],
            "sigma_min": float(singular_values[-1]),
            "sigma_max": float(singular_values[0]),
        })
        if current_norm <= residual_tolerance and scaled_step_norm <= step_tolerance:
            return {"converged": True, "state": state, "history": history}
        if not accepted:
            trust_radius *= 0.25
            if trust_radius < trust_radius_minimum:
                return {
                    "converged": False,
                    "failure": "TRUST_RADIUS_BELOW_MINIMUM",
                    "state": state,
                    "history": history,
                }
            continue
        if accepted_factor == 1.0 and candidate_norm < 0.25 * current_norm:
            trust_radius = min(2.0 * trust_radius, 4.0 * trust_radius_initial)
        elif accepted_factor < 0.25:
            trust_radius = max(0.5 * trust_radius, trust_radius_minimum)
        recent_norms.append(candidate_norm)
        if len(recent_norms) > stagnation_window_iterations:
            recent_norms.pop(0)
        if len(recent_norms) == stagnation_window_iterations:
            improvement = (
                recent_norms[0] - recent_norms[-1]
            ) / max(recent_norms[0], 1.0e-300)
            if improvement < stagnation_relative_improvement_floor:
                return {
                    "converged": False,
                    "failure": "STAGNATION",
                    "state": state,
                    "history": history,
                }
    return {
        "converged": False,
        "failure": "MAXIMUM_ITERATIONS",
        "state": state,
        "history": history,
    }


def direct_invocation_denied() -> int:
    print("NOT_AUTHORIZED: primary kernel has no direct execution entry point")
    return EXIT_NOT_AUTHORIZED


if __name__ == "__main__":
    raise SystemExit(direct_invocation_denied())
