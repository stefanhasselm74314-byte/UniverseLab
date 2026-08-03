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
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def consistent_payload() -> dict:
    d_chi = math.sqrt(0.4)
    return {
        "M6_fourth": 2.0,
        "shell_L": 2.0,
        "shell_A": 0.0,
        "shell_phi": 1.0,
        "lambda": 2.6,
        "lambda_phi": -0.2,
        "Z_sigma": 4.0,
        "Z_sigma_phi": 0.0,
        "q_sigma": 1.0,
        "d_chi": d_chi,
        "continuity_tolerance": 1e-12,
        "sides": [
            {
                "n_r": 1,
                "A": 0.0,
                "A_prime": 0.2,
                "L": 2.0,
                "L_prime": 0.6,
                "phi": 1.0,
                "phi_prime": 0.1,
                "Z_phi": 1.0,
                "Z_F": 1.0,
                "F_rchi": 2.0 * d_chi,
            },
            {
                "n_r": 1,
                "A": 0.0,
                "A_prime": 0.1,
                "L": 2.0,
                "L_prime": 0.4,
                "phi": 1.0,
                "phi_prime": 0.1,
                "Z_phi": 1.0,
                "Z_F": 1.0,
                "F_rchi": 2.0 * d_chi,
            },
        ],
    }


class JunctionContractTests(unittest.TestCase):
    def test_consistent_metric_system_closes(self) -> None:
        result = MODULE.evaluate(consistent_payload())
        self.assertAlmostEqual(result["oriented_sums"]["A_Sigma"], 0.3)
        self.assertAlmostEqual(result["oriented_sums"]["L_Sigma"], 0.5)
        self.assertAlmostEqual(result["winding"]["Y_sigma"], 0.4)
        self.assertAlmostEqual(result["residuals"]["metric_4d"], 0.0)
        self.assertAlmostEqual(result["residuals"]["metric_chi"], 0.0)
        self.assertAlmostEqual(result["residuals"]["anisotropy"], 0.0)

    def test_required_lambda_relation(self) -> None:
        result = MODULE.evaluate(consistent_payload())
        self.assertAlmostEqual(result["required_sources"]["lambda_required"], 2.6)

    def test_scalar_matching_includes_z_phi(self) -> None:
        payload = consistent_payload()
        payload["sides"][0]["Z_phi"] = 2.0
        payload["lambda_phi"] = -0.3
        result = MODULE.evaluate(payload)
        self.assertAlmostEqual(result["residuals"]["scalar"], 0.0)

    def test_gauge_matching(self) -> None:
        result = MODULE.evaluate(consistent_payload())
        self.assertAlmostEqual(result["residuals"]["gauge"], 0.0)

    def test_pure_tension_gate(self) -> None:
        payload = consistent_payload()
        payload["Z_sigma"] = 0.0
        payload["d_chi"] = 0.0
        payload["sides"][0]["L_prime"] = 0.4
        payload["sides"][1]["L_prime"] = 0.2
        payload["lambda"] = 2.4
        result = MODULE.evaluate(payload)
        self.assertAlmostEqual(result["oriented_sums"]["A_Sigma"], 0.3)
        self.assertAlmostEqual(result["oriented_sums"]["L_Sigma"], 0.3)
        self.assertAlmostEqual(result["required_sources"]["pure_tension_residual"], 0.0)
        self.assertAlmostEqual(result["residuals"]["metric_4d"], 0.0)
        self.assertAlmostEqual(result["residuals"]["metric_chi"], 0.0)

    def test_negative_required_winding_is_flagged(self) -> None:
        payload = consistent_payload()
        payload["sides"][0]["L_prime"] = 0.2
        payload["sides"][1]["L_prime"] = 0.0
        result = MODULE.evaluate(payload)
        self.assertFalse(result["winding"]["positive_winding_gate"])

    def test_induced_metric_mismatch_fails_closed(self) -> None:
        payload = consistent_payload()
        payload["sides"][1]["L"] = 2.1
        with self.assertRaises(MODULE.JunctionInputError):
            MODULE.evaluate(payload)

    def test_unhealthy_kinetic_functions_fail_closed(self) -> None:
        payload = consistent_payload()
        payload["sides"][0]["Z_F"] = 0.0
        with self.assertRaises(MODULE.JunctionInputError):
            MODULE.evaluate(payload)
        payload = consistent_payload()
        payload["sides"][0]["Z_phi"] = -1.0
        with self.assertRaises(MODULE.JunctionInputError):
            MODULE.evaluate(payload)

    def test_normal_orientation_is_explicit(self) -> None:
        payload = consistent_payload()
        payload["sides"][1]["n_r"] = -1
        result = MODULE.evaluate(payload)
        self.assertEqual(result["oriented_sums"]["normal_signature"], [1, -1])
        self.assertNotAlmostEqual(result["residuals"]["metric_4d"], 0.0)

    def test_cli_emits_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.json"
            path.write_text(json.dumps(consistent_payload()), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(MODULE_PATH), str(path)],
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)
            self.assertEqual(result["status"], "DIAGNOSTIC_ONLY")
            self.assertEqual(result["gates"]["K1-D"], "NOT_RELEASED")


if __name__ == "__main__":
    unittest.main()
