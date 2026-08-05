#!/usr/bin/env python3
"""One-shot canonical synchronization after the audited Background-3C8 adapter controls."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "project-manifest.json"
LATEST_PATH = ROOT / "registry/session-checkpoint-latest.json"
SNAPSHOT_PATH = ROOT / "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.27.json"
DECISION_LOG_PATH = ROOT / "registry/decision-log.jsonl"

RELEASE = "2.19-c-phys-m1-background-3c8-physical-adapter-audited-v0.1"
DECISION_ID = "UL-DEC-0034"
CHECKPOINT_ID = "UL-CHK-20260805-027"
TIMESTAMP = "2026-08-05T07:27:00+02:00"
BASIS_COMMIT = "b4b2be8128fcaf9cf8980d3b1b4ed1aa71c60355"
NEXT_BLOCK = "C-PHYS-R1.0-BACKGROUND-3C9_PHYSICAL_ADAPTER_AUTHORIZATION_REVIEW_ONLY"
OLD_NEXT_BLOCK = "C-PHYS-R1.0-BACKGROUND-3C8_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_ONLY"
ACTIVE_STATUS = "ACTIVE_PHYSICAL_ADAPTER_AUTHORIZATION_REVIEW_REMAINING"
ADAPTER_STATUS = "PASS_AUDITED_MANUFACTURED_CONTROLS_ONLY"
PACKAGE_DIGEST = "497d6da51d0d7f436ae7cf24d8c4acad93d5e2423ab9eb717ec016c776e27613"
SCHEDULE_DIGEST = "95001986dc93818f0fea3124cf9ddcd63eb136f8d206f6200a4e8c0cf6d54927"

CONTRACT = "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C8PhysicalExecutionAdapterContract_v0.1.json"
AUDIT_RESULT = "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C8PhysicalExecutionAdapterAuditResult_v0.1.json"
LEDGER = "science/hzt-m0/md2s/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C8PhysicalExecutionAdapterLedger_v0.1.md"
ADAPTER = "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c8_physical_execution_adapter_v0.1.py"
WORKER = "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c8_manufactured_backend_worker_v0.1.py"
VALIDATOR = "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c8_v0.1.py"
TEST = "tests/2026-08-05_test_hzt_m0_s6_c_phys_m1_background_3c8_v0.1.py"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"top-level object required: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def recursive_replace(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, dict):
        return {key: recursive_replace(item, replacements) for key, item in value.items()}
    if isinstance(value, list):
        return [recursive_replace(item, replacements) for item in value]
    if isinstance(value, str):
        return replacements.get(value, value)
    return value


def append_unique(values: list[Any], items: list[Any]) -> None:
    for item in items:
        if item not in values:
            values.append(item)


def update_manifest() -> dict[str, Any]:
    manifest = load_json(MANIFEST_PATH)
    manifest = recursive_replace(
        manifest,
        {
            OLD_NEXT_BLOCK: NEXT_BLOCK,
            "ACTIVE_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_REMAINING": ACTIVE_STATUS,
            "BACKGROUND_3C7_AUTHORIZATION_DENIED_PHYSICAL_ADAPTER_IMPLEMENTATION_REMAINING":
                "BACKGROUND_3C8_ADAPTER_AUDITED_AUTHORIZATION_REVIEW_REMAINING",
            "INTEGRATED_CONTROL_RELEASE_AUDITED_PHYSICAL_ADAPTER_MISSING":
                "PHYSICAL_ADAPTER_AUDITED_MANUFACTURED_CONTROLS_ONLY_AUTHORIZATION_REVIEW_REMAINING",
        },
    )
    manifest["release"] = RELEASE
    manifest["release_date"] = "2026-08-05"

    for track in manifest.get("architecture", {}).get("research_tracks", []):
        if track.get("id") == "MD2S-R1-C-PHYS":
            track["status"] = ACTIVE_STATUS

    gates = manifest.setdefault("gates", {})
    gates.update({
        "R1.0": ACTIVE_STATUS,
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
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    })

    parent = manifest.setdefault("parent_action_v0_1", {})
    parent["next_block"] = NEXT_BLOCK
    operator = manifest.setdefault("c_phys_operator_entry", {})
    operator["status"] = "BACKGROUND_3C8_ADAPTER_AUDITED_AUTHORIZATION_REVIEW_REMAINING"
    operator["solver_authorized"] = False
    operator["next_block"] = NEXT_BLOCK
    c_phys_m1 = manifest.setdefault("c_phys_m1", {})
    c_phys_m1["next_block"] = NEXT_BLOCK
    c_phys_m1["background_existence"] = "NOT_ESTABLISHED"
    c_phys_m1["physical_evidence_effect"] = "NONE"

    central = manifest.setdefault("central_registries", {})
    central["session_checkpoint_snapshot"] = str(SNAPSHOT_PATH.relative_to(ROOT))
    central["c_phys_m1_background_3c8_contract"] = CONTRACT
    central["c_phys_m1_background_3c8_audit_result"] = AUDIT_RESULT
    central["c_phys_m1_background_3c8_ledger"] = LEDGER

    text = json.dumps(manifest, ensure_ascii=False)
    forbidden = [
        OLD_NEXT_BLOCK,
        "ACTIVE_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_REMAINING",
        "BACKGROUND_3C7_AUTHORIZATION_DENIED_PHYSICAL_ADAPTER_IMPLEMENTATION_REMAINING",
        '"BACKGROUND_3C8_PHYSICAL_EXECUTION_ADAPTER": "NOT_STARTED"',
    ]
    if any(token in text for token in forbidden):
        raise RuntimeError("stale Background-3C8 manifest state remains")
    return manifest


def update_checkpoint() -> dict[str, Any]:
    checkpoint = load_json(LATEST_PATH)
    checkpoint = recursive_replace(
        checkpoint,
        {
            OLD_NEXT_BLOCK: NEXT_BLOCK,
            "ACTIVE_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_REMAINING": ACTIVE_STATUS,
            "INTEGRATED_CONTROL_RELEASE_AUDITED_PHYSICAL_ADAPTER_MISSING":
                "PHYSICAL_ADAPTER_AUDITED_MANUFACTURED_CONTROLS_ONLY_AUTHORIZATION_REVIEW_REMAINING",
            "No source-bound physical adapter or operative single-use grant exists.":
                "The source-bound adapter has passed manufactured controls only; no operative single-use grant exists.",
            "Do not import or call the physical backends during Background-3C8 target-path development.":
                "Do not interpret static source binding or manufactured adapter controls as real-backend execution.",
            "Do not create an operative grant or execute CP01R1 in Background-3C8.":
                "Do not create an operative grant or execute CP01R1 during Background-3C9 review.",
        },
    )
    checkpoint["checkpoint_id"] = CHECKPOINT_ID
    checkpoint["timestamp"] = TIMESTAMP
    checkpoint["basis_commit"] = BASIS_COMMIT
    checkpoint["canonical_snapshot"] = str(SNAPSHOT_PATH.relative_to(ROOT))
    checkpoint["supersedes"] = "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.26.json"

    sources = checkpoint.setdefault("sources", [])
    append_unique(sources, [CONTRACT, AUDIT_RESULT, LEDGER, ADAPTER, WORKER, VALIDATOR, TEST])

    checkpoint["current_goal"] = (
        "Perform the Background-3C9 physical-adapter authorization review only, without importing "
        "or calling either physical backend, creating an operative grant, or executing CP01R1."
    )
    checkpoint["current_workstream"] = (
        "PRIMARY_C_PHYS_M1_BACKGROUND_3C9_PHYSICAL_ADAPTER_AUTHORIZATION_REVIEW_"
        "WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC"
    )
    workstreams = checkpoint.setdefault("current_workstreams", [])
    if not workstreams:
        raise RuntimeError("checkpoint current_workstreams missing")
    workstreams[0]["track_id"] = "MD2S-R1-C-PHYS"
    workstreams[0]["model_id"] = "HZT-M0-S6-C-PHYS-M1"
    workstreams[0]["priority"] = "PRIMARY"
    workstreams[0]["next_block"] = NEXT_BLOCK
    checkpoint["governance_principle"] = (
        "A source-bound adapter validated with manufactured stubs remains software QA only. "
        "Physical authorization requires a separate fail-closed review and may not be inferred from 3C8."
    )

    gates = checkpoint.setdefault("gate_state", {})
    gates.update({
        "MD2S-R1-C-PHYS": ACTIVE_STATUS,
        "R1.0": ACTIVE_STATUS,
        "BACKGROUND_SOLVER_IMPLEMENTATION":
            "PHYSICAL_ADAPTER_AUDITED_MANUFACTURED_CONTROLS_ONLY_AUTHORIZATION_REVIEW_REMAINING",
        "BACKGROUND_3C8_PHYSICAL_EXECUTION_ADAPTER": ADAPTER_STATUS,
        "BACKGROUND_3C9_AUTHORIZATION_REVIEW": "NOT_STARTED",
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
    results[:] = [item for item in results if item.get("result_id") != "UL-RES-C-PHYS-M1-BG3C8-001"]
    results.append({
        "result_id": "UL-RES-C-PHYS-M1-BG3C8-001",
        "statement": (
            "The source-bound Background-3C8 adapter passed immutable run, seed and 35-entry schedule binding, "
            "real-backend AST export binding without import, manufactured primary-to-independent handoff, "
            "result-schema preview, replay rejection, timeout, signal and atomic-artifact controls while all "
            "physical solver and CP01R1 counters remained zero."
        ),
        "status": ADAPTER_STATUS,
        "evidence_effect": "SOFTWARE_PHYSICAL_ADAPTER_BINDING_AND_MANUFACTURED_TRANSACTION_QA_ONLY",
        "physical_evidence_effect": "NONE",
        "package_manifest_sha256": PACKAGE_DIGEST,
        "schedule_sha256": SCHEDULE_DIGEST,
        "sources": [CONTRACT, AUDIT_RESULT, LEDGER],
    })

    blockers = checkpoint.setdefault("open_blockers", [])
    blockers[:] = [
        item for item in blockers
        if item.get("blocker_id") not in {
            "UL-BLK-C-PHYS-BACKGROUND-3C8-001",
            "UL-BLK-C-PHYS-BACKGROUND-3C9-001",
        }
    ]
    blockers.append({
        "blocker_id": "UL-BLK-C-PHYS-BACKGROUND-3C9-001",
        "track_id": "MD2S-R1-C-PHYS",
        "statement": (
            "The fail-closed Background-3C9 authorization review remains unperformed; 3C8 used manufactured "
            "stubs only and no operative single-use grant or physical backend execution is authorized."
        ),
        "sources": [AUDIT_RESULT],
    })

    checkpoint["active_assumptions"] = [
        "CP01R1 remains the sole frozen physical run input and has not been executed.",
        "Background-3C8 binds real backend sources statically but executes manufactured stubs only.",
        "No operative single-use grant exists.",
        "No physical result directory, physical backend import or physical solver invocation exists.",
    ]
    checkpoint["forbidden_inferences"] = [
        "Do not interpret the Background-3C8 adapter audit as CP01R1 authorization.",
        "Do not interpret AST source binding as a real backend import or call.",
        "Do not interpret manufactured primary-independent agreement as physical backend agreement.",
        "Do not create an operative grant or execute CP01R1 during Background-3C9 review.",
        "Do not infer a background, continuum theorem, stability, ghost freedom or evidence upgrade.",
    ]
    checkpoint["entry_points"] = [CONTRACT, AUDIT_RESULT, LEDGER, ADAPTER, VALIDATOR, TEST]
    checkpoint["next_exact_action"] = (
        "Execute C-PHYS-R1.0-BACKGROUND-3C9_PHYSICAL_ADAPTER_AUTHORIZATION_REVIEW_ONLY: review the "
        "manufactured-control adapter release fail-closed; perform zero physical imports, Newton, shooting, "
        "CP01R1, grant-creation and physical-result operations."
    )

    text = json.dumps(checkpoint, ensure_ascii=False)
    forbidden = [
        OLD_NEXT_BLOCK,
        "ACTIVE_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_REMAINING",
        "UL-BLK-C-PHYS-BACKGROUND-3C8-001",
        '"BACKGROUND_3C8_PHYSICAL_EXECUTION_ADAPTER": "NOT_STARTED"',
    ]
    if any(token in text for token in forbidden):
        raise RuntimeError("stale Background-3C8 checkpoint state remains")
    return checkpoint


def append_decision() -> None:
    lines = [line for line in DECISION_LOG_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    decisions = [json.loads(line) for line in lines]
    if any(item.get("decision_id") == DECISION_ID for item in decisions):
        raise RuntimeError(f"decision {DECISION_ID} already exists")
    decision = {
        "decision_id": DECISION_ID,
        "date": "2026-08-05",
        "topic": "background_3c8_physical_execution_adapter_audit",
        "decision": (
            "The source-bound Background-3C8 physical execution adapter is accepted as "
            "PASS_AUDITED_MANUFACTURED_CONTROLS_ONLY. Immutable run, payload, seed and schedule binding, "
            "real-backend AST export binding without import, candidate handoff, result-schema translation, "
            "single-consumption control capability, replay rejection, resource limits, timeout, signal and "
            "atomic external artifacts passed. No physical backend, solver, CP01R1, operative grant or physical "
            "result was used or created."
        ),
        "status": "ACTIVE",
        "reason": (
            "The adapter mechanics are reproducibly audited with package digest " + PACKAGE_DIGEST +
            " and schedule digest " + SCHEDULE_DIGEST +
            ". Manufactured controls establish software transaction integrity only and cannot authorize physical execution."
        ),
        "sources": [CONTRACT, AUDIT_RESULT, LEDGER, VALIDATOR, TEST],
        "evidence_effect": "SOFTWARE_PHYSICAL_ADAPTER_BINDING_AND_MANUFACTURED_TRANSACTION_QA_ONLY",
        "physical_evidence_effect": "NONE",
        "supersedes": None,
    }
    with DECISION_LOG_PATH.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(decision, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> None:
    if SNAPSHOT_PATH.exists():
        raise RuntimeError("checkpoint v1.27 already exists")
    manifest = update_manifest()
    checkpoint = update_checkpoint()
    append_decision()
    write_json(MANIFEST_PATH, manifest)
    write_json(SNAPSHOT_PATH, checkpoint)
    write_json(LATEST_PATH, checkpoint)
    if SNAPSHOT_PATH.read_bytes() != LATEST_PATH.read_bytes():
        raise RuntimeError("checkpoint snapshot and stable alias differ")
    print("PASS: Background-3C8 canonical synchronization prepared")


if __name__ == "__main__":
    main()
