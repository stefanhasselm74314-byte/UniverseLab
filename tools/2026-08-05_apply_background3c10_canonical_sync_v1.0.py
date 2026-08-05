#!/usr/bin/env python3
"""One-shot canonical synchronization after the audited Background-3C10 R3 release.

This script advances public project state only. It preserves R1/R2 as immutable
fail-closed results and records R3 as real-backend analytic a_F=0 software QA.
It creates no grant, performs no backend import, and executes no numerical path.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "project-manifest.json"
LATEST_PATH = ROOT / "registry/session-checkpoint-latest.json"
SNAPSHOT_PATH = ROOT / "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.29.json"
DECISION_LOG_PATH = ROOT / "registry/decision-log.jsonl"

OLD_RELEASE = "2.20-c-phys-m1-background-3c9-authorization-denied-v0.1"
NEW_RELEASE = "2.21-c-phys-m1-background-3c10-real-backend-control-audited-v0.1"
OLD_CHECKPOINT = "UL-CHK-20260805-028"
NEW_CHECKPOINT = "UL-CHK-20260805-029"
DECISION_ID = "UL-DEC-0036"
BASIS_COMMIT = "e8c6e78d7dddd60d92a83bc8fbe82c3ef79e5e98"
OLD_NEXT = "C-PHYS-R1.0-BACKGROUND-3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE_IMPLEMENTATION_ONLY"
NEW_NEXT = "C-PHYS-R1.0-BACKGROUND-3C11_REAL_BACKEND_CONTROL_RELEASE_AUTHORIZATION_REVIEW_ONLY"
OLD_ACTIVE = "ACTIVE_REAL_BACKEND_ADAPTER_CONTROL_RELEASE_IMPLEMENTATION_REMAINING"
NEW_ACTIVE = "ACTIVE_REAL_BACKEND_CONTROL_RELEASE_AUTHORIZATION_REVIEW_REMAINING"
OLD_SOLVER_IMPLEMENTATION = "PHYSICAL_ADAPTER_AUDITED_MANUFACTURED_CONTROLS_ONLY_REAL_BACKEND_CONTROL_RELEASE_REMAINING"
NEW_SOLVER_IMPLEMENTATION = "REAL_BACKEND_AF0_CONTROL_RELEASE_AUDITED_AUTHORIZATION_REVIEW_REMAINING"
R1_STATUS = "FAIL_CLOSED_PRIMARY_UNIFORM_BULK_THRESHOLD_AT_N96"
R2_STATUS = "FAIL_CLOSED_CANDIDATE_JSON_KEY_ORDER_MISTAKEN_FOR_VECTOR_ORDER"
R3_STATUS = "PASS_REAL_BACKEND_AF0_CONTROL_RELEASE_NO_TARGET_SOLVE"
R3_GATE = "PASS_AUDITED_AF0_CONTROL_ONLY"
PACKAGE_DIGEST = "a7b48c88061e00cc3dc44dd00a2a17855a7f8c65dd228f725101fde9a1839eb4"
CANDIDATE_DIGEST = "6a00f71f4904574841d17eaebba7f8318fc136d477ab6fd324f3354f1b33e400"

SOURCE_PATHS = [
    "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlContract_v0.1.json",
    "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlFailureResult_v0.1.json",
    "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlContract_v0.2.json",
    "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlFailureResult_v0.2.json",
    "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlContract_v0.3.json",
    "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlAuditResult_v0.3.json",
    "science/hzt-m0/md2s/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlLedger_v0.1.md",
    "science/hzt-m0/md2s/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlLedger_v0.2.md",
    "science/hzt-m0/md2s/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlLedger_v0.3.md",
    "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_worker_v0.1.py",
    "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_worker_v0.2.py",
    "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_worker_v0.3.py",
    "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_control_release_v0.1.py",
    "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_control_release_v0.2.py",
    "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_control_release_v0.3.py",
    "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c10_v0.1.py",
    "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c10_v0.2.py",
    "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c10_v0.3.py",
    "tests/2026-08-05_test_hzt_m0_s6_c_phys_m1_background_3c10_v0.1.py",
    "tests/2026-08-05_test_hzt_m0_s6_c_phys_m1_background_3c10_v0.2.py",
    "tests/2026-08-05_test_hzt_m0_s6_c_phys_m1_background_3c10_v0.3.py",
    ".github/workflows/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10_RealBackendControl_v0.3.yml",
    ".github/workflows/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10_AuditResultBinding_v0.1.yml",
]


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"object required: {path}")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=False, ensure_ascii=False) + "\n"


def replace_exact(value: Any, old: Any, new: Any) -> int:
    count = 0
    if isinstance(value, dict):
        for key, item in list(value.items()):
            if item == old:
                value[key] = deepcopy(new)
                count += 1
            else:
                count += replace_exact(item, old, new)
    elif isinstance(value, list):
        for index, item in enumerate(list(value)):
            if item == old:
                value[index] = deepcopy(new)
                count += 1
            else:
                count += replace_exact(item, old, new)
    return count


def append_unique(sequence: list[Any], value: Any, *, key: str | None = None) -> None:
    if key is None:
        if value not in sequence:
            sequence.append(value)
        return
    identity = value.get(key) if isinstance(value, dict) else None
    for index, item in enumerate(sequence):
        if isinstance(item, dict) and item.get(key) == identity:
            sequence[index] = value
            return
    sequence.append(value)


def remove_by_id(sequence: list[Any], identifiers: set[str], field: str) -> None:
    sequence[:] = [
        item for item in sequence
        if not (isinstance(item, dict) and item.get(field) in identifiers)
    ]


def update_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("release") != OLD_RELEASE:
        raise RuntimeError(f"unexpected manifest release: {manifest.get('release')}")
    manifest["release"] = NEW_RELEASE
    manifest["release_date"] = "2026-08-05"

    replace_exact(manifest, OLD_NEXT, NEW_NEXT)
    replace_exact(manifest, OLD_ACTIVE, NEW_ACTIVE)
    replace_exact(manifest, OLD_SOLVER_IMPLEMENTATION, NEW_SOLVER_IMPLEMENTATION)

    tracks = manifest.get("architecture", {}).get("research_tracks", [])
    for track in tracks:
        if track.get("id") == "MD2S-R1-C-PHYS":
            track["status"] = NEW_ACTIVE

    gates = manifest.setdefault("gates", {})
    gates.update({
        "R1.0": NEW_ACTIVE,
        "BACKGROUND_SOLVER_IMPLEMENTATION": NEW_SOLVER_IMPLEMENTATION,
        "BACKGROUND_3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE": R3_GATE,
        "BACKGROUND_3C10_R1": R1_STATUS,
        "BACKGROUND_3C10_R2": R2_STATUS,
        "BACKGROUND_3C10_R3": R3_STATUS,
        "BACKGROUND_3C11_AUTHORIZATION_REVIEW": "NOT_STARTED",
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

    manifest["next_block"] = NEW_NEXT
    for section_name in ("parent_action_v0_1", "c_phys_operator_entry", "c_phys_m1"):
        section = manifest.get(section_name)
        if isinstance(section, dict):
            section["next_block"] = NEW_NEXT
    operator = manifest.get("c_phys_operator_entry")
    if isinstance(operator, dict):
        operator["status"] = "BACKGROUND_3C10_REAL_BACKEND_AF0_CONTROL_AUDITED_AUTHORIZATION_REVIEW_REMAINING"
        operator["solver_authorized"] = False
        operator["physical_background"] = "NOT_ESTABLISHED"
        operator["physical_evidence_effect"] = "NONE"

    manifest["background_3c10"] = {
        "track_id": "MD2S-R1-C-PHYS",
        "model_id": "HZT-M0-S6-C-PHYS-M1",
        "classification": "SOFTWARE_REAL_BACKEND_ANALYTIC_CONTROL_TRANSACTION_QA_ONLY",
        "status": R3_GATE,
        "active_control_run_id": "HZT-M0-S6-C-PHYS-M1-BG3C10-AF0-CONTROL-R3",
        "append_only_failures": {
            "R1": R1_STATUS,
            "R2": R2_STATUS,
        },
        "package_manifest_sha256": PACKAGE_DIGEST,
        "source_count": 24,
        "candidate_sha256": CANDIDATE_DIGEST,
        "model_a_F": 0.0,
        "frozen_target_a_F": "1/4_NOT_EXECUTED",
        "primary_node_counts": [24, 48, 96],
        "independent_pole_cutoffs": [0.001, 0.0005, 0.00025],
        "independent_integration_call_count": 6,
        "json_mapping_key_order_semantic": False,
        "handoff_vector_order_source": "EXPLICIT_CANDIDATE_FIELDS_CONTRACT",
        "primary_newton_calls": 0,
        "shooting_jacobian_calls": 0,
        "nonlinear_root_calls": 0,
        "cp01r1_attempts": 0,
        "target_a_F_one_quarter_solves": 0,
        "operative_grants": 0,
        "physical_result_artifacts": 0,
        "continuum_convergence_inference_allowed": False,
        "physical_background": "NOT_ESTABLISHED",
        "physical_evidence_effect": "NONE",
        "audit_result": "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlAuditResult_v0.3.json",
        "next_block": NEW_NEXT,
    }

    registries = manifest.setdefault("central_registries", {})
    registries["session_checkpoint_snapshot"] = str(SNAPSHOT_PATH.relative_to(ROOT))
    registries.update({
        "background_3c10_contract_r1": SOURCE_PATHS[0],
        "background_3c10_failure_r1": SOURCE_PATHS[1],
        "background_3c10_contract_r2": SOURCE_PATHS[2],
        "background_3c10_failure_r2": SOURCE_PATHS[3],
        "background_3c10_contract_r3": SOURCE_PATHS[4],
        "background_3c10_audit_result_r3": SOURCE_PATHS[5],
        "background_3c10_ledger_r3": SOURCE_PATHS[8],
    })

    verified = manifest.setdefault("verified_results", [])
    append_unique(verified, {
        "result_id": "UL-RES-C-PHYS-M1-BG3C10-001",
        "statement": "The actual primary and independent M1 backend modules completed the exact analytic a_F=0 control transaction across isolated process boundaries with an explicit SHA-256-bound eight-field handoff, six DOP853 regional integrations, timeout and signal controls, and zero Newton, shooting-Jacobian, nonlinear-root, CP01R1, grant or physical-result operations. R1 and R2 remain immutable fail-closed records.",
        "status": R3_GATE,
        "evidence_effect": "SOFTWARE_REAL_BACKEND_ANALYTIC_CONTROL_TRANSACTION_QA_ONLY",
        "physical_evidence_effect": "NONE",
        "package_manifest_sha256": PACKAGE_DIGEST,
        "candidate_sha256": CANDIDATE_DIGEST,
        "sources": SOURCE_PATHS[:9],
    }, key="result_id")


def update_checkpoint(latest: dict[str, Any]) -> dict[str, Any]:
    if latest.get("checkpoint_id") != OLD_CHECKPOINT:
        raise RuntimeError(f"unexpected checkpoint: {latest.get('checkpoint_id')}")
    checkpoint = deepcopy(latest)
    checkpoint["checkpoint_id"] = NEW_CHECKPOINT
    checkpoint["timestamp"] = "2026-08-05T10:51:00+02:00"
    checkpoint["basis_commit"] = BASIS_COMMIT
    checkpoint["canonical_snapshot"] = str(SNAPSHOT_PATH.relative_to(ROOT))
    checkpoint["supersedes"] = "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.28.json"

    sources = checkpoint.setdefault("sources", [])
    for source in SOURCE_PATHS:
        append_unique(sources, source)

    replace_exact(checkpoint, OLD_NEXT, NEW_NEXT)
    replace_exact(checkpoint, OLD_ACTIVE, NEW_ACTIVE)
    replace_exact(checkpoint, OLD_SOLVER_IMPLEMENTATION, NEW_SOLVER_IMPLEMENTATION)

    checkpoint["current_goal"] = "Perform the Background-3C11 authorization review of the audited real-backend a_F=0 control release without importing a backend, creating a grant, or executing CP01R1."
    checkpoint["current_workstream"] = "PRIMARY_C_PHYS_M1_BACKGROUND_3C11_REAL_BACKEND_CONTROL_RELEASE_AUTHORIZATION_REVIEW_WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC"
    workstreams = checkpoint.setdefault("current_workstreams", [])
    for stream in workstreams:
        if stream.get("track_id") == "MD2S-R1-C-PHYS":
            stream["next_block"] = NEW_NEXT
            stream["priority"] = "PRIMARY"
    checkpoint["governance_principle"] = "Passing a real-backend analytic a_F=0 control transaction establishes software interface and orchestration QA only. It does not authorize the frozen a_F=1/4 target path; authorization remains fail-closed and requires a separate review and operative single-use grant release."

    gate = checkpoint.setdefault("gate_state", {})
    gate.update({
        "MD2S-R1-C-PHYS": NEW_ACTIVE,
        "R1.0": NEW_ACTIVE,
        "BACKGROUND_SOLVER_IMPLEMENTATION": NEW_SOLVER_IMPLEMENTATION,
        "BACKGROUND_3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE": R3_GATE,
        "BACKGROUND_3C10_R1": R1_STATUS,
        "BACKGROUND_3C10_R2": R2_STATUS,
        "BACKGROUND_3C10_R3": R3_STATUS,
        "BACKGROUND_3C11_AUTHORIZATION_REVIEW": "NOT_STARTED",
        "BACKGROUND_3C_EXECUTION": "NOT_AUTHORIZED",
        "BACKGROUND_SOLVER_EXECUTION": "NOT_AUTHORIZED",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "OFFICIAL_MD2S_SOLVER": "NOT_AUTHORIZED",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "PHYSICAL_EVIDENCE_EFFECT": "NONE",
    })

    verified = checkpoint.setdefault("verified_results", [])
    append_unique(verified, {
        "result_id": "UL-RES-C-PHYS-M1-BG3C10-001",
        "statement": "The actual primary and independent M1 backend modules completed the exact analytic a_F=0 control transaction through isolated process boundaries. The explicit eight-field handoff, six DOP853 integrations, import-time timeout and signal probes, schema preview, atomic external artifacts and negative interface tests passed. R1 and R2 remain immutable fail-closed records; no target solve occurred.",
        "status": R3_GATE,
        "evidence_effect": "SOFTWARE_REAL_BACKEND_ANALYTIC_CONTROL_TRANSACTION_QA_ONLY",
        "physical_evidence_effect": "NONE",
        "package_manifest_sha256": PACKAGE_DIGEST,
        "candidate_sha256": CANDIDATE_DIGEST,
        "sources": SOURCE_PATHS[:9],
    }, key="result_id")

    blockers = checkpoint.setdefault("open_blockers", [])
    remove_by_id(blockers, {
        "UL-BLK-C-PHYS-BACKGROUND-3C10-001",
        "UL-BLK-C-PHYS-BACKGROUND-3C9-001",
    }, "blocker_id")
    append_unique(blockers, {
        "blocker_id": "UL-BLK-C-PHYS-BACKGROUND-3C11-001",
        "track_id": "MD2S-R1-C-PHYS",
        "statement": "CP01R1 remains unauthorized. Background-3C11 must review whether the audited a_F=0 real-backend control release is sufficient for target-path eligibility; no operative single-use grant schema, issuance, expiry, consumption, replay prevention or target-path authorization binding presently exists.",
        "sources": [SOURCE_PATHS[5], "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C9PhysicalAdapterAuthorizationReview_v0.1.json"],
    }, key="blocker_id")

    checkpoint["active_assumptions"] = [
        "CP01R1 remains the sole frozen physical run input and has not been executed.",
        "Background-3C10 R3 is an exact analytic a_F=0 real-backend software control only.",
        "Background-3C10 R1 and R2 remain immutable fail-closed records and are not reclassified as PASS.",
        "The eight-component handoff vector is an analytic control vector, not a physical background candidate.",
        "The N=96 bulk residual uses a registered roundoff envelope and is not a continuum-convergence result.",
        "No operative single-use grant or physical result directory exists.",
    ]
    checkpoint["forbidden_inferences"] = [
        "Do not interpret the Background-3C10 R3 PASS as CP01R1 authorization.",
        "Do not interpret real-backend agreement at a_F=0 as evidence for a physical a_F=1/4 background.",
        "Do not reclassify R1 or R2 as passing controls.",
        "Do not infer continuum convergence, existence, uniqueness, Fredholmness, stability, ghost freedom, K1-D, K1-E or physical evidence.",
        "Do not create a grant or execute a backend during Background-3C11.",
    ]
    checkpoint["entry_points"] = [
        SOURCE_PATHS[4], SOURCE_PATHS[5], SOURCE_PATHS[8],
        SOURCE_PATHS[14], SOURCE_PATHS[17], SOURCE_PATHS[20],
    ]
    checkpoint["next_exact_action"] = "Execute C-PHYS-R1.0-BACKGROUND-3C11_REAL_BACKEND_CONTROL_RELEASE_AUTHORIZATION_REVIEW_ONLY as a read-only fail-closed review; import no backend, create no operative grant, and execute no CP01R1 or target-root path."
    return checkpoint


def append_decision() -> None:
    lines = [line for line in DECISION_LOG_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    decisions = [json.loads(line) for line in lines]
    if any(item.get("decision_id") == DECISION_ID for item in decisions):
        raise RuntimeError(f"decision already exists: {DECISION_ID}")
    decision = {
        "decision_id": DECISION_ID,
        "date": "2026-08-05",
        "topic": "background_3c10_real_backend_analytic_control_release_audit",
        "decision": "Background-3C10 R3 is accepted as PASS_AUDITED_AF0_CONTROL_ONLY. The actual primary and independent backend modules completed the exact analytic a_F=0 control transaction across isolated process boundaries with explicit field-order reconstruction, SHA-256 handoff, six DOP853 integrations, timeout and signal controls, schema preview and atomic external artifacts. R1 and R2 remain immutable fail-closed records. No CP01R1, a_F=1/4 target solve, Newton, shooting Jacobian, nonlinear root, operative grant or physical result occurred.",
        "status": "ACTIVE",
        "reason": "The closed 24-source package and persistent audit result reproduce package digest a7b48c88061e00cc3dc44dd00a2a17855a7f8c65dd228f725101fde9a1839eb4. The result establishes real-backend analytic software-interface QA only; target-path authorization remains a separate fail-closed decision.",
        "sources": [SOURCE_PATHS[1], SOURCE_PATHS[3], SOURCE_PATHS[4], SOURCE_PATHS[5], SOURCE_PATHS[8]],
        "evidence_effect": "SOFTWARE_REAL_BACKEND_ANALYTIC_CONTROL_TRANSACTION_QA_ONLY",
        "physical_evidence_effect": "NONE",
        "supersedes": None,
    }
    with DECISION_LOG_PATH.open("a", encoding="utf-8") as stream:
        if DECISION_LOG_PATH.stat().st_size and not DECISION_LOG_PATH.read_bytes().endswith(b"\n"):
            stream.write("\n")
        stream.write(json.dumps(decision, sort_keys=False, separators=(",", ":"), ensure_ascii=False) + "\n")


def validate_output(manifest: dict[str, Any], checkpoint: dict[str, Any]) -> None:
    if manifest["release"] != NEW_RELEASE:
        raise RuntimeError("release update failed")
    gates = manifest["gates"]
    expected = {
        "BACKGROUND_3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE": R3_GATE,
        "BACKGROUND_3C11_AUTHORIZATION_REVIEW": "NOT_STARTED",
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
        if gates.get(key) != value:
            raise RuntimeError(f"manifest gate drift: {key}={gates.get(key)!r}")
    if manifest.get("next_block") != NEW_NEXT:
        raise RuntimeError("manifest next block drift")
    if checkpoint["checkpoint_id"] != NEW_CHECKPOINT:
        raise RuntimeError("checkpoint ID drift")
    if checkpoint["current_workstreams"][0]["next_block"] != NEW_NEXT:
        raise RuntimeError("checkpoint next block drift")
    blocker_ids = {item.get("blocker_id") for item in checkpoint.get("open_blockers", []) if isinstance(item, dict)}
    if "UL-BLK-C-PHYS-BACKGROUND-3C11-001" not in blocker_ids:
        raise RuntimeError("3C11 blocker missing")
    if "UL-BLK-C-PHYS-BACKGROUND-3C10-001" in blocker_ids:
        raise RuntimeError("completed 3C10 blocker remains")


def main() -> None:
    manifest = load_json(MANIFEST_PATH)
    latest = load_json(LATEST_PATH)
    update_manifest(manifest)
    checkpoint = update_checkpoint(latest)
    validate_output(manifest, checkpoint)
    append_decision()
    MANIFEST_PATH.write_text(canonical_json(manifest), encoding="utf-8")
    snapshot_bytes = canonical_json(checkpoint).encode("utf-8")
    SNAPSHOT_PATH.write_bytes(snapshot_bytes)
    LATEST_PATH.write_bytes(snapshot_bytes)
    print(json.dumps({
        "status": "PASS_BACKGROUND_3C10_CANONICAL_SYNC",
        "release": NEW_RELEASE,
        "decision": DECISION_ID,
        "checkpoint": NEW_CHECKPOINT,
        "basis_commit": BASIS_COMMIT,
        "next_block": NEW_NEXT,
        "physical_evidence_effect": "NONE",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
