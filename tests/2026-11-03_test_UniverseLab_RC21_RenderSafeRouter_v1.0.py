#!/usr/bin/env python3
"""Exact-manifest router generator tests. No deployment or browser integration."""

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-11-03_UniverseLab_RC21_RenderSafeRouter_v1.0.py"
TEMPLATE = ROOT / "tools/2026-11-03_UniverseLab_RC21_SafeRouterTemplate_v1.0.js"
MANIFEST = ROOT / "governance/2026-11-03_UniverseLab_RC19_PublicFiles_v1.0_DRAFT.json"
SCRIPT = ROOT / "drafts/2026-11-03_UniverseLab_RC21_SafeDocumentRouter_v1.0_DRAFT.js"
PROVENANCE = ROOT / "drafts/2026-11-03_UniverseLab_RC21_RouterProvenance_v1.0_DRAFT.json"

spec = importlib.util.spec_from_file_location("rc21_candidate", TOOL)
rc21 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = rc21
spec.loader.exec_module(rc21)


class RC21GeneratorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="rc21-gen-test-")
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)

    def edited_manifest(self, transform):
        doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
        transform(doc)
        output = self.work / "manifest.json"
        output.write_text(json.dumps(doc), encoding="utf-8")
        return output

    def test_exact_generator_content_and_provenance(self):
        content, prov = rc21.render(ROOT, MANIFEST, TEMPLATE)
        self.assertEqual(content, SCRIPT.read_text(encoding="utf-8"))
        self.assertEqual(prov, json.loads(PROVENANCE.read_text(encoding="utf-8")))
        self.assertEqual(prov["status"], "CANDIDATE_NOT_INSTALLED")
        self.assertEqual(prov["public_source_paths"], 77)
        self.assertFalse(prov["website_changed"])
        self.assertEqual(prov["physical_gate_effect"], "NONE")
        self.assertEqual(prov["physical_evidence_effect"], "NONE")
        self.assertEqual(prov["manifest_sha256"], hashlib.sha256(MANIFEST.read_bytes()).hexdigest())
        self.assertEqual(prov["generated_router_sha256"], hashlib.sha256(content.encode()).hexdigest())
        self.assertEqual(content, rc21.render(ROOT, MANIFEST, TEMPLATE)[0], "deterministic rendering")

    def test_manifest_is_full_pinned_original_inventory(self):
        document = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(len(document["files"]), 446)
        self.assertEqual(document["basis_main_commit"], "51bcc8fccb092c104ac0fca5fc98a5b996dcb914")
        self.assertEqual(len([x for x in document["files"] if Path(x["path"]).suffix.lower()
                              in rc21.PUBLIC_SOURCE_SUFFIXES]), 77)
        self.assertNotIn("science/solver-hub/2026-08-07_ULSH-01_MD2S-BVP_Roadmap_v1.0.md",
                         {x["path"] for x in document["files"]})

    def test_drifted_public_content_digest_fail_closed(self):
        def change(d):
            d["files"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(rc21.CandidateHold, "PUBLIC_FILE_DIGEST_MISMATCH"):
            rc21.render(ROOT, self.edited_manifest(change), TEMPLATE)

    def test_missing_public_viewer_fail_closed(self):
        def change(d):
            d["files"] = [entry for entry in d["files"]
                          if entry["path"] != "2026-08-27_UniverseLab_DocumentViewer_v1.0.html"]
        with self.assertRaisesRegex(rc21.CandidateHold, "PUBLIC_VIEWER_MISSING_FROM_MANIFEST"):
            rc21.render(ROOT, self.edited_manifest(change), TEMPLATE)

    def test_unapproved_source_path_fail_closed(self):
        def change(d):
            d["files"].append({"path": "science/secret.md", "sha256": "0" * 64})
            d["files"].sort(key=lambda x: x["path"])
        with self.assertRaisesRegex(Exception, "BLOCKED_PREFIX"):
            rc21.render(ROOT, self.edited_manifest(change), TEMPLATE)

    def test_duplicate_manifest_entry_fail_closed(self):
        def change(d):
            d["files"].append(d["files"][-1])
        with self.assertRaisesRegex(Exception, "DUPLICATE_PATH"):
            rc21.render(ROOT, self.edited_manifest(change), TEMPLATE)

    def test_template_missing_or_duplicate_placeholder_fail_closed(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        for mutated in (
            template.replace("__RC21_ELIGIBLE_COUNT__", "77"),
            template + "\n// __RC21_MANIFEST_SHA256__\n",
        ):
            candidate = self.work / "invalid-template.js"
            candidate.write_text(mutated, encoding="utf-8")
            with self.assertRaisesRegex(rc21.CandidateHold, "TEMPLATE_PLACEHOLDER_NOT_UNIQUE"):
                rc21.render(ROOT, MANIFEST, candidate)

    def test_cli_check_existing_and_provenance_drift(self):
        args = [sys.executable, str(TOOL), "--root", str(ROOT), "--manifest", str(MANIFEST),
                "--template", str(TEMPLATE), "--output", str(self.work / "router.js"),
                "--provenance-out", str(self.work / "provenance.json"), "--check-existing"]
        (self.work / "router.js").write_bytes(SCRIPT.read_bytes())
        (self.work / "provenance.json").write_bytes(PROVENANCE.read_bytes())
        success = subprocess.run(args, check=False, capture_output=True, text=True)
        self.assertEqual(success.returncode, 0, success.stdout + success.stderr)
        (self.work / "router.js").write_text("// drift\n", encoding="utf-8")
        broken = subprocess.run(args, check=False, capture_output=True, text=True)
        self.assertEqual(broken.returncode, 2)
        self.assertIn("GENERATED_ROUTER_DRIFT", broken.stdout)
        (self.work / "router.js").write_bytes(SCRIPT.read_bytes())
        (self.work / "provenance.json").write_text("{}\n", encoding="utf-8")
        broken = subprocess.run(args, check=False, capture_output=True, text=True)
        self.assertEqual(broken.returncode, 2)
        self.assertIn("GENERATED_PROVENANCE_DRIFT", broken.stdout)

    def test_cli_refuses_existing_output_without_mutating_it(self):
        out = self.work / "no-overwrite.js"
        out.write_text("owner contents", encoding="utf-8")
        args = [sys.executable, str(TOOL), "--root", str(ROOT), "--manifest", str(MANIFEST),
                "--template", str(TEMPLATE), "--output", str(out)]
        result = subprocess.run(args, check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("OUTPUT_EXISTS_EXPLICIT_NO_OVERWRITE", result.stdout)
        self.assertEqual(out.read_text(encoding="utf-8"), "owner contents")


if __name__ == "__main__":
    unittest.main(verbosity=2)
