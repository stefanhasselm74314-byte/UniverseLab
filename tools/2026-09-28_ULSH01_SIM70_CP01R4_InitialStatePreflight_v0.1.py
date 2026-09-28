#!/usr/bin/env python3
"""SIM-70 QA-only initial-state preflight for the frozen CP01R4 solver.

This helper is intentionally not wired into the operational release path.
It demonstrates the fail-closed guard required before the first residual or
Jacobian evaluation without changing the frozen numerical method.
"""
from __future__ import annotations

from typing import Any

import numpy as np


def validate_initial_state(
    backend: Any,
    initial: Any,
    node_count: int,
    *,
    rho_min: float = 1.0e-4,
    ell_margin: float = 1.0e-8,
) -> dict[str, Any]:
    reasons: list[str] = []
    array = np.asarray(initial)

    expected = int(backend.state_size(node_count))
    if array.ndim != 1 or array.size != expected:
        reasons.append("STATE_SHAPE_INVALID")
        return {
            "pass": False,
            "reasons": reasons,
            "residual_evaluated": False,
            "jacobian_evaluated": False,
            "solver_executed": False,
        }

    if np.iscomplexobj(array):
        reasons.append("COMPLEX_INITIAL_STATE_FORBIDDEN")
    if not np.all(np.isfinite(array)):
        reasons.append("NONFINITE_INITIAL_STATE")

    if not reasons:
        try:
            regions, parameters = backend.unpack_state(array, node_count)
        except Exception:
            reasons.append("STATE_UNPACK_FAILED")
        else:
            if float(parameters[5]) <= rho_min:
                reasons.append("RHO_N_BELOW_MARGIN")
            if float(parameters[6]) <= rho_min:
                reasons.append("RHO_S_BELOW_MARGIN")
            tau = backend.chebyshev_lobatto(node_count).tau
            north_lhat = 1.0 + tau * regions[0][1]
            south_lhat = 1.0 + tau * regions[1][1]
            if float(np.min(north_lhat)) <= ell_margin:
                reasons.append("ELL_N_BELOW_MARGIN")
            if float(np.min(south_lhat)) <= ell_margin:
                reasons.append("ELL_S_BELOW_MARGIN")

    return {
        "pass": not reasons,
        "reasons": reasons,
        "residual_evaluated": False,
        "jacobian_evaluated": False,
        "solver_executed": False,
        "physical_interpretation": "NONE",
        "canonical_effect": "NONE",
        "integration_status": "QA_ONLY_NOT_WIRED_TO_FROZEN_OPERATIONAL_PATH",
    }
