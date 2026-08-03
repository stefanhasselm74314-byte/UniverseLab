#!/usr/bin/env python3
"""Diagnostic reference implementation for the conditional MD-2S radial equations.

This is not an official boundary-value solver.  It evaluates the frozen generic
Einstein-Maxwell-scalar equations, centre-series coefficients and residuals.
No physical release or evidence effect follows from successful execution.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict


class ContractError(ValueError):
    """Raised when an input violates the declared equation contract."""


def _finite(name: str, value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ContractError(f"{name} must be numeric") from exc
    if not math.isfinite(number):
        raise ContractError(f"{name} must be finite")
    return number


def _positive(name: str, value: Any) -> float:
    number = _finite(name, value)
    if number <= 0.0:
        raise ContractError(f"{name} must be positive")
    return number


def magnetic_quantities(*, A: float, L: float, Q: float, Z_F: float) -> Dict[str, float]:
    """Return F_rchi, B^2 and M=Z_F B^2 from the Maxwell first integral."""
    A = _finite("A", A)
    L = _finite("L", L)
    Q = _finite("Q", Q)
    Z_F = _positive("Z_F", Z_F)
    exp_factor = math.exp(-4.0 * A)
    f_rchi = Q * L * exp_factor / Z_F
    b_sq = Q * Q * math.exp(-8.0 * A) / (Z_F * Z_F)
    magnetic_energy = Z_F * b_sq
    first_integral = math.exp(4.0 * A) * Z_F * f_rchi / L if L != 0.0 else math.nan
    return {
        "F_rchi": f_rchi,
        "B_sq": b_sq,
        "M": magnetic_energy,
        "first_integral": first_integral,
    }


def curvature_components(
    *, A: float, Ap: float, App: float, L: float, Lp: float, Lpp: float, K4: float
) -> Dict[str, float]:
    """Evaluate Ricci, scalar-curvature and Einstein mixed components for L>0."""
    A = _finite("A", A)
    Ap = _finite("Ap", Ap)
    App = _finite("App", App)
    L = _positive("L", L)
    Lp = _finite("Lp", Lp)
    Lpp = _finite("Lpp", Lpp)
    K4 = _finite("K4", K4)
    s = Lp / L
    lpp_over_l = Lpp / L
    k = K4 * math.exp(-2.0 * A)

    r4 = 3.0 * k - App - 4.0 * Ap * Ap - Ap * s
    rr = -lpp_over_l - 4.0 * (App + Ap * Ap)
    rchi = -lpp_over_l - 4.0 * Ap * s
    scalar = 12.0 * k - 20.0 * Ap * Ap - 8.0 * App - 8.0 * Ap * s - 2.0 * lpp_over_l

    g4 = 3.0 * App + 6.0 * Ap * Ap + 3.0 * Ap * s + lpp_over_l - 3.0 * k
    gr = 6.0 * Ap * Ap + 4.0 * Ap * s - 6.0 * k
    gchi = 4.0 * App + 10.0 * Ap * Ap - 6.0 * k
    return {
        "S": s,
        "R4_mixed": r4,
        "Rrr": rr,
        "Rchi_mixed": rchi,
        "R6": scalar,
        "G4_mixed": g4,
        "Gr_mixed": gr,
        "Gchi_mixed": gchi,
    }


def matter_components(*, phip: float, Z_phi: float, V: float, M: float) -> Dict[str, float]:
    phip = _finite("phip", phip)
    Z_phi = _positive("Z_phi", Z_phi)
    V = _finite("V", V)
    M = _finite("M", M)
    kinetic = Z_phi * phip * phip
    return {
        "T4": -0.5 * kinetic - V - 0.5 * M,
        "Tr": +0.5 * kinetic - V + 0.5 * M,
        "Tchi": -0.5 * kinetic - V + 0.5 * M,
    }


def residuals(
    *,
    A: float,
    Ap: float,
    App: float,
    L: float,
    Lp: float,
    Lpp: float,
    phi: float,
    phip: float,
    phipp: float,
    K4: float,
    Lambda6: float,
    kappa6_sq: float,
    Q: float,
    Z_phi: float,
    Z_phi_phi: float,
    Z_F: float,
    Z_F_phi: float,
    V: float,
    V_phi: float,
) -> Dict[str, float]:
    """Evaluate all local bulk residuals at an ordinary point L>0."""
    del phi  # The point value enters only through supplied functions and derivatives.
    kappa6_sq = _positive("kappa6_sq", kappa6_sq)
    Lambda6 = _finite("Lambda6", Lambda6)
    Z_phi_phi = _finite("Z_phi_phi", Z_phi_phi)
    Z_F_phi = _finite("Z_F_phi", Z_F_phi)
    V_phi = _finite("V_phi", V_phi)

    magnetic = magnetic_quantities(A=A, L=L, Q=Q, Z_F=Z_F)
    curvature = curvature_components(A=A, Ap=Ap, App=App, L=L, Lp=Lp, Lpp=Lpp, K4=K4)
    matter = matter_components(phip=phip, Z_phi=Z_phi, V=V, M=magnetic["M"])
    s = curvature["S"]

    e4 = curvature["G4_mixed"] + Lambda6 - kappa6_sq * matter["T4"]
    er = curvature["Gr_mixed"] + Lambda6 - kappa6_sq * matter["Tr"]
    echi = curvature["Gchi_mixed"] + Lambda6 - kappa6_sq * matter["Tchi"]
    scalar = (
        Z_phi * (phipp + (4.0 * Ap + s) * phip)
        + 0.5 * Z_phi_phi * phip * phip
        - V_phi
        - 0.5 * Z_F_phi * magnetic["B_sq"]
    )
    return {
        "E4": e4,
        "Er_constraint": er,
        "Echi": echi,
        "Ephi": scalar,
        **magnetic,
        **curvature,
        **matter,
    }


def evolution_second_derivatives(
    *,
    A: float,
    Ap: float,
    L: float,
    Lp: float,
    phi: float,
    phip: float,
    K4: float,
    Lambda6: float,
    kappa6_sq: float,
    Q: float,
    Z_phi: float,
    Z_phi_phi: float,
    Z_F: float,
    Z_F_phi: float,
    V: float,
    V_phi: float,
) -> Dict[str, float]:
    """Return A'', L'' and phi'' for the declared independent evolution choice."""
    del phi
    A = _finite("A", A)
    Ap = _finite("Ap", Ap)
    L = _positive("L", L)
    Lp = _finite("Lp", Lp)
    phip = _finite("phip", phip)
    K4 = _finite("K4", K4)
    Lambda6 = _finite("Lambda6", Lambda6)
    kappa6_sq = _positive("kappa6_sq", kappa6_sq)
    Z_phi = _positive("Z_phi", Z_phi)
    Z_phi_phi = _finite("Z_phi_phi", Z_phi_phi)
    Z_F = _positive("Z_F", Z_F)
    Z_F_phi = _finite("Z_F_phi", Z_F_phi)
    V = _finite("V", V)
    V_phi = _finite("V_phi", V_phi)
    Q = _finite("Q", Q)

    s = Lp / L
    k = K4 * math.exp(-2.0 * A)
    magnetic = magnetic_quantities(A=A, L=L, Q=Q, Z_F=Z_F)
    kinetic = Z_phi * phip * phip

    app = 0.25 * (
        kappa6_sq * (-0.5 * kinetic - V + 0.5 * magnetic["M"])
        + 6.0 * k
        - Lambda6
        - 10.0 * Ap * Ap
    )
    lpp_over_l = (
        kappa6_sq * (-0.5 * kinetic - V - 0.5 * magnetic["M"])
        - 3.0 * app
        - 6.0 * Ap * Ap
        - 3.0 * Ap * s
        + 3.0 * k
        - Lambda6
    )
    phipp = (
        -(4.0 * Ap + s) * phip
        - 0.5 * (Z_phi_phi / Z_phi) * phip * phip
        + V_phi / Z_phi
        + 0.5 * (Z_F_phi / Z_phi) * magnetic["B_sq"]
    )
    return {
        "App": app,
        "Lpp": L * lpp_over_l,
        "Lpp_over_L": lpp_over_l,
        "phipp": phipp,
        **magnetic,
    }


def radial_constraint(
    *, A: float, Ap: float, L: float, Lp: float, phip: float, K4: float,
    Lambda6: float, kappa6_sq: float, Q: float, Z_phi: float, Z_F: float, V: float
) -> float:
    """Return Er = G_r + Lambda6 - kappa6^2 T_r."""
    A = _finite("A", A)
    Ap = _finite("Ap", Ap)
    L = _positive("L", L)
    Lp = _finite("Lp", Lp)
    phip = _finite("phip", phip)
    K4 = _finite("K4", K4)
    Lambda6 = _finite("Lambda6", Lambda6)
    kappa6_sq = _positive("kappa6_sq", kappa6_sq)
    Z_phi = _positive("Z_phi", Z_phi)
    V = _finite("V", V)
    magnetic = magnetic_quantities(A=A, L=L, Q=Q, Z_F=Z_F)
    g_r = 6.0 * Ap * Ap + 4.0 * Ap * Lp / L - 6.0 * K4 * math.exp(-2.0 * A)
    t_r = 0.5 * Z_phi * phip * phip - V + 0.5 * magnetic["M"]
    return g_r + Lambda6 - kappa6_sq * t_r


def center_series_coefficients(
    *, A0: float, phi0: float, K4: float, Lambda6: float, kappa6_sq: float,
    Q: float, Z_phi0: float, Z_F0: float, Z_F_phi0: float, V0: float,
    V_phi0: float, Delta_chi: float
) -> Dict[str, float]:
    """Return the leading regular-centre coefficients for the generic model."""
    del phi0
    A0 = _finite("A0", A0)
    K4 = _finite("K4", K4)
    Lambda6 = _finite("Lambda6", Lambda6)
    kappa6_sq = _positive("kappa6_sq", kappa6_sq)
    Q = _finite("Q", Q)
    Z_phi0 = _positive("Z_phi0", Z_phi0)
    Z_F0 = _positive("Z_F0", Z_F0)
    Z_F_phi0 = _finite("Z_F_phi0", Z_F_phi0)
    V0 = _finite("V0", V0)
    V_phi0 = _finite("V_phi0", V_phi0)
    Delta_chi = _positive("Delta_chi", Delta_chi)

    kc = K4 * math.exp(-2.0 * A0)
    b0_sq = Q * Q * math.exp(-8.0 * A0) / (Z_F0 * Z_F0)
    m0 = Z_F0 * b0_sq
    ell1 = 2.0 * math.pi / Delta_chi
    a2 = (6.0 * kc - Lambda6 - kappa6_sq * V0 + 0.5 * kappa6_sq * m0) / 8.0
    c2 = kappa6_sq * V0 / 12.0 - 5.0 * kappa6_sq * m0 / 24.0 - kc + Lambda6 / 12.0
    p2 = (V_phi0 + 0.5 * Z_F_phi0 * b0_sq) / (4.0 * Z_phi0)
    flux_linear = Q * ell1 * math.exp(-4.0 * A0) / Z_F0
    return {
        "Kc": kc,
        "B0_sq": b0_sq,
        "M0": m0,
        "ell1": ell1,
        "a2": a2,
        "c2": c2,
        "p2": p2,
        "F_rchi_linear_coefficient": flux_linear,
        "A_chi_quadratic_coefficient": 0.5 * flux_linear,
        "deficit_angle": conical_deficit(Delta_chi=Delta_chi, ell1=ell1),
    }


def center_einstein_residuals(
    *, a2: float, c2: float, A0: float, K4: float, Lambda6: float,
    kappa6_sq: float, V0: float, M0: float
) -> Dict[str, float]:
    """Evaluate the three leading Einstein residuals of the centre series."""
    a2 = _finite("a2", a2)
    c2 = _finite("c2", c2)
    A0 = _finite("A0", A0)
    K4 = _finite("K4", K4)
    Lambda6 = _finite("Lambda6", Lambda6)
    kappa6_sq = _positive("kappa6_sq", kappa6_sq)
    V0 = _finite("V0", V0)
    M0 = _finite("M0", M0)
    kc = K4 * math.exp(-2.0 * A0)
    e4 = 12.0 * a2 + 6.0 * c2 - 3.0 * kc + Lambda6 - kappa6_sq * (-V0 - 0.5 * M0)
    er = 8.0 * a2 - 6.0 * kc + Lambda6 - kappa6_sq * (-V0 + 0.5 * M0)
    echi = er
    return {"E4_center": e4, "Er_center": er, "Echi_center": echi}


def center_scalar_residual(
    *, p2: float, Z_phi0: float, V_phi0: float, Z_F_phi0: float, B0_sq: float
) -> float:
    p2 = _finite("p2", p2)
    Z_phi0 = _positive("Z_phi0", Z_phi0)
    V_phi0 = _finite("V_phi0", V_phi0)
    Z_F_phi0 = _finite("Z_F_phi0", Z_F_phi0)
    B0_sq = _finite("B0_sq", B0_sq)
    return 4.0 * Z_phi0 * p2 - V_phi0 - 0.5 * Z_F_phi0 * B0_sq


def conical_deficit(*, Delta_chi: float, ell1: float) -> float:
    Delta_chi = _positive("Delta_chi", Delta_chi)
    ell1 = _finite("ell1", ell1)
    return 2.0 * math.pi - Delta_chi * ell1


def bianchi_constraint_derivative(
    *, Er: float, E4: float, Echi: float, Ap: float, L: float, Lp: float
) -> float:
    """Return Er' implied by the radial contracted Bianchi identity."""
    Er = _finite("Er", Er)
    E4 = _finite("E4", E4)
    Echi = _finite("Echi", Echi)
    Ap = _finite("Ap", Ap)
    L = _positive("L", L)
    Lp = _finite("Lp", Lp)
    return -4.0 * Ap * (Er - E4) - (Lp / L) * (Er - Echi)


