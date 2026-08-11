#!/usr/bin/env python3
"""Regression tests for ULSH-01 WP3-D1, strictly no physical solve."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d1_failure_diagnosis_v1.0.py"
CONTRACT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D1_CP01R1FailureDiagnosis_CP01R2Protocol_v1.0.json"
MATRIX = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D1_CP01R1FailureDiagnosticMatrix_v1.0.json"

spec = importlib.util.spec_from_file_location("ulsh_wp3_d1", TOOL)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

audit = module.audit()
assert audit["status"] == "PASS_WP3_D1_DIAGNOSIS_AUDIT_CP01R2_DESIGN_NO_EXECUTION"
assert audit["solver_calls"] == 0
assert audit["physical_solve_authorized"] is False
assert audit["physical_solve_executed"] is False
assert audit["physical_evidence_effect"] == "NONE"

contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
assert contract["cp01r2_protocol_design"]["state"] == "DESIGNED_NOT_AUTHORIZED_NOT_EXECUTED"
assert contract["governance"]["K1-D"] == "NOT_RELEASED"
assert contract["governance"]["K1-E"] == "NOT_ADMISSIBLE"
assert contract["governance"]["WP4"] == "BLOCKED"
assert matrix["aggregate"]["trust_cap_active_iterations"] == matrix["aggregate"]["total_newton_iterations"] == 1967
assert matrix["aggregate"]["max_iteration_entries"] == 30
assert matrix["aggregate"]["max_iteration_rejected_iterations"] == 0
assert matrix["aggregate"]["trust_radius_failure_entries"] == 4
assert matrix["aggregate"]["rrqr_failure_entries"] == 1

# The R2 design must expand for a high-quality clipped step without demanding a
# 75% one-step raw residual collapse, which was the CP01R1 source-level trap.
assert module.r2_radius_update(1.0, 0.90, 1.0) == 2.0
assert module.r2_radius_update(1.0, 0.10, 1.0) == 0.25
assert module.r2_radius_update(1.0, 0.50, 1.0) == 1.0

# Continuation is deterministic and requires >=10% original-residual progress.
assert module.progress_continuation_eligible(initial=1.0, final=0.90, finite=True, admissible=True, timed_out=False)
assert not module.progress_continuation_eligible(initial=1.0, final=0.9000001, finite=True, admissible=True, timed_out=False)
assert not module.progress_continuation_eligible(initial=1.0, final=0.50, finite=True, admissible=False, timed_out=False)
assert not module.progress_continuation_eligible(initial=1.0, final=0.50, finite=True, admissible=True, timed_out=True)

print("PASS_WP3_D1_FAILURE_DIAGNOSIS_TEST_NO_EXECUTION")
