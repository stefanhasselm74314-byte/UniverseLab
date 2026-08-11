#!/usr/bin/env python3
"""ULSH-01 / WP2-H2 transaction supervisor v1.3.

Final H2 transaction wrapper. It strengthens v1.2 with a positive effective-BLAS
thread count probe and one independent parent-process wall-clock timer spanning
child target execution, target finalization, >=80-bit precision QA, result
packaging and atomic commit. Audit is no-solve.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import ctypes
import importlib.util
import json
import multiprocessing as mp
import os
from pathlib import Path
import pickle
import signal
import sys
import time
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.2.py"
_SPEC = importlib.util.spec_from_file_location("ulsh_wp2_h2_tx_v12", BASE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("unable to import WP2-H2 transaction v1.2")
BASE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = BASE
_SPEC.loader.exec_module(BASE)

RUN_ID = BASE.RUN_ID
FROZEN_PAYLOAD_SHA256 = BASE.FROZEN_PAYLOAD_SHA256
DEPENDENCY_LOCK_SHA256 = BASE.DEPENDENCY_LOCK_SHA256
CONTRACT_PATH = BASE.CONTRACT_PATH
TARGET_PATH = BASE.TARGET_PATH
RESOURCE_POLICY_PATH = BASE.RESOURCE_POLICY_PATH
RELEASE_PATH = BASE.RELEASE_PATH
GRANT_PATH = BASE.GRANT_PATH
THREAD_ENV_KEYS = BASE.THREAD_ENV_KEYS
UTILS = BASE.UTILS
H1 = BASE.H1

AuthorizationDenied = BASE.AuthorizationDenied
ContractFailure = BASE.ContractFailure
ResourceFailure = BASE.ResourceFailure
ExecutionFailure = BASE.ExecutionFailure


def load_json(path: Path) -> dict[str, Any]:
    return BASE.load_json(path)


def sha256_file(path: Path) -> str:
    return BASE.sha256_file(path)


def static_preflight() -> dict[str, Any]:
    audit = BASE.static_preflight()
    audit["status"] = "PASS_WP2_H2_V13_STATIC_PREFLIGHT_NO_SOLVE"
    audit["effective_blas_thread_attestation_required"] = True
    audit["continuous_total_transaction_deadline"] = True
    audit["solver_calls"] = 0
    audit["physical_solve_authorized"] = False
    audit["physical_solve_executed"] = False
    audit["physical_evidence_effect"] = "NONE"
    return audit


def effective_blas_thread_attestation() -> dict[str, Any]:
    candidates: list[str] = []
    maps = Path("/proc/self/maps")
    if maps.is_file():
        for line in maps.read_text(encoding="utf-8", errors="replace").splitlines():
            path = line.rsplit(None, 1)[-1] if "/" in line else ""
            lower = path.lower()
            if path.startswith("/") and any(token in lower for token in ("openblas", "mkl_rt", "blis")):
                candidates.append(path)
    candidates = list(dict.fromkeys(candidates))
    probes: list[dict[str, Any]] = []
    symbols = (
        "openblas_get_num_threads",
        "openblas_get_num_threads64_",
        "scipy_openblas_get_num_threads",
        "scipy_openblas_get_num_threads64_",
        "MKL_Get_Max_Threads",
        "bli_thread_get_num_threads",
    )
    for path in candidates:
        try:
            library = ctypes.CDLL(path)
        except OSError:
            continue
        for symbol in symbols:
            function = getattr(library, symbol, None)
            if function is None:
                continue
            function.restype = ctypes.c_int
            try:
                count = int(function())
            except Exception:
                continue
            probes.append({"library": path, "symbol": symbol, "reported_threads": count})
    if not probes:
        raise ResourceFailure("unable to positively query loaded BLAS thread-pool size")
    bad = [probe for probe in probes if probe["reported_threads"] != 1]
    if bad:
        raise ResourceFailure(f"effective BLAS thread pool is not one thread: {bad}")
    return {"status": "PASS_EFFECTIVE_BLAS_THREAD_COUNT_ONE", "probes": probes}


@contextmanager
def total_transaction_wall_clock_limit(seconds: float):
    if seconds <= 0.0:
        raise ResourceFailure("total wall-clock budget must be positive")
    if os.name != "posix" or not hasattr(signal, "SIGALRM") or not hasattr(signal, "setitimer"):
        raise ResourceFailure("POSIX setitimer required for H2 total transaction wall-clock enforcement")
    def handler(_signum, _frame):
        raise ResourceFailure("total H2 transaction wall-clock budget exceeded")
    previous = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)
    if previous_timer[0] > 0.0:
        raise ResourceFailure("unexpected pre-existing parent ITIMER_REAL")
    signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, float(seconds))
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, previous)


def _target_child(capability_dict: dict[str, Any], raw_path_text: str, error_path_text: str) -> None:
    BASE._target_child(capability_dict, raw_path_text, error_path_text)


def supervised_target_execution(capability_dict: dict[str, Any], grant_dir: Path, total_seconds: int) -> tuple[dict[str, Any], float]:
    raw_path = grant_dir / "h2-v13-raw-target-result.pickle"
    error_path = grant_dir / "h2-v13-target-child-error.json"
    if raw_path.exists() or error_path.exists():
        raise ExecutionFailure("v1.3 target supervisor paths already exist")
    context = mp.get_context("spawn")
    process = context.Process(target=_target_child, args=(capability_dict, str(raw_path), str(error_path)), daemon=False)
    started = time.monotonic()
    try:
        process.start()
        process.join(float(total_seconds))
        if process.is_alive():
            raise ResourceFailure("target child exceeded supervisor deadline")
        elapsed = time.monotonic() - started
        if process.exitcode != 0:
            message = "target child failed without error record"
            if error_path.is_file():
                try:
                    message = error_path.read_text(encoding="utf-8")
                except OSError:
                    pass
            raise ExecutionFailure(f"target child exit={process.exitcode}: {message}")
        if not raw_path.is_file():
            raise ExecutionFailure("target child exited successfully without raw result")
        with raw_path.open("rb") as stream:
            raw = pickle.load(stream)
        if not isinstance(raw, dict):
            raise ExecutionFailure("target child raw result is not a mapping")
        return raw, elapsed
    finally:
        if process.pid is not None and process.is_alive():
            process.terminate()
            process.join(5.0)
            if process.is_alive():
                process.kill()
                process.join(5.0)
        raw_path.unlink(missing_ok=True)
        error_path.unlink(missing_ok=True)


def execute(transaction_root: Path) -> dict[str, Any]:
    preflight = static_preflight()
    release, grant, release_sha, grant_sha = BASE.validate_release_and_grant()
    external_root = UTILS.ensure_external_transaction_root(transaction_root)
    result_dir, staging = BASE.pre_solver_output_collision_guard(external_root, grant)
    BASE.strict_startup_environment()
    H1.enforce_process_limits()
    runtime = H1.validate_runtime()
    runtime["effective_blas_threads"] = effective_blas_thread_attestation()
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
        with total_transaction_wall_clock_limit(float(limits["maximum_wall_clock_seconds_total"])):
            raw_result, supervised_elapsed = supervised_target_execution(capability_dict, grant_dir, int(limits["maximum_wall_clock_seconds_total"]))
            package = H1.package_schema_complete_result(staging, raw_result, runtime, grant, release_sha, grant_sha, int(limits["maximum_result_bytes"]))
            result_dir.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staging, result_dir)
            UTILS._fsync_directory(result_dir.parent)
        UTILS.mark_state(grant_dir, "SUCCEEDED", result_directory=str(result_dir), result_sha256=package["result_sha256"], final_classification=package["final_classification"], replay_permitted=False)
        return {"status": "PHYSICAL_TRANSACTION_COMPLETED_SCHEMA_COMPLETE_RESULT_QUARANTINED_H2_V13", "run_id": RUN_ID, "result_directory": str(result_dir), "result_sha256": package["result_sha256"], "final_classification": package["final_classification"], "supervised_target_elapsed_wall_clock_seconds": supervised_elapsed, "grant_spent": True, "replay_permitted": False, "physical_evidence_effect": "NONE"}
    except BaseException as exc:
        try:
            failure = {"schema": "universelab.ulsh-01.wp2-h2-v13.failure-record.v1", "run_id": RUN_ID, "created_utc": H1.utc_now(), "error_type": type(exc).__name__, "error": str(exc), "result_package_committed": False, "grant_spent": True, "replay_permitted": False, "retry_requires_new_grant": True, "physical_evidence_effect": "NONE"}
            UTILS.atomic_json(grant_dir / "failure.json", failure)
            UTILS.mark_state(grant_dir, "FAILED" if isinstance(exc, Exception) else "CRASHED_OR_INDETERMINATE", error_type=type(exc).__name__, replay_permitted=False, retry_requires_new_grant=True)
        finally:
            pass
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
        return BASE.EXIT_NOT_AUTHORIZED
    except ContractFailure as exc:
        print(f"CONTRACT_FAILURE: {exc}", file=sys.stderr)
        return BASE.EXIT_CONTRACT_FAILURE
    except ResourceFailure as exc:
        print(f"RESOURCE_FAILURE: {exc}", file=sys.stderr)
        return BASE.EXIT_RESOURCE_FAILURE
    except UTILS.ReplayOrCrash as exc:
        print(f"REPLAY_OR_CRASH: {exc}", file=sys.stderr)
        return BASE.EXIT_REPLAY_OR_CRASH
    except Exception as exc:
        print(f"EXECUTION_FAILURE: {type(exc).__name__}: {exc}", file=sys.stderr)
        return BASE.EXIT_EXECUTION_FAILURE
    return BASE.EXIT_EXECUTION_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
