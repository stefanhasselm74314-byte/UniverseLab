#!/usr/bin/env python3
"""Regression tests for Background-3C8 physical adapter controls."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c8_physical_execution_adapter_v0.1.py"
VALIDATOR_PATH = ROOT / "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c8_v0.1.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def expect_error(function, fragment: str) -> None:
    try:
        function()
    except Exception as error:
        assert fragment in str(error), (fragment, type(error).__name__, str(error))
    else:
        raise AssertionError(f"expected error containing {fragment!r}")


def main() -> None:
    adapter = load(ADAPTER_PATH, "background3c8_adapter_tests")
    validator = load(VALIDATOR_PATH, "background3c8_validator_tests")

    result = validator.validate()
    assert result["status"] == "PASS"
    assert result["physical_solver_calls"] == 0
    assert result["cp01r1_attempts"] == 0
    assert result["physical_evidence_effect"] == "NONE"

    schedule = adapter.build_schedule()
    assert len(schedule) == 35
    assert schedule[0] == {
        "ordinal": 0,
        "seed_index": 0,
        "seed_multiplier": "0",
        "node_count": 24,
        "degree": 23,
    }
    assert schedule[-1] == {
        "ordinal": 34,
        "seed_index": 6,
        "seed_multiplier": "-1/2",
        "node_count": 96,
        "degree": 95,
    }
    assert len({(item["seed_index"], item["node_count"]) for item in schedule}) == 35

    audit = adapter.audit_release()
    assert audit["source_count"] == 12
    assert audit["forbidden_modules"] == []
    assert audit["forbidden_calls"] == []
    assert audit["backend_binding"]["physical_backend_imported"] is False

    with tempfile.TemporaryDirectory(prefix="universelab-bg3c8-regression-") as temporary:
        root = Path(temporary)
        expect_error(
            lambda: adapter.run_control(
                "not_registered",
                f"{adapter.CONTROL_ID_PREFIX}UNREGISTERED",
                root,
            ),
            "unregistered manufactured control case",
        )
        expect_error(
            lambda: adapter.run_control(
                "manufactured_success",
                "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1",
                root,
            ),
            "control ID is outside the registered prefix",
        )
        expect_error(
            lambda: adapter.ensure_external_output_root(ROOT / "artifacts" / "forbidden-bg3c8-control"),
            "external to the repository",
        )

        capability = adapter.issue_manufactured_capability(
            f"{adapter.CONTROL_ID_PREFIX}REGRESSION-REPLAY",
            audit["package_manifest_sha256"],
        )
        ledger = root / "capability-ledger"
        adapter.consume_capability_once(capability, ledger)
        expect_error(
            lambda: adapter.consume_capability_once(capability, ledger),
            "replay rejected",
        )

        tampered = dict(capability)
        tampered["physical_authorized"] = True
        expect_error(
            lambda: adapter.consume_capability_once(tampered, root / "tampered-ledger"),
            "scope violation",
        )

    denial = adapter.denied_physical_run(adapter.RUN_ID)
    assert denial["status"] == "NOT_AUTHORIZED"
    assert denial["physical_backend_imported"] is False
    assert denial["solver_calls"] == 0
    assert denial["cp01r1_attempted"] is False
    assert denial["operative_grant_created"] is False
    assert denial["result_artifact_created"] is False

    expect_error(
        lambda: adapter.denied_physical_run("UNREGISTERED-PHYSICAL-RUN"),
        "physical run ID mismatch",
    )

    assert adapter.PRIMARY_PHYSICAL_ROOT_CALL_COUNT == 0
    assert adapter.INDEPENDENT_PHYSICAL_ROOT_CALL_COUNT == 0
    assert adapter.SHOOTING_JACOBIAN_CALL_COUNT == 0
    assert adapter.CP01R1_ATTEMPT_COUNT == 0
    print("PASS: Background-3C8 physical adapter regression tests")


if __name__ == "__main__":
    main()
