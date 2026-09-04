#!/usr/bin/env python3
"""Fail-closed Band V-C G11 state-freshness closure gate.

The state-freshness repair intentionally changes the DE/EN canonical public
status pages. Therefore the Band-V-A/V-B 989-candidate corpus is historical
provenance after this changeset. This gate proves that the live claim delta is
confined to those two status pages and creates no new HIGH claim. Historical
claim ledgers are never rewritten in place.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools/2026-09-01_validate_UniverseLab_CurrentMainCanonicalStateReconciliation_v1.0.py"
SCANNER = ROOT / "tools/2026-09-03_extract_UniverseLab_PublicScientificClaims_v1.0.py"
HISTORICAL_CANDIDATES = ROOT / "registry/2026-09-03_UniverseLab_PublicScientificClaimLexicalCandidates_v0.1.json"
CURRENT = ROOT / "registry/2026-09-04_UniverseLab_CurrentMainCanonicalState_v1.3.json"
SITE = ROOT / "registry/2026-09-04_UniverseLab_SiteState_v1.4.json"
CHECKPOINT = ROOT / "registry/2026-09-04_UniverseLab_SessionCheckpoint_v1.34.json"
ALIAS = ROOT / "registry/session-checkpoint-latest.json"
CLOSURE = ROOT / "registry/2026-09-04_UniverseLab_BandVC_G11_StateFreshnessClosure_v1.0.json"
MANIFEST = ROOT / "project-manifest.json"
SHELL = ROOT / "assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js"
DE = ROOT / "research-status.html"
EN = ROOT / "research-status-en.html"
OLD_CURRENT = ROOT / "registry/2026-09-03_UniverseLab_CurrentMainCanonicalState_v1.2.json"
OLD_SITE = ROOT / "registry/2026-09-03_UniverseLab_SiteState_v1.3.json"
OLD_CHECKPOINT = ROOT / "registry/2026-09-03_UniverseLab_SessionCheckpoint_v1.33.json"

BASIS = "3022dc8aac27ed2054fdb7643708fe57440b9256"
TREE = "b073c74b53fb0119ca9f72e3de3ad9399796266d"
STATUS_DELTA_PATHS = {"research-status.html", "research-status-en.html"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    validator = module("ul_state_reconcile_post_vc", VALIDATOR)
    validator.validate(ROOT, strict_source_existence=True)

    current, site, checkpoint = load(CURRENT), load(SITE), load(CHECKPOINT)
    manifest, closure = load(MANIFEST), load(CLOSURE)

    assert ALIAS.read_bytes() == CHECKPOINT.read_bytes()
    assert current["basis_main_commit"] == site["basis_main_commit"] == checkpoint["basis_commit"] == manifest["basis_main_commit"] == BASIS
    assert current["basis_main_tree"] == site["basis_main_tree"] == checkpoint["basis_tree"] == manifest["basis_main_tree"] == TREE
    assert current["snapshot_date"] == site["snapshot_date"] == manifest["release_date"] == "2026-09-04"
    assert checkpoint["timestamp"].startswith("2026-09-04T")

    assert current["public_claim_governance"]["high_claim_gate"] == "COMPLETE_MERGED_CURRENT_LEXICAL_HIGH_0"
    assert current["public_claim_governance"]["medium_claim_gate"] == "COMPLETE_MERGED_42_OF_42_CONTEXTUALLY_ADJUDICATED"
    assert current["public_claim_governance"]["band_vc_gate"] == "MERGED_15_FAMILIES_11_MISSING_LINKS_REGISTERED"
    assert site["analysis_state"]["band_v_b_medium_claims"] == "COMPLETE_MERGED_42_OF_42_CONTEXTUALLY_ADJUDICATED"
    assert site["analysis_state"]["band_v_c"] == "MERGED_15_FAMILY_CLAIM_EVIDENCE_CROSSWALK"
    assert checkpoint["completed_blocks"]["band_v_c"]["merge_commit"] == BASIS

    assert closure["gap_id"] == "UL-BVC-G11"
    assert closure["closure_status"] == "IMPLEMENTED_REVIEW_PENDING"
    assert closure["scientific_missing_links_after_closure"] == 10
    assert closure["governance_provenance_missing_links_after_closure"] == 0
    assert closure["physical_gate_effect"] == closure["physical_evidence_effect"] == "NONE"

    expected_firewalls = {
        "FM-G0": "OPEN",
        "RATIFIED_HUMAN_TRUST_ROOT": "NOT_RATIFIED",
        "RUNTIME_ISSUANCE_BINDINGS": "BLOCKED",
        "AuthorizationDecision": "NOT_CREATED",
        "SingleUseGrant": "NOT_CREATED",
        "BACKEND_IMPORT": "NOT_EXECUTED",
        "SOLVER_EXECUTION": "NOT_EXECUTED",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "PHYSICAL_RESPONSE_RANK": "NOT_EXECUTED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
    }
    for key, expected in expected_firewalls.items():
        assert manifest["gates"][key] == expected, (key, manifest["gates"][key], expected)
        assert closure["unchanged_firewalls"][key] == expected
    assert manifest["physical_gate_effect"] == manifest["physical_evidence_effect"] == "NONE"

    assert manifest["canonical_state"] == "registry/2026-09-04_UniverseLab_CurrentMainCanonicalState_v1.3.json"
    assert manifest["site_state"] == "registry/2026-09-04_UniverseLab_SiteState_v1.4.json"
    assert manifest["session_checkpoint"] == "registry/2026-09-04_UniverseLab_SessionCheckpoint_v1.34.json"
    assert manifest["next_allowed_repository_step"] == "BAND_VC_MISSING_LINK_REMEDIATION_NO_PHYSICAL_EXECUTION"

    shell = SHELL.read_text(encoding="utf-8")
    de = DE.read_text(encoding="utf-8")
    en = EN.read_text(encoding="utf-8")
    assert "./registry/2026-09-04_UniverseLab_SiteState_v1.4.json" in shell
    assert "./registry/2026-09-03_UniverseLab_SiteState_v1.3.json" not in shell
    for html in (de, en):
        assert "registry/2026-09-04_UniverseLab_CurrentMainCanonicalState_v1.3.json" in html
        assert "registry/2026-09-04_UniverseLab_SiteState_v1.4.json" in html
        assert "registry/2026-09-04_UniverseLab_SessionCheckpoint_v1.34.json" in html
        assert "registry/2026-09-04_UniverseLab_PublicScientificMediumAdjudicationSummary_v1.0.json" in html
        assert "registry/2026-09-04_UniverseLab_BandVC_ClaimEvidenceCrosswalk_v1.0.json" in html
        assert "registry/2026-09-04_UniverseLab_BandVC_MissingLinkRegister_v1.0.json" in html
    assert "42/42" in de and "42/42" in en
    assert "15" in de and "15" in en
    assert "K1-D" in de and "NOT RELEASED" in de and "K1-E" in de and "NOT ADMISSIBLE" in de
    assert "K1-D" in en and "NOT RELEASED" in en and "K1-E" in en and "NOT ADMISSIBLE" in en
    assert "keine physische HZT-Bestätigung" in de
    assert "not physical confirmation of HZT" in en

    # Historical snapshots remain append-only and retain their old post-Band-V-A basis.
    old_current, old_site, old_checkpoint = load(OLD_CURRENT), load(OLD_SITE), load(OLD_CHECKPOINT)
    assert old_current["basis_main_commit"] == "8351f2d7d9d0852768014c1fdfbbecfb4432fa55"
    assert old_site["basis_main_commit"] == "8351f2d7d9d0852768014c1fdfbbecfb4432fa55"
    assert old_checkpoint["basis_commit"] == "8351f2d7d9d0852768014c1fdfbbecfb4432fa55"

    # Post-V-C claim-delta audit. The frozen 989-candidate registry is historical.
    # Outside the two deliberately refreshed public status pages, the materialized
    # claim-ID set must be identical. The refreshed pages may change IDs/text but
    # must introduce no HIGH claim and must retain self-contained firewalls.
    historical = load(HISTORICAL_CANDIDATES)
    assert historical["candidate_count"] == 989
    historical_outside = {
        row["claim_id"] for row in historical["candidates"] if row["path"] not in STATUS_DELTA_PATHS
    }
    scanner = module("ul_post_vc_g11_claim_scanner", SCANNER)
    live_rows, live_summary = scanner.extract(ROOT)
    live_outside = {row.claim_id for row in live_rows if row.path not in STATUS_DELTA_PATHS}
    assert live_outside == historical_outside, (
        "claim drift outside declared status delta",
        sorted(historical_outside - live_outside)[:10],
        sorted(live_outside - historical_outside)[:10],
    )
    live_high = [row for row in live_rows if row.preliminary_risk_class == "HIGH"]
    assert live_high == [], [(row.path, row.source_line, row.text) for row in live_high]
    live_status_rows = [row for row in live_rows if row.path in STATUS_DELTA_PATHS]
    assert live_status_rows
    assert all(row.preliminary_risk_class != "HIGH" for row in live_status_rows)
    assert any("keine physische HZT-Bestätigung" in row.text for row in live_status_rows if row.path == "research-status.html")
    assert any("not physical confirmation of HZT" in row.text for row in live_status_rows if row.path == "research-status-en.html")
    assert live_summary["physical_gate_effect"] == "NONE"
    assert live_summary["physical_evidence_effect"] == "NONE"

    print(
        "UniverseLab Band V-C G11 state freshness closure gate: PASS "
        "successor=v1.3/v1.4/v1.34 alias_byte_identical=yes "
        "band_vb_historical_medium=42/42 band_vc_families=15 scientific_missing_links=10 "
        f"governance_provenance_missing_links=0 live_claims={len(live_rows)} live_high=0 "
        f"status_delta_claims={len(live_status_rows)} physical_gate_effect=NONE physical_evidence_effect=NONE"
    )


if __name__ == "__main__":
    main()
