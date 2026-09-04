#!/usr/bin/env python3
"""Successor-aware Band V-C claim→evidence crosswalk gate."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CROSSWALK = ROOT / "registry/2026-09-04_UniverseLab_BandVC_ClaimEvidenceCrosswalk_v1.0.json"
GAPS = ROOT / "registry/2026-09-04_UniverseLab_BandVC_MissingLinkRegister_v1.0.json"
CENSUS = ROOT / "registry/2026-09-03_UniverseLab_PublicScientificClaimCensus_v1.0.json"
HISTORICAL_MEDIUM = ROOT / "registry/2026-09-04_UniverseLab_PublicScientificMediumAdjudicationSummary_v1.0.json"
DELTA = ROOT / "registry/2026-09-04_UniverseLab_BandVC_StatusPageMediumDeltaAdjudication_v1.0.json"
MANIFEST = ROOT / "project-manifest.json"
ALIAS = ROOT / "registry/session-checkpoint-latest.json"
G11 = ROOT / "registry/2026-09-04_UniverseLab_BandVC_G11_StateFreshnessClosure_v1.0.json"

ALLOWED = {"VERIFIED_PRESENT","REFERENCE_ONLY","BLOCKED_BY_UNRELEASED_MAP","MISSING_REQUIRED_LINK","NOT_APPLICABLE","DECLARED_PROSPECTIVE"}
FIREWALLS = {"FM-G0":"OPEN","RATIFIED_HUMAN_TRUST_ROOT":"NOT_RATIFIED","RUNTIME_ISSUANCE_BINDINGS":"BLOCKED","AuthorizationDecision":"NOT_CREATED","SingleUseGrant":"NOT_CREATED","BACKEND_IMPORT":"NOT_EXECUTED","SOLVER_EXECUTION":"NOT_EXECUTED","PHYSICAL_BACKGROUND":"NOT_ESTABLISHED","PHYSICAL_RESPONSE_RANK":"NOT_EXECUTED","K1-D":"NOT_RELEASED","K1-E":"NOT_ADMISSIBLE"}


def load(path: Path):
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def repo_path(value: str) -> Path:
    assert isinstance(value, str) and value and not value.startswith("/") and ".." not in Path(value).parts
    path = ROOT / value
    assert path.is_file(), value
    return path


def main() -> None:
    crosswalk, gaps, census = load(CROSSWALK), load(GAPS), load(CENSUS)
    historical, delta, manifest, alias = load(HISTORICAL_MEDIUM), load(DELTA), load(MANIFEST), load(ALIAS)

    families = crosswalk["families"]
    census_ids = {row["claim_family_id"] for row in census["claim_families"]}
    cross_ids = [row["claim_family_id"] for row in families]
    assert crosswalk["family_count"] == 15
    assert len(families) == 15 and len(set(cross_ids)) == 15
    assert set(cross_ids) == census_ids

    axes = ("claim","equation_or_derivation","code","test","data","falsifier_or_gate")
    missing_families = set()
    for row in families:
        for axis in axes:
            assert row[axis] in ALLOWED, (row["claim_family_id"], axis, row[axis])
            if row[axis] == "MISSING_REQUIRED_LINK":
                missing_families.add(row["claim_family_id"])
        assert row["evidence_scope"] and row["notes"]

    gap_rows = gaps["gaps"]
    gap_families = {family_id for row in gap_rows for family_id in row.get("family_ids", [])}
    assert gaps["gap_count"] == len(gap_rows) == 11
    assert missing_families <= gap_families
    assert gaps["blocking_scientific_gap_count"] == 10
    assert gaps["governance_provenance_gap_count"] == 1
    assert {row["gap_id"] for row in gap_rows} == {f"UL-BVC-G{i:02d}" for i in range(1,12)}

    for family in census["claim_families"]:
        for field in ("source_paths","code_paths","test_paths"):
            for source in family.get(field, []):
                repo_path(source)

    # Historical Band-V-B evidence remains 42/42.
    assert historical["materialized_claim_candidates"] == 989
    assert historical["materialized_high_candidates"] == 0
    assert historical["materialized_medium_candidates"] == 42
    assert historical["result"]["medium_contextually_adjudicated_total"] == 42
    assert historical["result"]["medium_contextually_unadjudicated"] == 0
    assert historical["result"]["positive_physical_hzt_overclaims"] == 0
    assert historical["result"]["physical_claim_promotions"] == 0
    assert historical["physical_gate_effect"] == historical["physical_evidence_effect"] == "NONE"

    # Current successor delta is 7/7 and creates no physical claim.
    assert delta["scope"]["current_materialized_claim_candidates"] == 993
    assert delta["scope"]["current_materialized_high_candidates"] == 0
    assert delta["scope"]["current_materialized_medium_candidates"] == 46
    assert delta["global_result"]["delta_candidates"] == 7
    assert delta["global_result"]["contextually_adjudicated"] == 7
    assert delta["global_result"]["contextually_unadjudicated"] == 0
    assert delta["global_result"]["physical_claim_promotions"] == 0
    assert delta["physical_gate_effect"] == delta["physical_evidence_effect"] == "NONE"

    checkpoint_path = repo_path(alias["canonical_snapshot"])
    checkpoint = load(checkpoint_path)
    state = load(repo_path(alias["canonical_state"]))
    site = load(repo_path(alias["site_state"]))
    assert ALIAS.read_bytes() == checkpoint_path.read_bytes()
    assert checkpoint == alias
    assert manifest["canonical_state"] == alias["canonical_state"]
    assert manifest["site_state"] == alias["site_state"]
    assert manifest["session_checkpoint"] == alias["canonical_snapshot"]
    assert state["basis_main_commit"] == site["basis_main_commit"] == checkpoint["basis_commit"] == manifest["basis_main_commit"]

    if G11.is_file() and manifest.get("next_allowed_repository_step") == "BAND_VC_MISSING_LINK_REMEDIATION_NO_PHYSICAL_EXECUTION":
        closure = load(G11)
        assert closure["gap_id"] == "UL-BVC-G11"
        assert closure["scientific_missing_links_after_closure"] == 10
        assert closure["governance_provenance_missing_links_after_closure"] == 0
        assert closure["physical_gate_effect"] == closure["physical_evidence_effect"] == "NONE"
        assert state["public_claim_governance"]["medium_claim_gate"] == "CURRENT_COMPLETE_46_OF_46_WITH_42_HISTORICAL_PLUS_7_SUCCESSOR_DELTA"
        assert state["public_claim_governance"]["current_materialized_claim_candidates"] == 993
        assert state["public_claim_governance"]["current_materialized_medium_candidates"] == 46
        assert state["public_claim_governance"]["current_medium_contextually_unadjudicated"] == 0
        assert state["public_claim_governance"]["band_vc_gate"] == "MERGED_15_FAMILIES_11_MISSING_LINKS_REGISTERED"
        freshness = "G11_CLOSED_APPEND_ONLY"
    else:
        assert "BAND_VB_MEDIUM" in manifest["next_allowed_repository_step"]
        freshness = "G11_HISTORICALLY_OPEN"

    for key, expected in FIREWALLS.items():
        assert manifest["gates"][key] == expected, (key, manifest["gates"][key], expected)
    assert manifest["physical_gate_effect"] == manifest["physical_evidence_effect"] == "NONE"
    assert crosswalk["physical_gate_effect"] == crosswalk["physical_evidence_effect"] == "NONE"
    assert gaps["physical_gate_effect"] == gaps["physical_evidence_effect"] == "NONE"

    print(
        "UniverseLab Band V-C crosswalk: PASS families=15 gaps=11 scientific_blocking=10 "
        f"historical_medium=42/42 current_medium=46/46 delta=7/7 freshness={freshness} "
        "physical_gate_effect=NONE physical_evidence_effect=NONE"
    )


if __name__ == "__main__":
    main()
