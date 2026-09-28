#!/usr/bin/env python3
"""Regression guard for Band V-B public metadata reconciliation."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"


def main() -> None:
    text = SITEMAP.read_text(encoding="utf-8")
    exact = (
        "<loc>https://stefanhasselm74314-byte.github.io/UniverseLab/observatory-en.html</loc>"
        "<lastmod>2026-09-03</lastmod>"
    )
    assert exact in text
    assert (
        "<loc>https://stefanhasselm74314-byte.github.io/UniverseLab/observatory-en.html</loc>"
        "<lastmod>2026-08-19</lastmod>"
    ) not in text
    assert text.count("<loc>https://stefanhasselm74314-byte.github.io/UniverseLab/observatory-en.html</loc>") == 1
    print("UniverseLab Band V-B sitemap lastmod regression: PASS")


if __name__ == "__main__":
    main()
