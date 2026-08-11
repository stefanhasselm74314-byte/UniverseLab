#!/usr/bin/env python3
"""ULSH-01 / WP3-D1 CP01R1 failure diagnosis audit.

Stdlib-only. This tool does not import numerical backends, does not create a
release/grant, and cannot execute CP01R1 or CP01R2. It verifies the immutable
CP01R1 diagnostic summary against frozen source behavior and the designed
CP01R2 no-execution protocol.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D1_CP01R1FailureDiagnosis_CP01R2Protocol_v1.0.json"
MATRIX = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D1_CP01R1FailureDiagnosticMatrix_v1.0.json"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"top-level object required: {path}")
    return value


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def r2_radius_update(delta: float, rho: float, scaled_step_norm: float) -> float:
    """Pure protocol probe; not a solver implementation."""
    if rho < 0.25:
        return max(1.0e-12, 0.25 * delta)
    if rho > 0.75 and scaled_step_norm >= 0.8 * delta:
        return min(64.0, 2.0 * delta)
    return delta


def progress_continuation_eligible(*, initial: float, final: float, finite: bool, admissible: bool, timed_out: bool) -> bool:
    return bool(finite and admissible and not timed_out and final <= 0.90 * initial)


def audit() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    matrix = load_json(MATRIX)

    if contract["status"] != "PASS_WP3_D1_FAILURE_MODE_DIAGNOSIS_CP01R2_PROTOCOL_DESIGNED_NO_EXECUTION":
        raise RuntimeError("unexpected D1 status")
    if contract["governance"]["physical_solve_authorized"] is not False or contract["governance"]["physical_solve_executed"] is not False:
        raise RuntimeError("D1 must remain no-execution")
    if contract["cp01r2_protocol_design"]["state"] != "DESIGNED_NOT_AUTHORIZED_NOT_EXECUTED":
        raise RuntimeError("CP01R2 state drift")

    for name, binding in contract["source_bindings"].items():
        path = ROOT / binding["path"]
        observed = git_blob_sha1(path)
        if observed != binding["git_blob_sha1"]:
            raise RuntimeError(f"source binding drift: {name}: {observed}")

    if matrix["source_result_sha256"] != "8562ba77cb0aeda87aceee3b7be301c06e948070beebc8916769c38d99b45ec8":
        raise RuntimeError("CP01R1 result binding drift")
    agg = matrix["aggregate"]
    if agg["entry_count"] != 35 or len(matrix["entries"]) != 35:
        raise RuntimeError("diagnostic matrix cardinality drift")
    if agg["total_newton_iterations"] != 1967 or agg["trust_cap_active_iterations"] != 1967 or agg["trust_cap_active_fraction"] != 1.0:
        raise RuntimeError("trust-cap diagnosis drift")
    if agg["max_iteration_entries"] != 30 or agg["max_iteration_rejected_iterations"] != 0:
        raise RuntimeError("MAXIMUM_ITERATIONS diagnosis drift")
    if agg["trust_radius_failure_entries"] != 4 or agg["rrqr_failure_entries"] != 1:
        raise RuntimeError("terminal failure inventory drift")
    lo, hi = agg["n96_R4D_abs_range"]
    if not (1.1252 < lo < 1.1254 and 1.4088 < hi < 1.4090):
        raise RuntimeError("N96 R_4D range drift")
    conditions = [agg["condition_by_node_count"][str(n)]["condition_median"] for n in (24, 32, 48, 64, 96)]
    if conditions != sorted(conditions) or not all(right > left for left, right in zip(conditions, conditions[1:])):
        raise RuntimeError("fine-mesh conditioning trend drift")

    primary = (ROOT / contract["source_bindings"]["cp01r1_primary_kernel_base"]["path"]).read_text(encoding="utf-8")
    target = (ROOT / contract["source_bindings"]["cp01r1_target_h1"]["path"]).read_text(encoding="utf-8")
    seed_adapter = (ROOT / contract["source_bindings"]["cp01r1_primary_seed_adapter"]["path"]).read_text(encoding="utf-8")
    required_primary_fragments = (
        "if raw_step_norm > trust_radius:",
        "candidate_norm < 0.25 * current_norm",
        "trust_radius = min(2.0 * trust_radius, 4.0 * trust_radius_initial)",
    )
    if not all(fragment in primary for fragment in required_primary_fragments):
        raise RuntimeError("CP01R1 trust-region source behavior drift")
    if "continuation[seed_index] =" not in target or "initial = primary.seven_seeds(node_count)[seed_index]" not in target:
        raise RuntimeError("CP01R1 continuation source behavior drift")
    if "SEED_AMPLITUDE_SCALE = 1.0 / 20.0" not in seed_adapter:
        raise RuntimeError("CP01R1 seed amplitude source behavior drift")

    r2 = contract["cp01r2_protocol_design"]
    if r2["physical_sector_freeze"]["acceptance_thresholds"] != "IDENTICAL_TO_CP01R1":
        raise RuntimeError("CP01R2 acceptance thresholds must not be relaxed")
    seed_mesh = r2["seed_and_mesh_freeze"]
    if any((seed_mesh["random_restarts"], seed_mesh["adaptive_mesh_insertion"], seed_mesh["parameter_scan"], seed_mesh["homotopy_or_parameter_loading"])):
        raise RuntimeError("CP01R2 causal-isolation freeze drift")
    if r2_radius_update(1.0, 0.90, 1.0) != 2.0:
        raise RuntimeError("designed R2 radius rule does not remove CP01R1 expansion starvation")
    if not progress_continuation_eligible(initial=1.6, final=1.3, finite=True, admissible=True, timed_out=False):
        raise RuntimeError("designed R2 progress-continuation rule drift")
    if progress_continuation_eligible(initial=1.6, final=1.55, finite=True, admissible=True, timed_out=False):
        raise RuntimeError("designed R2 progress-continuation threshold drift")

    forbidden_release = list(ROOT.glob("registry/*CP01R2*ReleaseAuthorization*.json"))
    forbidden_grant = list(ROOT.glob("registry/*CP01R2*ExecutionGrant*.json"))
    if forbidden_release or forbidden_grant:
        raise RuntimeError("CP01R2 release/grant must be absent during D1")

    return {
        "status": "PASS_WP3_D1_DIAGNOSIS_AUDIT_CP01R2_DESIGN_NO_EXECUTION",
        "run_reviewed": "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1",
        "cp01r1_entries": 35,
        "cp01r1_newton_iterations": 1967,
        "trust_cap_active_fraction": 1.0,
        "dominant_failure_hypothesis": "TRUST_REGION_CAP_STARVATION_PLUS_SCALE_GEOMETRY",
        "cp01r2_state": "DESIGNED_NOT_AUTHORIZED_NOT_EXECUTED",
        "solver_imports": 0,
        "solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    print(json.dumps(audit(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
