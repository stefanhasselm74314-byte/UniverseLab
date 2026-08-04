#!/usr/bin/env python3
"""Regression tests for the canonical three-track state through Operator-2B."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_validate_g0_three_track_sync_v1.6.py"

SPEC = importlib.util.spec_from_file_location("g0_sync_v1_6", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import G0 v1.6 validator")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class G0Operator2BSynchronizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.validate()
        cls.manifest = json.loads((ROOT / "project-manifest.json").read_text(encoding="utf-8"))
        cls.checkpoint = json.loads(
            (ROOT / "registry/session-checkpoint-latest.json").read_text(encoding="utf-8")
        )
        cls.contract = json.loads(
            (
                ROOT
                / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceContract_v0.1.json"
            ).read_text(encoding="utf-8")
        )

    def test_three_tracks_remain_exact(self) -> None:
        self.assertEqual(
            self.result["tracks"],
            ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"],
        )

    def test_manifest_release_and_active_model(self) -> None:
        self.assertEqual(
            self.manifest["release"],
            "2.7-c-phys-m1-operator-2b-v0.1",
        )
        physical = self.manifest["architecture"]["research_tracks"][1]
        self.assertEqual(physical["active_model"], "HZT-M0-S6-C-PHYS-M1")

    def test_operator_2a_results_are_preserved(self) -> None:
        gates = self.manifest["gates"]
        self.assertEqual(gates["OPERATOR_2A"], "PASS_FORMAL_OPERATOR_STRUCTURE")
        self.assertEqual(
            self.manifest["c_phys_operator_entry"]["constraint_dependency_proof"],
            "PROVEN_SYMBOLIC_CONDITIONAL",
        )

    def test_operator_2b_spaces_are_frozen(self) -> None:
        spaces = self.contract["little_holder_spaces"]
        self.assertEqual(
            spaces["regional_profile_domain"],
            "X_s=h^{2,alpha_H}^3 x h^{1,alpha_H}",
        )
        self.assertEqual(spaces["regional_bulk_target"], "Y_s=h^{0,alpha_H}^4")
        self.assertEqual(self.manifest["gates"]["WEIGHTED_FUNCTION_SPACES"], "FROZEN")

    def test_trace_template_is_not_rank(self) -> None:
        trace = self.contract["linearized_boundary_trace_template"]
        self.assertEqual(trace["matrix_shape"], "8 x 22")
        self.assertFalse(trace["numeric_matrix_constructed"])
        self.assertEqual(trace["rank_claim"], "NOT_ADMISSIBLE_WITHOUT_W_star")
        self.assertEqual(
            self.manifest["gates"]["FULL_LINEARIZED_BOUNDARY_TRACE_RANK"],
            "NOT_PROVEN",
        )

    def test_fredholm_and_background_remain_open(self) -> None:
        gates = self.manifest["gates"]
        self.assertEqual(gates["FREDHOLM_PROPERTY"], "NOT_PROVEN")
        self.assertEqual(gates["CONTINUUM_BVP_JACOBIAN"], "NOT_PROVEN")
        self.assertEqual(gates["PHYSICAL_BACKGROUND"], "NOT_ESTABLISHED")

    def test_checkpoint_v1_14_is_canonical(self) -> None:
        self.assertEqual(self.checkpoint["checkpoint_id"], "UL-CHK-20260804-014")
        self.assertEqual(
            self.checkpoint["canonical_snapshot"],
            "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.14.json",
        )
        self.assertEqual(
            self.checkpoint["gate_state"]["OPERATOR_2B"],
            "PASS_FORMAL_FUNCTION_SPACE_AND_TRACE_TEMPLATE",
        )

    def test_decision_is_append_only(self) -> None:
        self.assertEqual(self.result["decision"], "UL-DEC-0022")

    def test_next_block_is_background_3a_method_only(self) -> None:
        next_block = self.result["next_recommended_block"]
        self.assertEqual(next_block["track_id"], "MD2S-R1-C-PHYS")
        self.assertEqual(next_block["gate"], "C-PHYS-R1.0-BACKGROUND-3A")
        self.assertEqual(next_block["execution"], "METHOD_PREREGISTRATION_ONLY")

    def test_release_gates_remain_closed(self) -> None:
        gates = self.manifest["gates"]
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
            "G0_THREE_TRACK_SYNCHRONIZATION_OPERATOR_2B",
        )


if __name__ == "__main__":
    unittest.main()
