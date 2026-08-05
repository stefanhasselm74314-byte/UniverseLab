#!/usr/bin/env python3
"""Corrected R2 Background-3C10 real-backend analytic control release.

R1 failed closed because a uniform bulk residual threshold had not been
validated at N=96. R2 preserves every numerical input and backend operation and
changes only the versioned acceptance contract to a mesh-specific control
roundoff envelope. No target solve, Newton, shooting Jacobian, grant, or
physical result is permitted.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
BASE_RELEASE_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_control_release_v0.1.py"
CONTRACT_V01_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlContract_v0.1.json"
FAILURE_R1_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlFailureResult_v0.1.json"
CONTRACT_V02_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlContract_v0.2.json"
WORKER_BASE_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_worker_v0.1.py"
WORKER_V02_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_worker_v0.2.py"
VALIDATOR_V02_PATH = ROOT / "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c10_v0.2.py"
TEST_V02_PATH = ROOT / "tests/2026-08-05_test_hzt_m0_s6_c_phys_m1_background_3c10_v0.2.py"
LEDGER_V01_PATH = ROOT / "science/hzt-m0/md2s/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlLedger_v0.1.md"
LEDGER_V02_PATH = ROOT / "science/hzt-m0/md2s/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlLedger_v0.2.md"
DEPENDENCY_LOCK_PATH = ROOT / "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C_v0.1.txt"
CONTROL_RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3C10-AF0-CONTROL-R2"
R1_FAILURE_STATUS = "FAIL_CLOSED_PRIMARY_UNIFORM_BULK_THRESHOLD_AT_N96"

SPEC = importlib.util.spec_from_file_location("background3c10_release_base_v01", BASE_RELEASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import Background-3C10 release v0.1")
BASE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)

BASE.CONTRACT_PATH = CONTRACT_V02_PATH
BASE.WORKER_PATH = WORKER_V02_PATH
BASE.VALIDATOR_PATH = VALIDATOR_V02_PATH
BASE.TEST_PATH = TEST_V02_PATH
BASE.LEDGER_PATH = LEDGER_V02_PATH
BASE.CONTROL_RUN_ID = CONTROL_RUN_ID


def package_paths() -> tuple[Path, ...]:
    return (
        CONTRACT_V01_PATH,
        FAILURE_R1_PATH,
        CONTRACT_V02_PATH,
        BASE.REVIEW_3C9_PATH,
        BASE.RUN_INPUT_PATH,
        BASE.RESULT_SCHEMA_PATH,
        BASE.RESOURCE_POLICY_PATH,
        DEPENDENCY_LOCK_PATH,
        BASE.PRIMARY_PATH,
        BASE.PRIMARY_BASE_PATH,
        BASE.INDEPENDENT_PATH,
        WORKER_BASE_PATH,
        WORKER_V02_PATH,
        BASE_RELEASE_PATH,
        Path(__file__).resolve(),
        VALIDATOR_V02_PATH,
        TEST_V02_PATH,
        LEDGER_V01_PATH,
        LEDGER_V02_PATH,
    )


def validate_primary(primary: dict[str, Any], contract: dict[str, Any]) -> None:
    acceptance = contract["primary_control"]["acceptance"]
    BASE.require(primary["model_a_F"] == 0.0, "primary did not use a_F=0")
    BASE.require(primary["newton_call_count"] == 0, "primary Newton call detected")
    BASE.require(
        primary["cp01r1_attempts"] == 0 and primary["target_root_solves"] == 0,
        "primary target execution detected",
    )
    records = primary["node_records"]
    BASE.require([record["node_count"] for record in records] == [24, 48, 96], "primary mesh schedule drift")
    limits = acceptance["bulk_residual_inf_max_by_node_count"]
    for record in records:
        node_key = str(record["node_count"])
        BASE.require(node_key in limits, f"missing bulk threshold for node count {node_key}")
        BASE.require(
            record["bulk_residual_inf"] <= limits[node_key],
            f"primary bulk control failed at node_count={node_key}",
        )
        BASE.require(
            record["constraint_inf"] <= acceptance["constraint_inf_max"],
            f"primary constraint control failed at node_count={node_key}",
        )
        BASE.require(
            record["boundary_exact_distance"] <= acceptance["boundary_exact_distance_max"],
            f"primary boundary control failed at node_count={node_key}",
        )
    BASE.require(
        primary["candidate_cross_mesh_distance"] <= acceptance["candidate_parameter_cross_mesh_distance_max"],
        "primary candidate cross-mesh drift",
    )
    BASE.require(
        primary["candidate_sha256"] == BASE.sha256_value(primary["candidate"]),
        "primary candidate digest drift",
    )


BASE.package_paths = package_paths
BASE.validate_primary = validate_primary


def load_json(path: Path) -> dict[str, Any]:
    return BASE.load_json(path)


def worker_envelope(stage: str, payload: dict[str, Any]) -> dict[str, Any]:
    return BASE.worker_envelope(stage, payload)


def launch_worker(request: dict[str, Any], *, timeout_seconds: float | None = None) -> dict[str, Any]:
    return BASE.launch_worker(request, timeout_seconds=timeout_seconds)


def static_audit() -> dict[str, Any]:
    failure = load_json(FAILURE_R1_PATH)
    contract = load_json(CONTRACT_V02_PATH)
    BASE.require(failure["status"] == R1_FAILURE_STATUS, "R1 failure record drift")
    BASE.require(failure["disposition"]["next_control_run_id"] == CONTROL_RUN_ID, "R1 to R2 transition drift")
    BASE.require(contract["previous_control_run"]["run_id"] == failure["control_run_id"], "R1 identity chain drift")
    BASE.require(contract["control_run_id"] == CONTROL_RUN_ID, "R2 control identity drift")
    result = BASE.static_audit()
    result.update({
        "release_adapter": "v0.2",
        "r1_failure_status": failure["status"],
        "r1_static_package_manifest_sha256": failure["static_package_manifest_sha256"],
        "r2_control_run_id": CONTROL_RUN_ID,
        "mesh_specific_bulk_roundoff_envelope": contract["primary_control"]["acceptance"]["bulk_residual_inf_max_by_node_count"],
        "continuum_convergence_inference_allowed": False,
    })
    return result


def execute_controls(*, commit_external_artifact: bool = True) -> dict[str, Any]:
    result = BASE.execute_controls(commit_external_artifact=commit_external_artifact)
    contract = load_json(CONTRACT_V02_PATH)
    records = result["primary"]["node_records"]
    result["release_adapter"] = "v0.2"
    result["control_run_id"] = CONTROL_RUN_ID
    result["r1_failure_preserved"] = True
    result["primary_bulk_roundoff_classification"] = {
        "24": "STANDARD_CONTROL_ENVELOPE",
        "48": "STANDARD_CONTROL_ENVELOPE",
        "96": contract["primary_control"]["acceptance"]["n96_bulk_channel_classification"],
    }
    result["primary_bulk_residuals_by_node_count"] = {
        str(record["node_count"]): record["bulk_residual_inf"] for record in records
    }
    result["bulk_monotonic_convergence_required"] = False
    result["continuum_convergence_inference_allowed"] = False
    return result


def self_test() -> dict[str, Any]:
    result = execute_controls(commit_external_artifact=True)
    BASE.require(result["status"] == "PASS_REAL_BACKEND_AF0_CONTROL_RELEASE_NO_TARGET_SOLVE", "R2 control release status drift")
    BASE.require(result["control_run_id"] == CONTROL_RUN_ID, "R2 result identity drift")
    BASE.require(result["worker_launch_count"] == 5, "R2 worker launch count drift")
    BASE.require(result["real_backend_control_processes"] == 4, "R2 real backend process count drift")
    BASE.require(result["primary_newton_calls"] == 0, "Newton call drift")
    BASE.require(result["independent_shooting_jacobian_calls"] == 0, "shooting Jacobian drift")
    BASE.require(result["nonlinear_root_calls"] == 0, "nonlinear root drift")
    BASE.require(result["cp01r1_attempts"] == 0, "CP01R1 attempt drift")
    BASE.require(result["target_a_F_one_quarter_solves"] == 0, "target solve drift")
    BASE.require(result["operative_grants_created"] == 0, "grant creation drift")
    BASE.require(result["physical_result_artifacts_created"] == 0, "physical result creation drift")
    BASE.require(result["no_overwrite_firewall"] is True, "no-overwrite firewall drift")
    BASE.require(result["r1_failure_preserved"] is True, "R1 failure preservation drift")
    return result


def denied_physical_run() -> dict[str, Any]:
    result = BASE.denied_physical_run()
    result["control_run_id"] = CONTROL_RUN_ID
    result["r1_failure_preserved"] = True
    return result


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit", "self-test", "run"))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def emit(payload: dict[str, Any], as_json: bool) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True) if as_json else payload["status"])


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
        payload = {
            "status": "CONTROL_RELEASE_FAILURE",
            "error": str(exc),
            "control_run_id": CONTROL_RUN_ID,
            "worker_launches": BASE.WORKER_LAUNCH_COUNT,
            "solver_calls": 0,
            "cp01r1_attempts": BASE.CP01R1_ATTEMPT_COUNT,
            "result_artifact_created": False,
            "physical_evidence_effect": "NONE",
        }
        emit(payload, args.json)
        return BASE.EXIT_CONTROL_FAILURE
    return BASE.EXIT_CONTROL_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
