#!/usr/bin/env python3
"""ULSH-01 / WP3-D5 CP01R2 immediate runtime issuer v1.0.

The script performs the mandatory fresh governance/source recheck and only then
creates the exact CP01R2 release authorization plus one fresh single-use grant
inside the checked-out runtime workspace. It does not itself call the solver.
The immediately following GitHub Actions step invokes the independently reviewed
CP01R2 transaction supervisor exactly once.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SUPERVISOR_PATH = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3h1_cp01r2_transaction_v1.1.py"
CONTRACT_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2TransactionHardeningContract_v1.0.json"
RR1_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_RR1_IndependentReview_v1.0.json"
D4_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D4_CP01R2ReleaseDecision_v1.0.json"
TRIGGER_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D5_CP01R2ImmediateExecutionTrigger_v1.0.json"
RELEASE_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2_PhysicalSolveReleaseAuthorization_v1.0.json"
GRANT_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2_SingleUseExecutionGrant_v1.0.json"
DEPENDENCY_PATH = ROOT / "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3B_v0.1.txt"

EXPECTED_RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2"
EXPECTED_PAYLOAD_SHA256 = "e8b8e82d2cb1472d91c387a40c8f84024c2549a3dcc2c897df5561f7bf721b36"
EXPECTED_SCHEDULE_SHA256 = "929f59d018cc511f36c98ef26a8614ed495fe699a067b1b33e6c5b53efaf8e0b"
EXPECTED_DEPENDENCY_SHA256 = "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f"
EXPECTED_PLANNED_ENTRY_COUNT = 35
EXPECTED_D4_DECISION_ID = "ULSH-01-WP3-D4-CP01R2-RELEASE-DEC-20260812-A"
EXPECTED_D4_BLOB = "a50a9f44947e816d732320b832c4220b97e75b8f"
EXPECTED_RR1_BLOB = "e240cb9b7fb4990575a99c3f436640b7fd91cb8b"
EXPECTED_CONTRACT_BLOB = "ebe9193b6da50f6f352ac5397749d9caaceaf047"
EXPECTED_SUPERVISOR_BLOB = "07d1532be17e5d5d81c96ad4438c3195ca4653aa"
EXPECTED_TARGET_BLOB = "199815ac9e4014cc0d68fde71d634cdac24516ce"
EXPECTED_RESULT_SCHEMA_BLOB = "54bf49acdfcca128e3b909d6e479b1178c77c276"
EXPECTED_TRIGGER_INTENT = "ISSUE_EXACT_CP01R2_RELEASE_AND_FRESH_SINGLE_USE_GRANT_AFTER_MANDATORY_RECHECK_THEN_START_CP01R2_IMMEDIATELY"
EXPECTED_EXECUTION_HOLDER = "GITHUB_ACTIONS_HOSTED_UBUNTU_24_04"
EXPECTED_REPRO_TICKET = "ULSH-01-WP3-D5-CP01R2-GHA-20260812-A"
ISSUER_VALIDITY_SECONDS = 3300


class IssuanceFailure(RuntimeError):
    pass


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
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    data = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.issuer-{os.getpid()}")
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


def import_supervisor():
    spec = importlib.util.spec_from_file_location("ulsh_cp01r2_runtime_supervisor", SUPERVISOR_PATH)
    if spec is None or spec.loader is None:
        raise IssuanceFailure("cannot import exact CP01R2 transaction supervisor")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def require(condition: bool, message: str) -> None:
    if not condition:
        raise IssuanceFailure(message)


def fresh_recheck(supervisor: Any) -> dict[str, Any]:
    require(os.environ.get("GITHUB_REF") == "refs/heads/main", "physical transaction may run only from refs/heads/main")
    require(os.environ.get("GITHUB_RUN_ATTEMPT") == "1", "workflow rerun is forbidden before runtime issuance")
    require(not RELEASE_PATH.exists() and not GRANT_PATH.exists(), "CP01R2 release/grant path already exists before issuance")

    d4 = load_json(D4_PATH)
    rr1 = load_json(RR1_PATH)
    trigger = load_json(TRIGGER_PATH)
    contract = load_json(CONTRACT_PATH)

    require(git_blob_sha1(D4_PATH) == EXPECTED_D4_BLOB, "D4 release-decision bytes drifted")
    require(git_blob_sha1(RR1_PATH) == EXPECTED_RR1_BLOB, "D3H1-RR1 bytes drifted")
    require(git_blob_sha1(CONTRACT_PATH) == EXPECTED_CONTRACT_BLOB, "D3H1 contract bytes drifted")
    require(git_blob_sha1(SUPERVISOR_PATH) == EXPECTED_SUPERVISOR_BLOB, "CP01R2 supervisor bytes drifted")

    require(d4.get("status") == "PASS_WP3_D4_CP01R2_SINGLE_USE_RELEASE_AUTHORIZED_NO_EXECUTION", "D4 release decision is not PASS")
    require(d4.get("decision_id") == EXPECTED_D4_DECISION_ID, "D4 decision id drift")
    require(d4.get("run_id") == EXPECTED_RUN_ID and d4.get("run_payload_sha256") == EXPECTED_PAYLOAD_SHA256, "D4 run/payload binding drift")
    require(d4.get("schedule_sha256") == EXPECTED_SCHEDULE_SHA256, "D4 schedule binding drift")
    require(d4.get("dependency_lock_sha256") == EXPECTED_DEPENDENCY_SHA256, "D4 dependency binding drift")
    decision = d4.get("decision", {})
    require(decision.get("release_physical_solve") is True, "D4 does not authorize release issuance")
    require(decision.get("authorization_scope") == "SINGLE_USE_CP01R2_ONLY", "D4 scope is not CP01R2-only")
    require(decision.get("execution_requires_fresh_single_use_grant") is True, "D4 fresh-grant requirement missing")
    require(decision.get("grant_replay_permitted") is False, "D4 replay firewall drift")
    for key in ("parallel_execution", "adaptive_retry", "parameter_or_topology_mutation", "method_or_threshold_relaxation", "branch_scan", "fallback_method"):
        require(decision.get(key) is False, f"D4 forbidden capability enabled: {key}")

    require(rr1.get("review_status") == "PASS_WP3_D3H1_RR1_D3_BLOCKERS_VERIFIED_CLOSED_NO_EXECUTION", "D3H1-RR1 is not PASS")
    require(rr1.get("new_release_blockers") == [], "D3H1-RR1 contains release blockers")
    require(len(rr1.get("review_gates", {})) == 8 and all(value == "PASS" for value in rr1["review_gates"].values()), "D3H1-RR1 is not 8/8 PASS")
    disposition = rr1.get("D3_blocker_disposition", {})
    require(disposition.get("D3-B01", {}).get("status") == "VERIFIED_CLOSED", "D3-B01 is not independently closed")
    require(disposition.get("D3-B02", {}).get("status") == "VERIFIED_CLOSED", "D3-B02 is not independently closed")

    require(trigger.get("status") == "ARMED_PENDING_MERGE_TO_MAIN", "operator trigger status drift")
    require(trigger.get("operator_intent") == EXPECTED_TRIGGER_INTENT, "operator trigger intent mismatch")
    require(trigger.get("governance_release_decision_id") == EXPECTED_D4_DECISION_ID, "trigger D4 decision binding mismatch")
    require(trigger.get("run_id") == EXPECTED_RUN_ID and trigger.get("run_payload_sha256") == EXPECTED_PAYLOAD_SHA256, "trigger run/payload binding drift")
    require(trigger.get("schedule_sha256") == EXPECTED_SCHEDULE_SHA256 and trigger.get("planned_entry_count") == EXPECTED_PLANNED_ENTRY_COUNT, "trigger schedule binding drift")
    require(trigger.get("execution_holder") == EXPECTED_EXECUTION_HOLDER, "execution holder mismatch")
    require(trigger.get("reproducibility_ticket_id") == EXPECTED_REPRO_TICKET, "reproducibility ticket mismatch")

    require(contract.get("status") == "PASS_D3H1_IMPLEMENTED_NO_EXECUTION_PENDING_INDEPENDENT_REVIEW", "D3H1 contract status drift")
    require(contract.get("run_id") == EXPECTED_RUN_ID and contract.get("run_payload_sha256") == EXPECTED_PAYLOAD_SHA256, "D3H1 contract run binding drift")
    require(contract.get("schedule_sha256") == EXPECTED_SCHEDULE_SHA256, "D3H1 contract schedule drift")
    require(contract.get("dependency_lock_sha256") == EXPECTED_DEPENDENCY_SHA256, "D3H1 contract dependency drift")
    require(contract["source_bindings"]["cp01r2_execution_target"]["git_blob_sha1"] == EXPECTED_TARGET_BLOB, "target binding drift")
    require(contract["source_bindings"]["cp01r2_result_schema"]["git_blob_sha1"] == EXPECTED_RESULT_SCHEMA_BLOB, "result-schema binding drift")
    require(contract["grant_protocol"]["maximum_validity_seconds"] == 3600, "grant validity contract drift")
    require(ISSUER_VALIDITY_SECONDS <= contract["grant_protocol"]["maximum_validity_seconds"], "issuer validity exceeds contract maximum")

    require(sha256_file(DEPENDENCY_PATH) == EXPECTED_DEPENDENCY_SHA256, "dependency-lock bytes drifted")

    preflight = supervisor.static_preflight()
    require(preflight.get("status") == "PASS_WP3_D3H1_CP01R2_TRANSACTION_STATIC_PREFLIGHT_NO_EXECUTION", "CP01R2 static preflight did not PASS")
    require(preflight.get("run_id") == EXPECTED_RUN_ID and preflight.get("run_payload_sha256") == EXPECTED_PAYLOAD_SHA256, "fresh preflight run binding mismatch")
    require(preflight.get("schedule_sha256") == EXPECTED_SCHEDULE_SHA256, "fresh preflight schedule mismatch")
    require(preflight.get("solver_calls") == 0 and preflight.get("physical_solve_executed") is False, "fresh preflight violated no-execution firewall")

    return {
        "status": "PASS_FRESH_RECHECK_ELIGIBLE_FOR_IMMEDIATE_CP01R2_ISSUANCE",
        "checked_out_git_head": git_head(),
        "github_run_id": os.environ.get("GITHUB_RUN_ID", "UNSET"),
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", "UNSET"),
        "run_id": EXPECTED_RUN_ID,
        "run_payload_sha256": EXPECTED_PAYLOAD_SHA256,
        "schedule_sha256": EXPECTED_SCHEDULE_SHA256,
        "planned_entry_count": EXPECTED_PLANNED_ENTRY_COUNT,
        "dependency_lock_sha256": EXPECTED_DEPENDENCY_SHA256,
        "transaction_contract_sha256": sha256_file(CONTRACT_PATH),
        "source_bundle_sha256": preflight["source_bundle_sha256"],
        "result_schema_git_blob_sha1": EXPECTED_RESULT_SCHEMA_BLOB,
        "target_git_blob_sha1": EXPECTED_TARGET_BLOB,
        "governance_release_decision_id": EXPECTED_D4_DECISION_ID,
        "execution_holder": EXPECTED_EXECUTION_HOLDER,
        "reproducibility_ticket_id": EXPECTED_REPRO_TICKET,
        "release_path_absent_before_issuance": True,
        "grant_path_absent_before_issuance": True,
        "solver_calls_during_recheck": 0,
        "physical_evidence_effect": "NONE",
    }


def issue(supervisor: Any, recheck: dict[str, Any]) -> dict[str, Any]:
    base = supervisor.BASE
    contract = load_json(CONTRACT_PATH)
    protocol = contract["grant_protocol"]
    now = datetime.now(timezone.utc).replace(microsecond=0)
    expires = now + timedelta(seconds=ISSUER_VALIDITY_SECONDS)
    github_run_id = os.environ.get("GITHUB_RUN_ID", "local")
    github_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    head = recheck["checked_out_git_head"]
    authorization_decision_id = f"UL-DEC-CP01R2-{github_run_id}-{github_attempt}"
    nonce_material = f"{github_run_id}:{github_attempt}:{head}:{utc_text(now)}:{recheck['source_bundle_sha256']}:{EXPECTED_D4_DECISION_ID}".encode("utf-8")
    nonce = hashlib.sha256(nonce_material).hexdigest()[:32]

    grant = {
        "schema": protocol["grant_schema"],
        "version": "1.0.0",
        "status": "GRANTED_SINGLE_USE_FOR_IMMEDIATE_CP01R2",
        "physical_solve_authorized": True,
        "run_id": EXPECTED_RUN_ID,
        "run_payload_sha256": EXPECTED_PAYLOAD_SHA256,
        "schedule_sha256": EXPECTED_SCHEDULE_SHA256,
        "planned_entry_count": EXPECTED_PLANNED_ENTRY_COUNT,
        "dependency_lock_sha256": EXPECTED_DEPENDENCY_SHA256,
        "result_schema_git_blob_sha1": EXPECTED_RESULT_SCHEMA_BLOB,
        "target_git_blob_sha1": EXPECTED_TARGET_BLOB,
        "transaction_contract_sha256": recheck["transaction_contract_sha256"],
        "source_bundle_sha256": recheck["source_bundle_sha256"],
        "authorization_decision_id": authorization_decision_id,
        "governance_release_decision_id": EXPECTED_D4_DECISION_ID,
        "grant_nonce": nonce,
        "issued_at": utc_text(now),
        "not_before": utc_text(now),
        "expires_at": utc_text(expires),
        "maximum_start_validity_seconds": ISSUER_VALIDITY_SECONDS,
        "single_use": True,
        "no_retry": True,
        "no_scan": True,
        "no_fallback": True,
        "no_parameter_or_topology_mutation": True,
        "parallel_execution_allowed": False,
        "method_or_threshold_relaxation_allowed": False,
        "random_restart_allowed": False,
        "adaptive_mesh_insertion_allowed": False,
        "independent_backend_required_after_primary_candidate": True,
        "replay_permitted": False,
        "execution_holder": EXPECTED_EXECUTION_HOLDER,
        "reproducibility_ticket_id": EXPECTED_REPRO_TICKET,
        "issued_from_git_head": head,
        "issued_from_github_run_id": github_run_id,
        "issued_from_github_run_attempt": github_attempt,
        "physical_evidence_effect": "NONE"
    }
    atomic_json(GRANT_PATH, grant)
    grant_sha = sha256_file(GRANT_PATH)

    release = {
        "schema": protocol["release_schema"],
        "version": "1.0.0",
        "status": "GRANTED",
        "physical_solve_authorized": True,
        "run_id": EXPECTED_RUN_ID,
        "run_payload_sha256": EXPECTED_PAYLOAD_SHA256,
        "schedule_sha256": EXPECTED_SCHEDULE_SHA256,
        "planned_entry_count": EXPECTED_PLANNED_ENTRY_COUNT,
        "dependency_lock_sha256": EXPECTED_DEPENDENCY_SHA256,
        "result_schema_git_blob_sha1": EXPECTED_RESULT_SCHEMA_BLOB,
        "target_git_blob_sha1": EXPECTED_TARGET_BLOB,
        "transaction_contract_sha256": recheck["transaction_contract_sha256"],
        "source_bundle_sha256": recheck["source_bundle_sha256"],
        "grant_sha256": grant_sha,
        "authorization_decision_id": authorization_decision_id,
        "governance_release_decision_id": EXPECTED_D4_DECISION_ID,
        "issued_at": utc_text(now),
        "grant_expires_at": utc_text(expires),
        "scope": "EXACT_CP01R2_SINGLE_USE_7_SEEDS_X_5_NODE_LEVELS_NO_SCAN_NO_FALLBACK_NO_MUTATION",
        "execution_holder": EXPECTED_EXECUTION_HOLDER,
        "reproducibility_ticket_id": EXPECTED_REPRO_TICKET,
        "issued_from_git_head": head,
        "issued_from_github_run_id": github_run_id,
        "issued_from_github_run_attempt": github_attempt,
        "physical_evidence_effect_before_separate_result_review": "NONE"
    }
    atomic_json(RELEASE_PATH, release)
    release_sha = sha256_file(RELEASE_PATH)

    validated_release, validated_grant, validated_release_sha, validated_grant_sha = base.validate_release_and_grant(now=datetime.now(timezone.utc))
    require(validated_release_sha == release_sha and validated_grant_sha == grant_sha, "runtime validator hash mismatch")
    require(validated_release.get("governance_release_decision_id") == EXPECTED_D4_DECISION_ID, "release lost D4 governance binding")
    require(validated_grant.get("governance_release_decision_id") == EXPECTED_D4_DECISION_ID, "grant lost D4 governance binding")
    require(validated_release.get("authorization_decision_id") == validated_grant.get("authorization_decision_id") == authorization_decision_id, "release/grant authorization-decision binding mismatch")

    return {
        "status": "PASS_EXACT_CP01R2_RELEASE_AND_FRESH_SINGLE_USE_GRANT_ISSUED_FOR_IMMEDIATE_EXECUTION",
        "run_id": EXPECTED_RUN_ID,
        "authorization_decision_id": authorization_decision_id,
        "governance_release_decision_id": EXPECTED_D4_DECISION_ID,
        "grant_nonce": nonce,
        "grant_sha256": grant_sha,
        "release_authorization_sha256": release_sha,
        "issued_at": utc_text(now),
        "not_before": utc_text(now),
        "expires_at": utc_text(expires),
        "checked_out_git_head": head,
        "schedule_sha256": EXPECTED_SCHEDULE_SHA256,
        "planned_entry_count": EXPECTED_PLANNED_ENTRY_COUNT,
        "execution_holder": EXPECTED_EXECUTION_HOLDER,
        "reproducibility_ticket_id": EXPECTED_REPRO_TICKET,
        "physical_solve_authorized": True,
        "physical_solve_executed_at_issuance": False,
        "next_action": "IMMEDIATELY_CALL_EXACT_CP01R2_TRANSACTION_V1_1_EXECUTE_ONCE",
        "replay_permitted": False,
        "physical_evidence_effect": "NONE"
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()
    try:
        supervisor = import_supervisor()
        recheck = fresh_recheck(supervisor)
        issuance = issue(supervisor, recheck)
        summary = {"fresh_recheck": recheck, "issuance": issuance}
        atomic_json(Path(args.summary), summary)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"ISSUANCE_FAILURE: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 78


if __name__ == "__main__":
    raise SystemExit(main())
