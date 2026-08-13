#!/usr/bin/env python3
"""Validate H3 time-dependent 6D M1 cosmological closure contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry/2026-08-13_HZT-M0_S6_C-PHYS_H3_TimeDependent6D_M1_CosmologicalClosure_v0.1.json"


def git_blob_sha1(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], cwd=ROOT, text=True).strip()


def fail(msg: str) -> None:
    raise SystemExit(f"H3 validation failed: {msg}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    data = json.loads(REG.read_text(encoding="utf-8"))
    if data["status"] != "PASS_LOCAL_PARENT_TO_B2_RECONSTRUCTION_AND_MINIMAL_AXISYMMETRIC_D2NQ_NO_GO_FULL_DYNAMIC_SELECTION_STILL_OPEN":
        fail("unexpected status")
    if data["solver_execution"] is not False or data["physical_evidence_effect"] != "NONE":
        fail("execution/evidence firewall violated")

    fw = data["external_material_firewall"]
    if fw["gemini_blocks"] != "EXTERNAL_UNVERIFIED_GEMINI_DRAFT" or fw["gemini_equations_used_as_premises"]:
        fail("Gemini firewall violated")
    if fw["two_time_signature_imported"]:
        fail("two-time branch imported")

    sig = data["canonical_signature"]
    if sig["ambient_signature"] != "(-,+,+,+,+,+)" or sig["physical_times"] != 1:
        fail("canonical one-time signature changed")

    bridge = data["exact_local_parent_to_extrinsic_bridge"]
    if bridge["alpha_i"] != "-n_i[ln(n)]":
        fail("alpha bridge mismatch")
    if bridge["beta_i"] != "n_i[ln(a)]":
        fail("beta bridge mismatch")
    if bridge["B_squared"] != "delta^ij n_i[ln(a)] n_j[ln(a)]":
        fail("B^2 bridge mismatch")

    ax = data["minimal_axisymmetric_fixed_section_test"]
    if ax["normal_rank"] != 1:
        fail("minimal axisymmetric normal rank must be one")
    if ax["result"] != "NO_GO_FOR_NONZERO_B_LAMBDA_AND_B_m_IN_THE_MINIMAL_CHI_INDEPENDENT_DIAGONAL_FIXED_SECTION_SUBSECTOR":
        fail("axisymmetric no-go disposition changed")

    sel = data["selection_status"]
    if sel["S_i_equals_zero"] != "CONDITIONAL_NOT_GENERIC":
        fail("S_i incorrectly promoted")
    if sel["full_M1_D2NQ_dynamic_selection"] != "OPEN_REQUIRES_NONMINIMAL_TWO_NORMAL_TIME_DEPENDENT_CLOSURE":
        fail("full dynamic selection incorrectly closed")

    gates = data["gate_disposition"]
    expected = {
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "WP4": "BLOCKED",
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected.items():
        if gates.get(key) != value:
            fail(f"gate {key} expected {value}")

    for binding in data["source_bindings"]:
        p = ROOT / binding["path"]
        if not p.is_file():
            fail(f"missing source {binding['path']}")
        actual = git_blob_sha1(p)
        if actual != binding["git_blob_sha1"]:
            fail(f"source hash mismatch for {binding['path']}: {actual}")

    digest = hashlib.sha256(REG.read_bytes()).hexdigest()
    report = {
        "status": "PASS",
        "registry_sha256": digest,
        "source_bindings": len(data["source_bindings"]),
        "local_B2_bridge": "PASS",
        "factorized_warp_dust": "NO_GO_IN_SUBSECTOR",
        "minimal_axisymmetric_two_component_target": "NO_GO_IN_SUBSECTOR",
        "full_dynamic_selection": "OPEN",
        "K1-D": gates["K1-D"],
        "physical_evidence_effect": gates["physical_evidence_effect"],
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("[PASS] H3 time-dependent 6D M1 closure contract validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
