#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c10_v0.3.py"
RELEASE_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_control_release_v0.3.py"
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
    validator = load("background3c10_validator_v03_test", VALIDATOR_PATH)
    release = load("background3c10_release_v03_test", RELEASE_PATH)

    result = validator.validate()
    assert result["status"] == "PASS"
    assert result["r1_status"] == release.R1_FAILURE_STATUS
    assert result["r2_status"] == release.R2_FAILURE_STATUS
    assert result["r3_control_run_id"] == release.CONTROL_RUN_ID
    assert result["control_status"] == "PASS_REAL_BACKEND_AF0_CONTROL_RELEASE_NO_TARGET_SOLVE"
    assert result["candidate_sha256"] == "6a00f71f4904574841d17eaebba7f8318fc136d477ab6fd324f3354f1b33e400"
    assert result["worker_launch_count"] == 5
    assert result["real_backend_control_processes"] == 4
    assert result["independent_integration_call_count"] == 6
    assert result["primary_timeout_import_attested"] is True
    assert result["independent_signal_import_attested"] is True
    assert result["additional_probe_worker_launches"] == 2
    assert result["json_mapping_key_order_semantic"] is False
    assert result["handoff_vector_order_source"] == "EXPLICIT_CANDIDATE_FIELDS_CONTRACT"
    assert result["primary_newton_calls"] == 0
    assert result["shooting_jacobian_calls"] == 0
    assert result["nonlinear_root_calls"] == 0
    assert result["cp01r1_attempts"] == 0
    assert result["target_a_F_one_quarter_solves"] == 0
    assert result["operative_grants"] == 0
    assert result["physical_result_artifacts"] == 0
    assert result["continuum_convergence_inference_allowed"] is False
    assert result["physical_evidence_effect"] == "NONE"

    residuals = result["primary_bulk_residuals_by_node_count"]
    assert residuals["24"] <= 1e-9
    assert residuals["48"] <= 1e-9
    assert residuals["96"] <= 3e-8
    assert residuals["96"] > 1e-9

    payload = release.load_json(RUN_INPUT_PATH)["frozen_run_payload"]
    primary_request = release.worker_envelope("primary_control", payload)
    primary_request["node_counts"] = [24, 48, 96]
    primary_raw = release.launch_worker(primary_request)
    assert primary_raw["returncode"] == 0
    primary = primary_raw["stdout"]

    base_independent = release.worker_envelope("independent_control", payload)
    base_independent["cutoffs"] = [0.001, 0.0005, 0.00025]
    base_independent["handoff"] = {
        "candidate": primary["candidate"],
        "candidate_sha256": primary["candidate_sha256"],
    }

    reordered = release.launch_worker(base_independent)
    assert reordered["returncode"] == 0
    assert reordered["stdout"]["status"] == "PASS_REAL_INDEPENDENT_AF0_CONTROL_NO_ROOT"
    assert reordered["stdout"]["json_mapping_key_order_semantic"] is False

    missing = release.BASE.json.loads(release.BASE.json.dumps(base_independent))
    del missing["handoff"]["candidate"]["q_N"]
    missing_result = release.launch_worker(missing)
    assert missing_result["returncode"] == 2
    assert "missing" in missing_result["stdout"]["error"]

    unknown = release.BASE.json.loads(release.BASE.json.dumps(base_independent))
    unknown["handoff"]["candidate"]["unexpected"] = 1.0
    unknown_result = release.launch_worker(unknown)
    assert unknown_result["returncode"] == 2
    assert "unknown" in unknown_result["stdout"]["error"]

    forbidden = release.worker_envelope("primary_control", payload)
    forbidden["node_counts"] = [24, 48, 96]
    forbidden["control_a_F"] = 0.25
    rejection = release.launch_worker(forbidden)
    assert rejection["returncode"] == 2
    assert "a_F=0" in rejection["stdout"]["error"]

    stale_r2 = release.worker_envelope("primary_control", payload)
    stale_r2["node_counts"] = [24, 48, 96]
    stale_r2["control_run_id"] = "HZT-M0-S6-C-PHYS-M1-BG3C10-AF0-CONTROL-R2"
    stale_rejection = release.launch_worker(stale_r2)
    assert stale_rejection["returncode"] == 2
    assert "R3" in stale_rejection["stdout"]["error"]

    try:
        release.BASE.AtomicControlWriter(ROOT, "FORBIDDEN-REPOSITORY-OUTPUT")
    except release.BASE.ReleaseFailure as exc:
        assert "external" in str(exc)
    else:
        raise AssertionError("repository output root was accepted")

    denial = release.denied_physical_run()
    assert denial["status"] == "NOT_AUTHORIZED"
    assert denial["control_run_id"] == release.CONTROL_RUN_ID
    assert denial["r1_failure_preserved"] is True
    assert denial["r2_failure_preserved"] is True
    assert denial["physical_backend_imported"] is False
    assert denial["solver_calls"] == 0
    assert denial["cp01r1_attempted"] is False
    assert denial["target_a_F_one_quarter_solve"] is False
    assert denial["operative_grant_created"] is False
    assert denial["result_artifact_created"] is False

    print("PASS: Background-3C10 R3 explicit-order regression tests")


if __name__ == "__main__":
    main()
