#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools/2026-08-01_apply_mobile_typography_v1.1.py"
SPEC = importlib.util.spec_from_file_location("mobile_typography_v1_1", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MobileTypographyV11ContractTests(unittest.TestCase):
    def test_replaces_v1_0_link(self) -> None:
        source = f"<html><head>{MODULE.OLD_LINK}</head><body></body></html>"
        patched, changed = MODULE.patch_text(source, "index.html")
        self.assertTrue(changed)
        self.assertIn(MODULE.LINK, patched)
        self.assertNotIn(MODULE.OLD_LINK, patched)

    def test_patch_is_idempotent(self) -> None:
        source = "<html><head><style>body{font-size:12px}</style></head><body></body></html>"
        patched, changed = MODULE.patch_text(source, "index.html")
        self.assertTrue(changed)
        patched_twice, changed_twice = MODULE.patch_text(patched, "index.html")
        self.assertFalse(changed_twice)
        self.assertEqual(patched, patched_twice)

    def test_both_versions_fail_closed(self) -> None:
        source = f"<head>{MODULE.OLD_LINK}{MODULE.LINK}</head>"
        with self.assertRaises(ValueError):
            MODULE.patch_text(source, "broken.html")

    def test_missing_head_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.patch_text("<html><body></body></html>", "broken.html")

    def test_apply_and_check_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            css = root / MODULE.STYLESHEET.removeprefix("./")
            css.parent.mkdir(parents=True)
            css.write_text("@media(max-width:720px){body{font-size:17px}}", encoding="utf-8")
            for relative in MODULE.TARGETS:
                (root / relative).write_text(
                    f"<html><head>{MODULE.OLD_LINK}</head><body></body></html>",
                    encoding="utf-8",
                )
            changed = MODULE.apply(root, check=False)
            self.assertEqual(set(changed), set(MODULE.TARGETS))
            self.assertEqual(MODULE.apply(root, check=True), [])

    def test_missing_stylesheet_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in MODULE.TARGETS:
                (root / relative).write_text(
                    f"<html><head>{MODULE.LINK}</head><body></body></html>",
                    encoding="utf-8",
                )
            with self.assertRaises(RuntimeError):
                MODULE.apply(root, check=True)


if __name__ == "__main__":
    unittest.main()
