#!/usr/bin/env python3
"""Physics-free manufactured worker for Background-3C8 adapter controls.

The worker never imports NumPy, SciPy, or either physical numerical backend.
It only validates serialized adapter envelopes and emits deterministic control
payloads for primary-schedule and independent-handoff transactions.
"""
from __future__ import annotations

import hashlib
import json
import os
import signal
import sys
import time
from typing import Any


RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
RUN_PAYLOAD_SHA256 = "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302"
SEED_SET_ID = "M1-BG3B-CP01-SEEDS-01"
SEED_SPEC_SHA256 = "b6e4319cc29736799a0b46320002e51cd17b70b724a6b4c6e86567a316996161"
CONTROL_SCOPE = "MANUFACTURED_ADAPTER_CONTROL_ONLY"


class WorkerError(RuntimeError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def validate_common(payload: dict[str, Any]) -> None:
    binding = payload.get("binding", {})
    capability = payload.get("capability", {})
    if binding.get("run_id") != RUN_ID:
        raise WorkerError("run ID binding mismatch")
    if binding.get("run_payload_sha256") != RUN_PAYLOAD_SHA256:
        raise WorkerError("run payload binding mismatch")
    if binding.get("seed_set_id") != SEED_SET_ID:
        raise WorkerError("seed set binding mismatch")
    if binding.get("seed_spec_sha256") != SEED_SPEC_SHA256:
        raise WorkerError("seed specification binding mismatch")
    if capability.get("scope") != CONTROL_SCOPE:
        raise WorkerError("worker capability is not control-only")
    if capability.get("physical_authorized") is not False:
        raise WorkerError("physical authorization is forbidden")
    if capability.get("run_id") != RUN_ID:
        raise WorkerError("capability run ID mismatch")
    if capability.get("run_payload_sha256") != RUN_PAYLOAD_SHA256:
        raise WorkerError("capability payload mismatch")
    token_payload = capability.get("token_payload")
    if not isinstance(token_payload, dict):
        raise WorkerError("missing capability token payload")
    if capability.get("token_sha256") != sha256_value(token_payload):
        raise WorkerError("capability token digest mismatch")


def validate_schedule(schedule: Any) -> list[dict[str, Any]]:
    if not isinstance(schedule, list) or len(schedule) != 35:
        raise WorkerError("manufactured schedule must contain 35 entries")
    expected_nodes = [24, 32, 48, 64, 96]
    expected_multipliers = ["0", "1/8", "-1/8", "1/4", "-1/4", "1/2", "-1/2"]
    cursor = 0
    normalized: list[dict[str, Any]] = []
    for seed_index, multiplier in enumerate(expected_multipliers):
        for node_count in expected_nodes:
            item = schedule[cursor]
            expected = {
                "ordinal": cursor,
                "seed_index": seed_index,
                "seed_multiplier": multiplier,
                "node_count": node_count,
                "degree": node_count - 1,
            }
            if item != expected:
                raise WorkerError(f"schedule mismatch at ordinal {cursor}")
            normalized.append(expected)
            cursor += 1
    return normalized


def primary_stub(payload: dict[str, Any]) -> dict[str, Any]:
    schedule = validate_schedule(payload.get("schedule"))
    schedule_sha256 = sha256_value(schedule)
    expected_schedule_sha256 = payload.get("schedule_sha256")
    if schedule_sha256 != expected_schedule_sha256:
        raise WorkerError("primary schedule digest mismatch")

    history: list[dict[str, Any]] = []
    for item in schedule:
        seed_index = int(item["seed_index"])
        node_count = int(item["node_count"])
        manufactured_residual = (seed_index + 1) / float(node_count**4)
        history.append({
            **item,
            "manufactured_residual_inf": manufactured_residual,
            "manufactured_step_norm": manufactured_residual / 2.0,
            "stub_status": "MANUFACTURED_NO_PHYSICAL_SOLVE",
        })

    candidate_core = {
        "candidate_id": "BG3C8-MANUFACTURED-CANDIDATE-0001",
        "source_seed_indices": [0],
        "source_node_count": 96,
        "schedule_sha256": schedule_sha256,
        "augmented_variables": {
            "varphi_N_0": "0_control",
            "q_N": "0_control",
            "A_S_0": "0_control",
            "varphi_S_0": "0_control",
            "q_S": "0_control",
            "rho_N": "1_control",
            "rho_S": "1_control",
            "k4": "0_control"
        },
        "profile_descriptor": "MANUFACTURED_SERIALIZATION_ONLY",
        "physical_candidate": False,
    }
    candidate_handoff = {
        **candidate_core,
        "candidate_payload_sha256": sha256_value(candidate_core),
    }
    return {
        "schema": "universelab.background-3c8-primary-manufactured-stub.v0.1",
        "stage": "primary",
        "backend_kind": "MANUFACTURED_STUB",
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "schedule_sha256": schedule_sha256,
        "schedule_entry_count": len(schedule),
        "per_seed_per_level_history": history,
        "candidate_handoff": candidate_handoff,
        "physical_backend_imported": False,
        "newton_calls": 0,
        "target_solves": 0,
        "physical_evidence_effect": "NONE",
    }


def independent_stub(payload: dict[str, Any], *, disagreement: bool) -> dict[str, Any]:
    handoff = payload.get("candidate_handoff")
    if not isinstance(handoff, dict):
        raise WorkerError("candidate handoff missing")
    core = {key: value for key, value in handoff.items() if key != "candidate_payload_sha256"}
    if handoff.get("candidate_payload_sha256") != sha256_value(core):
        raise WorkerError("candidate handoff digest mismatch")
    if handoff.get("physical_candidate") is not False:
        raise WorkerError("manufactured handoff may not claim a physical candidate")

    residual = 1.0 if disagreement else 0.0
    distance = 1.0 if disagreement else 0.0
    agreement = (
        "MANUFACTURED_DISAGREEMENT_EXPECTED"
        if disagreement
        else "MANUFACTURED_AGREEMENT_CONTROL"
    )
    return {
        "schema": "universelab.background-3c8-independent-manufactured-stub.v0.1",
        "stage": "independent",
        "backend_kind": "MANUFACTURED_STUB",
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "candidate_id": handoff["candidate_id"],
        "candidate_payload_sha256": handoff["candidate_payload_sha256"],
        "per_candidate_residuals": {
            "R_A": residual,
            "R_ell": residual,
            "R_varphi": residual,
            "R_patch": residual,
            "R_4D": residual,
            "R_chi": residual,
            "R_scalar": residual,
            "R_gauge": residual
        },
        "candidate_distance_to_primary": distance,
        "agreement_classification": agreement,
        "physical_backend_imported": False,
        "regional_integration_calls": 0,
        "shooting_calls": 0,
        "shooting_jacobian_calls": 0,
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        if not isinstance(payload, dict):
            raise WorkerError("top-level object required")
        validate_common(payload)
        behavior = payload.get("behavior", "success")
        if behavior == "timeout":
            time.sleep(5.0)
        if behavior == "signal":
            os.kill(os.getpid(), signal.SIGTERM)
        stage = payload.get("stage")
        if stage == "primary":
            result = primary_stub(payload)
        elif stage == "independent":
            result = independent_stub(payload, disagreement=behavior == "disagreement")
        else:
            raise WorkerError("unknown manufactured stage")
        sys.stdout.buffer.write(canonical_json_bytes(result) + b"\n")
        return 0
    except (WorkerError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        failure = {
            "schema": "universelab.background-3c8-manufactured-worker-failure.v0.1",
            "status": "MANUFACTURED_WORKER_FAILURE",
            "error": f"{type(error).__name__}: {error}",
            "physical_backend_imported": False,
            "physical_solver_calls": 0,
            "physical_evidence_effect": "NONE",
        }
        sys.stdout.buffer.write(canonical_json_bytes(failure) + b"\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
