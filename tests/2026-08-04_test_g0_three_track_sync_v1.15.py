#!/usr/bin/env python3
"""Regression tests for canonical Background-3C4 synchronization."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools/2026-08-04_validate_g0_three_track_sync_v1.15.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("g0_v115", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to import G0 v1.15 validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main():
    result = load_validator().validate()
    assert result["status"] == "PASS"
    assert result["execution_authorized"] is False
    assert result["solver_calls"] == 0
    assert result["physical_evidence_effect"] == "NONE"
    assert result["next_block"].endswith("AUTHORIZATION_REVIEW_ONLY")
    print("PASS: G0 v1.15 canonical Background-3C4 regression tests")


if __name__ == "__main__":
    main()
