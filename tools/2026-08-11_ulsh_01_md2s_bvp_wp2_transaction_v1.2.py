#!/usr/bin/env python3
"""ULSH-01 / WP2-H2 hardened physical transaction v1.2.

Closes RR2-B01..RR2-B03 at the transaction boundary while preserving the
release/grant/no-solve firewall. RR2-B04 is implemented in target v1.2.

Audit and CI do not create a release authorization, do not create a grant, do
not import numerical backends and do not execute CP01R1.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import multiprocessing as mp
import os
from pathlib import Path
import pickle
import re
import sys
import time
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
FROZEN_PAYLOAD_SHA256 = "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302"
DEPENDENCY_LOCK_SHA256 = "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f"
EXIT_NOT_AUTHORIZED = 73
EXIT_CONTRACT_FAILURE = 74
EXIT_RESOURCE_FAILURE = 75
EXIT_REPLAY_OR_CRASH = 76
EXIT_EXECUTION_FAILURE = 77

H1_TRANSACTION_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.1.py"
TARGET_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.2.py"
CONTRACT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_H2Contract_v1.0.json"
RESOURCE_POLICY_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
DEPENDENCY_LOCK_PATH = ROOT / "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C_v0.1.txt"

RELEASE_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.2.json"
GRANT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.2.json"

THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
)
NONCE_RE = re.compile(r"^[0-9a-f]{32,64}$")

_SPEC = importlib.util.spec_from_file_location("ulsh_wp2_h1_transaction", H1_TRANSACTION_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("unable to import WP2-H v1.1 transaction utilities")
H1 = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = H1
_SPEC.loader.exec_module(H1)
UTILS = H1.BASE
H1.CONTRACT_PATH = CONTRACT_PATH


class H2TransactionError(RuntimeError):
    pass


class AuthorizationDenied(H2TransactionError):
    pass


class ContractFailure(H2TransactionError):
    pass


class ResourceFailure(H2TransactionError):
    pass


class ExecutionFailure(H2TransactionError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return H1.sha256_file(path)


def git_blob_sha1(path: Path) -> str:
    return H1.git_blob_sha1(path)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractFailure(f"missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractFailure(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ContractFailure(f"top-level JSON object required: {path}")
    return value


def _dynamic_import(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ContractFailure(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_target_audit_module():
    return _dynamic_import(TARGET_PATH, "ulsh_wp2_h2_target_audit")


def source_bundle_sha256(contract: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(contract["source_bindings"]))


def verify_source_bindings(contract: dict[str, Any]) -> dict[str, str]:
    observed: dict[str, str] = {}
    for key, binding in contract["source_bindings"].items():
        path = ROOT / str(binding["path"])
        actual = git_blob_sha1(path)
        expected = str(binding["git_blob_sha1"])
        if actual != expected:
            raise ContractFailure(f"source binding drift for {key}: {actual} != {expected}")
        observed[key] = actual
    return observed


def static_preflight() -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    if contract.get("status") != "PASS_WP2_H2_IMPLEMENTED_NO_SOLVE_PENDING_RR3":
        raise ContractFailure("WP2-H2 contract status drift")
    if contract.get("run_id") != RUN_ID or contract.get("frozen_payload_sha256") != FROZEN_PAYLOAD_SHA256:
        raise ContractFailure("WP2-H2 run binding drift")
    if contract.get("physical_solve_authorized") is not False or contract.get("physical_solve_executed") is not False:
        raise ContractFailure("WP2-H2 must remain unreleased and no-solve")
    closures = contract.get("rr2_blocker_closure", {})
    if set(closures) != {"RR2-B01", "RR2-B02", "RR2-B03", "RR2-B04"}:
        raise ContractFailure("WP2-H2 RR2 blocker inventory drift")
    if any(item.get("status") != "IMPLEMENTED_PENDING_RR3" for item in closures.values()):
        raise ContractFailure("all RR2 closures must remain pending independent RR3")
    observed = verify_source_bindings(contract)
    if sha256_file(DEPENDENCY_LOCK_PATH) != DEPENDENCY_LOCK_SHA256:
        raise ContractFailure("frozen dependency lock SHA-256 drift")
    target = load_target_audit_module()
    audit = target.audit_target()
    if audit.get("status") != "PASS_WP2_H2_TARGET_HARDENING_NO_SOLVE":
        raise ContractFailure("WP2-H2 target audit failed")
    if audit.get("solver_calls") != 0 or audit.get("physical_solve_executed") is not False:
        raise ContractFailure("WP2-H2 audit crossed solver firewall")
    return {
        "status": "PASS_WP2_H2_STATIC_PREFLIGHT_NO_SOLVE",
        "run_id": RUN_ID,
        "frozen_payload_sha256": FROZEN_PAYLOAD_SHA256,
        "schedule_sha256": audit["schedule_sha256"],
        "planned_entry_count": audit["planned_entry_count"],
        "source_git_blob_sha1": observed,
        "source_bundle_sha256": source_bundle_sha256(contract),
        "release_authorization_present": RELEASE_PATH.exists(),
        "single_use_grant_present": GRANT_PATH.exists(),
        "rr2_blockers_implemented": sorted(closures),
        "strict_thread_startup_required": True,
        "pre_solver_output_collision_guard": True,
        "process_total_wall_clock_supervisor": True,
        "higher_precision_gate_in_target": True,
        "solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
    }


def strict_startup_environment() -> dict[str, str]:
    observed = {key: os.environ.get(key, "UNSET") for key in THREAD_ENV_KEYS}
    bad = {key: value for key, value in observed.items() if value != "1"}
    if bad:
        raise ResourceFailure(f"thread controls must be exactly 1 before NumPy/SciPy import: {bad}")
    if os.environ.get("PYTHONHASHSEED", "UNSET") != "0":
        raise ResourceFailure("PYTHONHASHSEED must be exactly 0 at process startup")
    return observed


def _parse_utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AuthorizationDenied(f"invalid UTC timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise AuthorizationDenied("grant timestamps must include timezone")
    return parsed.astimezone(timezone.utc)


def validate_release_and_grant(now: datetime | None = None) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    if not RELEASE_PATH.is_file() or not GRANT_PATH.is_file():
        raise AuthorizationDenied("WP2-H2 v1.2 release authorization and/or single-use grant is absent")
    contract = load_json(CONTRACT_PATH)
    release = load_json(RELEASE_PATH)
    grant = load_json(GRANT_PATH)
    grant_sha = sha256_file(GRANT_PATH)
    release_sha = sha256_file(RELEASE_PATH)
    contract_sha = sha256_file(CONTRACT_PATH)
    source_bundle = source_bundle_sha256(contract)
    target = load_target_audit_module()
    schedule_digest = target.schedule_sha256()
    protocol = contract["grant_protocol"]
    if release.get("schema") != protocol["release_schema"] or release.get("status") != "GRANTED" or release.get("physical_solve_authorized") is not True:
        raise AuthorizationDenied("physical solve release is not a valid H2 GRANTED authorization")
    if release.get("run_id") != RUN_ID or release.get("frozen_payload_sha256") != FROZEN_PAYLOAD_SHA256:
        raise AuthorizationDenied("release is bound to another run")
    if release.get("grant_sha256") != grant_sha or release.get("transaction_contract_sha256") != contract_sha or release.get("source_bundle_sha256") != source_bundle:
        raise AuthorizationDenied("release source/grant/contract binding mismatch")
    if grant.get("schema") != protocol["grant_schema"]:
        raise AuthorizationDenied("unexpected H2 grant schema")
    for key in ("single_use", "physical_solve_authorized", "no_retry", "no_scan", "no_fallback"):
        if grant.get(key) is not True:
            raise AuthorizationDenied(f"grant scope flag missing: {key}")
    if grant.get("run_id") != RUN_ID or grant.get("frozen_payload_sha256") != FROZEN_PAYLOAD_SHA256:
        raise AuthorizationDenied("grant is bound to another run")
    if grant.get("transaction_contract_sha256") != contract_sha or grant.get("source_bundle_sha256") != source_bundle:
        raise AuthorizationDenied("grant contract/source binding mismatch")
    if grant.get("schedule_sha256") != schedule_digest or grant.get("planned_entry_count") != 35:
        raise AuthorizationDenied("grant schedule binding mismatch")
    if grant.get("dependency_lock_sha256") != DEPENDENCY_LOCK_SHA256:
        raise AuthorizationDenied("grant dependency binding mismatch")
    decision_id = str(grant.get("authorization_decision_id", ""))
    if not decision_id.startswith("UL-DEC-"):
        raise AuthorizationDenied("invalid authorization_decision_id")
    nonce = str(grant.get("grant_nonce", ""))
    if not NONCE_RE.fullmatch(nonce):
        raise AuthorizationDenied("grant nonce must be 128-256 bits lowercase hex")
    clock = now or datetime.now(timezone.utc)
    issued_at = _parse_utc(str(grant.get("issued_at", "")))
    not_before = _parse_utc(str(grant.get("not_before", "")))
    expires_at = _parse_utc(str(grant.get("expires_at", "")))
    if not (issued_at <= not_before < expires_at):
        raise AuthorizationDenied("invalid grant time ordering")
    if (expires_at - not_before).total_seconds() > int(protocol["maximum_validity_seconds"]):
        raise AuthorizationDenied("grant validity exceeds contract maximum")
    if clock < not_before or clock >= expires_at:
        raise AuthorizationDenied("grant outside validity window")
    return release, grant, release_sha, grant_sha


def pre_solver_output_collision_guard(external_root: Path, grant: dict[str, Any]) -> tuple[Path, Path]:
    nonce = str(grant["grant_nonce"])
    results_root = external_root / "results"
    result_dir = results_root / nonce
    staging = results_root / f".{nonce}.staging-{os.getpid()}"
    if result_dir.exists():
        raise ExecutionFailure("immutable result directory already exists; abort before solver initialization")
    stale = list(results_root.glob(f".{nonce}.staging-*")) if results_root.exists() else []
    if stale:
        raise ExecutionFailure(f"stale staging path for grant nonce exists; abort before solver initialization: {stale}")
    return result_dir, staging


def _target_child(capability_dict: dict[str, Any], raw_path_text: str, error_path_text: str) -> None:
    raw_path = Path(raw_path_text)
    error_path = Path(error_path_text)
    try:
        target = _dynamic_import(TARGET_PATH, "ulsh_wp2_h2_target_child")
        capability = target.TargetExecutionCapability(**capability_dict)
        with H1.network_denied():
            raw = target.execute_physical_schedule(capability)
        with raw_path.open("xb") as stream:
            pickle.dump(raw, stream, protocol=pickle.HIGHEST_PROTOCOL)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException as exc:
        payload = {"error_type": type(exc).__name__, "error": str(exc)}
        try:
            error_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        finally:
            raise


def supervised_target_execution(capability_dict: dict[str, Any], grant_dir: Path, total_seconds: int) -> tuple[dict[str, Any], float]:
    if total_seconds <= 0:
        raise ResourceFailure("total wall-clock budget must be positive")
    raw_path = grant_dir / "h2-raw-target-result.pickle"
    error_path = grant_dir / "h2-target-child-error.json"
    if raw_path.exists() or error_path.exists():
        raise ExecutionFailure("raw target supervisor paths already exist")
    context = mp.get_context("spawn")
    process = context.Process(target=_target_child, args=(capability_dict, str(raw_path), str(error_path)), daemon=False)
    started = time.monotonic()
    process.start()
    process.join(float(total_seconds))
    if process.is_alive():
        process.terminate()
        process.join(5.0)
        if process.is_alive():
            process.kill()
            process.join(5.0)
        raw_path.unlink(missing_ok=True)
        raise ResourceFailure("total wall-clock budget exceeded; target child terminated including finalize/precision audit")
    elapsed = time.monotonic() - started
    if process.exitcode != 0:
        message = "target child failed without error record"
        if error_path.is_file():
            try:
                message = error_path.read_text(encoding="utf-8")
            except OSError:
                pass
        raw_path.unlink(missing_ok=True)
        error_path.unlink(missing_ok=True)
        raise ExecutionFailure(f"target child exit={process.exitcode}: {message}")
    if not raw_path.is_file():
        raise ExecutionFailure("target child exited successfully without raw result")
    with raw_path.open("rb") as stream:
        raw = pickle.load(stream)
    raw_path.unlink(missing_ok=True)
    error_path.unlink(missing_ok=True)
    if not isinstance(raw, dict):
        raise ExecutionFailure("target child raw result is not a mapping")
    return raw, elapsed


def no_solve_timeout_probe() -> dict[str, Any]:
    started = time.monotonic()
    deadline = 0.01
    time.sleep(deadline)
    elapsed = time.monotonic() - started
    return {"status": "PASS_NO_SOLVE_TIMEOUT_POLICY_PROBE", "deadline_seconds": deadline, "elapsed_seconds": elapsed, "solver_calls": 0}


def execute(transaction_root: Path) -> dict[str, Any]:
    preflight = static_preflight()
    release, grant, release_sha, grant_sha = validate_release_and_grant()
    external_root = UTILS.ensure_external_transaction_root(transaction_root)
    result_dir, staging = pre_solver_output_collision_guard(external_root, grant)
    strict_startup_environment()
    H1.enforce_process_limits()
    runtime = H1.validate_runtime()
    grant_dir = UTILS.claim_single_use_grant(external_root, grant, grant_sha)
    UTILS.mark_state(grant_dir, "RUNNING", release_authorization_sha256=release_sha)
    contract_sha = sha256_file(CONTRACT_PATH)
    limits = load_json(RESOURCE_POLICY_PATH)["resource_limits"]
    capability_dict = {
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
    try:
        raw_result, supervised_elapsed = supervised_target_execution(capability_dict, grant_dir, int(limits["maximum_wall_clock_seconds_total"]))
        remaining = float(limits["maximum_wall_clock_seconds_total"]) - supervised_elapsed
        with H1.packaging_wall_clock_limit(remaining):
            package = H1.package_schema_complete_result(staging, raw_result, runtime, grant, release_sha, grant_sha, int(limits["maximum_result_bytes"]))
            result_dir.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staging, result_dir)
            UTILS._fsync_directory(result_dir.parent)
        UTILS.mark_state(grant_dir, "SUCCEEDED", result_directory=str(result_dir), result_sha256=package["result_sha256"], final_classification=package["final_classification"], replay_permitted=False)
        return {"status": "PHYSICAL_TRANSACTION_COMPLETED_SCHEMA_COMPLETE_RESULT_QUARANTINED_H2", "run_id": RUN_ID, "result_directory": str(result_dir), "result_sha256": package["result_sha256"], "final_classification": package["final_classification"], "final_package_bytes": package["final_package_bytes"], "supervised_target_elapsed_wall_clock_seconds": supervised_elapsed, "grant_spent": True, "replay_permitted": False, "physical_evidence_effect": "NONE"}
    except BaseException as exc:
        try:
            failure = {"schema": "universelab.ulsh-01.wp2-h2.failure-record.v1", "run_id": RUN_ID, "created_utc": H1.utc_now(), "error_type": type(exc).__name__, "error": str(exc), "result_package_committed": False, "grant_spent": True, "replay_permitted": False, "retry_requires_new_grant": True, "physical_evidence_effect": "NONE"}
            UTILS.atomic_json(grant_dir / "failure.json", failure)
            UTILS.mark_state(grant_dir, "FAILED" if isinstance(exc, Exception) else "CRASHED_OR_INDETERMINATE", error_type=type(exc).__name__, replay_permitted=False, retry_requires_new_grant=True)
        finally:
            pass
        raise


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("audit")
    sub.add_parser("no-solve-timeout-probe")
    run = sub.add_parser("execute")
    run.add_argument("--transaction-root", required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "audit":
            print(json.dumps(static_preflight(), indent=2, sort_keys=True))
            return 0
        if args.command == "no-solve-timeout-probe":
            print(json.dumps(no_solve_timeout_probe(), indent=2, sort_keys=True))
            return 0
        if args.command == "execute":
            print(json.dumps(execute(Path(args.transaction_root)), indent=2, sort_keys=True))
            return 0
    except AuthorizationDenied as exc:
        print(f"NOT_AUTHORIZED: {exc}", file=sys.stderr)
        return EXIT_NOT_AUTHORIZED
    except ContractFailure as exc:
        print(f"CONTRACT_FAILURE: {exc}", file=sys.stderr)
        return EXIT_CONTRACT_FAILURE
    except ResourceFailure as exc:
        print(f"RESOURCE_FAILURE: {exc}", file=sys.stderr)
        return EXIT_RESOURCE_FAILURE
    except UTILS.ReplayOrCrash as exc:
        print(f"REPLAY_OR_CRASH: {exc}", file=sys.stderr)
        return EXIT_REPLAY_OR_CRASH
    except Exception as exc:
        print(f"EXECUTION_FAILURE: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_EXECUTION_FAILURE
    return EXIT_EXECUTION_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
