#!/usr/bin/env python3
"""ULSH-01 / WP2 source-bound entry point for the frozen CP01R1 physical BVP.

Audit/schedule operations are non-numerical.  Numerical backends are imported
only by execute_physical_schedule() after a transaction capability has already
passed the WP2 grant/release firewall.  This module has no direct solve CLI.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
FROZEN_PAYLOAD_SHA256 = "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302"
SEED_SPEC_SHA256 = "b6e4319cc29736799a0b46320002e51cd17b70b724a6b4c6e86567a316996161"
DEPENDENCY_LOCK_SHA256 = "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f"
EXPECTED_A_F = Fraction(1, 4)
SEED_IDS = (
    "S0_ANALYTIC_CONTINUATION",
    "S1_SYMMETRIC_ZERO",
    "S2_SMALL_DEF_N",
    "S3_SMALL_DEF_S",
    "S4_K4_LOW",
    "S5_K4_HIGH",
    "S6_MIXED",
)
NODE_COUNTS = (24, 32, 48, 64, 96)
PLANNED_ENTRY_COUNT = 35

RUN_INPUT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"
PREREG_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"
SEED_SPEC_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BSeedSpecification_v0.1.json"
PRIMARY_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py"
PRIMARY_BASE_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.1.py"
INDEPENDENT_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_independent_backend_v0.1.py"

PRIMARY_SHA256 = "13b289fbde886240d993e90d4906776e7f33926dd19a37e24402172045162f26"
PRIMARY_BASE_SHA256 = "114d00ba10ba1df2f061f022254f5fd1a29b206e1ecf3413eeb062281dc43745"
INDEPENDENT_SHA256 = "d271a6b9f4783060832b20655700c415098012afa9880fc0b046a94ecbcef217"


class TargetContractError(RuntimeError):
    pass


class TargetExecutionDenied(RuntimeError):
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


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TargetContractError(f"top-level JSON object required: {path}")
    return value


def parse_fraction(value: Any) -> Fraction:
    if isinstance(value, str):
        return Fraction(value)
    return Fraction(value)


def frozen_payload() -> dict[str, Any]:
    freeze = load_json(RUN_INPUT_PATH)
    payload = freeze.get("frozen_run_payload")
    if not isinstance(payload, dict):
        raise TargetContractError("missing frozen_run_payload")
    if freeze.get("frozen_run_payload_sha256") != FROZEN_PAYLOAD_SHA256:
        raise TargetContractError("frozen payload digest drift")
    if sha256_bytes(canonical_json_bytes(payload)) != FROZEN_PAYLOAD_SHA256:
        raise TargetContractError("canonical frozen payload bytes do not match CP01R1 digest")
    if payload.get("run_id") != RUN_ID:
        raise TargetContractError("run_id drift")
    if parse_fraction(payload["model_parameters_ordered"]["a_F"]) != EXPECTED_A_F:
        raise TargetContractError("a_F must remain exactly 1/4")
    if payload.get("seed_spec_sha256") != SEED_SPEC_SHA256:
        raise TargetContractError("seed specification digest drift")
    if payload.get("dependency_lock_sha256") != DEPENDENCY_LOCK_SHA256:
        raise TargetContractError("dependency lock digest drift")
    return payload


def build_schedule() -> list[dict[str, Any]]:
    """Return the immutable seed-major 7 x 5 schedule; no solver import/call."""
    schedule: list[dict[str, Any]] = []
    ordinal = 0
    for seed_index, seed_id in enumerate(SEED_IDS):
        previous_id: str | None = None
        for node_count in NODE_COUNTS:
            ordinal += 1
            entry_id = f"CP01R1-E{ordinal:02d}-{seed_id}-N{node_count}"
            schedule.append({
                "ordinal": ordinal,
                "entry_id": entry_id,
                "seed_index": seed_index,
                "seed_id": seed_id,
                "node_count": node_count,
                "continuation_from_entry_id": previous_id,
            })
            previous_id = entry_id
    if len(schedule) != PLANNED_ENTRY_COUNT:
        raise TargetContractError("schedule cardinality drift")
    return schedule


def schedule_sha256() -> str:
    return sha256_bytes(canonical_json_bytes(build_schedule()))


def validate_schedule_against_sources() -> dict[str, Any]:
    payload = frozen_payload()
    seed_spec = load_json(SEED_SPEC_PATH)
    prereg = load_json(PREREG_PATH)
    declared_seed_ids = tuple(seed["seed_id"] for seed in seed_spec.get("seeds_ordered", []))
    if declared_seed_ids != SEED_IDS:
        raise TargetContractError("seed order differs from frozen seven-seed schedule")
    if tuple(prereg["solver_protocol"]["mesh_hierarchy"]["regional_node_counts"]) != NODE_COUNTS:
        raise TargetContractError("mesh hierarchy differs from frozen five-level schedule")
    if prereg["solver_protocol"]["seed_policy"]["seed_count"] != 7:
        raise TargetContractError("preregistered seed count drift")
    schedule = build_schedule()
    return {
        "run_id": payload["run_id"],
        "a_F": str(EXPECTED_A_F),
        "seed_count": len(SEED_IDS),
        "node_counts": list(NODE_COUNTS),
        "planned_entry_count": len(schedule),
        "schedule_sha256": sha256_bytes(canonical_json_bytes(schedule)),
    }


def validate_backend_hashes() -> dict[str, str]:
    observed = {
        "primary": sha256_file(PRIMARY_PATH),
        "primary_base": sha256_file(PRIMARY_BASE_PATH),
        "independent": sha256_file(INDEPENDENT_PATH),
    }
    expected = {
        "primary": PRIMARY_SHA256,
        "primary_base": PRIMARY_BASE_SHA256,
        "independent": INDEPENDENT_SHA256,
    }
    if observed != expected:
        raise TargetContractError(f"backend source hash drift: {observed}")
    return observed


def audit_target() -> dict[str, Any]:
    schedule = validate_schedule_against_sources()
    hashes = validate_backend_hashes()
    return {
        "status": "PASS_SOURCE_BOUND_TARGET_ENTRYPOINT_NO_SOLVE",
        **schedule,
        "backend_sha256": hashes,
        "solver_imported": False,
        "solver_calls": 0,
        "physical_solve_executed": False,
    }


def _dynamic_import(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise TargetContractError(f"cannot import backend: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _validate_capability(capability: TargetExecutionCapability) -> None:
    if not isinstance(capability, TargetExecutionCapability):
        raise TargetExecutionDenied("target execution requires WP2 capability")
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


def _prolongate_state(primary: Any, state: Any, old_n: int, new_n: int):
    """Deterministic mesh prolongation for initial guesses only, never observables."""
    import numpy as np
    old_regions, parameters = primary.unpack_state(state, old_n)
    old_tau = primary.chebyshev_lobatto(old_n).tau
    new_tau = primary.chebyshev_lobatto(new_n).tau
    new_regions = []
    for region in old_regions:
        new_regions.append([np.interp(new_tau, old_tau, field) for field in region])
    return primary.pack_state(new_regions, parameters.copy())


def execute_physical_schedule(capability: TargetExecutionCapability) -> dict[str, Any]:
    """Execute CP01R1 only after the WP2 transaction has issued a valid capability.

    This function is intentionally never called by WP2 CI/audit.  It contains
    no parameter substitution, no control a_F override, no random retry, and no
    surrogate fallback.  The immutable 35-entry schedule is the outer plan;
    each planned entry records primary and independent backend channels.
    """
    _validate_capability(capability)
    payload = frozen_payload()
    validate_backend_hashes()

    # Numerical imports happen only after every capability/source check above.
    primary = _dynamic_import(PRIMARY_PATH, "ulsh_wp2_primary_cp01r1")
    independent = _dynamic_import(INDEPENDENT_PATH, "ulsh_wp2_independent_cp01r1")
    import numpy as np
    from scipy.optimize import least_squares

    primary_model = primary.model_from_payload(payload, control_a_F=False)
    primary_sector = primary.sector_from_payload(payload)
    independent_model = independent.model_from_payload(payload, control_a_F=False)
    independent_sector = independent.sector_from_payload(payload)
    if Fraction(str(primary_model.a_F)) != EXPECTED_A_F or Fraction(str(independent_model.a_F)) != EXPECTED_A_F:
        raise TargetContractError("backend model construction changed a_F")

    schedule = build_schedule()
    results: list[dict[str, Any]] = []
    continuation: dict[str, tuple[int, Any]] = {}
    for entry in schedule:
        seed_id = entry["seed_id"]
        seed_index = int(entry["seed_index"])
        node_count = int(entry["node_count"])
        if seed_id in continuation:
            old_n, old_state = continuation[seed_id]
            initial = _prolongate_state(primary, old_state, old_n, node_count)
        else:
            initial = primary.seven_seeds(node_count)[seed_index]

        primary_result = primary.damped_newton(
            initial, node_count, primary_model, primary_sector,
            maximum_iterations=40,
            residual_tolerance=1.0e-9,
            step_tolerance=1.0e-9,
        )
        primary_state = np.asarray(primary_result["state"], dtype=float)
        primary_residual, primary_detail = primary.residual(primary_state, node_count, primary_model, primary_sector)
        primary_inf = float(np.max(np.abs(primary_residual)))
        primary_bc = float(np.max(np.abs(primary_detail["boundary"])))
        if bool(primary_result.get("converged")):
            continuation[seed_id] = (node_count, primary_state.copy())

        _regions, shooting_initial = primary.unpack_state(primary_state, node_count)
        shooting_initial = np.asarray(shooting_initial, dtype=float)

        def independent_residual(vector):
            values, _ = independent.shooting_residual(
                vector, independent_model, independent_sector,
                epsilon=1.0e-6,
                sample_count=max(257, 4 * node_count + 1),
            )
            return values

        independent_result = least_squares(
            independent_residual,
            shooting_initial,
            jac=lambda x: independent.centered_fd_jacobian(independent_residual, x, relative_step=1.0e-6),
            method="trf",
            max_nfev=40,
            ftol=1.0e-9,
            xtol=1.0e-9,
            gtol=1.0e-9,
        )
        independent_inf = float(np.max(np.abs(independent_result.fun)))
        agreement_scalar = float(np.max(np.abs(np.asarray(independent_result.x) - shooting_initial)))

        results.append({
            "entry_id": entry["entry_id"],
            "seed_id": seed_id,
            "node_count": node_count,
            "primary": {
                "converged": bool(primary_result.get("converged")),
                "failure": primary_result.get("failure"),
                "residual_inf": primary_inf,
                "four_bc_inf": primary_bc,
                "iterations": len(primary_result.get("history", [])),
            },
            "independent": {
                "converged": bool(independent_result.success) and independent_inf <= 1.0e-8,
                "residual_inf": independent_inf,
                "nfev": int(independent_result.nfev),
            },
            "agreement_scalar": agreement_scalar,
        })

    return {
        "run_id": RUN_ID,
        "frozen_input_sha256": FROZEN_PAYLOAD_SHA256,
        "schedule_sha256": schedule_sha256(),
        "planned_schedule_entries": PLANNED_ENTRY_COUNT,
        "matrix_entries": results,
        "physical_evidence_effect": "NONE_PENDING_QA_AND_RELEASE_CHAIN",
    }


def main() -> int:
    # Deliberately audit-only: physical execution has no direct CLI entry point.
    print(json.dumps(audit_target(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
