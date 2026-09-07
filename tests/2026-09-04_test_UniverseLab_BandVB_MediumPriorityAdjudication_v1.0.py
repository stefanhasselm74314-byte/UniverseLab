#!/usr/bin/env python3
"""Band V-B priority MEDIUM historical + current-corpus regression gate."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "registry/2026-09-04_UniverseLab_PublicScientificMediumPriorityAdjudication_v1.0.json"
CURRENT_CANDIDATES = ROOT / "registry/2026-09-03_UniverseLab_PublicScientificClaimLexicalCandidates_v0.1.json"
DELTA = ROOT / "registry/2026-09-04_UniverseLab_BandVC_StatusPageMediumDeltaAdjudication_v1.0.json"
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
    ledger = load(LEDGER)
    assert ledger["schema"] == "universelab.public-scientific-medium-priority-adjudication.v1"
    assert ledger["basis_main_commit"] == "edeab749981781a08b0d449984840ab024b0a8f8"
    assert ledger["scope"]["candidate_count"] == 9
    assert ledger["scope"]["minimum_preliminary_risk_score"] == 6
    assert ledger["physical_gate_effect"] == "NONE"
    assert ledger["physical_evidence_effect"] == "NONE"

    records = {row["claim_id"]: row for row in ledger["records"]}
    assert set(records) == EXPECTED_IDS
    assert len(records) == 9
    for record in records.values():
        assert record["positive_physical_hzt_claim"] is False
        assert record["parent_derivation_established"] is False
        assert record["empirical_evidence_claim"] is False
        assert record["physical_evidence_effect"] == "NONE"

    result = ledger["global_result"]
    assert result["priority_medium_candidates"] == 9
    assert result["contextually_adjudicated"] == 9
    assert result["positive_physical_hzt_overclaims"] == 0
    assert result["empirical_confirmation_claims"] == 0
    assert result["parent_derivation_promotions"] == 0
    assert result["historical_or_rejected_claims"] == 2
    assert result["open_requirements_or_obligations"] == 2
    assert result["method_or_documentation_scope_descriptions"] == 5
    assert result["physical_claim_promotions"] == 0

    # Historical context sentinels remain intact.
    contains("legacy.html", "Claim Firewall", "not admissible", "historical", "Keine aktuelle Parentableitung")
    contains("hyperzeit-methods.html", "beweist jedoch nicht, dass die 4D-Lorentzstruktur aus HPVS hervorgeht", "Für Hyperzeit müsste ein eigener RG-Fluss")
    contains("guide-en.html", "Observational comparison becomes admissible only when every required map is released", "A fitted parameter is not a derivation from the six-dimensional parent sector")
    contains("hyperzeit-methods-en.html", "become theory tests only after a released forward map exists", "A good fit without that derivation is not evidence for Hyperzeit")
    contains("hyperzeit-material-v2-en.html", "Literature compatibility is not treated as derivation or evidence for Hyperzeit", "Applicable only after forward-map release")
    contains("hyperzeit-material-v2.html", "nicht den Bestätigungsgrad der Theorie", "Erst nach Freigabe des Forward-Modells")
    contains("navigator.html", "Methoden und Qualitätssicherung")

    # The successor status pages are tested semantically rather than by obsolete text.
    contains("research-status-en.html", "not physical evidence for HZT", "Open proof obligations", "a bound HZT data/covariance/selection/nuisance/likelihood stack;")
    contains("research-status.html", "keine physische Evidenz für HZT", "Offene Beweispflichten", "gebundener HZT-Daten-/Kovarianz-/Selection-/Nuisance-/Likelihood-Stack;")

    current = load(CURRENT_CANDIDATES)
    current_medium = [row for row in current["candidates"] if row["preliminary_risk_class"] == "MEDIUM"]
    current_high = [row for row in current["candidates"] if row["preliminary_risk_class"] == "HIGH"]
    assert len(current["candidates"]) == 993
    assert current_high == []
    assert len(current_medium) == 46

    delta = load(DELTA)
    assert delta["global_result"]["delta_candidates"] == 7
    assert delta["global_result"]["contextually_adjudicated"] == 7
    assert delta["global_result"]["contextually_unadjudicated"] == 0
    assert delta["global_result"]["positive_physical_hzt_overclaims"] == 0
    assert delta["global_result"]["physical_claim_promotions"] == 0

    scanner = module("ul_priority_medium_current_scanner", SCANNER)
    rows, summary = scanner.extract(ROOT)
    high = [row for row in rows if row.preliminary_risk_class == "HIGH"]
    medium = [row for row in rows if row.preliminary_risk_class == "MEDIUM"]
    assert high == []
    assert len(rows) == 993
    assert len(medium) == 46
    assert summary["physical_gate_effect"] == summary["physical_evidence_effect"] == "NONE"

    print(
        "UniverseLab priority MEDIUM gate: PASS historical_priority=9 current_claims=993 "
        "current_medium=46 current_high=0 successor_delta=7/7 physical_promotions=0"
    )


if __name__ == "__main__":
    main()
