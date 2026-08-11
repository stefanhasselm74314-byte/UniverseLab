#!/usr/bin/env python3
"""ULSH-01 / WP2-H3 transaction supervisor v1.4.

Closes RR3-B01 and RR3-B02 without executing CP01R1. Audit is the default path.
Physical execute remains impossible unless a later, separately reviewed exact H3
release authorization and single-use grant are present.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
import re
import sys
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.3.py"
CONTRACT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_H3Contract_v1.0.json"
RR3_REVIEW_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_RR3Review_v1.0.json"
RELEASE_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.3.json"
GRANT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.3.json"

_SPEC = importlib.util.spec_from_file_location("ulsh_wp2_h2_tx_v13", BASE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("unable to import WP2-H2 transaction v1.3")
H2 = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = H2
_SPEC.loader.exec_module(H2)

RUN_ID = H2.RUN_ID
FROZEN_PAYLOAD_SHA256 = H2.FROZEN_PAYLOAD_SHA256
DEPENDENCY_LOCK_SHA256 = H2.DEPENDENCY_LOCK_SHA256
RESOURCE_POLICY_PATH = H2.RESOURCE_POLICY_PATH
UTILS = H2.UTILS
H1 = H2.H1

AuthorizationDenied = H2.AuthorizationDenied
ContractFailure = H2.ContractFailure
ResourceFailure = H2.ResourceFailure
ExecutionFailure = H2.ExecutionFailure
NONCE_RE = re.compile(r"^[0-9a-f]{32,64}$")


def load_json(path: Path) -> dict[str, Any]:
    return H2.load_json(path)


def sha256_file(path: Path) -> str:
    return H2.sha256_file(path)


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _walk_nonfinite(value: Any, path: str = "$") -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if isinstance(value, float) and not math.isfinite(value):
        findings.append({"path": path, "kind": "positive_infinity" if value > 0 else "negative_infinity" if value < 0 else "nan"})
    elif isinstance(value, dict):
        for key, item in value.items():
            findings.extend(_walk_nonfinite(item, f"{path}.{key}"))
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            findings.extend(_walk_nonfinite(item, f"{path}[{index}]"))
    return findings


def json_safe_diagnostic_projection(value: Any, path: str = "$") -> tuple[Any, list[dict[str, str]]]:
    """Replace only nonfinite diagnostic sentinels with null and record every path.

    Missing/nonfinite information remains missing; it is never converted into a
    finite measurement or acceptance value.
    """
    replacements: list[dict[str, str]] = []
    if isinstance(value, float) and not math.isfinite(value):
        kind = "positive_infinity" if value > 0 else "negative_infinity" if value < 0 else "nan"
        replacements.append({"path": path, "original_nonfinite_kind": kind, "replacement": "null", "reason": "JSON_SAFE_MISSING_OR_UNBOUNDED_DIAGNOSTIC_NOT_A_FINITE_MEASUREMENT"})
        return None, replacements
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            projected, found = json_safe_diagnostic_projection(item, f"{path}.{key}")
            out[key] = projected
            replacements.extend(found)
        return out, replacements
    if isinstance(value, list):
        out_list: list[Any] = []
        for index, item in enumerate(value):
            projected, found = json_safe_diagnostic_projection(item, f"{path}[{index}]")
            out_list.append(projected)
            replacements.extend(found)
        return out_list, replacements
    if isinstance(value, tuple):
        out_tuple: list[Any] = []
        for index, item in enumerate(value):
            projected, found = json_safe_diagnostic_projection(item, f"{path}[{index}]")
            out_tuple.append(projected)
            replacements.extend(found)
        return out_tuple, replacements
    return value, replacements


def sanitize_raw_result_for_immutable_json(raw_result: dict[str, Any]) -> dict[str, Any]:
    projected, replacements = json_safe_diagnostic_projection(raw_result)
    if not isinstance(projected, dict):
        raise ContractFailure("sanitized target result must remain a mapping")
    acceptance = projected.setdefault("acceptance_audit", {})
    if not isinstance(acceptance, dict):
        raise ContractFailure("acceptance_audit must remain a mapping")
    acceptance["json_safe_nonfinite_replacements"] = replacements
    acceptance["json_safe_nonfinite_policy"] = "NONFINITE_DIAGNOSTIC_SENTINEL_TO_NULL_PLUS_EXPLICIT_PATH_REASON_NEVER_TO_FINITE_MEASUREMENT"
    remaining = _walk_nonfinite(projected)
    if remaining:
        raise ContractFailure(f"nonfinite values remain after JSON-safe projection: {remaining}")
    json.dumps(projected, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return projected


def inspect_committed_result(result_dir: Path, expected_package: dict[str, Any] | None) -> dict[str, Any]:
    present = result_dir.is_dir()
    audit: dict[str, Any] = {"result_package_committed": present, "result_directory": str(result_dir)}
    if not present:
        audit.update({"verification_status": "NOT_COMMITTED", "result_sha256": None, "artifact_manifest_sha256": None})
        return audit
    result_path = result_dir / "result.json"
    manifest_path = result_dir / "artifact-manifest.json"
    if not result_path.is_file() or not manifest_path.is_file():
        audit.update({"verification_status": "COMMITTED_DIRECTORY_INCOMPLETE", "result_sha256": None, "artifact_manifest_sha256": None})
        return audit
    result_sha = sha256_file(result_path)
    manifest_sha = sha256_file(manifest_path)
    audit.update({"result_sha256": result_sha, "artifact_manifest_sha256": manifest_sha})
    if expected_package is None:
        audit["verification_status"] = "COMMITTED_PRESENT_EXPECTATION_UNAVAILABLE"
    elif result_sha == expected_package.get("result_sha256") and manifest_sha == expected_package.get("artifact_manifest_sha256"):
        audit["verification_status"] = "COMMITTED_HASHES_MATCH_PRECOMMIT_PACKAGE"
    else:
        audit["verification_status"] = "COMMITTED_HASH_MISMATCH_INDETERMINATE"
    return audit


def _parse_utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AuthorizationDenied(f"invalid UTC timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise AuthorizationDenied("grant timestamps must include timezone")
    return parsed.astimezone(timezone.utc)


def source_bundle_sha256(contract: dict[str, Any]) -> str:
    bindings = contract.get("source_bindings", {})
    material: list[dict[str, str]] = []
    for key in sorted(bindings):
        binding = bindings[key]
        path = ROOT / binding["path"]
        observed = git_blob_sha1(path)
        if observed != binding["git_blob_sha1"]:
            raise ContractFailure(f"H3 source binding drift for {key}: {observed}")
        material.append({"key": key, "path": binding["path"], "git_blob_sha1": observed})
    payload = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_h3_release_and_grant(now: datetime | None = None) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    if not RELEASE_PATH.is_file() or not GRANT_PATH.is_file():
        raise AuthorizationDenied("WP2-H3 exact release authorization and/or single-use grant is absent")
    contract = load_json(CONTRACT_PATH)
    release = load_json(RELEASE_PATH)
    grant = load_json(GRANT_PATH)
    protocol = contract["grant_protocol"]
    grant_sha = sha256_file(GRANT_PATH)
    release_sha = sha256_file(RELEASE_PATH)
    contract_sha = sha256_file(CONTRACT_PATH)
    bundle_sha = source_bundle_sha256(contract)
    schedule_sha = H2.static_preflight()["schedule_sha256"]
    if release.get("schema") != protocol["release_schema"] or release.get("status") != "GRANTED" or release.get("physical_solve_authorized") is not True:
        raise AuthorizationDenied("H3 release authorization is not an exact GRANTED release")
    if release.get("run_id") != RUN_ID or release.get("frozen_payload_sha256") != FROZEN_PAYLOAD_SHA256:
        raise AuthorizationDenied("H3 release run binding mismatch")
    if release.get("grant_sha256") != grant_sha or release.get("transaction_contract_sha256") != contract_sha or release.get("source_bundle_sha256") != bundle_sha:
        raise AuthorizationDenied("H3 release exact binding mismatch")
    if grant.get("schema") != protocol["grant_schema"]:
        raise AuthorizationDenied("unexpected H3 grant schema")
    for key in ("single_use", "physical_solve_authorized", "no_retry", "no_scan", "no_fallback"):
        if grant.get(key) is not True:
            raise AuthorizationDenied(f"H3 grant scope flag missing: {key}")
    if grant.get("run_id") != RUN_ID or grant.get("frozen_payload_sha256") != FROZEN_PAYLOAD_SHA256:
        raise AuthorizationDenied("H3 grant run binding mismatch")
    if grant.get("transaction_contract_sha256") != contract_sha or grant.get("source_bundle_sha256") != bundle_sha:
        raise AuthorizationDenied("H3 grant exact source/contract binding mismatch")
    if grant.get("schedule_sha256") != schedule_sha or grant.get("planned_entry_count") != 35:
        raise AuthorizationDenied("H3 grant schedule binding mismatch")
    if grant.get("dependency_lock_sha256") != DEPENDENCY_LOCK_SHA256:
        raise AuthorizationDenied("H3 grant dependency binding mismatch")
    if grant.get("resource_policy_git_blob_sha1") != contract["source_bindings"]["resource_policy"]["git_blob_sha1"]:
        raise AuthorizationDenied("H3 grant resource-policy binding mismatch")
    if grant.get("result_schema_git_blob_sha1") != contract["source_bindings"]["result_schema"]["git_blob_sha1"]:
        raise AuthorizationDenied("H3 grant result-schema binding mismatch")
    if not str(grant.get("authorization_decision_id", "")).startswith("UL-DEC-"):
        raise AuthorizationDenied("H3 authorization_decision_id invalid")
    nonce = str(grant.get("grant_nonce", ""))
    if not NONCE_RE.fullmatch(nonce):
        raise AuthorizationDenied("H3 grant nonce must be 128-256 bits lowercase hex")
    issued = _parse_utc(str(grant.get("issued_at", "")))
    not_before = _parse_utc(str(grant.get("not_before", "")))
    expires = _parse_utc(str(grant.get("expires_at", "")))
    clock = now or datetime.now(timezone.utc)
    if not (issued <= not_before < expires):
        raise AuthorizationDenied("invalid H3 grant time ordering")
    if (expires - not_before).total_seconds() > int(protocol["maximum_validity_seconds"]):
        raise AuthorizationDenied("H3 grant validity window exceeds contract maximum")
    if clock < not_before or clock >= expires:
        raise AuthorizationDenied("H3 grant outside validity window")
    return release, grant, release_sha, grant_sha


def static_preflight() -> dict[str, Any]:
    base = H2.static_preflight()
    if RELEASE_PATH.exists() or GRANT_PATH.exists():
        raise ContractFailure("H3 implementation/audit phase requires release and grant to remain absent")
    rr3 = load_json(RR3_REVIEW_PATH)
    contract = load_json(CONTRACT_PATH)
    if rr3.get("review_status") != "BLOCKED_WP2_RR3_NEW_RELEASE_BLOCKERS_FOUND_NO_SOLVE":
        raise ContractFailure("unexpected RR3 review basis")
    if contract.get("status") != "PASS_WP2_H3_IMPLEMENTED_NO_SOLVE_PENDING_RR4":
        raise ContractFailure("unexpected H3 contract status")
    bundle = source_bundle_sha256(contract)
    base.update({
        "status": "PASS_WP2_H3_STATIC_PREFLIGHT_NO_SOLVE_PENDING_RR4",
        "h3_source_bundle_sha256": bundle,
        "RR3-B01": "IMPLEMENTED_PENDING_RR4",
        "RR3-B02": "IMPLEMENTED_PENDING_RR4",
        "solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
    })
    return base


def execute(transaction_root: Path) -> dict[str, Any]:
    # This path is unreachable until a later exact H3 release+grant exists.
    preflight = H2.static_preflight()
    release, grant, release_sha, grant_sha = validate_h3_release_and_grant()
    external_root = UTILS.ensure_external_transaction_root(transaction_root)
    result_dir, staging = H2.BASE.pre_solver_output_collision_guard(external_root, grant)
    H2.BASE.strict_startup_environment()
    H1.enforce_process_limits()
    runtime = H1.validate_runtime()
    runtime["effective_blas_threads"] = H2.effective_blas_thread_attestation()
    grant_dir = UTILS.claim_single_use_grant(external_root, grant, grant_sha)
    UTILS.mark_state(grant_dir, "RUNNING", release_authorization_sha256=release_sha)
    contract_sha = sha256_file(CONTRACT_PATH)
    limits = load_json(RESOURCE_POLICY_PATH)["resource_limits"]
    capability = {
        "run_id": RUN_ID,
        "frozen_payload_sha256": FROZEN_PAYLOAD_SHA256,
        "schedule_sha256": preflight["schedule_sha256"],
        "grant_sha256": grant_sha,
        "transaction_contract_sha256": contract_sha,
        "release_authorization_sha256": release_sha,
        "physical_solve_authorized": True,
        "maximum_wall_clock_seconds_total": int(limits["maximum_wall_clock_seconds_total"]),
        "maximum_wall_clock_seconds_per_seed_per_level": int(limits["maximum_wall_clock_seconds_per_seed_per_level"]),
    }
    package: dict[str, Any] | None = None
    supervised_elapsed: float | None = None
    try:
        with H2.total_transaction_wall_clock_limit(float(limits["maximum_wall_clock_seconds_total"])):
            raw_result, supervised_elapsed = H2.supervised_target_execution(capability, grant_dir, int(limits["maximum_wall_clock_seconds_total"]))
            safe_result = sanitize_raw_result_for_immutable_json(raw_result)
            package = H1.package_schema_complete_result(staging, safe_result, runtime, grant, release_sha, grant_sha, int(limits["maximum_result_bytes"]))
            result_dir.parent.mkdir(parents=True, exist_ok=True)
            UTILS.mark_state(grant_dir, "COMMITTING_RESULT", expected_result_directory=str(result_dir), expected_result_sha256=package["result_sha256"], expected_artifact_manifest_sha256=package["artifact_manifest_sha256"], replay_permitted=False)
            os.replace(staging, result_dir)
            UTILS._fsync_directory(result_dir.parent)
            commit_marker = {
                "schema": "universelab.ulsh-01.wp2-h3.result-commit-marker.v1",
                "run_id": RUN_ID,
                "result_directory": str(result_dir),
                "result_sha256": package["result_sha256"],
                "artifact_manifest_sha256": package["artifact_manifest_sha256"],
                "created_utc": H1.utc_now(),
                "replay_permitted": False,
                "physical_evidence_effect": "NONE",
            }
            UTILS.atomic_json(grant_dir / "result-commit.json", commit_marker)
            UTILS.mark_state(grant_dir, "SUCCEEDED", result_directory=str(result_dir), result_sha256=package["result_sha256"], final_classification=package["final_classification"], replay_permitted=False)
        return {"status": "PHYSICAL_TRANSACTION_COMPLETED_SCHEMA_COMPLETE_RESULT_QUARANTINED_H3_V14", "run_id": RUN_ID, "result_directory": str(result_dir), "result_sha256": package["result_sha256"] if package else None, "final_classification": package["final_classification"] if package else None, "supervised_target_elapsed_wall_clock_seconds": supervised_elapsed, "grant_spent": True, "replay_permitted": False, "physical_evidence_effect": "NONE"}
    except BaseException as exc:
        commit_audit = inspect_committed_result(result_dir, package)
        committed = bool(commit_audit["result_package_committed"])
        durable_state = "COMMITTED_INDETERMINATE" if committed else ("FAILED" if isinstance(exc, Exception) else "CRASHED_OR_INDETERMINATE")
        failure = {
            "schema": "universelab.ulsh-01.wp2-h3-v14.failure-record.v1",
            "run_id": RUN_ID,
            "created_utc": H1.utc_now(),
            "error_type": type(exc).__name__,
            "error": str(exc),
            "commit_audit": commit_audit,
            "result_package_committed": committed,
            "grant_spent": True,
            "replay_permitted": False,
            "retry_requires_new_grant": True,
            "physical_evidence_effect": "NONE",
        }
        UTILS.atomic_json(grant_dir / "failure.json", failure)
        UTILS.mark_state(grant_dir, durable_state, error_type=type(exc).__name__, result_package_committed=committed, commit_verification_status=commit_audit["verification_status"], replay_permitted=False, retry_requires_new_grant=True)
        raise


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("audit")
    run = sub.add_parser("execute")
    run.add_argument("--transaction-root", required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "audit":
            print(json.dumps(static_preflight(), indent=2, sort_keys=True))
            return 0
        if args.command == "execute":
            print(json.dumps(execute(Path(args.transaction_root)), indent=2, sort_keys=True))
            return 0
    except AuthorizationDenied as exc:
        print(f"NOT_AUTHORIZED: {exc}", file=sys.stderr)
        return H2.BASE.EXIT_NOT_AUTHORIZED
    except ContractFailure as exc:
        print(f"CONTRACT_FAILURE: {exc}", file=sys.stderr)
        return H2.BASE.EXIT_CONTRACT_FAILURE
    except ResourceFailure as exc:
        print(f"RESOURCE_FAILURE: {exc}", file=sys.stderr)
        return H2.BASE.EXIT_RESOURCE_FAILURE
    except UTILS.ReplayOrCrash as exc:
        print(f"REPLAY_OR_CRASH: {exc}", file=sys.stderr)
        return H2.BASE.EXIT_REPLAY_OR_CRASH
    except Exception as exc:
        print(f"EXECUTION_FAILURE: {type(exc).__name__}: {exc}", file=sys.stderr)
        return H2.BASE.EXIT_EXECUTION_FAILURE
    return H2.BASE.EXIT_EXECUTION_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
