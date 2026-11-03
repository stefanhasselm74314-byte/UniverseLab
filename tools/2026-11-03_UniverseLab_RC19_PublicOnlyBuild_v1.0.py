#!/usr/bin/env python3
"""RC19 candidate: construct an exact-path, digest-pinned static Pages tree.

This program does not deploy, merge, configure rulesets, or grant authority.
Its manifest is a review *candidate*, not a production publication decision.
"""

from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import stat
from urllib.parse import unquote, urlsplit


SCHEMA = "universelab.rc19.public-only-allowlist.v1"
BLOCKED_SEGMENTS = frozenset(
    {"drafts", "governance", "science", "tools", "tests", ".git", ".github",
     "prompts", "recovery", "reproducibility", "requirements", "__pycache__"}
)
PUBLIC_DIRS = frozenset({"assets", "registry", "schemas"})
ROOT_EXTENSIONS = frozenset(
    {".html", ".js", ".css", ".json", ".xml", ".txt",
     ".webmanifest", ".csv", ".md"}
)
NESTED_EXTENSIONS = ROOT_EXTENSIONS | frozenset(
    {".png", ".jpg", ".jpeg", ".svg", ".webp", ".ico", ".woff", ".woff2", ".jsonl"}
)
HEX_40 = re.compile(r"^[a-f0-9]{40}$")
HEX_64 = re.compile(r"^[a-f0-9]{64}$")
CSS_URL = re.compile(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)", re.I)
JS_FETCH = re.compile(r"\b(?:fetch|importScripts)\(\s*['\"]([^'\"]+)['\"]", re.I)


class BuildHold(RuntimeError):
    """A fail-closed candidate result, not a permission to release."""


def validate_path(raw: object) -> str:
    if not isinstance(raw, str) or not raw or len(raw) > 240:
        raise BuildHold("INVALID_PATH_TYPE_OR_LENGTH")
    if any(token in raw for token in ("\\", "\x00", "\n", "%", "*", "?", "[", "]")):
        raise BuildHold(f"NON_CANONICAL_PATH:{raw!r}")
    path = PurePosixPath(raw)
    parts = raw.split("/")
    if path.is_absolute() or any(p in {"", ".", ".."} or p.startswith(".") for p in parts):
        raise BuildHold(f"UNSAFE_PATH:{raw!r}")
    if any(p in BLOCKED_SEGMENTS for p in parts):
        raise BuildHold(f"BLOCKED_PREFIX:{raw!r}")
    if len(parts) == 1:
        permitted = path.suffix.lower() in ROOT_EXTENSIONS
    else:
        permitted = len(parts) == 2 and parts[0] in PUBLIC_DIRS and path.suffix.lower() in NESTED_EXTENSIONS
    if not permitted:
        raise BuildHold(f"PATH_OUTSIDE_STATIC_PUBLIC_ENVELOPE:{raw!r}")
    return raw


def load_manifest(path: Path) -> dict[str, str]:
    try:
        raw = path.read_text(encoding="utf-8")
        obj = json.loads(raw, object_pairs_hook=_unique_object)
    except (UnicodeError, OSError, ValueError) as exc:
        raise BuildHold(f"MANIFEST_PARSE_FAILED:{exc}") from exc
    if not isinstance(obj, dict) or set(obj) != {
        "schema", "status", "basis_main_commit", "basis_main_tree", "files"
    }:
        raise BuildHold("MANIFEST_SCHEMA_FIELDS_INVALID")
    if obj["schema"] != SCHEMA or obj["status"] != "DRAFT_NOT_AUTHORIZED":
        raise BuildHold("MANIFEST_IDENTITY_OR_STATUS_INVALID")
    if not isinstance(obj["basis_main_commit"], str) or not HEX_40.fullmatch(obj["basis_main_commit"]):
        raise BuildHold("MANIFEST_BASE_COMMIT_INVALID")
    if not isinstance(obj["basis_main_tree"], str) or not HEX_40.fullmatch(obj["basis_main_tree"]):
        raise BuildHold("MANIFEST_BASE_TREE_INVALID")
    entries = obj["files"]
    if not isinstance(entries, list) or not entries or len(entries) > 1000:
        raise BuildHold("MANIFEST_ENTRIES_INVALID")
    result: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise BuildHold("MANIFEST_FILE_FIELDS_INVALID")
        p = validate_path(entry["path"])
        h = entry["sha256"]
        if not isinstance(h, str) or not HEX_64.fullmatch(h):
            raise BuildHold(f"INVALID_DIGEST:{p}")
        if p in result:
            raise BuildHold(f"DUPLICATE_PATH:{p}")
        result[p] = h
    if list(result) != sorted(result):
        raise BuildHold("MANIFEST_NOT_SORTED")
    for critical in ("index.html", "navigator.html", "sw.js", "manifest.webmanifest", "robots.txt", "sitemap.xml"):
        if critical not in result:
            raise BuildHold(f"CRITICAL_ROUTE_NOT_ALLOWED:{critical}")
    return result


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"DUPLICATE_JSON_KEY:{key}")
        obj[key] = value
    return obj


