#!/usr/bin/env python3
"""Regression and fail-closed tests for the MD-2S C1 BVP preflight."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/2026-08-03_validate_md2s_c1_bvp_preflight_v0.1.py"
SPEC = importlib.util.spec_from_file_location("md2s_c1_preflight", MODULE_PATH)
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class C1BVPPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = json.loads((ROOT / MOD.MODEL_PATH).read_text(encoding="utf-8"))
        self.preflight = json.loads((ROOT / MOD.PREFLIGHT_PATH).read_text(encoding="utf-8"))

    def test_repository_contract_passes(self) -> None:
        result = MOD.validate_repository(ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["model_id"], "HZT-M0-S6-C1")
        self.assertEqual(result["unknown_count"], 8)
        self.assertEqual(result["residual_count"], 8)
        self.assertEqual(result["maximum_structural_matching"], 8)
        self.assertFalse(result["solver_authorized"])

    def test_model_definition_is_candidate_not_historical_identity(self) -> None:
        MOD.validate_model(self.model)
        self.assertEqual(self.model["historical_A0_identity"], "NOT_CLAIMED")
        self.assertEqual(self.model["governance"]["R1.1"], "BLOCKED")
        self.assertEqual(self.model["governance"]["K1-D"], "NOT_RELEASED")
        self.assertEqual(self.model["governance"]["K1-E"], "NOT_ADMISSIBLE")

    def test_square_count_is_eight_by_eight(self) -> None:
        summary = MOD.validate_preflight(self.preflight)
        self.assertEqual(summary["unknown_count"], 8)
        self.assertEqual(summary["residual_count"], 8)
        self.assertEqual(summary["maximum_structural_matching"], 8)

    def test_declared_matching_is_perfect(self) -> None:
        edges = self.preflight["structural_dependency_edges"]
        size, matching = MOD.maximum_matching(edges)
        self.assertEqual(size, 8)
        self.assertEqual(len(matching), 8)

    def test_fixed_k4_variant_is_codimension_one(self) -> None:
        fixed = self.preflight["fixed_K4_variant"]
        self.assertEqual(fixed["continuous_unknown_count"], 7)
        self.assertEqual(fixed["residual_count"], 8)
        self.assertEqual(fixed["generic_codimension"], 1)

    def test_scalar_shift_risk_is_detected(self) -> None:
        self.assertTrue(MOD.scalar_shift_risk(m_phi_sq=0.0, lambda1=0.0))
        self.assertFalse(MOD.scalar_shift_risk(m_phi_sq=1.0, lambda1=0.0))
        self.assertFalse(MOD.scalar_shift_risk(m_phi_sq=0.0, lambda1=1.0))

    def test_negative_scalar_mass_parameter_fails_closed(self) -> None:
        with self.assertRaises(MOD.ContractError):
            MOD.scalar_shift_risk(m_phi_sq=-1.0, lambda1=0.0)

    def test_missing_dependency_edge_breaks_declared_matching(self) -> None:
        broken = copy.deepcopy(self.preflight)
        broken["structural_dependency_edges"]["R_A"].remove("A_S_0")
        with self.assertRaises(MOD.ContractError):
            MOD.validate_preflight(broken)

    def test_duplicate_unknown_fails_closed(self) -> None:
        broken = copy.deepcopy(self.preflight)
        broken["continuous_unknowns_square_bvp"][-1] = "rho_S"
        with self.assertRaises(MOD.ContractError):
            MOD.validate_preflight(broken)

    def test_solver_gate_cannot_be_promoted(self) -> None:
        broken = copy.deepcopy(self.preflight)
        broken["solver_authorized"] = True
        with self.assertRaises(MOD.ContractError):
            MOD.validate_preflight(broken)

    def test_global_flux_is_not_double_counted(self) -> None:
        text = self.preflight["not_counted_as_independent_boundary_residuals"]["global_flux"]
        self.assertIn("encoded once", text)
        residual_ids = [item["id"] for item in self.preflight["independent_residuals"]]
        self.assertNotIn("R_flux", residual_ids)


if __name__ == "__main__":
    unittest.main(verbosity=2)
