#!/usr/bin/env python3
"""One-shot canonical synchronization after Background-3C11 denial.

Advances public governance state only. No backend import, solver, grant, or
result artifact is created.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "project-manifest.json"
LATEST_PATH = ROOT / "registry/session-checkpoint-latest.json"
SNAPSHOT_PATH = ROOT / "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.30.json"
DECISION_LOG_PATH = ROOT / "registry/decision-log.jsonl"

OLD_RELEASE = "2.21-c-phys-m1-background-3c10-real-backend-control-audited-v0.1"
NEW_RELEASE = "2.22-c-phys-m1-background-3c11-authorization-denied-v0.1"
OLD_CHECKPOINT = "UL-CHK-20260805-029"
NEW_CHECKPOINT = "UL-CHK-20260805-030"
DECISION_ID = "UL-DEC-0037"
BASIS_COMMIT = "a5dcb30fd74afa6ccde92c140e67b71f77fbdaf2"
OLD_NEXT = "C-PHYS-R1.0-BACKGROUND-3C11_REAL_BACKEND_CONTROL_RELEASE_AUTHORIZATION_REVIEW_ONLY"
NEW_NEXT = "C-PHYS-R1.0-BACKGROUND-3C12_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE_IMPLEMENTATION_ONLY"
OLD_ACTIVE = "ACTIVE_REAL_BACKEND_CONTROL_RELEASE_AUTHORIZATION_REVIEW_REMAINING"
NEW_ACTIVE = "ACTIVE_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE_IMPLEMENTATION_REMAINING"
OLD_SOLVER_IMPLEMENTATION = "REAL_BACKEND_AF0_CONTROL_RELEASE_AUDITED_AUTHORIZATION_REVIEW_REMAINING"
NEW_SOLVER_IMPLEMENTATION = "REAL_BACKEND_AF0_CONTROL_AUDITED_TARGET_PATH_AND_GRANT_RELEASE_MISSING"
DENIAL = "DENIED_OPERATIVE_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE_ABSENT"
PACKAGE_DIGEST = "a7b48c88061e00cc3dc44dd00a2a17855a7f8c65dd228f725101fde9a1839eb4"
REVIEW_PATH = "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C11RealBackendControlAuthorizationReview_v0.1.json"
LEDGER_PATH = "science/hzt-m0/md2s/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C11AuthorizationReviewLedger_v0.1.md"
VALIDATOR_PATH = "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c11_v0.1.py"
TEST_PATH = "tests/2026-08-05_test_hzt_m0_s6_c_phys_m1_background_3c11_v0.1.py"
WORKFLOW_PATH = ".github/workflows/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C11_AuthorizationReview_v0.1.yml"
SOURCES = [REVIEW_PATH, LEDGER_PATH, VALIDATOR_PATH, TEST_PATH, WORKFLOW_PATH]


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"object required: {path}")
    return value


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


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


def remove_ids(sequence: list[Any], field: str, identities: set[str]) -> None:
    sequence[:] = [
        item for item in sequence
        if not (isinstance(item, dict) and item.get(field) in identities)
    ]


def update_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("release") != OLD_RELEASE:
        raise RuntimeError(f"unexpected release: {manifest.get('release')}")
    manifest["release"] = NEW_RELEASE
    manifest["release_date"] = "2026-08-05"
    replace_exact(manifest, OLD_NEXT, NEW_NEXT)
    replace_exact(manifest, OLD_ACTIVE, NEW_ACTIVE)
    replace_exact(manifest, OLD_SOLVER_IMPLEMENTATION, NEW_SOLVER_IMPLEMENTATION)

    for track in manifest.get("architecture", {}).get("research_tracks", []):
        if track.get("id") == "MD2S-R1-C-PHYS":
            track["status"] = NEW_ACTIVE

    gates = manifest.setdefault("gates", {})
    gates.update({
        "R1.0": NEW_ACTIVE,
        "BACKGROUND_SOLVER_IMPLEMENTATION": NEW_SOLVER_IMPLEMENTATION,
        "BACKGROUND_3C11_AUTHORIZATION_REVIEW": DENIAL,
        "BACKGROUND_3C12_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE": "NOT_STARTED",
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
        operator["status"] = "BACKGROUND_3C11_AUTHORIZATION_DENIED_TARGET_PATH_AND_GRANT_RELEASE_REMAINING"
        operator["solver_authorized"] = False
        operator["physical_background"] = "NOT_ESTABLISHED"
        operator["physical_evidence_effect"] = "NONE"

    manifest["background_3c11"] = {
        "track_id": "MD2S-R1-C-PHYS",
        "model_id": "HZT-M0-S6-C-PHYS-M1",
        "classification": "APPEND_ONLY_FAIL_CLOSED_TARGET_PATH_EXECUTION_ELIGIBILITY_REVIEW",
        "status": DENIAL,
        "reviewed_control_release": "BACKGROUND_3C10_R3_PASS_AUDITED_AF0_CONTROL_ONLY",
        "package_manifest_sha256": PACKAGE_DIGEST,
        "review_imported_backend": False,
        "physical_solver_calls": 0,
        "cp01r1_attempts": 0,
        "target_a_F_one_quarter_solves": 0,
        "operative_grants": 0,
        "physical_result_artifacts": 0,
        "physical_background": "NOT_ESTABLISHED",
        "physical_evidence_effect": "NONE",
        "review": REVIEW_PATH,
        "next_block": NEW_NEXT,
    }

    registries = manifest.setdefault("central_registries", {})
    registries["session_checkpoint_snapshot"] = str(SNAPSHOT_PATH.relative_to(ROOT))
    registries.update({
        "background_3c11_authorization_review": REVIEW_PATH,
        "background_3c11_authorization_ledger": LEDGER_PATH,
    })

    append_unique(manifest.setdefault("verified_results", []), {
        "result_id": "UL-RES-C-PHYS-M1-BG3C11-001",
        "statement": "The read-only Background-3C11 review denies CP01R1 authorization because the audited real-backend release covers only the analytic a_F=0 control, while no separately source-bound a_F=1/4 target-path release or operative single-use grant transaction exists. No backend, solver, grant or result artifact was used.",
        "status": DENIAL,
        "evidence_effect": "GOVERNANCE_AND_TARGET_PATH_EXECUTION_SAFETY_REVIEW_ONLY",
        "physical_evidence_effect": "NONE",
        "package_manifest_sha256": PACKAGE_DIGEST,
        "sources": SOURCES[:4],
    }, key="result_id")


def update_checkpoint(latest: dict[str, Any]) -> dict[str, Any]:
    if latest.get("checkpoint_id") != OLD_CHECKPOINT:
        raise RuntimeError(f"unexpected checkpoint: {latest.get('checkpoint_id')}")
    checkpoint = deepcopy(latest)
    checkpoint["checkpoint_id"] = NEW_CHECKPOINT
    checkpoint["timestamp"] = "2026-08-05T12:05:00+02:00"
    checkpoint["basis_commit"] = BASIS_COMMIT
    checkpoint["canonical_snapshot"] = str(SNAPSHOT_PATH.relative_to(ROOT))
    checkpoint["supersedes"] = "registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.29.json"
    for source in SOURCES:
        append_unique(checkpoint.setdefault("sources", []), source)

    replace_exact(checkpoint, OLD_NEXT, NEW_NEXT)
    replace_exact(checkpoint, OLD_ACTIVE, NEW_ACTIVE)
    replace_exact(checkpoint, OLD_SOLVER_IMPLEMENTATION, NEW_SOLVER_IMPLEMENTATION)

    checkpoint["current_goal"] = "Implement and audit Background-3C12 nonoperative single-use-grant and source-bound target-path release controls without importing either backend or executing CP01R1."
    checkpoint["current_workstream"] = "PRIMARY_C_PHYS_M1_BACKGROUND_3C12_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE_IMPLEMENTATION_WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC"
    for stream in checkpoint.setdefault("current_workstreams", []):
        if stream.get("track_id") == "MD2S-R1-C-PHYS":
            stream["next_block"] = NEW_NEXT
            stream["priority"] = "PRIMARY"
    checkpoint["governance_principle"] = "A passing real-backend a_F=0 control does not authorize the frozen a_F=1/4 target path. Authorization requires a separately versioned target-path release and an operative single-use grant with exact digest binding, atomic consumption, replay prevention and crash semantics."

    checkpoint.setdefault("gate_state", {}).update({
        "MD2S-R1-C-PHYS": NEW_ACTIVE,
        "R1.0": NEW_ACTIVE,
        "BACKGROUND_SOLVER_IMPLEMENTATION": NEW_SOLVER_IMPLEMENTATION,
        "BACKGROUND_3C11_AUTHORIZATION_REVIEW": DENIAL,
        "BACKGROUND_3C12_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE": "NOT_STARTED",
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

    append_unique(checkpoint.setdefault("verified_results", []), {
        "result_id": "UL-RES-C-PHYS-M1-BG3C11-001",
        "statement": "Background-3C11 denies CP01R1 authorization because the audited real-backend transaction is restricted to a_F=0 and neither a source-bound a_F=1/4 target-path release nor an operative replay-safe single-use grant exists. The review imported no backend and executed no solver.",
        "status": DENIAL,
        "evidence_effect": "GOVERNANCE_AND_TARGET_PATH_EXECUTION_SAFETY_REVIEW_ONLY",
        "physical_evidence_effect": "NONE",
        "package_manifest_sha256": PACKAGE_DIGEST,
        "sources": SOURCES[:4],
    }, key="result_id")

    blockers = checkpoint.setdefault("open_blockers", [])
    remove_ids(blockers, "blocker_id", {
        "UL-BLK-C-PHYS-BACKGROUND-3C11-001",
    })
    append_unique(blockers, {
        "blocker_id": "UL-BLK-C-PHYS-BACKGROUND-3C12-001",
        "track_id": "MD2S-R1-C-PHYS",
        "statement": "A separately source-bound a_F=1/4 target-path entry point and a nonoperative single-use-grant state machine with exact digest binding, validity window, nonce, atomic consumption, replay prevention and crash recovery remain unimplemented and unaudited.",
        "sources": [REVIEW_PATH],
    }, key="blocker_id")

    checkpoint["active_assumptions"] = [
        "CP01R1 remains the sole frozen physical run input and has not been executed.",
        "Background-3C10 R3 remains analytic a_F=0 real-backend software QA only.",
        "Background-3C10 R1 and R2 remain immutable fail-closed records.",
        "No a_F=1/4 target-path release or operative single-use grant exists.",
        "No physical result directory exists.",
    ]
    checkpoint["forbidden_inferences"] = [
        "Do not interpret the Background-3C11 denial as evidence against M1 or Hyperzeit.",
        "Do not interpret the Background-3C10 a_F=0 control as target-path validation at a_F=1/4.",
        "Do not create an operative grant or import a backend during Background-3C12.",
        "Do not infer physical background existence, uniqueness, Fredholmness, stability, ghost freedom, K1-D, K1-E or evidence.",
    ]
    checkpoint["entry_points"] = [REVIEW_PATH, LEDGER_PATH, VALIDATOR_PATH, TEST_PATH]
    checkpoint["next_exact_action"] = "Execute C-PHYS-R1.0-BACKGROUND-3C12_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE_IMPLEMENTATION_ONLY with synthetic/nonoperative grant controls and static target-path binding only; import no backend and execute no CP01R1."
    return checkpoint


def append_decision() -> None:
    lines = [line for line in DECISION_LOG_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    decisions = [json.loads(line) for line in lines]
    if any(item.get("decision_id") == DECISION_ID for item in decisions):
        raise RuntimeError(f"decision exists: {DECISION_ID}")
    decision = {
        "decision_id": DECISION_ID,
        "date": "2026-08-05",
        "topic": "background_3c11_target_path_authorization_review",
        "decision": "CP01R1 authorization is denied because the audited real-backend release is restricted to the analytic a_F=0 control and no separately versioned a_F=1/4 target-path release or operative single-use grant transaction exists. The review imported no backend and performed no solver, grant or result operation.",
        "status": "ACTIVE",
        "reason": "Control-path correctness is not target-path authorization. The target release must bind the exact main commit, frozen payload, seeds, 35-entry schedule, backend and dependency hashes, resource policy and result schema; the grant must provide validity, nonce, atomic consumption, replay protection and crash semantics before backend import.",
        "sources": SOURCES[:4],
        "evidence_effect": "GOVERNANCE_AND_TARGET_PATH_EXECUTION_SAFETY_REVIEW_ONLY",
        "physical_evidence_effect": "NONE",
        "supersedes": None,
    }
    with DECISION_LOG_PATH.open("a", encoding="utf-8") as stream:
        if DECISION_LOG_PATH.stat().st_size and not DECISION_LOG_PATH.read_bytes().endswith(b"\n"):
            stream.write("\n")
        stream.write(json.dumps(decision, separators=(",", ":"), ensure_ascii=False) + "\n")


def validate(manifest: dict[str, Any], checkpoint: dict[str, Any]) -> None:
    if manifest["release"] != NEW_RELEASE:
        raise RuntimeError("release drift")
    if manifest["gates"]["BACKGROUND_3C11_AUTHORIZATION_REVIEW"] != DENIAL:
        raise RuntimeError("3C11 status drift")
    if manifest["gates"]["BACKGROUND_3C12_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE"] != "NOT_STARTED":
        raise RuntimeError("3C12 status drift")
    if manifest["next_block"] != NEW_NEXT:
        raise RuntimeError("next block drift")
    if checkpoint["checkpoint_id"] != NEW_CHECKPOINT:
        raise RuntimeError("checkpoint drift")
    if checkpoint["current_workstreams"][0]["next_block"] != NEW_NEXT:
        raise RuntimeError("checkpoint next block drift")
    blocker_ids = {item.get("blocker_id") for item in checkpoint["open_blockers"] if isinstance(item, dict)}
    if "UL-BLK-C-PHYS-BACKGROUND-3C11-001" in blocker_ids:
        raise RuntimeError("completed blocker remains")
    if "UL-BLK-C-PHYS-BACKGROUND-3C12-001" not in blocker_ids:
        raise RuntimeError("3C12 blocker missing")


def main() -> None:
    manifest = load_json(MANIFEST_PATH)
    latest = load_json(LATEST_PATH)
    update_manifest(manifest)
    checkpoint = update_checkpoint(latest)
    validate(manifest, checkpoint)
    append_decision()
    MANIFEST_PATH.write_bytes(canonical(manifest))
    snapshot = canonical(checkpoint)
    SNAPSHOT_PATH.write_bytes(snapshot)
    LATEST_PATH.write_bytes(snapshot)
    print(json.dumps({
        "status": "PASS_BACKGROUND_3C11_CANONICAL_SYNC",
        "release": NEW_RELEASE,
        "decision": DECISION_ID,
        "checkpoint": NEW_CHECKPOINT,
        "basis_commit": BASIS_COMMIT,
        "next_block": NEW_NEXT,
        "physical_evidence_effect": "NONE"
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
