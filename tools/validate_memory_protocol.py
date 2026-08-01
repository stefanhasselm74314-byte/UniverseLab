#!/usr/bin/env python3
"""Read-only, fail-closed validator for the public UniverseLab memory protocol."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

REQUIRED_FILES = (
    "governance/UNIVERSELAB_MEMORY_PROTOCOL_v1.0.md",
    "registry/session-checkpoint-latest.json",
    "registry/decision-log.jsonl",
    "prompts/UNIVERSELAB_CHAT_BOOTSTRAP_v1.0.md",
    "tools/validate_memory_protocol.py",
    "tests/test_memory_protocol.py",
)

# Only public-memory content is scanned for privacy. Validator and test source
# contain detection patterns by design and are checked through syntax/unit tests.
PRIVACY_SCAN_FILES = REQUIRED_FILES[:4]
CHECKPOINT_PATH = "registry/session-checkpoint-latest.json"
DECISION_LOG_PATH = "registry/decision-log.jsonl"

CHECKPOINT_REQUIRED_FIELDS = {
    "schema", "checkpoint_id", "timestamp", "privacy_classification",
    "basis_commit", "architecture", "current_goal", "current_workstream",
    "gate_state", "verified_results", "open_blockers",
    "active_assumptions", "forbidden_inferences", "entry_points",
    "next_exact_action",
}
DECISION_REQUIRED_FIELDS = {
    "decision_id", "date", "topic", "decision", "status", "reason",
    "sources", "evidence_effect", "supersedes",
}
FORBIDDEN_JSON_KEYS = {
    "address", "api_key", "email", "password", "personal_notes", "phone",
    "private_key", "raw_chat", "secret", "share_link", "token", "transcript",
}
PRIVACY_PATTERNS = (
    ("chat_share_link", re.compile(r"https?://chatgpt\.com/share/", re.I)),
    ("openai_style_key", re.compile(r"\bsk-[A-Za-z0-9]{16,}\b")),
    ("github_classic_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("github_fine_grained_token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("private_key_block", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("email_address", re.compile(
        r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9.-])"
    )),
    ("unix_private_path", re.compile(r"(?:^|[\s'\"])/(?:home|Users)/[^\s'\"]+", re.M)),
    ("windows_private_path", re.compile(r"\b[A-Za-z]:\\Users\\[^\s'\"]+", re.I)),
    ("raw_dialogue_marker", re.compile(
        r"^(?:User|Assistant|Benutzer|Nutzer|ChatGPT|Stefan)\s*:\s+", re.I | re.M
    )),
)


@dataclass(frozen=True)
class Issue:
    category: str
    path: str
    message: str

    def render(self) -> str:
        return f"[{self.category}] {self.path}: {self.message}"


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def scan_privacy(path: str, text: str) -> list[Issue]:
    return [
        Issue("PRIVACY", path, f"forbidden pattern detected: {name}")
        for name, pattern in PRIVACY_PATTERNS
        if pattern.search(text)
    ]


def scan_forbidden_keys(path: str, value: Any, trail: str = "$") -> list[Issue]:
    issues: list[Issue] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).strip().lower() in FORBIDDEN_JSON_KEYS:
                issues.append(Issue("PRIVACY", path, f"forbidden JSON field at {trail}.{key}"))
            issues.extend(scan_forbidden_keys(path, nested, f"{trail}.{key}"))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            issues.extend(scan_forbidden_keys(path, nested, f"{trail}[{index}]"))
    return issues


def validate_source(root: Path, owner: str, source: Any) -> list[Issue]:
    if not nonempty(source):
        return [Issue("SCHEMA", owner, "source must be a non-empty string")]
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", source):
        return [Issue("PRIVACY", owner, f"external source URL is not allowed: {source}")]
    candidate = PurePosixPath(source)
    if candidate.is_absolute() or ".." in candidate.parts:
        return [Issue("PROVENANCE", owner, f"source path escapes repository: {source}")]
    if not (root / candidate).is_file():
        return [Issue("PROVENANCE", owner, f"source file does not exist: {source}")]
    return []


def validate_sources(root: Path, owner: str, sources: Any) -> list[Issue]:
    if not isinstance(sources, list) or not sources:
        return [Issue("PROVENANCE", owner, "sources must be a non-empty list")]
    issues: list[Issue] = []
    for source in sources:
        issues.extend(validate_source(root, owner, source))
    return issues


def validate_basis_commit(root: Path, commit: Any, check_git: bool) -> list[Issue]:
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        return [Issue("PROVENANCE", CHECKPOINT_PATH, "basis_commit must be a 40-character lowercase SHA-1")]
    if not check_git:
        return []
    if not (root / ".git").exists():
        return [Issue("PROVENANCE", CHECKPOINT_PATH, "Git checkout unavailable for basis_commit verification")]
    result = subprocess.run(
        ["git", "-C", str(root), "cat-file", "-e", f"{commit}^{{commit}}"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode:
        return [Issue("PROVENANCE", CHECKPOINT_PATH, f"basis_commit is absent from Git history: {commit}")]
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

    try:
        parsed = datetime.fromisoformat(data.get("timestamp", ""))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError
    except (TypeError, ValueError):
        issues.append(Issue("SCHEMA", path, "timestamp must be ISO-8601 with an explicit timezone"))

    issues.extend(validate_basis_commit(root, data.get("basis_commit"), check_git))

    architecture = data.get("architecture")
    if not isinstance(architecture, list) or not architecture or not all(nonempty(x) for x in architecture):
        issues.append(Issue("SCHEMA", path, "architecture must be a non-empty string list"))
    for field in ("current_goal", "current_workstream", "next_exact_action"):
        if not nonempty(data.get(field)):
            issues.append(Issue("SCHEMA", path, f"{field} must be a non-empty string"))

    gates = data.get("gate_state")
    if not isinstance(gates, dict):
        issues.append(Issue("SCHEMA", path, "gate_state must be an object"))
    else:
        for gate, expected in {"K1-D": "NOT_RELEASED", "K1-E": "NOT_ADMISSIBLE"}.items():
            if gates.get(gate) != expected:
                issues.append(Issue("GOVERNANCE", path, f"{gate} must remain {expected}"))

    results = data.get("verified_results")
    seen_results: set[str] = set()
    if not isinstance(results, list):
        issues.append(Issue("SCHEMA", path, "verified_results must be a list"))
    else:
        for index, item in enumerate(results):
            label = f"verified_results[{index}]"
            if not isinstance(item, dict):
                issues.append(Issue("SCHEMA", path, f"{label} must be an object"))
                continue
            result_id = item.get("result_id")
            if not nonempty(result_id):
                issues.append(Issue("SCHEMA", path, f"{label}.result_id is required"))
            elif result_id in seen_results:
                issues.append(Issue("SCHEMA", path, f"duplicate result_id: {result_id}"))
            else:
                seen_results.add(result_id)
            for field in ("statement", "status", "evidence_effect"):
                if not nonempty(item.get(field)):
                    issues.append(Issue("SCHEMA", path, f"{label}.{field} is required"))
            issues.extend(validate_sources(root, path, item.get("sources")))

    blockers = data.get("open_blockers")
    seen_blockers: set[str] = set()
    if not isinstance(blockers, list):
        issues.append(Issue("SCHEMA", path, "open_blockers must be a list"))
    else:
        for index, item in enumerate(blockers):
            label = f"open_blockers[{index}]"
            if not isinstance(item, dict):
                issues.append(Issue("SCHEMA", path, f"{label} must be an object"))
                continue
            blocker_id = item.get("blocker_id")
            if not nonempty(blocker_id):
                issues.append(Issue("SCHEMA", path, f"{label}.blocker_id is required"))
            elif blocker_id in seen_blockers:
                issues.append(Issue("SCHEMA", path, f"duplicate blocker_id: {blocker_id}"))
            else:
                seen_blockers.add(blocker_id)
            if not nonempty(item.get("statement")):
                issues.append(Issue("SCHEMA", path, f"{label}.statement is required"))
            issues.extend(validate_sources(root, path, item.get("sources")))

    for field in ("active_assumptions", "forbidden_inferences", "entry_points"):
        values = data.get(field)
        if not isinstance(values, list) or not values or not all(nonempty(x) for x in values):
            issues.append(Issue("SCHEMA", path, f"{field} must be a non-empty string list"))
    if isinstance(data.get("entry_points"), list):
        for source in data["entry_points"]:
            issues.extend(validate_source(root, path, source))

    issues.extend(scan_forbidden_keys(path, data))
    return issues


def parse_decision_log(text: str) -> tuple[list[dict[str, Any]], list[Issue]]:
    decisions: list[dict[str, Any]] = []
    issues: list[Issue] = []
    for number, raw in enumerate(text.splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            issues.append(Issue("SCHEMA", DECISION_LOG_PATH, f"line {number}: invalid JSON: {exc.msg}"))
            continue
        if not isinstance(value, dict):
            issues.append(Issue("SCHEMA", DECISION_LOG_PATH, f"line {number}: entry must be an object"))
            continue
        decisions.append(value)
    return decisions, issues


def validate_decisions(root: Path, decisions: list[dict[str, Any]]) -> list[Issue]:
    path = DECISION_LOG_PATH
    if not decisions:
        return [Issue("SCHEMA", path, "decision log must contain at least one entry")]
    issues: list[Issue] = []
    seen_ids: set[str] = set()
    active_topics: dict[str, str] = {}

    for index, item in enumerate(decisions):
        label = f"entry[{index}]"
        missing = sorted(DECISION_REQUIRED_FIELDS - set(item))
        if missing:
            issues.append(Issue("SCHEMA", path, f"{label} missing fields: {', '.join(missing)}"))
        decision_id = item.get("decision_id")
        if not re.fullmatch(r"UL-DEC-\d{4}", str(decision_id or "")):
            issues.append(Issue("SCHEMA", path, f"{label} has invalid decision_id"))
        elif decision_id in seen_ids:
            issues.append(Issue("SCHEMA", path, f"duplicate decision_id: {decision_id}"))
        else:
            seen_ids.add(decision_id)

        for field in ("date", "topic", "decision", "status", "reason", "evidence_effect"):
            if not nonempty(item.get(field)):
                issues.append(Issue("SCHEMA", path, f"{label}.{field} is required"))
        try:
            datetime.strptime(str(item.get("date", "")), "%Y-%m-%d")
        except ValueError:
            issues.append(Issue("SCHEMA", path, f"{label}.date must use YYYY-MM-DD"))

        status = item.get("status")
        if status not in {"ACTIVE", "SUPERSEDED"}:
            issues.append(Issue("SCHEMA", path, f"{label}.status must be ACTIVE or SUPERSEDED"))
        topic = item.get("topic")
        if status == "ACTIVE" and nonempty(topic):
            if topic in active_topics:
                issues.append(Issue(
                    "GOVERNANCE", path,
                    f"multiple active decisions for topic {topic}: {active_topics[topic]} and {decision_id}",
                ))
            else:
                active_topics[topic] = str(decision_id)

        supersedes = item.get("supersedes")
        if supersedes is not None and (not isinstance(supersedes, str) or supersedes not in seen_ids):
            issues.append(Issue("PROVENANCE", path, f"{label}.supersedes must reference an earlier decision"))
        issues.extend(validate_sources(root, path, item.get("sources")))
        issues.extend(scan_forbidden_keys(path, item, f"$[{index}]"))
    return issues


def validate_repository(root: Path, *, check_git: bool = True) -> list[Issue]:
    root = root.resolve()
    issues: list[Issue] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            issues.append(Issue("SCHEMA", relative, "required memory artifact is missing"))

    for relative in PRIVACY_SCAN_FILES:
        path = root / relative
        if path.is_file():
            try:
                issues.extend(scan_privacy(relative, path.read_text(encoding="utf-8")))
            except UnicodeDecodeError:
                issues.append(Issue("SCHEMA", relative, "file must be UTF-8 text"))

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
        decisions, parse_issues = parse_decision_log(decision_file.read_text(encoding="utf-8"))
        issues.extend(parse_issues)
        issues.extend(validate_decisions(root, decisions))

    for relative in PRIVACY_SCAN_FILES[::3]:
        path = root / relative
        if path.is_file() and "PUBLIC_SANITIZED" not in path.read_text(encoding="utf-8"):
            issues.append(Issue("PRIVACY", relative, "PUBLIC_SANITIZED classification is missing"))

    return sorted(set(issues), key=lambda issue: (issue.category, issue.path, issue.message))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--skip-git", action="store_true", help="Skip basis-commit existence check")
    args = parser.parse_args(argv)
    issues = validate_repository(args.root, check_git=not args.skip_git)
    if issues:
        for issue in issues:
            print(issue.render())
        print(f"PRIVACY_GATE={'FAIL' if any(x.category == 'PRIVACY' for x in issues) else 'PASS'}")
        print("MEMORY_CONTRACT=FAIL")
        return 1
    print("PRIVACY_GATE=PASS")
    print("MEMORY_CONTRACT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
