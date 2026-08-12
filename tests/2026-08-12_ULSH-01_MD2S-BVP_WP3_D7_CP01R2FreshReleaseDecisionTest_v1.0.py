#!/usr/bin/env python3
"""Regression checks for WP3-D7. No physical execution."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d7_cp01r2_fresh_release_decision_v1.0.py"

spec = importlib.util.spec_from_file_location("ulsh_d7_release_decision", TOOL)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

result = module.validate()
assert result["status"] == module.EXPECTED_STATUS
assert result["release_blockers"] == []
assert result["fresh_runtime_recheck_required"] is True
assert result["future_release_authorization_present"] is False
assert result["future_single_use_grant_present"] is False
assert result["solver_calls"] == 0
assert result["physical_solve_executed"] is False
assert result["physical_evidence_effect"] == "NONE"
assert "numpy" not in sys.modules
assert "scipy" not in sys.modules

# Decision-only regression: runtime artifacts must not be committed by this WP.
assert not module.FUTURE_RELEASE.exists()
assert not module.FUTURE_GRANT.exists()
print("PASS: WP3-D7 fresh release decision is internally consistent and no-execution")
