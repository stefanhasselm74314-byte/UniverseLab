#!/usr/bin/env python3
"""Regression tests for M1 Operator-2B function spaces and trace template."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_verify_hzt_m0_s6_c_phys_m1_operator_2b_v0.1.py"
CONTRACT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceContract_v0.1.json"

SPEC = importlib.util.spec_from_file_location("m1_operator_2b", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import Operator-2B verifier")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class M1Operator2BTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.result = MODULE.validate()

    def test_fixed_domain_chart(self) -> None:
        coordinates = self.contract["fixed_domain_coordinates"]
        self.assertEqual(coordinates["fixed_coordinate"], "y in [0,1]")
        self.assertEqual(coordinates["pole_regular_coordinate"], "tau=y^2 in [0,1]")
        self.assertEqual(
            coordinates["derivative_rule"],
            "d/dx_s=(2*sqrt(tau)/rho_s)*d/dtau",
        )

    def test_affine_chart_encodes_pole_conditions(self) -> None:
        chart = self.contract["pole_regular_affine_chart"]
        expected = {
            "A_N(0)=0",
            "A_s_x(0)=0",
            "ell_s(0)=0",
            "ell_s_x(0)=1",
            "varphi_s_x(0)=0",
            "a_chi_s(0)=0",
        }
        self.assertEqual(set(chart["automatic_pole_conditions"]), expected)

    def test_little_holder_spaces_and_dense_core(self) -> None:
        spaces = self.contract["little_holder_spaces"]
        self.assertEqual(
            spaces["regional_profile_domain"],
            "X_s=h^{2,alpha_H}^3 x h^{1,alpha_H}",
        )
        self.assertEqual(spaces["regional_bulk_target"], "Y_s=h^{0,alpha_H}^4")
        self.assertIn("densely embedded", spaces["dense_embedding"])
        self.assertIn("closure of C-infinity", spaces["definition"])

    def test_augmented_parameter_count_remains_eight(self) -> None:
        parameters = self.contract["augmented_parameter_space"]
        self.assertEqual(parameters["dimension"], 8)
        self.assertEqual(len(parameters["continuous_vector_order"]), 8)
        self.assertIn("not promoted", parameters["model_shape_parameters"])

    def test_regularized_bulk_target_has_no_negative_tau_powers(self) -> None:
        bulk = self.contract["regularized_bulk_operator"]
        self.assertFalse(bulk["negative_tau_powers_after_regularization"])
        self.assertEqual(bulk["target"], "F_bulk:U_adm->Y_bulk")
        self.assertIn("C-infinity", bulk["smoothness"])

    def test_cap_trace_dimensions(self) -> None:
        trace = self.contract["cap_trace_operator"]
        self.assertEqual(trace["regional_trace_dimension"], 7)
        self.assertEqual(trace["combined_profile_trace_dimension"], 14)
        self.assertIn("continuous", trace["continuity"])

    def test_linearized_boundary_template_is_not_a_rank_result(self) -> None:
        trace = self.contract["linearized_boundary_trace_template"]
        self.assertEqual(trace["matrix_shape"], "8 x 22")
        self.assertFalse(trace["numeric_matrix_constructed"])
        self.assertEqual(trace["rank_claim"], "NOT_ADMISSIBLE_WITHOUT_W_star")

    def test_bounded_closed_graph_is_not_fredholm(self) -> None:
        linearized = self.contract["linearized_operator_template"]
        self.assertIn("bounded linear map", linearized["boundedness"])
        self.assertEqual(linearized["Fredholm_property"], "NOT_PROVEN")
        self.assertEqual(linearized["kernel"], "NOT_COMPUTED")
        self.assertEqual(linearized["cokernel"], "NOT_COMPUTED")

    def test_future_kernel_protocol_is_not_executed(self) -> None:
        protocol = self.contract["future_kernel_cokernel_protocol"]
        self.assertEqual(protocol["current_execution"], "NOT_EXECUTED")
        self.assertIn("two independent discretizations", protocol["kernel_test"])
        self.assertIn("adjoint", protocol["cokernel_test"].lower())

    def test_release_gates_remain_closed(self) -> None:
        gate = self.contract["gate_state"]
        self.assertEqual(gate["R1.1"], "BLOCKED")
        self.assertEqual(gate["R1.2"], "BLOCKED")
        self.assertEqual(gate["full_linearized_boundary_trace_rank"], "NOT_PROVEN")
        self.assertEqual(gate["Fredholm_property"], "NOT_PROVEN")
        self.assertEqual(gate["continuum_BVP_Jacobian"], "NOT_PROVEN")
        self.assertEqual(gate["physical_background"], "NOT_ESTABLISHED")
        self.assertEqual(gate["official_MD2S_solver"], "NOT_AUTHORIZED")
        self.assertEqual(gate["K1-D"], "NOT_RELEASED")
        self.assertEqual(gate["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(gate["physical_evidence_effect"], "NONE")

    def test_symbolic_verifier_passes(self) -> None:
        self.assertEqual(self.result["status"], "PASS_FORMAL")
        self.assertEqual(
            self.result["chart_derivatives"]["status"],
            "PASS_EXACT_SYMBOLIC",
        )
        self.assertEqual(
            self.result["endpoint_traces"]["status"],
            "PASS_EXACT_SYMBOLIC",
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
        self.assertEqual(payload["status"], "PASS_FORMAL")
        self.assertEqual(
            payload["contract"],
            "C_PHYS_M1_OPERATOR_2B_FUNCTION_SPACE_TRACE",
        )


if __name__ == "__main__":
    unittest.main()
