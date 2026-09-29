#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/2026-08-27_hzt_m0_s6_c_phys_m1_ulsh01_wp2_cp01r4_target_release_v0.1.py"
spec = importlib.util.spec_from_file_location("ulsh01_wp2_cp01r4_release", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def expect_error(exc_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc_type:
        return
    raise AssertionError(f"expected {exc_type.__name__}")


def test_full_release_preflight_no_backend_import():
    with tempfile.TemporaryDirectory() as td:
        manifest_path = Path(td) / "manifest.json"
        result = module.review(ROOT, manifest_path)
        assert result["status"] == "PASS_CP01R4_RELEASE_PREFLIGHT_IMPLEMENTATION_ONLY"
        assert result["method_freeze_complete"] is True
        assert result["barycentric_prolongation_synthetic_QA"] == "PASS"
        assert result["backend_imported"] is False
        assert result["solver_executed"] is False
        assert result["physical_execution_authorized"] is False
        assert result["WP2_closed"] is False
        assert result["WP3_started"] is False
        assert result["WP4_started"] is False
        assert result["physical_evidence_effect"] == "NONE"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["run_id"] == module.RUN_ID
        assert manifest["run_payload_sha256"] == module.RUN_PAYLOAD_SHA256
        assert manifest["target_contract_digest_sha256"] == module.TARGET_DIGEST
        assert manifest["backend_imported"] is False
        assert manifest["solver_executed"] is False
        assert len(manifest["member_sha256"]) == 15
        assert len(manifest["package_digest_sha256"]) == 64
    assert module.BACKEND_IMPORT_COUNT == 0
    assert module.SOLVER_CALL_COUNT == 0


def test_barycentric_prolongation_exact_low_order_polynomial():
    module.validate_synthetic_prolongation()
    for old_count, new_count in ((24, 32), (32, 48), (48, 64), (64, 96)):
        source_nodes = module.tau_nodes(old_count)
        source = [2.0 + 0.5*t - 4.0*t*t + t**3 for t in source_nodes]
        got = module.barycentric_interpolate(source, old_count, new_count)
        expected = [2.0 + 0.5*t - 4.0*t*t + t**3 for t in module.tau_nodes(new_count)]
        assert max(abs(a-b) for a, b in zip(got, expected)) <= 2.0e-12
    assert module.BACKEND_IMPORT_COUNT == 0
    assert module.SOLVER_CALL_COUNT == 0


def test_synthetic_decision_grant_binding_replay_and_individual_token_reuse():
    _, _, manifest, bindings = module.preflight(ROOT)
    commit = "a" * 40
    now = datetime(2026, 8, 27, 12, 0, tzinfo=timezone.utc)
    decision = module.make_synthetic_control_decision(manifest, bindings, commit)
    decision_id = module.verify_decision(decision, manifest, bindings, commit, now)
    decision_sha = module.canonical_sha256(decision)
    grant = module.make_synthetic_control_grant(manifest, bindings, commit, decision_id, decision_sha)
    verified = module.verify_grant(grant, decision_id, decision_sha, manifest, bindings, commit, now, control_only=True)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        record = module.atomic_reserve_grant(root, verified, control_only=True)
        assert record.is_file()
        payload = json.loads(record.read_text(encoding="utf-8"))
        assert payload["state"] == "RESERVED"
        assert payload["control_only"] is True
        assert payload["backend_imported"] is False
        assert payload["solver_executed"] is False
        expect_error(module.ReplayError, module.atomic_reserve_grant, root, verified, control_only=True)
        # Same grant_id with a new nonce must also be rejected because grant_id reuse is forbidden.
        changed_nonce = dict(verified)
        changed_nonce["nonce"] = "different-synthetic-nonce"
        expect_error(module.ReplayError, module.atomic_reserve_grant, root, changed_nonce, control_only=True)
    assert module.BACKEND_IMPORT_COUNT == 0
    assert module.SOLVER_CALL_COUNT == 0


def test_fail_closed_binding_checks():
    _, _, manifest, bindings = module.preflight(ROOT)
    commit = "a" * 40
    now = datetime(2026, 8, 27, 12, 0, tzinfo=timezone.utc)
    decision = module.make_synthetic_control_decision(manifest, bindings, commit)
    decision_id = module.verify_decision(decision, manifest, bindings, commit, now)
    decision_sha = module.canonical_sha256(decision)
    grant = module.make_synthetic_control_grant(manifest, bindings, commit, decision_id, decision_sha)

    bad = dict(grant)
    bad["run_payload_sha256"] = "0" * 64
    expect_error(module.ReleaseError, module.verify_grant, bad, decision_id, decision_sha, manifest, bindings, commit, now, control_only=True)

    bad = dict(grant)
    bad["release_package_manifest_sha256"] = "0" * 64
    expect_error(module.ReleaseError, module.verify_grant, bad, decision_id, decision_sha, manifest, bindings, commit, now, control_only=True)

    bad = dict(grant)
    bad["repository_commit_sha"] = "b" * 40
    expect_error(module.ReleaseError, module.verify_grant, bad, decision_id, decision_sha, manifest, bindings, commit, now, control_only=True)

    bad = dict(grant)
    bad["not_before_utc"] = "2026-08-28T00:00:00Z"
    bad["expires_at_utc"] = "2026-08-29T00:00:00Z"
    expect_error(module.AuthorizationError, module.verify_grant, bad, decision_id, decision_sha, manifest, bindings, commit, now, control_only=True)

    bad_decision = json.loads(json.dumps(decision))
    bad_decision["decision"]["wp3_authorized"] = True
    expect_error(module.ReleaseError, module.verify_decision, bad_decision, manifest, bindings, commit, now)
    assert module.BACKEND_IMPORT_COUNT == 0
    assert module.SOLVER_CALL_COUNT == 0


def test_run_without_operational_artifacts_denied_before_backend_import():
    rc = module.main(["run", "--repo-root", str(ROOT), "--json"])
    assert rc == module.EXIT_NOT_AUTHORIZED
    assert module.BACKEND_IMPORT_COUNT == 0
    assert module.SOLVER_CALL_COUNT == 0


def test_static_reservation_precedes_execution_call():
    source = MODULE_PATH.read_text(encoding="utf-8")
    function_start = source.index("def execute_authorized")
    function_end = source.index("\ndef parse_args", function_start)
    body = source[function_start:function_end]
    reserve_at = body.index("atomic_reserve_grant")
    execute_at = body.index("execute_primary_target")
    assert reserve_at < execute_at
    assert "_load_primary_backend" not in body
    assert "independent_backend" not in body
    assert module.BACKEND_IMPORT_COUNT == 0
    assert module.SOLVER_CALL_COUNT == 0


if __name__ == "__main__":
    test_full_release_preflight_no_backend_import()
    test_barycentric_prolongation_exact_low_order_polynomial()
    test_synthetic_decision_grant_binding_replay_and_individual_token_reuse()
    test_fail_closed_binding_checks()
    test_run_without_operational_artifacts_denied_before_backend_import()
    test_static_reservation_precedes_execution_call()
    print("ULSH-01 WP2 CP01R4 release QA: PASS (NO BACKEND IMPORT / NO SOLVER EXECUTION)")
