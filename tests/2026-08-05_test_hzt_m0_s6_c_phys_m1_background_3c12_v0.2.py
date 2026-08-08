#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c12_v0.2.py"
RELEASE_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c12_target_path_release_v0.2.py"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def expect_grant_rejection(callable_value, expected_text: str) -> None:
    try:
        callable_value()
    except Exception as exc:
        if expected_text not in str(exc):
            raise AssertionError(f"unexpected rejection: {exc}") from exc
    else:
        raise AssertionError("invalid grant or request was accepted")


def main() -> None:
    validator = load("background3c12_validator_v02_test", VALIDATOR_PATH)
    release = load("background3c12_release_v02_test", RELEASE_PATH)

    result = validator.validate()
    assert result["status"] == "PASS"
    assert result["audit_status"] == "PASS_3C12_V02_STATIC_AUDIT_NO_BACKEND_IMPORT_NO_EXECUTION"
    assert result["control_status"] == "PASS_3C12_V02_NONOPERATIVE_GRANT_AND_TARGET_PATH_CONTROLS"
    assert result["source_count"] == 18
    assert result["target_run_id"] == release.BASE.TARGET_RUN_ID
    assert result["target_a_F"] == release.BASE.TARGET_A_F
    assert result["schedule_entry_count"] == 35
    assert result["schedule_sha256"] == release.BASE.SCHEDULE_SHA256
    assert result["terminal_states"] == release.BASE.TERMINAL_BY_OUTCOME
    assert result["worker_launch_count"] == 5
    assert result["replay_rejections"] == 6
    assert result["parallel_reservation_race"] == "PASS_EXACTLY_ONE_WINNER"
    assert result["invalid_rejections"] == [
        "binding", "control_override", "digest", "expired", "not_before", "operative",
    ]
    assert result["physical_backend_imports"] == 0
    assert result["physical_solver_calls"] == 0
    assert result["cp01r1_attempts"] == 0
    assert result["target_solves"] == 0
    assert result["operative_grants"] == 0
    assert result["physical_result_artifacts"] == 0
    assert result["physical_evidence_effect"] == "NONE"

    binding = release.expected_binding()
    now = datetime.now(timezone.utc)
    grant = release.issue_synthetic_grant(binding, now=now)
    assert grant["issued_at_utc"] == grant["not_before_utc"]

    missing = dict(grant)
    missing.pop("nonce")
    expect_grant_rejection(
        lambda: release.BASE.validate_grant(missing, binding, now=now),
        "field set drift",
    )

    unknown = dict(grant)
    unknown["unknown_field"] = "forbidden"
    expect_grant_rejection(
        lambda: release.BASE.validate_grant(unknown, binding, now=now),
        "field set drift",
    )

    with tempfile.TemporaryDirectory(prefix="universelab-bg3c12-test-") as temporary:
        store = release.BASE.GrantStateStore(Path(temporary) / "states")

        wrong_a_f_grant = release.issue_synthetic_grant(binding, now=now)
        wrong_a_f = release.target_request("success")
        wrong_a_f["target_a_F"] = "0"
        before = list(store.root.iterdir())
        expect_grant_rejection(
            lambda: release.BASE.execute_synthetic_transaction(
                wrong_a_f_grant, wrong_a_f, store, binding, now=now,
            ),
            "a_F drift",
        )
        assert list(store.root.iterdir()) == before

        wrong_schedule_grant = release.issue_synthetic_grant(binding, now=now)
        wrong_schedule = release.target_request("success")
        wrong_schedule["schedule_sha256"] = "0" * 64
        before = list(store.root.iterdir())
        expect_grant_rejection(
            lambda: release.BASE.execute_synthetic_transaction(
                wrong_schedule_grant, wrong_schedule, store, binding, now=now,
            ),
            "schedule drift",
        )
        assert list(store.root.iterdir()) == before

        override_grant = release.issue_synthetic_grant(binding, now=now)
        override = release.target_request("success")
        override["model_override"] = {"a_F": 0}
        before = list(store.root.iterdir())
        expect_grant_rejection(
            lambda: release.BASE.execute_synthetic_transaction(
                override_grant, override, store, binding, now=now,
            ),
            "control override field rejected",
        )
        assert list(store.root.iterdir()) == before

    try:
        release.BASE.GrantStateStore(ROOT / "forbidden-grant-state")
    except release.BASE.ReleaseFailure as exc:
        assert "external" in str(exc)
    else:
        raise AssertionError("repository grant state root was accepted")

    denial = release.denied_physical_run()
    assert denial["status"] == "NOT_AUTHORIZED"
    assert denial["release_adapter"] == "v0.2"
    assert denial["physical_backend_imported"] is False
    assert denial["solver_calls"] == 0
    assert denial["cp01r1_attempted"] is False
    assert denial["target_a_F_one_quarter_solve"] is False
    assert denial["operative_grant_created"] is False
    assert denial["result_artifact_created"] is False
    assert denial["physical_evidence_effect"] == "NONE"

    print("PASS: Background-3C12 v0.2 regression tests")


if __name__ == "__main__":
    main()
