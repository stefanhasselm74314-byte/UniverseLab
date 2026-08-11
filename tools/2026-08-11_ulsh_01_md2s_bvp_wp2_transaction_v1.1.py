#!/usr/bin/env python3
"""ULSH-01 / WP2-H hardened physical BVP transaction v1.1.

This module closes release-review blockers RR-B02, RR-B03 and RR-B04 while
preserving the single-use/replay firewall from WP2 v1.0. It does not create a
release authorization or grant and audit/CI paths never execute the physical
CP01R1 solver.

Physical execution remains unreachable unless later append-only v1.1 release
and single-use grant artifacts are created and exactly bind this hardened source
bundle. A spent grant is never retried, including after timeout, packaging
failure, resource failure or crash.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager, redirect_stdout
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import re
import signal
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

CONTRACT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_HardeningContract_v1.0.json"
TARGET_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.1.py"
BASE_TRANSACTION_PATH = ROOT / "tools/2026-08-10_ulsh_01_md2s_bvp_wp2_transaction_v1.0.py"
RUN_INPUT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"
RESOURCE_POLICY_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
RESULT_SCHEMA_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResultSchema_v0.1.json"
PREREG_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"
DEPENDENCY_LOCK_PATH = ROOT / "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C_v0.1.txt"

# Deliberately absent in this hardening build. Their creation is a later review act.
RELEASE_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.1.json"
GRANT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.1.json"

THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
)
NONCE_RE = re.compile(r"^[0-9a-f]{32,64}$")
SAFE_ARTIFACT_KEY_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
ALLOWED_FINAL_CLASSIFICATIONS = {
    "NUMERICAL_CANDIDATE_BACKGROUND_DIAGNOSTIC",
    "NUMERICAL_ROOT_REJECTED_BY_QA",
    "NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL",
    "MULTIPLE_NUMERICAL_CANDIDATE_BACKGROUNDS_DIAGNOSTIC",
    "NOT_EXECUTED_INPUT_CONTRACT_FAILURE",
    "NOT_EXECUTED_AUTHORIZATION_FAILURE",
    "NOT_EXECUTED_IMPLEMENTATION_FAILURE",
}

_BASE_SPEC = importlib.util.spec_from_file_location("ulsh_wp2_transaction_v10_base", BASE_TRANSACTION_PATH)
if _BASE_SPEC is None or _BASE_SPEC.loader is None:
    raise RuntimeError("unable to import WP2 v1.0 transaction utilities")
BASE = importlib.util.module_from_spec(_BASE_SPEC)
sys.modules[_BASE_SPEC.name] = BASE
_BASE_SPEC.loader.exec_module(BASE)


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


class ResultBudgetExceeded(ResourceFailure):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")


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
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


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
    # Hardened target imports only stdlib + frozen stdlib-only target until execution.
    return _dynamic_import(TARGET_PATH, "ulsh_wp2h_target_audit")


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


def verify_source_bindings(contract: dict[str, Any]) -> dict[str, str]:
    observed: dict[str, str] = {}
    for key, binding in contract["source_bindings"].items():
        path = ROOT / str(binding["path"])
        expected = str(binding["git_blob_sha1"])
        actual = git_blob_sha1(path)
        if actual != expected:
            raise ContractFailure(f"source binding drift for {key}: {actual} != {expected}")
        observed[key] = actual
    return observed


def source_bundle_sha256(contract: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(contract["source_bindings"]))


def static_preflight() -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    if contract.get("run_id") != RUN_ID or contract.get("frozen_payload_sha256") != FROZEN_PAYLOAD_SHA256:
        raise ContractFailure("WP2-H contract run binding drift")
    if contract.get("status") != "PASS_WP2_HARDENING_IMPLEMENTED_NO_SOLVE_PENDING_REREVIEW":
        raise ContractFailure("WP2-H contract status drift")
    if contract.get("physical_solve_authorized") is not False or contract.get("physical_solve_executed") is not False:
        raise ContractFailure("WP2-H must remain no-solve and unreleased")
    closures = contract.get("release_review_blocker_closure", {})
    if set(closures) != {"RR-B01", "RR-B02", "RR-B03", "RR-B04"}:
        raise ContractFailure("WP2-H blocker closure inventory drift")
    if any(item.get("status") != "IMPLEMENTED_PENDING_REREVIEW" for item in closures.values()):
        raise ContractFailure("all four WP2-H blockers must be implemented pending re-review")
    observed = verify_source_bindings(contract)
    if sha256_file(DEPENDENCY_LOCK_PATH) != DEPENDENCY_LOCK_SHA256:
        raise ContractFailure("canonical Background3C dependency lock SHA-256 drift")

    target = load_target_audit_module()
    target_audit = target.audit_target()
    if target_audit.get("status") != "PASS_WP2_HARDENED_TARGET_NO_SOLVE":
        raise ContractFailure("hardened target audit failed")
    if target_audit.get("planned_entry_count") != 35 or target_audit.get("a_F") != "1/4":
        raise ContractFailure("hardened target schedule/payload drift")
    if target_audit.get("solver_calls") != 0 or target_audit.get("physical_solve_executed") is not False:
        raise ContractFailure("WP2-H audit crossed numerical execution firewall")
    if not target_audit.get("stage_timeout_enforced_in_target"):
        raise ContractFailure("RR-B01 closure drift")
    if not target_audit.get("schema_complete_primary_capture") or not target_audit.get("schema_complete_independent_capture"):
        raise ContractFailure("RR-B03 closure drift")

    return {
        "status": "PASS_WP2_HARDENING_STATIC_PREFLIGHT_NO_SOLVE",
        "run_id": RUN_ID,
        "frozen_payload_sha256": FROZEN_PAYLOAD_SHA256,
        "schedule_sha256": target_audit["schedule_sha256"],
        "planned_entry_count": 35,
        "source_git_blob_sha1": observed,
        "source_bundle_sha256": source_bundle_sha256(contract),
        "release_authorization_present": RELEASE_PATH.exists(),
        "single_use_grant_present": GRANT_PATH.exists(),
        "release_review_blockers_implemented": sorted(closures),
        "solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
    }


def _cpu_identity() -> dict[str, Any]:
    descriptors: list[str] = []
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.is_file():
        try:
            for line in cpuinfo.read_text(encoding="utf-8", errors="replace").splitlines():
                key, sep, value = line.partition(":")
                if sep and key.strip().lower() in {"model name", "hardware", "processor"} and value.strip():
                    descriptors.append(value.strip())
                    if len(descriptors) >= 4:
                        break
        except OSError:
            pass
    processor = platform.processor().strip()
    if processor:
        descriptors.append(processor)
    descriptors = list(dict.fromkeys(descriptors))
    identity = {
        "machine": platform.machine(),
        "processor": processor,
        "platform": platform.platform(),
        "uname": list(platform.uname()),
        "descriptors": descriptors,
        "logical_cores": os.cpu_count(),
    }
    if not identity["machine"] or not identity["platform"]:
        raise ResourceFailure("positive CPU/platform identity record unavailable")
    if not descriptors and not processor:
        # machine + uname are still positive architecture identity, but record the fallback explicitly.
        identity["identity_fallback"] = "ARCHITECTURE_AND_UNAME_ONLY"
    return identity


def _blas_lapack_metadata() -> dict[str, Any]:
    try:
        import numpy as np
        import scipy
    except Exception as exc:
        raise ResourceFailure(f"cannot import frozen NumPy/SciPy for BLAS/LAPACK attestation: {exc}") from exc

    numpy_buffer = io.StringIO()
    scipy_buffer = io.StringIO()
    with redirect_stdout(numpy_buffer):
        np.__config__.show()
    with redirect_stdout(scipy_buffer):
        scipy.show_config()
    numpy_text = numpy_buffer.getvalue().strip()
    scipy_text = scipy_buffer.getvalue().strip()
    combined = f"{numpy_text}\n{scipy_text}".lower()
    if not numpy_text or not scipy_text or ("blas" not in combined and "lapack" not in combined):
        raise ResourceFailure("BLAS/LAPACK implementation metadata is incomplete")
    return {
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "numpy_config": numpy_text,
        "scipy_config": scipy_text,
    }


def runtime_attestation() -> dict[str, Any]:
    expected = expected_dependencies()
    observed: dict[str, str] = {}
    for name in expected:
        try:
            observed[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            observed[name] = "NOT_INSTALLED"
    return {
        "schema": "universelab.ulsh-01.wp2-h.runtime-attestation.v1",
        "created_utc": utc_now(),
        "python": {
            "implementation": platform.python_implementation(),
            "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "executable_name": Path(sys.executable).name,
            "pythonhashseed": os.environ.get("PYTHONHASHSEED", "UNSET"),
        },
        "dependencies_expected": expected,
        "dependencies_observed": observed,
        "thread_environment": {key: os.environ.get(key, "UNSET") for key in THREAD_ENV_KEYS},
        "cpu_identity": _cpu_identity(),
        "blas_lapack": _blas_lapack_metadata(),
        "network_policy": "FORBIDDEN_DURING_EXECUTION",
        "gpu_policy": "FORBIDDEN",
        "randomness_policy": "FORBIDDEN",
        "run_id": RUN_ID,
        "frozen_payload_sha256": FROZEN_PAYLOAD_SHA256,
    }


def validate_runtime() -> dict[str, Any]:
    att = runtime_attestation()
    if sys.version_info[:2] != (3, 12):
        raise ResourceFailure(f"Python 3.12 required, found {att['python']['version']}")
    if att["python"]["pythonhashseed"] != "0":
        raise ResourceFailure("execute requires process startup with PYTHONHASHSEED=0")
    if att["dependencies_observed"] != att["dependencies_expected"]:
        raise ResourceFailure("installed dependency versions differ from frozen Background3C lock")
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
    if not resource["reproducibility"]["cpu_and_blas_metadata_required"]:
        raise ResourceFailure("CPU/BLAS reproducibility requirement unexpectedly disabled")
    return att


def validate_release_and_grant(now: datetime | None = None) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    if not RELEASE_PATH.is_file() or not GRANT_PATH.is_file():
        raise AuthorizationDenied("WP2-H v1.1 release authorization and/or single-use grant is absent")
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
    if release.get("schema") != protocol["release_schema"]:
        raise AuthorizationDenied("unexpected WP2-H release schema")
    if release.get("status") != "GRANTED" or release.get("physical_solve_authorized") is not True:
        raise AuthorizationDenied("physical solve release is not GRANTED")
    if release.get("run_id") != RUN_ID or release.get("frozen_payload_sha256") != FROZEN_PAYLOAD_SHA256:
        raise AuthorizationDenied("release is bound to another run")
    if release.get("grant_sha256") != grant_sha:
        raise AuthorizationDenied("release does not pin exact grant bytes")
    if release.get("transaction_contract_sha256") != contract_sha:
        raise AuthorizationDenied("release does not pin exact WP2-H contract bytes")
    if release.get("source_bundle_sha256") != source_bundle:
        raise AuthorizationDenied("release source-bundle binding mismatch")

    if grant.get("schema") != protocol["grant_schema"]:
        raise AuthorizationDenied("unexpected WP2-H grant schema")
    for key in ("single_use", "physical_solve_authorized", "no_retry", "no_scan", "no_fallback"):
        if grant.get(key) is not True:
            raise AuthorizationDenied(f"grant scope flag missing: {key}")
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
    decision_id = str(grant.get("authorization_decision_id", ""))
    if not decision_id.startswith("UL-DEC-"):
        raise AuthorizationDenied("grant authorization_decision_id is invalid")

    nonce = str(grant.get("grant_nonce", ""))
    if not NONCE_RE.fullmatch(nonce):
        raise AuthorizationDenied("grant nonce must be 128-256 bits lowercase hex")
    clock = now or datetime.now(timezone.utc)
    issued_at = parse_utc(str(grant.get("issued_at", "")))
    not_before = parse_utc(str(grant.get("not_before", "")))
    expires_at = parse_utc(str(grant.get("expires_at", "")))
    if not (issued_at <= not_before < expires_at):
        raise AuthorizationDenied("invalid grant time ordering")
    if (expires_at - not_before).total_seconds() > int(protocol["maximum_validity_seconds"]):
        raise AuthorizationDenied("grant validity window exceeds contract maximum")
    if clock < not_before or clock >= expires_at:
        raise AuthorizationDenied("grant is outside its validity window")
    return release, grant, release_sha, grant_sha


def enforce_process_limits() -> None:
    limits = load_json(RESOURCE_POLICY_PATH)["resource_limits"]
    for key in THREAD_ENV_KEYS:
        os.environ[key] = "1"
    if os.name == "posix":
        import resource
        memory = int(limits["maximum_memory_bytes"])
        cpu = int(limits["maximum_wall_clock_seconds_total"])
        resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
        current_soft, current_hard = resource.getrlimit(resource.RLIMIT_CPU)
        hard = cpu + 1 if current_hard in (-1, resource.RLIM_INFINITY) else min(current_hard, cpu + 1)
        resource.setrlimit(resource.RLIMIT_CPU, (min(cpu, hard), hard))


@contextmanager
def network_denied():
    import socket
    original_socket = socket.socket
    original_create = socket.create_connection
    original_getaddrinfo = socket.getaddrinfo

    def denied(*_args, **_kwargs):
        raise RuntimeError("network access forbidden by WP2-H resource policy")

    socket.socket = denied  # type: ignore[assignment]
    socket.create_connection = denied  # type: ignore[assignment]
    socket.getaddrinfo = denied  # type: ignore[assignment]
    try:
        yield
    finally:
        socket.socket = original_socket  # type: ignore[assignment]
        socket.create_connection = original_create  # type: ignore[assignment]
        socket.getaddrinfo = original_getaddrinfo  # type: ignore[assignment]


@contextmanager
def packaging_wall_clock_limit(seconds: float):
    if seconds <= 0.0:
        raise ResourceFailure("no total wall-clock budget remains for immutable result packaging")
    if os.name != "posix" or not hasattr(signal, "SIGALRM") or not hasattr(signal, "setitimer"):
        raise ResourceFailure("POSIX setitimer required for fail-closed packaging wall-clock enforcement")

    def handler(_signum, _frame):
        raise ResourceFailure("total wall-clock budget exceeded during immutable result packaging")

    previous = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)
    if previous_timer[0] > 0.0:
        raise ResourceFailure("unexpected pre-existing ITIMER_REAL before packaging")
    signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, float(seconds))
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, previous)


class BoundedStagingWriter:
    """Atomic staging writer with a cumulative immutable byte ceiling."""

    def __init__(self, root: Path, maximum_bytes: int):
        self.root = root.resolve()
        self.maximum_bytes = int(maximum_bytes)
        self.bytes_written = 0
        if self.maximum_bytes <= 0:
            raise ResultBudgetExceeded("result byte budget must be positive")

    def _resolve(self, relative: str) -> Path:
        target = (self.root / relative).resolve()
        if target == self.root or self.root not in target.parents:
            raise ContractFailure(f"artifact path escapes staging root: {relative}")
        return target

    def write_bytes(self, relative: str, data: bytes) -> Path:
        projected = self.bytes_written + len(data)
        if projected > self.maximum_bytes:
            raise ResultBudgetExceeded(
                f"result byte budget exceeded before commit: {projected} > {self.maximum_bytes}"
            )
        path = self._resolve(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
        with temp.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        BASE._fsync_directory(path.parent)
        self.bytes_written = projected
        return path

    def write_json(self, relative: str, payload: dict[str, Any]) -> Path:
        return self.write_bytes(relative, canonical_json_bytes(payload) + b"\n")


def _parameter_topology_hashes() -> dict[str, str]:
    run_input = load_json(RUN_INPUT_PATH)
    payload = run_input["frozen_run_payload"]
    return {
        "model_parameters_sha256": sha256_bytes(canonical_json_bytes(payload["model_parameters_ordered"])),
        "topological_sector_sha256": sha256_bytes(canonical_json_bytes(payload["topological_sector_ordered"])),
        "full_frozen_payload_sha256": FROZEN_PAYLOAD_SHA256,
    }


def _validate_result_payload(result: dict[str, Any]) -> None:
    schema = load_json(RESULT_SCHEMA_PATH)
    if result.get("schema") != schema["schema"]:
        raise ContractFailure("result schema identifier drift")
    missing = sorted(set(schema["required_top_level_fields"]) - set(result))
    if missing:
        raise ContractFailure(f"schema-complete result missing top-level fields: {missing}")
    if result.get("final_classification") not in ALLOWED_FINAL_CLASSIFICATIONS:
        raise ContractFailure("result final classification outside frozen vocabulary")
    if result.get("physical_evidence_effect") != "NONE":
        raise ContractFailure("result must preserve physical_evidence_effect=NONE")
    for field in schema["primary_backend_required_fields"]:
        if field not in result["primary_backend"]:
            raise ContractFailure(f"primary_backend missing required field: {field}")
    for field in schema["independent_backend_required_fields"]:
        if field not in result["independent_backend"]:
            raise ContractFailure(f"independent_backend missing required field: {field}")
    for index, candidate in enumerate(result["candidate_inventory"]):
        missing_candidate = sorted(set(schema["candidate_required_fields"]) - set(candidate))
        if missing_candidate:
            raise ContractFailure(f"candidate {index} missing required fields: {missing_candidate}")
        digest = candidate.get("profile_artifact_sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ContractFailure(f"candidate {index} profile artifact digest is not closed")


def _artifact_manifest_entries(root: Path) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "artifact-manifest.json":
            continue
        relative = path.relative_to(root).as_posix()
        entries[relative] = {
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
    return entries


def package_schema_complete_result(
    staging: Path,
    raw_result: dict[str, Any],
    runtime: dict[str, Any],
    grant: dict[str, Any],
    release_sha: str,
    grant_sha: str,
    maximum_result_bytes: int,
) -> dict[str, Any]:
    if raw_result.get("schema_complete_capture") is not True:
        raise ContractFailure("hardened target did not return schema-complete capture")
    if raw_result.get("run_id") != RUN_ID or raw_result.get("frozen_input_sha256") != FROZEN_PAYLOAD_SHA256:
        raise ContractFailure("raw target result run binding drift")
    if raw_result.get("physical_evidence_effect") != "NONE":
        raise ContractFailure("raw target result crossed evidence firewall")

    staging.mkdir(parents=True, exist_ok=False)
    writer = BoundedStagingWriter(staging, maximum_result_bytes)
    contract = load_json(CONTRACT_PATH)
    bundle_sha = source_bundle_sha256(contract)
    run_input = load_json(RUN_INPUT_PATH)
    prereg = load_json(PREREG_PATH)

    writer.write_json("run-input.json", run_input)
    writer.write_json("runtime-attestation.json", runtime)
    provenance = {
        "schema": "universelab.ulsh-01.wp2-h.provenance.v1",
        "run_id": RUN_ID,
        "frozen_payload_sha256": FROZEN_PAYLOAD_SHA256,
        "parameter_topology_hashes": _parameter_topology_hashes(),
        "source_bundle_sha256": bundle_sha,
        "source_bindings": contract["source_bindings"],
        "backend_bindings": contract["backend_bindings"],
        "dependency_lock_sha256": DEPENDENCY_LOCK_SHA256,
        "release_authorization_sha256": release_sha,
        "single_use_grant_sha256": grant_sha,
        "authorization_decision_id": grant["authorization_decision_id"],
        "physical_evidence_effect": "NONE",
    }
    writer.write_json("provenance.json", provenance)
    execution_log = {
        "schema": "universelab.ulsh-01.wp2-h.execution-log.v1",
        "run_id": RUN_ID,
        "schedule_sha256": raw_result["schedule_sha256"],
        "planned_schedule_entries": raw_result["planned_schedule_entries"],
        "matrix_entries": raw_result["matrix_entries"],
        "stage_timeout_count": raw_result["stage_timeout_count"],
        "total_budget_exhausted": raw_result["total_budget_exhausted"],
        "execution_elapsed_wall_clock_seconds": raw_result["execution_elapsed_wall_clock_seconds"],
    }
    writer.write_json("per-seed-execution-log.json", execution_log)

    profile_hashes: dict[str, str] = {}
    for key, payload in sorted(raw_result.get("profile_artifacts", {}).items()):
        if not SAFE_ARTIFACT_KEY_RE.fullmatch(str(key)):
            raise ContractFailure(f"unsafe candidate profile artifact key: {key}")
        path = writer.write_json(f"profiles/{key}.json", payload)
        profile_hashes[str(key)] = sha256_file(path)

    candidate_inventory = json.loads(json.dumps(raw_result["candidate_inventory"], allow_nan=False))
    for candidate in candidate_inventory:
        key = str(candidate.pop("profile_artifact_key", ""))
        if key not in profile_hashes:
            raise ContractFailure(f"candidate profile artifact missing for key: {key}")
        candidate["profile_artifact_sha256"] = profile_hashes[key]

    result_payload = {
        "schema": load_json(RESULT_SCHEMA_PATH)["schema"],
        "run_id": RUN_ID,
        "run_payload_sha256": FROZEN_PAYLOAD_SHA256,
        "implementation_source_sha256": bundle_sha,
        "dependency_lock_sha256": DEPENDENCY_LOCK_SHA256,
        "authorization_decision_id": grant["authorization_decision_id"],
        "execution_started_utc": raw_result["execution_started_utc"],
        "execution_finished_utc": utc_now(),
        "machine_environment": runtime,
        "primary_backend": raw_result["primary_backend"],
        "independent_backend": raw_result["independent_backend"],
        "candidate_inventory": candidate_inventory,
        "acceptance_audit": raw_result["acceptance_audit"],
        "final_classification": raw_result["final_classification"],
        "physical_evidence_effect": "NONE",
        "forbidden_inferences": raw_result["forbidden_inferences"],
    }
    _validate_result_payload(result_payload)
    result_path = writer.write_json("result.json", result_payload)

    mandatory = set(prereg["mandatory_run_artifacts"])
    if "machine-readable final classification" not in mandatory or "forbidden-inference statement" not in mandatory:
        raise ContractFailure("preregistration mandatory artifact vocabulary drift")

    manifest = {
        "schema": "universelab.ulsh-01.wp2-h.artifact-manifest.v1",
        "run_id": RUN_ID,
        "authorization_decision_id": grant["authorization_decision_id"],
        "canonical_repository_promotion_target": (
            f"artifacts/hzt-m0/md2s/background3c/{RUN_ID}/{grant['authorization_decision_id']}/"
        ),
        "promotion_mode": "BYTE_FOR_BYTE_ONLY_AFTER_SEPARATE_REVIEW_NO_RECOMPUTATION",
        "manifest_excludes_itself": True,
        "artifacts": _artifact_manifest_entries(staging),
        "result_sha256": sha256_file(result_path),
        "maximum_result_bytes": int(maximum_result_bytes),
        "bytes_before_manifest": writer.bytes_written,
        "physical_evidence_effect": "NONE",
    }
    manifest_path = writer.write_json("artifact-manifest.json", manifest)
    final_bytes = sum(path.stat().st_size for path in staging.rglob("*") if path.is_file())
    if final_bytes > int(maximum_result_bytes):
        raise ResultBudgetExceeded(
            f"final staged package exceeds result byte budget: {final_bytes} > {maximum_result_bytes}"
        )
    return {
        "result_sha256": sha256_file(result_path),
        "artifact_manifest_sha256": sha256_file(manifest_path),
        "profile_artifact_count": len(profile_hashes),
        "final_package_bytes": final_bytes,
        "maximum_result_bytes": int(maximum_result_bytes),
        "final_classification": result_payload["final_classification"],
    }


def execute(transaction_root: Path) -> dict[str, Any]:
    # No numerical library/backend import occurs before exact later release+grant validation.
    preflight = static_preflight()
    release, grant, release_sha, grant_sha = validate_release_and_grant()
    runtime = validate_runtime()
    external_root = BASE.ensure_external_transaction_root(transaction_root)
    grant_dir = BASE.claim_single_use_grant(external_root, grant, grant_sha)
    BASE.mark_state(grant_dir, "RUNNING", release_authorization_sha256=release_sha)

    contract_sha = sha256_file(CONTRACT_PATH)
    target = load_target_audit_module()
    limits = load_json(RESOURCE_POLICY_PATH)["resource_limits"]
    capability = target.TargetExecutionCapability(
        run_id=RUN_ID,
        frozen_payload_sha256=FROZEN_PAYLOAD_SHA256,
        schedule_sha256=preflight["schedule_sha256"],
        grant_sha256=grant_sha,
        transaction_contract_sha256=contract_sha,
        release_authorization_sha256=release_sha,
        physical_solve_authorized=True,
        maximum_wall_clock_seconds_total=int(limits["maximum_wall_clock_seconds_total"]),
        maximum_wall_clock_seconds_per_seed_per_level=int(limits["maximum_wall_clock_seconds_per_seed_per_level"]),
    )

    try:
        enforce_process_limits()
        with network_denied():
            raw_result = target.execute_physical_schedule(capability)
        elapsed = float(raw_result["execution_elapsed_wall_clock_seconds"])
        remaining = float(limits["maximum_wall_clock_seconds_total"]) - elapsed
        result_dir = external_root / "results" / str(grant["grant_nonce"])
        if result_dir.exists():
            raise ExecutionFailure("immutable result directory already exists")
        staging = external_root / "results" / f".{grant['grant_nonce']}.staging-{os.getpid()}"
        with packaging_wall_clock_limit(remaining):
            package = package_schema_complete_result(
                staging,
                raw_result,
                runtime,
                grant,
                release_sha,
                grant_sha,
                int(limits["maximum_result_bytes"]),
            )
            result_dir.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staging, result_dir)
            BASE._fsync_directory(result_dir.parent)
        BASE.mark_state(
            grant_dir,
            "SUCCEEDED",
            result_directory=str(result_dir),
            result_sha256=package["result_sha256"],
            final_classification=package["final_classification"],
            replay_permitted=False,
        )
        return {
            "status": "PHYSICAL_TRANSACTION_COMPLETED_SCHEMA_COMPLETE_RESULT_QUARANTINED",
            "run_id": RUN_ID,
            "result_directory": str(result_dir),
            "result_sha256": package["result_sha256"],
            "final_classification": package["final_classification"],
            "final_package_bytes": package["final_package_bytes"],
            "grant_spent": True,
            "replay_permitted": False,
            "physical_evidence_effect": "NONE",
        }
    except BaseException as exc:
        try:
            failure = {
                "schema": "universelab.ulsh-01.wp2-h.failure-record.v1",
                "run_id": RUN_ID,
                "created_utc": utc_now(),
                "error_type": type(exc).__name__,
                "error": str(exc),
                "failure_classification": (
                    "RESULT_BYTE_BUDGET_EXCEEDED_AFTER_GRANT_SPEND"
                    if isinstance(exc, ResultBudgetExceeded)
                    else "HARDENED_TRANSACTION_FAILED_AFTER_GRANT_SPEND"
                ),
                "result_package_committed": False,
                "grant_spent": True,
                "replay_permitted": False,
                "retry_requires_new_grant": True,
                "physical_evidence_effect": "NONE",
            }
            BASE.atomic_json(grant_dir / "failure.json", failure)
            BASE.mark_state(
                grant_dir,
                "FAILED" if isinstance(exc, Exception) else "CRASHED_OR_INDETERMINATE",
                error_type=type(exc).__name__,
                replay_permitted=False,
                retry_requires_new_grant=True,
            )
        finally:
            pass
        raise


def self_test_budget(temp_root: Path) -> dict[str, Any]:
    root = BASE.ensure_external_transaction_root(temp_root)
    staging = root / "budget-test"
    staging.mkdir(parents=True, exist_ok=False)
    writer = BoundedStagingWriter(staging, 64)
    writer.write_bytes("a.bin", b"a" * 32)
    blocked = False
    try:
        writer.write_bytes("b.bin", b"b" * 33)
    except ResultBudgetExceeded:
        blocked = True
    if not blocked or (staging / "b.bin").exists():
        raise ResultBudgetExceeded("cumulative result-byte self-test failed")
    return {
        "status": "PASS_RESULT_BYTE_BUDGET_SELF_TEST_NO_SOLVE",
        "bytes_written": writer.bytes_written,
        "overflow_blocked": True,
        "solver_calls": 0,
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("audit")
    budget = sub.add_parser("self-test-budget")
    budget.add_argument("--transaction-root", required=True)
    run = sub.add_parser("execute")
    run.add_argument("--transaction-root", required=True)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "audit":
            print(json.dumps(static_preflight(), indent=2, sort_keys=True))
            return 0
        if args.command == "self-test-budget":
            print(json.dumps(self_test_budget(Path(args.transaction_root)), indent=2, sort_keys=True))
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
    except BASE.ReplayOrCrash as exc:
        print(f"REPLAY_OR_CRASH: {exc}", file=sys.stderr)
        return EXIT_REPLAY_OR_CRASH
    except Exception as exc:
        print(f"EXECUTION_FAILURE: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_EXECUTION_FAILURE
    return EXIT_EXECUTION_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
