#!/usr/bin/env python3
"""Successor-aware Band V-B complete MEDIUM contextual adjudication gate.

The priority and completion ledgers remain an exact disjoint partition of the
42 frozen Band-V-A materialized MEDIUM candidates. Later append-only updates to
research-status*.html are treated as a declared live-corpus delta and may not
rewrite the historical 42/42 adjudication or create lexical HIGH claims.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PRIORITY = ROOT / "registry/2026-09-04_UniverseLab_PublicScientificMediumPriorityAdjudication_v1.0.json"
COMPLETION = ROOT / "registry/2026-09-04_UniverseLab_PublicScientificMediumCompletionAdjudication_v1.0.json"
SUMMARY = ROOT / "registry/2026-09-04_UniverseLab_PublicScientificMediumAdjudicationSummary_v1.0.json"
CANDIDATES = ROOT / "registry/2026-09-03_UniverseLab_PublicScientificClaimLexicalCandidates_v0.1.json"
ASSIGNMENTS = ROOT / "registry/2026-09-03_UniverseLab_PublicScientificClaimFamilyAssignments_v0.1.json"
SCANNER = ROOT / "tools/2026-09-03_extract_UniverseLab_PublicScientificClaims_v1.0.py"
STATUS_DELTA_PATHS = {"research-status.html", "research-status-en.html"}

EXPECTED_CLASS_COUNTS = {
    "HISTORICAL_INFRASTRUCTURE_DESCRIPTION": 1,
    "INTERNAL_REFERENCE_KERNEL_VALIDATION": 2,
    "LOCAL_MATHEMATICAL_DERIVATION_SCOPED": 1,
    "METADATA_OR_SCOPE_DESCRIPTION": 12,
    "METHODOLOGY_GATE_NOT_FIT_RESULT": 1,
    "METHOD_FRAMEWORK_NOT_COMPLETED_REDUCTION": 4,
    "NEGATED_SCOPE_FIREWALL": 1,
    "OBSERVABLE_TARGET_MAP_NOT_THEORY_PREDICTION": 1,
    "OPEN_PROOF_OBLIGATION_NOT_IDENTIFIED": 2,
    "PROGRAM_ROADMAP_NOT_RESULT": 6,
    "STATUS_LEGEND_DEFINITION": 1,
    "UI_INPUT_LABEL_NOT_CONFIRMATION": 1,
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
    priority = load(PRIORITY)
    completion = load(COMPLETION)
    summary = load(SUMMARY)
    candidates = load(CANDIDATES)
    assignments = load(ASSIGNMENTS)

    assert completion["basis_main_commit"] == "32bd028ace1068a400067f8c890137b27c05fa3c"
    assert completion["scope"]["candidate_count"] == 33
    assert completion["scope"]["preliminary_risk_scores"] == [4, 5]
    assert completion["class_counts"] == EXPECTED_CLASS_COUNTS
    assert completion["physical_gate_effect"] == "NONE"
    assert completion["physical_evidence_effect"] == "NONE"

    candidate_map = {row["claim_id"]: row for row in candidates["candidates"]}
    assignment_map = {row["claim_id"]: row for row in assignments["assignments"]}
    materialized_medium = {
        row["claim_id"] for row in candidates["candidates"]
        if row["preliminary_risk_class"] == "MEDIUM"
    }
    materialized_high = {
        row["claim_id"] for row in candidates["candidates"]
        if row["preliminary_risk_class"] == "HIGH"
    }
    priority_ids = {row["claim_id"] for row in priority["records"]}
    completion_ids = {row["claim_id"] for row in completion["records"]}

    assert len(candidates["candidates"]) == 989
    assert len(materialized_medium) == 42
    assert materialized_high == set()
    assert len(priority_ids) == 9
    assert len(completion_ids) == 33
    assert priority_ids.isdisjoint(completion_ids)
    assert priority_ids | completion_ids == materialized_medium

    for row in completion["records"]:
        claim_id = row["claim_id"]
        candidate = candidate_map[claim_id]
        assignment = assignment_map[claim_id]
        assert candidate["preliminary_risk_class"] == "MEDIUM"
        assert candidate["preliminary_risk_score"] in (4, 5)
        assert candidate["preliminary_risk_score"] == row["risk_score"]
        assert candidate["path"] == row["path"]
        assert assignment["manual_review_required"] is True
        assert assignment["routing_status"] in {
            "AUTOMATED_FAMILY_ROUTING_NOT_ADJUDICATED",
            "AUTOMATED_FALLBACK_ROUTING_MANUAL_REVIEW_REQUIRED",
        }

    result = completion["global_result"]
    assert result["completion_candidates"] == 33
    assert result["contextually_adjudicated"] == 33
    assert result["positive_physical_hzt_overclaims"] == 0
    assert result["empirical_hzt_confirmation_claims"] == 0
    assert result["complete_parent_derivation_promotions"] == 0
    assert result["physical_claim_promotions"] == 0
    assert result["locally_scoped_mathematical_derivation_claims"] == 1
    assert result["internal_reference_kernel_validation_claims"] == 2
    assert result["contextually_unadjudicated_medium_after_this_block"] == 0

    assert summary["materialized_claim_candidates"] == 989
    assert summary["materialized_high_candidates"] == 0
    assert summary["materialized_medium_candidates"] == 42
    assert summary["result"]["medium_contextually_adjudicated_total"] == 42
    assert summary["result"]["medium_contextually_unadjudicated"] == 0
    assert summary["result"]["positive_physical_hzt_overclaims"] == 0
    assert summary["result"]["physical_claim_promotions"] == 0
    assert summary["lexical_state_after_adjudication"]["HIGH"] == 0
    assert summary["lexical_state_after_adjudication"]["MEDIUM"] == 42
    assert summary["physical_gate_effect"] == "NONE"
    assert summary["physical_evidence_effect"] == "NONE"

    # Critical context sentinels outside the intentionally refreshed status pages.
    contains("README.md", "## Auffindbarkeit", "Relevante Suchbegriffe")
    contains("hyperlab-en.html", "What does not follow automatically", "a regular cosmological origin", "It is not a closed or observationally confirmed theory of nature")
    contains("hyperzeit-material.html", "Jede Karte sagt, wofür die Quelle brauchbar ist und was sie ausdrücklich nicht für Hyperzeit beweist", "K1-D bleibt nicht freigegeben", "K1-E bleibt unzulässig")
    contains("index-en.html", "speculative 6D Hyperzeit hypotheses explicitly separated", "K1-D", "NOT RELEASED", "K1-E", "NOT ADMISSIBLE")
    contains("index.html", "experimentelle 6D-Hyperzeitmodelle", "experimentellen 6D-Hypothesen", "Spekulation klar getrennt")
    contains("tafelwerk.html", "Jede nicht etablierte Beziehung trägt einen sichtbaren Evidenzstatus", "abgeleitet\u201c bedeutet mathematisch aus einem angegebenen Ansatz abgeleitet")
    contains("2026-08-19_UniverseLab_BibliographyCatalog_v1.0.html", "menschenlesbare Ansicht der maschinenlesbaren Hyperzeit-Bibliographie")
    contains("2026-08-29_UniverseLab_Hyperzeit_10M_ResearchProgram_v1.0.html", "Primärer Pfad:", "CP01R4-HOLD", "Parent→Reduced-Brücke + NR-Grundgerüst", "FM-G0 bleibt offen")
    contains("about.html", "Wissenschaftliche Leitlinien", "Etabliert", "Standardmodell oder empirisch gut bestätigte Physik")
    contains("baryogenesis-v12.html", "als erste Klasse bestätigt", "Nullrichtungen sind nur Kandidaten erster Klasse", "vollständige Feldtheorie", "OFFEN")
    contains("guide.html", "etablierter Kosmologie", "numerischer Prüfung", "spekulativen Modellhypothesen")
    contains("hyperzeit-material-v2-en.html", "Literature compatibility is not treated as derivation or evidence for Hyperzeit", "Applicable only after forward-map release")
    contains("hyperzeit-material-v2.html", "nicht den Bestätigungsgrad der Theorie", "K=3H_a+2H_b", "=-6H_a^2-12H_aH_b-2H_b^2", "Parent Action", "Ghostfreiheit", "Forward Model")
    contains("hyperzeit-methods-en.html", "claims that are not transferable to Hyperzeit", "Controlled dimensional reduction", "Gauge reduction, constraints and boundary structure must be handled separately")
    contains("hyperzeit-methods.html", "Kontrolliertes Ziel für 6D→4D", "nicht als bereits bewiesene Brücke")
    contains("legacy.html", "historische Arbeitsnotiz", "H19-H28 · Konditional", "Brauchbare EFT-Schablonen")
    contains("solver-hub-en.html", "PLANNED", "Cosmology / Likelihood", "Permitted only after a released fundamental-to-observable forward map exists")
    contains("solver-hub.html", "Work-package completion != solver release", "Cosmology / Likelihood", "Erst nach Freigabe der fundamentalen Forward-Map")
    contains("universelab-audit-2026-07-31.html", "fehlerkontrollierte 6D→4D-Reduktion", "K1-E bleibt selbst danach separat", "Modellselektion ist keine Bestätigung einer ontologischen Interpretation")
    contains("validation-en.html", "Validated scope", "Not released", "an internal PASS is not empirical confirmation of a model")
    contains("validation.html", "Geprüfter Scope", "Nicht freigegeben", "Ein PASS bestätigt ausschließlich die interne mathematische, numerische und sprachübergreifende Konsistenz")

    # Successor status pages preserve the same epistemic firewalls while adding
    # Band-V-C audit progress.
    contains("research-status-en.html", "Open proof obligations", "What is not identified", "the complete parent→reduced→observable map", "not evidence for HZT")
    contains("research-status.html", "Offene Beweispflichten", "Was nicht identifiziert ist", "vollständige Parent→Reduced→Observable-Map", "keine Evidenz für HZT")

    # Re-extract the live corpus. Only the two declared status pages may change
    # claim IDs relative to the frozen 989-candidate Band-V-A/V-B register.
    scanner = module("ul_band_vb_medium_completion_scanner_successor", SCANNER)
    rows, scanner_summary = scanner.extract(ROOT)
    high = [row for row in rows if row.preliminary_risk_class == "HIGH"]
    assert high == [], [(row.path, row.source_line, row.text) for row in high]

    frozen_nonstatus = {
        row["claim_id"] for row in candidates["candidates"]
        if row["path"] not in STATUS_DELTA_PATHS
    }
    live_nonstatus = {
        row.claim_id for row in rows
        if row.path not in STATUS_DELTA_PATHS
    }
    assert live_nonstatus == frozen_nonstatus, {
        "missing_outside_status": sorted(frozen_nonstatus - live_nonstatus),
        "new_outside_status": sorted(live_nonstatus - frozen_nonstatus),
    }
    assert all(row.preliminary_risk_class != "HIGH" for row in rows if row.path in STATUS_DELTA_PATHS)
    assert scanner_summary["physical_gate_effect"] == "NONE"
    assert scanner_summary["physical_evidence_effect"] == "NONE"

    print(
        "UniverseLab Band V-B MEDIUM completion gate: PASS "
        f"frozen_medium=42 context_adjudicated=42 context_unadjudicated=0 current_live_claims={len(rows)} "
        "current_high=0 status_delta_paths=2 positive_overclaims=0 physical_promotions=0"
    )


if __name__ == "__main__":
    main()
