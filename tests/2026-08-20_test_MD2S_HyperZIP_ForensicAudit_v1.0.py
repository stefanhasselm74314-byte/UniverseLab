#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry/2026-08-20_MD2S_R1L_ForensicEvidenceRegister_v1.2.json"
DOC = ROOT / "recovery/2026-08-20_MD2S_HyperZIP_ForensicAudit_v1.0.md"


def main() -> int:
    data = json.loads(REG.read_text(encoding="utf-8"))
    doc = DOC.read_text(encoding="utf-8")

    assert data["status"] == "FORENSIC_RECOVERY_ONLY"
    assert data["identifier"]["exact_string"] == "MD2S-R1-L"
    assert data["identifier"]["recovered_role"] == "LEGACY_REPRODUCTION_TRACK_ID"
    assert data["identifier"]["original_historical_solver_artifact_recovered"] is False

    audit = data["hyper_zip_archive_audit"]
    assert audit["classification"] == "E7_ARCHIVE_LEVEL_FORENSIC_AUDIT"
    assert audit["audit_scope"]["pdf_file_count"] == 40
    assert audit["audit_scope"]["page_count"] == 1279
    assert audit["audit_scope"]["long_chat_pdf_page_count"] == 1191
    assert audit["md2s_terminal_result_in_archive"] == "B1.4N_REPORTED"
    assert audit["b14o_status_in_archive"] == "NEXT_AUDIT_OPENED_NO_RESULT_PRESENT"
    assert audit["archive_contains_only_pdfs"] is True
    assert audit["primary_solver_transaction_recovered_from_hyper_zip"] is False
    assert audit["reproducible_md2s_numerics_from_hyper_zip"] is False

    for required in (
        "solver_inputs",
        "solver_outputs",
        "residual_logs",
        "sha256_manifests",
        "referenced_subpackages",
    ):
        assert required in audit["missing_from_archive"]

    assert data["promotion_policy"]["archive_scoped_absence_may_be_promoted_to_global_nonexistence"] is False
    assert data["two_sided_interface"]["exact_historical_replay"] == "NOT_REPRODUCIBLE_FROM_SURVIVING_ARCHIVE"

    assert "absence from `Hyper.zip` is not proof that the historical artifacts never existed elsewhere" in doc
    assert "Until such primary artifacts are recovered" in doc

    assert data["governance"] == {
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
        "physical_gate_effect": "NONE",
    }

    print(json.dumps({
        "status": "PASS_MD2S_HYPERZIP_FORENSIC_AUDIT_BINDING",
        "archive_scope_only": True,
        "historical_solver_artifact_recovered": False,
        "physical_evidence_effect": "NONE",
        "physical_gate_effect": "NONE"
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
