#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools/2026-08-01_apply_mobile_typography_v1.0.py"
SPEC = importlib.util.spec_from_file_location("mobile_typography", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MobileTypographyContractTests(unittest.TestCase):
    def test_patch_is_idempotent(self) -> None:
        source = "<html><head><style>body{font-size:12px}</style></head><body></body></html>"
        patched, changed = MODULE.patch_text(source, "index.html")
        self.assertTrue(changed)
        self.assertIn(MODULE.LINK, patched)
        patched_twice, changed_twice = MODULE.patch_text(patched, "index.html")
        self.assertFalse(changed_twice)
        self.assertEqual(patched, patched_twice)

    def test_link_is_inserted_after_existing_inline_style(self) -> None:
        source = "<head><style>.x{display:block}</style></head>"
        patched, _ = MODULE.patch_text(source, "page.html")
        self.assertLess(patched.index("</style>"), patched.index(MODULE.LINK))
        self.assertLess(patched.index(MODULE.LINK), patched.index("</head>"))

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
                (root / relative).write_text("<html><head></head><body></body></html>", encoding="utf-8")

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
