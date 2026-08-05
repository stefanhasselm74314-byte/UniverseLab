#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
COMPACT = ROOT / "assets/2026-08-05_UniverseLab_DesktopCompact_v1.0.css"
TYPOGRAPHY = (
    ROOT / "assets/2026-08-01_UniverseLab_MobileTypography_v1.0.css",
    ROOT / "assets/2026-08-01_UniverseLab_MobileTypography_v1.1.css",
)
IMPORT = '@import url("./2026-08-05_UniverseLab_DesktopCompact_v1.0.css");'


def require(text: str, pattern: str, label: str) -> None:
    if re.search(pattern, text, flags=re.MULTILINE) is None:
        raise AssertionError(f"missing compact UI contract: {label}")


def main() -> None:
    css = COMPACT.read_text(encoding="utf-8")

    # Desktop-only contract: the compact layer must never redefine mobile rules.
    if "@media (max-width" in css or "@media(max-width" in css:
        raise AssertionError("desktop compact layer contains a mobile max-width rule")
    if "transform: scale" in css or "zoom:" in css:
        raise AssertionError("visual density must not be implemented through page scaling")
    if "display: none" in css:
        raise AssertionError("compact UI must not hide page content")

    require(css, r"@media \(min-width: 721px\)", "desktop base breakpoint")
    require(css, r"@media \(min-width: 901px\)", "desktop layout breakpoint")
    require(css, r"@media \(min-width: 1240px\)", "wide desktop breakpoint")

    # The four pages observed in the screen recording receive explicit contracts.
    require(css, r"\.app:has\(\.param-grid\)", "comparison calculator scope")
    require(css, r"repeat\(4, minmax\(0, 1fr\)\)", "four-column wide parameter grid")
    require(css, r"main:has\(\.gates\)", "research status scope")
    require(css, r"\.app:has\(\.quick-grid\)", "guide scope")
    require(css, r"repeat\(6, minmax\(0, 1fr\)\)", "six-column guide quick links")
    require(css, r"\.app:has\(\.branch-grid\)", "HyperLab scope")

    # Density is achieved by spacing/raster changes, not unreadably small type.
    require(css, r"min-height: 38px !important", "desktop control height")
    require(css, r"width: min\(1480px, calc\(100% - 32px\)\)", "comparison desktop width")
    require(css, r"height: 285px !important", "compact chart height")
    require(css, r"padding: 11px 14px !important|padding: 12px 14px !important", "compact card padding")

    # Both current typography entry points must load the same desktop layer.
    for path in TYPOGRAPHY:
        text = path.read_text(encoding="utf-8")
        if text.count(IMPORT) != 1:
            raise AssertionError(f"desktop compact import count drift in {path.name}")
        import_index = text.index(IMPORT)
        first_rule_index = text.index("html {")
        if import_index > first_rule_index:
            raise AssertionError(f"CSS import is not before style rules in {path.name}")
        if "@media (max-width: 720px)" not in text:
            raise AssertionError(f"mobile typography contract missing in {path.name}")

    print("PASS: UniverseLab desktop compact UI v1.0 contract")


if __name__ == "__main__":
    main()
