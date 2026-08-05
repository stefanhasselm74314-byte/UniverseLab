#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools/2026-08-05_validate_g0_three_track_sync_v1.22.py"


def main() -> None:
    spec = importlib.util.spec_from_file_location("g0_v122_test", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("validator import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    result = module.validate()
    assert result["status"] == "PASS"
    assert result["release"] == module.RELEASE
    assert result["decision"] == module.DECISION
    assert result["checkpoint"] == module.CHECKPOINT
    assert result["review_status"] == module.DENIAL
    assert result["r1_status"] == module.R1_STATUS
    assert result["r2_status"] == module.R2_STATUS
    assert result["r3_status"] == module.R3_STATUS
    assert result["package_manifest_sha256"] == module.PACKAGE_DIGEST
    assert result["execution_authorized"] is False
    assert result["review_imports_numerical_backend"] is False
    assert result["physical_solver_calls"] == 0
    assert result["cp01r1_attempts"] == 0
    assert result["target_a_F_one_quarter_solves"] == 0
    assert result["operative_grants"] == 0
    assert result["physical_result_artifacts"] == 0
    assert result["physical_evidence_effect"] == "NONE"
    assert result["next_block"] == module.NEXT
    assert module.find_exact({"x": module.OLD_NEXT}, module.OLD_NEXT) == ["$.x"]
    assert module.LATEST.read_bytes() == module.SNAPSHOT.read_bytes()
    print("PASS: G0 v1.22 Background-3C11 regression tests")


if __name__ == "__main__":
    main()
