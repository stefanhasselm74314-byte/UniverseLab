#!/usr/bin/env python3
"""Validate the A1/MACS J0308.9+2645 false-anomaly control record.

Methods/governance audit only: no network, NumPy/SciPy, solver, likelihood or
physical forward-model execution is permitted here.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "registry/2026-08-12_HZT-M0_Lensing_A1-MACSJ0308_FalseAnomalyControl_v1.0.json"
EXPECTED_CASE = "HZT-M0-LENS-DS-A1-MACSJ0308-20260812-A"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load() -> dict[str, Any]:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def audit() -> dict[str, Any]:
    d = load()
    require(d["case_id"] == EXPECTED_CASE, "case id mismatch")
    require(d["classification"] == "LENSING_DATA_SYSTEMATICS_FALSE_ANOMALY_CONTROL", "classification mismatch")
    require(d["status"] == "REGISTERED_METHODS_CONTROL_NO_HZT_EVIDENCE", "status mismatch")

    primary = d["sources"]["primary_scientific"]
    secondary = d["sources"]["secondary_media"]
    require(primary["arxiv_id"] == "2607.12129", "primary arXiv id mismatch")
    require(primary["source_role"] == "PRIMARY_SCIENTIFIC_SOURCE", "primary source role mismatch")
    require(secondary["source_role"] == "SECONDARY_CONTEXT_ONLY", "media source promoted above primary")

    seq = d["false_anomaly_sequence"]
    require(seq["initial_catalogue_photometric_redshift_approx"] == 4.4, "initial z mismatch")
    require(seq["initial_interpretation_status"] == "FALSIFIED_AS_PHOTOMETRIC_SYSTEMATIC_WITHIN_CURRENT_ANALYSIS", "high-z interpretation not quarantined")
    require(0.0 < seq["f200w_flux_capture_fraction_approx"] <= 0.05, "extended-source flux-loss control drifted")

    corrected = d["corrected_interpretation"]
    require(corrected["redshift_status"] == "CONDITIONAL_PHOTOMETRIC_PENDING_SPECTROSCOPY", "corrected z over-promoted")
    require(corrected["adopted_photometric_redshift_approx"] == 1.4, "adopted z mismatch")
    require(corrected["plausible_redshift_range"] == [1.2, 1.7], "plausible z range mismatch")
    require(corrected["six_band_probability_z_gt_3"] <= 0.001, "high-z probability gate drifted")
    require(corrected["lensing_nature_status"] == "STRONG_GRAVITATIONAL_ARC_CANDIDATE_NOT_YET_DEFINITIVE", "candidate lensing state over-promoted")
    require("spatially resolved spectroscopy" in corrected["required_confirmation"], "spectroscopy confirmation gate missing")

    methodology = d["universelab_methodological_use"]
    require(methodology["bucket"] == "Lensing/Data-Systematics/False-Anomaly-Control", "methods bucket mismatch")
    require(methodology["control_rule"] == "CATALOGUE_RESULT_IS_NOT_PHYSICAL_IDENTIFICATION", "control rule mismatch")
    require(len(methodology["high_z_gate"]) >= 6, "high-z gate incomplete")

    hzt = d["hzt_relevance"]
    require(hzt["direct_hzt_evidence"] == "NONE", "A1 improperly promoted to HZT evidence")
    require(hzt["early_universe_anomaly_for_hzt"] == "NO", "A1 improperly retained as HZT early-universe anomaly")
    require(hzt["current_modified_gravity_test"] == "NO", "A1 improperly promoted to current gravity test")
    require(hzt["future_lensing_test_value"] == "CONDITIONAL", "future lensing value must remain conditional")

    gov = d["governance_firewall"]
    require(gov["solver_state_modified"] is False, "methods record modified solver state")
    require(gov["WP4"] == "BLOCKED", "WP4 advanced")
    require(gov["K1-D"] == "NOT_RELEASED", "K1-D advanced")
    require(gov["K1-E"] == "NOT_ADMISSIBLE", "K1-E advanced")
    require(gov["physical_evidence_effect"] == "NONE", "physical evidence effect changed")

    forbidden = set(d["forbidden_inferences"])
    required_forbidden = {
        "DO_NOT_CLASSIFY_A1_AS_A_ROBUST_EXTREME_EARLY_UNIVERSE_OBJECT",
        "DO_NOT_TREAT_PHOTOMETRIC_REDSHIFT_AS_SPECTROSCOPIC_CONFIRMATION",
        "DO_NOT_TREAT_CORRECTED_PHOTOMETRY_AS_EVIDENCE_FOR_HZT_OR_MODIFIED_GRAVITY",
        "DO_NOT_ADVANCE_WP4_K1D_OR_K1E_FROM_THIS_CASE",
    }
    require(required_forbidden <= forbidden, "forbidden-inference firewall incomplete")

    return {
        "status": "PASS_A1_FALSE_ANOMALY_CONTROL_NO_HZT_EVIDENCE",
        "case_id": EXPECTED_CASE,
        "high_z_interpretation": "FALSIFIED_AS_PHOTOMETRIC_SYSTEMATIC_WITHIN_CURRENT_ANALYSIS",
        "current_redshift": "CONDITIONAL_PHOTOMETRIC_Z_APPROX_1P4_PENDING_SPECTROSCOPY",
        "lensing_status": "STRONG_CANDIDATE_NOT_DEFINITIVE",
        "future_hzt_lensing_value": "CONDITIONAL_ONLY",
        "solver_calls": 0,
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    try:
        result = audit()
    except Exception as exc:
        print(json.dumps({"status": "BLOCKED_A1_FALSE_ANOMALY_CONTROL", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
