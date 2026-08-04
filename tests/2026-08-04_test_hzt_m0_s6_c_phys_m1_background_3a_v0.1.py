#!/usr/bin/env python3
"""Regression tests for C-PHYS-M1 BACKGROUND-3A preregistration."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_verify_hzt_m0_s6_c_phys_m1_background_3a_v0.1.py"
CONTRACT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"
REQUIREMENTS = ROOT / "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3A_v0.1.txt"

SPEC = importlib.util.spec_from_file_location("background_3a_verifier", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import BACKGROUND-3A verifier")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class Background3APreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.result = MODULE.validate()

    def test_exact_control_seed(self) -> None:
        seed = self.result["exact_bulk_seed"]
        self.assertEqual(seed["bulk_residuals"], "PASS_EXACT")
        self.assertEqual(seed["constraint"], "PASS_EXACT")
        self.assertEqual(seed["patch_residual"], "PASS_EXACT")
        self.assertEqual(seed["nonzero_cap_defects"], "PASS_EXPLICIT")

    def test_seed_is_not_mislabeled_as_solution(self) -> None:
        seed = self.contract["exact_bulk_control_seed"]
        self.assertEqual(
            seed["classification"],
            "EXACT_BULK_AND_PATCH_SEED_BOUNDARY_INEXACT",
        )
        self.assertTrue(seed["not_a_solution_claim"])
        defects = seed["deliberately_nonzero_cap_defects"]
        self.assertEqual(defects["R_4d"], "1+9*y0/8")
        self.assertEqual(defects["R_chi"], "1-9*y0/8")
        self.assertEqual(defects["R_gauge_local"], "-3*y0/2")

    def test_tau_chart_limits_are_exact(self) -> None:
        chart = self.result["tau_chart"]
        self.assertEqual(chart["status"], "PASS_EXACT_LIMITS")
        self.assertEqual(chart["Lhat_0"], "1")
        self.assertEqual(chart["u_ell_0"], "-pi**2/24")
        self.assertEqual(chart["u_g_N_0"], "+pi**2/16")
        self.assertEqual(chart["u_g_S_0"], "-pi**2/16")

    def test_model_instance_and_sector_are_fixed(self) -> None:
        instance = self.contract["diagnostic_instance"]
        self.assertEqual(
            instance["dimensionless_model_parameters"],
            {
                "Lambda_hat": 1,
                "mhat_phi_sq": 1,
                "a_F": "1/4",
                "lambda_hat": 1,
                "z_sigma_hat": 1,
                "q_hat": 1,
            },
        )
        self.assertEqual(instance["discrete_sector"]["sector_id"], "NF1-NS1-MS1")
        self.assertEqual(instance["parameter_scan"], "FORBIDDEN_IN_BACKGROUND_3A_AND_3B")
        self.assertEqual(instance["sector_scan"], "FORBIDDEN_IN_BACKGROUND_3A_AND_3B")

    def test_only_a_f_is_continued(self) -> None:
        homotopy = self.contract["control_homotopy"]
        self.assertEqual(homotopy["only_varied_model_coefficient"], "a_F(h)=h/4")
        self.assertTrue(homotopy["all_other_model_parameters_fixed"])
        self.assertTrue(homotopy["discrete_sector_fixed"])
        self.assertEqual(homotopy["minimum_step"], "1/256")
        self.assertIn("NO_ACCEPTED_CANDIDATE", homotopy["failure_rule"])

    def test_primary_backend_is_deterministic(self) -> None:
        primary = self.contract["primary_backend"]
        self.assertEqual(primary["continuation_degree"], 32)
        self.assertEqual(primary["target_refinement_degrees"], [48, 64, 96])
        self.assertEqual(
            primary["jacobian"]["method"],
            "complex_step_componentwise_on_analytic_residual_map",
        )
        self.assertEqual(primary["determinism"]["random_numbers"], "FORBIDDEN")
        self.assertFalse(primary["jacobian"]["fallback_allowed"])

    def test_independent_backend_is_structurally_different(self) -> None:
        backend = self.contract["independent_backend"]
        self.assertEqual(backend["coordinate"], "physical dimensionless x_s")
        self.assertEqual(backend["integrator"], "DOP853")
        self.assertEqual(backend["pole_cutoff_sequence"], ["1e-3", "5e-4", "2.5e-4"])
        self.assertIn("finite-difference", backend["boundary_root_method"])

    def test_acceptance_is_joint_and_fail_closed(self) -> None:
        acceptance = self.contract["fail_closed_candidate_acceptance"]
        self.assertEqual(
            acceptance["classification_if_all_pass"],
            "NUMERICAL_BACKGROUND_CANDIDATE_DIAGNOSTIC",
        )
        self.assertEqual(
            acceptance["classification_if_any_fail"],
            "NO_ACCEPTED_CANDIDATE",
        )
        self.assertEqual(
            acceptance["required_primary_conditions"]["normalized_bulk_residual_inf_at_N96"],
            "<=1e-9",
        )
        self.assertEqual(
            acceptance["required_independent_backend_conditions"]["profile_agreement_with_primary"],
            "<=5e-5",
        )

    def test_no_execution_occurred(self) -> None:
        execution = self.contract["execution_protocol"]
        self.assertEqual(execution["current_execution_state"], "NOT_STARTED")
        self.assertFalse(execution["result_artifact_created"])
        self.assertFalse(self.result["solver_executed"])
        self.assertFalse(self.result["candidate_background_created"])

    def test_release_and_evidence_gates_remain_closed(self) -> None:
        gate = self.contract["gate_state"]
        self.assertEqual(gate["BACKGROUND_3B"], "NOT_STARTED")
        self.assertEqual(
            gate["diagnostic_candidate_execution"],
            "NOT_AUTHORIZED_IN_THIS_BLOCK",
        )
        self.assertEqual(gate["physical_background"], "NOT_ESTABLISHED")
        self.assertEqual(gate["background_existence"], "NOT_PROVEN")
        self.assertEqual(gate["Fredholm_property"], "NOT_PROVEN")
        self.assertEqual(gate["official_MD2S_solver"], "NOT_AUTHORIZED")
        self.assertEqual(gate["R1.1"], "BLOCKED")
        self.assertEqual(gate["R1.2"], "BLOCKED")
        self.assertEqual(gate["K1-D"], "NOT_RELEASED")
        self.assertEqual(gate["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(gate["physical_evidence_effect"], "NONE")

    def test_dependency_versions_are_pinned(self) -> None:
        pins = REQUIREMENTS.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            pins,
            [
                "numpy==2.1.3",
                "scipy==1.14.1",
                "sympy==1.13.3",
                "mpmath==1.3.0",
            ],
        )

    def test_cli_returns_machine_readable_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TOOL), "--json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "PASS_METHOD_PREREGISTRATION")
        self.assertEqual(
            payload["contract"],
            "C_PHYS_M1_BACKGROUND_3A_PREREGISTRATION",
        )


if __name__ == "__main__":
    unittest.main()
