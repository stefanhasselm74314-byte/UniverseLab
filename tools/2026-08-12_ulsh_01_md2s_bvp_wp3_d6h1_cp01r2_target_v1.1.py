#!/usr/bin/env python3
"""ULSH-01 / WP3-D6H1 CP01R2 hardened physical target v1.1.

Append-only hardening of the frozen CP01R2 v1.0 target. This version changes no
physical equation, model parameter, topology, seed, mesh, acceptance threshold,
or ETRN-01 solve rule. It closes only the D6 result-loss/finalization defects:

D6-B01: legacy CP01R1 finalization is normalized for the CP01R2-valid state
         "N=96 terminal progress state exists but no local root exists".
D6-B02: every schedule record is atomically fsync'ed as a strict-JSON,
         SHA-256 chained write-ahead checkpoint before advancing to the next
         schedule entry.

Audit is the default path and imports no numerical backend. Physical execution
requires the exact transaction capability plus an explicit checkpoint root.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import pickle
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3h1_cp01r2_target_v1.0.py"
CHECKPOINT_SCHEMA_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2CheckpointSchema_v1.0.json"
EXPECTED_BASE_BLOB = "199815ac9e4014cc0d68fde71d634cdac24516ce"
EXPECTED_CHECKPOINT_SCHEMA_BLOB = "339f579c8b3d9f1ffffca04e79a5acf817a3c2eb"

_SPEC = importlib.util.spec_from_file_location("ulsh_cp01r2_target_v10", BASE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("cannot load frozen CP01R2 target v1.0")
BASE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = BASE
_SPEC.loader.exec_module(BASE)

RUN_ID = BASE.RUN_ID
RUN_PAYLOAD_SHA256 = BASE.RUN_PAYLOAD_SHA256
SCHEDULE_SHA256 = BASE.SCHEDULE_SHA256
DEPENDENCY_LOCK_SHA256 = BASE.DEPENDENCY_LOCK_SHA256
NODE_COUNTS = BASE.NODE_COUNTS
SEED_ORDER = BASE.SEED_ORDER
PLANNED_ENTRY_COUNT = BASE.PLANNED_ENTRY_COUNT
BOUNDARY_ORDER = BASE.BOUNDARY_ORDER
FORBIDDEN_INFERENCES = BASE.FORBIDDEN_INFERENCES
TargetContractError = BASE.TargetContractError
TargetExecutionDenied = BASE.TargetExecutionDenied
TargetExecutionCapability = BASE.TargetExecutionCapability

CHECKPOINT_DOCUMENT_SCHEMA = "universelab.ulsh-01.md2s-bvp.cp01r2-entry-checkpoint.v1"
CHECKPOINT_STATE_SCHEMA = "universelab.ulsh-01.md2s-bvp.cp01r2-checkpoint-state.v1"


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _strict_json_projection(value: Any, path: str = "$") -> tuple[Any, list[dict[str, str]]]:
    replacements: list[dict[str, str]] = []
    if isinstance(value, float) and not math.isfinite(value):
        kind = "positive_infinity" if value > 0 else "negative_infinity" if value < 0 else "nan"
        return None, [{
            "path": path,
            "original_nonfinite_kind": kind,
            "replacement": "null",
            "reason": "JSON_SAFE_CHECKPOINT_DIAGNOSTIC_NOT_A_FINITE_MEASUREMENT",
        }]
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            projected, found = _strict_json_projection(item, f"{path}.{key}")
            out[str(key)] = projected
            replacements.extend(found)
        return out, replacements
    if isinstance(value, (list, tuple)):
        out_list: list[Any] = []
        for index, item in enumerate(value):
            projected, found = _strict_json_projection(item, f"{path}[{index}]")
            out_list.append(projected)
            replacements.extend(found)
        return out_list, replacements
    return value, replacements


def _atomic_create_bytes(path: Path, data: bytes) -> None:
    """Create one immutable checkpoint path, fsync it, then fsync the directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise TargetContractError(f"checkpoint overwrite/replay forbidden: {path}")
    temp = path.with_name(path.name + ".tmp")
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        offset = 0
        while offset < len(data):
            offset += os.write(fd, data[offset:])
        os.fsync(fd)
    finally:
        os.close(fd)
    if path.exists():
        temp.unlink(missing_ok=True)
        raise TargetContractError(f"checkpoint target appeared during atomic create: {path}")
    os.replace(temp, path)
    _fsync_directory(path.parent)


