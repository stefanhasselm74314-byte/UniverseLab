#!/usr/bin/env python3
"""Implementation-only QA for the Background3C5 finite-thickness residual operator.

This is algebraic/software QA. A PASS has physical_evidence_effect=NONE.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
TARGET = HERE / "2026-08-15_hzt_background3c5_finite_thickness_operator_v0.1.py"
SPEC = importlib.util.spec_from_file_location("bg3c5op", TARGET)
assert SPEC is not None and SPEC.loader is not None
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def zeros(x):
    return np.zeros_like(np.asarray(x, dtype=float))


def test_normalization_identity():
    n = M.Normalization(M6=2.0, a_F=0.25, q_hat=0.8, m_layer=3)
    n.validate()
    assert np.isclose(n.q_ref, 0.4)
    assert np.isclose(n.gSigma, 1.2)
    phi = np.array([0.0, 4.0, 8.0])
    assert np.allclose(n.varphi(phi), [0.0, 1.0, 2.0])
    assert np.allclose(n.dZ_F_dphi(phi), (-2.0 * n.a_F / n.M6**2) * n.Z_F(phi))


def test_charge_lattice_reconstruction():
    for m in (-3, -1, 0, 2, 5):
        n = M.Normalization(M6=5.0, a_F=0.0, q_hat=1.25, m_layer=m)
        assert np.isclose(n.gSigma / n.q_ref if n.q_ref else 0.0, float(m))


def test_flat_zero_source_residual():
    # Algebraic reference state on a finite interval. This is not a physical
    # center solution because B is held constant rather than conical.
    r = np.linspace(1.0, 2.0, 17)
    z = np.zeros_like(r)
    p = M.Profile(r=r, A=z, B=z, C=z, phi=z, s=z, Q=z,
                  theta_prime=z, A_chi=z)
    n = M.Normalization(M6=1.0, a_F=0.25, q_hat=1.0, m_layer=1)
    potentials = M.Potentials(
        V_bulk=zeros,
        dV_bulk_dphi=zeros,
        V_sigma=zeros,
        dV_sigma_ds=zeros,
        Lambda_delta=0.0,
    )
    out = M.evaluate_residuals(p, n, potentials)
    for name, value in out.residual_inf().items():
        assert value < 1.0e-13, (name, value)
    assert np.allclose(out.chi, 0.0)
    assert np.allclose(out.At_prime, 0.0)


def test_maxwell_source_sign_and_identity():
    r = np.linspace(0.5, 1.5, 21)
    A = np.full_like(r, 0.1)
    B = np.full_like(r, -0.2)
    C = np.full_like(r, 0.05)
    phi = np.full_like(r, 0.3)
    s = np.full_like(r, 0.4)
    theta_prime = np.full_like(r, 0.7)
    A_chi = np.full_like(r, 0.2)
    Q = np.zeros_like(r)
    p = M.Profile(r=r, A=A, B=B, C=C, phi=phi, s=s, Q=Q,
                  theta_prime=theta_prime, A_chi=A_chi)
    n = M.Normalization(M6=2.0, a_F=0.25, q_hat=0.8, m_layer=3)
    potentials = M.Potentials(zeros, zeros, zeros, zeros)
    out = M.evaluate_residuals(p, n, potentials)
    chi = theta_prime - n.gSigma * A_chi
    expected_J = 2.0 * n.gSigma * np.exp(3*A - B + C + n.gamma) * s**2 * chi
    assert np.allclose(out.maxwell, expected_J, rtol=1e-13, atol=1e-13)


def test_firewall_constants():
    assert M.PHYSICAL_EXECUTION_AUTHORIZED is False
    assert M.RANK_R_CLAIM_ALLOWED is False
    assert M.PHYSICAL_EVIDENCE_EFFECT.startswith("NONE")


def main():
    tests = [
        test_normalization_identity,
        test_charge_lattice_reconstruction,
        test_flat_zero_source_residual,
        test_maxwell_source_sign_and_identity,
        test_firewall_constants,
    ]
    for fn in tests:
        fn()
        print(f"PASS {fn.__name__}")
    print("PASS_BACKGROUND3C5_OPERATOR_QA__PHYSICAL_EVIDENCE_EFFECT_NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
