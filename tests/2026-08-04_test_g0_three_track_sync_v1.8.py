#!/usr/bin/env python3
"""Regression tests for G0 Background-3A canonical synchronization v1.8."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_validate_g0_three_track_sync_v1.8.py"

SPEC = importlib.util.spec_from_file_location("g0_background3a_v1_8", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import G0 v1.8 validator")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def test_canonical_background_3a_state() -> None:
    payload = MOD.validate()
    assert payload["status"] == "PASS"
    assert payload["decision"] == "UL-DEC-0023"
    assert payload["checkpoint"]["checkpoint_id"] == "UL-CHK-20260804-016"
    assert payload["background_3a"]["execution"] == "NOT_EXECUTED"
    assert payload["background_3a"]["node_levels"] == [24, 32, 48, 64, 96]
    assert payload["background_3a"]["seed_count"] == 7
    assert payload["next_recommended_block"] == "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY"
    assert payload["solver_authorized"] is False
    assert payload["physical_evidence_effect"] == "NONE"


def test_immutable_firewall() -> None:
    payload = MOD.validate()
    gates = payload["gate_state"]
    assert gates["BACKGROUND_3A"] == "PREREGISTERED_NOT_EXECUTED"
    assert gates["BACKGROUND_METHOD"] == "FROZEN_PREREGISTERED"
    assert gates["BACKGROUND_RUN_INPUT"] == "NOT_FROZEN"
    assert gates["BACKGROUND_SOLVER_EXECUTION"] == "FORBIDDEN_PENDING_BACKGROUND_3B_AND_LATER_GATE"
    assert gates["R1.1"] == "BLOCKED"
    assert gates["R1.2"] == "BLOCKED"
    assert gates["FULL_LINEARIZED_BOUNDARY_TRACE_RANK"] == "NOT_PROVEN"
    assert gates["FREDHOLM_PROPERTY"] == "NOT_PROVEN"
    assert gates["CONTINUUM_BVP_JACOBIAN"] == "NOT_PROVEN"
    assert gates["PHYSICAL_BACKGROUND"] == "NOT_ESTABLISHED"
    assert gates["official_MD2S_solver"] == "NOT_AUTHORIZED"
    assert gates["K1-D"] == "NOT_RELEASED"
    assert gates["K1-E"] == "NOT_ADMISSIBLE"
    assert gates["physical_evidence_effect"] == "NONE"


def main() -> int:
    test_canonical_background_3a_state()
    test_immutable_firewall()
    print("PASS: G0 Background-3A canonical regression tests v1.8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