def _atomic_replace_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = BASE.canonical_json_bytes(value)
    temp = path.with_name(path.name + ".tmp")
    with temp.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)
    _fsync_directory(path.parent)


def _checkpoint_filename(ordinal: int, entry_id: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in entry_id)
    return f"entry-{ordinal:03d}-{safe}.json"


def checkpoint_entry(
    checkpoint_root: Path,
    record: dict[str, Any],
    previous_checkpoint_sha256: str | None,
    terminal_state: Any | None = None,
) -> str:
    """Durably write one schedule record before the target advances.

    The checkpoint contains the complete matrix record plus, for completed
    numerical stages, the terminal state vector needed to reconstruct the
    numerical terminal point if later finalization fails.
    """
    ordinal = int(record["ordinal"])
    entry_id = str(record["entry_id"])
    payload_record = dict(record)
    if terminal_state is not None:
        try:
            payload_record["write_ahead_terminal_state"] = terminal_state.tolist()
        except AttributeError:
            payload_record["write_ahead_terminal_state"] = list(terminal_state)
    projected_record, replacements = _strict_json_projection(payload_record, "$.record")
    document = {
        "schema": CHECKPOINT_DOCUMENT_SCHEMA,
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "schedule_sha256": SCHEDULE_SHA256,
        "ordinal": ordinal,
        "entry_id": entry_id,
        "seed_index": int(record["seed_index"]),
        "node_count": int(record["node_count"]),
        "previous_checkpoint_sha256": previous_checkpoint_sha256,
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "record": projected_record,
        "json_safe_nonfinite_replacements": replacements,
    }
    data = BASE.canonical_json_bytes(document)
    path = checkpoint_root / _checkpoint_filename(ordinal, entry_id)
    _atomic_create_bytes(path, data)
    digest = hashlib.sha256(data).hexdigest()
    _atomic_replace_json(checkpoint_root / "state.json", {
        "schema": CHECKPOINT_STATE_SCHEMA,
        "run_id": RUN_ID,
        "schedule_sha256": SCHEDULE_SHA256,
        "durable_checkpoint_count": ordinal,
        "last_entry_id": entry_id,
        "last_checkpoint_sha256": digest,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "replay_permitted": False,
    })
    return digest


def recover_checkpoint_prefix(checkpoint_root: Path) -> dict[str, Any]:
    """Verify the durable contiguous prefix and its SHA-256 chain."""
    if not checkpoint_root.is_dir():
        return {"count": 0, "chain_head_sha256": None, "records": []}
    files = sorted(checkpoint_root.glob("entry-*.json"))
    expected_ordinal = 1
    previous: str | None = None
    recovered: list[dict[str, Any]] = []
    for path in files:
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        document = json.loads(raw.decode("utf-8"))
        if int(document.get("ordinal", -1)) != expected_ordinal:
            raise TargetContractError(f"checkpoint ordinal gap/duplicate at {path.name}")
        if document.get("previous_checkpoint_sha256") != previous:
            raise TargetContractError(f"checkpoint chain mismatch at {path.name}")
        if document.get("schema") != CHECKPOINT_DOCUMENT_SCHEMA:
            raise TargetContractError(f"checkpoint schema mismatch at {path.name}")
        if document.get("run_id") != RUN_ID or document.get("schedule_sha256") != SCHEDULE_SHA256:
            raise TargetContractError(f"checkpoint run/schedule mismatch at {path.name}")
        recovered.append(document)
        previous = digest
        expected_ordinal += 1
    state_path = checkpoint_root / "state.json"
    if recovered and state_path.is_file():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if int(state.get("durable_checkpoint_count", -1)) != len(recovered):
            raise TargetContractError("checkpoint state pointer count mismatch")
        if state.get("last_checkpoint_sha256") != previous:
            raise TargetContractError("checkpoint state pointer chain-head mismatch")
    return {"count": len(recovered), "chain_head_sha256": previous, "records": recovered}


