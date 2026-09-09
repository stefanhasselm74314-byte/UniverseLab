#!/usr/bin/env python3
"""Deterministic regression guard for the known-dead GSRA / Orion Pulse links.

This test deliberately performs no network requests.  It protects the public link
hub against accidentally re-introducing the three external targets that were
verified dead on 2026-09-09.  A future replacement may be activated only by
updating the link hub and this guard together after the replacement has been
explicitly verified and canonically assigned.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINKS = ROOT / "links.html"
REGISTER = ROOT / "ACTIVE_LINKS.md"

DEAD_TARGETS = {
    "GSRA Source Brief": "https://github.com/stefanhasselm74314-byte/gsra-orion-pulse/blob/main/docs/2026-08-19_GSRA-OrionPulse_SourceLinkBrief_v1.0.md",
    "Telemetry Contract": "https://docs.google.com/document/d/1EUwZhP8MEMfLz1Ocb_r7UxIA5doTiSCM59PCqiLHcco/edit",
    "Release Notes": "https://docs.google.com/document/d/1CCKgG5dmBkjHNiiVLm7RoKM8nfzmlhDpTTqiVpJsytM/edit",
}


def extract_gsra_section(html: str) -> str:
    match = re.search(
        r'<section class="sec"><h2>GSRA / Orion Pulse · separates Projekt</h2>.*?</section>',
        html,
        flags=re.DOTALL,
    )
    assert match is not None, "GSRA / Orion Pulse section is missing from links.html"
    return match.group(0)


def main() -> None:
    html = LINKS.read_text(encoding="utf-8")
    register = REGISTER.read_text(encoding="utf-8")
    section = extract_gsra_section(html)

    # The three historically dead targets must not silently return as active URLs.
    for label, url in DEAD_TARGETS.items():
        assert url not in html, f"Known-dead target reintroduced in links.html: {label}"
        assert url not in register, f"Known-dead target reintroduced in ACTIVE_LINKS.md: {label}"

    # Until a verified successor contract exists, the public cards stay fail-closed.
    for label in ("Source Brief", "Telemetry Contract", "Release Notes"):
        assert f"<h3>{label}</h3>" in section, f"Missing GSRA card: {label}"

    assert section.count('class="tag blocked"') == 3, "All three GSRA cards must remain BLOCKIERT"
    assert section.count('class="dead"') == 3, "All three GSRA cards must remain non-clickable"
    assert "<a " not in section, "GSRA section contains an active link without a verified successor contract"
    assert section.count("Nicht verfügbar") == 3, "Blocked cards must visibly state Nicht verfügbar"

    # The canonical text register must preserve the same fail-closed status and recovery rule.
    assert "## 8. GSRA / Orion Pulse — separates Projekt" in register
    assert register.count("**BLOCKIERT / KEIN KANONISCHES ZIEL**") >= 3
    assert "Alte 404-Ziele dürfen nicht reaktiviert werden." in register

    print("PASS: known-dead GSRA / Orion Pulse targets remain blocked and non-clickable")


if __name__ == "__main__":
    main()
