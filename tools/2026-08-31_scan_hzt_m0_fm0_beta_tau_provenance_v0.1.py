#!/usr/bin/env python3
"""Repository-wide diagnostic scan for FM-0 beta_tau provenance.

This is a read-only discovery tool. It does not import a physics backend, run a
solver, alter a gate, or treat a search miss as proof of physical nonexistence.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
TEXT_SUFFIXES = {
    ".md", ".json", ".jsonl", ".csv", ".tsv", ".html", ".htm", ".py",
    ".yml", ".yaml", ".js", ".mjs", ".cjs", ".txt", ".toml", ".ini",
    ".cfg", ".conf", ".xml", ".tex", ".cff", ".css", ".sh", ".ps1",
}
CURRENT_TOKEN = re.compile(r"(?<![A-Za-z0-9_])(beta_tau|β_τ|βτ)(?![A-Za-z0-9_])")
LEGACY_PATTERNS = {
    "legacy_beta_symbol": re.compile(r"(?<![A-Za-z0-9_])(beta|β)(?![A-Za-z0-9_])"),
    "tau_derivative": re.compile(r"(?:∂_τ|partial_tau|d/dtau|d_tau)"),
    "lambda_theta": re.compile(r"(?:lambda_Theta|λ_Θ)"),
    "hubble_anchor": re.compile(r"(?:beta\s*=\s*H0|β\s*=\s*H₀)"),
}
EXPECTED_DECLARATION_FRAGMENTS = (
    "HZT_M0_ForwardMap_FM0_",
    "UniverseLab_Hyperzeit_10M_ResearchProgram",
)
MAX_HITS_PER_BUCKET = 300


def is_text_candidate(path: Path) -> bool:
    if path == SELF or ".git" in path.parts:
        return False
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {"README", "LICENSE"}


def add_hit(bucket: list[dict], path: Path, line_no: int, line: str, pattern: str) -> None:
    if len(bucket) >= MAX_HITS_PER_BUCKET:
        return
    bucket.append(
        {
            "path": path.relative_to(ROOT).as_posix(),
            "line": line_no,
            "pattern": pattern,
            "text": line.strip()[:500],
        }
    )


def main() -> int:
    current_hits: list[dict] = []
    non_fm0_current_hits: list[dict] = []
    legacy_hits: list[dict] = []
    unreadable: list[str] = []
    scanned_files = 0

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or not is_text_candidate(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            unreadable.append(path.relative_to(ROOT).as_posix())
            continue
        scanned_files += 1
        rel = path.relative_to(ROOT).as_posix()
        expected_declaration = any(fragment in rel for fragment in EXPECTED_DECLARATION_FRAGMENTS)
        for line_no, line in enumerate(text.splitlines(), start=1):
            if CURRENT_TOKEN.search(line):
                add_hit(current_hits, path, line_no, line, "current_token")
                if not expected_declaration and "scan_hzt_m0_fm0_beta_tau" not in rel and "BetaTauProvenanceScan" not in rel:
                    add_hit(non_fm0_current_hits, path, line_no, line, "current_token_outside_expected_fm0_declarations")
            for name, pattern in LEGACY_PATTERNS.items():
                if pattern.search(line):
                    add_hit(legacy_hits, path, line_no, line, name)

    legacy_csv = ROOT / "legacy-formeln-H1-H64.csv"
    baseline_errors: list[str] = []
    if not legacy_csv.is_file():
        baseline_errors.append("missing legacy-formeln-H1-H64.csv")
    else:
        legacy_text = legacy_csv.read_text(encoding="utf-8")
        required_fragments = [
            "H32;7.2 Effektive Driftgleichung;∂_τ ϑ = βϑ - λ_Θ ∇²ϑ;open",
            "H33;7.2 Effektive Driftgleichung;∇²ϑ - (β/λ_Θ)ϑ = 0;open",
            "H34;8.1 Kosmische Verankerung;a₀ = λ_Θ c β;historical",
            "H35;8.1 Kosmische Verankerung;β = H₀;historical",
            "H36;8.1 Kosmische Verankerung;a₀ = λ_Θ c H₀;historical",
        ]
        for fragment in required_fragments:
            if fragment not in legacy_text:
                baseline_errors.append(f"missing required legacy fragment: {fragment}")

    result = {
        "schema": "hzt-m0.forward-map.fm0.beta-tau-provenance-scan.v0.1",
        "classification": "DIAGNOSTIC_SOURCE_DISCOVERY_NO_NEW_PHYSICS",
        "scanned_text_files": scanned_files,
        "current_token_hit_count": len(current_hits),
        "current_token_hits": current_hits,
        "current_token_outside_expected_fm0_declaration_count": len(non_fm0_current_hits),
        "current_token_outside_expected_fm0_declaration_hits": non_fm0_current_hits,
        "legacy_context_hit_count": len(legacy_hits),
        "legacy_context_hits": legacy_hits,
        "unreadable_text_candidates": unreadable,
        "baseline_errors": baseline_errors,
        "interpretation_rule": "A zero candidate count is not proof of physical nonexistence; it only means no additional tracked UTF-8 text binding was found by these lexical patterns.",
        "physical_gate_effect": "NONE",
        "physical_evidence_effect": "NONE",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if baseline_errors else 0


if __name__ == "__main__":
    sys.exit(main())
