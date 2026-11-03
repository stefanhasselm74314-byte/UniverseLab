#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/2026-08-27_hzt_m0_s6_c_phys_m1_ulsh01_wp2_target_transaction_v0.1.py"

spec = importlib.util.spec_from_file_location("ulsh01_wp2_transaction", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def expect_error(exc_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc_type:
        return
    raise AssertionError(f"expected {exc_type.__name__}")


def test_full_nonexecuting_preflight():
    with tempfile.TemporaryDirectory() as td:
        manifest_path = Path(td) / "release_manifest.json"
        out = module.review(ROOT, manifest_path)
        assert out["status"] == "PASS_WP2_TRANSACTION_PREFLIGHT_IMPLEMENTATION_ONLY"
        assert out["physical_execution_authorized"] is False
        assert out["backend_imported"] is False
        assert out["solver_executed"] is False
        assert out["WP2_closed"] is False
        assert out["WP3_started"] is False
        assert out["WP4_started"] is False
        assert out["physical_evidence_effect"] == "NONE"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["target_contract_digest_sha256"] == module.TARGET_DIGEST
        assert manifest["run_payload_sha256"] == module.RUN_PAYLOAD_SHA256
        assert manifest["solver_executed"] is False
        assert manifest["backend_imported"] is False
        assert len(manifest["package_digest_sha256"]) == 64
        assert len(manifest["member_sha256"]) >= 13


def make_control_grant(package_digest: str) -> dict:
    return {
        "grant_id": "CONTROL-GRANT-0001",
        "authorization_decision_id": "CONTROL-DECISION-0001",
        "nonce": "control-nonce-unique-0001",
        "not_before_utc": "2026-08-27T00:00:00Z",
        "expires_at_utc": "2026-08-28T00:00:00Z",
        "single_use": True,
        "scope": "SYNTHETIC_CONTROL_ONLY_NO_BACKEND_IMPORT",
        "control_only": True,
        "authorized": False,
        "repository_commit_sha": "a" * 40,
        "target_contract_digest_sha256": module.TARGET_DIGEST,
        "run_payload_sha256": module.RUN_PAYLOAD_SHA256,
        "release_package_manifest_sha256": package_digest,
        "dependency_lock_sha256": module.DEPENDENCY_LOCK_SHA256,
        "primary_source_sha256": module.PRIMARY_SHA256,
        "primary_base_source_sha256": module.PRIMARY_BASE_SHA256,
        "independent_source_sha256": module.INDEPENDENT_SHA256,
        "target_a_F": "1/4",
        "control_override_allowed": False,
        "automatic_authorization": False,
    }


def test_control_grant_binding_and_single_use_replay():
    tx = module.load_json(ROOT / "registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_TargetTransactionContract_v0.1.json")
    manifest = module.build_release_manifest(ROOT, tx)
    grant = make_control_grant(manifest["package_digest_sha256"])
    now = datetime(2026, 8, 27, 12, 0, tzinfo=timezone.utc)
    module.validate_grant_bindings(
        grant,
        manifest,
        repository_commit_sha="a" * 40,
        now=now,
        control_only=True,
    )
    with tempfile.TemporaryDirectory() as td:
        reservation = module.atomic_reserve_control_grant(td, grant)
        assert reservation.is_file()
        record = json.loads(reservation.read_text(encoding="utf-8"))
        assert record["state"] == "RESERVED"
        assert record["control_only"] is True
        assert record["backend_imported"] is False
        assert record["solver_executed"] is False
        expect_error(module.ReplayError, module.atomic_reserve_control_grant, td, grant)


def test_control_grant_binding_fail_closed():
    tx = module.load_json(ROOT / "registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_TargetTransactionContract_v0.1.json")
    manifest = module.build_release_manifest(ROOT, tx)
    now = datetime(2026, 8, 27, 12, 0, tzinfo=timezone.utc)
    grant = make_control_grant(manifest["package_digest_sha256"])

    bad = dict(grant)
    bad["target_contract_digest_sha256"] = "0" * 64
    expect_error(module.TransactionError, module.validate_grant_bindings, bad, manifest, repository_commit_sha="a" * 40, now=now, control_only=True)

    bad = dict(grant)
    bad["release_package_manifest_sha256"] = "0" * 64
    expect_error(module.TransactionError, module.validate_grant_bindings, bad, manifest, repository_commit_sha="a" * 40, now=now, control_only=True)

    bad = dict(grant)
    bad["not_before_utc"] = "2026-08-28T00:00:00Z"
    bad["expires_at_utc"] = "2026-08-29T00:00:00Z"
    expect_error(module.TransactionError, module.validate_grant_bindings, bad, manifest, repository_commit_sha="a" * 40, now=now, control_only=True)

    physical = dict(grant)
    physical["control_only"] = False
    physical["scope"] = f"{module.RUN_ID}_TARGET_ONLY"
    physical["authorized"] = True
    with tempfile.TemporaryDirectory() as td:
        expect_error(module.TransactionError, module.atomic_reserve_control_grant, td, physical)


def test_no_real_backend_import_or_solver_surface():
    source = MODULE_PATH.read_text(encoding="utf-8")
    forbidden = ["importlib", "subprocess", "solve_bvp", "scipy", "damped_newton(", "shooting_residual("]
    for token in forbidden:
        assert token not in source, token
    assert module.PHYSICAL_EXECUTION_AUTHORIZED is False
    assert module.PHYSICAL_BACKEND_IMPORT_ALLOWED is False
    assert module.TARGET_SOLVE_ALLOWED is False
    assert module.PHYSICAL_RESULT_CREATION_ALLOWED is False


if __name__ == "__main__":
    test_full_nonexecuting_preflight()
    test_control_grant_binding_and_single_use_replay()
    test_control_grant_binding_fail_closed()
    test_no_real_backend_import_or_solver_surface()
    print("ULSH-01 WP2 CP01R2 transaction QA: PASS (NO BACKEND IMPORT / NO SOLVER EXECUTION)")
