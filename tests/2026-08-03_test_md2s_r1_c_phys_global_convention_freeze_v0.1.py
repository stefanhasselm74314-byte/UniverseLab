#!/usr/bin/env python3
"""Regression tests for C-PHYS global convention freeze v0.1."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-03_validate_md2s_r1_c_phys_global_convention_freeze_v0.1.py"
CONTRACT = ROOT / "registry/2026-08-03_MD2S_R1_C_PHYS_GlobalConventionFreezeContract_v0.1.json"

SPEC = importlib.util.spec_from_file_location("c_phys_global_freeze", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import global convention validator")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class GlobalConventionFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.validate()
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_orientation_types_are_distinct(self) -> None:
        orientation = self.contract["regional_coordinates_and_orientations"]
        self.assertEqual(
            orientation["outward_boundary_normals_in_local_coordinates"],
            {"n_N^r": 1, "n_S^r": 1},
        )
        self.assertEqual(
            orientation["global_two_form_orientation_signs"],
            {"epsilon_N": 1, "epsilon_S": -1},
        )

    def test_flux_and_patch_are_equivalent(self) -> None:
        regression = self.result["flux_patch_regression"]
        self.assertLessEqual(abs(regression["flux_residual"]), 1.0e-12)
        self.assertLessEqual(abs(regression["patch_residual"]), 1.0e-12)
        self.assertIn(
            "R_flux",
            self.contract["not_additional_independent_residuals"],
        )

    def test_charge_identity_is_not_assumed(self) -> None:
        lattice = self.contract["charge_lattice"]
        self.assertEqual(lattice["cap_charge"], "q_sigma=m_sigma*q_ref")
        self.assertEqual(lattice["q_ref_equals_q_sigma"], "ONLY_IF_m_sigma_EQUALS_1")
        self.assertEqual(lattice["m_sigma_domain"], "positive_integer")

    def test_frame_removes_only_one_warp_constant(self) -> None:
        frame = self.contract["four_dimensional_frame"]
        self.assertEqual(frame["condition"], "A_N(0)=0")
        self.assertEqual(frame["A_S(0)"], "CONTINUOUS_SHOOTING_UNKNOWN")
        self.assertTrue(frame["must_not_also_fix_A_S_0"])

    def test_square_count_is_conditional(self) -> None:
        count = self.contract["structural_BVP_count"]
        self.assertEqual(count["continuous_unknowns"], 8)
        self.assertEqual(count["independent_boundary_residuals"], 8)
        self.assertEqual(
            count["status"],
            "SQUARE_COUNT_STRUCTURALLY_CLOSED_CONDITIONAL_ON_FUNCTION_FREEZE",
        )

    def test_exact_functions_remain_open(self) -> None:
        function_class = self.contract["admissible_function_class"]
        self.assertEqual(
            function_class["exact_forms"],
            "OPEN_REQUIRES_VERSIONED_MODEL_SELECTION",
        )
        self.assertFalse(self.contract["track_firewall"]["C1_V_functional_forms_migrated"])

    def test_release_gates_remain_closed(self) -> None:
        gates = self.result["gate_state"]
        self.assertEqual(gates["R1.1"], "BLOCKED")
        self.assertEqual(gates["R1.2"], "BLOCKED")
        self.assertEqual(gates["official_MD2S_solver"], "NOT_AUTHORIZED")
        self.assertEqual(gates["K1-D"], "NOT_RELEASED")
        self.assertEqual(gates["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(gates["physical_evidence_effect"], "NONE")

    def test_cli_passes(self) -> None:
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
            "MD2S_R1_C_PHYS_GLOBAL_CONVENTION_FREEZE_V0_1",
        )


if __name__ == "__main__":
    unittest.main()
