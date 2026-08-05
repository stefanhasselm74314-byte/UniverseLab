#!/usr/bin/env python3
"""Background-3C8 source-bound physical adapter control release.

This module binds the frozen CP01R1 payload, seed schedule, physical backend
source inventory, candidate handoff, result-schema translation, resource
boundary, and replay prevention. All executable controls use manufactured
backend stubs. Real physical backend import and CP01R1 execution are denied.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import tempfile
from typing import Any, Iterable
import uuid


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C8PhysicalExecutionAdapterContract_v0.1.json"
WORKER_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c8_manufactured_backend_worker_v0.1.py"
RUN_INPUT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"
SEED_SPEC_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BSeedSpecification_v0.1.json"
RESULT_SCHEMA_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResultSchema_v0.1.json"
RESOURCE_POLICY_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
REVIEW_3C7_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C7IntegratedReleaseAuthorizationReview_v0.1.json"
PRIMARY_V01_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.1.py"
PRIMARY_V02_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py"
INDEPENDENT_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_independent_backend_v0.1.py"
OPERATIVE_GRANT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
PHYSICAL_ARTIFACT_ROOT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"

RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
RUN_PAYLOAD_SHA256 = "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302"
SEED_SET_ID = "M1-BG3B-CP01-SEEDS-01"
SEED_SPEC_SHA256 = "b6e4319cc29736799a0b46320002e51cd17b70b724a6b4c6e86567a316996161"
CONTROL_ID_PREFIX = "HZT-M0-S6-C-PHYS-M1-BG3C8-CONTROL-"
CONTROL_SCOPE = "MANUFACTURED_ADAPTER_CONTROL_ONLY"
EXIT_NOT_AUTHORIZED = 73
EXIT_ADAPTER_FAILURE = 74

STUB_SUBPROCESS_LAUNCH_COUNT = 0
PRIMARY_PHYSICAL_ROOT_CALL_COUNT = 0
INDEPENDENT_PHYSICAL_ROOT_CALL_COUNT = 0
SHOOTING_JACOBIAN_CALL_COUNT = 0
CP01R1_ATTEMPT_COUNT = 0


class AdapterError(RuntimeError):
    pass


class ReplayRejected(AdapterError):
    pass


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


def sha256_value(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise AdapterError(f"missing required file: {path.relative_to(ROOT)}") from error
    except json.JSONDecodeError as error:
        raise AdapterError(f"invalid JSON: {path.relative_to(ROOT)}") from error
    if not isinstance(value, dict):
        raise AdapterError(f"top-level object required: {path.relative_to(ROOT)}")
    return value


def package_manifest() -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    sources: dict[str, str] = {}
    for relative in contract["package_source_paths"]:
        path = ROOT / relative
        if not path.is_file():
            raise AdapterError(f"missing package source: {relative}")
        sources[relative] = sha256_file(path)
    return {
        "sources": sources,
        "source_count": len(sources),
        "package_manifest_sha256": sha256_value(sources),
    }


def function_definitions(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modules.add(node.module or "")
    return modules


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


def validate_real_backend_bindings(contract: dict[str, Any]) -> dict[str, Any]:
    primary_binding = contract["physical_backend_bindings"]["primary"]
    independent_binding = contract["physical_backend_bindings"]["independent"]
    primary_exports = function_definitions(PRIMARY_V01_PATH) | function_definitions(PRIMARY_V02_PATH)
    independent_exports = function_definitions(INDEPENDENT_PATH)
    missing_primary = sorted(set(primary_binding["expected_exports"]) - primary_exports)
    missing_independent = sorted(set(independent_binding["expected_exports"]) - independent_exports)
    if missing_primary or missing_independent:
        raise AdapterError(
            f"physical backend export drift: primary={missing_primary}, independent={missing_independent}"
        )
    return {
        "primary_source_sha256": sha256_file(PRIMARY_V02_PATH),
        "primary_base_source_sha256": sha256_file(PRIMARY_V01_PATH),
        "independent_source_sha256": sha256_file(INDEPENDENT_PATH),
        "primary_exports_verified": sorted(primary_binding["expected_exports"]),
        "independent_exports_verified": sorted(independent_binding["expected_exports"]),
        "physical_backend_imported": False,
    }


def build_schedule() -> list[dict[str, Any]]:
    multipliers = ["0", "1/8", "-1/8", "1/4", "-1/4", "1/2", "-1/2"]
    node_counts = [24, 32, 48, 64, 96]
    schedule: list[dict[str, Any]] = []
    ordinal = 0
    for seed_index, multiplier in enumerate(multipliers):
        for node_count in node_counts:
            schedule.append({
                "ordinal": ordinal,
                "seed_index": seed_index,
                "seed_multiplier": multiplier,
                "node_count": node_count,
                "degree": node_count - 1,
            })
            ordinal += 1
    return schedule


def validate_frozen_bindings(contract: dict[str, Any]) -> dict[str, Any]:
    run_input = load_json(RUN_INPUT_PATH)
    seed_spec = load_json(SEED_SPEC_PATH)
    result_schema = load_json(RESULT_SCHEMA_PATH)
    resource_policy = load_json(RESOURCE_POLICY_PATH)
    review = load_json(REVIEW_3C7_PATH)
    binding = contract["immutable_run_binding"]
    payload = run_input["frozen_run_payload"]
    if binding["run_id"] != RUN_ID or payload["run_id"] != RUN_ID:
        raise AdapterError("run ID binding drift")
    if binding["run_payload_sha256"] != RUN_PAYLOAD_SHA256:
        raise AdapterError("contract run payload digest drift")
    if run_input["frozen_run_payload_sha256"] != RUN_PAYLOAD_SHA256:
        raise AdapterError("frozen run payload digest drift")
    if binding["seed_set_id"] != SEED_SET_ID or seed_spec["seed_set_id"] != SEED_SET_ID:
        raise AdapterError("seed set binding drift")
    if binding["seed_spec_sha256"] != SEED_SPEC_SHA256:
        raise AdapterError("contract seed digest drift")
    if seed_spec["canonical_payload_sha256"] != SEED_SPEC_SHA256:
        raise AdapterError("seed specification digest drift")
    if binding["seed_count"] != 7 or seed_spec["seed_generation"]["seed_count"] != 7:
        raise AdapterError("seed count drift")
    if binding["node_counts_ordered"] != [24, 32, 48, 64, 96]:
        raise AdapterError("node schedule drift")
    schedule = build_schedule()
    if len(schedule) != binding["expected_schedule_entries"]:
        raise AdapterError("schedule entry count drift")
    if result_schema["run_id"] != RUN_ID:
        raise AdapterError("result schema run ID drift")
    if resource_policy["run_id"] != RUN_ID:
        raise AdapterError("resource policy run ID drift")
    if resource_policy["current_state"]["execution_authorized"] is not False:
        raise AdapterError("resource policy unexpectedly authorizes execution")
    if review["status"] != "DENIED_PHYSICAL_BACKEND_ADAPTER_AND_SINGLE_USE_GRANT_RELEASE_ABSENT":
        raise AdapterError("Background-3C7 review status drift")
    return {
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "seed_set_id": SEED_SET_ID,
        "seed_spec_sha256": SEED_SPEC_SHA256,
        "schedule_entry_count": len(schedule),
        "schedule_sha256": sha256_value(schedule),
        "dependency_lock_sha256": payload["dependency_lock_sha256"],
    }


def issue_manufactured_capability(control_id: str, package_digest: str) -> dict[str, Any]:
    if not control_id.startswith(CONTROL_ID_PREFIX):
        raise AdapterError("control ID is outside the registered prefix")
    token_payload = {
        "scope": CONTROL_SCOPE,
        "control_id": control_id,
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "adapter_package_sha256": package_digest,
        "physical_authorized": False,
        "nonce": control_id,
    }
    return {
        "scope": CONTROL_SCOPE,
        "control_id": control_id,
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "adapter_package_sha256": package_digest,
        "physical_authorized": False,
        "token_payload": token_payload,
        "token_sha256": sha256_value(token_payload),
    }


def consume_capability_once(capability: dict[str, Any], ledger_root: Path) -> Path:
    if capability.get("scope") != CONTROL_SCOPE or capability.get("physical_authorized") is not False:
        raise AdapterError("manufactured capability scope violation")
    ledger_root.mkdir(parents=True, exist_ok=True)
    marker = ledger_root / f"{capability['token_sha256']}.consumed.json"
    payload = {
        "schema": "universelab.background-3c8-manufactured-capability-consumption.v0.1",
        "token_sha256": capability["token_sha256"],
        "control_id": capability["control_id"],
        "scope": capability["scope"],
        "physical_authorized": False,
    }
    try:
        with marker.open("xb") as stream:
            stream.write(canonical_json_bytes(payload) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as error:
        raise ReplayRejected("manufactured capability replay rejected") from error
    return marker


def ensure_external_output_root(output_root: Path) -> Path:
    resolved = output_root.expanduser().resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        pass
    else:
        raise AdapterError("control output root must be external to the repository")
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def resource_preexec(contract: dict[str, Any]):
    if os.name != "posix":
        return None
    limits = contract["resource_control"]
    def apply() -> None:
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (int(limits["worker_address_space_bytes"]),) * 2)
        resource.setrlimit(resource.RLIMIT_CPU, (int(limits["worker_cpu_seconds"]), int(limits["worker_cpu_seconds"]) + 1))
        resource.setrlimit(resource.RLIMIT_FSIZE, (int(limits["worker_file_bytes"]),) * 2)
        resource.setrlimit(resource.RLIMIT_NOFILE, (int(limits["worker_open_files"]),) * 2)
    return apply


def launch_stub(payload: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    global STUB_SUBPROCESS_LAUNCH_COUNT
    STUB_SUBPROCESS_LAUNCH_COUNT += 1
    limits = contract["resource_control"]
    encoded = canonical_json_bytes(payload)
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
    timed_out = False
    try:
        stdout, stderr = process.communicate(encoded, timeout=float(limits["stage_timeout_seconds"]))
    except subprocess.TimeoutExpired:
        timed_out = True
        process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=float(limits["termination_grace_seconds"]))
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
    maximum = int(limits["maximum_captured_stream_bytes"])
    if len(stdout) > maximum or len(stderr) > maximum:
        raise AdapterError("manufactured worker stream exceeds capture limit")
    result: dict[str, Any] | None = None
    if stdout:
        try:
            value = json.loads(stdout.decode("utf-8"))
            if isinstance(value, dict):
                result = value
        except (UnicodeDecodeError, json.JSONDecodeError):
            result = None
    return {
        "returncode": process.returncode,
        "timed_out": timed_out,
        "stdout_bytes": len(stdout),
        "stderr_bytes": len(stderr),
        "stdout_sha256": sha256_bytes(stdout),
        "stderr_sha256": sha256_bytes(stderr),
        "payload": result,
    }


def validate_primary_response(response: dict[str, Any], schedule: list[dict[str, Any]]) -> dict[str, Any]:
    payload = response.get("payload")
    if response["timed_out"] or response["returncode"] != 0 or not isinstance(payload, dict):
        raise AdapterError("manufactured primary stub did not complete successfully")
    if payload.get("stage") != "primary" or payload.get("backend_kind") != "MANUFACTURED_STUB":
        raise AdapterError("primary stub identity mismatch")
    if payload.get("schedule_sha256") != sha256_value(schedule):
        raise AdapterError("primary schedule echo mismatch")
    if payload.get("schedule_entry_count") != 35:
        raise AdapterError("primary schedule entry count mismatch")
    if len(payload.get("per_seed_per_level_history", [])) != 35:
        raise AdapterError("primary history length mismatch")
    if payload.get("newton_calls") != 0 or payload.get("physical_backend_imported") is not False:
        raise AdapterError("primary physical execution firewall violated")
    handoff = payload.get("candidate_handoff")
    if not isinstance(handoff, dict):
        raise AdapterError("primary candidate handoff missing")
    core = {key: value for key, value in handoff.items() if key != "candidate_payload_sha256"}
    if handoff.get("candidate_payload_sha256") != sha256_value(core):
        raise AdapterError("primary candidate handoff digest mismatch")
    return payload


def validate_independent_response(response: dict[str, Any], handoff: dict[str, Any]) -> dict[str, Any]:
    payload = response.get("payload")
    if response["timed_out"] or response["returncode"] != 0 or not isinstance(payload, dict):
        raise AdapterError("manufactured independent stub did not complete successfully")
    if payload.get("stage") != "independent" or payload.get("backend_kind") != "MANUFACTURED_STUB":
        raise AdapterError("independent stub identity mismatch")
    if payload.get("candidate_payload_sha256") != handoff["candidate_payload_sha256"]:
        raise AdapterError("independent candidate digest mismatch")
    if payload.get("shooting_calls") != 0 or payload.get("shooting_jacobian_calls") != 0:
        raise AdapterError("independent physical execution firewall violated")
    if payload.get("physical_backend_imported") is not False:
        raise AdapterError("independent backend import firewall violated")
    return payload


def build_result_schema_preview(
    package_digest: str,
    binding: dict[str, Any],
    backend_binding: dict[str, Any],
    primary: dict[str, Any],
    independent: dict[str, Any],
) -> dict[str, Any]:
    schema = load_json(RESULT_SCHEMA_PATH)
    candidate_handoff = primary["candidate_handoff"]
    independent_residuals = independent["per_candidate_residuals"]
    candidate = {
        "candidate_id": candidate_handoff["candidate_id"],
        "source_seed_indices": candidate_handoff["source_seed_indices"],
        "profile_artifact_sha256": candidate_handoff["candidate_payload_sha256"],
        "augmented_variables": candidate_handoff["augmented_variables"],
        "admissibility_gates": {"manufactured_control_only": True, "physical_candidate": False},
        "all_eight_boundary_residuals": independent_residuals,
        "bulk_residual_max": 0.0,
        "constraint_max": 0.0,
        "fine_mesh_profile_difference": 0.0,
        "fine_mesh_augmented_difference": 0.0,
        "independent_backend_distance": independent["candidate_distance_to_primary"],
        "classification": independent["agreement_classification"],
    }
    preview = {
        "schema": schema["schema"],
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "implementation_source_sha256": package_digest,
        "dependency_lock_sha256": binding["dependency_lock_sha256"],
        "authorization_decision_id": "MANUFACTURED_CONTROL_NO_OPERATIVE_DECISION",
        "execution_started_utc": None,
        "execution_finished_utc": None,
        "machine_environment": {
            "classification": "MANUFACTURED_ADAPTER_CONTROL_ONLY",
            "python": platform.python_version(),
            "platform": platform.platform(),
            "physical_execution": False,
        },
        "primary_backend": {
            "node_counts": [24, 32, 48, 64, 96],
            "per_seed_per_level_history": primary["per_seed_per_level_history"],
            "all_boundary_residuals": [],
            "bulk_residual_norms": [],
            "constraint_norms": [],
            "profile_convergence": {"classification": "MANUFACTURED_SERIALIZATION_ONLY"},
            "augmented_variable_convergence": {"classification": "MANUFACTURED_SERIALIZATION_ONLY"},
            "spectral_tail_table": [],
            "rrqr_ranks": [],
            "singular_values": [],
            "condition_estimates": [],
        },
        "independent_backend": {
            "implementation_source_sha256": backend_binding["independent_source_sha256"],
            "residual_assembly_independence_statement": "MANUFACTURED_STUB_ONLY_REAL_BACKEND_NOT_IMPORTED",
            "grid_or_mesh_definition": {"classification": "MANUFACTURED_HANDOFF_CONTROL"},
            "per_candidate_residuals": independent_residuals,
            "candidate_distance_to_primary": independent["candidate_distance_to_primary"],
            "agreement_classification": independent["agreement_classification"],
        },
        "candidate_inventory": [candidate],
        "acceptance_audit": {
            "schema_preview_only": True,
            "physical_result": False,
            "operative_grant": False,
            "physical_backend_imported": False,
        },
        "final_classification": "NOT_EXECUTED_IMPLEMENTATION_FAILURE",
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
    required_top = set(schema["required_top_level_fields"])
    if not required_top.issubset(preview):
        raise AdapterError("result schema preview misses top-level fields")
    if not set(schema["primary_backend_required_fields"]).issubset(preview["primary_backend"]):
        raise AdapterError("result schema preview misses primary fields")
    if not set(schema["independent_backend_required_fields"]).issubset(preview["independent_backend"]):
        raise AdapterError("result schema preview misses independent fields")
    if not set(schema["candidate_required_fields"]).issubset(candidate):
        raise AdapterError("result schema preview misses candidate fields")
    return preview


def write_control_artifact(final_directory: Path, payload: dict[str, Any], maximum_bytes: int) -> Path:
    if final_directory.exists():
        raise AdapterError("final control artifact already exists")
    staging = final_directory.with_name(f".{final_directory.name}.staging-{uuid.uuid4().hex}")
    staging.mkdir(parents=True, exist_ok=False)
    try:
        result_data = canonical_json_bytes(payload) + b"\n"
        if len(result_data) > maximum_bytes:
            raise AdapterError("control result exceeds artifact budget")
        result_path = staging / "result.json"
        with result_path.open("xb") as stream:
            stream.write(result_data)
            stream.flush()
            os.fsync(stream.fileno())
        manifest = {
            "schema": "universelab.background-3c8-control-artifact-manifest.v0.1",
            "control_id": payload["control_id"],
            "physical_result": False,
            "files": {"result.json": sha256_bytes(result_data)},
        }
        manifest_data = canonical_json_bytes(manifest) + b"\n"
        with (staging / "artifact-manifest.json").open("xb") as stream:
            stream.write(manifest_data)
            stream.flush()
            os.fsync(stream.fileno())
        if sum(item.stat().st_size for item in staging.iterdir()) > maximum_bytes:
            raise AdapterError("control artifact set exceeds budget")
        os.replace(staging, final_directory)
        return final_directory
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def audit_release() -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    if contract["status"] != "IMPLEMENTED_PENDING_AUDIT_PHYSICAL_EXECUTION_NOT_AUTHORIZED":
        raise AdapterError("3C8 contract status drift")
    if contract["canonical_entry_point"] != str(Path(__file__).relative_to(ROOT)):
        raise AdapterError("canonical adapter entry-point binding mismatch")
    if contract["physical_execution_authorized"] is not False:
        raise AdapterError("physical execution unexpectedly authorized")
    if contract["cp01r1_execution_authorized"] is not False:
        raise AdapterError("CP01R1 unexpectedly authorized")
    if contract["operative_grant_creation_allowed"] is not False:
        raise AdapterError("operative grant creation unexpectedly allowed")
    binding = validate_frozen_bindings(contract)
    backend_binding = validate_real_backend_bindings(contract)
    package = package_manifest()

    modules = imported_modules(Path(__file__)) | imported_modules(WORKER_PATH)
    calls = called_names(Path(__file__)) | called_names(WORKER_PATH)
    forbidden_module_fragments = {
        "background_3c_primary_kernel",
        "background_3c_independent_backend",
    }
    forbidden_calls = {
        "damped_newton",
        "shooting_residual",
        "centered_fd_jacobian",
        "complex_step_jacobian",
        "integrate_region",
    }
    violating_modules = sorted(
        module for module in modules
        if any(fragment in module for fragment in forbidden_module_fragments)
    )
    violating_calls = sorted(calls & forbidden_calls)
    if violating_modules or violating_calls:
        raise AdapterError(
            f"physical execution dependency in control path: modules={violating_modules}, calls={violating_calls}"
        )
    if OPERATIVE_GRANT_PATH.exists() or PHYSICAL_ARTIFACT_ROOT.exists():
        raise AdapterError("operative grant or physical artifact unexpectedly exists")
    return {
        "status": "PASS_PHYSICAL_ADAPTER_STATIC_AUDIT_NO_PHYSICAL_EXECUTION",
        "package_manifest_sha256": package["package_manifest_sha256"],
        "source_count": package["source_count"],
        "run_binding": binding,
        "backend_binding": backend_binding,
        "inspected_control_modules": len(modules),
        "inspected_control_call_names": len(calls),
        "forbidden_modules": violating_modules,
        "forbidden_calls": violating_calls,
        "stub_subprocess_launches": STUB_SUBPROCESS_LAUNCH_COUNT,
        "primary_physical_root_calls": PRIMARY_PHYSICAL_ROOT_CALL_COUNT,
        "independent_physical_root_calls": INDEPENDENT_PHYSICAL_ROOT_CALL_COUNT,
        "shooting_jacobian_calls": SHOOTING_JACOBIAN_CALL_COUNT,
        "cp01r1_attempts": CP01R1_ATTEMPT_COUNT,
        "operative_grant_present": False,
        "physical_result_artifact_present": False,
        "physical_evidence_effect": "NONE",
    }


def common_worker_payload(
    stage: str,
    behavior: str,
    capability: dict[str, Any],
    binding: dict[str, Any],
) -> dict[str, Any]:
    return {
        "stage": stage,
        "behavior": behavior,
        "binding": {
            "run_id": RUN_ID,
            "run_payload_sha256": RUN_PAYLOAD_SHA256,
            "seed_set_id": SEED_SET_ID,
            "seed_spec_sha256": SEED_SPEC_SHA256,
            "schedule_sha256": binding["schedule_sha256"],
        },
        "capability": capability,
    }


def run_control(case: str, control_id: str, output_root: Path) -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    if case not in contract["allowed_control_cases"]:
        raise AdapterError("unregistered manufactured control case")
    root = ensure_external_output_root(output_root)
    final_directory = root / control_id
    if final_directory.exists():
        raise AdapterError("final control artifact already exists")
    audit = audit_release()
    binding = audit["run_binding"]
    capability = issue_manufactured_capability(control_id, audit["package_manifest_sha256"])
    consume_capability_once(capability, root / ".capability-ledger")
    schedule = build_schedule()

    primary_behavior = "success"
    if case == "manufactured_timeout":
        primary_behavior = "timeout"
    elif case == "manufactured_signal":
        primary_behavior = "signal"
    primary_request = common_worker_payload("primary", primary_behavior, capability, binding)
    primary_request["schedule"] = schedule
    primary_request["schedule_sha256"] = binding["schedule_sha256"]
    primary_response = launch_stub(primary_request, contract)

    if primary_response["timed_out"]:
        return {
            "status": "PASS_CONTROL_ADAPTER_CLEAN_ABORT",
            "case": case,
            "control_id": control_id,
            "final_classification": "CONTROL_ADAPTER_TIMEOUT_CLEAN_ABORT",
            "final_artifact_created": False,
            "physical_solver_calls": 0,
            "physical_evidence_effect": "NONE",
        }
    if primary_response["returncode"] is not None and primary_response["returncode"] < 0:
        return {
            "status": "PASS_CONTROL_ADAPTER_CLEAN_ABORT",
            "case": case,
            "control_id": control_id,
            "final_classification": "CONTROL_ADAPTER_SIGNAL_CLEAN_ABORT",
            "final_artifact_created": False,
            "physical_solver_calls": 0,
            "physical_evidence_effect": "NONE",
        }

    primary = validate_primary_response(primary_response, schedule)
    independent_behavior = "disagreement" if case == "manufactured_disagreement" else "success"
    independent_request = common_worker_payload("independent", independent_behavior, capability, binding)
    independent_request["candidate_handoff"] = primary["candidate_handoff"]
    independent_response = launch_stub(independent_request, contract)
    independent = validate_independent_response(independent_response, primary["candidate_handoff"])
    preview = build_result_schema_preview(
        audit["package_manifest_sha256"],
        binding,
        audit["backend_binding"],
        primary,
        independent,
    )
    final_classification = (
        "CONTROL_ADAPTER_DISAGREEMENT_REJECTED_AS_EXPECTED"
        if case == "manufactured_disagreement"
        else "CONTROL_ADAPTER_TRANSACTION_PASS"
    )
    result = {
        "schema": "universelab.background-3c8-control-transaction-result.v0.1",
        "status": "PASS_CONTROL_ADAPTER_TRANSACTION_COMMITTED",
        "case": case,
        "control_id": control_id,
        "created_utc": utc_now(),
        "package_manifest_sha256": audit["package_manifest_sha256"],
        "run_binding": binding,
        "manufactured_capability": {
            "scope": capability["scope"],
            "token_sha256": capability["token_sha256"],
            "physical_authorized": False,
            "single_consumption": True,
        },
        "primary_process": {key: value for key, value in primary_response.items() if key != "payload"},
        "independent_process": {key: value for key, value in independent_response.items() if key != "payload"},
        "primary_stub": primary,
        "independent_stub": independent,
        "result_schema_preview": preview,
        "result_schema_preview_is_physical_result": False,
        "final_classification": final_classification,
        "physical_backend_imported": False,
        "physical_solver_calls": 0,
        "cp01r1_attempted": False,
        "operative_grant_created": False,
        "physical_evidence_effect": "NONE",
    }
    write_control_artifact(
        final_directory,
        result,
        int(contract["resource_control"]["maximum_control_artifact_bytes"]),
    )
    return {
        "status": result["status"],
        "case": case,
        "control_id": control_id,
        "final_classification": final_classification,
        "final_artifact_created": True,
        "final_artifact_path": str(final_directory),
        "package_manifest_sha256": audit["package_manifest_sha256"],
        "physical_solver_calls": 0,
        "physical_evidence_effect": "NONE",
    }


def self_test() -> dict[str, Any]:
    audit = audit_release()
    start_launches = STUB_SUBPROCESS_LAUNCH_COUNT
    classifications: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="universelab-bg3c8-") as temporary:
        root = Path(temporary)
        for suffix, case in (
            ("SUCCESS", "manufactured_success"),
            ("DISAGREEMENT", "manufactured_disagreement"),
            ("TIMEOUT", "manufactured_timeout"),
            ("SIGNAL", "manufactured_signal"),
        ):
            control_id = f"{CONTROL_ID_PREFIX}{suffix}"
            result = run_control(case, control_id, root)
            classifications[case] = result["final_classification"]
            if case in {"manufactured_success", "manufactured_disagreement"}:
                if not (root / control_id / "result.json").is_file():
                    raise AdapterError("committable control did not create result.json")
            elif (root / control_id).exists():
                raise AdapterError("clean-abort control created a final artifact")

        no_overwrite = False
        try:
            run_control("manufactured_success", f"{CONTROL_ID_PREFIX}SUCCESS", root)
        except AdapterError as error:
            no_overwrite = str(error)
        if not no_overwrite:
            raise AdapterError("no-overwrite test did not reject existing final path")

        replay_capability = issue_manufactured_capability(
            f"{CONTROL_ID_PREFIX}REPLAY",
            audit["package_manifest_sha256"],
        )
        replay_ledger = root / ".replay-ledger"
        consume_capability_once(replay_capability, replay_ledger)
        replay_rejected = False
        try:
            consume_capability_once(replay_capability, replay_ledger)
        except ReplayRejected:
            replay_rejected = True
        if not replay_rejected:
            raise AdapterError("manufactured capability replay was not rejected")

    expected = load_json(CONTRACT_PATH)["expected_control_classifications"]
    if classifications != expected:
        raise AdapterError(f"control classification drift: {classifications}")
    launches = STUB_SUBPROCESS_LAUNCH_COUNT - start_launches
    if launches != 6:
        raise AdapterError(f"expected six manufactured subprocess launches, found {launches}")
    return {
        "status": "PASS_PHYSICAL_ADAPTER_MANUFACTURED_END_TO_END_CONTROLS",
        "package_manifest_sha256": audit["package_manifest_sha256"],
        "classifications": classifications,
        "manufactured_subprocess_launches": launches,
        "committed_external_control_artifacts": 2,
        "clean_abort_controls": 2,
        "capability_replay_rejected": True,
        "no_overwrite_firewall": no_overwrite,
        "primary_physical_root_calls": 0,
        "independent_physical_root_calls": 0,
        "shooting_jacobian_calls": 0,
        "cp01r1_attempts": 0,
        "operative_grant_present": False,
        "repository_physical_result_present": False,
        "physical_evidence_effect": "NONE",
    }


def denied_physical_run(run_id: str | None) -> dict[str, Any]:
    if run_id not in {None, RUN_ID}:
        raise AdapterError("physical run ID mismatch")
    return {
        "status": "NOT_AUTHORIZED",
        "reason": "Background-3C8 is implementation-only and cannot execute CP01R1",
        "run_id": RUN_ID,
        "physical_backend_imported": False,
        "solver_calls": 0,
        "cp01r1_attempted": False,
        "operative_grant_created": False,
        "result_artifact_created": False,
        "physical_evidence_effect": "NONE",
    }


def emit(payload: dict[str, Any], as_json: bool) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True) if as_json else payload["status"])


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("audit", "self-test"):
        item = subparsers.add_parser(command)
        item.add_argument("--json", action="store_true")
    control = subparsers.add_parser("control")
    control.add_argument("--case", required=True)
    control.add_argument("--control-id", required=True)
    control.add_argument("--output-root", required=True)
    control.add_argument("--json", action="store_true")
    run = subparsers.add_parser("run")
    run.add_argument("--run-id")
    run.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
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
    except (AdapterError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        emit({
            "status": "ADAPTER_CONTROL_FAILURE",
            "error": f"{type(error).__name__}: {error}",
            "physical_backend_imported": False,
            "solver_calls": 0,
            "cp01r1_attempted": False,
            "result_artifact_created": False,
            "physical_evidence_effect": "NONE",
        }, True)
        return EXIT_ADAPTER_FAILURE
    return EXIT_ADAPTER_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
