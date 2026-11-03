#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import pathlib
import sys
import inspect
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE / '2026-08-16_hzt_background3c5_full_operator_candidate_v0.3.py'
spec = importlib.util.spec_from_file_location('g5op', TARGET)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def layer_zero():
    z = lambda v: np.zeros_like(np.asarray(v, float))
    return m.Layer(z, z, 0.0, z, z)


def main():
    # Governance remains fail-closed even though the coefficient identity is closed.
    g = m.governance()
    assert g['physical_execution_authorized'] is False
    assert g['rank_R_claim_allowed'] is False
    assert g['evidence_effect'] == 'NONE_IMPLEMENTATION_ONLY'
    assert g['Gamma_Sigma'] == 'm_layer*q_hat'
    assert g['Gamma_Sigma_status'] == 'PROVENANCE_CLOSED_CANONICAL_M1'

    # Gamma_Sigma must not be a free caller-supplied argument anymore.
    assert 'Gamma_Sigma' not in inspect.signature(m.evaluate).parameters

    # Smooth synthetic profile, used only for algebraic identities.
    x = np.linspace(0.1, 1.0, 64)
    A = 0.03 * x * x
    ell = x + 0.01 * x**3
    v = 0.2 + 0.02 * x * x
    ach = 0.04 * x * x
    model = m.Model(0.2, 0.7, 0.3, 0.01)
    sec = m.Sector(1, 2, 0.4)

    # Frozen charge-lattice identity.
    assert abs(sec.ghat_sigma - sec.m_layer * sec.q_hat) < 1e-15
    assert abs(sec.Gamma_Sigma - sec.ghat_sigma) < 1e-15
    assert abs(sec.Gamma_Sigma - 0.8) < 1e-15

    p0 = m.Profile(x, A, ell, v, np.zeros_like(x), ach)
    r0 = m.evaluate(p0, model, sec, layer_zero())

    # With s=0 and V_layer=0, layer equation and Maxwell current source vanish.
    assert np.max(np.abs(r0.E_s)) < 1e-12
    achx = m.d(ach, x)
    Z = np.exp(-2 * model.a_F * v)
    P0 = np.exp(4 * A) * Z * achx / ell
    assert np.max(np.abs(r0.E_flux - m.d(P0, x))) < 1e-12

    # Stress sign regression: constant nonzero s, flat layer potential.
    const = lambda vv: np.full_like(np.asarray(vv, float), 0.6)
    zero = lambda vv: np.zeros_like(np.asarray(vv, float))
    lay = m.Layer(const, zero, 0.5, zero, zero)
    s = np.full_like(x, 0.15)
    p = m.Profile(x, A, ell, v, s, ach)
    r = m.evaluate(p, model, sec, lay)
    V = 0.5 * 0.6 * s**2 + 0.25 * 0.5 * s**4
    w = sec.n - sec.ghat_sigma * ach
    Echi = 0.5 * s**2 * w**2 / ell**2

    # Er=0 for constant s. Exact Einstein insertion signs.
    assert np.max(np.abs((r.E_A - r0.E_A) - (-Echi + V))) < 2e-10
    assert np.max(np.abs((r.E_ell - r0.E_ell) - ell * (Echi + V))) < 2e-10
    assert np.max(np.abs((r.rr_constraint - r0.rr_constraint) - ell * (Echi + V))) < 2e-10

    # Exact Maxwell source coefficient regression. This specifically excludes
    # the quarantined factor-2 normalization from operator v0.1.
    expected_source = sec.Gamma_Sigma * np.exp(4 * A) * s**2 * w / ell
    source_from_residual = r.E_flux - m.d(P0, x)
    assert np.max(np.abs(source_from_residual - expected_source)) < 2e-12
    assert np.max(np.abs(source_from_residual - 2.0 * expected_source)) > 1e-6

    # Conservative bulk flux identity: frozen first integral gives P=q_s.
    qs = 0.37
    achx_control = qs * ell * np.exp(-4 * A + 2 * model.a_F * v)
    P = m.maxwell_flux(A, ell, v, achx_control, model.a_F)
    assert np.max(np.abs(P - qs)) < 1e-12

    print('G5 operator candidate v0.3 regression QA: PASS (Gamma_Sigma provenance closed; software/algebra only)')


if __name__ == '__main__':
    main()
