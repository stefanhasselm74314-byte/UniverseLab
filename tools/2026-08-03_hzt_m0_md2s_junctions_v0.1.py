#!/usr/bin/env python3
"""Diagnostic reference evaluator for the conditional MD-2S junction contract.

This module evaluates algebraic continuity, metric, scalar and local gauge
residuals. It does not solve the radial BVP, impose global flux quantization or
release any physical gate.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


class JunctionInputError(ValueError):
    """Raised when a junction input violates the declared contract."""


@dataclass(frozen=True)
class SideData:
    normal_r: float
    A_prime: float
    L: float
    L_prime: float
    phi_prime: float = 0.0
    Z_phi: float = 1.0
    Q: float = 0.0

    def validate(self) -> None:
        if self.normal_r not in (-1.0, 1.0):
            raise JunctionInputError("normal_r must be exactly -1 or +1")
        if not math.isfinite(self.L) or self.L <= 0.0:
            raise JunctionInputError("L must be finite and strictly positive")
        if not math.isfinite(self.Z_phi) or self.Z_phi <= 0.0:
            raise JunctionInputError("Z_phi must be finite and strictly positive")
        for name in ("A_prime", "L_prime", "phi_prime", "Q"):
            if not math.isfinite(getattr(self, name)):
                raise JunctionInputError(f"{name} must be finite")


@dataclass(frozen=True)
class JunctionGeometry:
    A_sigma: float
    L_sigma: float


@dataclass(frozen=True)
class MetricSources:
    lambda_required: float
    Y_required: float



def _finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise JunctionInputError(f"{name} must be finite")
    return value



def geometry(sides: Iterable[SideData]) -> JunctionGeometry:
    sides = tuple(sides)
    if len(sides) < 2:
        raise JunctionInputError("at least two oriented sides are required")
    for side in sides:
        side.validate()
    return JunctionGeometry(
        A_sigma=sum(side.normal_r * side.A_prime for side in sides),
        L_sigma=sum(side.normal_r * side.L_prime / side.L for side in sides),
    )



def winding_quantities(*, L: float, Z_sigma: float, winding_n: float,
                       q_sigma: float, A_chi: float) -> dict[str, float]:
    L = _finite("L", L)
    Z_sigma = _finite("Z_sigma", Z_sigma)
    if L <= 0.0:
        raise JunctionInputError("L must be strictly positive")
    if Z_sigma < 0.0:
        raise JunctionInputError("Z_sigma must be non-negative for the positive-winding gate")
    d_chi = _finite("winding_n", winding_n) - _finite("q_sigma", q_sigma) * _finite("A_chi", A_chi)
    X_sigma = d_chi * d_chi / (L * L)
    return {
        "D_chi_sigma": d_chi,
        "X_sigma": X_sigma,
        "Y_sigma": Z_sigma * X_sigma,
    }



def required_metric_sources(*, A_sigma: float, L_sigma: float,
                            kappa6_squared: float) -> MetricSources:
    A_sigma = _finite("A_sigma", A_sigma)
    L_sigma = _finite("L_sigma", L_sigma)
    kappa6_squared = _finite("kappa6_squared", kappa6_squared)
    if kappa6_squared <= 0.0:
        raise JunctionInputError("kappa6_squared must be strictly positive")
    inv = 1.0 / kappa6_squared
    return MetricSources(
        lambda_required=0.5 * inv * (7.0 * A_sigma + L_sigma),
        Y_required=inv * (L_sigma - A_sigma),
    )



def metric_residuals(*, A_sigma: float, L_sigma: float,
                     kappa6_squared: float, lambda_value: float,
                     Y_sigma: float) -> dict[str, float]:
    kappa6_squared = _finite("kappa6_squared", kappa6_squared)
    if kappa6_squared <= 0.0:
        raise JunctionInputError("kappa6_squared must be strictly positive")
    A_sigma = _finite("A_sigma", A_sigma)
    L_sigma = _finite("L_sigma", L_sigma)
    lambda_value = _finite("lambda_value", lambda_value)
    Y_sigma = _finite("Y_sigma", Y_sigma)
    return {
        "R_4d": -(3.0 * A_sigma + L_sigma)
                + kappa6_squared * (lambda_value + 0.5 * Y_sigma),
        "R_chi": -4.0 * A_sigma
                 + kappa6_squared * (lambda_value - 0.5 * Y_sigma),
        "pure_tension_residual": A_sigma - L_sigma,
        "positive_winding_margin": L_sigma - A_sigma,
    }



def scalar_residual(*, sides: Iterable[SideData], lambda_phi: float,
                    Z_sigma_phi: float, X_sigma: float) -> float:
    sides = tuple(sides)
    for side in sides:
        side.validate()
    return (
        sum(side.normal_r * side.Z_phi * side.phi_prime for side in sides)
        + _finite("lambda_phi", lambda_phi)
        + 0.5 * _finite("Z_sigma_phi", Z_sigma_phi) * _finite("X_sigma", X_sigma)
    )



def gauge_residual_Q(*, sides: Iterable[SideData], A: float, L: float,
                     q_sigma: float, Z_sigma: float,
                     D_chi_sigma: float) -> float:
    sides = tuple(sides)
    for side in sides:
        side.validate()
    A = _finite("A", A)
    L = _finite("L", L)
    if L <= 0.0:
        raise JunctionInputError("L must be strictly positive")
    q_sigma = _finite("q_sigma", q_sigma)
    Z_sigma = _finite("Z_sigma", Z_sigma)
    D_chi_sigma = _finite("D_chi_sigma", D_chi_sigma)
    if Z_sigma < 0.0:
        raise JunctionInputError("Z_sigma must be non-negative")
    bulk_term = math.exp(-4.0 * A) / L * sum(
        side.normal_r * side.Q for side in sides
    )
    surface_term = q_sigma * Z_sigma * D_chi_sigma / (L * L)
    return bulk_term - surface_term



def continuity_residuals(left: dict[str, float], right: dict[str, float]) -> dict[str, float]:
    required = ("A", "L", "phi", "A_chi")
    missing = [key for key in required if key not in left or key not in right]
    if missing:
        raise JunctionInputError(f"continuity data missing: {', '.join(missing)}")
    if float(left["L"]) <= 0.0 or float(right["L"]) <= 0.0:
        raise JunctionInputError("both induced L values must be strictly positive")
    return {
        "Delta_A": _finite("left.A", left["A"]) - _finite("right.A", right["A"]),
        "Delta_L": _finite("left.L", left["L"]) - _finite("right.L", right["L"]),
        "Delta_phi": _finite("left.phi", left["phi"]) - _finite("right.phi", right["phi"]),
        "Delta_A_chi": _finite("left.A_chi", left["A_chi"]) - _finite("right.A_chi", right["A_chi"]),
    }



def side_from_mapping(data: dict[str, Any]) -> SideData:
    return SideData(
        normal_r=float(data["normal_r"]),
        A_prime=float(data["A_prime"]),
        L=float(data["L"]),
        L_prime=float(data["L_prime"]),
        phi_prime=float(data.get("phi_prime", 0.0)),
        Z_phi=float(data.get("Z_phi", 1.0)),
        Q=float(data.get("Q", 0.0)),
    )



def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    sides = tuple(side_from_mapping(item) for item in payload["sides"])
    geom = geometry(sides)
    kappa6_squared = float(payload["kappa6_squared"])
    winding = winding_quantities(
        L=float(payload["surface"]["L"]),
        Z_sigma=float(payload["surface"]["Z_sigma"]),
        winding_n=float(payload["surface"]["winding_n"]),
        q_sigma=float(payload["surface"]["q_sigma"]),
        A_chi=float(payload["surface"]["A_chi"]),
    )
    required = required_metric_sources(
        A_sigma=geom.A_sigma,
        L_sigma=geom.L_sigma,
        kappa6_squared=kappa6_squared,
    )
    lambda_value = float(payload["surface"].get("lambda", required.lambda_required))
    Y_sigma = float(payload["surface"].get("Y_sigma", winding["Y_sigma"]))
    result: dict[str, Any] = {
        "status": "DIAGNOSTIC_ONLY",
        "evidence_effect": "NONE",
        "geometry": {
            "A_sigma": geom.A_sigma,
            "L_sigma": geom.L_sigma,
        },
        "winding": winding,
        "required_sources": {
            "lambda_required": required.lambda_required,
            "Y_required": required.Y_required,
        },
        "metric_residuals": metric_residuals(
            A_sigma=geom.A_sigma,
            L_sigma=geom.L_sigma,
            kappa6_squared=kappa6_squared,
            lambda_value=lambda_value,
            Y_sigma=Y_sigma,
        ),
        "scalar_residual": scalar_residual(
            sides=sides,
            lambda_phi=float(payload["surface"].get("lambda_phi", 0.0)),
            Z_sigma_phi=float(payload["surface"].get("Z_sigma_phi", 0.0)),
            X_sigma=winding["X_sigma"],
        ),
        "gauge_residual": gauge_residual_Q(
            sides=sides,
            A=float(payload["surface"]["A"]),
            L=float(payload["surface"]["L"]),
            q_sigma=float(payload["surface"]["q_sigma"]),
            Z_sigma=float(payload["surface"]["Z_sigma"]),
            D_chi_sigma=winding["D_chi_sigma"],
        ),
    }
    if "left_induced" in payload and "right_induced" in payload:
        result["continuity_residuals"] = continuity_residuals(
            payload["left_induced"], payload["right_induced"]
        )
    return result



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 JSON input file")
    parser.add_argument("--output", type=Path, help="optional JSON output file")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = evaluate(payload)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
