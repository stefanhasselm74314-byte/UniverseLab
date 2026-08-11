#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
TARGET_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.2.py"
TX_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.3.py"
CONTRACT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_H2Contract_v1.0.json"
RELEASE_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.2.json"
GRANT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.2.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


TARGET = load_module(TARGET_PATH, "ulsh_wp2_h2_target_test")
TX = load_module(TX_PATH, "ulsh_wp2_h2_tx_test")


class WP2H2Test(unittest.TestCase):
    def test_contract_state_and_firewall(self):
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "PASS_WP2_H2_IMPLEMENTED_NO_SOLVE_PENDING_RR3")
        self.assertEqual(set(contract["rr2_blocker_closure"]), {"RR2-B01", "RR2-B02", "RR2-B03", "RR2-B04"})
        self.assertTrue(all(item["status"] == "IMPLEMENTED_PENDING_RR3" for item in contract["rr2_blocker_closure"].values()))
        self.assertFalse(contract["physical_solve_authorized"])
        self.assertFalse(contract["physical_solve_executed"])
        self.assertEqual(contract["K1-D"], "NOT_RELEASED")
        self.assertEqual(contract["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(contract["physical_evidence_effect"], "NONE")
        self.assertFalse(RELEASE_PATH.exists())
        self.assertFalse(GRANT_PATH.exists())

    def test_target_audit_no_solve(self):
        audit = TARGET.audit_target()
        self.assertEqual(audit["status"], "PASS_WP2_H2_TARGET_HARDENING_NO_SOLVE")
        self.assertEqual(audit["planned_entry_count"], 35)
        self.assertTrue(audit["higher_precision_audit_required"])
        self.assertEqual(audit["solver_calls"], 0)
        self.assertFalse(audit["physical_solve_executed"])
        self.assertEqual(audit["physical_evidence_effect"], "NONE")

    def test_transaction_static_preflight_no_solve(self):
        audit = TX.static_preflight()
        self.assertEqual(audit["status"], "PASS_WP2_H2_V13_STATIC_PREFLIGHT_NO_SOLVE")
        self.assertTrue(audit["pre_solver_output_collision_guard"])
        self.assertTrue(audit["strict_thread_startup_required"])
        self.assertTrue(audit["process_total_wall_clock_supervisor"])
        self.assertTrue(audit["effective_blas_thread_attestation_required"])
        self.assertTrue(audit["continuous_total_transaction_deadline"])
        self.assertEqual(audit["solver_calls"], 0)
        self.assertFalse(audit["physical_solve_authorized"])
        self.assertFalse(audit["physical_solve_executed"])

    def test_rr2_b01_ordering_is_pre_runtime_and_pre_grant(self):
        source = TX_PATH.read_text(encoding="utf-8")
        execute_start = source.index("def execute(transaction_root")
        body = source[execute_start:]
        collision = body.index("pre_solver_output_collision_guard")
        strict = body.index("strict_startup_environment")
        runtime = body.index("validate_runtime")
        spend = body.index("claim_single_use_grant")
        supervised = body.index("supervised_target_execution")
        self.assertLess(collision, strict)
        self.assertLess(collision, runtime)
        self.assertLess(collision, spend)
        self.assertLess(collision, supervised)

    def test_rr2_b02_strict_env_rejects_unset_before_runtime(self):
        saved = {key: os.environ.get(key) for key in TX.THREAD_ENV_KEYS}
        saved_hash = os.environ.get("PYTHONHASHSEED")
        try:
            for key in TX.THREAD_ENV_KEYS:
                os.environ.pop(key, None)
            os.environ["PYTHONHASHSEED"] = "0"
            with self.assertRaises(TX.ResourceFailure):
                TX.BASE.strict_startup_environment()
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            if saved_hash is None:
                os.environ.pop("PYTHONHASHSEED", None)
            else:
                os.environ["PYTHONHASHSEED"] = saved_hash

    def test_rr2_b02_effective_blas_probe(self):
        runtime = TX.H1.validate_runtime()
        self.assertEqual(runtime["dependencies_observed"], runtime["dependencies_expected"])
        probe = TX.effective_blas_thread_attestation()
        self.assertEqual(probe["status"], "PASS_EFFECTIVE_BLAS_THREAD_COUNT_ONE")
        self.assertTrue(probe["probes"])
        self.assertTrue(all(item["reported_threads"] == 1 for item in probe["probes"]))

    def test_rr2_b03_parent_timer_is_real_and_fail_closed(self):
        started = time.monotonic()
        with self.assertRaises(TX.ResourceFailure):
            with TX.total_transaction_wall_clock_limit(0.02):
                time.sleep(0.2)
        self.assertLess(time.monotonic() - started, 0.15)
        source = TX_PATH.read_text(encoding="utf-8")
        self.assertIn("with total_transaction_wall_clock_limit", source)
        self.assertIn("supervised_target_execution", source)
        self.assertIn("package_schema_complete_result", source)
        self.assertIn("os.replace(staging, result_dir)", source)

    def test_rr2_b04_precision_policy_is_predeclared_fail_closed(self):
        source = TARGET_PATH.read_text(encoding="utf-8")
        self.assertIn("ALL_OTHERWISE_PASSING_CANDIDATES", source)
        self.assertIn("np.longdouble", source)
        self.assertIn("mantissa_bits < 64", source)
        self.assertIn("candidate[\"classification\"] = REJECT_CLASS", source)
        self.assertNotIn("BEST_FIT", source)

    def test_no_execute_call_in_test_source(self):
        source = Path(__file__).read_text(encoding="utf-8")
        forbidden = "execute" + "_physical_schedule("
        self.assertNotIn(forbidden, source)
        self.assertNotIn("TX.execute(", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
