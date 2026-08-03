#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools/2026-08-03_apply_model_picker_v1.0.py"
SPEC = importlib.util.spec_from_file_location("model_picker_migration", TOOL_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ModelPickerContractTests(unittest.TestCase):
    def test_patch_inserts_assets_once(self) -> None:
        source = (
            "<head>"
            + MODULE.TYPOGRAPHY_LINK
            + "</head><body>"
            + MODULE.APP_SHELL_SCRIPT
            + "</body>"
        )
        patched, changed = MODULE.patch_text(source)
        self.assertTrue(changed)
        self.assertEqual(patched.count(MODULE.CSS_LINK), 1)
        self.assertEqual(patched.count(MODULE.JS_SCRIPT), 1)
        patched_again, changed_again = MODULE.patch_text(patched)
        self.assertFalse(changed_again)
        self.assertEqual(patched_again, patched)

    def test_missing_anchor_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.patch_text("<html><head></head><body></body></html>")

    def test_apply_and_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in (
                MODULE.CSS_PATH.removeprefix("./"),
                MODULE.JS_PATH.removeprefix("./"),
            ):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("asset", encoding="utf-8")

            (root / MODULE.TARGET).write_text(
                "<head>"
                + MODULE.TYPOGRAPHY_LINK
                + "</head><body>"
                + MODULE.APP_SHELL_SCRIPT
                + "</body>",
                encoding="utf-8",
            )
            self.assertTrue(MODULE.apply(root, check=False))
            self.assertFalse(MODULE.apply(root, check=True))

    def test_javascript_accessibility_contract(self) -> None:
        script = (ROOT / "assets/2026-08-03_UniverseLab_ModelPicker_v1.0.js").read_text(encoding="utf-8")
        for token in (
            "role=\"dialog\"",
            "aria-modal=\"true\"",
            "role=\"radiogroup\"",
            "aria-checked",
            "event.key==='Escape'",
            "event.key==='Tab'",
            "UniverseLabModel",
            "applyPreset",
            "ul-native-preset-hidden",
        ):
            self.assertIn(token, script)

    def test_css_visual_contract(self) -> None:
        css = (ROOT / "assets/2026-08-03_UniverseLab_ModelPicker_v1.0.css").read_text(encoding="utf-8")
        for token in (
            ".ul-model-picker-layer",
            "backdrop-filter: blur(14px)",
            ".ul-model-picker-dialog",
            ".ul-model-picker-option[aria-checked=\"true\"]",
            "min-height: 76px",
            "z-index: 13000",
        ):
            self.assertIn(token, css)


if __name__ == "__main__":
    unittest.main()
