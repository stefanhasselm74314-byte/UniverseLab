#!/usr/bin/env python3
"""Quarantined CP01 background implementation for HZT-M0-S6-C-PHYS-M1.

Available commands:

- audit: verify differentiation, dimensions, the exact a_F=0 control seed and
  the execution firewall. This never runs Newton or shooting.
- run: require a separate GRANTED authorization artifact before any numerical
  construction. The repository's v0.1 authorization is deliberately NOT_GRANTED.

This is a diagnostic implementation, never the official MD-2S solver.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import sys
from typing import Any, Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RUN_CONTRACT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.1.json"
SEED_SPEC = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BSeedSpecification_v0.1.json"
IMPLEMENTATION_CONTRACT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CImplementationContract_v0.1.json"
AUTHORIZATION = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.1.json"

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


class AuthorizationError(RuntimeError):
    pass


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
    raw_blocks: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
    scale_blocks: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
    constraint_raw: np.ndarray
    constraint_scale: np.ndarray


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ImplementationError(f"missing required artifact: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ImplementationError(f"JSON root must be object: {path.relative_to(ROOT)}")
    return value


def chebyshev_lobatto(degree: int) -> Grid:
    if degree < 2:
        raise ValueError("degree must be at least two")
    j = np.arange(degree + 1)
    x_desc = np.cos(np.pi * j / degree)
    tau_desc = (x_desc + 1.0) / 2.0
    weights_desc = (-1.0) ** j
    weights_desc[[0, -1]] *= 0.5
    tau = tau_desc[::-1].copy()
    weights = weights_desc[::-1].copy()
    n = degree + 1
    D = np.zeros((n, n), dtype=float)
    for i in range(n):
        for k in range(n):
            if i != k:
                D[i, k] = weights[k] / (weights[i] * (tau[i] - tau[k]))
        D[i, i] = -np.sum(D[i, :])
    return Grid(degree=degree, tau=tau, D=D, D2=D @ D)


def state_size(degree: int) -> int:
    return 8 * (degree + 1) + 8


def unpack_state(state: np.ndarray, degree: int) -> tuple[list[list[np.ndarray]], np.ndarray]:
    state = np.asarray(state)
    expected = state_size(degree)
    if state.ndim != 1 or state.size != expected:
        raise ValueError(f"state must have shape ({expected},)")
    width = degree + 1
    offset = 0
    regions: list[list[np.ndarray]] = []
    for _ in range(2):
        fields: list[np.ndarray] = []
        for _ in FIELD_ORDER:
            fields.append(state[offset : offset + width])
            offset += width
        regions.append(fields)
    return regions, state[offset : offset + 8]


def pack_state(regions: list[list[np.ndarray]], parameters: np.ndarray) -> np.ndarray:
    return np.concatenate([*regions[0], *regions[1], np.asarray(parameters)])


def _scale(*terms: np.ndarray) -> np.ndarray:
    total = np.ones_like(np.asarray(terms[0]), dtype=np.result_type(*terms, float))
    for term in terms:
        total = total + np.abs(term)
    return total


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
    ell_xx_over_ell = 2.0 / rho**2 * (3.0 * Lhat_t + 2.0 * tau * Lhat_tt) / Lhat
    A_x_ell_x_over_ell = 2.0 / rho**2 * (
        (u_A + tau * u_A_t) * (Lhat + 2.0 * tau * Lhat_t) / Lhat
    )
    varphi_x_ell_x_over_ell = 2.0 / rho**2 * (
        (u_varphi + tau * u_varphi_t) * (Lhat + 2.0 * tau * Lhat_t) / Lhat
    )
    a_chi = tau * u_g

    rho_F = 0.5 * q**2 * np.exp(-8.0 * A + 2.0 * model.a_F * varphi)
    exp_minus_2A = np.exp(-2.0 * A)

    A_terms = (
        4.0 * A_xx,
        10.0 * A_x**2,
        -6.0 * k4 * exp_minus_2A,
        np.full_like(A, model.Lambda_hat),
        0.5 * varphi_x**2,
        0.5 * model.mhat_phi_sq * varphi**2,
        -rho_F,
    )
    F_A = sum(A_terms)

    ell_terms = (
        ell_xx_over_ell,
        3.0 * A_xx,
        6.0 * A_x**2,
        3.0 * A_x_ell_x_over_ell,
        -3.0 * k4 * exp_minus_2A,
        np.full_like(A, model.Lambda_hat),
        0.5 * varphi_x**2,
        0.5 * model.mhat_phi_sq * varphi**2,
        rho_F,
    )
    F_ell = sum(ell_terms)

    varphi_terms = (
        varphi_xx,
        4.0 * A_x * varphi_x,
        varphi_x_ell_x_over_ell,
        -model.mhat_phi_sq * varphi,
        2.0 * model.a_F * rho_F,
    )
    F_varphi = sum(varphi_terms)

    gauge_terms = (
        2.0 / rho * (u_g + tau * u_g_t),
        -q * rho * Lhat * np.exp(-4.0 * A + 2.0 * model.a_F * varphi),
    )
    F_gauge = sum(gauge_terms)

    constraint_terms = (
        -6.0 * k4 * exp_minus_2A,
        6.0 * A_x**2,
        np.full_like(A, model.Lambda_hat),
        4.0 * A_x_ell_x_over_ell,
        -0.5 * varphi_x**2,
        0.5 * model.mhat_phi_sq * varphi**2,
        -rho_F,
    )
    constraint = sum(constraint_terms)

    return RegionEvaluation(
        A=A, ell=ell, varphi=varphi, a_chi=a_chi,
        A_x=A_x, ell_x=ell_x, varphi_x=varphi_x, Lhat=Lhat,
        raw_blocks=(F_A, F_ell, F_varphi, F_gauge),
        scale_blocks=tuple(_scale(*terms) for terms in (A_terms, ell_terms, varphi_terms, gauge_terms)),
        constraint_raw=constraint,
        constraint_scale=_scale(*constraint_terms),
    )


def boundary_residual(
    north: RegionEvaluation, south: RegionEvaluation,
    parameters: np.ndarray, model: Model, sector: Sector,
) -> tuple[np.ndarray, np.ndarray]:
    _, q_N, _, _, q_S, _, _, _ = parameters
    i = -1
    ell_sigma = 0.5 * (north.ell[i] + south.ell[i])
    A_sum = north.A_x[i] + south.A_x[i]
    ell_sum = (north.ell_x[i] + south.ell_x[i]) / ell_sigma
    varphi_sum = north.varphi_x[i] + south.varphi_x[i]
    d_chi = sector.N_sigma - sector.m_sigma * model.q_hat * south.a_chi[i]
    Y_sigma = model.z_sigma_hat * d_chi**2 / ell_sigma**2

    terms = (
        (north.A[i], -south.A[i]),
        (north.ell[i], -south.ell[i]),
        (north.varphi[i], -south.varphi[i]),
        (north.a_chi[i], -south.a_chi[i], -sector.N_F / model.q_hat),
        (-3.0 * A_sum, -ell_sum, model.lambda_hat, 0.5 * Y_sigma),
        (-4.0 * A_sum, model.lambda_hat, -0.5 * Y_sigma),
        (north.varphi_x[i], south.varphi_x[i]),
        (
            q_N * np.exp(-4.0 * north.A[i]) / ell_sigma,
            q_S * np.exp(-4.0 * south.A[i]) / ell_sigma,
            -sector.m_sigma * model.q_hat * model.z_sigma_hat * d_chi / ell_sigma**2,
        ),
    )
    raw = np.asarray([sum(row) for row in terms], dtype=np.result_type(parameters, north.A, float))
    scale = np.asarray([1.0 + sum(abs(value) for value in row) for row in terms])
    return raw, scale


def residual_and_scale(
    state: np.ndarray, degree: int, model: Model, sector: Sector,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    grid = chebyshev_lobatto(degree)
    regions, p = unpack_state(state, degree)
    varphi_N_0, q_N, A_S_0, varphi_S_0, q_S, rho_N, rho_S, k4 = p
    north = evaluate_region(
        regions[0], A0=0.0, varphi0=varphi_N_0, rho=rho_N,
        q=q_N, k4=k4, grid=grid, model=model,
    )
    south = evaluate_region(
        regions[1], A0=A_S_0, varphi0=varphi_S_0, rho=rho_S,
        q=q_S, k4=k4, grid=grid, model=model,
    )
    boundary_raw, boundary_scale = boundary_residual(north, south, p, model, sector)
    raw = np.concatenate([*north.raw_blocks, *south.raw_blocks, boundary_raw])
    scale = np.concatenate([*north.scale_blocks, *south.scale_blocks, boundary_scale])
    metadata = {
        "north": north,
        "south": south,
        "boundary_raw": boundary_raw,
        "constraint_norm": float(max(
            np.max(np.abs(north.constraint_raw / north.constraint_scale)),
            np.max(np.abs(south.constraint_raw / south.constraint_scale)),
        )),
    }
    return raw, scale, metadata


def normalized_residual(state: np.ndarray, degree: int, model: Model, sector: Sector) -> np.ndarray:
    raw, scale, _ = residual_and_scale(state, degree, model, sector)
    return raw / scale


def control_seed_state(degree: int) -> np.ndarray:
    grid = chebyshev_lobatto(degree)
    tau = grid.tau
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


def seed_direction(degree: int) -> np.ndarray:
    grid = chebyshev_lobatto(degree)
    tau = grid.tau
    one_minus_tau = 1.0 - tau
    const = np.ones_like(tau)
    regions = [
        [const / 64.0, one_minus_tau / 64.0, one_minus_tau / 32.0, one_minus_tau / 64.0],
        [-const / 64.0, -one_minus_tau / 64.0, -one_minus_tau / 32.0, -one_minus_tau / 64.0],
    ]
    parameters = np.asarray([1/32, 1/64, 0.0, -1/32, -1/64, 1/64, -1/64, 1/128])
    return pack_state(regions, parameters)


def seven_seeds(degree: int) -> list[np.ndarray]:
    base = control_seed_state(degree)
    direction = seed_direction(degree)
    multipliers = (0.0, 1/8, -1/8, 1/4, -1/4, 1/2, -1/2)
    return [base + multiplier * direction for multiplier in multipliers]


def admissible(state: np.ndarray, degree: int) -> bool:
    if np.iscomplexobj(state):
        return True
    regions, p = unpack_state(state, degree)
    rho_N, rho_S = float(p[5]), float(p[6])
    if rho_N <= 0.0 or rho_S <= 0.0 or not np.all(np.isfinite(state)):
        return False
    tau = chebyshev_lobatto(degree).tau
    return bool(
        np.min(1.0 + tau * regions[0][1]) > 0.0
        and np.min(1.0 + tau * regions[1][1]) > 0.0
    )


def complex_step_jacobian(
    state: np.ndarray, degree: int, model: Model, sector: Sector,
    fixed_scale: np.ndarray, step: float = 1.0e-30,
) -> np.ndarray:
    state = np.asarray(state, dtype=float)
    jac = np.empty((state.size, state.size), dtype=float)
    for column in range(state.size):
        probe = state.astype(complex)
        probe[column] += 1j * step
        raw, _, _ = residual_and_scale(probe, degree, model, sector)
        jac[:, column] = np.imag(raw / fixed_scale) / step
    return jac


def damped_newton(
    initial: np.ndarray, degree: int, model: Model, sector: Sector,
    *, maximum_iterations: int = 80, residual_tolerance: float = 1.0e-10,
    step_tolerance: float = 1.0e-11, trust_radius: float = 1.0,
) -> dict[str, Any]:
    state = np.asarray(initial, dtype=float).copy()
    history: list[dict[str, float]] = []
    for iteration in range(maximum_iterations):
        raw, scale, metadata = residual_and_scale(state, degree, model, sector)
        normalized = raw / scale
        norm = float(np.max(np.abs(normalized)))
        jac = complex_step_jacobian(state, degree, model, sector, scale)
        singular_values = np.linalg.svd(jac, compute_uv=False)
        delta = np.linalg.lstsq(jac, -normalized, rcond=1.0e-12)[0]
        delta_norm = float(np.linalg.norm(delta))
        if delta_norm > trust_radius:
            delta *= trust_radius / delta_norm
            delta_norm = trust_radius
        accepted = False
        for backtrack in range(13):
            factor = 0.5**backtrack
            candidate = state + factor * delta
            if not admissible(candidate, degree):
                continue
            candidate_norm = float(np.max(np.abs(normalized_residual(candidate, degree, model, sector))))
            if candidate_norm < norm:
                state = candidate
                accepted = True
                break
        history.append({
            "iteration": float(iteration),
            "normalized_residual_inf": norm,
            "step_2": delta_norm,
            "sigma_min": float(singular_values[-1]),
            "sigma_max": float(singular_values[0]),
            "constraint_inf": float(metadata["constraint_norm"]),
        })
        if norm <= residual_tolerance and delta_norm <= step_tolerance:
            return {"converged": True, "state": state, "history": history}
        if not accepted:
            return {"converged": False, "state": state, "history": history, "failure": "NO_DESCENT_STEP"}
    return {"converged": False, "state": state, "history": history, "failure": "MAXIMUM_ITERATIONS"}


def model_from_run_contract(*, control_a_F: bool = False) -> Model:
    run = load_json(RUN_CONTRACT)
    p = run["frozen_inputs"]["model_parameters"]
    return Model(
        Lambda_hat=float(p["Lambda_hat"]),
        mhat_phi_sq=float(p["mhat_phi_sq"]),
        a_F=0.0 if control_a_F else float(p["a_F"]),
        lambda_hat=float(p["lambda_hat"]),
        z_sigma_hat=float(p["z_sigma_hat"]),
        q_hat=float(p["q_hat"]),
    )


def sector_from_run_contract() -> Sector:
    run = load_json(RUN_CONTRACT)
    t = run["frozen_inputs"]["topological_sector"]
    return Sector(N_F=int(t["N_F"]), N_sigma=int(t["N_sigma"]), m_sigma=int(t["m_sigma"]))


def audit() -> dict[str, Any]:
    degree = 24
    grid = chebyshev_lobatto(degree)
    polynomial_errors = {}
    for power in range(8):
        values = grid.tau**power
        exact = np.zeros_like(values) if power == 0 else power * grid.tau ** (power - 1)
        polynomial_errors[str(power)] = float(np.max(np.abs(grid.D @ values - exact)))
    if max(polynomial_errors.values()) > 5.0e-12:
        raise ImplementationError("Chebyshev differentiation audit failed")

    seed = control_seed_state(degree)
    control_model = model_from_run_contract(control_a_F=True)
    sector = sector_from_run_contract()
    raw, scale, metadata = residual_and_scale(seed, degree, control_model, sector)
    bulk = raw[:-8]
    boundary = metadata["boundary_raw"]
    y0 = (8.0 - 2.0 * math.sqrt(10.0)) / 3.0
    expected_boundary = np.asarray([
        0.0, 0.0, 0.0, 0.0,
        1.0 + 9.0 * y0 / 8.0,
        1.0 - 9.0 * y0 / 8.0,
        0.0,
        -3.0 * y0 / 2.0,
    ])
    if np.max(np.abs(bulk)) > 1.0e-9:
        raise ImplementationError("control-seed bulk assembly audit failed")
    if np.max(np.abs(boundary - expected_boundary)) > 5.0e-11:
        raise ImplementationError("control-seed boundary assembly audit failed")

    authorization = load_json(AUTHORIZATION)
    if authorization["authorized"] is not False or authorization["status"] != "NOT_GRANTED":
        raise ImplementationError("repository authorization artifact must remain NOT_GRANTED")
    return {
        "status": "PASS_IMPLEMENTATION_AUDIT_NO_SOLVER_EXECUTION",
        "degree": degree,
        "state_size": state_size(degree),
        "polynomial_derivative_error_max": max(polynomial_errors.values()),
        "control_bulk_raw_inf": float(np.max(np.abs(bulk))),
        "control_boundary_raw": dict(zip(BOUNDARY_ORDER, map(float, boundary))),
        "control_constraint_inf": float(metadata["constraint_norm"]),
        "seven_seed_count": len(seven_seeds(degree)),
        "authorization_status": authorization["status"],
        "newton_executed": False,
        "shooting_executed": False,
        "candidate_background_created": False,
    }


def require_execution_authorization() -> dict[str, Any]:
    authorization = load_json(AUTHORIZATION)
    implementation = load_json(IMPLEMENTATION_CONTRACT)
    run = load_json(RUN_CONTRACT)
    if authorization.get("authorized") is not True:
        raise AuthorizationError("BACKGROUND-3C execution authorization is NOT_GRANTED")
    if authorization.get("status") != "GRANTED_QUARANTINED_DIAGNOSTIC":
        raise AuthorizationError("authorization status is not GRANTED_QUARANTINED_DIAGNOSTIC")
    if authorization.get("run_id") != run["run_id"]:
        raise AuthorizationError("authorization run_id mismatch")
    if authorization.get("implementation_git_blob_sha") != implementation["implementation_source"]["git_blob_sha"]:
        raise AuthorizationError("authorization implementation hash mismatch")
    return authorization


def execute_quarantined() -> dict[str, Any]:
    require_execution_authorization()
    run = load_json(RUN_CONTRACT)
    model = model_from_run_contract(control_a_F=False)
    sector = sector_from_run_contract()
    degree = int(run["method_bindings"]["mesh_levels"][0])
    results = []
    for index, seed in enumerate(seven_seeds(degree)):
        solve = damped_newton(seed, degree, model, sector)
        results.append({
            "seed_index": index,
            "converged": bool(solve["converged"]),
            "history": solve["history"],
        })
    return {
        "classification": "QUARANTINED_DIAGNOSTIC_EXECUTION_RAW",
        "run_id": run["run_id"],
        "degree": degree,
        "seed_results": results,
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit", "run"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = audit() if args.command == "audit" else execute_quarantined()
    except AuthorizationError as exc:
        payload = {"status": "NOT_AUTHORIZED", "error": str(exc), "solver_executed": False}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"NOT AUTHORIZED: {exc}")
        return EXIT_NOT_AUTHORIZED
    except (ImplementationError, ValueError, KeyError, FloatingPointError) as exc:
        payload = {"status": "FAIL", "error": str(exc)}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"FAIL: {exc}")
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
