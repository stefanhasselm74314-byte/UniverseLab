from __future__ import annotations

import importlib.util
import math
import pathlib
import sys
import unittest


MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "tools"
    / "hzt_m0_spectral_bridge_v0_1.py"
)
SPEC = importlib.util.spec_from_file_location("hzt_m0_spectral_bridge_v0_1", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot import {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SpectralBridgeTests(unittest.TestCase):
    def test_reference_bessel_roots(self) -> None:
        xi_d = MODULE.xi_dirichlet_axisymmetric()
        xi_n = MODULE.xi_neumann_first_massive_axisymmetric()
        self.assertAlmostEqual(xi_d, 2.404825557695773, places=13)
        self.assertAlmostEqual(xi_n, 3.831705970207512, places=13)
        self.assertAlmostEqual(MODULE.bessel_j0(xi_d), 0.0, places=13)
        self.assertAlmostEqual(MODULE.bessel_j1(xi_n), 0.0, places=13)

    def test_md2q_diagnostic_values(self) -> None:
        result = MODULE.evaluate_md2q_spectral_diagnostic()
        self.assertAlmostEqual(result.radius_chi, 0.9411764705882353, places=15)
        self.assertAlmostEqual(result.xi_eff, 0.05176470588235294, places=15)
        self.assertAlmostEqual(
            result.m_dirichlet_axisymmetric,
            result.xi_dirichlet_axisymmetric / result.radius_chi,
            places=15,
        )
        self.assertAlmostEqual(
            result.m_neumann_first_massive_axisymmetric,
            result.xi_neumann_first_massive_axisymmetric / result.radius_chi,
            places=15,
        )
        self.assertGreater(result.dirichlet_mass_ratio_to_m_eff, 40.0)
        self.assertGreater(result.neumann_mass_ratio_to_m_eff, 70.0)

    def test_inverse_radius_scaling(self) -> None:
        xi = MODULE.xi_dirichlet_axisymmetric()
        m_1 = MODULE.mass_from_radius(xi, 1.0)
        m_2 = MODULE.mass_from_radius(xi, 2.0)
        self.assertAlmostEqual(m_1 / m_2, 2.0, places=15)

    def test_radius_mass_inverse(self) -> None:
        xi = 2.5
        radius = 4.0
        mass = MODULE.mass_from_radius(xi, radius)
        reconstructed = MODULE.radius_required_for_mass(xi, mass)
        self.assertAlmostEqual(reconstructed, radius, places=15)

    def test_bisection_fails_without_bracket(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.bisect_root(lambda x: x * x + 1.0, -1.0, 1.0)

    def test_invalid_inputs_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.radius_from_tension(0.0, 1.0)
        with self.assertRaises(ValueError):
            MODULE.radius_from_tension(1.0, -1.0)
        with self.assertRaises(ValueError):
            MODULE.mass_from_radius(-1.0, 1.0)
        with self.assertRaises(ValueError):
            MODULE.radius_required_for_mass(1.0, 0.0)
        with self.assertRaises(ValueError):
            MODULE.bessel_j0(math.inf)


if __name__ == "__main__":
    unittest.main()
