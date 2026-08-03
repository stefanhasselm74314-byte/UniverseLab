#!/usr/bin/env python3
"""Regression tests for the MD2S-R1-C-PHYS operator-entry contract."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "2026-08-03_validate_md2s_r1_c_phys_operator_entry_v0.1.py"
CONTRACT = ROOT / "registry" / "2026-08-03_MD2S_R1_C_PHYS_ParentActionOperatorEntryContract_v0.1.json"

SPEC = importlib.util.spec_from_file_location("c_phys_operator_entry_validator", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import C-PHYS validator")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CPhysOperatorEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.validate()
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_track_and_phase_are_isolated(self) -> None:
        self.assertEqual(self.result["track_id"], "MD2S-R1-C-PHYS")
        self.assertEqual(self.result["phase"], "R1.0")
        self.assertFalse(
            self.contract["track_firewall"]["C1_V_equations_used_as_physical_source"]
        )
        self.assertEqual(
            self.contract["track_firewall"]["historical_A0_identity"],
            "NOT_CLAIMED",
        )

    def test_minimal_parent_action_is_not_overextended(self) -> None:
        action = self.contract["parent_action"]
        self.assertEqual(
            action["scalar_kinetic_function"],
            "Z_phi=1_FROZEN_FOR_THIS_MINIMAL_BRANCH",
        )
        self.assertEqual(action["Gauss_Bonnet"], "EXCLUDED_FROM_THIS_CONTRACT")
        self.assertIn("exact U(phi)", self.contract["model_freeze_closure_matrix"]["MF-001"]["open"])
        self.assertIn("exact Z_F(phi)", self.contract["model_freeze_closure_matrix"]["MF-001"]["open"])

    def test_bulk_equations_and_constraint_have_conditional_status(self) -> None:
        equations = self.contract["regularized_bulk_equations"]
        self.assertEqual(equations["status"], "DERIVED_GENERIC_NOT_MODEL_CLOSED")
        self.assertIn("4 A_s''", equations["E_A"])
        self.assertIn("L_s phi_s''", equations["E_phi"])
        self.assertEqual(self.contract["radial_constraint"]["dependency_proof"], "OPEN")

    def test_pole_and_junction_regressions_close(self) -> None:
        for residual in self.result["pole_coefficient_regression"].values():
            self.assertLessEqual(abs(residual), 1.0e-12)
        self.assertLessEqual(abs(self.result["junction_identity_residual"]), 1.0e-12)

    def test_operator_theorems_remain_blocked(self) -> None:
        operator = self.contract["continuum_operator_scaffold"]
        self.assertEqual(operator["Freholm_status"], "NOT_PROVEN")
        self.assertEqual(operator["continuum_Jacobian"], "NOT_CONSTRUCTED")
        self.assertEqual(operator["implicit_function_theorem"], "NOT_ADMISSIBLE")
        self.assertTrue(operator["square_count"].startswith("OPEN_"))

    def test_release_gates_are_immutable(self) -> None:
        gates = self.result["gate_state"]
        self.assertEqual(gates["R1.1"], "BLOCKED")
        self.assertEqual(gates["R1.2"], "BLOCKED")
        self.assertEqual(gates["official_MD2S_solver"], "NOT_AUTHORIZED")
        self.assertEqual(gates["K1-D"], "NOT_RELEASED")
        self.assertEqual(gates["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(gates["physical_evidence_effect"], "NONE")

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
            "MD2S_R1_C_PHYS_PARENT_ACTION_OPERATOR_ENTRY_V0_1",
        )


if __name__ == "__main__":
    unittest.main()
