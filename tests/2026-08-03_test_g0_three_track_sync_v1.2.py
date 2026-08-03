#!/usr/bin/env python3
"""Regression tests for consolidated G0, C-PHYS and G1.1 state."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "2026-08-03_validate_g0_three_track_sync_v1.2.py"

SPEC = importlib.util.spec_from_file_location("g0_three_track_validator_v1_2", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import G0 v1.2 validator")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ConsolidatedPostMergeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.validate()
        cls.manifest = json.loads((ROOT / "project-manifest.json").read_text(encoding="utf-8"))
        cls.checkpoint = json.loads((ROOT / "registry/session-checkpoint-latest.json").read_text(encoding="utf-8"))

    def test_three_tracks_remain_separate(self) -> None:
        self.assertEqual(
            self.result["tracks"],
            ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"],
        )

    def test_c_phys_is_primary_but_not_released(self) -> None:
        workstreams = {
            item["track_id"]: item for item in self.checkpoint["current_workstreams"]
        }
        self.assertEqual(workstreams["MD2S-R1-C-PHYS"]["priority"], "PRIMARY")
        self.assertEqual(
            self.checkpoint["gate_state"]["CONTINUUM_BVP_OPERATOR"],
            "SCAFFOLD_ONLY",
        )
        self.assertEqual(self.checkpoint["gate_state"]["R1.1"], "BLOCKED")
        self.assertEqual(
            self.checkpoint["gate_state"]["OFFICIAL_MD2S_SOLVER"],
            "NOT_AUTHORIZED",
        )

    def test_g1_1_status_is_atomic_and_diagnostic(self) -> None:
        result = json.loads(
            (
                ROOT
                / "registry/2026-08-03_HZT_M0_S6_C1_V_G1_1_SymmetricPredictorResult_v0.2.json"
            ).read_text(encoding="utf-8")
        )
        claims = json.loads(
            (
                ROOT / "registry/2026-08-03_UniverseLab_ClaimRegister_G1_1_v0.2.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(result["status"], "NUMERICALLY_CONFIRMED_DIAGNOSTIC")
        self.assertEqual(claims["claims"][0]["status"], "NUMERICALLY_CONFIRMED_DIAGNOSTIC")
        self.assertEqual(result["physical_evidence_effect"], "NONE")
        self.assertEqual(claims["claims"][0]["physical_evidence_effect"], "NONE")

    def test_checkpoint_alias_matches_v1_9(self) -> None:
        snapshot = json.loads(
            (
                ROOT / "registry/2026-08-03_UniverseLab_SessionCheckpoint_v1.9.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(snapshot, self.checkpoint)
        self.assertEqual(snapshot["checkpoint_id"], "UL-CHK-20260803-009")

    def test_release_gates_unchanged(self) -> None:
        gates = self.manifest["gates"]
        self.assertEqual(gates["K1-D"], "NOT_RELEASED")
        self.assertEqual(gates["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(gates["R1.1"], "BLOCKED")
        self.assertEqual(gates["official_MD2S_solver"], "NOT_AUTHORIZED")
        self.assertEqual(gates["physical_evidence_effect"], "NONE")

    def test_cli_returns_pass(self) -> None:
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
