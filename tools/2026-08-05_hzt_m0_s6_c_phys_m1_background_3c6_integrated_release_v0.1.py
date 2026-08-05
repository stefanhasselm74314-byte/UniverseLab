#!/usr/bin/env python3
"""Integrated synthetic/control execution release for Background-3C6.

The release exercises a complete subprocess transaction with resource limits,
timeouts, signal handling, classification and atomic artifacts. It never imports
the primary or independent Hyperzeit numerical backend and cannot execute CP01R1.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C6IntegratedExecutionReleaseContract_v0.1.json"
WORKER_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c6_synthetic_worker_v0.1.py"
PHYSICAL_ARTIFACT_ROOT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
PHYSICAL_GRANT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
EXIT_NOT_AUTHORIZED = 73
EXIT_CONTROL_FAILURE = 74
SUBPROCESS_LAUNCH_COUNT = 0
PRIMARY_ROOT_CALL_COUNT = 0
INDEPENDENT_ROOT_CALL_COUNT = 0
SHOOTING_JACOBIAN_CALL_COUNT = 0
CP01R1_ATTEMPT_COUNT = 0


class ControlReleaseError(RuntimeError):
    pass


class ScopeDenied(ControlReleaseError):
    pass


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def package_manifest() -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    entries: list[dict[str, Any]] = []
    digest = hashlib.sha256()
    for relative in contract["package_source_paths"]:
        path = ROOT / relative
        if not path.is_file():
            raise ControlReleaseError(f"missing package source: {relative}")
        data = path.read_bytes()
        encoded = relative.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
        entries.append({"path": relative, "sha256": sha256_bytes(data), "bytes": len(data)})
    return {
        "schema": "universelab.background-3c6-package-manifest.v0.1",
        "source_count": len(entries),
        "sources": entries,
        "package_manifest_sha256": digest.hexdigest(),
    }


def environment_attestation(package_digest: str) -> dict[str, Any]:
    dependencies: dict[str, str] = {}
    for name in ("numpy", "scipy", "sympy", "mpmath"):
        try:
            dependencies[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            dependencies[name] = "NOT_INSTALLED_NOT_REQUIRED_FOR_CONTROL_RELEASE"
    return {
        "schema": "universelab.background-3c6-environment-attestation.v0.1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "package_manifest_sha256": package_digest,
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "executable_name": Path(sys.executable).name,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "dependencies": dependencies,
        "thread_environment": {
            name: os.environ.get(name, "UNSET")
            for name in (
                "OMP_NUM_THREADS",
                "OPENBLAS_NUM_THREADS",
                "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS",
            )
        },
        "network_policy": "FORBIDDEN_BY_CONTROL_WORKER_DESIGN_AND_ENVIRONMENT",
        "randomness_policy": "FORBIDDEN",
        "physical_backend_imported": False,
    }


def validate_scope(case: str, control_id: str, output_root: Path) -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    scope = contract["control_scope"]
    if case not in scope["allowed_cases"]:
        raise ScopeDenied("control case is not registered")
    if not control_id.startswith(scope["allowed_run_id_prefix"]):
        raise ScopeDenied("control ID is outside the registered prefix")
    upper = control_id.upper()
    if any(forbidden.upper() in upper for forbidden in scope["forbidden_run_ids"]):
        raise ScopeDenied("physical run ID is forbidden in Background-3C6")
    if "CP01" in upper or "BG3B" in upper:
        raise ScopeDenied("CP01/CP01R1 identifiers are forbidden in control release")
    root = output_root.resolve()
    repository = ROOT.resolve()
    if root == repository or repository in root.parents:
        raise ScopeDenied("control output root must be external to the repository")
    if not root.is_dir():
        raise ScopeDenied("control output root must already exist")
    if root.is_symlink():
        raise ScopeDenied("control output root may not be a symlink")
    if PHYSICAL_GRANT_PATH.exists() or PHYSICAL_ARTIFACT_ROOT.exists():
        raise ScopeDenied("physical grant or CP01R1 artifact path unexpectedly exists")
    return contract


def _resource_preexec(limits: dict[str, Any]):
    def apply() -> None:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (int(limits["worker_cpu_seconds"]), int(limits["worker_cpu_seconds"])))
        resource.setrlimit(resource.RLIMIT_AS, (int(limits["worker_address_space_bytes"]), int(limits["worker_address_space_bytes"])))
        resource.setrlimit(resource.RLIMIT_FSIZE, (int(limits["worker_file_bytes"]), int(limits["worker_file_bytes"])))
        resource.setrlimit(resource.RLIMIT_NOFILE, (int(limits["worker_open_files"]), int(limits["worker_open_files"])))
    return apply


def worker_environment() -> dict[str, str]:
    env = dict(os.environ)
    for key in list(env):
        if key.lower() in {"http_proxy", "https_proxy", "all_proxy", "no_proxy"}:
            env.pop(key, None)
    env.update({
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
        "VECLIB_MAXIMUM_THREADS": "1",
        "PYTHONHASHSEED": "0",
        "UNIVERSELAB_NETWORK_ACCESS": "DENIED",
        "UNIVERSELAB_PHYSICAL_BACKEND_ACCESS": "DENIED",
    })
    return env


def terminate_process(process: subprocess.Popen[bytes], grace_seconds: float) -> tuple[bytes, bytes]:
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        return process.communicate(timeout=grace_seconds)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return process.communicate()


def write_canonical(path: Path, payload: dict[str, Any]) -> None:
    data = canonical_bytes(payload)
    with path.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def validate_worker_payload(payload: dict[str, Any], case: str, control_id: str) -> None:
    if payload.get("schema") != "universelab.background-3c6-control-worker-result.v0.1":
        raise ControlReleaseError("worker schema mismatch")
    if payload.get("case") != case or payload.get("control_id") != control_id:
        raise ControlReleaseError("worker identity mismatch")
    if payload.get("physical_model_evaluated") is not False:
        raise ControlReleaseError("worker claims physical-model evaluation")
    if payload.get("solver_called") is not False:
        raise ControlReleaseError("worker claims solver execution")
    if payload.get("physical_evidence_effect") != "NONE":
        raise ControlReleaseError("worker evidence firewall mismatch")


def commit_control_artifact(
    *, stage: Path, final: Path, result: dict[str, Any], package_digest: str,
    maximum_bytes: int,
) -> dict[str, Any]:
    result_path = stage / "result.json"
    manifest_path = stage / "artifact-manifest.json"
    write_canonical(result_path, result)
    manifest = {
        "schema": "universelab.background-3c6-control-artifact-manifest.v0.1",
        "control_id": result["control_id"],
        "classification": result["final_classification"],
        "package_manifest_sha256": package_digest,
        "files": [{"path": "result.json", "sha256": sha256_file(result_path), "bytes": result_path.stat().st_size}],
        "physical_evidence_effect": "NONE",
    }
    write_canonical(manifest_path, manifest)
    total = result_path.stat().st_size + manifest_path.stat().st_size
    if total > maximum_bytes:
        raise ControlReleaseError("control artifact exceeds frozen size limit")
    fsync_directory(stage)
    os.replace(stage, final)
    fsync_directory(final.parent)
    return manifest


def run_control(case: str, control_id: str, output_root: Path) -> dict[str, Any]:
    global SUBPROCESS_LAUNCH_COUNT
    contract = validate_scope(case, control_id, output_root)
    limits = contract["resource_control"]
    package = package_manifest()
    package_digest = package["package_manifest_sha256"]
    attestation = environment_attestation(package_digest)
    final = output_root.resolve() / control_id
    stage = output_root.resolve() / f".{control_id}.staging-{os.getpid()}"
    if final.exists() or final.is_symlink():
        raise ControlReleaseError("final control artifact already exists")
    if stage.exists() or stage.is_symlink():
        raise ControlReleaseError("staging path already exists")
    stage.mkdir(mode=0o700)
    worker_output = stage / "worker-result.json"
    command = [
        sys.executable,
        str(WORKER_PATH),
        "--case", case,
        "--control-id", control_id,
        "--output", str(worker_output),
    ]
    started_wall = time.time()
    started_mono = time.monotonic()
    process: subprocess.Popen[bytes] | None = None
    try:
        if os.name != "posix":
            raise ControlReleaseError("Background-3C6 resource controls require POSIX")
        SUBPROCESS_LAUNCH_COUNT += 1
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env=worker_environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            preexec_fn=_resource_preexec(limits),
        )
        timed_out = False
        try:
            stdout, stderr = process.communicate(timeout=float(limits["stage_timeout_seconds"]))
        except subprocess.TimeoutExpired:
            timed_out = True
            stdout, stderr = terminate_process(process, float(limits["termination_grace_seconds"]))
        elapsed = time.monotonic() - started_mono
        maximum_stream = int(limits["maximum_captured_stream_bytes"])
        if len(stdout) > maximum_stream or len(stderr) > maximum_stream:
            raise ControlReleaseError("captured stream exceeds frozen limit")
        process_record = {
            "returncode": process.returncode,
            "timed_out": timed_out,
            "elapsed_seconds": elapsed,
            "stdout_sha256": sha256_bytes(stdout),
            "stdout_bytes": len(stdout),
            "stderr_sha256": sha256_bytes(stderr),
            "stderr_bytes": len(stderr),
        }
        if timed_out:
            classification = "CONTROL_TRANSACTION_TIMEOUT_CLEAN_ABORT"
            shutil.rmtree(stage, ignore_errors=True)
            return {
                "status": "PASS_EXPECTED_CONTROL_ABORT",
                "control_id": control_id,
                "case": case,
                "final_classification": classification,
                "process": process_record,
                "final_artifact_created": False,
                "staging_removed": not stage.exists(),
                "package_manifest_sha256": package_digest,
                "physical_solver_calls": 0,
                "physical_evidence_effect": "NONE",
            }
        if process.returncode is not None and process.returncode < 0:
            classification = "CONTROL_TRANSACTION_SIGNAL_CLEAN_ABORT"
            shutil.rmtree(stage, ignore_errors=True)
            return {
                "status": "PASS_EXPECTED_CONTROL_ABORT",
                "control_id": control_id,
                "case": case,
                "final_classification": classification,
                "process": process_record,
                "final_artifact_created": False,
                "staging_removed": not stage.exists(),
                "package_manifest_sha256": package_digest,
                "physical_solver_calls": 0,
                "physical_evidence_effect": "NONE",
            }
        if not worker_output.is_file() or worker_output.is_symlink():
            raise ControlReleaseError("worker output is missing or unsafe")
        if worker_output.stat().st_size > int(limits["maximum_worker_payload_bytes"]):
            raise ControlReleaseError("worker payload exceeds frozen limit")
        worker_payload = load_json(worker_output)
        validate_worker_payload(worker_payload, case, control_id)
        worker_output.unlink()
        if case == "analytic_success":
            if process.returncode != 0 or worker_payload.get("accepted") is not True:
                raise ControlReleaseError("analytic success control did not pass")
            if worker_payload.get("identity", {}).get("exact") is not True:
                raise ControlReleaseError("analytic identity is not exact")
            classification = "CONTROL_TRANSACTION_PASS"
        elif case == "synthetic_reject":
            if process.returncode != 2 or worker_payload.get("accepted") is not False:
                raise ControlReleaseError("synthetic rejection control mismatch")
            classification = "CONTROL_TRANSACTION_REJECTED_AS_EXPECTED"
        else:
            raise ControlReleaseError("non-aborting control case reached payload path")
        result = {
            "schema": "universelab.background-3c6-integrated-control-result.v0.1",
            "control_id": control_id,
            "case": case,
            "package_manifest_sha256": package_digest,
            "execution_started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started_wall)),
            "execution_finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "environment_attestation": attestation,
            "resource_limits": limits,
            "process": process_record,
            "worker_payload": worker_payload,
            "final_classification": classification,
            "primary_root_calls": 0,
            "independent_root_calls": 0,
            "shooting_jacobian_calls": 0,
            "cp01r1_attempts": 0,
            "physical_model_evaluated": False,
            "physical_evidence_effect": "NONE",
            "forbidden_inferences": [
                "No physical background follows from a control transaction.",
                "No CP01R1 authorization or solver release follows from this artifact.",
                "No continuum existence uniqueness stability or evidence claim follows.",
            ],
        }
        manifest = commit_control_artifact(
            stage=stage,
            final=final,
            result=result,
            package_digest=package_digest,
            maximum_bytes=int(limits["maximum_final_artifact_bytes"]),
        )
        return {
            "status": "PASS_CONTROL_TRANSACTION_COMMITTED",
            "control_id": control_id,
            "case": case,
            "final_classification": classification,
            "process": process_record,
            "final_artifact_created": True,
            "final_artifact_path": str(final),
            "artifact_manifest_sha256": sha256_bytes(canonical_bytes(manifest)),
            "package_manifest_sha256": package_digest,
            "physical_solver_calls": 0,
            "physical_evidence_effect": "NONE",
        }
    except BaseException:
        if process is not None and process.poll() is None:
            terminate_process(process, float(limits["termination_grace_seconds"]))
        shutil.rmtree(stage, ignore_errors=True)
        raise


def verify_committed_artifact(path: Path) -> dict[str, Any]:
    result_path = path / "result.json"
    manifest_path = path / "artifact-manifest.json"
    result = load_json(result_path)
    manifest = load_json(manifest_path)
    listed = manifest["files"]
    if len(listed) != 1 or listed[0]["path"] != "result.json":
        raise ControlReleaseError("artifact manifest inventory mismatch")
    if listed[0]["sha256"] != sha256_file(result_path):
        raise ControlReleaseError("artifact result hash mismatch")
    if result["physical_evidence_effect"] != "NONE":
        raise ControlReleaseError("artifact evidence firewall mismatch")
    return {"result": result, "manifest": manifest}


def audit_release() -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    package = package_manifest()
    source_text = Path(__file__).read_text(encoding="utf-8")
    forbidden_import_tokens = (
        "background_3c_primary_kernel",
        "background_3c_independent_backend",
        "damped_newton(",
        "centered_fd_jacobian(",
    )
    if any(token in source_text for token in forbidden_import_tokens):
        raise ControlReleaseError("integrated control release contains forbidden backend token")
    if contract["physical_execution_authorized"] is not False:
        raise ControlReleaseError("physical execution unexpectedly authorized")
    if PHYSICAL_GRANT_PATH.exists() or PHYSICAL_ARTIFACT_ROOT.exists():
        raise ControlReleaseError("physical grant or result path unexpectedly exists")
    return {
        "status": "PASS_INTEGRATED_CONTROL_RELEASE_AUDIT_NO_PHYSICAL_EXECUTION",
        "package_manifest_sha256": package["package_manifest_sha256"],
        "source_count": package["source_count"],
        "allowed_cases": contract["control_scope"]["allowed_cases"],
        "subprocess_launch_count": SUBPROCESS_LAUNCH_COUNT,
        "primary_root_calls": PRIMARY_ROOT_CALL_COUNT,
        "independent_root_calls": INDEPENDENT_ROOT_CALL_COUNT,
        "shooting_jacobian_calls": SHOOTING_JACOBIAN_CALL_COUNT,
        "cp01r1_attempts": CP01R1_ATTEMPT_COUNT,
        "physical_grant_present": False,
        "physical_result_artifact_present": False,
        "physical_evidence_effect": "NONE",
    }


def self_test() -> dict[str, Any]:
    before = SUBPROCESS_LAUNCH_COUNT
    with tempfile.TemporaryDirectory(prefix="universelab-bg3c6-") as directory:
        root = Path(directory)
        controls = {
            "analytic_success": "HZT-M0-S6-C-PHYS-M1-BG3C6-CONTROL-ANALYTIC-SUCCESS",
            "synthetic_reject": "HZT-M0-S6-C-PHYS-M1-BG3C6-CONTROL-SYNTHETIC-REJECT",
            "synthetic_timeout": "HZT-M0-S6-C-PHYS-M1-BG3C6-CONTROL-SYNTHETIC-TIMEOUT",
            "synthetic_signal": "HZT-M0-S6-C-PHYS-M1-BG3C6-CONTROL-SYNTHETIC-SIGNAL",
        }
        results = {case: run_control(case, control_id, root) for case, control_id in controls.items()}
        success_path = root / controls["analytic_success"]
        reject_path = root / controls["synthetic_reject"]
        verify_committed_artifact(success_path)
        verify_committed_artifact(reject_path)
        if (root / controls["synthetic_timeout"]).exists():
            raise ControlReleaseError("timeout control created a final artifact")
        if (root / controls["synthetic_signal"]).exists():
            raise ControlReleaseError("signal control created a final artifact")
        try:
            run_control("analytic_success", controls["analytic_success"], root)
        except ControlReleaseError as error:
            no_overwrite = str(error)
        else:
            raise ControlReleaseError("no-overwrite control failed")
        launches_before_forbidden = SUBPROCESS_LAUNCH_COUNT
        try:
            run_control("analytic_success", "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1", root)
        except ScopeDenied as error:
            forbidden_scope = str(error)
        else:
            raise ControlReleaseError("physical run ID was not denied")
        if SUBPROCESS_LAUNCH_COUNT != launches_before_forbidden:
            raise ControlReleaseError("scope denial occurred after subprocess launch")
        if SUBPROCESS_LAUNCH_COUNT - before != 4:
            raise ControlReleaseError("unexpected subprocess launch count in self-test")
        return {
            "status": "PASS_INTEGRATED_CONTROL_RELEASE_SELF_TEST",
            "classifications": {case: result["final_classification"] for case, result in results.items()},
            "committed_control_artifacts": 2,
            "clean_abort_controls": 2,
            "subprocess_launches": SUBPROCESS_LAUNCH_COUNT - before,
            "no_overwrite_firewall": no_overwrite,
            "physical_scope_firewall": forbidden_scope,
            "primary_root_calls": 0,
            "independent_root_calls": 0,
            "shooting_jacobian_calls": 0,
            "cp01r1_attempts": 0,
            "repository_artifact_created": False,
            "physical_evidence_effect": "NONE",
        }


def denied_physical_run(run_id: str | None) -> dict[str, Any]:
    return {
        "status": "NOT_AUTHORIZED",
        "reason": "BACKGROUND_3C6_IS_CONTROL_ONLY_AND_CANNOT_EXECUTE_CP01R1",
        "requested_run_id": run_id,
        "exit_code": EXIT_NOT_AUTHORIZED,
        "subprocess_launches": 0,
        "solver_calls": 0,
        "result_artifact_created": False,
        "physical_evidence_effect": "NONE",
        "next_block": "C-PHYS-R1.0-BACKGROUND-3C7_INTEGRATED_RELEASE_AUTHORIZATION_REVIEW_ONLY",
    }


def emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload["status"])


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("audit", "self-test"):
        item = subparsers.add_parser(name)
        item.add_argument("--json", action="store_true")
    control = subparsers.add_parser("control")
    control.add_argument("--case", required=True)
    control.add_argument("--control-id", required=True)
    control.add_argument("--output-root", required=True)
    control.add_argument("--json", action="store_true")
    run = subparsers.add_parser("run")
    run.add_argument("--run-id")
    run.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "audit":
            emit(audit_release(), args.json)
            return 0
        if args.command == "self-test":
            emit(self_test(), args.json)
            return 0
        if args.command == "control":
            emit(run_control(args.case, args.control_id, Path(args.output_root)), args.json)
            return 0
        if args.command == "run":
            emit(denied_physical_run(args.run_id), args.json)
            return EXIT_NOT_AUTHORIZED
    except (ControlReleaseError, OSError, ValueError, json.JSONDecodeError) as error:
        emit({
            "status": "CONTROL_RELEASE_FAILURE",
            "error": f"{type(error).__name__}: {error}",
            "solver_calls": 0,
            "result_artifact_created": False,
            "physical_evidence_effect": "NONE",
        }, True)
        return EXIT_CONTROL_FAILURE
    return EXIT_CONTROL_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
