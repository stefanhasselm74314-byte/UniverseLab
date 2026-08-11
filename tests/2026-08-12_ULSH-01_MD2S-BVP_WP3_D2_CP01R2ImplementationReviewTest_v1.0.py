#!/usr/bin/env python3
"""Regression tests for ULSH-01 WP3-D2; physical execution is forbidden."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d2_cp01r2_etrn_v1.0.py"
REVIEW_TOOL = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d2_independent_protocol_review_v1.0.py"
CONTRACT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D2_CP01R2ImplementationContract_v1.0.json"
REVIEW = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D2_CP01R2IndependentProtocolReview_v1.0.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


impl = load_module("ulsh_wp3_d2_impl_test", IMPLEMENTATION)
reviewer = load_module("ulsh_wp3_d2_review_test", REVIEW_TOOL)

# Implementation audit must be no-execution and preserve the exact 7x5 schedule.
audit = impl.audit()
assert audit["status"] == "PASS_WP3_D2_ETRN01_IMPLEMENTATION_AUDIT_NO_EXECUTION"
assert audit["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2"
assert audit["schedule_entries"] == 35
assert audit["physical_backend_imported"] is False
assert audit["physical_solver_calls"] == 0
assert audit["physical_solve_authorized"] is False
assert audit["physical_solve_executed"] is False
assert audit["physical_evidence_effect"] == "NONE"
schedule = impl.build_schedule()
assert len(schedule) == 35
assert [row["node_count"] for row in schedule[:5]] == [24, 32, 48, 64, 96]
assert [row["seed_index"] for row in schedule[::5]] == list(range(7))

# D1 trust-starvation failure mode is directly removed at the control-policy level.
assert impl.radius_update(1.0, 1.0, 1.0) == 2.0
assert impl.radius_update(1.0, 0.20, 1.0) == 0.25
assert impl.radius_update(1.0, 0.50, 1.0) == 1.0
assert impl.backtracking_factors()[0] == 1.0
assert impl.backtracking_factors()[-1] == 0.5**20
assert len(impl.backtracking_factors()) == 21

# Progress continuation is exact, deterministic and cannot use inadmissible/timed-out states.
assert impl.progress_continuation_eligible(initial=1.0, final=0.90, finite=True, admissible=True, timed_out=False)
assert not impl.progress_continuation_eligible(initial=1.0, final=0.9000001, finite=True, admissible=True, timed_out=False)
assert not impl.progress_continuation_eligible(initial=1.0, final=0.50, finite=False, admissible=True, timed_out=False)
assert not impl.progress_continuation_eligible(initial=1.0, final=0.50, finite=True, admissible=False, timed_out=False)
assert not impl.progress_continuation_eligible(initial=1.0, final=0.50, finite=True, admissible=True, timed_out=True)

# Physical execution must be impossible from the D2 implementation artifact.
denied = False
try:
    impl.execute_physical_schedule()
except impl.PhysicalExecutionDenied:
    denied = True
assert denied

# Source-level implementation checks: real SVD/equilibration logic exists, but no physical binding.
source = IMPLEMENTATION.read_text(encoding="utf-8")
for fragment in (
    "column_scale = np.maximum(column_norms, EQUILIBRATION_FLOOR)",
    "J_column = J / column_scale[None, :]",
    "row_scale = 1.0 / np.maximum(row_norms, EQUILIBRATION_FLOOR)",
    "U, scaled_singular, Vt = np.linalg.svd(A, full_matrices=False)",
    "dx = z / column_scale",
    "trial_inf < residual_inf",
    "rho >= RHO_ACCEPT_MIN",
    '"raw_condition_estimate"',
    '"scaled_condition_estimate"',
):
    assert fragment in source
for forbidden in (
    "background_3c_primary_kernel",
    "PRIMARY_PATH",
    "INDEPENDENT_PATH",
    "scipy.optimize",
    "least_squares",
):
    assert forbidden not in source

# Independent review must reproduce all seven gates without a physical solve.
independent = reviewer.review()
assert independent["status"] == "PASS_WP3_D2_INDEPENDENT_PROTOCOL_REVIEW_NO_EXECUTION"
assert set(independent["review_gates"]) == {
    "IR01_PROTOCOL_FIDELITY",
    "IR02_SYNTHETIC_SCALING_AND_TRUST_RADIUS",
    "IR03_ORIGINAL_RESIDUAL_ACCEPTANCE_FIREWALL",
    "IR04_PROGRESS_CONTINUATION_DETERMINISM",
    "IR05_RAW_AND_SCALED_DIAGNOSTIC_CAPTURE",
    "IR06_NO_PHYSICAL_EXECUTION_CAPABILITY",
    "IR07_NO_RELEASE_OR_GRANT_ARTIFACT",
}
assert all(item["status"] == "PASS" for item in independent["review_gates"].values())
assert independent["physical_solver_calls"] == 0
assert independent["physical_solve_authorized"] is False
assert independent["physical_solve_executed"] is False

contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
review = json.loads(REVIEW.read_text(encoding="utf-8"))
assert contract["implementation_state"] == "IMPLEMENTED_FOR_REVIEW_NOT_PHYSICALLY_BOUND_NOT_AUTHORIZED_NOT_EXECUTED"
assert contract["physical_freeze"]["acceptance_thresholds"] == "IDENTICAL_TO_CP01R1"
assert contract["governance"]["WP4"] == "BLOCKED"
assert contract["governance"]["K1-D"] == "NOT_RELEASED"
assert contract["governance"]["K1-E"] == "NOT_ADMISSIBLE"
assert review["review_status"] == independent["status"]
assert all(value == "PASS" for value in review["review_gates"].values())
assert review["governance"]["physical_evidence_effect"] == "NONE"

# Authorization artifacts remain absent.
assert not list(ROOT.glob("registry/*CP01R2*ReleaseAuthorization*.json"))
assert not list(ROOT.glob("registry/*CP01R2*ExecutionGrant*.json"))

print("PASS_WP3_D2_CP01R2_IMPLEMENTATION_REVIEW_TEST_NO_EXECUTION")
