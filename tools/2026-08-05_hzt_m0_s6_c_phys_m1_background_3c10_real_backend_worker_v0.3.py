#!/usr/bin/env python3
"""R3 worker adapter with explicit handoff vector reconstruction.

JSON mapping key order is deliberately treated as non-semantic. The complete
candidate field set is validated and the numerical vector is reconstructed in
the versioned contractual order before delegating to the unchanged real worker.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "tools/2026-08-05_hzt_m0_s6_c_phys_m1_background_3c10_real_backend_worker_v0.2.py"
R2_CONTROL_RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3C10-AF0-CONTROL-R2"
R3_CONTROL_RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3C10-AF0-CONTROL-R3"
CANDIDATE_FIELDS = (
    "varphi_N_0", "q_N", "A_S_0", "varphi_S_0",
    "q_S", "rho_N", "rho_S", "k4",
)

SPEC = importlib.util.spec_from_file_location("background3c10_real_worker_adapter_v02", BASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import Background-3C10 worker v0.2")
BASE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)


def canonical_bytes(value: Any) -> bytes:
    return BASE.canonical_bytes(value)


def translate_request(request: dict[str, Any]) -> dict[str, Any]:
    if request.get("control_run_id") != R3_CONTROL_RUN_ID:
        raise BASE.BASE.ControlFailure("corrected R3 control run identity required")
    translated = json.loads(json.dumps(request))
    translated["control_run_id"] = R2_CONTROL_RUN_ID
    if translated.get("stage") == "independent_control":
        handoff = translated.get("handoff")
        if not isinstance(handoff, dict):
            raise BASE.BASE.ControlFailure("candidate handoff missing")
        candidate = handoff.get("candidate")
        if not isinstance(candidate, dict):
            raise BASE.BASE.ControlFailure("candidate mapping missing")
        actual = set(candidate)
        expected = set(CANDIDATE_FIELDS)
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        if missing:
            raise BASE.BASE.ControlFailure(f"candidate fields missing: {missing}")
        if unknown:
            raise BASE.BASE.ControlFailure(f"candidate fields unknown: {unknown}")
        handoff["candidate"] = {field: candidate[field] for field in CANDIDATE_FIELDS}
    return translated


def dispatch(request: dict[str, Any]) -> dict[str, Any]:
    translated = translate_request(request)
    return BASE.dispatch(translated)


def main() -> int:
    try:
        request = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        if not isinstance(request, dict):
            raise BASE.BASE.ControlFailure("request root must be an object")
        result = dispatch(request)
    except Exception as exc:
        result = {
            "status": "CONTROL_FAILURE",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "control_run_id": R3_CONTROL_RUN_ID,
            "physical_evidence_effect": "NONE",
        }
        sys.stdout.buffer.write(canonical_bytes(result))
        return 2
    result["control_run_id"] = R3_CONTROL_RUN_ID
    result["worker_adapter"] = "v0.3"
    result["handoff_vector_order_source"] = "EXPLICIT_CANDIDATE_FIELDS_CONTRACT"
    result["json_mapping_key_order_semantic"] = False
    result["numerical_worker"] = str(BASE_PATH.relative_to(ROOT))
    sys.stdout.buffer.write(canonical_bytes(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
