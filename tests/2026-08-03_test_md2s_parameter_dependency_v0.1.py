#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/2026-08-03_validate_md2s_parameter_dependency_v0.1.py"
CONTRACT_PATH = ROOT / "registry/2026-08-03_MD2S_ParameterAngularFluxContract_v0.1.json"
GRAPH_PATH = ROOT / "registry/2026-08-03_MD2S_SymbolicDependencyGraph_v0.1.json"
SPEC = importlib.util.spec_from_file_location("md2s_parameter_dependency_v0_1", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def payload() -> dict:
    return {
        "Delta_chi": 2.0 * math.pi,
        "N_sigma": 1,
        "q_sigma": 0.5,
        "A_chi": 0.2,
        "L": 2.0,
        "Z_sigma": 4.0,
        "q_ref": 1.0,
        "N_flux": 1,
        "segments": [
            {
                "r": [0.0, 1.0],
                "A": [0.0, 0.0],
                "L": [1.0, 1.0],
                "Z_F": [1.0, 1.0],
                "Q": 1.0,
            }
        ],
    }


class ParameterDependencyTests(unittest.TestCase):
    def test_repository_contracts_pass(self) -> None:
        result = MODULE.validate_files(CONTRACT_PATH, GRAPH_PATH)
        self.assertEqual(result["status"], "PASS")
        self.assertGreater(result["node_count"], 30)
        self.assertGreater(result["edge_count"], 40)
        self.assertEqual(result["gates"]["K1-D"], "NOT_RELEASED")

    def test_winding_quantities(self) -> None:
        result = MODULE.evaluate_payload(payload())
        self.assertAlmostEqual(result["winding"]["partial_chi_sigma"], 1.0)
        self.assertAlmostEqual(result["winding"]["d_chi"], 0.9)
        self.assertAlmostEqual(result["winding"]["X_sigma"], 0.2025)
        self.assertAlmostEqual(result["winding"]["Y_sigma"], 0.81)

    def test_constant_flux_quantization(self) -> None:
        result = MODULE.evaluate_payload(payload())
        self.assertAlmostEqual(result["flux"]["Phi_F"], 2.0 * math.pi)
        self.assertAlmostEqual(result["flux"]["R_flux"], 0.0)

    def test_angular_reparametrization_invariance(self) -> None:
        original = MODULE.evaluate_payload(payload())
        transformed_payload = MODULE.rescale_angular_payload(payload(), 3.5)
        transformed = MODULE.evaluate_payload(transformed_payload)
        self.assertAlmostEqual(
            original["winding"]["X_sigma"], transformed["winding"]["X_sigma"]
        )
        self.assertAlmostEqual(
            original["winding"]["Y_sigma"], transformed["winding"]["Y_sigma"]
        )
        self.assertAlmostEqual(original["flux"]["Phi_F"], transformed["flux"]["Phi_F"])
        self.assertAlmostEqual(original["flux"]["R_flux"], transformed["flux"]["R_flux"])

    def test_noninteger_sector_fails_closed(self) -> None:
        bad = payload()
        bad["N_sigma"] = 1.5
        with self.assertRaises(MODULE.ContractError):
            MODULE.evaluate_payload(bad)

    def test_unhealthy_domains_fail_closed(self) -> None:
        bad = payload()
        bad["Z_sigma"] = -1.0
        with self.assertRaises(MODULE.ContractError):
            MODULE.evaluate_payload(bad)
        bad = payload()
        bad["segments"][0]["Z_F"] = [1.0, 0.0]
        with self.assertRaises(MODULE.ContractError):
            MODULE.evaluate_payload(bad)
        bad = payload()
        bad["q_ref"] = 0.0
        with self.assertRaises(MODULE.ContractError):
            MODULE.evaluate_payload(bad)

    def test_graph_cycle_is_detected(self) -> None:
        graph = MODULE.load_json(GRAPH_PATH)
        graph = copy.deepcopy(graph)
        graph["edges"].append({"from": "P6_K1E", "to": "P0_KAPPA6"})
        issues, _ = MODULE.validate_dependency_graph(graph)
        self.assertTrue(any("cycle" in issue for issue in issues))

    def test_unknown_graph_node_is_detected(self) -> None:
        graph = MODULE.load_json(GRAPH_PATH)
        graph = copy.deepcopy(graph)
        graph["edges"].append({"from": "P0_KAPPA6", "to": "MISSING_NODE"})
        issues, _ = MODULE.validate_dependency_graph(graph)
        self.assertTrue(any("unknown node" in issue for issue in issues))

    def test_governance_mutation_is_detected(self) -> None:
        contract = MODULE.load_json(CONTRACT_PATH)
        contract = copy.deepcopy(contract)
        contract["freeze_effect"]["K1-D"] = "RELEASED"
        issues = MODULE.validate_parameter_contract(contract)
        self.assertTrue(any("K1-D" in issue for issue in issues))

    def test_cli_emits_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.json"
            input_path.write_text(json.dumps(payload()), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(MODULE_PATH), "--input", str(input_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(
                result["diagnostic_evaluation"]["status"], "DIAGNOSTIC_ONLY"
            )
            self.assertEqual(result["gates"]["K1-E"], "NOT_ADMISSIBLE")


if __name__ == "__main__":
    unittest.main()
