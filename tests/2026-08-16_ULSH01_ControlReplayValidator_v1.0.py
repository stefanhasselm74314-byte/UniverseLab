#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-08-16_ULSH01_ControlReplayContract_v1.0.json"
REFERENCE = ROOT / "reproducibility/ulsh-01/2026-08-16_ULSH01_ControlReferenceOutput_v1.0.json"
TOLERANCE = ROOT / "reproducibility/ulsh-01/2026-08-16_ULSH01_ToleranceContract_v1.0.json"
SITE_STATE = ROOT / "registry/2026-08-16_UniverseLab_SiteState_v1.0.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"object required: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_close(actual: float, expected: float, *, rel_tol: float, abs_tol: float, label: str) -> float:
    error = abs(float(actual) - float(expected))
    if not math.isclose(float(actual), float(expected), rel_tol=rel_tol, abs_tol=abs_tol):
        raise AssertionError(f"{label}: actual={actual!r} expected={expected!r} abs_error={error!r}")
    return error


def validate(replay_path: Path, denied_path: Path, denied_exit_code: int) -> dict[str, Any]:
    contract = load(CONTRACT)
    reference = load(REFERENCE)
    tolerance = load(TOLERANCE)
    replay = load(replay_path)
    denied = load(denied_path)
    site_state = load(SITE_STATE)

    assert contract["schema"] == "universelab.ulsh01.control-replay-contract.v1"
    assert contract["module_id"] == "ULSH-01"
    assert contract["solver_id"] == "MD2S-BVP"
    assert contract["execution_binding"]["control_a_F"] == 0.0
    assert contract["required_firewalls"]["physical_target_authorized"] is False
    assert contract["scientific_semantics"]["physical_evidence_effect"] == "NONE"
    assert contract["scientific_semantics"]["physical_gate_effect"] == "NONE"

    replay_tol = tolerance["future_replay_numeric_tolerance"]
    compare = contract["comparison_contract"]
    assert compare["candidate_absolute_tolerance"] == replay_tol["candidate_absolute_tolerance"]
    assert compare["candidate_relative_tolerance"] == replay_tol["candidate_relative_tolerance"]
    assert compare["metric_thresholds_remain_authoritative"] is True
    assert replay_tol["metric_thresholds_remain_authoritative"] is True
    assert compare["bitwise_float_identity_required"] is False

    assert replay["status"] == "PASS_REAL_BACKEND_AF0_CONTROL_RELEASE_NO_TARGET_SOLVE"
    assert replay["control_run_id"] == reference["control_run_id"] == contract["execution_binding"]["control_run_id"]
    assert replay["physical_evidence_effect"] == "NONE"
    assert replay["json_mapping_key_order_semantic"] is False
    assert replay["handoff_vector_order_source"] == "EXPLICIT_CANDIDATE_FIELDS_CONTRACT"
    assert replay["r1_failure_preserved"] is True
    assert replay["r2_failure_preserved"] is True
    assert replay["tampered_handoff_rejected"] is True
    assert replay["no_overwrite_firewall"] is True
    assert replay["timeout_probe"] == "PASS_REAL_PRIMARY_IMPORT_THEN_CLEAN_TERMINATION"
    assert replay["signal_probe"] == "PASS_REAL_INDEPENDENT_IMPORT_THEN_SIGNAL_TERMINATION"
    assert replay["worker_launch_count"] == 5
    assert replay["real_backend_control_processes"] == 4

    firewalls = contract["required_firewalls"]
    for key in (
        "cp01r1_attempts",
        "target_a_F_one_quarter_solves",
        "primary_newton_calls",
        "independent_shooting_jacobian_calls",
        "nonlinear_root_calls",
        "operative_grants_created",
        "physical_result_artifacts_created",
    ):
        assert replay[key] == firewalls[key] == 0, f"firewall drift: {key}={replay[key]!r}"

    primary = replay["primary"]
    ref_primary = reference["primary_control"]
    pacc = tolerance["primary_acceptance"]
    assert primary["status"] == ref_primary["status"]
    assert primary["model_a_F"] == ref_primary["model_a_F"] == 0.0
    assert primary["newton_call_count"] == 0
    nodes = [int(record["node_count"]) for record in primary["node_records"]]
    assert nodes == compare["primary_node_schedule_exact"]
    primary_metric_ratios: dict[str, float] = {}
    for record in primary["node_records"]:
        node = str(record["node_count"])
        bulk_limit = float(pacc["bulk_residual_inf_max_by_node_count"][node])
        assert float(record["bulk_residual_inf"]) <= bulk_limit
        assert float(record["constraint_inf"]) <= float(pacc["constraint_inf_max"])
        assert float(record["boundary_exact_distance"]) <= float(pacc["boundary_exact_distance_max"])
        primary_metric_ratios[f"bulk_{node}"] = float(record["bulk_residual_inf"]) / bulk_limit
    assert float(primary["candidate_cross_mesh_distance"]) <= float(pacc["candidate_parameter_cross_mesh_distance_max"])

    atol = float(compare["candidate_absolute_tolerance"])
    rtol = float(compare["candidate_relative_tolerance"])
    candidate = primary["candidate"]
    ref_candidate = ref_primary["candidate"]
    assert set(candidate) == set(ref_candidate)
    candidate_errors = {
        key: assert_close(candidate[key], ref_candidate[key], rel_tol=rtol, abs_tol=atol, label=f"candidate.{key}")
        for key in sorted(ref_candidate)
    }
    candidate_digest_exact = primary.get("candidate_sha256") == ref_primary.get("candidate_sha256")

    independent = replay["independent"]
    ref_independent = reference["independent_control"]
    iacc = tolerance["independent_acceptance"]
    assert independent["status"] == ref_independent["status"]
    assert independent["model_a_F"] == ref_independent["model_a_F"] == 0.0
    assert independent["integration_call_count"] == iacc["integration_call_count"]
    assert independent["shooting_jacobian_call_count"] == iacc["shooting_jacobian_call_count"] == 0
    assert independent["nonlinear_root_calls"] == iacc["nonlinear_root_call_count"] == 0
    cutoffs = [float(record["epsilon"]) for record in independent["cutoff_records"]]
    assert cutoffs == [float(value) for value in compare["independent_cutoff_schedule_exact"]]

    # The raw independent backend records intentionally contain the independent
    # metrics and boundary vector.  The cross-backend distance is computed by
    # the release layer and exported separately in cutoff_table.  Validate both
    # structures and bind them by epsilon instead of assuming the derived field
    # is present in the raw backend record.
    cutoff_table = replay["cutoff_table"]
    assert len(cutoff_table) == len(independent["cutoff_records"])
    table_by_epsilon = {float(record["epsilon"]): record for record in cutoff_table}
    assert set(table_by_epsilon) == set(cutoffs)

    independent_metric_ratios: list[dict[str, float]] = []
    for record in independent["cutoff_records"]:
        epsilon = float(record["epsilon"])
        derived = table_by_epsilon[epsilon]
        assert_close(derived["profile_error_inf"], record["profile_error_inf"], rel_tol=0.0, abs_tol=0.0, label=f"cutoff_table[{epsilon}].profile")
        assert_close(derived["constraint_inf"], record["constraint_inf"], rel_tol=0.0, abs_tol=0.0, label=f"cutoff_table[{epsilon}].constraint")
        assert_close(derived["boundary_exact_distance"], record["boundary_exact_distance"], rel_tol=0.0, abs_tol=0.0, label=f"cutoff_table[{epsilon}].boundary")
        backend_distance = float(derived["primary_independent_boundary_distance"])
        assert float(record["profile_error_inf"]) <= float(iacc["profile_error_inf_max"])
        assert float(record["constraint_inf"]) <= float(iacc["constraint_inf_max"])
        assert float(record["boundary_exact_distance"]) <= float(iacc["boundary_exact_distance_max"])
        assert backend_distance <= float(iacc["primary_independent_boundary_distance_max"])
        independent_metric_ratios.append({
            "epsilon": epsilon,
            "profile": float(record["profile_error_inf"]) / float(iacc["profile_error_inf_max"]),
            "constraint": float(record["constraint_inf"]) / float(iacc["constraint_inf_max"]),
            "boundary": float(record["boundary_exact_distance"]) / float(iacc["boundary_exact_distance_max"]),
            "backend_distance": backend_distance / float(iacc["primary_independent_boundary_distance_max"]),
        })

    assert denied_exit_code == firewalls["physical_run_cli_exit_code"] == 73
    assert denied["status"] == "NOT_AUTHORIZED"
    assert denied["control_run_id"] == reference["control_run_id"]
    assert denied["solver_calls"] == 0
    assert denied["cp01r1_attempted"] is False
    assert denied["target_a_F_one_quarter_solve"] is False
    assert denied["operative_grant_created"] is False
    assert denied["result_artifact_created"] is False
    assert denied["physical_evidence_effect"] == "NONE"

    modules = {item["module_id"]: item for item in site_state["modules"]}
    u = modules["ULSH-01"]
    assert u["governance"]["solver_release"] == "NOT_AUTHORIZED"
    assert u["scientific"]["physical_background"] == "NOT_ESTABLISHED"
    assert u["governance"]["K1-D"] == "NOT_RELEASED"
    assert u["governance"]["K1-E"] == "NOT_ADMISSIBLE"
    assert u["governance"]["physical_evidence_effect"] == "NONE"
    assert u["release_gate"]["status"] == "NOT_SATISFIED"

    return {
        "schema": "universelab.ulsh01.control-replay-status.v1",
        "version": "1.0.0",
        "module_id": "ULSH-01",
        "solver_id": "MD2S-BVP",
        "replay_id": contract["replay_id"],
        "status": contract["pass_status"],
        "control_replay": "NUMERICAL_MATCH",
        "reference_candidate_match": "NUMERICAL_MATCH",
        "candidate_bitwise_digest_match": candidate_digest_exact,
        "candidate_max_absolute_error": max(candidate_errors.values(), default=0.0),
        "metric_thresholds": "PASS",
        "primary_metric_fraction_of_limits": primary_metric_ratios,
        "independent_metric_fraction_of_limits": independent_metric_ratios,
        "execution_firewalls": "PASS",
        "physical_cli_denial": "PASS_EXIT_73",
        "replay_result_sha256": sha256(replay_path),
        "reference_output_sha256": sha256(REFERENCE),
        "replay_commit": os.environ.get("GITHUB_SHA", "LOCAL_WORKTREE"),
        "workflow_run_id": os.environ.get("GITHUB_RUN_ID", "LOCAL"),
        "physical_target": "NOT_APPLICABLE_NOT_AUTHORIZED",
        "solver_release": "NOT_AUTHORIZED",
        "physical_background": "NOT_ESTABLISHED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
        "physical_gate_effect": "NONE"
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay", type=Path, required=True)
    parser.add_argument("--denied", type=Path, required=True)
    parser.add_argument("--denied-exit-code-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    denied_exit_code = int(args.denied_exit_code_file.read_text(encoding="utf-8").strip())
    result = validate(args.replay, args.denied, denied_exit_code)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
