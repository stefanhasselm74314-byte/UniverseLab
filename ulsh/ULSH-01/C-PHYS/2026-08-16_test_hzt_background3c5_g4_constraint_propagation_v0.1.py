#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import pathlib
import sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / '2026-08-16_hzt_background3c5_full_operator_candidate_v0.3.py'
spec = importlib.util.spec_from_file_location('g5op_for_g4', TARGET)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def run(N: int) -> tuple[float, float]:
    x = np.linspace(0.2, 1.2, N)
    A = 0.02*x**2 + 0.003*x**3
    ell = x + 0.015*x**3
    v = 0.18 + 0.025*x**2 + 0.004*x**3
    s = 0.07*x + 0.01*x**3
    ach = 0.035*x**2 + 0.004*x**3

    model = m.Model(0.2, 0.7, 0.3, 0.01)
    sec = m.Sector(1, 2, 0.4)
    ms = lambda vv: 0.6 + 0.1*(np.asarray(vv, float) - 0.18)
    dms = lambda vv: np.full_like(np.asarray(vv, float), 0.1)
    z = lambda vv: np.zeros_like(np.asarray(vv, float))
    layer = m.Layer(ms, dms, 0.5, z, z)

    p = m.Profile(x, A, ell, v, s, ach)
    r = m.evaluate(p, model, sec, layer)

    Ax = m.d(A, x)
    ex = m.d(ell, x)
    vx = m.d(v, x)
    sx = m.d(s, x)
    achx = m.d(ach, x)

    Rrr = r.rr_constraint / ell
    Rmu = r.E_ell / ell
    Rchi = r.E_A

    B = (
        m.d(Rrr, x)
        + 4.0*Ax*(Rrr - Rmu)
        + (ex/ell)*(Rrr - Rchi)
        + (r.E_varphi/ell)*vx
        + r.E_s*sx
        + np.exp(-4.0*A)*(achx/ell)*r.E_flux
    )

    # Remove the boundary stencil zone. Continuum identity is exact; this test
    # checks that the implementation approaches it at the expected finite-
    # difference rate on a generic off-shell smooth profile.
    q = B[4:-4]
    return float(np.max(np.abs(q))), float(np.sqrt(np.mean(q*q)))


def main() -> None:
    # Governance remains fail-closed.
    g = m.governance()
    assert g['physical_execution_authorized'] is False
    assert g['rank_R_claim_allowed'] is False

    max128, rms128 = run(128)
    max256, rms256 = run(256)

    # Second-order finite-difference implementation: halving h should reduce
    # the Bianchi residual by approximately four. Use a conservative bound.
    assert max256 < 3.0e-7, (max128, max256)
    assert rms256 < 2.0e-7, (rms128, rms256)
    assert max256/max128 < 0.35, (max128, max256)
    assert rms256/rms128 < 0.35, (rms128, rms256)

    print('G4 constraint-propagation regression QA: PASS (continuum identity analytic; finite-difference convergence only)')


if __name__ == '__main__':
    main()
