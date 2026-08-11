#!/usr/bin/env python3
"""Regression contract for UniverseLab 2.2 parameter-sweep semantics.

This is intentionally a no-network, no-browser static/numerical sanity test.
It protects the model routing that was exposed by the 2026-08-11 manual sweep
checks: w must route through wCDM, beta/I_B through the effective bridge, and
Omega_m through LambdaCDM. Delta-H/H in the sweep is sensitivity relative to
the current global parameter point in that same model.
"""
from __future__ import annotations

from pathlib import Path
import math
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "compare-direct.html"
REDIRECT = ROOT / "compare.html"
OR = 9.2e-5


def e0(z: float, om: float, ol: float) -> float:
    a = 1.0 / (1.0 + z)
    ok = 1.0 - OR - om - ol
    return math.sqrt(max(1e-12, OR / a**4 + om / a**3 + ok / a**2 + ol))


def ew(z: float, om: float, ol: float, w: float) -> float:
    a = 1.0 / (1.0 + z)
    ok = 1.0 - OR - om - ol
    return math.sqrt(max(1e-12, OR / a**4 + om / a**3 + ok / a**2 + ol * a ** (-3.0 * (1.0 + w))))


def main() -> None:
    html = PAGE.read_text(encoding="utf-8")
    redirect = REDIRECT.read_text(encoding="utf-8")

    assert "function sweepModel(k){return k==='w'?1:(k==='b'||k==='ib'?2:0)}" in html
    assert "const x=lo+(hi-lo)*i/60,pp=P({[k]:x})" in html
    assert "href=H(z,p,model)" in html
    assert "(H(z,pp,model)/href-1)*100" in html
    assert "q(z,pp,model)" in html
    assert "mu(z,pp,model)" in html
    assert "age(pp,model)" in html
    assert "cv('#schart',[{c:'#68cfff',d}],lo,hi)" in html
    assert "x-Achse: tatsächlicher Parameterwert" in html

    match = re.search(r"function sweep\(\)\{(.*?)\}function table", html, re.S)
    assert match, "sweep() block not found"
    sweep = match.group(1)
    assert "q(z,pp,2)" not in sweep
    assert "mu(z,pp,2)" not in sweep
    assert "age(pp,2)" not in sweep
    assert "d.map((v,i)=>({x:i" not in sweep

    # w must visibly affect H in wCDM at z=1.
    om, ol, z = 0.315, 0.684908, 1.0
    ref_w = -1.0
    h_ref = ew(z, om, ol, ref_w)
    dh_low = ew(z, om, ol, -1.5) / h_ref - 1.0
    dh_high = ew(z, om, ol, -0.5) / h_ref - 1.0
    assert abs(dh_low - dh_high) > 1e-3

    # Omega_m sensitivity is evaluated against the fixed global reference point,
    # not divided by an LCDM curve carrying the same swept Omega_m.
    h_om_ref = e0(z, om, ol)
    dh_om_low = e0(z, 0.1, ol) / h_om_ref - 1.0
    dh_om_high = e0(z, 0.6, ol) / h_om_ref - 1.0
    assert abs(dh_om_low - dh_om_high) > 1e-2

    assert "compare-direct.html?v=23" in redirect
    print("UniverseLab compare sweep regression: PASS")


if __name__ == "__main__":
    main()
