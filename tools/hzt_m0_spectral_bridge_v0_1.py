#!/usr/bin/env python3
"""Reference utilities for the conditional HZT-M0 MDS-01 spectral bridge.

The module provides a dependency-free flat-disk benchmark for

    m_n = xi_n / R_chi

and a diagnostic comparison with the locked MD-2Q effective values. It does
not identify the physical HZT-M0 fluctuation operator and does not release
K1-D or K1-E.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from typing import Callable


@dataclass(frozen=True)
class SpectralDiagnostic:
    kappa_6: float
    lambda_chi: float
    radius_chi: float
    m_eff: float
    xi_eff: float
    xi_dirichlet_axisymmetric: float
    xi_neumann_first_massive_axisymmetric: float
    m_dirichlet_axisymmetric: float
    m_neumann_first_massive_axisymmetric: float
    radius_required_for_dirichlet_match: float
    radius_required_for_neumann_match: float
    dirichlet_mass_ratio_to_m_eff: float
    neumann_mass_ratio_to_m_eff: float


def _positive(name: str, value: float) -> float:
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive, got {value!r}")
    return value


def bessel_j0(x: float, *, tolerance: float = 1.0e-16, max_terms: int = 256) -> float:
    """Evaluate J_0(x) by its entire power series."""
    if not math.isfinite(x):
        raise ValueError("x must be finite")
    _positive("tolerance", tolerance)
    if max_terms < 2:
        raise ValueError("max_terms must be >= 2")

    y = x * x / 4.0
    term = 1.0
    total = term
    for k in range(1, max_terms + 1):
        term *= -y / (k * k)
        total_next = total + term
        if abs(term) <= tolerance * max(1.0, abs(total_next)):
            return total_next
        total = total_next
    raise RuntimeError("J0 series did not converge within max_terms")


def bessel_j1(x: float, *, tolerance: float = 1.0e-16, max_terms: int = 256) -> float:
    """Evaluate J_1(x) by its entire power series."""
    if not math.isfinite(x):
        raise ValueError("x must be finite")
    _positive("tolerance", tolerance)
    if max_terms < 2:
        raise ValueError("max_terms must be >= 2")

    y = x * x / 4.0
    term = x / 2.0
    total = term
    for k in range(1, max_terms + 1):
        term *= -y / (k * (k + 1))
        total_next = total + term
        if abs(term) <= tolerance * max(1.0, abs(total_next)):
            return total_next
        total = total_next
    raise RuntimeError("J1 series did not converge within max_terms")


def bisect_root(
    function: Callable[[float], float],
    lower: float,
    upper: float,
    *,
    tolerance: float = 1.0e-14,
    max_iterations: int = 256,
) -> float:
    """Find a bracketed scalar root by deterministic bisection."""
    if not math.isfinite(lower) or not math.isfinite(upper) or lower >= upper:
        raise ValueError("lower and upper must be finite with lower < upper")
    _positive("tolerance", tolerance)
    if max_iterations < 1:
        raise ValueError("max_iterations must be >= 1")

    f_lower = function(lower)
    f_upper = function(upper)
    if not math.isfinite(f_lower) or not math.isfinite(f_upper):
        raise ValueError("function values at the bracket must be finite")
    if f_lower == 0.0:
        return lower
    if f_upper == 0.0:
        return upper
    if f_lower * f_upper > 0.0:
        raise ValueError("root is not bracketed")

    for _ in range(max_iterations):
        midpoint = 0.5 * (lower + upper)
        f_mid = function(midpoint)
        if not math.isfinite(f_mid):
            raise ValueError("function returned a non-finite midpoint value")
        if abs(f_mid) <= tolerance or 0.5 * (upper - lower) <= tolerance:
            return midpoint
        if f_lower * f_mid <= 0.0:
            upper = midpoint
            f_upper = f_mid
        else:
            lower = midpoint
            f_lower = f_mid
    raise RuntimeError("bisection did not converge within max_iterations")


def xi_dirichlet_axisymmetric() -> float:
    """First positive zero of J0: flat-disk l=0 Dirichlet coefficient."""
    return bisect_root(bessel_j0, 2.0, 3.0)


def xi_neumann_first_massive_axisymmetric() -> float:
    """First positive zero of J1: flat-disk l=0 first massive Neumann coefficient."""
    return bisect_root(bessel_j1, 3.0, 4.0)


def radius_from_tension(kappa_6: float, lambda_chi: float) -> float:
    """Inherited candidate R_chi = 4/(kappa_6^2 lambda_chi)."""
    _positive("kappa_6", kappa_6)
    _positive("lambda_chi", lambda_chi)
    return 4.0 / (kappa_6 * kappa_6 * lambda_chi)


def mass_from_radius(xi: float, radius_chi: float) -> float:
    """Return m = xi/R_chi for a declared dimensionless spectral coefficient."""
    _positive("xi", xi)
    _positive("radius_chi", radius_chi)
    return xi / radius_chi


def radius_required_for_mass(xi: float, mass: float) -> float:
    """Return R_chi = xi/m for a declared spectral coefficient."""
    _positive("xi", xi)
    _positive("mass", mass)
    return xi / mass


def evaluate_md2q_spectral_diagnostic(
    *,
    kappa_6: float = 1.0,
    lambda_chi: float = 4.25,
    m_eff: float = 0.055,
) -> SpectralDiagnostic:
    """Compare the locked MD-2Q point with standard flat-disk scalar roots."""
    radius = radius_from_tension(kappa_6, lambda_chi)
    _positive("m_eff", m_eff)
    xi_eff = m_eff * radius
    xi_d = xi_dirichlet_axisymmetric()
    xi_n = xi_neumann_first_massive_axisymmetric()
    m_d = mass_from_radius(xi_d, radius)
    m_n = mass_from_radius(xi_n, radius)
    return SpectralDiagnostic(
        kappa_6=kappa_6,
        lambda_chi=lambda_chi,
        radius_chi=radius,
        m_eff=m_eff,
        xi_eff=xi_eff,
        xi_dirichlet_axisymmetric=xi_d,
        xi_neumann_first_massive_axisymmetric=xi_n,
        m_dirichlet_axisymmetric=m_d,
        m_neumann_first_massive_axisymmetric=m_n,
        radius_required_for_dirichlet_match=radius_required_for_mass(xi_d, m_eff),
        radius_required_for_neumann_match=radius_required_for_mass(xi_n, m_eff),
        dirichlet_mass_ratio_to_m_eff=m_d / m_eff,
        neumann_mass_ratio_to_m_eff=m_n / m_eff,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kappa-6", dest="kappa_6", type=float, default=1.0)
    parser.add_argument("--lambda-chi", dest="lambda_chi", type=float, default=4.25)
    parser.add_argument("--m-eff", dest="m_eff", type=float, default=0.055)
    return parser


def main() -> int:
    args = _parser().parse_args()
    diagnostic = evaluate_md2q_spectral_diagnostic(
        kappa_6=args.kappa_6,
        lambda_chi=args.lambda_chi,
        m_eff=args.m_eff,
    )
    payload = asdict(diagnostic)
    payload.update(
        {
            "status": "CONDITIONAL_FLAT_DISK_SPECTRAL_BENCHMARK",
            "physical_operator_identified": False,
            "K1-D": "NOT_RELEASED",
            "K1-E": "NOT_ADMISSIBLE",
            "evidence_effect": "NONE",
        }
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
