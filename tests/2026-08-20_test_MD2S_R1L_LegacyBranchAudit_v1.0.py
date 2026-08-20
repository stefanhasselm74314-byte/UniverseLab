#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "registry/2026-08-20_MD2S_R1L_LegacyBranchAudit_v1.0.json"
REG = ROOT / "registry/2026-08-19_MD2S_R1L_ForensicEvidenceRegister_v1.1.json"
DOC = ROOT / "recovery/2026-08-19_MD2S_R1L_ForensicRecovery_v1.1.md"


def main() -> int:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    reg = json.loads(REG.read_text(encoding="utf-8"))
    doc = DOC.read_text(encoding="utf-8")

    assert audit["status"] == "FORENSIC_BRANCH_AUDIT_COMPLETE_WITH_LIMITS"
    ident = audit["identifier_finding"]
    assert ident["identifier"] == "MD2S-R1-L"
    assert ident["exact_string_recovered"] is True
    assert ident["recovered_role"] == "LEGACY_REPRODUCTION_TRACK_ID"
    assert ident["may_define_current_canon"] is False
    assert ident["original_historical_artifact_identifier_recovered"] is False

    assert len(audit["audited_branches"]) == 13
    assert audit["branch_findings"]["c1_preflight_branches"]["historical_A0_identity"] == "NOT_CLAIMED"
    assert audit["branch_findings"]["c1_preflight_branches"]["c1_anchor_interface_example"]["classification"] == "C1_ANALYTIC_ANCHOR_NOT_HISTORICAL_INTERFACE_DATA"

    assert audit["source_reconstruction_ledger_findings"]["historical_radial_ODEs"] == "MISSING_PRIMARY_TECHNICAL_SOURCE"
    assert audit["source_reconstruction_ledger_findings"]["historical_cap_action_and_oriented_junction_conventions"] == "MISSING_PRIMARY_TECHNICAL_SOURCE"
    assert audit["source_reconstruction_ledger_findings"]["B1_4K_primary_solver_artifact"] == "NOT_RECOVERED"
    assert audit["source_reconstruction_ledger_findings"]["B1_4L_primary_solver_artifact"] == "NOT_RECOVERED"

    assert audit["historical_two_sided_interface"]["status"] == "MISSING_SURVIVING_ARCHIVE"
    assert audit["historical_two_sided_interface"]["exact_historical_replay"] == "NOT_REPRODUCIBLE_FROM_SURVIVING_ARCHIVE"

    assert audit["promotion_firewall"]["C1_anchor_may_fill_historical_missing_fields"] is False
    assert audit["promotion_firewall"]["rebuild_junction_equations_may_be_assumed_historical"] is False
    assert audit["promotion_firewall"]["B1_4K_verified_solver_output"] is False
    assert audit["promotion_firewall"]["B1_4L_verified_solver_output"] is False

    rid = reg["identifier"]
    assert rid["exact_string"] == "MD2S-R1-L"
    assert rid["exact_string_recovered"] is True
    assert rid["recovered_role"] == "LEGACY_REPRODUCTION_TRACK_ID"
    assert rid["canonical_artifact_identifier_recovered"] is False
    assert rid["original_historical_solver_artifact_recovered"] is False
    assert reg["legacy_branch_audit"]["audited_legacy_agent_md2s_branch_count"] == 13
    assert reg["legacy_branch_audit"]["historical_primary_solver_export_recovered"] is False
    assert reg["legacy_branch_audit"]["historical_two_sided_interface_export_recovered"] is False
    assert reg["legacy_branch_audit"]["C1_historical_A0_identity"] == "NOT_CLAIMED"

    assert reg["b14k"]["primary_solver_artifact_recovered"] is False
    assert reg["b14l"]["primary_solver_artifact_recovered"] is False
    assert reg["two_sided_interface"]["classification"] == "E5_MISSING_SURVIVING_ARCHIVE"

    governance = reg["governance"]
    assert governance == {
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
        "physical_gate_effect": "NONE",
    }

    forbidden = [
        "B1.4K = VERIFIED_SOLVER_OUTPUT",
        "B1.4L = VERIFIED_SOLVER_OUTPUT",
        "C1 = HISTORICAL_MD2S_R1L",
        "PHYSICAL_BACKGROUND = ESTABLISHED",
        "K1-D = RELEASED",
        "K1-E = ADMISSIBLE",
    ]
    for phrase in forbidden:
        assert phrase not in doc

    print(json.dumps({
        "status": "PASS_MD2S_R1L_LEGACY_BRANCH_AUDIT",
        "identifier_role": "LEGACY_REPRODUCTION_TRACK_ID",
        "historical_primary_solver_export_recovered": False,
        "physical_evidence_effect": "NONE",
        "physical_gate_effect": "NONE"
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
