#!/usr/bin/env python3
"""Regression tests for Operator-2B governance with checkpoint v1.15."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_validate_g0_three_track_sync_v1.7.py"
CHECKPOINT = ROOT / "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.15.json"
ALIAS = ROOT / "registry/session-checkpoint-latest.json"
MANIFEST = ROOT / "project-manifest.json"

SPEC = importlib.util.spec_from_file_location("g0_sync_v1_7", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import G0 v1.7 validator")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class G0CheckpointV115Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.validate()
        cls.checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        cls.alias = json.loads(ALIAS.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_checkpoint_v1_15_is_canonical(self) -> None:
        self.assertEqual(self.checkpoint["checkpoint_id"], "UL-CHK-20260804-015")
        self.assertEqual(
            self.checkpoint["canonical_snapshot"],
            "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.15.json",
        )
        self.assertEqual(
            self.checkpoint["supersedes"],
            "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.14.json",
        )
        self.assertEqual(self.alias, self.checkpoint)

    def test_basis_commit_exists_in_history(self) -> None:
        basis = self.checkpoint["basis_commit"]
        self.assertRegex(basis, r"^[0-9a-f]{40}$")
        completed = subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "-e", f"{basis}^{{commit}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_provenance_correction_changes_no_science(self) -> None:
        correction = self.checkpoint["provenance_correction"]
        self.assertFalse(correction["scientific_state_changed"])
        self.assertFalse(correction["gate_state_changed"])
        self.assertEqual(
            correction["evidence_effect"],
            "GOVERNANCE_PROVENANCE_ONLY",
        )
        self.assertFalse(self.result["scientific_state_changed"])
        self.assertFalse(self.result["gate_state_changed"])

    def test_manifest_points_to_v1_15(self) -> None:
        self.assertEqual(
            self.manifest["central_registries"]["session_checkpoint_snapshot"],
            "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.15.json",
        )
        self.assertEqual(
            self.manifest["release"],
            "2.7-c-phys-m1-operator-2b-v0.1",
        )

    def test_operator_2b_state_is_preserved(self) -> None:
        gates = self.checkpoint["gate_state"]
        self.assertEqual(
            gates["OPERATOR_2B"],
            "PASS_FORMAL_FUNCTION_SPACE_AND_TRACE_TEMPLATE",
        )
        self.assertEqual(
            gates["CONTINUUM_BVP_OPERATOR"],
            "FUNCTION_SPACE_AND_TRACE_TEMPLATE_DEFINED",
        )
        self.assertEqual(
            gates["FULL_LINEARIZED_BOUNDARY_TRACE_TEMPLATE"],
            "DEFINED_NOT_EVALUATED",
        )

    def test_unproven_results_remain_unproven(self) -> None:
        gates = self.checkpoint["gate_state"]
        self.assertEqual(gates["FULL_LINEARIZED_BOUNDARY_TRACE_RANK"], "NOT_PROVEN")
        self.assertEqual(gates["FREDHOLM_PROPERTY"], "NOT_PROVEN")
        self.assertEqual(gates["CONTINUUM_BVP_JACOBIAN"], "NOT_PROVEN")
        self.assertEqual(gates["PHYSICAL_BACKGROUND"], "NOT_ESTABLISHED")

    def test_release_gates_remain_closed(self) -> None:
        gates = self.checkpoint["gate_state"]
        self.assertEqual(gates["R1.1"], "BLOCKED")
        self.assertEqual(gates["R1.2"], "BLOCKED")
        self.assertEqual(gates["OFFICIAL_MD2S_SOLVER"], "NOT_AUTHORIZED")
        self.assertEqual(gates["K1-D"], "NOT_RELEASED")
        self.assertEqual(gates["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(gates["PHYSICAL_EVIDENCE_EFFECT"], "NONE")

    def test_decision_0022_remains_latest(self) -> None:
        self.assertEqual(self.result["decision"], "UL-DEC-0022")

    def test_next_block_remains_method_only(self) -> None:
        next_block = self.result["next_recommended_block"]
        self.assertEqual(next_block["gate"], "C-PHYS-R1.0-BACKGROUND-3A")
        self.assertEqual(next_block["execution"], "METHOD_PREREGISTRATION_ONLY")

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
            "G0_THREE_TRACK_SYNCHRONIZATION_OPERATOR_2B_PROVENANCE_V1_15",
        )


if __name__ == "__main__":
    unittest.main()
