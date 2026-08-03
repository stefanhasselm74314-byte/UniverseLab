#!/usr/bin/env python3
"""Regression tests for the C-PHYS-M1 Operator-2A canonical state."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_validate_g0_three_track_sync_v1.5.py"
SPEC = importlib.util.spec_from_file_location("g0_three_track_validator_v1_5", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import G0 v1.5 validator")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class Operator2ACanonicalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.validate()
        cls.manifest = json.loads((ROOT / "project-manifest.json").read_text(encoding="utf-8"))
        cls.checkpoint = json.loads((ROOT / "registry/session-checkpoint-latest.json").read_text(encoding="utf-8"))
        cls.contract = json.loads((ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2AContract_v0.1.json").read_text(encoding="utf-8"))

    def test_operator_2a_is_formal_only(self) -> None:
        self.assertEqual(self.manifest["gates"]["CONSTRAINT_PROPAGATION"], "PROVEN_SYMBOLIC_CONDITIONAL")
        self.assertEqual(self.manifest["gates"]["CONTINUUM_BVP_OPERATOR"], "SPECIALIZED_FORMAL_OPERATOR_DEFINED")
        self.assertEqual(self.manifest["gates"]["BOUNDARY_TRACE_MAP"], "NOT_CONSTRUCTED")
        self.assertEqual(self.manifest["gates"]["COMPLEMENTING_BOUNDARY_CONDITION"], "NOT_PROVEN")

    def test_constraint_is_propagated_not_endpoint_residual(self) -> None:
        self.assertEqual(self.contract["radial_constraint"]["BVP_role"], "PROPAGATED_QA_CHANNEL_NOT_ADDITIONAL_ENDPOINT_RESIDUAL")
        self.assertEqual(len(self.contract["boundary_operator_audit"]["independent_cap_residuals"]), 8)

    def test_principal_and_pole_status(self) -> None:
        self.assertEqual(self.contract["principal_part"]["determinant"], "4*ell")
        self.assertEqual(self.contract["principal_part"]["interior_status"], "FULL_RANK")
        self.assertEqual(self.contract["principal_part"]["pole_status"], "REGULAR_SINGULAR_BECAUSE_ELL_TO_ZERO")

    def test_next_primary_block_is_operator_2b(self) -> None:
        workstreams = {item["track_id"]: item for item in self.checkpoint["current_workstreams"]}
        self.assertEqual(workstreams["MD2S-R1-C-PHYS"]["next_block"], "C-PHYS-R1.0-OPERATOR-2B")
        self.assertEqual(workstreams["HZT-M0-S6-C1-V"]["priority"], "PARALLEL_DIAGNOSTIC_ONLY")

    def test_release_gates_remain_closed(self) -> None:
        gates = self.checkpoint["gate_state"]
        self.assertEqual(gates["R1.1"], "BLOCKED")
        self.assertEqual(gates["R1.2"], "BLOCKED")
        self.assertEqual(gates["FREDHOLM_PROPERTY"], "NOT_PROVEN")
        self.assertEqual(gates["CONTINUUM_BVP_JACOBIAN"], "NOT_PROVEN")
        self.assertEqual(gates["PHYSICAL_BACKGROUND"], "NOT_ESTABLISHED")
        self.assertEqual(gates["OFFICIAL_MD2S_SOLVER"], "NOT_AUTHORIZED")
        self.assertEqual(gates["K1-D"], "NOT_RELEASED")
        self.assertEqual(gates["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(gates["PHYSICAL_EVIDENCE_EFFECT"], "NONE")

    def test_cli_passes(self) -> None:
        completed = subprocess.run([sys.executable, str(TOOL), "--json"], cwd=ROOT, check=True, capture_output=True, text=True)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["contract"], "G0_THREE_TRACK_SYNCHRONIZATION")


if __name__ == "__main__":
    unittest.main()
