from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.validate_memory_protocol import (
    parse_decision_log,
    scan_forbidden_keys,
    scan_privacy,
    validate_checkpoint,
    validate_decisions,
    validate_repository,
)

ROOT = Path(__file__).resolve().parents[1]


class MemoryProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checkpoint = json.loads(
            (ROOT / "registry/session-checkpoint-latest.json").read_text(encoding="utf-8")
        )
        text = (ROOT / "registry/decision-log.jsonl").read_text(encoding="utf-8")
        cls.decisions, parse_issues = parse_decision_log(text)
        if parse_issues:
            raise AssertionError(parse_issues)

    def test_repository_contract_passes_without_git_probe(self) -> None:
        self.assertEqual(validate_repository(ROOT, check_git=False), [])

    def test_privacy_scanner_blocks_share_link_email_key_and_dialogue(self) -> None:
        samples = {
            "share": "https://chatgpt.com/" + "share/example",
            "mail": "person" + "@" + "example.com",
            "key": "sk-" + "A" * 24,
            "dialogue": "User" + ": private statement",
        }
        for label, sample in samples.items():
            with self.subTest(label=label):
                self.assertTrue(scan_privacy("sample", sample))

    def test_forbidden_json_field_is_blocked(self) -> None:
        field = "trans" + "cript"
        issues = scan_forbidden_keys("sample.json", {field: "not allowed"})
        self.assertTrue(any("forbidden JSON field" in issue.message for issue in issues))

    def test_checkpoint_rejects_bad_commit_format(self) -> None:
        checkpoint = copy.deepcopy(self.checkpoint)
        checkpoint["basis_commit"] = "not-a-commit"
        issues = validate_checkpoint(ROOT, checkpoint, check_git=False)
        self.assertTrue(any("basis_commit" in issue.message for issue in issues))

    def test_checkpoint_rejects_missing_source(self) -> None:
        checkpoint = copy.deepcopy(self.checkpoint)
        checkpoint["verified_results"][0]["sources"] = ["missing/source.json"]
        issues = validate_checkpoint(ROOT, checkpoint, check_git=False)
        self.assertTrue(any("source file does not exist" in issue.message for issue in issues))

    def test_duplicate_decision_id_is_blocked(self) -> None:
        decisions = copy.deepcopy(self.decisions)
        duplicate = copy.deepcopy(decisions[0])
        duplicate["topic"] = "separate_test_topic"
        decisions.append(duplicate)
        issues = validate_decisions(ROOT, decisions)
        self.assertTrue(any("duplicate decision_id" in issue.message for issue in issues))

    def test_multiple_active_decisions_for_one_topic_are_blocked(self) -> None:
        decisions = copy.deepcopy(self.decisions)
        duplicate_topic = copy.deepcopy(decisions[0])
        duplicate_topic["decision_id"] = "UL-DEC-9999"
        decisions.append(duplicate_topic)
        issues = validate_decisions(ROOT, decisions)
        self.assertTrue(any("multiple active decisions" in issue.message for issue in issues))

    def test_supersedes_must_reference_earlier_decision(self) -> None:
        decisions = copy.deepcopy(self.decisions)
        decisions[0]["supersedes"] = "UL-DEC-9999"
        issues = validate_decisions(ROOT, decisions)
        self.assertTrue(any("must reference an earlier decision" in issue.message for issue in issues))


if __name__ == "__main__":
    unittest.main()
