#!/usr/bin/env python3
"""ULSH-01 / WP3-D8 CP01R2 fresh runtime issuer v2.0.

Default mode is audit-only. Runtime issuance is allowed only on the first
GitHub Actions attempt of the exact push to main that carries the D8 trigger.
The issuer performs a fresh source/governance recheck, creates one new v2.0
release authorization and one fresh single-use grant, then exits. The following
workflow step must spend that grant exactly once through the independently
reviewed D6H1 transaction supervisor v1.2.

This module changes no physical equation, parameter, topology, seed, mesh,
threshold, ETRN-01 rule or independent-backend requirement.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SUPERVISOR_PATH = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d6h1_cp01r2_transaction_v1.2.py"
TARGET_PATH = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d6h1_cp01r2_target_v1.1.py"
CONTRACT_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2HardeningContract_v1.0.json"
D6R1_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6R1_CP01R2IndependentReview_v1.0.json"
D7_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D7_CP01R2FreshReleaseDecision_v1.0.json"
TRIGGER_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D8_CP01R2ImmediateExecutionTrigger_v2.0.json"
CHECKPOINT_SCHEMA_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2CheckpointSchema_v1.0.json"
RESULT_SCHEMA_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2ResultSchema_v1.0.json"
DEPENDENCY_PATH = ROOT / "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3B_v0.1.txt"
RELEASE_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2_PhysicalSolveReleaseAuthorization_v2.0.json"
GRANT_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2_SingleUseExecutionGrant_v2.0.json"

EXPECTED_RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2"
EXPECTED_PAYLOAD_SHA256 = "e8b8e82d2cb1472d91c387a40c8f84024c2549a3dcc2c897df5561f7bf721b36"
EXPECTED_SCHEDULE_SHA256 = "929f59d018cc511f36c98ef26a8614ed495fe699a067b1b33e6c5b53efaf8e0b"
EXPECTED_DEPENDENCY_SHA256 = "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f"
EXPECTED_PLANNED_ENTRY_COUNT = 35
EXPECTED_D7_DECISION_ID = "ULSH-01-WP3-D7-CP01R2-FRESH-RELEASE-DEC-20260812-A"
EXPECTED_D7_BLOB = "7c72b82bc7114908bf151e846002f1b5227021b9"
EXPECTED_D6R1_BLOB = "635427fefce59dd2698bf47c92c65a788b4fe816"
EXPECTED_CONTRACT_BLOB = "e20be1172785aba293bb97212220856e77591bdf"
EXPECTED_SUPERVISOR_BLOB = "080aab132948d095716a9d0675518b82088cd9b3"
EXPECTED_TARGET_BLOB = "ad1dd5201ca7399bc283a24a38b18df55f3b7e75"
EXPECTED_CHECKPOINT_SCHEMA_BLOB = "339f579c8b3d9f1ffffca04e79a5acf817a3c2eb"
EXPECTED_RESULT_SCHEMA_BLOB = "54bf49acdfcca128e3b909d6e479b1178c77c276"
EXPECTED_TRIGGER_INTENT = "FRESH_RUNTIME_RECHECK_THEN_ISSUE_V2_SINGLE_USE_CP01R2_GRANT_AND_EXECUTE_IMMEDIATELY"
EXPECTED_EXECUTION_HOLDER = "GITHUB_ACTIONS_HOSTED_UBUNTU_24_04"
EXPECTED_REPRO_TICKET = "ULSH-01-WP3-D8-CP01R2-GHA-20260812-A"
EXPECTED_ARMED_FROM_MAIN = "7cf538929e57614b7c0c13a7244764ac203a1915"
ISSUER_VALIDITY_SECONDS = 3300


class IssuanceFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise IssuanceFailure(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IssuanceFailure(f"cannot load required JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise IssuanceFailure(f"top-level object required: {path}")
    return value


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    data = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.d8-issuer-{os.getpid()}")
    with temp.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)
    if os.name == "posix":
        fd = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise IssuanceFailure(f"cannot attest checked-out git HEAD: {exc}") from exc


def import_supervisor() -> Any:
    spec = importlib.util.spec_from_file_location("ulsh_cp01r2_d8_supervisor", SUPERVISOR_PATH)
    if spec is None or spec.loader is None:
        raise IssuanceFailure("cannot import exact D6H1 transaction supervisor")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def static_audit(supervisor: Any) -> dict[str, Any]:
    require(not RELEASE_PATH.exists() and not GRANT_PATH.exists(), "fresh v2.0 release/grant must be absent before D8 issuance")
    d7 = load_json(D7_PATH)
    d6r1 = load_json(D6R1_PATH)
    contract = load_json(CONTRACT_PATH)
    trigger = load_json(TRIGGER_PATH)

    exact_blobs = {
        D7_PATH: EXPECTED_D7_BLOB,
        D6R1_PATH: EXPECTED_D6R1_BLOB,
        CONTRACT_PATH: EXPECTED_CONTRACT_BLOB,
        SUPERVISOR_PATH: EXPECTED_SUPERVISOR_BLOB,
        TARGET_PATH: EXPECTED_TARGET_BLOB,
        CHECKPOINT_SCHEMA_PATH: EXPECTED_CHECKPOINT_SCHEMA_BLOB,
        RESULT_SCHEMA_PATH: EXPECTED_RESULT_SCHEMA_BLOB,
    }
    for path, expected in exact_blobs.items():
        require(git_blob_sha1(path) == expected, f"source binding drift: {path}")
    require(sha256_file(DEPENDENCY_PATH) == EXPECTED_DEPENDENCY_SHA256, "dependency lock bytes drifted")

    require(d7.get("status") == "PASS_WP3_D7_CP01R2_ELIGIBLE_FOR_FRESH_SINGLE_USE_RELEASE_ISSUANCE_NO_EXECUTION", "D7 release decision is not PASS")
    require(d7.get("decision_id") == EXPECTED_D7_DECISION_ID, "D7 decision id drift")
    require(d7.get("run_id") == EXPECTED_RUN_ID and d7.get("run_payload_sha256") == EXPECTED_PAYLOAD_SHA256, "D7 run/payload drift")
    require(d7.get("schedule_sha256") == EXPECTED_SCHEDULE_SHA256 and d7.get("planned_entry_count") == EXPECTED_PLANNED_ENTRY_COUNT, "D7 schedule drift")
    require(d7.get("dependency_lock_sha256") == EXPECTED_DEPENDENCY_SHA256, "D7 dependency drift")
    decision = d7.get("decision", {})
    require(decision.get("eligible_for_fresh_release_issuance") is True and decision.get("release_physical_solve") is True, "D7 does not permit fresh issuance")
    require(decision.get("authorization_scope") == "SINGLE_USE_CP01R2_D6H1_HARDENED_PATH_ONLY", "D7 scope drift")
    require(decision.get("fresh_runtime_recheck_required_immediately_before_issuance") is True, "D7 fresh recheck requirement missing")
    require(decision.get("execution_requires_fresh_single_use_grant") is True and decision.get("grant_replay_permitted") is False, "D7 grant/replay firewall drift")
    for key in ("parallel_execution", "adaptive_retry", "parameter_or_topology_mutation", "method_or_threshold_relaxation", "branch_scan", "fallback_method", "old_grant_reuse", "failed_attempt_result_reclassification"):
        require(decision.get(key) is False, f"D7 forbidden capability enabled: {key}")
    require(d7.get("next_allowed_action") == "ULSH-01_WP3_D8_CP01R2_FRESH_RUNTIME_RECHECK_RELEASE_ISSUANCE_SINGLE_USE_GRANT_AND_IMMEDIATE_EXECUTION", "D7 next-action drift")

    require(d6r1.get("review_status") == "PASS_WP3_D6R1_D6_BLOCKERS_VERIFIED_CLOSED_NO_EXECUTION", "D6R1 review is not PASS")
    require(d6r1.get("new_release_blockers") == [], "D6R1 contains release blockers")
    disposition = d6r1.get("D6_blocker_disposition", {})
    require(disposition.get("D6-B01", {}).get("status") == "VERIFIED_CLOSED", "D6-B01 not verified closed")
    require(disposition.get("D6-B02", {}).get("status") == "VERIFIED_CLOSED", "D6-B02 not verified closed")

    require(contract.get("status") == "PASS_D6H1_IMPLEMENTED_NO_EXECUTION_PENDING_INDEPENDENT_REVIEW", "D6H1 contract status drift")
    require(contract.get("run_id") == EXPECTED_RUN_ID and contract.get("run_payload_sha256") == EXPECTED_PAYLOAD_SHA256, "D6H1 contract run drift")
    require(contract.get("schedule_sha256") == EXPECTED_SCHEDULE_SHA256 and contract.get("dependency_lock_sha256") == EXPECTED_DEPENDENCY_SHA256, "D6H1 contract schedule/dependency drift")
    protocol = contract.get("grant_protocol", {})
    require(protocol.get("future_release_path") == str(RELEASE_PATH.relative_to(ROOT)), "D6H1 future release path drift")
    require(protocol.get("future_grant_path") == str(GRANT_PATH.relative_to(ROOT)), "D6H1 future grant path drift")
    require(protocol.get("maximum_validity_seconds") == 3600 and ISSUER_VALIDITY_SECONDS <= 3600, "grant validity contract drift")

    require(trigger.get("status") == "ARMED_PENDING_MERGE_TO_MAIN", "D8 trigger status drift")
    require(trigger.get("operator_intent") == EXPECTED_TRIGGER_INTENT, "D8 trigger intent drift")
    require(trigger.get("governance_release_decision_id") == EXPECTED_D7_DECISION_ID, "D8 trigger D7 binding drift")
    require(trigger.get("run_id") == EXPECTED_RUN_ID and trigger.get("run_payload_sha256") == EXPECTED_PAYLOAD_SHA256, "D8 trigger run/payload drift")
    require(trigger.get("schedule_sha256") == EXPECTED_SCHEDULE_SHA256 and trigger.get("planned_entry_count") == EXPECTED_PLANNED_ENTRY_COUNT, "D8 trigger schedule drift")
    require(trigger.get("armed_from_main_commit") == EXPECTED_ARMED_FROM_MAIN, "D8 trigger baseline-main drift")
    require(trigger.get("execution_holder") == EXPECTED_EXECUTION_HOLDER and trigger.get("reproducibility_ticket_id") == EXPECTED_REPRO_TICKET, "D8 execution holder/ticket drift")

    preflight = supervisor.static_preflight()
    require(preflight.get("status") == "PASS_WP3_D6H1_CP01R2_TRANSACTION_HARDENING_NO_EXECUTION", "D6H1 transaction static preflight did not PASS")
    require(preflight.get("run_id") == EXPECTED_RUN_ID and preflight.get("run_payload_sha256") == EXPECTED_PAYLOAD_SHA256, "transaction preflight run drift")
    require(preflight.get("schedule_sha256") == EXPECTED_SCHEDULE_SHA256, "transaction preflight schedule drift")
    require(preflight.get("solver_calls") == 0 and preflight.get("physical_solve_executed") is False, "audit crossed no-execution boundary")

    return {
        "status": "PASS_WP3_D8_STATIC_AUDIT_ELIGIBLE_FOR_FRESH_RUNTIME_RECHECK_NO_EXECUTION",
        "run_id": EXPECTED_RUN_ID,
        "run_payload_sha256": EXPECTED_PAYLOAD_SHA256,
        "schedule_sha256": EXPECTED_SCHEDULE_SHA256,
        "planned_entry_count": EXPECTED_PLANNED_ENTRY_COUNT,
        "dependency_lock_sha256": EXPECTED_DEPENDENCY_SHA256,
        "d7_decision_id": EXPECTED_D7_DECISION_ID,
        "d6_blockers": {"D6-B01": "VERIFIED_CLOSED", "D6-B02": "VERIFIED_CLOSED"},
        "transaction_contract_sha256": sha256_file(CONTRACT_PATH),
        "source_bundle_sha256": preflight["source_bundle_sha256"],
        "target_git_blob_sha1": EXPECTED_TARGET_BLOB,
        "supervisor_git_blob_sha1": EXPECTED_SUPERVISOR_BLOB,
        "future_release_authorization_present": False,
        "future_single_use_grant_present": False,
        "solver_calls": 0,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
    }


def fresh_runtime_recheck(supervisor: Any) -> dict[str, Any]:
    audit = static_audit(supervisor)
    require(os.environ.get("GITHUB_EVENT_NAME") == "push", "physical issuance requires GitHub push event")
    require(os.environ.get("GITHUB_REF") == "refs/heads/main", "physical issuance requires refs/heads/main")
    require(os.environ.get("GITHUB_RUN_ATTEMPT") == "1", "workflow rerun is forbidden before issuance")
    head = git_head()
    require(os.environ.get("GITHUB_SHA") == head, "GITHUB_SHA does not match checked-out HEAD")
    require(head != EXPECTED_ARMED_FROM_MAIN, "D8 must execute from the merged trigger commit, not the pre-trigger baseline")
    audit.update({
        "status": "PASS_WP3_D8_FRESH_RUNTIME_RECHECK_ELIGIBLE_FOR_V2_SINGLE_USE_ISSUANCE",
        "checked_out_git_head": head,
        "github_run_id": os.environ.get("GITHUB_RUN_ID", "UNSET"),
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", "UNSET"),
        "github_event_name": os.environ.get("GITHUB_EVENT_NAME", "UNSET"),
        "execution_holder": EXPECTED_EXECUTION_HOLDER,
        "reproducibility_ticket_id": EXPECTED_REPRO_TICKET,
    })
    return audit


def issue(supervisor: Any, recheck: dict[str, Any]) -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    protocol = contract["grant_protocol"]
    now = datetime.now(timezone.utc).replace(microsecond=0)
    expires = now + timedelta(seconds=ISSUER_VALIDITY_SECONDS)
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    head = recheck["checked_out_git_head"]
    authorization_decision_id = f"UL-DEC-CP01R2-D8-{run_id}-{attempt}"
    nonce = secrets.token_hex(16)

    grant = {
        "schema": protocol["grant_schema"], "version": "2.0.0",
        "status": "GRANTED_SINGLE_USE_FOR_IMMEDIATE_CP01R2", "physical_solve_authorized": True,
        "run_id": EXPECTED_RUN_ID, "run_payload_sha256": EXPECTED_PAYLOAD_SHA256,
        "schedule_sha256": EXPECTED_SCHEDULE_SHA256, "planned_entry_count": EXPECTED_PLANNED_ENTRY_COUNT,
        "dependency_lock_sha256": EXPECTED_DEPENDENCY_SHA256,
        "result_schema_git_blob_sha1": EXPECTED_RESULT_SCHEMA_BLOB, "target_git_blob_sha1": EXPECTED_TARGET_BLOB,
        "transaction_contract_sha256": recheck["transaction_contract_sha256"], "source_bundle_sha256": recheck["source_bundle_sha256"],
        "authorization_decision_id": authorization_decision_id, "governance_release_decision_id": EXPECTED_D7_DECISION_ID,
        "grant_nonce": nonce, "issued_at": utc_text(now), "not_before": utc_text(now), "expires_at": utc_text(expires),
        "maximum_start_validity_seconds": ISSUER_VALIDITY_SECONDS,
        "single_use": True, "no_retry": True, "no_scan": True, "no_fallback": True,
        "no_parameter_or_topology_mutation": True, "parallel_execution_allowed": False,
        "method_or_threshold_relaxation_allowed": False, "random_restart_allowed": False,
        "adaptive_mesh_insertion_allowed": False, "independent_backend_required_after_primary_candidate": True,
        "replay_permitted": False, "execution_holder": EXPECTED_EXECUTION_HOLDER,
        "reproducibility_ticket_id": EXPECTED_REPRO_TICKET, "issued_from_git_head": head,
        "issued_from_github_run_id": run_id, "issued_from_github_run_attempt": attempt,
        "attempt_label": "CP01R2_FRESH_ATTEMPT_2_NOT_REPLAY_OF_D5", "physical_evidence_effect": "NONE"
    }
    atomic_json(GRANT_PATH, grant)
    grant_sha = sha256_file(GRANT_PATH)

    release = {
        "schema": protocol["release_schema"], "version": "2.0.0", "status": "GRANTED",
        "physical_solve_authorized": True, "run_id": EXPECTED_RUN_ID,
        "run_payload_sha256": EXPECTED_PAYLOAD_SHA256, "schedule_sha256": EXPECTED_SCHEDULE_SHA256,
        "planned_entry_count": EXPECTED_PLANNED_ENTRY_COUNT, "dependency_lock_sha256": EXPECTED_DEPENDENCY_SHA256,
        "result_schema_git_blob_sha1": EXPECTED_RESULT_SCHEMA_BLOB, "target_git_blob_sha1": EXPECTED_TARGET_BLOB,
        "transaction_contract_sha256": recheck["transaction_contract_sha256"], "source_bundle_sha256": recheck["source_bundle_sha256"],
        "grant_sha256": grant_sha, "authorization_decision_id": authorization_decision_id,
        "governance_release_decision_id": EXPECTED_D7_DECISION_ID, "issued_at": utc_text(now), "grant_expires_at": utc_text(expires),
        "scope": "EXACT_CP01R2_D6H1_HARDENED_SINGLE_USE_7_SEEDS_X_5_NODE_LEVELS_NO_SCAN_NO_FALLBACK_NO_MUTATION",
        "execution_holder": EXPECTED_EXECUTION_HOLDER, "reproducibility_ticket_id": EXPECTED_REPRO_TICKET,
        "issued_from_git_head": head, "issued_from_github_run_id": run_id, "issued_from_github_run_attempt": attempt,
        "attempt_label": "CP01R2_FRESH_ATTEMPT_2_NOT_REPLAY_OF_D5",
        "physical_evidence_effect_before_separate_result_review": "NONE"
    }
    atomic_json(RELEASE_PATH, release)
    release_sha = sha256_file(RELEASE_PATH)

    supervisor._patch_base_for_d6h1()
    base = supervisor.BASE
    validated_release, validated_grant, validated_release_sha, validated_grant_sha = base.validate_release_and_grant(now=datetime.now(timezone.utc))
    require(validated_release_sha == release_sha and validated_grant_sha == grant_sha, "runtime validator hash mismatch")
    require(validated_release.get("governance_release_decision_id") == EXPECTED_D7_DECISION_ID, "release lost D7 binding")
    require(validated_grant.get("governance_release_decision_id") == EXPECTED_D7_DECISION_ID, "grant lost D7 binding")
    require(validated_release.get("authorization_decision_id") == validated_grant.get("authorization_decision_id") == authorization_decision_id, "release/grant authorization binding mismatch")

    return {
        "status": "PASS_WP3_D8_V2_RELEASE_AND_FRESH_SINGLE_USE_GRANT_ISSUED_FOR_IMMEDIATE_EXECUTION",
        "run_id": EXPECTED_RUN_ID, "authorization_decision_id": authorization_decision_id,
        "governance_release_decision_id": EXPECTED_D7_DECISION_ID, "grant_nonce": nonce,
        "grant_sha256": grant_sha, "release_authorization_sha256": release_sha,
        "issued_at": utc_text(now), "not_before": utc_text(now), "expires_at": utc_text(expires),
        "checked_out_git_head": head, "schedule_sha256": EXPECTED_SCHEDULE_SHA256,
        "planned_entry_count": EXPECTED_PLANNED_ENTRY_COUNT, "execution_holder": EXPECTED_EXECUTION_HOLDER,
        "reproducibility_ticket_id": EXPECTED_REPRO_TICKET, "physical_solve_authorized": True,
        "physical_solve_executed_at_issuance": False,
        "next_action": "IMMEDIATELY_CALL_D6H1_CP01R2_TRANSACTION_V1_2_EXECUTE_ONCE",
        "replay_permitted": False, "physical_evidence_effect": "NONE"
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", action="store_true", help="explicit audit-only mode")
    parser.add_argument("--issue-summary", help="runtime-only: write fresh recheck and issuance summary")
    args = parser.parse_args()
    try:
        supervisor = import_supervisor()
        if args.issue_summary:
            recheck = fresh_runtime_recheck(supervisor)
            issuance = issue(supervisor, recheck)
            summary = {"fresh_runtime_recheck": recheck, "issuance": issuance}
            atomic_json(Path(args.issue_summary), summary)
            print(json.dumps(summary, indent=2, sort_keys=True))
            return 0
        audit = static_audit(supervisor)
        print(json.dumps(audit, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"D8_ISSUANCE_FAILURE: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 78


if __name__ == "__main__":
    raise SystemExit(main())
