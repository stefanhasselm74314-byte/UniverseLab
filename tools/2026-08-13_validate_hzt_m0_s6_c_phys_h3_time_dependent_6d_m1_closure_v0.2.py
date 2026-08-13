#!/usr/bin/env python3
"""Validate corrected H3 v0.2 time-dependent 6D M1 closure contract."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry/2026-08-13_HZT-M0_S6_C-PHYS_H3_TimeDependent6D_M1_CosmologicalClosure_v0.2.json"


def blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], cwd=ROOT, text=True).strip()


def fail(msg: str) -> None:
    raise SystemExit(f"H3 v0.2 validation failed: {msg}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    d = json.loads(REG.read_text(encoding="utf-8"))

    if d["version"] != "0.2.0": fail("wrong version")
    if d["solver_execution"] is not False or d["physical_evidence_effect"] != "NONE": fail("execution/evidence firewall")
    if d["external_material_firewall"]["gemini_blocks"] != "EXTERNAL_UNVERIFIED_GEMINI_DRAFT": fail("Gemini firewall")
    if d["canonical_signature"]["physical_times"] != 1: fail("one-time signature changed")

    sup = d["supersedes"]
    sp = ROOT / sup["path"]
    if blob(sp) != sup["git_blob_sha1"]: fail("superseded v0.1 binding mismatch")

    for b in d["source_bindings"]:
        p = ROOT / b["path"]
        if not p.is_file() or blob(p) != b["git_blob_sha1"]:
            fail(f"source binding mismatch: {b['path']}")

    c = d["rank_one_counterexample"]
    if c["v0_1_no_go"] != "FALSIFIED_BY_EXPLICIT_RANK_ONE_COUNTEREXAMPLE": fail("v0.1 no-go not retracted")
    if d["corrected_axisymmetric_disposition"]["answer"] != "OPEN": fail("dynamic selection incorrectly closed")

    g = d["gate_disposition"]
    if g["H3_v0_1_rank_one_no_go"] != "RETRACTED_FALSIFIED_BY_COUNTEREXAMPLE": fail("correction gate missing")
    for k, v in {"K1-D":"NOT_RELEASED", "K1-E":"NOT_ADMISSIBLE", "WP4":"BLOCKED", "physical_evidence_effect":"NONE"}.items():
        if g.get(k) != v: fail(f"gate {k}")

    out = {
        "status": "PASS",
        "h3_v0_1_rank_one_no_go": "RETRACTED",
        "rank_one_target_realisability": "PASS_KINEMATIC_SOURCE_FREE",
        "factorized_warp_dust": "NO_GO_IN_SUBSECTOR",
        "full_parent_dynamic_selection": "OPEN",
        "K1-D": "NOT_RELEASED",
        "physical_evidence_effect": "NONE"
    }
    print(json.dumps(out, indent=2, sort_keys=True) if args.json else "[PASS] H3 v0.2 correction validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
