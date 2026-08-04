#!/usr/bin/env python3
"""Validate Background-3C primary implementation v0.2 without solver execution."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CImplementationContract_v0.2.json"
AUTH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.1.json"
RESULT_SCHEMA = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResultSchema_v0.1.json"
RESOURCE_POLICY = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
FUTURE_GRANT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
GATE_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_gate_v0.2.py"


class ContractError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing required artifact: {path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root must be object: {path.relative_to(ROOT)}")
    return value


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def load_gate():
    spec = importlib.util.spec_from_file_location("background3c_gate_canonical_v02", GATE_PATH)
    if spec is None or spec.loader is None:
        raise ContractError("unable to import canonical Background-3C gate")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_source_identity(contract: dict[str, Any]) -> dict[str, str]:
    source = contract["implementation_source"]
    pairs = {
        "canonical_primary_kernel": "canonical_primary_kernel_git_blob_sha",
        "internal_base_kernel": "internal_base_kernel_git_blob_sha",
        "canonical_audit_and_execution_gate": "canonical_audit_and_execution_gate_git_blob_sha",
        "internal_base_gate": "internal_base_gate_git_blob_sha",
        "dependency_lock": "dependency_lock_git_blob_sha",
    }
    result: dict[str, str] = {}
    for path_key, hash_key in pairs.items():
        relative = source[path_key]
        path = ROOT / relative
        require(path.is_file(), f"missing source file: {relative}")
        actual = git_blob_sha(path)
        require(actual == source[hash_key], f"source blob hash drift: {relative}")
        result[relative] = actual
    require(source["direct_kernel_execution"] == "FORBIDDEN_EXIT_73", "direct execution firewall drift")
    require(source["run_command"] == "FAIL_CLOSED_EXIT_73_BEFORE_NEWTON", "run command firewall drift")
    return result


def validate_contract(contract: dict[str, Any]) -> dict[str, Any]:
    require(contract["schema"] == "universelab.hzt-m0-s6-c-phys-m1.background-3c-implementation.v0.2", "implementation schema drift")
    require(contract["classification"] == "QUARANTINED_PRIMARY_IMPLEMENTATION_NO_EXECUTION", "implementation classification drift")
    require(contract["status"] == "PRIMARY_IMPLEMENTATION_PRESENT_PENDING_CI_EXECUTION_NOT_AUTHORIZED", "implementation status drift")
    require(contract["official_solver_authorized"] is False, "official solver authorization opened")
    require(contract["diagnostic_execution_authorized"] is False, "diagnostic execution authorization opened")
    binding = contract["frozen_input_binding"]
    require(binding["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1", "run binding drift")
    require(binding["run_payload_sha256"] == "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302", "run payload hash drift")
    require(binding["seed_amplitude_scale"] == "1/20", "seed amplitude binding drift")
    require(binding["seed_multipliers_in_order"] == ["0", "1/8", "-1/8", "1/4", "-1/4", "1/2", "-1/2"], "seed multiplier binding drift")
    backend = contract["implemented_primary_backend"]
    require(backend["regional_node_counts"] == [24, 32, 48, 64, 96], "node schedule drift")
    require(backend["node_count_to_degree"] == "degree=node_count-1", "degree rule drift")
    require(backend["discrete_shape"] == "8N+8_by_8N+8", "discrete shape drift")
    require(backend["linear_solver"] == "RANK_REVEALING_QR_PRIMARY", "primary linear solver drift")
    require(backend["singular_value_role"] == "SVD_DIAGNOSTIC_ONLY", "SVD role drift")
    require(backend["maximum_iterations"] == 60, "maximum iterations drift")
    require(backend["maximum_backtracking_steps"] == 20, "backtracking limit drift")
    blockers = contract["blocking_prerequisites"]
    require(blockers["independent_backend_implementation"] == "NOT_PRESENT", "independent backend overclaim")
    require(blockers["independent_residual_assembly"] == "NOT_PRESENT", "independent residual overclaim")
    require(blockers["execution_authorization"] == "NOT_GRANTED", "execution authorization overclaim")
    state = contract["current_execution_state"]
    require(all(value is False for value in state.values()), "execution-state overclaim")
    gates = contract["gate_state"]
    expected = {
        "BACKGROUND_3C_INDEPENDENT_BACKEND": "NOT_PRESENT",
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
    for key, value in expected.items():
        require(gates.get(key) == value, f"implementation gate drift: {key}")
    return {"run_id": binding["run_id"], "gates": expected}


def validate_authorization() -> dict[str, Any]:
    authorization = load_json(AUTH)
    require(authorization["status"] == "NOT_GRANTED", "authorization status drift")
    require(authorization["authorized"] is False, "authorization opened")
    require(authorization["current_effect"]["run_command_allowed"] is False, "run command allowed")
    require(authorization["current_effect"]["newton_execution_allowed"] is False, "Newton execution allowed")
    require(authorization["current_effect"]["result_artifact_creation_allowed"] is False, "result creation allowed")
    require(not FUTURE_GRANT.exists(), "unexpected future grant artifact present")
    return {"status": authorization["status"], "future_grant_present": False}


def validate_result_and_resource_contracts() -> dict[str, Any]:
    result = load_json(RESULT_SCHEMA)
    resources = load_json(RESOURCE_POLICY)
    require(result["status"] == "FROZEN_NOT_INSTANTIATED", "result schema status drift")
    require(result["immutable_output_policy"]["overwrite_existing_path"] is False, "output overwrite opened")
    require(result["current_state"]["result_artifact_created"] is False, "result artifact overclaim")
    require(resources["status"] == "FROZEN_EXECUTION_NOT_AUTHORIZED", "resource policy status drift")
    require(resources["execution_environment"]["network_access"] is False, "network access opened")
    require(resources["execution_environment"]["randomness"] is False, "randomness opened")
    require(resources["resource_limits"]["maximum_cpu_threads"] == 1, "thread limit drift")
    return {"result_schema": result["status"], "resource_policy": resources["status"]}


def validate() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    contract_result = validate_contract(contract)
    source_hashes = validate_source_identity(contract)
    authorization = validate_authorization()
    schemas = validate_result_and_resource_contracts()
    gate = load_gate()
    audit = gate.audit()
    require(audit["status"] == "PASS_PRIMARY_IMPLEMENTATION_AUDIT_NO_SOLVER_EXECUTION", "primary audit status drift")
    require(audit["newton_call_count"] == 0, "Newton executed during primary audit")
    require(audit["result_artifact_created"] is False, "result artifact created during audit")
    require(audit["independent_backend"] == "NOT_PRESENT_BLOCKING", "independent backend overclaim")
    return {
        "status": "PASS",
        "contract": contract["schema"],
        "implementation": contract_result,
        "source_hashes": source_hashes,
        "authorization": authorization,
        "schemas": schemas,
        "audit": audit,
        "solver_executed": False,
        "physical_evidence_effect": "NONE",
        "next_block": contract["next_block"]["id"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = validate()
    except (ContractError, RuntimeError, ValueError, KeyError, FloatingPointError) as exc:
        payload = {"status": "FAIL", "error": str(exc), "solver_executed": False}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"FAIL: {exc}")
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else "PASS: Background-3C primary implementation audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
