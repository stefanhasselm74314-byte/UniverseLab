#!/usr/bin/env python3
"""ULSH-01 / WP3-D6H1 CP01R2 hardened transaction supervisor v1.2.

Append-only wrapper around the independently reviewed D3H1 CP01R2 transaction
base. It changes no physical solve rule. It rebinds a future fresh transaction
to the D6H1 hardened target and preserves a durable checkpoint recovery summary
whether the target succeeds or fails. Default invocation is audit-only.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import pickle
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3h1_cp01r2_transaction_v1.0.py"
TARGET = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d6h1_cp01r2_target_v1.1.py"
CHECKPOINT_SCHEMA = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2CheckpointSchema_v1.0.json"
D6_REVIEW = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6_CP01R2FailedExecutionReview_v1.0.json"
CONTRACT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2HardeningContract_v1.0.json"
RESULT_SCHEMA = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2ResultSchema_v1.0.json"
RELEASE_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2_PhysicalSolveReleaseAuthorization_v2.0.json"
GRANT_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2_SingleUseExecutionGrant_v2.0.json"
EXPECTED_BASE_TRANSACTION_BLOB = "315cfb4eae8c07efb66d264d66a601d5f888ce38"
EXPECTED_TARGET_BLOB = "ad1dd5201ca7399bc283a24a38b18df55f3b7e75"
EXPECTED_CHECKPOINT_SCHEMA_BLOB = "339f579c8b3d9f1ffffca04e79a5acf817a3c2eb"
EXPECTED_D6_REVIEW_BLOB = "7e017e67d3aeeec2469ea007ca87604ea7dabe03"
EXPECTED_RESULT_SCHEMA_BLOB = "54bf49acdfcca128e3b909d6e479b1178c77c276"

_SPEC = importlib.util.spec_from_file_location("ulsh_cp01r2_transaction_d3h1_base", BASE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("cannot load D3H1 CP01R2 transaction base")
BASE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = BASE
_SPEC.loader.exec_module(BASE)

RUN_ID = BASE.RUN_ID
RUN_PAYLOAD_SHA256 = BASE.RUN_PAYLOAD_SHA256
SCHEDULE_SHA256 = BASE.SCHEDULE_SHA256
DEPENDENCY_LOCK_SHA256 = BASE.DEPENDENCY_LOCK_SHA256
PLANNED_ENTRY_COUNT = BASE.PLANNED_ENTRY_COUNT
TransactionError = BASE.TransactionError
AuthorizationDenied = BASE.AuthorizationDenied
ResultClosureError = BASE.ResultClosureError


def _load_target():
    spec = importlib.util.spec_from_file_location("ulsh_cp01r2_target_d6h1_tx", TARGET)
    if spec is None or spec.loader is None:
        raise TransactionError("cannot load D6H1 target")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _patch_base_for_d6h1() -> None:
    BASE.TARGET = TARGET
    BASE.EXPECTED_TARGET_BLOB = EXPECTED_TARGET_BLOB
    BASE.CONTRACT = CONTRACT
    BASE.RELEASE_PATH = RELEASE_PATH
    BASE.GRANT_PATH = GRANT_PATH
    BASE.RESULT_SCHEMA = RESULT_SCHEMA
    BASE.EXPECTED_RESULT_SCHEMA_BLOB = EXPECTED_RESULT_SCHEMA_BLOB
    BASE.supervised_target_execution = supervised_target_execution


def _checkpoint_recovery_payload(checkpoint_root: Path, target: Any, return_code: int) -> dict[str, Any]:
    try:
        recovered = target.recover_checkpoint_prefix(checkpoint_root)
        status = "RECOVERED_DURABLE_PREFIX"
        error = None
    except Exception as exc:
        recovered = {"count": None, "chain_head_sha256": None}
        status = "CHECKPOINT_RECOVERY_VALIDATION_FAILED"
        error = f"{type(exc).__name__}: {exc}"
    return {
        "schema": "universelab.ulsh-01.md2s-bvp.cp01r2-checkpoint-recovery.v1",
        "run_id": RUN_ID,
        "schedule_sha256": SCHEDULE_SHA256,
        "target_return_code": return_code,
        "status": status,
        "durable_checkpoint_count": recovered.get("count"),
        "chain_head_sha256": recovered.get("chain_head_sha256"),
        "error": error,
        "replay_permitted": False,
        "physical_evidence_effect": "NONE",
    }


def supervised_target_execution(
    capability: dict[str, Any],
    grant_dir: Path,
    total_seconds: int,
    maximum_result_bytes: int,
) -> tuple[dict[str, Any], Path, Path]:
    capability_path = grant_dir / "target-capability.json"
    raw_pickle = grant_dir / "target-result.pickle"
    stdout_log = grant_dir / "target-stdout.txt"
    stderr_log = grant_dir / "target-stderr.txt"
    checkpoint_root = grant_dir / "entry-checkpoints"
    BASE._atomic_json(capability_path, capability)
    deny_dir = BASE._prepare_network_denial(grant_dir)
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(deny_dir) + (os.pathsep + existing_pythonpath if existing_pythonpath else "")
    env["UNIVERSELAB_NETWORK_POLICY"] = "DENY_CP01R2_SOLVER"
    command = [
        sys.executable,
        str(TARGET),
        "--execute-capability",
        str(capability_path),
        "--result-pickle",
        str(raw_pickle),
        "--checkpoint-root",
        str(checkpoint_root),
    ]
    with stdout_log.open("wb") as out, stderr_log.open("wb") as err:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=out, stderr=err)
        try:
            return_code = process.wait(timeout=total_seconds)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            return_code = -9
            target = _load_target()
            BASE._atomic_json(
                grant_dir / "checkpoint-recovery.json",
                _checkpoint_recovery_payload(checkpoint_root, target, return_code),
            )
            raise TransactionError("CP01R2 total hard wall-clock limit exceeded; durable prefix preserved")

    target = _load_target()
    recovery = _checkpoint_recovery_payload(checkpoint_root, target, return_code)
    BASE._atomic_json(grant_dir / "checkpoint-recovery.json", recovery)

    if return_code != 0:
        raise TransactionError(
            f"CP01R2 hardened target failed with return code {return_code}; "
            f"durable checkpoint prefix count={recovery.get('durable_checkpoint_count')}"
        )
    if recovery.get("status") != "RECOVERED_DURABLE_PREFIX" or recovery.get("durable_checkpoint_count") != PLANNED_ENTRY_COUNT:
        raise ResultClosureError("successful target return without a valid durable 35-entry checkpoint chain")
    if not raw_pickle.is_file():
        raise TransactionError("CP01R2 hardened target did not produce transient result payload")
    if raw_pickle.stat().st_size > maximum_result_bytes:
        raise ResultClosureError("transient target result exceeds frozen result budget")
    with raw_pickle.open("rb") as stream:
        raw = pickle.load(stream)
    if not isinstance(raw, dict):
        raise ResultClosureError("target result must be mapping")
    checkpoint_audit = raw.get("write_ahead_checkpoint_audit")
    if not isinstance(checkpoint_audit, dict):
        raise ResultClosureError("target result missing write-ahead checkpoint audit")
    if checkpoint_audit.get("durable_checkpoint_count") != PLANNED_ENTRY_COUNT:
        raise ResultClosureError("target result checkpoint count mismatch")
    if checkpoint_audit.get("chain_head_sha256") != recovery.get("chain_head_sha256"):
        raise ResultClosureError("target/result checkpoint chain-head mismatch")
    return raw, stdout_log, stderr_log


def static_preflight() -> dict[str, Any]:
    if BASE.git_blob_sha1(BASE_PATH) != EXPECTED_BASE_TRANSACTION_BLOB:
        raise TransactionError("D3H1 transaction base blob drift")
    if BASE.git_blob_sha1(TARGET) != EXPECTED_TARGET_BLOB:
        raise TransactionError("D6H1 target blob drift")
    if BASE.git_blob_sha1(CHECKPOINT_SCHEMA) != EXPECTED_CHECKPOINT_SCHEMA_BLOB:
        raise TransactionError("D6H1 checkpoint schema blob drift")
    if BASE.git_blob_sha1(D6_REVIEW) != EXPECTED_D6_REVIEW_BLOB:
        raise TransactionError("D6 failed-execution review blob drift")
    if BASE.git_blob_sha1(RESULT_SCHEMA) != EXPECTED_RESULT_SCHEMA_BLOB:
        raise TransactionError("result schema blob drift")
    if RELEASE_PATH.exists() or GRANT_PATH.exists():
        raise TransactionError("D6H1 no-execution phase requires future release/grant absence")
    d6 = BASE.load_json(D6_REVIEW)
    blockers = d6.get("new_release_blockers", {})
    if blockers.get("D6-B01", {}).get("status") != "OPEN_RELEASE_BLOCKER":
        raise TransactionError("D6-B01 review basis drift")
    if blockers.get("D6-B02", {}).get("status") != "OPEN_RELEASE_BLOCKER":
        raise TransactionError("D6-B02 review basis drift")
    disposition = d6.get("grant_and_governance_disposition", {})
    if disposition.get("runtime_grant_spent") is not True or disposition.get("runtime_grant_replay_permitted") is not False:
        raise TransactionError("spent/non-replayable D5 grant basis drift")
    contract = BASE.load_json(CONTRACT)
    if contract.get("status") != "PASS_D6H1_IMPLEMENTED_NO_EXECUTION_PENDING_INDEPENDENT_REVIEW":
        raise TransactionError("D6H1 contract status drift")
    if contract.get("run_id") != RUN_ID or contract.get("run_payload_sha256") != RUN_PAYLOAD_SHA256:
        raise TransactionError("D6H1 contract run binding drift")
    if contract.get("schedule_sha256") != SCHEDULE_SHA256:
        raise TransactionError("D6H1 contract schedule binding drift")
    target = _load_target()
    target_audit = target.audit_target()
    if target_audit.get("solver_calls") != 0 or target_audit.get("physical_solve_executed") is not False:
        raise TransactionError("D6H1 target audit violated no-execution firewall")
    bundle = BASE.source_bundle_sha256(contract)
    return {
        "status": "PASS_WP3_D6H1_CP01R2_TRANSACTION_HARDENING_NO_EXECUTION",
        "run_id": RUN_ID,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "schedule_sha256": SCHEDULE_SHA256,
        "source_bundle_sha256": bundle,
        "D6-B01": "IMPLEMENTED_PENDING_INDEPENDENT_REVIEW",
        "D6-B02": "IMPLEMENTED_PENDING_INDEPENDENT_REVIEW",
        "target_finalization_consumes_durable_checkpoint_matrix": True,
        "transaction_preserves_checkpoint_recovery_on_target_failure": True,
        "old_d5_grant_replay_permitted": False,
        "future_release_authorization_present": False,
        "future_single_use_grant_present": False,
        "solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
    }


def execute(transaction_root: Path) -> dict[str, Any]:
    _patch_base_for_d6h1()
    return BASE.execute(transaction_root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--transaction-root")
    args = parser.parse_args()
    if args.execute:
        if not args.transaction_root:
            raise AuthorizationDenied("--transaction-root required")
        print(json.dumps(execute(Path(args.transaction_root)), indent=2, sort_keys=True))
        return 0
    print(json.dumps(static_preflight(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
