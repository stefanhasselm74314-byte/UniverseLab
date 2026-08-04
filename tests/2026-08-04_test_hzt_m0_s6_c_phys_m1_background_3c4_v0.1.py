#!/usr/bin/env python3
"""Regression tests for the fail-closed Background-3C4 execution package."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_execution_runner_v0.1.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("background3c4_runner_tests", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to import runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def expect_raises(error_type, function, *args, **kwargs):
    try:
        function(*args, **kwargs)
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


def main():
    runner = load_runner()
    audit = runner.audit_package()
    assert audit["primary_root_calls"] == 0
    assert audit["independent_root_calls"] == 0

    completed = subprocess.run(
        [sys.executable, str(RUNNER_PATH), "run", "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == runner.EXIT_NOT_AUTHORIZED
    payload = json.loads(completed.stdout)
    assert payload["status"] == "NOT_AUTHORIZED"
    assert payload["solver_calls"] == 0
    assert payload["result_artifact_created"] is False

    expected_output = ROOT / "artifacts/hzt-m0/md2s/background3c" / runner.RUN_ID
    assert not expected_output.exists()

    with tempfile.TemporaryDirectory(prefix="bg3c4-grants-") as temporary:
        temp = Path(temporary)
        base = {
            "schema": "universelab.hzt-m0-s6-c-phys-m1.background-3c-execution-authorization.v0.2",
            "status": "GRANTED",
            "authorized": True,
            "run_id": runner.RUN_ID,
            "run_payload_sha256": runner.RUN_PAYLOAD_SHA256,
            "authorization_decision_id": "UL-DEC-TEST-ONLY",
            "execution_package_manifest_sha256": audit["package_manifest_sha256"],
            "scope": "SINGLE_CP01R1_EXECUTION_NO_RETRY_NO_SCAN",
        }
        bad_digest = copy.deepcopy(base)
        bad_digest["execution_package_manifest_sha256"] = "0" * 64
        bad_digest_path = temp / "bad-digest.json"
        bad_digest_path.write_text(json.dumps(bad_digest), encoding="utf-8")
        expect_raises(
            runner.AuthorizationDenied,
            runner.GrantVerifier(audit["package_manifest_sha256"]).verify,
            bad_digest_path,
        )

        bad_scope = copy.deepcopy(base)
        bad_scope["scope"] = "PARAMETER_SCAN"
        bad_scope_path = temp / "bad-scope.json"
        bad_scope_path.write_text(json.dumps(bad_scope), encoding="utf-8")
        expect_raises(
            runner.AuthorizationDenied,
            runner.GrantVerifier(audit["package_manifest_sha256"]).verify,
            bad_scope_path,
        )

    cases = [
        ({"execution_started": False, "not_executed_reason": "INPUT"}, "NOT_EXECUTED_INPUT_CONTRACT_FAILURE"),
        ({"execution_started": False, "not_executed_reason": "AUTHORIZATION"}, "NOT_EXECUTED_AUTHORIZATION_FAILURE"),
        ({"execution_started": True, "accepted_candidate_count": 0, "rejected_root_count": 0}, "NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL"),
        ({"execution_started": True, "accepted_candidate_count": 1, "rejected_root_count": 0}, "NUMERICAL_CANDIDATE_BACKGROUND_DIAGNOSTIC"),
        ({"execution_started": True, "accepted_candidate_count": 2, "rejected_root_count": 0}, "MULTIPLE_NUMERICAL_CANDIDATE_BACKGROUNDS_DIAGNOSTIC"),
        ({"execution_started": True, "accepted_candidate_count": 0, "rejected_root_count": 1}, "NUMERICAL_ROOT_REJECTED_BY_QA"),
    ]
    for summary, expected in cases:
        assert runner.ClassificationEngine.classify(summary) == expected

    with tempfile.TemporaryDirectory(prefix="bg3c4-writer-") as temporary:
        root = Path(temporary)
        final = root / "result"
        with runner.AtomicResultWriter(final, 1024 * 1024) as writer:
            writer.commit({"schema": "test", "run_id": runner.RUN_ID})
        assert final.is_dir()
        expect_raises(runner.ArtifactFailure, runner.AtomicResultWriter(final, 1024).__enter__)

        final2 = root / "interrupted"
        with runner.AtomicResultWriter(final2, 1024 * 1024) as writer:
            partial = writer.interrupt("SIGTERM_TEST")
        assert not final2.exists()
        assert (partial / "partial.json").is_file()

    expect_raises(
        runner.AuthorizationDenied,
        runner.PrimaryRootAdapter(None).solve,
        None, 24, None, None,
    )
    expect_raises(
        runner.AuthorizationDenied,
        runner.IndependentRootAdapter(None).solve,
        None, None, None, epsilon=1e-3,
    )

    print("PASS: Background-3C4 fail-closed execution-package regression tests")


if __name__ == "__main__":
    main()
