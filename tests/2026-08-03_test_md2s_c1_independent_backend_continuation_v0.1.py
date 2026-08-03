#!/usr/bin/env python3
"""Regression tests for the independent C1 backend and linear tangent preflight."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "2026-08-03_md2s_c1_independent_backend_continuation_v0.1.py"
CONTRACT_PATH = ROOT / "registry" / "2026-08-03_MD2S_C1_IndependentBackendContinuationContract_v0.1.json"
ADDENDUM_PATH = ROOT / "science" / "hzt-m0" / "md2s" / "2026-08-03_MD2S_R1_ModelFreezeAddendum_v0.6.json"

spec = importlib.util.spec_from_file_location("md2s_c1_independent_backend", TOOL_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("unable to load independent C1 evaluator")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class C1IndependentBackendContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validation = module.validate_preflight()

    def test_contract_status_and_method_independence(self) -> None:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["model_id"], "HZT-M0-S6-C1")
        self.assertEqual(
            contract["status"],
            "INDEPENDENT_BACKEND_AND_LINEAR_TANGENT_PREFLIGHT_PASS_EXECUTION_BLOCKED",
        )
        self.assertEqual(
            contract["independent_backend"]["integration_method"],
            "implicit_midpoint",
        )
        self.assertIn(
            "RK4 integrator",
            contract["independent_backend"]["not_reused_from_reference"],
        )
        self.assertEqual(
            contract["independent_sensitivity"]["method"],
            "symmetric finite difference of the complete extrapolated implicit-midpoint IVP-to-residual map",
        )
        self.assertFalse(contract["official_solver_authorized"])

    def test_addendum_keeps_all_release_gates_closed(self) -> None:
        addendum = json.loads(ADDENDUM_PATH.read_text(encoding="utf-8"))
        state = addendum["gate_state"]
        self.assertEqual(state["C1_BACKEND_AGREEMENT"], "PASS")
        self.assertEqual(
            state["C1_LINEAR_LAMBDA0_TANGENT"],
            "NUMERICALLY_CONFIRMED_DIAGNOSTIC",
        )
        self.assertEqual(
            state["C1_CONTINUUM_IMPLICIT_FUNCTION_THEOREM"],
            "NOT_PROVEN",
        )
        self.assertEqual(state["C1_NONLINEAR_CONTINUATION"], "NOT_EXECUTED")
        self.assertEqual(state["C1_ROOT_CORRECTOR"], "NOT_IMPLEMENTED")
        self.assertEqual(state["C1_OFFICIAL_SOLVER"], "NOT_AUTHORIZED")
        self.assertEqual(state["R1.1"], "BLOCKED")
        self.assertEqual(state["K1-D"], "NOT_RELEASED")
        self.assertEqual(state["K1-E"], "NOT_ADMISSIBLE")

    def test_independent_anchor_residual_convergence(self) -> None:
        self.assertLessEqual(self.validation["independent_residual_50"], 1.0e-8)
        self.assertLessEqual(self.validation["independent_residual_100"], 1.0e-9)
        self.assertLess(
            self.validation["independent_residual_100"],
            self.validation["independent_residual_50"] / 10.0,
        )

    def test_independent_jacobian_converges_and_matches_reference(self) -> None:
        self.assertLessEqual(
            self.validation["independent_jacobian_relative_change_50_to_100"],
            5.0e-8,
        )
        self.assertLessEqual(
            self.validation["independent_to_reference_jacobian_relative_frobenius"],
            2.0e-8,
        )
        self.assertLessEqual(
            self.validation["singular_spectrum_max_relative"],
            2.0e-7,
        )

    def test_independent_rank_and_condition(self) -> None:
        self.assertEqual(self.validation["independent_rank"], 8)
        self.assertLess(self.validation["independent_condition_number"], 1.0e6)
        singular_values = self.validation["independent_singular_values"]
        self.assertEqual(len(singular_values), 8)
        self.assertAlmostEqual(
            singular_values[-1],
            0.0695893845775842,
            delta=2.0e-10,
        )

    def test_lambda0_parameter_derivative(self) -> None:
        expected = [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0]
        actual = self.validation["parameter_residual_derivative"]
        self.assertEqual(len(actual), 8)
        for left, right in zip(actual, expected):
            self.assertAlmostEqual(left, right, delta=1.0e-10)

    def test_linear_tangent_closes_and_matches_reference(self) -> None:
        self.assertLessEqual(
            self.validation["linear_closure_infinity_norm"],
            1.0e-10,
        )
        self.assertLessEqual(
            self.validation["tangent_relative_difference"],
            2.0e-7,
        )
        tangent = self.validation["independent_tangent"]
        self.assertAlmostEqual(tangent[1], 0.425, delta=2.0e-8)
        self.assertAlmostEqual(tangent[4], -0.425, delta=2.0e-8)
        self.assertAlmostEqual(tangent[5], tangent[6], delta=1.0e-8)
        self.assertAlmostEqual(tangent[7], 0.0479166666667, delta=2.0e-8)

    def test_no_global_corrector_or_root_solver_is_exposed(self) -> None:
        prohibited = {
            "solve_bvp",
            "root_solve",
            "newton_corrector",
            "continuation_step",
            "track_branch",
        }
        self.assertTrue(prohibited.isdisjoint(set(dir(module))))
        self.assertFalse(self.validation["nonlinear_corrector_implemented"])
        self.assertFalse(self.validation["root_solver_implemented"])
        self.assertFalse(self.validation["official_solver_authorized"])

    def test_fail_closed_invalid_parameters_and_steps(self) -> None:
        with self.assertRaises(module.ContractError):
            module.C1Parameters(q0=0.0).validate()
        with self.assertRaises(module.ContractError):
            module.C1Parameters(z_sigma=0.0).validate()
        with self.assertRaises(module.ContractError):
            module.C1Parameters(m2=-1.0).validate()
        with self.assertRaises(module.ContractError):
            module.implicit_midpoint_region(0.0, 0.0, 0.5, 1.0, 0.25, steps=4)

    def test_fail_closed_singular_linear_system(self) -> None:
        with self.assertRaises(module.ContractError):
            module.solve_linear([[1.0, 2.0], [2.0, 4.0]], [1.0, 2.0])

    def test_cli_residual_is_machine_readable_and_blocked(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(TOOL_PATH),
                "--mode",
                "residual",
                "--base-steps",
                "20",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(len(payload["normalized_residuals"]), 8)
        self.assertFalse(payload["official_solver_authorized"])


if __name__ == "__main__":
    unittest.main()
