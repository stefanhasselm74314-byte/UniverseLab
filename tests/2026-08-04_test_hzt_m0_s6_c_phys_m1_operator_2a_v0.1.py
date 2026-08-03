#!/usr/bin/env python3
"""Regression tests for HZT-M0-S6-C-PHYS-M1 Operator-2A."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_verify_hzt_m0_s6_c_phys_m1_operator_2a_v0.1.py"
CONTRACT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2AContract_v0.1.json"

SPEC = importlib.util.spec_from_file_location("c_phys_m1_operator_2a", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import Operator-2A verifier")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class Operator2ATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_constraint_identity(self) -> None:
        result = MODULE.derive_constraint_identity()
        self.assertEqual(
            result["off_shell_identity"],
            "C_x+4*A_x*C=ell_x*E_A+4*A_x*E_ell-varphi_x*E_varphi",
        )
        self.assertEqual(result["on_shell_propagation"], "C_x=-4*A_x*C")

    def test_pole_series_exactly_closes(self) -> None:
        result = MODULE.verify_pole_series()
        self.assertEqual(
            result["series_order"],
            "A,varphi,a_chi through x^4; ell through x^5",
        )
        self.assertIn("aF", result["f4"])
        self.assertIn("a4", result["l5"])

    def test_principal_matrix(self) -> None:
        result = MODULE.verify_principal_matrix()
        self.assertEqual(result["determinant"], "4*ell")
        self.assertEqual(result["interior_status"], "FULL_RANK_FOR_ELL_POSITIVE")
        self.assertEqual(result["complementing_boundary_status"], "NOT_PROVEN")

    def test_contract_status_is_formal_only(self) -> None:
        self.assertEqual(
            self.contract["status"],
            "DIFFERENTIAL_OPERATOR_AND_CONSTRAINT_PROPAGATION_CLOSED_BOUNDARY_TRACE_INVERTIBILITY_OPEN",
        )
        self.assertEqual(
            self.contract["operator_status"]["continuum_operator"],
            "SPECIALIZED_FORMAL_OPERATOR_DEFINED",
        )
        self.assertEqual(
            self.contract["operator_status"]["Fredholm_property"],
            "NOT_PROVEN",
        )
        self.assertEqual(
            self.contract["boundary_operator_audit"]["linearized_trace_map_constructed"],
            False,
        )

    def test_constraint_is_not_double_counted(self) -> None:
        self.assertEqual(
            self.contract["radial_constraint"]["BVP_role"],
            "PROPAGATED_QA_CHANNEL_NOT_ADDITIONAL_ENDPOINT_RESIDUAL",
        )
        self.assertEqual(
            len(self.contract["boundary_operator_audit"]["independent_cap_residuals"]),
            8,
        )

    def test_release_gates_remain_closed(self) -> None:
        gates = self.contract["gate_state"]
        self.assertEqual(gates["R1.1"], "BLOCKED")
        self.assertEqual(gates["R1.2"], "BLOCKED")
        self.assertEqual(gates["continuum_BVP_Jacobian"], "NOT_PROVEN")
        self.assertEqual(gates["physical_background"], "NOT_ESTABLISHED")
        self.assertEqual(gates["official_MD2S_solver"], "NOT_AUTHORIZED")
        self.assertEqual(gates["K1-D"], "NOT_RELEASED")
        self.assertEqual(gates["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(gates["physical_evidence_effect"], "NONE")

    def test_cli_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TOOL)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "PASS_FORMAL")
        self.assertEqual(payload["contract"], "C_PHYS_M1_OPERATOR_2A_SYMBOLIC_QA")


if __name__ == "__main__":
    unittest.main()
