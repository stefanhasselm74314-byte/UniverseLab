#!/usr/bin/env python3
"""ULSH-01 WP2 CP01R4 target-release hardening adapter v0.2.

This adapter preserves the v0.1 frozen numerical path and adds release-subject
Git HEAD verification, no-overwrite result semantics, process memory limiting,
and stricter primary admissibility reporting. Audit/self-test never import the
numerical backend and never execute the solver.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterable

try:
    import resource
except ImportError:  # pragma: no cover - operational release is POSIX-only
    resource = None

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "tools/2026-08-27_hzt_m0_s6_c_phys_m1_ulsh01_wp2_cp01r4_target_release_v0.1.py"
TRANSACTION_V03_PATH = Path("registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_TargetTransactionContract_v0.3.json")

SPEC = importlib.util.spec_from_file_location("ulsh01_wp2_cp01r4_release_base_v01", BASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import CP01R4 release base v0.1")
BASE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)

# Rebind only the release transaction package. The frozen CP01R4 numerical payload
# and historical primary numerical sources are unchanged.
BASE.TRANSACTION_CONTRACT_PATH = TRANSACTION_V03_PATH

EXIT_NOT_AUTHORIZED = BASE.EXIT_NOT_AUTHORIZED
EXIT_PREFLIGHT_FAILURE = BASE.EXIT_PREFLIGHT_FAILURE
EXIT_EXECUTION_FAILURE = BASE.EXIT_EXECUTION_FAILURE
TARGET_DIGEST = BASE.TARGET_DIGEST
RUN_ID = BASE.RUN_ID
RUN_PAYLOAD_SHA256 = BASE.RUN_PAYLOAD_SHA256
DEPENDENCY_LOCK_SHA256 = BASE.DEPENDENCY_LOCK_SHA256
PRIMARY_SHA256 = BASE.PRIMARY_SHA256
PRIMARY_BASE_SHA256 = BASE.PRIMARY_BASE_SHA256
ReleaseError = BASE.ReleaseError
AuthorizationError = BASE.AuthorizationError
ReplayError = BASE.ReplayError
SolveTimeout = BASE.SolveTimeout

ORIGINAL_EVALUATE_STATE = BASE.evaluate_state
ORIGINAL_CANDIDATE_FINAL_QA = BASE.candidate_final_qa


def require(condition: bool, message: str) -> None:
    BASE.require(condition, message)


def git_head_sha(repo_root: str | Path) -> str:
    """Resolve the actual checked-out release-subject commit."""
    proc = subprocess.run(
        ["git", "-C", str(Path(repo_root).resolve()), "rev-parse", "HEAD"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=15,
    )
    if proc.returncode != 0:
        raise ReleaseError(f"unable to resolve actual Git HEAD: {proc.stderr.strip()}")
    value = proc.stdout.strip().lower()
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise ReleaseError(f"Git HEAD is not a full 40-hex SHA: {value!r}")
    return value


def inspect_process_memory_limit(policy: dict[str, Any]) -> dict[str, Any]:
    """Compute the frozen RLIMIT_AS action without mutating the process."""
    if resource is None or not hasattr(resource, "RLIMIT_AS"):
        return {
            "supported": False,
            "reason": "RLIMIT_AS_UNAVAILABLE",
            "mutated": False,
        }
    requested = int(policy["resource_limits"]["maximum_memory_bytes"])
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    infinity = resource.RLIM_INFINITY

    finite = [requested]
    if soft != infinity and soft >= 0:
        finite.append(int(soft))
    if hard != infinity and hard >= 0:
        finite.append(int(hard))
    proposed_soft = min(finite)
    return {
        "supported": True,
        "requested_bytes": requested,
        "current_soft": int(soft),
        "current_hard": int(hard),
        "proposed_soft": int(proposed_soft),
        "existing_stricter_limit_preserved": (
            (soft != infinity and soft >= 0 and int(soft) < requested)
            or (hard != infinity and hard >= 0 and int(hard) < requested)
        ),
        "mutated": False,
    }


def apply_process_resource_limits(policy: dict[str, Any]) -> dict[str, Any]:
    """Fail closed unless the frozen address-space limit can be enforced."""
    plan = inspect_process_memory_limit(policy)
    if not plan.get("supported"):
        raise ReleaseError("operational release requires POSIX RLIMIT_AS support")
    assert resource is not None
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    proposed = int(plan["proposed_soft"])
    try:
        resource.setrlimit(resource.RLIMIT_AS, (proposed, hard))
    except (OSError, ValueError) as exc:
        raise ReleaseError(f"unable to enforce frozen memory limit: {exc}") from exc
    after_soft, after_hard = resource.getrlimit(resource.RLIMIT_AS)
    if after_soft == resource.RLIM_INFINITY or int(after_soft) > proposed:
        raise ReleaseError("RLIMIT_AS did not tighten to the frozen/protective bound")
    return {
        **plan,
        "applied_soft": int(after_soft),
        "applied_hard": int(after_hard),
        "mutated": True,
    }


def _finite_arrays(backend: Any, *arrays: Any) -> bool:
    np = backend.np
    return all(bool(np.all(np.isfinite(array))) for array in arrays)


def evaluate_state_hardened(backend: Any, state: Any, n: int, model: Any, sector: Any):
    """Add explicit gates required by the frozen CP01R4 admissibility contract."""
    metrics, info = ORIGINAL_EVALUATE_STATE(backend, state, n, model, sector)
    north, south = info["north"], info["south"]
    ell_sigma = 0.5 * (north.ell[-1] + south.ell[-1])
    metrics["cap_ell_margin_gate"] = bool(ell_sigma > 1.0e-8)
    metrics["finite_profiles_and_first_required_derivatives"] = _finite_arrays(
        backend,
        north.A, north.ell, north.varphi, north.a_chi,
        north.A_x, north.ell_x, north.varphi_x,
        south.A, south.ell, south.varphi, south.a_chi,
        south.A_x, south.ell_x, south.varphi_x,
    )
    metrics["active_m1_domains_hold"] = bool(
        model.mhat_phi_sq > 0.0
        and model.a_F > 0.0
        and model.z_sigma_hat > 0.0
        and model.q_hat > 0.0
    )
    metrics["fixed_discrete_sector_valid"] = bool(
        isinstance(sector.N_F, int)
        and isinstance(sector.N_sigma, int)
        and isinstance(sector.m_sigma, int)
        and sector.m_sigma > 0
    )
    return metrics, info


def candidate_final_qa_hardened(backend: Any, track: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    result = ORIGINAL_CANDIDATE_FINAL_QA(backend, track, payload)
    failures = list(result.get("failures", []))
    for level in payload["convergence_requirements"]["required_successful_levels"]:
        record = track.get("levels", {}).get(str(level))
        if not record or not record.get("converged"):
            continue
        metrics = record.get("metrics", {})
        for key in (
            "cap_ell_margin_gate",
            "finite_profiles_and_first_required_derivatives",
            "active_m1_domains_hold",
            "fixed_discrete_sector_valid",
        ):
            if metrics.get(key) is not True:
                failures.append(f"N{level}_{key}")
    result["failures"] = sorted(set(failures))
    result["pass"] = len(result["failures"]) == 0
    result["release_adapter_v0_2_admissibility_hardening"] = True
    return result


# Patch only QA/admissibility helpers used by the future v0.1 numerical execution.
# No backend is imported by assigning these functions.
BASE.evaluate_state = evaluate_state_hardened
BASE.candidate_final_qa = candidate_final_qa_hardened


def exclusive_result_write(path: str | Path, encoded: bytes, maximum_bytes: int) -> None:
    """Create the result exactly once; existing result paths are never overwritten."""
    result_path = Path(path)
    if len(encoded) > int(maximum_bytes):
        raise ReleaseError("result exceeds frozen maximum_result_bytes")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(result_path, flags, 0o600)
    except FileExistsError as exc:
        raise ReleaseError("result output already exists; no-overwrite firewall") from exc
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        try:
            result_path.unlink(missing_ok=True)
        finally:
            raise


def review(repo_root: Path, manifest_output: Path | None = None) -> dict[str, Any]:
    payload, policy, manifest, bindings = BASE.preflight(repo_root)
    BASE.validate_synthetic_prolongation()
    head = git_head_sha(repo_root)
    memory_plan = inspect_process_memory_limit(policy)
    if manifest_output is not None:
        manifest_output.parent.mkdir(parents=True, exist_ok=True)
        manifest_output.write_bytes(BASE.canonical_bytes(manifest) + b"\n")
    return {
        "status": "PASS_CP01R4_RELEASE_V02_PREFLIGHT_IMPLEMENTATION_ONLY",
        "run_id": RUN_ID,
        "target_contract_digest_sha256": TARGET_DIGEST,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "release_subject_git_head_sha": head,
        "release_package_manifest_sha256": manifest["package_digest_sha256"],
        "release_package_member_count": len(manifest["member_sha256"]),
        "method_freeze_complete": True,
        "barycentric_prolongation_synthetic_QA": "PASS",
        "git_head_binding_implemented": True,
        "result_no_overwrite_implemented": True,
        "memory_limit_plan": memory_plan,
        "memory_limit_mutated_during_audit": False,
        "backend_imported": False,
        "solver_executed": False,
        "physical_execution_authorized": False,
        "operative_grant_created": False,
        "operative_authorization_decision_created": False,
        "WP2_closed": False,
        "WP3_started": False,
        "WP4_started": False,
        "physical_background": "NOT_ESTABLISHED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
        "bindings": bindings,
    }


def synthetic_authorization_replay_qa(repo_root: Path, reservation_dir: Path) -> dict[str, Any]:
    result = BASE.synthetic_authorization_replay_qa(repo_root, reservation_dir)
    require(BASE.BACKEND_IMPORT_COUNT == 0, "backend imported during synthetic QA")
    require(BASE.SOLVER_CALL_COUNT == 0, "solver called during synthetic QA")
    result["release_adapter"] = "v0.2"
    result["actual_git_head_validation_used_for_physical_execution_only"] = True
    result["memory_limit_mutated"] = False
    return result


def execute_authorized(
    repo_root: Path,
    decision_path: Path,
    grant_path: Path,
    reservation_dir: Path,
    result_output: Path,
    caller_repository_commit_sha: str,
    now: datetime,
) -> dict[str, Any]:
    """Future operational path. This is not invoked by CI or this implementation turn."""
    actual_head = git_head_sha(repo_root)
    if caller_repository_commit_sha.lower() != actual_head:
        raise AuthorizationError(
            "caller repository commit does not equal actual checked-out Git HEAD"
        )
    if result_output.exists():
        raise AuthorizationError("result output already exists; deny before grant reservation")

    payload, policy, manifest, bindings = BASE.preflight(repo_root)
    decision = BASE.load_json(decision_path)
    decision_id = BASE.verify_decision(decision, manifest, bindings, actual_head, now)
    decision_sha = BASE.file_sha256(decision_path)
    grant = BASE.verify_grant(
        BASE.load_json(grant_path),
        decision_id,
        decision_sha,
        manifest,
        bindings,
        actual_head,
        now,
        control_only=False,
    )
    attestation = BASE.environment_attestation(policy)
    attestation_sha = BASE.canonical_sha256(attestation)

    # Single-use token is consumed before any process-limit mutation or backend import.
    reservation = BASE.atomic_reserve_grant(reservation_dir, grant, control_only=False)
    try:
        resource_enforcement = apply_process_resource_limits(policy)
        result = BASE.execute_primary_target(repo_root, payload, policy)
        output = {
            "schema": "universelab.hzt-m0-s6-c-phys-m1.ulsh01-wp2-cp01r4-primary-result.v0.2",
            "run_id": RUN_ID,
            "repository_commit_sha": actual_head,
            "target_contract_digest_sha256": TARGET_DIGEST,
            "run_payload_sha256": RUN_PAYLOAD_SHA256,
            "release_package_manifest_sha256": manifest["package_digest_sha256"],
            "authorization_decision_id": decision_id,
            "authorization_decision_sha256": decision_sha,
            "grant_id": grant["grant_id"],
            "environment_attestation": attestation,
            "environment_attestation_sha256": attestation_sha,
            "resource_enforcement": resource_enforcement,
            "primary_execution": result,
            "solver_call_count": BASE.SOLVER_CALL_COUNT,
            "backend_import_count": BASE.BACKEND_IMPORT_COUNT,
            "physical_background": "NOT_ESTABLISHED_UNTIL_RESULT_INTERPRETATION_AND_WP3_CROSSCHECK",
            "WP3_authorized": False,
            "WP4_authorized": False,
            "physical_response_rank": "NOT_EXECUTED",
            "K1-D": "NOT_RELEASED",
            "K1-E": "NOT_ADMISSIBLE",
            "physical_evidence_effect": "PRIMARY_NUMERICAL_DIAGNOSTIC_ONLY_IF_AUTHORIZED_RUN_OCCURRED",
            "forbidden_inferences": [
                "A primary numerical candidate is not a continuum existence or uniqueness proof.",
                "WP2 does not establish Fredholmness, stability, ghost freedom or physical viability.",
                "WP2 does not authorize WP3, WP4, the 41-job response evaluation, K1-D or K1-E.",
                "Provisional one-sided cap traces are not WP4-frozen interface data."
            ],
        }
        encoded = BASE.canonical_bytes(output) + b"\n"
        exclusive_result_write(
            result_output,
            encoded,
            int(policy["resource_limits"]["maximum_result_bytes"]),
        )
        BASE.update_reservation(
            reservation,
            "SUCCEEDED",
            backend_imported=BASE.BACKEND_IMPORT_COUNT > 0,
            solver_executed=BASE.SOLVER_CALL_COUNT > 0,
        )
        return output
    except SolveTimeout:
        BASE.update_reservation(
            reservation,
            "TIMED_OUT",
            backend_imported=BASE.BACKEND_IMPORT_COUNT > 0,
            solver_executed=BASE.SOLVER_CALL_COUNT > 0,
        )
        raise
    except BaseException:
        try:
            BASE.update_reservation(
                reservation,
                "FAILED",
                backend_imported=BASE.BACKEND_IMPORT_COUNT > 0,
                solver_executed=BASE.SOLVER_CALL_COUNT > 0,
            )
        finally:
            raise


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit", "self-test", "run"))
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--manifest-output")
    parser.add_argument("--reservation-dir")
    parser.add_argument("--decision")
    parser.add_argument("--grant")
    parser.add_argument("--result-output")
    parser.add_argument("--repository-commit-sha")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def emit(value: dict[str, Any], as_json: bool) -> None:
    print(json.dumps(value, indent=2, sort_keys=True) if as_json else value["status"])


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    try:
        if args.command == "audit":
            emit(
                review(repo_root, Path(args.manifest_output) if args.manifest_output else None),
                args.json,
            )
            return 0
        if args.command == "self-test":
            require(args.reservation_dir is not None, "--reservation-dir required for self-test")
            emit(
                synthetic_authorization_replay_qa(repo_root, Path(args.reservation_dir)),
                args.json,
            )
            return 0

        required = {
            "--decision": args.decision,
            "--grant": args.grant,
            "--reservation-dir": args.reservation_dir,
            "--result-output": args.result_output,
            "--repository-commit-sha": args.repository_commit_sha,
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise AuthorizationError(
                "operative execution denied; missing " + ", ".join(missing)
            )
        result = execute_authorized(
            repo_root,
            Path(args.decision),
            Path(args.grant),
            Path(args.reservation_dir),
            Path(args.result_output),
            str(args.repository_commit_sha),
            datetime.now(timezone.utc),
        )
        print(
            json.dumps(result, indent=2, sort_keys=True)
            if args.json
            else result["primary_execution"]["classification"]
        )
        return 0
    except AuthorizationError as exc:
        emit(
            {
                "status": "NOT_AUTHORIZED",
                "error": str(exc),
                "backend_import_count": BASE.BACKEND_IMPORT_COUNT,
                "solver_call_count": BASE.SOLVER_CALL_COUNT,
                "physical_evidence_effect": "NONE",
            },
            args.json,
        )
        return EXIT_NOT_AUTHORIZED
    except ReleaseError as exc:
        emit(
            {
                "status": "FAIL_CLOSED_RELEASE_ERROR",
                "error": str(exc),
                "backend_import_count": BASE.BACKEND_IMPORT_COUNT,
                "solver_call_count": BASE.SOLVER_CALL_COUNT,
                "physical_evidence_effect": (
                    "NONE" if BASE.SOLVER_CALL_COUNT == 0
                    else "EXECUTION_ATTEMPT_DIAGNOSTIC_ONLY"
                ),
            },
            args.json,
        )
        return EXIT_PREFLIGHT_FAILURE
    return EXIT_EXECUTION_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
