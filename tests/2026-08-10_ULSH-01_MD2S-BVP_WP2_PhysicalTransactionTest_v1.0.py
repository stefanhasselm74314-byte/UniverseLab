#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TARGET_PATH = ROOT / "tools/2026-08-10_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.0.py"
TX_PATH = ROOT / "tools/2026-08-10_ulsh_01_md2s_bvp_wp2_transaction_v1.0.py"
CONTRACT_PATH = ROOT / "registry/2026-08-10_ULSH-01_MD2S-BVP_WP2_PhysicalTransactionContract_v1.0.json"
RELEASE_PATH = ROOT / "registry/2026-08-10_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.0.json"
GRANT_PATH = ROOT / "registry/2026-08-10_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.0.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class WP2PhysicalTransactionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.target = load_module(TARGET_PATH, "test_ulsh_wp2_target")
        cls.tx = load_module(TX_PATH, "test_ulsh_wp2_transaction")
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_contract_remains_unreleased_and_unsolved(self):
        self.assertEqual(self.contract["acceptance_decision"], "PASS_WP2_TRANSACTION_RELEASE_READY_NO_SOLVE")
        self.assertFalse(self.contract["physical_solve_authorized"])
        self.assertFalse(self.contract["physical_solve_executed"])
        self.assertFalse(self.contract["operative_grant_present"])
        self.assertFalse(self.contract["release_authorization_present"])
        self.assertFalse(RELEASE_PATH.exists())
        self.assertFalse(GRANT_PATH.exists())

    def test_target_payload_and_schedule_are_exact(self):
        audit = self.target.audit_target()
        self.assertEqual(audit["status"], "PASS_SOURCE_BOUND_TARGET_ENTRYPOINT_NO_SOLVE")
        self.assertEqual(audit["run_id"], "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1")
        self.assertEqual(audit["a_F"], "1/4")
        self.assertEqual(audit["seed_count"], 7)
        self.assertEqual(audit["node_counts"], [24, 32, 48, 64, 96])
        self.assertEqual(audit["planned_entry_count"], 35)
        self.assertEqual(audit["solver_calls"], 0)
        self.assertFalse(audit["physical_solve_executed"])
        schedule = self.target.build_schedule()
        self.assertEqual(len(schedule), 35)
        self.assertEqual([row["ordinal"] for row in schedule], list(range(1, 36)))
        self.assertEqual([row["seed_index"] for row in schedule[:5]], [0] * 5)
        self.assertEqual([row["node_count"] for row in schedule[:5]], [24, 32, 48, 64, 96])
        self.assertEqual([row["seed_index"] for row in schedule[-5:]], [6] * 5)

    def test_backend_hashes_are_exact(self):
        observed = self.target.validate_backend_hashes()
        expected = {key: value["sha256"] for key, value in self.contract["backend_bindings"].items()}
        self.assertEqual(observed, expected)

    def test_static_preflight_calls_no_solver(self):
        preflight = self.tx.static_preflight()
        self.assertEqual(preflight["status"], "PASS_WP2_STATIC_PREFLIGHT_RELEASE_READY_NO_SOLVE")
        self.assertEqual(preflight["planned_entry_count"], 35)
        self.assertEqual(preflight["solver_calls"], 0)
        self.assertFalse(preflight["physical_solve_executed"])
        self.assertFalse(preflight["release_authorization_present"])
        self.assertFalse(preflight["single_use_grant_present"])

    def test_execute_is_fail_closed_without_release_and_grant(self):
        with self.assertRaises(self.tx.AuthorizationDenied):
            self.tx.validate_release_and_grant()

    def test_replay_and_crash_semantics_use_only_external_tempdir(self):
        with tempfile.TemporaryDirectory(prefix="ulsh-wp2-test-") as temp:
            result = self.tx.self_test_replay_crash(Path(temp))
        self.assertEqual(result["status"], "PASS_SINGLE_USE_REPLAY_CRASH_SELF_TEST_NO_SOLVE")
        self.assertTrue(result["replay_blocked"])
        self.assertEqual(result["crash_state"], "CRASHED_OR_INDETERMINATE")
        self.assertEqual(result["solver_calls"], 0)

    def test_target_source_contains_no_control_override_or_direct_execute_cli(self):
        source = TARGET_PATH.read_text(encoding="utf-8")
        self.assertNotIn("control_a_F=True", source)
        self.assertNotIn("control_a_F = True", source)
        self.assertNotIn("a_F=0.0", source)
        self.assertNotIn("a_F = 0.0", source)
        self.assertNotIn("manufactured", source.lower())
        self.assertIn("control_a_F=False", source)
        self.assertNotIn('sub.add_parser("execute")', source)

    def test_transaction_source_does_not_auto_create_release_or_grant(self):
        source = TX_PATH.read_text(encoding="utf-8")
        self.assertNotIn("RELEASE_PATH.write", source)
        self.assertNotIn("GRANT_PATH.write", source)
        self.assertIn("os.O_EXCL", source)
        self.assertIn("CRASHED_OR_INDETERMINATE", source)
        self.assertIn("retry_requires_new_grant", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
