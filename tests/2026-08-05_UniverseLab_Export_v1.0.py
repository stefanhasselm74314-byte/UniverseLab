#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "assets/2026-08-05_UniverseLab_Export_v1.0.js"
CSS = ROOT / "assets/2026-08-05_UniverseLab_Export_v1.0.css"
STYLE_TAG = '<link rel="stylesheet" href="./assets/2026-08-05_UniverseLab_Export_v1.0.css">'
SCRIPT_TAG = '<script src="./assets/2026-08-05_UniverseLab_Export_v1.0.js" defer></script>'

PAGES = {
    "guide.html": ("UniverseLab Handbuch", "UniverseLab-Handbuch", "on"),
    "tafelwerk.html": ("UniverseLab Mathematisches Tafelwerk", "UniverseLab-Tafelwerk", "off"),
    "research-status.html": ("UniverseLab Forschungsstatus", "UniverseLab-Forschungsstatus", "off"),
    "hyperlab.html": ("UniverseLab HyperLab", "UniverseLab-HyperLab", "off"),
}


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing {label}: {needle}")


def main() -> None:
    js = JS.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")

    # Supported outputs and scope mechanics.
    for token in (
        "Drucken / PDF",
        "Markdown",
        "Textdatei",
        "HTML-Dokument",
        "Text kopieren",
        "Nur geöffnete Kapitel",
        "chapter:",
        "window.print()",
        "new Blob",
        "navigator.clipboard",
        "application",
    ):
        require(js, token, "export capability")

    for extension in ("'md'", "'txt'", "'html'"):
        require(js, extension, "download format")

    # No telemetry, remote transport or third-party runtime dependency.
    forbidden_js = (
        "XMLHttpRequest",
        "sendBeacon",
        "WebSocket",
        "EventSource",
        "fetch(",
        "import(",
        "eval(",
        "new Function",
    )
    for token in forbidden_js:
        if token in js:
            raise AssertionError(f"forbidden network/dynamic code path: {token}")

    # Print contract must isolate export content and support A4/PDF output.
    for token in (
        "@page",
        "size: A4",
        "body.ul-export-printing > *:not(#ul-export-print-root)",
        "#ul-export-print-root",
        "break-before: page",
        "table",
        "pre",
    ):
        require(css, token, "print stylesheet")

    if "display: none !important" not in css:
        raise AssertionError("print isolation missing")
    if "@media print" not in css:
        raise AssertionError("print media contract missing")
    if "@media (max-width: 720px)" not in css:
        raise AssertionError("mobile export controls missing")

    # Every integrated page must carry exactly one module pair and explicit metadata.
    for relative, (title, filename, page_breaks) in PAGES.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        if text.count(STYLE_TAG) != 1:
            raise AssertionError(f"stylesheet integration drift in {relative}")
        if text.count(SCRIPT_TAG) != 1:
            raise AssertionError(f"script integration drift in {relative}")
        require(text, f'data-ul-export-title="{title}"', f"title metadata in {relative}")
        require(text, f'data-ul-export-filename="{filename}"', f"filename metadata in {relative}")
        require(text, f'data-ul-export-page-breaks="{page_breaks}"', f"page-break metadata in {relative}")

    guide = (ROOT / "guide.html").read_text(encoding="utf-8")
    chapter_count = len(re.findall(r'<details\b[^>]*class="[^"]*chapter', guide, flags=re.IGNORECASE))
    if chapter_count < 4:
        raise AssertionError(f"guide chapter detection unexpectedly low: {chapter_count}")

    # Integration must remain content-preserving: exactly the head tags and body metadata are expected.
    for relative in PAGES:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if "data-ul-export=\"off\"" in text:
            raise AssertionError(f"export unexpectedly disabled in {relative}")

    print("PASS: UniverseLab export v1.0 regression contract")
    print(f"PASS: detected {chapter_count} printable guide chapters")


if __name__ == "__main__":
    main()
