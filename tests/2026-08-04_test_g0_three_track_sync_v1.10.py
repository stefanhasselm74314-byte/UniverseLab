#!/usr/bin/env python3
"""Regression tests for G0 Background-3B canonical synchronization v1.10."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-04_validate_g0_three_track_sync_v1.10.py"

SPEC = importlib.util.spec_from_file_location("g0_background3b_v1_10", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import G0 v1.10 validator")
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def test_canonical_state() -> None:
    payload = MOD.validate()
    assert payload["status"] == "PASS"
    assert payload["background_3b_contract_status"] == "PASS"
    assert payload["run_payload_sha256"] == "625118d21d70fb563c310e985ba83126a18b8680278b7b11908c1bc550f79536"
    assert payload["seed_payload_sha256"] == "b6e4319cc29736799a0b46320002e51cd17b70b724a6b4c6e86567a316996161"
    assert payload["dependency_lock_sha256"] == "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f"
    assert payload["checkpoint"]["checkpoint_id"] == "UL-CHK-20260804-018"
    assert payload["decision"] == "UL-DEC-0025"
    assert payload["next_block"] == "C-PHYS-R1.0-BACKGROUND-3C_EXECUTION_IMPLEMENTATION_AND_AUTHORIZATION_GATE"
    assert payload["solver_implementation"] == "NOT_PRESENT"
    assert payload["solver_authorized"] is False
    assert payload["physical_evidence_effect"] == "NONE"


def test_immutable_firewall() -> None:
    payload = MOD.validate()
    gates = payload["gate_state"]
    assert gates["BACKGROUND_3B"] == "RUN_INPUT_FROZEN_EXECUTION_NOT_AUTHORIZED"
    assert gates["BACKGROUND_RUN_INPUT"] == "FROZEN_CP01"
    assert gates["BACKGROUND_SOLVER_IMPLEMENTATION"] == "NOT_PRESENT"
    assert gates["BACKGROUND_SOLVER_EXECUTION"] == "NOT_AUTHORIZED"
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
    test_immutable_firewall()
    print("PASS: G0 Background-3B canonical regression tests v1.10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
