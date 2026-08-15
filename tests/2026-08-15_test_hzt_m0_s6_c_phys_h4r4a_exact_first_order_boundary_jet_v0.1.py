#!/usr/bin/env python3
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools" / "2026-08-15_validate_hzt_m0_s6_c_phys_h4r4a_exact_first_order_boundary_jet_v0.1.py"
REGISTRY = ROOT / "registry" / "2026-08-15_HZT-M0_S6_C-PHYS_H4R4A_ExactFirstOrder_BoundaryJet_TheoremReview_v0.1.json"

spec = importlib.util.spec_from_file_location("h4r4a_validator", VALIDATOR)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class H4R4AContractTests(unittest.TestCase):
    def test_registry_contract(self):
        mod.check_registry(REGISTRY)

    def test_exact_bulk_source_matches_independent_euler_lagrange_reconstruction(self):
        mod.check_bulk_euler_lagrange()

    def test_boundary_principal_flux_and_rank(self):
        mod.check_boundary_principal_flux()

    def test_boundary_first_time_jet_chain_rule(self):
        mod.check_boundary_first_jet()

    def test_no_physical_or_gate_promotion(self):
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertFalse(data["solver_execution"])
        self.assertFalse(data["mms_execution"])
        self.assertFalse(data["gate_disposition"]["physical_parent_solve_authorized"])
        self.assertEqual(data["gate_disposition"]["D2NQ_parent_dynamic_selection"], "OPEN_NOT_EXECUTED")
        self.assertEqual(data["gate_disposition"]["full_ghost_freedom"], "OPEN")
        self.assertEqual(data["gate_disposition"]["K1-D"], "NOT_RELEASED")
        self.assertEqual(data["gate_disposition"]["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(data["gate_disposition"]["WP4"], "BLOCKED")
        self.assertEqual(data["physical_evidence_effect"], "NONE")

    def test_one_time_and_gemini_firewall(self):
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(data["canonical_signature"]["ambient_signature"], "(-,+,+,+,+,+)")
        self.assertEqual(data["canonical_signature"]["physical_times"], 1)
        fw = data["external_material_firewall"]
        self.assertEqual(fw["gemini_blocks"], "EXTERNAL_UNVERIFIED_GEMINI_DRAFT")
        self.assertFalse(fw["gemini_equations_used_as_premises"])
        self.assertFalse(fw["gemini_code_used_as_validation"])
        self.assertFalse(fw["two_time_signature_imported"])

    def test_theorem_scope_remains_reduced_and_conditional(self):
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        decision = data["theorem_review"]["decision"]
        self.assertIn("REDUCED_LOCAL_IBVP", decision)
        self.assertIn("CONDITIONALLY", decision)
        self.assertEqual(data["gate_disposition"]["full_parent_global_background_existence"], "OPEN_NOT_EXECUTED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
