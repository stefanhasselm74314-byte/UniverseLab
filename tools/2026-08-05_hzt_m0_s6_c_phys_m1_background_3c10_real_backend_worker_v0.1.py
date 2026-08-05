#!/usr/bin/env python3
"""Isolated real-backend worker for Background-3C10 analytic controls.

The worker may import the frozen primary and independent backend modules only
inside an explicit a_F=0 control transaction. It never calls Newton, a shooting
Jacobian, a nonlinear root solver, or the CP01R1 target path.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import signal
import sys
import time
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PRIMARY_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py"
INDEPENDENT_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_independent_backend_v0.1.py"
CONTROL_RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3C10-AF0-CONTROL-R1"
FROZEN_RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
BOUNDARY_ORDER = (
    "R_A", "R_ell", "R_varphi", "R_patch",
    "R_4D", "R_chi", "R_scalar", "R_gauge",
)
CANDIDATE_FIELDS = (
    "varphi_N_0", "q_N", "A_S_0", "varphi_S_0",
    "q_S", "rho_N", "rho_S", "k4",
)


class ControlFailure(RuntimeError):
    pass


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


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ControlFailure(f"unable to import {path.relative_to(ROOT)}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def exact_boundary_vector() -> np.ndarray:
    y0 = (8.0 - 2.0 * math.sqrt(10.0)) / 3.0
    return np.asarray([
        0.0, 0.0, 0.0, 0.0,
        1.0 + 9.0 * y0 / 8.0,
        1.0 - 9.0 * y0 / 8.0,
        0.0,
        -3.0 * y0 / 2.0,
    ])


def validate_envelope(request: dict[str, Any]) -> dict[str, Any]:
    if request.get("control_run_id") != CONTROL_RUN_ID:
        raise ControlFailure("control run identity drift")
    if request.get("frozen_physical_run_id") != FROZEN_RUN_ID:
        raise ControlFailure("frozen physical run identity drift")
    if request.get("scope") != "REAL_BACKEND_ANALYTIC_AF0_CONTROL_ONLY":
        raise ControlFailure("worker scope violation")
    if request.get("control_a_F") != 0.0:
        raise ControlFailure("only the exact a_F=0 control is allowed")
    if request.get("cp01r1_execution") is not False:
        raise ControlFailure("CP01R1 execution flag must remain false")
    if request.get("target_root_solve") is not False:
        raise ControlFailure("target root solve flag must remain false")
    payload = request.get("payload")
    if not isinstance(payload, dict):
        raise ControlFailure("frozen payload object missing")
    if payload.get("run_id") != FROZEN_RUN_ID:
        raise ControlFailure("payload run identity drift")
    if payload.get("model_parameters_ordered", {}).get("a_F") != "1/4":
        raise ControlFailure("frozen target parameter drift")
    return payload


def primary_control(request: dict[str, Any]) -> dict[str, Any]:
    payload = validate_envelope(request)
    node_counts = request.get("node_counts")
    if node_counts != [24, 48, 96]:
        raise ControlFailure("primary control node schedule drift")
    module = load_module("background3c10_primary_real_backend", PRIMARY_PATH)
    if module.NEWTON_CALL_COUNT != 0:
        raise ControlFailure("primary Newton counter nonzero at import")
    model = module.model_from_payload(payload, control_a_F=True)
    sector = module.sector_from_payload(payload)
    if float(model.a_F) != 0.0:
        raise ControlFailure("primary control override failed")
    expected_boundary = exact_boundary_vector()
    records: list[dict[str, Any]] = []
    candidates: list[list[float]] = []
    for node_count in node_counts:
        state = module.control_seed_state(node_count)
        vector, metadata = module.residual(state, node_count, model, sector)
        _regions, parameters = module.unpack_state(state, node_count)
        candidate = [float(value) for value in parameters]
        candidates.append(candidate)
        bulk = np.asarray(vector[:-8], dtype=float)
        boundary = np.asarray(metadata["boundary"], dtype=float)
        constraint_inf = float(max(
            np.max(np.abs(metadata["north"].constraint)),
            np.max(np.abs(metadata["south"].constraint)),
        ))
        records.append({
            "node_count": int(node_count),
            "bulk_residual_inf": float(np.max(np.abs(bulk))),
            "constraint_inf": constraint_inf,
            "boundary": [float(value) for value in boundary],
            "boundary_exact_distance": float(np.max(np.abs(boundary - expected_boundary))),
            "candidate": dict(zip(CANDIDATE_FIELDS, candidate)),
            "candidate_sha256": sha256_value(dict(zip(CANDIDATE_FIELDS, candidate))),
        })
    reference = np.asarray(candidates[-1])
    cross_mesh_distance = float(max(
        np.max(np.abs(np.asarray(candidate) - reference)) for candidate in candidates
    ))
    if module.NEWTON_CALL_COUNT != 0:
        raise ControlFailure("primary Newton was called during analytic control")
    return {
        "status": "PASS_REAL_PRIMARY_AF0_CONTROL_NO_NEWTON",
        "stage": "primary_control",
        "real_backend_imported": True,
        "source_sha256": sha256_file(PRIMARY_PATH),
        "base_source_sha256": sha256_file(module.BASE_PATH),
        "model_a_F": float(model.a_F),
        "node_records": records,
        "candidate": records[-1]["candidate"],
        "candidate_sha256": records[-1]["candidate_sha256"],
        "candidate_cross_mesh_distance": cross_mesh_distance,
        "newton_call_count": int(module.NEWTON_CALL_COUNT),
        "cp01r1_attempts": 0,
        "target_root_solves": 0,
        "physical_evidence_effect": "NONE",
    }


def independent_control(request: dict[str, Any]) -> dict[str, Any]:
    payload = validate_envelope(request)
    cutoffs = request.get("cutoffs")
    if cutoffs != [0.001, 0.0005, 0.00025]:
        raise ControlFailure("independent cutoff schedule drift")
    handoff = request.get("handoff")
    if not isinstance(handoff, dict):
        raise ControlFailure("candidate handoff missing")
    candidate = handoff.get("candidate")
    if not isinstance(candidate, dict) or tuple(candidate.keys()) != CANDIDATE_FIELDS:
        raise ControlFailure("candidate field order drift")
    if handoff.get("candidate_sha256") != sha256_value(candidate):
        raise ControlFailure("candidate handoff digest mismatch")
    module = load_module("background3c10_independent_real_backend", INDEPENDENT_PATH)
    if module.SHOOTING_JACOBIAN_CALL_COUNT != 0:
        raise ControlFailure("shooting Jacobian counter nonzero at import")
    if module.INTEGRATION_CALL_COUNT != 0:
        raise ControlFailure("integration counter nonzero at import")
    model = module.model_from_payload(payload, control_a_F=True)
    sector = module.sector_from_payload(payload)
    shooting = np.asarray([candidate[field] for field in CANDIDATE_FIELDS], dtype=float)
    expected_boundary = exact_boundary_vector()
    records: list[dict[str, Any]] = []
    for epsilon in cutoffs:
        boundary, regional = module.shooting_residual(
            shooting, model, sector, epsilon=float(epsilon), sample_count=513,
        )
        profile_errors: dict[str, float] = {}
        for name, parameter_index in (("north", 1), ("south", 4)):
            solution = regional[name]
            exact = module.exact_control_profile(solution.x, shooting[parameter_index])
            profile_errors[name] = float(np.max(np.abs(solution.y - exact)))
        constraint_inf = float(max(
            np.max(np.abs(regional["north"].constraint)),
            np.max(np.abs(regional["south"].constraint)),
        ))
        boundary_array = np.asarray(boundary, dtype=float)
        records.append({
            "epsilon": float(epsilon),
            "boundary": [float(value) for value in boundary_array],
            "boundary_exact_distance": float(np.max(np.abs(boundary_array - expected_boundary))),
            "profile_error_inf": float(max(profile_errors.values())),
            "constraint_inf": constraint_inf,
            "profile_errors": profile_errors,
        })
    if module.SHOOTING_JACOBIAN_CALL_COUNT != 0:
        raise ControlFailure("shooting Jacobian was called during analytic control")
    return {
        "status": "PASS_REAL_INDEPENDENT_AF0_CONTROL_NO_ROOT",
        "stage": "independent_control",
        "real_backend_imported": True,
        "source_sha256": sha256_file(INDEPENDENT_PATH),
        "model_a_F": float(model.a_F),
        "cutoff_records": records,
        "integration_call_count": int(module.INTEGRATION_CALL_COUNT),
        "shooting_jacobian_call_count": int(module.SHOOTING_JACOBIAN_CALL_COUNT),
        "nonlinear_root_calls": 0,
        "cp01r1_attempts": 0,
        "target_root_solves": 0,
        "physical_evidence_effect": "NONE",
    }


def write_readiness(payload: dict[str, Any]) -> None:
    sys.stdout.buffer.write(canonical_bytes(payload))
    sys.stdout.buffer.flush()


def timeout_probe(request: dict[str, Any]) -> dict[str, Any]:
    validate_envelope(request)
    module = load_module("background3c10_primary_timeout_probe", PRIMARY_PATH)
    if module.NEWTON_CALL_COUNT != 0:
        raise ControlFailure("Newton counter nonzero in timeout probe")
    write_readiness({
        "status": "REAL_PRIMARY_IMPORTED_TIMEOUT_PROBE_READY",
        "source_sha256": sha256_file(PRIMARY_PATH),
        "newton_call_count": int(module.NEWTON_CALL_COUNT),
        "physical_evidence_effect": "NONE",
    })
    time.sleep(float(request.get("sleep_seconds", 30.0)))
    return {"status": "UNEXPECTED_TIMEOUT_PROBE_COMPLETION"}


def signal_probe(request: dict[str, Any]) -> dict[str, Any]:
    validate_envelope(request)
    module = load_module("background3c10_independent_signal_probe", INDEPENDENT_PATH)
    if module.SHOOTING_JACOBIAN_CALL_COUNT != 0:
        raise ControlFailure("Jacobian counter nonzero in signal probe")
    write_readiness({
        "status": "REAL_INDEPENDENT_IMPORTED_SIGNAL_PROBE_READY",
        "source_sha256": sha256_file(INDEPENDENT_PATH),
        "shooting_jacobian_call_count": int(module.SHOOTING_JACOBIAN_CALL_COUNT),
        "physical_evidence_effect": "NONE",
    })
    os.kill(os.getpid(), signal.SIGTERM)
    return {"status": "UNEXPECTED_SIGNAL_PROBE_COMPLETION"}


def main() -> int:
    try:
        request = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        if not isinstance(request, dict):
            raise ControlFailure("request root must be an object")
        stage = request.get("stage")
        if stage == "primary_control":
            result = primary_control(request)
        elif stage == "independent_control":
            result = independent_control(request)
        elif stage == "timeout_probe":
            result = timeout_probe(request)
        elif stage == "signal_probe":
            result = signal_probe(request)
        else:
            raise ControlFailure("unregistered worker stage")
    except Exception as exc:
        result = {
            "status": "CONTROL_FAILURE",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "physical_evidence_effect": "NONE",
        }
        sys.stdout.buffer.write(canonical_bytes(result))
        return 2
    sys.stdout.buffer.write(canonical_bytes(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
