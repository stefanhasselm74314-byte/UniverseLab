#!/usr/bin/env python3
"""Correct nested manifest fields after Background-3C6 canonicalization."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-manifest.json"
NEXT_BLOCK = "C-PHYS-R1.0-BACKGROUND-3C7_INTEGRATED_RELEASE_AUTHORIZATION_REVIEW_ONLY"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = manifest.setdefault("parent_action_v0_1", {})
    parent["next_block"] = NEXT_BLOCK
    operator = manifest.setdefault("c_phys_operator_entry", {})
    operator["status"] = "BACKGROUND_3C6_CONTROL_RELEASE_AUDITED_AUTHORIZATION_REVIEW_REMAINING"
    operator["solver_authorized"] = False
    operator["next_block"] = NEXT_BLOCK
    text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    forbidden = (
        '"next_block": "C-PHYS-R1.0-BACKGROUND-3C6_INTEGRATED_EXECUTION_RELEASE_IMPLEMENTATION_ONLY"',
        '"status": "BACKGROUND_3C_AUTHORIZATION_DENIED_EXECUTION_RUNNER_MISSING"',
    )
    if any(token in text for token in forbidden):
        raise RuntimeError("stale nested Background-3C manifest status remains")
    MANIFEST.write_text(text, encoding="utf-8")
    print("PASS: nested Background-3C6 manifest drift corrected")


if __name__ == "__main__":
    main()
