#!/usr/bin/env python3
"""Band V-B historical + post-V-C successor MEDIUM closure regression.

Proves both layers simultaneously:
- the historical Band-V-B ledgers remain an exact 42/42 adjudication;
- the current materialized 993-claim corpus has HIGH=0, MEDIUM=46 and is
  contextually covered by 39 still-live historical IDs plus seven adjudicated
  status-page successor IDs. Three historical status-page MEDIUM IDs are retired.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PRIORITY = ROOT / "registry/2026-09-04_UniverseLab_PublicScientificMediumPriorityAdjudication_v1.0.json"
COMPLETION = ROOT / "registry/2026-09-04_UniverseLab_PublicScientificMediumCompletionAdjudication_v1.0.json"
HISTORICAL_SUMMARY = ROOT / "registry/2026-09-04_UniverseLab_PublicScientificMediumAdjudicationSummary_v1.0.json"
CURRENT_CANDIDATES = ROOT / "registry/2026-09-03_UniverseLab_PublicScientificClaimLexicalCandidates_v0.1.json"
CURRENT_ASSIGNMENTS = ROOT / "registry/2026-09-03_UniverseLab_PublicScientificClaimFamilyAssignments_v0.1.json"
DELTA = ROOT / "registry/2026-09-04_UniverseLab_BandVC_StatusPageMediumDeltaAdjudication_v1.0.json"
SCANNER = ROOT / "tools/2026-09-03_extract_UniverseLab_PublicScientificClaims_v1.0.py"
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


def contains(path: str, *needles: str) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    for needle in needles:
        assert needle in text, (path, needle)


def main() -> None:
    priority = load(PRIORITY)
    completion = load(COMPLETION)
    historical = load(HISTORICAL_SUMMARY)
    candidates = load(CURRENT_CANDIDATES)
    assignments = load(CURRENT_ASSIGNMENTS)
    delta = load(DELTA)

    historical_ids = {row["claim_id"] for row in priority["records"]} | {row["claim_id"] for row in completion["records"]}
    assert len(priority["records"]) == 9
    assert len(completion["records"]) == 33
    assert len(historical_ids) == 42
    assert historical["materialized_claim_candidates"] == 989
    assert historical["materialized_high_candidates"] == 0
    assert historical["materialized_medium_candidates"] == 42
    assert historical["result"]["medium_contextually_adjudicated_total"] == 42
    assert historical["result"]["medium_contextually_unadjudicated"] == 0
    assert historical["result"]["positive_physical_hzt_overclaims"] == 0
    assert historical["result"]["physical_claim_promotions"] == 0
    assert historical["physical_gate_effect"] == "NONE"
    assert historical["physical_evidence_effect"] == "NONE"

    current_rows = candidates["candidates"]
    current_medium_rows = [row for row in current_rows if row["preliminary_risk_class"] == "MEDIUM"]
    current_high_rows = [row for row in current_rows if row["preliminary_risk_class"] == "HIGH"]
    current_medium_ids = {row["claim_id"] for row in current_medium_rows}
    assert len(current_rows) == 993
    assert current_high_rows == []
    assert len(current_medium_ids) == 46
    assert assignments["candidate_count"] == 993
    assert assignments["assignment_count"] == 993
    assert assignments["high_medium_candidate_count"] == 46
    assert assignments["unknown_family_ids"] == 0
    assert assignments["unmapped_candidates"] == 0

    still_live_historical = current_medium_ids & historical_ids
    retired_historical = historical_ids - current_medium_ids
    successor_delta = current_medium_ids - historical_ids
    assert len(still_live_historical) == 39
    assert len(retired_historical) == 3
    assert len(successor_delta) == 7

    delta_ids = {row["claim_id"] for row in delta["records"]}
    assert delta["scope"]["historical_band_vb_medium_ids"] == 42
    assert delta["scope"]["historical_medium_ids_still_live"] == 39
    assert delta["scope"]["historical_medium_ids_retired_by_status_page_successor"] == 3
    assert delta["scope"]["current_materialized_claim_candidates"] == 993
    assert delta["scope"]["current_materialized_high_candidates"] == 0
    assert delta["scope"]["current_materialized_medium_candidates"] == 46
    assert delta["scope"]["new_current_medium_ids_not_in_historical_band_vb_set"] == 7
    assert delta_ids == successor_delta
    assert all(row["path"] in STATUS_PATHS for row in delta["records"])
    assert all(row["positive_physical_hzt_claim"] is False for row in delta["records"])
    assert all(row["empirical_confirmation_claim"] is False for row in delta["records"])
    assert all(row["parent_derivation_claim"] is False for row in delta["records"])
    assert delta["global_result"]["contextually_adjudicated"] == 7
    assert delta["global_result"]["contextually_unadjudicated"] == 0
    assert delta["global_result"]["physical_claim_promotions"] == 0
    assert delta["physical_gate_effect"] == "NONE"
    assert delta["physical_evidence_effect"] == "NONE"

    historical_paths = {row["claim_id"]: row["path"] for row in priority["records"] + completion["records"]}
    assert all(historical_paths[claim_id] in STATUS_PATHS for claim_id in retired_historical)

    contains("research-status-en.html", "As a repository-audit mapping only", "not physical evidence for HZT", "Open proof obligations", "the complete parent→reduced→observable map")
    contains("research-status.html", "Als reine Repository-Auditzuordnung", "keine physische Evidenz für HZT", "Offene Beweispflichten", "vollständige Parent→Reduced→Observable-Map")

    scanner = module("ul_medium_completion_current_scanner", SCANNER)
    live, live_summary = scanner.extract(ROOT)
    live_high = [row for row in live if row.preliminary_risk_class == "HIGH"]
    live_medium = [row for row in live if row.preliminary_risk_class == "MEDIUM"]
    assert live_high == [], [(row.path, row.source_line, row.text) for row in live_high]
    assert len(live) == 993
    assert len(live_medium) == 46
    assert {row.claim_id for row in live_medium} == current_medium_ids
    assert live_summary["physical_gate_effect"] == "NONE"
    assert live_summary["physical_evidence_effect"] == "NONE"

    print(
        "UniverseLab MEDIUM closure: PASS historical=42/42 current=46/46 "
        "still_live_historical=39 retired_historical=3 successor_delta=7/7 "
        "current_high=0 physical_promotions=0"
    )


if __name__ == "__main__":
    main()
