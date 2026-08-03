#!/usr/bin/env python3
"""Regression tests for the additive C-PHYS Freeze-1B canonical state."""

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


class Freeze1BCanonicalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.validate()
        cls.manifest = json.loads((ROOT / "project-manifest.json").read_text(encoding="utf-8"))
        cls.checkpoint = json.loads((ROOT / "registry/session-checkpoint-latest.json").read_text(encoding="utf-8"))
        cls.freeze_1a = json.loads(
            (
                ROOT
                / "registry/2026-08-03_MD2S_R1_C_PHYS_GlobalConventionFreezeContract_v0.1.json"
            ).read_text(encoding="utf-8")
        )
        cls.freeze_1b = json.loads(
            (
                ROOT
                / "registry/2026-08-03_MD2S_R1_C_PHYS_MinimalEFTFunctionFreezeContract_v0.1.json"
            ).read_text(encoding="utf-8")
        )

    def test_freeze_1a_global_conventions_remain_frozen(self) -> None:
        self.assertEqual(self.freeze_1a["angular_convention"]["Delta_chi"], "2*pi")
        self.assertEqual(
            self.freeze_1a["regional_coordinates_and_orientations"][
                "global_two_form_orientation_signs"
            ],
            {"epsilon_N": 1, "epsilon_S": -1},
        )
        self.assertEqual(
            self.freeze_1a["charge_lattice"]["cap_charge"],
            "q_sigma=m_sigma*q_ref",
        )

    def test_freeze_1b_is_additive_model_definition(self) -> None:
        self.assertEqual(self.freeze_1b["model_family_id"], "C-PHYS-ME1")
        self.assertEqual(
            self.freeze_1b["classification"],
            "VERSIONED_MODEL_SELECTION_NOT_DERIVATION",
        )
        self.assertEqual(self.freeze_1b["evidence_effect"], "MODEL_DEFINITION_ONLY")
        self.assertEqual(self.freeze_1b["physical_evidence_effect"], "NONE")
        self.assertFalse(self.freeze_1b["solver_authorized"])

    def test_structural_count_is_functionally_specialized_conditional(self) -> None:
        self.assertEqual(
            self.checkpoint["gate_state"]["STRUCTURAL_BVP_COUNT"],
            "SQUARE_FUNCTIONALLY_SPECIALIZED_CONDITIONAL",
        )
        self.assertEqual(
            self.manifest["gates"]["CONTINUUM_BVP_JACOBIAN"],
            "NOT_PROVEN",
        )

    def test_exact_functions_are_closed_but_benchmark_is_open(self) -> None:
        open_items = self.manifest["c_phys_operator_entry"]["open_model_freeze_items"]
        self.assertNotIn("exact U(phi)", open_items)
        self.assertNotIn("exact Z_F(phi)", open_items)
        self.assertNotIn("exact lambda(phi)", open_items)
        self.assertNotIn("exact Z_sigma(phi)", open_items)
        self.assertIn("benchmark continuous parameter tuple", open_items)
        self.assertIn("benchmark integer sector", open_items)
        self.assertFalse(
            self.freeze_1b["track_firewall"]["C1_V_functional_forms_migrated"]
        )

    def test_primary_next_block_is_freeze_1c(self) -> None:
        workstreams = {
            item["track_id"]: item for item in self.checkpoint["current_workstreams"]
        }
        self.assertEqual(
            workstreams["MD2S-R1-C-PHYS"]["next_block"],
            "C-PHYS-R1.0-FREEZE-1C",
        )
        self.assertEqual(
            workstreams["HZT-M0-S6-C1-V"]["priority"],
            "PARALLEL_DIAGNOSTIC_ONLY",
        )

    def test_release_gates_remain_closed(self) -> None:
        gates = self.manifest["gates"]
        self.assertEqual(gates["R1.1"], "BLOCKED")
        self.assertEqual(gates["R1.2"], "BLOCKED")
        self.assertEqual(gates["official_MD2S_solver"], "NOT_AUTHORIZED")
        self.assertEqual(gates["K1-D"], "NOT_RELEASED")
        self.assertEqual(gates["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(gates["physical_evidence_effect"], "NONE")

    def test_decisions_are_append_only(self) -> None:
        lines = [
            json.loads(line)
            for line in (ROOT / "registry/decision-log.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
        ids = [item["decision_id"] for item in lines]
        self.assertIn("UL-DEC-0019", ids)
        self.assertEqual(ids[-1], "UL-DEC-0020")
        self.assertLess(ids.index("UL-DEC-0019"), ids.index("UL-DEC-0020"))

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
