#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
REVIEWER_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_rr2_review_v1.0.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


REVIEWER = load_module(REVIEWER_PATH, "ulsh_wp2_rr2_reviewer_test")


class HardeningReReviewTest(unittest.TestCase):
    def test_rr2_review_reproduces_blocked_decision(self):
        audit = REVIEWER.audit()
        self.assertEqual(audit["status"], "PASS_RR2_REVIEW_REPRODUCED_BLOCKED_NO_SOLVE")
        self.assertEqual(audit["review_status"], "BLOCKED_WP2_RR2_NEW_RELEASE_BLOCKERS_FOUND_NO_SOLVE")
        self.assertEqual(set(audit["new_release_blockers_reproduced"]), {"RR2-B01", "RR2-B02", "RR2-B03", "RR2-B04"})
        self.assertTrue(all(audit["new_release_blockers_reproduced"].values()))
        self.assertTrue(all(audit["original_RR_closures_verified"].values()))
        self.assertEqual(audit["solver_calls"], 0)
        self.assertFalse(audit["solver_imported"])
        self.assertFalse(audit["physical_solve_authorized"])
        self.assertFalse(audit["physical_solve_executed"])
        self.assertEqual(audit["K1-D"], "NOT_RELEASED")
        self.assertEqual(audit["K1-E"], "NOT_ADMISSIBLE")
        self.assertEqual(audit["physical_evidence_effect"], "NONE")

    def test_release_and_grant_remain_absent(self):
        self.assertFalse(REVIEWER.RELEASE_PATH.exists())
        self.assertFalse(REVIEWER.GRANT_PATH.exists())

    def test_reviewer_has_no_numerical_import_or_solver_call_ast(self):
        source = REVIEWER_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_roots: set[str] = set()
        called_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_names.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called_names.add(node.func.attr)
        self.assertTrue({"numpy", "scipy"}.isdisjoint(imported_roots))
        self.assertTrue({"damped_newton", "shooting_residual", "execute_physical_schedule"}.isdisjoint(called_names))


if __name__ == "__main__":
    unittest.main(verbosity=2)
