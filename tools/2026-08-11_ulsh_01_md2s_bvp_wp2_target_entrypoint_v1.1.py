#!/usr/bin/env python3
"""ULSH-01 / WP2-H hardened source-bound CP01R1 target entry point v1.1.

This module closes the execution-side parts of release-review blockers RR-B01 and
RR-B03 without authorizing or executing a physical solve in audit/CI paths.

Hardening additions over the frozen WP2 v1.0 target:
- fail-closed per-seed/per-node-level wall-clock enforcement;
- total wall-clock accounting without changing the immutable 7 x 5 schedule;
- lossless capture of the preregistered residual, constraint, convergence,
  spectral-tail, Jacobian/SVD, independent-backend and admissibility channels;
- deterministic final classification under the already frozen result vocabulary.

Direct invocation remains an audit only. Numerical backends are imported only by
execute_physical_schedule() after a capability issued by the hardened transaction
has passed a later, separate release + single-use-grant firewall.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
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

ROOT = Path(__file__).resolve().parents[1]
BASE_TARGET_PATH = ROOT / "tools/2026-08-10_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.0.py"
RESOURCE_POLICY_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
RESULT_SCHEMA_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResultSchema_v0.1.json"
PREREG_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"

_SPEC = importlib.util.spec_from_file_location("ulsh_wp2_target_v10_base", BASE_TARGET_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("unable to import frozen WP2 v1.0 target")
BASE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = BASE
_SPEC.loader.exec_module(BASE)

RUN_ID = BASE.RUN_ID
FROZEN_PAYLOAD_SHA256 = BASE.FROZEN_PAYLOAD_SHA256
SEED_SET_ID = BASE.SEED_SET_ID
SEED_MULTIPLIERS = BASE.SEED_MULTIPLIERS
NODE_COUNTS = BASE.NODE_COUNTS
PLANNED_ENTRY_COUNT = BASE.PLANNED_ENTRY_COUNT
DEPENDENCY_LOCK_SHA256 = BASE.DEPENDENCY_LOCK_SHA256
PRIMARY_PATH = BASE.PRIMARY_PATH
PRIMARY_BASE_PATH = BASE.PRIMARY_BASE_PATH
INDEPENDENT_PATH = BASE.INDEPENDENT_PATH
PRIMARY_SHA256 = BASE.PRIMARY_SHA256
PRIMARY_BASE_SHA256 = BASE.PRIMARY_BASE_SHA256
INDEPENDENT_SHA256 = BASE.INDEPENDENT_SHA256
PARAMETER_ORDER = (
    "varphi_N_0", "q_N", "A_S_0", "varphi_S_0",
    "q_S", "rho_N", "rho_S", "k4",
)
BOUNDARY_ORDER = (
    "R_A", "R_ell", "R_varphi", "R_patch",
    "R_4D", "R_chi", "R_scalar", "R_gauge",
)
FORBIDDEN_INFERENCES = [
    "continuum_existence",
    "uniqueness",
    "Fredholm_property",
    "continuum_BVP_Jacobian_invertibility",
    "perturbative_stability",
    "ghost_freedom",
    "K1-D_release",
    "K1-E_admissibility",
    "physical_confirmation",
]


class TargetContractError(RuntimeError):
    pass


class TargetExecutionDenied(RuntimeError):
    pass


class StageTimeoutError(TimeoutError):
    pass


@dataclass(frozen=True)
class TargetExecutionCapability:
    run_id: str
    frozen_payload_sha256: str
    schedule_sha256: str
    grant_sha256: str
    transaction_contract_sha256: str
    release_authorization_sha256: str
    physical_solve_authorized: bool
    maximum_wall_clock_seconds_total: int
    maximum_wall_clock_seconds_per_seed_per_level: int


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TargetContractError(f"top-level JSON object required: {path}")
    return value


def _dynamic_import(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise TargetContractError(f"cannot import backend: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def build_schedule() -> list[dict[str, Any]]:
    return BASE.build_schedule()


def schedule_sha256() -> str:
    return BASE.schedule_sha256()


def frozen_payload() -> dict[str, Any]:
    return BASE.frozen_payload()


def _to_builtin(value: Any) -> Any:
    try:
        import numpy as np
    except ImportError:
        np = None  # type: ignore[assignment]
    if np is not None:
        if isinstance(value, np.ndarray):
            return [_to_builtin(item) for item in value.tolist()]
        if isinstance(value, np.generic):
            return value.item()
    if isinstance(value, dict):
        return {str(key): _to_builtin(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_builtin(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def validate_schedule_against_sources() -> dict[str, Any]:
    return BASE.validate_schedule_against_sources()


def validate_backend_hashes() -> dict[str, str]:
    return BASE.validate_backend_hashes()


def _resource_limits() -> dict[str, int]:
    limits = load_json(RESOURCE_POLICY_PATH)["resource_limits"]
    return {
        "total": int(limits["maximum_wall_clock_seconds_total"]),
        "stage": int(limits["maximum_wall_clock_seconds_per_seed_per_level"]),
    }


def _validate_capability(capability: TargetExecutionCapability) -> None:
    if not isinstance(capability, TargetExecutionCapability):
        raise TargetExecutionDenied("hardened target execution requires WP2-H capability")
    if capability.physical_solve_authorized is not True:
        raise TargetExecutionDenied("physical solve is not authorized")
    if capability.run_id != RUN_ID or capability.frozen_payload_sha256 != FROZEN_PAYLOAD_SHA256:
        raise TargetExecutionDenied("capability is bound to another run")
    if capability.schedule_sha256 != schedule_sha256():
        raise TargetExecutionDenied("capability schedule digest mismatch")
    for value in (
        capability.grant_sha256,
        capability.transaction_contract_sha256,
        capability.release_authorization_sha256,
    ):
        if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
            raise TargetExecutionDenied("capability contains an invalid SHA-256 binding")
    limits = _resource_limits()
    if capability.maximum_wall_clock_seconds_total != limits["total"]:
        raise TargetExecutionDenied("total wall-clock capability differs from frozen resource policy")
    if capability.maximum_wall_clock_seconds_per_seed_per_level != limits["stage"]:
        raise TargetExecutionDenied("per-stage wall-clock capability differs from frozen resource policy")


@contextmanager
def stage_wall_clock_limit(seconds: float, entry_id: str):
    """Enforce one immutable schedule-entry timeout, fail-closed if unavailable."""
    if seconds <= 0.0:
        raise StageTimeoutError(f"{entry_id}: no wall-clock budget remains")
    if os.name != "posix" or not hasattr(signal, "SIGALRM") or not hasattr(signal, "setitimer"):
        raise TargetContractError(
            "physical execution requires POSIX SIGALRM/setitimer for frozen per-entry timeout enforcement"
        )

    def handler(_signum, _frame):
        raise StageTimeoutError(f"{entry_id}: per-seed/per-level wall-clock limit exceeded")

    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)
    if previous_timer[0] > 0.0:
        raise TargetContractError("unexpected pre-existing ITIMER_REAL; nested wall-clock timers are forbidden")
    signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, float(seconds))
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, previous_handler)


def _spectral_tail(primary: Any, values: Any, tau: Any) -> dict[str, Any]:
    import numpy as np
    x = 2.0 * np.asarray(tau, dtype=float) - 1.0
    y = np.asarray(values, dtype=float)
    coefficients = np.polynomial.chebyshev.chebfit(x, y, deg=y.size - 1)
    tail = np.abs(coefficients[-8:])
    if np.all(tail <= np.finfo(float).tiny):
        slope = 0.0
        decreasing = True
    else:
        log_tail = np.log10(np.maximum(tail, np.finfo(float).tiny))
        slope = float(np.polyfit(np.arange(tail.size, dtype=float), log_tail, 1)[0])
        decreasing = bool(slope < 0.0 or tail[-1] <= tail[0])
    return {
        "last_eight_absolute_coefficients": tail.tolist(),
        "maximum_last_eight": float(np.max(tail)),
        "log10_linear_slope": slope,
        "decreases_overall": decreasing,
    }


def _diagnostic_jacobian(primary: Any, state: Any, node_count: int, model: Any, sector: Any) -> dict[str, Any]:
    import numpy as np
    import scipy.linalg as la
    jacobian = primary.complex_step_jacobian(state, node_count, model, sector)
    singular_values = np.asarray(la.svdvals(jacobian), dtype=float)
    sigma_max = float(singular_values[0]) if singular_values.size else 0.0
    sigma_min = float(singular_values[-1]) if singular_values.size else 0.0
    rank = int(np.count_nonzero(singular_values > 1.0e-12 * sigma_max)) if sigma_max > 0.0 else 0
    condition = math.inf if sigma_min <= 0.0 else sigma_max / sigma_min
    return {
        "rrqr_rank_diagnostic": rank,
        "column_count": int(jacobian.shape[1]),
        "singular_values_diagnostic": singular_values.tolist(),
        "sigma_max": sigma_max,
        "sigma_min": sigma_min,
        "condition_estimate_diagnostic": condition,
        "interpretation": "DISCRETE_NUMERICAL_DIAGNOSTIC_NOT_CONTINUUM_RANK_OR_FREDHOLM_PROOF",
    }


def _profile_artifact(primary: Any, state: Any, node_count: int, detail: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    import numpy as np
    grid = primary.chebyshev_lobatto(node_count)
    regions, parameters = primary.unpack_state(state, node_count)
    north = detail["north"]
    south = detail["south"]
    physical_fields = ("A", "ell", "varphi", "a_chi", "A_x", "ell_x", "varphi_x", "constraint")
    return {
        "schema": "universelab.ulsh-01.wp2-h.candidate-profile.v1",
        "run_id": RUN_ID,
        "entry_id": entry["entry_id"],
        "seed_index": int(entry["seed_index"]),
        "node_count": node_count,
        "tau": np.asarray(grid.tau, dtype=float).tolist(),
        "regularized_profile_order": ["u_A", "u_ell", "u_varphi", "u_g"],
        "regularized_profiles": {
            "north": [np.asarray(field, dtype=float).tolist() for field in regions[0]],
            "south": [np.asarray(field, dtype=float).tolist() for field in regions[1]],
        },
        "physical_profiles": {
            "north": {name: np.asarray(getattr(north, name), dtype=float).tolist() for name in physical_fields},
            "south": {name: np.asarray(getattr(south, name), dtype=float).tolist() for name in physical_fields},
        },
        "augmented_variable_order": list(PARAMETER_ORDER),
        "augmented_variables": {name: float(value) for name, value in zip(PARAMETER_ORDER, parameters)},
        "all_eight_boundary_residuals": {
            name: float(value) for name, value in zip(BOUNDARY_ORDER, detail["boundary"])
        },
    }


def _regularized_profile_distance(primary: Any, coarse_state: Any, coarse_n: int, fine_state: Any, fine_n: int) -> tuple[float, float]:
    import numpy as np
    coarse_regions, coarse_parameters = primary.unpack_state(coarse_state, coarse_n)
    fine_regions, fine_parameters = primary.unpack_state(fine_state, fine_n)
    coarse_tau = primary.chebyshev_lobatto(coarse_n).tau
    fine_tau = primary.chebyshev_lobatto(fine_n).tau
    profile_max = 0.0
    for region_index in range(2):
        for field_index in range(4):
            interpolated = np.interp(fine_tau, coarse_tau, coarse_regions[region_index][field_index])
            profile_max = max(
                profile_max,
                float(np.max(np.abs(interpolated - fine_regions[region_index][field_index]))),
            )
    augmented = float(np.max(np.abs(np.asarray(coarse_parameters) - np.asarray(fine_parameters))))
    return profile_max, augmented


def _independent_profile_distance(primary_detail: dict[str, Any], primary_parameters: Any, independent_detail: dict[str, Any], independent_parameters: Any) -> float:
    import numpy as np
    maximum = float(np.max(np.abs(np.asarray(independent_parameters) - np.asarray(primary_parameters))))
    for name, rho_index in (("north", 5), ("south", 6)):
        primary_region = primary_detail[name]
        independent_region = independent_detail[name]
        rho = float(primary_parameters[rho_index])
        tau_primary = np.linspace(0.0, 1.0, len(primary_region.A))
        # Primary collocation nodes are Lobatto, not uniform; derive them from length.
        n = len(primary_region.A)
        tau_primary = (np.cos(np.pi * np.arange(n) / (n - 1))[::-1] + 1.0) / 2.0
        tau_independent = (np.asarray(independent_region.x, dtype=float) / rho) ** 2
        mask = tau_primary >= float(tau_independent[0])
        channels = (
            (np.asarray(primary_region.A, dtype=float), 0),
            (np.asarray(primary_region.ell, dtype=float), 2),
            (np.asarray(primary_region.varphi, dtype=float), 4),
            (np.asarray(primary_region.a_chi, dtype=float), 6),
        )
        for primary_values, index in channels:
            interpolated = np.interp(
                tau_primary[mask], tau_independent,
                np.asarray(independent_region.y[index], dtype=float),
            )
            maximum = max(maximum, float(np.max(np.abs(primary_values[mask] - interpolated))))
    return maximum


def _admissibility(primary: Any, state: Any, node_count: int, detail: dict[str, Any], model: Any, sector: Any, thresholds: dict[str, Any]) -> dict[str, Any]:
    import numpy as np
    regions, parameters = primary.unpack_state(state, node_count)
    north, south = detail["north"], detail["south"]
    boundary = np.asarray(detail["boundary"], dtype=float)
    ell_sigma = 0.5 * (float(north.ell[-1]) + float(south.ell[-1]))
    d_chi = int(sector.N_sigma) - int(sector.m_sigma) * float(model.q_hat) * float(south.a_chi[-1])
    Y_sigma = float(model.z_sigma_hat) * d_chi**2 / ell_sigma**2 if ell_sigma > 0.0 else -math.inf
    finite_channels = [
        np.asarray(north.A), np.asarray(north.ell), np.asarray(north.varphi), np.asarray(north.a_chi),
        np.asarray(north.A_x), np.asarray(north.ell_x), np.asarray(north.varphi_x),
        np.asarray(south.A), np.asarray(south.ell), np.asarray(south.varphi), np.asarray(south.a_chi),
        np.asarray(south.A_x), np.asarray(south.ell_x), np.asarray(south.varphi_x),
        np.asarray(parameters), boundary,
    ]
    active_domain = bool(
        math.isfinite(float(model.Lambda_hat))
        and float(model.mhat_phi_sq) > 0.0
        and float(model.a_F) > 0.0
        and math.isfinite(float(model.lambda_hat))
        and float(model.z_sigma_hat) > 0.0
        and float(model.q_hat) > 0.0
    )
    topology_ok = bool(
        isinstance(int(sector.N_F), int)
        and isinstance(int(sector.N_sigma), int)
        and int(sector.m_sigma) > 0
        and abs(float(boundary[3])) <= float(thresholds["boundary_residual_max"])
    )
    gates = {
        "rho_N_positive": float(parameters[5]) > float(thresholds["minimum_rho_N"]),
        "rho_S_positive": float(parameters[6]) > float(thresholds["minimum_rho_S"]),
        "ell_positive_on_open_intervals": bool(
            np.min(np.asarray(north.ell)[1:-1]) > float(thresholds["minimum_interior_ell_margin"])
            and np.min(np.asarray(south.ell)[1:-1]) > float(thresholds["minimum_interior_ell_margin"])
        ),
        "ell_cap_positive": bool(
            float(north.ell[-1]) > float(thresholds["minimum_cap_ell_margin"])
            and float(south.ell[-1]) > float(thresholds["minimum_cap_ell_margin"])
        ),
        "finite_all_profiles_and_first_required_derivatives": all(bool(np.all(np.isfinite(item))) for item in finite_channels),
        "M1_active_domain_respected": active_domain,
        "charge_lattice_and_patch_sector_respected": topology_ok,
        "positive_winding_gate": Y_sigma >= float(thresholds["minimum_positive_winding_margin"]),
        "no_nan_or_infinity": bool(np.all(np.isfinite(np.asarray(state, dtype=float)))),
    }
    return {"gates": gates, "Y_sigma": Y_sigma, "all_pass": all(gates.values())}


def _residual_monotonicity(records: dict[int, dict[str, Any]]) -> dict[str, Any]:
    pairs = ((48, 64), (64, 96))
    details: list[dict[str, Any]] = []
    all_pass = True
    for coarse, fine in pairs:
        if coarse not in records or fine not in records:
            details.append({"pair": [coarse, fine], "available": False, "pass": False})
            all_pass = False
            continue
        component_pass: dict[str, bool] = {}
        for key in ("bulk_residual_max", "boundary_residual_max", "constraint_max"):
            left = float(records[coarse][key])
            right = float(records[fine][key])
            passed = right <= 1.25 * max(left, 1.0e-300)
            component_pass[key] = passed
            all_pass = all_pass and passed
        details.append({"pair": [coarse, fine], "available": True, "component_pass": component_pass, "pass": all(component_pass.values())})
    return {"pairs": details, "all_pass": all_pass}


def _finalize(raw_entries: list[dict[str, Any]], internal_states: dict[tuple[int, int], Any], internal_details: dict[tuple[int, int], dict[str, Any]], independent_records: dict[tuple[int, int], dict[str, Any]], primary: Any, model: Any, sector: Any, thresholds: dict[str, Any]) -> dict[str, Any]:
    import numpy as np
    by_seed: dict[int, dict[int, dict[str, Any]]] = {seed: {} for seed in range(7)}
    for record in raw_entries:
        if record.get("status") == "COMPLETED":
            by_seed[int(record["seed_index"])][int(record["node_count"])] = record

    profile_convergence: list[dict[str, Any]] = []
    augmented_convergence: list[dict[str, Any]] = []
    spectral_table: list[dict[str, Any]] = []
    candidate_inventory: list[dict[str, Any]] = []
    profile_artifacts: dict[str, dict[str, Any]] = {}
    per_seed_acceptance: list[dict[str, Any]] = []
    passing_states: list[tuple[str, Any]] = []

    for seed_index in range(7):
        records = by_seed[seed_index]
        pair_values: dict[str, dict[str, float]] = {}
        for coarse, fine in ((48, 64), (64, 96)):
            key = f"{coarse}->{fine}"
            if (seed_index, coarse) in internal_states and (seed_index, fine) in internal_states:
                profile_diff, augmented_diff = _regularized_profile_distance(
                    primary,
                    internal_states[(seed_index, coarse)], coarse,
                    internal_states[(seed_index, fine)], fine,
                )
                pair_values[key] = {"profile": profile_diff, "augmented": augmented_diff}
                profile_convergence.append({"seed_index": seed_index, "pair": [coarse, fine], "difference_max": profile_diff})
                augmented_convergence.append({"seed_index": seed_index, "pair": [coarse, fine], "difference_max": augmented_diff})
            else:
                pair_values[key] = {"profile": math.inf, "augmented": math.inf}

        n96_key = (seed_index, 96)
        n96_record = records.get(96)
        has_n96_root = bool(n96_record and n96_record.get("primary", {}).get("candidate_under_local_residual_gate"))
        required_success = all(
            level in records and bool(records[level].get("primary", {}).get("candidate_under_local_residual_gate"))
            for level in (48, 64, 96)
        )
        monotonic = _residual_monotonicity(records)
        fine_profile = pair_values["64->96"]["profile"]
        fine_augmented = pair_values["64->96"]["augmented"]
        convergence_pass = (
            fine_profile <= float(thresholds["fine_mesh_profile_difference_max"])
            and fine_augmented <= float(thresholds["fine_mesh_augmented_difference_max"])
        )
        spectral_pass = False
        admissibility = {"gates": {}, "Y_sigma": None, "all_pass": False}
        independent_distance = math.inf
        independent_pass = False
        candidate_id = f"CP01R1-CAND-S{seed_index}"

        if n96_key in internal_states:
            state = internal_states[n96_key]
            detail = internal_details[n96_key]
            grid = primary.chebyshev_lobatto(96)
            regions, parameters = primary.unpack_state(state, 96)
            field_rows: list[dict[str, Any]] = []
            all_spectral = True
            for region_name, region_fields in (("north", regions[0]), ("south", regions[1])):
                for field_name, values in zip(("u_A", "u_ell", "u_varphi", "u_g"), region_fields):
                    tail = _spectral_tail(primary, values, grid.tau)
                    passed = tail["decreases_overall"] and tail["maximum_last_eight"] < 1.0e-9
                    all_spectral = all_spectral and passed
                    row = {"seed_index": seed_index, "node_count": 96, "region": region_name, "field": field_name, **tail, "pass": passed}
                    field_rows.append(row)
                    spectral_table.append(row)
            spectral_pass = all_spectral
            admissibility = _admissibility(primary, state, 96, detail, model, sector, thresholds)
            if n96_key in independent_records:
                independent_distance = float(independent_records[n96_key]["candidate_distance_to_primary"])
                independent_pass = bool(
                    independent_records[n96_key]["agreement_classification"] == "AGREES_WITHIN_PREREGISTERED_DISTANCE"
                )
            profile_artifacts[candidate_id] = _profile_artifact(primary, state, 96, detail, {
                "entry_id": n96_record["entry_id"] if n96_record else f"CP01R1-S{seed_index}-N96",
                "seed_index": seed_index,
            })
            if has_n96_root:
                all_pass = bool(
                    required_success
                    and monotonic["all_pass"]
                    and convergence_pass
                    and spectral_pass
                    and admissibility["all_pass"]
                    and independent_pass
                    and float(n96_record["constraint_max"]) <= float(thresholds["rr_constraint_max"])
                    and float(n96_record["diagnostic"]["condition_estimate_diagnostic"] or math.inf)
                        <= float(thresholds["maximum_reported_discrete_condition_number_without_high_precision_audit"])
                )
                classification = (
                    "NUMERICAL_CANDIDATE_BACKGROUND_DIAGNOSTIC"
                    if all_pass else "NUMERICAL_ROOT_REJECTED_BY_QA"
                )
                candidate_inventory.append({
                    "candidate_id": candidate_id,
                    "source_seed_indices": [seed_index],
                    "profile_artifact_sha256": None,
                    "profile_artifact_key": candidate_id,
                    "augmented_variables": {
                        name: float(value) for name, value in zip(PARAMETER_ORDER, parameters)
                    },
                    "admissibility_gates": admissibility,
                    "all_eight_boundary_residuals": {
                        name: float(value) for name, value in zip(BOUNDARY_ORDER, detail["boundary"])
                    },
                    "bulk_residual_max": float(n96_record["bulk_residual_max"]),
                    "constraint_max": float(n96_record["constraint_max"]),
                    "fine_mesh_profile_difference": fine_profile,
                    "fine_mesh_augmented_difference": fine_augmented,
                    "independent_backend_distance": independent_distance,
                    "classification": classification,
                })
                if all_pass:
                    passing_states.append((candidate_id, np.asarray(state, dtype=float).copy()))
        else:
            field_rows = []
            all_pass = False
            classification = "NO_N96_ROOT"

        per_seed_acceptance.append({
            "seed_index": seed_index,
            "has_n96_local_root": has_n96_root,
            "required_successful_levels_48_64_96": required_success,
            "residual_monotonicity": monotonic,
            "fine_pair_profile_difference": fine_profile,
            "fine_pair_augmented_difference": fine_augmented,
            "fine_pair_convergence_pass": convergence_pass,
            "spectral_tail_pass": spectral_pass,
            "admissibility": admissibility,
            "independent_backend_distance": independent_distance,
            "independent_backend_pass": independent_pass,
            "classification": classification,
        })

    distinct_passing: list[tuple[str, Any]] = []
    distinctness_threshold = 1.0e-6
    for candidate_id, state in passing_states:
        if not any(float(np.max(np.abs(state - existing))) <= distinctness_threshold for _, existing in distinct_passing):
            distinct_passing.append((candidate_id, state))

    if len(distinct_passing) > 1:
        final_classification = "MULTIPLE_NUMERICAL_CANDIDATE_BACKGROUNDS_DIAGNOSTIC"
    elif len(distinct_passing) == 1:
        final_classification = "NUMERICAL_CANDIDATE_BACKGROUND_DIAGNOSTIC"
    elif candidate_inventory:
        final_classification = "NUMERICAL_ROOT_REJECTED_BY_QA"
    else:
        final_classification = "NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL"

    primary_backend = {
        "node_counts": list(NODE_COUNTS),
        "per_seed_per_level_history": [
            {
                "entry_id": record["entry_id"],
                "seed_index": record["seed_index"],
                "node_count": record["node_count"],
                "status": record["status"],
                "newton_history": record.get("newton_history", []),
                "failure": record.get("failure"),
                "elapsed_wall_clock_seconds": record.get("elapsed_wall_clock_seconds"),
            }
            for record in raw_entries
        ],
        "all_boundary_residuals": [
            {"entry_id": record["entry_id"], "values": record.get("all_eight_boundary_residuals")}
            for record in raw_entries if record.get("all_eight_boundary_residuals") is not None
        ],
        "bulk_residual_norms": [
            {"entry_id": record["entry_id"], "max_abs": record.get("bulk_residual_max")}
            for record in raw_entries
        ],
        "constraint_norms": [
            {"entry_id": record["entry_id"], "max_abs": record.get("constraint_max"), "profiles": record.get("rr_constraint_profile")}
            for record in raw_entries
        ],
        "profile_convergence": profile_convergence,
        "augmented_variable_convergence": augmented_convergence,
        "spectral_tail_table": spectral_table,
        "rrqr_ranks": [
            {"entry_id": record["entry_id"], "rank": record.get("diagnostic", {}).get("rrqr_rank_diagnostic")}
            for record in raw_entries if record.get("diagnostic")
        ],
        "singular_values": [
            {"entry_id": record["entry_id"], "values": record.get("diagnostic", {}).get("singular_values_diagnostic"), "label": "DISCRETE_DIAGNOSTIC"}
            for record in raw_entries if record.get("diagnostic")
        ],
        "condition_estimates": [
            {"entry_id": record["entry_id"], "value": record.get("diagnostic", {}).get("condition_estimate_diagnostic"), "label": "DISCRETE_DIAGNOSTIC"}
            for record in raw_entries if record.get("diagnostic")
        ],
    }
    independent_backend = {
        "implementation_source_sha256": INDEPENDENT_SHA256,
        "residual_assembly_independence_statement": "Independent x-space DOP853 backend does not import or wrap the primary tau-collocation residual assembly.",
        "grid_or_mesh_definition": "Two independent regional x-grids; >=257 sampled points per region for every dispatched comparison.",
        "per_candidate_residuals": [
            {"entry_id": value["entry_id"], "all_eight_boundary_residuals": value["all_eight_boundary_residuals"], "constraint_max": value["constraint_max"]}
            for value in independent_records.values()
        ],
        "candidate_distance_to_primary": [
            {"entry_id": value["entry_id"], "distance": value["candidate_distance_to_primary"]}
            for value in independent_records.values()
        ],
        "agreement_classification": [
            {"entry_id": value["entry_id"], "classification": value["agreement_classification"]}
            for value in independent_records.values()
        ],
    }
    acceptance_audit = {
        "thresholds": _to_builtin(thresholds),
        "per_seed": per_seed_acceptance,
        "distinctness_threshold": distinctness_threshold,
        "passing_candidate_ids": [candidate_id for candidate_id, _ in passing_states],
        "distinct_passing_candidate_ids": [candidate_id for candidate_id, _ in distinct_passing],
        "all_thresholds_must_pass_simultaneously": True,
        "interpretation": "NUMERICAL_QA_ONLY_NOT_PHYSICAL_CONFIRMATION",
    }
    return {
        "primary_backend": primary_backend,
        "independent_backend": independent_backend,
        "candidate_inventory": candidate_inventory,
        "acceptance_audit": acceptance_audit,
        "profile_artifacts": profile_artifacts,
        "final_classification": final_classification,
    }


def audit_target() -> dict[str, Any]:
    base = BASE.audit_target()
    limits = load_json(RESOURCE_POLICY_PATH)["resource_limits"]
    schema = load_json(RESULT_SCHEMA_PATH)
    prereg = load_json(PREREG_PATH)
    required_primary = set(schema["primary_backend_required_fields"])
    provided_primary = {
        "node_counts", "per_seed_per_level_history", "all_boundary_residuals",
        "bulk_residual_norms", "constraint_norms", "profile_convergence",
        "augmented_variable_convergence", "spectral_tail_table", "rrqr_ranks",
        "singular_values", "condition_estimates",
    }
    if required_primary != provided_primary:
        raise TargetContractError("hardened primary result capture does not cover frozen schema")
    mandatory = set(prereg["mandatory_run_artifacts"])
    if "rr-constraint profile" not in mandatory or "spectral-tail table" not in mandatory:
        raise TargetContractError("preregistration mandatory-artifact vocabulary drift")
    return {
        "status": "PASS_WP2_HARDENED_TARGET_NO_SOLVE",
        "base_target_status": base["status"],
        "run_id": RUN_ID,
        "frozen_payload_sha256": FROZEN_PAYLOAD_SHA256,
        "schedule_sha256": base["schedule_sha256"],
        "planned_entry_count": base["planned_entry_count"],
        "a_F": base["a_F"],
        "backend_sha256": base["backend_sha256"],
        "per_stage_timeout_seconds": int(limits["maximum_wall_clock_seconds_per_seed_per_level"]),
        "total_timeout_seconds": int(limits["maximum_wall_clock_seconds_total"]),
        "stage_timeout_enforced_in_target": True,
        "schema_complete_primary_capture": True,
        "schema_complete_independent_capture": True,
        "candidate_profile_artifact_capture": True,
        "full_admissibility_capture": True,
        "solver_imported": False,
        "solver_calls": 0,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
    }


def execute_physical_schedule(capability: TargetExecutionCapability) -> dict[str, Any]:
    """Execute the immutable CP01R1 schedule only after a later valid capability.

    A timeout consumes no retry: the affected seed is blocked at that entry and all
    higher mesh levels for that seed are recorded as skipped. Other seeds continue
    in the immutable order if total budget remains. No adaptive insertion, fallback,
    random restart, parameter substitution or silent retry is available.
    """
    _validate_capability(capability)
    payload = frozen_payload()
    validate_schedule_against_sources()
    validate_backend_hashes()

    primary = _dynamic_import(PRIMARY_PATH, "ulsh_wp2h_primary_cp01r1")
    independent = _dynamic_import(INDEPENDENT_PATH, "ulsh_wp2h_independent_cp01r1")
    import numpy as np
    from scipy.optimize import least_squares

    primary_model = primary.model_from_payload(payload, control_a_F=False)
    primary_sector = primary.sector_from_payload(payload)
    independent_model = independent.model_from_payload(payload, control_a_F=False)
    independent_sector = independent.sector_from_payload(payload)
    if float(primary_model.a_F) != 0.25 or float(independent_model.a_F) != 0.25:
        raise TargetContractError("backend model construction changed a_F")

    prereg = load_json(PREREG_PATH)
    nonlinear = prereg["nonlinear_method"]
    thresholds = prereg["acceptance_thresholds"]
    limits = _resource_limits()
    start_monotonic = time.monotonic()
    execution_started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    entries: list[dict[str, Any]] = []
    continuation: dict[int, tuple[int, Any]] = {}
    internal_states: dict[tuple[int, int], Any] = {}
    internal_details: dict[tuple[int, int], dict[str, Any]] = {}
    independent_records: dict[tuple[int, int], dict[str, Any]] = {}
    blocked_seed: dict[int, str] = {}
    total_budget_exhausted = False

    for entry in build_schedule():
        seed_index = int(entry["seed_index"])
        node_count = int(entry["node_count"])
        if total_budget_exhausted:
            entries.append({
                **entry, "seed_id": BASE.seed_slot_id(seed_index),
                "status": "SKIPPED_TOTAL_WALL_CLOCK_BUDGET_EXHAUSTED",
                "failure": "TOTAL_WALL_CLOCK_BUDGET_EXHAUSTED",
                "newton_history": [],
            })
            continue
        if seed_index in blocked_seed:
            entries.append({
                **entry, "seed_id": BASE.seed_slot_id(seed_index),
                "status": "SKIPPED_AFTER_STAGE_TIMEOUT_NO_RETRY",
                "failure": blocked_seed[seed_index],
                "newton_history": [],
            })
            continue

        elapsed_total = time.monotonic() - start_monotonic
        remaining_total = float(limits["total"]) - elapsed_total
        if remaining_total <= 0.0:
            total_budget_exhausted = True
            entries.append({
                **entry, "seed_id": BASE.seed_slot_id(seed_index),
                "status": "SKIPPED_TOTAL_WALL_CLOCK_BUDGET_EXHAUSTED",
                "failure": "TOTAL_WALL_CLOCK_BUDGET_EXHAUSTED",
                "newton_history": [],
            })
            continue
        allowed_stage = min(float(limits["stage"]), remaining_total)
        stage_started = time.monotonic()

        try:
            with stage_wall_clock_limit(allowed_stage, str(entry["entry_id"])):
                if seed_index in continuation:
                    old_n, old_state = continuation[seed_index]
                    initial = BASE._prolongate_state(primary, old_state, old_n, node_count)
                else:
                    initial = primary.seven_seeds(node_count)[seed_index]

                primary_result = primary.damped_newton(
                    initial,
                    node_count,
                    primary_model,
                    primary_sector,
                    maximum_iterations=int(nonlinear["maximum_newton_iterations_per_mesh"]),
                    maximum_backtracking_steps=int(nonlinear["maximum_backtracking_steps"]),
                    armijo_parameter=float(nonlinear["armijo_parameter"]),
                    minimum_step_fraction=float(nonlinear["minimum_step_fraction"]),
                    trust_radius_initial=float(nonlinear["trust_region_initial_radius"]),
                    trust_radius_minimum=float(nonlinear["trust_region_minimum_radius"]),
                    residual_tolerance=float(thresholds["bulk_residual_max"]),
                    stagnation_window_iterations=int(nonlinear["stagnation_window_iterations"]),
                    stagnation_relative_improvement_floor=float(nonlinear["stagnation_relative_improvement_floor"]),
                )
                primary_state = np.asarray(primary_result["state"], dtype=float)
                _, primary_detail = primary.residual(primary_state, node_count, primary_model, primary_sector)
                bulk_vector = np.concatenate([
                    *primary_detail["north"].residual_blocks,
                    *primary_detail["south"].residual_blocks,
                ])
                bulk_inf = float(np.max(np.abs(bulk_vector)))
                boundary = np.asarray(primary_detail["boundary"], dtype=float)
                boundary_inf = float(np.max(np.abs(boundary)))
                constraint_profile = {
                    "north": np.asarray(primary_detail["north"].constraint, dtype=float).tolist(),
                    "south": np.asarray(primary_detail["south"].constraint, dtype=float).tolist(),
                }
                constraint_inf = float(max(
                    np.max(np.abs(primary_detail["north"].constraint)),
                    np.max(np.abs(primary_detail["south"].constraint)),
                ))
                primary_candidate = bool(
                    primary_result.get("converged")
                    and bulk_inf <= float(thresholds["bulk_residual_max"])
                    and boundary_inf <= float(thresholds["boundary_residual_max"])
                )
                diagnostic = _diagnostic_jacobian(
                    primary, primary_state, node_count, primary_model, primary_sector
                )

                independent_record: dict[str, Any] | None = None
                if primary_candidate:
                    _regions, shooting_initial = primary.unpack_state(primary_state, node_count)
                    shooting_initial = np.asarray(shooting_initial, dtype=float)
                    sample_count = max(257, 4 * node_count + 1)

                    def independent_residual(vector):
                        values, _ = independent.shooting_residual(
                            vector, independent_model, independent_sector,
                            epsilon=1.0e-6, sample_count=sample_count,
                        )
                        return values

                    independent_result = least_squares(
                        independent_residual,
                        shooting_initial,
                        jac=lambda x: independent.centered_fd_jacobian(
                            independent_residual, x, relative_step=1.0e-6
                        ),
                        method="trf",
                        max_nfev=int(nonlinear["maximum_newton_iterations_per_mesh"]),
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
                    candidate_distance = _independent_profile_distance(
                        primary_detail, shooting_initial, independent_detail, independent_result.x
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

                if primary_candidate:
                    continuation[seed_index] = (node_count, primary_state.copy())
                    internal_states[(seed_index, node_count)] = primary_state.copy()
                    internal_details[(seed_index, node_count)] = primary_detail

                entries.append({
                    **entry,
                    "seed_id": BASE.seed_slot_id(seed_index),
                    "status": "COMPLETED",
                    "primary": {
                        "converged": bool(primary_result.get("converged")),
                        "candidate_under_local_residual_gate": primary_candidate,
                        "failure": primary_result.get("failure"),
                    },
                    "failure": primary_result.get("failure"),
                    "bulk_residual_max": bulk_inf,
                    "boundary_residual_max": boundary_inf,
                    "all_eight_boundary_residuals": {
                        name: float(value) for name, value in zip(BOUNDARY_ORDER, boundary)
                    },
                    "rr_constraint_profile": constraint_profile,
                    "constraint_max": constraint_inf,
                    "diagnostic": _to_builtin(diagnostic),
                    "newton_history": _to_builtin(primary_result.get("history", [])),
                    "independent": independent_record,
                    "elapsed_wall_clock_seconds": time.monotonic() - stage_started,
                })
        except StageTimeoutError as exc:
            blocked_seed[seed_index] = "STAGE_TIMEOUT_NO_RETRY"
            entries.append({
                **entry,
                "seed_id": BASE.seed_slot_id(seed_index),
                "status": "TIMED_OUT_NO_RETRY",
                "failure": "STAGE_TIMEOUT_NO_RETRY",
                "timeout_message": str(exc),
                "newton_history": [],
                "elapsed_wall_clock_seconds": time.monotonic() - stage_started,
            })

        if time.monotonic() - start_monotonic >= float(limits["total"]):
            total_budget_exhausted = True

    finalized = _finalize(
        entries, internal_states, internal_details, independent_records,
        primary, primary_model, primary_sector, thresholds,
    )
    execution_elapsed = time.monotonic() - start_monotonic
    return {
        "run_id": RUN_ID,
        "frozen_input_sha256": FROZEN_PAYLOAD_SHA256,
        "schedule_sha256": schedule_sha256(),
        "planned_schedule_entries": PLANNED_ENTRY_COUNT,
        "execution_started_utc": execution_started_utc,
        "execution_elapsed_wall_clock_seconds": execution_elapsed,
        "per_stage_timeout_seconds": limits["stage"],
        "total_timeout_seconds": limits["total"],
        "matrix_entries": entries,
        "stage_timeout_count": sum(record.get("status") == "TIMED_OUT_NO_RETRY" for record in entries),
        "total_budget_exhausted": total_budget_exhausted,
        **finalized,
        "forbidden_inferences": FORBIDDEN_INFERENCES,
        "schema_complete_capture": True,
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    print(json.dumps(audit_target(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
