from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "validate_public_repository_privacy.py"
SPEC = importlib.util.spec_from_file_location("public_privacy", MODULE_PATH)
assert SPEC and SPEC.loader
public_privacy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(public_privacy)


class PublicRepositoryPrivacyTests(unittest.TestCase):
    def make_repo(self) -> tempfile.TemporaryDirectory[str]:
        temp = tempfile.TemporaryDirectory()
        (Path(temp.name) / "registry").mkdir(parents=True)
        return temp

    def test_clean_sanitized_registry_passes(self) -> None:
        with self.make_repo() as temp:
            root = Path(temp)
            payload = {
                "privacy_classification": "PUBLIC_SANITIZED",
                "historical_attachment_groups_identified": 12,
                "physical_gate_effect": "NONE",
            }
            (root / "registry" / "clean.json").write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(public_privacy.validate_repository(root), [])

    def test_attachment_identifier_fails(self) -> None:
        with self.make_repo() as temp:
            root = Path(temp)
            (root / "registry" / "leak.json").write_text(
                json.dumps({"attachment_id": "file-AbCdEf1234567890"}), encoding="utf-8"
            )
            findings = public_privacy.validate_repository(root)
            self.assertTrue(any("attachment" in item.detail for item in findings))

    def test_conversation_identifier_key_fails(self) -> None:
        with self.make_repo() as temp:
            root = Path(temp)
            (root / "registry" / "leak.json").write_text(
                json.dumps({"source_conversation_id": "00000000-0000-0000-0000-000000000000"}),
                encoding="utf-8",
            )
            findings = public_privacy.validate_repository(root)
            self.assertTrue(any("conversation" in item.detail for item in findings))

    def test_account_audit_filename_fails(self) -> None:
        with self.make_repo() as temp:
            root = Path(temp)
            (root / "registry" / "leak.json").write_text(
                json.dumps({"title": "Gesamtanalyse_ChatGPT_Account_2026.docx"}), encoding="utf-8"
            )
            findings = public_privacy.validate_repository(root)
            self.assertTrue(any("account_audit_artifact" in item.detail for item in findings))


if __name__ == "__main__":
    unittest.main()
