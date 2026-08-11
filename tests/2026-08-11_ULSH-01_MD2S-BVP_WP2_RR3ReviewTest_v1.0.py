#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
REVIEWER_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_rr3_review_v1.0.py"
REVIEW_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_RR3Review_v1.0.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


REVIEWER = load_module(REVIEWER_PATH, "ulsh_wp2_rr3_review_test")


class WP2RR3ReviewTest(unittest.TestCase):
    def test_review_reproduces_blocked_decision(self):
        audit = REVIEWER.audit()
        self.assertEqual(audit["status"], "PASS_RR3_REVIEW_REPRODUCED_BLOCKED_NO_SOLVE")
        self.assertEqual(audit["review_status"], "BLOCKED_WP2_RR3_NEW_RELEASE_BLOCKERS_FOUND_NO_SOLVE")
        self.assertEqual(set(audit["new_release_blockers_reproduced"]), {"RR3-B01", "RR3-B02"})
        self.assertTrue(all(audit["new_release_blockers_reproduced"].values()))
        self.assertTrue(all(audit["h2_rr2_closures_verified"].values()))
        self.assertFalse(audit["numerical_backend_imported"])
        self.assertEqual(audit["solver_calls"], 0)
        self.assertFalse(audit["physical_solve_authorized"])
        self.assertFalse(audit["physical_solve_executed"])
        self.assertEqual(audit["K1-D"], "NOT_RELEASED")
        self.assertEqual(audit["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(audit["physical_evidence_effect"], "NONE")

    def test_review_json_status_and_firewall(self):
        review = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
        self.assertEqual(review["review_status"], "BLOCKED_WP2_RR3_NEW_RELEASE_BLOCKERS_FOUND_NO_SOLVE")
        self.assertEqual(set(review["new_release_blockers"]), {"RR3-B01", "RR3-B02"})
        self.assertFalse(review["release_state"]["physical_solve_authorized"])
        self.assertFalse(review["release_state"]["physical_solve_executed"])
        self.assertEqual(review["release_state"]["physical_evidence_effect"], "NONE")

    def test_rr3_b01_strict_json_rejects_nonfinite(self):
        with self.assertRaises(ValueError):
            json.dumps({"sentinel": math.inf}, allow_nan=False)
        h1_target = REVIEWER.H1_TARGET_PATH.read_text(encoding="utf-8")
        h1_tx = REVIEWER.H1_TX_PATH.read_text(encoding="utf-8")
        self.assertIn("independent_distance = math.inf", h1_target)
        self.assertIn("-math.inf", h1_target)
        self.assertIn("allow_nan=False", h1_tx)

    def test_rr3_b02_commit_state_race_markers(self):
        source = REVIEWER.H2_TX_PATH.read_text(encoding="utf-8")
        body = source[source.index("def execute(transaction_root"):]
        self.assertLess(body.index("with total_transaction_wall_clock_limit"), body.index("os.replace(staging, result_dir)"))
        self.assertLess(body.index("os.replace(staging, result_dir)"), body.index('UTILS.mark_state(grant_dir, "SUCCEEDED"'))
        failure = body[body.index("except BaseException as exc:"):]
        self.assertIn('"result_package_committed": False', failure)
        self.assertNotIn("result_dir.exists()", failure)

    def test_release_and_grant_absent(self):
        self.assertFalse(REVIEWER.RELEASE_PATH.exists())
        self.assertFalse(REVIEWER.GRANT_PATH.exists())

    def test_reviewer_is_stdlib_no_solve(self):
        source = REVIEWER_PATH.read_text(encoding="utf-8")
        self.assertNotIn("import numpy", source)
        self.assertNotIn("import scipy", source)
        self.assertNotIn("damped_newton(", source)
        self.assertNotIn("shooting_residual(", source)
        forbidden = "execute" + "_physical_schedule("
        self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
