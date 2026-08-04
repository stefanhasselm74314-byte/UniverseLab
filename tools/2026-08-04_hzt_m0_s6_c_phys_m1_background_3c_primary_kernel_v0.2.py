#!/usr/bin/env python3
"""Canonical v0.2 adapter for the Background-3C primary kernel.

It preserves the v0.1 collocation and Newton implementation and replaces only
the seed construction with the exact Background-3B seed specification:
seed_j = base + (1/20) * multiplier_j * fixed_direction.
Direct invocation remains forbidden.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.1.py"
SPEC = importlib.util.spec_from_file_location("background3c_primary_kernel_base_v01", BASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import Background-3C primary base kernel")
BASE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)

SEED_AMPLITUDE_SCALE = 1.0 / 20.0
SEED_MULTIPLIERS = (0.0, 1 / 8, -1 / 8, 1 / 4, -1 / 4, 1 / 2, -1 / 2)


def seed_direction(node_count: int) -> np.ndarray:
    tau = BASE.chebyshev_lobatto(node_count).tau
    one_minus_tau = 1.0 - tau
    regions = [
        [
            one_minus_tau,
            one_minus_tau**2,
            one_minus_tau,
            tau * one_minus_tau,
        ],
        [
            -one_minus_tau,
            -one_minus_tau**2,
            -one_minus_tau,
            -tau * one_minus_tau,
        ],
    ]
    parameters = np.asarray([1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0])
    return BASE.pack_state(regions, parameters)


def seven_seeds(node_count: int) -> list[np.ndarray]:
    base = BASE.control_seed_state(node_count)
    direction = seed_direction(node_count)
    return [
        base + SEED_AMPLITUDE_SCALE * multiplier * direction
        for multiplier in SEED_MULTIPLIERS
    ]


BASE.seed_direction = seed_direction
BASE.seven_seeds = seven_seeds


def __getattr__(name: str):
    return getattr(BASE, name)


def direct_invocation_denied() -> int:
    return BASE.direct_invocation_denied()


if __name__ == "__main__":
    raise SystemExit(direct_invocation_denied())
