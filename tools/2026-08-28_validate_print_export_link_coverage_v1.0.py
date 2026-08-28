#!/usr/bin/env python3
"""UniverseLab print/export link coverage audit v1.0.

Scans HTML anchor navigation across the repository and verifies that human-facing
links into UniverseLab are covered by one of the established presentation layers:
HTML/global export, machine-data viewer, document viewer, or source-text viewer.

Explicit raw/download links are exempt by design. External websites are reported
as out of scope because UniverseLab cannot inject UI into foreign origins.

This is a presentation/navigation QA gate only. It does not modify scientific data,
solver state, governance gates, rank R, K1-D, K1-E, or evidence status.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

ROOT_PREFIX = "/UniverseLab/"
GITHUB_BLOB_PREFIX = "/stefanhasselm74314-byte/UniverseLab/blob/main/"

MACHINE_EXT = {".json", ".jsonl", ".ndjson", ".csv", ".tsv"}
DOCUMENT_EXT = {".md", ".markdown", ".txt", ".yml", ".yaml"}
SOURCE_EXT = {
    ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".css", ".scss",
    ".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd", ".toml", ".ini", ".cfg",
    ".conf", ".xml", ".tex", ".bib", ".sql", ".r", ".jl", ".java", ".c", ".h",
    ".cpp", ".hpp", ".log", ".properties",
}
HTML_EXT = {"", ".html", ".htm"}
SKIP_SCHEMES = {"mailto", "tel", "javascript", "data", "blob"}

REQUIRED_FILES = {
    "global_export": "assets/2026-08-19_UniverseLab_SitePrintExport_v1.0.js",
    "machine_viewer": "2026-08-20_UniverseLab_MachineDataViewer_v1.1.html",
    "document_router": "assets/2026-08-27_UniverseLab_DocumentLinkRouter_v1.0.js",
    "document_viewer": "2026-08-27_UniverseLab_DocumentViewer_v1.0.html",
    "source_viewer": "2026-08-27_UniverseLab_SourceTextViewer_v1.0.html",
    "bootstrap": "assets/2026-08-19_UniverseLab_SitePrintExportBootstrap_v1.0.js",
    "service_worker": "2026-08-19_UniverseLab_SitePrintExportServiceWorker_v1.0.js",
}


@dataclass(frozen=True)
class Link:
    source: Path
    href: str
    attrs: dict[str, str | None]

    @property
    def explicit_raw(self) -> bool:
        return (
            "download" in self.attrs
            or self.attrs.get("data-ul-raw-link") == "1"
            or self.attrs.get("data-ul-no-data-viewer") == "1"
            or self.attrs.get("data-ul-no-document-viewer") == "1"
        )


class AnchorParser(HTMLParser):
    def __init__(self, source: Path):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.links: list[Link] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attr_map = {k.lower(): v for k, v in attrs}
        href = attr_map.get("href")
        if href:
            self.links.append(Link(self.source, href, attr_map))


def classify_extension(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix in MACHINE_EXT:
        return "machine-viewer"
    if suffix in DOCUMENT_EXT:
        return "document-viewer"
    if suffix in SOURCE_EXT:
        return "source-viewer"
    if suffix in HTML_EXT:
        return "html-global-or-native"
    return "unsupported-internal-file"


def repository_target(repo_root: Path, link: Link) -> tuple[str, Path | None, str]:
    """Return (scope, local_target, normalized_display)."""
    raw = link.href.strip()
    if raw.startswith("#"):
        return "anchor", None, raw

    parsed = urlparse(raw)
    if parsed.scheme.lower() in SKIP_SCHEMES:
        return "non-http", None, raw

    # Canonical GitHub blob links into this repository are treated as local files.
    if parsed.scheme in {"http", "https"} and parsed.netloc.lower() == "github.com":
        if parsed.path.startswith(GITHUB_BLOB_PREFIX):
            repo_path = unquote(parsed.path[len(GITHUB_BLOB_PREFIX):]).lstrip("/")
            return "internal-github-blob", repo_root / repo_path, repo_path
        return "external-github", None, raw

    if parsed.scheme in {"http", "https"}:
        host = parsed.netloc.lower()
        if host == "stefanhasselm74314-byte.github.io" and parsed.path.startswith(ROOT_PREFIX):
            repo_path = unquote(parsed.path[len(ROOT_PREFIX):]).lstrip("/") or "index.html"
            return "internal-pages", repo_root / repo_path, repo_path
        return "external", None, raw

    # Relative or root-relative UniverseLab link.
    clean = unquote(parsed.path)
    if not clean or clean.endswith("/"):
        if clean.startswith(ROOT_PREFIX):
            repo_path = clean[len(ROOT_PREFIX):].lstrip("/") + "index.html"
            return "internal-relative", repo_root / repo_path, repo_path
        if clean in {"", "./", "../"}:
            target = (repo_root / link.source.parent / clean / "index.html").resolve()
            return "internal-relative", target, str(target.relative_to(repo_root.resolve()))

    if clean.startswith(ROOT_PREFIX):
        repo_path = clean[len(ROOT_PREFIX):].lstrip("/")
        return "internal-relative", repo_root / repo_path, repo_path
    if clean.startswith("/"):
        return "external-root", None, raw

    base = (repo_root / link.source.parent).resolve()
    target = (base / clean).resolve()
    try:
        rel = target.relative_to(repo_root.resolve())
    except ValueError:
        return "external-relative", None, raw
    return "internal-relative", target, rel.as_posix()


def audit(repo_root: Path) -> int:
    missing_required = [path for path in REQUIRED_FILES.values() if not (repo_root / path).is_file()]
    if missing_required:
        print("FAIL: required presentation-layer files are missing:")
        for path in missing_required:
            print(f"  - {path}")
        return 1

    html_files = sorted(
        p for p in repo_root.rglob("*.html")
        if ".git" not in p.parts and "node_modules" not in p.parts
    )
    links: list[Link] = []
    parse_errors: list[str] = []
    for path in html_files:
        rel = path.relative_to(repo_root)
        try:
            parser = AnchorParser(rel)
            parser.feed(path.read_text(encoding="utf-8", errors="replace"))
            links.extend(parser.links)
        except Exception as exc:  # fail closed on unreadable HTML
            parse_errors.append(f"{rel}: {exc}")

    categories: Counter[str] = Counter()
    unsupported: list[tuple[Link, str, Path | None]] = []
    missing_targets: list[tuple[Link, str]] = []
    examples: defaultdict[str, list[str]] = defaultdict(list)

    for link in links:
        scope, target, display = repository_target(repo_root, link)
        if scope in {"anchor", "non-http", "external", "external-github", "external-root", "external-relative"}:
            categories[scope] += 1
            continue

        if link.explicit_raw:
            categories["explicit-raw-download"] += 1
            continue

        kind = classify_extension(display)
        categories[kind] += 1
        if len(examples[kind]) < 5:
            examples[kind].append(f"{link.source}: {link.href}")

        if kind == "unsupported-internal-file":
            unsupported.append((link, display, target))
        elif target is not None and not target.exists():
            # Missing targets are surfaced as warnings here; dedicated link-integrity
            # checks may have their own policy. They are not a print/export failure.
            missing_targets.append((link, display))

    print("UniverseLab print/export link coverage audit v1.0")
    print(f"HTML pages scanned: {len(html_files)}")
    print(f"Anchor links scanned: {len(links)}")
    print("Coverage classes:")
    for key in sorted(categories):
        print(f"  {key}: {categories[key]}")

    if parse_errors:
        print("\nFAIL: HTML parse/read errors:")
        for item in parse_errors:
            print(f"  - {item}")

    if unsupported:
        print("\nFAIL: internal human-facing file links without a governed viewer/export route:")
        for link, display, target in unsupported:
            existence = "exists" if target is not None and target.exists() else "missing/unknown"
            print(f"  - {link.source}: {link.href} -> {display} [{existence}]")
        print("\nAdd a governed viewer/router for these file types or mark truly intentional raw/download links explicitly.")

    if missing_targets:
        print("\nWARN: covered links whose local target was not found in this checkout:")
        for link, display in missing_targets[:50]:
            print(f"  - {link.source}: {link.href} -> {display}")
        if len(missing_targets) > 50:
            print(f"  ... {len(missing_targets) - 50} more")

    if unsupported or parse_errors:
        return 1

    print("\nPASS: every scanned internal human-facing file link is covered by the current print/export/viewer architecture or is explicitly raw/download.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="repository root")
    args = parser.parse_args()
    return audit(Path(args.root).resolve())


if __name__ == "__main__":
    raise SystemExit(main())
