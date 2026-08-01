#!/usr/bin/env python3
"""Controlled MDS-05 warp-volume and 6D→4D Planck normalization utilities.

Scientific scope
----------------
For the HZT-M0-S6 metric

    ds6^2 = exp(2 A(y)) g4_mn(x) dx^m dx^n + g2_ab(y) dy^a dy^b,

the coefficient of the four-dimensional Ricci scalar inherited from the
six-dimensional Einstein-Hilbert term is

    M4_bulk^2 = M6^4 * V_W = V_W / kappa6^2,

with

    V_W = integral d^2y sqrt(g2) exp(2 A).

For the axial chart ds2_int = dr^2 + L(r)^2 dchi^2,

    V_W = Delta_chi * integral dr L(r) exp(2 A(r)).

Optional localized Einstein-Hilbert terms can be added explicitly. No
localized term is part of the canonical SCI-001/SCI-002 v0.1 parent core.
This module therefore defaults them to zero and never infers them from a
benchmark.

The routines are diagnostic/derivational. They do not release K1-D or K1-E
and do not establish full graviton ghost freedom.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence


class WarpVolumeError(ValueError):
    """Raised when a profile or normalization contract is invalid."""


@dataclass(frozen=True)
class WarpRegion:
    """One connected axial internal region.

    r and L carry length units; A is dimensionless. The angular coordinate
    has period chi_period and is dimensionless.
    """

    r: Sequence[float]
    A: Sequence[float]
    L: Sequence[float]
    chi_period: float = 2.0 * math.pi
    label: str = "region"


@dataclass(frozen=True)
class CapEinsteinTerm5D:
    """Localized five-dimensional Einstein-Hilbert term on an axial cap.

    Action convention:
        (M5^3 / 2) integral d^5x sqrt(-h) R5

    Its four-dimensional contribution is
        Delta_chi * M5^3 * L_sigma * exp(2 A_sigma).
    """

    M5_cubed: float
    L_sigma: float
    A_sigma: float
    chi_period: float = 2.0 * math.pi
    label: str = "cap5d"


@dataclass(frozen=True)
class BraneEinsteinTerm4D:
    """Localized four-dimensional Einstein-Hilbert term.

    Action convention:
        (M4_loc^2 / 2) integral d^4x sqrt(-gamma) R[gamma],
        gamma_mn = exp(2 A_sigma) g4_mn.

    In the g4 frame its contribution is M4_loc^2 exp(2 A_sigma).
    """

    M4_local_squared: float
    A_sigma: float
    label: str = "brane4d"


def _finite_sequence(values: Sequence[float], name: str) -> list[float]:
    out = [float(v) for v in values]
    if not out:
        raise WarpVolumeError(f"{name} must not be empty")
    if not all(math.isfinite(v) for v in out):
        raise WarpVolumeError(f"{name} contains non-finite values")
    return out


def validate_region(region: WarpRegion) -> tuple[list[float], list[float], list[float]]:
    r = _finite_sequence(region.r, f"{region.label}.r")
    A = _finite_sequence(region.A, f"{region.label}.A")
    L = _finite_sequence(region.L, f"{region.label}.L")

    if not (len(r) == len(A) == len(L)):
        raise WarpVolumeError(f"{region.label}: r, A and L must have equal length")
    if len(r) < 2:
        raise WarpVolumeError(f"{region.label}: at least two profile points are required")
    if not math.isfinite(region.chi_period) or region.chi_period <= 0.0:
        raise WarpVolumeError(f"{region.label}: chi_period must be positive and finite")
    if any(r[i + 1] <= r[i] for i in range(len(r) - 1)):
        raise WarpVolumeError(f"{region.label}: r must be strictly increasing")
    if any(l < 0.0 for l in L):
        raise WarpVolumeError(f"{region.label}: L must be non-negative")

    return r, A, L


def warped_volume_axisymmetric(region: WarpRegion) -> float:
    """Return Delta_chi * integral dr L exp(2A) using trapezoidal quadrature."""

    r, A, L = validate_region(region)
    integrand = []
    for a, l in zip(A, L):
        try:
            value = l * math.exp(2.0 * a)
        except OverflowError as exc:
            raise WarpVolumeError(f"{region.label}: exp(2A) overflow") from exc
        if not math.isfinite(value):
            raise WarpVolumeError(f"{region.label}: non-finite warp-volume integrand")
        integrand.append(value)

    radial = math.fsum(
        0.5 * (integrand[i] + integrand[i + 1]) * (r[i + 1] - r[i])
        for i in range(len(r) - 1)
    )
    volume = region.chi_period * radial
    if not math.isfinite(volume) or volume < 0.0:
        raise WarpVolumeError(f"{region.label}: invalid warped volume")
    return volume


def total_warped_volume(regions: Iterable[WarpRegion]) -> float:
    values = [warped_volume_axisymmetric(region) for region in regions]
    if not values:
        raise WarpVolumeError("at least one internal region is required")
    return math.fsum(values)


def cap5d_planck_contribution(term: CapEinsteinTerm5D) -> float:
    if term.M5_cubed < 0.0 or not math.isfinite(term.M5_cubed):
        raise WarpVolumeError(f"{term.label}: M5_cubed must be finite and non-negative")
    if term.L_sigma < 0.0 or not math.isfinite(term.L_sigma):
        raise WarpVolumeError(f"{term.label}: L_sigma must be finite and non-negative")
    if term.chi_period <= 0.0 or not math.isfinite(term.chi_period):
        raise WarpVolumeError(f"{term.label}: chi_period must be positive and finite")
    if not math.isfinite(term.A_sigma):
        raise WarpVolumeError(f"{term.label}: A_sigma must be finite")
    try:
        result = (
            term.chi_period
            * term.M5_cubed
            * term.L_sigma
            * math.exp(2.0 * term.A_sigma)
        )
    except OverflowError as exc:
        raise WarpVolumeError(f"{term.label}: exp(2A_sigma) overflow") from exc
    if not math.isfinite(result):
        raise WarpVolumeError(f"{term.label}: non-finite contribution")
    return result


def brane4d_planck_contribution(term: BraneEinsteinTerm4D) -> float:
    if term.M4_local_squared < 0.0 or not math.isfinite(term.M4_local_squared):
        raise WarpVolumeError(
            f"{term.label}: M4_local_squared must be finite and non-negative"
        )
    if not math.isfinite(term.A_sigma):
        raise WarpVolumeError(f"{term.label}: A_sigma must be finite")
    try:
        result = term.M4_local_squared * math.exp(2.0 * term.A_sigma)
    except OverflowError as exc:
        raise WarpVolumeError(f"{term.label}: exp(2A_sigma) overflow") from exc
    if not math.isfinite(result):
        raise WarpVolumeError(f"{term.label}: non-finite contribution")
    return result


def effective_planck_mass_squared(
    *,
    kappa6_squared: float,
    warped_volume: float,
    cap_terms_5d: Iterable[CapEinsteinTerm5D] = (),
    brane_terms_4d: Iterable[BraneEinsteinTerm4D] = (),
) -> dict[str, float]:
    """Compute the g4-frame coefficient M4^2 = 1/kappa4^2.

    Dimensions in natural units:
      [kappa6^2] = L^4,
      [V_W] = L^2,
      [M4^2] = L^-2.
    """

    if kappa6_squared <= 0.0 or not math.isfinite(kappa6_squared):
        raise WarpVolumeError("kappa6_squared must be positive and finite")
    if warped_volume < 0.0 or not math.isfinite(warped_volume):
        raise WarpVolumeError("warped_volume must be finite and non-negative")

    bulk = warped_volume / kappa6_squared
    cap = math.fsum(cap5d_planck_contribution(term) for term in cap_terms_5d)
    brane = math.fsum(brane4d_planck_contribution(term) for term in brane_terms_4d)
    total = bulk + cap + brane

    if not math.isfinite(total) or total <= 0.0:
        raise WarpVolumeError(
            "effective M4^2 must be positive; the 4D Einstein-Hilbert coefficient is invalid"
        )

    return {
        "bulk_M4_squared": bulk,
        "cap5d_M4_squared": cap,
        "brane4d_M4_squared": brane,
        "total_M4_squared": total,
        "kappa4_squared": 1.0 / total,
        "G4": 1.0 / (8.0 * math.pi * total),
    }


def dimensionless_warped_volume(*, K4: float, warped_volume: float) -> float:
    """Return Vhat_W = K4 V_W, valid for K4>0."""

    if K4 <= 0.0 or not math.isfinite(K4):
        raise WarpVolumeError("K4 must be positive and finite")
    if warped_volume < 0.0 or not math.isfinite(warped_volume):
        raise WarpVolumeError("warped_volume must be finite and non-negative")
    return K4 * warped_volume


def benchmark_volume_candidates(
    *,
    reported_value: float,
    K4: float,
    chi_period: float = 2.0 * math.pi,
) -> dict[str, float]:
    """Return non-exclusive interpretations of a legacy dimensionless value.

    This function deliberately does not choose an interpretation:
    - full_dimensionless: reported = K4 * V_W(full angular integral)
    - per_radian_dimensionless: reported = K4 * integral dr L exp(2A)
    """

    if reported_value < 0.0 or not math.isfinite(reported_value):
        raise WarpVolumeError("reported_value must be finite and non-negative")
    if K4 <= 0.0 or not math.isfinite(K4):
        raise WarpVolumeError("K4 must be positive and finite")
    if chi_period <= 0.0 or not math.isfinite(chi_period):
        raise WarpVolumeError("chi_period must be positive and finite")

    return {
        "if_full_dimensionless_then_V_W": reported_value / K4,
        "if_per_radian_dimensionless_then_V_W": chi_period * reported_value / K4,
    }
