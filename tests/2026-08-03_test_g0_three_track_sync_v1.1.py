#!/usr/bin/env python3
"""Regression tests for G0 three-track synchronization with append-only decisions."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "2026-08-03_validate_g0_three_track_sync_v1.1.py"

spec = importlib.util.spec_from_file_location("g0_three_track_validator_v1_1", TOOL)
if spec is None or spec.loader is None:
    raise RuntimeError("unable to import G0 validator v1.1")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class G0ThreeTrackV11Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = module.validate()

    def test_three_tracks_are_exact_and_ordered(self) -> None:
        self.assertEqual(
            self.result["tracks"],
            ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"],
        )

    def test_physical_r1_and_c1_phases_are_separate(self) -> None:
        self.assertEqual(self.result["physical_r1"]["R1.1"], "BLOCKED")
        self.assertEqual(self.result["physical_r1"]["R1.2"], "BLOCKED")
        self.assertEqual(self.result["c1_verification"]["C1-V0"], "PASS")
        self.assertEqual(self.result["c1_verification"]["C1-V1"], "PASS_DIAGNOSTIC")
        self.assertEqual(self.result["c1_verification"]["C1-V2"], "PASS_DIAGNOSTIC")
        self.assertEqual(self.result["c1_verification"]["C1-V3"], "PARTIAL")
        self.assertEqual(self.result["c1_verification"]["C1-V4"], "NOT_STARTED")

    def test_historical_a0_evidence_is_downgraded(self) -> None:
        claims = module.load_json(
            "registry/2026-08-03_UniverseLab_ClaimRegister_G0_v1.0.json"
        )
        correction = claims["superseded_claims"]["MD2S-BG-001"]
        self.assertEqual(correction["status"], "OPEN")
        self.assertEqual(
            correction["canonical_label"],
            "REPORTED_NOT_INDEPENDENTLY_REPRODUCED",
        )

    def test_c1_is_manufactured_verification_only(self) -> None:
        model = module.load_json(
            "registry/2026-08-03_HZT_M0_S6_C1_V_ModelContract_v0.2.json"
        )
        self.assertEqual(model["classification"], "MANUFACTURED_VERIFICATION_MODEL")
        self.assertEqual(
            model["anchor"]["classification"],
            "EXACT_MANUFACTURED_VERIFICATION_BACKGROUND",
        )
        self.assertEqual(model["anchor"]["k4"], 0.25)
        self.assertEqual(model["anchor"]["GR_like_IR_interpretation"], "FORBIDDEN")
        self.assertEqual(model["physical_evidence_effect"], "NONE")

    def test_discrete_rank_does_not_upgrade_continuum(self) -> None:
        jacobian = module.load_json(
            "registry/2026-08-03_HZT_M0_S6_C1_V_DimensionlessJacobianContract_v0.2.json"
        )
        self.assertEqual(jacobian["result"]["rank"], 8)
        self.assertEqual(jacobian["continuum_BVP_Jacobian"], "NOT_PROVEN")
        self.assertEqual(jacobian["evidence_effect"], "DISCRETE_QA_ONLY")

    def test_local_tangent_does_not_establish_branch(self) -> None:
        backend = module.load_json(
            "registry/2026-08-03_HZT_M0_S6_C1_V_BackendTangentContract_v0.2.json"
        )
        self.assertTrue(backend["validated_results"]["local_first_tangent_only"])
        self.assertEqual(backend["verification_phases"]["C1-V3"], "PARTIAL")
        self.assertEqual(backend["nonlinear_solution_family"], "NOT_ESTABLISHED")
        self.assertFalse(backend["official_solver_authorized"])

    def test_gates_are_unchanged(self) -> None:
        gate = self.result["gate_state"]
        self.assertEqual(gate["K1-D"], "NOT_RELEASED")
        self.assertEqual(gate["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(gate["R1.1"], "BLOCKED")
        self.assertEqual(gate["official_MD2S_solver"], "NOT_AUTHORIZED")
        self.assertEqual(gate["physical_evidence_effect"], "NONE")

    def test_decision_log_allows_later_append_only_decisions(self) -> None:
        lines = [
            json.loads(line)
            for line in (ROOT / "registry/decision-log.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        ids = [entry["decision_id"] for entry in lines]
        self.assertIn("UL-DEC-0014", ids)
        self.assertIn("UL-DEC-0015", ids)
        self.assertLess(ids.index("UL-DEC-0014"), ids.index("UL-DEC-0015"))

    def test_next_block_is_exactly_g1_1(self) -> None:
        next_block = self.result["next_recommended_block"]
        self.assertEqual(next_block["gate"], "G1.1")
        self.assertEqual(next_block["track_id"], "HZT-M0-S6-C1-V")

    def test_validator_hash_is_stable(self) -> None:
        digest = __import__("hashlib").sha256(TOOL.read_bytes()).hexdigest()
        self.assertEqual(
            digest,
            "2df90969627faef5c89be5fd36ea5bee71efce6505c043bff1530da52712f24e",
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
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["contract"], "G0_THREE_TRACK_SYNCHRONIZATION")


if __name__ == "__main__":
    unittest.main()
