#!/usr/bin/env python3
"""Fail-closed privacy scanner for public UniverseLab text artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml"}
SCAN_ROOTS = ("registry", "governance", "prompts", "science")
ROOT_FILES = (
    "README.md",
    "project-manifest.json",
    "convention-registry.json",
    "research-status.html",
    "source.html",
    "index.html",
    "navigator-app.html",
    "hyperlab.html",
    "baryogenesis.html",
)
EXCLUDED_PARTS = {".git", "node_modules", "vendor"}

FORBIDDEN_JSON_KEYS = {
    "address", "api_key", "attachment_id", "attachment_ids",
    "conversation_id", "conversation_ids", "email", "password",
    "personal_notes", "phone", "private_key", "raw_chat", "secret",
    "share_link", "source_conversation_id", "source_conversation_ids",
    "token", "transcript",
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
    ("chat_attachment_identifier", re.compile(r"\bfile-[A-Za-z0-9]{12,}\b")),
    ("conversation_metadata_key", re.compile(r"\b(?:source_)?conversation_ids?\b\s*[:=]", re.I)),
    ("attachment_metadata_key", re.compile(r"\battachment_ids?\b\s*[:=]", re.I)),
    ("account_audit_artifact", re.compile(r"ChatGPT[_ -]?Account", re.I)),
    ("personalized_archive_prefix", re.compile(r"\bHassi_Hyperzeit_", re.I)),
    ("raw_dialogue_marker", re.compile(r"^(?:User|Assistant|Benutzer|Nutzer|ChatGPT|Stefan)\s*:\s+", re.I | re.M)),
)


@dataclass(frozen=True)
class Finding:
    category: str
    path: str
    detail: str

    def render(self) -> str:
        return f"[{self.category}] {self.path}: {self.detail}"


def iter_public_files(root: Path) -> Iterable[Path]:
    seen: set[Path] = set()
    for relative in ROOT_FILES:
        path = root / relative
        if path.is_file():
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield path
    for relative in SCAN_ROOTS:
        base = root / relative
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            if EXCLUDED_PARTS.intersection(path.parts):
                continue
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield path


def scan_text(path: str, text: str) -> list[Finding]:
    return [Finding("PRIVACY", path, f"forbidden pattern detected: {name}")
            for name, pattern in PRIVACY_PATTERNS if pattern.search(text)]


def scan_json_keys(path: str, value: Any, trail: str = "$") -> list[Finding]:
    findings: list[Finding] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).strip().lower() in FORBIDDEN_JSON_KEYS:
                findings.append(Finding("PRIVACY", path, f"forbidden JSON key at {trail}.{key}"))
            findings.extend(scan_json_keys(path, nested, f"{trail}.{key}"))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            findings.extend(scan_json_keys(path, nested, f"{trail}[{index}]"))
    return findings


def validate_file(root: Path, path: Path) -> list[Finding]:
    relative = path.relative_to(root).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [Finding("ENCODING", relative, "public text artifact must be UTF-8")]
    findings = scan_text(relative, text)
    if path.suffix.lower() == ".json":
        try:
            values = [json.loads(text)]
        except json.JSONDecodeError as exc:
            return findings + [Finding("SCHEMA", relative, f"invalid JSON: {exc.msg}")]
    elif path.suffix.lower() == ".jsonl":
        values = []
        for number, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                values.append(json.loads(line))
            except json.JSONDecodeError as exc:
                findings.append(Finding("SCHEMA", relative, f"line {number}: {exc.msg}"))
    else:
        values = []
    for value in values:
        findings.extend(scan_json_keys(relative, value))
    return findings


def validate_repository(root: Path) -> list[Finding]:
    root = root.resolve()
    findings: list[Finding] = []
    for path in iter_public_files(root):
        findings.extend(validate_file(root, path))
    return sorted(set(findings), key=lambda item: (item.path, item.detail))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root")
    args = parser.parse_args(argv)
    findings = validate_repository(Path(args.root))
    if findings:
        print("PUBLIC_PRIVACY_GATE = FAIL")
        for finding in findings:
            print(finding.render())
        return 1
    print("PUBLIC_PRIVACY_GATE = PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
