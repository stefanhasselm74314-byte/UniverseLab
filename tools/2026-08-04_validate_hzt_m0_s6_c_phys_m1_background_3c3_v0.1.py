#!/usr/bin/env python3
"""Validate fail-closed Background-3C3 execution authorization review."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C3ExecutionAuthorizationReview_v0.1.json"
AUTH_DENIAL = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.1.json"
FUTURE_GRANT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
DUAL_VALIDATOR = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3c2_v0.1.py"
OUTPUT_ROOT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"


class ContractError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing JSON: {path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root must be object: {path.relative_to(ROOT)}")
    return value


def load_dual_validator():
    spec = importlib.util.spec_from_file_location("background3c2_for_authorization_review", DUAL_VALIDATOR)
    if spec is None or spec.loader is None:
        raise ContractError("unable to import Background-3C2 validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_review(review: dict[str, Any]) -> dict[str, Any]:
    require(review["schema"] == "universelab.hzt-m0-s6-c-phys-m1.background-3c3-execution-authorization-review.v0.1", "review schema drift")
    require(review["classification"] == "FAIL_CLOSED_EXECUTION_AUTHORIZATION_REVIEW_NO_SOLVER_EXECUTION", "review classification drift")
    require(review["status"] == "REVIEW_COMPLETE_AUTHORIZATION_DENIED", "review status drift")
    require(review["review_outcome"] == "DENIED_MISSING_EXECUTION_PACKAGE", "review outcome drift")
    require(review["authorized"] is False, "authorization opened")
    require(review["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1", "run id drift")
    require(review["run_payload_sha256"] == "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302", "run hash drift")
    satisfied = review["satisfied_prerequisites"]
    require(all(value is True for value in satisfied.values()), "satisfied prerequisite drift")
    blockers = review["blocking_prerequisites"]
    expected_blockers = {
        "source_hash_bound_execution_runner": "NOT_PRESENT",
        "independent_target_root_solver": "NOT_IMPLEMENTED",
        "immutable_result_writer": "NOT_IMPLEMENTED",
        "resource_enforcement_layer": "NOT_IMPLEMENTED",
        "environment_attestation": "NOT_IMPLEMENTED",
        "classification_engine": "NOT_IMPLEMENTED",
        "interruption_and_partial_artifact_protocol": "NOT_IMPLEMENTED",
        "append_only_execution_grant": "ABSENT",
    }
    for key, value in expected_blockers.items():
        require(blockers[key]["status"] == value, f"blocking prerequisite drift: {key}")
    logic = review["review_logic"]
    require(logic["all_required_prerequisites_pass"] is False, "all-prerequisites overclaim")
    require(logic["default_on_missing_or_ambiguous_item"] == "DENY", "fail-closed default drift")
    require(logic["review_may_execute_solver"] is False, "review execution opened")
    effect = review["execution_effect"]
    require(all(value is False for value in effect.values()), "execution effect opened")
    gates = review["gate_state"]
    expected_gates = {
        "BACKGROUND_3C_AUTHORIZATION_REVIEW": "DENIED_MISSING_EXECUTION_PACKAGE",
        "BACKGROUND_3C_EXECUTION": "NOT_AUTHORIZED",
        "BACKGROUND_SOLVER_EXECUTION": "NOT_AUTHORIZED",
        "physical_background": "NOT_ESTABLISHED",
        "full_linearized_boundary_trace_rank": "NOT_PROVEN",
        "Fredholm_property": "NOT_PROVEN",
        "continuum_BVP_Jacobian": "NOT_PROVEN",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected_gates.items():
        require(gates.get(key) == value, f"review gate drift: {key}")
    require(review["next_block"]["id"] == "C-PHYS-R1.0-BACKGROUND-3C4_EXECUTION_RUNNER_IMPLEMENTATION_ONLY", "next block drift")
    return {"blockers": expected_blockers, "gates": expected_gates}


def validate() -> dict[str, Any]:
    dual = load_dual_validator().validate()
    require(dual["status"] == "PASS", "dual-backend prerequisite revalidation failed")
    require(dual["audit"]["primary_newton_call_count"] == 0, "primary Newton executed")
    require(dual["audit"]["independent_shooting_jacobian_call_count"] == 0, "shooting Jacobian executed")
    denial = load_json(AUTH_DENIAL)
    require(denial["status"] == "NOT_GRANTED" and denial["authorized"] is False, "immutable denial drift")
    require(not FUTURE_GRANT.exists(), "unexpected grant artifact present")
    require(not OUTPUT_ROOT.exists(), "unexpected result directory present")
    review = load_json(REVIEW)
    review_result = validate_review(review)
    return {
        "status": "PASS",
        "contract": review["schema"],
        "review_outcome": review["review_outcome"],
        "blocking_prerequisites": review_result["blockers"],
        "dual_backend_prerequisite": dual["audit"]["status"],
        "solver_executed": False,
        "execution_authorized": False,
        "result_artifact_created": False,
        "physical_evidence_effect": "NONE",
        "next_block": review["next_block"]["id"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = validate()
    except (ContractError, RuntimeError, ValueError, KeyError, FloatingPointError) as exc:
        payload = {"status": "FAIL", "error": str(exc), "execution_authorized": False}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"FAIL: {exc}")
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else "PASS: Background-3C3 authorization denied fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
