#!/usr/bin/env python3
"""Contract and result tests for the preregistered C1-V G1.1 predictor test."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "2026-08-03_hzt_m0_s6_c1_v_g1_1_symmetric_predictor_v0.1.py"
RESULT = ROOT / "registry" / "2026-08-03_HZT_M0_S6_C1_V_G1_1_SymmetricPredictorResult_v0.1.json"
CSV = ROOT / "science" / "hzt-m0" / "md2s" / "2026-08-03_HZT_M0_S6_C1_V_G1_1_SymmetricPredictorEvaluations_v0.1.csv"
LATEST_CHECKPOINT = ROOT / "registry" / "session-checkpoint-latest.json"

spec = importlib.util.spec_from_file_location("c1_v_g1_1_predictor", TOOL)
if spec is None or spec.loader is None:
    raise RuntimeError("unable to import G1.1 predictor tool")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class G11PredictorContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.recorded = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.fresh = module.run_registered_test()

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

    def test_fresh_execution_passes_registered_diagnostic(self) -> None:
        self.assertEqual(self.fresh["status"], "PASS_DIAGNOSTIC")
        self.assertEqual(self.fresh["result_status"], "NUMERICALLY_CONFIRMED")
        self.assertTrue(all(self.fresh["checks"].values()))
        self.assertFalse(self.fresh["nonlinear_corrector_implemented"])
        self.assertFalse(self.fresh["root_solver_implemented"])
        self.assertFalse(self.fresh["branch_tracking_implemented"])
        self.assertFalse(self.fresh["second_derivative_computed"])

    def test_recorded_hashes_match_fresh_execution(self) -> None:
        self.assertEqual(
            self.recorded["preregistration"]["hash_sha256_canonical_json"],
            self.fresh["preregistration_hash"],
        )
        self.assertEqual(
            self.recorded["hashes"]["evaluator_code_sha256"],
            self.fresh["code_hash"],
        )
        self.assertEqual(
            self.recorded["hashes"]["reference_code_sha256"],
            self.fresh["reference_code_hash"],
        )
        self.assertEqual(
            self.recorded["hashes"]["independent_code_sha256"],
            self.fresh["independent_code_hash"],
        )
        self.assertEqual(
            self.recorded["hashes"]["parameter_sha256"],
            self.fresh["parameter_hash"],
        )

    def test_recorded_fits_match_fresh_execution(self) -> None:
        recorded = sorted(
            self.recorded["fit_results"],
            key=lambda item: (item["backend"], item["resolution"], item["sign"]),
        )
        fresh = sorted(
            self.fresh["fit_analyses"],
            key=lambda item: (item["backend"], item["resolution"], item["sign"]),
        )
        self.assertEqual(len(recorded), len(fresh))
        for expected, actual in zip(recorded, fresh):
            self.assertEqual(
                (expected["backend"], expected["resolution"], expected["sign"]),
                (actual["backend"], actual["resolution"], actual["sign"]),
            )
            self.assertAlmostEqual(expected["slope"], actual["slope"], places=10)
            for left, right in zip(expected["halving_ratios"], actual["halving_ratios"]):
                self.assertAlmostEqual(left, right, places=10)
            self.assertTrue(actual["pass"])

    def test_evaluation_table_hash_is_canonical(self) -> None:
        digest = hashlib.sha256(CSV.read_bytes()).hexdigest()
        self.assertEqual(
            digest,
            self.recorded["hashes"]["evaluation_csv_sha256"],
        )

    def test_checkpoint_alias_matches_declared_snapshot(self) -> None:
        latest = json.loads(LATEST_CHECKPOINT.read_text(encoding="utf-8"))
        snapshot_path = latest.get("canonical_snapshot")
        self.assertIsInstance(snapshot_path, str)
        snapshot = ROOT / snapshot_path
        self.assertTrue(snapshot.is_file())
        self.assertEqual(latest, json.loads(snapshot.read_text(encoding="utf-8")))

    def test_release_gates_remain_closed(self) -> None:
        gate = self.recorded["gate_state"]
        self.assertEqual(gate["G1.1"], "PASS_DIAGNOSTIC")
        self.assertEqual(gate["C1-V3"], "PARTIAL")
        self.assertEqual(gate["C1-V4"], "NOT_STARTED")
        self.assertEqual(gate["R1.1"], "BLOCKED")
        self.assertEqual(gate["official_MD2S_solver"], "NOT_AUTHORIZED")
        self.assertEqual(gate["K1-D"], "NOT_RELEASED")
        self.assertEqual(gate["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(gate["physical_evidence_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
