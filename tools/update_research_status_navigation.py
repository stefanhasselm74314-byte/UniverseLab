#!/usr/bin/env python3
"""Synchronize the UniverseLab research-status navigation.

The migration is conservative and idempotent:
- add the research status to the main navigation after HyperLab;
- add a visible research-status card to the start page;
- add a matching link to navigation/action groups on core subpages;
- register research-status.html in sitemap.xml;
- support --check for CI drift detection.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS_HREF = "./research-status.html"
STATUS_URL = "https://stefanhasselm74314-byte.github.io/UniverseLab/research-status.html"
CORE_PAGES = (
    "index.html",
    "portal.html",
    "observatory.html",
    "journey.html",
    "compare-safe.html",
    "hyperlab.html",
    "universe3d.html",
    "validation.html",
    "guide.html",
)

ANCHOR_RE = re.compile(
    r"<a\b[^>]*href=(?P<quote>[\"'])(?P<href>[^\"']+)(?P=quote)[^>]*>.*?</a>",
    re.I | re.S,
)


def clone_anchor(anchor: str, href: str, text: str) -> str:
    """Clone an anchor's attributes while replacing href and body."""
    match = re.match(r"(?P<open><a\b[^>]*>)(?P<body>.*)</a>\s*$", anchor, re.I | re.S)
    if not match:
        raise ValueError(f"Cannot parse anchor: {anchor[:120]!r}")
    open_tag = re.sub(
        r"href=([\"']).*?\1",
        f'href="{href}"',
        match.group("open"),
        count=1,
        flags=re.I | re.S,
    )
    return f"{open_tag}{text}</a>"


def href_matches(href: str, filename: str) -> bool:
    clean = href.split("?", 1)[0].split("#", 1)[0]
    if filename == "index.html" and clean in {"", ".", "./", "/", "/UniverseLab", "/UniverseLab/"}:
        return True
    return clean in {filename, f"./{filename}", f"/{filename}", f"/UniverseLab/{filename}"}


def add_after_first_matching_anchor(text: str, candidates: tuple[str, ...]) -> tuple[str, bool]:
    if "research-status.html" in text:
        return text, False
    for match in ANCHOR_RE.finditer(text):
        href = match.group("href")
        if any(href_matches(href, candidate) for candidate in candidates):
            status_anchor = clone_anchor(match.group(0), STATUS_HREF, "Forschungsstatus")
            return text[: match.end()] + status_anchor + text[match.end() :], True
    return text, False


def update_index(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    if "research-status.html" not in text:
        text, changed = add_after_first_matching_anchor(text, ("hyperlab.html",))
        if changed:
            changes.append("main navigation")

    if "STATUS / 07" not in text:
        hyper_card = re.compile(
            r"(<article\b[^>]*class=[\"'][^\"']*card[^\"']*[\"'][^>]*>"
            r"(?:(?!</article>).)*?href=[\"'](?:\./)?hyperlab\.html[\"']"
            r"(?:(?!</article>).)*?</article>)",
            re.I | re.S,
        )
        card = (
            '<article class="card"><div class="code">STATUS / 07 · FORSCHUNG</div>'
            '<h3>Forschungsstatus</h3>'
            '<p>Gate-Lage, offene Brücken, reproduzierbare Audits und der aktuelle Stand von HPVS und HZT-M0.</p>'
            '<a href="./research-status.html"><span>Status öffnen</span><span>→</span></a></article>'
        )
        match = hyper_card.search(text)
        if not match:
            raise RuntimeError("HyperLab card not found in index.html; refusing an unsafe insertion")
        text = text[: match.end()] + "\n" + card + text[match.end() :]
        changes.append("start-page card")
    return text, changes


def update_subpage(path: Path, text: str) -> tuple[str, list[str]]:
    if path.name in {"portal.html", "research-status.html"} or "research-status.html" in text:
        return text, []
    updated, changed = add_after_first_matching_anchor(
        text,
        (
            "hyperlab.html",
            "portal.html",
            "index.html",
            "journey.html",
            "guide.html",
            "compare-safe.html",
            "compare.html",
            "observatory.html",
            "validation.html",
        ),
    )
    if not changed:
        raise RuntimeError(f"No safe navigation anchor found in {path.name}")
    return updated, ["subpage navigation"]


def update_sitemap(text: str) -> tuple[str, list[str]]:
    if STATUS_URL in text:
        return text, []
    entry = (
        "  <url>\n"
        f"    <loc>{STATUS_URL}</loc>\n"
        "    <lastmod>2026-08-01</lastmod>\n"
        "  </url>\n"
    )
    if "</urlset>" not in text:
        raise RuntimeError("sitemap.xml has no </urlset> marker")
    return text.replace("</urlset>", entry + "</urlset>", 1), ["sitemap entry"]


def planned_updates() -> dict[Path, tuple[str, list[str]]]:
    updates: dict[Path, tuple[str, list[str]]] = {}
    for name in CORE_PAGES:
        path = ROOT / name
        if not path.exists():
            raise FileNotFoundError(f"Required core page missing: {name}")
        original = path.read_text(encoding="utf-8")
        if name == "index.html":
            changed, labels = update_index(original)
        else:
            changed, labels = update_subpage(path, original)
        if changed != original:
            updates[path] = (changed, labels)

    sitemap = ROOT / "sitemap.xml"
    if not sitemap.exists():
        raise FileNotFoundError("sitemap.xml is missing")
    original = sitemap.read_text(encoding="utf-8")
    changed, labels = update_sitemap(original)
    if changed != original:
        updates[sitemap] = (changed, labels)
    return updates


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Apply updates in place")
    parser.add_argument("--check", action="store_true", help="Fail when updates are required")
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("Choose exactly one of --write or --check")

    try:
        updates = planned_updates()
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"navigation sync failed: {exc}", file=sys.stderr)
        return 2

    if args.check:
        if updates:
            for path, (_, labels) in updates.items():
                print(f"needs update: {path.relative_to(ROOT)} ({', '.join(labels)})")
            return 1
        print("research-status navigation is synchronized")
        return 0

    for path, (content, labels) in updates.items():
        path.write_text(content, encoding="utf-8")
        print(f"updated: {path.relative_to(ROOT)} ({', '.join(labels)})")
    if not updates:
        print("no navigation changes required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
