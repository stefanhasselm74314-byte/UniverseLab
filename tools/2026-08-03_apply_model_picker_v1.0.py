#!/usr/bin/env python3
"""Apply or verify the UniverseLab Observatory custom model picker.

The migration is deliberately narrow: it adds one dated stylesheet and one
script reference to observatory.html. Existing model logic and page content are
left unchanged.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TARGET = "observatory.html"
CSS_PATH = "./assets/2026-08-03_UniverseLab_ModelPicker_v1.0.css"
JS_PATH = "./assets/2026-08-03_UniverseLab_ModelPicker_v1.0.js"
CSS_LINK = f'<link rel="stylesheet" href="{CSS_PATH}">'
JS_SCRIPT = f'<script src="{JS_PATH}"></script>'
TYPOGRAPHY_LINK = '<link rel="stylesheet" href="./assets/2026-08-01_UniverseLab_MobileTypography_v1.1.css">'
APP_SHELL_SCRIPT = '<script src="./app-shell.js"></script>'


def patch_text(text: str) -> tuple[str, bool]:
    changed = False

    if CSS_LINK not in text:
        if TYPOGRAPHY_LINK not in text:
            raise ValueError("observatory.html: mobile typography anchor missing")
        text = text.replace(TYPOGRAPHY_LINK, TYPOGRAPHY_LINK + "\n" + CSS_LINK, 1)
        changed = True

    if JS_SCRIPT not in text:
        if APP_SHELL_SCRIPT not in text:
            raise ValueError("observatory.html: app-shell script anchor missing")
        text = text.replace(APP_SHELL_SCRIPT, APP_SHELL_SCRIPT + JS_SCRIPT, 1)
        changed = True

    return text, changed


def validate_assets(root: Path) -> None:
    missing = [
        relative
        for relative in (CSS_PATH.removeprefix("./"), JS_PATH.removeprefix("./"))
        if not (root / relative).is_file()
    ]
    if missing:
        raise RuntimeError("missing model picker asset(s): " + ", ".join(missing))


def apply(root: Path, check: bool) -> bool:
    validate_assets(root)
    target = root / TARGET
    if not target.is_file():
        raise RuntimeError(f"missing target: {TARGET}")

    text = target.read_text(encoding="utf-8")
    try:
        patched, changed = patch_text(text)
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc

    if check and changed:
        raise RuntimeError("MODEL_PICKER_CONTRACT = FAIL: observatory links missing")
    if not check and changed:
        target.write_text(patched, encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        changed = apply(Path(args.root).resolve(), check=args.check)
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    if args.check:
        print("MODEL_PICKER_CONTRACT = PASS")
    else:
        print(f"updated {TARGET}" if changed else "no migration changes required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
