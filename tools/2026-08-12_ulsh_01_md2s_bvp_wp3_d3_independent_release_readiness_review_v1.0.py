#!/usr/bin/env python3
"""Independent ULSH-01 WP3-D3 CP01R2 release-readiness review, no execution."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3_CP01R2PhysicalBindingReleaseReadinessReview_v1.0.json"
TARGET = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3_cp01r2_physical_target_binding_v1.0.py"
CP01R1_TX = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.4.py"


class D3ReviewError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise D3ReviewError(f"top-level object required: {path}")
    return value


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _load_target():
    spec = importlib.util.spec_from_file_location("ulsh_wp3_d3_target_review", TARGET)
    if spec is None or spec.loader is None:
        raise D3ReviewError("cannot load D3 target")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def review() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    if contract["physical_target_binding_status"] != "PASS_SOURCE_CONTRACT_BOUND_NO_EXECUTION":
        raise D3ReviewError("physical binding contract is not PASS")
    if contract["release_readiness_status"] != "BLOCKED_CP01R2_TRANSACTION_SUPERVISOR_AND_IMMUTABLE_RESULT_CLOSURE_NOT_YET_REBOUND":
        raise D3ReviewError("release-readiness classification drift")

    for name, binding in contract["source_bindings"].items():
        path = ROOT / binding["path"]
        if "git_blob_sha1" in binding:
            observed = git_blob_sha1(path)
            if observed != binding["git_blob_sha1"]:
                raise D3ReviewError(f"source binding drift: {name}: {observed}")

    target = _load_target()
    target_audit = target.audit()
    if target_audit["status"] != "PASS_WP3_D3_CP01R2_PHYSICAL_TARGET_BOUND_RELEASE_READY_FOR_SEPARATE_DECISION_NO_EXECUTION":
        raise D3ReviewError("target audit did not pass")
    if target_audit["physical_target_binding_complete"] is not True:
        raise D3ReviewError("target binding incomplete")
    if target_audit["physical_residual_evaluations"] != 0 or target_audit["solver_calls"] != 0:
        raise D3ReviewError("D3 audit evaluated physical residual or solver")
    if target_audit["physical_solve_authorized"] is not False or target_audit["physical_solve_executed"] is not False:
        raise D3ReviewError("D3 no-execution firewall drift")

    for forbidden_call in (target.issue_release_authorization, target.issue_execution_grant, target.execute_physical_schedule):
        try:
            forbidden_call()
        except target.PhysicalExecutionDenied:
            pass
        else:
            raise D3ReviewError("D3 forbidden execution/issuance entry point did not fail closed")

    gates = contract["review_gates"]
    pass_gates = [name for name, state in gates.items() if state == "PASS"]
    blocked_gates = [name for name, state in gates.items() if state == "BLOCKED"]
    if len(pass_gates) != 8 or set(blocked_gates) != {
        "D3-RB09_EXACT_CP01R2_TRANSACTION_SUPERVISOR_BINDING",
        "D3-RB10_CP01R2_IMMUTABLE_RESULT_COMMIT_AND_ARTIFACT_CLOSURE",
    }:
        raise D3ReviewError("D3 gate inventory drift")

    tx_source = CP01R1_TX.read_text(encoding="utf-8")
    cp01r1_specific_fragments = (
        "WP2-H3 transaction supervisor v1.4",
        "PhysicalSolveReleaseAuthorization_v1.3.json",
        "SingleUseExecutionGrant_v1.3.json",
    )
    if not all(fragment in tx_source for fragment in cp01r1_specific_fragments):
        raise D3ReviewError("CP01R1 transaction provenance changed unexpectedly")

    cp01r2_transaction_files = list(ROOT.glob("tools/*cp01r2*transaction*.py"))
    cp01r2_result_schema_files = list(ROOT.glob("registry/*CP01R2*ResultSchema*.json"))
    if cp01r2_transaction_files:
        raise D3ReviewError("D3-B01 must be re-reviewed because a CP01R2 transaction now exists")
    if cp01r2_result_schema_files:
        raise D3ReviewError("D3-B02 must be re-reviewed because a CP01R2 result schema now exists")

    if list(ROOT.glob("registry/*CP01R2*ReleaseAuthorization*.json")) or list(ROOT.glob("registry/*CP01R2*ExecutionGrant*.json")):
        raise D3ReviewError("release/grant artifact forbidden in D3")

    return {
        "status": "PASS_WP3_D3_INDEPENDENT_REVIEW_PHYSICAL_TARGET_BOUND_RELEASE_BLOCKED_NO_EXECUTION",
        "run_id": contract["run_id"],
        "pass_gates": pass_gates,
        "blocked_gates": blocked_gates,
        "release_blockers": ["D3-B01", "D3-B02"],
        "target_binding": "PASS",
        "release_readiness": "BLOCKED",
        "solver_backend_imported": False,
        "physical_residual_evaluations": 0,
        "solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
        "next_allowed_action": contract["next_allowed_action"],
    }


def main() -> int:
    print(json.dumps(review(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
