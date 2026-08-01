#!/usr/bin/env python3
"""Apply or verify UniverseLab mobile typography v1.1.

The migration replaces the v1.0 stylesheet link with v1.1, or inserts the v1.1
link before </head> when no earlier link exists. Existing page content, inline
CSS, canvas dimensions, images and scientific data are not rewritten.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

OLD_STYLESHEET = "./assets/2026-08-01_UniverseLab_MobileTypography_v1.0.css"
STYLESHEET = "./assets/2026-08-01_UniverseLab_MobileTypography_v1.1.css"
OLD_LINK = f'<link rel="stylesheet" href="{OLD_STYLESHEET}">'
LINK = f'<link rel="stylesheet" href="{STYLESHEET}">'
TARGETS = (
    "index.html",
    "observatory.html",
    "journey.html",
    "compare-safe.html",
    "hyperlab.html",
    "universe3d.html",
    "validation.html",
    "guide.html",
    "research-status.html",
    "emergence.html",
)


def patch_text(text: str, path: str) -> tuple[str, bool]:
    if LINK in text:
        if OLD_LINK in text:
            raise ValueError(f"{path}: both v1.0 and v1.1 links present")
        return text, False
    if OLD_LINK in text:
        return text.replace(OLD_LINK, LINK, 1), True
    marker = "</head>"
    index = text.lower().find(marker)
    if index < 0:
        raise ValueError(f"{path}: missing </head>")
    return text[:index] + LINK + "\n" + text[index:], True


def apply(root: Path, check: bool) -> list[str]:
    failures: list[str] = []
    changed: list[str] = []

    css_path = root / STYLESHEET.removeprefix("./")
    if not css_path.is_file():
        failures.append(f"missing stylesheet: {css_path.relative_to(root)}")

    for relative in TARGETS:
        path = root / relative
        if not path.is_file():
            failures.append(f"missing target: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        try:
            patched, did_change = patch_text(text, relative)
        except ValueError as exc:
            failures.append(str(exc))
            continue
        if did_change:
            if check:
                failures.append(f"missing v1.1 typography link: {relative}")
            else:
                path.write_text(patched, encoding="utf-8")
                changed.append(relative)

    if failures:
        raise RuntimeError("\n".join(failures))
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
        print("MOBILE_TYPOGRAPHY_V1_1_CONTRACT = PASS")
    else:
        print(f"updated {len(changed)} page(s)")
        for path in changed:
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
