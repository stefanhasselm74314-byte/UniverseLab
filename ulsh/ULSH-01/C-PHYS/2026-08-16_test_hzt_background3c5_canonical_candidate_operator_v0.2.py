#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
TARGET = HERE / "2026-08-16_hzt_background3c5_canonical_candidate_operator_v0.2.py"
SPEC = importlib.util.spec_from_file_location("bg3c5_v02", TARGET)
assert SPEC is not None and SPEC.loader is not None
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def model():
    return M.BulkModel(Lambda_hat=0.7, mhat_phi_sq=2.5, a_F=0.3, k4=0.12)


def test_governance_firewall():
    assert M.PHYSICAL_EXECUTION_AUTHORIZED is False
    assert M.RANK_R_CLAIM_ALLOWED is False
    assert M.PHYSICAL_EVIDENCE_EFFECT == "NONE_IMPLEMENTATION_ONLY"
    assert M.PARENT_EQUIVALENCE_STATUS == "BULK_EXACT__FINITE_THICKNESS_NORMALIZATION_PENDING"


def test_exact_bulk_pole_coefficients_against_frozen_formulas():
    m = model()
    f0 = 0.27
    q_s = 0.44
    got = M.bulk_pole_coefficients(f0=f0, q_s=q_s, model=m)
    rho = 0.5 * q_s**2 * np.exp(2.0 * m.a_F * f0)
    a2 = (6.0*m.k4 - m.Lambda_hat - 0.5*m.mhat_phi_sq*f0**2 + rho) / 8.0
    f2 = (m.mhat_phi_sq*f0 - 2.0*m.a_F*rho) / 4.0
    g2 = 0.5*q_s*np.exp(2.0*m.a_F*f0)
    l3 = (3.0*m.k4 - 12.0*a2 - m.Lambda_hat - 0.5*m.mhat_phi_sq*f0**2 - rho) / 6.0
    expect = {"rho_F0": rho, "a2": a2, "f2": f2, "g2": g2, "l3": l3}
    for key, value in expect.items():
        assert np.isclose(got[key], value, rtol=0.0, atol=1e-15), (key, got[key], value)


def test_center_series_axis_conditions_and_winding_power():
    m = model()
    sector = M.ChargeSector(n=3, m_layer=2, q_hat=0.8)
    x = np.array([0.0, 1e-4, 2e-4, 4e-4])
    s_amp = 1.7
    p = M.center_series(x, f0=0.2, q_s=0.35, model=m, sector=sector, s_amplitude=s_amp)
    assert p.A[0] == 0.0
    assert p.ell[0] == 0.0
    assert p.a_chi[0] == 0.0
    assert p.varphi[0] == 0.2
    assert p.s[0] == 0.0
    assert np.allclose(p.s[1:] / x[1:]**3, s_amp, rtol=1e-14, atol=1e-14)
    assert abs(p.ell[1] / x[1] - 1.0) < 1e-6


def test_n0_center_amplitude_is_finite():
    m = model()
    sector = M.ChargeSector(n=0, m_layer=1, q_hat=0.9)
    x = np.array([0.0, 1e-4, 2e-4])
    p = M.center_series(x, f0=-0.1, q_s=0.2, model=m, sector=sector, s_amplitude=0.33)
    assert np.allclose(p.s, 0.33)


def test_center_free_data_budget():
    a = M.center_free_data_count(n=2, k4_fixed=True)
    assert a["free_data"] == ("f0", "g2", "s_abs_n")
    assert a["count"] == 3
    assert a["A0_fixed"] == 0.0
    assert a["ell_x0_fixed"] == 1.0
    assert a["conical_rescue_parameter"] is False
    b = M.center_free_data_count(n=0, k4_fixed=False)
    assert b["free_data"] == ("f0", "g2", "s0", "k4")
    assert b["count"] == 4


def test_charge_lattice_winding_is_dimensionless_contract():
    sector = M.ChargeSector(n=2, m_layer=3, q_hat=0.4)
    assert np.isclose(sector.ghat_sigma, 1.2)
    a_chi = np.array([0.1, 0.2])
    w = sector.n - sector.ghat_sigma * a_chi
    assert np.allclose(w, np.array([1.88, 1.76]))


def test_bulk_control_operator_accepts_regular_off_axis_profile():
    m = model()
    x = np.linspace(1e-3, 0.05, 129)
    p = M.center_series(x, f0=0.15, q_s=0.3, model=m)
    out = M.evaluate_bulk_control(p, m, q_s=0.3)
    infs = out.residual_inf()
    assert set(infs) == {"E_A", "E_ell", "E_varphi", "E_gauge", "rr_constraint"}
    assert all(np.isfinite(v) for v in infs.values())


def test_layer_local_frobenius_structure_is_finite_off_axis():
    m = model()
    sector = M.ChargeSector(n=1, m_layer=1, q_hat=0.6)
    layer = M.LayerCandidate(
        mhat_sigma_sq=lambda varphi: 0.8 + 0.0*np.asarray(varphi),
        lambdahat_sigma=0.2,
    )
    x = np.linspace(1e-4, 0.02, 129)
    p = M.center_series(x, f0=0.1, q_s=0.2, model=m, sector=sector, s_amplitude=0.05)
    out = M.evaluate_layer_local(p, sector, layer)
    assert np.all(np.isfinite(out.E_s))
    assert np.all(np.isfinite(out.winding))


if __name__ == "__main__":
    tests = [name for name in globals() if name.startswith("test_")]
    for name in sorted(tests):
        globals()[name]()
    print(f"PASS {len(tests)} tests")
