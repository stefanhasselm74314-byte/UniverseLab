#!/usr/bin/env python3
"""Regression tests for HZT-M0-S6-C-PHYS-M1 Freeze-1B."""

from __future__ import annotations

import copy
import importlib.util
import math
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "2026-08-03_validate_hzt_m0_s6_c_phys_m1_function_freeze_v0.1.py"

spec = importlib.util.spec_from_file_location("c_phys_m1_freeze_validator", TOOL)
if spec is None or spec.loader is None:
    raise RuntimeError("unable to import C-PHYS-M1 function-freeze validator")
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)


class CPhysM1FunctionFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = validator.load_contract(ROOT)

    def issue_categories(self, data: dict) -> set[str]:
        return {issue.category for issue in validator.validate_contract(data, ROOT)}

    def test_repository_contract_passes(self) -> None:
        self.assertEqual(validator.validate_repository(ROOT), [])

    def test_exact_function_family(self) -> None:
        functions = self.contract["exact_functions"]
        self.assertEqual(functions["U"]["formula"], "U(phi)=0.5*mhat_phi_sq*M6^6*varphi^2")
        self.assertEqual(functions["Z_F"]["formula"], "Z_F(phi)=exp(-2*a_F*varphi)")
        self.assertEqual(functions["lambda"]["formula"], "lambda(phi)=lambda_hat*M6^5")
        self.assertEqual(functions["Z_sigma"]["formula"], "Z_sigma(phi)=z_sigma_hat*M6^3")

    def test_valid_parameter_point(self) -> None:
        self.assertEqual(
            validator.validate_parameter_point(
                lambda_hat=-0.4,
                lambda6_hat=0.1,
                mhat_phi_sq=3.0,
                a_f=0.25,
                z_sigma_hat=1.2,
                q_hat=0.8,
            ),
            [],
        )

    def test_nonpositive_mass_is_rejected(self) -> None:
        issues = validator.validate_parameter_point(
            lambda_hat=0.0,
            lambda6_hat=0.0,
            mhat_phi_sq=0.0,
            a_f=0.2,
            z_sigma_hat=1.0,
            q_hat=1.0,
        )
        self.assertIn("DOMAIN", {item.category for item in issues})

    def test_zero_active_flux_slope_is_rejected(self) -> None:
        issues = validator.validate_parameter_point(
            lambda_hat=0.0,
            lambda6_hat=0.0,
            mhat_phi_sq=1.0,
            a_f=0.0,
            z_sigma_hat=1.0,
            q_hat=1.0,
        )
        self.assertIn("DOMAIN", {item.category for item in issues})

    def test_nonpositive_winding_coefficient_is_rejected(self) -> None:
        issues = validator.validate_parameter_point(
            lambda_hat=0.0,
            lambda6_hat=0.0,
            mhat_phi_sq=1.0,
            a_f=0.2,
            z_sigma_hat=-1.0,
            q_hat=1.0,
        )
        self.assertIn("DOMAIN", {item.category for item in issues})

    def test_nonpositive_charge_unit_is_rejected(self) -> None:
        issues = validator.validate_parameter_point(
            lambda_hat=0.0,
            lambda6_hat=0.0,
            mhat_phi_sq=1.0,
            a_f=0.2,
            z_sigma_hat=1.0,
            q_hat=0.0,
        )
        self.assertIn("DOMAIN", {item.category for item in issues})

    def test_hidden_bulk_constant_is_rejected(self) -> None:
        bad = copy.deepcopy(self.contract)
        bad["exact_functions"]["U"]["formula"] = "U(phi)=U0+0.5*mhat_phi_sq*M6^6*varphi^2"
        self.assertIn("MODEL", self.issue_categories(bad))

    def test_c1_parameter_migration_is_rejected(self) -> None:
        bad = copy.deepcopy(self.contract)
        bad["track_firewall"]["C1_V_parameter_values_migrated"] = True
        self.assertIn("FIREWALL", self.issue_categories(bad))

    def test_local_scalar_source_reintroduction_is_rejected(self) -> None:
        bad = copy.deepcopy(self.contract)
        bad["exact_functions"]["lambda"]["derivatives"]["d_lambda_dphi"] = "lambda1"
        self.assertIn("MODEL", self.issue_categories(bad))

    def test_parameter_budget_expansion_is_rejected(self) -> None:
        bad = copy.deepcopy(self.contract)
        bad["dimensionless_model_parameter_vector"]["ordered_parameters"].append("alpha_lambda")
        bad["dimensionless_model_parameter_vector"]["count"] = 7
        self.assertIn("P0", self.issue_categories(bad))

    def test_release_gate_opening_is_rejected(self) -> None:
        bad = copy.deepcopy(self.contract)
        bad["gate_state"]["R1.1"] = "ACTIVE"
        bad["gate_state"]["K1-D"] = "RELEASED"
        categories = self.issue_categories(bad)
        self.assertIn("GATE", categories)

    def test_potential_and_gauge_kinetic_properties(self) -> None:
        m2 = 2.5
        a_f = 0.4
        samples = [-5.0, -2.0, 0.0, 2.0, 5.0]
        for value in samples:
            self.assertGreaterEqual(validator.u(value, m2), 0.0)
            self.assertGreater(validator.z_f(value, a_f), 0.0)
        self.assertEqual(validator.u(0.0, m2), 0.0)
        self.assertEqual(validator.z_f(0.0, a_f), 1.0)

    def test_flux_density_matches_inverse_zf(self) -> None:
        q_s = 0.7
        warp = -0.1
        varphi = 0.3
        a_f = 0.2
        expected = 0.5 * q_s * q_s * math.exp(-8.0 * warp) / validator.z_f(varphi, a_f)
        self.assertAlmostEqual(validator.rho_f(q_s, warp, varphi, a_f), expected, places=14)

    def test_model_and_control_are_distinct(self) -> None:
        controls = self.contract["nested_control_limits"]
        self.assertEqual(
            controls["a_F_to_zero"]["classification"],
            "DECLARED_DECOUPLING_CONTROL_NOT_ACTIVE_C_PHYS_M1",
        )
        self.assertTrue(controls["a_F_to_zero"]["does_not_establish_C1_V_identity"])

    def test_next_block_is_operator_2a(self) -> None:
        self.assertEqual(self.contract["next_block"]["id"], "C-PHYS-R1.0-OPERATOR-2A")


if __name__ == "__main__":
    unittest.main()
