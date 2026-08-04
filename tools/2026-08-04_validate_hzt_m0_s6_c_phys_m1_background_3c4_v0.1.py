#!/usr/bin/env python3
"""Fail-closed validator for Background-3C4 execution-runner implementation."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_execution_runner_v0.1.py"
CONTRACT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C4ExecutionRunnerContract_v0.1.json"
GRANT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
ARTIFACT_ROOT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"


def load_module():
    spec = importlib.util.spec_from_file_location("background3c4_runner", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to import 3C4 runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate() -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    runner = load_module()
    audit = runner.audit_package()
    self_test = runner.self_test()

    assert contract["status"] == "IMPLEMENTED_AUDIT_ONLY_EXECUTION_NOT_AUTHORIZED"
    assert contract["execution_authorized"] is False
    assert contract["physical_evidence_effect"] == "NONE"
    assert contract["authorization_firewall"]["future_grant_present"] is False
    assert not GRANT_PATH.exists()
    assert not ARTIFACT_ROOT.exists()

    assert audit["status"] == "PASS_EXECUTION_PACKAGE_AUDIT_NO_SOLVER_CALLS"
    assert audit["authorization_grant_present"] is False
    assert audit["primary_root_calls"] == 0
    assert audit["independent_root_calls"] == 0
    assert audit["independent_jacobian_calls"] == 0
    assert audit["result_artifact_created"] is False
    assert re.fullmatch(r"[0-9a-f]{64}", audit["package_manifest_sha256"])

    assert self_test["status"] == "PASS_EXECUTION_PACKAGE_SELF_TEST_NO_SOLVER_CALLS"
    assert self_test["primary_root_calls"] == 0
    assert self_test["independent_root_calls"] == 0
    assert self_test["independent_jacobian_calls"] == 0
    assert self_test["repository_result_artifact_created"] is False

    return {
        "status": "PASS",
        "audit_status": audit["status"],
        "self_test_status": self_test["status"],
        "package_manifest_sha256": audit["package_manifest_sha256"],
        "grant_present": False,
        "solver_calls": 0,
        "result_artifact_created": False,
        "physical_evidence_effect": "NONE",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS: Background-3C4 execution package implemented and audited without solver calls")


if __name__ == "__main__":
    main()
