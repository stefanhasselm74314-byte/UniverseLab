from __future__ import annotations

import importlib.util
import math
import pathlib
import unittest


MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "tools"
    / "hzt_m0_overlap_bridge_v0_1.py"
)
SPEC = importlib.util.spec_from_file_location("hzt_m0_overlap_bridge_v0_1", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot import {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class OverlapBridgeTests(unittest.TestCase):
    def test_md2q_locked_point(self) -> None:
        point = MODULE.evaluate_bridge_point(
            alpha=0.15,
            sigma_B=1.2,
            kappa_6=1.0,
            lambda_chi=4.25,
            beta_0=0.1,
        )
        self.assertAlmostEqual(point.gamma, 0.9944444444444445, places=15)
        self.assertAlmostEqual(point.x, 0.8808919646289889, places=15)
        self.assertAlmostEqual(point.q, 0.5855868950525662, places=15)
        self.assertAlmostEqual(point.eta_bulk, 0.024267488339526102, places=15)
        self.assertAlmostEqual(
            point.d_eta_d_lambda_chi,
            0.0029405899018908354,
            places=15,
        )

    def test_overlap_formula_matches_independent_quadrature(self) -> None:
        gamma = 0.9944444444444445
        radius = MODULE.radius_from_tension(1.0, 4.25)
        x = gamma * radius * radius
        analytic = MODULE.q_flat_gaussian_2d(x)
        numeric = MODULE.numerical_q_flat_gaussian_2d(
            gamma,
            radius,
            intervals=20_000,
        )
        self.assertAlmostEqual(analytic, numeric, places=12)

    def test_exact_peak(self) -> None:
        beta_0 = 0.1
        x_peak, q_peak, eta_peak = MODULE.exact_peak(beta_0)
        self.assertAlmostEqual(x_peak, math.log(2.0), places=15)
        self.assertEqual(q_peak, 0.5)
        self.assertEqual(eta_peak, 0.025)
        self.assertAlmostEqual(MODULE.d_eta_dx(beta_0, x_peak), 0.0, places=15)
        self.assertAlmostEqual(
            MODULE.eta_partition_mixing(beta_0, x_peak),
            eta_peak,
            places=15,
        )

    def test_exact_derivative_matches_finite_difference(self) -> None:
        beta_0 = 0.1
        x = 0.8808919646289889
        h = 1.0e-6
        finite = (
            MODULE.eta_partition_mixing(beta_0, x + h)
            - MODULE.eta_partition_mixing(beta_0, x - h)
        ) / (2.0 * h)
        exact = MODULE.d_eta_dx(beta_0, x)
        self.assertAlmostEqual(finite, exact, places=10)

    def test_small_x_asymptotic(self) -> None:
        beta_0 = 0.1
        x = 1.0e-8
        eta = MODULE.eta_partition_mixing(beta_0, x)
        leading = beta_0 * x
        self.assertAlmostEqual(eta / leading, 1.0, places=7)

    def test_large_x_asymptotic(self) -> None:
        beta_0 = 0.1
        x = 30.0
        eta = MODULE.eta_partition_mixing(beta_0, x)
        leading = beta_0 * math.exp(-x)
        self.assertAlmostEqual(eta / leading, 1.0, places=12)

    def test_x_only_columns_are_collinear(self) -> None:
        shape = [1.0, 2.0, -0.5, 3.0]
        columns = MODULE.x_only_jacobian_columns(
            shape,
            dx_dp=[1.5, -2.0, 0.25],
            eta_x=0.4,
        )
        reference = columns[0]
        for column in columns[1:]:
            for i, value_i in enumerate(reference):
                for j, value_j in enumerate(reference):
                    determinant = value_i * column[j] - value_j * column[i]
                    self.assertAlmostEqual(determinant, 0.0, places=14)

    def test_x_only_columns_vanish_at_peak(self) -> None:
        eta_x = MODULE.d_eta_dx(0.1, math.log(2.0))
        columns = MODULE.x_only_jacobian_columns(
            [1.0, -2.0, 4.0],
            dx_dp=[1.0, -3.0, 8.0],
            eta_x=eta_x,
        )
        for column in columns:
            for value in column:
                self.assertAlmostEqual(value, 0.0, places=15)

    def test_invalid_inputs_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.gamma_from_profiles(-1.0, 1.0)
        with self.assertRaises(ValueError):
            MODULE.gamma_from_profiles(0.1, 0.0)
        with self.assertRaises(ValueError):
            MODULE.x_from_parameters(1.0, 0.0, 1.0)
        with self.assertRaises(ValueError):
            MODULE.q_flat_gaussian_2d(-0.1)
        with self.assertRaises(ValueError):
            MODULE.numerical_q_flat_gaussian_2d(1.0, 1.0, intervals=99)


if __name__ == "__main__":
    unittest.main()
