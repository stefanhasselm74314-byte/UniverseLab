#!/usr/bin/env python3
"""Backend-free synthetic worker for Background-3C12 state-machine controls."""
from __future__ import annotations

import json
import os
import signal
import sys
import time
from typing import Any

SCOPE = "SYNTHETIC_NONOPERATIVE_TARGET_PATH_TRANSACTION_ONLY"
ALLOWED_OUTCOMES = {"success", "failure", "timeout", "signal", "crash"}


def emit(value: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(value, sort_keys=True, separators=(",", ":")))
    sys.stdout.flush()


def validate(request: dict[str, Any]) -> str:
    if request.get("scope") != SCOPE:
        raise ValueError("synthetic target worker scope violation")
    if request.get("operative") is not False:
        raise ValueError("operative worker request forbidden")
    if request.get("physical_backend_import") is not False:
        raise ValueError("backend import request forbidden")
    if request.get("cp01r1_execution") is not False:
        raise ValueError("CP01R1 request forbidden")
    if request.get("target_solve") is not False:
        raise ValueError("target solve request forbidden")
    outcome = request.get("outcome")
    if outcome not in ALLOWED_OUTCOMES:
        raise ValueError("unregistered synthetic outcome")
    return str(outcome)


def main() -> int:
    try:
        request = json.loads(sys.stdin.read())
        if not isinstance(request, dict):
            raise ValueError("request root must be an object")
        outcome = validate(request)
        common = {
            "scope": SCOPE,
            "outcome": outcome,
            "physical_backend_imported": False,
            "solver_calls": 0,
            "cp01r1_attempts": 0,
            "target_solves": 0,
            "physical_evidence_effect": "NONE",
        }
        if outcome == "success":
            emit({"status": "SYNTHETIC_TARGET_SUCCESS", **common})
            return 0
        if outcome == "failure":
            emit({"status": "SYNTHETIC_TARGET_FAILURE", **common})
            return 2
        if outcome == "timeout":
            emit({"status": "SYNTHETIC_TARGET_TIMEOUT_READY", **common})
            time.sleep(float(request.get("sleep_seconds", 30.0)))
            return 3
        if outcome == "signal":
            emit({"status": "SYNTHETIC_TARGET_SIGNAL_READY", **common})
            os.kill(os.getpid(), signal.SIGTERM)
            return 4
        if outcome == "crash":
            emit({"status": "SYNTHETIC_TARGET_CRASH_READY", **common})
            os._exit(91)
    except Exception as exc:
        emit({
            "status": "SYNTHETIC_WORKER_REJECTED",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "physical_backend_imported": False,
            "solver_calls": 0,
            "cp01r1_attempts": 0,
            "target_solves": 0,
            "physical_evidence_effect": "NONE",
        })
        return 64
    return 64


if __name__ == "__main__":
    raise SystemExit(main())
