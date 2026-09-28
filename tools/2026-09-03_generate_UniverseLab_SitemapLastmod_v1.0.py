#!/usr/bin/env python3
"""Regenerate sitemap <lastmod> values from committed page history.

The date is the latest commit date of the mapped page resource in the
Europe/Berlin timezone. The script does not infer dates from content, branch
creation, registry metadata or the current clock.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Iterable
from urllib.parse import urlsplit

BASE_URL = "https://stefanhasselm74314-byte.github.io/UniverseLab/"
URL_LINE = re.compile(
    r"^(?P<prefix>\s*<url><loc>)(?P<loc>[^<]+)(?P<middle></loc><lastmod>)(?P<date>\d{4}-\d{2}-\d{2})(?P<suffix></lastmod>.*)$"
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class SitemapError(RuntimeError):
    pass


@dataclass(frozen=True)
class Entry:
    line_index: int
    loc: str
    repository_path: str
    old_date: str
    new_date: str


def repository_path_for_location(loc: str) -> str:
    if not loc.startswith(BASE_URL):
        raise SitemapError(f"LOCATION_OUTSIDE_CANONICAL_BASE:{loc}")
    parsed = urlsplit(loc)
    relative = parsed.path.removeprefix("/UniverseLab/")
    if not relative:
        relative = "index.html"
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts:
        raise SitemapError(f"UNSAFE_SITEMAP_PATH:{relative}")
    return path.as_posix()


def latest_commit_date(repo: Path, repository_path: str) -> str:
    target = repo / repository_path
    if not target.is_file():
        raise SitemapError(f"SITEMAP_TARGET_MISSING:{repository_path}")
    env = os.environ.copy()
    env["TZ"] = "Europe/Berlin"
    command = [
        "git", "-C", str(repo), "log", "-1",
        "--date=format-local:%Y-%m-%d", "--format=%ad", "--", repository_path,
    ]
    result = subprocess.run(command, check=False, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise SitemapError(f"GIT_LOG_FAILED:{repository_path}:{result.stderr.strip()}")
    value = result.stdout.strip()
    if not DATE_RE.fullmatch(value):
        raise SitemapError(f"NO_COMMIT_DATE:{repository_path}:{value!r}")
    # Parsing provides a second strict calendar validation.
    datetime.strptime(value, "%Y-%m-%d")
    return value


def generate(repo: Path, sitemap_path: Path) -> tuple[str, list[Entry]]:
    source = sitemap_path.read_text(encoding="utf-8")
    lines = source.splitlines(keepends=True)
    entries: list[Entry] = []
    seen_locations: set[str] = set()
    seen_paths: set[str] = set()

    for index, line in enumerate(lines):
        ending = "\n" if line.endswith("\n") else ""
        body = line[:-1] if ending else line
        match = URL_LINE.fullmatch(body)
        if not match:
            continue
        loc = match.group("loc")
        if loc in seen_locations:
            raise SitemapError(f"DUPLICATE_LOCATION:{loc}")
        seen_locations.add(loc)
        repository_path = repository_path_for_location(loc)
        if repository_path in seen_paths:
            raise SitemapError(f"DUPLICATE_REPOSITORY_PATH:{repository_path}")
        seen_paths.add(repository_path)
        new_date = latest_commit_date(repo, repository_path)
        entries.append(Entry(index, loc, repository_path, match.group("date"), new_date))
        lines[index] = (
            f"{match.group('prefix')}{loc}{match.group('middle')}"
            f"{new_date}{match.group('suffix')}{ending}"
        )

    if not entries:
        raise SitemapError("NO_SITEMAP_ENTRIES_FOUND")
    if source.count("<url>") != len(entries):
        raise SitemapError(
            f"UNPARSED_URL_ENTRIES:xml={source.count('<url>')}:parsed={len(entries)}"
        )
    return "".join(lines), entries


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--repo", default=".")
    value.add_argument("--sitemap", default="sitemap.xml")
    value.add_argument("--check", action="store_true")
    value.add_argument("--generated-output", default="sitemap.generated.xml")
    value.add_argument("--report", default="sitemap-lastmod-report.tsv")
    return value


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(list(argv) if argv is not None else None)
    repo = Path(args.repo).resolve()
    sitemap = (repo / args.sitemap).resolve()
    generated_output = (repo / args.generated_output).resolve()
    report_path = (repo / args.report).resolve()
    try:
        generated, entries = generate(repo, sitemap)
        generated_output.write_text(generated, encoding="utf-8")
        report_lines = ["location\trepository_path\told_lastmod\tnew_lastmod"]
        report_lines.extend(
            f"{entry.loc}\t{entry.repository_path}\t{entry.old_date}\t{entry.new_date}"
            for entry in entries
        )
        report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
        if args.check:
            current = sitemap.read_text(encoding="utf-8")
            if current != generated:
                changed = [entry for entry in entries if entry.old_date != entry.new_date]
                print(
                    f"SITEMAP_LASTMOD_MISMATCH:{len(changed)} entries require regeneration",
                    file=sys.stderr,
                )
                for entry in changed:
                    print(
                        f"  {entry.repository_path}: {entry.old_date} -> {entry.new_date}",
                        file=sys.stderr,
                    )
                return 1
            print(f"UniverseLab sitemap lastmod contract: PASS ({len(entries)} entries)")
            return 0
        sitemap.write_text(generated, encoding="utf-8")
        changed = sum(entry.old_date != entry.new_date for entry in entries)
        print(f"UniverseLab sitemap regenerated: {changed}/{len(entries)} lastmod values changed")
        return 0
    except (OSError, SitemapError, ValueError) as exc:
        print(f"SITEMAP_GENERATION_FAIL_CLOSED:{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
