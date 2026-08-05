#!/usr/bin/env python3
"""Integrate the shared UniverseLab export layer into text-heavy public pages.

This tool is intentionally narrow and idempotent. It adds only:
- one export stylesheet link,
- one deferred export script,
- page-specific body data attributes.

It never rewrites page content, inline application scripts, scientific status text,
or existing styles.
"""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
STYLE = '<link rel="stylesheet" href="./assets/2026-08-05_UniverseLab_Export_v1.0.css">'
SCRIPT = '<script src="./assets/2026-08-05_UniverseLab_Export_v1.0.js" defer></script>'

PAGES = {
    "guide.html": {
        "title": "UniverseLab Handbuch",
        "filename": "UniverseLab-Handbuch",
        "page_breaks": "on",
    },
    "tafelwerk.html": {
        "title": "UniverseLab Mathematisches Tafelwerk",
        "filename": "UniverseLab-Tafelwerk",
        "page_breaks": "off",
    },
    "research-status.html": {
        "title": "UniverseLab Forschungsstatus",
        "filename": "UniverseLab-Forschungsstatus",
        "page_breaks": "off",
    },
    "hyperlab.html": {
        "title": "UniverseLab HyperLab",
        "filename": "UniverseLab-HyperLab",
        "page_breaks": "off",
    },
}


def inject_head(text: str) -> str:
    if text.count(STYLE) > 1 or text.count(SCRIPT) > 1:
        raise RuntimeError("duplicate export integration detected")
    additions = []
    if STYLE not in text:
        additions.append(STYLE)
    if SCRIPT not in text:
        additions.append(SCRIPT)
    if not additions:
        return text
    if "</head>" not in text:
        raise RuntimeError("missing </head>")
    return text.replace("</head>", "\n".join(additions) + "\n</head>", 1)


def inject_body_attributes(text: str, *, title: str, filename: str, page_breaks: str) -> str:
    match = re.search(r"<body(?P<attrs>[^>]*)>", text, flags=re.IGNORECASE)
    if not match:
        raise RuntimeError("missing <body> tag")
    attrs = match.group("attrs")
    required = {
        "data-ul-export-title": title,
        "data-ul-export-filename": filename,
        "data-ul-export-page-breaks": page_breaks,
    }
    for key, value in required.items():
        pattern = rf'\s{re.escape(key)}="[^"]*"'
        replacement = f' {key}="{value}"'
        if re.search(pattern, attrs):
            attrs = re.sub(pattern, replacement, attrs, count=1)
        else:
            attrs += replacement
    return text[: match.start()] + f"<body{attrs}>" + text[match.end() :]


def main() -> None:
    changed = []
    for relative, settings in PAGES.items():
        path = ROOT / relative
        original = path.read_text(encoding="utf-8")
        updated = inject_head(original)
        updated = inject_body_attributes(updated, **settings)
        if updated.count(STYLE) != 1 or updated.count(SCRIPT) != 1:
            raise RuntimeError(f"integration count failed for {relative}")
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(relative)
    print("Integrated export layer:", ", ".join(changed) if changed else "already current")


if __name__ == "__main__":
    main()
