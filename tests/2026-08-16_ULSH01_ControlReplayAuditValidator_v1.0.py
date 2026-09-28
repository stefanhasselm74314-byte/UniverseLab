#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "registry/2026-08-16_ULSH01_ControlReplayAuditResult_v1.0.json"
REPLAY_CONTRACT = ROOT / "registry/2026-08-16_ULSH01_ControlReplayContract_v1.0.json"
REFERENCE = ROOT / "reproducibility/ulsh-01/2026-08-16_ULSH01_ControlReferenceOutput_v1.0.json"
SOURCE_AUDIT = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlAuditResult_v0.3.json"
SITE_STATE = ROOT / "registry/2026-08-16_UniverseLab_SiteState_v1.0.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"object required: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> dict[str, Any]:
    audit = load(AUDIT)
    contract = load(REPLAY_CONTRACT)
    reference = load(REFERENCE)
    source_audit = load(SOURCE_AUDIT)
    site_state = load(SITE_STATE)

    assert audit["schema"] == "universelab.ulsh01.control-replay-audit-result.v1"
    assert audit["module_id"] == contract["module_id"] == "ULSH-01"
    assert audit["solver_id"] == contract["solver_id"] == "MD2S-BVP"
    assert audit["replay_id"] == contract["replay_id"]
    assert audit["status"] == contract["pass_status"] == "PASS_FRESH_AF0_CONTROL_REPLAY_NUMERICAL_MATCH"
    assert audit["control_replay"] == "NUMERICAL_MATCH"
    assert audit["physical_evidence_effect"] == "NONE"
    assert audit["physical_gate_effect"] == "NONE"

    execution = audit["canonical_main_execution"]
    commit = execution["repository_commit"]
    assert re.fullmatch(r"[0-9a-f]{40}", commit)
    assert execution["workflow_conclusion"] == "success"
    assert execution["workflow_run_id"] == 31933256761
    assert execution["workflow_job_id"] == 95131171072
    assert execution["runner"] == contract["execution_binding"]["runner"] == "ubuntu-24.04"
    assert execution["python"] == contract["execution_binding"]["python"] == "3.12"
    artifact = execution["artifact"]
    assert artifact["id"] == 9259899329
    assert artifact["name"] == "2026-08-16_ULSH01_ControlReplayStatus_v1.0"
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", artifact["digest"])
    assert artifact["repository_audit_persists_after_artifact_expiry"] is True

    members = audit["artifact_member_sha256"]
    assert set(members) == {
        "2026-08-16_ULSH01_ControlReplayStatus_v1.0.json",
        "2026-08-16_ULSH01_FreshAF0ControlReplay_v1.0.json",
        "2026-08-16_ULSH01_PhysicalTargetDenial_v1.0.json",
        "2026-08-16_ULSH01_PhysicalTargetDenialExitCode_v1.0.txt",
        "2026-08-16_ULSH01_StaticPackageStatus_v1.0.json",
    }
    assert all(re.fullmatch(r"[0-9a-f]{64}", value) for value in members.values())

    binding = audit["reference_binding"]
    assert binding["control_run_id"] == reference["control_run_id"] == source_audit["control_run_id"]
    assert binding["reference_output_sha256"] == sha256(REFERENCE)
    assert binding["closed_package_manifest_sha256"] == source_audit["closed_package"]["package_manifest_sha256"]
    assert binding["candidate_sha256"] == reference["primary_control"]["candidate_sha256"]
    assert binding["candidate_bitwise_digest_match"] is True
    assert binding["candidate_max_absolute_error"] == 0.0
    assert binding["candidate_numeric_tolerance_absolute"] == contract["comparison_contract"]["candidate_absolute_tolerance"] == 1e-12
    assert binding["candidate_numeric_tolerance_relative"] == contract["comparison_contract"]["candidate_relative_tolerance"] == 1e-12

    metrics = audit["fresh_replay_metrics"]
    assert metrics["metric_thresholds"] == "PASS"
    assert set(metrics["primary_bulk_fraction_of_limit"]) == {"24", "48", "96"}
    assert all(0.0 <= float(value) <= 1.0 for value in metrics["primary_bulk_fraction_of_limit"].values())
    assert [float(row["epsilon"]) for row in metrics["independent_cutoff_fraction_of_limit"]] == [0.001, 0.0005, 0.00025]
    for row in metrics["independent_cutoff_fraction_of_limit"]:
        for key in ("profile", "constraint", "boundary", "backend_distance"):
            assert 0.0 <= float(row[key]) <= 1.0

    firewall = audit["execution_firewall"]
    assert firewall["status"] == "PASS"
    for key in (
        "cp01r1_attempts",
        "target_a_F_one_quarter_solves",
        "primary_newton_calls",
        "independent_shooting_jacobian_calls",
        "nonlinear_root_calls",
        "operative_grants_created",
        "physical_result_artifacts_created",
    ):
        assert firewall[key] == 0
    assert firewall["physical_cli_denial"] == "PASS_EXIT_73"
    assert firewall["physical_target"] == "NOT_APPLICABLE_NOT_AUTHORIZED"

    gov = audit["governance_state_after_replay"]
    assert gov == {
        "solver_release": "NOT_AUTHORIZED",
        "physical_background": "NOT_ESTABLISHED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
        "physical_gate_effect": "NONE",
        "ULSH01_release_gate": "NOT_SATISFIED",
    }

    assert site_state["version"] == "1.0.2"
    assert site_state["source_commit"] == commit
    assert site_state["physical_gate_effect"] == "NONE"
    assert site_state["governance"]["K1-D"] == "NOT_RELEASED"
    assert site_state["governance"]["K1-E"] == "NOT_ADMISSIBLE"
    assert site_state["governance"]["physical_evidence_effect"] == "NONE"
    modules = {module["module_id"]: module for module in site_state["modules"]}
    u = modules["ULSH-01"]
    assert u["technical"]["reference_replay"] == "NUMERICAL_MATCH_AF0_CONTROL_ONLY"
    assert u["technical"]["control_replay"] == audit["status"]
    assert u["technical"]["control_replay_scope"] == "SOFTWARE_NUMERICAL_REPRODUCIBILITY_ONLY"
    assert u["technical"]["physical_target_replay"] == "NOT_APPLICABLE_NOT_AUTHORIZED"
    assert u["governance"]["solver_release"] == "NOT_AUTHORIZED"
    assert u["governance"]["K1-D"] == "NOT_RELEASED"
    assert u["governance"]["K1-E"] == "NOT_ADMISSIBLE"
    assert u["governance"]["physical_evidence_effect"] == "NONE"
    assert u["scientific"]["physical_background"] == "NOT_ESTABLISHED"
    assert u["release_gate"]["status"] == "NOT_SATISFIED"
    provenance = u["provenance"]
    assert provenance["control_replay_audit"] == "registry/2026-08-16_ULSH01_ControlReplayAuditResult_v1.0.json"
    assert provenance["control_replay_main_commit"] == commit
    assert provenance["control_replay_workflow_run_id"] == str(execution["workflow_run_id"])
    assert provenance["control_replay_artifact_id"] == str(artifact["id"])
    assert provenance["control_replay_artifact_digest"] == artifact["digest"]

    return {
        "schema": "universelab.ulsh01.control-replay-audit-validation.v1",
        "version": "1.0.0",
        "module_id": "ULSH-01",
        "status": "PASS_PERSISTED_CONTROL_REPLAY_AUDIT_BINDING",
        "control_replay": "NUMERICAL_MATCH",
        "canonical_replay_commit": commit,
        "canonical_workflow_run_id": execution["workflow_run_id"],
        "canonical_artifact_id": artifact["id"],
        "reference_output_sha256": binding["reference_output_sha256"],
        "candidate_max_absolute_error": binding["candidate_max_absolute_error"],
        "metric_thresholds": "PASS",
        "execution_firewalls": "PASS",
        "physical_target": "NOT_APPLICABLE_NOT_AUTHORIZED",
        "solver_release": "NOT_AUTHORIZED",
        "physical_background": "NOT_ESTABLISHED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
        "physical_gate_effect": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
