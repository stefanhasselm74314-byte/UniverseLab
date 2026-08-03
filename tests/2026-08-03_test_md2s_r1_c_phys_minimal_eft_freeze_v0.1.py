#!/usr/bin/env python3
"""Regression tests for MD2S-R1-C-PHYS Freeze-1B."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-03_validate_md2s_r1_c_phys_minimal_eft_freeze_v0.1.py"
CONTRACT = ROOT / "registry/2026-08-03_MD2S_R1_C_PHYS_MinimalEFTFunctionFreezeContract_v0.1.json"
STATUS = ROOT / "registry/2026-08-03_UniverseLab_C_PHYS_Freeze1B_Status_v0.1.json"
CLAIMS = ROOT / "registry/2026-08-03_UniverseLab_ClaimRegister_C_PHYS_Freeze1B_v0.1.json"

spec = importlib.util.spec_from_file_location("c_phys_freeze_1b_validator", TOOL)
if spec is None or spec.loader is None:
    raise RuntimeError("unable to import Freeze-1B validator")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class CPhysFreeze1BTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.status = json.loads(STATUS.read_text(encoding="utf-8"))
        cls.claims = json.loads(CLAIMS.read_text(encoding="utf-8"))
        cls.result = module.validate()

    def test_exact_function_family(self) -> None:
        functions = self.contract["exact_functions"]
        self.assertEqual(functions["U"]["formula"], "U(phi)=1/2*m_phi^2*phi^2")
        self.assertEqual(functions["Z_F"]["formula"], "Z_F(phi)=1")
        self.assertEqual(
            functions["lambda"]["formula"],
            "lambda(phi)=M6^5*tau*exp(alpha*varphi)",
        )
        self.assertEqual(
            functions["Z_sigma"]["formula"],
            "Z_sigma(phi)=M6^3*z_sigma",
        )

    def test_scalar_domain_and_charge_normalization(self) -> None:
        self.assertEqual(
            self.contract["field_normalization_and_domain"]["scalar_domain_varphi"],
            "R",
        )
        charge = self.contract["charge_normalization"]
        self.assertEqual(charge["q_ref"], "1/M6")
        self.assertTrue(charge["not_a_coordinate_convention"])

    def test_parameter_budget_is_exactly_five(self) -> None:
        budget = self.contract["parameter_identifiability_budget"]
        self.assertEqual(budget["continuous_model_parameter_count"], 5)
        self.assertEqual(len(budget["continuous_dimensionless_model_parameters"]), 5)
        self.assertEqual(budget["continuous_shooting_unknown_count"], 8)
        self.assertEqual(budget["independent_boundary_residual_count"], 8)
        self.assertFalse(budget["fit_authorized"])

    def test_redundancies_are_explicit(self) -> None:
        removed = " ".join(
            self.contract["minimality_and_redundancy_audit"]["removed_exact_redundancies"]
        )
        self.assertIn("U0", removed)
        self.assertIn("Lambda6", removed)
        self.assertIn("alpha", removed)
        self.assertIn("phi->-phi", removed)

    def test_function_positivity_is_not_stability(self) -> None:
        audit = self.contract["positivity_and_boundedness_audit"]
        self.assertTrue(audit["U_bounded_below"])
        self.assertTrue(audit["Z_F_strictly_positive"])
        self.assertTrue(audit["lambda_strictly_positive"])
        self.assertTrue(audit["Z_sigma_strictly_positive"])
        self.assertFalse(audit["background_ghost_freedom_proven"])
        self.assertFalse(audit["perturbative_stability_proven"])

    def test_track_firewall(self) -> None:
        firewall = self.contract["track_firewall"]
        self.assertEqual(firewall["historical_A0_identity"], "NOT_CLAIMED")
        self.assertFalse(firewall["historical_parameter_values_used"])
        self.assertFalse(firewall["C1_V_parameter_values_migrated"])
        self.assertFalse(firewall["C1_V_functional_forms_migrated"])
        self.assertFalse(firewall["observational_fit_used_to_select_functions"])

    def test_release_gates_remain_closed(self) -> None:
        gate = self.contract["gate_state"]
        self.assertEqual(gate["R1.0"], "ACTIVE_MODEL_FREEZE_INCOMPLETE")
        self.assertEqual(
            gate["R1.0_substate"],
            "FUNCTION_FAMILY_FROZEN_BENCHMARK_INSTANCE_OPEN",
        )
        self.assertEqual(gate["R1.1"], "BLOCKED")
        self.assertEqual(gate["R1.2"], "BLOCKED")
        self.assertEqual(gate["official_MD2S_solver"], "NOT_AUTHORIZED")
        self.assertEqual(gate["K1-D"], "NOT_RELEASED")
        self.assertEqual(gate["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(gate["physical_evidence_effect"], "NONE")

    def test_claim_register_preserves_evidence_limits(self) -> None:
        items = self.claims["claims"]
        self.assertEqual(items[0]["status"], "CONDITIONAL")
        self.assertEqual(items[0]["evidence_effect"], "MODEL_DEFINITION_ONLY")
        self.assertEqual(items[1]["evidence_effect"], "FORMAL_MODEL_ACCOUNTING_ONLY")
        self.assertEqual(items[2]["evidence_effect"], "INPUT_HYGIENE_ONLY")
        self.assertTrue(all(item["physical_evidence_effect"] == "NONE" for item in items))

    def test_checkpoint_and_manifest_are_synchronized(self) -> None:
        self.assertEqual(
            self.result["synchronization"]["checkpoint"],
            "UL-CHK-20260803-011",
        )
        self.assertEqual(
            self.result["synchronization"]["manifest_release"],
            "2.5-c-phys-freeze-1b-v0.1",
        )

    def test_decision_is_append_only(self) -> None:
        self.assertEqual(self.result["decision"], "UL-DEC-0020")

    def test_next_block_is_freeze_1c_without_solver(self) -> None:
        self.assertEqual(self.result["next_block"], "C-PHYS-R1.0-FREEZE-1C")
        self.assertFalse(self.result["solver_authorized"])
        self.assertEqual(self.result["physical_evidence_effect"], "NONE")

    def test_cli_returns_machine_readable_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TOOL), "--json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(
            payload["contract"],
            "MD2S_R1_C_PHYS_MINIMAL_EFT_FUNCTION_FREEZE",
        )


if __name__ == "__main__":
    unittest.main()
