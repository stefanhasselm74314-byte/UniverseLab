"""RC20 adversarial link-router and staged-privacy fixture tests."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "tools/2026-11-03_UniverseLab_RC20_RuntimePrivacyAudit_v1.0.py"
SPEC = importlib.util.spec_from_file_location("rc20_audit_test", SRC)
rc20 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(rc20)


class RC20CompatibilityPrivacyFixtures(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="rc20-qa-")
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.repo = self.dir / "repo"
        self.stage = self.dir / "staged"
        self.repo.mkdir()
        self.stage.mkdir()

    def source(self, relative: str, text: str) -> None:
        p = self.repo / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def staged(self, relative: str, text: str) -> None:
        p = self.stage / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def route(self, html: str, target: str, *, page: str = "solver-hub.html") -> tuple[list, list, dict]:
        self.staged(page, html)
        self.source(target, "synthetic public documentation fixture")
        return rc20._source_route_findings(self.repo, self.stage, {page})

    def test_01_github_md_redirect_to_excluded_local_document(self) -> None:
        target = "science/solver-hub/example.md"
        html = ('<a href="https://github.com/stefanhasselm74314-byte/UniverseLab/blob/main/'
                + target + '">Roadmap</a>'
                + '<script src="assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js"></script>')
        excluded, missing, context = self.route(html, target)
        self.assertEqual([x["target"] for x in excluded], [target])
        self.assertEqual(excluded[0]["router_activation"], "GLOBAL_SHELL_CHAIN")
        self.assertEqual(missing, [])
        self.assertEqual(context["pages_with_direct_global_shell"], 1)

    def test_02_github_python_source_excluded(self) -> None:
        target = "md2s_bvp_solver_v1_0.py"
        excluded, _, _ = self.route(
            f'<a href="https://github.com/stefanhasselm74314-byte/UniverseLab/blob/main/{target}">Source</a>',
            target)
        self.assertEqual(excluded[0]["router_activation"], "SERVICE_WORKER_CONDITIONAL")

    def test_03_raw_link_optout_not_rewritten(self) -> None:
        target = "science/example.md"
        excluded, _, _ = self.route(
            f'<a href="{target}" data-ul-raw-link="1">Raw</a>', target)
        self.assertEqual(excluded, [])

    def test_04_boolean_zero_optout_does_not_suppress_router(self) -> None:
        target = "science/example.md"
        excluded, _, _ = self.route(
            f'<a href="{target}" data-ul-raw-link="0">Not raw</a>', target)
        self.assertEqual(len(excluded), 1)

    def test_05_download_attribute_skips_router(self) -> None:
        target = "science/example.md"
        excluded, _, _ = self.route(
            f'<a href="{target}" download>Download</a>', target)
        self.assertEqual(excluded, [])

    def test_06_same_origin_absolute_viewer_link(self) -> None:
        target = "science/example.md"
        excluded, _, _ = self.route(
            f'<a href="/UniverseLab/{target}">Local</a>', target)
        self.assertEqual(len(excluded), 1)

    def test_07_other_git_repo_does_not_rewrite(self) -> None:
        target = "science/example.md"
        excluded, _, _ = self.route(
            f'<a href="https://github.com/other/repo/blob/main/{target}">Other</a>', target)
        self.assertEqual(excluded, [])

    def test_08_html_target_not_document_router_candidate(self) -> None:
        target = "other.html"
        excluded, _, _ = self.route('<a href="other.html">HTML</a>', target)
        self.assertEqual(excluded, [])

    def test_09_allowed_target_is_not_missing(self) -> None:
        target = "science/example.md"
        page = "solver-hub.html"
        self.staged(page, f'<a href="{target}">Local</a>')
        self.staged(target, "included")
        self.source(target, "included")
        excluded, missing, _ = rc20._source_route_findings(
            self.repo, self.stage, {page, target})
        self.assertEqual(excluded, [])
        self.assertEqual(missing, [])

    def test_10_already_absent_repo_target_separate_category(self) -> None:
        self.staged("solver-hub.html", '<a href="nonexistent.md">Absent</a>')
        excluded, missing, _ = rc20._source_route_findings(
            self.repo, self.stage, {"solver-hub.html"})
        self.assertEqual(excluded, [])
        self.assertEqual(missing[0]["target"], "nonexistent.md")

    def test_11_registry_roadmap_dynamic_target_detected(self) -> None:
        renderer = "2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.html"
        registry = "registry/2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.json"
        target = "science/solver-hub/workpackage.md"
        self.staged(renderer, "roadmap_path github.com")
        self.staged(registry, json.dumps({"solvers": [{"roadmap_path": target}]}))
        self.source(target, "fixture")
        findings = rc20._data_driven_roadmap_findings(
            self.repo, self.stage, {renderer, registry})
        self.assertEqual([x["target"] for x in findings], [target])

    def test_12_no_data_driven_claim_without_renderer_binding(self) -> None:
        renderer = "2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.html"
        registry = "registry/2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.json"
        self.staged(renderer, "No dynamic references")
        self.staged(registry, json.dumps({"solvers": [{"roadmap_path": "science/secret.md"}]}))
        self.source("science/secret.md", "fixture")
        self.assertEqual(rc20._data_driven_roadmap_findings(
            self.repo, self.stage, {renderer, registry}), [])

    def test_13_clean_privacy_fixture(self) -> None:
        self.staged("index.html", "<title>UniverseLab</title>")
        findings, scope = rc20._privacy_scan(REPO, self.stage, {"index.html"})
        self.assertEqual(findings, [])
        self.assertEqual(scope["files_scanned"], 1)

    def test_14_synthetic_email_pattern_detected_without_value_echo(self) -> None:
        self.staged("index.html", "Please write to synthetic.person@example.test")
        findings, _ = rc20._privacy_scan(REPO, self.stage, {"index.html"})
        self.assertIn("PATTERN:email_address", [x["category"] for x in findings])
        self.assertNotIn("synthetic.person", json.dumps(findings))

    def test_15_synthetic_api_token_detected_without_echo(self) -> None:
        self.staged("index.html", "ghp_" + "A" * 30)
        findings, _ = rc20._privacy_scan(REPO, self.stage, {"index.html"})
        self.assertIn("PATTERN:github_classic_token", [x["category"] for x in findings])

    def test_16_forbidden_nested_json_key_detected(self) -> None:
        self.staged("registry/data.json", '{"outer":{"private_key":"placeholder"}}')
        findings, _ = rc20._privacy_scan(REPO, self.stage, {"registry/data.json"})
        self.assertIn("FORBIDDEN_JSON_KEY", [x["category"] for x in findings])

    def test_17_duplicate_json_key_cannot_pass(self) -> None:
        self.staged("registry/data.json", '{"safe":1,"safe":2}')
        findings, _ = rc20._privacy_scan(REPO, self.stage, {"registry/data.json"})
        self.assertIn("DUPLICATE_JSON_KEY", [x["category"] for x in findings])

    def test_18_nonfinite_json_cannot_pass(self) -> None:
        self.staged("registry/data.json", '{"x":NaN}')
        findings, _ = rc20._privacy_scan(REPO, self.stage, {"registry/data.json"})
        self.assertIn("INVALID_JSON", [x["category"] for x in findings])

    def test_19_malformed_jsonl_cannot_pass(self) -> None:
        self.staged("registry/data.jsonl", '{"ok":1}\ninvalid\n')
        findings, _ = rc20._privacy_scan(REPO, self.stage, {"registry/data.jsonl"})
        self.assertIn("INVALID_JSON", [x["category"] for x in findings])

    def test_20_invalid_utf8_cannot_pass(self) -> None:
        path = self.stage / "index.html"
        path.write_bytes(b"\xff\xfe")
        findings, _ = rc20._privacy_scan(REPO, self.stage, {"index.html"})
        self.assertEqual(findings, [{"path": "index.html", "category": "INVALID_UTF8"}])

    def test_21_unscanned_extension_is_explicit(self) -> None:
        (self.stage / "file.bin").write_bytes(b"test")
        findings, scope = rc20._privacy_scan(REPO, self.stage, {"file.bin"})
        self.assertEqual(findings, [{"path": "file.bin", "category": "UNSCANNED_FILE_TYPE"}])
        self.assertEqual(scope["files_scanned"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
