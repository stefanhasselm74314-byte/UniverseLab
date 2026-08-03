#!/usr/bin/env python3
"""Regression tests for the C-PHYS-M1 function-freeze canonical state."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-03_validate_g0_three_track_sync_v1.4.py"

SPEC = importlib.util.spec_from_file_location("g0_three_track_validator_v1_4", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import G0 v1.4 validator")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CPhysM1CanonicalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.validate()
        cls.manifest = json.loads((ROOT / "project-manifest.json").read_text(encoding="utf-8"))
        cls.checkpoint = json.loads((ROOT / "registry/session-checkpoint-latest.json").read_text(encoding="utf-8"))
        cls.contract = json.loads((ROOT / "registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json").read_text(encoding="utf-8"))
        cls.status = json.loads((ROOT / "registry/2026-08-03_UniverseLab_C_PHYS_M1_FunctionFreezeStatus_v0.1.json").read_text(encoding="utf-8"))

    def test_m1_identity_and_classification(self) -> None:
        self.assertEqual(self.contract["model_id"], "HZT-M0-S6-C-PHYS-M1")
        self.assertEqual(
            self.contract["classification"],
            "VERSIONED_PHYSICAL_CANDIDATE_MODEL_SELECTION_NOT_DERIVATION",
        )
        self.assertEqual(self.status["evidence_effect"], "MODEL_DEFINITION_ONLY")
        self.assertEqual(self.status["physical_evidence_effect"], "NONE")

    def test_exact_functions_are_frozen(self) -> None:
        functions = self.contract["exact_functions"]
        self.assertEqual(functions["U"]["formula"], "U(phi)=0.5*mhat_phi_sq*M6^6*varphi^2")
        self.assertEqual(functions["Z_F"]["formula"], "Z_F(phi)=exp(-2*a_F*varphi)")
        self.assertEqual(functions["lambda"]["formula"], "lambda(phi)=lambda_hat*M6^5")
        self.assertEqual(functions["Z_sigma"]["formula"], "Z_sigma(phi)=z_sigma_hat*M6^3")
        self.assertEqual(self.manifest["c_phys_operator_entry"]["open_model_freeze_items"], [])

    def test_information_budget_is_six(self) -> None:
        vector = self.contract["dimensionless_model_parameter_vector"]
        self.assertEqual(vector["count"], 6)
        self.assertEqual(
            vector["ordered_parameters"],
            ["Lambda_hat", "mhat_phi_sq", "a_F", "lambda_hat", "z_sigma_hat", "q_hat"],
        )
        self.assertFalse(vector["silent_promotion_to_shooting_variables"])

    def test_track_firewall_is_intact(self) -> None:
        firewall = self.contract["track_firewall"]
        self.assertFalse(firewall["C1_V_parameter_values_migrated"])
        self.assertFalse(firewall["C1_V_numerical_results_used"])
        self.assertEqual(firewall["historical_A0_identity"], "NOT_CLAIMED")
        self.assertEqual(firewall["C1_V_identity"], "NOT_CLAIMED")

    def test_operator_2a_is_primary_next_block(self) -> None:
        workstreams = {item["track_id"]: item for item in self.checkpoint["current_workstreams"]}
        primary = workstreams["MD2S-R1-C-PHYS"]
        self.assertEqual(primary["model_id"], "HZT-M0-S6-C-PHYS-M1")
        self.assertEqual(primary["next_block"], "C-PHYS-R1.0-OPERATOR-2A")
        self.assertEqual(workstreams["HZT-M0-S6-C1-V"]["priority"], "PARALLEL_DIAGNOSTIC_ONLY")

    def test_model_definition_does_not_claim_solution(self) -> None:
        gates = self.manifest["gates"]
        self.assertEqual(gates["FUNCTION_SELECTION"], "PASS_POSTULATED_MODEL_FAMILY")
        self.assertEqual(gates["PHYSICAL_BACKGROUND"], "NOT_ESTABLISHED")
        self.assertEqual(gates["CONTINUUM_BVP_OPERATOR"], "SCAFFOLD_ONLY")
        self.assertEqual(gates["CONTINUUM_BVP_JACOBIAN"], "NOT_PROVEN")

    def test_release_gates_remain_closed(self) -> None:
        gates = self.manifest["gates"]
        self.assertEqual(gates["R1.1"], "BLOCKED")
        self.assertEqual(gates["R1.2"], "BLOCKED")
        self.assertEqual(gates["official_MD2S_solver"], "NOT_AUTHORIZED")
        self.assertEqual(gates["K1-D"], "NOT_RELEASED")
        self.assertEqual(gates["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(gates["physical_evidence_effect"], "NONE")

    def test_checkpoint_alias_matches_v1_11(self) -> None:
        dated = json.loads((ROOT / "registry/2026-08-03_UniverseLab_SessionCheckpoint_v1.11.json").read_text(encoding="utf-8"))
        self.assertEqual(self.checkpoint, dated)
        self.assertEqual(self.checkpoint["checkpoint_id"], "UL-CHK-20260803-011")

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
        self.assertEqual(payload["contract"], "G0_THREE_TRACK_SYNCHRONIZATION")


if __name__ == "__main__":
    unittest.main()
