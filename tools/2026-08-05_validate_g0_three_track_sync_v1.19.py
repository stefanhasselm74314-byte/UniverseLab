#!/usr/bin/env python3
"""Canonical G0 v1.19 validator after the Background-3C8 adapter audit."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RELEASE = "2.19-c-phys-m1-background-3c8-physical-adapter-audited-v0.1"
DECISION = "UL-DEC-0034"
CHECKPOINT = "UL-CHK-20260805-027"
ADAPTER_STATUS = "PASS_AUDITED_MANUFACTURED_CONTROLS_ONLY"
NEXT = "C-PHYS-R1.0-BACKGROUND-3C9_PHYSICAL_ADAPTER_AUTHORIZATION_REVIEW_ONLY"
OLD_NEXT = "C-PHYS-R1.0-BACKGROUND-3C8_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_ONLY"
OLD_ACTIVE = "ACTIVE_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_REMAINING"
PACKAGE_DIGEST = "497d6da51d0d7f436ae7cf24d8c4acad93d5e2423ab9eb717ec016c776e27613"
SCHEDULE_DIGEST = "95001986dc93818f0fea3124cf9ddcd63eb136f8d206f6200a4e8c0cf6d54927"
SNAPSHOT = ROOT / "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.27.json"
LATEST = ROOT / "registry/session-checkpoint-latest.json"
MANIFEST = ROOT / "project-manifest.json"
DECISIONS = ROOT / "registry/decision-log.jsonl"
AUDIT_RESULT = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C8PhysicalExecutionAdapterAuditResult_v0.1.json"
ADAPTER_VALIDATOR = ROOT / "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c8_v0.1.py"
GRANTS = [
    ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",
    ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",
]
ARTIFACT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def find_exact(value: Any, target: str, path: str = "$") -> list[str]:
    if isinstance(value, dict):
        result: list[str] = []
        for key, item in value.items():
            result.extend(find_exact(item, target, f"{path}.{key}"))
        return result
    if isinstance(value, list):
        result = []
        for index, item in enumerate(value):
            result.extend(find_exact(item, target, f"{path}[{index}]"))
        return result
    return [path] if value == target else []


def load_adapter_validator():
    spec = importlib.util.spec_from_file_location("bg3c8_g0", ADAPTER_VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("adapter validator import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate() -> dict:
    manifest = load(MANIFEST)
    latest = load(LATEST)
    snapshot = load(SNAPSHOT)
    audit = load(AUDIT_RESULT)
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
    assert latest["basis_commit"] == "b4b2be8128fcaf9cf8980d3b1b4ed1aa71c60355"
    assert latest["canonical_snapshot"] == str(SNAPSHOT.relative_to(ROOT))
    assert latest["current_workstreams"][0]["next_block"] == NEXT

    selected = [item for item in decisions if item.get("decision_id") == DECISION]
    assert len(selected) == 1
    assert selected[0]["physical_evidence_effect"] == "NONE"
    assert selected[0]["evidence_effect"] == "SOFTWARE_PHYSICAL_ADAPTER_BINDING_AND_MANUFACTURED_TRANSACTION_QA_ONLY"

    gates = manifest["gates"]
    expected = {
        "R1.0": "ACTIVE_PHYSICAL_ADAPTER_AUTHORIZATION_REVIEW_REMAINING",
        "BACKGROUND_SOLVER_IMPLEMENTATION":
            "PHYSICAL_ADAPTER_AUDITED_MANUFACTURED_CONTROLS_ONLY_AUTHORIZATION_REVIEW_REMAINING",
        "BACKGROUND_3C8_PHYSICAL_EXECUTION_ADAPTER": ADAPTER_STATUS,
        "BACKGROUND_3C9_AUTHORIZATION_REVIEW": "NOT_STARTED",
        "BACKGROUND_3C_EXECUTION": "NOT_AUTHORIZED",
        "BACKGROUND_SOLVER_EXECUTION": "NOT_AUTHORIZED",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "FULL_LINEARIZED_BOUNDARY_TRACE_RANK": "NOT_PROVEN",
        "FREDHOLM_PROPERTY": "NOT_PROVEN",
        "CONTINUUM_BVP_JACOBIAN": "NOT_PROVEN",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected.items():
        assert gates.get(key) == value, (key, gates.get(key), value)

    assert manifest["next_block"] == NEXT
    assert manifest["parent_action_v0_1"]["next_block"] == NEXT
    assert manifest["c_phys_operator_entry"]["next_block"] == NEXT
    assert manifest["c_phys_operator_entry"]["solver_authorized"] is False
    assert manifest["c_phys_m1"]["next_block"] == NEXT
    assert find_exact(manifest, OLD_NEXT) == []
    assert find_exact(manifest, OLD_ACTIVE) == []
    assert find_exact(latest, OLD_NEXT) == []
    assert find_exact(latest, OLD_ACTIVE) == []

    assert audit["status"] == "PASS_PHYSICAL_ADAPTER_AUDIT_MANUFACTURED_CONTROLS_ONLY"
    assert audit["package_manifest_sha256"] == PACKAGE_DIGEST
    assert audit["immutable_run_binding"]["schedule_sha256"] == SCHEDULE_DIGEST
    assert audit["immutable_run_binding"]["schedule_entry_count"] == 35
    assert audit["real_backend_source_binding"]["physical_backend_imported"] is False
    counts = audit["transaction_counts"]
    assert counts["manufactured_subprocess_launches"] == 6
    assert counts["committed_external_control_artifacts"] == 2
    assert counts["clean_abort_controls_without_final_artifact"] == 2
    assert counts["primary_physical_root_calls"] == 0
    assert counts["independent_physical_root_calls"] == 0
    assert counts["shooting_jacobian_calls"] == 0
    assert counts["cp01r1_attempts"] == 0
    assert counts["operative_grants_created"] == 0
    assert counts["repository_physical_result_artifacts"] == 0
    assert audit["physical_evidence_effect"] == "NONE"

    adapter_result = load_adapter_validator().validate()
    assert adapter_result["status"] == "PASS"
    assert adapter_result["package_manifest_sha256"] == PACKAGE_DIGEST
    assert adapter_result["schedule_sha256"] == SCHEDULE_DIGEST
    assert adapter_result["physical_backend_imported"] is False
    assert adapter_result["physical_solver_calls"] == 0
    assert adapter_result["cp01r1_attempts"] == 0
    assert adapter_result["operative_grant_present"] is False
    assert adapter_result["physical_result_artifact_present"] is False

    blockers = {item["blocker_id"] for item in latest["open_blockers"]}
    assert "UL-BLK-C-PHYS-BACKGROUND-3C8-001" not in blockers
    assert "UL-BLK-C-PHYS-BACKGROUND-3C9-001" in blockers
    verified = {item["result_id"]: item for item in latest["verified_results"]}
    result = verified["UL-RES-C-PHYS-M1-BG3C8-001"]
    assert result["status"] == ADAPTER_STATUS
    assert result["package_manifest_sha256"] == PACKAGE_DIGEST
    assert result["schedule_sha256"] == SCHEDULE_DIGEST
    assert result["physical_evidence_effect"] == "NONE"

    assert all(not path.exists() for path in GRANTS)
    assert not ARTIFACT.exists()

    return {
        "status": "PASS",
        "release": RELEASE,
        "decision": DECISION,
        "checkpoint": CHECKPOINT,
        "adapter_status": ADAPTER_STATUS,
        "package_manifest_sha256": PACKAGE_DIGEST,
        "schedule_sha256": SCHEDULE_DIGEST,
        "execution_authorized": False,
        "physical_backend_imported": False,
        "physical_solver_calls": 0,
        "cp01r1_attempts": 0,
        "physical_evidence_effect": "NONE",
        "next_block": NEXT,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else "PASS: G0 v1.19")


if __name__ == "__main__":
    main()
