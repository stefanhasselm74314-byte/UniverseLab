#!/usr/bin/env python3
"""Corrected R2 envelope adapter for the Background-3C10 real worker.

The numerical implementation remains the v0.1 real-backend worker. This adapter
creates a new immutable control-run identity after the fail-closed R1 acceptance
contract failure. It translates only the control-run envelope; no numerical
function, model parameter, mesh, cutoff, backend, or solver path is changed.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_worker_v0.1.py"
R1_CONTROL_RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3C10-AF0-CONTROL-R1"
R2_CONTROL_RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3C10-AF0-CONTROL-R2"

SPEC = importlib.util.spec_from_file_location("background3c10_real_worker_base_v01", BASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import Background-3C10 worker v0.1")
BASE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)


def canonical_bytes(value: Any) -> bytes:
    return BASE.canonical_bytes(value)


def translate_request(request: dict[str, Any]) -> dict[str, Any]:
    if request.get("control_run_id") != R2_CONTROL_RUN_ID:
        raise BASE.ControlFailure("corrected R2 control run identity required")
    translated = json.loads(json.dumps(request))
    translated["control_run_id"] = R1_CONTROL_RUN_ID
    return translated


def dispatch(request: dict[str, Any]) -> dict[str, Any]:
    translated = translate_request(request)
    stage = translated.get("stage")
    if stage == "primary_control":
        return BASE.primary_control(translated)
    if stage == "independent_control":
        return BASE.independent_control(translated)
    if stage == "timeout_probe":
        return BASE.timeout_probe(translated)
    if stage == "signal_probe":
        return BASE.signal_probe(translated)
    raise BASE.ControlFailure("unregistered corrected worker stage")


def main() -> int:
    try:
        request = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        if not isinstance(request, dict):
            raise BASE.ControlFailure("request root must be an object")
        result = dispatch(request)
    except Exception as exc:
        result = {
            "status": "CONTROL_FAILURE",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "control_run_id": R2_CONTROL_RUN_ID,
            "physical_evidence_effect": "NONE",
        }
        sys.stdout.buffer.write(canonical_bytes(result))
        return 2
    result["control_run_id"] = R2_CONTROL_RUN_ID
    result["worker_adapter"] = "v0.2"
    result["numerical_worker"] = str(BASE_PATH.relative_to(ROOT))
    sys.stdout.buffer.write(canonical_bytes(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
