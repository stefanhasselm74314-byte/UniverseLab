#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c10_v0.1.py"
RELEASE_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_control_release_v0.1.py"
RUN_INPUT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    validator = load("background3c10_validator_test", VALIDATOR_PATH)
    release = load("background3c10_release_test", RELEASE_PATH)

    result = validator.validate()
    assert result["status"] == "PASS"
    assert result["control_status"] == "PASS_REAL_BACKEND_AF0_CONTROL_RELEASE_NO_TARGET_SOLVE"
    assert result["worker_launch_count"] == 5
    assert result["real_backend_control_processes"] == 4
    assert result["independent_integration_call_count"] == 6
    assert result["primary_newton_calls"] == 0
    assert result["shooting_jacobian_calls"] == 0
    assert result["nonlinear_root_calls"] == 0
    assert result["cp01r1_attempts"] == 0
    assert result["target_a_F_one_quarter_solves"] == 0
    assert result["operative_grants"] == 0
    assert result["physical_result_artifacts"] == 0
    assert result["physical_evidence_effect"] == "NONE"

    payload = release.load_json(RUN_INPUT_PATH)["frozen_run_payload"]
    forbidden = release.worker_envelope("primary_control", payload)
    forbidden["node_counts"] = [24, 48, 96]
    forbidden["control_a_F"] = 0.25
    rejection = release.launch_worker(forbidden)
    assert rejection["timed_out"] is False
    assert rejection["returncode"] == 2
    assert rejection["stdout"]["status"] == "CONTROL_FAILURE"
    assert "a_F=0" in rejection["stdout"]["error"]

    try:
        release.AtomicControlWriter(ROOT, "FORBIDDEN-REPOSITORY-OUTPUT")
    except release.ReleaseFailure as exc:
        assert "external" in str(exc)
    else:
        raise AssertionError("repository output root was accepted")

    denial = release.denied_physical_run()
    assert denial["status"] == "NOT_AUTHORIZED"
    assert denial["physical_backend_imported"] is False
    assert denial["solver_calls"] == 0
    assert denial["cp01r1_attempted"] is False
    assert denial["target_a_F_one_quarter_solve"] is False
    assert denial["operative_grant_created"] is False
    assert denial["result_artifact_created"] is False

    print("PASS: Background-3C10 real-backend control regression tests")


if __name__ == "__main__":
    main()
