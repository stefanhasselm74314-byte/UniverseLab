#!/usr/bin/env python3
"""Background-3C12 nonoperative grant and target-path control release.

This module never imports a physical backend and cannot execute CP01R1. It
implements only source binding, synthetic grant validation, atomic one-time
consumption, replay rejection, and backend-free target-transaction controls.
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import secrets
import signal
import subprocess
import sys
import tempfile
import threading
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
GRANT_CONTRACT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C12SingleUseGrantContract_v0.1.json"
TARGET_CONTRACT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C12TargetPathReleaseContract_v0.1.json"
REVIEW_3C11_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C11RealBackendControlAuthorizationReview_v0.1.json"
RUN_INPUT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"
SEED_SPEC_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BSeedSpecification_v0.1.json"
RESOURCE_POLICY_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
RESULT_SCHEMA_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResultSchema_v0.1.json"
DEPENDENCY_LOCK_PATH = ROOT / "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C_v0.1.txt"
PRIMARY_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py"
PRIMARY_BASE_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.1.py"
INDEPENDENT_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_independent_backend_v0.1.py"
WORKER_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c12_synthetic_target_worker_v0.1.py"
VALIDATOR_PATH = ROOT / "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c12_v0.1.py"
TEST_PATH = ROOT / "tests/2026-08-05_test_hzt_m0_s6_c_phys_m1_background_3c12_v0.1.py"
LEDGER_PATH = ROOT / "science/hzt-m0/md2s/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C12GrantTargetPathLedger_v0.1.md"
AUDIT_RESULT_PATH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C12GrantTargetPathAuditResult_v0.1.json"

TARGET_RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
TARGET_A_F = "1/4"
FROZEN_PAYLOAD_SHA256 = "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302"
SEED_SPEC_SHA256 = "b6e4319cc29736799a0b46320002e51cd17b70b724a6b4c6e86567a316996161"
SCHEDULE_SHA256 = "95001986dc93818f0fea3124cf9ddcd63eb136f8d206f6200a4e8c0cf6d54927"
PRIMARY_SHA256 = "8ce1c0eceed64245d091d4bed492f3cf2a9c8314f631a03045aaa9696fb11c92"
PRIMARY_BASE_SHA256 = "830d4b4fdd28c8888876125479df3542eeb3864d4328764feb96b5d34bd91599"
INDEPENDENT_SHA256 = "a8afd7b548366acf9f5ac72e91bcf07372913cc21a8790d86d0a989a89f03e7b"
DEPENDENCY_LOCK_SHA256 = "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f"
DENIAL_3C11 = "DENIED_OPERATIVE_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE_ABSENT"
GRANT_CLASSIFICATION = "SYNTHETIC_NONOPERATIVE_TEST_GRANT_NOT_AUTHORIZATION"
GRANT_ACTION = "SYNTHETIC_TARGET_PATH_TRANSACTION_CONTROL_ONLY"
WORKER_SCOPE = "SYNTHETIC_NONOPERATIVE_TARGET_PATH_TRANSACTION_ONLY"
EXIT_NOT_AUTHORIZED = 73
EXIT_CONTROL_FAILURE = 74
FORBIDDEN_REQUEST_FIELDS = {
    "control_a_F", "control_override", "analytic_control", "manufactured_control",
    "use_a_F_zero", "model_override",
}
FORBIDDEN_REQUEST_VALUES = {"a_F=0", "CONTROL_OVERRIDE", "ANALYTIC_AF0_CONTROL"}
TERMINAL_BY_OUTCOME = {
    "success": "CONSUMED_SYNTHETIC_SUCCESS",
    "failure": "CONSUMED_SYNTHETIC_FAILURE",
    "timeout": "CONSUMED_SYNTHETIC_TIMEOUT",
    "signal": "CONSUMED_SYNTHETIC_SIGNAL",
    "crash": "CONSUMED_SYNTHETIC_CRASH",
}

WORKER_LAUNCH_COUNT = 0
PHYSICAL_BACKEND_IMPORT_COUNT = 0
PHYSICAL_SOLVER_CALL_COUNT = 0
CP01R1_ATTEMPT_COUNT = 0
TARGET_SOLVE_COUNT = 0
OPERATIVE_GRANT_COUNT = 0
PHYSICAL_RESULT_COUNT = 0


class ReleaseFailure(RuntimeError):
    pass


class GrantRejected(ReleaseFailure):
    pass


class ReplayRejected(ReleaseFailure):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_value(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReleaseFailure(f"JSON object required: {path}")
    return value


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise GrantRejected("grant timestamp must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def checkout_commit_sha() -> str:
    try:
        value = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
            stderr=subprocess.DEVNULL, timeout=5,
        ).strip()
    except Exception as exc:
        raise ReleaseFailure(f"unable to attest checkout commit: {exc}") from exc
    if len(value) != 40 or any(char not in "0123456789abcdef" for char in value.lower()):
        raise ReleaseFailure("invalid checkout commit attestation")
    return value.lower()


def package_paths() -> tuple[Path, ...]:
    return (
        GRANT_CONTRACT_PATH, TARGET_CONTRACT_PATH, REVIEW_3C11_PATH,
        RUN_INPUT_PATH, SEED_SPEC_PATH, RESOURCE_POLICY_PATH, RESULT_SCHEMA_PATH,
        DEPENDENCY_LOCK_PATH, PRIMARY_PATH, PRIMARY_BASE_PATH, INDEPENDENT_PATH,
        WORKER_PATH, Path(__file__).resolve(), VALIDATOR_PATH, TEST_PATH, LEDGER_PATH,
    )


def package_manifest() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for path in package_paths():
        if not path.is_file():
            raise ReleaseFailure(f"closed package source missing: {path.relative_to(ROOT)}")
        records.append({"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path)})
    return records


def package_digest() -> str:
    return sha256_value(package_manifest())


def build_target_schedule() -> list[dict[str, int]]:
    records: list[dict[str, int]] = []
    ordinal = 0
    for seed_index in range(7):
        for node_count in (24, 32, 48, 64, 96):
            records.append({
                "ordinal": ordinal,
                "seed_index": seed_index,
                "node_count": node_count,
            })
            ordinal += 1
    return records


def expected_binding() -> dict[str, str]:
    return {
        "checkout_commit_sha": checkout_commit_sha(),
        "target_release_package_sha256": package_digest(),
        "frozen_run_payload_sha256": FROZEN_PAYLOAD_SHA256,
        "seed_spec_sha256": SEED_SPEC_SHA256,
        "schedule_sha256": SCHEDULE_SHA256,
        "primary_source_sha256": PRIMARY_SHA256,
        "primary_base_source_sha256": PRIMARY_BASE_SHA256,
        "independent_source_sha256": INDEPENDENT_SHA256,
        "dependency_lock_sha256": DEPENDENCY_LOCK_SHA256,
        "resource_policy_sha256": sha256_file(RESOURCE_POLICY_PATH),
        "result_schema_sha256": sha256_file(RESULT_SCHEMA_PATH),
    }


def grant_without_digest(grant: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in grant.items() if key != "grant_digest_sha256"}


def issue_synthetic_grant(
    binding: dict[str, str], *, now: datetime | None = None,
    not_before_offset_seconds: int = -1, lifetime_seconds: int = 600,
    operative: bool = False,
) -> dict[str, Any]:
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    not_before = current + timedelta(seconds=not_before_offset_seconds)
    expires = current + timedelta(seconds=lifetime_seconds)
    grant: dict[str, Any] = {
        "schema": "universelab.background-3c12-synthetic-grant-instance.v0.1",
        "grant_id": "SYNTHETIC-" + secrets.token_hex(16),
        "authorization_decision_id": "NONOPERATIVE-CONTROL-NO-AUTHORIZATION",
        "classification": GRANT_CLASSIFICATION,
        "operative": operative,
        "issued_at_utc": iso_utc(current),
        "not_before_utc": iso_utc(not_before),
        "expires_at_utc": iso_utc(expires),
        "nonce": secrets.token_hex(16),
        "target_run_id": TARGET_RUN_ID,
        "target_a_F": TARGET_A_F,
        "binding": dict(binding),
        "allowed_action": GRANT_ACTION,
        "forbidden_actions": [
            "PHYSICAL_BACKEND_IMPORT", "CP01R1_EXECUTION", "TARGET_ROOT_SOLVE",
            "OPERATIVE_GRANT_ISSUANCE", "PHYSICAL_RESULT_WRITE",
        ],
    }
    grant["grant_digest_sha256"] = sha256_value(grant_without_digest(grant))
    return grant


def validate_no_control_override(request: Any, path: str = "$") -> None:
    if isinstance(request, dict):
        for key, value in request.items():
            if key in FORBIDDEN_REQUEST_FIELDS:
                raise GrantRejected(f"control override field rejected at {path}.{key}")
            validate_no_control_override(value, f"{path}.{key}")
    elif isinstance(request, list):
        for index, value in enumerate(request):
            validate_no_control_override(value, f"{path}[{index}]")
    elif isinstance(request, str) and request in FORBIDDEN_REQUEST_VALUES:
        raise GrantRejected(f"control override value rejected at {path}")


def validate_grant(
    grant: dict[str, Any], binding: dict[str, str], *, now: datetime | None = None,
) -> None:
    contract = load_json(GRANT_CONTRACT_PATH)
    required = set(contract["grant_schema_fields"])
    if set(grant) != required:
        missing = sorted(required - set(grant))
        unknown = sorted(set(grant) - required)
        raise GrantRejected(f"grant field set drift missing={missing} unknown={unknown}")
    if grant.get("classification") != GRANT_CLASSIFICATION:
        raise GrantRejected("grant classification drift")
    if grant.get("operative") is not False:
        raise GrantRejected("operative grant rejected")
    if grant.get("target_run_id") != TARGET_RUN_ID or grant.get("target_a_F") != TARGET_A_F:
        raise GrantRejected("target identity drift")
    if grant.get("allowed_action") != GRANT_ACTION:
        raise GrantRejected("grant action drift")
    nonce = grant.get("nonce")
    if not isinstance(nonce, str) or len(nonce) < 32:
        raise GrantRejected("grant nonce too short")
    if grant.get("grant_digest_sha256") != sha256_value(grant_without_digest(grant)):
        raise GrantRejected("grant integrity digest mismatch")
    actual_binding = grant.get("binding")
    if actual_binding != binding:
        raise GrantRejected("grant binding mismatch")
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    issued = parse_utc(str(grant["issued_at_utc"]))
    not_before = parse_utc(str(grant["not_before_utc"]))
    expires = parse_utc(str(grant["expires_at_utc"]))
    if issued > not_before:
        raise GrantRejected("issued-at after not-before")
    if not_before >= expires:
        raise GrantRejected("invalid grant validity window")
    if (expires - issued).total_seconds() > 3600:
        raise GrantRejected("synthetic grant lifetime exceeds contract")
    if current < not_before:
        raise GrantRejected("grant not yet valid")
    if current >= expires:
        raise GrantRejected("grant expired")


@dataclass
class GrantStateStore:
    root: Path

    def __post_init__(self) -> None:
        resolved = self.root.resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            pass
        else:
            raise ReleaseFailure("grant state root must be external to repository")
        resolved.mkdir(parents=True, exist_ok=True)
        self.root = resolved

    def grant_dir(self, grant_id: str) -> Path:
        if not grant_id.startswith("SYNTHETIC-"):
            raise GrantRejected("synthetic grant ID required")
        return self.root / grant_id

    def state_path(self, grant_id: str) -> Path:
        return self.grant_dir(grant_id) / "state.json"

    def _write_atomic(self, path: Path, value: dict[str, Any]) -> None:
        temporary = path.with_name(path.name + ".tmp-" + secrets.token_hex(8))
        data = canonical_bytes(value)
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)

    def reserve(self, grant: dict[str, Any]) -> dict[str, Any]:
        directory = self.grant_dir(str(grant["grant_id"]))
        try:
            directory.mkdir(mode=0o700)
        except FileExistsError as exc:
            raise ReplayRejected("grant already reserved or consumed") from exc
        state = {
            "grant_id": grant["grant_id"],
            "grant_digest_sha256": grant["grant_digest_sha256"],
            "state": "RESERVED_SYNTHETIC",
            "terminal": False,
        }
        self._write_atomic(directory / "state.json", state)
        return state

    def read(self, grant_id: str) -> dict[str, Any]:
        return load_json(self.state_path(grant_id))

    def consume(self, grant_id: str, terminal_state: str, detail: dict[str, Any]) -> dict[str, Any]:
        if terminal_state not in TERMINAL_BY_OUTCOME.values():
            raise ReleaseFailure("unregistered terminal state")
        current = self.read(grant_id)
        if current.get("state") != "RESERVED_SYNTHETIC" or current.get("terminal") is not False:
            raise ReplayRejected("grant is not in reservable terminal-transition state")
        terminal = {
            "grant_id": grant_id,
            "grant_digest_sha256": current["grant_digest_sha256"],
            "state": terminal_state,
            "terminal": True,
            "detail": detail,
        }
        self._write_atomic(self.state_path(grant_id), terminal)
        return terminal


def worker_preexec() -> None:
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_FSIZE, (4 * 1024 * 1024, 4 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
    os.setsid()


def parse_worker_stdout(data: bytes) -> dict[str, Any] | None:
    if not data:
        return None
    try:
        value = json.loads(data.decode("utf-8"))
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def launch_worker(outcome: str, *, timeout_seconds: float = 3.0) -> dict[str, Any]:
    global WORKER_LAUNCH_COUNT
    WORKER_LAUNCH_COUNT += 1
    request = {
        "scope": WORKER_SCOPE,
        "outcome": outcome,
        "operative": False,
        "physical_backend_import": False,
        "cp01r1_execution": False,
        "target_solve": False,
        "sleep_seconds": 30.0,
    }
    process = subprocess.Popen(
        [sys.executable, str(WORKER_PATH)], cwd=ROOT,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        preexec_fn=worker_preexec,
    )
    try:
        stdout, stderr = process.communicate(canonical_bytes(request), timeout=timeout_seconds)
        return {
            "timed_out": False,
            "returncode": process.returncode,
            "stdout": parse_worker_stdout(stdout),
            "stderr": stderr.decode("utf-8", errors="replace"),
        }
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            stdout, stderr = process.communicate(timeout=1.0)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, stderr = process.communicate()
        return {
            "timed_out": True,
            "returncode": process.returncode,
            "stdout": parse_worker_stdout(stdout),
            "stderr": stderr.decode("utf-8", errors="replace"),
        }


def target_request(outcome: str) -> dict[str, Any]:
    return {
        "target_run_id": TARGET_RUN_ID,
        "target_a_F": TARGET_A_F,
        "schedule_sha256": SCHEDULE_SHA256,
        "synthetic_outcome": outcome,
        "physical_execution": False,
    }


def execute_synthetic_transaction(
    grant: dict[str, Any], request: dict[str, Any], store: GrantStateStore,
    binding: dict[str, str], *, now: datetime | None = None,
) -> dict[str, Any]:
    validate_no_control_override(request)
    if request.get("target_run_id") != TARGET_RUN_ID:
        raise GrantRejected("target request run identity drift")
    if request.get("target_a_F") != TARGET_A_F:
        raise GrantRejected("target request a_F drift")
    if request.get("schedule_sha256") != SCHEDULE_SHA256:
        raise GrantRejected("target request schedule drift")
    if request.get("physical_execution") is not False:
        raise GrantRejected("physical execution request forbidden")
    outcome = str(request.get("synthetic_outcome"))
    if outcome not in TERMINAL_BY_OUTCOME:
        raise GrantRejected("synthetic outcome not registered")
    validate_grant(grant, binding, now=now)
    store.reserve(grant)
    result = launch_worker(outcome)
    detail = {
        "outcome": outcome,
        "timed_out": result["timed_out"],
        "returncode": result["returncode"],
        "worker_status": result["stdout"].get("status") if isinstance(result["stdout"], dict) else None,
        "physical_backend_imported": False,
        "solver_calls": 0,
        "cp01r1_attempts": 0,
        "target_solves": 0,
        "physical_evidence_effect": "NONE",
    }
    terminal = store.consume(str(grant["grant_id"]), TERMINAL_BY_OUTCOME[outcome], detail)
    return {"worker": result, "terminal": terminal}


def result_schema_preview(binding: dict[str, str]) -> dict[str, Any]:
    schema = load_json(RESULT_SCHEMA_PATH)
    required = list(schema["required_top_level_fields"])
    preview = {field: None for field in required}
    preview.update({
        "schema": schema["schema"],
        "run_id": TARGET_RUN_ID,
        "run_payload_sha256": FROZEN_PAYLOAD_SHA256,
        "implementation_source_sha256": binding["target_release_package_sha256"],
        "dependency_lock_sha256": DEPENDENCY_LOCK_SHA256,
        "authorization_decision_id": "SYNTHETIC_NONOPERATIVE_NO_AUTHORIZATION",
        "final_classification": "NOT_EXECUTED_AUTHORIZATION_FAILURE",
        "physical_evidence_effect": "NONE",
        "forbidden_inferences": ["synthetic control is not physical execution"],
    })
    return {
        "required_fields": required,
        "mapped_fields": sorted(preview),
        "preview_sha256": sha256_value(preview),
        "result_schema_preview_is_physical_result": False,
        "result_artifact_created": False,
    }


def scan_source(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    calls: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modules.add(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
    return {"modules": sorted(modules), "calls": sorted(calls)}


def static_audit() -> dict[str, Any]:
    grant_contract = load_json(GRANT_CONTRACT_PATH)
    target_contract = load_json(TARGET_CONTRACT_PATH)
    review = load_json(REVIEW_3C11_PATH)
    run_input = load_json(RUN_INPUT_PATH)
    schedule = build_target_schedule()
    if grant_contract["operative"] is not False:
        raise ReleaseFailure("grant contract operative drift")
    if review["status"] != DENIAL_3C11 or review["authorization_decision"]["authorized"] is not False:
        raise ReleaseFailure("3C11 denial basis drift")
    if target_contract["target_identity"]["schedule_entry_count"] != len(schedule):
        raise ReleaseFailure("target schedule entry count drift")
    if run_input["frozen_run_payload"]["run_id"] != TARGET_RUN_ID:
        raise ReleaseFailure("frozen run identity drift")
    if run_input["frozen_run_payload"]["model_parameters_ordered"]["a_F"] != TARGET_A_F:
        raise ReleaseFailure("frozen target a_F drift")
    if sha256_file(PRIMARY_PATH) != PRIMARY_SHA256:
        raise ReleaseFailure("primary backend source drift")
    if sha256_file(PRIMARY_BASE_PATH) != PRIMARY_BASE_SHA256:
        raise ReleaseFailure("primary base source drift")
    if sha256_file(INDEPENDENT_PATH) != INDEPENDENT_SHA256:
        raise ReleaseFailure("independent backend source drift")
    if sha256_file(DEPENDENCY_LOCK_PATH) != DEPENDENCY_LOCK_SHA256:
        raise ReleaseFailure("dependency lock drift")
    release_scan = scan_source(Path(__file__).resolve())
    worker_scan = scan_source(WORKER_PATH)
    forbidden_modules = {"numpy", "scipy", "socket", "urllib", "http.client"}
    forbidden_calls = {
        "damped_newton", "shooting_residual", "centered_fd_jacobian",
        "least_squares", "solve_ivp", "root",
    }
    if forbidden_modules.intersection(release_scan["modules"] + worker_scan["modules"]):
        raise ReleaseFailure("forbidden module imported by 3C12 control package")
    if forbidden_calls.intersection(release_scan["calls"] + worker_scan["calls"]):
        raise ReleaseFailure("forbidden numerical call present in 3C12 control package")
    manifest = package_manifest()
    digest = sha256_value(manifest)
    binding = expected_binding()
    return {
        "status": "PASS_3C12_STATIC_AUDIT_NO_BACKEND_IMPORT_NO_EXECUTION",
        "package_manifest_sha256": digest,
        "source_count": len(manifest),
        "checkout_commit_sha": binding["checkout_commit_sha"],
        "target_run_id": TARGET_RUN_ID,
        "target_a_F": TARGET_A_F,
        "schedule_entry_count": len(schedule),
        "schedule_sha256": SCHEDULE_SHA256,
        "target_plan_sha256": sha256_value(schedule),
        "binding": binding,
        "release_modules": release_scan["modules"],
        "worker_modules": worker_scan["modules"],
        "physical_backend_imports": PHYSICAL_BACKEND_IMPORT_COUNT,
        "physical_solver_calls": PHYSICAL_SOLVER_CALL_COUNT,
        "cp01r1_attempts": CP01R1_ATTEMPT_COUNT,
        "target_solves": TARGET_SOLVE_COUNT,
        "operative_grants": OPERATIVE_GRANT_COUNT,
        "physical_results": PHYSICAL_RESULT_COUNT,
        "physical_evidence_effect": "NONE",
    }


def assert_replay_rejected(store: GrantStateStore, grant: dict[str, Any]) -> None:
    try:
        store.reserve(grant)
    except ReplayRejected:
        return
    raise ReleaseFailure("consumed grant replay was accepted")


def self_test() -> dict[str, Any]:
    audit = static_audit()
    binding = audit["binding"]
    now = datetime.now(timezone.utc)
    terminal_states: dict[str, str] = {}
    replay_rejections = 0
    invalid_rejections: list[str] = []
    with tempfile.TemporaryDirectory(prefix="universelab-bg3c12-") as temporary:
        root = Path(temporary)
        store = GrantStateStore(root / "states")
        for outcome in ("success", "failure", "timeout", "signal", "crash"):
            grant = issue_synthetic_grant(binding, now=now)
            result = execute_synthetic_transaction(
                grant, target_request(outcome), store, binding, now=now,
            )
            terminal_states[outcome] = result["terminal"]["state"]
            assert_replay_rejected(store, grant)
            replay_rejections += 1

        race_grant = issue_synthetic_grant(binding, now=now)
        race_results: list[str] = []
        race_lock = threading.Lock()
        def reserve_race() -> None:
            try:
                store.reserve(race_grant)
                value = "WIN"
            except ReplayRejected:
                value = "REPLAY_REJECTED"
            with race_lock:
                race_results.append(value)
        threads = [threading.Thread(target=reserve_race) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        if sorted(race_results) != ["REPLAY_REJECTED", "WIN"]:
            raise ReleaseFailure(f"parallel reservation race drift: {race_results}")
        store.consume(race_grant["grant_id"], "CONSUMED_SYNTHETIC_FAILURE", {"race_control": True})
        assert_replay_rejected(store, race_grant)
        replay_rejections += 1

        invalid_cases: list[tuple[str, dict[str, Any], dict[str, Any], datetime]] = []
        expired = issue_synthetic_grant(binding, now=now - timedelta(hours=2), lifetime_seconds=60)
        invalid_cases.append(("expired", expired, target_request("success"), now))
        future = issue_synthetic_grant(binding, now=now, not_before_offset_seconds=120, lifetime_seconds=300)
        invalid_cases.append(("not_before", future, target_request("success"), now))
        mismatch_binding = issue_synthetic_grant({**binding, "schedule_sha256": "0" * 64}, now=now)
        invalid_cases.append(("binding", mismatch_binding, target_request("success"), now))
        tampered = issue_synthetic_grant(binding, now=now)
        tampered["nonce"] = "f" * 32
        invalid_cases.append(("digest", tampered, target_request("success"), now))
        operative = issue_synthetic_grant(binding, now=now, operative=True)
        invalid_cases.append(("operative", operative, target_request("success"), now))
        override = issue_synthetic_grant(binding, now=now)
        override_request = target_request("success")
        override_request["control_override"] = {"a_F": 0}
        invalid_cases.append(("control_override", override, override_request, now))

        for name, grant, request, validation_time in invalid_cases:
            before = set(path.name for path in store.root.iterdir())
            try:
                execute_synthetic_transaction(
                    grant, request, store, binding, now=validation_time,
                )
            except GrantRejected:
                invalid_rejections.append(name)
            else:
                raise ReleaseFailure(f"invalid case accepted: {name}")
            after = set(path.name for path in store.root.iterdir())
            if after != before:
                raise ReleaseFailure(f"invalid case reserved state before rejection: {name}")

    if terminal_states != TERMINAL_BY_OUTCOME:
        raise ReleaseFailure(f"terminal state matrix drift: {terminal_states}")
    preview = result_schema_preview(binding)
    return {
        "status": "PASS_3C12_NONOPERATIVE_GRANT_AND_TARGET_PATH_CONTROLS",
        "package_manifest_sha256": audit["package_manifest_sha256"],
        "checkout_commit_sha": audit["checkout_commit_sha"],
        "target_run_id": TARGET_RUN_ID,
        "target_a_F": TARGET_A_F,
        "schedule_entry_count": audit["schedule_entry_count"],
        "schedule_sha256": SCHEDULE_SHA256,
        "target_plan_sha256": audit["target_plan_sha256"],
        "terminal_states": terminal_states,
        "worker_launch_count": WORKER_LAUNCH_COUNT,
        "replay_rejections": replay_rejections,
        "parallel_reservation_race": "PASS_EXACTLY_ONE_WINNER",
        "invalid_rejections": sorted(invalid_rejections),
        "grant_instances_persisted_in_repository": 0,
        "operative_grants_created": OPERATIVE_GRANT_COUNT,
        "physical_backend_imports": PHYSICAL_BACKEND_IMPORT_COUNT,
        "physical_solver_calls": PHYSICAL_SOLVER_CALL_COUNT,
        "cp01r1_attempts": CP01R1_ATTEMPT_COUNT,
        "target_solves": TARGET_SOLVE_COUNT,
        "physical_result_artifacts": PHYSICAL_RESULT_COUNT,
        "result_schema_translation": preview,
        "physical_evidence_effect": "NONE",
        "next_block": load_json(TARGET_CONTRACT_PATH)["next_block_if_pass"],
    }


def denied_physical_run() -> dict[str, Any]:
    return {
        "status": "NOT_AUTHORIZED",
        "reason": "Background-3C12 is nonoperative implementation and synthetic control only",
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


def emit(value: dict[str, Any], as_json: bool) -> None:
    print(json.dumps(value, indent=2, sort_keys=True) if as_json else value["status"])


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
        emit({
            "status": "CONTROL_RELEASE_FAILURE",
            "error": str(exc),
            "physical_backend_imports": PHYSICAL_BACKEND_IMPORT_COUNT,
            "physical_solver_calls": PHYSICAL_SOLVER_CALL_COUNT,
            "cp01r1_attempts": CP01R1_ATTEMPT_COUNT,
            "target_solves": TARGET_SOLVE_COUNT,
            "operative_grants": OPERATIVE_GRANT_COUNT,
            "physical_results": PHYSICAL_RESULT_COUNT,
            "physical_evidence_effect": "NONE",
        }, args.json)
        return EXIT_CONTROL_FAILURE
    return EXIT_CONTROL_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
