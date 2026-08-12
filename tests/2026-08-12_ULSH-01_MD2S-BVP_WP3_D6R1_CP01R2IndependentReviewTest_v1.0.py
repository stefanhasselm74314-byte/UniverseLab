#!/usr/bin/env python3
"""Regression harness for ULSH-01 / WP3-D6R1 independent review."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d6r1_cp01r2_independent_review_v1.0.py"

spec = importlib.util.spec_from_file_location("ulsh_wp3_d6r1_review_test", TOOL)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot import D6R1 independent reviewer")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

result = module.review()
assert result["review_status"] == "PASS_WP3_D6R1_D6_BLOCKERS_VERIFIED_CLOSED_NO_EXECUTION"
assert result["review_gates"] == "8/8_PASS"
assert result["D6-B01"] == "VERIFIED_CLOSED"
assert result["D6-B02"] == "VERIFIED_CLOSED"
assert result["new_release_blockers"] == []
assert result["old_d5_grant"] == "SPENT_NON_REPLAYABLE"
assert result["future_release_authorization_present"] is False
assert result["future_single_use_grant_present"] is False
assert result["solver_calls"] == 0
assert result["physical_solve_executed"] is False
assert result["physical_evidence_effect"] == "NONE"
assert "numpy" not in sys.modules
assert "scipy" not in sys.modules
print("PASS_WP3_D6R1_CP01R2_INDEPENDENT_REVIEW_TEST_NO_EXECUTION")
