#!/usr/bin/env python3
"""Band V-C claim→equation/code/test/data/falsifier crosswalk gate.

This is a nonoperative audit gate. It verifies family coverage, declared
repository evidence links, fail-closed missing-link accounting and unchanged
physical/authorization firewalls. It performs no physical solver execution.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / "registry/2026-09-03_UniverseLab_PublicScientificClaimCensus_v1.0.json"
CROSSWALK = ROOT / "registry/2026-09-04_UniverseLab_BandVC_ClaimEvidenceCrosswalk_v1.0.json"
GAPS = ROOT / "registry/2026-09-04_UniverseLab_BandVC_MissingLinkRegister_v1.0.json"
MEDIUM = ROOT / "registry/2026-09-04_UniverseLab_PublicScientificMediumAdjudicationSummary_v1.0.json"
MANIFEST = ROOT / "project-manifest.json"
STATE = ROOT / "registry/2026-09-03_UniverseLab_CurrentMainCanonicalState_v1.2.json"
SITE = ROOT / "registry/2026-09-03_UniverseLab_SiteState_v1.3.json"
SESSION = ROOT / "registry/2026-09-03_UniverseLab_SessionCheckpoint_v1.33.json"

EXPECTED_FAMILIES = {
    "UL-CLM-FLRW-BACKGROUND-001",
    "UL-CLM-DISTANCE-GEOMETRY-001",
    "UL-CLM-LINEAR-GROWTH-001",
    "UL-CLM-BRIDGE-BACKGROUND-001",
    "UL-CLM-BRIDGE-IDENTIFIABILITY-001",
    "UL-CLM-BRIDGE-UNRELEASED-OBSERVABLES-001",
    "UL-CLM-PARENT-FORWARD-MAP-001",
    "UL-CLM-PHYSICAL-SOLUTION-STABILITY-001",
    "UL-CLM-DATA-LIKELIHOOD-001",
    "UL-CLM-EMERGENCE-SEPARATION-001",
    "UL-CLM-PREDICTIONS-FALSIFIERS-001",
    "UL-CLM-PUBLIC-STATUS-GOVERNANCE-001",
    "UL-CLM-FM0-PROGRAM-001",
    "UL-CLM-EDUCATIONAL-VISUAL-001",
    "UL-CLM-HISTORICAL-ARCHIVE-001",
}

ALLOWED_LINK_STATUS = {
    "VERIFIED_PRESENT",
    "REFERENCE_ONLY",
    "BLOCKED_BY_UNRELEASED_MAP",
    "MISSING_REQUIRED_LINK",
    "NOT_APPLICABLE",
    "DECLARED_PROSPECTIVE",
}

FIREWALLS = {
    "K1-D": "NOT_RELEASED",
    "K1-E": "NOT_ADMISSIBLE",
    "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
    "PHYSICAL_RESPONSE_RANK": "NOT_EXECUTED",
    "RATIFIED_HUMAN_TRUST_ROOT": "NOT_RATIFIED",
    "RUNTIME_ISSUANCE_BINDINGS": "BLOCKED",
    "AuthorizationDecision": "NOT_CREATED",
    "SingleUseGrant": "NOT_CREATED",
    "BACKEND_IMPORT": "NOT_EXECUTED",
    "SOLVER_EXECUTION": "NOT_EXECUTED",
    "FM-G0": "OPEN",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def assert_paths_exist(paths):
    for rel in paths:
        p = ROOT / rel
        assert p.exists(), f"missing repository evidence path: {rel}"


def has_gate_material(family: dict) -> bool:
    return any(
        family.get(key)
        for key in (
            "falsifiers",
            "forbidden_inference",
            "closure_conditions",
            "required_evidence",
            "required_release_conditions",
            "required_qualifier",
            "authority_rule",
        )
    )


def main() -> None:
    census = load(CENSUS)
    crosswalk = load(CROSSWALK)
    gaps = load(GAPS)
    medium = load(MEDIUM)
    manifest = load(MANIFEST)
    state = load(STATE)
    site = load(SITE)
    session = load(SESSION)

    assert crosswalk["basis_main_commit"] == "e4e92090d313abf8a53d7b7354923983c9cda939"
    assert crosswalk["family_count"] == 15
    assert gaps["basis_main_commit"] == crosswalk["basis_main_commit"]
    assert gaps["gap_count"] == 11
    assert gaps["blocking_scientific_gap_count"] == 10
    assert gaps["governance_provenance_gap_count"] == 1

    census_map = {f["claim_family_id"]: f for f in census["claim_families"]}
    crosswalk_map = {f["claim_family_id"]: f for f in crosswalk["families"]}
    assert set(census_map) == EXPECTED_FAMILIES
    assert set(crosswalk_map) == EXPECTED_FAMILIES
    assert len(crosswalk_map) == len(crosswalk["families"]) == 15

    axes = ("claim", "equation_or_derivation", "code", "test", "data", "falsifier_or_gate")
    for family_id, row in crosswalk_map.items():
        family = census_map[family_id]
        for axis in axes:
            assert row[axis] in ALLOWED_LINK_STATUS, (family_id, axis, row[axis])
        assert row["claim"] == "VERIFIED_PRESENT"

        if row["equation_or_derivation"] == "VERIFIED_PRESENT":
            assert family.get("equations"), f"{family_id} lacks declared equations"
        if row["code"] == "VERIFIED_PRESENT":
            assert family.get("code_paths"), f"{family_id} lacks code_paths"
            assert_paths_exist(family["code_paths"])
        if row["test"] == "VERIFIED_PRESENT":
            assert family.get("test_paths"), f"{family_id} lacks test_paths"
            assert_paths_exist(family["test_paths"])
        if row["falsifier_or_gate"] == "VERIFIED_PRESENT":
            assert has_gate_material(family), f"{family_id} lacks a falsifier/gate declaration"

        # Every explicitly bound source/code/test path from the family catalog
        # must still resolve in the repository. Presence is not physical proof.
        assert_paths_exist(family.get("source_paths", []))
        assert_paths_exist(family.get("code_paths", []))
        assert_paths_exist(family.get("test_paths", []))

    gap_ids = [g["gap_id"] for g in gaps["gaps"]]
    assert len(gap_ids) == len(set(gap_ids)) == 11
    gap_families = {fid for g in gaps["gaps"] for fid in g["family_ids"]}
    for family_id, row in crosswalk_map.items():
        if "MISSING_REQUIRED_LINK" in {row[a] for a in axes}:
            assert family_id in gap_families, f"missing-link family not represented in gap register: {family_id}"

    assert [g["gap_id"] for g in gaps["gaps"] if g["severity"] == "P1_GOVERNANCE_PROVENANCE"] == ["UL-BVC-G11"]
    assert gaps["gaps"][-1]["status"] == "OPEN_NONPHYSICAL"

    # Band V-B must be fully contextually closed before V-C is admissible.
    assert medium["materialized_claim_candidates"] == 989
    assert medium["materialized_high_candidates"] == 0
    assert medium["materialized_medium_candidates"] == 42
    assert medium["result"]["medium_contextually_adjudicated_total"] == 42
    assert medium["result"]["medium_contextually_unadjudicated"] == 0
    assert medium["result"]["positive_physical_hzt_overclaims"] == 0
    assert medium["result"]["physical_claim_promotions"] == 0
    assert medium["physical_gate_effect"] == "NONE"
    assert medium["physical_evidence_effect"] == "NONE"

    # Current manifest firewalls stay closed. V-C may not promote them.
    for key, value in FIREWALLS.items():
        assert manifest["gates"][key] == value, (key, manifest["gates"][key], value)
    assert manifest["physical_gate_effect"] == "NONE"
    assert manifest["physical_evidence_effect"] == "NONE"
    assert crosswalk["physical_gate_effect"] == "NONE"
    assert crosswalk["physical_evidence_effect"] == "NONE"
    assert gaps["physical_gate_effect"] == "NONE"
    assert gaps["physical_evidence_effect"] == "NONE"

    # G11 is an observed provenance freshness defect, not a guessed one.
    assert state["active_analysis_block"]["status"] == "IMPLEMENTED_IN_CHANGESET_REVIEW_PENDING"
    assert state["public_claim_governance"]["medium_claim_gate"] == "NOT_STARTED"
    assert site["analysis_state"]["band_v_b_medium_claims"] == "NOT_STARTED"
    assert session["active_block"]["status"] == "IMPLEMENTED_IN_CHANGESET_REVIEW_PENDING"
    assert "BAND_VB_MEDIUM" in manifest["next_allowed_repository_step"]

    print(
        "UniverseLab Band V-C claim evidence crosswalk gate: PASS "
        "families=15 gaps=11 scientific_or_empirical_blocking=10 governance_provenance=1 "
        "band_vb_medium=42/42 physical_gate_effect=NONE physical_evidence_effect=NONE"
    )


if __name__ == "__main__":
    main()
