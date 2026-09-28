#!/usr/bin/env python3
"""Regression tests for UL-FNS-v1.2 platform-required aliases."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "2026-08-01_validate_file_naming_v1.0.py"
POLICY_PATH = ROOT / "registry" / "2026-09-23_UniverseLab_FileNamingPolicy_v1.2.json"

SPEC = importlib.util.spec_from_file_location("universelab_file_naming_validator_v12", TOOL_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load validator from {TOOL_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


class FileNamingContractV12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy, issues = VALIDATOR.load_policy(POLICY_PATH)
        if issues or cls.policy is None:
            raise AssertionError([issue.render() for issue in issues])

    def test_google_search_console_exact_alias_passes(self) -> None:
        issues = VALIDATOR.validate_path("googlebc3b5b4a4888e35c.html", self.policy)
        self.assertEqual([], issues, [issue.render() for issue in issues])

    def test_other_undated_verification_like_name_still_fails(self) -> None:
        issues = VALIDATOR.validate_path("google-other-token.html", self.policy)
        self.assertTrue(issues)
        self.assertIn("NAMING", {issue.category for issue in issues})

    def test_standard_dated_name_still_passes(self) -> None:
        issues = VALIDATOR.validate_path(
            "registry/2026-09-23_UniverseLab_FileNamingPolicy_v1.2.json",
            self.policy,
        )
        self.assertEqual([], issues, [issue.render() for issue in issues])


if __name__ == "__main__":
    unittest.main(verbosity=2)
