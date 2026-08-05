#!/usr/bin/env python3
"""One-shot canonical synchronization after the merged Background-3C6 audit."""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-manifest.json"
DECISIONS = ROOT / "registry/decision-log.jsonl"
LATEST = ROOT / "registry/session-checkpoint-latest.json"
SNAPSHOT = ROOT / "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.25.json"

RELEASE = "2.17-c-phys-m1-background-3c6-integrated-control-release-audited-v0.1"
DECISION_ID = "UL-DEC-0032"
CHECKPOINT_ID = "UL-CHK-20260805-025"
BASIS_COMMIT = "5311dee824b334c8b93e4adf43fb3526c6af5648"
NEXT_BLOCK = "C-PHYS-R1.0-BACKGROUND-3C7_INTEGRATED_RELEASE_AUTHORIZATION_REVIEW_ONLY"
DIGEST = "297272556025d86eadad2c8f18caaa4f48fd643c295c8c7dc384be5606b9d147"

SOURCES = [
    "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C6IntegratedExecutionReleaseContract_v0.1.json",
    "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C6IntegratedExecutionReleaseAuditResult_v0.1.json",
    "science/hzt-m0/md2s/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C6IntegratedExecutionReleaseLedger_v0.1.md",
    "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c6_synthetic_worker_v0.1.py",
    "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c6_integrated_release_v0.1.py",
    "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c6_integrated_release_v0.2.py",
    "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c6_v0.1.py",
    "tests/2026-08-05_test_hzt_m0_s6_c_phys_m1_background_3c6_v0.1.py",
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_manifest() -> None:
    manifest = read_json(MANIFEST)
    manifest["release"] = RELEASE
    manifest["release_date"] = "2026-08-05"
    for track in manifest.get("architecture", {}).get("research_tracks", []):
        if track.get("id") == "MD2S-R1-C-PHYS":
            track["status"] = "ACTIVE_INTEGRATED_RELEASE_AUTHORIZATION_REVIEW_REMAINING"
    gates = manifest.setdefault("gates", {})
    gates.update({
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
    })
    manifest["next_block"] = NEXT_BLOCK
    write_json(MANIFEST, manifest)


def append_decision() -> None:
    existing = DECISIONS.read_text(encoding="utf-8")
    if f'"decision_id":"{DECISION_ID}"' in existing or f'"decision_id": "{DECISION_ID}"' in existing:
        raise RuntimeError(f"decision {DECISION_ID} already exists")
    decision = {
        "decision_id": DECISION_ID,
        "date": "2026-08-05",
        "topic": "background_3c6_integrated_control_release_audit",
        "decision": "The source-bound Background-3C6 integrated transaction is accepted as PASS_AUDITED_CONTROL_ONLY after exact analytic success, intentional rejection, timeout and signal controls completed end to end. This acceptance is software orchestration QA only and does not authorize CP01R1 or any physical backend execution.",
        "status": "ACTIVE",
        "reason": "The closed package digest, AST dependency firewall, resource-limited subprocess boundary, timeout and signal cleanup, classification engine, atomic artifacts, no-overwrite policy and physical exit-73 path all passed while every physical solver counter and CP01R1 attempt remained zero.",
        "sources": SOURCES[:3],
        "evidence_effect": "SOFTWARE_END_TO_END_CONTROL_TRANSACTION_QA_ONLY",
        "physical_evidence_effect": "NONE",
        "supersedes": None,
    }
    with DECISIONS.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(decision, separators=(",", ":"), ensure_ascii=False) + "\n")


