#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry/2026-08-20_MD2S_R1L_TranscriptRecoveryAudit_v1.0.json"


def main():
    data = json.loads(REG.read_text(encoding="utf-8"))

    assert data["status"] == "TARGET_TRANSCRIPTS_VERIFIED_RAW_MESSAGE_EXTRACTION_NOT_SURFACED"
    inv = data["historical_transcript_inventory"]
    assert inv["target_count"] == 2
    assert inv["target_dates"] == ["2026-07-10", "2026-07-21"]
    assert inv["official_export_presence"] == "VERIFIED"
    assert inv["full_transcript_presence_in_refresh_inventory"] == "VERIFIED"
    assert inv["private_identifiers_committed_to_public_repository"] is False

    ext = data["direct_extraction_result"]
    assert ext["message_level_primary_target_extraction"] == "BLOCKED_IN_CURRENT_SEARCH_INTERFACE"
    assert ext["primary_md2s_solver_artifact_recovered"] is False
    assert ext["historical_run_bound_solver_io_recovered"] is False
    assert ext["historical_two_sided_interface_export_recovered"] is False
    assert ext["historical_sha256_manifest_recovered"] is False

    guard = data["evidence_hygiene"]
    assert all(value is False for value in guard.values())

    gov = data["governance"]
    assert gov == {
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
        "physical_gate_effect": "NONE",
    }

    # Public-repo privacy invariant: no private conversation identifier keys.
    text = REG.read_text(encoding="utf-8").lower()
    for forbidden in ("conversation_id", "conversation-id", "conversation id"):
        assert forbidden not in text

    print("PASS_MD2S_R1L_TRANSCRIPT_RECOVERY_AUDIT_V1")


if __name__ == "__main__":
    main()