def _n96_record_by_seed(entries: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for record in entries:
        if int(record.get("node_count", -1)) == 96:
            out[int(record["seed_index"])] = record
    return out


def cp01r2_terminal_state_classification(
    record: dict[str, Any] | None,
    has_terminal_state: bool,
    legacy_acceptance_classification: str | None = None,
) -> str:
    """Total classification for all CP01R2 N=96 state/root combinations."""
    if record is not None and record.get("status") == "TIMED_OUT_NO_RETRY":
        return "N96_TIMEOUT_NO_RETRY"
    if record is not None and record.get("status") == "SKIPPED_AFTER_TIMEOUT_NO_RETRY":
        return "N96_SKIPPED_AFTER_TIMEOUT_NO_RETRY"
    if not has_terminal_state:
        return "NO_N96_TERMINAL_STATE"
    has_root = bool((record or {}).get("primary", {}).get("candidate_under_local_residual_gate"))
    if not has_root:
        return "N96_TERMINAL_STATE_NO_LOCAL_ROOT"
    if legacy_acceptance_classification == "NUMERICAL_CANDIDATE_BACKGROUND_DIAGNOSTIC":
        return "N96_LOCAL_ROOT_ACCEPTED_DIAGNOSTIC_CANDIDATE"
    if legacy_acceptance_classification is not None:
        return "N96_LOCAL_ROOT_REJECTED_BY_QA"
    return "N96_LOCAL_ROOT_PRESENT_PENDING_QA"


def prepare_legacy_finalize_views(
    entries: list[dict[str, Any]],
    internal_states: dict[tuple[int, int], Any],
    internal_details: dict[tuple[int, int], dict[str, Any]],
) -> tuple[dict[tuple[int, int], Any], dict[tuple[int, int], dict[str, Any]], dict[int, str]]:
    """Make CP01R2 non-root progress states safe for the inherited finalizer.

    Legacy CP01R1 `_finalize` assumes N=96 state presence implies a local root.
    CP01R2 intentionally stores progress-continuation terminal states even when
    they are not roots. For only that non-root case, copies passed into the
    legacy finalizer omit the N=96 state/detail. The durable checkpoint retains
    the actual terminal state and matrix record. Root states are never removed.
    """
    states = dict(internal_states)
    details = dict(internal_details)
    n96_records = _n96_record_by_seed(entries)
    terminal: dict[int, str] = {}
    for seed_index in SEED_ORDER:
        key = (int(seed_index), 96)
        record = n96_records.get(int(seed_index))
        has_state = key in internal_states
        terminal[int(seed_index)] = cp01r2_terminal_state_classification(record, has_state)
        has_root = bool((record or {}).get("primary", {}).get("candidate_under_local_residual_gate"))
        if has_state and not has_root:
            states.pop(key, None)
            details.pop(key, None)
    return states, details, terminal


def finalize_cp01r2_safe(
    entries: list[dict[str, Any]],
    internal_states: dict[tuple[int, int], Any],
    internal_details: dict[tuple[int, int], dict[str, Any]],
    independent_records: dict[tuple[int, int], dict[str, Any]],
    primary: Any,
    model: Any,
    sector: Any,
    thresholds: dict[str, Any],
    legacy: Any,
) -> dict[str, Any]:
    safe_states, safe_details, terminal = prepare_legacy_finalize_views(entries, internal_states, internal_details)
    finalized = legacy._finalize(entries, safe_states, safe_details, independent_records, primary, model, sector, thresholds)
    finalized = BASE._replace_cp01r1_tokens(finalized)
    rows = finalized.get("per_seed_acceptance", [])
    for row in rows:
        seed_index = int(row["seed_index"])
        base_classification = row.get("classification")
        record = _n96_record_by_seed(entries).get(seed_index)
        has_state = (seed_index, 96) in internal_states
        row["cp01r2_terminal_state_classification"] = cp01r2_terminal_state_classification(
            record, has_state, str(base_classification) if base_classification is not None else None
        )
        row["n96_terminal_state_present_in_execution_memory"] = has_state
        row["n96_nonroot_state_excluded_from_legacy_candidate_finalizer"] = bool(
            has_state and not bool((record or {}).get("primary", {}).get("candidate_under_local_residual_gate"))
        )
    finalized.setdefault("primary_backend", {})["cp01r2_terminal_state_classification"] = [
        {"seed_index": seed, "classification": terminal[seed]} for seed in sorted(terminal)
    ]
    return finalized


def audit_target() -> dict[str, Any]:
    if git_blob_sha1(BASE_PATH) != EXPECTED_BASE_BLOB:
        raise TargetContractError("frozen CP01R2 v1.0 target blob drift")
    if git_blob_sha1(CHECKPOINT_SCHEMA_PATH) != EXPECTED_CHECKPOINT_SCHEMA_BLOB:
        raise TargetContractError("D6H1 checkpoint schema blob drift")
    base = BASE.audit_target()
    schema = BASE.load_json(CHECKPOINT_SCHEMA_PATH)
    if schema.get("checkpoint_document_schema") != CHECKPOINT_DOCUMENT_SCHEMA:
        raise TargetContractError("checkpoint document schema drift")
    if schema.get("ordering", {}).get("advance_to_next_entry_requires_durable_checkpoint") is not True:
        raise TargetContractError("write-ahead ordering contract drift")
    return {
        **base,
        "status": "PASS_WP3_D6H1_CP01R2_TARGET_HARDENING_NO_EXECUTION",
        "D6-B01": "IMPLEMENTED_PENDING_INDEPENDENT_REVIEW",
        "D6-B02": "IMPLEMENTED_PENDING_INDEPENDENT_REVIEW",
        "legacy_finalizer_nonroot_n96_normalization": True,
        "durable_per_entry_checkpoint_before_schedule_advance": True,
        "checkpoint_hash_chain": "SHA-256",
        "checkpoint_terminal_state_capture": True,
        "solver_imported": False,
        "solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
    }


def execute_physical_schedule(
    capability: TargetExecutionCapability,
    checkpoint_root: Path,
) -> dict[str, Any]:
    BASE._validate_capability(capability)
    BASE._verify_sources()
    if git_blob_sha1(CHECKPOINT_SCHEMA_PATH) != EXPECTED_CHECKPOINT_SCHEMA_BLOB:
        raise TargetContractError("checkpoint schema drift before execution")
    if checkpoint_root.exists() and any(checkpoint_root.iterdir()):
        raise TargetContractError("checkpoint root must be absent or empty before a new single-use execution")
    checkpoint_root.mkdir(parents=True, exist_ok=True)
    _fsync_directory(checkpoint_root.parent)
    BASE._enforce_memory_limit(capability.maximum_memory_bytes)
    payload = BASE.frozen_payload()

    etrn = BASE.dynamic_import(BASE.D2_ETRN, "ulsh_cp01r2_etrn_d6h1")
    primary = BASE.dynamic_import(BASE.SEED_ADAPTER, "ulsh_cp01r2_primary_d6h1")
    independent = BASE.dynamic_import(BASE.INDEPENDENT, "ulsh_cp01r2_independent_d6h1")
    legacy = BASE.dynamic_import(BASE.LEGACY_QA, "ulsh_cp01r2_legacy_qa_d6h1")
    precision = BASE.dynamic_import(BASE.PRECISION_QA, "ulsh_cp01r2_precision_qa_d6h1")
    import numpy as np
    from scipy.optimize import least_squares

    model = primary.model_from_payload(payload, control_a_F=False)
    sector = primary.sector_from_payload(payload)
    independent_model = independent.model_from_payload(payload, control_a_F=False)
    independent_sector = independent.sector_from_payload(payload)
    if float(model.a_F) != 0.25 or float(independent_model.a_F) != 0.25:
        raise TargetContractError("physical model a_F drift")

    prereg = BASE.load_json(BASE.PREREG)
    thresholds = prereg["acceptance_thresholds"]
    limits = BASE.load_json(BASE.RESOURCE)["resource_limits"]
    entries: list[dict[str, Any]] = []
    internal_states: dict[tuple[int, int], Any] = {}
    internal_details: dict[tuple[int, int], dict[str, Any]] = {}
    independent_records: dict[tuple[int, int], dict[str, Any]] = {}
    previous_terminal: dict[int, dict[str, Any]] = {}
    blocked_seed: dict[int, str] = {}
    previous_checkpoint_sha256: str | None = None
    execution_started_utc = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()

    def commit_record(record: dict[str, Any], terminal_state: Any | None = None) -> None:
        nonlocal previous_checkpoint_sha256
        entries.append(record)
        previous_checkpoint_sha256 = checkpoint_entry(
            checkpoint_root, record, previous_checkpoint_sha256, terminal_state=terminal_state
        )
        recovered = recover_checkpoint_prefix(checkpoint_root)
        if int(recovered["count"]) != len(entries):
            raise TargetContractError("checkpoint prefix is not durable before schedule advance")

    for entry in BASE.build_schedule():
        seed_index = int(entry["seed_index"])
        node_count = int(entry["node_count"])
        if seed_index in blocked_seed:
            commit_record({
                **entry,
                "status": "SKIPPED_AFTER_TIMEOUT_NO_RETRY",
                "failure": blocked_seed[seed_index],
                "newton_history": [],
                "initialization_source": "SKIPPED",
                "continuation_source_entry_id": None,
                "stage_initial_residual_inf": None,
                "stage_final_residual_inf": None,
                "continuation_admissible": False,
                "eligible_for_next_mesh": False,
            })
            continue

        prior = previous_terminal.get(seed_index)
        if prior and prior.get("eligible_for_next_mesh") is True:
            initial = BASE._prolongate_state(primary, prior["state"], int(prior["node_count"]), node_count)
            initialization_source = "PROGRESS_CONTINUATION_FROM_IMMEDIATELY_PRECEDING_MESH_TERMINAL_STATE"
            continuation_source = str(prior["entry_id"])
        else:
            initial = primary.seven_seeds(node_count)[seed_index]
            initialization_source = "FRESH_FROZEN_CP01R1_SEED_SAME_INDEX"
            continuation_source = None

        initial_residual, _ = primary.residual(initial, node_count, model, sector)
        initial_inf = float(np.max(np.abs(np.asarray(initial_residual, dtype=float))))
        stage_started = time.monotonic()
        try:
            with legacy.stage_wall_clock_limit(
                float(limits["maximum_wall_clock_seconds_per_seed_per_level"]), entry["entry_id"]
            ):
                result = etrn.etrn_solve_generic(
                    initial,
                    lambda state: primary.residual(state, node_count, model, sector)[0],
                    lambda state: primary.complex_step_jacobian(state, node_count, model, sector),
                    lambda state: primary.admissible(state, node_count),
                    residual_tolerance=float(thresholds["bulk_residual_max"]),
                    maximum_iterations=120,
                )
                state = np.asarray(result["state"], dtype=float)
                full_residual, detail = primary.residual(state, node_count, model, sector)
                final_inf = float(np.max(np.abs(np.asarray(full_residual, dtype=float))))
                bulk_vector = np.concatenate([*detail["north"].residual_blocks, *detail["south"].residual_blocks])
                bulk_inf = float(np.max(np.abs(bulk_vector)))
                boundary = np.asarray(detail["boundary"], dtype=float)
                boundary_inf = float(np.max(np.abs(boundary)))
                constraint_profile = {
                    "north": np.asarray(detail["north"].constraint, dtype=float).tolist(),
                    "south": np.asarray(detail["south"].constraint, dtype=float).tolist(),
                }
                constraint_inf = float(max(
                    np.max(np.abs(detail["north"].constraint)),
                    np.max(np.abs(detail["south"].constraint)),
                ))
                local_candidate = bool(
                    result.get("converged")
                    and bulk_inf <= float(thresholds["bulk_residual_max"])
                    and boundary_inf <= float(thresholds["boundary_residual_max"])
                )
                diagnostic = legacy._diagnostic_jacobian(primary, state, node_count, model, sector)
                legacy_admissibility = legacy._admissibility(
                    primary, state, node_count, detail, model, sector, thresholds
                )
                continuation_admissible = bool(primary.admissible(state, node_count))
                eligible = etrn.progress_continuation_eligible(
                    initial=initial_inf,
                    final=final_inf,
                    finite=bool(np.all(np.isfinite(state))),
                    admissible=continuation_admissible,
                    timed_out=False,
                )
                previous_terminal[seed_index] = {
                    "entry_id": entry["entry_id"],
                    "node_count": node_count,
                    "state": state.copy(),
                    "eligible_for_next_mesh": eligible,
                }
                internal_states[(seed_index, node_count)] = state.copy()
                internal_details[(seed_index, node_count)] = detail

                independent_record: dict[str, Any] | None = None
                if local_candidate:
                    _regions, shooting_initial = primary.unpack_state(state, node_count)
                    shooting_initial = np.asarray(shooting_initial, dtype=float)
                    sample_count = max(257, 4 * node_count + 1)

                    def independent_residual(vector):
                        values, _ = independent.shooting_residual(
                            vector,
                            independent_model,
                            independent_sector,
                            epsilon=1.0e-6,
                            sample_count=sample_count,
                        )
                        return values

                    independent_result = least_squares(
                        independent_residual,
                        shooting_initial,
                        jac=lambda x: independent.centered_fd_jacobian(
                            independent_residual, x, relative_step=1.0e-6
                        ),
                        method="trf",
                        max_nfev=120,
                        ftol=float(thresholds["bulk_residual_max"]),
                        xtol=float(thresholds["bulk_residual_max"]),
                        gtol=float(thresholds["bulk_residual_max"]),
                    )
                    final_boundary, independent_detail = independent.shooting_residual(
                        independent_result.x,
                        independent_model,
                        independent_sector,
                        epsilon=1.0e-6,
                        sample_count=sample_count,
                    )
                    independent_constraint = float(max(
                        np.max(np.abs(independent_detail["north"].constraint)),
                        np.max(np.abs(independent_detail["south"].constraint)),
                    ))
                    candidate_distance = legacy._independent_profile_distance(
                        detail, shooting_initial, independent_detail, independent_result.x
                    )
                    independent_inf = float(np.max(np.abs(final_boundary)))
                    agreement = (
                        "AGREES_WITHIN_PREREGISTERED_DISTANCE"
                        if bool(independent_result.success)
                        and independent_inf <= float(thresholds["boundary_residual_max"])
                        and candidate_distance <= float(thresholds["independent_backend_candidate_distance_max"])
                        else "DISAGREES_OR_NOT_CONVERGED"
                    )
                    independent_record = {
                        "entry_id": entry["entry_id"],
                        "converged": bool(independent_result.success),
                        "points_per_region": sample_count,
                        "all_eight_boundary_residuals": {
                            name: float(value) for name, value in zip(BOUNDARY_ORDER, final_boundary)
                        },
                        "boundary_residual_max": independent_inf,
                        "constraint_max": independent_constraint,
                        "candidate_distance_to_primary": candidate_distance,
                        "agreement_classification": agreement,
                        "nfev": int(independent_result.nfev),
                    }
                    independent_records[(seed_index, node_count)] = independent_record

                record = {
                    **entry,
                    "seed_id": f"M1-BG3B-CP01-SEEDS-01:S{seed_index}",
                    "status": "COMPLETED",
                    "initialization_source": initialization_source,
                    "continuation_source_entry_id": continuation_source,
                    "stage_initial_residual_inf": initial_inf,
                    "stage_final_residual_inf": final_inf,
                    "continuation_admissible": continuation_admissible,
                    "eligible_for_next_mesh": eligible,
                    "primary": {
                        "converged": bool(result.get("converged")),
                        "candidate_under_local_residual_gate": local_candidate,
                        "failure": result.get("failure"),
                    },
                    "failure": result.get("failure"),
                    "bulk_residual_max": bulk_inf,
                    "boundary_residual_max": boundary_inf,
                    "all_eight_boundary_residuals": {
                        name: float(value) for name, value in zip(BOUNDARY_ORDER, boundary)
                    },
                    "rr_constraint_profile": constraint_profile,
                    "constraint_max": constraint_inf,
                    "diagnostic": legacy._to_builtin(diagnostic),
                    "newton_history": legacy._to_builtin(result.get("history", [])),
                    "independent": independent_record,
                    "legacy_full_qa_admissibility": legacy._to_builtin(legacy_admissibility),
                    "elapsed_wall_clock_seconds": time.monotonic() - stage_started,
                }
                commit_record(record, terminal_state=state)
        except legacy.StageTimeoutError as exc:
            blocked_seed[seed_index] = "STAGE_TIMEOUT_NO_RETRY"
            previous_terminal.pop(seed_index, None)
            commit_record({
                **entry,
                "seed_id": f"M1-BG3B-CP01-SEEDS-01:S{seed_index}",
                "status": "TIMED_OUT_NO_RETRY",
                "failure": "STAGE_TIMEOUT_NO_RETRY",
                "timeout_message": str(exc),
                "newton_history": [],
                "initialization_source": initialization_source,
                "continuation_source_entry_id": continuation_source,
                "stage_initial_residual_inf": initial_inf,
                "stage_final_residual_inf": None,
                "continuation_admissible": False,
                "eligible_for_next_mesh": False,
                "elapsed_wall_clock_seconds": time.monotonic() - stage_started,
            })

    recovered = recover_checkpoint_prefix(checkpoint_root)
    if int(recovered["count"]) != PLANNED_ENTRY_COUNT:
        raise TargetContractError(
            f"full schedule completed in memory but durable checkpoint count is {recovered['count']} != {PLANNED_ENTRY_COUNT}"
        )

    finalized = finalize_cp01r2_safe(
        entries,
        internal_states,
        internal_details,
        independent_records,
        primary,
        model,
        sector,
        thresholds,
        legacy,
    )
    finalized["primary_backend"].update(BASE._etrn_provenance(entries))
    raw = {
        "schema": "universelab.ulsh-01.md2s-bvp.cp01r2-result.v1",
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "schedule_sha256": SCHEDULE_SHA256,
        "implementation_source_sha256": BASE.sha256_file(Path(__file__)),
        "dependency_lock_sha256": DEPENDENCY_LOCK_SHA256,
        "execution_started_utc": execution_started_utc,
        "execution_finished_utc": datetime.now(timezone.utc).isoformat(),
        "planned_schedule_entries": PLANNED_ENTRY_COUNT,
        "matrix_entries": entries,
        "stage_timeout_count": sum(record.get("status") == "TIMED_OUT_NO_RETRY" for record in entries),
        "execution_elapsed_wall_clock_seconds": time.monotonic() - start,
        "write_ahead_checkpoint_audit": {
            "durable_checkpoint_count": recovered["count"],
            "chain_head_sha256": recovered["chain_head_sha256"],
            "full_schedule_prefix_durable_before_finalization": True,
            "terminal_state_included_for_completed_entries": True,
        },
        **finalized,
        "forbidden_inferences": FORBIDDEN_INFERENCES,
        "physical_evidence_effect": "NONE",
    }
    raw = precision._apply_precision_gate(raw)
    raw["primary_backend"].update(BASE._etrn_provenance(entries))
    return raw


def _capability_from_json(path: Path) -> TargetExecutionCapability:
    data = BASE.load_json(path)
    return TargetExecutionCapability(**data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-capability")
    parser.add_argument("--result-pickle")
    parser.add_argument("--checkpoint-root")
    args = parser.parse_args()
    physical = any((args.execute_capability, args.result_pickle, args.checkpoint_root))
    if physical:
        if not args.execute_capability or not args.result_pickle or not args.checkpoint_root:
            raise TargetExecutionDenied(
                "--execute-capability, --result-pickle and --checkpoint-root are all required"
            )
        result = execute_physical_schedule(
            _capability_from_json(Path(args.execute_capability)),
            Path(args.checkpoint_root),
        )
        with Path(args.result_pickle).open("wb") as stream:
            pickle.dump(result, stream, protocol=5)
            stream.flush()
            os.fsync(stream.fileno())
        return 0
    print(json.dumps(audit_target(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
