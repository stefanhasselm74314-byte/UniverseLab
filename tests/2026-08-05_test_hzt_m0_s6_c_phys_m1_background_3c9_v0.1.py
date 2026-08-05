#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c9_v0.1.py"


def main() -> None:
    spec = importlib.util.spec_from_file_location("background3c9_test", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("validator import failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    result = module.validate()
    assert result["status"] == "PASS"
    assert result["review_status"] == module.DENIAL
    assert result["package_manifest_sha256"] == module.PACKAGE_DIGEST
    assert result["schedule_sha256"] == module.SCHEDULE_DIGEST
    assert result["physical_backend_imported"] is False
    assert result["physical_solver_calls"] == 0
    assert result["cp01r1_attempts"] == 0
    assert result["grant_created"] is False
    assert result["result_artifact_created"] is False
    assert result["physical_evidence_effect"] == "NONE"
    assert result["next_block"] == module.NEXT
    print("PASS: Background-3C9 authorization review regression tests")


if __name__ == "__main__":
    main()
