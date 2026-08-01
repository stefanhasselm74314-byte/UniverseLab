#!/usr/bin/env python3
"""Regression tests for UL-FNS-v1.0."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "2026-08-01_validate_file_naming_v1.0.py"
POLICY_PATH = ROOT / "registry" / "2026-08-01_UniverseLab_FileNamingPolicy_v1.0.json"

SPEC = importlib.util.spec_from_file_location("universelab_file_naming_validator", TOOL_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load validator from {TOOL_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


class FileNamingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy, issues = VALIDATOR.load_policy(POLICY_PATH)
        if issues or cls.policy is None:
            raise AssertionError([issue.render() for issue in issues])

    def assert_passes(self, path: str) -> None:
        issues = VALIDATOR.validate_path(path, self.policy)
        self.assertEqual([], issues, [issue.render() for issue in issues])

    def assert_fails(self, path: str, category: str = "NAMING") -> None:
        issues = VALIDATOR.validate_path(path, self.policy)
        self.assertTrue(issues, path)
        self.assertIn(category, {issue.category for issue in issues})

    def test_standard_name_passes(self) -> None:
        self.assert_passes("science/2026-08-01_HZT-M0_MDS05_Warpvolumen_v0.1.md")

    def test_time_disambiguated_name_passes(self) -> None:
        self.assert_passes("outputs/2026-08-01_1725_MD2S_ResidualAudit_v0.1.json")

    def test_status_suffix_passes(self) -> None:
        self.assert_passes("governance/2026-08-01_MD2S_ModelFreeze_v1.0_RELEASED.md")

    def test_compound_extension_passes(self) -> None:
        self.assert_passes("archive/2026-08-01_UniverseLab_CanonicalBackup_v1.0.tar.gz")

    def test_registered_latest_alias_passes(self) -> None:
        self.assert_passes("registry/session-checkpoint-latest.json")

    def test_registered_append_only_alias_passes(self) -> None:
        self.assert_passes("registry/decision-log.jsonl")

    def test_missing_date_fails(self) -> None:
        self.assert_fails("science/HZT-M0_MDS05_Warpvolumen_v0.1.md")

    def test_invalid_calendar_date_fails(self) -> None:
        self.assert_fails("science/2026-02-30_HZT-M0_Result_v0.1.md")

    def test_invalid_time_fails(self) -> None:
        self.assert_fails("science/2026-08-01_2461_HZT-M0_Result_v0.1.md")

    def test_missing_version_fails(self) -> None:
        self.assert_fails("science/2026-08-01_HZT-M0_Result.md")

    def test_whitespace_fails(self) -> None:
        self.assert_fails("science/2026-08-01_HZT M0_Result_v0.1.md")

    def test_non_ascii_filename_fails(self) -> None:
        self.assert_fails("science/2026-08-01_HZT-M0_Überblick_v0.1.md")

    def test_unregistered_stable_name_fails(self) -> None:
        self.assert_fails("registry/current-state.json")

    def test_duplicate_paths_are_checked_once(self) -> None:
        paths = [
            "science/2026-08-01_HZT-M0_Result_v0.1.md",
            "science/2026-08-01_HZT-M0_Result_v0.1.md",
        ]
        self.assertEqual([], VALIDATOR.validate_paths(paths, self.policy))

    def test_current_contract_artifacts_all_pass(self) -> None:
        paths = [
            "governance/2026-08-01_UNIVERSELAB_FILE_NAMING_STANDARD_v1.0.md",
            "registry/2026-08-01_UniverseLab_FileNamingPolicy_v1.0.json",
            "tools/2026-08-01_validate_file_naming_v1.0.py",
            "tests/2026-08-01_test_file_naming_v1.0.py",
            ".github/workflows/2026-08-01_UniverseLab_FileNamingContract_v1.0.yml",
        ]
        issues = VALIDATOR.validate_paths(paths, self.policy)
        self.assertEqual([], issues, [issue.render() for issue in issues])

    def test_policy_rejects_duplicate_alias(self) -> None:
        data = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        data["stable_aliases"].append(dict(data["stable_aliases"][0]))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "policy.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            policy, issues = VALIDATOR.load_policy(path)
        self.assertIsNone(policy)
        self.assertTrue(any("duplicate alias" in issue.message for issue in issues))

    def test_policy_requires_alias_reason(self) -> None:
        data = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        data["stable_aliases"][0]["reason"] = ""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "policy.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            policy, issues = VALIDATOR.load_policy(path)
        self.assertIsNone(policy)
        self.assertTrue(any("reason is required" in issue.message for issue in issues))


if __name__ == "__main__":
    unittest.main(verbosity=2)
