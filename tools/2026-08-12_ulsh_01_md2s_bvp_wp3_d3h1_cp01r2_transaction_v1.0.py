#!/usr/bin/env python3
"""ULSH-01 / WP3-D3H1 CP01R2 transaction supervisor.

The implementation preserves the proven CP01R1 H3 transaction invariants while
rebinding them to the immutable CP01R2 payload, schedule, target and result
schema. Audit is the default path. No release authorization or grant is issued
by this module; physical execution is impossible while those future artifacts
are absent.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager, redirect_stdout
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import pickle
import platform
import re
import shutil
import signal
import subprocess
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2"
RUN_PAYLOAD_SHA256 = "e8b8e82d2cb1472d91c387a40c8f84024c2549a3dcc2c897df5561f7bf721b36"
SCHEDULE_SHA256 = "929f59d018cc511f36c98ef26a8614ed495fe699a067b1b33e6c5b53efaf8e0b"
DEPENDENCY_LOCK_SHA256 = "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f"
PLANNED_ENTRY_COUNT = 35
CONTRACT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2TransactionHardeningContract_v1.0.json"
RESULT_SCHEMA = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2ResultSchema_v1.0.json"
D3_REVIEW = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3_CP01R2PhysicalBindingReleaseReadinessReview_v1.0.json"
RESOURCE = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
TARGET = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3h1_cp01r2_target_v1.0.py"
H3_REFERENCE = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.4.py"
RELEASE_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2_PhysicalSolveReleaseAuthorization_v1.0.json"
GRANT_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2_SingleUseExecutionGrant_v1.0.json"
EXPECTED_TARGET_BLOB = "199815ac9e4014cc0d68fde71d634cdac24516ce"
EXPECTED_RESULT_SCHEMA_BLOB = "54bf49acdfcca128e3b909d6e479b1178c77c276"
NONCE_RE = re.compile(r"^[0-9a-f]{32,64}$")
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
)


class TransactionError(RuntimeError):
    pass


class AuthorizationDenied(TransactionError):
    pass


class ResultClosureError(TransactionError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TransactionError(f"top-level JSON object required: {path}")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = canonical_json_bytes(payload)
    temp = path.with_name(path.name + ".tmp")
    with temp.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)
    _fsync_directory(path.parent)


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


def json_safe_projection(value: Any, path: str = "$") -> tuple[Any, list[dict[str, str]]]:
    replacements: list[dict[str, str]] = []
    if isinstance(value, float) and not math.isfinite(value):
        kind = "positive_infinity" if value > 0 else "negative_infinity" if value < 0 else "nan"
        return None, [{"path": path, "original_nonfinite_kind": kind, "replacement": "null", "reason": "JSON_SAFE_MISSING_OR_UNBOUNDED_DIAGNOSTIC_NOT_A_FINITE_MEASUREMENT"}]
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            projected, found = json_safe_projection(item, f"{path}.{key}")
            out[str(key)] = projected
            replacements.extend(found)
        return out, replacements
    if isinstance(value, (list, tuple)):
        out_list: list[Any] = []
        for index, item in enumerate(value):
            projected, found = json_safe_projection(item, f"{path}[{index}]")
            out_list.append(projected)
            replacements.extend(found)
        return out_list, replacements
    return value, replacements


def sanitize_result(value: dict[str, Any]) -> dict[str, Any]:
    projected, replacements = json_safe_projection(value)
    if not isinstance(projected, dict):
        raise ResultClosureError("result must remain a mapping")
    acceptance = projected.setdefault("acceptance_audit", {})
    if not isinstance(acceptance, dict):
        raise ResultClosureError("acceptance_audit must be a mapping")
    acceptance["json_safe_nonfinite_replacements"] = replacements
    acceptance["json_safe_nonfinite_policy"] = "NONFINITE_DIAGNOSTIC_SENTINEL_TO_NULL_PLUS_EXPLICIT_PATH_REASON_NEVER_TO_FINITE_MEASUREMENT"
    remaining = _walk_nonfinite(projected)
    if remaining:
        raise ResultClosureError(f"nonfinite values remain after sanitation: {remaining}")
    canonical_json_bytes(projected)
    return projected


def source_bundle_sha256(contract: dict[str, Any]) -> str:
    material: list[dict[str, str]] = []
    for key in sorted(contract["source_bindings"]):
        binding = contract["source_bindings"][key]
        path = ROOT / binding["path"]
        observed = git_blob_sha1(path)
        if observed != binding["git_blob_sha1"]:
            raise TransactionError(f"source binding drift: {key}: {observed}")
        material.append({"key": key, "path": binding["path"], "git_blob_sha1": observed})
    return hashlib.sha256(canonical_json_bytes(material)).hexdigest()


def _parse_utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AuthorizationDenied(f"invalid UTC timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise AuthorizationDenied("timezone required")
    return parsed.astimezone(timezone.utc)


def validate_release_and_grant(now: datetime | None = None) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    if not RELEASE_PATH.is_file() or not GRANT_PATH.is_file():
        raise AuthorizationDenied("CP01R2 exact release authorization and single-use grant are absent")
    contract = load_json(CONTRACT)
    release = load_json(RELEASE_PATH)
    grant = load_json(GRANT_PATH)
    protocol = contract["grant_protocol"]
    release_sha = sha256_file(RELEASE_PATH)
    grant_sha = sha256_file(GRANT_PATH)
    contract_sha = sha256_file(CONTRACT)
    bundle_sha = source_bundle_sha256(contract)
    if release.get("schema") != protocol["release_schema"] or release.get("status") != "GRANTED" or release.get("physical_solve_authorized") is not True:
        raise AuthorizationDenied("release authorization is not exact GRANTED")
    if grant.get("schema") != protocol["grant_schema"]:
        raise AuthorizationDenied("grant schema mismatch")
    for document, label in ((release, "release"), (grant, "grant")):
        if document.get("run_id") != RUN_ID or document.get("run_payload_sha256") != RUN_PAYLOAD_SHA256:
            raise AuthorizationDenied(f"{label} run binding mismatch")
        if document.get("schedule_sha256") != SCHEDULE_SHA256 or document.get("planned_entry_count") != PLANNED_ENTRY_COUNT:
            raise AuthorizationDenied(f"{label} schedule binding mismatch")
        if document.get("dependency_lock_sha256") != DEPENDENCY_LOCK_SHA256:
            raise AuthorizationDenied(f"{label} dependency binding mismatch")
        if document.get("result_schema_git_blob_sha1") != EXPECTED_RESULT_SCHEMA_BLOB:
            raise AuthorizationDenied(f"{label} result-schema binding mismatch")
        if document.get("target_git_blob_sha1") != EXPECTED_TARGET_BLOB:
            raise AuthorizationDenied(f"{label} target binding mismatch")
    if release.get("grant_sha256") != grant_sha or release.get("transaction_contract_sha256") != contract_sha or release.get("source_bundle_sha256") != bundle_sha:
        raise AuthorizationDenied("release exact contract/source/grant binding mismatch")
    if grant.get("transaction_contract_sha256") != contract_sha or grant.get("source_bundle_sha256") != bundle_sha:
        raise AuthorizationDenied("grant source/contract binding mismatch")
    for key in ("single_use", "physical_solve_authorized", "no_retry", "no_scan", "no_fallback", "no_parameter_or_topology_mutation"):
        if grant.get(key) is not True:
            raise AuthorizationDenied(f"grant scope flag missing: {key}")
    nonce = str(grant.get("grant_nonce", ""))
    if not NONCE_RE.fullmatch(nonce):
        raise AuthorizationDenied("grant nonce must be 128-256 bit lowercase hex")
    if not str(grant.get("authorization_decision_id", "")).startswith("UL-DEC-"):
        raise AuthorizationDenied("authorization_decision_id invalid")
    issued = _parse_utc(str(grant.get("issued_at", "")))
    not_before = _parse_utc(str(grant.get("not_before", "")))
    expires = _parse_utc(str(grant.get("expires_at", "")))
    clock = now or datetime.now(timezone.utc)
    if not (issued <= not_before < expires):
        raise AuthorizationDenied("grant time ordering invalid")
    if (expires - not_before).total_seconds() > int(protocol["maximum_validity_seconds"]):
        raise AuthorizationDenied("grant validity exceeds contract maximum")
    if clock < not_before or clock >= expires:
        raise AuthorizationDenied("grant outside validity window")
    return release, grant, release_sha, grant_sha


def output_paths(transaction_root: Path, grant: dict[str, Any]) -> tuple[Path, Path]:
    decision = str(grant["authorization_decision_id"])
    result_dir = transaction_root / "artifacts" / "hzt-m0" / "md2s" / "background3c" / RUN_ID / decision
    staging = result_dir.with_name(result_dir.name + f".staging-{grant['grant_nonce']}")
    return result_dir, staging


def pre_solver_output_collision_guard(transaction_root: Path, grant: dict[str, Any]) -> tuple[Path, Path]:
    result_dir, staging = output_paths(transaction_root, grant)
    if result_dir.exists() or staging.exists():
        raise ResultClosureError("immutable output collision: abort before grant spend, backend import or solver initialization")
    return result_dir, staging


def claim_single_use_grant(transaction_root: Path, grant: dict[str, Any], grant_sha: str) -> Path:
    grant_dir = transaction_root / "grant-state" / str(grant["grant_nonce"])
    grant_dir.mkdir(parents=True, exist_ok=False)
    spent = grant_dir / "spent.json"
    payload = canonical_json_bytes({
        "schema": "universelab.ulsh-01.md2s-bvp.cp01r2-grant-spend.v1",
        "run_id": RUN_ID,
        "grant_sha256": grant_sha,
        "grant_nonce": grant["grant_nonce"],
        "spent_at_utc": datetime.now(timezone.utc).isoformat(),
        "replay_permitted": False,
    })
    fd = os.open(spent, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(fd, payload)
        os.fsync(fd)
    finally:
        os.close(fd)
    _fsync_directory(grant_dir)
    _fsync_directory(grant_dir.parent)
    return grant_dir


def mark_state(grant_dir: Path, state: str, **extra: Any) -> None:
    _atomic_json(grant_dir / "state.json", {
        "schema": "universelab.ulsh-01.md2s-bvp.cp01r2-transaction-state.v1",
        "run_id": RUN_ID,
        "state": state,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "replay_permitted": False,
        **extra,
    })


def strict_startup_environment() -> None:
    bad = {key: os.environ.get(key) for key in THREAD_ENV_KEYS if os.environ.get(key) != "1"}
    if bad:
        raise TransactionError(f"all BLAS/OpenMP thread variables must be exactly '1' before numerical import: {bad}")


def runtime_attestation() -> dict[str, Any]:
    import numpy as np
    import scipy
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        np.__config__.show()
    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "logical_cpu_count": os.cpu_count(),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "thread_environment": {key: os.environ.get(key) for key in THREAD_ENV_KEYS},
        "numpy_longdouble_mantissa_bits": int(np.finfo(np.longdouble).nmant) + 1,
        "blas_lapack_configuration": buffer.getvalue(),
    }


def _prepare_network_denial(grant_dir: Path) -> Path:
    deny_dir = grant_dir / "python-network-deny"
    deny_dir.mkdir()
    sitecustomize = deny_dir / "sitecustomize.py"
    sitecustomize.write_text(
        "import socket\n"
        "def _deny(*args, **kwargs):\n    raise RuntimeError('CP01R2 solver network access denied by frozen resource policy')\n"
        "socket.create_connection = _deny\n"
        "socket.getaddrinfo = _deny\n"
        "_orig_socket = socket.socket\n"
        "class _DeniedSocket(_orig_socket):\n"
        "    def connect(self, *args, **kwargs):\n        return _deny(*args, **kwargs)\n"
        "    def connect_ex(self, *args, **kwargs):\n        return _deny(*args, **kwargs)\n"
        "socket.socket = _DeniedSocket\n",
        encoding="utf-8",
    )
    with sitecustomize.open("rb") as stream:
        os.fsync(stream.fileno())
    _fsync_directory(deny_dir)
    return deny_dir


@contextmanager
def post_target_wall_clock_limit(seconds: float):
    if seconds <= 0.0:
        raise TransactionError("no total wall-clock budget remains for packaging/commit")
    if os.name != "posix" or not hasattr(signal, "SIGALRM") or not hasattr(signal, "setitimer"):
        raise TransactionError("POSIX SIGALRM/setitimer required for post-target total deadline")
    def handler(_signum, _frame):
        raise TransactionError("CP01R2 total transaction wall-clock limit exceeded during packaging/commit")
    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)
    if previous_timer[0] > 0.0:
        raise TransactionError("unexpected pre-existing parent ITIMER_REAL")
    signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, float(seconds))
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, previous_handler)


def validate_result_closure(result: dict[str, Any]) -> None:
    schema = load_json(RESULT_SCHEMA)
    if result.get("run_id") != RUN_ID or result.get("run_payload_sha256") != RUN_PAYLOAD_SHA256 or result.get("schedule_sha256") != SCHEDULE_SHA256:
        raise ResultClosureError("result run identity drift")
    missing = set(schema["required_top_level_fields"]) - set(result)
    if missing:
        raise ResultClosureError(f"missing required result fields: {sorted(missing)}")
    primary = result.get("primary_backend")
    independent = result.get("independent_backend")
    if not isinstance(primary, dict) or not isinstance(independent, dict):
        raise ResultClosureError("backend sections must be mappings")
    missing_primary = (set(schema["legacy_primary_backend_required_fields"]) | set(schema["cp01r2_etrn01_required_fields"])) - set(primary)
    if missing_primary:
        raise ResultClosureError(f"missing primary result closure fields: {sorted(missing_primary)}")
    missing_independent = set(schema["independent_backend_required_fields"]) - set(independent)
    if missing_independent:
        raise ResultClosureError(f"missing independent result closure fields: {sorted(missing_independent)}")
    if result.get("final_classification") not in schema["allowed_final_classifications"]:
        raise ResultClosureError("final classification outside frozen vocabulary")
    if result.get("physical_evidence_effect") != "NONE":
        raise ResultClosureError("physical evidence effect must remain NONE")
    for candidate in result.get("candidate_inventory", []):
        if not isinstance(candidate, dict):
            raise ResultClosureError("candidate must be a mapping")
        missing_candidate = set(schema["candidate_required_fields"]) - set(candidate)
        if missing_candidate:
            raise ResultClosureError(f"candidate closure incomplete: {sorted(missing_candidate)}")
    for row in primary["trust_radius_rho_history"]:
        if row.get("acceptance_merit") not in (None, "ORIGINAL_UNSCALED_RESIDUAL_INFINITY_NORM"):
            raise ResultClosureError("scaled merit leaked into acceptance history")


def _directory_size(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def _write_bytes_bounded(path: Path, data: bytes, staging: Path, maximum_bytes: int) -> None:
    if len(data) > maximum_bytes:
        raise ResultClosureError("single artifact exceeds maximum package size")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    if _directory_size(staging) > maximum_bytes:
        raise ResultClosureError("staged result package exceeds 1 GiB resource limit")


def package_schema_complete_result(staging: Path, raw_result: dict[str, Any], runtime: dict[str, Any], grant: dict[str, Any], release_sha: str, grant_sha: str, maximum_bytes: int, stdout_log: Path, stderr_log: Path) -> dict[str, Any]:
    if staging.exists():
        raise ResultClosureError("staging path already exists")
    staging.mkdir(parents=True)
    projected = sanitize_result(raw_result)
    profiles = projected.get("profile_artifacts", {})
    if not isinstance(profiles, dict):
        raise ResultClosureError("profile_artifacts must be mapping")
    profile_refs: dict[str, dict[str, str]] = {}
    artifact_rows: list[dict[str, str]] = []
    for candidate_id, profile in profiles.items():
        profile_path = staging / "profiles" / f"{candidate_id}.json"
        profile_bytes = canonical_json_bytes(profile)
        _write_bytes_bounded(profile_path, profile_bytes, staging, maximum_bytes)
        digest = sha256_file(profile_path)
        profile_refs[candidate_id] = {"path": str(profile_path.relative_to(staging)), "sha256": digest}
        artifact_rows.append({"path": str(profile_path.relative_to(staging)), "sha256": digest})
    for candidate in projected.get("candidate_inventory", []):
        candidate_id = str(candidate.get("candidate_id", ""))
        if candidate_id in profile_refs:
            candidate["profile_artifact_sha256"] = profile_refs[candidate_id]["sha256"]
    projected["profile_artifacts"] = profile_refs
    projected["schema"] = "universelab.ulsh-01.md2s-bvp.cp01r2-result.v1"
    projected["implementation_source_sha256"] = sha256_file(TARGET)
    projected["dependency_lock_sha256"] = DEPENDENCY_LOCK_SHA256
    projected["authorization_decision_id"] = grant["authorization_decision_id"]
    projected["execution_finished_utc"] = projected.get("execution_finished_utc") or datetime.now(timezone.utc).isoformat()
    projected["machine_environment"] = runtime
    projected["transaction_provenance"] = {
        "release_authorization_sha256": release_sha,
        "single_use_grant_sha256": grant_sha,
        "transaction_contract_sha256": sha256_file(CONTRACT),
        "source_bundle_sha256": source_bundle_sha256(load_json(CONTRACT)),
        "replay_permitted": False,
    }
    validate_result_closure(projected)
    result_path = staging / "result.json"
    _write_bytes_bounded(result_path, canonical_json_bytes(projected), staging, maximum_bytes)
    result_sha = sha256_file(result_path)
    artifact_rows.insert(0, {"path": "result.json", "sha256": result_sha})
    for label, source in (("execution-stdout.txt", stdout_log), ("execution-stderr.txt", stderr_log)):
        data = source.read_bytes() if source.is_file() else b""
        target = staging / label
        _write_bytes_bounded(target, data, staging, maximum_bytes)
        artifact_rows.append({"path": label, "sha256": sha256_file(target)})
    manifest = {
        "schema": "universelab.ulsh-01.md2s-bvp.cp01r2-artifact-manifest.v1",
        "run_id": RUN_ID,
        "authorization_decision_id": grant["authorization_decision_id"],
        "artifacts": artifact_rows,
        "result_sha256": result_sha,
        "all_listed_artifacts_hashed": True,
    }
    manifest_path = staging / "artifact-manifest.json"
    _write_bytes_bounded(manifest_path, canonical_json_bytes(manifest), staging, maximum_bytes)
    if _directory_size(staging) > maximum_bytes:
        raise ResultClosureError("final staged package exceeds 1 GiB limit")
    return {
        "result_sha256": result_sha,
        "artifact_manifest_sha256": sha256_file(manifest_path),
        "package_bytes": _directory_size(staging),
    }


def inspect_committed_result(result_dir: Path, expected: dict[str, Any] | None) -> dict[str, Any]:
    if not result_dir.is_dir():
        return {"result_package_committed": False, "verification_status": "NOT_COMMITTED"}
    result = result_dir / "result.json"
    manifest = result_dir / "artifact-manifest.json"
    if not result.is_file() or not manifest.is_file():
        return {"result_package_committed": True, "verification_status": "COMMITTED_DIRECTORY_INCOMPLETE"}
    observed = {"result_sha256": sha256_file(result), "artifact_manifest_sha256": sha256_file(manifest)}
    if expected and all(observed[key] == expected.get(key) for key in observed):
        status = "COMMITTED_HASHES_MATCH_PRECOMMIT_PACKAGE"
    else:
        status = "COMMITTED_PRESENT_EXPECTATION_UNAVAILABLE_OR_MISMATCH"
    return {"result_package_committed": True, "verification_status": status, **observed}


def supervised_target_execution(capability: dict[str, Any], grant_dir: Path, total_seconds: int, maximum_result_bytes: int) -> tuple[dict[str, Any], Path, Path]:
    capability_path = grant_dir / "target-capability.json"
    raw_pickle = grant_dir / "target-result.pickle"
    stdout_log = grant_dir / "target-stdout.txt"
    stderr_log = grant_dir / "target-stderr.txt"
    _atomic_json(capability_path, capability)
    deny_dir = _prepare_network_denial(grant_dir)
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(deny_dir) + (os.pathsep + existing_pythonpath if existing_pythonpath else "")
    env["UNIVERSELAB_NETWORK_POLICY"] = "DENY_CP01R2_SOLVER"
    command = [sys.executable, str(TARGET), "--execute-capability", str(capability_path), "--result-pickle", str(raw_pickle)]
    with stdout_log.open("wb") as out, stderr_log.open("wb") as err:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=out, stderr=err)
        try:
            return_code = process.wait(timeout=total_seconds)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise TransactionError("CP01R2 total 21600-second hard wall-clock limit exceeded")
    if return_code != 0:
        raise TransactionError(f"CP01R2 target process failed with return code {return_code}")
    if not raw_pickle.is_file():
        raise TransactionError("CP01R2 target did not produce transient result payload")
    if raw_pickle.stat().st_size > maximum_result_bytes:
        raise ResultClosureError("transient target result exceeds 1 GiB result budget")
    with raw_pickle.open("rb") as stream:
        raw = pickle.load(stream)
    if not isinstance(raw, dict):
        raise ResultClosureError("target result must be mapping")
    return raw, stdout_log, stderr_log


def static_preflight() -> dict[str, Any]:
    if RELEASE_PATH.exists() or GRANT_PATH.exists():
        raise TransactionError("D3H1 no-execution phase requires release/grant absence")
    if git_blob_sha1(TARGET) != EXPECTED_TARGET_BLOB:
        raise TransactionError("CP01R2 target blob drift")
    if git_blob_sha1(RESULT_SCHEMA) != EXPECTED_RESULT_SCHEMA_BLOB:
        raise TransactionError("CP01R2 result schema blob drift")
    d3 = load_json(D3_REVIEW)
    if d3["release_blockers"]["D3-B01"]["status"] != "OPEN_RELEASE_BLOCKER" or d3["release_blockers"]["D3-B02"]["status"] != "OPEN_RELEASE_BLOCKER":
        raise TransactionError("D3 blocker basis drift")
    contract = load_json(CONTRACT)
    if contract["status"] != "PASS_D3H1_IMPLEMENTED_NO_EXECUTION_PENDING_INDEPENDENT_REVIEW":
        raise TransactionError("D3H1 contract status drift")
    if contract["run_id"] != RUN_ID or contract["run_payload_sha256"] != RUN_PAYLOAD_SHA256 or contract["schedule_sha256"] != SCHEDULE_SHA256:
        raise TransactionError("D3H1 contract run binding drift")
    bundle = source_bundle_sha256(contract)
    target_spec = importlib.util.spec_from_file_location("ulsh_cp01r2_target_audit", TARGET)
    if target_spec is None or target_spec.loader is None:
        raise TransactionError("cannot load target audit")
    target = importlib.util.module_from_spec(target_spec)
    sys.modules[target_spec.name] = target
    target_spec.loader.exec_module(target)
    target_audit = target.audit_target()
    if target_audit["solver_calls"] != 0 or target_audit["physical_solve_executed"] is not False:
        raise TransactionError("target audit violated no-execution firewall")
    h3_source = H3_REFERENCE.read_text(encoding="utf-8")
    for fragment in ("COMMITTING_RESULT", "json_safe_diagnostic_projection", "claim_grant_atomically"):
        if fragment not in h3_source:
            raise TransactionError(f"H3 provenance invariant missing: {fragment}")
    return {
        "status": "PASS_WP3_D3H1_CP01R2_TRANSACTION_STATIC_PREFLIGHT_NO_EXECUTION",
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "schedule_sha256": SCHEDULE_SHA256,
        "source_bundle_sha256": bundle,
        "D3-B01": "IMPLEMENTED_PENDING_INDEPENDENT_REVIEW",
        "D3-B02": "IMPLEMENTED_PENDING_INDEPENDENT_REVIEW",
        "release_authorization_present": False,
        "single_use_grant_present": False,
        "solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
    }


def execute(transaction_root: Path) -> dict[str, Any]:
    release, grant, release_sha, grant_sha = validate_release_and_grant()
    transaction_root = transaction_root.resolve()
    transaction_root.mkdir(parents=True, exist_ok=True)
    result_dir, staging = pre_solver_output_collision_guard(transaction_root, grant)
    strict_startup_environment()
    runtime = runtime_attestation()
    limits = load_json(RESOURCE)["resource_limits"]
    maximum_result_bytes = int(limits["maximum_result_bytes"])
    maximum_memory_bytes = int(limits["maximum_memory_bytes"])
    total_seconds = int(limits["maximum_wall_clock_seconds_total"])
    stage_seconds = int(limits["maximum_wall_clock_seconds_per_seed_per_level"])
    grant_dir = claim_single_use_grant(transaction_root, grant, grant_sha)
    mark_state(grant_dir, "RUNNING", release_authorization_sha256=release_sha)
    transaction_started = time.monotonic()
    capability = {
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "schedule_sha256": SCHEDULE_SHA256,
        "grant_sha256": grant_sha,
        "transaction_contract_sha256": sha256_file(CONTRACT),
        "release_authorization_sha256": release_sha,
        "source_bundle_sha256": source_bundle_sha256(load_json(CONTRACT)),
        "physical_solve_authorized": True,
        "maximum_wall_clock_seconds_total": total_seconds,
        "maximum_wall_clock_seconds_per_seed_per_level": stage_seconds,
        "maximum_memory_bytes": maximum_memory_bytes,
    }
    package: dict[str, Any] | None = None
    try:
        raw, stdout_log, stderr_log = supervised_target_execution(capability, grant_dir, total_seconds, maximum_result_bytes)
        remaining = float(total_seconds) - (time.monotonic() - transaction_started)
        with post_target_wall_clock_limit(remaining):
            package = package_schema_complete_result(staging, raw, runtime, grant, release_sha, grant_sha, maximum_result_bytes, stdout_log, stderr_log)
            result_dir.parent.mkdir(parents=True, exist_ok=True)
            mark_state(grant_dir, "COMMITTING_RESULT", expected_result_directory=str(result_dir), expected_result_sha256=package["result_sha256"], expected_artifact_manifest_sha256=package["artifact_manifest_sha256"])
            os.replace(staging, result_dir)
            _fsync_directory(result_dir.parent)
            marker = {
                "schema": "universelab.ulsh-01.md2s-bvp.cp01r2-result-commit-marker.v1",
                "run_id": RUN_ID,
                "authorization_decision_id": grant["authorization_decision_id"],
                "result_sha256": package["result_sha256"],
                "artifact_manifest_sha256": package["artifact_manifest_sha256"],
                "committed_at_utc": datetime.now(timezone.utc).isoformat(),
                "replay_permitted": False,
            }
            _atomic_json(result_dir / "result-commit-marker.json", marker)
            marker_sha = sha256_file(result_dir / "result-commit-marker.json")
            mark_state(grant_dir, "SUCCEEDED", result_package_committed=True, result_directory=str(result_dir), result_sha256=package["result_sha256"], artifact_manifest_sha256=package["artifact_manifest_sha256"], result_commit_marker_sha256=marker_sha)
        return {"status": "SUCCEEDED", "result_directory": str(result_dir), **package, "result_commit_marker_sha256": marker_sha}
    except BaseException as exc:
        committed = inspect_committed_result(result_dir, package)
        if committed.get("verification_status") == "COMMITTED_HASHES_MATCH_PRECOMMIT_PACKAGE":
            mark_state(grant_dir, "COMMITTED_INDETERMINATE", error=f"{type(exc).__name__}: {exc}", **committed)
        else:
            mark_state(grant_dir, "FAILED", error=f"{type(exc).__name__}: {exc}", **committed)
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--transaction-root")
    args = parser.parse_args()
    if args.execute:
        if not args.transaction_root:
            raise AuthorizationDenied("--transaction-root required")
        print(json.dumps(execute(Path(args.transaction_root)), indent=2, sort_keys=True))
        return 0
    print(json.dumps(static_preflight(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
