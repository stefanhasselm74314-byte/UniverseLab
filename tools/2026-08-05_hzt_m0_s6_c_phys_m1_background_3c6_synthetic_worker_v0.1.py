#!/usr/bin/env python3
"""Physics-free subprocess worker for Background-3C6 integration controls.

This worker deliberately contains no Hyperzeit equations, no numerical backend
imports and no root solver. It exists only to exercise orchestration, resource,
timeout, signal, classification and atomic-artifact paths.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import signal
import sys
import time

ALLOWED_CASES = {
    "analytic_success",
    "synthetic_reject",
    "synthetic_timeout",
    "synthetic_signal",
}


def canonical_bytes(payload: dict) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def write_payload(path: Path, payload: dict) -> None:
    if path.exists() or path.is_symlink():
        raise RuntimeError("worker output path must not already exist")
    if not path.parent.is_dir():
        raise RuntimeError("worker output parent must exist")
    data = canonical_bytes(payload)
    with path.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def analytic_success_payload(control_id: str) -> dict:
    a = Fraction(3, 5)
    b = Fraction(4, 5)
    total = a * a + b * b
    return {
        "schema": "universelab.background-3c6-control-worker-result.v0.1",
        "control_id": control_id,
        "case": "analytic_success",
        "accepted": total == 1,
        "identity": {
            "statement": "(3/5)^2+(4/5)^2=1",
            "lhs_numerator": total.numerator,
            "lhs_denominator": total.denominator,
            "rhs_numerator": 1,
            "rhs_denominator": 1,
            "exact": total == 1,
        },
        "physical_model_evaluated": False,
        "solver_called": False,
        "physical_evidence_effect": "NONE",
    }


def synthetic_reject_payload(control_id: str) -> dict:
    return {
        "schema": "universelab.background-3c6-control-worker-result.v0.1",
        "control_id": control_id,
        "case": "synthetic_reject",
        "accepted": False,
        "rejection_reason": "INTENTIONAL_CONTROL_REJECTION",
        "synthetic_residual": 1.0,
        "physical_model_evaluated": False,
        "solver_called": False,
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True, choices=sorted(ALLOWED_CASES))
    parser.add_argument("--control-id", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    output = Path(args.output).resolve()
    if args.case == "analytic_success":
        write_payload(output, analytic_success_payload(args.control_id))
        return 0
    if args.case == "synthetic_reject":
        write_payload(output, synthetic_reject_payload(args.control_id))
        return 2
    if args.case == "synthetic_timeout":
        time.sleep(5.0)
        return 70
    if args.case == "synthetic_signal":
        os.kill(os.getpid(), signal.SIGTERM)
        return 71
    return 72


if __name__ == "__main__":
    raise SystemExit(main())
