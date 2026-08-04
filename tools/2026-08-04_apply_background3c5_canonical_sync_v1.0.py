#!/usr/bin/env python3
"""One-shot append-only canonical synchronization after Background-3C5."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "project-manifest.json"
DECISION_LOG_PATH = ROOT / "registry/decision-log.jsonl"
LATEST_PATH = ROOT / "registry/session-checkpoint-latest.json"
SNAPSHOT_PATH = ROOT / "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.24.json"

RELEASE = "2.16-c-phys-m1-background-3c5-authorization-denied-v0.1"
DECISION_ID = "UL-DEC-0031"
CHECKPOINT_ID = "UL-CHK-20260804-024"
BASIS_COMMIT = "b61bfbd813e0070dff1296db595b846aa803c3ec"
NEXT_BLOCK = "C-PHYS-R1.0-BACKGROUND-3C6_INTEGRATED_EXECUTION_RELEASE_IMPLEMENTATION_ONLY"
TRACK_STATUS = "ACTIVE_INTEGRATED_EXECUTION_RELEASE_IMPLEMENTATION_REMAINING"

NEW_SOURCES = [
    "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C5ExecutionPackageAuthorizationReview_v0.1.json",
    "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C5AuthorizationReviewLedger_v0.1.md",
    "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3c5_v0.1.py",
    "tests/2026-08-04_test_hzt_m0_s6_c_phys_m1_background_3c5_v0.1.py",
]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def recursive_replace(value):
    if isinstance(value, dict):
        return {key: recursive_replace(item) for key, item in value.items()}
    if isinstance(value, list):
        return [recursive_replace(item) for item in value]
    if isinstance(value, str):
        replacements = {
            "ACTIVE_EXECUTION_PACKAGE_AUTHORIZATION_REVIEW_REMAINING": TRACK_STATUS,
            "C-PHYS-R1.0-BACKGROUND-3C5_EXECUTION_PACKAGE_AUTHORIZATION_REVIEW_ONLY": NEXT_BLOCK,
            "Perform the append-only Background-3C5 authorization review of the audited CP01R1 execution package without running either numerical backend.": "Implement and audit the integrated Background-3C6 execution release using synthetic or analytic end-to-end controls only, without running CP01R1.",
            "PRIMARY_C_PHYS_M1_BACKGROUND_3C5_AUTHORIZATION_REVIEW_WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC": "PRIMARY_C_PHYS_M1_BACKGROUND_3C6_INTEGRATED_EXECUTION_RELEASE_WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC",
        }
        return replacements.get(value, value)
    return value


def synchronize_manifest():
    manifest = recursive_replace(load_json(MANIFEST_PATH))
    manifest["release"] = RELEASE
    for track in manifest.get("architecture", {}).get("research_tracks", []):
        if track.get("id") == "MD2S-R1-C-PHYS":
            track["status"] = TRACK_STATUS
    gates = manifest.setdefault("gates", {})
    gates.update({
        "R1.0": TRACK_STATUS,
        "BACKGROUND_SOLVER_IMPLEMENTATION": "EXECUTION_PACKAGE_COMPONENTS_AUDITED_INTEGRATED_RELEASE_INCOMPLETE",
        "BACKGROUND_3C5_AUTHORIZATION_REVIEW": "DENIED_INTEGRATED_EXECUTION_RELEASE_INCOMPLETE",
        "BACKGROUND_3C6_EXECUTION_RELEASE": "NOT_STARTED",
        "BACKGROUND_3C_EXECUTION": "NOT_AUTHORIZED",
        "BACKGROUND_SOLVER_EXECUTION": "NOT_AUTHORIZED",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    })
    if "next_block" in manifest:
        manifest["next_block"] = NEXT_BLOCK
    dump_json(MANIFEST_PATH, manifest)


def append_decision():
    records = [json.loads(line) for line in DECISION_LOG_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    if any(item.get("decision_id") == DECISION_ID for item in records):
        raise RuntimeError(f"{DECISION_ID} already exists")
    decision = {
        "decision_id": DECISION_ID,
        "date": "2026-08-04",
        "topic": "c_phys_m1_background_3c5_authorization_review",
        "decision": "CP01R1 execution authorization is denied because the audited Background-3C4 components are not yet connected as an integrated, resource-contained, single-use execution release. Runner v0.1 intentionally refuses execution even after a hypothetical valid grant. Background-3C6 may implement only synthetic or analytic end-to-end release tests and may not run CP01R1 or create a grant.",
        "status": "ACTIVE",
        "reason": "Component-level software QA is necessary but insufficient for execution authorization. The actual run path does not orchestrate frozen seeds and meshes, subprocess resource enforcement, signal handling, attestation, classification and atomic artifact commit as one tested transaction.",
        "sources": NEW_SOURCES,
        "evidence_effect": "GOVERNANCE_AND_EXECUTION_SAFETY_REVIEW_ONLY",
        "supersedes": None,
    }
    with DECISION_LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(decision, ensure_ascii=False, separators=(",", ":")) + "\n")


def synchronize_checkpoint():
    checkpoint = recursive_replace(load_json(LATEST_PATH))
    checkpoint["checkpoint_id"] = CHECKPOINT_ID
    checkpoint["timestamp"] = "2026-08-04T21:35:00+02:00"
    checkpoint["basis_commit"] = BASIS_COMMIT
    checkpoint["canonical_snapshot"] = str(SNAPSHOT_PATH.relative_to(ROOT))
    checkpoint["supersedes"] = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.23.json"
    checkpoint["current_goal"] = "Implement and audit the integrated Background-3C6 execution release using synthetic or analytic end-to-end controls only, without running CP01R1."
    checkpoint["current_workstream"] = "PRIMARY_C_PHYS_M1_BACKGROUND_3C6_INTEGRATED_EXECUTION_RELEASE_WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC"
    for item in checkpoint.get("current_workstreams", []):
        if item.get("track_id") == "MD2S-R1-C-PHYS":
            item["next_block"] = NEXT_BLOCK
    for source in NEW_SOURCES:
        if source not in checkpoint.setdefault("sources", []):
            checkpoint["sources"].append(source)
    gates = checkpoint.setdefault("gate_state", {})
    gates.update({
        "MD2S-R1-C-PHYS": TRACK_STATUS,
        "R1.0": TRACK_STATUS,
        "BACKGROUND_SOLVER_IMPLEMENTATION": "EXECUTION_PACKAGE_COMPONENTS_AUDITED_INTEGRATED_RELEASE_INCOMPLETE",
        "BACKGROUND_3C5_AUTHORIZATION_REVIEW": "DENIED_INTEGRATED_EXECUTION_RELEASE_INCOMPLETE",
        "BACKGROUND_3C6_EXECUTION_RELEASE": "NOT_STARTED",
        "BACKGROUND_3C_EXECUTION": "NOT_AUTHORIZED",
        "BACKGROUND_SOLVER_EXECUTION": "NOT_AUTHORIZED",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "OFFICIAL_MD2S_SOLVER": "NOT_AUTHORIZED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "PHYSICAL_EVIDENCE_EFFECT": "NONE",
    })
    results = [item for item in checkpoint.setdefault("verified_results", []) if item.get("result_id") != "UL-RES-C-PHYS-M1-BG3C5-001"]
    results.append({
        "result_id": "UL-RES-C-PHYS-M1-BG3C5-001",
        "statement": "The Background-3C5 review denies CP01R1 authorization because the audited components are not yet wired into an integrated, resource-contained, single-use execution release; no grant, solver call or result artifact is created.",
        "status": "DENIED_INTEGRATED_EXECUTION_RELEASE_INCOMPLETE",
        "evidence_effect": "GOVERNANCE_AND_EXECUTION_SAFETY_REVIEW_ONLY",
        "sources": NEW_SOURCES[:2],
    })
    checkpoint["verified_results"] = results
    blockers = [item for item in checkpoint.setdefault("open_blockers", []) if item.get("blocker_id") != "UL-BLK-C-PHYS-BACKGROUND-3C5-001"]
    blockers.append({
        "blocker_id": "UL-BLK-C-PHYS-BACKGROUND-3C6-001",
        "track_id": "MD2S-R1-C-PHYS",
        "statement": "The audited components are not connected as an integrated single-use execution release with subprocess resource enforcement, signal handling, frozen run orchestration, classification and atomic artifact commit.",
        "sources": NEW_SOURCES[:2],
    })
    checkpoint["open_blockers"] = blockers
    checkpoint["active_assumptions"] = [
        "CP01R1 remains the sole frozen run input and remains unexecuted.",
        "The Background-3C4 component package has software-QA status only.",
        "Background-3C5 denied authorization and no grant exists.",
        "Background-3C6 may use only synthetic or analytic end-to-end controls."
    ]
    checkpoint["forbidden_inferences"] = [
        "Do not interpret authorization denial as evidence against the M1 model.",
        "Do not run CP01R1, create a grant or create a repository result in Background-3C6.",
        "Do not call primary or independent root adapters with the physical target.",
        "Do not infer continuum existence, uniqueness, stability, ghost freedom or physical evidence."
    ]
    checkpoint["entry_points"] = NEW_SOURCES
    checkpoint["next_exact_action"] = "Execute C-PHYS-R1.0-BACKGROUND-3C6_INTEGRATED_EXECUTION_RELEASE_IMPLEMENTATION_ONLY: wire and audit the complete transaction using synthetic or analytic controls only; perform zero CP01R1 solver calls and create no grant."
    dump_json(SNAPSHOT_PATH, checkpoint)
    dump_json(LATEST_PATH, checkpoint)


def main():
    synchronize_manifest()
    append_decision()
    synchronize_checkpoint()
    print(json.dumps({"status":"PASS","release":RELEASE,"decision":DECISION_ID,"checkpoint":CHECKPOINT_ID,"execution_authorized":False,"next_block":NEXT_BLOCK}, indent=2))


if __name__ == "__main__":
    main()
