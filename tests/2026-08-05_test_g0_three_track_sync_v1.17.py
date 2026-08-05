#!/usr/bin/env python3
"""Regression tests for G0 v1.17 Background-3C6 canonical state."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools/2026-08-05_validate_g0_three_track_sync_v1.17.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("g0_v117_regression", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to import G0 v1.17 validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    validator = load_validator()
    result = validator.validate()
    assert result["status"] == "PASS"
    assert result["release"] == validator.RELEASE
    assert result["decision"] == validator.DECISION
    assert result["checkpoint"] == validator.CHECKPOINT
    assert result["package_manifest_sha256"] == validator.DIGEST
    assert result["control_subprocesses"] == 4
    assert result["physical_solver_calls"] == 0
    assert result["cp01r1_attempts"] == 0
    assert result["execution_authorized"] is False
    assert result["physical_background"] == "NOT_ESTABLISHED"
    assert result["physical_evidence_effect"] == "NONE"
    assert result["next_block"] == validator.NEXT

    sample = {
        "a": validator.OLD_NEXT,
        "b": [0, {"status": validator.OLD_STATUS}],
    }
    assert validator.find_exact(sample, validator.OLD_NEXT) == ["$.a"]
    assert validator.find_exact(sample, validator.OLD_STATUS) == ["$.b[1].status"]
    assert validator.find_exact(sample, "ABSENT") == []

    assert validator.LATEST.read_bytes() == validator.SNAPSHOT.read_bytes()
    assert not validator.GRANT.exists()
    assert not validator.PHYSICAL_ARTIFACT.exists()
    print("PASS: G0 v1.17 Background-3C6 regression tests")


if __name__ == "__main__":
    main()
