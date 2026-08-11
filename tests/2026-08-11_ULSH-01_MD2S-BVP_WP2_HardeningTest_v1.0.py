#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TARGET_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.1.py"
TRANSACTION_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.1.py"
CONTRACT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_HardeningContract_v1.0.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


TARGET = load_module(TARGET_PATH, "ulsh_wp2h_test_target")
TRANSACTION = load_module(TRANSACTION_PATH, "ulsh_wp2h_test_transaction")


class HardeningTest(unittest.TestCase):
    def test_contract_state(self):
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "PASS_WP2_HARDENING_IMPLEMENTED_NO_SOLVE_PENDING_REREVIEW")
        self.assertEqual(set(contract["release_review_blocker_closure"]), {"RR-B01", "RR-B02", "RR-B03", "RR-B04"})
        self.assertFalse(contract["physical_solve_authorized"])
        self.assertFalse(contract["physical_solve_executed"])
        self.assertEqual(contract["physical_evidence_effect"], "NONE")

    def test_target_audit(self):
        audit = TARGET.audit_target()
        self.assertEqual(audit["status"], "PASS_WP2_HARDENED_TARGET_NO_SOLVE")
        self.assertEqual(audit["planned_entry_count"], 35)
        self.assertEqual(audit["a_F"], "1/4")
        self.assertEqual(audit["per_stage_timeout_seconds"], 1800)
        self.assertTrue(audit["stage_timeout_enforced_in_target"])
        self.assertTrue(audit["schema_complete_primary_capture"])
        self.assertTrue(audit["schema_complete_independent_capture"])
        self.assertEqual(audit["solver_calls"], 0)
        self.assertFalse(audit["physical_solve_executed"])

    def test_transaction_audit(self):
        audit = TRANSACTION.static_preflight()
        self.assertEqual(audit["status"], "PASS_WP2_HARDENING_STATIC_PREFLIGHT_NO_SOLVE")
        self.assertEqual(audit["release_review_blockers_implemented"], ["RR-B01", "RR-B02", "RR-B03", "RR-B04"])
        self.assertEqual(audit["solver_calls"], 0)
        self.assertFalse(audit["physical_solve_authorized"])
        self.assertFalse(audit["physical_solve_executed"])

    def test_result_budget_guard(self):
        with tempfile.TemporaryDirectory(prefix="ulsh-wp2h-") as temporary:
            staging = Path(temporary) / "staging"
            staging.mkdir()
            writer = TRANSACTION.BoundedStagingWriter(staging, 64)
            writer.write_bytes("a.bin", b"a" * 32)
            with self.assertRaises(TRANSACTION.ResultBudgetExceeded):
                writer.write_bytes("b.bin", b"b" * 33)
            self.assertEqual(writer.bytes_written, 32)
            self.assertFalse((staging / "b.bin").exists())

    def test_dependency_path_normalized(self):
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            contract["source_bindings"]["dependency_lock"]["path"],
            "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C_v0.1.txt",
        )


if __name__ == "__main__":
    unittest.main()
