#!/usr/bin/env python3
"""One-shot canonical synchronization after the merged Background-3C7 review."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-manifest.json"
DECISIONS = ROOT / "registry/decision-log.jsonl"
LATEST = ROOT / "registry/session-checkpoint-latest.json"
SNAPSHOT = ROOT / "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.26.json"

RELEASE = "2.18-c-phys-m1-background-3c7-authorization-denied-v0.1"
DECISION_ID = "UL-DEC-0033"
CHECKPOINT_ID = "UL-CHK-20260805-026"
BASIS_COMMIT = "24d9e3d7a5fdadaeef185cf596bce3f394add60a"
NEXT_BLOCK = "C-PHYS-R1.0-BACKGROUND-3C8_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_ONLY"
DENIAL = "DENIED_PHYSICAL_BACKEND_ADAPTER_AND_SINGLE_USE_GRANT_RELEASE_ABSENT"
OLD_NEXT = "C-PHYS-R1.0-BACKGROUND-3C7_INTEGRATED_RELEASE_AUTHORIZATION_REVIEW_ONLY"
OLD_STATUS = "BACKGROUND_3C6_CONTROL_RELEASE_AUDITED_AUTHORIZATION_REVIEW_REMAINING"
NEW_STATUS = "BACKGROUND_3C7_AUTHORIZATION_DENIED_PHYSICAL_ADAPTER_IMPLEMENTATION_REMAINING"

SOURCES = [
    "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C7IntegratedReleaseAuthorizationReview_v0.1.json",
    "science/hzt-m0/md2s/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C7AuthorizationReviewLedger_v0.1.md",
    "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c7_v0.1.py",
    "tests/2026-08-05_test_hzt_m0_s6_c_phys_m1_background_3c7_v0.1.py",
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def replace_exact(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: replace_exact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_exact(item) for item in value]
    if value == OLD_NEXT:
        return NEXT_BLOCK
    if value == OLD_STATUS:
        return NEW_STATUS
    return value


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


def update_manifest() -> None:
    manifest = replace_exact(read_json(MANIFEST))
    manifest["release"] = RELEASE
    manifest["release_date"] = "2026-08-05"
    for track in manifest.get("architecture", {}).get("research_tracks", []):
        if track.get("id") == "MD2S-R1-C-PHYS":
            track["status"] = "ACTIVE_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_REMAINING"
    gates = manifest.setdefault("gates", {})
    gates.update({
        "R1.0": "ACTIVE_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_REMAINING",
        "BACKGROUND_SOLVER_IMPLEMENTATION": "INTEGRATED_CONTROL_RELEASE_AUDITED_PHYSICAL_ADAPTER_MISSING",
        "BACKGROUND_3C6_EXECUTION_RELEASE": "PASS_AUDITED_CONTROL_ONLY",
        "BACKGROUND_3C7_AUTHORIZATION_REVIEW": DENIAL,
        "BACKGROUND_3C8_PHYSICAL_EXECUTION_ADAPTER": "NOT_STARTED",
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
    manifest.setdefault("parent_action_v0_1", {})["next_block"] = NEXT_BLOCK
    operator = manifest.setdefault("c_phys_operator_entry", {})
    operator["status"] = NEW_STATUS
    operator["solver_authorized"] = False
    operator["next_block"] = NEXT_BLOCK
    stale = {
        OLD_NEXT: find_exact(manifest, OLD_NEXT),
        OLD_STATUS: find_exact(manifest, OLD_STATUS),
    }
    stale = {key: paths for key, paths in stale.items() if paths}
    if stale:
        raise RuntimeError(f"stale Background-3C7 manifest values remain: {stale}")
    write_json(MANIFEST, manifest)


def append_decision() -> None:
    existing = DECISIONS.read_text(encoding="utf-8")
    if f'"decision_id":"{DECISION_ID}"' in existing or f'"decision_id": "{DECISION_ID}"' in existing:
        raise RuntimeError(f"decision {DECISION_ID} already exists")
    decision = {
        "decision_id": DECISION_ID,
        "date": "2026-08-05",
        "topic": "background_3c7_physical_execution_authorization_review",
        "decision": "CP01R1 execution authorization is denied because the audited Background-3C6 release is control-only, explicitly forbids physical backend imports and lacks a source-bound physical adapter, real-backend transaction binding and single-use replay-protected grant release.",
        "status": "ACTIVE",
        "reason": "Synthetic end-to-end orchestration QA cannot authorize a nonexistent physical execution path. A separately versioned Background-3C8 adapter must bind the frozen run payload, seeds, meshes, both backends, resource controls, classification and grant-consumption semantics before another review.",
        "sources": SOURCES[:2],
        "evidence_effect": "GOVERNANCE_AND_EXECUTION_SAFETY_REVIEW_ONLY",
        "physical_evidence_effect": "NONE",
        "supersedes": None,
    }
    with DECISIONS.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(decision, separators=(",", ":"), ensure_ascii=False) + "\n")


def update_checkpoint() -> None:
    previous = read_json(LATEST)
    checkpoint = replace_exact(copy.deepcopy(previous))
    checkpoint.update({
        "checkpoint_id": CHECKPOINT_ID,
        "timestamp": "2026-08-05T06:40:00+02:00",
        "basis_commit": BASIS_COMMIT,
        "canonical_snapshot": str(SNAPSHOT.relative_to(ROOT)),
        "supersedes": previous.get("canonical_snapshot"),
        "current_goal": "Implement and audit the Background-3C8 physical execution adapter using analytic controls and manufactured backend stubs only, without executing CP01R1 or creating an operative grant.",
        "current_workstream": "PRIMARY_C_PHYS_M1_BACKGROUND_3C8_PHYSICAL_ADAPTER_IMPLEMENTATION_WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC",
        "governance_principle": "A control transaction is not a physical execution release. Physical authorization requires a separately source-bound adapter and single-use replay-protected grant release.",
        "next_exact_action": "Execute C-PHYS-R1.0-BACKGROUND-3C8_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_ONLY: implement adapter contracts and manufactured controls only; perform zero CP01R1, Newton, shooting-root and physical result operations.",
    })
    source_list = checkpoint.setdefault("sources", [])
    for source in SOURCES:
        if source not in source_list:
            source_list.append(source)
    workstreams = checkpoint.setdefault("current_workstreams", [])
    found = False
    for item in workstreams:
        if item.get("track_id") == "MD2S-R1-C-PHYS":
            item.update({
                "model_id": "HZT-M0-S6-C-PHYS-M1",
                "priority": "PRIMARY",
                "next_block": NEXT_BLOCK,
            })
            found = True
    if not found:
        workstreams.insert(0, {
            "track_id": "MD2S-R1-C-PHYS",
            "model_id": "HZT-M0-S6-C-PHYS-M1",
            "priority": "PRIMARY",
            "next_block": NEXT_BLOCK,
        })
    gates = checkpoint.setdefault("gate_state", {})
    gates.update({
        "MD2S-R1-C-PHYS": "ACTIVE_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_REMAINING",
        "R1.0": "ACTIVE_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_REMAINING",
        "BACKGROUND_SOLVER_IMPLEMENTATION": "INTEGRATED_CONTROL_RELEASE_AUDITED_PHYSICAL_ADAPTER_MISSING",
        "BACKGROUND_3C6_EXECUTION_RELEASE": "PASS_AUDITED_CONTROL_ONLY",
        "BACKGROUND_3C7_AUTHORIZATION_REVIEW": DENIAL,
        "BACKGROUND_3C8_PHYSICAL_EXECUTION_ADAPTER": "NOT_STARTED",
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
    result_id = "UL-RES-C-PHYS-M1-BG3C7-001"
    if not any(item.get("result_id") == result_id for item in results):
        results.append({
            "result_id": result_id,
            "statement": "The Background-3C7 review denies CP01R1 authorization because the audited integrated release is control-only and no source-bound physical adapter or single-use replay-protected grant release exists.",
            "status": DENIAL,
            "evidence_effect": "GOVERNANCE_AND_EXECUTION_SAFETY_REVIEW_ONLY",
            "physical_evidence_effect": "NONE",
            "sources": SOURCES[:2],
        })
    blockers = checkpoint.setdefault("open_blockers", [])
    blockers[:] = [
        item for item in blockers
        if "BACKGROUND-3C7" not in str(item.get("blocker_id", ""))
    ]
    blocker_id = "UL-BLK-C-PHYS-BACKGROUND-3C8-001"
    if not any(item.get("blocker_id") == blocker_id for item in blockers):
        blockers.append({
            "blocker_id": blocker_id,
            "track_id": "MD2S-R1-C-PHYS",
            "statement": "A source-bound physical execution adapter, real-backend transaction wiring and single-use replay-protected grant release remain unimplemented and unaudited.",
            "sources": [
                "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C7IntegratedReleaseAuthorizationReview_v0.1.json"
            ],
        })
    checkpoint["active_assumptions"] = [
        "CP01R1 remains the sole frozen physical run input and has not been executed.",
        "Background-3C6 remains a synthetic and analytic control release only.",
        "No source-bound physical adapter or operative single-use grant exists.",
        "No physical result directory or physical backend invocation exists.",
    ]
    checkpoint["forbidden_inferences"] = [
        "Do not interpret the Background-3C7 denial as evidence against the M1 equations or Hyperzeit.",
        "Do not import or call the physical backends during Background-3C8 target-path development.",
        "Do not create an operative grant or execute CP01R1 in Background-3C8.",
        "Do not infer a background, continuum theorem, stability, ghost freedom or evidence upgrade.",
    ]
    checkpoint["entry_points"] = [
        "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C7IntegratedReleaseAuthorizationReview_v0.1.json",
        "science/hzt-m0/md2s/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C7AuthorizationReviewLedger_v0.1.md",
        "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c7_v0.1.py",
        "tests/2026-08-05_test_hzt_m0_s6_c_phys_m1_background_3c7_v0.1.py",
    ]
    stale = {
        OLD_NEXT: find_exact(checkpoint, OLD_NEXT),
        OLD_STATUS: find_exact(checkpoint, OLD_STATUS),
    }
    stale = {key: paths for key, paths in stale.items() if paths}
    if stale:
        raise RuntimeError(f"stale Background-3C7 checkpoint values remain: {stale}")
    write_json(SNAPSHOT, checkpoint)
    write_json(LATEST, checkpoint)


def main() -> None:
    update_manifest()
    append_decision()
    update_checkpoint()
    print("PASS: Background-3C7 canonical synchronization applied")


if __name__ == "__main__":
    main()
