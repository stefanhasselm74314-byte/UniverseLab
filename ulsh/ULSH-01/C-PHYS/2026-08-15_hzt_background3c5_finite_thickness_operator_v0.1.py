#!/usr/bin/env python3
"""HZT-M0 / S6 / C-PHYS Background3C5 finite-thickness residual operator v0.1.

IMPLEMENTATION-ONLY. This module evaluates the currently frozen local residual
blocks. It is deliberately NOT a nonlinear BVP solver, does not authorize a
physical run, and produces no physical evidence.

Authoritative conventions:
    varphi = phi / M6**2
    Z_phi = 1
    Z_F = exp(-2*a_F*varphi)
    q_ref = q_hat / M6
    gSigma = m_layer*q_hat/M6

The caller owns the radial discretization, center-series treatment, outer
matching and nonlinear solve. Those remain separate authorization gates.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import numpy as np

Array = np.ndarray
ScalarFn = Callable[[Array], Array]
BiScalarFn = Callable[[Array, Array], Array]


@dataclass(frozen=True)
class Normalization:
    M6: float
    a_F: float
    q_hat: float
    m_layer: int
    gamma: float = 0.0

    def validate(self) -> None:
        if not np.isfinite(self.M6) or self.M6 <= 0.0:
            raise ValueError("M6 must be finite and positive")
        if not np.isfinite(self.a_F) or not np.isfinite(self.q_hat):
            raise ValueError("a_F and q_hat must be finite")
        if int(self.m_layer) != self.m_layer:
            raise ValueError("m_layer must be an integer charge-lattice label")

    @property
    def q_ref(self) -> float:
        return self.q_hat / self.M6

    @property
    def gSigma(self) -> float:
        return self.m_layer * self.q_hat / self.M6

    def varphi(self, phi: Array) -> Array:
        return np.asarray(phi) / self.M6**2

    def Z_F(self, phi: Array) -> Array:
        return np.exp(-2.0 * self.a_F * self.varphi(phi))

    def dZ_F_dphi(self, phi: Array) -> Array:
        return (-2.0 * self.a_F / self.M6**2) * self.Z_F(phi)


@dataclass(frozen=True)
class Potentials:
    V_bulk: ScalarFn
    dV_bulk_dphi: ScalarFn
    V_sigma: ScalarFn
    dV_sigma_ds: ScalarFn
    Lambda_delta: float = 0.0

    def V_tot(self, phi: Array, s: Array) -> Array:
        return self.V_bulk(phi) + self.Lambda_delta + self.V_sigma(s)


@dataclass(frozen=True)
class Profile:
    r: Array
    A: Array
    B: Array
    C: Array
    phi: Array
    s: Array
    Q: Array
    theta_prime: Array
    A_chi: Array


@dataclass(frozen=True)
class ResidualEvaluation:
    r: Array
    maxwell: Array
    scalar: Array
    matter: Array
    einstein_u: Array
    einstein_v: Array
    einstein_w: Array
    constraint: Array
    chi: Array
    At_prime: Array
    electric_invariant: Array

    def residual_inf(self) -> dict[str, float]:
        blocks = {
            "maxwell": self.maxwell,
            "scalar": self.scalar,
            "matter": self.matter,
            "einstein_u": self.einstein_u,
            "einstein_v": self.einstein_v,
            "einstein_w": self.einstein_w,
            "constraint": self.constraint,
        }
        return {
            name: float(np.max(np.abs(value))) if value.size else 0.0
            for name, value in blocks.items()
        }


def _as_1d(name: str, value: Array, n: int | None = None) -> Array:
    arr = np.asarray(value, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    if n is not None and arr.size != n:
        raise ValueError(f"{name} has size {arr.size}; expected {n}")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains non-finite values")
    return arr


def validate_profile(profile: Profile) -> Profile:
    r = _as_1d("r", profile.r)
    if r.size < 5:
        raise ValueError("at least five radial nodes are required for residual QA")
    if np.any(np.diff(r) <= 0.0):
        raise ValueError("r must be strictly increasing")
    n = r.size
    fields = {
        name: _as_1d(name, getattr(profile, name), n)
        for name in ("A", "B", "C", "phi", "s", "Q", "theta_prime", "A_chi")
    }
    return Profile(r=r, **fields)


def derivative(y: Array, r: Array) -> Array:
    """Second-order edge / central numerical derivative for residual QA only."""
    return np.gradient(np.asarray(y, dtype=float), np.asarray(r, dtype=float), edge_order=2)


def evaluate_residuals(
    profile: Profile,
    normalization: Normalization,
    potentials: Potentials,
) -> ResidualEvaluation:
    """Evaluate the frozen Background3C5 local residual blocks.

    A zero vector is necessary for a solution but is not by itself a certified
    BVP solution: center regularity, outer matching, branch continuity,
    discretization convergence and provenance are audited elsewhere.
    """
    normalization.validate()
    p = validate_profile(profile)
    r = p.r

    A1 = derivative(p.A, r)
    B1 = derivative(p.B, r)
    C1 = derivative(p.C, r)
    phi1 = derivative(p.phi, r)
    s1 = derivative(p.s, r)

    u, v, w = A1, B1, phi1
    u1, v1, w1 = derivative(u, r), derivative(v, r), derivative(w, r)

    chi = p.theta_prime - normalization.gSigma * p.A_chi
    ZF = normalization.Z_F(p.phi)
    dZF = normalization.dZ_F_dphi(p.phi)

    exp3ABCg = np.exp(3.0 * p.A + p.B - p.C + normalization.gamma)
    exp3ABpCg = np.exp(3.0 * p.A + p.B + p.C + normalization.gamma)
    exp3AmBpCg = np.exp(3.0 * p.A - p.B + p.C + normalization.gamma)

    At_prime = p.Q * np.exp(-3.0 * p.A - p.B + p.C - normalization.gamma) / ZF
    electric_invariant = np.exp(-2.0 * p.C) * At_prime**2

    J_src = (
        2.0 * normalization.gSigma
        * exp3AmBpCg
        * p.s**2
        * chi
    )
    maxwell = derivative(p.Q, r) + J_src

    scalar_flux = exp3ABCg * phi1
    scalar_source = exp3ABpCg * (
        0.25 * dZF * np.exp(-2.0 * p.C) * At_prime**2
        + potentials.dV_bulk_dphi(p.phi)
    )
    scalar = derivative(scalar_flux, r) - scalar_source

    matter_flux = exp3AmBpCg * s1
    matter = (
        derivative(matter_flux, r)
        - exp3AmBpCg * p.s * chi**2
        - 0.5 * exp3ABpCg * potentials.dV_sigma_ds(p.s)
    )

    Vtot = potentials.V_tot(p.phi, p.s)
    T0 = np.exp(-2.0 * p.C) * s1**2 - 2.0 * potentials.V_sigma(p.s)
    Tchi = np.exp(-2.0 * p.B) * p.s**2 * chi**2

    Cu = (
        -(1.0 / 6.0) * np.exp(2.0 * p.C) * Vtot
        + (1.0 / 24.0) * electric_invariant
        + 0.25 * np.exp(2.0 * p.C - 2.0 * p.B) * p.s**2 * chi**2
        + 0.25 * s1**2
    )
    Cv = (
        -(1.0 / 6.0) * np.exp(2.0 * p.C) * Vtot
        - 0.125 * electric_invariant
        - 0.75 * np.exp(2.0 * p.C - 2.0 * p.B) * p.s**2 * chi**2
        - 0.75 * s1**2
    )
    Cw = np.exp(2.0 * p.C) * potentials.dV_bulk_dphi(p.phi)

    Su = -u * (3.0 * u + v - C1) + (1.0 / 6.0) * np.exp(2.0 * p.C) * (T0 + Tchi)
    Sv = -v * (3.0 * u + v - C1) + (1.0 / 6.0) * np.exp(2.0 * p.C) * (T0 - 3.0 * Tchi)
    Sw = -w * (3.0 * u + v - C1)

    einstein_u = u1 - (Cu + Su)
    einstein_v = v1 - (Cv + Sv)
    einstein_w = w1 - (Cw + Sw)

    constraint = (
        np.exp(-2.0 * p.C) * (6.0 * u**2 + 6.0 * u * v - 0.5 * w**2)
        + Vtot
        + 0.5 * electric_invariant
        + 0.5 * np.exp(-2.0 * p.B) * p.s**2 * chi**2
        - 0.5 * np.exp(-2.0 * p.C) * s1**2
    )

    return ResidualEvaluation(
        r=r,
        maxwell=maxwell,
        scalar=scalar,
        matter=matter,
        einstein_u=einstein_u,
        einstein_v=einstein_v,
        einstein_w=einstein_w,
        constraint=constraint,
        chi=chi,
        At_prime=At_prime,
        electric_invariant=electric_invariant,
    )


PHYSICAL_EXECUTION_AUTHORIZED = False
PHYSICAL_EVIDENCE_EFFECT = "NONE_IMPLEMENTATION_ONLY"
RANK_R_CLAIM_ALLOWED = False


if __name__ == "__main__":
    raise SystemExit(
        "implementation-only residual operator; no standalone physical execution is authorized"
    )