def _compute(payload: Dict[str, Any]) -> Dict[str, Any]:
    mode = payload.get("mode")
    data = payload.get("data", {})
    if not isinstance(data, dict):
        raise ContractError("data must be an object")
    if mode == "bulk":
        evolved = evolution_second_derivatives(**data)
        local = dict(data)
        local.update({"App": evolved["App"], "Lpp": evolved["Lpp"], "phipp": evolved["phipp"]})
        return {"mode": mode, "evolution": evolved, "residuals": residuals(**local)}
    if mode == "center":
        coeff = center_series_coefficients(**data)
        einstein = center_einstein_residuals(
            a2=coeff["a2"], c2=coeff["c2"], A0=data["A0"], K4=data["K4"],
            Lambda6=data["Lambda6"], kappa6_sq=data["kappa6_sq"], V0=data["V0"], M0=coeff["M0"]
        )
        scalar = center_scalar_residual(
            p2=coeff["p2"], Z_phi0=data["Z_phi0"], V_phi0=data["V_phi0"],
            Z_F_phi0=data["Z_F_phi0"], B0_sq=coeff["B0_sq"]
        )
        return {"mode": mode, "coefficients": coeff, "einstein_residuals": einstein, "scalar_residual": scalar}
    raise ContractError("mode must be 'bulk' or 'center'")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON input containing mode and data")
    parser.add_argument("--output", type=Path, help="optional JSON output path")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = {
            "schema": "universelab.md2s-radial-equation-evaluation.v0.1",
            "status": "DIAGNOSTIC_ONLY",
            "evidence_effect": "NONE",
            "result": _compute(payload),
        }
    except (OSError, json.JSONDecodeError, ContractError, KeyError, TypeError) as exc:
        parser.error(str(exc))
        return 2
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
