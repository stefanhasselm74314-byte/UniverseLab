#!/usr/bin/env python3
"""Deterministically route Band V-A lexical claim candidates to review families.

Routing is coverage/provenance infrastructure only. It does not adjudicate
scientific truth, change epistemic status, create evidence, authorize execution,
or infer a parent-theory derivation.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fnmatch import fnmatch
import json
from pathlib import Path
import sys
from typing import Any, Iterable

FALLBACK = "UL-CLM-EDUCATIONAL-VISUAL-001"

KEYWORD_RULES: dict[str, tuple[str, ...]] = {
    "UL-CLM-FLRW-BACKGROUND-001": (
        "flrw", "friedmann", "lcdm", "λcdm", "h(z)", "expansion", "expansion history",
        "expansionsgeschichte", "omega_k", "omega_m", "omega_de", "Ωₖ", "Ωₘ", "ΩΛ", "e²",
    ),
    "UL-CLM-DISTANCE-GEOMETRY-001": (
        "d_c", "d_m", "d_l", "d_a", "distance", "distanz", "etherington", "luminosity distance",
        "angular diameter", "komovierend", "comoving",
    ),
    "UL-CLM-LINEAR-GROWTH-001": (
        "growth", "wachstum", "fσ", "sigma8", "σ8", "linear-gr", "linear gr", "d(a)",
    ),
    "UL-CLM-BRIDGE-BACKGROUND-001": (
        "brücke", "bridge", "βτ", "beta_tau", "𝓘b", "i_b", "rchi", "rχ", "a_c",
    ),
    "UL-CLM-BRIDGE-IDENTIFIABILITY-001": (
        "βτ𝓘b", "beta_tau i_b", "produkt", "product degeneracy", "identifizier", "identifiability",
        "jacobian", "jacobi", "rang", "rank",
    ),
    "UL-CLM-BRIDGE-UNRELEASED-OBSERVABLES-001": (
        "unreleased_growth_map", "unreleased_lensing_map", "keine freigegebene perturb", "no released perturb",
        "poisson", "lensing map", "Σ(a,k)", "η(a,k)", "mu(k", "μ(k",
    ),
    "UL-CLM-PARENT-FORWARD-MAP-001": (
        "parent→", "parent->", "parent to reduced", "parent-to-reduced", "6d→4d", "6d->4d",
        "forward map", "forward-map", "parent sector", "parent-sektor", "parent action", "parent-aktion",
        "six-dimensional parent", "sechsdimensional", "6d-herleitung", "6d-ableitung",
    ),
    "UL-CLM-PHYSICAL-SOLUTION-STABILITY-001": (
        "ghost", "stabilität", "stability", "kinetic", "hamilton", "physical background",
        "physischer hintergrund", "response rank", "response-rank", "bvp", "k1-d", "k1-e",
        "not_established", "not executed", "not_executed",
    ),
    "UL-CLM-DATA-LIKELIHOOD-001": (
        "likelihood", "covariance", "kovarianz", "posterior", "nuisance", "selection function",
        "datenvektor", "data vector", "desi", "kids", "pantheon", "planck", "euclid", "bao", "rsd",
    ),
    "UL-CLM-EMERGENCE-SEPARATION-001": (
        "emergence", "zellautomat", "cellular automaton", "conway", "displayn", "cell hash",
    ),
    "UL-CLM-PREDICTIONS-FALSIFIERS-001": (
        "prediction", "vorhersage", "falsifiz", "testable", "testbar", "measurable", "messbar",
        "mond", "rar", "gravitational wave", "gravitationswelle", "gw", "lensing", "growth",
    ),
    "UL-CLM-PUBLIC-STATUS-GOVERNANCE-001": (
        "governance", "authorization", "authorisierung", "singleusegrant", "authorizationdecision",
        "trust root", "status", "not released", "not admissible", "blocked", "blockiert",
        "physical_evidence_effect", "physical gate effect",
    ),
    "UL-CLM-FM0-PROGRAM-001": (
        "fm-0", "fm0", "fm-g0", "workstream", "work package", "work-package", "gap register",
        "roadmap", "arbeitsprogramm",
    ),
    "UL-CLM-EDUCATIONAL-VISUAL-001": (
        "guide", "handbuch", "visualisierung", "visualization", "journey", "portal", "navigator",
        "about", "tafelwerk", "educational", "didaktisch",
    ),
    "UL-CLM-HISTORICAL-ARCHIVE-001": (
        "historisch", "historical", "legacy", "archive", "archiv", "provenance record",
    ),
}

CATEGORY_RULES: dict[str, tuple[str, ...]] = {
    "THEORY_6D_PARENT": ("UL-CLM-PARENT-FORWARD-MAP-001",),
    "OBSERVATIONAL_DATA": ("UL-CLM-DATA-LIKELIHOOD-001",),
    "PREDICTION_SIGNATURE": ("UL-CLM-PREDICTIONS-FALSIFIERS-001",),
    "STATUS_FIREWALL": ("UL-CLM-PUBLIC-STATUS-GOVERNANCE-001",),
}

PAGE_RULES: tuple[tuple[str, str], ...] = (
    ("*legacy*.html", "UL-CLM-HISTORICAL-ARCHIVE-001"),
    ("*audit*.html", "UL-CLM-HISTORICAL-ARCHIVE-001"),
    ("navigator-app.html", "UL-CLM-HISTORICAL-ARCHIVE-001"),
    ("compare.html", "UL-CLM-HISTORICAL-ARCHIVE-001"),
    ("compare-direct.html", "UL-CLM-HISTORICAL-ARCHIVE-001"),
    ("emergence*.html", "UL-CLM-EMERGENCE-SEPARATION-001"),
    ("research-status*.html", "UL-CLM-PUBLIC-STATUS-GOVERNANCE-001"),
    ("solver-hub*.html", "UL-CLM-PUBLIC-STATUS-GOVERNANCE-001"),
    ("source*.html", "UL-CLM-PUBLIC-STATUS-GOVERNANCE-001"),
    ("index*.html", "UL-CLM-EDUCATIONAL-VISUAL-001"),
    ("about*.html", "UL-CLM-EDUCATIONAL-VISUAL-001"),
    ("guide*.html", "UL-CLM-EDUCATIONAL-VISUAL-001"),
    ("journey*.html", "UL-CLM-EDUCATIONAL-VISUAL-001"),
    ("universe3d*.html", "UL-CLM-EDUCATIONAL-VISUAL-001"),
    ("portal.html", "UL-CLM-EDUCATIONAL-VISUAL-001"),
)


class RoutingError(RuntimeError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RoutingError(f"TOP_LEVEL_NOT_OBJECT:{path}")
    return value


def route(row: dict[str, Any], allowed: set[str]) -> dict[str, Any]:
    claim_id = row.get("claim_id")
    path = row.get("path")
    source_sha = row.get("source_sha256")
    text = str(row.get("text", ""))
    lower = text.casefold()
    cats = set(row.get("lexical_categories") or [])
    if not isinstance(claim_id, str) or not claim_id:
        raise RoutingError("MISSING_CLAIM_ID")
    if not isinstance(path, str) or not path:
        raise RoutingError(f"MISSING_PATH:{claim_id}")
    if not isinstance(source_sha, str) or len(source_sha) != 64:
        raise RoutingError(f"INVALID_SOURCE_SHA256:{claim_id}")

    families: set[str] = set()
    basis: list[str] = []

    for pattern, family_id in PAGE_RULES:
        if fnmatch(path, pattern):
            families.add(family_id)
            basis.append(f"PAGE_PATTERN:{pattern}->{family_id}")

    for category in sorted(cats):
        for family_id in CATEGORY_RULES.get(category, ()):
            families.add(family_id)
            basis.append(f"LEXICAL_CATEGORY:{category}->{family_id}")

    for family_id, terms in KEYWORD_RULES.items():
        matched = next((term for term in terms if term.casefold() in lower), None)
        if matched is not None:
            families.add(family_id)
            basis.append(f"BOUNDED_TEXT_HINT:{matched}->{family_id}")

    # Scope itself can establish only routing context, never scientific truth.
    if row.get("page_scope") == "TRACKED_ARCHIVE_OR_UTILITY_PAGE":
        families.add("UL-CLM-HISTORICAL-ARCHIVE-001")
        basis.append("PAGE_SCOPE:TRACKED_ARCHIVE_OR_UTILITY_PAGE")

    fallback = False
    if not families:
        families.add(FALLBACK)
        basis.append("FALLBACK:UNRESOLVED_BY_AUTOMATIC_HINTS")
        fallback = True

    unknown = sorted(families - allowed)
    if unknown:
        raise RoutingError(f"UNKNOWN_FAMILY_ID:{claim_id}:{unknown}")

    risk = row.get("preliminary_risk_class")
    manual = risk in {"HIGH", "MEDIUM"} or fallback
    return {
        "claim_id": claim_id,
        "path": path,
        "source_sha256": source_sha,
        "family_ids": sorted(families),
        "routing_basis": basis,
        "routing_status": (
            "AUTOMATED_FALLBACK_ROUTING_MANUAL_REVIEW_REQUIRED"
            if fallback else "AUTOMATED_FAMILY_ROUTING_NOT_ADJUDICATED"
        ),
        "manual_review_required": manual,
        "candidate_risk_class": risk,
        "candidate_explicit_status": row.get("explicit_status"),
        "candidate_adjudication_status": row.get("adjudication_status"),
    }


def build(candidate_register: dict[str, Any], family_catalog: dict[str, Any]) -> dict[str, Any]:
    candidates = candidate_register.get("candidates")
    families = family_catalog.get("claim_families")
    if not isinstance(candidates, list) or not isinstance(families, list):
        raise RoutingError("MISSING_CANDIDATES_OR_FAMILIES")
    family_ids = [row.get("claim_family_id") for row in families if isinstance(row, dict)]
    if any(not isinstance(value, str) or not value for value in family_ids):
        raise RoutingError("INVALID_FAMILY_ID")
    if len(family_ids) != len(set(family_ids)):
        raise RoutingError("DUPLICATE_FAMILY_ID")
    allowed = set(family_ids)
    if FALLBACK not in allowed:
        raise RoutingError("FALLBACK_FAMILY_MISSING")

    ids = [row.get("claim_id") for row in candidates if isinstance(row, dict)]
    if len(ids) != len(candidates) or any(not isinstance(value, str) or not value for value in ids):
        raise RoutingError("INVALID_CANDIDATE_ID")
    if len(ids) != len(set(ids)):
        raise RoutingError("DUPLICATE_CANDIDATE_ID")

    assignments = [route(row, allowed) for row in candidates]
    assigned_ids = {row["claim_id"] for row in assignments}
    missing = sorted(set(ids) - assigned_ids)
    extra = sorted(assigned_ids - set(ids))
    if missing or extra:
        raise RoutingError(f"COVERAGE_MISMATCH:missing={missing[:8]}:extra={extra[:8]}")
    if any(not row["family_ids"] for row in assignments):
        raise RoutingError("UNMAPPED_CANDIDATE")

    high_medium = {row["claim_id"] for row in candidates if row.get("preliminary_risk_class") in {"HIGH", "MEDIUM"}}
    manual_ids = {row["claim_id"] for row in assignments if row["manual_review_required"]}
    missed_priority = sorted(high_medium - manual_ids)
    if missed_priority:
        raise RoutingError(f"PRIORITY_CANDIDATE_NOT_MANUAL:{missed_priority[:8]}")

    fallback_count = sum(row["routing_status"].startswith("AUTOMATED_FALLBACK") for row in assignments)
    family_counts = Counter(family for row in assignments for family in row["family_ids"])
    return {
        "schema": "universelab.public-scientific-claim-family-assignments.v0.1",
        "status": "PASS_COMPLETE_AUTOMATED_ROUTING_NOT_SCIENTIFIC_ADJUDICATION",
        "candidate_basis_commit": candidate_register.get("basis_commit"),
        "candidate_count": len(candidates),
        "assignment_count": len(assignments),
        "unmapped_candidates": 0,
        "unknown_family_ids": 0,
        "fallback_assignment_count": fallback_count,
        "manual_review_required_count": len(manual_ids),
        "high_medium_candidate_count": len(high_medium),
        "family_counts": dict(sorted(family_counts.items())),
        "assignments": assignments,
        "semantics": {
            "routing_is_scientific_adjudication": False,
            "routing_changes_epistemic_status": False,
            "routing_creates_evidence": False,
            "fallback_is_scientific_classification": False,
        },
        "physical_gate_effect": "NONE",
        "physical_evidence_effect": "NONE",
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--families", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        result = build(load(Path(args.candidates)), load(Path(args.families)))
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({
            "status": result["status"],
            "candidate_count": result["candidate_count"],
            "assignment_count": result["assignment_count"],
            "unmapped_candidates": result["unmapped_candidates"],
            "fallback_assignment_count": result["fallback_assignment_count"],
            "manual_review_required_count": result["manual_review_required_count"],
            "physical_gate_effect": "NONE",
            "physical_evidence_effect": "NONE",
        }, sort_keys=True, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, RoutingError, TypeError, ValueError) as exc:
        print(json.dumps({
            "status": "FAIL_CLOSED",
            "error": f"{type(exc).__name__}:{exc}",
            "physical_gate_effect": "NONE",
            "physical_evidence_effect": "NONE",
        }, sort_keys=True, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
