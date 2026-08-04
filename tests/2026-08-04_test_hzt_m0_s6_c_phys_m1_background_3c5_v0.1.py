#!/usr/bin/env python3
"""Regression tests for Background-3C5 fail-closed authorization review."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3c5_v0.1.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("background3c5_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to import Background-3C5 validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main():
    result = load_validator().validate()
    assert result["status"] == "PASS"
    assert result["review_status"] == "DENIED_INTEGRATED_EXECUTION_RELEASE_INCOMPLETE"
    assert result["integrated_execution_release"] == "INCOMPLETE"
    assert result["grant_created"] is False
    assert result["solver_calls"] == 0
    assert result["result_artifact_created"] is False
    assert result["physical_evidence_effect"] == "NONE"
    assert result["next_block"].endswith("IMPLEMENTATION_ONLY")
    print("PASS: Background-3C5 authorization review regression tests")


if __name__ == "__main__":
    main()
