#!/usr/bin/env python3
"""Regression contract for retirement of the duplicate direct comparison sweep.

The historical direct-mode sweep was tied to an independent inline calculator.
After route consolidation, this test protects the opposite invariant: no legacy
sweep engine may reappear, and the canonical SAFE bridge semantics remain intact.
"""
from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECT = ROOT / "compare-direct.html"
REDIRECT = ROOT / "compare.html"
SAFE = ROOT / "compare-safe.html"
ADAPTER = ROOT / "assets/2026-09-01_UniverseLab_CompareSafeAdapter_v2.0.js"
ENGINE = ROOT / "assets/2026-09-01_UniverseLab_CosmologyEngine_v1.0.js"
OR = 9.2e-5


def e_lcdm(z: float, om: float, ode: float) -> float:
    a = 1.0 / (1.0 + z)
    ok = 1.0 - OR - om - ode
    e2 = OR / a**4 + om / a**3 + ok / a**2 + ode
    assert e2 > 0
    return math.sqrt(e2)


def bridge_delta(z: float, beta: float, ib: float, rchi: float) -> float:
    a = 1.0 / (1.0 + z)
    ac = 1.0 / (1.0 + 2.5 / max(.02, rchi))
    return beta * ib * math.exp(-((a / ac) ** 2))


def main() -> None:
    direct = DIRECT.read_text(encoding="utf-8")
    redirect = REDIRECT.read_text(encoding="utf-8")
    safe = SAFE.read_text(encoding="utf-8")
    adapter = ADAPTER.read_text(encoding="utf-8")
    engine = ENGINE.read_text(encoding="utf-8")

    for page in (direct, redirect):
        assert "./compare-safe.html" in page
        assert "location.replace(target.href)" in page
        assert "target.search=location.search" in page
        assert "target.hash=location.hash" in page
        for forbidden in (
            "function sweep(", "function sweepModel(", "function e0(", "function ew(",
            "function eb(", "function dc(", "Math.sqrt(Math.max(1e-12", "Math.sqrt(Math.max(.02",
        ):
            assert forbidden not in page, forbidden

    assert "2026-09-01_UniverseLab_CompareSafeAdapter_v2.0.js" in safe
    assert "UNRELEASED_GROWTH_MAP" in safe
    assert "UNRELEASED_LENSING_MAP" in safe
    assert "C.validateBackgroundDomain" in adapter
    assert "CSV_BLOCKED_INVALID_DOMAIN" in adapter
    assert "Math.sqrt(Math.max(" not in adapter
    assert "UNRELEASED_GROWTH_MAP" in engine

    # The canonical background channel identifies only beta_tau * I_B.
    for z in (0.0, .5, 1.0, 3.0, 8.0):
        d1 = bridge_delta(z, .05, .4, 1.0)
        d2 = bridge_delta(z, .10, .2, 1.0)
        assert abs(d1 - d2) < 1e-15

    # Omega_m remains an active LCDM background direction relative to a fixed reference.
    z, ode = 1.0, .684908
    ref = e_lcdm(z, .315, ode)
    low = e_lcdm(z, .1, ode) / ref - 1.0
    high = e_lcdm(z, .6, ode) / ref - 1.0
    assert abs(low - high) > 1e-2

    # The old arbitrary wCDM-times-bridge sweep is intentionally unavailable.
    assert 'id="w"' in safe and 'disabled' in safe
    assert "RETIRED_DUPLICATE_ENGINE" in (ROOT / "compare-app.js").read_text(encoding="utf-8")

    print("UniverseLab compare sweep retirement/consolidation regression: PASS")


if __name__ == "__main__":
    main()
