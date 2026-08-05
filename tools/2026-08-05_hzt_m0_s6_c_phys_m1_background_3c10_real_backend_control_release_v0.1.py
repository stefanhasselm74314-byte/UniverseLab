#!/usr/bin/env python3
"""Background-3C10 real-backend analytic control release.

This release imports the actual primary and independent backend modules only in
resource-contained child processes and only for the exact analytic a_F=0
control. It does not execute CP01R1, Newton, a shooting Jacobian, or a nonlinear
root solve. All artifacts are external temporary control artifacts.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
from typing import Any, Iterable
import uuid

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlContract_v0.1.json"
REVIEW_3C9_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C9PhysicalAdapterAuthorizationReview_v0.1.json"
RUN_INPUT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"
RESULT_SCHEMA_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResultSchema_v0.1.json"
RESOURCE_POLICY_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
PRIMARY_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py"
PRIMARY_BASE_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.1.py"
INDEPENDENT_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_independent_backend_v0.1.py"
WORKER_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_worker_v0.1.py"
VALIDATOR_PATH = ROOT / "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c10_v0.1.py"
TEST_PATH = ROOT / "tests/2026-08-05_test_hzt_m0_s6_c_phys_m1_background_3c10_v0.1.py"
LEDGER_PATH = ROOT / "science/hzt-m0/md2s/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C10RealBackendAdapterControlLedger_v0.1.md"
OPERATIVE_GRANT_PATHS = (
    ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",
    ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",
)
PHYSICAL_ARTIFACT_ROOT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"

CONTROL_RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3C10-AF0-CONTROL-R1"
FROZEN_RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
FROZEN_PAYLOAD_SHA256 = "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302"
DENIAL_3C9 = "DENIED_REAL_BACKEND_ADAPTER_TRANSACTION_AND_OPERATIVE_SINGLE_USE_GRANT_RELEASE_ABSENT"
EXIT_NOT_AUTHORIZED = 73
EXIT_CONTROL_FAILURE = 74

WORKER_LAUNCH_COUNT = 0
CP01R1_ATTEMPT_COUNT = 0
TARGET_ROOT_SOLVE_COUNT = 0
OPERATIVE_GRANT_CREATE_COUNT = 0
PHYSICAL_RESULT_CREATE_COUNT = 0


class ReleaseFailure(RuntimeError):
    pass


class NotAuthorized(ReleaseFailure):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


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
        raise ReleaseFailure(f"missing required file: {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ReleaseFailure(f"invalid JSON: {path.relative_to(ROOT)}") from exc
    if not isinstance(value, dict):
        raise ReleaseFailure(f"top-level object required: {path.relative_to(ROOT)}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseFailure(message)


def package_paths() -> tuple[Path, ...]:
    return (
        CONTRACT_PATH, REVIEW_3C9_PATH, RUN_INPUT_PATH, RESULT_SCHEMA_PATH,
        RESOURCE_POLICY_PATH, PRIMARY_PATH, PRIMARY_BASE_PATH, INDEPENDENT_PATH,
        WORKER_PATH, Path(__file__).resolve(), VALIDATOR_PATH, TEST_PATH, LEDGER_PATH,
    )


def package_manifest() -> dict[str, Any]:
    sources: dict[str, str] = {}
    for path in package_paths():
        if not path.is_file():
            raise ReleaseFailure(f"closed package source missing: {path.relative_to(ROOT)}")
        sources[str(path.relative_to(ROOT))] = sha256_file(path)
    return {
        "sources": sources,
        "source_count": len(sources),
        "package_manifest_sha256": sha256_value(sources),
    }


def called_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.add(node.func.attr)
    return names


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modules.add(node.module or "")
    return modules


def static_audit() -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    review = load_json(REVIEW_3C9_PATH)
    run_input = load_json(RUN_INPUT_PATH)
    result_schema = load_json(RESULT_SCHEMA_PATH)
    resource_policy = load_json(RESOURCE_POLICY_PATH)
    require(contract["status"] == "IMPLEMENTED_PENDING_AUDIT_REAL_BACKEND_ANALYTIC_CONTROLS_ONLY", "3C10 status drift")
    require(contract["control_run_id"] == CONTROL_RUN_ID, "control run ID drift")
    require(contract["frozen_physical_run_id"] == FROZEN_RUN_ID, "frozen run ID drift")
    require(contract["frozen_run_payload_sha256"] == FROZEN_PAYLOAD_SHA256, "payload digest drift")
    require(contract["control_override"]["a_F"] == 0.0, "control override drift")
    require(review["status"] == DENIAL_3C9, "3C9 review drift")
    require(review["authorization_decision"]["authorized"] is False, "3C9 unexpectedly authorizes execution")
    require(run_input["frozen_run_payload"]["run_id"] == FROZEN_RUN_ID, "run input identity drift")
    require(run_input["frozen_run_payload_sha256"] == FROZEN_PAYLOAD_SHA256, "run input hash drift")
    require(result_schema["current_state"]["result_artifact_created"] is False, "result schema overclaim")
    require(resource_policy["current_state"]["execution_authorized"] is False, "resource policy authorization drift")
    worker_calls = called_names(WORKER_PATH)
    forbidden_calls = {"damped_newton", "complex_step_jacobian", "rrqr_step", "centered_fd_jacobian", "least_squares", "root"}
    require(not (worker_calls & forbidden_calls), f"forbidden worker call path: {sorted(worker_calls & forbidden_calls)}")
    release_modules = imported_modules(Path(__file__).resolve())
    require("numpy" not in release_modules and "scipy" not in release_modules, "parent release may not import numerical backends")
    require(all(not path.exists() for path in OPERATIVE_GRANT_PATHS), "operative grant unexpectedly present")
    require(not PHYSICAL_ARTIFACT_ROOT.exists(), "physical result path unexpectedly present")
    manifest = package_manifest()
    return {
        "status": "PASS_REAL_BACKEND_CONTROL_STATIC_AUDIT_NO_BACKEND_IMPORT",
        "package_manifest_sha256": manifest["package_manifest_sha256"],
        "source_count": manifest["source_count"],
        "primary_source_sha256": sha256_file(PRIMARY_PATH),
        "primary_base_source_sha256": sha256_file(PRIMARY_BASE_PATH),
        "independent_source_sha256": sha256_file(INDEPENDENT_PATH),
        "worker_source_sha256": sha256_file(WORKER_PATH),
        "worker_forbidden_calls": sorted(worker_calls & forbidden_calls),
        "parent_imports_numerical_backend": False,
        "worker_launches": 0,
        "cp01r1_attempts": 0,
        "target_root_solves": 0,
        "operative_grants": 0,
        "physical_results": 0,
        "physical_evidence_effect": "NONE",
    }


def resource_preexec(contract: dict[str, Any]):
    if os.name != "posix":
        return None
    limits = contract["process_controls"]
    def apply() -> None:
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (int(limits["worker_address_space_bytes"]),) * 2)
        resource.setrlimit(resource.RLIMIT_CPU, (int(limits["worker_cpu_seconds"]), int(limits["worker_cpu_seconds"]) + 1))
        resource.setrlimit(resource.RLIMIT_FSIZE, (int(limits["worker_file_bytes"]),) * 2)
        resource.setrlimit(resource.RLIMIT_NOFILE, (int(limits["worker_open_files"]),) * 2)
    return apply


def worker_envelope(stage: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "stage": stage,
        "scope": "REAL_BACKEND_ANALYTIC_AF0_CONTROL_ONLY",
        "control_run_id": CONTROL_RUN_ID,
        "frozen_physical_run_id": FROZEN_RUN_ID,
        "control_a_F": 0.0,
        "cp01r1_execution": False,
        "target_root_solve": False,
        "payload": payload,
    }


def launch_worker(request: dict[str, Any], *, timeout_seconds: float | None = None) -> dict[str, Any]:
    global WORKER_LAUNCH_COUNT
    WORKER_LAUNCH_COUNT += 1
    contract = load_json(CONTRACT_PATH)
    limits = contract["process_controls"]
    environment = os.environ.copy()
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        environment[key] = "1"
    environment["PYTHONHASHSEED"] = "0"
    environment["PYTHONNOUSERSITE"] = "1"
    process = subprocess.Popen(
        [sys.executable, str(WORKER_PATH)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
        preexec_fn=resource_preexec(contract),
    )
    timeout = float(limits["stage_timeout_seconds"] if timeout_seconds is None else timeout_seconds)
    timed_out = False
    try:
        stdout, stderr = process.communicate(canonical_bytes(request), timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=float(limits["termination_grace_seconds"]))
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
    maximum = int(limits["maximum_captured_stream_bytes"])
    require(len(stdout) <= maximum and len(stderr) <= maximum, "worker stream capture limit exceeded")
    parsed: dict[str, Any] | None = None
    if stdout:
        try:
            value = json.loads(stdout.decode("utf-8"))
            if isinstance(value, dict):
                parsed = value
        except (UnicodeDecodeError, json.JSONDecodeError):
            parsed = None
    return {
        "returncode": process.returncode,
        "timed_out": timed_out,
        "stdout": parsed,
        "stderr": stderr.decode("utf-8", errors="replace"),
    }


def require_success(result: dict[str, Any], expected_status: str) -> dict[str, Any]:
    require(result["timed_out"] is False, f"unexpected timeout for {expected_status}")
    require(result["returncode"] == 0, f"worker failed for {expected_status}: {result['stderr']}")
    payload = result["stdout"]
    require(isinstance(payload, dict), f"missing worker JSON for {expected_status}")
    require(payload.get("status") == expected_status, f"worker status drift: {payload.get('status')}")
    return payload


def validate_primary(primary: dict[str, Any], contract: dict[str, Any]) -> None:
    acceptance = contract["primary_control"]["acceptance"]
    require(primary["model_a_F"] == 0.0, "primary did not use a_F=0")
    require(primary["newton_call_count"] == 0, "primary Newton call detected")
    require(primary["cp01r1_attempts"] == 0 and primary["target_root_solves"] == 0, "primary target execution detected")
    require([record["node_count"] for record in primary["node_records"]] == [24, 48, 96], "primary mesh schedule drift")
    for record in primary["node_records"]:
        require(record["bulk_residual_inf"] <= acceptance["bulk_residual_inf_max"], "primary bulk control failed")
        require(record["constraint_inf"] <= acceptance["constraint_inf_max"], "primary constraint control failed")
        require(record["boundary_exact_distance"] <= acceptance["boundary_exact_distance_max"], "primary boundary control failed")
    require(primary["candidate_cross_mesh_distance"] <= acceptance["candidate_parameter_cross_mesh_distance_max"], "primary candidate cross-mesh drift")
    require(primary["candidate_sha256"] == sha256_value(primary["candidate"]), "primary candidate digest drift")


def validate_independent(independent: dict[str, Any], primary: dict[str, Any], contract: dict[str, Any]) -> list[dict[str, float]]:
    acceptance = contract["independent_control"]["acceptance"]
    require(independent["model_a_F"] == 0.0, "independent did not use a_F=0")
    require(independent["integration_call_count"] == acceptance["integration_call_count"], "independent integration count drift")
    require(independent["shooting_jacobian_call_count"] == 0, "shooting Jacobian call detected")
    require(independent["nonlinear_root_calls"] == 0, "independent nonlinear root call detected")
    require(independent["cp01r1_attempts"] == 0 and independent["target_root_solves"] == 0, "independent target execution detected")
    primary_boundary = primary["node_records"][-1]["boundary"]
    table: list[dict[str, float]] = []
    for record in independent["cutoff_records"]:
        backend_distance = max(abs(float(a) - float(b)) for a, b in zip(record["boundary"], primary_boundary))
        require(record["profile_error_inf"] <= acceptance["profile_error_inf_max"], "independent profile control failed")
        require(record["constraint_inf"] <= acceptance["constraint_inf_max"], "independent constraint control failed")
        require(record["boundary_exact_distance"] <= acceptance["boundary_exact_distance_max"], "independent boundary control failed")
        require(backend_distance <= acceptance["primary_independent_boundary_distance_max"], "real backend boundary disagreement")
        table.append({
            "epsilon": float(record["epsilon"]),
            "profile_error_inf": float(record["profile_error_inf"]),
            "constraint_inf": float(record["constraint_inf"]),
            "boundary_exact_distance": float(record["boundary_exact_distance"]),
            "primary_independent_boundary_distance": float(backend_distance),
        })
    return table


def result_schema_translation_preview(primary: dict[str, Any], independent: dict[str, Any], package_digest: str) -> dict[str, Any]:
    schema = load_json(RESULT_SCHEMA_PATH)
    required = schema["required_top_level_fields"]
    preview = {
        "schema": schema["schema"],
        "run_id": CONTROL_RUN_ID,
        "run_payload_sha256": FROZEN_PAYLOAD_SHA256,
        "implementation_source_sha256": package_digest,
        "dependency_lock_sha256": load_json(RUN_INPUT_PATH)["frozen_run_payload"]["dependency_lock_sha256"],
        "authorization_decision_id": "CONTROL_ONLY_NO_AUTHORIZATION",
        "execution_started_utc": None,
        "execution_finished_utc": None,
        "machine_environment": {"classification": "REAL_BACKEND_CONTROL_PROCESS_ONLY"},
        "primary_backend": {
            "classification": primary["status"],
            "node_counts": [record["node_count"] for record in primary["node_records"]],
            "candidate_sha256": primary["candidate_sha256"],
            "newton_call_count": primary["newton_call_count"],
        },
        "independent_backend": {
            "classification": independent["status"],
            "cutoffs": [record["epsilon"] for record in independent["cutoff_records"]],
            "integration_call_count": independent["integration_call_count"],
            "shooting_jacobian_call_count": independent["shooting_jacobian_call_count"],
        },
        "candidate_inventory": [{
            "candidate_id": "EXACT_AF0_CONTROL_HANDOFF",
            "profile_artifact_sha256": primary["candidate_sha256"],
            "classification": "ANALYTIC_CONTROL_NOT_PHYSICAL_CANDIDATE",
        }],
        "acceptance_audit": {"classification": "CONTROL_ONLY"},
        "final_classification": "NOT_EXECUTED_IMPLEMENTATION_FAILURE",
        "physical_evidence_effect": "NONE",
        "forbidden_inferences": [
            "physical_background", "continuum_existence", "stability",
            "ghost_freedom", "K1-D_release", "K1-E_admissibility",
        ],
    }
    require(set(preview) == set(required), "result-schema top-level translation incomplete")
    return {
        "required_fields": required,
        "mapped_fields": list(preview.keys()),
        "preview_sha256": sha256_value(preview),
        "preview": preview,
        "result_schema_preview_is_physical_result": False,
        "result_artifact_created": False,
    }


class AtomicControlWriter:
    def __init__(self, output_root: Path, control_id: str):
        resolved = output_root.expanduser().resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            pass
        else:
            raise ReleaseFailure("control output root must be external to repository")
        self.output_root = resolved
        self.control_id = control_id
        self.final = resolved / control_id
        self.partial = resolved / f".{control_id}.partial-{uuid.uuid4().hex}"

    def commit(self, result: dict[str, Any]) -> Path:
        if self.final.exists():
            raise ReleaseFailure("final control artifact already exists")
        self.output_root.mkdir(parents=True, exist_ok=True)
        self.partial.mkdir(parents=False, exist_ok=False)
        result_bytes = canonical_bytes(result) + b"\n"
        result_path = self.partial / "result.json"
        result_path.write_bytes(result_bytes)
        manifest = {
            "schema": "universelab.background-3c10-control-artifact-manifest.v0.1",
            "control_id": self.control_id,
            "result_sha256": hashlib.sha256(result_bytes).hexdigest(),
            "physical_result": False,
            "physical_evidence_effect": "NONE",
        }
        (self.partial / "artifact-manifest.json").write_bytes(canonical_bytes(manifest) + b"\n")
        os.replace(self.partial, self.final)
        return self.final

    def cleanup(self) -> None:
        if self.partial.exists():
            shutil.rmtree(self.partial)


def execute_controls(*, commit_external_artifact: bool = True) -> dict[str, Any]:
    audit = static_audit()
    contract = load_json(CONTRACT_PATH)
    payload = load_json(RUN_INPUT_PATH)["frozen_run_payload"]

    primary_request = worker_envelope("primary_control", payload)
    primary_request["node_counts"] = contract["primary_control"]["node_counts"]
    primary = require_success(
        launch_worker(primary_request),
        "PASS_REAL_PRIMARY_AF0_CONTROL_NO_NEWTON",
    )
    validate_primary(primary, contract)

    handoff = {
        "candidate": primary["candidate"],
        "candidate_sha256": primary["candidate_sha256"],
    }
    independent_request = worker_envelope("independent_control", payload)
    independent_request["cutoffs"] = contract["independent_control"]["pole_cutoffs"]
    independent_request["handoff"] = handoff
    independent = require_success(
        launch_worker(independent_request),
        "PASS_REAL_INDEPENDENT_AF0_CONTROL_NO_ROOT",
    )
    cutoff_table = validate_independent(independent, primary, contract)

    tampered_request = json.loads(json.dumps(independent_request))
    tampered_request["handoff"]["candidate_sha256"] = "0" * 64
    tampered = launch_worker(tampered_request)
    require(tampered["timed_out"] is False and tampered["returncode"] == 2, "tampered handoff was not rejected")
    require(isinstance(tampered["stdout"], dict) and tampered["stdout"].get("status") == "CONTROL_FAILURE", "tampered handoff classification drift")
    require("digest mismatch" in tampered["stdout"].get("error", ""), "tampered handoff reason drift")

    timeout_request = worker_envelope("timeout_probe", payload)
    timeout_request["sleep_seconds"] = 30.0
    timeout_result = launch_worker(timeout_request, timeout_seconds=1.0)
    require(timeout_result["timed_out"] is True, "real-primary timeout probe did not time out")
    require(timeout_result["returncode"] in (-signal.SIGTERM, -signal.SIGKILL), "timeout probe termination drift")

    signal_request = worker_envelope("signal_probe", payload)
    signal_result = launch_worker(signal_request)
    require(signal_result["timed_out"] is False, "signal probe unexpectedly timed out")
    require(signal_result["returncode"] == -signal.SIGTERM, "real-independent signal probe return code drift")

    translation = result_schema_translation_preview(primary, independent, audit["package_manifest_sha256"])
    result = {
        "schema": "universelab.hzt-m0-s6-c-phys-m1.background-3c10-control-result.v0.1",
        "status": "PASS_REAL_BACKEND_AF0_CONTROL_RELEASE_NO_TARGET_SOLVE",
        "control_run_id": CONTROL_RUN_ID,
        "frozen_physical_run_id": FROZEN_RUN_ID,
        "package_manifest_sha256": audit["package_manifest_sha256"],
        "primary": primary,
        "independent": independent,
        "cutoff_table": cutoff_table,
        "handoff_digest_verified": True,
        "tampered_handoff_rejected": True,
        "timeout_probe": "PASS_REAL_PRIMARY_IMPORT_THEN_CLEAN_TERMINATION",
        "signal_probe": "PASS_REAL_INDEPENDENT_IMPORT_THEN_SIGNAL_TERMINATION",
        "result_schema_translation": translation,
        "worker_launch_count": WORKER_LAUNCH_COUNT,
        "real_backend_control_processes": 4,
        "primary_newton_calls": 0,
        "independent_shooting_jacobian_calls": 0,
        "nonlinear_root_calls": 0,
        "cp01r1_attempts": CP01R1_ATTEMPT_COUNT,
        "target_a_F_one_quarter_solves": TARGET_ROOT_SOLVE_COUNT,
        "operative_grants_created": OPERATIVE_GRANT_CREATE_COUNT,
        "physical_result_artifacts_created": PHYSICAL_RESULT_CREATE_COUNT,
        "physical_evidence_effect": "NONE",
        "next_block": "C-PHYS-R1.0-BACKGROUND-3C11_REAL_BACKEND_CONTROL_RELEASE_AUTHORIZATION_REVIEW_ONLY",
    }
    external_artifact = None
    no_overwrite = False
    if commit_external_artifact:
        with tempfile.TemporaryDirectory(prefix="universelab-bg3c10-") as temporary:
            output_root = Path(temporary) / "controls"
            writer = AtomicControlWriter(output_root, CONTROL_RUN_ID)
            try:
                final = writer.commit(result)
                require((final / "result.json").is_file(), "atomic control result missing")
                require((final / "artifact-manifest.json").is_file(), "atomic control manifest missing")
                external_artifact = "PASS_TEMPORARY_EXTERNAL_DIRECTORY_ONLY"
                second = AtomicControlWriter(output_root, CONTROL_RUN_ID)
                try:
                    second.commit(result)
                except ReleaseFailure as exc:
                    no_overwrite = "already exists" in str(exc)
                else:
                    raise ReleaseFailure("no-overwrite control failed")
            finally:
                writer.cleanup()
    result["external_atomic_control_artifact"] = external_artifact
    result["no_overwrite_firewall"] = no_overwrite
    require(all(not path.exists() for path in OPERATIVE_GRANT_PATHS), "control transaction created a grant")
    require(not PHYSICAL_ARTIFACT_ROOT.exists(), "control transaction created a physical result path")
    return result


def self_test() -> dict[str, Any]:
    result = execute_controls(commit_external_artifact=True)
    require(result["status"] == "PASS_REAL_BACKEND_AF0_CONTROL_RELEASE_NO_TARGET_SOLVE", "control release status drift")
    require(result["worker_launch_count"] == 5, "worker launch count drift")
    require(result["real_backend_control_processes"] == 4, "real backend control process count drift")
    require(result["primary_newton_calls"] == 0, "Newton call drift")
    require(result["independent_shooting_jacobian_calls"] == 0, "shooting Jacobian drift")
    require(result["nonlinear_root_calls"] == 0, "nonlinear root drift")
    require(result["cp01r1_attempts"] == 0, "CP01R1 attempt drift")
    require(result["target_a_F_one_quarter_solves"] == 0, "target solve drift")
    require(result["operative_grants_created"] == 0, "grant creation drift")
    require(result["physical_result_artifacts_created"] == 0, "physical result creation drift")
    require(result["no_overwrite_firewall"] is True, "no-overwrite firewall drift")
    return result


def denied_physical_run() -> dict[str, Any]:
    return {
        "status": "NOT_AUTHORIZED",
        "reason": "Background-3C10 is an a_F=0 real-backend control release only; CP01R1 and target-root execution remain forbidden",
        "physical_backend_imported": False,
        "solver_calls": 0,
        "cp01r1_attempted": False,
        "target_a_F_one_quarter_solve": False,
        "operative_grant_created": False,
        "result_artifact_created": False,
        "physical_evidence_effect": "NONE",
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit", "self-test", "run"))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def emit(payload: dict[str, Any], as_json: bool) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True) if as_json else payload["status"])


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "audit":
            emit(static_audit(), args.json)
            return 0
        if args.command == "self-test":
            emit(self_test(), args.json)
            return 0
        if args.command == "run":
            emit(denied_physical_run(), args.json)
            return EXIT_NOT_AUTHORIZED
    except ReleaseFailure as exc:
        payload = {
            "status": "CONTROL_RELEASE_FAILURE",
            "error": str(exc),
            "worker_launches": WORKER_LAUNCH_COUNT,
            "solver_calls": 0,
            "cp01r1_attempts": CP01R1_ATTEMPT_COUNT,
            "result_artifact_created": False,
            "physical_evidence_effect": "NONE",
        }
        emit(payload, args.json)
        return EXIT_CONTROL_FAILURE
    return EXIT_CONTROL_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
