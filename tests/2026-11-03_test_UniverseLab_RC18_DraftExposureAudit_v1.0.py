#!/usr/bin/env python3
"""RC18 mock tests; no unsafe code or Git tree contents executed."""
from __future__ import annotations
import importlib.util,io,json,sys,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"tools/2026-11-03_UniverseLab_RC18_DraftExposureAudit_v1.0.py"
spec=importlib.util.spec_from_file_location("universelab_rc18_scan",SCRIPT)
mod=importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)

ROOT_UPLOAD=b"""name: Deploy UniverseLab to GitHub Pages
on:
  push:
    branches: [main]
jobs:
  deploy:
    steps:
      - name: Checkout repository
        uses: actions/checkout@v6
      - name: Upload static site
        uses: actions/upload-pages-artifact@v4
        with:
          path: .
      - name: Deploy
        uses: actions/deploy-pages@v4
"""
FILTERED_UPLOAD=ROOT_UPLOAD.replace(b"path: .",b"path: _site")

def inventory(extra=None,deployment=ROOT_UPLOAD):
    x={
      mod.DEPLOY:deployment,
      "app.js":b"const STATE='./registry/session-checkpoint-latest.json';",
      "tools/scanner.py":b"for filename in root.rglob('*.json'): pass",
      "index.html":b"<main>UniverseLab</main>",
      "readme.md":b"Archive notes",
      "diagram.png":b"\x89PNG\r\n\x1a\n",
    }
    if extra:x.update(extra)
    return x

class ExposureTests(unittest.TestCase):
    def test_01_exact_root_deployment_risk(self):
        report=mod.analyze(inventory())
        self.assertTrue(report["pages_upload_repository_root"])
        self.assertEqual(report["automatic_routine_merge"],"HOLD_UNFILTERED_PUBLICATION")
        self.assertIn("PAGES_ROOT_UPLOAD_WOULD_INCLUDE_NEW_DRAFT_FILES",report["risks"])

    def test_02_explicit_upload_allowlist_is_separate_precondition(self):
        report=mod.analyze(inventory(deployment=FILTERED_UPLOAD))
        self.assertFalse(report["pages_upload_repository_root"])
        # Even a safe upload directory would not remove PUBLIC GitHub visibility
        self.assertIn("PUBLIC_REPOSITORY_EXPOSES_CONTENT_EVEN_WITHOUT_PAGES",report["risks"])
        self.assertEqual(report["automatic_routine_merge"],"HOLD_UNFILTERED_PUBLICATION")

    def test_03_main_drafts_are_not_required_for_exposure(self):
        report=mod.analyze(inventory())
        self.assertEqual(report["existing_main_draft_count"],0)
        self.assertTrue(report["pages_upload_repository_root"])

    def test_04_tracked_draft_finds_actual_path(self):
        report=mod.analyze(inventory({"drafts/2026-11-03_Test_DRAFT.json":b'{"status":"DRAFT"}'}))
        self.assertEqual(report["existing_main_draft_count"],1)

    def test_05_direct_draft_reference_not_missed(self):
        report=mod.analyze(inventory({"scripts/import.js":b'fetch("./drafts/test.json");'}))
        self.assertIn("scripts/import.js",report["direct_draft_reference_files"])

    def test_06_generic_discovery_must_be_reviewed(self):
        report=mod.analyze(inventory())
        self.assertIn("tools/scanner.py",report["generic_discovery_files"])

    def test_07_indirect_discovery_does_not_establish_execution(self):
        report=mod.analyze(inventory({"tools/list_all.py":b"for file in Path('.').rglob('*.json'): print(file)"}))
        self.assertIn("tools/list_all.py",report["generic_discovery_files"])
        self.assertIn("not verified runtime dataflow",report["scope"])

    def test_08_unrecognized_binary_not_executed(self):
        report=mod.analyze(inventory({"malicious.exe":b"do not run"}))
        self.assertGreater(report["non_text_or_unknown_ext_count"],0)

    def test_09_missing_pages_deploy_fail_closed(self):
        files=inventory();files.pop(mod.DEPLOY)
        with self.assertRaises(mod.Hold):
            mod.analyze(files)

    def test_10_duplicate_pages_publish_step_fail_closed(self):
        duplicate=ROOT_UPLOAD+ b"\n      - name: Upload static site\n        uses: actions/upload-pages-artifact@v4\n        with:\n          path: .\n"
        with self.assertRaises(mod.Hold):
            mod.analyze(inventory(deployment=duplicate))

    def test_11_oversized_source_blob_rejected(self):
        with self.assertRaises(mod.Hold):
            mod.analyze(inventory({"huge.py":b"x"*(mod.LIMIT_FILE+1)}))

    def test_12_invalid_inventory_rejected(self):
        with self.assertRaises(mod.Hold):
            mod.analyze({mod.DEPLOY:ROOT_UPLOAD,123:b"oops"})

    def test_13_no_publish_or_main_mutation_in_scanner(self):
        source=SCRIPT.read_text(encoding="utf-8")
        for term in ("actions/deploy-pages@", "git push", "git commit",
                     "os.system(", "requests.post(", "eval(", "exec("):
            self.assertNotIn(term,source)
        self.assertIn("git_archive",source) if "git_archive" in source else self.assertIn("pinned_archive",source)

if __name__=="__main__":
    unittest.main(verbosity=2)
