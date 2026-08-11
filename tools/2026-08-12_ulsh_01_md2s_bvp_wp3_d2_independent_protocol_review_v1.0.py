#!/usr/bin/env python3
"""Independent protocol review for ULSH-01 / WP3-D2 CP01R2 implementation.

Stdlib-only by design. It does not import any physical numerical backend and it
does not execute CP01R2. It independently checks the D1->D2 protocol mapping,
uses analytic synthetic systems to test the intended scaling/trust geometry,
and verifies the hard physical-execution firewall.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D2_CP01R2ImplementationContract_v1.0.json"
D1 = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D1_CP01R1FailureDiagnosis_CP01R2Protocol_v1.0.json"
IMPLEMENTATION = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d2_cp01r2_etrn_v1.0.py"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"top-level object required: {path}")
    return value


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _load_implementation():
    spec = importlib.util.spec_from_file_location("ulsh_wp3_d2_etrn_review", IMPLEMENTATION)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import D2 implementation")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analytic_scaled_diagonal_probe() -> dict[str, float]:
    """Independent closed-form probe for J=diag(1e6,1e-6)."""
    j1, j2 = 1.0e6, 1.0e-6
    c1, c2 = abs(j1), abs(j2)
    jc1, jc2 = j1 / c1, j2 / c2
    row1, row2 = 1.0 / abs(jc1), 1.0 / abs(jc2)
    a1, a2 = row1 * jc1, row2 * jc2
    raw_condition = abs(j1 / j2)
    scaled_condition = abs(a1 / a2)
    return {
        "column_scale_1": c1,
        "column_scale_2": c2,
        "scaled_diag_1": a1,
        "scaled_diag_2": a2,
        "raw_condition": raw_condition,
        "scaled_condition": scaled_condition,
    }


def analytic_clipped_progress_probe() -> dict[str, float]:
    """1D linear model: 10 -> 9 residual is only 10% drop but rho=1."""
    r = 10.0
    J = 1.0
    delta = 1.0
    full_step = -10.0
    clipped_step = math.copysign(delta, full_step)
    trial = r + J * clipped_step
    current_phi = 0.5 * r * r
    trial_phi = 0.5 * trial * trial
    predicted = r + J * clipped_step
    predicted_phi = 0.5 * predicted * predicted
    rho = (current_phi - trial_phi) / (current_phi - predicted_phi)
    relative_residual_drop = (r - abs(trial)) / r
    return {
        "rho": rho,
        "relative_residual_drop": relative_residual_drop,
        "scaled_step_norm": abs(clipped_step),
        "delta": delta,
    }


def review() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    d1 = load_json(D1)
    source = IMPLEMENTATION.read_text(encoding="utf-8")

    findings: dict[str, dict[str, Any]] = {}

    # IR01: exact protocol fidelity.
    bound = contract["source_bindings"]
    for key, binding in bound.items():
        observed = git_blob_sha1(ROOT / binding["path"])
        if observed != binding["git_blob_sha1"]:
            raise RuntimeError(f"source binding drift: {key}: {observed}")
    d1_design = d1["cp01r2_protocol_design"]
    impl = contract["etrn01_implementation"]
    assert d1_design["run_id"] == contract["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2"
    assert d1_design["primary_nonlinear_method"]["maximum_iterations_per_mesh"] == impl["maximum_iterations_per_mesh"] == 120
    assert d1_design["primary_nonlinear_method"]["trust_radius_maximum"] == impl["trust_radius_maximum"] == 64.0
    assert contract["physical_freeze"]["planned_entry_count"] == 35
    findings["IR01_PROTOCOL_FIDELITY"] = {"status": "PASS", "interpretation": "D1 numerical design and all physical freezes are preserved."}

    # IR02: independent synthetic geometry checks.
    diag = analytic_scaled_diagonal_probe()
    if not (diag["raw_condition"] >= 0.999e12 and abs(diag["scaled_condition"] - 1.0) < 1.0e-15):
        raise RuntimeError("analytic scaling probe failed")
    clipped = analytic_clipped_progress_probe()
    if not (abs(clipped["rho"] - 1.0) < 1.0e-15 and 0.09 < clipped["relative_residual_drop"] < 0.11):
        raise RuntimeError("analytic clipped-progress probe failed")
    module = _load_implementation()
    if module.radius_update(clipped["delta"], clipped["rho"], clipped["scaled_step_norm"]) != 2.0:
        raise RuntimeError("implementation fails high-quality clipped-progress expansion")
    findings["IR02_SYNTHETIC_SCALING_AND_TRUST_RADIUS"] = {
        "status": "PASS",
        "raw_condition_probe": diag["raw_condition"],
        "scaled_condition_probe": diag["scaled_condition"],
        "clipped_probe_residual_drop_fraction": clipped["relative_residual_drop"],
        "clipped_probe_rho": clipped["rho"],
        "interpretation": "ETRN geometry can expand after a high-quality clipped step without requiring a 75% one-step residual collapse."
    }

    # IR03: scaling is absent from acceptance merit/gates.
    required_acceptance_fragments = (
        'trial_inf < residual_inf',
        'rho >= RHO_ACCEPT_MIN',
        'admissible_fn(trial_state)',
        '"acceptance_merit": "ORIGINAL_UNSCALED_RESIDUAL_INFINITY_NORM"',
        'predicted = r + J @ dx',
    )
    if not all(fragment in source for fragment in required_acceptance_fragments):
        raise RuntimeError("original-residual acceptance firewall source mapping incomplete")
    findings["IR03_ORIGINAL_RESIDUAL_ACCEPTANCE_FIREWALL"] = {"status": "PASS", "interpretation": "Equilibration is linear-solve preconditioning only."}

    # IR04: deterministic progress-continuation semantics.
    if not module.progress_continuation_eligible(initial=1.0, final=0.90, finite=True, admissible=True, timed_out=False):
        raise RuntimeError("continuation should accept exact 10% progress")
    if module.progress_continuation_eligible(initial=1.0, final=0.9000001, finite=True, admissible=True, timed_out=False):
        raise RuntimeError("continuation threshold relaxed")
    if module.progress_continuation_eligible(initial=1.0, final=0.5, finite=True, admissible=False, timed_out=False):
        raise RuntimeError("inadmissible continuation accepted")
    schedule = module.build_schedule()
    if len(schedule) != 35 or [row["seed_index"] for row in schedule[::5]] != list(range(7)):
        raise RuntimeError("schedule determinism drift")
    findings["IR04_PROGRESS_CONTINUATION_DETERMINISM"] = {"status": "PASS", "interpretation": "No random restart, adaptive mesh insertion, parameter loading or homotopy is introduced."}

    # IR05: raw and scaled diagnostics are both implementation outputs/history.
    required_diag_fragments = (
        '"raw_rank"', '"raw_condition_estimate"', '"raw_singular_values"',
        '"scaled_rank"', '"scaled_condition_estimate"', '"scaled_singular_values"',
    )
    if not all(fragment in source for fragment in required_diag_fragments):
        raise RuntimeError("raw/scaled diagnostic capture incomplete")
    findings["IR05_RAW_AND_SCALED_DIAGNOSTIC_CAPTURE"] = {"status": "PASS", "interpretation": "Scaled diagnostics cannot be substituted for raw physical-equation diagnostics."}

    # IR06: hard no-execution firewall and no physical backend binding.
    forbidden_physical_fragments = (
        "background_3c_primary_kernel", "PRIMARY_PATH", "INDEPENDENT_PATH",
        "least_squares", "scipy.optimize", "execute_physical_schedule(capability",
    )
    if any(fragment in source for fragment in forbidden_physical_fragments):
        raise RuntimeError("D2 implementation unexpectedly binds a physical backend")
    denied = False
    try:
        module.execute_physical_schedule()
    except module.PhysicalExecutionDenied:
        denied = True
    if not denied:
        raise RuntimeError("physical execution firewall did not fail closed")
    findings["IR06_NO_PHYSICAL_EXECUTION_CAPABILITY"] = {"status": "PASS", "interpretation": "WP3-D2 can run only generic/synthetic method tests; CP01R2 physical execution is impossible from this artifact."}

    # IR07: no authorization artifacts exist.
    releases = list(ROOT.glob("registry/*CP01R2*ReleaseAuthorization*.json"))
    grants = list(ROOT.glob("registry/*CP01R2*ExecutionGrant*.json"))
    if releases or grants:
        raise RuntimeError("forbidden CP01R2 release/grant artifact present")
    findings["IR07_NO_RELEASE_OR_GRANT_ARTIFACT"] = {"status": "PASS", "interpretation": "No execution authority exists."}

    if any(item["status"] != "PASS" for item in findings.values()):
        raise RuntimeError("independent review contains a non-pass gate")

    return {
        "status": "PASS_WP3_D2_INDEPENDENT_PROTOCOL_REVIEW_NO_EXECUTION",
        "run_id": contract["run_id"],
        "review_gates": findings,
        "implementation_clarifications_review": {
            "backtracked_rho_denominator": "ACCEPTED_NUMERICAL_SEMANTIC_CLARIFICATION_NO_PHYSICS_CHANGE",
            "all_trials_rejected": "ACCEPTED_CONSERVATIVE_FAIL_CLOSED_CONTROL_FLOW_NO_PHYSICS_CHANGE"
        },
        "physical_solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
        "next_allowed_action": contract["next_if_review_passes"],
    }


def main() -> int:
    print(json.dumps(review(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
