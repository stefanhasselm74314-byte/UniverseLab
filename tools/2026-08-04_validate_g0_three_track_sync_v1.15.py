#!/usr/bin/env python3
"""Canonical G0 v1.15 validator after Background-3C4 package audit."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RELEASE = "2.15-c-phys-m1-background-3c4-execution-package-audited-v0.1"
EXPECTED_DECISION = "UL-DEC-0030"
EXPECTED_CHECKPOINT = "UL-CHK-20260804-023"
EXPECTED_SNAPSHOT = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.23.json"
EXPECTED_DIGEST = "f274333e6d0a94e9c4bedfe179e9781d7175e484dc70de5396aedee7872033cd"
EXPECTED_NEXT = "C-PHYS-R1.0-BACKGROUND-3C5_EXECUTION_PACKAGE_AUTHORIZATION_REVIEW_ONLY"

MANIFEST = ROOT / "project-manifest.json"
DECISIONS = ROOT / "registry/decision-log.jsonl"
LATEST = ROOT / "registry/session-checkpoint-latest.json"
SNAPSHOT = ROOT / EXPECTED_SNAPSHOT
CONTRACT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C4ExecutionRunnerContract_v0.1.json"
AUDIT_RESULT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C4ExecutionPackageAuditResult_v0.1.json"
BG3C4_VALIDATOR = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3c4_v0.1.py"
GRANT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
ARTIFACT_ROOT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_bg3c4_validator():
    spec = importlib.util.spec_from_file_location("bg3c4_validator_for_g0", BG3C4_VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to import Background-3C4 validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate():
    manifest = load(MANIFEST)
    latest = load(LATEST)
    snapshot = load(SNAPSHOT)
    contract = load(CONTRACT)
    audit_result = load(AUDIT_RESULT)
    decisions = [json.loads(line) for line in DECISIONS.read_text(encoding="utf-8").splitlines() if line.strip()]

    assert manifest["release"] == EXPECTED_RELEASE
    assert latest == snapshot
    assert latest["checkpoint_id"] == EXPECTED_CHECKPOINT
    assert latest["canonical_snapshot"] == EXPECTED_SNAPSHOT
    assert latest["current_workstreams"][0]["next_block"] == EXPECTED_NEXT
    assert latest["next_exact_action"].startswith("Execute " + EXPECTED_NEXT)

    matching = [item for item in decisions if item.get("decision_id") == EXPECTED_DECISION]
    assert len(matching) == 1
    assert matching[0]["evidence_effect"] == "SOFTWARE_EXECUTION_PACKAGE_QA_ONLY"

    gates = manifest["gates"]
    expected = {
        "R1.0": "ACTIVE_EXECUTION_PACKAGE_AUTHORIZATION_REVIEW_REMAINING",
        "BACKGROUND_SOLVER_IMPLEMENTATION": "EXECUTION_PACKAGE_AUDITED_NO_EXECUTION",
        "BACKGROUND_3C4_EXECUTION_PACKAGE": "PASS_AUDITED_NO_EXECUTION",
        "BACKGROUND_3C5_AUTHORIZATION_REVIEW": "NOT_STARTED",
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
    for key, value in expected.items():
        assert gates[key] == value, (key, gates.get(key), value)

    assert contract["execution_authorized"] is False
    assert contract["physical_evidence_effect"] == "NONE"
    assert audit_result["package_manifest_sha256"] == EXPECTED_DIGEST
    assert audit_result["call_counters"] == {
        "primary_root_calls": 0,
        "independent_root_calls": 0,
        "independent_jacobian_calls": 0,
        "target_a_F_one_quarter_solves": 0,
    }
    assert audit_result["authorization_state"]["execution_authorized"] is False
    assert not GRANT.exists()
    assert not ARTIFACT_ROOT.exists()

    bg3c4 = load_bg3c4_validator().validate()
    assert bg3c4["status"] == "PASS"
    assert bg3c4["package_manifest_sha256"] == EXPECTED_DIGEST
    assert bg3c4["solver_calls"] == 0
    assert bg3c4["result_artifact_created"] is False

    blocker_ids = {item["blocker_id"] for item in latest["open_blockers"]}
    assert "UL-BLK-C-PHYS-BACKGROUND-3C4-001" not in blocker_ids
    assert "UL-BLK-C-PHYS-BACKGROUND-3C5-001" in blocker_ids

    return {
        "status": "PASS",
        "release": EXPECTED_RELEASE,
        "decision": EXPECTED_DECISION,
        "checkpoint": EXPECTED_CHECKPOINT,
        "package_manifest_sha256": EXPECTED_DIGEST,
        "execution_authorized": False,
        "solver_calls": 0,
        "physical_evidence_effect": "NONE",
        "next_block": EXPECTED_NEXT,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else "PASS: G0 v1.15 Background-3C4 canonical state")


if __name__ == "__main__":
    main()
