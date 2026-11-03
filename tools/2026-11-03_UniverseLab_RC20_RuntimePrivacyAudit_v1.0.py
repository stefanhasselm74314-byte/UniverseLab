#!/usr/bin/env python3
"""RC20 read-only staged-site privacy and source-aware link compatibility audit.

Static analysis, not browser execution or a real Pages-artifact attestation.
Never promote, merge, deploy, or release a scientific claim.
"""

from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
import importlib.util
import json
import posixpath
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = "/UniverseLab/"
GITHUB_BLOB = "/stefanhasselm74314-byte/UniverseLab/blob/main/"
DOC_SUFFIXES = frozenset({".md", ".markdown", ".txt", ".yml", ".yaml"})
SOURCE_SUFFIXES = frozenset({
    ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".css", ".scss",
    ".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd", ".toml", ".ini",
    ".cfg", ".conf", ".xml", ".tex", ".bib", ".sql", ".r", ".jl",
    ".java", ".c", ".h", ".cpp", ".hpp", ".log", ".properties",
})
PRIVACY_TEXT_SUFFIXES = frozenset({
    ".html", ".js", ".css", ".json", ".jsonl", ".md", ".txt",
    ".webmanifest", ".csv", ".xml", ".svg", ".yml", ".yaml",
})
REQUIRED_CHAIN = (
    "assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js",
    "assets/2026-08-19_UniverseLab_SitePrintExportBootstrap_v1.0.js",
    "assets/2026-08-27_UniverseLab_DocumentLinkRouter_v1.0.js",
    "2026-08-19_UniverseLab_SitePrintExportServiceWorker_v1.0.js",
    "2026-08-27_UniverseLab_DocumentViewer_v1.0.html",
    "2026-08-27_UniverseLab_SourceTextViewer_v1.0.html",
)


class AuditError(RuntimeError):
    pass


class _HTMLLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[dict[str, str]] = []
        self.external_executables: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "a" and a.get("href"):
            self.anchors.append(a)
        if tag in {"script", "iframe", "link"}:
            url = a.get("src", "") or a.get("href", "")
            scheme = urlsplit(url)
            if scheme.scheme in {"https", "http"}:
                if tag != "link" or a.get("rel", "").lower() in {"stylesheet", "modulepreload", "preload"}:
                    self.external_executables.append((tag, scheme.netloc.lower()))


