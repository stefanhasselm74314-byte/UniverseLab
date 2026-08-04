#!/usr/bin/env python3
"""Audit-only dual-backend gate for C-PHYS-M1 Background-3C2.

The gate reuses the already audited primary audit command and independently
loads the x-space backend. It compares only the analytic control background.
No Newton or shooting-root iteration is permitted.
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PRIMARY_GATE_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_gate_v0.2.py"
INDEPENDENT_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_independent_backend_v0.1.py"
AUTH_DENIAL = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.1.json"
FUTURE_GRANT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
OUTPUT_ROOT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
EXIT_NOT_AUTHORIZED = 73
EXPECTED_BOUNDARY_ORDER = (
    "R_A", "R_ell", "R_varphi", "R_patch",
    "R_4D", "R_chi", "R_scalar", "R_gauge",
)


class DualBackendError(RuntimeError):
    pass


class AuthorizationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DualBackendError(message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing JSON: {path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DualBackendError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root must be object: {path.relative_to(ROOT)}")
    return value


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise DualBackendError(f"unable to import {path.relative_to(ROOT)}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def audit_source_independence() -> dict[str, Any]:
    source = INDEPENDENT_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    forbidden_tokens = (
        "background_3c_primary_kernel",
        "background_3c_gate_v0.2",
        "PRIMARY_GATE_PATH",
        "primary.residual",
    )
    for token in forbidden_tokens:
        require(token not in source, f"independent backend references primary implementation: {token}")
    require("scipy.integrate" in imports, "independent DOP853 import missing")
    require("solve_ivp" in source and 'method="DOP853"' in source, "independent DOP853 implementation missing")
    require("def rhs_x" in source, "independent x-space rhs missing")
    require("def cap_residuals" in source, "independent cap residual assembly missing")
    require("def pole_coefficients" in source, "independent higher pole series missing")
    return {"imports": sorted(set(imports)), "forbidden_primary_references": False}


def exact_boundary_vector() -> np.ndarray:
    y0 = (8.0 - 2.0 * math.sqrt(10.0)) / 3.0
    return np.asarray([
        0.0, 0.0, 0.0, 0.0,
        1.0 + 9.0 * y0 / 8.0,
        1.0 - 9.0 * y0 / 8.0,
        0.0,
        -3.0 * y0 / 2.0,
    ])


def audit() -> dict[str, Any]:
    source_audit = audit_source_independence()
    primary_gate = load_module("background3c_primary_gate_for_dual_audit", PRIMARY_GATE_PATH)
    independent = load_module("background3c_independent_backend_for_dual_audit", INDEPENDENT_PATH)
    require(primary_gate.BASE.load_kernel().NEWTON_CALL_COUNT == 0, "primary Newton count nonzero before audit")
    require(independent.INTEGRATION_CALL_COUNT == 0, "independent integration count nonzero before audit")
    require(independent.SHOOTING_JACOBIAN_CALL_COUNT == 0, "independent shooting Jacobian count nonzero before audit")

    primary = primary_gate.audit()
    require(primary["newton_call_count"] == 0, "primary Newton executed during dual audit")
    independent_result = independent.control_audit()
    require(independent_result["shooting_jacobian_call_count"] == 0, "shooting Jacobian executed during dual audit")
    records = independent_result["cutoffs"]
    require([record["epsilon"] for record in records] == [1.0e-3, 5.0e-4, 2.5e-4], "cutoff schedule drift")
    exact_boundary = exact_boundary_vector()
    primary_boundary = np.asarray([
        primary["control_boundary_raw"][name] for name in EXPECTED_BOUNDARY_ORDER
    ])
    primary_exact_distance = float(np.max(np.abs(primary_boundary - exact_boundary)))
    require(primary_exact_distance <= 5.0e-10, "primary control boundary drift")

    cutoff_table: list[dict[str, float]] = []
    for record in records:
        boundary = np.asarray(record["boundary"])
        boundary_exact_distance = float(np.max(np.abs(boundary - exact_boundary)))
        backend_distance = float(np.max(np.abs(boundary - primary_boundary)))
        require(record["profile_error_max"] <= 2.0e-8, "independent profile control audit failed")
        require(record["constraint_max"] <= 2.0e-10, "independent constraint control audit failed")
        require(boundary_exact_distance <= 2.0e-8, "independent boundary control audit failed")
        require(backend_distance <= 2.0e-8, "primary-independent boundary disagreement")
        cutoff_table.append({
            "epsilon": float(record["epsilon"]),
            "profile_error_max": float(record["profile_error_max"]),
            "constraint_max": float(record["constraint_max"]),
            "boundary_exact_distance": boundary_exact_distance,
            "primary_independent_boundary_distance": backend_distance,
        })

    require(independent.INTEGRATION_CALL_COUNT == 6, "unexpected independent integration count")
    require(independent.SHOOTING_JACOBIAN_CALL_COUNT == 0, "independent shooting Jacobian executed")
    require(primary_gate.BASE.load_kernel().NEWTON_CALL_COUNT == 0, "primary Newton executed")
    require(not FUTURE_GRANT.exists(), "unexpected execution grant present")
    require(not OUTPUT_ROOT.exists(), "unexpected result output directory present")
    authorization = load_json(AUTH_DENIAL)
    require(authorization["status"] == "NOT_GRANTED" and authorization["authorized"] is False, "authorization denial drift")
    return {
        "status": "PASS_DUAL_BACKEND_CONTROL_AUDIT_NO_NONLINEAR_EXECUTION",
        "source_independence": source_audit,
        "run_id": primary["run_id"],
        "run_payload_sha256": primary["run_payload_sha256"],
        "primary_newton_call_count": primary["newton_call_count"],
        "independent_integration_call_count": independent.INTEGRATION_CALL_COUNT,
        "independent_shooting_jacobian_call_count": independent.SHOOTING_JACOBIAN_CALL_COUNT,
        "primary_exact_boundary_distance": primary_exact_distance,
        "cutoff_table": cutoff_table,
        "authorization_status": authorization["status"],
        "execution_authorized": False,
        "result_artifact_created": False,
        "physical_evidence_effect": "NONE",
    }


def require_execution_authorization() -> None:
    denial = load_json(AUTH_DENIAL)
    if denial.get("status") != "NOT_GRANTED" or denial.get("authorized") is not False:
        raise AuthorizationError("immutable v0.1 denial artifact drift")
    if not FUTURE_GRANT.exists():
        raise AuthorizationError("Background-3C execution grant v0.2 is absent")
    raise AuthorizationError("Background-3C2 is an audit-only dual-backend package; a separately versioned execution runner is still required")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit", "run"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "run":
            require_execution_authorization()
            raise DualBackendError("unreachable execution path")
        payload = audit()
    except AuthorizationError as exc:
        payload = {"status": "NOT_AUTHORIZED", "error": str(exc), "solver_executed": False, "result_artifact_created": False}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"NOT AUTHORIZED: {exc}")
        return EXIT_NOT_AUTHORIZED
    except (DualBackendError, RuntimeError, ValueError, KeyError, FloatingPointError) as exc:
        payload = {"status": "FAIL", "error": str(exc), "solver_executed": False}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"FAIL: {exc}")
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
