#!/usr/bin/env python3
"""Verified utilities for the conditional MD-2P-corr overlap bridge.

This module derives and evaluates only the flat two-dimensional Gaussian
cumulative overlap fraction

    q(x) = 1 - exp(-x),  x = gamma R_chi^2,

and the explicitly effective partition-mixing closure

    eta_bulk = beta_0 q(1-q).

It does not claim a derivation from the complete 6D action and it does not
release K1-D or K1-E.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class BridgePoint:
    alpha: float
    sigma_B: float
    kappa_6: float
    lambda_chi: float
    beta_0: float
    gamma: float
    R_chi: float
    x: float
    q: float
    eta_bulk: float
    d_eta_dx: float
    d_eta_d_lambda_chi: float
    d_eta_d_kappa_6: float
    d_eta_d_gamma: float
    log_sensitivity_lambda_chi: float
    log_sensitivity_kappa_6: float
    log_sensitivity_gamma: float


def _require_positive(name: str, value: float) -> float:
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive, got {value!r}")
    return value


def _require_nonnegative(name: str, value: float) -> float:
    if not math.isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be finite and nonnegative, got {value!r}")
    return value


def gamma_from_profiles(alpha: float, sigma_B: float) -> float:
    """Return gamma = 2 alpha + 1/sigma_B^2."""
    _require_nonnegative("alpha", alpha)
    _require_positive("sigma_B", sigma_B)
    return 2.0 * alpha + 1.0 / (sigma_B * sigma_B)


def radius_from_tension(kappa_6: float, lambda_chi: float) -> float:
    """Return the inherited candidate radius R_chi = 4/(kappa_6^2 lambda_chi)."""
    _require_positive("kappa_6", kappa_6)
    _require_positive("lambda_chi", lambda_chi)
    return 4.0 / (kappa_6 * kappa_6 * lambda_chi)


def x_from_parameters(gamma: float, kappa_6: float, lambda_chi: float) -> float:
    """Return x = 16 gamma/(kappa_6^4 lambda_chi^2)."""
    _require_positive("gamma", gamma)
    _require_positive("kappa_6", kappa_6)
    _require_positive("lambda_chi", lambda_chi)
    return 16.0 * gamma / (kappa_6**4 * lambda_chi**2)


def q_flat_gaussian_2d(x: float) -> float:
    """Normalized cumulative radial Gaussian fraction in two flat dimensions."""
    _require_nonnegative("x", x)
    return -math.expm1(-x)


def eta_partition_mixing(beta_0: float, x: float) -> float:
    """Effective closure eta_bulk = beta_0 q(1-q)."""
    _require_nonnegative("beta_0", beta_0)
    q = q_flat_gaussian_2d(x)
    one_minus_q = math.exp(-x)
    return beta_0 * q * one_minus_q


def d_eta_dx(beta_0: float, x: float) -> float:
    """Exact derivative d eta_bulk/dx."""
    _require_nonnegative("beta_0", beta_0)
    _require_nonnegative("x", x)
    exp_minus_x = math.exp(-x)
    return beta_0 * exp_minus_x * (2.0 * exp_minus_x - 1.0)


def exact_peak(beta_0: float) -> tuple[float, float, float]:
    """Return (x_peak, q_peak, eta_peak)."""
    _require_nonnegative("beta_0", beta_0)
    return math.log(2.0), 0.5, beta_0 / 4.0


def _simpson_integral_radial_gaussian(gamma: float, radius: float, intervals: int) -> float:
    """Numerically integrate 2*pi*r*exp(-gamma*r^2) from 0 to radius."""
    _require_positive("gamma", gamma)
    _require_nonnegative("radius", radius)
    if intervals < 2 or intervals % 2:
        raise ValueError("intervals must be an even integer >= 2")
    if radius == 0.0:
        return 0.0

    h = radius / intervals

    def integrand(r: float) -> float:
        return 2.0 * math.pi * r * math.exp(-gamma * r * r)

    total = integrand(0.0) + integrand(radius)
    for i in range(1, intervals):
        total += (4.0 if i % 2 else 2.0) * integrand(i * h)
    return total * h / 3.0


def numerical_q_flat_gaussian_2d(gamma: float, radius: float, intervals: int = 20_000) -> float:
    """Independent quadrature check of the cumulative overlap fraction."""
    numerator = _simpson_integral_radial_gaussian(gamma, radius, intervals)
    denominator = math.pi / gamma
    return numerator / denominator


def evaluate_bridge_point(
    *,
    alpha: float,
    sigma_B: float,
    kappa_6: float,
    lambda_chi: float,
    beta_0: float,
) -> BridgePoint:
    """Evaluate the candidate bridge and its exact local sensitivities."""
    gamma = gamma_from_profiles(alpha, sigma_B)
    radius = radius_from_tension(kappa_6, lambda_chi)
    x = x_from_parameters(gamma, kappa_6, lambda_chi)
    q = q_flat_gaussian_2d(x)
    eta = eta_partition_mixing(beta_0, x)
    eta_x = d_eta_dx(beta_0, x)

    dx_d_lambda = -2.0 * x / lambda_chi
    dx_d_kappa = -4.0 * x / kappa_6
    dx_d_gamma = x / gamma

    d_eta_d_lambda = eta_x * dx_d_lambda
    d_eta_d_kappa = eta_x * dx_d_kappa
    d_eta_d_gamma = eta_x * dx_d_gamma

    if eta == 0.0:
        log_lambda = math.nan
        log_kappa = math.nan
        log_gamma = math.nan
    else:
        log_lambda = lambda_chi * d_eta_d_lambda / eta
        log_kappa = kappa_6 * d_eta_d_kappa / eta
        log_gamma = gamma * d_eta_d_gamma / eta

    return BridgePoint(
        alpha=alpha,
        sigma_B=sigma_B,
        kappa_6=kappa_6,
        lambda_chi=lambda_chi,
        beta_0=beta_0,
        gamma=gamma,
        R_chi=radius,
        x=x,
        q=q,
        eta_bulk=eta,
        d_eta_dx=eta_x,
        d_eta_d_lambda_chi=d_eta_d_lambda,
        d_eta_d_kappa_6=d_eta_d_kappa,
        d_eta_d_gamma=d_eta_d_gamma,
        log_sensitivity_lambda_chi=log_lambda,
        log_sensitivity_kappa_6=log_kappa,
        log_sensitivity_gamma=log_gamma,
    )


def x_only_jacobian_columns(
    observable_shape: Sequence[float],
    dx_dp: Iterable[float],
    eta_x: float,
) -> list[list[float]]:
    """Return Jacobian columns for controls entering only through x.

    Every returned column is a scalar multiple of ``observable_shape``;
    therefore the block rank is <= 1. At eta_x == 0 all columns vanish.
    """
    shape = [float(value) for value in observable_shape]
    if not shape:
        raise ValueError("observable_shape must not be empty")
    if not all(math.isfinite(value) for value in shape):
        raise ValueError("observable_shape must contain only finite values")
    if not math.isfinite(eta_x):
        raise ValueError("eta_x must be finite")

    columns: list[list[float]] = []
    for derivative in dx_dp:
        if not math.isfinite(derivative):
            raise ValueError("dx_dp must contain only finite values")
        scale = eta_x * derivative
        columns.append([scale * component for component in shape])
    return columns


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--alpha", type=float, default=0.15)
    parser.add_argument("--sigma-B", dest="sigma_B", type=float, default=1.2)
    parser.add_argument("--kappa-6", dest="kappa_6", type=float, default=1.0)
    parser.add_argument("--lambda-chi", dest="lambda_chi", type=float, default=4.25)
    parser.add_argument("--beta-0", dest="beta_0", type=float, default=0.1)
    parser.add_argument("--quadrature-intervals", type=int, default=20_000)
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    point = evaluate_bridge_point(
        alpha=args.alpha,
        sigma_B=args.sigma_B,
        kappa_6=args.kappa_6,
        lambda_chi=args.lambda_chi,
        beta_0=args.beta_0,
    )
    q_numeric = numerical_q_flat_gaussian_2d(
        point.gamma,
        point.R_chi,
        intervals=args.quadrature_intervals,
    )
    payload = asdict(point)
    payload.update(
        {
            "q_numerical_quadrature": q_numeric,
            "q_quadrature_absolute_error": abs(q_numeric - point.q),
            "status": "CONDITIONAL_FLAT_2D_GAUSSIAN_OVERLAP",
            "evidence_effect": "NONE",
            "K1-D": "NOT_RELEASED",
            "K1-E": "NOT_ADMISSIBLE",
        }
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
