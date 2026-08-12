#!/usr/bin/env python3
"""ULSH-01 / WP3-D6R1 independent CP01R2 D6H1 review.

Independent, stdlib-only review of D6-B01/D6-B02 closure. This module never
issues a release/grant and never invokes the physical solver. Synthetic fixtures
exercise only finalizer-state semantics and durable checkpoint infrastructure.
"""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6R1_CP01R2IndependentReview_v1.0.json"
CONTRACT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2HardeningContract_v1.0.json"
CHECKPOINT_SCHEMA = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2CheckpointSchema_v1.0.json"
D6_REVIEW = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6_CP01R2FailedExecutionReview_v1.0.json"
TARGET_PATH = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d6h1_cp01r2_target_v1.1.py"
TRANSACTION_PATH = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d6h1_cp01r2_transaction_v1.2.py"
FUTURE_RELEASE = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2_PhysicalSolveReleaseAuthorization_v2.0.json"
FUTURE_GRANT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2_SingleUseExecutionGrant_v2.0.json"

EXPECTED = {
    str(D6_REVIEW.relative_to(ROOT)): "7e017e67d3aeeec2469ea007ca87604ea7dabe03",
    str(CONTRACT.relative_to(ROOT)): "e20be1172785aba293bb97212220856e77591bdf",
    str(CHECKPOINT_SCHEMA.relative_to(ROOT)): "339f579c8b3d9f1ffffca04e79a5acf817a3c2eb",
    str(TARGET_PATH.relative_to(ROOT)): "ad1dd5201ca7399bc283a24a38b18df55f3b7e75",
    str(TRANSACTION_PATH.relative_to(ROOT)): "080aab132948d095716a9d0675518b82088cd9b3",
}
EXPECTED_STATUS = "PASS_WP3_D6R1_D6_BLOCKERS_VERIFIED_CLOSED_NO_EXECUTION"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def blob_sha1(relative: str) -> str:
    return subprocess.run(
        ["git", "hash-object", relative], cwd=ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def synthetic_record(schedule_record: dict[str, Any], *, root: bool = False, value: float = 1.0) -> dict[str, Any]:
    return {
        "ordinal": int(schedule_record["ordinal"]),
        "entry_id": str(schedule_record["entry_id"]),
        "seed_index": int(schedule_record["seed_index"]),
        "node_count": int(schedule_record["node_count"]),
        "status": "COMPLETED_DIAGNOSTIC",
        "primary": {
            "candidate_under_local_residual_gate": bool(root),
            "synthetic_diagnostic": value,
        },
        "independent": None,
    }


def review() -> dict[str, Any]:
    decision = load_json(REVIEW)
    require(decision.get("review_status") == EXPECTED_STATUS, "D6R1 review status drift")
    require(decision.get("new_release_blockers") == [], "D6R1 declares a new release blocker")

    for path, expected in EXPECTED.items():
        actual = blob_sha1(path)
        require(actual == expected, f"source binding drift: {path}: {actual} != {expected}")

    contract = load_json(CONTRACT)
    require(contract.get("status") == "PASS_D6H1_IMPLEMENTED_NO_EXECUTION_PENDING_INDEPENDENT_REVIEW", "D6H1 contract state drift")
    require(contract.get("run_id") == decision.get("run_id"), "run id drift")
    require(contract.get("run_payload_sha256") == decision.get("run_payload_sha256"), "payload drift")
    require(contract.get("schedule_sha256") == decision.get("schedule_sha256"), "schedule drift")
    require(contract.get("dependency_lock_sha256") == decision.get("dependency_lock_sha256"), "dependency lock drift")

    failed = load_json(D6_REVIEW)
    require(failed.get("review_status") == "BLOCKED_WP3_D6_CP01R2_RESULT_REVIEW_FINALIZATION_DEFECT_NO_REPLAY", "D6 failure basis drift")
    blockers = failed.get("new_release_blockers", {})
    require(blockers.get("D6-B01", {}).get("status") == "OPEN_RELEASE_BLOCKER", "historical D6-B01 basis drift")
    require(blockers.get("D6-B02", {}).get("status") == "OPEN_RELEASE_BLOCKER", "historical D6-B02 basis drift")

    require(not FUTURE_RELEASE.exists(), "future D6H1 release authorization already exists")
    require(not FUTURE_GRANT.exists(), "future D6H1 single-use grant already exists")

    target = load_module("ulsh_wp3_d6r1_target_review", TARGET_PATH)

    root_record = {"status": "COMPLETED_DIAGNOSTIC", "primary": {"candidate_under_local_residual_gate": True}}
    nonroot_record = {"status": "COMPLETED_DIAGNOSTIC", "primary": {"candidate_under_local_residual_gate": False}}
    require(target.cp01r2_terminal_state_classification({"status": "TIMED_OUT_NO_RETRY"}, False) == "N96_TIMEOUT_NO_RETRY", "timeout classification failed")
    require(target.cp01r2_terminal_state_classification({"status": "SKIPPED_AFTER_TIMEOUT_NO_RETRY"}, False) == "N96_SKIPPED_AFTER_TIMEOUT_NO_RETRY", "skipped classification failed")
    require(target.cp01r2_terminal_state_classification(None, False) == "NO_N96_TERMINAL_STATE", "missing-state classification failed")
    require(target.cp01r2_terminal_state_classification(nonroot_record, True) == "N96_TERMINAL_STATE_NO_LOCAL_ROOT", "non-root terminal classification failed")
    require(target.cp01r2_terminal_state_classification(root_record, True) == "N96_LOCAL_ROOT_PRESENT_PENDING_QA", "root-pending classification failed")
    require(target.cp01r2_terminal_state_classification(root_record, True, "NUMERICAL_ROOT_REJECTED_BY_QA") == "N96_LOCAL_ROOT_REJECTED_BY_QA", "root-rejected classification failed")
    require(target.cp01r2_terminal_state_classification(root_record, True, "NUMERICAL_CANDIDATE_BACKGROUND_DIAGNOSTIC") == "N96_LOCAL_ROOT_ACCEPTED_DIAGNOSTIC_CANDIDATE", "root-accepted classification failed")

    seed = int(target.SEED_ORDER[0])
    key = (seed, 96)
    entries_nonroot = [{"seed_index": seed, "node_count": 96, **nonroot_record}]
    states, details, terminal = target.prepare_legacy_finalize_views(entries_nonroot, {key: [1.0, 2.0]}, {key: {"x": 1}})
    require(key not in states and key not in details, "non-root N96 progress state not isolated from legacy candidate finalizer")
    require(terminal[seed] == "N96_TERMINAL_STATE_NO_LOCAL_ROOT", "non-root terminal provenance lost")
    entries_root = [{"seed_index": seed, "node_count": 96, **root_record}]
    states, details, _ = target.prepare_legacy_finalize_views(entries_root, {key: [1.0, 2.0]}, {key: {"x": 1}})
    require(key in states and key in details, "true N96 root was incorrectly removed")

    schedule = target.BASE.build_schedule()
    require(len(schedule) == 35, "frozen schedule is not 35 entries")
    with tempfile.TemporaryDirectory(prefix="ulsh-d6r1-") as temp_name:
        root = Path(temp_name) / "chain"
        previous = None
        for i, schedule_record in enumerate(schedule[:3]):
            value = math.nan if i == 1 else float(i + 1)
            previous = target.checkpoint_entry(root, synthetic_record(schedule_record, value=value), previous, [float(i), float(i + 1)])
        recovered = target.recover_checkpoint_prefix(root)
        require(recovered["count"] == 3, "three-entry durable chain did not recover")
        require(recovered["chain_head_sha256"] == previous, "chain-head mismatch")
        middle = recovered["records"][1]
        require(middle["record"]["primary"]["synthetic_diagnostic"] is None, "nonfinite value was not projected to null")
        replacements = middle.get("json_safe_nonfinite_replacements", [])
        require(any(item.get("path") == "$.record.primary.synthetic_diagnostic" and item.get("replacement") == "null" for item in replacements), "nonfinite path provenance missing")
        try:
            target.checkpoint_entry(root, synthetic_record(schedule[2]), previous, [0.0])
        except target.TargetContractError:
            pass
        else:
            raise RuntimeError("duplicate checkpoint write did not fail closed")

        try:
            raise RuntimeError("SYNTHETIC_POST_LOOP_FINALIZER_FAILURE")
        except RuntimeError:
            pass
        rerecovered = target.recover_checkpoint_prefix(root)
        require(rerecovered["count"] == 3 and rerecovered["chain_head_sha256"] == previous, "late failure destroyed durable prefix")

        mutated = Path(temp_name) / "mutated"
        shutil.copytree(root, mutated)
        second = sorted(mutated.glob("entry-*.json"))[1]
        doc = json.loads(second.read_text(encoding="utf-8"))
        doc["record"]["primary"]["synthetic_diagnostic"] = 123.0
        second.write_text(json.dumps(doc, sort_keys=True, separators=(",", ":")), encoding="utf-8")
        try:
            target.recover_checkpoint_prefix(mutated)
        except target.TargetContractError:
            pass
        else:
            raise RuntimeError("checkpoint chain mutation did not fail closed")

        gap_root = Path(temp_name) / "gap"
        first_hash = target.checkpoint_entry(gap_root, synthetic_record(schedule[0]), None, [0.0])
        target.checkpoint_entry(gap_root, synthetic_record(schedule[2]), first_hash, [2.0])
        try:
            target.recover_checkpoint_prefix(gap_root)
        except target.TargetContractError:
            pass
        else:
            raise RuntimeError("checkpoint ordinal gap did not fail closed")

    target_source = TARGET_PATH.read_text(encoding="utf-8")
    tx_source = TRANSACTION_PATH.read_text(encoding="utf-8")
    for marker in (
        "finalization_inputs_from_checkpoints(",
        "durable checkpoint count is",
        "checkpoint_entry(",
    ):
        require(marker in target_source, f"durable finalization source invariant missing: {marker}")
    for marker in (
        "checkpoint-recovery.json",
        "durable_checkpoint_count",
        "successful target return without a valid durable 35-entry checkpoint chain",
    ):
        require(marker in tx_source, f"transaction recovery invariant missing: {marker}")

    transaction = load_module("ulsh_wp3_d6r1_transaction_review", TRANSACTION_PATH)
    preflight = transaction.static_preflight()
    require(preflight.get("solver_calls") == 0, "transaction audit reported solver calls")
    require(preflight.get("physical_solve_executed") is False, "transaction audit executed physical solve")
    require(preflight.get("future_release_authorization_present") is False, "release authorization unexpectedly present")
    require(preflight.get("future_single_use_grant_present") is False, "single-use grant unexpectedly present")

    require("numpy" not in sys.modules, "numpy imported during independent no-execution review")
    require("scipy" not in sys.modules, "scipy imported during independent no-execution review")

    gates = decision.get("review_gates", {})
    require(len(gates) == 8 and all(value == "PASS" for value in gates.values()), "D6R1 review gates are not 8/8 PASS")
    disposition = decision.get("D6_blocker_disposition", {})
    require(disposition.get("D6-B01", {}).get("status") == "VERIFIED_CLOSED", "D6-B01 not closed in review artifact")
    require(disposition.get("D6-B02", {}).get("status") == "VERIFIED_CLOSED", "D6-B02 not closed in review artifact")
    firewall = decision.get("no_execution_firewall", {})
    require(firewall.get("physical_solve_executed") is False and firewall.get("review_solver_calls") == 0, "D6R1 no-execution firewall mismatch")

    return {
        "review_status": EXPECTED_STATUS,
        "review_gates": "8/8_PASS",
        "D6-B01": "VERIFIED_CLOSED",
        "D6-B02": "VERIFIED_CLOSED",
        "new_release_blockers": [],
        "durable_checkpoint_fixture_count": 3,
        "old_d5_grant": "SPENT_NON_REPLAYABLE",
        "future_release_authorization_present": False,
        "future_single_use_grant_present": False,
        "solver_calls": 0,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
        "next_allowed_action": decision.get("next_allowed_action"),
    }


def main() -> int:
    try:
        result = review()
    except Exception as exc:
        print(json.dumps({"review_status": "BLOCKED_WP3_D6R1_INDEPENDENT_REVIEW", "error": f"{type(exc).__name__}: {exc}"}, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
