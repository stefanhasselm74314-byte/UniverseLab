#!/usr/bin/env python3
"""Validate names of newly added UniverseLab files.

The validator is read-only and intentionally non-retroactive. It receives the
paths added or renamed in the current changeset and accepts either:

1. a dated, versioned canonical filename defined by UL-FNS-v1.0; or
2. an exact stable alias registered in the machine-readable policy.

Existing repository files are not scanned unless explicitly supplied.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

DEFAULT_POLICY = "registry/2026-08-01_UniverseLab_FileNamingPolicy_v1.0.json"
EXPECTED_SCHEMA = "universelab.file-naming-policy.v1"


@dataclass(frozen=True)
class Issue:
    category: str
    path: str
    message: str

    def render(self) -> str:
        return f"[{self.category}] {self.path}: {self.message}"


@dataclass(frozen=True)
class NamingPolicy:
    policy_id: str
    filename_pattern: re.Pattern[str]
    stable_aliases: frozenset[str]
    raw: dict[str, Any]


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _normalize_repo_path(raw: str) -> str:
    value = raw.strip().replace("\\", "/")
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts:
        raise ValueError("path must be a non-empty repository-relative path")
    normalized = path.as_posix()
    if normalized in {".", ""}:
        raise ValueError("path must identify a file")
    return normalized


def load_policy(path: Path) -> tuple[NamingPolicy | None, list[Issue]]:
    issues: list[Issue] = []
    display_path = path.as_posix()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, [Issue("POLICY", display_path, "policy file does not exist")]
    except json.JSONDecodeError as exc:
        return None, [Issue("POLICY", display_path, f"invalid JSON: {exc.msg}")]

    if not isinstance(data, dict):
        return None, [Issue("POLICY", display_path, "policy root must be an object")]
    if data.get("schema") != EXPECTED_SCHEMA:
        issues.append(Issue("POLICY", display_path, "unexpected schema identifier"))
    if data.get("status") != "ACTIVE":
        issues.append(Issue("POLICY", display_path, "policy status must be ACTIVE"))

    policy_id = data.get("policy_id")
    if not _nonempty_string(policy_id):
        issues.append(Issue("POLICY", display_path, "policy_id must be a non-empty string"))
        policy_id = "UNKNOWN"

    regex_text = data.get("filename_regex")
    pattern: re.Pattern[str] | None = None
    if not _nonempty_string(regex_text):
        issues.append(Issue("POLICY", display_path, "filename_regex is required"))
    else:
        try:
            pattern = re.compile(regex_text)
        except re.error as exc:
            issues.append(Issue("POLICY", display_path, f"invalid filename_regex: {exc}"))

    aliases_raw = data.get("stable_aliases")
    aliases: set[str] = set()
    if not isinstance(aliases_raw, list):
        issues.append(Issue("POLICY", display_path, "stable_aliases must be a list"))
    else:
        for index, entry in enumerate(aliases_raw):
            label = f"stable_aliases[{index}]"
            if not isinstance(entry, dict):
                issues.append(Issue("POLICY", display_path, f"{label} must be an object"))
                continue
            alias_path = entry.get("path")
            alias_type = entry.get("alias_type")
            reason = entry.get("reason")
            if not _nonempty_string(alias_path):
                issues.append(Issue("POLICY", display_path, f"{label}.path is required"))
                continue
            if not _nonempty_string(alias_type):
                issues.append(Issue("POLICY", display_path, f"{label}.alias_type is required"))
            if not _nonempty_string(reason):
                issues.append(Issue("POLICY", display_path, f"{label}.reason is required"))
            try:
                normalized = _normalize_repo_path(alias_path)
            except ValueError as exc:
                issues.append(Issue("POLICY", display_path, f"{label}.path: {exc}"))
                continue
            if normalized in aliases:
                issues.append(Issue("POLICY", display_path, f"duplicate alias path: {normalized}"))
            aliases.add(normalized)

    if issues or pattern is None:
        return None, issues
    return NamingPolicy(str(policy_id), pattern, frozenset(aliases), data), []


def _validate_date(value: str) -> bool:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return parsed.strftime("%Y-%m-%d") == value


def _validate_time(value: str | None) -> bool:
    if value is None:
        return True
    if not re.fullmatch(r"\d{4}", value):
        return False
    hour = int(value[:2])
    minute = int(value[2:])
    return 0 <= hour <= 23 and 0 <= minute <= 59


def validate_path(path: str, policy: NamingPolicy) -> list[Issue]:
    try:
        normalized = _normalize_repo_path(path)
    except ValueError as exc:
        return [Issue("PATH", path, str(exc))]

    if normalized in policy.stable_aliases:
        return []

    basename = PurePosixPath(normalized).name
    if not basename.isascii():
        return [Issue("NAMING", normalized, "filename must use ASCII characters only")]
    if any(character.isspace() for character in basename):
        return [Issue("NAMING", normalized, "filename must not contain whitespace")]

    match = policy.filename_pattern.fullmatch(basename)
    if match is None:
        return [
            Issue(
                "NAMING",
                normalized,
                "new file must use YYYY-MM-DD[_HHMM]_Area_Title_vX.Y[_STATUS].ext or be a registered stable alias",
            )
        ]

    groups = match.groupdict()
    date_value = groups.get("date")
    time_value = groups.get("time")
    title = groups.get("title")
    major = groups.get("major")
    minor = groups.get("minor")
    extension = groups.get("extension")

    issues: list[Issue] = []
    if not date_value or not _validate_date(date_value):
        issues.append(Issue("NAMING", normalized, f"invalid calendar date: {date_value!r}"))
    if not _validate_time(time_value):
        issues.append(Issue("NAMING", normalized, f"invalid HHMM time: {time_value!r}"))
    if not title or title.strip("._-") == "":
        issues.append(Issue("NAMING", normalized, "descriptive title segment is empty"))
    if major is None or minor is None:
        issues.append(Issue("NAMING", normalized, "numeric version vX.Y is required"))
    if not extension or extension == ".":
        issues.append(Issue("NAMING", normalized, "file extension is required"))
    return issues


def validate_paths(paths: Iterable[str], policy: NamingPolicy) -> list[Issue]:
    issues: list[Issue] = []
    seen: set[str] = set()
    for raw in paths:
        if not raw.strip():
            continue
        try:
            normalized = _normalize_repo_path(raw)
        except ValueError:
            normalized = raw.strip()
        if normalized in seen:
            continue
        seen.add(normalized)
        issues.extend(validate_path(raw, policy))
    return issues


def _read_paths(args: argparse.Namespace) -> list[str]:
    paths = list(args.path or [])
    if args.paths_file:
        paths.extend(Path(args.paths_file).read_text(encoding="utf-8").splitlines())
    if args.stdin:
        paths.extend(sys.stdin.read().splitlines())
    return paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", default=DEFAULT_POLICY, help="machine-readable naming policy")
    parser.add_argument("--path", action="append", help="one added or renamed repository path")
    parser.add_argument("--paths-file", help="UTF-8 file containing one repository path per line")
    parser.add_argument("--stdin", action="store_true", help="read newline-separated paths from stdin")
    parser.add_argument("--json-output", action="store_true", help="emit machine-readable validation output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    policy, policy_issues = load_policy(Path(args.policy))
    paths = _read_paths(args)

    issues = list(policy_issues)
    if policy is not None:
        issues.extend(validate_paths(paths, policy))

    if args.json_output:
        payload = {
            "policy": policy.policy_id if policy else None,
            "checked_paths": len({path for path in paths if path.strip()}),
            "status": "FAIL" if issues else "PASS",
            "issues": [
                {"category": issue.category, "path": issue.path, "message": issue.message}
                for issue in issues
            ],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        if issues:
            print("UniverseLab file naming contract: FAIL")
            for issue in issues:
                print(issue.render())
        else:
            print(f"UniverseLab file naming contract: PASS ({len({p for p in paths if p.strip()})} paths)")

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
