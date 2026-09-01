#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/2026-08-27_hzt_m0_s6_c_phys_m1_ulsh01_wp2_cp01r4_target_release_v0.2.py"

spec = importlib.util.spec_from_file_location("ulsh01_wp2_cp01r4_release_v02", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def expect_error(exc_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc_type:
        return
    raise AssertionError(f"expected {exc_type.__name__}")


def test_full_v02_preflight_is_nonexecuting_and_16_member_bound():
    before_imports = module.BASE.BACKEND_IMPORT_COUNT
    before_solves = module.BASE.SOLVER_CALL_COUNT
    with tempfile.TemporaryDirectory() as td:
        manifest_path = Path(td) / "manifest.json"
        result = module.review(ROOT, manifest_path)
        assert result["status"] == "PASS_CP01R4_RELEASE_V02_PREFLIGHT_IMPLEMENTATION_ONLY"
        assert result["release_package_member_count"] == 16
        assert result["method_freeze_complete"] is True
        assert result["barycentric_prolongation_synthetic_QA"] == "PASS"
        assert result["git_head_binding_implemented"] is True
        assert result["result_no_overwrite_implemented"] is True
        assert result["memory_limit_mutated_during_audit"] is False
        assert result["backend_imported"] is False
        assert result["solver_executed"] is False
        assert result["physical_execution_authorized"] is False
        assert result["WP2_closed"] is False
        assert result["WP3_started"] is False
        assert result["WP4_started"] is False
        assert result["physical_evidence_effect"] == "NONE"
        assert re.fullmatch(r"[0-9a-f]{40}", result["release_subject_git_head_sha"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["run_id"] == module.RUN_ID
        assert manifest["run_payload_sha256"] == module.RUN_PAYLOAD_SHA256
        assert manifest["target_contract_digest_sha256"] == module.TARGET_DIGEST
        assert manifest["backend_imported"] is False
        assert manifest["solver_executed"] is False
        assert manifest["physical_evidence_effect"] == "NONE"
        assert len(manifest["member_sha256"]) == 16
        assert len(manifest["package_digest_sha256"]) == 64
    assert module.BASE.BACKEND_IMPORT_COUNT == before_imports == 0
    assert module.BASE.SOLVER_CALL_COUNT == before_solves == 0


def test_synthetic_barycentric_and_grant_replay_remain_backend_free():
    module.BASE.validate_synthetic_prolongation()
    with tempfile.TemporaryDirectory() as td:
        result = module.synthetic_authorization_replay_qa(ROOT, Path(td))
        assert result["status"] == "PASS_SYNTHETIC_DECISION_GRANT_BINDING_AND_REPLAY_QA"
        assert result["replay_rejected"] is True
        assert result["backend_imported"] is False
        assert result["solver_executed"] is False
        assert result["memory_limit_mutated"] is False
    assert module.BASE.BACKEND_IMPORT_COUNT == 0
    assert module.BASE.SOLVER_CALL_COUNT == 0


def test_git_head_sha_uses_actual_temporary_repository_head():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "qa@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "ULSH QA"], check=True)
        (repo / "probe.txt").write_text("probe\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "probe.txt"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "probe"], check=True)
        expected = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip().lower()
        assert module.git_head_sha(repo) == expected
        assert re.fullmatch(r"[0-9a-f]{40}", expected)
    assert module.BASE.BACKEND_IMPORT_COUNT == 0
    assert module.BASE.SOLVER_CALL_COUNT == 0


def test_memory_limit_inspection_does_not_mutate_ci_process():
    policy = module.BASE.load_json(ROOT / module.BASE.RESOURCE_POLICY_PATH)
    if module.resource is None or not hasattr(module.resource, "RLIMIT_AS"):
        plan = module.inspect_process_memory_limit(policy)
        assert plan["supported"] is False
        return
    before = module.resource.getrlimit(module.resource.RLIMIT_AS)
    plan = module.inspect_process_memory_limit(policy)
    after = module.resource.getrlimit(module.resource.RLIMIT_AS)
    assert before == after
    assert plan["supported"] is True
    assert plan["mutated"] is False
    assert plan["requested_bytes"] == 8589934592
    assert plan["proposed_soft"] <= 8589934592
    assert module.BASE.BACKEND_IMPORT_COUNT == 0
    assert module.BASE.SOLVER_CALL_COUNT == 0


def test_exclusive_result_write_refuses_overwrite_without_solver_surface():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "result.json"
        module.exclusive_result_write(path, b"{\"probe\":true}\n", 1024)
        first = path.read_bytes()
        expect_error(module.ReleaseError, module.exclusive_result_write, path, b"changed\n", 1024)
        assert path.read_bytes() == first
    assert module.BASE.BACKEND_IMPORT_COUNT == 0
    assert module.BASE.SOLVER_CALL_COUNT == 0


def test_operational_command_without_decision_grant_is_denied_preimport():
    rc = module.main(["run", "--repo-root", str(ROOT), "--json"])
    assert rc == module.EXIT_NOT_AUTHORIZED
    assert module.BASE.BACKEND_IMPORT_COUNT == 0
    assert module.BASE.SOLVER_CALL_COUNT == 0


def test_static_order_reservation_then_resource_limit_then_primary_backend():
    source = MODULE_PATH.read_text(encoding="utf-8")
    start = source.index("def execute_authorized")
    end = source.index("\ndef parse_args", start)
    body = source[start:end]
    no_overwrite_at = body.index("result_output.exists")
    reserve_at = body.index("BASE.atomic_reserve_grant")
    limit_at = body.index("apply_process_resource_limits")
    execute_at = body.index("BASE.execute_primary_target")
    exclusive_write_at = body.index("exclusive_result_write")
    assert no_overwrite_at < reserve_at < limit_at < execute_at < exclusive_write_at
    assert "BASE._load_primary_backend" not in body
    assert "shooting_residual" not in body
    assert "independent_backend" not in body
    assert module.BASE.BACKEND_IMPORT_COUNT == 0
    assert module.BASE.SOLVER_CALL_COUNT == 0


def test_release_v02_does_not_change_cp01r4_payload_or_target_digest():
    run_input = module.BASE.load_json(ROOT / module.BASE.RUN_INPUT_PATH)
    payload = run_input["frozen_run_payload"]
    assert module.BASE.canonical_sha256(payload) == module.RUN_PAYLOAD_SHA256
    assert module.RUN_PAYLOAD_SHA256 == "8e5976a22c4be78b5e4fe7834c9947de8a4acea7781363c7aeb83aa73982ac8c"
    assert payload["target_contract_digest_sha256"] == module.TARGET_DIGEST
    assert payload["model_parameters_ordered"]["a_F"] == "1/4"
    assert module.BASE.BACKEND_IMPORT_COUNT == 0
    assert module.BASE.SOLVER_CALL_COUNT == 0


if __name__ == "__main__":
    test_full_v02_preflight_is_nonexecuting_and_16_member_bound()
    test_synthetic_barycentric_and_grant_replay_remain_backend_free()
    test_git_head_sha_uses_actual_temporary_repository_head()
    test_memory_limit_inspection_does_not_mutate_ci_process()
    test_exclusive_result_write_refuses_overwrite_without_solver_surface()
    test_operational_command_without_decision_grant_is_denied_preimport()
    test_static_order_reservation_then_resource_limit_then_primary_backend()
    test_release_v02_does_not_change_cp01r4_payload_or_target_digest()
    print("ULSH-01 WP2 CP01R4 release hardening QA v0.2: PASS (NO BACKEND IMPORT / NO SOLVER EXECUTION)")
