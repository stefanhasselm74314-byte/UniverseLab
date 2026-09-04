#!/usr/bin/env python3
"""Fail-closed Band V-C G11 state-freshness + claim-delta closure gate."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools/2026-09-01_validate_UniverseLab_CurrentMainCanonicalStateReconciliation_v1.0.py"
SCANNER = ROOT / "tools/2026-09-03_extract_UniverseLab_PublicScientificClaims_v1.0.py"
CURRENT_CANDIDATES = ROOT / "registry/2026-09-03_UniverseLab_PublicScientificClaimLexicalCandidates_v0.1.json"
HISTORICAL_PRIORITY = ROOT / "registry/2026-09-04_UniverseLab_PublicScientificMediumPriorityAdjudication_v1.0.json"
HISTORICAL_COMPLETION = ROOT / "registry/2026-09-04_UniverseLab_PublicScientificMediumCompletionAdjudication_v1.0.json"
HISTORICAL_SUMMARY = ROOT / "registry/2026-09-04_UniverseLab_PublicScientificMediumAdjudicationSummary_v1.0.json"
DELTA = ROOT / "registry/2026-09-04_UniverseLab_BandVC_StatusPageMediumDeltaAdjudication_v1.0.json"
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
STATUS_PATHS = {"research-status.html", "research-status-en.html"}


def load(path: Path):
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    # Existing strict validator remains authoritative for pointer/firewall shape.
    validator = module("ul_state_reconcile_post_vc_current", VALIDATOR)
    validator.validate(ROOT, strict_source_existence=True)

    current, site, checkpoint = load(CURRENT), load(SITE), load(CHECKPOINT)
    manifest, closure, delta = load(MANIFEST), load(CLOSURE), load(DELTA)
    candidates = load(CURRENT_CANDIDATES)
    priority, completion, historical = load(HISTORICAL_PRIORITY), load(HISTORICAL_COMPLETION), load(HISTORICAL_SUMMARY)

    assert ALIAS.read_bytes() == CHECKPOINT.read_bytes()
    assert current["basis_main_commit"] == site["basis_main_commit"] == checkpoint["basis_commit"] == manifest["basis_main_commit"] == BASIS
    assert current["basis_main_tree"] == site["basis_main_tree"] == checkpoint["basis_tree"] == manifest["basis_main_tree"] == TREE
    assert current["snapshot_date"] == site["snapshot_date"] == manifest["release_date"] == "2026-09-04"
    assert checkpoint["timestamp"].startswith("2026-09-04T")

    # Historical 42/42 Band-V-B snapshot remains intact.
    historical_ids = {row["claim_id"] for row in priority["records"]} | {row["claim_id"] for row in completion["records"]}
    assert len(historical_ids) == 42
    assert historical["materialized_claim_candidates"] == 989
    assert historical["materialized_medium_candidates"] == 42
    assert historical["result"]["medium_contextually_adjudicated_total"] == 42
    assert historical["result"]["medium_contextually_unadjudicated"] == 0
    assert historical["result"]["physical_claim_promotions"] == 0

    # Current materialized corpus and exact seven-ID successor delta.
    current_medium = {row["claim_id"] for row in candidates["candidates"] if row["preliminary_risk_class"] == "MEDIUM"}
    current_high = [row for row in candidates["candidates"] if row["preliminary_risk_class"] == "HIGH"]
    assert len(candidates["candidates"]) == 993
    assert current_high == []
    assert len(current_medium) == 46
    still_live = current_medium & historical_ids
    retired = historical_ids - current_medium
    new_ids = current_medium - historical_ids
    assert len(still_live) == 39
    assert len(retired) == 3
    assert len(new_ids) == 7
    assert {row["claim_id"] for row in delta["records"]} == new_ids
    assert all(row["path"] in STATUS_PATHS for row in delta["records"])
    assert delta["global_result"]["contextually_adjudicated"] == 7
    assert delta["global_result"]["contextually_unadjudicated"] == 0
    assert delta["global_result"]["positive_physical_hzt_overclaims"] == 0
    assert delta["global_result"]["physical_claim_promotions"] == 0

    # Active state mirrors the layered provenance exactly.
    pcg = current["public_claim_governance"]
    assert pcg["current_materialized_claim_candidates"] == 993
    assert pcg["current_materialized_high_candidates"] == 0
    assert pcg["current_materialized_medium_candidates"] == 46
    assert pcg["historical_medium_ids_still_live"] == 39
    assert pcg["retired_historical_status_page_medium_ids"] == 3
    assert pcg["new_status_page_medium_ids"] == 7
    assert pcg["new_status_page_medium_contextually_adjudicated"] == 7
    assert pcg["current_medium_contextually_adjudicated"] == 46
    assert pcg["current_medium_contextually_unadjudicated"] == 0
    assert pcg["medium_claim_gate"] == "CURRENT_COMPLETE_46_OF_46_WITH_42_HISTORICAL_PLUS_7_SUCCESSOR_DELTA"
    assert pcg["band_vc_gate"] == "MERGED_15_FAMILIES_11_MISSING_LINKS_REGISTERED"
    assert site["analysis_state"]["current_materialized_claim_candidates"] == 993
    assert site["analysis_state"]["current_lexical_medium"] == 46
    assert site["analysis_state"]["current_medium_contextually_adjudicated"] == 46
    assert site["analysis_state"]["current_medium_contextually_unadjudicated"] == 0
    assert checkpoint["active_block"]["current_materialized_claim_candidates"] == 993
    assert checkpoint["active_block"]["current_lexical_medium"] == 46
    assert checkpoint["active_block"]["current_medium_contextually_adjudicated"] == 46
    assert checkpoint["active_block"]["current_medium_contextually_unadjudicated"] == 0
    assert manifest["public_claim_audit"]["current_materialized_claim_candidates"] == 993
    assert manifest["public_claim_audit"]["current_lexical_medium"] == 46
    assert manifest["public_claim_audit"]["current_medium_contextually_adjudicated"] == 46
    assert manifest["public_claim_audit"]["current_medium_contextually_unadjudicated"] == 0

    assert closure["gap_id"] == "UL-BVC-G11"
    assert closure["closure_status"] == "IMPLEMENTED_REVIEW_PENDING"
    assert closure["scientific_missing_links_after_closure"] == 10
    assert closure["governance_provenance_missing_links_after_closure"] == 0
    cp = closure["claim_delta_provenance"]
    assert cp["historical_band_vb_claim_candidates"] == 989
    assert cp["historical_band_vb_medium_candidates"] == 42
    assert cp["current_materialized_claim_candidates"] == 993
    assert cp["current_materialized_high_candidates"] == 0
    assert cp["current_materialized_medium_candidates"] == 46
    assert cp["historical_medium_ids_still_live"] == 39
    assert cp["retired_historical_status_page_medium_ids"] == 3
    assert cp["new_status_page_medium_ids"] == 7
    assert cp["new_status_page_medium_contextually_adjudicated"] == 7
    assert cp["current_medium_contextually_adjudicated"] == 46
    assert cp["current_medium_contextually_unadjudicated"] == 0
    assert closure["physical_gate_effect"] == closure["physical_evidence_effect"] == "NONE"

    expected_firewalls = {
        "FM-G0":"OPEN","RATIFIED_HUMAN_TRUST_ROOT":"NOT_RATIFIED","RUNTIME_ISSUANCE_BINDINGS":"BLOCKED",
        "AuthorizationDecision":"NOT_CREATED","SingleUseGrant":"NOT_CREATED","BACKEND_IMPORT":"NOT_EXECUTED",
        "SOLVER_EXECUTION":"NOT_EXECUTED","PHYSICAL_BACKGROUND":"NOT_ESTABLISHED","PHYSICAL_RESPONSE_RANK":"NOT_EXECUTED",
        "K1-D":"NOT_RELEASED","K1-E":"NOT_ADMISSIBLE",
    }
    for key, expected in expected_firewalls.items():
        assert manifest["gates"][key] == expected, (key, manifest["gates"][key], expected)
        assert closure["unchanged_firewalls"][key] == expected
    assert manifest["physical_gate_effect"] == manifest["physical_evidence_effect"] == "NONE"

    shell, de, en = SHELL.read_text(encoding="utf-8"), DE.read_text(encoding="utf-8"), EN.read_text(encoding="utf-8")
    assert "./registry/2026-09-04_UniverseLab_SiteState_v1.4.json" in shell
    for html in (de, en):
        assert "registry/2026-09-04_UniverseLab_CurrentMainCanonicalState_v1.3.json" in html
        assert "registry/2026-09-04_UniverseLab_SiteState_v1.4.json" in html
        assert "registry/2026-09-04_UniverseLab_SessionCheckpoint_v1.34.json" in html
        assert "registry/2026-09-04_UniverseLab_BandVC_ClaimEvidenceCrosswalk_v1.0.json" in html
    assert "Als reine Repository-Auditzuordnung" in de and "keine physische Evidenz für HZT" in de
    assert "As a repository-audit mapping only" in en and "not physical evidence for HZT" in en

    # Historical dated snapshots are untouched.
    assert load(OLD_CURRENT)["basis_main_commit"] == "8351f2d7d9d0852768014c1fdfbbecfb4432fa55"
    assert load(OLD_SITE)["basis_main_commit"] == "8351f2d7d9d0852768014c1fdfbbecfb4432fa55"
    assert load(OLD_CHECKPOINT)["basis_commit"] == "8351f2d7d9d0852768014c1fdfbbecfb4432fa55"

    # Live scanner independently reproduces current materialization and no HIGH.
    scanner = module("ul_post_vc_g11_current_scanner", SCANNER)
    live_rows, live_summary = scanner.extract(ROOT)
    live_high = [row for row in live_rows if row.preliminary_risk_class == "HIGH"]
    live_medium = [row for row in live_rows if row.preliminary_risk_class == "MEDIUM"]
    assert live_high == [], [(row.path, row.source_line, row.text) for row in live_high]
    assert len(live_rows) == 993
    assert len(live_medium) == 46
    assert {row.claim_id for row in live_medium} == current_medium
    assert live_summary["physical_gate_effect"] == live_summary["physical_evidence_effect"] == "NONE"

    print(
        "UniverseLab Band V-C G11 closure: PASS successor=v1.3/v1.4/v1.34 "
        "historical_medium=42/42 current_claims=993 current_medium=46/46 delta=7/7 "
        "current_high=0 scientific_missing_links=10 governance_provenance_missing_links=0 "
        "physical_gate_effect=NONE physical_evidence_effect=NONE"
    )


if __name__ == "__main__":
    main()