def update_checkpoint() -> None:
    previous = read_json(LATEST)
    checkpoint = copy.deepcopy(previous)
    checkpoint.update({
        "checkpoint_id": CHECKPOINT_ID,
        "timestamp": "2026-08-05T06:20:00+02:00",
        "basis_commit": BASIS_COMMIT,
        "canonical_snapshot": str(SNAPSHOT.relative_to(ROOT)),
        "supersedes": previous.get("canonical_snapshot"),
        "current_goal": "Perform the append-only Background-3C7 authorization review of the audited integrated control release without creating a grant or executing CP01R1.",
        "current_workstream": "PRIMARY_C_PHYS_M1_BACKGROUND_3C7_AUTHORIZATION_REVIEW_WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC",
        "governance_principle": "An end-to-end synthetic control release validates orchestration only. It is not a physical grant, result or evidence upgrade, and a later review may not execute CP01R1 automatically.",
        "next_exact_action": "Execute C-PHYS-R1.0-BACKGROUND-3C7_INTEGRATED_RELEASE_AUTHORIZATION_REVIEW_ONLY: revalidate the frozen package and decide eligibility without creating a grant, importing a physical backend or running CP01R1.",
    })
    source_list = checkpoint.setdefault("sources", [])
    for source in SOURCES:
        if source not in source_list:
            source_list.append(source)
    workstreams = checkpoint.setdefault("current_workstreams", [])
    found_primary = False
    for item in workstreams:
        if item.get("track_id") == "MD2S-R1-C-PHYS":
            item.update({
                "model_id": "HZT-M0-S6-C-PHYS-M1",
                "priority": "PRIMARY",
                "next_block": NEXT_BLOCK,
            })
            found_primary = True
    if not found_primary:
        workstreams.insert(0, {
            "track_id": "MD2S-R1-C-PHYS",
            "model_id": "HZT-M0-S6-C-PHYS-M1",
            "priority": "PRIMARY",
            "next_block": NEXT_BLOCK,
        })
    gates = checkpoint.setdefault("gate_state", {})
    gates.update({
        "MD2S-R1-C-PHYS": "ACTIVE_INTEGRATED_RELEASE_AUTHORIZATION_REVIEW_REMAINING",
        "R1.0": "ACTIVE_INTEGRATED_RELEASE_AUTHORIZATION_REVIEW_REMAINING",
        "BACKGROUND_SOLVER_IMPLEMENTATION": "INTEGRATED_CONTROL_RELEASE_AUDITED_PHYSICAL_EXECUTION_NOT_AUTHORIZED",
        "BACKGROUND_3C6_EXECUTION_RELEASE": "PASS_AUDITED_CONTROL_ONLY",
        "BACKGROUND_3C7_AUTHORIZATION_REVIEW": "NOT_STARTED",
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
    result_id = "UL-RES-C-PHYS-M1-BG3C6-001"
    if not any(item.get("result_id") == result_id for item in results):
        results.append({
            "result_id": result_id,
            "statement": "The source-bound Background-3C6 transaction passed exact analytic success, intentional rejection, timeout and signal end-to-end controls with atomic temporary artifacts or clean aborts while all physical solver and CP01R1 counters remained zero.",
            "status": "PASS_AUDITED_CONTROL_ONLY",
            "evidence_effect": "SOFTWARE_END_TO_END_CONTROL_TRANSACTION_QA_ONLY",
            "physical_evidence_effect": "NONE",
            "package_manifest_sha256": DIGEST,
            "sources": SOURCES[:3],
        })
    blockers = checkpoint.setdefault("open_blockers", [])
    blockers[:] = [
        item for item in blockers
        if "BACKGROUND-3C6" not in str(item.get("blocker_id", ""))
    ]
    blocker_id = "UL-BLK-C-PHYS-BACKGROUND-3C7-001"
    if not any(item.get("blocker_id") == blocker_id for item in blockers):
        blockers.append({
            "blocker_id": blocker_id,
            "track_id": "MD2S-R1-C-PHYS",
            "statement": "The integrated control release has not passed an append-only authorization review for physical single-use execution eligibility; no CP01R1 grant exists.",
            "sources": [
                "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C6IntegratedExecutionReleaseAuditResult_v0.1.json"
            ],
        })
    checkpoint["active_assumptions"] = [
        "CP01R1 remains the sole frozen physical run input and has not been executed.",
        "Background-3C6 controls are synthetic or exact analytic and contain no physical backend import.",
        "The integrated control release is not a grant and may not be reused as one.",
        "No physical result directory or append-only execution grant exists.",
    ]
    checkpoint["forbidden_inferences"] = [
        "Do not interpret the Background-3C6 control PASS as a physical background or model confirmation.",
        "Do not create a grant or call either physical backend during Background-3C7 review.",
        "Do not infer continuum existence uniqueness stability ghost freedom or a released forward map.",
        "Do not change K1-D K1-E or physical evidence status from software control QA.",
    ]
    checkpoint["entry_points"] = [
        "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C6IntegratedExecutionReleaseContract_v0.1.json",
        "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C6IntegratedExecutionReleaseAuditResult_v0.1.json",
        "science/hzt-m0/md2s/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C6IntegratedExecutionReleaseLedger_v0.1.md",
        "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c6_integrated_release_v0.2.py",
        "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c6_v0.1.py",
        "tests/2026-08-05_test_hzt_m0_s6_c_phys_m1_background_3c6_v0.1.py",
    ]
    write_json(SNAPSHOT, checkpoint)
    write_json(LATEST, checkpoint)


def main() -> None:
    update_manifest()
    append_decision()
    update_checkpoint()
    print("PASS: Background-3C6 canonical synchronization applied")


if __name__ == "__main__":
    main()