def _source_file(root: Path, rel: str) -> Path:
    current = root
    for part in rel.split("/"):
        current = current / part
        try:
            mode = current.lstat().st_mode
        except OSError as exc:
            raise BuildHold(f"SOURCE_PATH_MISSING:{rel}:{exc}") from exc
        if stat.S_ISLNK(mode):
            raise BuildHold(f"SOURCE_SYMLINK_FORBIDDEN:{rel}")
    if not current.is_file() or not stat.S_ISREG(current.stat().st_mode):
        raise BuildHold(f"SOURCE_NOT_REGULAR_FILE:{rel}")
    if current.stat().st_mode & 0o111:
        raise BuildHold(f"SOURCE_EXECUTABLE_FORBIDDEN:{rel}")
    return current


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class _HTMLRefs(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: set[str] = set()
        self.style_content: list[str] = []
        self._inside_style = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "style":
            self._inside_style = True
        for key, value in attrs:
            if key in {"href", "src", "poster", "data-src"} and value:
                self.links.add(value)
            if key == "style" and value:
                self.links.update(CSS_URL.findall(value))

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self._inside_style = False

    def handle_data(self, data: str) -> None:
        if self._inside_style:
            self.style_content.append(data)


def _relative_target(page: str, url: str) -> str | None:
    if not url or "${" in url or "{" in url or "}" in url:
        return None
    parsed = urlsplit(url.strip())
    if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/"):
        return None
    path = unquote(parsed.path)
    if "\\" in path or "\x00" in path:
        return None
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(page), path))
    if resolved in {"..", "."} or resolved.startswith("../"):
        return None
    if path.endswith("/"):
        resolved = posixpath.join(resolved, "index.html")
    return resolved


def audit_literal_links(source: Path, allowed: set[str]) -> dict[str, list[str]]:
    """Static-literal coverage only; dynamic JS, runtime requests and URLs are not proven."""
    uncovered: set[str] = set()
    preexisting_missing: set[str] = set()
    for rel in sorted(allowed):
        suffix = PurePosixPath(rel).suffix.lower()
        if suffix not in {".html", ".css", ".js"}:
            continue
        content = (source / rel).read_text(encoding="utf-8", errors="replace")
        refs: set[str] = set()
        if suffix == ".html":
            parser = _HTMLRefs()
            parser.feed(content)
            refs |= parser.links
            for style in parser.style_content:
                refs.update(CSS_URL.findall(style))
        if suffix == ".css":
            refs.update(CSS_URL.findall(content))
        if suffix in {".js", ".html"}:
            refs.update(JS_FETCH.findall(content))
        for url in refs:
            # fetch('...') in an external JS file is resolved against the page
            # URL, normally the site root, not the JS asset directory.
            ref_base = "index.html" if suffix == ".js" else rel
            target = _relative_target(ref_base, url)
            if target is None or target in allowed:
                continue
            probe = source / target
            if probe.is_file():
                uncovered.add(f"{rel} -> {target}")
            else:
                preexisting_missing.add(f"{rel} -> {target}")
    return {"uncovered_existing": sorted(uncovered), "preexisting_missing": sorted(preexisting_missing)}


