#!/usr/bin/env python3
"""ULSH-01 / WP3 CP01R1 immediate-transaction issuer v1.0.

This script performs the mandatory fresh pre-issuance recheck and only then
creates the exact H3 v1.3 release authorization and single-use execution grant
in the checked-out runtime workspace. It does not call the numerical solver.
The immediately following workflow step invokes the already RR4-reviewed H3
transaction supervisor v1.4 exactly once.
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
H3_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.4.py"
H3_CONTRACT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_H3Contract_v1.0.json"
RR4_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_RR4Review_v1.0.json"
WP3_DECISION_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP3_CP01R1ReleaseDecision_v1.0.json"
TRIGGER_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP3_CP01R1ImmediateExecutionTrigger_v1.0.json"
RELEASE_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.3.json"
GRANT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.3.json"

EXPECTED_RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
EXPECTED_PAYLOAD_SHA256 = "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302"
EXPECTED_H3_CONTRACT_BLOB = "a09067d749493fa14c61fc8a7678ca353a005566"
EXPECTED_H3_TRANSACTION_BLOB = "2dd09d9ade6d6ae69c1949833e88b2af49c13710"
EXPECTED_WP3_DECISION_BLOB = "e9fabf7387868784a1e168845113338c7fe05414"
EXPECTED_H3_SOURCE_BUNDLE_SHA256 = "022b1ede18d217c3278445ea1cfd65fad475d28a6ebaa7327cc9c46904c877cd"
EXPECTED_DEPENDENCY_LOCK_SHA256 = "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f"


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


def import_h3():
    spec = importlib.util.spec_from_file_location("ulsh_wp2_h3_runtime", H3_PATH)
    if spec is None or spec.loader is None:
        raise IssuanceFailure("cannot import exact H3 transaction supervisor")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise IssuanceFailure(f"cannot attest checked-out git HEAD: {exc}") from exc


def fresh_recheck(h3: Any) -> dict[str, Any]:
    if os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise IssuanceFailure("immediate physical transaction may run only from refs/heads/main")
    if RELEASE_PATH.exists() or GRANT_PATH.exists():
        raise IssuanceFailure("H3 v1.3 release/grant path already exists before issuance")

    decision = load_json(WP3_DECISION_PATH)
    rr4 = load_json(RR4_PATH)
    trigger = load_json(TRIGGER_PATH)
    contract = load_json(H3_CONTRACT_PATH)

    if git_blob_sha1(WP3_DECISION_PATH) != EXPECTED_WP3_DECISION_BLOB:
        raise IssuanceFailure("WP3 release-decision bytes drifted")
    if decision.get("decision_status") != "PASS_ELIGIBLE_FOR_EXACT_H3_SINGLE_USE_RELEASE_ISSUANCE_NO_EXECUTION":
        raise IssuanceFailure("WP3 release decision is not PASS")
    if decision.get("run_id") != EXPECTED_RUN_ID or decision.get("frozen_payload_sha256") != EXPECTED_PAYLOAD_SHA256:
        raise IssuanceFailure("WP3 run/payload binding drift")
    if rr4.get("review_status") != "PASS_WP2_RR4_H3_RELEASE_READINESS_VERIFIED_NO_SOLVE":
        raise IssuanceFailure("RR4 release-readiness review is not PASS")
    if rr4.get("new_release_blockers") != {}:
        raise IssuanceFailure("RR4 contains release blockers")
    if trigger.get("operator_intent") != "ISSUE_EXACT_H3_RELEASE_AND_SINGLE_USE_GRANT_AFTER_FRESH_RECHECK_THEN_START_CP01R1_IMMEDIATELY":
        raise IssuanceFailure("operator trigger does not authorize the exact immediate sequence")
    if trigger.get("run_id") != EXPECTED_RUN_ID or trigger.get("frozen_payload_sha256") != EXPECTED_PAYLOAD_SHA256:
        raise IssuanceFailure("operator trigger run/payload binding drift")

    if git_blob_sha1(H3_CONTRACT_PATH) != EXPECTED_H3_CONTRACT_BLOB:
        raise IssuanceFailure("H3 contract git blob drift")
    if git_blob_sha1(H3_PATH) != EXPECTED_H3_TRANSACTION_BLOB:
        raise IssuanceFailure("H3 transaction git blob drift")
    if decision["h3_basis"]["contract_git_blob_sha1"] != EXPECTED_H3_CONTRACT_BLOB:
        raise IssuanceFailure("WP3 H3 contract binding drift")
    if decision["h3_basis"]["transaction_git_blob_sha1"] != EXPECTED_H3_TRANSACTION_BLOB:
        raise IssuanceFailure("WP3 H3 transaction binding drift")

    preflight = h3.static_preflight()
    if preflight.get("run_id") != EXPECTED_RUN_ID or preflight.get("frozen_payload_sha256") != EXPECTED_PAYLOAD_SHA256:
        raise IssuanceFailure("fresh H3 preflight run/payload mismatch")
    if preflight.get("planned_entry_count") != 35:
        raise IssuanceFailure("fresh H3 preflight is not the frozen 35-entry schedule")
    if preflight.get("h3_source_bundle_sha256") != EXPECTED_H3_SOURCE_BUNDLE_SHA256:
        raise IssuanceFailure("fresh H3 source-bundle digest drift")
    if decision["h3_basis"]["source_bundle_sha256"] != EXPECTED_H3_SOURCE_BUNDLE_SHA256:
        raise IssuanceFailure("WP3 source-bundle binding drift")
    if h3.DEPENDENCY_LOCK_SHA256 != EXPECTED_DEPENDENCY_LOCK_SHA256:
        raise IssuanceFailure("dependency-lock constant drift")

    binding = contract["source_bindings"]["dependency_lock"]
    dependency_path = ROOT / binding["path"]
    if sha256_file(dependency_path) != EXPECTED_DEPENDENCY_LOCK_SHA256:
        raise IssuanceFailure("dependency-lock bytes drift")

    return {
        "status": "PASS_FRESH_RECHECK_ELIGIBLE_FOR_IMMEDIATE_H3_ISSUANCE",
        "checked_out_git_head": git_head(),
        "github_run_id": os.environ.get("GITHUB_RUN_ID", "UNSET"),
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", "UNSET"),
        "run_id": EXPECTED_RUN_ID,
        "frozen_payload_sha256": EXPECTED_PAYLOAD_SHA256,
        "schedule_sha256": preflight["schedule_sha256"],
        "planned_entry_count": preflight["planned_entry_count"],
        "h3_contract_sha256": sha256_file(H3_CONTRACT_PATH),
        "h3_source_bundle_sha256": preflight["h3_source_bundle_sha256"],
        "dependency_lock_sha256": EXPECTED_DEPENDENCY_LOCK_SHA256,
        "resource_policy_git_blob_sha1": contract["source_bindings"]["resource_policy"]["git_blob_sha1"],
        "result_schema_git_blob_sha1": contract["source_bindings"]["result_schema"]["git_blob_sha1"],
        "release_path_absent_before_issuance": True,
        "grant_path_absent_before_issuance": True,
        "solver_calls_during_recheck": 0,
        "physical_evidence_effect": "NONE",
    }


def issue(h3: Any, recheck: dict[str, Any]) -> dict[str, Any]:
    contract = load_json(H3_CONTRACT_PATH)
    protocol = contract["grant_protocol"]
    now = datetime.now(timezone.utc).replace(microsecond=0)
    expires = now + timedelta(seconds=3300)
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    head = recheck["checked_out_git_head"]
    decision_id = f"UL-DEC-CP01R1-{run_id}-{attempt}"
    nonce_material = f"{run_id}:{attempt}:{head}:{utc_text(now)}:{recheck['h3_source_bundle_sha256']}".encode("utf-8")
    nonce = hashlib.sha256(nonce_material).hexdigest()[:32]

    grant = {
        "schema": protocol["grant_schema"],
        "version": "1.3.0",
        "status": "GRANTED_SINGLE_USE_FOR_IMMEDIATE_CP01R1",
        "run_id": EXPECTED_RUN_ID,
        "frozen_payload_sha256": EXPECTED_PAYLOAD_SHA256,
        "transaction_contract_sha256": recheck["h3_contract_sha256"],
        "source_bundle_sha256": recheck["h3_source_bundle_sha256"],
        "schedule_sha256": recheck["schedule_sha256"],
        "planned_entry_count": 35,
        "dependency_lock_sha256": EXPECTED_DEPENDENCY_LOCK_SHA256,
        "resource_policy_git_blob_sha1": recheck["resource_policy_git_blob_sha1"],
        "result_schema_git_blob_sha1": recheck["result_schema_git_blob_sha1"],
        "authorization_decision_id": decision_id,
        "grant_nonce": nonce,
        "issued_at": utc_text(now),
        "not_before": utc_text(now),
        "expires_at": utc_text(expires),
        "maximum_start_validity_seconds": 3300,
        "single_use": True,
        "physical_solve_authorized": True,
        "no_retry": True,
        "no_scan": True,
        "no_fallback": True,
        "parameter_mutation_allowed": False,
        "topology_mutation_allowed": False,
        "random_restart_allowed": False,
        "adaptive_mesh_insertion_allowed": False,
        "independent_backend_required_after_primary_candidate": True,
        "issued_from_git_head": head,
        "issued_from_github_run_id": run_id,
        "physical_evidence_effect": "NONE",
    }
    atomic_json(GRANT_PATH, grant)
    grant_sha = sha256_file(GRANT_PATH)

    release = {
        "schema": protocol["release_schema"],
        "version": "1.3.0",
        "status": "GRANTED",
        "physical_solve_authorized": True,
        "run_id": EXPECTED_RUN_ID,
        "frozen_payload_sha256": EXPECTED_PAYLOAD_SHA256,
        "transaction_contract_sha256": recheck["h3_contract_sha256"],
        "source_bundle_sha256": recheck["h3_source_bundle_sha256"],
        "grant_sha256": grant_sha,
        "authorization_decision_id": decision_id,
        "issued_at": utc_text(now),
        "grant_expires_at": utc_text(expires),
        "scope": "EXACT_H3_SINGLE_USE_CP01R1_7_SEEDS_X_5_NODE_LEVELS_NO_SCAN_NO_FALLBACK",
        "issued_from_git_head": head,
        "issued_from_github_run_id": run_id,
        "physical_evidence_effect_before_execution": "NONE",
    }
    atomic_json(RELEASE_PATH, release)
    release_sha = sha256_file(RELEASE_PATH)

    # Re-parse and validate the exact bytes the H3 transaction will consume.
    h3.validate_h3_release_and_grant(now=datetime.now(timezone.utc))
    return {
        "status": "PASS_EXACT_H3_RELEASE_AND_SINGLE_USE_GRANT_ISSUED_FOR_IMMEDIATE_EXECUTION",
        "run_id": EXPECTED_RUN_ID,
        "authorization_decision_id": decision_id,
        "grant_nonce": nonce,
        "grant_sha256": grant_sha,
        "release_authorization_sha256": release_sha,
        "issued_at": utc_text(now),
        "not_before": utc_text(now),
        "expires_at": utc_text(expires),
        "checked_out_git_head": head,
        "schedule_sha256": recheck["schedule_sha256"],
        "planned_entry_count": 35,
        "physical_solve_authorized": True,
        "physical_solve_executed_at_issuance": False,
        "next_action": "IMMEDIATELY_CALL_EXACT_H3_TRANSACTION_V1_4_EXECUTE_ONCE",
        "replay_permitted": False,
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()
    try:
        h3 = import_h3()
        recheck = fresh_recheck(h3)
        issuance = issue(h3, recheck)
        summary = {"fresh_recheck": recheck, "issuance": issuance}
        atomic_json(Path(args.summary), summary)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"ISSUANCE_FAILURE: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 78


if __name__ == "__main__":
    raise SystemExit(main())
