#!/usr/bin/env python3
"""Reference evaluator for the conditional MD-2S oriented cap junction system."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


class JunctionInputError(ValueError):
    """Raised when the junction payload violates the declared contract."""


def _finite(name: str, value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise JunctionInputError(f"{name} must be numeric") from exc
    if not math.isfinite(number):
        raise JunctionInputError(f"{name} must be finite")
    return number


def evaluate(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise JunctionInputError("payload must be an object")

    m6_4 = _finite("M6_fourth", payload.get("M6_fourth"))
    shell_l = _finite("shell_L", payload.get("shell_L"))
    lam = _finite("lambda", payload.get("lambda"))
    lam_phi = _finite("lambda_phi", payload.get("lambda_phi", 0.0))
    z_sigma = _finite("Z_sigma", payload.get("Z_sigma"))
    z_sigma_phi = _finite("Z_sigma_phi", payload.get("Z_sigma_phi", 0.0))
    q_sigma = _finite("q_sigma", payload.get("q_sigma", 0.0))
    d_chi = _finite("d_chi", payload.get("d_chi", 0.0))
    continuity_tol = _finite("continuity_tolerance", payload.get("continuity_tolerance", 1e-10))

    if m6_4 <= 0:
        raise JunctionInputError("M6_fourth must be positive")
    if shell_l <= 0:
        raise JunctionInputError("shell_L must be positive")
    if z_sigma < 0:
        raise JunctionInputError("Z_sigma must be non-negative for the healthy minimal winding branch")
    if continuity_tol < 0:
        raise JunctionInputError("continuity_tolerance must be non-negative")

    sides = payload.get("sides")
    if not isinstance(sides, list) or len(sides) < 2:
        raise JunctionInputError("sides must contain at least two adjacent regions")

    a_sum = 0.0
    l_sum = 0.0
    scalar_flux = 0.0
    gauge_flux = 0.0
    normal_signature: list[int] = []
    continuity_residuals: list[float] = []

    shell_a = payload.get("shell_A")
    shell_phi = payload.get("shell_phi")
    if shell_a is not None:
        shell_a = _finite("shell_A", shell_a)
    if shell_phi is not None:
        shell_phi = _finite("shell_phi", shell_phi)

    for index, side in enumerate(sides):
        if not isinstance(side, dict):
            raise JunctionInputError(f"sides[{index}] must be an object")
        n_r = _finite(f"sides[{index}].n_r", side.get("n_r"))
        if n_r not in (-1.0, 1.0):
            raise JunctionInputError(f"sides[{index}].n_r must be +1 or -1")
        normal_signature.append(int(n_r))

        a_prime = _finite(f"sides[{index}].A_prime", side.get("A_prime"))
        l_value = _finite(f"sides[{index}].L", side.get("L"))
        l_prime = _finite(f"sides[{index}].L_prime", side.get("L_prime"))
        phi_prime = _finite(f"sides[{index}].phi_prime", side.get("phi_prime"))
        z_phi = _finite(f"sides[{index}].Z_phi", side.get("Z_phi"))
        z_f = _finite(f"sides[{index}].Z_F", side.get("Z_F"))
        f_rchi = _finite(f"sides[{index}].F_rchi", side.get("F_rchi"))

        if l_value <= 0:
            raise JunctionInputError(f"sides[{index}].L must be positive")
        if z_phi <= 0:
            raise JunctionInputError(f"sides[{index}].Z_phi must be positive")
        if z_f <= 0:
            raise JunctionInputError(f"sides[{index}].Z_F must be positive")
        if abs(l_value - shell_l) > continuity_tol:
            raise JunctionInputError(
                f"sides[{index}].L violates induced-metric continuity: {l_value} vs {shell_l}"
            )

        if shell_a is not None and "A" in side:
            a_value = _finite(f"sides[{index}].A", side["A"])
            continuity_residuals.append(a_value - shell_a)
            if abs(a_value - shell_a) > continuity_tol:
                raise JunctionInputError(f"sides[{index}].A violates frame-fixed continuity")
        if shell_phi is not None and "phi" in side:
            phi_value = _finite(f"sides[{index}].phi", side["phi"])
            continuity_residuals.append(phi_value - shell_phi)
            if abs(phi_value - shell_phi) > continuity_tol:
                raise JunctionInputError(f"sides[{index}].phi violates scalar continuity")

        a_sum += n_r * a_prime
        l_sum += n_r * l_prime / l_value
        scalar_flux += n_r * z_phi * phi_prime
        gauge_flux += n_r * z_f * f_rchi / (l_value * l_value)

    x_sigma = d_chi * d_chi / (shell_l * shell_l)
    y_sigma = z_sigma * x_sigma
    d_chi_upper = d_chi / (shell_l * shell_l)

    metric_4d = -m6_4 * (3.0 * a_sum + l_sum) + lam + 0.5 * y_sigma
    metric_chi = -4.0 * m6_4 * a_sum + lam - 0.5 * y_sigma
    anisotropy = y_sigma - m6_4 * (l_sum - a_sum)
    scalar = scalar_flux + lam_phi + 0.5 * z_sigma_phi * x_sigma
    gauge = gauge_flux - q_sigma * z_sigma * d_chi_upper

    y_required = m6_4 * (l_sum - a_sum)
    lambda_required = 0.5 * m6_4 * (7.0 * a_sum + l_sum)
    pure_tension_residual = a_sum - l_sum

    return {
        "schema": "universelab.md2s-junction-evaluation.v0.1",
        "status": "DIAGNOSTIC_ONLY",
        "evidence_effect": "NONE",
        "oriented_sums": {
            "A_Sigma": a_sum,
            "L_Sigma": l_sum,
            "normal_signature": normal_signature,
        },
        "winding": {
            "X_sigma": x_sigma,
            "Y_sigma": y_sigma,
            "Y_sigma_required": y_required,
            "positive_winding_gate": y_required >= 0.0,
        },
        "required_sources": {
            "lambda_required": lambda_required,
            "pure_tension_residual": pure_tension_residual,
        },
        "residuals": {
            "metric_4d": metric_4d,
            "metric_chi": metric_chi,
            "anisotropy": anisotropy,
            "scalar": scalar,
            "gauge": gauge,
            "continuity_max_abs": max((abs(x) for x in continuity_residuals), default=0.0),
        },
        "gates": {
            "MF-001": "PARTIAL_CONDITIONAL",
            "MF-002": "PARTIAL_CONDITIONAL",
            "MF-005_FORM": "DERIVED_CONDITIONAL",
            "MF-005_NUMERICAL": "BLOCKED_UNLESS_ALL_INPUTS_ARE_SOURCE_BACKED",
            "OFFICIAL_SOLVER_IMPLEMENTATION": "FORBIDDEN",
            "K1-D": "NOT_RELEASED",
            "K1-E": "NOT_ADMISSIBLE",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON junction payload")
    parser.add_argument("--output", type=Path, help="optional output path")
    args = parser.parse_args()

    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = evaluate(payload)
    except (OSError, json.JSONDecodeError, JunctionInputError) as exc:
        parser.error(str(exc))

    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
