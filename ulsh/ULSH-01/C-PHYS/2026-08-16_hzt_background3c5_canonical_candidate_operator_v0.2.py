#!/usr/bin/env python3
"""Canonical-variable Background3C5 candidate operator v0.2.

This module replaces the quarantined B/C/Q/At-prime representation for ongoing
ULSH-01 development.  It uses the frozen M1 variables

    x = M6 r,
    ell = M6 L,
    varphi = phi/M6^2,
    a_chi = A_chi/M6,

and reproduces the exact frozen bulk-control equations and pole coefficients.

IMPORTANT GOVERNANCE
--------------------
The finite-thickness layer amplitude normalization is not yet independently
provenance-bound.  Therefore the layer extension below is an explicit candidate
parameterization in hatted variables, not an authorized physical operator.
No nonlinear solve, physical background, response-rank, K1-D or K1-E claim is
allowed from this file.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import numpy as np

Array = np.ndarray

PHYSICAL_EXECUTION_AUTHORIZED = False
PHYSICAL_EVIDENCE_EFFECT = "NONE_IMPLEMENTATION_ONLY"
RANK_R_CLAIM_ALLOWED = False
PARENT_EQUIVALENCE_STATUS = "BULK_EXACT__FINITE_THICKNESS_NORMALIZATION_PENDING"


@dataclass(frozen=True)
class BulkModel:
    Lambda_hat: float
    mhat_phi_sq: float
    a_F: float
    k4: float

    def validate(self) -> None:
        values = (self.Lambda_hat, self.mhat_phi_sq, self.a_F, self.k4)
        if not all(np.isfinite(v) for v in values):
            raise ValueError("bulk parameters must be finite")
        if self.mhat_phi_sq <= 0.0:
            raise ValueError("mhat_phi_sq must be strictly positive")
        if self.a_F < 0.0:
            raise ValueError("a_F must be nonnegative (a_F=0 only as declared control)")


@dataclass(frozen=True)
class ChargeSector:
    n: int
    m_layer: int
    q_hat: float

    def validate(self) -> None:
        if int(self.n) != self.n:
            raise ValueError("n must be integer")
        if int(self.m_layer) != self.m_layer or self.m_layer <= 0:
            raise ValueError("m_layer must be a positive integer")
        if not np.isfinite(self.q_hat) or self.q_hat <= 0.0:
            raise ValueError("q_hat must be positive")

    @property
    def ghat_sigma(self) -> float:
        """Dimensionless product gSigma*M6 = m_layer*q_hat."""
        return float(self.m_layer) * float(self.q_hat)


@dataclass(frozen=True)
class LayerCandidate:
    """Explicit candidate hatted layer convention.

    This class is intentionally segregated from BulkModel because the exact
    dimensionless amplitude normalization is still a G2/G5 provenance gate.
    The functions return dimensionless coefficients in that candidate convention.
    """

    mhat_sigma_sq: Callable[[Array], Array]
    lambdahat_sigma: float
    Vhat_offset: Callable[[Array], Array] = lambda varphi: np.zeros_like(np.asarray(varphi, dtype=float))

    def Vhat(self, varphi: Array, s: Array) -> Array:
        v = np.asarray(varphi, dtype=float)
        q = np.asarray(s, dtype=float)
        return (
            np.asarray(self.Vhat_offset(v), dtype=float)
            + 0.5 * np.asarray(self.mhat_sigma_sq(v), dtype=float) * q**2
            + 0.25 * self.lambdahat_sigma * q**4
        )

    def dVhat_ds(self, varphi: Array, s: Array) -> Array:
        v = np.asarray(varphi, dtype=float)
        q = np.asarray(s, dtype=float)
        return np.asarray(self.mhat_sigma_sq(v), dtype=float) * q + self.lambdahat_sigma * q**3


@dataclass(frozen=True)
class Profile:
    x: Array
    A: Array
    ell: Array
    varphi: Array
    s: Array
    a_chi: Array


@dataclass(frozen=True)
class BulkResiduals:
    E_A: Array
    E_ell: Array
    E_varphi: Array
    E_gauge: Array
    rr_constraint: Array

    def residual_inf(self) -> dict[str, float]:
        return {
            name: float(np.max(np.abs(np.asarray(getattr(self, name)))))
            for name in ("E_A", "E_ell", "E_varphi", "E_gauge", "rr_constraint")
        }


@dataclass(frozen=True)
class LayerLocalResiduals:
    E_s: Array
    winding: Array


def _one_dim(name: str, value: Array, n: int | None = None) -> Array:
    arr = np.asarray(value, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    if n is not None and arr.size != n:
        raise ValueError(f"{name} has wrong size")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains non-finite values")
    return arr


def validate_profile(profile: Profile) -> Profile:
    x = _one_dim("x", profile.x)
    if x.size < 5 or np.any(np.diff(x) <= 0.0):
        raise ValueError("x requires at least five strictly increasing nodes")
    if np.any(x <= 0.0):
        raise ValueError("residual evaluation excludes x=0; use center_series() there")
    n = x.size
    values = {
        name: _one_dim(name, getattr(profile, name), n)
        for name in ("A", "ell", "varphi", "s", "a_chi")
    }
    if np.any(values["ell"] <= 0.0):
        raise ValueError("ell must remain positive away from the regular axis")
    return Profile(x=x, **values)


def derivative(y: Array, x: Array) -> Array:
    return np.gradient(np.asarray(y, dtype=float), np.asarray(x, dtype=float), edge_order=2)


def bulk_flux_density(A: Array, varphi: Array, q_s: float, a_F: float) -> Array:
    return 0.5 * q_s**2 * np.exp(-8.0 * np.asarray(A) + 2.0 * a_F * np.asarray(varphi))


def evaluate_bulk_control(profile: Profile, model: BulkModel, q_s: float) -> BulkResiduals:
    """Exact frozen M1 bulk-control operator.

    These expressions are copied algebraically from the canonical M1 Function
    Freeze Contract.  They are the mandatory s->0 regression target.
    """
    model.validate()
    p = validate_profile(profile)
    if not np.isfinite(q_s):
        raise ValueError("q_s must be finite")

    Ax = derivative(p.A, p.x)
    Axx = derivative(Ax, p.x)
    ellx = derivative(p.ell, p.x)
    ellxx = derivative(ellx, p.x)
    fx = derivative(p.varphi, p.x)
    fxx = derivative(fx, p.x)
    achix = derivative(p.a_chi, p.x)

    rhoF = bulk_flux_density(p.A, p.varphi, q_s, model.a_F)
    e2A = np.exp(-2.0 * p.A)

    E_A = (
        4.0 * Axx + 10.0 * Ax**2 - 6.0 * model.k4 * e2A
        + model.Lambda_hat + 0.5 * fx**2
        + 0.5 * model.mhat_phi_sq * p.varphi**2 - rhoF
    )
    E_ell = (
        ellxx + 3.0 * Axx * p.ell + 6.0 * Ax**2 * p.ell
        + 3.0 * Ax * ellx - 3.0 * model.k4 * e2A * p.ell
        + model.Lambda_hat * p.ell
        + p.ell * (0.5 * fx**2 + 0.5 * model.mhat_phi_sq * p.varphi**2 + rhoF)
    )
    E_varphi = (
        p.ell * fxx + (4.0 * Ax * p.ell + ellx) * fx
        - p.ell * model.mhat_phi_sq * p.varphi
        + 2.0 * model.a_F * p.ell * rhoF
    )
    E_gauge = achix - q_s * p.ell * np.exp(-4.0 * p.A + 2.0 * model.a_F * p.varphi)
    rr_constraint = (
        p.ell * (-6.0 * model.k4 * e2A + 6.0 * Ax**2 + model.Lambda_hat)
        + 4.0 * Ax * ellx
        - p.ell * (0.5 * fx**2 - 0.5 * model.mhat_phi_sq * p.varphi**2 + rhoF)
    )
    return BulkResiduals(E_A, E_ell, E_varphi, E_gauge, rr_constraint)


def evaluate_layer_local(profile: Profile, sector: ChargeSector, layer: LayerCandidate) -> LayerLocalResiduals:
    """Candidate local layer-amplitude equation in canonical geometry.

    This implements only the already-derived Frobenius-compatible local equation

      s'' + (4 A' + ell'/ell) s' - (w^2/ell^2) s - dVhat/ds = 0

    in the declared candidate hatted convention.  Backreaction on Einstein,
    scalar and Maxwell equations is deliberately NOT silently added until the
    final dimensionless layer normalization is provenance-bound.
    """
    sector.validate()
    p = validate_profile(profile)
    Ax = derivative(p.A, p.x)
    ellx = derivative(p.ell, p.x)
    sx = derivative(p.s, p.x)
    sxx = derivative(sx, p.x)
    winding = sector.n - sector.ghat_sigma * p.a_chi
    E_s = (
        sxx + (4.0 * Ax + ellx / p.ell) * sx
        - (winding**2 / p.ell**2) * p.s
        - layer.dVhat_ds(p.varphi, p.s)
    )
    return LayerLocalResiduals(E_s=E_s, winding=winding)


def bulk_pole_coefficients(*, f0: float, q_s: float, model: BulkModel) -> dict[str, float]:
    """Exact frozen regular-axis coefficients in the north frame A(0)=0."""
    model.validate()
    if not np.isfinite(f0) or not np.isfinite(q_s):
        raise ValueError("f0 and q_s must be finite")
    rhoF0 = 0.5 * q_s**2 * np.exp(2.0 * model.a_F * f0)
    a2 = (
        6.0 * model.k4 - model.Lambda_hat
        - 0.5 * model.mhat_phi_sq * f0**2 + rhoF0
    ) / 8.0
    f2 = (model.mhat_phi_sq * f0 - 2.0 * model.a_F * rhoF0) / 4.0
    g2 = 0.5 * q_s * np.exp(2.0 * model.a_F * f0)
    l3 = (
        3.0 * model.k4 - 12.0 * a2 - model.Lambda_hat
        - 0.5 * model.mhat_phi_sq * f0**2 - rhoF0
    ) / 6.0
    return {"rho_F0": rhoF0, "a2": a2, "f2": f2, "g2": g2, "l3": l3}


def center_series(
    x: Array,
    *,
    f0: float,
    q_s: float,
    model: BulkModel,
    sector: ChargeSector | None = None,
    s_amplitude: float = 0.0,
) -> Profile:
    """Regular north-axis initializer through the frozen leading orders.

    For a nonzero winding sector, s ~ s_amplitude*x**abs(n).  This routine does
    not invent the next finite-thickness coefficient alpha_s while its exact
    hatted normalization remains open.
    """
    xx = _one_dim("x", x)
    if np.any(xx < 0.0):
        raise ValueError("x must be nonnegative")
    coeff = bulk_pole_coefficients(f0=f0, q_s=q_s, model=model)
    A = coeff["a2"] * xx**2
    ell = xx + coeff["l3"] * xx**3
    varphi = f0 + coeff["f2"] * xx**2
    a_chi = coeff["g2"] * xx**2
    if sector is None:
        s = np.zeros_like(xx)
    else:
        sector.validate()
        power = abs(sector.n)
        if power == 0:
            s = np.full_like(xx, float(s_amplitude))
        else:
            s = float(s_amplitude) * xx**power
    return Profile(x=xx, A=A, ell=ell, varphi=varphi, s=s, a_chi=a_chi)


def center_free_data_count(*, n: int, k4_fixed: bool = True) -> dict[str, object]:
    """Return the G2 local regular-data budget after frozen gauge fixing."""
    data = ["f0", "g2", "s_abs_n" if n != 0 else "s0"]
    if not k4_fixed:
        data.append("k4")
    return {
        "free_data": tuple(data),
        "count": len(data),
        "A0_fixed": 0.0,
        "ell_x0_fixed": 1.0,
        "conical_rescue_parameter": False,
    }


if __name__ == "__main__":
    raise SystemExit(
        "candidate residual library only; physical Background3C5 execution is not authorized"
    )
