#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "compare-safe.html").read_text(encoding="utf-8")
DESKTOP = (ROOT / "compare-desktop.html").read_text(encoding="utf-8")
CSS = (ROOT / "assets/2026-08-06_UniverseLab_SplitPane_v1.1.css").read_text(encoding="utf-8")
JS = (ROOT / "assets/2026-08-05_UniverseLab_SplitPane_v1.0.js").read_text(encoding="utf-8")


def exactly(text: str, token: str, count: int = 1) -> None:
    actual = text.count(token)
    if actual != count:
        raise AssertionError(f"{token!r}: expected {count}, got {actual}")


def main() -> None:
    exactly(PAGE, 'data-ul-split-key="compare-safe"')
    exactly(PAGE, 'data-ul-pane="start"')
    exactly(PAGE, 'data-ul-pane="end"')
    exactly(PAGE, '2026-08-06_UniverseLab_SplitPane_v1.1.css')
    exactly(PAGE, '2026-08-05_UniverseLab_SplitPane_v1.0.js')
    exactly(PAGE, 'data-ul-split-default="340"')
    exactly(PAGE, 'data-ul-split-min="280"')
    exactly(PAGE, 'data-ul-split-max="560"')
    exactly(PAGE, 'data-ul-split-end-min="600"')

    if '<details class="panel params" data-ul-pane="start" open>' not in PAGE:
        raise AssertionError("desktop parameter pane is not initially available")
    if '<div class="compare-results" data-ul-pane="end">' not in PAGE:
        raise AssertionError("comparison result pane missing")

    # Preserve the complete calculator surface and scientific implementation hooks.
    for element_id in (
        "H0", "Om", "Ol", "w", "s8", "beta", "ib", "rchi",
        "reset", "csv", "chart", "view-compare", "view-distance", "view-formulas",
    ):
        if f'id="{element_id}"' not in PAGE:
            raise AssertionError(f"calculator element lost: {element_id}")

    for formula in (
        "function eL", "function eW", "function eB", "function age", "function dc",
        "Math.sqrt", "CSV speichern",
    ):
        if formula not in PAGE:
            raise AssertionError(f"calculator logic marker lost: {formula}")

    # Desktop wrapper must continue embedding the same safe calculator.
    if 'src="./compare-safe.html' not in DESKTOP:
        raise AssertionError("desktop comparison wrapper no longer embeds compare-safe")

    if not CSS.startswith("/* UniverseLab split-pane workspace v1.1"):
        raise AssertionError("unexpected split-pane v1.1 header")
    exactly(CSS, '@import url("./2026-08-05_UniverseLab_SplitPane_v1.0.css");')
    for marker in (
        '[data-ul-split-key="compare-safe"]',
        'width: min(1500px, calc(100% - 28px))',
        'grid-template-columns: minmax(0, 1.45fr) minmax(310px, .55fr)',
        '@media (max-width: 900px)',
    ):
        if marker not in CSS:
            raise AssertionError(f"compare layout contract missing: {marker}")

    if "localStorage" not in JS or "pointerdown" not in JS or "keydown" not in JS:
        raise AssertionError("stable split-pane controller lost required interaction paths")

    if "zoom:" in CSS or "transform: scale" in CSS or "display: none" in CSS:
        raise AssertionError("comparison density must not use page scaling or hide content")

    # Basic structural balance around the injected workspace.
    start = PAGE.index('data-ul-split-key="compare-safe"')
    end = PAGE.index('</main>', start)
    workspace = PAGE[start:end]
    if workspace.count('data-ul-pane="start"') != 1 or workspace.count('data-ul-pane="end"') != 1:
        raise AssertionError("split workspace pane structure drift")

    print("PASS: UniverseLab comparison split-pane v1.1 contract")


if __name__ == "__main__":
    main()
