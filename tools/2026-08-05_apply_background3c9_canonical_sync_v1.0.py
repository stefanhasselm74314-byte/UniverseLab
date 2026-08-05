#!/usr/bin/env python3
"""One-shot canonical synchronization after Background-3C9 authorization denial."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-manifest.json"
LATEST = ROOT / "registry/session-checkpoint-latest.json"
SNAPSHOT = ROOT / "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.28.json"
DECISIONS = ROOT / "registry/decision-log.jsonl"

RELEASE = "2.20-c-phys-m1-background-3c9-authorization-denied-v0.1"
DECISION_ID = "UL-DEC-0035"
CHECKPOINT_ID = "UL-CHK-20260805-028"
TIMESTAMP = "2026-08-05T07:39:00+02:00"
BASIS_COMMIT = "19b134797a3a4cdf9852ec77084009c317c1642e"
DENIAL = "DENIED_REAL_BACKEND_ADAPTER_TRANSACTION_AND_OPERATIVE_SINGLE_USE_GRANT_RELEASE_ABSENT"
OLD_NEXT = "C-PHYS-R1.0-BACKGROUND-3C9_PHYSICAL_ADAPTER_AUTHORIZATION_REVIEW_ONLY"
NEXT = "C-PHYS-R1.0-BACKGROUND-3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE_IMPLEMENTATION_ONLY"
OLD_ACTIVE = "ACTIVE_PHYSICAL_ADAPTER_AUTHORIZATION_REVIEW_REMAINING"
ACTIVE = "ACTIVE_REAL_BACKEND_ADAPTER_CONTROL_RELEASE_IMPLEMENTATION_REMAINING"
REVIEW = "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C9PhysicalAdapterAuthorizationReview_v0.1.json"
LEDGER = "science/hzt-m0/md2s/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C9AuthorizationReviewLedger_v0.1.md"
VALIDATOR = "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c9_v0.1.py"
TEST = "tests/2026-08-05_test_hzt_m0_s6_c_phys_m1_background_3c9_v0.1.py"
PACKAGE_DIGEST = "497d6da51d0d7f436ae7cf24d8c4acad93d5e2423ab9eb717ec016c776e27613"
SCHEDULE_DIGEST = "95001986dc93818f0fea3124cf9ddcd63eb136f8d206f6200a4e8c0cf6d54927"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"top-level object required: {path}")
    return value


def write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def replace(value: Any, mapping: dict[str, str]) -> Any:
    if isinstance(value, dict):
        return {key: replace(item, mapping) for key, item in value.items()}
    if isinstance(value, list):
        return [replace(item, mapping) for item in value]
    if isinstance(value, str):
        return mapping.get(value, value)
    return value


def append_unique(values: list[Any], items: list[Any]) -> None:
    for item in items:
        if item not in values:
            values.append(item)


def update_manifest() -> dict[str, Any]:
    manifest = replace(load(MANIFEST), {
        OLD_NEXT: NEXT,
        OLD_ACTIVE: ACTIVE,
        "BACKGROUND_3C8_ADAPTER_AUDITED_AUTHORIZATION_REVIEW_REMAINING":
            "BACKGROUND_3C9_AUTHORIZATION_DENIED_REAL_BACKEND_CONTROL_RELEASE_REMAINING",
        "PHYSICAL_ADAPTER_AUDITED_MANUFACTURED_CONTROLS_ONLY_AUTHORIZATION_REVIEW_REMAINING":
            "PHYSICAL_ADAPTER_AUDITED_MANUFACTURED_CONTROLS_ONLY_REAL_BACKEND_CONTROL_RELEASE_REMAINING",
    })
    manifest["release"] = RELEASE
    manifest["release_date"] = "2026-08-05"
    for track in manifest.get("architecture", {}).get("research_tracks", []):
        if track.get("id") == "MD2S-R1-C-PHYS":
            track["status"] = ACTIVE
    gates = manifest.setdefault("gates", {})
    gates.update({
        "R1.0": ACTIVE,
        "BACKGROUND_SOLVER_IMPLEMENTATION":
            "PHYSICAL_ADAPTER_AUDITED_MANUFACTURED_CONTROLS_ONLY_REAL_BACKEND_CONTROL_RELEASE_REMAINING",
        "BACKGROUND_3C8_PHYSICAL_EXECUTION_ADAPTER": "PASS_AUDITED_MANUFACTURED_CONTROLS_ONLY",
        "BACKGROUND_3C9_AUTHORIZATION_REVIEW": DENIAL,
        "BACKGROUND_3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE": "NOT_STARTED",
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
    manifest.setdefault("parent_action_v0_1", {})["next_block"] = NEXT
    operator = manifest.setdefault("c_phys_operator_entry", {})
    operator["status"] = "BACKGROUND_3C9_AUTHORIZATION_DENIED_REAL_BACKEND_CONTROL_RELEASE_REMAINING"
    operator["solver_authorized"] = False
    operator["next_block"] = NEXT
    manifest.setdefault("c_phys_m1", {})["next_block"] = NEXT
    manifest["c_phys_m1"]["background_existence"] = "NOT_ESTABLISHED"
    manifest["c_phys_m1"]["physical_evidence_effect"] = "NONE"
    central = manifest.setdefault("central_registries", {})
    central["session_checkpoint_snapshot"] = str(SNAPSHOT.relative_to(ROOT))
    central["c_phys_m1_background_3c9_review"] = REVIEW
    central["c_phys_m1_background_3c9_ledger"] = LEDGER
    text = json.dumps(manifest, ensure_ascii=False)
    for stale in (OLD_NEXT, OLD_ACTIVE, '"BACKGROUND_3C9_AUTHORIZATION_REVIEW": "NOT_STARTED"'):
        if stale in text:
            raise RuntimeError(f"stale manifest value remains: {stale}")
    return manifest


def update_checkpoint() -> dict[str, Any]:
    checkpoint = replace(load(LATEST), {
        OLD_NEXT: NEXT,
        OLD_ACTIVE: ACTIVE,
        "PHYSICAL_ADAPTER_AUDITED_MANUFACTURED_CONTROLS_ONLY_AUTHORIZATION_REVIEW_REMAINING":
            "PHYSICAL_ADAPTER_AUDITED_MANUFACTURED_CONTROLS_ONLY_REAL_BACKEND_CONTROL_RELEASE_REMAINING",
    })
    checkpoint.update({
        "checkpoint_id": CHECKPOINT_ID,
        "timestamp": TIMESTAMP,
        "basis_commit": BASIS_COMMIT,
        "canonical_snapshot": str(SNAPSHOT.relative_to(ROOT)),
        "supersedes": "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.27.json",
        "current_goal": (
            "Implement and audit Background-3C10 real-backend adapter controls using isolated analytic a_F=0 "
            "transactions only, without CP01R1, target root solves, operative grants or physical results."
        ),
        "current_workstream": (
            "PRIMARY_C_PHYS_M1_BACKGROUND_3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE_"
            "WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC"
        ),
        "governance_principle": (
            "Manufactured adapter controls do not validate the real module boundary. Real-backend analytic "
            "controls must pass before any further authorization review."
        ),
    })
    append_unique(checkpoint.setdefault("sources", []), [REVIEW, LEDGER, VALIDATOR, TEST])
    checkpoint["current_workstreams"][0]["next_block"] = NEXT
    gates = checkpoint.setdefault("gate_state", {})
    gates.update({
        "MD2S-R1-C-PHYS": ACTIVE,
        "R1.0": ACTIVE,
        "BACKGROUND_SOLVER_IMPLEMENTATION":
            "PHYSICAL_ADAPTER_AUDITED_MANUFACTURED_CONTROLS_ONLY_REAL_BACKEND_CONTROL_RELEASE_REMAINING",
        "BACKGROUND_3C8_PHYSICAL_EXECUTION_ADAPTER": "PASS_AUDITED_MANUFACTURED_CONTROLS_ONLY",
        "BACKGROUND_3C9_AUTHORIZATION_REVIEW": DENIAL,
        "BACKGROUND_3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE": "NOT_STARTED",
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
    results[:] = [item for item in results if item.get("result_id") != "UL-RES-C-PHYS-M1-BG3C9-001"]
    results.append({
        "result_id": "UL-RES-C-PHYS-M1-BG3C9-001",
        "statement": (
            "The Background-3C9 review denies CP01R1 authorization because Background-3C8 validated "
            "manufactured adapter transactions only; real-backend analytic transactions and an operative "
            "single-use grant release remain absent."
        ),
        "status": DENIAL,
        "evidence_effect": "GOVERNANCE_AND_EXECUTION_SAFETY_REVIEW_ONLY",
        "physical_evidence_effect": "NONE",
        "package_manifest_sha256": PACKAGE_DIGEST,
        "schedule_sha256": SCHEDULE_DIGEST,
        "sources": [REVIEW, LEDGER],
    })
    blockers = checkpoint.setdefault("open_blockers", [])
    blockers[:] = [item for item in blockers if item.get("blocker_id") not in {
        "UL-BLK-C-PHYS-BACKGROUND-3C9-001",
        "UL-BLK-C-PHYS-BACKGROUND-3C10-001",
    }]
    blockers.append({
        "blocker_id": "UL-BLK-C-PHYS-BACKGROUND-3C10-001",
        "track_id": "MD2S-R1-C-PHYS",
        "statement": (
            "Real primary and independent analytic adapter transactions, real-boundary resource and interruption "
            "controls, and real-backend result-schema translation remain unimplemented and unaudited."
        ),
        "sources": [REVIEW],
    })
    checkpoint["active_assumptions"] = [
        "CP01R1 remains frozen and unexecuted.",
        "Background-3C8 executed manufactured stubs only.",
        "No real backend has crossed the adapter process boundary.",
        "No operative grant or physical result directory exists.",
    ]
    checkpoint["forbidden_inferences"] = [
        "Do not interpret the Background-3C9 denial as evidence against M1 or Hyperzeit.",
        "Do not execute CP01R1 or the target a_F=1/4 solve in Background-3C10.",
        "Do not perform primary Newton target solves or independent shooting-root solves in Background-3C10.",
        "Do not create an operative grant or physical result artifact.",
        "Do not infer background existence, continuum theorems, stability, ghost freedom or evidence upgrades.",
    ]
    checkpoint["entry_points"] = [REVIEW, LEDGER, VALIDATOR, TEST]
    checkpoint["next_exact_action"] = (
        "Execute C-PHYS-R1.0-BACKGROUND-3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE_IMPLEMENTATION_ONLY: "
        "run isolated analytic a_F=0 controls through the real modules without target root solves, CP01R1, "
        "operative grants or physical result artifacts."
    )
    text = json.dumps(checkpoint, ensure_ascii=False)
    for stale in (OLD_NEXT, OLD_ACTIVE, "UL-BLK-C-PHYS-BACKGROUND-3C9-001"):
        if stale in text:
            raise RuntimeError(f"stale checkpoint value remains: {stale}")
    return checkpoint


def append_decision() -> None:
    existing = [json.loads(line) for line in DECISIONS.read_text(encoding="utf-8").splitlines() if line.strip()]
    if any(item.get("decision_id") == DECISION_ID for item in existing):
        raise RuntimeError(f"decision {DECISION_ID} already exists")
    item = {
        "decision_id": DECISION_ID,
        "date": "2026-08-05",
        "topic": "background_3c9_real_backend_execution_authorization_review",
        "decision": (
            "CP01R1 authorization is denied because Background-3C8 validated source binding and manufactured "
            "adapter transactions only. Real primary and independent analytic adapter transactions, real-boundary "
            "resource and interruption controls, real result-schema translation and an operative single-use "
            "grant release remain absent."
        ),
        "status": "ACTIVE",
        "reason": (
            "AST source binding and stub agreement do not establish import-time or runtime compatibility across "
            "the real backend process boundary. Authorization defaults to denial while any prerequisite is absent."
        ),
        "sources": [REVIEW, LEDGER, VALIDATOR, TEST],
        "evidence_effect": "GOVERNANCE_AND_EXECUTION_SAFETY_REVIEW_ONLY",
        "physical_evidence_effect": "NONE",
        "supersedes": None,
    }
    with DECISIONS.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> None:
    if SNAPSHOT.exists():
        raise RuntimeError("checkpoint v1.28 already exists")
    manifest = update_manifest()
    checkpoint = update_checkpoint()
    append_decision()
    write(MANIFEST, manifest)
    write(SNAPSHOT, checkpoint)
    write(LATEST, checkpoint)
    if SNAPSHOT.read_bytes() != LATEST.read_bytes():
        raise RuntimeError("checkpoint alias mismatch")
    print("PASS: Background-3C9 canonical synchronization prepared")


if __name__ == "__main__":
    main()
