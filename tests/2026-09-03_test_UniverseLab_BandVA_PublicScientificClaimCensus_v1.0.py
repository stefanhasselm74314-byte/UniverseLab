#!/usr/bin/env python3
"""Regression tests for the Band V-A public scientific claim census.

These tests guard lexical polarity, exact source provenance and routing
semantics only. They do not adjudicate scientific truth, change epistemic
status, create physical evidence or authorize execution.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCANNER = ROOT / "tools/2026-09-03_extract_UniverseLab_PublicScientificClaims_v1.0.py"
MAPPER = ROOT / "tools/2026-09-03_map_UniverseLab_PublicScientificClaimsToFamilies_v1.0.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


M = load_module("universelab_band_va_claim_scanner", SCANNER)
R = load_module("universelab_band_va_family_mapper", MAPPER)


def classify(text: str):
    block = M.Block(
        path="synthetic.html",
        source_sha256="0" * 64,
        page_scope="SYNTHETIC_TEST",
        manifest_status=None,
        tag="p",
        region="main",
        line=1,
        text=text,
    )
    return M.candidate_from(block, text)


def assert_firewall(text: str) -> None:
    item = classify(text)
    assert item is not None, text
    assert item.explicit_status != "CLAIMED_PROVEN", (text, item)
    assert item.limiter_present is True, (text, item)
    assert item.preliminary_risk_class == "CONTEXT_OR_FIREWALL", (text, item)


def main() -> None:
    # P2 polarity regression: negated proof/evidence language must never be
    # inverted into a positive proof claim.
    for text in (
        "Was noch nicht bewiesen ist",
        "Insbesondere stellt die Anwendung keine bestätigte Ableitung einer 6D-Hyperzeit-Theorie dar.",
        "Nicht enthalten sind nichtlineares Wachstum und eine hergeleitete 6D-Hyperzeit-Kopplung.",
        "Sie beweist weder, dass Θ existiert, noch dass eine konkrete 6D-Mode den gewählten Quellenvektor erzeugt.",
        "Es beweist nicht, dass alle KK-, Metrik-, Flux- oder Radionbeiträge verschwinden.",
        "Ein bestandener 4×4-Benchmark beweist keine Ghostfreiheit des vollständigen 6D-Störungssystems.",
        "Noch keine 6D-Ableitung",
        "Jede Karte sagt, was sie ausdrücklich nicht für Hyperzeit beweist.",
        "Diese Erweiterung ist eine Sensitivitätsfläche, keine freigegebene Hyperzeit-Vorhersage.",
        "Blocker: vollständige 6D-Herleitung und Ghostfreiheit fehlen.",
        "Brücke Σ(a,k), η(a,k) nicht aus dem Parent-Sektor konstruiert.",
    ):
        assert_firewall(text)

    # Positive control remains a genuine high-risk proof claim.
    positive = classify("Die 6D-Theorie ist bewiesen.")
    assert positive is not None
    assert positive.explicit_status == "CLAIMED_PROVEN"
    assert positive.limiter_present is False
    assert positive.preliminary_risk_class == "HIGH"

    # Token-boundary regression: lexical terms must not fire inside unrelated
    # longer words (proven in Provenienz, Satz in Datensatz). Generic UI/module
    # label "Validation" is also not empirical confirmation by itself.
    assert "EVIDENCE_CONFIRMATION" not in M.categories("UniverseLab · Daten / Provenienz")
    assert M.explicit_status("UniverseLab · Daten / Provenienz") != "CLAIMED_PROVEN"
    assert M.explicit_status("Ein lesbarer Datensatz") != "CLAIMED_PROVEN"
    assert "EVIDENCE_CONFIRMATION" not in M.categories("Validation Console")

    # Navigation text must not leak through an ancestor header block.
    parser = M.VisibleBlockParser("synthetic.html", "1" * 64, "SYNTHETIC_TEST", None)
    parser.feed(
        "<header><nav>UL · UniverseLab Research status Solver Hub Observatory Comparison HyperLab Guide</nav>"
        "<p>Ein gültiger Hintergrund ist keine empirische Bestätigung.</p></header>"
    )
    candidates = []
    for block in parser.blocks:
        for sentence in M.split_sentences(block.text):
            item = M.candidate_from(block, sentence)
            if item:
                candidates.append(item)
    assert not any("Solver Hub Observatory" in row.text for row in candidates)
    assert any("keine empirische Bestätigung" in row.text for row in candidates)

    # Real repository provenance: the distance-firewall sentence belongs to the
    # local div on line 48, not the ancestor main block on line 24.
    rows, summary = M.extract(ROOT)
    assert summary["tracked_html_files"] >= 70
    distance = [
        row for row in rows
        if row.path == "compare-safe.html" and "Für Ωₖ≠0 darf D_C nicht als D_M behandelt werden" in row.text
    ]
    assert len(distance) == 1, distance
    assert distance[0].source_line == 48, distance[0]
    assert distance[0].tag == "div", distance[0]

    # Real navigation menu must not appear as a claim candidate.
    assert not any(
        row.path == "index-en.html" and "Research status Solver Hub Observatory Comparison HyperLab Guide" in row.text
        for row in rows
    )

    # Known public firewalls from the real corpus must not survive as HIGH or
    # MEDIUM overclaim candidates.
    known_firewalls = (
        ("baryogenesis-operator.html", "Sie beweist weder"),
        ("baryogenesis-v09.html", "Es beweist nicht"),
        ("baryogenesis-v10.html", "beweist keine Ghostfreiheit"),
        ("hyperzeit-material.html", "nicht für Hyperzeit beweist"),
        ("compare-safe.html", "nicht aus dem Parent-Sektor konstruiert"),
    )
    for path, fragment in known_firewalls:
        matched = [row for row in rows if row.path == path and fragment in row.text]
        assert matched, (path, fragment)
        assert all(row.limiter_present for row in matched), matched
        assert all(row.preliminary_risk_class == "CONTEXT_OR_FIREWALL" for row in matched), matched

    assert all(row.adjudication_status == "AUTOMATED_CANDIDATE_NOT_ADJUDICATED" for row in rows)

    # Family-routing regression. Specific scientific hints may route to one or
    # more real families, but routing remains non-adjudicating and preserves
    # manual review for a priority candidate.
    allowed = {
        "UL-CLM-PARENT-FORWARD-MAP-001",
        "UL-CLM-DATA-LIKELIHOOD-001",
        "UL-CLM-EDUCATIONAL-VISUAL-001",
    }
    routed = R.route({
        "claim_id": "UL-CLAIM-CANDIDATE-SYNTHETIC1",
        "path": "synthetic.html",
        "source_sha256": "2" * 64,
        "text": "A six-dimensional parent action must map to observables and likelihood inputs.",
        "lexical_categories": ["THEORY_6D_PARENT", "OBSERVATIONAL_DATA"],
        "preliminary_risk_class": "HIGH",
        "explicit_status": "UNCLASSIFIED",
        "adjudication_status": "AUTOMATED_CANDIDATE_NOT_ADJUDICATED",
        "page_scope": "SYNTHETIC_TEST",
    }, allowed)
    assert set(routed["family_ids"]) == {
        "UL-CLM-PARENT-FORWARD-MAP-001",
        "UL-CLM-DATA-LIKELIHOOD-001",
    }
    assert routed["routing_status"] == "AUTOMATED_FAMILY_ROUTING_NOT_ADJUDICATED"
    assert routed["manual_review_required"] is True
    assert routed["candidate_adjudication_status"] == "AUTOMATED_CANDIDATE_NOT_ADJUDICATED"

    # Fallback is a technical review-queue sink only. It must always require
    # manual review and must never be mistaken for scientific adjudication.
    fallback = R.route({
        "claim_id": "UL-CLAIM-CANDIDATE-SYNTHETIC2",
        "path": "synthetic.html",
        "source_sha256": "3" * 64,
        "text": "Unresolved scientific wording requiring human family review.",
        "lexical_categories": [],
        "preliminary_risk_class": "LOW",
        "explicit_status": "UNCLASSIFIED",
        "adjudication_status": "AUTOMATED_CANDIDATE_NOT_ADJUDICATED",
        "page_scope": "SYNTHETIC_TEST",
    }, allowed)
    assert fallback["family_ids"] == ["UL-CLM-EDUCATIONAL-VISUAL-001"]
    assert fallback["routing_status"] == "AUTOMATED_FALLBACK_ROUTING_MANUAL_REVIEW_REQUIRED"
    assert fallback["manual_review_required"] is True
    assert fallback["candidate_adjudication_status"] == "AUTOMATED_CANDIDATE_NOT_ADJUDICATED"

    print("UniverseLab Band V-A lexical/provenance/routing regressions: PASS")


if __name__ == "__main__":
    main()
