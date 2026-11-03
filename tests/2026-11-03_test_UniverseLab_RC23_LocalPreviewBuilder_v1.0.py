#!/usr/bin/env python3
"""RC23 non-distributing ZIP controls including loopback HTTP on extracted bytes."""

import functools
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen
import warnings
from zipfile import ZipFile, ZIP_STORED


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-11-03_UniverseLab_RC23_LocalPreviewBuilder_v1.0.py"
MANIFEST = ROOT / "governance/2026-11-03_UniverseLab_RC19_PublicFiles_v1.0_DRAFT.json"
CANDIDATE = ROOT / "drafts/2026-11-03_UniverseLab_RC21_SafeDocumentRouter_v1.0_DRAFT.js"
PROVENANCE = ROOT / "drafts/2026-11-03_UniverseLab_RC21_RouterProvenance_v1.0_DRAFT.json"
TEMPLATE = ROOT / "tools/2026-11-03_UniverseLab_RC21_SafeRouterTemplate_v1.0.js"

spec = importlib.util.spec_from_file_location("rc23_preview_tested", TOOL)
rc23 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = rc23
spec.loader.exec_module(rc23)


class RC23PreviewTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="rc23-local-qa-")
        self.addCleanup(temp.cleanup)
        self.tmp = Path(temp.name)
        self.out = self.tmp / "local-only.zip"

    def build(self, *, manifest=MANIFEST, candidate=CANDIDATE, provenance=PROVENANCE,
              template=TEMPLATE, out=None):
        return rc23.build(ROOT, manifest, candidate, provenance, template, out or self.out)

    def verify(self, out=None):
        return rc23.verify(ROOT, MANIFEST, CANDIDATE, PROVENANCE, TEMPLATE, out or self.out)

    def rewrite_zip(self, transform):
        self.build()
        result = self.tmp / "modified.zip"
        with ZipFile(self.out, "r") as original, ZipFile(result, "x", compression=ZIP_STORED) as output:
            for info in original.infolist():
                data = original.read(info)
                new_info, new_data = transform(info, data)
                output.writestr(new_info, new_data)
        return result

    def test_archive_shape_exact_public_446_plus_two_external_records(self):
        result = self.build()
        self.assertEqual(result["status"], "RC23_CANDIDATE_BUILT_NOT_DISTRIBUTED")
        self.assertEqual(result["zip_entries"], 448)
        self.assertEqual(result["public_file_count"], 446)
        self.assertFalse(result["published_pages_changed"])
        self.assertEqual(result["release_gate"], "HOLD")
        verified = self.verify()
        self.assertEqual(verified["status"], "RC23_ARCHIVE_VERIFIED_NOT_AUTHORIZED")
        with ZipFile(self.out) as arc:
            meta = json.loads(arc.read(rc23.META_NAME))
            source = json.loads(MANIFEST.read_text())
            expected = {f["path"]: f["sha256"] for f in source["files"]}
            self.assertEqual({p[len(rc23.PUBLIC_PREFIX):] for p in arc.namelist()
                              if p.startswith(rc23.PUBLIC_PREFIX)}, set(expected))
            self.assertEqual(len(meta["files"]), 446)
            self.assertEqual(meta["status"], "NONCANONICAL_NOT_DISTRIBUTED")
            self.assertEqual(meta["owner_distribution_approval"], "NOT_GRANTED")
            self.assertEqual(meta["in_place_public_path_additions"], 0)
            self.assertEqual(meta["unchanged_files"], 445)
            self.assertEqual(meta["overlay_path"], rc23.ROUTER)
            self.assertNotEqual(meta["original_router_sha256"], meta["rc21_router_sha256"])
            router = arc.read(rc23.PUBLIC_PREFIX + rc23.ROUTER)
            self.assertEqual(router, CANDIDATE.read_bytes())
            for rel, original_digest in expected.items():
                if rel == rc23.ROUTER:
                    continue
                self.assertEqual(hashlib.sha256(arc.read(rc23.PUBLIC_PREFIX + rel)).hexdigest(), original_digest)
            for rel in ("science/solver-hub/2026-08-07_ULSH-01_MD2S-BVP_Roadmap_v1.0.md",
                        "md2s_bvp_solver_v1_0.py", "tools/2026-08-03_validate_public_repository_privacy_v1.0.py"):
                self.assertNotIn(rc23.PUBLIC_PREFIX + rel, arc.namelist())

    def test_identical_zip_from_two_independent_builds(self):
        first = self.build()
        second = self.build(out=self.tmp / "another.zip")
        self.assertEqual(first["zip_sha256"], second["zip_sha256"])
        self.assertEqual(self.out.read_bytes(), (self.tmp / "another.zip").read_bytes())

    def test_refuse_existing_output_without_mutation(self):
        self.out.write_text("OWNER_BYTES", encoding="utf-8")
        with self.assertRaisesRegex(rc23.PreviewHold, "ZIP_OUTPUT_MUST_BE_ABSENT"):
            self.build()
        self.assertEqual(self.out.read_text(encoding="utf-8"), "OWNER_BYTES")

    def test_refuse_output_inside_repository(self):
        with self.assertRaisesRegex(rc23.PreviewHold, "ZIP_OUTSIDE_REPOSITORY_REQUIRED"):
            self.build(out=ROOT / "rc23_should_not_be_written.zip")
        self.assertFalse((ROOT / "rc23_should_not_be_written.zip").exists())

    def test_mutated_candidate_rejected_before_writing(self):
        bogus = self.tmp / "bogus-router.js"
        bogus.write_bytes(CANDIDATE.read_bytes() + b"\n/* unexpected */")
        with self.assertRaisesRegex(rc23.PreviewHold, "RC21_ROUTER_CANDIDATE_NOT_REPRODUCIBLE"):
            self.build(candidate=bogus)
        self.assertFalse(self.out.exists())

    def test_mutated_provenance_rejected_before_writing(self):
        bogus = self.tmp / "bogus-provenance.json"
        original = json.loads(PROVENANCE.read_text())
        original["status"] = "AUTHORIZED"  # deliberate illegal promotion
        bogus.write_text(json.dumps(original), encoding="utf-8")
        with self.assertRaisesRegex(rc23.PreviewHold, "RC21_PROVENANCE_MISMATCH"):
            self.build(provenance=bogus)
        self.assertFalse(self.out.exists())

    def test_mutated_manifest_digest_rejected(self):
        bogus = self.tmp / "bogus-manifest.json"
        original = json.loads(MANIFEST.read_text())
        original["files"][0]["sha256"] = "0" * 64
        bogus.write_text(json.dumps(original), encoding="utf-8")
        with self.assertRaisesRegex(Exception, "PUBLIC_FILE_DIGEST_MISMATCH"):
            self.build(manifest=bogus)
        self.assertFalse(self.out.exists())

    def test_archive_extra_unlisted_file_rejected(self):
        self.build()
        altered = self.tmp / "extra.zip"
        with ZipFile(self.out) as original, ZipFile(altered, "x") as target:
            for info in original.infolist():
                target.writestr(info, original.read(info))
            target.writestr("UniverseLab/science/secret.md", "NEVER")
        with self.assertRaisesRegex(rc23.PreviewHold, "ZIP_PATH_INVENTORY_MISMATCH"):
            self.verify(altered)

    def test_archive_traversal_path_rejected(self):
        self.build()
        altered = self.tmp / "traversal.zip"
        with ZipFile(self.out) as original, ZipFile(altered, "x") as target:
            for info in original.infolist():
                target.writestr(info, original.read(info))
            target.writestr("../unsafe.txt", "NEVER")
        with self.assertRaisesRegex(rc23.PreviewHold, "ZIP_PATH_INVENTORY_MISMATCH"):
            self.verify(altered)

    def test_archive_content_tampering_rejected(self):
        selected = rc23.PUBLIC_PREFIX + rc23.ROUTER
        altered = self.rewrite_zip(lambda info, data: (info, data + b"\nBAD" if info.filename == selected else data))
        with self.assertRaisesRegex(rc23.PreviewHold, "ZIP_ENTRY_LENGTH_MISMATCH"):
            self.verify(altered)

    def test_archive_executable_or_symlink_metadata_rejected(self):
        selected = rc23.PUBLIC_PREFIX + rc23.ROUTER
        def transform(info, data):
            if info.filename == selected:
                info.external_attr = 0o120777 << 16
            return info, data
        altered = self.rewrite_zip(transform)
        with self.assertRaisesRegex(rc23.PreviewHold, "ZIP_NONCANONICAL_ENTRY_METADATA"):
            self.verify(altered)

    def test_local_http_serves_exact_preview_files_only(self):
        self.build()
        extracted = self.tmp / "extracted"
        extracted.mkdir()
        with ZipFile(self.out) as arc:
            arc.extractall(extracted)
        class QuietHandler(SimpleHTTPRequestHandler):
            def log_message(self, *_args):
                return
        handler = functools.partial(QuietHandler, directory=str(extracted))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_address[1]}/UniverseLab/"
            expected = json.loads(MANIFEST.read_text())
            for file in expected["files"]:
                rel = file["path"]
                with urlopen(base + rel, timeout=6) as response:
                    self.assertEqual(response.status, 200, rel)
                    data = response.read()
                    if rel == rc23.ROUTER:
                        self.assertEqual(data, CANDIDATE.read_bytes())
                    else:
                        self.assertEqual(hashlib.sha256(data).hexdigest(), file["sha256"], rel)
            with urlopen(base, timeout=6) as response:
                self.assertEqual(response.status, 200)
            for excluded in ("md2s_bvp_solver_v1_0.py", "science/solver-hub/2026-08-07_ULSH-01_MD2S-BVP_Roadmap_v1.0.md", "tools/2026-08-03_validate_public_repository_privacy_v1.0.py"):
                with self.assertRaises(HTTPError) as ctx:
                    urlopen(base + excluded, timeout=6)
                self.assertEqual(ctx.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
