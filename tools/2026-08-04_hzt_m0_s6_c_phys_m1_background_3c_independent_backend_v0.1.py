#!/usr/bin/env python3
"""Independent x-space backend for C-PHYS-M1 Background-3C2.

The module independently codes the M1 bulk equations, higher pole series,
radial constraint, cap residuals and DOP853 regional integration. It does not
import or wrap the primary tau-collocation residual. Direct invocation is
forbidden and no nonlinear shooting solve is performed by the audit path.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Any, Callable

import numpy as np
from scipy.integrate import solve_ivp

EXIT_NOT_AUTHORIZED = 73
STATE_ORDER = ("A", "A_x", "ell", "ell_x", "varphi", "varphi_x", "a_chi")
SHOOTING_ORDER = (
    "varphi_N_0", "q_N", "A_S_0", "varphi_S_0",
    "q_S", "rho_N", "rho_S", "k4",
)
BOUNDARY_ORDER = (
    "R_A", "R_ell", "R_varphi", "R_patch",
    "R_4D", "R_chi", "R_scalar", "R_gauge",
)
INTEGRATION_CALL_COUNT = 0
SHOOTING_JACOBIAN_CALL_COUNT = 0


class IndependentBackendError(RuntimeError):
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
class PoleCoefficients:
    a2: float
    a4: float
    l3: float
    l5: float
    f2: float
    f4: float
    g2: float
    g4: float


@dataclass
class RegionalSolution:
    x: np.ndarray
    y: np.ndarray
    constraint: np.ndarray
    success: bool
    message: str


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


def flux_density(A: np.ndarray | float, varphi: np.ndarray | float, q: float, model: Model):
    return 0.5 * q**2 * np.exp(-8.0 * A + 2.0 * model.a_F * varphi)


def pole_coefficients(A0: float, varphi0: float, q: float, k4: float, model: Model) -> PoleCoefficients:
    K0 = k4 * math.exp(-2.0 * A0)
    R0 = 0.5 * q**2 * math.exp(-8.0 * A0 + 2.0 * model.a_F * varphi0)
    g2 = 0.5 * q * math.exp(-4.0 * A0 + 2.0 * model.a_F * varphi0)
    a2 = (
        6.0 * K0 - model.Lambda_hat
        - 0.5 * model.mhat_phi_sq * varphi0**2 + R0
    ) / 8.0
    f2 = (model.mhat_phi_sq * varphi0 - 2.0 * model.a_F * R0) / 4.0
    l3 = (
        3.0 * K0 - 12.0 * a2 - model.Lambda_hat
        - 0.5 * model.mhat_phi_sq * varphi0**2 - R0
    ) / 6.0
    a4 = (
        -K0 * a2 / 4.0 - R0 * a2 / 6.0
        + R0 * model.a_F * f2 / 24.0 - 5.0 * a2**2 / 6.0
        - f2**2 / 24.0 - model.mhat_phi_sq * varphi0 * f2 / 48.0
    )
    f4 = (
        R0 * model.a_F * a2 - R0 * model.a_F**2 * f2 / 4.0
        - R0 * model.a_F * l3 / 8.0 - a2 * f2 - f2 * l3 / 2.0
        + model.mhat_phi_sq * f2 / 16.0
        + model.mhat_phi_sq * varphi0 * l3 / 16.0
    )
    g4 = g2 * (-2.0 * a2 + model.a_F * f2 + l3 / 2.0)
    l5 = (
        -3.0 * K0 * (2.0 * a2 - l3) / 20.0
        - model.Lambda_hat * l3 / 20.0
        - R0 * (-8.0 * a2 + 2.0 * model.a_F * f2 + l3) / 20.0
        - 6.0 * a2**2 / 5.0 - 6.0 * a2 * l3 / 5.0
        - 12.0 * a4 / 5.0 - f2**2 / 10.0
        - model.mhat_phi_sq * varphi0 * f2 / 20.0
        - model.mhat_phi_sq * varphi0**2 * l3 / 40.0
    )
    return PoleCoefficients(a2=a2, a4=a4, l3=l3, l5=l5, f2=f2, f4=f4, g2=g2, g4=g4)


def pole_initial_state(epsilon: float, A0: float, varphi0: float, q: float, k4: float, model: Model) -> np.ndarray:
    if epsilon <= 0.0:
        raise ValueError("epsilon must be positive")
    c = pole_coefficients(A0, varphi0, q, k4, model)
    e2, e3, e4, e5 = epsilon**2, epsilon**3, epsilon**4, epsilon**5
    return np.asarray([
        A0 + c.a2 * e2 + c.a4 * e4,
        2.0 * c.a2 * epsilon + 4.0 * c.a4 * e3,
        epsilon + c.l3 * e3 + c.l5 * e5,
        1.0 + 3.0 * c.l3 * e2 + 5.0 * c.l5 * e4,
        varphi0 + c.f2 * e2 + c.f4 * e4,
        2.0 * c.f2 * epsilon + 4.0 * c.f4 * e3,
        c.g2 * e2 + c.g4 * e4,
    ], dtype=float)


def rhs_x(x: float, state: np.ndarray, q: float, k4: float, model: Model) -> np.ndarray:
    A, A_x, ell, ell_x, varphi, varphi_x, _a_chi = state
    if ell <= 0.0 or not np.all(np.isfinite(state)):
        raise IndependentBackendError("nonpositive ell or nonfinite x-space state")
    rho_F = float(flux_density(A, varphi, q, model))
    exp_minus_2A = math.exp(-2.0 * A)
    A_xx = (
        6.0 * k4 * exp_minus_2A - 10.0 * A_x**2 - model.Lambda_hat
        - 0.5 * varphi_x**2 - 0.5 * model.mhat_phi_sq * varphi**2 + rho_F
    ) / 4.0
    ell_xx = (
        -3.0 * A_xx * ell - 6.0 * A_x**2 * ell - 3.0 * A_x * ell_x
        + 3.0 * k4 * exp_minus_2A * ell - model.Lambda_hat * ell
        - ell * (0.5 * varphi_x**2 + 0.5 * model.mhat_phi_sq * varphi**2 + rho_F)
    )
    varphi_xx = (
        -(4.0 * A_x + ell_x / ell) * varphi_x
        + model.mhat_phi_sq * varphi - 2.0 * model.a_F * rho_F
    )
    a_chi_x = q * ell * math.exp(-4.0 * A + 2.0 * model.a_F * varphi)
    return np.asarray([A_x, A_xx, ell_x, ell_xx, varphi_x, varphi_xx, a_chi_x])


def radial_constraint(state: np.ndarray, q: float, k4: float, model: Model) -> float:
    A, A_x, ell, ell_x, varphi, varphi_x, _ = state
    rho_F = float(flux_density(A, varphi, q, model))
    return float(
        ell * (-6.0 * k4 * math.exp(-2.0 * A) + 6.0 * A_x**2 + model.Lambda_hat)
        + 4.0 * A_x * ell_x
        - ell * (0.5 * varphi_x**2 - 0.5 * model.mhat_phi_sq * varphi**2 + rho_F)
    )


def integrate_region(
    *, A0: float, varphi0: float, q: float, rho: float, k4: float,
    model: Model, epsilon: float, sample_count: int = 257,
    rtol: float = 1.0e-11, atol: float = 1.0e-13,
) -> RegionalSolution:
    global INTEGRATION_CALL_COUNT
    INTEGRATION_CALL_COUNT += 1
    if rho <= epsilon:
        raise ValueError("rho must exceed epsilon")
    initial = pole_initial_state(epsilon, A0, varphi0, q, k4, model)
    x = np.linspace(epsilon, rho, sample_count)
    solution = solve_ivp(
        lambda coordinate, state: rhs_x(coordinate, state, q, k4, model),
        (epsilon, rho),
        initial,
        method="DOP853",
        t_eval=x,
        rtol=rtol,
        atol=atol,
        max_step=(rho - epsilon) / 32.0,
    )
    if not solution.success:
        raise IndependentBackendError(f"DOP853 failure: {solution.message}")
    constraints = np.asarray([
        radial_constraint(solution.y[:, index], q, k4, model)
        for index in range(solution.y.shape[1])
    ])
    return RegionalSolution(
        x=solution.t,
        y=solution.y,
        constraint=constraints,
        success=solution.success,
        message=solution.message,
    )


def cap_residuals(
    north_state: np.ndarray, south_state: np.ndarray,
    shooting: np.ndarray, model: Model, sector: Sector,
) -> np.ndarray:
    _varphi_N_0, q_N, _A_S_0, _varphi_S_0, q_S, _rho_N, _rho_S, _k4 = shooting
    A_N, A_N_x, ell_N, ell_N_x, varphi_N, varphi_N_x, a_N = north_state
    A_S, A_S_x, ell_S, ell_S_x, varphi_S, varphi_S_x, a_S = south_state
    ell_sigma = 0.5 * (ell_N + ell_S)
    if ell_sigma <= 0.0:
        raise IndependentBackendError("nonpositive cap radius")
    A_sum = A_N_x + A_S_x
    ell_sum = (ell_N_x + ell_S_x) / ell_sigma
    d_chi = sector.N_sigma - sector.m_sigma * model.q_hat * a_S
    Y_sigma = model.z_sigma_hat * d_chi**2 / ell_sigma**2
    return np.asarray([
        A_N - A_S,
        ell_N - ell_S,
        varphi_N - varphi_S,
        a_N - a_S - sector.N_F / model.q_hat,
        -3.0 * A_sum - ell_sum + model.lambda_hat + 0.5 * Y_sigma,
        -4.0 * A_sum + model.lambda_hat - 0.5 * Y_sigma,
        varphi_N_x + varphi_S_x,
        q_N * math.exp(-4.0 * A_N) / ell_sigma
        + q_S * math.exp(-4.0 * A_S) / ell_sigma
        - sector.m_sigma * model.q_hat * model.z_sigma_hat * d_chi / ell_sigma**2,
    ])


def shooting_residual(
    shooting: np.ndarray, model: Model, sector: Sector, *, epsilon: float,
    sample_count: int = 257,
) -> tuple[np.ndarray, dict[str, RegionalSolution]]:
    shooting = np.asarray(shooting, dtype=float)
    if shooting.shape != (8,):
        raise ValueError("shooting vector must contain eight values")
    varphi_N_0, q_N, A_S_0, varphi_S_0, q_S, rho_N, rho_S, k4 = shooting
    north = integrate_region(
        A0=0.0, varphi0=varphi_N_0, q=q_N, rho=rho_N, k4=k4,
        model=model, epsilon=epsilon, sample_count=sample_count,
    )
    south = integrate_region(
        A0=A_S_0, varphi0=varphi_S_0, q=q_S, rho=rho_S, k4=k4,
        model=model, epsilon=epsilon, sample_count=sample_count,
    )
    boundary = cap_residuals(north.y[:, -1], south.y[:, -1], shooting, model, sector)
    return boundary, {"north": north, "south": south}


def centered_fd_jacobian(
    function: Callable[[np.ndarray], np.ndarray], point: np.ndarray,
    relative_step: float = 1.0e-6,
) -> np.ndarray:
    global SHOOTING_JACOBIAN_CALL_COUNT
    SHOOTING_JACOBIAN_CALL_COUNT += 1
    point = np.asarray(point, dtype=float)
    baseline = np.asarray(function(point), dtype=float)
    jacobian = np.empty((baseline.size, point.size), dtype=float)
    for column in range(point.size):
        step = relative_step * max(1.0, abs(point[column]))
        plus = point.copy(); plus[column] += step
        minus = point.copy(); minus[column] -= step
        jacobian[:, column] = (np.asarray(function(plus)) - np.asarray(function(minus))) / (2.0 * step)
    return jacobian


def control_shooting_vector() -> np.ndarray:
    y0 = (8.0 - 2.0 * math.sqrt(10.0)) / 3.0
    q0 = y0 / 2.0
    R0 = 1.0 / math.sqrt(y0)
    rho0 = math.pi * R0 / 2.0
    k4_0 = (1.0 - q0**2 / 2.0) / 6.0
    return np.asarray([0.0, q0, 0.0, 0.0, -q0, rho0, rho0, k4_0])


def exact_control_profile(x: np.ndarray, q: float) -> np.ndarray:
    y0 = (8.0 - 2.0 * math.sqrt(10.0)) / 3.0
    R0 = 1.0 / math.sqrt(y0)
    sign = 1.0 if q >= 0.0 else -1.0
    A = np.zeros_like(x)
    A_x = np.zeros_like(x)
    ell = R0 * np.sin(x / R0)
    ell_x = np.cos(x / R0)
    varphi = np.zeros_like(x)
    varphi_x = np.zeros_like(x)
    a_chi = sign * (1.0 - np.cos(x / R0)) / 2.0
    return np.vstack([A, A_x, ell, ell_x, varphi, varphi_x, a_chi])


def control_audit(cutoffs: tuple[float, ...] = (1.0e-3, 5.0e-4, 2.5e-4)) -> dict[str, Any]:
    payload = {
        "model_parameters_ordered": {
            "Lambda_hat": "1", "mhat_phi_sq": "1", "a_F": "1/4",
            "lambda_hat": "1", "z_sigma_hat": "1", "q_hat": "1"
        },
        "topological_sector_ordered": {"N_F": 1, "N_sigma": 1, "m_sigma": 1},
    }
    model = model_from_payload(payload, control_a_F=True)
    sector = sector_from_payload(payload)
    shooting = control_shooting_vector()
    records: list[dict[str, Any]] = []
    for epsilon in cutoffs:
        boundary, regional = shooting_residual(
            shooting, model, sector, epsilon=epsilon, sample_count=513,
        )
        profile_errors = {}
        for name, index in (("north", 1), ("south", 4)):
            solution = regional[name]
            exact = exact_control_profile(solution.x, shooting[index])
            profile_errors[name] = float(np.max(np.abs(solution.y - exact)))
        records.append({
            "epsilon": epsilon,
            "boundary": boundary,
            "profile_error_max": max(profile_errors.values()),
            "constraint_max": float(max(
                np.max(np.abs(regional["north"].constraint)),
                np.max(np.abs(regional["south"].constraint)),
            )),
            "profile_errors": profile_errors,
        })
    return {
        "cutoffs": records,
        "integration_call_count": INTEGRATION_CALL_COUNT,
        "shooting_jacobian_call_count": SHOOTING_JACOBIAN_CALL_COUNT,
    }


def direct_invocation_denied() -> int:
    print("NOT_AUTHORIZED: independent backend has no direct nonlinear execution entry point")
    return EXIT_NOT_AUTHORIZED


if __name__ == "__main__":
    raise SystemExit(direct_invocation_denied())
