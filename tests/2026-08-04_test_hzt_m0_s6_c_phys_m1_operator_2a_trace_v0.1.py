#!/usr/bin/env python3
"""Regression tests for supplemental Operator-2A regularity/trace QA."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_verify_hzt_m0_s6_c_phys_m1_operator_2a_trace_v0.1.py"
SPEC = importlib.util.spec_from_file_location("operator_2a_trace", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import trace verifier")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

class Operator2ATraceTests(unittest.TestCase):
    def test_pole_invariants(self) -> None:
        result = MODULE.verify_pole_invariant_expansions()
        self.assertEqual(result["status"], "PASS_FORMAL_FINITE_LOCAL_BUILDING_BLOCKS")
        self.assertEqual(result["internal_gaussian_curvature_limit"], "-6*l3")

    def test_cap_principal_transmission(self) -> None:
        result = MODULE.verify_cap_principal_transmission()
        self.assertEqual(result["metric_derivative_determinant"], "-4/ell_cap")
        self.assertEqual(result["metric_status"], "FULL_RANK_FOR_ELL_CAP_POSITIVE")
        self.assertEqual(result["full_augmented_trace_status"], "NOT_CONSTRUCTED")
        self.assertEqual(result["Fredholm_status"], "NOT_PROVEN")

    def test_firewalls(self) -> None:
        result = MODULE.verify_contract_firewalls()
        self.assertEqual(result["R1.1"], "BLOCKED")
        self.assertEqual(result["solver"], "NOT_AUTHORIZED")
        self.assertEqual(result["physical_evidence_effect"], "NONE")

    def test_cli(self) -> None:
        completed = subprocess.run([sys.executable, str(TOOL), "--json"], cwd=ROOT, check=True, capture_output=True, text=True)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "PASS_FORMAL")
        self.assertEqual(payload["contract"], "C_PHYS_M1_OPERATOR_2A_REGULARITY_TRACE_QA")

if __name__ == "__main__":
    unittest.main()
