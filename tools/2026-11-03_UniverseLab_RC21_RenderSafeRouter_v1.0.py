#!/usr/bin/env python3
"""Render an RC21 noninstalled browser router from the RC19 exact-path manifest.

The generated JS is evidence, not an authorized website asset. Installation
requires a separate owner decision, website workflow update and release QA.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys


PUBLIC_SOURCE_SUFFIXES = frozenset({
    ".md", ".markdown", ".txt", ".yml", ".yaml", ".py", ".js", ".mjs",
    ".cjs", ".ts", ".tsx", ".jsx", ".css", ".scss", ".sh", ".bash",
    ".zsh", ".ps1", ".bat", ".cmd", ".toml", ".ini", ".cfg", ".conf",
    ".xml", ".tex", ".bib", ".sql", ".r", ".jl", ".java", ".c",
    ".h", ".cpp", ".hpp", ".log", ".properties",
})
PLACEHOLDERS = (
    "__RC21_BASE_COMMIT__", "__RC21_MANIFEST_SHA256__",
    "__RC21_ELIGIBLE_COUNT__", "__RC21_PUBLIC_PATHS_JSON__",
)


class CandidateHold(RuntimeError):
    pass


def _load_rc19(root: Path):
    path = root / "tools/2026-11-03_UniverseLab_RC19_PublicOnlyBuild_v1.0.py"
    spec = importlib.util.spec_from_file_location("rc21_rc19_loader", path)
    if spec is None or spec.loader is None:
        raise CandidateHold("RC19_VALIDATOR_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def render(root: Path, manifest_path: Path, template_path: Path) -> tuple[str, dict]:
    root = root.resolve(strict=True)
    raw_manifest = manifest_path.read_bytes()
    if len(raw_manifest) > 300_000:
        raise CandidateHold("MANIFEST_OVERSIZED")
    parsed = json.loads(raw_manifest.decode("utf-8"))
    rc19 = _load_rc19(root)
    allowed = rc19.load_manifest(manifest_path)
    for viewer in (
        "2026-08-27_UniverseLab_DocumentViewer_v1.0.html",
        "2026-08-27_UniverseLab_SourceTextViewer_v1.0.html",
    ):
        if viewer not in allowed:
            raise CandidateHold("PUBLIC_VIEWER_MISSING_FROM_MANIFEST:" + viewer)
    # A path entry alone does not prove that the pinned public bytes exist.
    # Fail closed before rendering if any source file diverges from RC19.
    for path, expected in allowed.items():
        if rc19._sha256(rc19._source_file(root, path)) != expected:
            raise CandidateHold("PUBLIC_FILE_DIGEST_MISMATCH:" + path)
    paths = sorted(p for p in allowed
                   if PurePosixPath(p).suffix.lower() in PUBLIC_SOURCE_SUFFIXES)
    if not paths:
        raise CandidateHold("NO_ROUTABLE_PUBLIC_SOURCE_PATHS")
    template = template_path.read_text(encoding="utf-8")
    for name in PLACEHOLDERS:
        if template.count(name) != 1:
            raise CandidateHold("TEMPLATE_PLACEHOLDER_NOT_UNIQUE:" + name)
    content = template
    substitutions = {
        "__RC21_BASE_COMMIT__": parsed["basis_main_commit"],
        "__RC21_MANIFEST_SHA256__": hashlib.sha256(raw_manifest).hexdigest(),
        "__RC21_ELIGIBLE_COUNT__": str(len(paths)),
        "__RC21_PUBLIC_PATHS_JSON__": json.dumps(paths, ensure_ascii=False, separators=(",", ":")),
    }
    for key, value in substitutions.items():
        content = content.replace(key, value)
    if any(name in content for name in PLACEHOLDERS):
        raise CandidateHold("UNEXPANDED_TEMPLATE_PLACEHOLDER")
    return content, {
        "schema": "universelab.rc21.router-candidate-provenance.v1",
        "status": "CANDIDATE_NOT_INSTALLED",
        "manifest_sha256": substitutions["__RC21_MANIFEST_SHA256__"],
        "basis_main_commit": parsed["basis_main_commit"],
        "public_source_paths": len(paths),
        "generated_router_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "website_changed": False,
        "physical_gate_effect": "NONE",
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check-existing", action="store_true")
    parser.add_argument("--provenance-out", type=Path)
    args = parser.parse_args()
    try:
        content, provenance = render(args.root, args.manifest, args.template)
        provenance_json = json.dumps(provenance, indent=2) + "\n"
        if args.check_existing:
            if args.output.read_text(encoding="utf-8") != content:
                raise CandidateHold("GENERATED_ROUTER_DRIFT")
            if (args.provenance_out and
                    args.provenance_out.read_text(encoding="utf-8") != provenance_json):
                raise CandidateHold("GENERATED_PROVENANCE_DRIFT")
        else:
            if args.output.exists():
                raise CandidateHold("OUTPUT_EXISTS_EXPLICIT_NO_OVERWRITE")
            if args.provenance_out and args.provenance_out.exists():
                raise CandidateHold("PROVENANCE_OUTPUT_EXISTS")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content, encoding="utf-8")
            if args.provenance_out:
                args.provenance_out.parent.mkdir(parents=True, exist_ok=True)
                args.provenance_out.write_text(provenance_json, encoding="utf-8")
    except (CandidateHold, OSError, ValueError) as exc:
        print(json.dumps({"status": "RC21_HOLD", "reason": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(provenance, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
