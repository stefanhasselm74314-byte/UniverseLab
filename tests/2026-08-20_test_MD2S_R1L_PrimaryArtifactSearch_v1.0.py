#!/usr/bin/env python3
"""Read-only consistency validator for the scoped MD2S-R1-L primary-artifact search."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEARCH_PATH = ROOT / "registry/2026-08-20_MD2S_R1L_PrimaryArtifactSearch_v1.0.json"
REGISTER_PATH = ROOT / "registry/2026-08-20_MD2S_R1L_ForensicEvidenceRegister_v1.3.json"
REPORT_PATH = ROOT / "recovery/2026-08-20_MD2S_R1L_PrimaryArtifactSearch_v1.0.md"

LOCKED_GOVERNANCE = {
    "official_MD2S_solver": "NOT_AUTHORIZED",
    "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
    "K1-D": "NOT_RELEASED",
    "K1-E": "NOT_ADMISSIBLE",
    "physical_evidence_effect": "NONE",
    "physical_gate_effect": "NONE",
}

EXPECTED_TARGETS = {
    "MD2S_Gesamtpaket",
    "MD2S_reproduction_script",
    "MD2S_SHA256_manifest",
    "run_bound_solver_input_output_package",
    "run_bound_one_sided_bulk_cap_boundary_export",
    "A_prime_bulk",
    "A_prime_cap",
    "Lprime_over_L_bulk",
    "Lprime_over_L_cap",
}

EXPECTED_CHANNELS = {
    "file_library_index",
    "github_current_code_index",
    "github_commit_message_index",
    "hyper_zip_archive_audit",
    "chatgpt_export_register",
}


def load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    for path in [SEARCH_PATH, REGISTER_PATH, REPORT_PATH]:
        assert path.is_file(), path

    search = load(SEARCH_PATH)
    register = load(REGISTER_PATH)

    assert search["schema"] == "universelab.md2s.r1l.primary-artifact-search.v1"
    assert search["version"] == "1.0.0"
    assert search["track"] == "MD2S-R1-L"
    assert search["status"] == "SCOPED_RECOVERY_SEARCH_COMPLETE_NO_PRIMARY_ARTIFACT_RECOVERED"
    assert set(search["searched_targets"]) == EXPECTED_TARGETS
    assert set(search["search_channels"]) == EXPECTED_CHANNELS

    channels = search["search_channels"]
    for name, channel in channels.items():
        assert channel["searched"] is True, name
    assert channels["file_library_index"]["primary_target_recovered"] is False
    assert channels["github_current_code_index"]["primary_target_recovered"] is False
    assert channels["github_commit_message_index"]["primary_target_recovered"] is False
    assert channels["hyper_zip_archive_audit"]["primary_target_recovered"] is False
    assert channels["hyper_zip_archive_audit"]["archive_scope_only"] is True

    chat = channels["chatgpt_export_register"]
    assert chat["primary_file_artifact_recovered"] is False
    assert chat["transcript_targets_located"] is True
    assert chat["transcript_target_count"] == 2
    assert len(chat["public_labels"]) == 2
    assert chat["private_identifiers_committed_to_public_repository"] is False

    neg = search["negative_result_scope"]
    assert neg["global_nonexistence_claim"] is False
    assert neg["local_device_or_unuploaded_archive_coverage"] is False
    assert neg["deleted_unexported_chat_coverage"] is False
    assert neg["unindexed_external_storage_coverage"] is False

    assert all(value is False for value in search["artifact_disambiguation"].values())

    result = search["result"]
    assert result["primary_historical_solver_artifact_recovered"] is False
    assert result["historical_two_sided_interface_export_recovered"] is False
    assert result["historical_run_bound_solver_io_recovered"] is False
    assert result["historical_sha256_manifest_recovered"] is False
    assert result["search_status"] == "SCOPED_NEGATIVE_WITH_TRANSCRIPT_PROVENANCE_TARGETS"
    assert search["governance"] == LOCKED_GOVERNANCE

    assert register["version"] == "1.3.0"
    assert register["status"] == "FORENSIC_RECOVERY_ONLY"
    assert register["identifier"]["original_historical_solver_artifact_recovered"] is False
    assert "E8_SCOPED_MULTI_SOURCE_RECOVERY_SEARCH" in register["evidence_classes"]

    pa = register["primary_artifact_search"]
    assert pa["classification"] == "E8_SCOPED_MULTI_SOURCE_RECOVERY_SEARCH"
    assert pa["source"] == "registry/2026-08-20_MD2S_R1L_PrimaryArtifactSearch_v1.0.json"
    assert pa["primary_historical_solver_artifact_recovered"] is False
    assert pa["historical_sha256_manifest_recovered"] is False
    assert pa["historical_run_bound_solver_io_recovered"] is False
    assert pa["historical_two_sided_interface_export_recovered"] is False
    assert pa["transcript_provenance_targets_recovered"] is True
    assert pa["transcript_target_count"] == 2
    assert pa["private_transcript_identifiers_committed_to_public_repository"] is False
    assert pa["message_level_transcript_extraction_completed"] is False
    assert pa["global_nonexistence_claim"] is False

    policy = register["promotion_policy"]
    assert policy["archive_scoped_absence_may_be_promoted_to_global_nonexistence"] is False
    assert policy["scoped_multi_source_absence_may_be_promoted_to_global_nonexistence"] is False
    assert policy["C1_or_rebuild_data_may_fill_historical_missing_fields"] is False
    assert policy["chat_transcript_may_replace_primary_solver_artifact"] is False
    assert register["governance"] == LOCKED_GOVERNANCE

    report = REPORT_PATH.read_text(encoding="utf-8")
    for marker in [
        "GLOBAL NONEXISTENCE CLAIM:                  FORBIDDEN",
        "RECOVERED (2, PRIVATE REFERENCES)",
        "official_MD2S_solver = NOT_AUTHORIZED",
        "K1-D = NOT_RELEASED",
        "physical_evidence_effect = NONE",
    ]:
        assert marker in report, marker

    print("PASS_MD2S_R1L_SCOPED_PRIMARY_ARTIFACT_SEARCH")


if __name__ == "__main__":
    main()
