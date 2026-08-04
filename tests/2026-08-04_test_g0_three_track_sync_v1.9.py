#!/usr/bin/env python3
"""Regression tests for G0 Background-3A single-cap topology v1.9."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_validate_g0_three_track_sync_v1.9.py"

SPEC = importlib.util.spec_from_file_location("g0_background3a_topology_v1_9", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import G0 v1.9 validator")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def test_canonical_state() -> None:
    payload = MOD.validate()
    assert payload["status"] == "PASS"
    assert payload["method_status"] == "PASS"
    assert payload["topology_status"] == "PASS"
    assert payload["topology_vector"] == ["N_F", "N_sigma", "m_sigma"]
    assert payload["checkpoint"]["checkpoint_id"] == "UL-CHK-20260804-017"
    assert payload["decision"] == "UL-DEC-0024"
    assert payload["next_block"] == "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY"
    assert payload["solver_authorized"] is False
    assert payload["physical_evidence_effect"] == "NONE"


def test_firewall() -> None:
    payload = MOD.validate()
    gates = payload["gate_state"]
    assert gates["BACKGROUND_3A"] == "PREREGISTERED_NOT_EXECUTED_CORRECTED_TO_SINGLE_CAP_PHASE"
    assert gates["BACKGROUND_TOPOLOGY_SCHEMA"] == "FROZEN_SINGLE_CAP_PHASE"
    assert gates["BACKGROUND_RUN_INPUT"] == "NOT_FROZEN"
    assert gates["BACKGROUND_SOLVER_EXECUTION"] == "FORBIDDEN_PENDING_BACKGROUND_3B_AND_LATER_GATE"
    assert gates["R1.1"] == "BLOCKED"
    assert gates["R1.2"] == "BLOCKED"
    assert gates["official_MD2S_solver"] == "NOT_AUTHORIZED"
    assert gates["FULL_LINEARIZED_BOUNDARY_TRACE_RANK"] == "NOT_PROVEN"
    assert gates["FREDHOLM_PROPERTY"] == "NOT_PROVEN"
    assert gates["CONTINUUM_BVP_JACOBIAN"] == "NOT_PROVEN"
    assert gates["PHYSICAL_BACKGROUND"] == "NOT_ESTABLISHED"
    assert gates["K1-D"] == "NOT_RELEASED"
    assert gates["K1-E"] == "NOT_ADMISSIBLE"
    assert gates["physical_evidence_effect"] == "NONE"


def main() -> int:
    test_canonical_state()
    test_firewall()
    print("PASS: G0 Background-3A single-cap topology regression tests v1.9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
