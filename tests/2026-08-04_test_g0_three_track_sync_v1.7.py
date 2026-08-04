#!/usr/bin/env python3
"""Regression tests for the canonical Operator-2B checkpoint v1.15 state."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_validate_g0_three_track_sync_v1.7.py"

SPEC = importlib.util.spec_from_file_location("g0_operator2b_v1_7", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import G0 v1.7 validator")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def test_canonical_state() -> None:
    payload = MOD.validate()
    assert payload["status"] == "PASS"
    assert payload["decision"] == "UL-DEC-0022"
    assert payload["checkpoint"]["checkpoint_id"] == "UL-CHK-20260804-015"
    assert payload["checkpoint"]["snapshot"].endswith("SessionCheckpoint_v1.15.json")
    assert payload["operator_chain"]["trace_shape"] == "8 x 22"
    assert payload["solver_authorized"] is False
    assert payload["physical_evidence_effect"] == "NONE"


def test_immutable_gates() -> None:
    payload = MOD.validate()
    gates = payload["gate_state"]
    assert gates["R1.1"] == "BLOCKED"
    assert gates["R1.2"] == "BLOCKED"
    assert gates["FULL_LINEARIZED_BOUNDARY_TRACE_RANK"] == "NOT_PROVEN"
    assert gates["FREDHOLM_PROPERTY"] == "NOT_PROVEN"
    assert gates["CONTINUUM_BVP_JACOBIAN"] == "NOT_PROVEN"
    assert gates["PHYSICAL_BACKGROUND"] == "NOT_ESTABLISHED"
    assert gates["K1-D"] == "NOT_RELEASED"
    assert gates["K1-E"] == "NOT_ADMISSIBLE"
    assert gates["physical_evidence_effect"] == "NONE"


def main() -> int:
    test_canonical_state()
    test_immutable_gates()
    print("PASS: G0 Operator-2B canonical regression tests v1.7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
