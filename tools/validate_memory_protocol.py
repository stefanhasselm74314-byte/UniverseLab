#!/usr/bin/env python3
"""Validate the public-safe UniverseLab memory protocol.

The validator is read-only and fail-closed. It checks:
- required memory artifacts;
- sanitized checkpoint schema and repository-local sources;
- append-only decision log structure, uniqueness and supersession rules;
- basis-commit provenance when a Git checkout is available;
- obvious secrets, personal contact data, share links and raw-dialog markers.

It is intentionally conservative and does not auto-repair content.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

REQUIRED_FILES = (
    "governance/UNIVERSELAB_MEMORY_PROTOCOL_v1.0.md",
    "registry/session-checkpoint-latest.json",
    "registry/decision-log.jsonl",
    "prompts/UNIVERSELAB_CHAT_BOOTSTRAP_v1.0.md",
    "tools/validate_memory_protocol.py",
    "tests/test_memory_protocol.py",
)

CHECKPOINT_PATH = "registry/session-checkpoint-latest.json"
DECISION_LOG_PATH = "registry/decision-log.jsonl"

CHECKPOINT_REQUIRED_FIELDS = {
    "schema",
    "checkpoint_id",
    "timestamp",
    "privacy_classification",
    "basis_commit",
    "architecture",
    "current_goal",
    "current_workstream",
    "gate_state",
    "verified_results",
    "open_blockers",
    "active_assumptions",
    "forbidden_inferences",
    "entry_points",
    "next_exact_action",
}

DECISION_REQUIRED_FIELDS = {
    "decision_id",
    "date",
    "topic",
    "decision",
    "status",
    "reason",
    "sources",
    "evidence_effect",
    "supersedes",
}

FORBIDDEN_JSON_KEYS = {
    "address",
    "api_key",
    "email",
    "password",
    "personal_notes",
    "phone",
    "private_key",
    "raw_chat",
    "secret",
    "share_link",
    "token",
    "transcript",
}

PRIVACY_PATTERNS = (
    ("chat_share_link", re.compile(r"https?://chatgpt\.com/share/", re.I)),
    ("openai_style_key", re.compile(r"\bsk-[A-Za-z0-9]{16,}\b")),
    ("github_classic_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("github_fine_grained_token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("private_key_block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    (
        "email_address",
        re.compile(r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9.-])"),
    ),
    ("unix_private_path", re.compile(r"(?:^|[\s'\"])/(?:home|Users)/[^\s'\"]+", re.M)),
    ("windows_private_path", re.compile(r"\b[A-Za-z]:\\Users\\[^\s'\"]+", re.I)),
    (
        "raw_dialogue_marker",
        re.compile(r"^(?:User|Assistant|Benutzer|Nutzer|ChatGPT|Stefan)\s*:\s+", re.I | re.M),
    ),
)


@dataclass(frozen=True)
class Issue:
    category: str
    path: str
    message: str

    def render(self) -> str:
        return f"[{self.category}] {self.path}: {self.message}"


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _iter_sources(container: Any) -> Iterable[str]:
    if isinstance(container, dict):
        sources = container.get("sources")
        if isinstance(sources, list):
            for source in sources:
                if isinstance(source, str):
                    yield source


def scan_privacy(path: str, text: str) -> list[Issue]:
    issues: list[Issue] = []
    for name, pattern in PRIVACY_PATTERNS:
        if pattern.search(text):
            issues.append(Issue("PRIVACY", path, f"forbidden pattern detected: {name}"))
    return issues


def scan_forbidden_keys(path: str, value: Any, trail: str = "$") -> list[Issue]:
    issues: list[Issue] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = str(key).strip().lower()
            if normalized in FORBIDDEN_JSON_KEYS:
                issues.append(Issue("PRIVACY", path, f"forbidden JSON field at {trail}.{key}"))
            issues.extend(scan_forbidden_keys(path, nested, f"{trail}.{key}"))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            issues.extend(scan_forbidden_keys(path, nested, f"{trail}[{index}]"))
    return issues


def validate_relative_source(root: Path, owner_path: str, source: Any) -> list[Issue]:
    issues: list[Issue] = []
    if not _is_nonempty_string(source):
        return [Issue("SCHEMA", owner_path, "source must be a non-empty string")]
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", source):
        return [Issue("PRIVACY", owner_path, f"external source URL is not allowed: {source}")]
    candidate = PurePosixPath(source)
    if candidate.is_absolute() or ".." in candidate.parts:
        return [Issue("PROVENANCE", owner_path, f"source path escapes repository: {source}")]
    if not (root / candidate).is_file():
        issues.append(Issue("PROVENANCE", owner_path, f"source file does not exist: {source}"))
    return issues


def validate_basis_commit(root: Path, commit: Any, check_git: bool) -> list[Issue]:
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        return [Issue("PROVENANCE", CHECKPOINT_PATH, "basis_commit must be a 40-character lowercase SHA-1")]
    if not check_git:
        return []
    git_dir = root / ".git"
    if not git_dir.exists():
        return [Issue("PROVENANCE", CHECKPOINT_PATH, "Git checkout unavailable for basis_commit verification")]
    result = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"{commit}^{{commit}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return [Issue("PROVENANCE", CHECKPOINT_PATH, f"basis_commit is not present in Git history: {commit}")]
    return []


def validate_checkpoint(root: Path, data: Any, *, check_git: bool = True) -> list[Issue]:
    path = CHECKPOINT_PATH
    issues: list[Issue] = []
    if not isinstance(data, dict):
        return [Issue("SCHEMA", path, "checkpoint root must be an object")]

    missing = sorted(CHECKPOINT_REQUIRED_FIELDS - set(data))
    if missing:
        issues.append(Issue("SCHEMA", path, f"missing fields: {', '.join(missing)}"))

    if data.get("schema") != "universelab.session-checkpoint.v1":
        issues.append(Issue("SCHEMA", path, "unexpected schema identifier"))
    if not re.fullmatch(r"UL-CHK-\d{8}-\d{3}", str(data.get("checkpoint_id", ""))):
        issues.append(Issue("SCHEMA", path, "invalid checkpoint_id"))
    if data.get("privacy_classification") != "PUBLIC_SANITIZED":
        issues.append(Issue("PRIVACY", path, "privacy_classification must be PUBLIC_SANITIZED"))

    timestamp = data.get("timestamp")
    try:
        parsed = datetime.fromisoformat(timestamp) if isinstance(timestamp, str) else None
        if parsed is None or parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError
    except ValueError:
        issues.append(Issue("SCHEMA", path, "timestamp must be ISO-8601 with an explicit timezone"))

    issues.extend(validate_basis_commit(root, data.get("basis_commit"), check_git))

    architecture = data.get("architecture")
    if not isinstance(architecture, list) or not architecture or not all(_is_nonempty_string(x) for x in architecture):
        issues.append(Issue("SCHEMA", path, "architecture must be a non-empty string list"))

    for field in ("current_goal", "current_workstream", "next_exact_action"):
        if not _is_nonempty_string(data.get(field)):
            issues.append(Issue("SCHEMA", path, f"{field} must be a non-empty string"))

    gate_state = data.get("gate_state")
    if not isinstance(gate_state, dict):
        issues.append(Issue("SCHEMA", path, "gate_state must be an object"))
    else:
        required_gates = {"K1-D": "NOT_RELEASED", "K1-E": "NOT_ADMISSIBLE"}
        for gate, expected in required_gates.items():
            if gate_state.get(gate) != expected:
                issues.append(Issue("GOVERNANCE", path, f"{gate} must remain {expected}"))

    results = data.get("verified_results")
    result_ids: set[str] = set()
    if not isinstance(results, list):
        issues.append(Issue("SCHEMA", path, "verified_results must be a list"))
    else:
        for index, result in enumerate(results):
            label = f"verified_results[{index}]"
            if not isinstance(result, dict):
                issues.append(Issue("SCHEMA", path, f"{label} must be an object"))
                continue
            result_id = result.get("result_id")
            if not _is_nonempty_string(result_id):
                issues.append(Issue("SCHEMA", path, f"{label}.result_id is required"))
            elif result_id in result_ids:
                issues.append(Issue("SCHEMA", path, f"duplicate result_id: {result_id}"))
            else:
                result_ids.add(result_id)
            for field in ("statement", "status", "evidence_effect"):
                if not _is_nonempty_string(result.get(field)):
                    issues.append(Issue("SCHEMA", path, f"{label}.{field} is required"))
            sources = result.get("sources")
            if not isinstance(sources, list) or not sources:
                issues.append(Issue("PROVENANCE", path, f"{label}.sources must be non-empty"))
            else:
                for source in sources:
                    issues.extend(validate_relative_source(root, path, source))

    blockers = data.get("open_blockers")
    blocker_ids: set[str] = set()
    if not isinstance(blockers, list):
        issues.append(Issue("SCHEMA", path, "open_blockers must be a list"))
    else:
        for index, blocker in enumerate(blockers):
            label = f"open_blockers[{index}]"
            if not isinstance(blocker, dict):
                issues.append(Issue("SCHEMA", path, f"{label} must be an object"))
                continue
            blocker_id = blocker.get("blocker_id")
            if not _is_nonempty_string(blocker_id):
                issues.append(Issue("SCHEMA", path, f"{label}.blocker_id is required"))
            elif blocker_id in blocker_ids:
                issues.append(Issue("SCHEMA", path, f"duplicate blocker_id: {blocker_id}"))
            else:
                blocker_ids.add(blocker_id)
            if not _is_nonempty_string(blocker.get("statement")):
                issues.append(Issue("SCHEMA", path, f"{label}.statement is required"))
            sources = blocker.get("sources")
            if not isinstance(sources, list) or not sources:
                issues.append(Issue("PROVENANCE", path, f"{label}.sources must be non-empty"))
            else:
                for source in sources:
                    issues.extend(validate_relative_source(root, path, source))

    for field in ("active_assumptions", "forbidden_inferences", "entry_points"):
        values = data.get(field)
        if not isinstance(values, list) or not values or not all(_is_nonempty_string(x) for x in values):
            issues.append(Issue("SCHEMA", path, f"{field} must be a non-empty string list"))
    for source in data.get("entry_points", []) if isinstance(data.get("entry_points"), list) else []:
        issues.extend(validate_relative_source(root, path, source))

    issues.extend(scan_forbidden_keys(path, data))
    return issues


def parse_decision_log(text: str) -> tuple[list[dict[str, Any]], list[Issue]]:
    decisions: list[dict[str, Any]] = []
    issues: list[Issue] = []
    for line_number, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            issues.append(Issue("SCHEMA", DECISION_LOG_PATH, f"line {line_number}: invalid JSON: {exc.msg}"))
            continue
        if not isinstance(value, dict):
            issues.append(Issue("SCHEMA", DECISION_LOG_PATH, f"line {line_number}: entry must be an object"))
            continue
        decisions.append(value)
    return decisions, issues


def validate_decisions(root: Path, decisions: list[dict[str, Any]]) -> list[Issue]:
    path = DECISION_LOG_PATH
    issues: list[Issue] = []
    seen_ids: set[str] = set()
    active_topics: dict[str, str] = {}

    if not decisions:
        return [Issue("SCHEMA", path, "decision log must contain at least one entry")]

    for index, decision in enumerate(decisions):
        label = f"entry[{index}]"
        missing = sorted(DECISION_REQUIRED_FIELDS - set(decision))
        if missing:
            issues.append(Issue("SCHEMA", path, f"{label} missing fields: {', '.join(missing)}"))

        decision_id = decision.get("decision_id")
        if not re.fullmatch(r"UL-DEC-\d{4}", str(decision_id or "")):
            issues.append(Issue("SCHEMA", path, f"{label} has invalid decision_id"))
        elif decision_id in seen_ids:
            issues.append(Issue("SCHEMA", path, f"duplicate decision_id: {decision_id}"))
        else:
            seen_ids.add(decision_id)

        for field in ("date", "topic", "decision", "status", "reason", "evidence_effect"):
            if not _is_nonempty_string(decision.get(field)):
                issues.append(Issue("SCHEMA", path, f"{label}.{field} is required"))

        try:
            datetime.strptime(str(decision.get("date", "")), "%Y-%m-%d")
        except ValueError:
            issues.append(Issue("SCHEMA", path, f"{label}.date must use YYYY-MM-DD"))

        status = decision.get("status")
        if status not in {"ACTIVE", "SUPERSEDED"}:
            issues.append(Issue("SCHEMA", path, f"{label}.status must be ACTIVE or SUPERSEDED"))

        topic = decision.get("topic")
        if status == "ACTIVE" and _is_nonempty_string(topic):
            if topic in active_topics:
                issues.append(
                    Issue(
                        "GOVERNANCE",
                        path,
                        f"multiple active decisions for topic {topic}: {active_topics[topic]} and {decision_id}",
                    )
                )
            else:
                active_topics[topic] = str(decision_id)

        supersedes = decision.get("supersedes")
        if supersedes is not None:
            if not isinstance(supersedes, str) or supersedes not in seen_ids:
                issues.append(Issue("PROVENANCE", path, f"{label}.supersedes must reference an earlier decision"))

        sources = decision.get("sources")
        if not isinstance(sources, list) or not sources:
            issues.append(Issue("PROVENANCE", path, f"{label}.sources must be non-empty"))
        else:
            for source in sources:
                issues.extend(validate_relative_source(root, path, source))

        issues.extend(scan_forbidden_keys(path, decision, f"$[{index}]"))

    return issues


def validate_repository(root: Path, *, check_git: bool = True) -> list[Issue]:
    root = root.resolve()
    issues: list[Issue] = []

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            issues.append(Issue("SCHEMA", relative, "required memory artifact is missing"))

    for relative in REQUIRED_FILES:
        path = root / relative
        if path.is_file():
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                issues.append(Issue("SCHEMA", relative, "file must be UTF-8 text"))
                continue
            issues.extend(scan_privacy(relative, text))

    checkpoint_file = root / CHECKPOINT_PATH
    if checkpoint_file.is_file():
        try:
            checkpoint = json.loads(checkpoint_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(Issue("SCHEMA", CHECKPOINT_PATH, f"invalid JSON: {exc.msg}"))
        else:
            issues.extend(validate_checkpoint(root, checkpoint, check_git=check_git))

    decision_file = root / DECISION_LOG_PATH
    if decision_file.is_file():
        text = decision_file.read_text(encoding="utf-8")
        decisions, parse_issues = parse_decision_log(text)
        issues.extend(parse_issues)
        issues.extend(validate_decisions(root, decisions))

    for relative in (
        "governance/UNIVERSELAB_MEMORY_PROTOCOL_v1.0.md",
        "prompts/UNIVERSELAB_CHAT_BOOTSTRAP_v1.0.md",
    ):
        path = root / relative
        if path.is_file() and "PUBLIC_SANITIZED" not in path.read_text(encoding="utf-8"):
            issues.append(Issue("PRIVACY", relative, "PUBLIC_SANITIZED classification is missing"))

    # Stable, deterministic reporting.
    return sorted(set(issues), key=lambda item: (item.category, item.path, item.message))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skip-git", action="store_true", help="Skip basis-commit existence check")
    args = parser.parse_args(argv)

    issues = validate_repository(args.root, check_git=not args.skip_git)
    if issues:
        for issue in issues:
            print(issue.render())
        privacy_failed = any(issue.category == "PRIVACY" for issue in issues)
        print(f"PRIVACY_GATE={'FAIL' if privacy_failed else 'PASS'}")
        print("MEMORY_CONTRACT=FAIL")
        return 1

    print("PRIVACY_GATE=PASS")
    print("MEMORY_CONTRACT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
