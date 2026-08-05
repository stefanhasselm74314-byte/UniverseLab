#!/usr/bin/env python3
"""Regression tests for the Background-3C6 integrated control release."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ENTRY_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c6_integrated_release_v0.2.py"
CONTRACT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C6IntegratedExecutionReleaseContract_v0.1.json"


def load_entry():
    spec = importlib.util.spec_from_file_location("background3c6_regression_entry", ENTRY_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to import Background-3C6 entry point")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def expect_exception(exception_type, function, *args):
    try:
        function(*args)
    except exception_type as error:
        return str(error)
    raise AssertionError(f"expected {exception_type.__name__}")


def main() -> None:
    entry = load_entry()
    base = entry.BASE
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    audit = entry.audit_release()
    assert audit["status"] == "PASS_INTEGRATED_CONTROL_RELEASE_AUDIT_NO_PHYSICAL_EXECUTION"
    assert audit["subprocess_launch_count"] == 0
    assert audit["forbidden_modules"] == []
    assert audit["forbidden_calls"] == []

    with tempfile.TemporaryDirectory(prefix="universelab-bg3c6-regression-") as directory:
        root = Path(directory)
        initial_launches = base.SUBPROCESS_LAUNCH_COUNT
        invalid_case = expect_exception(
            base.ScopeDenied,
            base.run_control,
            "physical_target",
            "HZT-M0-S6-C-PHYS-M1-BG3C6-CONTROL-INVALID",
            root,
        )
        assert "not registered" in invalid_case
        assert base.SUBPROCESS_LAUNCH_COUNT == initial_launches

        forbidden_id = expect_exception(
            base.ScopeDenied,
            base.run_control,
            "analytic_success",
            "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1",
            root,
        )
        assert "outside the registered prefix" in forbidden_id or "forbidden" in forbidden_id
        assert base.SUBPROCESS_LAUNCH_COUNT == initial_launches

        repository_path = expect_exception(
            base.ScopeDenied,
            base.run_control,
            "analytic_success",
            "HZT-M0-S6-C-PHYS-M1-BG3C6-CONTROL-REPOSITORY-PATH",
            ROOT,
        )
        assert "external to the repository" in repository_path
        assert base.SUBPROCESS_LAUNCH_COUNT == initial_launches

        control_id = "HZT-M0-S6-C-PHYS-M1-BG3C6-CONTROL-NO-OVERWRITE"
        committed = base.run_control("analytic_success", control_id, root)
        assert committed["final_classification"] == "CONTROL_TRANSACTION_PASS"
        assert committed["final_artifact_created"] is True
        launches_after_commit = base.SUBPROCESS_LAUNCH_COUNT
        no_overwrite = expect_exception(
            base.ControlReleaseError,
            base.run_control,
            "analytic_success",
            control_id,
            root,
        )
        assert "already exists" in no_overwrite
        assert base.SUBPROCESS_LAUNCH_COUNT == launches_after_commit
        verified = base.verify_committed_artifact(root / control_id)
        assert verified["result"]["physical_model_evaluated"] is False
        assert verified["result"]["primary_root_calls"] == 0
        assert verified["result"]["independent_root_calls"] == 0
        assert verified["result"]["shooting_jacobian_calls"] == 0
        assert verified["result"]["cp01r1_attempts"] == 0

    denial = base.denied_physical_run("HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1")
    assert denial["status"] == "NOT_AUTHORIZED"
    assert denial["exit_code"] == 73
    assert denial["subprocess_launches"] == 0
    assert denial["solver_calls"] == 0
    assert denial["result_artifact_created"] is False

    assert contract["authorization_firewall"]["control_release_is_cp01r1_grant"] is False
    assert contract["authorization_firewall"]["control_release_may_be_reused_for_physical_execution"] is False
    assert contract["authorization_firewall"]["next_review_may_automatically_execute_cp01r1"] is False
    assert base.PRIMARY_ROOT_CALL_COUNT == 0
    assert base.INDEPENDENT_ROOT_CALL_COUNT == 0
    assert base.SHOOTING_JACOBIAN_CALL_COUNT == 0
    assert base.CP01R1_ATTEMPT_COUNT == 0
    print("PASS: Background-3C6 integrated control-release regression tests")


if __name__ == "__main__":
    main()
