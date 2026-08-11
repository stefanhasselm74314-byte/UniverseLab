#!/usr/bin/env python3
"""ULSH-01 / WP3-D3 CP01R2 physical-target binding audit.

Stdlib-only and strictly no-execution. This module binds the already reviewed
ETRN-01 method to exact source files/functions for the physical M1 target while
refusing to import numerical backends or provide a physical execution path.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3_CP01R2PhysicalTargetBindingContract_v1.0.json"
R2_INPUT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3_CP01R2RunInputFreeze_v1.0.json"
PARENT_INPUT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"
D1 = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D1_CP01R1FailureDiagnosis_CP01R2Protocol_v1.0.json"
D2 = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D2_CP01R2ImplementationContract_v1.0.json"
D2_REVIEW = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D2_CP01R2IndependentProtocolReview_v1.0.json"
PREREG = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"
RESOURCE = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2"
R2_PAYLOAD_SHA256 = "d4ed6f947c906006e39e74f4c4e1e430019d1e094e86e4ee90946ab77de10c75"
PARENT_PAYLOAD_SHA256 = "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302"


class D3BindingError(RuntimeError):
    pass


class PhysicalExecutionDenied(D3BindingError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise D3BindingError(f"top-level JSON object required: {path}")
    return value


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_sha256(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def ast_functions(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def execute_physical_schedule(*_args: Any, **_kwargs: Any) -> None:
    raise PhysicalExecutionDenied(
        "WP3-D3 binds the physical target but has no transaction capability; CP01R2 execution is forbidden"
    )


def _assert_source_bindings(contract: dict[str, Any]) -> None:
    for name, binding in contract["source_bindings"].items():
        path = ROOT / binding["path"]
        observed = git_blob_sha1(path)
        expected = binding["git_blob_sha1"]
        if observed != expected:
            raise D3BindingError(f"source binding drift for {name}: {observed} != {expected}")


def _assert_payload_rebind() -> None:
    r2 = load_json(R2_INPUT)
    parent = load_json(PARENT_INPUT)
    payload = r2["frozen_run_payload"]
    parent_payload = parent["frozen_run_payload"]
    if payload["run_id"] != RUN_ID:
        raise D3BindingError("CP01R2 run_id drift")
    if r2["frozen_run_payload_sha256"] != R2_PAYLOAD_SHA256 or canonical_sha256(payload) != R2_PAYLOAD_SHA256:
        raise D3BindingError("CP01R2 canonical payload digest drift")
    if parent["frozen_run_payload_sha256"] != PARENT_PAYLOAD_SHA256:
        raise D3BindingError("parent CP01R1 payload digest drift")
    equal_keys = (
        "model_parameters_ordered", "dimensional_anchor", "topological_sector_ordered",
        "alpha_H", "seed_set_id", "seed_spec_sha256", "dependency_lock_path",
        "dependency_lock_sha256",
    )
    for key in equal_keys:
        if payload[key] != parent_payload[key]:
            raise D3BindingError(f"physical-content drift between CP01R1 and CP01R2: {key}")
    if payload["model_parameters_ordered"]["a_F"] != "1/4":
        raise D3BindingError("a_F drift")
    if payload["numerical_method_id"] != "ETRN-01_EQUILIBRATED_TRUST_REGION_NEWTON":
        raise D3BindingError("ETRN-01 method binding drift")


def _assert_interfaces(contract: dict[str, Any]) -> None:
    source = contract["source_bindings"]
    base_path = ROOT / source["primary_kernel_base"]["path"]
    seed_path = ROOT / source["primary_seed_adapter"]["path"]
    independent_path = ROOT / source["independent_backend"]["path"]
    etrn_path = ROOT / source["d2_etrn01"]["path"]
    prolong_path = ROOT / source["prolongation_reference"]["path"]
    precision_path = ROOT / source["qa_precision_reference"]["path"]

    required_base = {
        "model_from_payload", "sector_from_payload", "residual", "admissible",
        "complex_step_jacobian", "unpack_state", "pack_state", "chebyshev_lobatto",
    }
    missing = required_base - ast_functions(base_path)
    if missing:
        raise D3BindingError(f"primary physical interface missing: {sorted(missing)}")
    if not {"seed_direction", "seven_seeds"}.issubset(ast_functions(seed_path)):
        raise D3BindingError("canonical seven-seed adapter interface drift")
    if not {"shooting_residual", "centered_fd_jacobian"}.issubset(ast_functions(independent_path)):
        raise D3BindingError("independent backend interface drift")
    required_etrn = {
        "equilibrated_svd_step", "model_reduction_ratio", "etrn_solve_generic",
        "progress_continuation_eligible", "radius_update", "execute_physical_schedule",
    }
    if not required_etrn.issubset(ast_functions(etrn_path)):
        raise D3BindingError("ETRN-01 reviewed interface drift")
    prolong_text = prolong_path.read_text(encoding="utf-8")
    if "def _prolongate_state" not in prolong_text or "np.interp" not in prolong_text:
        raise D3BindingError("deterministic prolongation reference drift")
    if "def _apply_precision_gate" not in precision_path.read_text(encoding="utf-8"):
        raise D3BindingError(">=80-bit precision QA reference drift")


def _assert_preconditions_and_gates() -> None:
    d1 = load_json(D1)
    d2 = load_json(D2)
    d2_review = load_json(D2_REVIEW)
    if d1["status"] != "PASS_WP3_D1_FAILURE_MODE_DIAGNOSIS_CP01R2_PROTOCOL_DESIGNED_NO_EXECUTION":
        raise D3BindingError("D1 precondition drift")
    if d1["cp01r2_protocol_design"]["state"] != "DESIGNED_NOT_AUTHORIZED_NOT_EXECUTED":
        raise D3BindingError("D1 CP01R2 state drift")
    if d2["status"] != "PASS_WP3_D2_CP01R2_ETRN01_IMPLEMENTED_AND_REVIEWED_NO_EXECUTION":
        raise D3BindingError("D2 implementation status drift")
    if d2_review["review_status"] != "PASS_WP3_D2_INDEPENDENT_PROTOCOL_REVIEW_NO_EXECUTION":
        raise D3BindingError("D2 independent review drift")

    thresholds = load_json(PREREG)["acceptance_thresholds"]
    expected = {
        "bulk_residual_max": 1e-10,
        "boundary_residual_max": 1e-10,
        "rr_constraint_max": 1e-9,
        "fine_mesh_profile_difference_max": 1e-8,
        "fine_mesh_augmented_difference_max": 1e-9,
        "independent_backend_candidate_distance_max": 1e-7,
        "maximum_reported_discrete_condition_number_without_high_precision_audit": 1e12,
    }
    for key, value in expected.items():
        if float(thresholds[key]) != value:
            raise D3BindingError(f"scientific acceptance threshold drift: {key}")

    resource = load_json(RESOURCE)["resource_limits"]
    if int(resource["maximum_wall_clock_seconds_per_seed_per_level"]) != 1800:
        raise D3BindingError("per-stage resource limit drift")
    if int(resource["maximum_wall_clock_seconds_total"]) != 21600:
        raise D3BindingError("total wall-clock limit drift")


def _assert_no_release_or_grant() -> None:
    patterns = (
        "registry/*CP01R2*ReleaseAuthorization*.json",
        "registry/*CP01R2*ExecutionGrant*.json",
        "registry/*CP01R2*SingleUse*Grant*.json",
    )
    found = [str(path.relative_to(ROOT)) for pattern in patterns for path in ROOT.glob(pattern)]
    if found:
        raise D3BindingError(f"D3 must not contain CP01R2 release/grant artifacts: {found}")


def audit() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    if contract["status"] != "PASS_D3_BINDING_DEFINED_PENDING_TRANSACTION_LAYER_NO_EXECUTION":
        raise D3BindingError("D3 contract status drift")
    if contract["run_id"] != RUN_ID:
        raise D3BindingError("D3 run_id drift")
    _assert_source_bindings(contract)
    _assert_payload_rebind()
    _assert_preconditions_and_gates()
    _assert_interfaces(contract)
    _assert_no_release_or_grant()
    if contract["governance"]["physical_solve_authorized"] is not False:
        raise D3BindingError("D3 may not authorize physical solve")
    if contract["governance"]["physical_solve_executed"] is not False:
        raise D3BindingError("D3 physical solve must remain unexecuted")
    return {
        "status": "PASS_WP3_D3_CP01R2_PHYSICAL_TARGET_BINDING_AUDIT_NO_EXECUTION",
        "run_id": RUN_ID,
        "cp01r2_payload_sha256": R2_PAYLOAD_SHA256,
        "physical_content_equal_to_cp01r1": True,
        "etrn01_bound_to_physical_interface": True,
        "scientific_acceptance_thresholds_unchanged": True,
        "independent_backend_bound": True,
        "higher_precision_qa_bound": True,
        "transaction_layer_present": False,
        "release_authorization_present": False,
        "execution_grant_present": False,
        "solver_imports": 0,
        "solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    print(json.dumps(audit(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
