#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "compare-safe.html").read_text(encoding="utf-8")
DESKTOP = (ROOT / "compare-desktop.html").read_text(encoding="utf-8")
CSS = (ROOT / "assets/2026-08-06_UniverseLab_SplitPane_v1.1.css").read_text(encoding="utf-8")
JS = (ROOT / "assets/2026-08-05_UniverseLab_SplitPane_v1.0.js").read_text(encoding="utf-8")
ADAPTER = (ROOT / "assets/2026-09-01_UniverseLab_CompareSafeAdapter_v2.0.js").read_text(encoding="utf-8")
ENGINE = (ROOT / "assets/2026-09-01_UniverseLab_CosmologyEngine_v1.0.js").read_text(encoding="utf-8")


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

    for element_id in (
        "H0", "Om", "Ol", "w", "s8", "beta", "ib", "rchi",
        "reset", "csv", "chart", "view-compare", "view-distance", "view-formulas",
    ):
        if f'id="{element_id}"' not in PAGE:
            raise AssertionError(f"calculator element lost: {element_id}")

    for marker in (
        '2026-09-01_UniverseLab_CosmologyEngine_v1.0.js',
        '2026-09-01_UniverseLab_CompareSafeAdapter_v2.0.js',
        'CSV speichern',
        'UNRELEASED_GROWTH_MAP',
        'UNRELEASED_LENSING_MAP',
    ):
        if marker not in PAGE:
            raise AssertionError(f"canonical calculator surface marker lost: {marker}")

    for marker in (
        'C.validateBackgroundDomain', 'C.e2FromA', 'C.ageGyr', 'C.E',
        'C.distanceModulus', 'C.transverseComovingDistance', 'C.bridgeScale',
        'CSV_BLOCKED_INVALID_DOMAIN', 'globalThis.UniverseLabCompareSafe',
        "globalThis.addEventListener('resize',schedule",
    ):
        if marker not in ADAPTER:
            raise AssertionError(f"canonical adapter logic marker lost: {marker}")

    for forbidden in (
        'function eL(', 'function eW(', 'function eB(', 'function simp(', 'function dc(',
        'Math.sqrt(Math.max(', 'Math.max(.02',
    ):
        if forbidden in PAGE or forbidden in ADAPTER or forbidden in ENGINE:
            raise AssertionError(f"forbidden legacy floor or duplicate path returned: {forbidden}")

    if 'UNRELEASED_GROWTH_MAP' not in ENGINE:
        raise AssertionError("canonical bridge growth firewall lost")

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

    start = PAGE.index('data-ul-split-key="compare-safe"')
    end = PAGE.index('</main>', start)
    workspace = PAGE[start:end]
    if workspace.count('data-ul-pane="start"') != 1 or workspace.count('data-ul-pane="end"') != 1:
        raise AssertionError("split workspace pane structure drift")

    print("PASS: UniverseLab comparison split-pane v1.1 contract")
    print("PASS: Compare SAFE uses the versioned canonical engine adapter without local floors")


if __name__ == "__main__":
    main()
