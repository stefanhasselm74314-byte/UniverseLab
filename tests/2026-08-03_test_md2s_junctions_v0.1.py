#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/2026-08-03_hzt_m0_md2s_junctions_v0.1.py"
SPEC = importlib.util.spec_from_file_location("md2s_junctions_v0_1", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


class JunctionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sides = (
            mod.SideData(normal_r=1.0, A_prime=0.4, L=2.0, L_prime=0.8,
                         phi_prime=0.2, Z_phi=1.5, Q=0.7),
            mod.SideData(normal_r=-1.0, A_prime=-0.1, L=2.0, L_prime=-0.2,
                         phi_prime=-0.1, Z_phi=2.0, Q=-0.3),
        )

    def test_oriented_geometry(self) -> None:
        geom = mod.geometry(self.sides)
        self.assertAlmostEqual(geom.A_sigma, 0.5)
        self.assertAlmostEqual(geom.L_sigma, 0.5)

    def test_pure_tension_limit(self) -> None:
        geom = mod.geometry(self.sides)
        src = mod.required_metric_sources(
            A_sigma=geom.A_sigma, L_sigma=geom.L_sigma, kappa6_squared=2.0
        )
        self.assertAlmostEqual(src.Y_required, 0.0)
        self.assertAlmostEqual(src.lambda_required, 1.0)
        residuals = mod.metric_residuals(
            A_sigma=geom.A_sigma,
            L_sigma=geom.L_sigma,
            kappa6_squared=2.0,
            lambda_value=src.lambda_required,
            Y_sigma=src.Y_required,
        )
        self.assertAlmostEqual(residuals["R_4d"], 0.0)
        self.assertAlmostEqual(residuals["R_chi"], 0.0)
        self.assertAlmostEqual(residuals["pure_tension_residual"], 0.0)

    def test_anisotropic_metric_closure(self) -> None:
        A_sigma, L_sigma, kappa2 = 0.2, 0.8, 0.5
        src = mod.required_metric_sources(
            A_sigma=A_sigma, L_sigma=L_sigma, kappa6_squared=kappa2
        )
        self.assertAlmostEqual(src.Y_required, 1.2)
        self.assertAlmostEqual(src.lambda_required, 2.2)
        residuals = mod.metric_residuals(
            A_sigma=A_sigma,
            L_sigma=L_sigma,
            kappa6_squared=kappa2,
            lambda_value=src.lambda_required,
            Y_sigma=src.Y_required,
        )
        self.assertAlmostEqual(residuals["R_4d"], 0.0)
        self.assertAlmostEqual(residuals["R_chi"], 0.0)
        self.assertGreaterEqual(residuals["positive_winding_margin"], 0.0)

    def test_winding_quantities(self) -> None:
        result = mod.winding_quantities(
            L=2.0, Z_sigma=3.0, winding_n=2.0, q_sigma=0.5, A_chi=2.0
        )
        self.assertAlmostEqual(result["D_chi_sigma"], 1.0)
        self.assertAlmostEqual(result["X_sigma"], 0.25)
        self.assertAlmostEqual(result["Y_sigma"], 0.75)

    def test_scalar_residual_keeps_Z_phi(self) -> None:
        value = mod.scalar_residual(
            sides=self.sides,
            lambda_phi=-0.4,
            Z_sigma_phi=0.8,
            X_sigma=0.5,
        )
        expected_bulk = 1.0 * 1.5 * 0.2 + (-1.0) * 2.0 * (-0.1)
        self.assertAlmostEqual(value, expected_bulk - 0.4 + 0.2)

    def test_gauge_residual_Q(self) -> None:
        A, L, q, z, d = 0.0, 2.0, 0.5, 4.0, 1.0
        bulk_oriented_Q = sum(side.normal_r * side.Q for side in self.sides)
        target_surface = math.exp(-4.0 * A) / L * bulk_oriented_Q
        d_for_zero = target_surface * L * L / (q * z)
        residual = mod.gauge_residual_Q(
            sides=self.sides, A=A, L=L, q_sigma=q,
            Z_sigma=z, D_chi_sigma=d_for_zero,
        )
        self.assertAlmostEqual(residual, 0.0)

    def test_continuity_residuals(self) -> None:
        left = {"A": 0.1, "L": 2.0, "phi": 0.3, "A_chi": 0.4}
        right = dict(left)
        residuals = mod.continuity_residuals(left, right)
        self.assertTrue(all(abs(value) == 0.0 for value in residuals.values()))

    def test_fail_closed_invalid_normal_and_kinetic_data(self) -> None:
        with self.assertRaises(mod.JunctionInputError):
            mod.geometry((
                mod.SideData(normal_r=0.0, A_prime=0.0, L=1.0, L_prime=0.0),
                mod.SideData(normal_r=1.0, A_prime=0.0, L=1.0, L_prime=0.0),
            ))
        with self.assertRaises(mod.JunctionInputError):
            mod.winding_quantities(
                L=1.0, Z_sigma=-1.0, winding_n=1.0, q_sigma=1.0, A_chi=0.0
            )
        with self.assertRaises(mod.JunctionInputError):
            mod.required_metric_sources(A_sigma=0.0, L_sigma=0.0, kappa6_squared=0.0)

    def test_cli_json_output(self) -> None:
        payload = {
            "kappa6_squared": 1.0,
            "sides": [
                {"normal_r": 1, "A_prime": 0.2, "L": 1.0, "L_prime": 0.3,
                 "phi_prime": 0.0, "Z_phi": 1.0, "Q": 0.0},
                {"normal_r": -1, "A_prime": -0.2, "L": 1.0, "L_prime": -0.3,
                 "phi_prime": 0.0, "Z_phi": 1.0, "Q": 0.0}
            ],
            "surface": {
                "A": 0.0, "L": 1.0, "Z_sigma": 0.0,
                "winding_n": 0.0, "q_sigma": 0.0, "A_chi": 0.0,
                "lambda_phi": 0.0, "Z_sigma_phi": 0.0
            },
            "left_induced": {"A": 0.0, "L": 1.0, "phi": 0.0, "A_chi": 0.0},
            "right_induced": {"A": 0.0, "L": 1.0, "phi": 0.0, "A_chi": 0.0}
        }
        with tempfile.TemporaryDirectory() as temp:
            input_path = Path(temp) / "input.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(MODULE_PATH), str(input_path)],
                text=True, capture_output=True, check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        output = json.loads(proc.stdout)
        self.assertEqual(output["status"], "DIAGNOSTIC_ONLY")
        self.assertEqual(output["evidence_effect"], "NONE")
        self.assertIn("metric_residuals", output)
        self.assertIn("continuity_residuals", output)


if __name__ == "__main__":
    unittest.main()
