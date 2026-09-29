#!/usr/bin/env python3
"""Background3C5 full finite-thickness operator candidate v0.3.

G5 implementation-only library. It extends the canonical bulk residuals with
parent-derived finite-thickness stress/scalar/amplitude terms and a conservative
Maxwell flux equation.

The Maxwell source normalization is provenance-closed in the canonical C-PHYS
M1 gauge convention:

    Gamma_Sigma = M6*gSigma = m_layer*q_hat.

This closure is an operator-identity result only. It does NOT authorize a
physical nonlinear BVP, establish a physical background, establish response
rank R, or change K1-D/K1-E/evidence status.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
import numpy as np

Array = np.ndarray
PHYSICAL_EXECUTION_AUTHORIZED = False
PHYSICAL_EVIDENCE_EFFECT = "NONE_IMPLEMENTATION_ONLY"
RANK_R_CLAIM_ALLOWED = False
G5_STATUS = "MAXWELL_COEFFICIENT_CLOSED__PARENT_EQUIVALENCE_PENDING"
GAMMA_SIGMA_STATUS = "PROVENANCE_CLOSED_CANONICAL_M1"


@dataclass(frozen=True)
class Model:
    Lambda_hat: float
    mhat_phi_sq: float
    a_F: float
    k4: float


@dataclass(frozen=True)
class Sector:
    n: int
    m_layer: int
    q_hat: float

    def validate(self) -> None:
        if int(self.n) != self.n:
            raise ValueError("n must be integer")
        if int(self.m_layer) != self.m_layer or self.m_layer <= 0:
            raise ValueError("m_layer must be a positive integer")
        if not np.isfinite(self.q_hat) or self.q_hat <= 0.0:
            raise ValueError("q_hat must be finite and positive")

    @property
    def ghat_sigma(self) -> float:
        """Canonical dimensionless charge: M6*gSigma = m_layer*q_hat."""
        return float(self.m_layer) * float(self.q_hat)

    @property
    def Gamma_Sigma(self) -> float:
        """Exact Maxwell-current coefficient in the frozen M1 convention."""
        return self.ghat_sigma


@dataclass(frozen=True)
class Layer:
    mhat_sigma_sq: Callable[[Array], Array]
    dmhat_sigma_sq_dvarphi: Callable[[Array], Array]
    lambdahat_sigma: float
    Lambda_hat_layer: Callable[[Array], Array] = lambda v: np.zeros_like(np.asarray(v, float))
    dLambda_hat_layer_dvarphi: Callable[[Array], Array] = lambda v: np.zeros_like(np.asarray(v, float))

    def V(self, v: Array, s: Array) -> Array:
        return (
            np.asarray(self.Lambda_hat_layer(v), float)
            + 0.5 * np.asarray(self.mhat_sigma_sq(v), float) * s**2
            + 0.25 * self.lambdahat_sigma * s**4
        )

    def dV_ds(self, v: Array, s: Array) -> Array:
        return np.asarray(self.mhat_sigma_sq(v), float) * s + self.lambdahat_sigma * s**3

    def dV_dvarphi(self, v: Array, s: Array) -> Array:
        return (
            np.asarray(self.dLambda_hat_layer_dvarphi(v), float)
            + 0.5 * np.asarray(self.dmhat_sigma_sq_dvarphi(v), float) * s**2
        )


@dataclass(frozen=True)
class Profile:
    x: Array
    A: Array
    ell: Array
    varphi: Array
    s: Array
    a_chi: Array


@dataclass(frozen=True)
class Residuals:
    E_A: Array
    E_ell: Array
    E_varphi: Array
    E_s: Array
    E_flux: Array
    rr_constraint: Array


def d(y: Array, x: Array) -> Array:
    return np.gradient(np.asarray(y, float), np.asarray(x, float), edge_order=2)


def validate(p: Profile) -> None:
    arrays = [np.asarray(getattr(p, k), float) for k in ("x", "A", "ell", "varphi", "s", "a_chi")]
    n = len(arrays[0])
    if n < 5 or any(a.ndim != 1 or len(a) != n or not np.all(np.isfinite(a)) for a in arrays):
        raise ValueError("invalid profile arrays")
    if np.any(np.diff(arrays[0]) <= 0) or np.any(arrays[0] <= 0):
        raise ValueError("x must be positive/increasing; center uses series")
    if np.any(arrays[2] <= 0):
        raise ValueError("ell must be positive away from axis")


def evaluate(p: Profile, model: Model, sector: Sector, layer: Layer) -> Residuals:
    """Evaluate the coefficient-closed G5 local candidate residuals.

    The Maxwell coefficient is not a caller-supplied fit/control parameter.
    It is fixed by the canonical charge lattice as

        Gamma_Sigma = sector.m_layer * sector.q_hat.

    Closure of this local operator coefficient does not authorize physical
    execution; global BVP, constraint-propagation and parent-equivalence gates
    remain separate.
    """
    validate(p)
    sector.validate()
    x = np.asarray(p.x, float)
    A = np.asarray(p.A, float)
    ell = np.asarray(p.ell, float)
    v = np.asarray(p.varphi, float)
    s = np.asarray(p.s, float)
    ach = np.asarray(p.a_chi, float)

    Ax = d(A, x)
    Axx = d(Ax, x)
    ex = d(ell, x)
    exx = d(ex, x)
    vx = d(v, x)
    vxx = d(vx, x)
    sx = d(s, x)
    sxx = d(sx, x)
    achx = d(ach, x)

    Z = np.exp(-2 * model.a_F * v)
    e2A = np.exp(-2 * A)
    w = sector.n - sector.ghat_sigma * ach
    Er = 0.5 * sx**2
    Echi = 0.5 * s**2 * w**2 / ell**2
    V = layer.V(v, s)

    # Canonical M1 Maxwell normalization: L_F = -Z_F F^2 / 4.
    rhoF = 0.5 * Z * achx**2 / ell**2

    EA = (
        4 * Axx + 10 * Ax**2 - 6 * model.k4 * e2A + model.Lambda_hat
        + 0.5 * vx**2 + 0.5 * model.mhat_phi_sq * v**2 - rhoF
        + Er - Echi + V
    )
    Eell = (
        exx + 3 * Axx * ell + 6 * Ax**2 * ell + 3 * Ax * ex
        - 3 * model.k4 * e2A * ell + model.Lambda_hat * ell
        + ell * (0.5 * vx**2 + 0.5 * model.mhat_phi_sq * v**2 + rhoF + Er + Echi + V)
    )
    Ev = (
        ell * vxx + (4 * Ax * ell + ex) * vx - ell * model.mhat_phi_sq * v
        + 2 * model.a_F * ell * rhoF - ell * layer.dV_dvarphi(v, s)
    )
    Es = (
        sxx + (4 * Ax + ex / ell) * sx
        - (w**2 / ell**2) * s - layer.dV_ds(v, s)
    )

    # P = exp(4A) Z_F a_chi,x / ell.
    # Exact dimensionless Maxwell equation:
    # P_x = -(M6*gSigma) exp(4A) s_hat^2 w / ell,
    # with M6*gSigma = m_layer*q_hat = Gamma_Sigma.
    P = np.exp(4 * A) * Z * achx / ell
    Eflux = d(P, x) + sector.Gamma_Sigma * np.exp(4 * A) * s**2 * w / ell

    Crr = (
        ell * (-6 * model.k4 * e2A + 6 * Ax**2 + model.Lambda_hat)
        + 4 * Ax * ex
        - ell * (0.5 * vx**2 - 0.5 * model.mhat_phi_sq * v**2 + rhoF)
        - ell * Er + ell * Echi + ell * V
    )
    return Residuals(EA, Eell, Ev, Es, Eflux, Crr)


def maxwell_flux(A: Array, ell: Array, varphi: Array, a_chi_x: Array, a_F: float) -> Array:
    return (
        np.exp(4 * np.asarray(A, float) - 2 * a_F * np.asarray(varphi, float))
        * np.asarray(a_chi_x, float)
        / np.asarray(ell, float)
    )


def governance() -> dict[str, object]:
    return {
        "G5": G5_STATUS,
        "physical_execution_authorized": PHYSICAL_EXECUTION_AUTHORIZED,
        "rank_R_claim_allowed": RANK_R_CLAIM_ALLOWED,
        "evidence_effect": PHYSICAL_EVIDENCE_EFFECT,
        "Gamma_Sigma": "m_layer*q_hat",
        "Gamma_Sigma_status": GAMMA_SIGMA_STATUS,
    }


if __name__ == "__main__":
    raise SystemExit("implementation-only G5 library; physical execution is not authorized")
