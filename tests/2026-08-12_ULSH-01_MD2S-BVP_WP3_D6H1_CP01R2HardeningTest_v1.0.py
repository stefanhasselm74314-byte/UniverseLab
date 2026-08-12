#!/usr/bin/env python3
"""No-execution regression tests for ULSH-01 / WP3-D6H1.

The suite exercises only source/audit, deterministic classification and synthetic
filesystem checkpoint logic. It must not import NumPy/SciPy or call a solver.
"""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TARGET_PATH = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d6h1_cp01r2_target_v1.1.py"
TX_PATH = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d6h1_cp01r2_transaction_v1.2.py"
RELEASE_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2_PhysicalSolveReleaseAuthorization_v2.0.json"
GRANT_PATH = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2_SingleUseExecutionGrant_v2.0.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


TARGET = load(TARGET_PATH, "wp3_d6h1_target_test")
TX = load(TX_PATH, "wp3_d6h1_tx_test")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def record_from_schedule(index: int, **extra):
    base = dict(TARGET.BASE.build_schedule()[index])
    base.update({
        "status": "COMPLETED",
        "primary": {"converged": False, "candidate_under_local_residual_gate": False, "failure": None},
        "newton_history": [],
        "independent": None,
    })
    base.update(extra)
    return base


def test_terminal_classification_total() -> None:
    nonroot = record_from_schedule(4)
    require(TARGET.cp01r2_terminal_state_classification(nonroot, True) == "N96_TERMINAL_STATE_NO_LOCAL_ROOT", "non-root N96 state classification failed")
    root = record_from_schedule(4, primary={"converged": True, "candidate_under_local_residual_gate": True, "failure": None})
    require(TARGET.cp01r2_terminal_state_classification(root, True) == "N96_LOCAL_ROOT_PRESENT_PENDING_QA", "root pending-QA classification failed")
    require(TARGET.cp01r2_terminal_state_classification(root, True, "NUMERICAL_ROOT_REJECTED_BY_QA") == "N96_LOCAL_ROOT_REJECTED_BY_QA", "rejected-root classification failed")
    require(TARGET.cp01r2_terminal_state_classification(root, True, "NUMERICAL_CANDIDATE_BACKGROUND_DIAGNOSTIC") == "N96_LOCAL_ROOT_ACCEPTED_DIAGNOSTIC_CANDIDATE", "accepted-root classification failed")
    require(TARGET.cp01r2_terminal_state_classification(nonroot, False) == "NO_N96_TERMINAL_STATE", "missing-state classification failed")
    timed = record_from_schedule(4, status="TIMED_OUT_NO_RETRY")
    require(TARGET.cp01r2_terminal_state_classification(timed, False) == "N96_TIMEOUT_NO_RETRY", "timeout classification failed")
    skipped = record_from_schedule(4, status="SKIPPED_AFTER_TIMEOUT_NO_RETRY")
    require(TARGET.cp01r2_terminal_state_classification(skipped, False) == "N96_SKIPPED_AFTER_TIMEOUT_NO_RETRY", "skipped classification failed")


def test_legacy_view_normalizes_nonroot_only() -> None:
    records = [record_from_schedule(4)]
    states = {(0, 96): [1.0]}
    details = {(0, 96): {"dummy": True}}
    safe_states, safe_details, terminal = TARGET.prepare_legacy_finalize_views(records, states, details)
    require((0, 96) not in safe_states and (0, 96) not in safe_details, "non-root N96 progress state not normalized out of legacy view")
    require(terminal[0] == "N96_TERMINAL_STATE_NO_LOCAL_ROOT", "terminal provenance lost during normalization")

    root_record = record_from_schedule(4, primary={"converged": True, "candidate_under_local_residual_gate": True, "failure": None})
    safe_states, safe_details, _ = TARGET.prepare_legacy_finalize_views([root_record], states, details)
    require((0, 96) in safe_states and (0, 96) in safe_details, "actual N96 root was incorrectly removed")


def write_prefix(root: Path, count: int) -> dict:
    previous = None
    for index in range(count):
        record = record_from_schedule(index, diagnostic={"synthetic": float("inf") if index == 0 else float(index)})
        previous = TARGET.checkpoint_entry(root, record, previous, terminal_state=[index + 0.25, index + 0.5])
    return TARGET.recover_checkpoint_prefix(root)


