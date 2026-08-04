#!/usr/bin/env python3
"""Validate Background-3C2 independent and dual-backend contracts without solve."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEPENDENT_CONTRACT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CIndependentBackendContract_v0.1.json"
DUAL_CONTRACT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CDualBackendPackageContract_v0.1.json"
AUTH_DENIAL = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.1.json"
FUTURE_GRANT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
INDEPENDENT_SOURCE = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_independent_backend_v0.1.py"
DUAL_GATE = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_dual_backend_gate_v0.1.py"
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


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ContractError(f"unable to import {path.relative_to(ROOT)}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_independent_contract(contract: dict[str, Any]) -> dict[str, Any]:
    require(contract["schema"] == "universelab.hzt-m0-s6-c-phys-m1.background-3c-independent-backend.v0.1", "independent schema drift")
    require(contract["classification"] == "INDEPENDENT_X_SPACE_BACKEND_NO_NONLINEAR_EXECUTION", "independent classification drift")
    require(contract["status"] == "INDEPENDENT_BACKEND_PRESENT_PENDING_CI_EXECUTION_NOT_AUTHORIZED", "independent status drift")
    source = contract["source"]
    require(source["path"] == str(INDEPENDENT_SOURCE.relative_to(ROOT)), "independent source path drift")
    require(source["git_blob_sha"] == git_blob_sha(INDEPENDENT_SOURCE), "independent source blob drift")
    require(source["imports_primary_residual"] is False and source["wraps_primary_residual"] is False, "independence overclaim")
    formulation = contract["independent_formulation"]
    require(formulation["coordinate"] == "physical_dimensionless_x", "independent coordinate drift")
    require(formulation["integrator"] == "SCIPY_SOLVE_IVP_DOP853", "independent integrator drift")
    require(formulation["pole_initialization"] == "A4_ELL5_VARPHI4_A_CHI4_FROM_OPERATOR2A", "pole series drift")
    require(formulation["control_cutoffs"] == [0.001, 0.0005, 0.00025], "cutoff schedule drift")
    require(formulation["future_root_method"] == "NOT_IMPLEMENTED_OR_EXECUTED_IN_3C2_AUDIT", "root execution overclaim")
    state = contract["current_execution_state"]
    require(all(value is False for value in state.values()), "independent execution-state overclaim")
    gates = contract["gate_state"]
    require(gates["BACKGROUND_3C_EXECUTION"] == "NOT_AUTHORIZED", "execution opened")
    require(gates["official_MD2S_solver"] == "NOT_AUTHORIZED", "official solver opened")
    require(gates["K1-D"] == "NOT_RELEASED" and gates["K1-E"] == "NOT_ADMISSIBLE", "K1 firewall drift")
    require(gates["physical_evidence_effect"] == "NONE", "physical evidence overclaim")
    return {"source_blob_sha": source["git_blob_sha"], "cutoffs": formulation["control_cutoffs"]}


def validate_dual_contract(contract: dict[str, Any]) -> dict[str, Any]:
    require(contract["schema"] == "universelab.hzt-m0-s6-c-phys-m1.background-3c-dual-backend-package.v0.1", "dual schema drift")
    require(contract["classification"] == "AUDIT_ONLY_DUAL_BACKEND_PACKAGE_NO_SOLVER_EXECUTION", "dual classification drift")
    require(contract["status"] == "DUAL_BACKEND_PACKAGE_PRESENT_PENDING_CI_EXECUTION_NOT_AUTHORIZED", "dual status drift")
    require(contract["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1", "dual run id drift")
    gate = contract["dual_gate"]
    require(gate["path"] == str(DUAL_GATE.relative_to(ROOT)), "dual gate path drift")
    require(gate["git_blob_sha"] == git_blob_sha(DUAL_GATE), "dual gate blob drift")
    require(gate["run_expected_exit_code"] == 73 and gate["direct_independent_backend_exit_code"] == 73, "exit-73 firewall drift")
    limits = contract["audit_execution_limits"]
    require(limits["primary_newton_calls"] == 0, "primary Newton limit drift")
    require(limits["independent_shooting_jacobian_calls"] == 0, "shooting Jacobian limit drift")
    require(limits["independent_shooting_root_calls"] == 0, "shooting root limit drift")
    require(limits["allowed_independent_control_integrations"] == 6, "control integration count drift")
    require(limits["target_model_integrations"] == 0 and limits["result_artifacts"] == 0, "target execution overclaim")
    authorization = contract["execution_authorization"]
    require(authorization["future_grant_present"] is False and authorization["authorized"] is False, "authorization overclaim")
    require(authorization["current_package_is_execution_runner"] is False, "execution runner overclaim")
    gates = contract["gate_state"]
    require(gates["BACKGROUND_3C_EXECUTION"] == "NOT_AUTHORIZED", "dual execution opened")
    require(gates["BACKGROUND_SOLVER_EXECUTION"] == "NOT_AUTHORIZED", "solver execution opened")
    require(gates["physical_background"] == "NOT_ESTABLISHED", "background overclaim")
    require(gates["physical_evidence_effect"] == "NONE", "dual physical evidence overclaim")
    return {"gate_blob_sha": gate["git_blob_sha"], "next_block": contract["next_block"]}


def validate() -> dict[str, Any]:
    independent_contract = load_json(INDEPENDENT_CONTRACT)
    dual_contract = load_json(DUAL_CONTRACT)
    denial = load_json(AUTH_DENIAL)
    require(denial["status"] == "NOT_GRANTED" and denial["authorized"] is False, "authorization denial drift")
    require(not FUTURE_GRANT.exists(), "unexpected execution grant present")
    require(not OUTPUT_ROOT.exists(), "unexpected result output directory present")
    independent_result = validate_independent_contract(independent_contract)
    dual_result = validate_dual_contract(dual_contract)
    gate = load_module("background3c_dual_gate_validator", DUAL_GATE)
    audit = gate.audit()
    require(audit["status"] == "PASS_DUAL_BACKEND_CONTROL_AUDIT_NO_NONLINEAR_EXECUTION", "dual audit status drift")
    require(audit["primary_newton_call_count"] == 0, "primary Newton executed")
    require(audit["independent_shooting_jacobian_call_count"] == 0, "shooting Jacobian executed")
    require(audit["independent_integration_call_count"] == 6, "independent integration count drift")
    require(audit["execution_authorized"] is False, "execution authorization overclaim")
    require(audit["result_artifact_created"] is False, "result artifact overclaim")
    return {
        "status": "PASS",
        "contract": dual_contract["schema"],
        "independent_backend": independent_result,
        "dual_package": dual_result,
        "audit": audit,
        "solver_executed": False,
        "execution_authorized": False,
        "physical_evidence_effect": "NONE",
        "next_block": dual_contract["next_block"],
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
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else "PASS: Background-3C2 independent dual-backend audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
