#!/usr/bin/env python3
"""Hardened firewall resolver for the post-migration current-main reconciliation."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_VALIDATOR = ROOT / "tools/2026-09-01_validate_UniverseLab_PostMigrationCurrentMainReconciliation_v1.0.py"
_spec = importlib.util.spec_from_file_location("ul_post_migration_reconciliation_v10", BASE_VALIDATOR)
assert _spec and _spec.loader
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)


def assert_firewalls(obj: dict[str, Any], *, context: str) -> None:
    candidates = []
    for key in ("physical_governance", "gate_state", "governance", "gates", "scientific_status_effect"):
        block = obj.get(key)
        if isinstance(block, dict) and ("K1-D" in block or "K1-E" in block):
            candidates.append((key, block))
    if not candidates and ("K1-D" in obj or "K1-E" in obj):
        candidates.append(("top_level", obj))
    assert candidates, f"{context}: no explicit K1 firewall block"
    for key, block in candidates:
        assert block.get("K1-D") == "NOT_RELEASED", f"{context}/{key}: K1-D promotion detected"
        assert block.get("K1-E") == "NOT_ADMISSIBLE", f"{context}/{key}: K1-E promotion detected"
    evidence_values = []
    for key, block in candidates:
        if "physical_evidence_effect" in block:
            evidence_values.append((key, block["physical_evidence_effect"]))
    if "physical_evidence_effect" in obj:
        evidence_values.append(("top_level", obj["physical_evidence_effect"]))
    assert evidence_values, f"{context}: no explicit physical evidence effect"
    assert all(value == "NONE" for _, value in evidence_values), f"{context}: physical evidence effect must remain NONE: {evidence_values}"
    assert obj.get("physical_gate_effect", "NONE") == "NONE", f"{context}: physical gate effect must remain NONE"


base.assert_firewalls = assert_firewalls


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    base.validate(args.root.resolve())


if __name__ == "__main__":
    main()