def _validate_metadata(path: Path, expected_sha: str) -> bytes:
    if not HEX_40.fullmatch(expected_sha):
        raise BuildHold("EXPECTED_DEPLOY_SHA_INVALID")
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 2048:
        raise BuildHold("DEPLOY_META_PATH_UNSAFE")
    try:
        obj = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except (UnicodeError, ValueError, OSError) as exc:
        raise BuildHold(f"DEPLOY_META_INVALID:{exc}") from exc
    if not isinstance(obj, dict) or set(obj) != {
        "schema", "source_sha", "source_ref", "event_name", "workflow_run_id", "workflow_run_attempt"
    }:
        raise BuildHold("DEPLOY_META_FIELDS_INVALID")
    if obj["schema"] != "UniverseLab.PagesDeployment.v1" or obj["source_sha"] != expected_sha:
        raise BuildHold("DEPLOY_META_SHA_OR_SCHEMA_INVALID")
    if type(obj["workflow_run_attempt"]) is not int or obj["workflow_run_attempt"] != 1:
        raise BuildHold("DEPLOY_META_RERUN_FORBIDDEN")
    if (obj["source_ref"] != "refs/heads/main"
            or obj["event_name"] not in {"push", "workflow_dispatch"}
            or not isinstance(obj["workflow_run_id"], str)
            or re.fullmatch(r"[0-9]{1,20}", obj["workflow_run_id"]) is None):
        raise BuildHold("DEPLOY_META_VALUES_INVALID")
    return (json.dumps(obj, sort_keys=True, indent=2) + "\n").encode("utf-8")


def build(
    source: Path, manifest_path: Path, output: Path, *,
    metadata: Path | None = None, expected_deploy_sha: str | None = None,
    strict_links: bool = True,
) -> dict:
    source = source.resolve(strict=True)
    output = output.resolve(strict=False)
    if output == source or output in source.parents or source / ".git" in output.parents:
        raise BuildHold("OUTPUT_LOCATION_FORBIDDEN")
    if output.exists():
        raise BuildHold("OUTPUT_MUST_BE_ABSENT_NOT_REUSED")
    allowed = load_manifest(manifest_path)
    # Verify the entire source set before creating any output.
    sizes: dict[str, int] = {}
    for rel, expected_digest in allowed.items():
        input_path = _source_file(source, rel)
        if _sha256(input_path) != expected_digest:
            raise BuildHold(f"CONTENT_SHA256_MISMATCH:{rel}")
        sizes[rel] = input_path.stat().st_size
    link_status = audit_literal_links(source, set(allowed))
    if strict_links and link_status["uncovered_existing"]:
        raise BuildHold("PUBLIC_LINK_TARGET_EXCLUDED:" + str(link_status["uncovered_existing"][:5]))

    deploy_meta = None
    if metadata is not None:
        if not expected_deploy_sha:
            raise BuildHold("EXPECTED_DEPLOY_SHA_REQUIRED")
        deploy_meta = _validate_metadata(metadata, expected_deploy_sha)
    elif expected_deploy_sha is not None:
        raise BuildHold("DEPLOY_META_MISSING")

    output.mkdir(parents=True)
    try:
        for rel, digest in allowed.items():
            target = output / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / rel, target, follow_symlinks=False)
            if _sha256(target) != digest:
                raise BuildHold(f"POST_COPY_HASH_MISMATCH:{rel}")
        if deploy_meta is not None:
            (output / "deploy-meta.json").write_bytes(deploy_meta)
        produced = {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()}
        expected = set(allowed) | ({"deploy-meta.json"} if deploy_meta is not None else set())
        if produced != expected:
            raise BuildHold("OUTPUT_INVENTORY_MISMATCH")
        if any(p.is_symlink() for p in output.rglob("*")):
            raise BuildHold("OUTPUT_SYMLINK_FORBIDDEN")
    except Exception:
        # A failed staging candidate is not a distributable artifact.
        shutil.rmtree(output)
        raise
    return {
        "status": "RC19_CANDIDATE_BUILD_PASS_NOT_RELEASE",
        "file_count": len(allowed),
        "staged_bytes": sum(sizes.values()) + (len(deploy_meta) if deploy_meta else 0),
        "uncovered_existing_links": link_status["uncovered_existing"],
        "preexisting_missing_literal_links": link_status["preexisting_missing"],
        "dynamic_runtime_link_closure": "NOT_PROVEN",
        "pages_deployment_changed": False,
        "canonical_promotion": "BLOCKED",
        "physical_gate_effect": "NONE",
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("."))
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--deploy-meta", type=Path)
    parser.add_argument("--expected-deploy-sha")
    parser.add_argument("--diagnostic-links-only", action="store_true",
                        help="Emit link gaps without failing; never use for authorized deployment")
    args = parser.parse_args()
    try:
        report = build(args.source, args.manifest, args.out,
                       metadata=args.deploy_meta, expected_deploy_sha=args.expected_deploy_sha,
                       strict_links=not args.diagnostic_links_only)
    except BuildHold as exc:
        print(json.dumps({"status": "RC19_HOLD", "reason": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
