#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "tools/2026-08-11_ULSH-01_MD2S-BVP_WP2_PhysicalReleaseReviewAudit_v1.0.py"
REVIEW_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_PhysicalReleaseReview_v1.0.json"
RELEASE_PATH = ROOT / "registry/2026-08-10_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.0.json"
GRANT_PATH = ROOT / "registry/2026-08-10_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.0.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class PhysicalReleaseReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = load_module(AUDIT_PATH, "ulsh_wp2_rr_audit_test")
        cls.review = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))

    def test_review_is_blocked_not_authorized(self):
        self.assertEqual(self.review["review_status"], "BLOCKED_WP2_PHYSICAL_RELEASE_REVIEW_NO_SOLVE")
        self.assertEqual(
            self.review["release_decision"],
            "DO_NOT_CREATE_PHYSICAL_SOLVE_RELEASE_OR_SINGLE_USE_GRANT",
        )
        self.assertFalse(self.review["physical_solve_authorized"])
        self.assertFalse(self.review["physical_solve_executed"])
        self.assertEqual(self.review["physical_evidence_effect"], "NONE")
        self.assertFalse(RELEASE_PATH.exists())
        self.assertFalse(GRANT_PATH.exists())

    def test_four_blockers_are_reproducible(self):
        result = self.audit.reproduce_findings()
        self.assertEqual(result["status"], "PASS_RELEASE_REVIEW_BLOCKERS_REPRODUCED_NO_SOLVE")
        self.assertEqual(result["blocking_findings"], ["RR-B01", "RR-B02", "RR-B03", "RR-B04"])
        self.assertEqual(result["solver_calls"], 0)
        self.assertFalse(result["physical_solve_authorized"])
        self.assertFalse(result["physical_solve_executed"])

    def test_resource_blockers_match_frozen_policy(self):
        result = self.audit.reproduce_findings()
        self.assertEqual(result["per_stage_wall_clock_seconds"], 1800)
        self.assertEqual(result["maximum_result_bytes"], 1073741824)

    def test_result_schema_gap_is_nonempty(self):
        result = self.audit.reproduce_findings()
        self.assertTrue(result["missing_result_top_level_literals"])
        self.assertTrue(result["missing_mandatory_markers"])

    def test_dependency_lock_alias_is_byte_identical_today(self):
        result = self.audit.reproduce_findings()
        self.assertEqual(result["dependency_lock_b_sha256"], result["dependency_lock_c_sha256"])

    def test_review_source_contains_no_solver_invocation(self):
        audit_source = AUDIT_PATH.read_text(encoding="utf-8")
        forbidden = (
            "damped_newton(",
            "shooting_residual(",
            "least_squares(",
            "solve_ivp(",
            "execute_physical_schedule(",
        )
        for token in forbidden:
            self.assertNotIn(token, audit_source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
