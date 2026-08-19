#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry/2026-08-19_MD2S_R1L_ForensicEvidenceRegister_v1.0.json"
DOC = ROOT / "recovery/2026-08-19_MD2S_R1L_ForensicRecovery_v1.0.md"


def main() -> int:
    data = json.loads(REG.read_text(encoding="utf-8"))
    doc = DOC.read_text(encoding="utf-8")

    assert data["status"] == "FORENSIC_RECOVERY_ONLY"
    assert data["exact_identifier_status"] == "MD2S-R1-L_NOT_FOUND_AS_CANONICAL_ARTIFACT_IDENTIFIER"

    assert data["a0"]["classification"] == "E1_VERIFIED_REPORTED_ARTIFACT"
    assert data["bvp_contract"]["classification"] == "E2_VERIFIED_CONTRACT_DEFINITION"
    assert data["bvp_contract"]["run_status"] == "NOT_EXECUTED"
    assert data["derived_checks"]["classification"] == "E3_DERIVED_CHECK"

    assert data["b14k"]["classification"] == "E4_UNVERIFIED_HISTORICAL_CHAT_REPORT"
    assert data["b14k"]["primary_solver_artifact_recovered"] is False
    assert data["b14l"]["classification"] == "E4_UNVERIFIED_HISTORICAL_CHAT_REPORT"
    assert data["b14l"]["primary_solver_artifact_recovered"] is False

    assert data["two_sided_interface"]["classification"] == "E5_MISSING_SURVIVING_ARCHIVE"
    assert data["two_sided_interface"]["exact_historical_replay"] == "NOT_REPRODUCIBLE_FROM_SURVIVING_ARCHIVE"
    assert data["ui_default_rule"]["interactive_calculator_zero_defaults_are_historical_data"] is False

    governance = data["governance"]
    assert governance == {
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
        "physical_gate_effect": "NONE",
    }

    forbidden_promotions = [
        "B1.4K = VERIFIED_SOLVER_OUTPUT",
        "B1.4L = VERIFIED_SOLVER_OUTPUT",
        "PHYSICAL_BACKGROUND = ESTABLISHED",
        "K1-D = RELEASED",
        "K1-E = ADMISSIBLE",
    ]
    for phrase in forbidden_promotions:
        assert phrase not in doc

    print(json.dumps({
        "status": "PASS_MD2S_R1L_FORENSIC_EVIDENCE_BINDING",
        "physical_evidence_effect": "NONE",
        "physical_gate_effect": "NONE"
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
