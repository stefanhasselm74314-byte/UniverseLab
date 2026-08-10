#!/usr/bin/env python3
"""ULSH-01 / WP2 physical BVP transaction guard.

The default/audit paths never import numerical backends and never execute the
CP01R1 solve.  `execute` is fail-closed and requires two future append-only
artifacts: a source-bound release authorization and a single-use grant.  Grant
consumption is atomic and permanent; a crash leaves the grant spent and a new
grant is required.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import sys
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

CONTRACT_PATH = ROOT / "registry/2026-08-10_ULSH-01_MD2S-BVP_WP2_PhysicalTransactionContract_v1.0.json"
TARGET_PATH = ROOT / "tools/2026-08-10_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.0.py"
RUN_INPUT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"
PREREG_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"
SEED_SPEC_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BSeedSpecification_v0.1.json"
RESOURCE_POLICY_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
RESULT_SCHEMA_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResultSchema_v0.1.json"
DEPENDENCY_LOCK_PATH = ROOT / "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3B_v0.1.txt"
WP1_CONTRACT_PATH = ROOT / "registry/2026-08-10_ULSH-01_MD2S-BVP_WP1_TargetBoundaryContract_v1.0.json"
WP1_LEDGER_PATH = ROOT / "science/hzt-m0/md2s/2026-08-10_ULSH-01_MD2S-BVP_WP1_TargetBoundaryLedger_v1.0.md"

# Deliberately absent in the WP2 build. Creating either file is a later release act.
RELEASE_PATH = ROOT / "registry/2026-08-10_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.0.json"
GRANT_PATH = ROOT / "registry/2026-08-10_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.0.json"

THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
)
NONCE_RE = re.compile(r"^[0-9a-f]{32,64}$")
TERMINAL_STATES = {"SUCCEEDED", "FAILED", "CRASHED_OR_INDETERMINATE"}


class TransactionError(RuntimeError):
    pass


class AuthorizationDenied(TransactionError):
    pass


class ContractFailure(TransactionError):
    pass


class ResourceFailure(TransactionError):
    pass


class ReplayOrCrash(TransactionError):
    pass


class ExecutionFailure(TransactionError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AuthorizationDenied(f"invalid UTC timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise AuthorizationDenied("grant timestamps must include timezone")
    return parsed.astimezone(timezone.utc)


def _dynamic_import(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ContractFailure(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_target_audit_module():
    # Target module itself imports only stdlib until its guarded execution function.
    return _dynamic_import(TARGET_PATH, "ulsh_wp2_target_audit")


def verify_git_blob_bindings(contract: dict[str, Any]) -> dict[str, str]:
    bindings = contract["source_bindings"]
    path_map = {
        "wp1_contract": WP1_CONTRACT_PATH,
        "wp1_ledger": WP1_LEDGER_PATH,
        "run_input": RUN_INPUT_PATH,
        "preregistration": PREREG_PATH,
        "seed_specification": SEED_SPEC_PATH,
        "resource_policy": RESOURCE_POLICY_PATH,
        "result_schema": RESULT_SCHEMA_PATH,
        "dependency_lock": DEPENDENCY_LOCK_PATH,
        "target_entrypoint": TARGET_PATH,
        "transaction_source": Path(__file__).resolve(),
    }
    observed: dict[str, str] = {}
    for key, path in path_map.items():
        expected = bindings[key]["git_blob_sha1"]
        actual = git_blob_sha1(path)
        if actual != expected:
            raise ContractFailure(f"source binding drift for {key}: {actual} != {expected}")
        observed[key] = actual
    return observed


def static_preflight() -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    if contract.get("run_id") != RUN_ID or contract.get("frozen_payload_sha256") != FROZEN_PAYLOAD_SHA256:
        raise ContractFailure("WP2 contract run binding drift")
    if contract.get("physical_solve_executed") is not False:
        raise ContractFailure("WP2 contract must not claim physical execution")
    if contract.get("physical_solve_authorized") is not False:
        raise ContractFailure("WP2 build must remain unreleased")
    observed_blobs = verify_git_blob_bindings(contract)
    if sha256_file(DEPENDENCY_LOCK_PATH) != DEPENDENCY_LOCK_SHA256:
        raise ContractFailure("dependency-lock SHA-256 drift")

    target = load_target_audit_module()
    target_audit = target.audit_target()
    if target_audit.get("status") != "PASS_SOURCE_BOUND_TARGET_ENTRYPOINT_NO_SOLVE":
        raise ContractFailure("target entrypoint audit failed")
    if target_audit.get("planned_entry_count") != 35 or target_audit.get("a_F") != "1/4":
        raise ContractFailure("target schedule/payload drift")
    if target_audit.get("solver_calls") != 0 or target_audit.get("physical_solve_executed") is not False:
        raise ContractFailure("audit path crossed numerical execution firewall")

    expected_backend = contract["backend_bindings"]
    for key, observed in target_audit["backend_sha256"].items():
        if observed != expected_backend[key]["sha256"]:
            raise ContractFailure(f"backend digest drift: {key}")

    release_present = RELEASE_PATH.exists()
    grant_present = GRANT_PATH.exists()
    return {
        "status": "PASS_WP2_STATIC_PREFLIGHT_RELEASE_READY_NO_SOLVE",
        "run_id": RUN_ID,
        "frozen_payload_sha256": FROZEN_PAYLOAD_SHA256,
        "schedule_sha256": target_audit["schedule_sha256"],
        "planned_entry_count": 35,
        "source_git_blob_sha1": observed_blobs,
        "backend_sha256": target_audit["backend_sha256"],
        "release_authorization_present": release_present,
        "single_use_grant_present": grant_present,
        "physical_solve_authorized": False,
        "solver_calls": 0,
        "physical_solve_executed": False,
    }


def expected_dependencies() -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in DEPENDENCY_LOCK_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "==" not in line:
            raise ContractFailure(f"non-exact dependency line: {line}")
        name, version = line.split("==", 1)
        result[name.strip()] = version.strip()
    if not result:
        raise ContractFailure("empty dependency lock")
    return result


def runtime_attestation() -> dict[str, Any]:
    expected = expected_dependencies()
    observed: dict[str, str] = {}
    for name in expected:
        try:
            observed[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            observed[name] = "NOT_INSTALLED"
    return {
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "pythonhashseed": os.environ.get("PYTHONHASHSEED", "UNSET"),
        "dependencies_expected": expected,
        "dependencies_observed": observed,
        "thread_environment": {key: os.environ.get(key, "UNSET") for key in THREAD_ENV_KEYS},
        "logical_cores": os.cpu_count(),
    }


def validate_runtime() -> dict[str, Any]:
    att = runtime_attestation()
    if sys.version_info[:2] != (3, 12):
        raise ResourceFailure(f"Python 3.12 required, found {att['python']}")
    if att["pythonhashseed"] != "0":
        raise ResourceFailure("execute requires process startup with PYTHONHASHSEED=0")
    if att["dependencies_observed"] != att["dependencies_expected"]:
        raise ResourceFailure("installed dependency versions differ from frozen lock")
    for key, value in att["thread_environment"].items():
        if value not in {"UNSET", "1"}:
            raise ResourceFailure(f"{key} must be unset or 1")
    resource = load_json(RESOURCE_POLICY_PATH)
    if resource["execution_environment"]["thread_count"] != 1:
        raise ResourceFailure("resource policy thread count drift")
    if resource["execution_environment"]["network_access"] is not False:
        raise ResourceFailure("network policy drift")
    if resource["execution_environment"]["randomness"] is not False:
        raise ResourceFailure("randomness policy drift")
    return att


def validate_release_and_grant(now: datetime | None = None) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    if not RELEASE_PATH.is_file() or not GRANT_PATH.is_file():
        raise AuthorizationDenied("WP2 release authorization and/or single-use grant is absent")
    contract = load_json(CONTRACT_PATH)
    release = load_json(RELEASE_PATH)
    grant = load_json(GRANT_PATH)
    grant_sha = sha256_file(GRANT_PATH)
    release_sha = sha256_file(RELEASE_PATH)
    contract_sha = sha256_file(CONTRACT_PATH)
    target = load_target_audit_module()
    schedule_digest = target.schedule_sha256()
    source_bundle = sha256_bytes(canonical_json_bytes(contract["source_bindings"]))

    if release.get("schema") != contract["grant_protocol"]["release_schema"]:
        raise AuthorizationDenied("unexpected release schema")
    if release.get("status") != "GRANTED" or release.get("physical_solve_authorized") is not True:
        raise AuthorizationDenied("physical solve release is not GRANTED")
    if release.get("run_id") != RUN_ID or release.get("frozen_payload_sha256") != FROZEN_PAYLOAD_SHA256:
        raise AuthorizationDenied("release is bound to another run")
    if release.get("grant_sha256") != grant_sha:
        raise AuthorizationDenied("release does not pin the exact grant bytes")
    if release.get("transaction_contract_sha256") != contract_sha:
        raise AuthorizationDenied("release does not pin the exact WP2 contract bytes")
    if release.get("source_bundle_sha256") != source_bundle:
        raise AuthorizationDenied("release source-bundle binding mismatch")

    if grant.get("schema") != contract["grant_protocol"]["grant_schema"]:
        raise AuthorizationDenied("unexpected grant schema")
    required_true = ("single_use", "physical_solve_authorized", "no_retry", "no_scan", "no_fallback")
    if any(grant.get(key) is not True for key in required_true):
        raise AuthorizationDenied("grant scope flags are incomplete")
    if grant.get("run_id") != RUN_ID or grant.get("frozen_payload_sha256") != FROZEN_PAYLOAD_SHA256:
        raise AuthorizationDenied("grant is bound to another run")
    if grant.get("transaction_contract_sha256") != contract_sha:
        raise AuthorizationDenied("grant contract binding mismatch")
    if grant.get("source_bundle_sha256") != source_bundle:
        raise AuthorizationDenied("grant source-bundle binding mismatch")
    if grant.get("schedule_sha256") != schedule_digest or grant.get("planned_entry_count") != 35:
        raise AuthorizationDenied("grant schedule binding mismatch")
    if grant.get("dependency_lock_sha256") != DEPENDENCY_LOCK_SHA256:
        raise AuthorizationDenied("grant dependency binding mismatch")
    if grant.get("resource_policy_git_blob_sha1") != contract["source_bindings"]["resource_policy"]["git_blob_sha1"]:
        raise AuthorizationDenied("grant resource-policy binding mismatch")
    if grant.get("result_schema_git_blob_sha1") != contract["source_bindings"]["result_schema"]["git_blob_sha1"]:
        raise AuthorizationDenied("grant result-schema binding mismatch")

    nonce = str(grant.get("grant_nonce", ""))
    if not NONCE_RE.fullmatch(nonce):
        raise AuthorizationDenied("grant nonce must be 128-256 bits lowercase hex")
    clock = now or datetime.now(timezone.utc)
    not_before = parse_utc(str(grant.get("not_before", "")))
    expires_at = parse_utc(str(grant.get("expires_at", "")))
    issued_at = parse_utc(str(grant.get("issued_at", "")))
    if not (issued_at <= not_before < expires_at):
        raise AuthorizationDenied("invalid grant time ordering")
    max_window = int(contract["grant_protocol"]["maximum_validity_seconds"])
    if (expires_at - not_before).total_seconds() > max_window:
        raise AuthorizationDenied("grant validity window exceeds contract maximum")
    if clock < not_before or clock >= expires_at:
        raise AuthorizationDenied("grant is outside its validity window")
    return release, grant, release_sha, grant_sha


def ensure_external_transaction_root(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    root = ROOT.resolve()
    if resolved == root or root in resolved.parents:
        raise ContractFailure("transaction root must be outside the repository")
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _fsync_directory(path: Path) -> None:
    if os.name != "posix":
        return
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    data = canonical_json_bytes(payload) + b"\n"
    with temp.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)
    _fsync_directory(path.parent)


def _state_path(grant_dir: Path) -> Path:
    return grant_dir / "state.json"


def mark_state(grant_dir: Path, state: str, **extra: Any) -> None:
    payload = {"state": state, "updated_utc": utc_now(), "run_id": RUN_ID, **extra}
    atomic_json(_state_path(grant_dir), payload)


def recover_or_reject_existing(grant_dir: Path) -> None:
    spend = grant_dir / "spent.json"
    if not spend.exists():
        return
    state_path = _state_path(grant_dir)
    state = None
    if state_path.exists():
        try:
            state = load_json(state_path).get("state")
        except ContractFailure:
            state = None
    if state not in TERMINAL_STATES:
        mark_state(grant_dir, "CRASHED_OR_INDETERMINATE", replay_permitted=False)
    raise ReplayOrCrash("single-use grant was already consumed; replay/retry is forbidden")


def claim_single_use_grant(transaction_root: Path, grant: dict[str, Any], grant_sha: str) -> Path:
    nonce = str(grant["grant_nonce"])
    grant_dir = transaction_root / "grants" / nonce
    grant_dir.mkdir(parents=True, exist_ok=True)
    recover_or_reject_existing(grant_dir)
    spend = grant_dir / "spent.json"
    payload = {
        "run_id": RUN_ID,
        "grant_nonce": nonce,
        "grant_sha256": grant_sha,
        "consumed_utc": utc_now(),
        "single_use": True,
        "replay_permitted": False,
        "retry_after_crash_permitted": False,
    }
    data = canonical_json_bytes(payload) + b"\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(spend, flags, 0o600)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
    _fsync_directory(grant_dir)
    mark_state(grant_dir, "CLAIMED", replay_permitted=False)
    return grant_dir


def enforce_process_limits() -> None:
    resource_policy = load_json(RESOURCE_POLICY_PATH)
    limits = resource_policy["resource_limits"]
    for key in THREAD_ENV_KEYS:
        os.environ[key] = "1"
    if os.name == "posix":
        import resource
        memory = int(limits["maximum_memory_bytes"])
        cpu = int(limits["maximum_wall_clock_seconds_total"])
        resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
        current_soft, current_hard = resource.getrlimit(resource.RLIMIT_CPU)
        new_hard = cpu + 1 if current_hard in (-1, resource.RLIM_INFINITY) else min(current_hard, cpu + 1)
        resource.setrlimit(resource.RLIMIT_CPU, (min(cpu, new_hard), new_hard))


@contextmanager
def wall_clock_limit(seconds: int):
    if os.name != "posix" or not hasattr(signal, "SIGALRM"):
        yield
        return
    def handler(_signum, _frame):
        raise TimeoutError("WP2 total wall-clock budget exceeded")
    previous = signal.signal(signal.SIGALRM, handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


@contextmanager
def network_denied():
    original_socket = socket.socket
    original_create = socket.create_connection
    original_getaddrinfo = socket.getaddrinfo
    def denied(*_args, **_kwargs):
        raise RuntimeError("network access forbidden by WP2 resource policy")
    socket.socket = denied  # type: ignore[assignment]
    socket.create_connection = denied  # type: ignore[assignment]
    socket.getaddrinfo = denied  # type: ignore[assignment]
    try:
        yield
    finally:
        socket.socket = original_socket  # type: ignore[assignment]
        socket.create_connection = original_create  # type: ignore[assignment]
        socket.getaddrinfo = original_getaddrinfo  # type: ignore[assignment]


def execute(transaction_root: Path) -> dict[str, Any]:
    # All authorization/hash/runtime checks precede claim, backend import and output.
    preflight = static_preflight()
    runtime = validate_runtime()
    release, grant, release_sha, grant_sha = validate_release_and_grant()
    external_root = ensure_external_transaction_root(transaction_root)
    grant_dir = claim_single_use_grant(external_root, grant, grant_sha)
    mark_state(grant_dir, "RUNNING", release_authorization_sha256=release_sha)

    contract_sha = sha256_file(CONTRACT_PATH)
    target = load_target_audit_module()
    capability = target.TargetExecutionCapability(
        run_id=RUN_ID,
        frozen_payload_sha256=FROZEN_PAYLOAD_SHA256,
        schedule_sha256=preflight["schedule_sha256"],
        grant_sha256=grant_sha,
        transaction_contract_sha256=contract_sha,
        release_authorization_sha256=release_sha,
        physical_solve_authorized=True,
    )
    limits = load_json(RESOURCE_POLICY_PATH)["resource_limits"]
    try:
        enforce_process_limits()
        with network_denied(), wall_clock_limit(int(limits["maximum_wall_clock_seconds_total"])):
            raw_result = target.execute_physical_schedule(capability)
        result_dir = external_root / "results" / grant["grant_nonce"]
        if result_dir.exists():
            raise ExecutionFailure("immutable result directory already exists")
        staging = external_root / "results" / f".{grant['grant_nonce']}.staging-{os.getpid()}"
        staging.mkdir(parents=True, exist_ok=False)
        atomic_json(staging / "raw-execution.json", raw_result)
        atomic_json(staging / "runtime-attestation.json", runtime)
        manifest = {
            "run_id": RUN_ID,
            "grant_sha256": grant_sha,
            "release_authorization_sha256": release_sha,
            "raw_execution_sha256": sha256_file(staging / "raw-execution.json"),
            "runtime_attestation_sha256": sha256_file(staging / "runtime-attestation.json"),
            "result_schema_git_blob_sha1": load_json(CONTRACT_PATH)["source_bindings"]["result_schema"]["git_blob_sha1"],
            "physical_evidence_effect": "NONE_PENDING_BOUND_RESULT_SCHEMA_QA",
        }
        atomic_json(staging / "artifact-manifest.json", manifest)
        result_dir.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staging, result_dir)
        _fsync_directory(result_dir.parent)
        mark_state(grant_dir, "SUCCEEDED", result_directory=str(result_dir), replay_permitted=False)
        return {
            "status": "PHYSICAL_TRANSACTION_COMPLETED_RAW_RESULT_QUARANTINED",
            "run_id": RUN_ID,
            "result_directory": str(result_dir),
            "grant_spent": True,
            "replay_permitted": False,
            "physical_evidence_effect": "NONE_PENDING_BOUND_RESULT_SCHEMA_QA",
        }
    except BaseException as exc:
        # The spend marker is never removed. Same grant can never be retried.
        try:
            mark_state(
                grant_dir,
                "FAILED" if isinstance(exc, Exception) else "CRASHED_OR_INDETERMINATE",
                error_type=type(exc).__name__,
                replay_permitted=False,
                retry_requires_new_grant=True,
            )
        finally:
            pass
        raise


def self_test_replay_crash(temp_root: Path) -> dict[str, Any]:
    root = ensure_external_transaction_root(temp_root)
    grant = {"grant_nonce": "0123456789abcdef0123456789abcdef"}
    grant_sha = "1" * 64
    first = claim_single_use_grant(root, grant, grant_sha)
    mark_state(first, "RUNNING")
    replay_blocked = False
    try:
        claim_single_use_grant(root, grant, grant_sha)
    except ReplayOrCrash:
        replay_blocked = True
    final_state = load_json(_state_path(first))["state"]
    if not replay_blocked or final_state != "CRASHED_OR_INDETERMINATE":
        raise ReplayOrCrash("replay/crash self-test failed")
    return {
        "status": "PASS_SINGLE_USE_REPLAY_CRASH_SELF_TEST_NO_SOLVE",
        "replay_blocked": True,
        "crash_state": final_state,
        "solver_calls": 0,
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("audit")
    test = sub.add_parser("self-test")
    test.add_argument("--transaction-root", required=True)
    run = sub.add_parser("execute")
    run.add_argument("--transaction-root", required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "audit":
            print(json.dumps(static_preflight(), indent=2, sort_keys=True))
            return 0
        if args.command == "self-test":
            print(json.dumps(self_test_replay_crash(Path(args.transaction_root)), indent=2, sort_keys=True))
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
    except ReplayOrCrash as exc:
        print(f"REPLAY_OR_CRASH: {exc}", file=sys.stderr)
        return EXIT_REPLAY_OR_CRASH
    except Exception as exc:
        print(f"EXECUTION_FAILURE: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_EXECUTION_FAILURE
    return EXIT_EXECUTION_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
