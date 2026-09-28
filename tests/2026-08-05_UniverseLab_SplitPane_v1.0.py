#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "assets/2026-08-05_UniverseLab_SplitPane_v1.0.js"
CSS = ROOT / "assets/2026-08-05_UniverseLab_SplitPane_v1.0.css"
OBSERVATORY_ADAPTER = ROOT / "assets/2026-09-01_UniverseLab_ObservatoryAdapter_v1.5.js"
STYLE = '<link rel="stylesheet" href="./assets/2026-08-05_UniverseLab_SplitPane_v1.0.css">'
SCRIPT = '<script src="./assets/2026-08-05_UniverseLab_SplitPane_v1.0.js" defer></script>'

PAGES = {
    "observatory.html": {
        "key": "observatory",
        "label": "Parameter",
        "default": "300",
        "minimum": "240",
        "maximum": "520",
        "end_minimum": "520",
    },
    "tafelwerk.html": {
        "key": "tafelwerk",
        "label": "Formelauswahl",
        "default": "360",
        "minimum": "280",
        "maximum": "580",
        "end_minimum": "560",
    },
}


def require(text: str, token: str, label: str) -> None:
    if token not in text:
        raise AssertionError(f"missing {label}: {token}")


def main() -> None:
    js = JS.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")

    for token in (
        "pointerdown",
        "pointermove",
        "pointerup",
        "setPointerCapture",
        "localStorage",
        "ArrowLeft",
        "ArrowRight",
        "Home",
        "End",
        "dblclick",
        "role', 'separator",
        "aria-valuemin",
        "aria-valuemax",
        "aria-valuenow",
        "universelab:split-pane-change",
        "window.dispatchEvent(new Event('resize'))",
        "Layout zurücksetzen",
        "ausblenden",
        "anzeigen",
    ):
        require(js, token, "split-pane behavior")

    for forbidden in (
        "fetch(",
        "XMLHttpRequest",
        "sendBeacon",
        "WebSocket",
        "EventSource",
        "eval(",
        "new Function",
    ):
        if forbidden in js:
            raise AssertionError(f"forbidden network or dynamic-code path: {forbidden}")

    for token in (
        "@media (min-width: 901px)",
        "@media (max-width: 900px)",
        "grid-template-columns: minmax(0, var(--ul-split-start)) 12px minmax(0, 1fr)",
        "grid-template-columns: 0 34px minmax(0, 1fr)",
        "cursor: col-resize",
        "touch-action: none",
        "ul-split-collapsed",
        "ul-split-dragging",
        "width: min(1480px, calc(100% - 28px))",
    ):
        require(css, token, "split-pane style")

    # Mobile must restore visible stacked panes and hide only the desktop controls.
    require(css, ".ul-split-controls,\n  .ul-splitter", "mobile control suppression")
    require(css, "grid-template-columns: minmax(0, 1fr) !important", "mobile stack")
    require(css, "opacity: 1 !important", "mobile pane visibility")
    require(css, "pointer-events: auto !important", "mobile pane interaction")

    for relative, expected in PAGES.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        if text.count(STYLE) != 1 or text.count(SCRIPT) != 1:
            raise AssertionError(f"asset integration drift in {relative}")
        if text.count('data-ul-split ') != 1:
            raise AssertionError(f"split root count drift in {relative}")
        if text.count('data-ul-pane="start"') != 1:
            raise AssertionError(f"start pane count drift in {relative}")
        if text.count('data-ul-pane="end"') != 1:
            raise AssertionError(f"end pane count drift in {relative}")
        for field, value in expected.items():
            attribute = {
                "key": "data-ul-split-key",
                "label": "data-ul-split-label",
                "default": "data-ul-split-default",
                "minimum": "data-ul-split-min",
                "maximum": "data-ul-split-max",
                "end_minimum": "data-ul-split-end-min",
            }[field]
            require(text, f'{attribute}="{value}"', f"{field} contract in {relative}")

    observatory = (ROOT / "observatory.html").read_text(encoding="utf-8")
    observatory_adapter = OBSERVATORY_ADAPTER.read_text(encoding="utf-8")
    for token in (
        '<canvas id="chart">',
        '2026-09-01_UniverseLab_ObservatoryAdapter_v1.5.js',
        'id="H0"',
        'id="Om"',
    ):
        require(observatory, token, "Observatory page continuity")
    for token in (
        "globalThis.addEventListener('resize',schedule",
        "globalThis.UniverseLabObservatory",
        "C.distanceModulus",
        "C.baoDMOverRd",
        "C.solveGrowth",
    ):
        require(observatory_adapter, token, "Observatory adapter continuity")

    tafelwerk = (ROOT / "tafelwerk.html").read_text(encoding="utf-8")
    for token in (
        "UniverseLab_Export_v1.0.css",
        "UniverseLab_Export_v1.0.js",
        'id="formulaList"',
        'id="formulaResult"',
    ):
        require(tafelwerk, token, "Tafelwerk continuity")

    print("PASS: UniverseLab split-pane v1.0 regression contract")
    print("PASS: Observatory and Tafelwerk preserve their scientific application anchors")


if __name__ == "__main__":
    main()
