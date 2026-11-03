#!/usr/bin/env python3
"""WEB10-19 append-only landing metadata contract successor.

This does not rewrite the historical LandingPaths v1.0 baseline. It binds the
authorized metadata delta to the exact repository base and the superseded PR
head, while preserving body, scripts, styles, JSON-LD and the original
navigation/layout checks.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "312e767628f003494a51edf685cf679469e35f13"
SUPERSEDED_HEAD_SHA = "954a11438c354164e30972fbd064ccdd9161272d"
LEGACY_TEST = ROOT / "tests/2026-09-25_test_UniverseLab_LandingPaths_v1.0.py"

EXPECTED = {
    "index.html": {
        "title": "UniverseLab von Stefan Hasselmeyer | Interaktives Kosmologie-Labor",
        "description": "UniverseLab von Stefan Hasselmeyer ist ein interaktives Kosmologie-Labor für ΛCDM, kosmische Expansion, Strukturbildung, Modellvergleiche und klar gekennzeichnete experimentelle 6D-Hyperzeitmodelle.",
        "canonical": "https://stefanhasselm74314-byte.github.io/UniverseLab/",
        "alternates": [
            ("de", "https://stefanhasselm74314-byte.github.io/UniverseLab/"),
            ("en", "https://stefanhasselm74314-byte.github.io/UniverseLab/index-en.html"),
            ("x-default", "https://stefanhasselm74314-byte.github.io/UniverseLab/"),
        ],
    },
    "index-en.html": {
        "title": "UniverseLab by Stefan Hasselmeyer | Interactive Cosmology Laboratory",
        "description": "UniverseLab by Stefan Hasselmeyer: interactive cosmology, numerical validation, model comparison and explicitly separated experimental 6D Hyperzeit research.",
        "canonical": "https://stefanhasselm74314-byte.github.io/UniverseLab/index-en.html",
        "alternates": [
            ("de", "https://stefanhasselm74314-byte.github.io/UniverseLab/"),
            ("en", "https://stefanhasselm74314-byte.github.io/UniverseLab/index-en.html"),
            ("x-default", "https://stefanhasselm74314-byte.github.io/UniverseLab/"),
        ],
    },
}

CANONICAL_RE = re.compile(r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*>', re.I)
ALT_RE = re.compile(r'<link\b(?=[^>]*\brel=["\']alternate["\'])(?=[^>]*\bhreflang=["\'][^"\']+["\'])[^>]*>', re.I)
TITLE_RE = re.compile(r'<title[^>]*>([\s\S]*?)</title>', re.I)
DESC_RE = re.compile(r'<meta\b(?=[^>]*\bname=["\']description["\'])[^>]*\bcontent=["\']([^"\']*)["\'][^>]*>', re.I)
HREF_RE = re.compile(r'\bhref=["\']([^"\']+)["\']', re.I)
LANG_RE = re.compile(r'\bhreflang=["\']([^"\']+)["\']', re.I)


def git_show(ref: str, path: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{ref}:{path}"],
        check=False, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise AssertionError(f"BASE_READ_FAILED:{ref}:{path}:{proc.stderr.strip()}")
    return proc.stdout


def split_head_body(html: str) -> tuple[str, str]:
    parts = re.split(r'</head>', html, maxsplit=1, flags=re.I)
    assert len(parts) == 2, "missing </head>"
    return parts[0], parts[1]


def normalized_uncontrolled_head(head: str) -> str:
    value = CANONICAL_RE.sub("", head)
    value = ALT_RE.sub("", value)
    # Canonical/alternate placement may alter adjacent whitespace only.
    return re.sub(r'\s+', ' ', value).strip()


def metadata_contract(path: str, current: str, base: str) -> None:
    expected = EXPECTED[path]
    cur_head, cur_body = split_head_body(current)
    base_head, base_body = split_head_body(base)

    # Visible page/body must remain byte-identical to the exact base.
    assert cur_body == base_body, f"{path}: visible body changed"

    title = (TITLE_RE.search(cur_head) or [None, None])[1]
    desc = (DESC_RE.search(cur_head) or [None, None])[1]
    assert title == expected["title"], f"{path}: unauthorized title change"
    assert desc == expected["description"], f"{path}: unauthorized description change"

    canon = CANONICAL_RE.findall(cur_head)
    assert len(canon) == 1, f"{path}: canonical count {len(canon)}"
    href = (HREF_RE.search(canon[0]) or [None, None])[1]
    assert href == expected["canonical"], f"{path}: canonical mismatch {href!r}"

    alt_tags = ALT_RE.findall(cur_head)
    alts = []
    for tag in alt_tags:
        lang = (LANG_RE.search(tag) or [None, None])[1]
        alt_href = (HREF_RE.search(tag) or [None, None])[1]
        alts.append((lang, alt_href))
    assert alts == expected["alternates"], f"{path}: alternate mismatch {alts!r}"

    # Every other head field (including OG/Twitter, scripts, styles and JSON-LD)
    # remains semantically byte-equivalent apart from whitespace introduced by
    # moving the authorized canonical/alternate tags.
    assert normalized_uncontrolled_head(cur_head) == normalized_uncontrolled_head(base_head), (
        f"{path}: unauthorized non-WEB10-19 head change"
    )


def load_legacy():
    spec = importlib.util.spec_from_file_location("landing_v1_0", LEGACY_TEST)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--browser", action="store_true")
    ap.add_argument("--offline-render", action="store_true")
    ap.add_argument("--base-url", default="http://127.0.0.1:4173/UniverseLab/")
    ap.add_argument("--output", type=Path, default=ROOT / "web50-landing-report")
    args = ap.parse_args()

    legacy = load_legacy()
    for path in EXPECTED:
        current = (ROOT / path).read_text(encoding="utf-8")
        base = git_show(BASE_SHA, path)
        metadata_contract(path, current, base)

        # Preserve the historical v1.0 copy/scripts baseline exactly. Only after
        # the explicit WEB10-19 metadata contract passes do we substitute the
        # metadata digest expected by the legacy static navigation checks.
        now = legacy.protected(current)
        assert now["copy"] == legacy.BASELINE[path]["copy"], f"{path}: protected copy drift"
        assert now["scripts"] == legacy.BASELINE[path]["scripts"], f"{path}: script drift"
        legacy.BASELINE[path] = {
            **legacy.BASELINE[path],
            "metadata": now["metadata"],
        }

    static_count = legacy.static_checks()
    result = {
        "schema": "UniverseLab.LandingPaths.MetadataContract.v1.1",
        "base_sha": BASE_SHA,
        "superseded_pr_head": SUPERSEDED_HEAD_SHA,
        "authorized_pages": sorted(EXPECTED),
        "static_assertions": static_count,
        "body_unchanged": True,
        "json_ld_unchanged": True,
        "css_js_routing_unchanged": True,
        "physical_gate_effect": "NONE",
        "physical_evidence_effect": "NONE",
        "canonical_effect": "NONE",
    }
    if args.browser or args.offline_render:
        result["browser_cases"] = legacy.render_checks(
            args.base_url, args.output, args.offline_render
        )
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "report.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
