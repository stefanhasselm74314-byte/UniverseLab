#!/usr/bin/env python3
"""Independent C1 implicit-midpoint backend and linear continuation preflight.

This module is diagnostic-only. It contains no nonlinear BVP corrector, root
finder, continuation stepper, or official solver release.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import pathlib
import sys
from dataclasses import dataclass, replace
from typing import Iterable, List, Sequence, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[1]
REFERENCE_TOOL = ROOT / "tools" / "2026-08-03_md2s_c1_dimensionless_jacobian_v0.1.py"

ANCHOR_VECTOR = (
    0.0,
    0.5,
    0.0,
    0.0,
    -0.5,
    math.pi / 2.0,
    math.pi / 2.0,
    0.25,
)
UNKNOWN_NAMES = (
    "varphi_N_0",
    "q_N",
    "A_S_0",
    "varphi_S_0",
    "q_S",
    "rho_N",
    "rho_S",
    "k4",
)
RESIDUAL_NAMES = (
    "R_A",
    "R_L",
    "R_varphi",
    "R_patch",
    "R_4d",
    "R_chi",
    "R_scalar",
    "R_gauge",
)
RESIDUAL_SCALES = (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0)
CENTER_EPSILON = 1.0e-5
BASE_STEPS = 100
SHOOTING_RELATIVE_STEP = 2.0e-6
PARAMETER_ABSOLUTE_STEP = 1.0e-6


class ContractError(ValueError):
    """Raised when a fail-closed contract invariant is violated."""


@dataclass(frozen=True)
class C1Parameters:
    lambda_geom: float = 1.0
    u0: float = 0.625
    m2: float = 1.0
    varphi_star: float = 0.0
    lambda0: float = 0.0
    lambda1: float = 0.0
    z_sigma: float = 1.0
    q0: float = 2.0
    n_sigma: int = 1
    n_flux: int = 2

    def validate(self) -> None:
        continuous = (
            self.lambda_geom,
            self.u0,
            self.m2,
            self.varphi_star,
            self.lambda0,
            self.lambda1,
            self.z_sigma,
            self.q0,
        )
        if not all(math.isfinite(item) for item in continuous):
            raise ContractError("all continuous C1 parameters must be finite")
        if self.m2 < 0.0:
            raise ContractError("m2 must be nonnegative")
        if self.z_sigma <= 0.0:
            raise ContractError("z_sigma must be strictly positive")
        if self.q0 <= 0.0:
            raise ContractError("q0 must be strictly positive")
        if not isinstance(self.n_sigma, int) or not isinstance(self.n_flux, int):
            raise ContractError("winding and flux sectors must be integers")


DEFAULT_PARAMETERS = C1Parameters()


def _load_reference_module():
    spec = importlib.util.spec_from_file_location("md2s_c1_reference_ad", REFERENCE_TOOL)
    if spec is None or spec.loader is None:
        raise ContractError("unable to load reference AD evaluator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def potential(varphi: float, parameters: C1Parameters) -> float:
    return parameters.u0 + 0.5 * parameters.m2 * (
        varphi - parameters.varphi_star
    ) ** 2


def center_state(
    A0: float,
    varphi0: float,
    q: float,
    k4: float,
    parameters: C1Parameters,
    epsilon: float = CENTER_EPSILON,
) -> List[float]:
    magnetic0 = q * q * math.exp(-8.0 * A0)
    curvature0 = k4 * math.exp(-2.0 * A0)
    u_value = potential(varphi0, parameters)
    a2 = (
        6.0 * curvature0
        - parameters.lambda_geom
        - u_value
        + 0.5 * magnetic0
    ) / 8.0
    c2 = (
        u_value / 12.0
        - 5.0 * magnetic0 / 24.0
        - curvature0
        + parameters.lambda_geom / 12.0
    )
    p2 = parameters.m2 * (varphi0 - parameters.varphi_star) / 4.0
    return [
        A0 + a2 * epsilon * epsilon,
        2.0 * a2 * epsilon,
        epsilon * (1.0 + c2 * epsilon * epsilon),
        1.0 + 3.0 * c2 * epsilon * epsilon,
        varphi0 + p2 * epsilon * epsilon,
        2.0 * p2 * epsilon,
        0.5 * q * math.exp(-4.0 * A0) * epsilon * epsilon,
    ]


def rhs(
    state: Sequence[float],
    q: float,
    k4: float,
    parameters: C1Parameters,
) -> List[float]:
    A, A_x, ell, ell_x, varphi, varphi_x, _a_chi = state
    if ell == 0.0:
        raise ContractError("ell reached zero inside radial integration")
    magnetic = q * q * math.exp(-8.0 * A)
    exp_minus_2A = math.exp(-2.0 * A)
    A_xx = (
        -10.0 * A_x * A_x
        + 6.0 * k4 * exp_minus_2A
        - parameters.lambda_geom
        - 0.5 * varphi_x * varphi_x
        - potential(varphi, parameters)
        + 0.5 * magnetic
    ) / 4.0
    ell_xx = ell * (
        -3.0 * A_xx
        - 6.0 * A_x * A_x
        - 3.0 * A_x * ell_x / ell
        + 3.0 * k4 * exp_minus_2A
        - parameters.lambda_geom
        - 0.5 * varphi_x * varphi_x
        - potential(varphi, parameters)
        - 0.5 * magnetic
    )
    varphi_xx = -(
        4.0 * A_x + ell_x / ell
    ) * varphi_x + parameters.m2 * (varphi - parameters.varphi_star)
    a_chi_x = q * ell * math.exp(-4.0 * A)
    return [A_x, A_xx, ell_x, ell_xx, varphi_x, varphi_xx, a_chi_x]


def max_abs(values: Iterable[float]) -> float:
    return max(abs(float(item)) for item in values)


def solve_linear(matrix: Sequence[Sequence[float]], rhs_vector: Sequence[float]) -> List[float]:
    size = len(matrix)
    if size == 0 or len(rhs_vector) != size or any(len(row) != size for row in matrix):
        raise ContractError("linear system must be nonempty and square")
    augmented = [
        [float(item) for item in row] + [float(rhs_vector[index])]
        for index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) <= 1.0e-15:
            raise ContractError("singular linear system in independent backend")
        if pivot != column:
            augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        for index in range(column, size + 1):
            augmented[column][index] /= pivot_value
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor == 0.0:
                continue
            for index in range(column, size + 1):
                augmented[row][index] -= factor * augmented[column][index]
    return [augmented[row][size] for row in range(size)]


def state_jacobian_fd(
    state: Sequence[float],
    q: float,
    k4: float,
    parameters: C1Parameters,
    relative_step: float = 1.0e-7,
) -> List[List[float]]:
    width = len(state)
    jacobian = [[0.0] * width for _ in range(width)]
    for column in range(width):
        step = relative_step * max(1.0, abs(state[column]))
        plus = list(state)
        minus = list(state)
        plus[column] += step
        minus[column] -= step
        f_plus = rhs(plus, q, k4, parameters)
        f_minus = rhs(minus, q, k4, parameters)
        for row in range(width):
            jacobian[row][column] = (f_plus[row] - f_minus[row]) / (2.0 * step)
    return jacobian


def implicit_midpoint_region(
    A0: float,
    varphi0: float,
    q: float,
    rho: float,
    k4: float,
    parameters: C1Parameters = DEFAULT_PARAMETERS,
    steps: int = BASE_STEPS,
    epsilon: float = CENTER_EPSILON,
    newton_tolerance: float = 1.0e-13,
    max_newton_iterations: int = 12,
) -> List[float]:
    parameters.validate()
    if not isinstance(steps, int) or steps < 8:
        raise ContractError("steps must be an integer >= 8")
    if rho <= epsilon:
        raise ContractError("rho must be greater than center epsilon")
    state = center_state(A0, varphi0, q, k4, parameters, epsilon)
    step = (rho - epsilon) / steps
    for _ in range(steps):
        predictor = rhs(state, q, k4, parameters)
        candidate = [value + step * slope for value, slope in zip(state, predictor)]
        converged = False
        for _iteration in range(max_newton_iterations):
            midpoint = [0.5 * (left + right) for left, right in zip(state, candidate)]
            midpoint_rhs = rhs(midpoint, q, k4, parameters)
            defect = [
                right - left - step * slope
                for left, right, slope in zip(state, candidate, midpoint_rhs)
            ]
            if max_abs(defect) <= newton_tolerance:
                converged = True
                break
            rhs_jacobian = state_jacobian_fd(midpoint, q, k4, parameters)
            newton_matrix = [
                [
                    (1.0 if row == column else 0.0)
                    - 0.5 * step * rhs_jacobian[row][column]
                    for column in range(len(state))
                ]
                for row in range(len(state))
            ]
            correction = solve_linear(newton_matrix, [-item for item in defect])
            candidate = [value + delta for value, delta in zip(candidate, correction)]
            if max_abs(correction) <= newton_tolerance:
                midpoint = [
                    0.5 * (left + right) for left, right in zip(state, candidate)
                ]
                final_defect = [
                    right - left - step * slope
                    for left, right, slope in zip(
                        state,
                        candidate,
                        rhs(midpoint, q, k4, parameters),
                    )
                ]
                converged = max_abs(final_defect) <= 1.0e-11
                break
        if not converged:
            raise ContractError("implicit midpoint Newton iteration did not converge")
        state = candidate
    return state


def extrapolated_region(
    A0: float,
    varphi0: float,
    q: float,
    rho: float,
    k4: float,
    parameters: C1Parameters = DEFAULT_PARAMETERS,
    base_steps: int = BASE_STEPS,
) -> List[float]:
    coarse = implicit_midpoint_region(A0, varphi0, q, rho, k4, parameters, base_steps)
    fine = implicit_midpoint_region(A0, varphi0, q, rho, k4, parameters, 2 * base_steps)
    return [
        (4.0 * fine_value - coarse_value) / 3.0
        for coarse_value, fine_value in zip(coarse, fine)
    ]


def normalized_residuals_independent(
    shooting_vector: Sequence[float],
    parameters: C1Parameters = DEFAULT_PARAMETERS,
    base_steps: int = BASE_STEPS,
) -> List[float]:
    if len(shooting_vector) != 8:
        raise ContractError("C1 shooting vector must contain exactly eight entries")
    parameters.validate()
    (
        varphi_N_0,
        q_N,
        A_S_0,
        varphi_S_0,
        q_S,
        rho_N,
        rho_S,
        k4,
    ) = [float(item) for item in shooting_vector]
    north = extrapolated_region(0.0, varphi_N_0, q_N, rho_N, k4, parameters, base_steps)
    south = extrapolated_region(A_S_0, varphi_S_0, q_S, rho_S, k4, parameters, base_steps)
    A_N, A_N_x, ell_N, ell_N_x, varphi_N, varphi_N_x, a_N = north
    A_S, A_S_x, ell_S, ell_S_x, varphi_S, varphi_S_x, a_S = south
    A_bar = 0.5 * (A_N + A_S)
    ell_bar = 0.5 * (ell_N + ell_S)
    varphi_bar = 0.5 * (varphi_N + varphi_S)
    if ell_bar <= 0.0 or ell_N <= 0.0 or ell_S <= 0.0:
        raise ContractError("cap radius must remain positive")
    A_sigma = A_N_x + A_S_x
    L_sigma = ell_N_x / ell_N + ell_S_x / ell_S
    d_chi = parameters.n_sigma - parameters.q0 * a_N
    Y_sigma = parameters.z_sigma * d_chi * d_chi / (ell_bar * ell_bar)
    cap_lambda = parameters.lambda0 + parameters.lambda1 * (
        varphi_bar - parameters.varphi_star
    )
    raw = [
        A_N - A_S,
        ell_N - ell_S,
        varphi_N - varphi_S,
        a_N - a_S - parameters.n_flux / parameters.q0,
        -(3.0 * A_sigma + L_sigma) + cap_lambda + 0.5 * Y_sigma,
        -4.0 * A_sigma + cap_lambda - 0.5 * Y_sigma,
        varphi_N_x + varphi_S_x + parameters.lambda1,
        math.exp(-4.0 * A_bar) * (q_N + q_S) / ell_bar
        - parameters.q0 * parameters.z_sigma * d_chi / (ell_bar * ell_bar),
    ]
    return [item / scale for item, scale in zip(raw, RESIDUAL_SCALES)]


def finite_difference_jacobian(
    shooting_vector: Sequence[float] = ANCHOR_VECTOR,
    parameters: C1Parameters = DEFAULT_PARAMETERS,
    base_steps: int = BASE_STEPS,
    relative_step: float = SHOOTING_RELATIVE_STEP,
) -> Tuple[List[float], List[List[float]]]:
    point = [float(item) for item in shooting_vector]
    baseline = normalized_residuals_independent(point, parameters, base_steps)
    jacobian = [[0.0] * len(point) for _ in baseline]
    for column in range(len(point)):
        step = relative_step * max(1.0, abs(point[column]))
        plus = list(point)
        minus = list(point)
        plus[column] += step
        minus[column] -= step
        residual_plus = normalized_residuals_independent(plus, parameters, base_steps)
        residual_minus = normalized_residuals_independent(minus, parameters, base_steps)
        for row in range(len(baseline)):
            jacobian[row][column] = (
                residual_plus[row] - residual_minus[row]
            ) / (2.0 * step)
    return baseline, jacobian


def matrix_frobenius(matrix: Sequence[Sequence[float]]) -> float:
    return math.sqrt(sum(value * value for row in matrix for value in row))


def matrix_relative_difference(
    left: Sequence[Sequence[float]],
    right: Sequence[Sequence[float]],
) -> float:
    if len(left) != len(right) or any(
        len(left_row) != len(right_row)
        for left_row, right_row in zip(left, right)
    ):
        raise ContractError("matrix dimensions do not match")
    numerator = math.sqrt(
        sum(
            (left_value - right_value) ** 2
            for left_row, right_row in zip(left, right)
            for left_value, right_value in zip(left_row, right_row)
        )
    )
    denominator = matrix_frobenius(right)
    if denominator == 0.0:
        raise ContractError("reference matrix has zero Frobenius norm")
    return numerator / denominator


def vector_relative_difference(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ContractError("vector dimensions do not match")
    numerator = math.sqrt(
        sum((left_value - right_value) ** 2 for left_value, right_value in zip(left, right))
    )
    denominator = math.sqrt(sum(value * value for value in right))
    if denominator == 0.0:
        raise ContractError("reference vector has zero norm")
    return numerator / denominator


def matrix_vector(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> List[float]:
    return [
        sum(value * component for value, component in zip(row, vector))
        for row in matrix
    ]


def lambda0_parameter_derivative(
    shooting_vector: Sequence[float] = ANCHOR_VECTOR,
    base_steps: int = BASE_STEPS,
    absolute_step: float = PARAMETER_ABSOLUTE_STEP,
) -> List[float]:
    plus_parameters = replace(DEFAULT_PARAMETERS, lambda0=absolute_step)
    minus_parameters = replace(DEFAULT_PARAMETERS, lambda0=-absolute_step)
    plus = normalized_residuals_independent(shooting_vector, plus_parameters, base_steps)
    minus = normalized_residuals_independent(shooting_vector, minus_parameters, base_steps)
    return [
        (plus_value - minus_value) / (2.0 * absolute_step)
        for plus_value, minus_value in zip(plus, minus)
    ]


def reference_ad_outputs(steps: int = 800):
    reference = _load_reference_module()
    residuals, jacobian = reference.ad_jacobian(
        reference.ANCHOR_VECTOR,
        reference.DEFAULT_PARAMETERS,
        steps,
    )
    rank, condition, singular_values, threshold = reference.rank_and_condition(jacobian)
    return reference, residuals, jacobian, rank, condition, singular_values, threshold


def continuation_tangent_report(base_steps: int = BASE_STEPS) -> dict:
    independent_residuals, independent_jacobian = finite_difference_jacobian(
        ANCHOR_VECTOR, DEFAULT_PARAMETERS, base_steps
    )
    parameter_derivative = lambda0_parameter_derivative(ANCHOR_VECTOR, base_steps)
    independent_tangent = solve_linear(
        independent_jacobian,
        [-item for item in parameter_derivative],
    )
    (
        reference,
        reference_residuals,
        reference_jacobian,
        reference_rank,
        reference_condition,
        reference_singular_values,
        reference_threshold,
    ) = reference_ad_outputs(800)
    expected_parameter_derivative = [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0]
    reference_tangent = solve_linear(
        reference_jacobian,
        [-item for item in expected_parameter_derivative],
    )
    closure = [
        value + derivative
        for value, derivative in zip(
            matrix_vector(independent_jacobian, independent_tangent),
            parameter_derivative,
        )
    ]
    independent_rank, independent_condition, independent_singular_values, independent_threshold = (
        reference.rank_and_condition(independent_jacobian)
    )
    singular_spectrum_relative = max(
        abs(left - right) / max(abs(right), 1.0e-15)
        for left, right in zip(independent_singular_values, reference_singular_values)
    )
    return {
        "model_id": "HZT-M0-S6-C1",
        "status": "DIAGNOSTIC_ONLY",
        "base_steps_per_region": base_steps,
        "fine_steps_per_region": 2 * base_steps,
        "independent_max_normalized_residual": max_abs(independent_residuals),
        "reference_max_normalized_residual": max_abs(reference_residuals),
        "independent_jacobian": independent_jacobian,
        "reference_jacobian": reference_jacobian,
        "independent_rank": independent_rank,
        "reference_rank": reference_rank,
        "independent_condition_number": independent_condition,
        "reference_condition_number": reference_condition,
        "independent_singular_values": independent_singular_values,
        "reference_singular_values": reference_singular_values,
        "independent_rank_threshold": independent_threshold,
        "reference_rank_threshold": reference_threshold,
        "jacobian_relative_frobenius": matrix_relative_difference(
            independent_jacobian, reference_jacobian
        ),
        "singular_spectrum_max_relative": singular_spectrum_relative,
        "continuation_parameter": "lambda0_hat",
        "parameter_residual_derivative": parameter_derivative,
        "independent_tangent": independent_tangent,
        "reference_tangent": reference_tangent,
        "tangent_relative_difference": vector_relative_difference(
            independent_tangent, reference_tangent
        ),
        "linear_closure_infinity_norm": max_abs(closure),
        "symmetric_tangent_mismatch": max(
            abs(independent_tangent[1] + independent_tangent[4]),
            abs(independent_tangent[5] - independent_tangent[6]),
            abs(independent_tangent[0]),
            abs(independent_tangent[2]),
            abs(independent_tangent[3]),
        ),
        "nonlinear_corrector_implemented": False,
        "root_solver_implemented": False,
        "official_solver_authorized": False,
        "R1.1": "BLOCKED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
    }


def validate_preflight() -> dict:
    residual_50, jacobian_50 = finite_difference_jacobian(
        ANCHOR_VECTOR, DEFAULT_PARAMETERS, 50
    )
    report = continuation_tangent_report(BASE_STEPS)
    jacobian_change = matrix_relative_difference(
        jacobian_50, report["independent_jacobian"]
    )
    expected_parameter_derivative = [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0]
    checks = {
        "independent_residual_50": max_abs(residual_50) <= 1.0e-8,
        "independent_residual_100": report["independent_max_normalized_residual"] <= 1.0e-9,
        "independent_jacobian_convergence": jacobian_change <= 5.0e-8,
        "backend_jacobian_agreement": report["jacobian_relative_frobenius"] <= 2.0e-8,
        "singular_spectrum_agreement": report["singular_spectrum_max_relative"] <= 2.0e-7,
        "independent_rank": report["independent_rank"] == 8,
        "reference_rank": report["reference_rank"] == 8,
        "independent_condition": report["independent_condition_number"] < 1.0e6,
        "parameter_derivative": max_abs(
            [
                actual - expected
                for actual, expected in zip(
                    report["parameter_residual_derivative"],
                    expected_parameter_derivative,
                )
            ]
        ) <= 1.0e-10,
        "linear_tangent_closure": report["linear_closure_infinity_norm"] <= 1.0e-10,
        "backend_tangent_agreement": report["tangent_relative_difference"] <= 2.0e-7,
        "symmetric_tangent": report["symmetric_tangent_mismatch"] <= 1.0e-8,
        "governance_firewall": (
            report["nonlinear_corrector_implemented"] is False
            and report["root_solver_implemented"] is False
            and report["official_solver_authorized"] is False
            and report["R1.1"] == "BLOCKED"
            and report["K1-D"] == "NOT_RELEASED"
            and report["K1-E"] == "NOT_ADMISSIBLE"
        ),
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ContractError("independent backend preflight failed: " + ", ".join(failed))
    return {
        "status": "PASS",
        "checks": checks,
        "independent_residual_50": max_abs(residual_50),
        "independent_residual_100": report["independent_max_normalized_residual"],
        "independent_jacobian_relative_change_50_to_100": jacobian_change,
        "independent_to_reference_jacobian_relative_frobenius": report[
            "jacobian_relative_frobenius"
        ],
        "singular_spectrum_max_relative": report["singular_spectrum_max_relative"],
        "independent_rank": report["independent_rank"],
        "independent_condition_number": report["independent_condition_number"],
        "independent_singular_values": report["independent_singular_values"],
        "continuation_parameter": report["continuation_parameter"],
        "parameter_residual_derivative": report["parameter_residual_derivative"],
        "independent_tangent": report["independent_tangent"],
        "reference_tangent": report["reference_tangent"],
        "tangent_relative_difference": report["tangent_relative_difference"],
        "linear_closure_infinity_norm": report["linear_closure_infinity_norm"],
        "nonlinear_corrector_implemented": False,
        "root_solver_implemented": False,
        "official_solver_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("validate", "report", "residual"),
        default="validate",
    )
    parser.add_argument("--base-steps", type=int, default=BASE_STEPS)
    args = parser.parse_args()
    try:
        if args.mode == "validate":
            payload = validate_preflight()
        elif args.mode == "report":
            payload = continuation_tangent_report(args.base_steps)
            payload.pop("independent_jacobian", None)
            payload.pop("reference_jacobian", None)
        else:
            payload = {
                "base_steps_per_region": args.base_steps,
                "normalized_residuals": dict(
                    zip(
                        RESIDUAL_NAMES,
                        normalized_residuals_independent(
                            ANCHOR_VECTOR, DEFAULT_PARAMETERS, args.base_steps
                        ),
                    )
                ),
                "official_solver_authorized": False,
            }
    except (ContractError, OverflowError, ZeroDivisionError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
