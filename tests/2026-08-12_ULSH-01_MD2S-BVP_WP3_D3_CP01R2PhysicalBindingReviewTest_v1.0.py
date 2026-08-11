#!/usr/bin/env python3
"""Regression tests for ULSH-01 WP3-D3 CP01R2 binding/review, strictly no execution."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3_cp01r2_physical_target_binding_v1.0.py"
REVIEW = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3_independent_release_readiness_review_v1.0.py"
CONTRACT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3_CP01R2PhysicalBindingReleaseReadinessReview_v1.0.json"
RUN_INPUT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3_CP01R2RunInputFreeze_v1.0.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


target = load_module("ulsh_wp3_d3_target_test", TARGET)
review = load_module("ulsh_wp3_d3_review_test", REVIEW)

target_audit = target.audit()
assert target_audit["status"] == "PASS_WP3_D3_CP01R2_PHYSICAL_TARGET_BOUND_RELEASE_READY_FOR_SEPARATE_DECISION_NO_EXECUTION"
assert target_audit["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2"
assert target_audit["run_payload_sha256"] == "e8b8e82d2cb1472d91c387a40c8f84024c2549a3dcc2c897df5561f7bf721b36"
assert target_audit["schedule_sha256"] == "929f59d018cc511f36c98ef26a8614ed495fe699a067b1b33e6c5b53efaf8e0b"
assert target_audit["planned_entry_count"] == 35
assert target_audit["physical_target_binding_complete"] is True
assert target_audit["physical_sector_identical_to_cp01r1"] is True
assert target_audit["etrn01_bound_at_source_contract_level"] is True
assert target_audit["physical_residual_evaluations"] == 0
assert target_audit["solver_calls"] == 0
assert target_audit["physical_solve_authorized"] is False
assert target_audit["physical_solve_executed"] is False
assert target_audit["K1-D"] == "NOT_RELEASED"
assert target_audit["K1-E"] == "NOT_ADMISSIBLE"
assert target_audit["physical_evidence_effect"] == "NONE"

for forbidden in (target.issue_release_authorization, target.issue_execution_grant, target.execute_physical_schedule):
    try:
        forbidden()
    except target.PhysicalExecutionDenied:
        pass
    else:
        raise AssertionError("D3 forbidden entry point did not fail closed")

review_audit = review.review()
assert review_audit["status"] == "PASS_WP3_D3_INDEPENDENT_REVIEW_PHYSICAL_TARGET_BOUND_RELEASE_BLOCKED_NO_EXECUTION"
assert review_audit["target_binding"] == "PASS"
assert review_audit["release_readiness"] == "BLOCKED"
assert set(review_audit["release_blockers"]) == {"D3-B01", "D3-B02"}
assert review_audit["physical_solve_authorized"] is False
assert review_audit["physical_solve_executed"] is False
assert review_audit["physical_evidence_effect"] == "NONE"

contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
run_input = json.loads(RUN_INPUT.read_text(encoding="utf-8"))
assert contract["physical_target_binding_status"] == "PASS_SOURCE_CONTRACT_BOUND_NO_EXECUTION"
assert contract["release_readiness_status"].startswith("BLOCKED_")
assert contract["review_gates"]["D3-RB09_EXACT_CP01R2_TRANSACTION_SUPERVISOR_BINDING"] == "BLOCKED"
assert contract["review_gates"]["D3-RB10_CP01R2_IMMUTABLE_RESULT_COMMIT_AND_ARTIFACT_CLOSURE"] == "BLOCKED"
assert contract["governance"]["WP4"] == "BLOCKED"
assert contract["governance"]["K1-D"] == "NOT_RELEASED"
assert contract["governance"]["K1-E"] == "NOT_ADMISSIBLE"
assert run_input["execution_firewall"]["release_authorization_present"] is False
assert run_input["execution_firewall"]["single_use_grant_present"] is False
assert run_input["execution_firewall"]["physical_solve_executed"] is False

print("PASS_WP3_D3_CP01R2_PHYSICAL_BINDING_RELEASE_READINESS_REVIEW_TEST_NO_EXECUTION")
