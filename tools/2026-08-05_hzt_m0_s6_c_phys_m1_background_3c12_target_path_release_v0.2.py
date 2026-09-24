#!/usr/bin/env python3
"""Corrected pre-audit Background-3C12 target-path release v0.2.

The v0.1 implementation remains the auditable base. This adapter changes only
one pre-audit default: immediately valid synthetic grants use
`not_before == issued_at`, as required by the frozen grant contract. No backend
is imported and no physical or target numerical path is executable.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
BASE_RELEASE_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c12_target_path_release_v0.1.py"
TARGET_CONTRACT_V01_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C12TargetPathReleaseContract_v0.1.json"
TARGET_CONTRACT_V02_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C12TargetPathReleaseContract_v0.2.json"
VALIDATOR_V02_PATH = ROOT / "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c12_v0.2.py"
TEST_V02_PATH = ROOT / "tests/2026-08-05_test_hzt_m0_s6_c_phys_m1_background_3c12_v0.2.py"
LEDGER_V02_PATH = ROOT / "science/hzt-m0/md2s/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C12GrantTargetPathLedger_v0.2.md"
AUDIT_RESULT_V02_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C12GrantTargetPathAuditResult_v0.2.json"

SPEC = importlib.util.spec_from_file_location("background3c12_target_release_base_v01", BASE_RELEASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import Background-3C12 target release v0.1")
BASE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)

ORIGINAL_ISSUE_SYNTHETIC_GRANT = BASE.issue_synthetic_grant
BASE.TARGET_CONTRACT_PATH = TARGET_CONTRACT_V02_PATH
BASE.VALIDATOR_PATH = VALIDATOR_V02_PATH
BASE.TEST_PATH = TEST_V02_PATH
BASE.LEDGER_PATH = LEDGER_V02_PATH
BASE.AUDIT_RESULT_PATH = AUDIT_RESULT_V02_PATH


def package_paths() -> tuple[Path, ...]:
    return (
        BASE.GRANT_CONTRACT_PATH,
        TARGET_CONTRACT_V01_PATH,
        TARGET_CONTRACT_V02_PATH,
        BASE.REVIEW_3C11_PATH,
        BASE.RUN_INPUT_PATH,
        BASE.SEED_SPEC_PATH,
        BASE.RESOURCE_POLICY_PATH,
        BASE.RESULT_SCHEMA_PATH,
        BASE.DEPENDENCY_LOCK_PATH,
        BASE.PRIMARY_PATH,
        BASE.PRIMARY_BASE_PATH,
        BASE.INDEPENDENT_PATH,
        BASE.WORKER_PATH,
        BASE_RELEASE_PATH,
        Path(__file__).resolve(),
        VALIDATOR_V02_PATH,
        TEST_V02_PATH,
        LEDGER_V02_PATH,
    )


def issue_synthetic_grant(
    binding: dict[str, str], *, now: datetime | None = None,
    not_before_offset_seconds: int = 0, lifetime_seconds: int = 600,
    operative: bool = False,
) -> dict[str, Any]:
    return ORIGINAL_ISSUE_SYNTHETIC_GRANT(
        binding,
        now=now,
        not_before_offset_seconds=not_before_offset_seconds,
        lifetime_seconds=lifetime_seconds,
        operative=operative,
    )


BASE.package_paths = package_paths
BASE.issue_synthetic_grant = issue_synthetic_grant


def load_json(path: Path) -> dict[str, Any]:
    return BASE.load_json(path)


def package_manifest() -> list[dict[str, str]]:
    return BASE.package_manifest()


def package_digest() -> str:
    return BASE.package_digest()


def expected_binding() -> dict[str, str]:
    return BASE.expected_binding()


def target_request(outcome: str) -> dict[str, Any]:
    return BASE.target_request(outcome)


def launch_worker(outcome: str, *, timeout_seconds: float = 3.0) -> dict[str, Any]:
    return BASE.launch_worker(outcome, timeout_seconds=timeout_seconds)


def static_audit() -> dict[str, Any]:
    contract_v01 = load_json(TARGET_CONTRACT_V01_PATH)
    contract_v02 = load_json(TARGET_CONTRACT_V02_PATH)
    if contract_v02.get("supersedes_for_audit") != str(TARGET_CONTRACT_V01_PATH.relative_to(ROOT)):
        raise BASE.ReleaseFailure("target release correction chain drift")
    correction = contract_v02.get("pre_audit_correction", {})
    if correction.get("audit_or_control_run_executed_under_v0_1") is not False:
        raise BASE.ReleaseFailure("v0.1 execution history drift")
    if correction.get("corrected_item") != "DEFAULT_SYNTHETIC_NOT_BEFORE_EQUALS_ISSUED_AT":
        raise BASE.ReleaseFailure("pre-audit correction identity drift")
    if contract_v01["target_identity"] != contract_v02["target_identity"]:
        raise BASE.ReleaseFailure("target identity changed during pre-audit correction")
    result = BASE.static_audit()
    wrapper_scan = BASE.scan_source(Path(__file__).resolve())
    forbidden_modules = {"numpy", "scipy", "socket", "urllib", "http.client"}
    forbidden_calls = {
        "damped_newton", "shooting_residual", "centered_fd_jacobian",
        "least_squares", "solve_ivp", "root",
    }
    if forbidden_modules.intersection(wrapper_scan["modules"]):
        raise BASE.ReleaseFailure("forbidden module imported by v0.2 adapter")
    if forbidden_calls.intersection(wrapper_scan["calls"]):
        raise BASE.ReleaseFailure("forbidden numerical call present in v0.2 adapter")
    result.update({
        "status": "PASS_3C12_V02_STATIC_AUDIT_NO_BACKEND_IMPORT_NO_EXECUTION",
        "release_adapter": "v0.2",
        "base_release": str(BASE_RELEASE_PATH.relative_to(ROOT)),
        "target_contract": str(TARGET_CONTRACT_V02_PATH.relative_to(ROOT)),
        "source_count": len(package_paths()),
        "pre_audit_correction": correction["corrected_item"],
        "default_not_before_equals_issued_at": True,
        "wrapper_modules": wrapper_scan["modules"],
    })
    return result


def self_test() -> dict[str, Any]:
    result = BASE.self_test()
    if result.get("status") != "PASS_3C12_NONOPERATIVE_GRANT_AND_TARGET_PATH_CONTROLS":
        raise BASE.ReleaseFailure("v0.2 self-test status drift")
    result.update({
        "status": "PASS_3C12_V02_NONOPERATIVE_GRANT_AND_TARGET_PATH_CONTROLS",
        "release_adapter": "v0.2",
        "source_count": len(package_paths()),
        "pre_audit_correction": "DEFAULT_SYNTHETIC_NOT_BEFORE_EQUALS_ISSUED_AT",
        "default_not_before_equals_issued_at": True,
    })
    return result


def denied_physical_run() -> dict[str, Any]:
    result = BASE.denied_physical_run()
    result["release_adapter"] = "v0.2"
    return result


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit", "self-test", "run"))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def emit(value: dict[str, Any], as_json: bool) -> None:
    print(json.dumps(value, indent=2, sort_keys=True) if as_json else value["status"])


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "audit":
            emit(static_audit(), args.json)
            return 0
        if args.command == "self-test":
            emit(self_test(), args.json)
            return 0
        if args.command == "run":
            emit(denied_physical_run(), args.json)
            return BASE.EXIT_NOT_AUTHORIZED
    except BASE.ReleaseFailure as exc:
        emit({
            "status": "CONTROL_RELEASE_FAILURE",
            "error": str(exc),
            "physical_backend_imports": BASE.PHYSICAL_BACKEND_IMPORT_COUNT,
            "physical_solver_calls": BASE.PHYSICAL_SOLVER_CALL_COUNT,
            "cp01r1_attempts": BASE.CP01R1_ATTEMPT_COUNT,
            "target_solves": BASE.TARGET_SOLVE_COUNT,
            "operative_grants": BASE.OPERATIVE_GRANT_COUNT,
            "physical_results": BASE.PHYSICAL_RESULT_COUNT,
            "physical_evidence_effect": "NONE",
        }, args.json)
        return BASE.EXIT_CONTROL_FAILURE
    return BASE.EXIT_CONTROL_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
