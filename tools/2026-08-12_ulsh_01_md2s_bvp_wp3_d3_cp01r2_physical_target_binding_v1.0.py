#!/usr/bin/env python3
"""ULSH-01 / WP3-D3 CP01R2 physical-target binding and release-readiness audit.

This module binds the already reviewed ETRN-01 method to the exact frozen M1
physical sources at the source-contract level only. It does NOT execute a
physical residual, initialize a nonlinear solve, issue a release authorization,
or create/consume a grant. Direct physical execution is fail-closed.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2"
RUN_INPUT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3_CP01R2RunInputFreeze_v1.0.json"
D1_PROTOCOL = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D1_CP01R1FailureDiagnosis_CP01R2Protocol_v1.0.json"
D2_CONTRACT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D2_CP01R2ImplementationContract_v1.0.json"
D2_REVIEW = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D2_CP01R2IndependentProtocolReview_v1.0.json"
D2_ETRN = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d2_cp01r2_etrn_v1.0.py"
CP01R1_RUN_INPUT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"
PREREG = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"
RESOURCE = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
PRIMARY_BASE = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.1.py"
SEED_ADAPTER = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py"
INDEPENDENT_BACKEND = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_independent_backend_v0.1.py"
CP01R1_TARGET = ROOT / "tools/2026-08-10_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.0.py"

EXPECTED_GIT_BLOBS = {
    D1_PROTOCOL: "7f89a61ace7a54182ade2cc97cb38558496e9f68",
    D2_CONTRACT: "fe6928a532da28510522fb034ae7a7573ffa0cb8",
    D2_REVIEW: "2734b120ffa9a481a092f87190605df24d02bcb0",
    D2_ETRN: "fd109330d44f504d89597c05f1dbfa638e0969bb",
    CP01R1_RUN_INPUT: "3547523a6524cb240399f4c0cbc3fdc0b128a0c0",
    PREREG: "9789101e0a168580b6906eb21edad5a5db2b64ce",
    RESOURCE: "954a9730d3fa34864df7168555912ebba2dd6c3d",
    PRIMARY_BASE: "d451be299d0ca93a7dc4587782675b7adab5cfd7",
    SEED_ADAPTER: "e232537ab80f099b0b3a914c509041c13825e950",
    CP01R1_TARGET: "ea02d02f61e8c072c1191577c1bf7660038ad516",
}
EXPECTED_RAW_SHA256 = {
    PRIMARY_BASE: "830d4b4fdd28c8888876125479df3542eeb3864d4328764feb96b5d34bd91599",
    SEED_ADAPTER: "8ce1c0eceed64245d091d4bed492f3cf2a9c8314f631a03045aaa9696fb11c92",
    INDEPENDENT_BACKEND: "a8afd7b548366acf9f5ac72e91bcf07372913cc21a8790d86d0a989a89f03e7b",
}
EXPECTED_RUN_PAYLOAD_SHA256 = "e8b8e82d2cb1472d91c387a40c8f84024c2549a3dcc2c897df5561f7bf721b36"
EXPECTED_SCHEDULE_SHA256 = "929f59d018cc511f36c98ef26a8614ed495fe699a067b1b33e6c5b53efaf8e0b"
NODE_COUNTS = (24, 32, 48, 64, 96)
SEED_ORDER = tuple(range(7))


class D3BindingError(RuntimeError):
    pass


class PhysicalExecutionDenied(D3BindingError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise D3BindingError(f"top-level JSON object required: {path}")
    return value


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def function_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


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
    return schedule


def schedule_sha256() -> str:
    return hashlib.sha256(canonical_json_bytes(build_schedule())).hexdigest()


def _verify_source_bindings() -> dict[str, Any]:
    observed_blobs: dict[str, str] = {}
    for path, expected in EXPECTED_GIT_BLOBS.items():
        observed = git_blob_sha1(path)
        if observed != expected:
            raise D3BindingError(f"source git-blob drift: {path}: {observed}")
        observed_blobs[str(path.relative_to(ROOT))] = observed
    observed_raw: dict[str, str] = {}
    for path, expected in EXPECTED_RAW_SHA256.items():
        observed = sha256_file(path)
        if observed != expected:
            raise D3BindingError(f"source raw SHA-256 drift: {path}: {observed}")
        observed_raw[str(path.relative_to(ROOT))] = observed
    return {"git_blob_sha1": observed_blobs, "raw_sha256": observed_raw}


def _verify_callable_surface() -> dict[str, list[str]]:
    primary_required = {
        "model_from_payload", "sector_from_payload", "chebyshev_lobatto",
        "unpack_state", "pack_state", "residual", "admissible",
        "complex_step_jacobian",
    }
    seed_required = {"seven_seeds"}
    independent_required = {
        "model_from_payload", "sector_from_payload", "shooting_residual",
        "centered_fd_jacobian",
    }
    etrn_required = {
        "equilibrated_svd_step", "model_reduction_ratio", "radius_update",
        "progress_continuation_eligible", "etrn_solve_generic",
    }
    surfaces = {
        "primary": function_names(PRIMARY_BASE),
        "seed_adapter": function_names(SEED_ADAPTER),
        "independent": function_names(INDEPENDENT_BACKEND),
        "etrn": function_names(D2_ETRN),
    }
    required = {
        "primary": primary_required,
        "seed_adapter": seed_required,
        "independent": independent_required,
        "etrn": etrn_required,
    }
    for name, needed in required.items():
        missing = needed - surfaces[name]
        if missing:
            raise D3BindingError(f"physical binding callable surface missing in {name}: {sorted(missing)}")
    return {name: sorted(required[name]) for name in required}


def physical_adapter_blueprint() -> dict[str, Any]:
    """Declarative future execution wiring. No backend is imported or called."""
    return {
        "primary_physics": {
            "model": "primary_base.model_from_payload(cp01r2_payload, control_a_F=False)",
            "sector": "primary_base.sector_from_payload(cp01r2_payload)",
            "residual_fn": "lambda x,N: primary_base.residual(x,N,model,sector)[0]",
            "detail_fn": "lambda x,N: primary_base.residual(x,N,model,sector)[1]",
            "jacobian_fn": "lambda x,N: primary_base.complex_step_jacobian(x,N,model,sector)",
            "admissible_fn": "lambda x,N: primary_base.admissible(x,N,rho_min=1e-4,ell_margin=1e-8)",
            "seed_fn": "seed_adapter.seven_seeds(N)[seed_index]",
            "prolongation": "same deterministic Lobatto interpolation semantics as CP01R1 target _prolongate_state",
        },
        "nonlinear_method": {
            "implementation": "WP3-D2 ETRN-01",
            "acceptance_merit": "ORIGINAL_UNSCALED_RESIDUAL_INFINITY_NORM",
            "scaling_effect_on_scientific_gates": "NONE",
            "maximum_iterations_per_mesh": 120,
            "progress_continuation": "terminal state only if finite/admissible/not timed out and final_inf <= 0.90*initial_inf",
        },
        "independent_backend": {
            "dispatch": "ONLY_AFTER_PRIMARY_LOCAL_ROOT_GATE",
            "implementation": "independent x-space shooting backend",
            "candidate_distance_threshold": 1e-7,
            "interpretation": "NUMERICAL_CROSSCHECK_ONLY_NOT_PHYSICAL_CONFIRMATION",
        },
        "qa_closure": {
            "bulk_residual_max": 1e-10,
            "boundary_residual_max": 1e-10,
            "rr_constraint_max": 1e-9,
            "required_successful_levels": [48, 64, 96],
            "fine_mesh_profile_difference_max": 1e-8,
            "fine_mesh_augmented_difference_max": 1e-9,
            "spectral_tail_max_at_N96": 1e-9,
            "condition_without_high_precision_max": 1e12,
            "higher_precision_audit": ">=80-bit residual re-evaluation for every otherwise passing candidate",
        },
    }


def audit() -> dict[str, Any]:
    run_input = load_json(RUN_INPUT)
    d1 = load_json(D1_PROTOCOL)
    d2 = load_json(D2_CONTRACT)
    d2_review = load_json(D2_REVIEW)
    cp01r1 = load_json(CP01R1_RUN_INPUT)
    prereg = load_json(PREREG)
    resource = load_json(RESOURCE)

    if run_input["status"] != "FROZEN_CP01R2_NOT_AUTHORIZED_NOT_EXECUTED":
        raise D3BindingError("CP01R2 run-input state drift")
    payload = run_input["frozen_run_payload"]
    if payload["run_id"] != RUN_ID:
        raise D3BindingError("CP01R2 run_id drift")
    observed_payload_hash = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    if observed_payload_hash != EXPECTED_RUN_PAYLOAD_SHA256 or run_input["frozen_run_payload_sha256"] != EXPECTED_RUN_PAYLOAD_SHA256:
        raise D3BindingError("CP01R2 frozen payload digest drift")
    if schedule_sha256() != EXPECTED_SCHEDULE_SHA256 or run_input["schedule_sha256"] != EXPECTED_SCHEDULE_SHA256:
        raise D3BindingError("CP01R2 schedule digest drift")

    old = cp01r1["frozen_run_payload"]
    for key in ("model_parameters_ordered", "dimensional_anchor", "topological_sector_ordered", "alpha_H", "seed_set_id", "seed_spec_sha256", "dependency_lock_path", "dependency_lock_sha256"):
        if payload[key] != old[key]:
            raise D3BindingError(f"physical identity drift relative to CP01R1: {key}")
    if payload["model_parameters_ordered"]["a_F"] != "1/4":
        raise D3BindingError("a_F must remain exactly 1/4")
    if tuple(payload["node_counts"]) != NODE_COUNTS or tuple(payload["seed_order"]) != SEED_ORDER:
        raise D3BindingError("seed/mesh freeze drift")

    if d1["status"] != "PASS_WP3_D1_FAILURE_MODE_DIAGNOSIS_CP01R2_PROTOCOL_DESIGNED_NO_EXECUTION":
        raise D3BindingError("D1 protocol status drift")
    if d2["implementation_state"] != "IMPLEMENTED_FOR_REVIEW_NOT_PHYSICALLY_BOUND_NOT_AUTHORIZED_NOT_EXECUTED":
        raise D3BindingError("D2 implementation state drift")
    if d2_review["review_status"] != "PASS_WP3_D2_INDEPENDENT_PROTOCOL_REVIEW_NO_EXECUTION":
        raise D3BindingError("D2 independent review not PASS")
    if not all(value == "PASS" for value in d2_review["review_gates"].values()):
        raise D3BindingError("one or more D2 independent review gates are not PASS")

    thresholds = prereg["acceptance_thresholds"]
    expected_thresholds = {
        "bulk_residual_max": 1e-10,
        "boundary_residual_max": 1e-10,
        "rr_constraint_max": 1e-9,
        "fine_mesh_profile_difference_max": 1e-8,
        "fine_mesh_augmented_difference_max": 1e-9,
        "independent_backend_candidate_distance_max": 1e-7,
        "minimum_rho_N": 1e-4,
        "minimum_rho_S": 1e-4,
        "minimum_interior_ell_margin": 1e-8,
        "minimum_cap_ell_margin": 1e-8,
        "minimum_positive_winding_margin": -1e-12,
        "maximum_reported_discrete_condition_number_without_high_precision_audit": 1e12,
        "all_thresholds_must_pass_simultaneously": True,
    }
    if thresholds != expected_thresholds:
        raise D3BindingError("scientific acceptance-threshold drift")
    if tuple(prereg["convergence_requirements"]["required_successful_levels"]) != (48, 64, 96):
        raise D3BindingError("required mesh gate drift")
    if resource["resource_limits"]["maximum_wall_clock_seconds_total"] != 21600 or resource["resource_limits"]["maximum_wall_clock_seconds_per_seed_per_level"] != 1800:
        raise D3BindingError("resource envelope drift")
    if resource["execution_environment"]["thread_count"] != 1 or resource["execution_environment"]["network_access"] is not False:
        raise D3BindingError("execution environment freeze drift")
    if resource["execution_order"]["independent_backend_after_primary_candidate_only"] is not True:
        raise D3BindingError("independent backend dispatch drift")

    sources = _verify_source_bindings()
    callable_surface = _verify_callable_surface()
    blueprint = physical_adapter_blueprint()

    forbidden_release = list(ROOT.glob("registry/*CP01R2*ReleaseAuthorization*.json"))
    forbidden_grant = list(ROOT.glob("registry/*CP01R2*ExecutionGrant*.json"))
    if forbidden_release or forbidden_grant:
        raise D3BindingError("D3 release-readiness review requires release/grant absence")

    return {
        "status": "PASS_WP3_D3_CP01R2_PHYSICAL_TARGET_BOUND_RELEASE_READY_FOR_SEPARATE_DECISION_NO_EXECUTION",
        "run_id": RUN_ID,
        "run_payload_sha256": observed_payload_hash,
        "schedule_sha256": schedule_sha256(),
        "planned_entry_count": len(build_schedule()),
        "physical_target_binding_complete": True,
        "physical_sector_identical_to_cp01r1": True,
        "etrn01_bound_at_source_contract_level": True,
        "callable_surface": callable_surface,
        "source_bindings": sources,
        "adapter_blueprint": blueprint,
        "release_authorization_present": False,
        "single_use_grant_present": False,
        "solver_backend_imported": False,
        "physical_residual_evaluations": 0,
        "solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "release_readiness": "PASS_FOR_SEPARATE_CP01R2_RELEASE_DECISION_ONLY",
        "WP3": "OPEN_CP01R2_PHYSICAL_TARGET_BOUND_RELEASE_DECISION_PENDING",
        "WP4": "BLOCKED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }


def issue_release_authorization(*_args: Any, **_kwargs: Any) -> None:
    raise PhysicalExecutionDenied("WP3-D3 cannot issue CP01R2 release authorization")


def issue_execution_grant(*_args: Any, **_kwargs: Any) -> None:
    raise PhysicalExecutionDenied("WP3-D3 cannot issue CP01R2 execution grant")


def execute_physical_schedule(*_args: Any, **_kwargs: Any) -> None:
    raise PhysicalExecutionDenied("WP3-D3 is binding/release-readiness review only; CP01R2 execution requires a later separate release decision and fresh single-use grant")


def main() -> int:
    print(json.dumps(audit(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
