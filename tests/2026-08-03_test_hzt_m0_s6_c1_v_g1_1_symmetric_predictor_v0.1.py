#!/usr/bin/env python3
"""Contract and unit tests for the preregistered C1-V G1.1 predictor test."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "2026-08-03_hzt_m0_s6_c1_v_g1_1_symmetric_predictor_v0.1.py"

spec = importlib.util.spec_from_file_location("c1_v_g1_1_predictor", TOOL)
if spec is None or spec.loader is None:
    raise RuntimeError("unable to import G1.1 predictor tool")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class G11PredictorContractTests(unittest.TestCase):
    def test_preregistration_is_fixed_and_symmetric(self) -> None:
        contract = module.load_contract()
        self.assertEqual(contract["track_id"], "HZT-M0-S6-C1-V")
        self.assertEqual(contract["block"], "G1.1")
        self.assertEqual(contract["status"], "PREREGISTERED_NOT_EXECUTED")
        self.assertEqual(
            contract["symmetric_step_magnitudes"],
            [0.08, 0.04, 0.02, 0.01, 0.005, 0.0025, 0.00125],
        )
        self.assertEqual(contract["windows"]["asymptotic_fit"], [0.04, 0.02, 0.01, 0.005])

    def test_backend_resolutions_are_preregistered(self) -> None:
        contract = module.load_contract()
        self.assertEqual(contract["backends"]["reference"]["steps"], [400, 800])
        self.assertEqual(contract["backends"]["independent"]["base_steps"], [50, 100])

    def test_predictor_is_linear_and_uncorrected(self) -> None:
        anchor = [1.0, -2.0]
        tangent = [0.5, 4.0]
        self.assertEqual(module.predictor(anchor, tangent, 0.25), [1.125, -1.0])
        contract = module.load_contract()
        self.assertFalse(contract["predictor"]["nonlinear_corrector"])
        self.assertFalse(contract["predictor"]["root_solver"])
        self.assertFalse(contract["predictor"]["branch_tracking"])
        self.assertFalse(contract["predictor"]["second_derivative"])

    def test_quadratic_synthetic_slope_and_ratios(self) -> None:
        magnitudes = [0.04, 0.02, 0.01, 0.005]
        norms = [3.0 * value * value for value in magnitudes]
        self.assertAlmostEqual(module.loglog_slope(magnitudes, norms), 2.0, places=12)
        ratios = [norms[index] / norms[index + 1] for index in range(len(norms) - 1)]
        for ratio in ratios:
            self.assertAlmostEqual(ratio, 4.0, places=12)

    def test_acceptance_corridor_is_not_adaptive(self) -> None:
        contract = module.load_contract()
        corridor = contract["acceptance_corridor"]
        self.assertEqual(corridor["loglog_slope"], [1.8, 2.2])
        self.assertEqual(corridor["halving_ratio_R_delta_over_R_half_delta"], [3.2, 4.8])
        self.assertEqual(corridor["minimum_consecutive_fit_magnitudes"], 4)
        self.assertIn("No post-run fit-window substitution", contract["pass_rule"])

    def test_release_gates_remain_closed(self) -> None:
        gate = module.load_contract()["gate_state"]
        self.assertEqual(gate["C1-V3"], "PARTIAL")
        self.assertEqual(gate["C1-V4"], "NOT_STARTED")
        self.assertEqual(gate["R1.1"], "BLOCKED")
        self.assertEqual(gate["official_MD2S_solver"], "NOT_AUTHORIZED")
        self.assertEqual(gate["K1-D"], "NOT_RELEASED")
        self.assertEqual(gate["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(gate["physical_evidence_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
