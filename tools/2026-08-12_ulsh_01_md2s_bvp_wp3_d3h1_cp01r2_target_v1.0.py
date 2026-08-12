#!/usr/bin/env python3
"""ULSH-01 / WP3-D3H1 source-bound CP01R2 physical target.

Audit is the default path and imports no numerical backend. The physical path is
reachable only through an exact transaction capability created by the future
CP01R2 single-use transaction supervisor. WP3-D3H1 CI never calls that path.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
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
RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2"
RUN_INPUT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3_CP01R2RunInputFreeze_v1.0.json"
D1_PROTOCOL = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D1_CP01R1FailureDiagnosis_CP01R2Protocol_v1.0.json"
D2_ETRN = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d2_cp01r2_etrn_v1.0.py"
PRIMARY = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.1.py"
SEED_ADAPTER = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py"
INDEPENDENT = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_independent_backend_v0.1.py"
LEGACY_QA = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.1.py"
PRECISION_QA = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.2.py"
PREREG = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"
RESOURCE = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
RESULT_SCHEMA = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2ResultSchema_v1.0.json"

RUN_PAYLOAD_SHA256 = "e8b8e82d2cb1472d91c387a40c8f84024c2549a3dcc2c897df5561f7bf721b36"
SCHEDULE_SHA256 = "929f59d018cc511f36c98ef26a8614ed495fe699a067b1b33e6c5b53efaf8e0b"
DEPENDENCY_LOCK_SHA256 = "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f"
NODE_COUNTS = (24, 32, 48, 64, 96)
SEED_ORDER = tuple(range(7))
PLANNED_ENTRY_COUNT = 35
BOUNDARY_ORDER = ("R_A", "R_ell", "R_varphi", "R_patch", "R_4D", "R_chi", "R_scalar", "R_gauge")
FORBIDDEN_INFERENCES = [
    "continuum_existence", "uniqueness", "Fredholm_property",
    "continuum_BVP_Jacobian_invertibility", "perturbative_stability",
    "ghost_freedom", "K1-D_release", "K1-E_admissibility",
    "physical_confirmation",
]
EXPECTED_BLOBS = {
    RUN_INPUT: "471f40a517140cc2a2d609f4828fd1004c4861e2",
    D1_PROTOCOL: "7f89a61ace7a54182ade2cc97cb38558496e9f68",
    D2_ETRN: "fd109330d44f504d89597c05f1dbfa638e0969bb",
    PRIMARY: "d451be299d0ca93a7dc4587782675b7adab5cfd7",
    SEED_ADAPTER: "e232537ab80f099b0b3a914c509041c13825e950",
    INDEPENDENT: "bed68e11a3682d8b140b6db0cbe71fd696c3ff34",
    LEGACY_QA: "304592405f843822e142110ba6a65fc845579489",
    PRECISION_QA: "db2f4a0ea1ac374209e52b21fdc72de23e5f419d",
}
EXPECTED_RAW_SHA256 = {
    PRIMARY: "830d4b4fdd28c8888876125479df3542eeb3864d4328764feb96b5d34bd91599",
    SEED_ADAPTER: "8ce1c0eceed64245d091d4bed492f3cf2a9c8314f631a03045aaa9696fb11c92",
    INDEPENDENT: "a8afd7b548366acf9f5ac72e91bcf07372913cc21a8790d86d0a989a89f03e7b",
}


class TargetContractError(RuntimeError):
    pass


class TargetExecutionDenied(TargetContractError):
    pass


@dataclass(frozen=True)
class TargetExecutionCapability:
    run_id: str
    run_payload_sha256: str
    schedule_sha256: str
    grant_sha256: str
    transaction_contract_sha256: str
    release_authorization_sha256: str
    source_bundle_sha256: str
    physical_solve_authorized: bool
    maximum_wall_clock_seconds_total: int
    maximum_wall_clock_seconds_per_seed_per_level: int
    maximum_memory_bytes: int


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TargetContractError(f"top-level object required: {path}")
    return value


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def dynamic_import(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise TargetContractError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def frozen_payload() -> dict[str, Any]:
    run_input = load_json(RUN_INPUT)
    payload = run_input["frozen_run_payload"]
    observed = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    if observed != RUN_PAYLOAD_SHA256 or run_input["frozen_run_payload_sha256"] != RUN_PAYLOAD_SHA256:
        raise TargetContractError("CP01R2 run-payload binding drift")
    return payload


def build_schedule() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    ordinal = 0
    for seed_index in SEED_ORDER:
        previous: str | None = None
        for node_count in NODE_COUNTS:
            ordinal += 1
            entry_id = f"CP01R2-E{ordinal:02d}-S{seed_index}-N{node_count}"
            rows.append({
                "ordinal": ordinal,
                "entry_id": entry_id,
                "seed_index": seed_index,
                "node_count": node_count,
                "continuation_from_entry_id": previous,
            })
            previous = entry_id
    if len(rows) != PLANNED_ENTRY_COUNT:
        raise TargetContractError("schedule cardinality drift")
    return rows


def schedule_sha256() -> str:
    return hashlib.sha256(canonical_json_bytes(build_schedule())).hexdigest()


def _verify_sources() -> None:
    for path, expected in EXPECTED_BLOBS.items():
        observed = git_blob_sha1(path)
        if observed != expected:
            raise TargetContractError(f"source blob drift: {path}: {observed}")
    for path, expected in EXPECTED_RAW_SHA256.items():
        observed = sha256_file(path)
        if observed != expected:
            raise TargetContractError(f"source SHA-256 drift: {path}: {observed}")


def _validate_capability(capability: TargetExecutionCapability) -> None:
    if not isinstance(capability, TargetExecutionCapability):
        raise TargetExecutionDenied("exact CP01R2 TargetExecutionCapability required")
    if capability.physical_solve_authorized is not True:
        raise TargetExecutionDenied("physical solve is not authorized")
    if capability.run_id != RUN_ID or capability.run_payload_sha256 != RUN_PAYLOAD_SHA256:
        raise TargetExecutionDenied("capability run binding mismatch")
    if capability.schedule_sha256 != SCHEDULE_SHA256 or schedule_sha256() != SCHEDULE_SHA256:
        raise TargetExecutionDenied("capability schedule binding mismatch")
    for value in (capability.grant_sha256, capability.transaction_contract_sha256, capability.release_authorization_sha256, capability.source_bundle_sha256):
        if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
            raise TargetExecutionDenied("invalid SHA-256 capability binding")
    limits = load_json(RESOURCE)["resource_limits"]
    if capability.maximum_wall_clock_seconds_total != int(limits["maximum_wall_clock_seconds_total"]):
        raise TargetExecutionDenied("total timeout capability drift")
    if capability.maximum_wall_clock_seconds_per_seed_per_level != int(limits["maximum_wall_clock_seconds_per_seed_per_level"]):
        raise TargetExecutionDenied("stage timeout capability drift")
    if capability.maximum_memory_bytes != int(limits["maximum_memory_bytes"]):
        raise TargetExecutionDenied("memory limit capability drift")


def _enforce_memory_limit(maximum_memory_bytes: int) -> None:
    if os.name != "posix":
        raise TargetContractError("physical execution requires POSIX RLIMIT_AS memory enforcement")
    import resource
    requested = int(maximum_memory_bytes)
    _soft, current_hard = resource.getrlimit(resource.RLIMIT_AS)
    infinity = resource.RLIM_INFINITY
    if current_hard not in (infinity, -1) and current_hard < requested:
        raise TargetContractError(f"host RLIMIT_AS hard limit {current_hard} is below frozen requirement {requested}")
    resource.setrlimit(resource.RLIMIT_AS, (requested, requested))
    observed_soft, observed_hard = resource.getrlimit(resource.RLIMIT_AS)
    if observed_soft != requested or observed_hard != requested:
        raise TargetContractError(f"failed to enforce exact RLIMIT_AS={requested}: {(observed_soft, observed_hard)}")


def _prolongate_state(primary: Any, state: Any, old_n: int, new_n: int):
    import numpy as np
    old_regions, parameters = primary.unpack_state(state, old_n)
    old_tau = primary.chebyshev_lobatto(old_n).tau
    new_tau = primary.chebyshev_lobatto(new_n).tau
    new_regions = [[np.interp(new_tau, old_tau, field) for field in region] for region in old_regions]
    return primary.pack_state(new_regions, parameters.copy())


def _replace_cp01r1_tokens(value: Any) -> Any:
    if isinstance(value, str):
        return value.replace("CP01R1", "CP01R2")
    if isinstance(value, dict):
        return {_replace_cp01r1_tokens(str(key)): _replace_cp01r1_tokens(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_replace_cp01r1_tokens(item) for item in value]
    if isinstance(value, tuple):
        return [_replace_cp01r1_tokens(item) for item in value]
    return value


def _etrn_provenance(entries: list[dict[str, Any]]) -> dict[str, Any]:
    raw_history: list[dict[str, Any]] = []
    scaled_history: list[dict[str, Any]] = []
    trust_history: list[dict[str, Any]] = []
    continuation: list[dict[str, Any]] = []
    for record in entries:
        continuation.append({
            "entry_id": record["entry_id"],
            "initialization_source": record.get("initialization_source"),
            "continuation_source_entry_id": record.get("continuation_source_entry_id"),
            "stage_initial_residual_inf": record.get("stage_initial_residual_inf"),
            "stage_final_residual_inf": record.get("stage_final_residual_inf"),
            "continuation_admissible": record.get("continuation_admissible"),
            "eligible_for_next_mesh": record.get("eligible_for_next_mesh", False),
            "continuation_rule": "finite_and_primary_admissible_and_not_timed_out_and_final<=0.90*initial",
        })
        for row in record.get("newton_history", []):
            raw_history.append({
                "entry_id": record["entry_id"], "iteration": row.get("iteration"),
                "rank": row.get("raw_rank"), "condition_estimate": row.get("raw_condition_estimate"),
                "interpretation": "DISCRETE_RAW_JACOBIAN_DIAGNOSTIC_NOT_CONTINUUM_RANK",
            })
            scaled_history.append({
                "entry_id": record["entry_id"], "iteration": row.get("iteration"),
                "rank": row.get("scaled_rank"), "condition_estimate": row.get("scaled_condition_estimate"),
                "interpretation": "ETRN_LINEAR_SOLVE_PRECONDITIONING_DIAGNOSTIC_ONLY",
            })
            trust_history.append({
                "entry_id": record["entry_id"], "iteration": row.get("iteration"),
                "trust_radius_before": row.get("trust_radius_before"),
                "trust_radius_after": row.get("trust_radius_after"),
                "rho": row.get("rho"), "accepted": row.get("accepted"),
                "accepted_factor": row.get("accepted_factor"),
                "accepted_scaled_step_norm": row.get("accepted_scaled_step_norm"),
                "trust_radius_active": row.get("trust_radius_active"),
                "acceptance_merit": row.get("acceptance_merit"),
            })
    return {
        "raw_rank_condition_history": raw_history,
        "scaled_rank_condition_history": scaled_history,
        "trust_radius_rho_history": trust_history,
        "progress_continuation_provenance": continuation,
    }


def audit_target() -> dict[str, Any]:
    _verify_sources()
    payload = frozen_payload()
    if schedule_sha256() != SCHEDULE_SHA256:
        raise TargetContractError("CP01R2 schedule digest drift")
    if payload["model_parameters_ordered"]["a_F"] != "1/4":
        raise TargetContractError("a_F drift")
    d1 = load_json(D1_PROTOCOL)
    if d1["cp01r2_protocol_design"]["state"] != "DESIGNED_NOT_AUTHORIZED_NOT_EXECUTED":
        raise TargetContractError("D1 CP01R2 protocol state drift")
    schema = load_json(RESULT_SCHEMA)
    expected_etrn = {"raw_rank_condition_history", "scaled_rank_condition_history", "trust_radius_rho_history", "progress_continuation_provenance"}
    if set(schema["cp01r2_etrn01_required_fields"]) != expected_etrn:
        raise TargetContractError("CP01R2 ETRN result closure drift")
    return {
        "status": "PASS_WP3_D3H1_CP01R2_TARGET_BOUND_NO_EXECUTION",
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "schedule_sha256": SCHEDULE_SHA256,
        "planned_entry_count": PLANNED_ENTRY_COUNT,
        "etrn01_result_provenance_capture": True,
        "legacy_qa_reused_source_bound": True,
        "higher_precision_qa_reused_source_bound": True,
        "memory_limit_enforced_before_numerical_import": True,
        "progress_continuation_uses_primary_domain_admissibility_not_boundary_acceptance": True,
        "solver_imported": False,
        "solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
    }


def execute_physical_schedule(capability: TargetExecutionCapability) -> dict[str, Any]:
    _validate_capability(capability)
    _verify_sources()
    _enforce_memory_limit(capability.maximum_memory_bytes)
    payload = frozen_payload()

    etrn = dynamic_import(D2_ETRN, "ulsh_cp01r2_etrn")
    primary = dynamic_import(SEED_ADAPTER, "ulsh_cp01r2_primary")
    independent = dynamic_import(INDEPENDENT, "ulsh_cp01r2_independent")
    legacy = dynamic_import(LEGACY_QA, "ulsh_cp01r2_legacy_qa")
    precision = dynamic_import(PRECISION_QA, "ulsh_cp01r2_precision_qa")
    import numpy as np
    from scipy.optimize import least_squares

    model = primary.model_from_payload(payload, control_a_F=False)
    sector = primary.sector_from_payload(payload)
    independent_model = independent.model_from_payload(payload, control_a_F=False)
    independent_sector = independent.sector_from_payload(payload)
    if float(model.a_F) != 0.25 or float(independent_model.a_F) != 0.25:
        raise TargetContractError("physical model a_F drift")

    prereg = load_json(PREREG)
    thresholds = prereg["acceptance_thresholds"]
    limits = load_json(RESOURCE)["resource_limits"]
    entries: list[dict[str, Any]] = []
    internal_states: dict[tuple[int, int], Any] = {}
    internal_details: dict[tuple[int, int], dict[str, Any]] = {}
    independent_records: dict[tuple[int, int], dict[str, Any]] = {}
    previous_terminal: dict[int, dict[str, Any]] = {}
    blocked_seed: dict[int, str] = {}
    execution_started_utc = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()

    for entry in build_schedule():
        seed_index = int(entry["seed_index"])
        node_count = int(entry["node_count"])
        if seed_index in blocked_seed:
            entries.append({**entry, "status": "SKIPPED_AFTER_TIMEOUT_NO_RETRY", "failure": blocked_seed[seed_index], "newton_history": [], "initialization_source": "SKIPPED"})
            continue
        prior = previous_terminal.get(seed_index)
        if prior and prior.get("eligible_for_next_mesh") is True:
            initial = _prolongate_state(primary, prior["state"], int(prior["node_count"]), node_count)
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
            with legacy.stage_wall_clock_limit(float(limits["maximum_wall_clock_seconds_per_seed_per_level"]), entry["entry_id"]):
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
                constraint_inf = float(max(np.max(np.abs(detail["north"].constraint)), np.max(np.abs(detail["south"].constraint))))
                local_candidate = bool(result.get("converged") and bulk_inf <= float(thresholds["bulk_residual_max"]) and boundary_inf <= float(thresholds["boundary_residual_max"]))
                diagnostic = legacy._diagnostic_jacobian(primary, state, node_count, model, sector)
                legacy_admissibility = legacy._admissibility(primary, state, node_count, detail, model, sector, thresholds)
                continuation_admissible = bool(primary.admissible(state, node_count))
                eligible = etrn.progress_continuation_eligible(
                    initial=initial_inf, final=final_inf,
                    finite=bool(np.all(np.isfinite(state))),
                    admissible=continuation_admissible, timed_out=False,
                )
                previous_terminal[seed_index] = {
                    "entry_id": entry["entry_id"], "node_count": node_count,
                    "state": state.copy(), "eligible_for_next_mesh": eligible,
                }
                internal_states[(seed_index, node_count)] = state.copy()
                internal_details[(seed_index, node_count)] = detail

                independent_record: dict[str, Any] | None = None
                if local_candidate:
                    _regions, shooting_initial = primary.unpack_state(state, node_count)
                    shooting_initial = np.asarray(shooting_initial, dtype=float)
                    sample_count = max(257, 4 * node_count + 1)
                    def independent_residual(vector):
                        values, _ = independent.shooting_residual(vector, independent_model, independent_sector, epsilon=1.0e-6, sample_count=sample_count)
                        return values
                    independent_result = least_squares(
                        independent_residual, shooting_initial,
                        jac=lambda x: independent.centered_fd_jacobian(independent_residual, x, relative_step=1.0e-6),
                        method="trf", max_nfev=120,
                        ftol=float(thresholds["bulk_residual_max"]),
                        xtol=float(thresholds["bulk_residual_max"]),
                        gtol=float(thresholds["bulk_residual_max"]),
                    )
                    final_boundary, independent_detail = independent.shooting_residual(
                        independent_result.x, independent_model, independent_sector,
                        epsilon=1.0e-6, sample_count=sample_count,
                    )
                    independent_constraint = float(max(np.max(np.abs(independent_detail["north"].constraint)), np.max(np.abs(independent_detail["south"].constraint))))
                    candidate_distance = legacy._independent_profile_distance(detail, shooting_initial, independent_detail, independent_result.x)
                    independent_inf = float(np.max(np.abs(final_boundary)))
                    agreement = "AGREES_WITHIN_PREREGISTERED_DISTANCE" if bool(independent_result.success) and independent_inf <= float(thresholds["boundary_residual_max"]) and candidate_distance <= float(thresholds["independent_backend_candidate_distance_max"]) else "DISAGREES_OR_NOT_CONVERGED"
                    independent_record = {
                        "entry_id": entry["entry_id"], "converged": bool(independent_result.success),
                        "points_per_region": sample_count,
                        "all_eight_boundary_residuals": {name: float(value) for name, value in zip(BOUNDARY_ORDER, final_boundary)},
                        "boundary_residual_max": independent_inf,
                        "constraint_max": independent_constraint,
                        "candidate_distance_to_primary": candidate_distance,
                        "agreement_classification": agreement,
                        "nfev": int(independent_result.nfev),
                    }
                    independent_records[(seed_index, node_count)] = independent_record

                entries.append({
                    **entry,
                    "seed_id": f"M1-BG3B-CP01-SEEDS-01:S{seed_index}",
                    "status": "COMPLETED",
                    "initialization_source": initialization_source,
                    "continuation_source_entry_id": continuation_source,
                    "stage_initial_residual_inf": initial_inf,
                    "stage_final_residual_inf": final_inf,
                    "continuation_admissible": continuation_admissible,
                    "eligible_for_next_mesh": eligible,
                    "primary": {"converged": bool(result.get("converged")), "candidate_under_local_residual_gate": local_candidate, "failure": result.get("failure")},
                    "failure": result.get("failure"),
                    "bulk_residual_max": bulk_inf,
                    "boundary_residual_max": boundary_inf,
                    "all_eight_boundary_residuals": {name: float(value) for name, value in zip(BOUNDARY_ORDER, boundary)},
                    "rr_constraint_profile": constraint_profile,
                    "constraint_max": constraint_inf,
                    "diagnostic": legacy._to_builtin(diagnostic),
                    "newton_history": legacy._to_builtin(result.get("history", [])),
                    "independent": independent_record,
                    "legacy_full_qa_admissibility": legacy._to_builtin(legacy_admissibility),
                    "elapsed_wall_clock_seconds": time.monotonic() - stage_started,
                })
        except legacy.StageTimeoutError as exc:
            blocked_seed[seed_index] = "STAGE_TIMEOUT_NO_RETRY"
            previous_terminal.pop(seed_index, None)
            entries.append({
                **entry, "seed_id": f"M1-BG3B-CP01-SEEDS-01:S{seed_index}",
                "status": "TIMED_OUT_NO_RETRY", "failure": "STAGE_TIMEOUT_NO_RETRY",
                "timeout_message": str(exc), "newton_history": [],
                "initialization_source": initialization_source,
                "continuation_source_entry_id": continuation_source,
                "stage_initial_residual_inf": initial_inf,
                "stage_final_residual_inf": None, "continuation_admissible": False,
                "eligible_for_next_mesh": False,
                "elapsed_wall_clock_seconds": time.monotonic() - stage_started,
            })

    finalized = legacy._finalize(entries, internal_states, internal_details, independent_records, primary, model, sector, thresholds)
    finalized = _replace_cp01r1_tokens(finalized)
    finalized["primary_backend"].update(_etrn_provenance(entries))
    raw = {
        "schema": "universelab.ulsh-01.md2s-bvp.cp01r2-result.v1",
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "schedule_sha256": SCHEDULE_SHA256,
        "implementation_source_sha256": sha256_file(Path(__file__)),
        "dependency_lock_sha256": DEPENDENCY_LOCK_SHA256,
        "execution_started_utc": execution_started_utc,
        "execution_finished_utc": datetime.now(timezone.utc).isoformat(),
        "planned_schedule_entries": PLANNED_ENTRY_COUNT,
        "matrix_entries": entries,
        "stage_timeout_count": sum(record.get("status") == "TIMED_OUT_NO_RETRY" for record in entries),
        "execution_elapsed_wall_clock_seconds": time.monotonic() - start,
        **finalized,
        "forbidden_inferences": FORBIDDEN_INFERENCES,
        "physical_evidence_effect": "NONE",
    }
    raw = precision._apply_precision_gate(raw)
    raw["primary_backend"].update(_etrn_provenance(entries))
    return raw


def _capability_from_json(path: Path) -> TargetExecutionCapability:
    data = load_json(path)
    return TargetExecutionCapability(**data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-capability")
    parser.add_argument("--result-pickle")
    args = parser.parse_args()
    if args.execute_capability or args.result_pickle:
        if not args.execute_capability or not args.result_pickle:
            raise TargetExecutionDenied("both --execute-capability and --result-pickle are required")
        result = execute_physical_schedule(_capability_from_json(Path(args.execute_capability)))
        with Path(args.result_pickle).open("wb") as stream:
            pickle.dump(result, stream, protocol=5)
        return 0
    print(json.dumps(audit_target(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
