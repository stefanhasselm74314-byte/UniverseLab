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
BASE_TOOL = ROOT / "tools/2026-08-04_verify_hzt_m0_s6_c_phys_m1_operator_2a_v0.1.py"
TRACE_TOOL = ROOT / "tools/2026-08-04_verify_hzt_m0_s6_c_phys_m1_operator_2a_trace_v0.1.py"
CONTRACT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2AContract_v0.1.json"
PREFLIGHT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2ARegularityTracePreflight_v0.1.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module("m1_operator_2a_base_tests", BASE_TOOL)
TRACE = load_module("m1_operator_2a_trace_tests", TRACE_TOOL)


class M1Operator2ATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
        cls.trace_result = TRACE.validate()

    def test_constraint_identity_is_exact(self) -> None:
        result = BASE.derive_constraint_identity()
        self.assertEqual(
            result["off_shell_identity"],
            "C_x+4*A_x*C=ell_x*E_A+4*A_x*E_ell-varphi_x*E_varphi",
        )
        self.assertEqual(result["on_shell_propagation"], "C_x=-4*A_x*C")

    def test_higher_pole_series_symbolically_closes(self) -> None:
        result = BASE.verify_pole_series()
        self.assertEqual(
            result["series_order"],
            "A,varphi,a_chi through x^4; ell through x^5",
        )
        self.assertIn("a2", result["a4"])
        self.assertIn("f2", result["f4"])
        self.assertIn("l3", result["l5"])

    def test_interior_principal_matrix(self) -> None:
        result = BASE.verify_principal_matrix()
        self.assertEqual(result["determinant"], "4*ell")
        self.assertEqual(result["interior_status"], "FULL_RANK_FOR_ELL_POSITIVE")
        self.assertEqual(result["complementing_boundary_status"], "NOT_PROVEN")

    def test_pole_local_invariants_are_finite(self) -> None:
        result = TRACE.verify_pole_invariant_expansions()
        self.assertEqual(result["status"], "PASS_FORMAL_FINITE_LOCAL_BUILDING_BLOCKS")
        self.assertEqual(result["internal_gaussian_curvature_limit"], "-6*l3")
        self.assertNotIn("zoo", " ".join(result.values()))

    def test_cap_principal_transmission_is_conditionally_full_rank(self) -> None:
        result = TRACE.verify_cap_principal_transmission()
        self.assertEqual(result["metric_derivative_determinant"], "-4/ell_cap")
        self.assertEqual(result["metric_status"], "FULL_RANK_FOR_ELL_CAP_POSITIVE")
        self.assertEqual(result["full_augmented_trace_status"], "NOT_CONSTRUCTED")
        self.assertEqual(result["Fredholm_status"], "NOT_PROVEN")

    def test_gauge_profile_and_augmented_residual_roles_are_separate(self) -> None:
        gauge = self.preflight["gauge_profile_closure"]
        self.assertEqual(
            gauge["profile_principal_status"],
            "CLOSED_BY_REGULAR_POLE_GAUGES_ONCE_q_N_AND_q_S_ARE_FIXED",
        )
        self.assertIn("AUGMENTED_RESIDUAL", gauge["cap_patch_residual_role"])
        self.assertTrue(gauge["double_counting_forbidden"])

    def test_full_trace_and_fredholm_claims_remain_open(self) -> None:
        gate = self.preflight["gate_state"]
        self.assertEqual(gate["full_linearized_boundary_trace"], "NOT_CONSTRUCTED")
        self.assertEqual(
            gate["complementing_boundary_condition"],
            "NOT_PROVEN_FOR_FULL_AUGMENTED_OPERATOR",
        )
        self.assertEqual(gate["Fredholm_property"], "NOT_PROVEN")
        self.assertEqual(gate["continuum_BVP_Jacobian"], "NOT_PROVEN")

    def test_constraint_is_not_double_counted(self) -> None:
        self.assertEqual(
            self.contract["radial_constraint"]["BVP_role"],
            "PROPAGATED_QA_CHANNEL_NOT_ADDITIONAL_ENDPOINT_RESIDUAL",
        )
        self.assertEqual(
            len(self.contract["boundary_operator_audit"]["independent_cap_residuals"]),
            8,
        )

    def test_release_firewalls_remain_closed(self) -> None:
        gate = self.contract["gate_state"]
        self.assertEqual(gate["R1.1"], "BLOCKED")
        self.assertEqual(gate["R1.2"], "BLOCKED")
        self.assertEqual(gate["official_MD2S_solver"], "NOT_AUTHORIZED")
        self.assertEqual(gate["K1-D"], "NOT_RELEASED")
        self.assertEqual(gate["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(gate["physical_evidence_effect"], "NONE")

    def test_base_cli_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(BASE_TOOL)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "PASS_FORMAL")
        self.assertEqual(payload["contract"], "C_PHYS_M1_OPERATOR_2A_SYMBOLIC_QA")

    def test_trace_cli_returns_machine_readable_pass(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TRACE_TOOL), "--json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "PASS_FORMAL")
        self.assertEqual(
            payload["contract"],
            "C_PHYS_M1_OPERATOR_2A_REGULARITY_TRACE_QA",
        )


if __name__ == "__main__":
    unittest.main()
