#!/usr/bin/env python3
"""Regression tests for the HZT-M0-S6-C1 dimensionless AD Jacobian preflight."""

from __future__ import annotations

import importlib.util
import json
import math
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "2026-08-03_md2s_c1_dimensionless_jacobian_v0.1.py"
CONTRACT_PATH = ROOT / "registry" / "2026-08-03_MD2S_C1_DimensionlessJacobianContract_v0.1.json"
ADDENDUM_PATH = ROOT / "science" / "hzt-m0" / "md2s" / "2026-08-03_MD2S_R1_ModelFreezeAddendum_v0.5.json"

spec = importlib.util.spec_from_file_location("md2s_c1_dimensionless_jacobian", TOOL_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("unable to load C1 Jacobian evaluator")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class C1DimensionlessJacobianTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validation = module.validate_preflight()

    def test_contract_status_and_governance(self) -> None:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["model_id"], "HZT-M0-S6-C1")
        self.assertEqual(
            contract["status"],
            "DIAGNOSTIC_JACOBIAN_PREFLIGHT_PASS_EXECUTION_BLOCKED",
        )
        self.assertFalse(contract["solver_authorized"])
        self.assertEqual(contract["historical_A0_identity"], "NOT_CLAIMED")
        self.assertEqual(contract["governance"]["R1.1"], "BLOCKED")
        self.assertEqual(contract["governance"]["K1-D"], "NOT_RELEASED")
        self.assertEqual(contract["governance"]["K1-E"], "NOT_ADMISSIBLE")

    def test_addendum_keeps_execution_blocked(self) -> None:
        addendum = json.loads(ADDENDUM_PATH.read_text(encoding="utf-8"))
        state = addendum["gate_state"]
        self.assertEqual(state["C1_DISCRETE_AD_JACOBIAN"], "RANK_8_STEP_CONVERGED_DIAGNOSTIC")
        self.assertEqual(state["C1_CONTINUUM_BVP_JACOBIAN"], "NOT_PROVEN")
        self.assertEqual(state["C1_ROOT_SOLVER"], "NOT_IMPLEMENTED")
        self.assertEqual(state["C1_OFFICIAL_SOLVER"], "NOT_AUTHORIZED")
        self.assertEqual(state["HISTORICAL_A0_IDENTITY"], "NOT_CLAIMED")

    def test_closed_form_anchor_residuals_are_zero(self) -> None:
        residuals = module.analytic_anchor_closed_form_residuals()
        self.assertEqual(len(residuals), 8)
        self.assertLessEqual(max(abs(value) for value in residuals), 1.0e-13)

    def test_anchor_profiles_match_cap_data(self) -> None:
        north = module.analytic_anchor_profiles(math.pi / 2.0, "N")
        south = module.analytic_anchor_profiles(math.pi / 2.0, "S")
        self.assertAlmostEqual(north[2], 1.0, places=14)
        self.assertAlmostEqual(south[2], 1.0, places=14)
        self.assertAlmostEqual(north[3], 0.0, places=14)
        self.assertAlmostEqual(south[3], 0.0, places=14)
        self.assertAlmostEqual(north[6], 0.5, places=14)
        self.assertAlmostEqual(south[6], -0.5, places=14)

    def test_pre_registered_residual_tolerances(self) -> None:
        self.assertLessEqual(self.validation["rk4_200_max_residual"], 2.0e-10)
        self.assertLessEqual(self.validation["rk4_400_max_residual"], 2.0e-11)
        self.assertLessEqual(self.validation["rk4_800_max_residual"], 1.0e-12)

    def test_forward_mode_ad_jacobian_is_full_rank_at_anchor(self) -> None:
        self.assertEqual(self.validation["rank_800"], 8)
        singular_values = self.validation["singular_values_800"]
        self.assertEqual(len(singular_values), 8)
        self.assertAlmostEqual(singular_values[-1], 0.0695893845582763, delta=1.0e-10)
        self.assertAlmostEqual(
            self.validation["condition_number_800"],
            221.95557616755255,
            delta=1.0e-7,
        )

    def test_jacobian_step_convergence(self) -> None:
        self.assertLessEqual(
            self.validation["jacobian_relative_change_400_to_800"],
            1.0e-9,
        )

    def test_rr_constraint_is_propagated(self) -> None:
        report = module.evaluate_anchor(200)
        self.assertLessEqual(report["constraint_maximum"], 1.0e-12)

    def test_known_scalar_shift_null_direction_is_reproduced(self) -> None:
        self.assertEqual(self.validation["shift_rank"], 7)
        regression = module.shift_null_regression(100)
        self.assertEqual(regression["rank"], 7)
        self.assertAlmostEqual(regression["singular_values"][-1], 0.0, places=14)

    def test_fail_closed_invalid_parameters(self) -> None:
        with self.assertRaises(module.ContractError):
            module.C1Parameters(q0=0.0).validate()
        with self.assertRaises(module.ContractError):
            module.C1Parameters(z_sigma=0.0).validate()
        with self.assertRaises(module.ContractError):
            module.C1Parameters(m2=-1.0).validate()

    def test_fail_closed_invalid_integration_contract(self) -> None:
        with self.assertRaises(module.ContractError):
            module.evaluate_anchor(4)
        invalid = list(module.ANCHOR_VECTOR)
        invalid[5] = module.CENTER_EPSILON / 2.0
        with self.assertRaises(module.ContractError):
            module.normalized_residuals(invalid, steps=20)

    def test_cli_validate_returns_machine_readable_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TOOL_PATH), "--mode", "validate"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertFalse(payload["solver_authorized"])
        self.assertEqual(payload["rank_800"], 8)
        self.assertEqual(payload["shift_rank"], 7)


if __name__ == "__main__":
    unittest.main()
