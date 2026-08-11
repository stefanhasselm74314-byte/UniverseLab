#!/usr/bin/env python3
"""ULSH-01 / WP3-D2 CP01R2 ETRN-01 implementation-review kernel.

This module implements the numerical method designed in WP3-D1 without binding
it to the physical CP01R2 backend. Direct physical execution is deliberately
impossible in WP3-D2: execute_physical_schedule() always fails closed.

The generic ETRN-01 routines may be exercised only on synthetic systems in CI.
No CP01R2 release authorization or execution grant is created or consumed here.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
D1_PROTOCOL = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D1_CP01R1FailureDiagnosis_CP01R2Protocol_v1.0.json"
RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2"
NODE_COUNTS = (24, 32, 48, 64, 96)
SEED_ORDER = tuple(range(7))
PLANNED_ENTRY_COUNT = 35
SVD_RELATIVE_CUTOFF = 1.0e-12
EQUILIBRATION_FLOOR = 1.0e-12
RHO_ACCEPT_MIN = 0.10
RHO_SHRINK = 0.25
RHO_EXPAND = 0.75
BOUNDARY_ACTIVITY_FRACTION = 0.80
TRUST_RADIUS_INITIAL = 1.0
TRUST_RADIUS_MINIMUM = 1.0e-12
TRUST_RADIUS_MAXIMUM = 64.0
MAX_BACKTRACKS = 20
MAX_ITERATIONS = 120
STAGNATION_WINDOW = 12
STAGNATION_FLOOR = 1.0e-4


class D2ImplementationError(RuntimeError):
    pass


class PhysicalExecutionDenied(D2ImplementationError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise D2ImplementationError(f"top-level object required: {path}")
    return value


def build_schedule() -> list[dict[str, Any]]:
    schedule: list[dict[str, Any]] = []
    ordinal = 0
    for seed_index in SEED_ORDER:
        previous: str | None = None
        for node_count in NODE_COUNTS:
            ordinal += 1
            entry_id = f"CP01R2-E{ordinal:02d}-S{seed_index}-N{node_count}"
            schedule.append({
                "ordinal": ordinal,
                "entry_id": entry_id,
                "seed_index": seed_index,
                "node_count": node_count,
                "continuation_from_entry_id": previous,
            })
            previous = entry_id
    if len(schedule) != PLANNED_ENTRY_COUNT:
        raise D2ImplementationError("CP01R2 schedule cardinality drift")
    return schedule


def radius_update(delta: float, rho: float, scaled_step_norm: float) -> float:
    if not (math.isfinite(delta) and delta > 0.0):
        raise D2ImplementationError("trust radius must be finite and positive")
    if rho < RHO_SHRINK:
        return max(TRUST_RADIUS_MINIMUM, RHO_SHRINK * delta)
    if rho > RHO_EXPAND and scaled_step_norm >= BOUNDARY_ACTIVITY_FRACTION * delta:
        return min(TRUST_RADIUS_MAXIMUM, 2.0 * delta)
    return delta


def progress_continuation_eligible(*, initial: float, final: float, finite: bool, admissible: bool, timed_out: bool) -> bool:
    return bool(
        finite
        and admissible
        and not timed_out
        and math.isfinite(initial)
        and math.isfinite(final)
        and initial >= 0.0
        and final <= 0.90 * initial
    )


def backtracking_factors() -> tuple[float, ...]:
    return tuple(0.5**index for index in range(MAX_BACKTRACKS + 1))


def _rank_condition(singular_values: Any, *, relative_cutoff: float = SVD_RELATIVE_CUTOFF) -> tuple[int, float, float]:
    import numpy as np
    values = np.asarray(singular_values, dtype=float)
    if values.ndim != 1:
        raise D2ImplementationError("singular value array must be one-dimensional")
    if values.size == 0:
        return 0, math.inf, 0.0
    sigma_max = float(values[0])
    cutoff = relative_cutoff * sigma_max if sigma_max > 0.0 else 0.0
    rank = int(np.count_nonzero(values > cutoff)) if sigma_max > 0.0 else 0
    sigma_min = float(values[-1])
    condition = math.inf if sigma_min <= 0.0 else sigma_max / sigma_min
    return rank, condition, cutoff


def equilibrated_svd_step(jacobian: Any, residual: Any, delta: float) -> dict[str, Any]:
    """Return one ETRN-01 trust-region step for a supplied synthetic/generic system.

    Column and row scaling affect only the linear solve. The returned dx is a
    step in the original variables and all acceptance logic remains defined on
    the unscaled residual equations.
    """
    import numpy as np

    J = np.asarray(jacobian, dtype=float)
    r = np.asarray(residual, dtype=float)
    if J.ndim != 2 or r.ndim != 1 or J.shape[0] != r.size:
        raise D2ImplementationError("incompatible Jacobian/residual shapes")
    if not np.all(np.isfinite(J)) or not np.all(np.isfinite(r)):
        raise D2ImplementationError("nonfinite Jacobian/residual")
    if not (math.isfinite(delta) and delta > 0.0):
        raise D2ImplementationError("delta must be finite and positive")

    column_norms = np.linalg.norm(J, axis=0)
    column_scale = np.maximum(column_norms, EQUILIBRATION_FLOOR)
    J_column = J / column_scale[None, :]
    row_norms = np.linalg.norm(J_column, axis=1)
    row_scale = 1.0 / np.maximum(row_norms, EQUILIBRATION_FLOOR)
    A = row_scale[:, None] * J_column
    b = -(row_scale * r)

    U, scaled_singular, Vt = np.linalg.svd(A, full_matrices=False)
    scaled_rank, scaled_condition, scaled_cutoff = _rank_condition(scaled_singular)
    coefficients = U.T @ b
    inverse = np.zeros_like(scaled_singular)
    active = scaled_singular > scaled_cutoff
    inverse[active] = 1.0 / scaled_singular[active]
    z_unclipped = Vt.T @ (inverse * coefficients)
    z_unclipped_norm = float(np.linalg.norm(z_unclipped))
    if z_unclipped_norm > delta:
        z = z_unclipped * (delta / z_unclipped_norm)
    else:
        z = z_unclipped
    scaled_step_norm = float(np.linalg.norm(z))
    dx = z / column_scale

    raw_singular = np.linalg.svd(J, compute_uv=False)
    raw_rank, raw_condition, raw_cutoff = _rank_condition(raw_singular)
    return {
        "dx": dx,
        "z": z,
        "z_unclipped": z_unclipped,
        "scaled_step_norm": scaled_step_norm,
        "unclipped_scaled_step_norm": z_unclipped_norm,
        "trust_radius_active": bool(z_unclipped_norm > delta),
        "column_scale": column_scale,
        "row_scale": row_scale,
        "raw_rank": raw_rank,
        "raw_condition_estimate": raw_condition,
        "raw_singular_values": raw_singular,
        "raw_rank_cutoff": raw_cutoff,
        "scaled_rank": scaled_rank,
        "scaled_condition_estimate": scaled_condition,
        "scaled_singular_values": scaled_singular,
        "scaled_rank_cutoff": scaled_cutoff,
        "interpretation": "LINEAR_SOLVE_PRECONDITIONING_ONLY_NOT_AN_ACCEPTANCE_GATE",
    }


def model_reduction_ratio(current_residual: Any, trial_residual: Any, jacobian: Any, trial_step: Any) -> dict[str, float | bool]:
    """Evaluate rho using the actual backtracked trial step in original equations."""
    import numpy as np

    r = np.asarray(current_residual, dtype=float)
    rt = np.asarray(trial_residual, dtype=float)
    J = np.asarray(jacobian, dtype=float)
    dx = np.asarray(trial_step, dtype=float)
    current_phi = 0.5 * float(r @ r)
    trial_phi = 0.5 * float(rt @ rt)
    predicted = r + J @ dx
    predicted_phi = 0.5 * float(predicted @ predicted)
    denominator = current_phi - predicted_phi
    actual = current_phi - trial_phi
    if not math.isfinite(denominator) or denominator <= 0.0:
        return {"rho": -math.inf, "predicted_reduction": denominator, "actual_reduction": actual, "denominator_positive": False}
    return {"rho": actual / denominator, "predicted_reduction": denominator, "actual_reduction": actual, "denominator_positive": True}


def etrn_solve_generic(
    initial: Any,
    residual_fn: Callable[[Any], Any],
    jacobian_fn: Callable[[Any], Any],
    admissible_fn: Callable[[Any], bool],
    *,
    residual_tolerance: float = 1.0e-10,
    maximum_iterations: int = MAX_ITERATIONS,
) -> dict[str, Any]:
    """Generic ETRN-01 implementation for synthetic implementation-review tests.

    This function has no knowledge of the CP01R2 physical equations, seeds,
    source paths, transaction capability, or release/grant protocol.
    """
    import numpy as np

    state = np.asarray(initial, dtype=float).copy()
    delta = TRUST_RADIUS_INITIAL
    history: list[dict[str, Any]] = []
    accepted_norms: list[float] = []

    for iteration in range(maximum_iterations):
        residual = np.asarray(residual_fn(state), dtype=float)
        residual_inf = float(np.max(np.abs(residual))) if residual.size else 0.0
        if not np.all(np.isfinite(residual)):
            return {"converged": False, "failure": "NONFINITE_RESIDUAL", "state": state, "history": history}
        if residual_inf <= residual_tolerance:
            return {"converged": True, "state": state, "history": history, "residual_inf": residual_inf}

        J = np.asarray(jacobian_fn(state), dtype=float)
        step = equilibrated_svd_step(J, residual, delta)
        accepted = False
        accepted_factor = 0.0
        accepted_rho = -math.inf
        accepted_residual_inf = residual_inf
        accepted_scaled_norm = 0.0

        for factor in backtracking_factors():
            trial_dx = factor * step["dx"]
            trial_z = factor * step["z"]
            trial_state = state + trial_dx
            if not bool(admissible_fn(trial_state)):
                continue
            trial_residual = np.asarray(residual_fn(trial_state), dtype=float)
            if not np.all(np.isfinite(trial_residual)):
                continue
            trial_inf = float(np.max(np.abs(trial_residual))) if trial_residual.size else 0.0
            ratio = model_reduction_ratio(residual, trial_residual, J, trial_dx)
            rho = float(ratio["rho"])
            if bool(ratio["denominator_positive"]) and trial_inf < residual_inf and rho >= RHO_ACCEPT_MIN:
                state = trial_state
                accepted = True
                accepted_factor = factor
                accepted_rho = rho
                accepted_residual_inf = trial_inf
                accepted_scaled_norm = float(np.linalg.norm(trial_z))
                break

        row = {
            "iteration": iteration,
            "residual_inf": residual_inf,
            "trial_residual_inf": accepted_residual_inf,
            "trust_radius_before": delta,
            "trust_radius_active": step["trust_radius_active"],
            "unclipped_scaled_step_norm": step["unclipped_scaled_step_norm"],
            "accepted_scaled_step_norm": accepted_scaled_norm,
            "accepted": accepted,
            "accepted_factor": accepted_factor,
            "rho": accepted_rho,
            "raw_rank": step["raw_rank"],
            "raw_condition_estimate": step["raw_condition_estimate"],
            "scaled_rank": step["scaled_rank"],
            "scaled_condition_estimate": step["scaled_condition_estimate"],
            "acceptance_merit": "ORIGINAL_UNSCALED_RESIDUAL_INFINITY_NORM",
        }

        if accepted:
            delta = radius_update(delta, accepted_rho, accepted_scaled_norm)
            accepted_norms.append(accepted_residual_inf)
            if len(accepted_norms) > STAGNATION_WINDOW:
                accepted_norms.pop(0)
            if len(accepted_norms) == STAGNATION_WINDOW:
                improvement = (accepted_norms[0] - accepted_norms[-1]) / max(accepted_norms[0], 1.0e-300)
                if improvement < STAGNATION_FLOOR:
                    row["trust_radius_after"] = delta
                    history.append(row)
                    return {"converged": False, "failure": "STAGNATION", "state": state, "history": history}
        else:
            # WP3-D2 deterministic clarification for the D1-unspecified all-trials-
            # rejected case: shrink once, never accept a non-improving step, and
            # fail closed once the minimum radius is reached.
            new_delta = max(TRUST_RADIUS_MINIMUM, RHO_SHRINK * delta)
            if new_delta <= TRUST_RADIUS_MINIMUM and delta <= TRUST_RADIUS_MINIMUM:
                row["trust_radius_after"] = new_delta
                history.append(row)
                return {"converged": False, "failure": "TRUST_RADIUS_BELOW_MINIMUM", "state": state, "history": history}
            delta = new_delta

        row["trust_radius_after"] = delta
        history.append(row)

    final_residual = np.asarray(residual_fn(state), dtype=float)
    return {
        "converged": False,
        "failure": "MAXIMUM_ITERATIONS",
        "state": state,
        "history": history,
        "residual_inf": float(np.max(np.abs(final_residual))) if final_residual.size else 0.0,
    }


def execute_physical_schedule(*_args: Any, **_kwargs: Any) -> None:
    raise PhysicalExecutionDenied(
        "WP3-D2 is implementation/review only; CP01R2 physical execution requires a later separately reviewed release transaction"
    )


def audit() -> dict[str, Any]:
    protocol = load_json(D1_PROTOCOL)
    design = protocol["cp01r2_protocol_design"]
    method = design["primary_nonlinear_method"]
    if protocol["status"] != "PASS_WP3_D1_FAILURE_MODE_DIAGNOSIS_CP01R2_PROTOCOL_DESIGNED_NO_EXECUTION":
        raise D2ImplementationError("D1 protocol status drift")
    if design["run_id"] != RUN_ID or design["state"] != "DESIGNED_NOT_AUTHORIZED_NOT_EXECUTED":
        raise D2ImplementationError("CP01R2 design binding drift")
    if tuple(design["seed_and_mesh_freeze"]["node_counts"]) != NODE_COUNTS:
        raise D2ImplementationError("CP01R2 mesh freeze drift")
    if tuple(design["seed_and_mesh_freeze"]["seed_order"]) != SEED_ORDER:
        raise D2ImplementationError("CP01R2 seed order drift")
    if method["maximum_iterations_per_mesh"] != MAX_ITERATIONS:
        raise D2ImplementationError("maximum-iteration design drift")
    if method["trust_radius_initial"] != TRUST_RADIUS_INITIAL or method["trust_radius_maximum"] != TRUST_RADIUS_MAXIMUM:
        raise D2ImplementationError("trust-radius design drift")
    if method["stagnation_window_iterations"] != STAGNATION_WINDOW or method["stagnation_relative_improvement_floor"] != STAGNATION_FLOOR:
        raise D2ImplementationError("stagnation design drift")
    if radius_update(1.0, 0.90, 1.0) != 2.0:
        raise D2ImplementationError("ETRN expansion rule drift")
    if not progress_continuation_eligible(initial=1.0, final=0.90, finite=True, admissible=True, timed_out=False):
        raise D2ImplementationError("progress-continuation design drift")
    if len(build_schedule()) != PLANNED_ENTRY_COUNT:
        raise D2ImplementationError("schedule drift")

    forbidden_release = list(ROOT.glob("registry/*CP01R2*ReleaseAuthorization*.json"))
    forbidden_grant = list(ROOT.glob("registry/*CP01R2*ExecutionGrant*.json"))
    if forbidden_release or forbidden_grant:
        raise D2ImplementationError("CP01R2 release/grant forbidden during WP3-D2")

    denied = False
    try:
        execute_physical_schedule()
    except PhysicalExecutionDenied:
        denied = True
    if not denied:
        raise D2ImplementationError("physical execution firewall failed")

    return {
        "status": "PASS_WP3_D2_ETRN01_IMPLEMENTATION_AUDIT_NO_EXECUTION",
        "run_id": RUN_ID,
        "method": "ETRN-01_EQUILIBRATED_TRUST_REGION_NEWTON",
        "schedule_entries": PLANNED_ENTRY_COUNT,
        "raw_and_scaled_rank_condition_capture": True,
        "original_residual_acceptance_firewall": True,
        "progress_continuation_implemented": True,
        "all_trials_rejected_policy": "DETERMINISTIC_SINGLE_RADIUS_SHRINK_FAIL_CLOSED_AT_MINIMUM",
        "physical_backend_imported": False,
        "physical_solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    print(json.dumps(audit(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
