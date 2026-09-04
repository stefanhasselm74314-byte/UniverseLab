#!/usr/bin/env python3
"""Band V-B priority MEDIUM contextual adjudication gate.

The gate adjudicates the nine materialized MEDIUM candidates with risk score
>= 6. It is a public-claim context audit only and must not promote physical
evidence, parent derivation, K1-D/K1-E, authorization, or solver execution.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "registry/2026-09-04_UniverseLab_PublicScientificMediumPriorityAdjudication_v1.0.json"
CANDIDATES = ROOT / "registry/2026-09-03_UniverseLab_PublicScientificClaimLexicalCandidates_v0.1.json"
ASSIGNMENTS = ROOT / "registry/2026-09-03_UniverseLab_PublicScientificClaimFamilyAssignments_v0.1.json"
SCANNER = ROOT / "tools/2026-09-03_extract_UniverseLab_PublicScientificClaims_v1.0.py"

EXPECTED_IDS = {
    "UL-CLAIM-CANDIDATE-DEADAD88A45BD4C2",
    "UL-CLAIM-CANDIDATE-75139DBB4E3BF354",
    "UL-CLAIM-CANDIDATE-E57BCD10CED0C7C3",
    "UL-CLAIM-CANDIDATE-9F3D3674A433EF77",
    "UL-CLAIM-CANDIDATE-ABE36E9E61CE8C2E",
    "UL-CLAIM-CANDIDATE-77A2A1C9E6CBF71E",
    "UL-CLAIM-CANDIDATE-5FF62CD3FB3CBD13",
    "UL-CLAIM-CANDIDATE-81BFEAE4C1F181E3",
    "UL-CLAIM-CANDIDATE-A0E49DE6A446BC01",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def contains(path: str, *needles: str) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    for needle in needles:
        assert needle in text, (path, needle)


def main() -> None:
    ledger = load(LEDGER)
    candidates = load(CANDIDATES)
    assignments = load(ASSIGNMENTS)

    assert ledger["schema"] == "universelab.public-scientific-medium-priority-adjudication.v1"
    assert ledger["basis_main_commit"] == "edeab749981781a08b0d449984840ab024b0a8f8"
    assert ledger["scope"]["candidate_count"] == 9
    assert ledger["scope"]["minimum_preliminary_risk_score"] == 6
    assert ledger["physical_gate_effect"] == "NONE"
    assert ledger["physical_evidence_effect"] == "NONE"

    records = {row["claim_id"]: row for row in ledger["records"]}
    assert set(records) == EXPECTED_IDS
    assert len(records) == 9

    candidate_map = {row["claim_id"]: row for row in candidates["candidates"]}
    assignment_map = {row["claim_id"]: row for row in assignments["assignments"]}
    selected_from_materialized = {
        row["claim_id"]
        for row in candidates["candidates"]
        if row["preliminary_risk_class"] == "MEDIUM" and row["preliminary_risk_score"] >= 6
    }
    assert selected_from_materialized == EXPECTED_IDS

    for claim_id, record in records.items():
        candidate = candidate_map[claim_id]
        assignment = assignment_map[claim_id]
        assert candidate["preliminary_risk_class"] == "MEDIUM"
        assert candidate["preliminary_risk_score"] >= 6
        assert candidate["path"] == record["path"]
        assert candidate["source_sha256"] == record["source_sha256"]
        assert assignment["family_ids"] == record["family_ids"]
        assert assignment["manual_review_required"] is True
        assert record["positive_physical_hzt_claim"] is False
        assert record["parent_derivation_established"] is False
        assert record["empirical_evidence_claim"] is False
        assert record["physical_evidence_effect"] == "NONE"

    result = ledger["global_result"]
    assert result == {
        "priority_medium_candidates": 9,
        "contextually_adjudicated": 9,
        "positive_physical_hzt_overclaims": 0,
        "empirical_confirmation_claims": 0,
        "parent_derivation_promotions": 0,
        "historical_or_rejected_claims": 2,
        "open_requirements_or_obligations": 2,
        "method_or_documentation_scope_descriptions": 5,
        "physical_claim_promotions": 0,
        "remaining_materialized_medium_candidates_before_lower_score_review": 33,
    }

    # Context sentinels: the isolated lexical phrase must not be allowed to
    # override the surrounding page semantics.
    contains(
        "legacy.html",
        "Claim Firewall",
        "not admissible",
        "Keine freigegebene vollständige Forward Map",
        "historical",
        "Keine aktuelle Parentableitung",
    )
    contains(
        "hyperzeit-methods.html",
        "beweist jedoch nicht, dass die 4D-Lorentzstruktur aus HPVS hervorgeht",
        "Für Hyperzeit müsste ein eigener RG-Fluss",
    )
    contains(
        "guide-en.html",
        "Observational comparison becomes admissible only when every required map is released",
        "A fitted parameter is not a derivation from the six-dimensional parent sector",
    )
    contains(
        "hyperzeit-methods-en.html",
        "become theory tests only after a released forward map exists",
        "A good fit without that derivation is not evidence for Hyperzeit",
    )
    contains(
        "hyperzeit-material-v2-en.html",
        "Literature compatibility is not treated as derivation or evidence for Hyperzeit",
        "Applicable only after forward-map release",
    )
    contains(
        "hyperzeit-material-v2.html",
        "nicht den Bestätigungsgrad der Theorie",
        "Erst nach Freigabe des Forward-Modells",
    )
    contains(
        "navigator.html",
        "Methoden und Qualitätssicherung",
        "Hilbertraum, RG, kontrollierte 6D→4D-Reduktion, Likelihood- und Solverstandards",
    )
    contains(
        "research-status-en.html",
        "Open proof obligations",
        "What is not identified",
        "an HZT-M0 likelihood or evidence interpretation;",
    )

    # Re-run the public scanner. This tranche does not rewrite public pages;
    # therefore the lexical queue remains 42 MEDIUM items, but the exact nine
    # highest-score items are now manually context-adjudicated in the ledger.
    scanner = module("ul_band_vb_medium_priority_scanner", SCANNER)
    rows, summary = scanner.extract(ROOT)
    high = [row for row in rows if row.preliminary_risk_class == "HIGH"]
    medium = [row for row in rows if row.preliminary_risk_class == "MEDIUM"]
    priority = [row for row in medium if row.preliminary_risk_score >= 6]
    assert high == []
    assert len(rows) == 989
    assert len(medium) == 42
    assert {row.claim_id for row in priority} == EXPECTED_IDS
    assert summary["physical_gate_effect"] == "NONE"
    assert summary["physical_evidence_effect"] == "NONE"

    print(
        "UniverseLab Band V-B priority MEDIUM gate: PASS "
        "materialized_medium=42 priority_reviewed=9 remaining_lower_score=33 "
        "positive_overclaims=0 physical_promotions=0"
    )


if __name__ == "__main__":
    main()
