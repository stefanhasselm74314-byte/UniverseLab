#!/usr/bin/env python3
"""UniverseLab P0 verifier v0.1.

Run from any location:
    python verify_universelab_p0_v0_1.py /path/to/UniverseLab

The script is read-only. It reports registry consistency, canonical
file existence, severity counts, hard-coded gate strings and query
version drift.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


EXPECTED_SEVERITIES = {
    "CRITICAL": 7,
    "HIGH": 12,
    "MEDIUM": 7,
}


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Cannot parse {path}: {exc}") from exc


def citation_version(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^version:\s*[\"']?([^\"'\n]+)", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    root = args.repo.resolve()
    required = [
        root / "project-manifest.json",
        root / "convention-registry.json",
        root / "universelab-audit-2026-07-31.json",
        root / "CITATION.cff",
        root / "RELEASE-2.1-AUDIT.md",
    ]

    missing_required = [str(p.relative_to(root)) for p in required if not p.exists()]
    if missing_required:
        result = {"status": "FAIL", "missing_required": missing_required}
        print(json.dumps(result, indent=2))
        return 2

    manifest = load_json(root / "project-manifest.json")
    conventions = load_json(root / "convention-registry.json")
    audit = load_json(root / "universelab-audit-2026-07-31.json")

    canonical_missing = []
    for page in manifest.get("canonical_pages", []):
        path = root / page["path"]
        if not path.exists():
            canonical_missing.append(page["path"])

    counts = Counter(issue["severity"] for issue in audit.get("issues", []))
    count_checks = {
        key: counts.get(key, 0) == value
        for key, value in EXPECTED_SEVERITIES.items()
    }
    total_ok = len(audit.get("issues", [])) == 26

    cff_version = citation_version(root / "CITATION.cff")
    version_consistent = cff_version == manifest.get("release")

    html_files = list(root.glob("*.html"))
    hardcoded_gate_hits = {}
    version_tokens = Counter()
    manifest_consumers = []

    gate_pattern = re.compile(
        r"K1-D|K1-E|NOT_RELEASED|NOT_ADMISSIBLE|nicht freigegeben|nicht zulässig",
        re.IGNORECASE,
    )
    version_pattern = re.compile(r"\?v=([A-Za-z0-9._-]+)")

    for path in html_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        if "project-manifest.json" in text:
            manifest_consumers.append(path.name)
        hits = gate_pattern.findall(text)
        if hits:
            hardcoded_gate_hits[path.name] = len(hits)
        for token in version_pattern.findall(text):
            version_tokens[token] += 1

    result = {
        "status": "PARTIAL_PASS",
        "schemas": {
            "manifest": manifest.get("schema"),
            "conventions": conventions.get("schema"),
            "audit": audit.get("schema"),
        },
        "release": manifest.get("release"),
        "citation_version": cff_version,
        "version_consistent": version_consistent,
        "canonical_missing": canonical_missing,
        "issue_counts": dict(counts),
        "issue_count_checks": count_checks,
        "issue_total": len(audit.get("issues", [])),
        "issue_total_ok": total_ok,
        "manifest_consumers": sorted(manifest_consumers),
        "html_file_count": len(html_files),
        "hardcoded_gate_hits": hardcoded_gate_hits,
        "query_version_tokens": dict(version_tokens),
        "gates": {
            "registry_files": "PASS",
            "audit_counts": "PASS" if all(count_checks.values()) and total_ok else "FAIL",
            "canonical_files": "PASS" if not canonical_missing else "FAIL",
            "runtime_consumption": "PASS" if manifest_consumers else "FAIL",
            "single_version_policy": "PASS" if len(version_tokens) <= 1 else "FAIL",
            "release_lock_hashes": "OPEN",
        },
    }

    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.json_out:
        args.json_out.write_text(output + "\n", encoding="utf-8")

    critical_fail = (
        canonical_missing
        or not version_consistent
        or not all(count_checks.values())
        or not total_ok
    )
    return 1 if critical_fail else 0


if __name__ == "__main__":
    sys.exit(main())
