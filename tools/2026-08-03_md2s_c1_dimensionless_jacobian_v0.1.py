#!/usr/bin/env python3
"""Diagnostic dimensionless C1 anchor and forward-mode AD Jacobian evaluator.

This module does not implement a root finder or authorize a global BVP solve.
It evaluates a fixed-step RK4 IVP-to-boundary-residual map at the exact C1
analytic anchor and differentiates that complete discrete map with forward-mode
automatic differentiation.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, replace
from typing import Iterable, List, Sequence, Tuple, Union

Number = Union[float, "Dual"]


class ContractError(ValueError):
    """Raised when a fail-closed contract invariant is violated."""


class Dual:
    """Scalar forward-mode dual number carrying a dense tangent vector."""

    __slots__ = ("value", "derivative")

    def __init__(self, value: float, derivative: Sequence[float]):
        self.value = float(value)
        self.derivative = tuple(float(item) for item in derivative)

    @classmethod
    def constant(cls, value: float, width: int) -> "Dual":
        return cls(value, (0.0,) * width)

    @classmethod
    def variable(cls, value: float, index: int, width: int) -> "Dual":
        if not 0 <= index < width:
            raise ContractError("dual variable index outside tangent width")
        derivative = [0.0] * width
        derivative[index] = 1.0
        return cls(value, derivative)

    def _coerce(self, other: Number) -> "Dual":
        if isinstance(other, Dual):
            if len(other.derivative) != len(self.derivative):
                raise ContractError("dual tangent widths do not match")
            return other
        return Dual.constant(float(other), len(self.derivative))

    def __add__(self, other: Number) -> "Dual":
        rhs = self._coerce(other)
        return Dual(
            self.value + rhs.value,
            [a + b for a, b in zip(self.derivative, rhs.derivative)],
        )

    __radd__ = __add__

    def __neg__(self) -> "Dual":
        return Dual(-self.value, [-item for item in self.derivative])

    def __sub__(self, other: Number) -> "Dual":
        return self + (-self._coerce(other))

    def __rsub__(self, other: Number) -> "Dual":
        return self._coerce(other) - self

    def __mul__(self, other: Number) -> "Dual":
        rhs = self._coerce(other)
        return Dual(
            self.value * rhs.value,
            [
                left * rhs.value + self.value * right
                for left, right in zip(self.derivative, rhs.derivative)
            ],
        )

    __rmul__ = __mul__

    def __truediv__(self, other: Number) -> "Dual":
        rhs = self._coerce(other)
        if rhs.value == 0.0:
            raise ContractError("division by zero in dual evaluation")
        inverse_square = 1.0 / (rhs.value * rhs.value)
        return Dual(
            self.value / rhs.value,
            [
                (left * rhs.value - self.value * right) * inverse_square
                for left, right in zip(self.derivative, rhs.derivative)
            ],
        )

    def __rtruediv__(self, other: Number) -> "Dual":
        return self._coerce(other) / self

    def __pow__(self, exponent: int) -> "Dual":
        if not isinstance(exponent, int):
            raise ContractError("only integer powers are permitted")
        if exponent < 0 and self.value == 0.0:
            raise ContractError("negative power of zero")
        value = self.value**exponent
        factor = 0.0 if exponent == 0 else exponent * self.value ** (exponent - 1)
        return Dual(value, [factor * item for item in self.derivative])


def scalar_exp(value: Number) -> Number:
    if isinstance(value, Dual):
        exponential = math.exp(value.value)
        return Dual(exponential, [exponential * item for item in value.derivative])
    return math.exp(float(value))


def scalar_value(value: Number) -> float:
    return value.value if isinstance(value, Dual) else float(value)


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
        finite_values = (
            self.lambda_geom,
            self.u0,
            self.m2,
            self.varphi_star,
            self.lambda0,
            self.lambda1,
            self.z_sigma,
            self.q0,
        )
        if not all(math.isfinite(item) for item in finite_values):
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


def potential(varphi: Number, parameters: C1Parameters) -> Number:
    return parameters.u0 + 0.5 * parameters.m2 * (
        varphi - parameters.varphi_star
    ) ** 2


def center_state(
    A0: Number,
    varphi0: Number,
    q: Number,
    k4: Number,
    parameters: C1Parameters,
    epsilon: float = CENTER_EPSILON,
) -> List[Number]:
    magnetic0 = q**2 * scalar_exp(-8.0 * A0)
    curvature0 = k4 * scalar_exp(-2.0 * A0)
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
        A0 + a2 * epsilon**2,
        2.0 * a2 * epsilon,
        epsilon * (1.0 + c2 * epsilon**2),
        1.0 + 3.0 * c2 * epsilon**2,
        varphi0 + p2 * epsilon**2,
        2.0 * p2 * epsilon,
        0.5 * q * scalar_exp(-4.0 * A0) * epsilon**2,
    ]


def rhs(
    state: Sequence[Number],
    q: Number,
    k4: Number,
    parameters: C1Parameters,
) -> List[Number]:
    A, A_x, ell, ell_x, varphi, varphi_x, _a_chi = state
    if scalar_value(ell) == 0.0:
        raise ContractError("ell reached zero inside radial integration")
    magnetic = q**2 * scalar_exp(-8.0 * A)
    exp_minus_2A = scalar_exp(-2.0 * A)
    A_xx = (
        -10.0 * A_x**2
        + 6.0 * k4 * exp_minus_2A
        - parameters.lambda_geom
        - 0.5 * varphi_x**2
        - potential(varphi, parameters)
        + 0.5 * magnetic
    ) / 4.0
    ell_xx = ell * (
        -3.0 * A_xx
        - 6.0 * A_x**2
        - 3.0 * A_x * ell_x / ell
        + 3.0 * k4 * exp_minus_2A
        - parameters.lambda_geom
        - 0.5 * varphi_x**2
        - potential(varphi, parameters)
        - 0.5 * magnetic
    )
    varphi_xx = -(
        4.0 * A_x + ell_x / ell
    ) * varphi_x + parameters.m2 * (varphi - parameters.varphi_star)
    a_chi_x = q * ell * scalar_exp(-4.0 * A)
    return [A_x, A_xx, ell_x, ell_xx, varphi_x, varphi_xx, a_chi_x]


def rr_constraint(
    state: Sequence[Number],
    q: Number,
    k4: Number,
    parameters: C1Parameters,
) -> Number:
    A, A_x, ell, ell_x, varphi, varphi_x, _a_chi = state
    magnetic = q**2 * scalar_exp(-8.0 * A)
    return (
        6.0 * A_x**2
        + 4.0 * A_x * ell_x / ell
        - 6.0 * k4 * scalar_exp(-2.0 * A)
        + parameters.lambda_geom
        - 0.5 * varphi_x**2
        + potential(varphi, parameters)
        - 0.5 * magnetic
    )


def _state_add(
    state: Sequence[Number],
    slope: Sequence[Number],
    factor: Number,
) -> List[Number]:
    return [value + factor * derivative for value, derivative in zip(state, slope)]


def integrate_region(
    A0: Number,
    varphi0: Number,
    q: Number,
    rho: Number,
    k4: Number,
    parameters: C1Parameters = DEFAULT_PARAMETERS,
    steps: int = 200,
    epsilon: float = CENTER_EPSILON,
) -> Tuple[List[Number], float | None]:
    parameters.validate()
    if not isinstance(steps, int) or steps < 8:
        raise ContractError("steps must be an integer >= 8")
    if scalar_value(rho) <= epsilon:
        raise ContractError("rho must be greater than center epsilon")
    state = center_state(A0, varphi0, q, k4, parameters, epsilon)
    step = (rho - epsilon) / steps
    monitor_constraint = not any(isinstance(item, Dual) for item in state)
    max_constraint = (
        abs(scalar_value(rr_constraint(state, q, k4, parameters)))
        if monitor_constraint
        else None
    )
    for _ in range(steps):
        k1 = rhs(state, q, k4, parameters)
        k2 = rhs(_state_add(state, k1, step / 2.0), q, k4, parameters)
        k3 = rhs(_state_add(state, k2, step / 2.0), q, k4, parameters)
        k4_stage = rhs(_state_add(state, k3, step), q, k4, parameters)
        state = [
            value
            + step
            * (s1 + 2.0 * s2 + 2.0 * s3 + s4)
            / 6.0
            for value, s1, s2, s3, s4 in zip(state, k1, k2, k3, k4_stage)
        ]
        if monitor_constraint:
            assert max_constraint is not None
            max_constraint = max(
                max_constraint,
                abs(scalar_value(rr_constraint(state, q, k4, parameters))),
            )
    return state, max_constraint


def normalized_residuals(
    shooting_vector: Sequence[Number],
    parameters: C1Parameters = DEFAULT_PARAMETERS,
    steps: int = 200,
) -> List[Number]:
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
    ) = shooting_vector
    north, _ = integrate_region(
        0.0, varphi_N_0, q_N, rho_N, k4, parameters, steps
    )
    south, _ = integrate_region(
        A_S_0, varphi_S_0, q_S, rho_S, k4, parameters, steps
    )
    A_N, A_N_x, ell_N, ell_N_x, varphi_N, varphi_N_x, a_N = north
    A_S, A_S_x, ell_S, ell_S_x, varphi_S, varphi_S_x, a_S = south
    A_bar = (A_N + A_S) / 2.0
    ell_bar = (ell_N + ell_S) / 2.0
    varphi_bar = (varphi_N + varphi_S) / 2.0
    if scalar_value(ell_bar) <= 0.0:
        raise ContractError("mean cap radius must remain positive")
    A_sigma = A_N_x + A_S_x
    L_sigma = ell_N_x / ell_N + ell_S_x / ell_S
    d_chi = parameters.n_sigma - parameters.q0 * a_N
    Y_sigma = parameters.z_sigma * d_chi**2 / ell_bar**2
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
        scalar_exp(-4.0 * A_bar)
        * (q_N + q_S)
        / ell_bar
        - parameters.q0 * parameters.z_sigma * d_chi / ell_bar**2,
    ]
    return [item / scale for item, scale in zip(raw, RESIDUAL_SCALES)]


def analytic_anchor_profiles(x: float, region: str) -> Tuple[float, ...]:
    if region not in {"N", "S"}:
        raise ContractError("region must be N or S")
    sign = 1.0 if region == "N" else -1.0
    return (
        0.0,
        0.0,
        math.sin(x),
        math.cos(x),
        0.0,
        0.0,
        0.5 * sign * (1.0 - math.cos(x)),
    )


def analytic_anchor_closed_form_residuals() -> Tuple[float, ...]:
    cap = math.pi / 2.0
    north = analytic_anchor_profiles(cap, "N")
    south = analytic_anchor_profiles(cap, "S")
    A_N, A_N_x, ell_N, ell_N_x, varphi_N, varphi_N_x, a_N = north
    A_S, A_S_x, ell_S, ell_S_x, varphi_S, varphi_S_x, a_S = south
    d_chi = DEFAULT_PARAMETERS.n_sigma - DEFAULT_PARAMETERS.q0 * a_N
    A_sigma = A_N_x + A_S_x
    L_sigma = ell_N_x / ell_N + ell_S_x / ell_S
    Y_sigma = DEFAULT_PARAMETERS.z_sigma * d_chi**2 / ell_N**2
    raw = (
        A_N - A_S,
        ell_N - ell_S,
        varphi_N - varphi_S,
        a_N - a_S - DEFAULT_PARAMETERS.n_flux / DEFAULT_PARAMETERS.q0,
        -(3.0 * A_sigma + L_sigma) + 0.5 * Y_sigma,
        -4.0 * A_sigma - 0.5 * Y_sigma,
        varphi_N_x + varphi_S_x,
        (0.5 - 0.5) / ell_N
        - DEFAULT_PARAMETERS.q0 * DEFAULT_PARAMETERS.z_sigma * d_chi / ell_N**2,
    )
    return tuple(item / scale for item, scale in zip(raw, RESIDUAL_SCALES))


def ad_jacobian(
    shooting_vector: Sequence[float] = ANCHOR_VECTOR,
    parameters: C1Parameters = DEFAULT_PARAMETERS,
    steps: int = 200,
) -> Tuple[List[float], List[List[float]]]:
    if len(shooting_vector) != 8:
        raise ContractError("C1 shooting vector must contain exactly eight entries")
    dual_vector = [
        Dual.variable(value, index, len(shooting_vector))
        for index, value in enumerate(shooting_vector)
    ]
    dual_residuals = normalized_residuals(dual_vector, parameters, steps)
    if not all(isinstance(item, Dual) for item in dual_residuals):
        raise ContractError("automatic differentiation did not propagate to all residuals")
    values = [item.value for item in dual_residuals]  # type: ignore[union-attr]
    jacobian = [list(item.derivative) for item in dual_residuals]  # type: ignore[union-attr]
    return values, jacobian


def _symmetric_eigenvalues_jacobi(
    matrix: Sequence[Sequence[float]],
    tolerance: float = 1.0e-14,
    max_iterations: int = 10000,
) -> List[float]:
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ContractError("Jacobi eigenvalue input must be nonempty and square")
    work = [list(map(float, row)) for row in matrix]
    for _ in range(max_iterations):
        largest = 0.0
        p = 0
        q = 0
        for row in range(size):
            for column in range(row + 1, size):
                candidate = abs(work[row][column])
                if candidate > largest:
                    largest = candidate
                    p, q = row, column
        if largest < tolerance:
            break
        app = work[p][p]
        aqq = work[q][q]
        apq = work[p][q]
        tau = (aqq - app) / (2.0 * apq)
        tangent = (1.0 if tau >= 0.0 else -1.0) / (
            abs(tau) + math.sqrt(1.0 + tau * tau)
        )
        cosine = 1.0 / math.sqrt(1.0 + tangent * tangent)
        sine = tangent * cosine
        for index in range(size):
            if index in (p, q):
                continue
            aip = work[index][p]
            aiq = work[index][q]
            work[index][p] = work[p][index] = cosine * aip - sine * aiq
            work[index][q] = work[q][index] = sine * aip + cosine * aiq
        work[p][p] = (
            cosine * cosine * app
            - 2.0 * sine * cosine * apq
            + sine * sine * aqq
        )
        work[q][q] = (
            sine * sine * app
            + 2.0 * sine * cosine * apq
            + cosine * cosine * aqq
        )
        work[p][q] = work[q][p] = 0.0
    else:
        raise ContractError("Jacobi eigenvalue iteration did not converge")
    return sorted((work[index][index] for index in range(size)), reverse=True)


def singular_values(jacobian: Sequence[Sequence[float]]) -> List[float]:
    rows = len(jacobian)
    columns = len(jacobian[0]) if rows else 0
    if rows == 0 or columns == 0 or any(len(row) != columns for row in jacobian):
        raise ContractError("Jacobian must be a nonempty rectangular matrix")
    gram = [
        [
            sum(jacobian[row][left] * jacobian[row][right] for row in range(rows))
            for right in range(columns)
        ]
        for left in range(columns)
    ]
    eigenvalues = _symmetric_eigenvalues_jacobi(gram)
    return [math.sqrt(max(value, 0.0)) for value in eigenvalues]


def rank_and_condition(jacobian: Sequence[Sequence[float]]) -> Tuple[int, float, List[float], float]:
    values = singular_values(jacobian)
    maximum = values[0]
    threshold = max(1.0e-12, 1.0e-10 * maximum)
    rank = sum(value > threshold for value in values)
    condition = math.inf if values[-1] <= threshold else maximum / values[-1]
    return rank, condition, values, threshold


def relative_frobenius_difference(
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
    denominator = math.sqrt(
        sum(value * value for row in right for value in row)
    )
    if denominator == 0.0:
        raise ContractError("right matrix has zero Frobenius norm")
    return numerator / denominator


def anchor_constraint_maximum(steps: int = 200) -> float:
    north, north_constraint = integrate_region(
        0.0,
        0.0,
        0.5,
        math.pi / 2.0,
        0.25,
        DEFAULT_PARAMETERS,
        steps,
    )
    south, south_constraint = integrate_region(
        0.0,
        0.0,
        -0.5,
        math.pi / 2.0,
        0.25,
        DEFAULT_PARAMETERS,
        steps,
    )
    del north, south
    assert north_constraint is not None and south_constraint is not None
    return max(north_constraint, south_constraint)


def evaluate_anchor(steps: int = 200) -> dict:
    residuals, jacobian = ad_jacobian(ANCHOR_VECTOR, DEFAULT_PARAMETERS, steps)
    rank, condition, values, threshold = rank_and_condition(jacobian)
    return {
        "model_id": "HZT-M0-S6-C1",
        "status": "DIAGNOSTIC_ONLY",
        "steps_per_region": steps,
        "max_normalized_residual": max(abs(item) for item in residuals),
        "normalized_residuals": dict(zip(RESIDUAL_NAMES, residuals)),
        "constraint_maximum": anchor_constraint_maximum(steps),
        "unknown_order": list(UNKNOWN_NAMES),
        "residual_order": list(RESIDUAL_NAMES),
        "jacobian": jacobian,
        "singular_values": values,
        "rank_threshold": threshold,
        "rank": rank,
        "condition_number": condition,
        "solver_authorized": False,
        "R1.1": "BLOCKED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
    }


def convergence_report(step_counts: Iterable[int] = (100, 200, 400, 800)) -> dict:
    reports = {steps: evaluate_anchor(steps) for steps in step_counts}
    jacobian_change = relative_frobenius_difference(
        reports[400]["jacobian"], reports[800]["jacobian"]
    ) if 400 in reports and 800 in reports else None
    return {
        "reports": {
            str(steps): {
                key: value
                for key, value in report.items()
                if key != "jacobian"
            }
            for steps, report in reports.items()
        },
        "jacobian_relative_change_400_to_800": jacobian_change,
        "solver_authorized": False,
    }


def shift_null_regression(steps: int = 200) -> dict:
    shift_parameters = replace(DEFAULT_PARAMETERS, m2=0.0, lambda1=0.0)
    residuals, jacobian = ad_jacobian(ANCHOR_VECTOR, shift_parameters, steps)
    rank, condition, values, threshold = rank_and_condition(jacobian)
    return {
        "steps_per_region": steps,
        "max_normalized_residual": max(abs(item) for item in residuals),
        "singular_values": values,
        "rank_threshold": threshold,
        "rank": rank,
        "condition_number": condition,
        "expected_rank": 7,
    }


def validate_preflight() -> dict:
    closed_form = analytic_anchor_closed_form_residuals()
    report_200 = evaluate_anchor(200)
    report_400 = evaluate_anchor(400)
    report_800 = evaluate_anchor(800)
    relative_change = relative_frobenius_difference(
        report_400["jacobian"], report_800["jacobian"]
    )
    shift = shift_null_regression(200)
    checks = {
        "closed_form_residual": max(abs(item) for item in closed_form) <= 1.0e-13,
        "rk4_200_residual": report_200["max_normalized_residual"] <= 2.0e-10,
        "rk4_400_residual": report_400["max_normalized_residual"] <= 2.0e-11,
        "jacobian_step_convergence": relative_change <= 1.0e-9,
        "anchor_rank": report_800["rank"] == 8,
        "anchor_condition": report_800["condition_number"] < 1.0e6,
        "constraint_propagation": report_800["constraint_maximum"] <= 1.0e-12,
        "shift_null_regression": shift["rank"] == 7,
        "governance_firewall": (
            report_800["solver_authorized"] is False
            and report_800["R1.1"] == "BLOCKED"
            and report_800["K1-D"] == "NOT_RELEASED"
            and report_800["K1-E"] == "NOT_ADMISSIBLE"
        ),
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ContractError("preflight failed: " + ", ".join(failed))
    return {
        "status": "PASS",
        "checks": checks,
        "closed_form_max_residual": max(abs(item) for item in closed_form),
        "rk4_200_max_residual": report_200["max_normalized_residual"],
        "rk4_400_max_residual": report_400["max_normalized_residual"],
        "rk4_800_max_residual": report_800["max_normalized_residual"],
        "jacobian_relative_change_400_to_800": relative_change,
        "rank_800": report_800["rank"],
        "condition_number_800": report_800["condition_number"],
        "singular_values_800": report_800["singular_values"],
        "shift_rank": shift["rank"],
        "solver_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("validate", "anchor", "convergence", "shift-null"),
        default="validate",
    )
    parser.add_argument("--steps", type=int, default=200)
    args = parser.parse_args()
    try:
        if args.mode == "validate":
            payload = validate_preflight()
        elif args.mode == "anchor":
            payload = evaluate_anchor(args.steps)
        elif args.mode == "convergence":
            payload = convergence_report()
        else:
            payload = shift_null_regression(args.steps)
    except (ContractError, OverflowError, ZeroDivisionError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
