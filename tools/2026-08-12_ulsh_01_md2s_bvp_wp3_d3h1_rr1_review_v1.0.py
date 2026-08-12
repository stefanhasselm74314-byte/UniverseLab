#!/usr/bin/env python3
"""Independent WP3-D3H1-RR1 review of CP01R2 transaction/result closure.

Stdlib-only review. It performs source-ordering and synthetic packaging/replay
probes but never creates a physical release/grant and never calls a solver.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2TransactionHardeningContract_v1.0.json"
RESULT_SCHEMA = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2ResultSchema_v1.0.json"
D3_REVIEW = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3_CP01R2PhysicalBindingReleaseReadinessReview_v1.0.json"
TARGET = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3h1_cp01r2_target_v1.0.py"
TRANSACTION = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3h1_cp01r2_transaction_v1.1.py"
TRANSACTION_BASE = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3h1_cp01r2_transaction_v1.0.py"
REVIEW_CONTRACT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_RR1_IndependentReview_v1.0.json"

RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2"
RUN_PAYLOAD_SHA256 = "e8b8e82d2cb1472d91c387a40c8f84024c2549a3dcc2c897df5561f7bf721b36"
SCHEDULE_SHA256 = "929f59d018cc511f36c98ef26a8614ed495fe699a067b1b33e6c5b53efaf8e0b"


class ReviewError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReviewError(f"top-level object required: {path}")
    return value


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ReviewError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _synthetic_raw_result() -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    primary = {
        "node_counts": [24, 32, 48, 64, 96],
        "per_seed_per_level_history": [],
        "all_boundary_residuals": [],
        "bulk_residual_norms": [],
        "constraint_norms": [],
        "profile_convergence": [],
        "augmented_variable_convergence": [],
        "spectral_tail_table": [],
        "rrqr_ranks": [],
        "singular_values": [],
        "condition_estimates": [],
        "raw_rank_condition_history": [{"entry_id": "SYNTH", "iteration": 0, "rank": 2, "condition_estimate": math.inf}],
        "scaled_rank_condition_history": [{"entry_id": "SYNTH", "iteration": 0, "rank": 2, "condition_estimate": 1.0}],
        "trust_radius_rho_history": [{"entry_id": "SYNTH", "iteration": 0, "trust_radius_before": 1.0, "trust_radius_after": 2.0, "rho": 1.0, "accepted": True, "accepted_factor": 1.0, "accepted_scaled_step_norm": 1.0, "trust_radius_active": True, "acceptance_merit": "ORIGINAL_UNSCALED_RESIDUAL_INFINITY_NORM"}],
        "progress_continuation_provenance": [{"entry_id": "SYNTH", "initialization_source": "FRESH_FROZEN_CP01R1_SEED_SAME_INDEX", "continuation_source_entry_id": None, "stage_initial_residual_inf": 10.0, "stage_final_residual_inf": 9.0, "continuation_admissible": True, "eligible_for_next_mesh": True}],
    }
    independent = {
        "implementation_source_sha256": "0" * 64,
        "residual_assembly_independence_statement": "synthetic review fixture",
        "grid_or_mesh_definition": "none",
        "per_candidate_residuals": [],
        "candidate_distance_to_primary": [],
        "agreement_classification": [],
    }
    return {
        "schema": "universelab.ulsh-01.md2s-bvp.cp01r2-result.v1",
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "schedule_sha256": SCHEDULE_SHA256,
        "implementation_source_sha256": "0" * 64,
        "dependency_lock_sha256": "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f",
        "execution_started_utc": now,
        "execution_finished_utc": now,
        "primary_backend": primary,
        "independent_backend": independent,
        "candidate_inventory": [],
        "acceptance_audit": {"passing_candidate_ids": [], "distinct_passing_candidate_ids": [], "interpretation": "SYNTHETIC_REVIEW_ONLY"},
        "profile_artifacts": {},
        "final_classification": "NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL",
        "physical_evidence_effect": "NONE",
        "forbidden_inferences": ["continuum_existence", "physical_confirmation"],
    }


def review() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    schema = load_json(RESULT_SCHEMA)
    d3 = load_json(D3_REVIEW)
    review_contract = load_json(REVIEW_CONTRACT)

    if contract["status"] != "PASS_D3H1_IMPLEMENTED_NO_EXECUTION_PENDING_INDEPENDENT_REVIEW":
        raise ReviewError("D3H1 implementation contract not in reviewable state")
    if contract["run_id"] != RUN_ID or contract["run_payload_sha256"] != RUN_PAYLOAD_SHA256 or contract["schedule_sha256"] != SCHEDULE_SHA256:
        raise ReviewError("D3H1 run identity drift")
    if d3["release_blockers"]["D3-B01"]["status"] != "OPEN_RELEASE_BLOCKER" or d3["release_blockers"]["D3-B02"]["status"] != "OPEN_RELEASE_BLOCKER":
        raise ReviewError("D3 blocker basis drift")

    for name, binding in review_contract["source_bindings"].items():
        path = ROOT / binding["path"]
        observed = git_blob_sha1(path)
        if observed != binding["git_blob_sha1"]:
            raise ReviewError(f"RR1 source drift: {name}: {observed}")

    tx = _load_module(TRANSACTION, "ulsh_d3h1_rr1_tx")
    target = _load_module(TARGET, "ulsh_d3h1_rr1_target")
    preflight = tx.static_preflight()
    target_audit = target.audit_target()
    if preflight["solver_calls"] != 0 or preflight["physical_solve_executed"] is not False:
        raise ReviewError("transaction preflight crossed no-execution firewall")
    if target_audit["solver_calls"] != 0 or target_audit["physical_solve_executed"] is not False:
        raise ReviewError("target audit crossed no-execution firewall")

    base_source = TRANSACTION_BASE.read_text(encoding="utf-8")
    execute_source = base_source.split("def execute(transaction_root: Path)", 1)[1]
    order = [
        execute_source.index("pre_solver_output_collision_guard"),
        execute_source.index("strict_startup_environment"),
        execute_source.index("runtime_attestation"),
        execute_source.index("claim_single_use_grant"),
        execute_source.index("supervised_target_execution"),
        execute_source.index("COMMITTING_RESULT"),
        execute_source.index("os.replace(staging, result_dir)"),
        execute_source.index("_fsync_directory(result_dir.parent)"),
        execute_source.index("result-commit-marker.json"),
        execute_source.index("\"SUCCEEDED\""),
    ]
    if order != sorted(order):
        raise ReviewError(f"transaction ordering invariant drift: {order}")
    for fragment in ("O_CREAT | os.O_EXCL", "COMMITTED_INDETERMINATE", "post_target_wall_clock_limit", "sitecustomize.py", "socket.create_connection", "maximum_memory_bytes"):
        if fragment not in base_source:
            raise ReviewError(f"missing transaction hardening invariant: {fragment}")

    target_source = TARGET.read_text(encoding="utf-8")
    execute_target = target_source.split("def execute_physical_schedule", 1)[1]
    if execute_target.index("_enforce_memory_limit") > execute_target.index("dynamic_import(D2_ETRN"):
        raise ReviewError("memory limit is not enforced before numerical import")
    if "continuation_admissible = bool(primary.admissible(state, node_count))" not in execute_target:
        raise ReviewError("progress continuation does not use primary physical-domain admissibility")
    if "admissible=continuation_admissible" not in execute_target or "final=final_inf" not in execute_target:
        raise ReviewError("progress-continuation 10-percent original-residual wiring drift")

    required_etrn = {"raw_rank_condition_history", "scaled_rank_condition_history", "trust_radius_rho_history", "progress_continuation_provenance"}
    if set(schema["cp01r2_etrn01_required_fields"]) != required_etrn:
        raise ReviewError("ETRN immutable result field set drift")
    if schema["immutable_output_policy"]["overwrite_existing_path"] is not False or schema["immutable_output_policy"]["replay_after_any_grant_spend"] is not False:
        raise ReviewError("immutable/replay policy drift")

    # Synthetic packaging proves the schema closure, nonfinite sanitation and manifest
    # path without importing or executing any physical backend.
    with tempfile.TemporaryDirectory(prefix="ulsh-d3h1-rr1-") as temp_text:
        temp = Path(temp_text)
        staging = temp / "staging"
        out = temp / "out.txt"
        err = temp / "err.txt"
        out.write_text("synthetic stdout\n", encoding="utf-8")
        err.write_text("", encoding="utf-8")
        grant = {"authorization_decision_id": "UL-DEC-SYNTHETIC-RR1", "grant_nonce": "a" * 32}
        runtime = {"platform": "synthetic", "blas_lapack_configuration": "synthetic", "thread_environment": {key: "1" for key in tx.BASE.THREAD_ENV_KEYS}}
        package = tx.BASE.package_schema_complete_result(staging, _synthetic_raw_result(), runtime, grant, "b" * 64, "c" * 64, 5_000_000, out, err)
        result = json.loads((staging / "result.json").read_text(encoding="utf-8"))
        manifest = json.loads((staging / "artifact-manifest.json").read_text(encoding="utf-8"))
        if package["result_sha256"] != tx.BASE.sha256_file(staging / "result.json") or not manifest["all_listed_artifacts_hashed"]:
            raise ReviewError("synthetic immutable package hash closure failed")
        if result["primary_backend"]["raw_rank_condition_history"][0]["condition_estimate"] is not None:
            raise ReviewError("nonfinite diagnostic was not projected to null")
        replacements = result["acceptance_audit"]["json_safe_nonfinite_replacements"]
        if not any(item["original_nonfinite_kind"] == "positive_infinity" for item in replacements):
            raise ReviewError("nonfinite replacement provenance missing")

        replay_root = temp / "replay"
        replay_grant = {"grant_nonce": "d" * 32}
        tx.BASE.claim_single_use_grant(replay_root, replay_grant, "e" * 64)
        replay_blocked = False
        try:
            tx.BASE.claim_single_use_grant(replay_root, replay_grant, "e" * 64)
        except Exception:
            replay_blocked = True
        if not replay_blocked:
            raise ReviewError("synthetic grant replay was not blocked")

        collision_root = temp / "collision"
        collision_grant = {"authorization_decision_id": "UL-DEC-COLLISION", "grant_nonce": "f" * 32}
        result_dir, _staging = tx.BASE.output_paths(collision_root, collision_grant)
        result_dir.mkdir(parents=True)
        collision_blocked = False
        try:
            tx.BASE.pre_solver_output_collision_guard(collision_root, collision_grant)
        except tx.BASE.ResultClosureError:
            collision_blocked = True
        if not collision_blocked:
            raise ReviewError("synthetic immutable output collision was not blocked")

    try:
        tx.BASE.validate_release_and_grant()
    except tx.BASE.AuthorizationDenied:
        pass
    else:
        raise ReviewError("release/grant unexpectedly present during D3H1-RR1")

    if tx.BASE.RELEASE_PATH.exists() or tx.BASE.GRANT_PATH.exists():
        raise ReviewError("release/grant artifact present during no-execution review")

    return {
        "status": "PASS_WP3_D3H1_RR1_D3_BLOCKERS_VERIFIED_CLOSED_NO_EXECUTION",
        "run_id": RUN_ID,
        "review_gates_passed": 8,
        "D3-B01": "VERIFIED_CLOSED",
        "D3-B02": "VERIFIED_CLOSED",
        "new_release_blockers": [],
        "nonblocking_warning": "Python-level network denial is source-verified for the controlled Python solver process; it is not claimed to be a kernel network namespace.",
        "synthetic_result_package": "PASS",
        "synthetic_replay_denial": "PASS",
        "synthetic_collision_guard": "PASS",
        "solver_imports": 0,
        "solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "WP4": "BLOCKED",
        "next_allowed_action": "ULSH-01_WP3_D4_CP01R2_SINGLE_USE_RELEASE_DECISION_NO_EXECUTION",
    }


def main() -> int:
    print(json.dumps(review(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
