#!/usr/bin/env python3
"""Fail-closed execution package for C-PHYS-M1 Background-3C4.

This module implements the source-bound runner, environment attestation,
resource envelope, atomic result writer, classification engine, interruption
protocol, and guarded primary/independent root adapters.

The package is intentionally NOT authorized to execute CP01R1. The `audit`
and `self-test` commands never call either numerical root solver. The `run`
command verifies a future append-only grant before importing numerical
backends or creating an output directory; absent that grant it exits with 73.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import sys
import tempfile
from typing import Any, Callable, Iterable
import uuid

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
RUN_PAYLOAD_SHA256 = "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302"
EXIT_NOT_AUTHORIZED = 73
EXIT_CONTRACT_FAILURE = 74
EXIT_RESOURCE_FAILURE = 75
EXIT_PARTIAL_ARTIFACT = 76
EXIT_AUDIT_FAILURE = 77

AUTHORIZATION_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
RESULT_SCHEMA_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResultSchema_v0.1.json"
RESOURCE_POLICY_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
RUN_INPUT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"
CONTRACT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C4ExecutionRunnerContract_v0.1.json"

PRIMARY_KERNEL_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py"
INDEPENDENT_BACKEND_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_independent_backend_v0.1.py"

PACKAGE_SOURCE_PATHS = (
    "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json",
    "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CImplementationContract_v0.2.json",
    "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CIndependentBackendContract_v0.1.json",
    "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CDualBackendPackageContract_v0.1.json",
    "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C2DualBackendAuditResult_v0.1.json",
    "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C3ExecutionAuthorizationReview_v0.1.json",
    "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResultSchema_v0.1.json",
    "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json",
    "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C4ExecutionRunnerContract_v0.1.json",
    "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C_v0.1.txt",
    "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.1.py",
    "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py",
    "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_independent_backend_v0.1.py",
    "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_execution_runner_v0.1.py",
)

REQUIRED_DEPENDENCIES = ("numpy", "scipy", "sympy", "mpmath")
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
ALLOWED_FINAL_CLASSIFICATIONS = {
    "NUMERICAL_CANDIDATE_BACKGROUND_DIAGNOSTIC",
    "NUMERICAL_ROOT_REJECTED_BY_QA",
    "NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL",
    "MULTIPLE_NUMERICAL_CANDIDATE_BACKGROUNDS_DIAGNOSTIC",
    "NOT_EXECUTED_INPUT_CONTRACT_FAILURE",
    "NOT_EXECUTED_AUTHORIZATION_FAILURE",
    "NOT_EXECUTED_IMPLEMENTATION_FAILURE",
}


class PackageError(RuntimeError):
    """Base execution-package error."""


class AuthorizationDenied(PackageError):
    """Raised before any numerical backend may be imported or called."""


class ContractFailure(PackageError):
    """Raised for contract/hash/schema mismatches."""


class ResourceFailure(PackageError):
    """Raised for resource-policy violations."""


class ArtifactFailure(PackageError):
    """Raised for atomic-artifact failures."""


@dataclass(frozen=True)
class ExecutionCapability:
    run_id: str
    authorization_decision_id: str
    package_manifest_sha256: str
    grant_path: str


@dataclass(frozen=True)
class ResourceEnvelope:
    wall_clock_total_seconds: int
    wall_clock_per_seed_level_seconds: int
    memory_bytes: int
    cpu_threads: int
    result_bytes: int

    @classmethod
    def from_policy(cls, policy: dict[str, Any]) -> "ResourceEnvelope":
        limits = policy["resource_limits"]
        return cls(
            wall_clock_total_seconds=int(limits["maximum_wall_clock_seconds_total"]),
            wall_clock_per_seed_level_seconds=int(limits["maximum_wall_clock_seconds_per_seed_per_level"]),
            memory_bytes=int(limits["maximum_memory_bytes"]),
            cpu_threads=int(limits["maximum_cpu_threads"]),
            result_bytes=int(limits["maximum_result_bytes"]),
        )

    def validate_static(self) -> None:
        if self.cpu_threads != 1:
            raise ResourceFailure("CP01R1 requires exactly one CPU thread")
        if min(
            self.wall_clock_total_seconds,
            self.wall_clock_per_seed_level_seconds,
            self.memory_bytes,
            self.result_bytes,
        ) <= 0:
            raise ResourceFailure("resource limits must be strictly positive")
        if self.wall_clock_per_seed_level_seconds > self.wall_clock_total_seconds:
            raise ResourceFailure("per-stage timeout exceeds total wall-clock budget")

    def subprocess_environment(self) -> dict[str, str]:
        env = os.environ.copy()
        for key in THREAD_ENV_KEYS:
            env[key] = str(self.cpu_threads)
        env["PYTHONHASHSEED"] = "0"
        return env

    def posix_preexec_fn(self) -> Callable[[], None] | None:
        if os.name != "posix":
            return None

        def apply_limits() -> None:
            import resource
            resource.setrlimit(resource.RLIMIT_AS, (self.memory_bytes, self.memory_bytes))
            resource.setrlimit(
                resource.RLIMIT_CPU,
                (self.wall_clock_total_seconds, self.wall_clock_total_seconds + 1),
            )
        return apply_limits


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractFailure(f"missing required file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ContractFailure(f"invalid JSON: {path.relative_to(ROOT)}") from exc
    if not isinstance(value, dict):
        raise ContractFailure(f"top-level JSON object required: {path.relative_to(ROOT)}")
    return value


def package_source_manifest(root: Path = ROOT) -> dict[str, str]:
    manifest: dict[str, str] = {}
    for relative in PACKAGE_SOURCE_PATHS:
        path = root / relative
        if not path.is_file():
            raise ContractFailure(f"missing package source: {relative}")
        manifest[relative] = sha256_file(path)
    return manifest


def package_manifest_sha256(root: Path = ROOT) -> str:
    return sha256_bytes(canonical_json_bytes(package_source_manifest(root)))


def dependency_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in REQUIRED_DEPENDENCIES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "NOT_INSTALLED"
    return versions


def environment_attestation(package_digest: str) -> dict[str, Any]:
    thread_environment = {key: os.environ.get(key, "UNSET") for key in THREAD_ENV_KEYS}
    return {
        "schema": "universelab.background-3c4-environment-attestation.v0.1",
        "created_utc": utc_now(),
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "executable_name": Path(sys.executable).name,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "dependencies": dependency_versions(),
        "thread_environment": thread_environment,
        "network_policy": "FORBIDDEN_DURING_EXECUTION",
        "gpu_policy": "FORBIDDEN",
        "randomness_policy": "FORBIDDEN",
        "package_manifest_sha256": package_digest,
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
    }


def validate_environment(attestation: dict[str, Any], *, require_dependencies: bool = True) -> None:
    if attestation["python"]["implementation"] != "CPython":
        raise ContractFailure("CPython is required")
    major_minor = ".".join(attestation["python"]["version"].split(".")[:2])
    if major_minor != "3.12":
        raise ContractFailure(f"Python 3.12 required, found {major_minor}")
    if require_dependencies:
        missing = [
            name for name, version in attestation["dependencies"].items()
            if version == "NOT_INSTALLED"
        ]
        if missing:
            raise ContractFailure(f"missing frozen dependencies: {missing}")
    for key, value in attestation["thread_environment"].items():
        if value not in {"UNSET", "1"}:
            raise ResourceFailure(f"{key} must be unset or 1, found {value}")


def validate_run_contracts() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    run_input = load_json(RUN_INPUT_PATH)
    result_schema = load_json(RESULT_SCHEMA_PATH)
    resource_policy = load_json(RESOURCE_POLICY_PATH)
    contract = load_json(CONTRACT_PATH)

    if run_input.get("frozen_run_payload_sha256") != RUN_PAYLOAD_SHA256:
        raise ContractFailure("CP01R1 run-payload hash mismatch")
    if run_input.get("frozen_run_payload", {}).get("run_id") != RUN_ID:
        raise ContractFailure("CP01R1 run-id mismatch")
    if result_schema.get("run_id") != RUN_ID:
        raise ContractFailure("result schema run-id mismatch")
    if resource_policy.get("run_id") != RUN_ID:
        raise ContractFailure("resource policy run-id mismatch")
    if contract.get("run_id") != RUN_ID:
        raise ContractFailure("3C4 contract run-id mismatch")
    if contract.get("run_payload_sha256") != RUN_PAYLOAD_SHA256:
        raise ContractFailure("3C4 contract payload hash mismatch")
    if set(result_schema.get("allowed_final_classifications", [])) != ALLOWED_FINAL_CLASSIFICATIONS:
        raise ContractFailure("result classification vocabulary drift")
    if result_schema.get("current_state", {}).get("solver_executed") is not False:
        raise ContractFailure("result schema may not claim execution")
    if resource_policy.get("current_state", {}).get("execution_authorized") is not False:
        raise ContractFailure("resource policy may not claim authorization")
    return result_schema, resource_policy, contract


class GrantVerifier:
    def __init__(self, expected_package_digest: str):
        self.expected_package_digest = expected_package_digest

    def verify(self, path: Path = AUTHORIZATION_PATH) -> ExecutionCapability:
        if not path.is_file():
            raise AuthorizationDenied("append-only execution grant is absent")
        grant = load_json(path)
        required = {
            "schema",
            "status",
            "authorized",
            "run_id",
            "run_payload_sha256",
            "authorization_decision_id",
            "execution_package_manifest_sha256",
            "scope",
        }
        missing = sorted(required - set(grant))
        if missing:
            raise AuthorizationDenied(f"grant missing fields: {missing}")
        if grant["schema"] != "universelab.hzt-m0-s6-c-phys-m1.background-3c-execution-authorization.v0.2":
            raise AuthorizationDenied("unexpected grant schema")
        if grant["status"] != "GRANTED" or grant["authorized"] is not True:
            raise AuthorizationDenied("authorization is not GRANTED")
        if grant["run_id"] != RUN_ID or grant["run_payload_sha256"] != RUN_PAYLOAD_SHA256:
            raise AuthorizationDenied("grant is bound to a different immutable run")
        if grant["execution_package_manifest_sha256"] != self.expected_package_digest:
            raise AuthorizationDenied("execution-package source digest mismatch")
        if grant["scope"] != "SINGLE_CP01R1_EXECUTION_NO_RETRY_NO_SCAN":
            raise AuthorizationDenied("grant scope is not the single preregistered run")
        decision_id = str(grant["authorization_decision_id"])
        if not decision_id.startswith("UL-DEC-"):
            raise AuthorizationDenied("append-only decision ID is invalid")
        return ExecutionCapability(
            run_id=RUN_ID,
            authorization_decision_id=decision_id,
            package_manifest_sha256=self.expected_package_digest,
            grant_path=str(path.relative_to(ROOT)),
        )


class ClassificationEngine:
    @staticmethod
    def classify(summary: dict[str, Any]) -> str:
        if not summary.get("execution_started", False):
            reason = summary.get("not_executed_reason")
            if reason == "INPUT":
                return "NOT_EXECUTED_INPUT_CONTRACT_FAILURE"
            if reason == "AUTHORIZATION":
                return "NOT_EXECUTED_AUTHORIZATION_FAILURE"
            return "NOT_EXECUTED_IMPLEMENTATION_FAILURE"
        if summary.get("implementation_failure", False):
            return "NOT_EXECUTED_IMPLEMENTATION_FAILURE"
        accepted = int(summary.get("accepted_candidate_count", 0))
        rejected = int(summary.get("rejected_root_count", 0))
        if accepted == 1:
            return "NUMERICAL_CANDIDATE_BACKGROUND_DIAGNOSTIC"
        if accepted > 1:
            return "MULTIPLE_NUMERICAL_CANDIDATE_BACKGROUNDS_DIAGNOSTIC"
        if rejected > 0:
            return "NUMERICAL_ROOT_REJECTED_BY_QA"
        return "NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL"

    @staticmethod
    def validate(classification: str) -> None:
        if classification not in ALLOWED_FINAL_CLASSIFICATIONS:
            raise ContractFailure(f"forbidden result classification: {classification}")


class AtomicResultWriter:
    """No-overwrite writer using a sibling staging directory and atomic rename."""

    def __init__(self, final_directory: Path, maximum_result_bytes: int):
        self.final_directory = final_directory
        self.maximum_result_bytes = maximum_result_bytes
        self.staging_directory = final_directory.with_name(
            f".{final_directory.name}.staging-{uuid.uuid4().hex}"
        )
        self._committed = False

    def __enter__(self) -> "AtomicResultWriter":
        if self.final_directory.exists():
            raise ArtifactFailure("final output path already exists")
        if self.staging_directory.exists():
            raise ArtifactFailure("staging path collision")
        self.staging_directory.mkdir(parents=True, exist_ok=False)
        return self

    def _write_json(self, name: str, payload: dict[str, Any]) -> str:
        data = canonical_json_bytes(payload) + b"\n"
        if len(data) > self.maximum_result_bytes:
            raise ArtifactFailure("single JSON artifact exceeds result-byte budget")
        path = self.staging_directory / name
        with path.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        return sha256_bytes(data)

    def commit(self, result: dict[str, Any], auxiliary: dict[str, dict[str, Any]] | None = None) -> Path:
        auxiliary = auxiliary or {}
        hashes: dict[str, str] = {}
        hashes["result.json"] = self._write_json("result.json", result)
        for name, payload in sorted(auxiliary.items()):
            if "/" in name or not name.endswith(".json"):
                raise ArtifactFailure(f"invalid auxiliary artifact name: {name}")
            hashes[name] = self._write_json(name, payload)
        manifest = {
            "schema": "universelab.background-3c4-artifact-manifest.v0.1",
            "run_id": RUN_ID,
            "created_utc": utc_now(),
            "files": hashes,
        }
        self._write_json("artifact-manifest.json", manifest)
        total = sum(path.stat().st_size for path in self.staging_directory.iterdir())
        if total > self.maximum_result_bytes:
            raise ArtifactFailure("staged artifact set exceeds result-byte budget")
        os.replace(self.staging_directory, self.final_directory)
        self._committed = True
        return self.final_directory

    def interrupt(self, reason: str) -> Path:
        partial = self.staging_directory.with_name(
            f".{self.final_directory.name}.partial-{uuid.uuid4().hex}"
        )
        marker = {
            "schema": "universelab.background-3c4-partial-artifact.v0.1",
            "run_id": RUN_ID,
            "interrupted_utc": utc_now(),
            "reason": reason,
            "final_result_created": False,
        }
        self._write_json("partial.json", marker)
        os.replace(self.staging_directory, partial)
        return partial

    def __exit__(self, exc_type, exc, traceback) -> bool:
        if not self._committed and self.staging_directory.exists():
            shutil.rmtree(self.staging_directory, ignore_errors=True)
        return False


@contextmanager
def wall_clock_alarm(seconds: int):
    if seconds <= 0:
        raise ResourceFailure("timeout must be positive")
    if os.name != "posix" or not hasattr(signal, "SIGALRM"):
        yield
        return

    def handler(_signum, _frame):
        raise TimeoutError(f"stage exceeded {seconds} seconds")

    previous = signal.signal(signal.SIGALRM, handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


def _dynamic_import(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ContractFailure(f"unable to import {path.relative_to(ROOT)}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class PrimaryRootAdapter:
    def __init__(self, capability: ExecutionCapability):
        self.capability = capability
        self.call_count = 0

    def solve(self, initial: Any, node_count: int, model: Any, sector: Any, **kwargs):
        if not isinstance(self.capability, ExecutionCapability):
            raise AuthorizationDenied("primary root adapter lacks execution capability")
        module = _dynamic_import(PRIMARY_KERNEL_PATH, "background3c_primary_authorized")
        self.call_count += 1
        return module.damped_newton(initial, node_count, model, sector, **kwargs)


class IndependentRootAdapter:
    def __init__(self, capability: ExecutionCapability):
        self.capability = capability
        self.call_count = 0
        self.jacobian_call_count = 0

    def solve(
        self,
        shooting_initial: Any,
        model: Any,
        sector: Any,
        *,
        epsilon: float,
        maximum_iterations: int = 40,
        residual_tolerance: float = 1.0e-9,
    ) -> dict[str, Any]:
        if not isinstance(self.capability, ExecutionCapability):
            raise AuthorizationDenied("independent root adapter lacks execution capability")
        import numpy as np
        from scipy.optimize import least_squares

        module = _dynamic_import(INDEPENDENT_BACKEND_PATH, "background3c_independent_authorized")
        self.call_count += 1

        def residual(vector):
            values, _ = module.shooting_residual(
                vector, model, sector, epsilon=epsilon
            )
            return values

        def jacobian(vector):
            self.jacobian_call_count += 1
            return module.centered_fd_jacobian(residual, vector)

        result = least_squares(
            residual,
            np.asarray(shooting_initial, dtype=float),
            jac=jacobian,
            method="trf",
            max_nfev=maximum_iterations,
            ftol=residual_tolerance,
            xtol=residual_tolerance,
            gtol=residual_tolerance,
        )
        return {
            "x": result.x,
            "fun": result.fun,
            "success": bool(result.success),
            "status": int(result.status),
            "message": str(result.message),
            "nfev": int(result.nfev),
            "njev": None if result.njev is None else int(result.njev),
        }


def build_result_skeleton(
    capability: ExecutionCapability,
    package_digest: str,
    attestation: dict[str, Any],
) -> dict[str, Any]:
    result_schema = load_json(RESULT_SCHEMA_PATH)
    classification = "NOT_EXECUTED_IMPLEMENTATION_FAILURE"
    ClassificationEngine.validate(classification)
    return {
        "schema": result_schema["schema"],
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "implementation_source_sha256": package_digest,
        "dependency_lock_sha256": load_json(RUN_INPUT_PATH)["frozen_run_payload"]["dependency_lock_sha256"],
        "authorization_decision_id": capability.authorization_decision_id,
        "execution_started_utc": None,
        "execution_finished_utc": None,
        "machine_environment": attestation,
        "primary_backend": {},
        "independent_backend": {},
        "candidate_inventory": [],
        "acceptance_audit": {},
        "final_classification": classification,
        "physical_evidence_effect": "NONE",
        "forbidden_inferences": [
            "continuum_existence",
            "uniqueness",
            "Fredholm_property",
            "perturbative_stability",
            "ghost_freedom",
            "K1-D_release",
            "K1-E_admissibility",
            "physical_confirmation",
        ],
    }


def audit_package(*, require_dependencies: bool = True) -> dict[str, Any]:
    _result_schema, resource_policy, contract = validate_run_contracts()
    envelope = ResourceEnvelope.from_policy(resource_policy)
    envelope.validate_static()
    manifest = package_source_manifest()
    digest = sha256_bytes(canonical_json_bytes(manifest))
    attestation = environment_attestation(digest)
    validate_environment(attestation, require_dependencies=require_dependencies)

    if contract.get("status") != "IMPLEMENTED_AUDIT_ONLY_EXECUTION_NOT_AUTHORIZED":
        raise ContractFailure("3C4 contract status drift")
    components = contract.get("components", {})
    required_components = {
        "source_hash_bound_runner",
        "environment_attestation",
        "resource_enforcement",
        "atomic_result_writer",
        "classification_engine",
        "interruption_protocol",
        "primary_root_adapter",
        "independent_root_adapter",
        "grant_verifier",
    }
    if set(components) != required_components:
        raise ContractFailure("3C4 component inventory drift")
    if any(value != "IMPLEMENTED_NOT_EXECUTED" for value in components.values()):
        raise ContractFailure("3C4 components must remain implemented-not-executed")
    if contract.get("execution_authorized") is not False:
        raise ContractFailure("3C4 may not authorize execution")
    if contract.get("physical_evidence_effect") != "NONE":
        raise ContractFailure("3C4 evidence firewall drift")

    return {
        "status": "PASS_EXECUTION_PACKAGE_AUDIT_NO_SOLVER_CALLS",
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "package_manifest_sha256": digest,
        "source_count": len(manifest),
        "environment": attestation,
        "resource_envelope": envelope.__dict__,
        "authorization_grant_present": AUTHORIZATION_PATH.exists(),
        "primary_root_calls": 0,
        "independent_root_calls": 0,
        "independent_jacobian_calls": 0,
        "result_artifact_created": False,
        "physical_evidence_effect": "NONE",
        "next_block": "C-PHYS-R1.0-BACKGROUND-3C5_EXECUTION_PACKAGE_AUTHORIZATION_REVIEW_ONLY",
    }


def self_test() -> dict[str, Any]:
    audit = audit_package(require_dependencies=True)
    policy = load_json(RESOURCE_POLICY_PATH)
    envelope = ResourceEnvelope.from_policy(policy)

    classifications = {
        "authorization": ClassificationEngine.classify(
            {"execution_started": False, "not_executed_reason": "AUTHORIZATION"}
        ),
        "input": ClassificationEngine.classify(
            {"execution_started": False, "not_executed_reason": "INPUT"}
        ),
        "none": ClassificationEngine.classify(
            {"execution_started": True, "accepted_candidate_count": 0, "rejected_root_count": 0}
        ),
        "one": ClassificationEngine.classify(
            {"execution_started": True, "accepted_candidate_count": 1, "rejected_root_count": 0}
        ),
        "multiple": ClassificationEngine.classify(
            {"execution_started": True, "accepted_candidate_count": 2, "rejected_root_count": 0}
        ),
        "rejected": ClassificationEngine.classify(
            {"execution_started": True, "accepted_candidate_count": 0, "rejected_root_count": 1}
        ),
    }
    for value in classifications.values():
        ClassificationEngine.validate(value)

    with tempfile.TemporaryDirectory(prefix="universelab-bg3c4-") as temporary:
        root = Path(temporary)
        final = root / "atomic-result"
        with AtomicResultWriter(final, envelope.result_bytes) as writer:
            writer.commit(
                {
                    "schema": "universelab.background-3c4-self-test-result.v0.1",
                    "run_id": RUN_ID,
                    "final_classification": "NOT_EXECUTED_IMPLEMENTATION_FAILURE",
                    "physical_evidence_effect": "NONE",
                },
                {"environment.json": audit["environment"]},
            )
        if not (final / "result.json").is_file():
            raise ArtifactFailure("atomic result self-test did not commit result.json")
        if not (final / "artifact-manifest.json").is_file():
            raise ArtifactFailure("atomic result self-test did not commit manifest")

        interrupted_final = root / "interrupted-result"
        with AtomicResultWriter(interrupted_final, envelope.result_bytes) as writer:
            partial = writer.interrupt("SELF_TEST_INTERRUPT")
        if interrupted_final.exists():
            raise ArtifactFailure("interrupted self-test created a final result")
        if not (partial / "partial.json").is_file():
            raise ArtifactFailure("interruption protocol did not preserve partial marker")

    try:
        GrantVerifier(audit["package_manifest_sha256"]).verify()
    except AuthorizationDenied:
        grant_refusal = True
    else:
        grant_refusal = False
    if not grant_refusal:
        raise AuthorizationDenied("self-test expected absent grant to be refused")

    return {
        "status": "PASS_EXECUTION_PACKAGE_SELF_TEST_NO_SOLVER_CALLS",
        "package_manifest_sha256": audit["package_manifest_sha256"],
        "classifications": classifications,
        "atomic_writer": "PASS_TEMPORARY_DIRECTORY_ONLY",
        "interruption_protocol": "PASS_TEMPORARY_DIRECTORY_ONLY",
        "authorization_refusal": "PASS_EXIT_PATH_PRE_BACKEND_IMPORT",
        "primary_root_calls": 0,
        "independent_root_calls": 0,
        "independent_jacobian_calls": 0,
        "repository_result_artifact_created": False,
        "physical_evidence_effect": "NONE",
    }


def run_authorized() -> int:
    _result_schema, resource_policy, _contract = validate_run_contracts()
    envelope = ResourceEnvelope.from_policy(resource_policy)
    envelope.validate_static()
    digest = package_manifest_sha256()
    capability = GrantVerifier(digest).verify(AUTHORIZATION_PATH)

    # This path is unreachable in v0.1 because no grant artifact exists. Its
    # components are implemented for a later append-only authorization review,
    # but no automatic grant or execution is created by this block.
    attestation = environment_attestation(digest)
    validate_environment(attestation)
    output_root = ROOT / "artifacts/hzt-m0/md2s/background3c" / RUN_ID
    final_directory = output_root / capability.authorization_decision_id
    if final_directory.exists():
        raise ArtifactFailure("immutable result path already exists")

    build_result_skeleton(capability, digest, attestation)
    raise AuthorizationDenied(
        "3C4 implements the package but v0.1 is not an execution release; "
        "a later reviewed runner version is required even after a grant appears"
    )


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("audit", "self-test", "run"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload["status"])


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "audit":
            emit(audit_package(), args.json)
            return 0
        if args.command == "self-test":
            emit(self_test(), args.json)
            return 0
        if args.command == "run":
            return run_authorized()
    except AuthorizationDenied as exc:
        payload = {
            "status": "NOT_AUTHORIZED",
            "reason": str(exc),
            "run_id": RUN_ID,
            "solver_calls": 0,
            "result_artifact_created": False,
            "physical_evidence_effect": "NONE",
        }
        if getattr(args, "json", False):
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(payload["reason"], file=sys.stderr)
        return EXIT_NOT_AUTHORIZED
    except ContractFailure as exc:
        print(f"CONTRACT_FAILURE: {exc}", file=sys.stderr)
        return EXIT_CONTRACT_FAILURE
    except ResourceFailure as exc:
        print(f"RESOURCE_FAILURE: {exc}", file=sys.stderr)
        return EXIT_RESOURCE_FAILURE
    except ArtifactFailure as exc:
        print(f"ARTIFACT_FAILURE: {exc}", file=sys.stderr)
        return EXIT_PARTIAL_ARTIFACT
    except Exception as exc:
        print(f"AUDIT_FAILURE: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_AUDIT_FAILURE
    return EXIT_AUDIT_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