def _get_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise AuditError(f"MODULE_UNAVAILABLE:{path.name}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _canonical_repo_path(page: str, url: str) -> str | None:
    """Emulate source-aware link-router target selection for static <a> links."""
    split = urlsplit(url.strip())
    path = unquote(split.path)
    if split.hostname == "github.com":
        if not path.startswith(GITHUB_BLOB):
            return None
        target = path[len(GITHUB_BLOB):]
    elif split.scheme or split.netloc:
        return None
    elif path.startswith(ROOT):
        target = path[len(ROOT):]
    elif path.startswith("/"):
        return None
    else:
        target = posixpath.normpath(posixpath.join(posixpath.dirname(page), path))
    if not target or target in {".", ".."} or target.startswith("../") or "\\" in target:
        return None
    if PurePosixPath(target).suffix.lower() not in DOC_SUFFIXES | SOURCE_SUFFIXES:
        return None
    return target


def _source_route_findings(repo: Path, stage: Path, allowed: set[str]) -> tuple[list[dict], list[dict], dict]:
    excluded_existing = []
    missing_in_repo = []
    executable_hosts = Counter()
    html_count = 0
    global_shell_pages = 0
    candidate_links = 0
    for rel in sorted(p for p in allowed if p.endswith(".html")):
        html_count += 1
        content = (stage / rel).read_text(encoding="utf-8", errors="replace")
        global_shell = "2026-08-16_UniverseLab_GlobalShell_v1.1.js" in content
        global_shell_pages += int(global_shell)
        parser = _HTMLLinks()
        parser.feed(content)
        for _, host in parser.external_executables:
            executable_hosts[host] += 1
        for anchor in parser.anchors:
            if ("download" in anchor or any(anchor.get(k) == "1" for k in (
                "data-ul-raw-link", "data-ul-no-document-viewer", "data-ul-no-data-viewer"
            ))):
                continue
            target = _canonical_repo_path(rel, anchor.get("href", ""))
            if not target:
                continue
            candidate_links += 1
            entry = {
                "source_html": rel,
                "target": target,
                "router_activation": "GLOBAL_SHELL_CHAIN" if global_shell else "SERVICE_WORKER_CONDITIONAL",
            }
            if target not in allowed:
                if (repo / target).is_file():
                    excluded_existing.append(entry)
                else:
                    missing_in_repo.append(entry)
    excluded_existing.sort(key=lambda x: (x["source_html"], x["target"]))
    missing_in_repo.sort(key=lambda x: (x["source_html"], x["target"]))
    return excluded_existing, missing_in_repo, {
        "html_files_checked": html_count,
        "pages_with_direct_global_shell": global_shell_pages,
        "eligible_static_document_source_links": candidate_links,
        "external_executable_hosts": dict(sorted(executable_hosts.items())),
        "runtime_generated_links": "NOT_ENUMERATED",
    }


def _data_driven_roadmap_findings(repo: Path, stage: Path, allowed: set[str]) -> list[dict]:
    """One evidence-bound renderer/data pairing, not arbitrary JSON-path guessing."""
    renderer = "2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.html"
    registry = "registry/2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.json"
    if renderer not in allowed or registry not in allowed:
        return []
    code = (stage / renderer).read_text(encoding="utf-8")
    if "roadmap_path" not in code or "github.com" not in code:
        return []
    obj = json.loads((stage / registry).read_text(encoding="utf-8"))
    findings = []
    for item in obj.get("solvers", []):
        path = item.get("roadmap_path")
        if not isinstance(path, str):
            continue
        if (repo / path).is_file() and path not in allowed:
            findings.append({
                "renderer": renderer,
                "registry": registry,
                "field": "solvers[*].roadmap_path",
                "target": path,
                "router_activation": "ASYNCHRONOUS_DOM_RACE_OR_SERVICE_WORKER_CONDITIONAL",
            })
    return sorted(findings, key=lambda x: x["target"])


def _strict_json_decode(raw: str, path: str, *, jsonl: bool = False) -> list[object]:
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise AuditError(f"DUPLICATE_JSON_KEY:{path}")
            result[key] = value
        return result
    try:
        if jsonl:
            return [json.loads(line, object_pairs_hook=unique_pairs,
                               parse_constant=lambda token: (_ for _ in ()).throw(ValueError("NONFINITE")))
                    for line in raw.splitlines() if line.strip()]
        return [json.loads(raw, object_pairs_hook=unique_pairs,
                           parse_constant=lambda token: (_ for _ in ()).throw(ValueError("NONFINITE")))]
    except (ValueError, TypeError) as exc:
        raise AuditError(f"INVALID_JSON:{path}:{type(exc).__name__}") from exc


def _privacy_scan(repo: Path, stage: Path, allowed: set[str]) -> tuple[list[dict], dict]:
    privacy = _get_module(repo / "tools/2026-08-03_validate_public_repository_privacy_v1.0.py", "rc20_privacy")
    findings: list[dict] = []
    scanned = 0
    total_bytes = 0
    for rel in sorted(allowed):
        path = stage / rel
        if path.suffix.lower() not in PRIVACY_TEXT_SUFFIXES:
            findings.append({"path": rel, "category": "UNSCANNED_FILE_TYPE"})
            continue
        scanned += 1
        raw = path.read_bytes()
        total_bytes += len(raw)
        try:
            content = raw.decode("utf-8", "strict")
        except UnicodeError:
            findings.append({"path": rel, "category": "INVALID_UTF8"})
            continue
        for name, pattern in privacy.PRIVACY_PATTERNS:
            if pattern.search(content):
                findings.append({"path": rel, "category": "PATTERN:" + name})
        if path.suffix.lower() in {".json", ".jsonl", ".webmanifest"}:
            try:
                values = _strict_json_decode(content, rel, jsonl=path.suffix.lower() == ".jsonl")
            except AuditError as exc:
                findings.append({"path": rel, "category": str(exc).split(":")[0]})
                continue
            for value in values:
                for warning in privacy.scan_json_keys(rel, value):
                    findings.append({"path": rel, "category": "FORBIDDEN_JSON_KEY"})
    findings = sorted({(f["path"], f["category"]) for f in findings})
    result = [{"path": path, "category": category} for path, category in findings]
    return result, {"files_scanned": scanned, "bytes_scanned": total_bytes,
                    "pattern_set": "2026-08-03_public_repository_privacy_v1.0_plus_strict_json_and_extra_types",
                    "semantic_personal_data_review": "NOT_PERFORMED"}


def audit(repo: Path, stage: Path, manifest: Path) -> dict:
    repo = repo.resolve(strict=True)
    stage = stage.resolve(strict=True)
    rc19 = _get_module(repo / "tools/2026-11-03_UniverseLab_RC19_PublicOnlyBuild_v1.0.py", "rc20_rc19")
    allowed = rc19.load_manifest(manifest)
    paths = set(allowed)
    actual = {p.relative_to(stage).as_posix() for p in stage.rglob("*") if p.is_file()}
    if actual != paths:
        raise AuditError("STAGING_FILES_DIFFER_FROM_EXACT_MANIFEST")
    for p, digest in allowed.items():
        if rc19._sha256(stage / p) != digest:
            raise AuditError(f"STAGING_CONTENT_HASH_DRIFT:{p}")
    if any(p.is_symlink() for p in stage.rglob("*")):
        raise AuditError("STAGING_SYMLINK_FORBIDDEN")

    excluded, missing, static = _source_route_findings(repo, stage, paths)
    roadmap = _data_driven_roadmap_findings(repo, stage, paths)
    privacy_findings, privacy_scope = _privacy_scan(repo, stage, paths)
    required_missing = sorted(set(REQUIRED_CHAIN) - paths)
    broken = len(excluded) > 0 or bool(required_missing)
    return {
        "schema": "universelab.rc20.runtime-privacy-audit.v1",
        "date": "2026-11-03",
        "source_main_commit": json.loads(manifest.read_text(encoding="utf-8"))["basis_main_commit"],
        "staging_files": len(paths),
        "source_link_router": {
            "status": "HOLD_EXCLUDED_ROUTED_TARGETS" if broken else "STATIC_NO_GAP_NOT_RUNTIME_PROOF",
            "excluded_existing_file_links": excluded,
            "data_driven_excluded_roadmap_targets": roadmap,
            "already_missing_repository_targets": missing,
            "required_chain_missing": required_missing,
            "summary": static,
        },
        "privacy": {
            "status": "PATTERN_HOLD" if privacy_findings else "PATTERN_PASS_NOT_PRIVACY_ATTESTATION",
            "findings": privacy_findings,
            "scope": privacy_scope,
        },
        "browser": {
            "desktop": "NOT_RUN",
            "android_real_device": "NOT_RUN",
            "android_emulation": "NOT_RUN",
            "dynamic_javascript_and_serviceworker_parity": "NOT_PROVEN",
        },
        "release_gate": "HOLD",  # Browser, content-owner and trusted required checks remain absent.
        "main_changed": False,
        "canonical_promotion": "BLOCKED",
        "physical_gate_effect": "NONE",
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("."))
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        result = audit(args.source, args.stage, args.manifest)
    except AuditError as exc:
        print(json.dumps({"status": "RC20_AUDIT_ERROR", "reason": str(exc)}))
        return 3
    if args.report:
        if args.report.resolve(strict=False).is_relative_to(args.stage.resolve(strict=True)):
            print(json.dumps({"status": "RC20_AUDIT_ERROR", "reason": "REPORT_INSIDE_PUBLIC_STAGING_FORBIDDEN"}))
            return 3
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    concise = {
        "status": "RC20_HOLD",
        "files": result["staging_files"],
        "routed_targets_excluded": len(result["source_link_router"]["excluded_existing_file_links"]),
        "data_driven_roadmap_targets_excluded": len(result["source_link_router"]["data_driven_excluded_roadmap_targets"]),
        "preexisting_unresolved": len(result["source_link_router"]["already_missing_repository_targets"]),
        "privacy_pattern_findings": len(result["privacy"]["findings"]),
        "browser": "NOT_RUN",
        "release_gate": result["release_gate"],
    }
    print(json.dumps(concise, sort_keys=True))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