def test_checkpoint_chain_and_nonfinite_projection() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "checkpoints"
        recovered = write_prefix(root, 3)
        require(recovered["count"] == 3, "three-entry durable prefix not recovered")
        require(isinstance(recovered["chain_head_sha256"], str) and len(recovered["chain_head_sha256"]) == 64, "chain head missing")
        first = recovered["records"][0]
        require(first["record"]["diagnostic"]["synthetic"] is None, "nonfinite checkpoint diagnostic was not projected to null")
        paths = [row["path"] for row in first["json_safe_nonfinite_replacements"]]
        require("$.record.diagnostic.synthetic" in paths, "nonfinite checkpoint provenance path missing")
        state = json.loads((root / "state.json").read_text(encoding="utf-8"))
        require(state["durable_checkpoint_count"] == 3, "checkpoint state pointer count mismatch")
        require(state["last_checkpoint_sha256"] == recovered["chain_head_sha256"], "checkpoint state pointer chain mismatch")


def test_duplicate_checkpoint_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "checkpoints"
        first = record_from_schedule(0)
        digest = TARGET.checkpoint_entry(root, first, None, terminal_state=[1.0])
        require(len(digest) == 64, "first checkpoint did not hash")
        try:
            TARGET.checkpoint_entry(root, first, None, terminal_state=[1.0])
        except TARGET.TargetContractError:
            pass
        else:
            raise AssertionError("duplicate checkpoint write did not fail closed")


def test_gap_and_chain_mutation_fail_closed() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "gap"
        write_prefix(root, 3)
        files = sorted(root.glob("entry-*.json"))
        files[1].unlink()
        try:
            TARGET.recover_checkpoint_prefix(root)
        except TARGET.TargetContractError:
            pass
        else:
            raise AssertionError("checkpoint gap did not fail closed")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "chain"
        write_prefix(root, 3)
        files = sorted(root.glob("entry-*.json"))
        second = json.loads(files[1].read_text(encoding="utf-8"))
        second["record"]["synthetic_mutation"] = True
        files[1].write_text(json.dumps(second, sort_keys=True, separators=(",", ":")), encoding="utf-8")
        try:
            TARGET.recover_checkpoint_prefix(root)
        except TARGET.TargetContractError:
            pass
        else:
            raise AssertionError("checkpoint hash-chain mutation did not fail closed")


def test_checkpoint_prefix_survives_later_failure() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "checkpoints"
        write_prefix(root, 5)
        try:
            raise RuntimeError("synthetic post-loop/finalizer failure")
        except RuntimeError:
            pass
        recovered = TARGET.recover_checkpoint_prefix(root)
        require(recovered["count"] == 5, "later failure erased durable checkpoint prefix")


def test_finalization_inputs_are_rebuilt_from_checkpoint_records() -> None:
    class FakeNP:
        @staticmethod
        def asarray(values, dtype=float):
            return [dtype(value) for value in values]

    class FakePrimary:
        @staticmethod
        def residual(state, node_count, model, sector):
            return [], {"recomputed": True, "node_count": node_count, "state": list(state)}

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "checkpoints"
        recovered = write_prefix(root, 3)
        entries, states, details, independent = TARGET.finalization_inputs_from_checkpoints(
            recovered, FakePrimary(), object(), object(), FakeNP
        )
        require(len(entries) == 3, "persisted matrix entries not rebuilt")
        require((0, 24) in states and (0, 32) in states and (0, 48) in states, "terminal states not rebuilt from checkpoint vectors")
        require(details[(0, 24)]["recomputed"] is True, "residual details not recomputed from persisted terminal state")
        require(independent == {}, "unexpected synthetic independent record")
        require("write_ahead_terminal_state" not in entries[0], "checkpoint-only terminal state leaked into canonical matrix record")


def test_no_execution_firewall() -> None:
    target_audit = TARGET.audit_target()
    tx_audit = TX.static_preflight()
    require(target_audit["status"] == "PASS_WP3_D6H1_CP01R2_TARGET_HARDENING_NO_EXECUTION", "target audit failed")
    require(tx_audit["status"] == "PASS_WP3_D6H1_CP01R2_TRANSACTION_HARDENING_NO_EXECUTION", "transaction audit failed")
    require(not RELEASE_PATH.exists() and not GRANT_PATH.exists(), "future runtime issuance artifact exists during D6H1")
    try:
        TX.execute(Path(tempfile.gettempdir()) / "ulsh-d6h1-no-exec-should-deny")
    except TX.AuthorizationDenied:
        pass
    else:
        raise AssertionError("transaction execute did not fail closed without future release/grant")
    require("numpy" not in sys.modules and "scipy" not in sys.modules, "D6H1 audit/no-authorization path imported a numerical backend")


def main() -> int:
    test_terminal_classification_total()
    test_legacy_view_normalizes_nonroot_only()
    test_checkpoint_chain_and_nonfinite_projection()
    test_duplicate_checkpoint_fails_closed()
    test_gap_and_chain_mutation_fail_closed()
    test_checkpoint_prefix_survives_later_failure()
    test_finalization_inputs_are_rebuilt_from_checkpoint_records()
    test_no_execution_firewall()
    print("PASS_WP3_D6H1_CP01R2_HARDENING_TEST_NO_EXECUTION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
