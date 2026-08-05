#!/usr/bin/env python3
"""Canonical G0 v1.17 validator after Background-3C6 control-release audit."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RELEASE = "2.17-c-phys-m1-background-3c6-integrated-control-release-audited-v0.1"
DECISION = "UL-DEC-0032"
CHECKPOINT = "UL-CHK-20260805-025"
SNAPSHOT = ROOT / "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.25.json"
LATEST = ROOT / "registry/session-checkpoint-latest.json"
MANIFEST = ROOT / "project-manifest.json"
DECISIONS = ROOT / "registry/decision-log.jsonl"
CONTRACT = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C6IntegratedExecutionReleaseContract_v0.1.json"
AUDIT_RESULT = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C6IntegratedExecutionReleaseAuditResult_v0.1.json"
BG3C6_VALIDATOR = ROOT / "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c6_v0.1.py"
GRANT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
PHYSICAL_ARTIFACT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
NEXT = "C-PHYS-R1.0-BACKGROUND-3C7_INTEGRATED_RELEASE_AUTHORIZATION_REVIEW_ONLY"
DIGEST = "297272556025d86eadad2c8f18caaa4f48fd643c295c8c7dc384be5606b9d147"
OLD_NEXT = "C-PHYS-R1.0-BACKGROUND-3C6_INTEGRATED_EXECUTION_RELEASE_IMPLEMENTATION_ONLY"
OLD_STATUS = "BACKGROUND_3C_AUTHORIZATION_DENIED_EXECUTION_RUNNER_MISSING"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_bg3c6_validator():
    spec = importlib.util.spec_from_file_location("bg3c6_g0_v117", BG3C6_VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to import Background-3C6 validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def find_exact(value: Any, target: str, path: str = "$") -> list[str]:
    if isinstance(value, dict):
        found: list[str] = []
        for key, item in value.items():
            found.extend(find_exact(item, target, f"{path}.{key}"))
        return found
    if isinstance(value, list):
        found = []
        for index, item in enumerate(value):
            found.extend(find_exact(item, target, f"{path}[{index}]"))
        return found
    return [path] if value == target else []


def validate() -> dict[str, Any]:
    manifest = load(MANIFEST)
    latest = load(LATEST)
    snapshot = load(SNAPSHOT)
    contract = load(CONTRACT)
    audit_result = load(AUDIT_RESULT)
    decisions = [
        json.loads(line)
        for line in DECISIONS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert manifest["release"] == RELEASE
    assert manifest["release_date"] == "2026-08-05"
    assert LATEST.read_bytes() == SNAPSHOT.read_bytes()
    assert latest == snapshot
    assert latest["checkpoint_id"] == CHECKPOINT
    assert latest["canonical_snapshot"] == str(SNAPSHOT.relative_to(ROOT))
    assert latest["basis_commit"] == "5311dee824b334c8b93e4adf43fb3526c6af5648"
    assert latest["current_workstreams"][0]["next_block"] == NEXT
    assert latest["next_exact_action"].startswith("Execute " + NEXT)

    selected = [item for item in decisions if item.get("decision_id") == DECISION]
    assert len(selected) == 1
    assert selected[0]["topic"] == "background_3c6_integrated_control_release_audit"
    assert selected[0]["evidence_effect"] == "SOFTWARE_END_TO_END_CONTROL_TRANSACTION_QA_ONLY"
    assert selected[0]["physical_evidence_effect"] == "NONE"

    gates = manifest["gates"]
    expected_gates = {
        "R1.0": "ACTIVE_INTEGRATED_RELEASE_AUTHORIZATION_REVIEW_REMAINING",
        "BACKGROUND_SOLVER_IMPLEMENTATION": "INTEGRATED_CONTROL_RELEASE_AUDITED_PHYSICAL_EXECUTION_NOT_AUTHORIZED",
        "BACKGROUND_3C6_EXECUTION_RELEASE": "PASS_AUDITED_CONTROL_ONLY",
        "BACKGROUND_3C7_AUTHORIZATION_REVIEW": "NOT_STARTED",
        "BACKGROUND_3C_EXECUTION": "NOT_AUTHORIZED",
        "BACKGROUND_SOLVER_EXECUTION": "NOT_AUTHORIZED",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    for key, expected in expected_gates.items():
        assert gates.get(key) == expected, (key, gates.get(key), expected)

    tracks = {
        item["id"]: item
        for item in manifest["architecture"]["research_tracks"]
    }
    assert tracks["MD2S-R1-C-PHYS"]["status"] == "ACTIVE_INTEGRATED_RELEASE_AUTHORIZATION_REVIEW_REMAINING"
    assert manifest["next_block"] == NEXT
    assert manifest["parent_action_v0_1"]["next_block"] == NEXT
    assert manifest["c_phys_operator_entry"]["status"] == "BACKGROUND_3C6_CONTROL_RELEASE_AUDITED_AUTHORIZATION_REVIEW_REMAINING"
    assert manifest["c_phys_operator_entry"]["solver_authorized"] is False
    assert manifest["c_phys_operator_entry"]["next_block"] == NEXT
    assert find_exact(manifest, OLD_NEXT) == []
    assert find_exact(manifest, OLD_STATUS) == []

    assert contract["physical_execution_authorized"] is False
    assert contract["cp01r1_execution_authorized"] is False
    assert contract["physical_evidence_effect"] == "NONE"
    assert audit_result["status"] == "PASS_INTEGRATED_CONTROL_RELEASE_AUDIT_NO_PHYSICAL_EXECUTION"
    assert audit_result["package_manifest_sha256"] == DIGEST
    assert audit_result["control_results"] == contract["expected_control_classifications"]
    counts = audit_result["transaction_counts"]
    assert counts["registered_control_subprocess_launches"] == 4
    assert counts["committed_control_artifacts_in_temporary_storage"] == 2
    assert counts["clean_abort_controls_without_final_artifact"] == 2
    assert counts["primary_root_calls"] == 0
    assert counts["independent_root_calls"] == 0
    assert counts["shooting_jacobian_calls"] == 0
    assert counts["cp01r1_attempts"] == 0
    assert counts["target_a_F_one_quarter_solves"] == 0
    assert load_bg3c6_validator().validate()["status"] == "PASS"

    blockers = {item["blocker_id"] for item in latest["open_blockers"]}
    assert "UL-BLK-C-PHYS-BACKGROUND-3C6-001" not in blockers
    assert "UL-BLK-C-PHYS-BACKGROUND-3C7-001" in blockers
    verified = {item["result_id"]: item for item in latest["verified_results"]}
    result = verified["UL-RES-C-PHYS-M1-BG3C6-001"]
    assert result["status"] == "PASS_AUDITED_CONTROL_ONLY"
    assert result["package_manifest_sha256"] == DIGEST
    assert result["physical_evidence_effect"] == "NONE"

    assert not GRANT.exists()
    assert not PHYSICAL_ARTIFACT.exists()

    return {
        "status": "PASS",
        "release": RELEASE,
        "decision": DECISION,
        "checkpoint": CHECKPOINT,
        "package_manifest_sha256": DIGEST,
        "control_subprocesses": 4,
        "physical_solver_calls": 0,
        "cp01r1_attempts": 0,
        "execution_authorized": False,
        "physical_background": "NOT_ESTABLISHED",
        "physical_evidence_effect": "NONE",
        "next_block": NEXT,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS: G0 v1.17 Background-3C6 canonical state")


if __name__ == "__main__":
    main()
