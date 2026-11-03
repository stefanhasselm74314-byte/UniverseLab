"""Adversarial RC19 fixture tests; never test an installed release guard."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


FILE = Path(__file__).resolve().parents[1] / "tools/2026-11-03_UniverseLab_RC19_PublicOnlyBuild_v1.0.py"
SPEC = importlib.util.spec_from_file_location("rc19_build", FILE)
rc19 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(rc19)


class RC19PublicOnlyBuildTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="rc19-fixture-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.src = self.base / "repository"
        self.src.mkdir()
        self.out = self.base / "staged"
        self.manifest = self.base / "public-list.json"
        self.contents = {
            "index.html": '<a href="navigator.html">Navigator</a><script src="app.js"></script>',
            "navigator.html": '<a href="./">Portal</a>',
            "sw.js": "self.addEventListener('fetch', e => {});",
            "app.js": "fetch('./registry/state.json');",
            "manifest.webmanifest": '{"name":"fixture"}',
            "robots.txt": "User-agent: *\nAllow: /\n",
            "sitemap.xml": '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>',
            "registry/state.json": '{"status":"noncanonical fixture"}',
        }
        for path, data in self.contents.items():
            self.write(path, data)
        self.save_manifest()

    def write(self, path: str, data: str) -> None:
        dest = self.src / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(data, encoding="utf-8")

    def payload(self) -> dict:
        return {
            "schema": rc19.SCHEMA,
            "status": "DRAFT_NOT_AUTHORIZED",
            "basis_main_commit": "1" * 40,
            "basis_main_tree": "2" * 40,
            "files": [
                {"path": path, "sha256": hashlib.sha256((self.src / path).read_bytes()).hexdigest()}
                for path in sorted(self.contents)
            ],
        }

    def save_manifest(self, obj: dict | None = None) -> None:
        self.manifest.write_text(json.dumps(obj or self.payload(), indent=2) + "\n", encoding="utf-8")

    def build(self, **kwargs) -> dict:
        return rc19.build(self.src, self.manifest, self.out, **kwargs)

    def expect_hold(self, phrase: str, **kwargs) -> None:
        with self.assertRaises(rc19.BuildHold) as e:
            self.build(**kwargs)
        self.assertIn(phrase, str(e.exception))

    def test_01_minimal_public_site_build(self) -> None:
        result = self.build()
        self.assertEqual(result["file_count"], len(self.contents))
        self.assertEqual(result["uncovered_existing_links"], [])
        self.assertEqual(result["pages_deployment_changed"], False)
        self.assertEqual(result["canonical_promotion"], "BLOCKED")
        self.assertEqual(
            {p.relative_to(self.out).as_posix() for p in self.out.rglob("*") if p.is_file()},
            set(self.contents),
        )

    def test_02_synthetic_draft_canary_excluded(self) -> None:
        marker = "RC19_SYNTHETIC_NONSECRET_CANARY_X9F"
        self.write("drafts/2026-11-03_fixture_DRAFT.json", marker)
        self.write("science/note.md", marker)
        self.write("governance/status.md", marker)
        self.build()
        self.assertFalse(any(marker.encode() in p.read_bytes() for p in self.out.rglob("*") if p.is_file()))
        self.assertFalse((self.out / "drafts").exists())

    def test_03_unlisted_workflows_and_tools_excluded(self) -> None:
        self.write(".github/workflows/deploy-pages.yml", "malicious synthetic workflow")
        self.write("tools/installer.py", "raise SystemExit(1)")
        self.build()
        self.assertFalse((self.out / ".github").exists())
        self.assertFalse((self.out / "tools").exists())

    def test_04_modified_authorized_asset_digest_fails(self) -> None:
        self.write("app.js", "fetch('https://untrusted.example')")
        self.expect_hold("CONTENT_SHA256_MISMATCH:app.js")

    def test_05_missing_authorized_file_fails(self) -> None:
        (self.src / "app.js").unlink()
        self.expect_hold("SOURCE_PATH_MISSING")

    def test_06_authorized_symlink_fails(self) -> None:
        (self.src / "navigator.html").unlink()
        (self.src / "navigator.html").symlink_to("index.html")
        self.expect_hold("SOURCE_SYMLINK_FORBIDDEN")

    def test_07_authorized_executable_fails(self) -> None:
        (self.src / "app.js").chmod(0o755)
        self.expect_hold("SOURCE_EXECUTABLE_FORBIDDEN")

    def test_08_manifest_path_traversal_fails(self) -> None:
        obj = self.payload()
        obj["files"][0]["path"] = "../drafts/secret.json"
        self.save_manifest(obj)
        self.expect_hold("UNSAFE_PATH")

    def test_09_manifest_explicit_draft_path_fails(self) -> None:
        obj = self.payload()
        obj["files"][0]["path"] = "drafts/canary.json"
        self.save_manifest(obj)
        self.expect_hold("BLOCKED_PREFIX")

    def test_10_duplicate_json_key_fails(self) -> None:
        raw = self.manifest.read_text(encoding="utf-8")
        self.manifest.write_text(raw.replace('"schema":', '"schema": "duplicate", "schema":', 1), encoding="utf-8")
        self.expect_hold("DUPLICATE_JSON_KEY")

    def test_11_duplicate_authorized_path_fails(self) -> None:
        obj = self.payload()
        obj["files"].append(obj["files"][-1].copy())
        self.save_manifest(obj)
        self.expect_hold("DUPLICATE_PATH")

    def test_12_glob_expansion_not_allowed(self) -> None:
        obj = self.payload()
        obj["files"][0]["path"] = "registry/*.json"
        self.save_manifest(obj)
        self.expect_hold("NON_CANONICAL_PATH")

    def test_13_unlisted_extension_fails(self) -> None:
        obj = self.payload()
        obj["files"][0]["path"] = "config.env"
        self.save_manifest(obj)
        self.expect_hold("PATH_OUTSIDE_STATIC_PUBLIC_ENVELOPE")

    def test_14_existing_output_not_overwritten(self) -> None:
        self.out.mkdir()
        (self.out / "user-file.txt").write_text("retain", encoding="utf-8")
        self.expect_hold("OUTPUT_MUST_BE_ABSENT")
        self.assertEqual((self.out / "user-file.txt").read_text(encoding="utf-8"), "retain")

    def test_15_existing_local_target_excluded_fails_link_check(self) -> None:
        self.write("index.html", '<a href="private.txt">secret</a>')
        self.write("private.txt", "synthetic")
        self.save_manifest()
        self.expect_hold("PUBLIC_LINK_TARGET_EXCLUDED")

    def test_16_external_url_does_not_break_local_check(self) -> None:
        self.write("index.html", '<a href="https://github.com/openai">External</a>')
        self.save_manifest()
        self.assertEqual(self.build()["uncovered_existing_links"], [])

    def test_17_known_missing_legacy_link_is_reported(self) -> None:
        self.write("index.html", '<a href="old-deleted.html">Old</a>')
        self.save_manifest()
        result = self.build()
        self.assertEqual(result["preexisting_missing_literal_links"], ["index.html -> old-deleted.html"])

    def test_18_correct_controlled_deploy_metadata(self) -> None:
        sha = "a" * 40
        meta = {
            "schema": "UniverseLab.PagesDeployment.v1",
            "source_sha": sha,
            "source_ref": "refs/heads/main",
            "event_name": "push",
            "workflow_run_id": "12345",
            "workflow_run_attempt": 1,
        }
        self.write("deploy-meta.json", json.dumps(meta))
        self.build(metadata=self.src / "deploy-meta.json", expected_deploy_sha=sha)
        self.assertEqual(json.loads((self.out / "deploy-meta.json").read_text()), meta)

    def test_19_wrong_deploy_metadata_sha_fails(self) -> None:
        self.write("deploy-meta.json", json.dumps({
            "schema": "UniverseLab.PagesDeployment.v1",
            "source_sha": "b" * 40,
            "source_ref": "refs/heads/main", "event_name": "push",
            "workflow_run_id": "123", "workflow_run_attempt": 1,
        }))
        self.expect_hold("DEPLOY_META_SHA_OR_SCHEMA_INVALID",
                         metadata=self.src / "deploy-meta.json", expected_deploy_sha="a" * 40)

    def test_20_rerun_deploy_metadata_forbidden(self) -> None:
        self.write("deploy-meta.json", json.dumps({
            "schema": "UniverseLab.PagesDeployment.v1",
            "source_sha": "a" * 40,
            "source_ref": "refs/heads/main", "event_name": "push",
            "workflow_run_id": "123", "workflow_run_attempt": 2,
        }))
        self.expect_hold("DEPLOY_META_RERUN_FORBIDDEN",
                         metadata=self.src / "deploy-meta.json", expected_deploy_sha="a" * 40)

    def test_21_invalid_metadata_fields_forbidden(self) -> None:
        self.write("deploy-meta.json", json.dumps({
            "schema": "UniverseLab.PagesDeployment.v1",
            "source_sha": "a" * 40,
            "source_ref": "refs/heads/main", "event_name": "push",
            "workflow_run_id": "123", "workflow_run_attempt": 1,
            "secret_extra": "not allowed",
        }))
        self.expect_hold("DEPLOY_META_FIELDS_INVALID",
                         metadata=self.src / "deploy-meta.json", expected_deploy_sha="a" * 40)

    def test_22_manifest_unsorted_paths_forbidden(self) -> None:
        obj = self.payload()
        obj["files"].reverse()
        self.save_manifest(obj)
        self.expect_hold("MANIFEST_NOT_SORTED")

    def test_23_percent_encoded_manifest_path_forbidden(self) -> None:
        obj = self.payload()
        obj["files"][0]["path"] = "%2e%2e/secret.json"
        self.save_manifest(obj)
        self.expect_hold("NON_CANONICAL_PATH")

    def test_24_no_manifest_file_can_grant_status(self) -> None:
        obj = self.payload()
        obj["status"] = "RATIFIED"
        self.save_manifest(obj)
        self.expect_hold("MANIFEST_IDENTITY_OR_STATUS_INVALID")

    def test_25_deploy_metadata_boolean_attempt_type_confusion_fails(self) -> None:
        self.write("deploy-meta.json", json.dumps({
            "schema": "UniverseLab.PagesDeployment.v1",
            "source_sha": "a" * 40,
            "source_ref": "refs/heads/main", "event_name": "push",
            "workflow_run_id": "123", "workflow_run_attempt": True,
        }))
        self.expect_hold("DEPLOY_META_RERUN_FORBIDDEN",
                         metadata=self.src / "deploy-meta.json", expected_deploy_sha="a" * 40)

    def test_26_deploy_metadata_untrusted_ref_fails(self) -> None:
        self.write("deploy-meta.json", json.dumps({
            "schema": "UniverseLab.PagesDeployment.v1",
            "source_sha": "a" * 40,
            "source_ref": "refs/heads/audit/proposal", "event_name": "push",
            "workflow_run_id": "123", "workflow_run_attempt": 1,
        }))
        self.expect_hold("DEPLOY_META_VALUES_INVALID",
                         metadata=self.src / "deploy-meta.json", expected_deploy_sha="a" * 40)

    def test_27_symlink_parent_path_fails(self) -> None:
        directory = self.src / "registry"
        directory.rename(self.src / "registry_actual")
        directory.symlink_to("registry_actual", target_is_directory=True)
        self.expect_hold("SOURCE_SYMLINK_FORBIDDEN")


if __name__ == "__main__":
    unittest.main(verbosity=2)
