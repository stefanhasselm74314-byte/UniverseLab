#!/usr/bin/env python3
"""Canonical v0.2 entry point for the Background-3C6 control release.

The v0.1 module contains the integrated transaction engine. This adapter
replaces only its static audit with an AST-based import/call inspection and is
the sole canonical command entry point. Physical execution remains impossible.
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c6_integrated_release_v0.1.py"
WORKER_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c6_synthetic_worker_v0.1.py"
SPEC = importlib.util.spec_from_file_location("background3c6_integrated_release_base_v01", BASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import Background-3C6 integrated release base")
BASE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)


def imported_modules(tree: ast.AST) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modules.add(node.module or "")
    return modules


def called_names(tree: ast.AST) -> set[str]:
    calls: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Name):
            calls.add(function.id)
        elif isinstance(function, ast.Attribute):
            calls.add(function.attr)
    return calls


def audit_release() -> dict:
    trees = {
        "engine": ast.parse(BASE_PATH.read_text(encoding="utf-8"), filename=str(BASE_PATH)),
        "worker": ast.parse(WORKER_PATH.read_text(encoding="utf-8"), filename=str(WORKER_PATH)),
    }
    modules = set().union(*(imported_modules(tree) for tree in trees.values()))
    calls = set().union(*(called_names(tree) for tree in trees.values()))
    forbidden_module_fragments = {
        "background_3c_primary_kernel",
        "background_3c_independent_backend",
    }
    forbidden_calls = {
        "damped_newton",
        "complex_step_jacobian",
        "centered_fd_jacobian",
        "shooting_residual",
    }
    violating_modules = sorted(
        module for module in modules
        if any(fragment in module for fragment in forbidden_module_fragments)
    )
    violating_calls = sorted(calls & forbidden_calls)
    if violating_modules or violating_calls:
        raise BASE.ControlReleaseError(
            f"forbidden physical backend dependency: modules={violating_modules}, calls={violating_calls}"
        )
    contract = BASE.load_json(BASE.CONTRACT_PATH)
    if contract.get("canonical_entry_point") != str(Path(__file__).relative_to(ROOT)):
        raise BASE.ControlReleaseError("canonical entry-point binding mismatch")
    if contract["physical_execution_authorized"] is not False:
        raise BASE.ControlReleaseError("physical execution unexpectedly authorized")
    if BASE.PHYSICAL_GRANT_PATH.exists() or BASE.PHYSICAL_ARTIFACT_ROOT.exists():
        raise BASE.ControlReleaseError("physical grant or CP01R1 artifact path unexpectedly exists")
    package = BASE.package_manifest()
    return {
        "status": "PASS_INTEGRATED_CONTROL_RELEASE_AUDIT_NO_PHYSICAL_EXECUTION",
        "package_manifest_sha256": package["package_manifest_sha256"],
        "source_count": package["source_count"],
        "inspected_modules": len(modules),
        "inspected_call_names": len(calls),
        "forbidden_modules": violating_modules,
        "forbidden_calls": violating_calls,
        "allowed_cases": contract["control_scope"]["allowed_cases"],
        "subprocess_launch_count": BASE.SUBPROCESS_LAUNCH_COUNT,
        "primary_root_calls": BASE.PRIMARY_ROOT_CALL_COUNT,
        "independent_root_calls": BASE.INDEPENDENT_ROOT_CALL_COUNT,
        "shooting_jacobian_calls": BASE.SHOOTING_JACOBIAN_CALL_COUNT,
        "cp01r1_attempts": BASE.CP01R1_ATTEMPT_COUNT,
        "physical_grant_present": False,
        "physical_result_artifact_present": False,
        "physical_evidence_effect": "NONE",
    }


BASE.audit_release = audit_release


def emit(payload: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload["status"])


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("audit", "self-test"):
        item = subparsers.add_parser(name)
        item.add_argument("--json", action="store_true")
    control = subparsers.add_parser("control")
    control.add_argument("--case", required=True)
    control.add_argument("--control-id", required=True)
    control.add_argument("--output-root", required=True)
    control.add_argument("--json", action="store_true")
    run = subparsers.add_parser("run")
    run.add_argument("--run-id")
    run.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "audit":
            emit(audit_release(), args.json)
            return 0
        if args.command == "self-test":
            emit(BASE.self_test(), args.json)
            return 0
        if args.command == "control":
            emit(BASE.run_control(args.case, args.control_id, Path(args.output_root)), args.json)
            return 0
        if args.command == "run":
            emit(BASE.denied_physical_run(args.run_id), args.json)
            return BASE.EXIT_NOT_AUTHORIZED
    except (BASE.ControlReleaseError, OSError, ValueError, json.JSONDecodeError) as error:
        emit({
            "status": "CONTROL_RELEASE_FAILURE",
            "error": f"{type(error).__name__}: {error}",
            "solver_calls": 0,
            "result_artifact_created": False,
            "physical_evidence_effect": "NONE",
        }, True)
        return BASE.EXIT_CONTROL_FAILURE
    return BASE.EXIT_CONTROL_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
