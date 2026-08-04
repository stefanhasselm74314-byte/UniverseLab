#!/usr/bin/env python3
"""One-shot append-only canonical synchronization after Background-3C4."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "project-manifest.json"
DECISION_LOG_PATH = ROOT / "registry/decision-log.jsonl"
LATEST_PATH = ROOT / "registry/session-checkpoint-latest.json"
SNAPSHOT_PATH = ROOT / "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.23.json"

RELEASE = "2.15-c-phys-m1-background-3c4-execution-package-audited-v0.1"
DECISION_ID = "UL-DEC-0030"
CHECKPOINT_ID = "UL-CHK-20260804-023"
BASIS_COMMIT = "42ff4673e81f140c75603ca4f951061c14126197"
NEXT_BLOCK = "C-PHYS-R1.0-BACKGROUND-3C5_EXECUTION_PACKAGE_AUTHORIZATION_REVIEW_ONLY"
TRACK_STATUS = "ACTIVE_EXECUTION_PACKAGE_AUTHORIZATION_REVIEW_REMAINING"
PACKAGE_DIGEST = "f274333e6d0a94e9c4bedfe179e9781d7175e484dc70de5396aedee7872033cd"

NEW_SOURCES = [
    "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C4ExecutionRunnerContract_v0.1.json",
    "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C4ExecutionPackageAuditResult_v0.1.json",
    "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C4ExecutionRunnerLedger_v0.1.md",
    "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_execution_runner_v0.1.py",
    "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3c4_v0.1.py",
    "tests/2026-08-04_test_hzt_m0_s6_c_phys_m1_background_3c4_v0.1.py",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def recursive_replace(value):
    if isinstance(value, dict):
        return {key: recursive_replace(item) for key, item in value.items()}
    if isinstance(value, list):
        return [recursive_replace(item) for item in value]
    if isinstance(value, str):
        replacements = {
            "ACTIVE_EXECUTION_RUNNER_IMPLEMENTATION_REMAINING": TRACK_STATUS,
            "C-PHYS-R1.0-BACKGROUND-3C4_EXECUTION_RUNNER_IMPLEMENTATION_ONLY": NEXT_BLOCK,
            "Implement and audit the missing CP01R1 execution runner, immutable result writer, resource enforcement, environment attestation, classification engine and interruption protocol without executing either numerical backend.": "Perform the append-only Background-3C5 authorization review of the audited CP01R1 execution package without running either numerical backend.",
            "PRIMARY_C_PHYS_M1_BACKGROUND_3C4_EXECUTION_RUNNER_IMPLEMENTATION_WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC": "PRIMARY_C_PHYS_M1_BACKGROUND_3C5_AUTHORIZATION_REVIEW_WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC",
        }
        return replacements.get(value, value)
    return value


def synchronize_manifest():
    manifest = recursive_replace(load_json(MANIFEST_PATH))
    manifest["release"] = RELEASE
    manifest["release_date"] = "2026-08-04"
    for track in manifest.get("architecture", {}).get("research_tracks", []):
        if track.get("id") == "MD2S-R1-C-PHYS":
            track["status"] = TRACK_STATUS
    gates = manifest.setdefault("gates", {})
    gates.update({
        "R1.0": TRACK_STATUS,
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
    })
    if "next_block" in manifest:
        manifest["next_block"] = NEXT_BLOCK
    if "next_exact_action" in manifest:
        manifest["next_exact_action"] = NEXT_BLOCK
    dump_json(MANIFEST_PATH, manifest)


def append_decision():
    records = [json.loads(line) for line in DECISION_LOG_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    if any(record.get("decision_id") == DECISION_ID for record in records):
        raise RuntimeError(f"{DECISION_ID} already exists")
    decision = {
        "decision_id": DECISION_ID,
        "date": "2026-08-04",
        "topic": "c_phys_m1_background_3c4_execution_package_audit",
        "decision": "The source-hash-bound CP01R1 execution package is accepted as PASS_AUDITED_NO_EXECUTION. Environment attestation, resource controls, atomic writing, interruption handling, closed classification and guarded primary/independent root adapters are implemented and audited with zero solver calls. Execution remains unauthorized and requires a separate append-only Background-3C5 review.",
        "status": "ACTIVE",
        "reason": "The package digest f274333e... is reproducibly verified, the run path fails closed with exit code 73 before backend import or output creation, and all root-call counters remain zero. Software execution readiness is distinct from authorization, numerical background existence and physical evidence.",
        "sources": NEW_SOURCES[:3],
        "evidence_effect": "SOFTWARE_EXECUTION_PACKAGE_QA_ONLY",
        "supersedes": None,
    }
    with DECISION_LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(decision, ensure_ascii=False, separators=(",", ":")) + "\n")


def synchronize_checkpoint():
    checkpoint = recursive_replace(load_json(LATEST_PATH))
    checkpoint["checkpoint_id"] = CHECKPOINT_ID
    checkpoint["timestamp"] = "2026-08-04T21:15:00+02:00"
    checkpoint["basis_commit"] = BASIS_COMMIT
    checkpoint["canonical_snapshot"] = str(SNAPSHOT_PATH.relative_to(ROOT))
    checkpoint["supersedes"] = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.22.json"
    checkpoint["current_goal"] = "Perform the append-only Background-3C5 authorization review of the audited CP01R1 execution package without running either numerical backend."
    checkpoint["current_workstream"] = "PRIMARY_C_PHYS_M1_BACKGROUND_3C5_AUTHORIZATION_REVIEW_WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC"
    for workstream in checkpoint.get("current_workstreams", []):
        if workstream.get("track_id") == "MD2S-R1-C-PHYS":
            workstream["next_block"] = NEXT_BLOCK
    sources = checkpoint.setdefault("sources", [])
    for source in NEW_SOURCES:
        if source not in sources:
            sources.append(source)
    gates = checkpoint.setdefault("gate_state", {})
    gates.update({
        "MD2S-R1-C-PHYS": TRACK_STATUS,
        "R1.0": TRACK_STATUS,
        "BACKGROUND_SOLVER_IMPLEMENTATION": "EXECUTION_PACKAGE_AUDITED_NO_EXECUTION",
        "BACKGROUND_3C4_EXECUTION_PACKAGE": "PASS_AUDITED_NO_EXECUTION",
        "BACKGROUND_3C5_AUTHORIZATION_REVIEW": "NOT_STARTED",
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
    results = checkpoint.setdefault("verified_results", [])
    results = [item for item in results if item.get("result_id") != "UL-RES-C-PHYS-M1-BG3C4-001"]
    results.append({
        "result_id": "UL-RES-C-PHYS-M1-BG3C4-001",
        "statement": "The source-hash-bound CP01R1 execution package, environment attestation, resource hooks, atomic writer, interruption protocol, classification engine and guarded root adapters pass audit and temporary-directory self-tests with zero solver calls and no repository result artifact.",
        "status": "PASS_EXECUTION_PACKAGE_AUDIT_NO_SOLVER_CALLS",
        "evidence_effect": "SOFTWARE_EXECUTION_PACKAGE_QA_ONLY",
        "sources": [
            NEW_SOURCES[0],
            NEW_SOURCES[1],
            NEW_SOURCES[2],
        ],
    })
    checkpoint["verified_results"] = results
    blockers = checkpoint.setdefault("open_blockers", [])
    blockers = [item for item in blockers if item.get("blocker_id") != "UL-BLK-C-PHYS-BACKGROUND-3C4-001"]
    blockers.append({
        "blocker_id": "UL-BLK-C-PHYS-BACKGROUND-3C5-001",
        "track_id": "MD2S-R1-C-PHYS",
        "statement": "No append-only CP01R1 execution grant exists, runner v0.1 is explicitly not an execution release, and the Background-3C5 authorization review has not been completed.",
        "sources": [
            NEW_SOURCES[0],
            NEW_SOURCES[1],
            "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C3ExecutionAuthorizationReview_v0.1.json",
        ],
    })
    checkpoint["open_blockers"] = blockers
    checkpoint["active_assumptions"] = [
        "CP01R1 remains the sole frozen run input.",
        "Both numerical backends and the execution package have software-QA status only.",
        "No append-only execution grant exists and runner v0.1 is not an execution release.",
        "No result directory or physical background exists."
    ]
    checkpoint["forbidden_inferences"] = [
        "Do not interpret the execution-package audit as a numerical background result.",
        "Do not create an authorization grant or call either root adapter before Background-3C5 is ratified.",
        "Do not create a repository result directory in Background-3C5.",
        "Do not infer continuum existence, uniqueness, Fredholmness, stability, ghost freedom or physical evidence."
    ]
    checkpoint["entry_points"] = [
        NEW_SOURCES[0],
        NEW_SOURCES[1],
        NEW_SOURCES[2],
        NEW_SOURCES[3],
        NEW_SOURCES[4],
        NEW_SOURCES[5],
    ]
    checkpoint["next_exact_action"] = "Execute C-PHYS-R1.0-BACKGROUND-3C5_EXECUTION_PACKAGE_AUTHORIZATION_REVIEW_ONLY: review the exact audited package digest and all execution prerequisites; perform zero solver calls and create no grant automatically."
    dump_json(SNAPSHOT_PATH, checkpoint)
    dump_json(LATEST_PATH, checkpoint)


def main():
    synchronize_manifest()
    append_decision()
    synchronize_checkpoint()
    print(json.dumps({
        "status": "PASS",
        "release": RELEASE,
        "decision": DECISION_ID,
        "checkpoint": CHECKPOINT_ID,
        "package_manifest_sha256": PACKAGE_DIGEST,
        "execution_authorized": False,
        "next_block": NEXT_BLOCK,
    }, indent=2))


if __name__ == "__main__":
    main()
