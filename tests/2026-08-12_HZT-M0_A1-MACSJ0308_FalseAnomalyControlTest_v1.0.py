#!/usr/bin/env python3
"""Regression test for A1/MACS J0308 false-anomaly control."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-12_hzt_m0_a1_macsj0308_false_anomaly_control_review_v1.0.py"

spec = importlib.util.spec_from_file_location("a1_false_anomaly_control", TOOL)
if spec is None or spec.loader is None:
    raise RuntimeError("unable to import A1 control validator")
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def main() -> int:
    result = mod.audit()
    assert result["status"] == "PASS_A1_FALSE_ANOMALY_CONTROL_NO_HZT_EVIDENCE"
    assert result["high_z_interpretation"] == "FALSIFIED_AS_PHOTOMETRIC_SYSTEMATIC_WITHIN_CURRENT_ANALYSIS"
    assert result["current_redshift"] == "CONDITIONAL_PHOTOMETRIC_Z_APPROX_1P4_PENDING_SPECTROSCOPY"
    assert result["lensing_status"] == "STRONG_CANDIDATE_NOT_DEFINITIVE"
    assert result["future_hzt_lensing_value"] == "CONDITIONAL_ONLY"
    assert result["solver_calls"] == 0
    assert result["physical_evidence_effect"] == "NONE"
    print("PASS_HZT_M0_A1_MACSJ0308_FALSE_ANOMALY_CONTROL_TEST")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
