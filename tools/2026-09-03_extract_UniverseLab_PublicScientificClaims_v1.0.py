#!/usr/bin/env python3
"""Extract public scientific claim candidates from UniverseLab pages.

This is a deterministic lexical census, not a scientific adjudicator.  It
extracts visible text blocks from every tracked HTML file plus README.md,
labels explicit scope/status markers, and ranks candidates for later manual
claim -> equation -> code -> test -> source -> falsifier review.

No network access, physical backend import, solver execution, authorization,
or evidence promotion is performed.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, asdict
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Any, Iterable
from urllib.parse import urlsplit

BASE_URL = "https://stefanhasselm74314-byte.github.io/UniverseLab/"
BLOCK_TAGS = {
    "address", "article", "aside", "blockquote", "caption", "dd", "details",
    "dialog", "div", "dl", "dt", "figcaption", "figure", "footer", "form",
    "h1", "h2", "h3", "h4", "h5", "h6", "header", "li", "main", "nav",
    "p", "pre", "section", "summary", "table", "td", "th", "tr",
}
HIDDEN_TAGS = {"script", "style", "template", "noscript", "svg"}
REGION_TAGS = {"main", "article", "section", "aside", "header", "nav", "footer"}
SPACE = re.compile(r"\s+")
DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}_")

LEXICON: dict[str, tuple[str, ...]] = {
    "THEORY_6D_PARENT": (
        "6d", "sechsdimensional", "six-dimensional", "hyperzeit", "parent-sektor",
        "parent sector", "parent→", "parent-to", "parent map", "parentabbildung",
    ),
    "DERIVATION_IDENTIFICATION": (
        "hergeleitet", "herleitung", "ableitung", "derives", "derived", "derivation",
        "identifiziert", "identification", "erklärt", "explains", "ursprung", "origin",
    ),
    "EVIDENCE_CONFIRMATION": (
        "beweist", "bewiesen", "bestätigt", "bestätigung", "nachgewiesen",
        "evidenz", "empirisch", "proves", "proved", "confirmed", "confirmation",
        "demonstrates", "evidence", "empirical", "validated", "validation",
    ),
    "PREDICTION_SIGNATURE": (
        "vorhersage", "vorhersagt", "prediction", "predicts", "signatur", "signature",
        "testbar", "testable", "messbar", "measurable", "falsifiz", "falsif",
    ),
    "OBSERVATIONAL_DATA": (
        "beobachtung", "observational", "observation", "messung", "measurement",
        "daten", "data", "likelihood", "kovarianz", "covariance", "posterior",
        "desi", "kids", "pantheon", "planck", "euclid", "lisa", "pta", "et/ce",
        "gravitationswelle", "gravitational wave", "gw-fenster", "bao", "supernova",
    ),
    "PHYSICAL_COSMOLOGY": (
        "friedmann", "flrw", "lcdm", "λcdm", "dunkle materie", "dark matter",
        "dunkle energie", "dark energy", "gravitation", "gravity", "raumzeit",
        "spacetime", "kosmolog", "cosmolog", "universum", "universe", "singularität",
        "singularity", "schwarzes loch", "black hole", "krümmung", "curvature",
        "struktur", "structure", "wachstum", "growth", "lensing",
    ),
    "NUMERICAL_METHOD": (
        "numerisch", "numerical", "rk4", "ode", "solver", "jacobi", "jacobian",
        "rang", "rank", "svd", "qr", "integration", "simpson", "residual",
    ),
    "STATUS_FIREWALL": (
        "not released", "not admissible", "not established", "not executed",
        "not authorized", "unreleased", "blocked", "gesperrt", "blockiert",
        "nicht freigegeben", "nicht veröffentlicht", "nicht hergeleitet", "offen",
        "open", "keine empirische", "no empirical", "keine evidenz", "no evidence",
        "keine likelihood", "no likelihood", "keine theoriebestätigung",
        "no theory confirmation", "≠", "not equal", "does not imply",
    ),
    "CONDITIONAL_HEURISTIC": (
        "konditional", "conditional", "modellannahme", "model assumption", "heuristisch",
        "heuristic", "didaktisch", "didactic", "referenz", "reference", "proxy",
        "kandidat", "candidate", "illustrativ", "illustrative", "visualisierung",
        "visualization", "demonstrator", "experimentell", "experimental",
    ),
}

STRONG_OVERCLAIM = (
    "beweist", "bewiesen", "bestätigt die theorie", "nachgewiesen", "proves",
    "proved", "confirms the theory", "confirmed the theory", "demonstrates that",
    "erklärt die dunkle materie", "explains dark matter", "ersetzt dunkle materie",
    "replaces dark matter", "hergeleitet aus 6d", "derived from 6d",
)
EXPLICIT_LIMITERS = LEXICON["STATUS_FIREWALL"] + LEXICON["CONDITIONAL_HEURISTIC"]
EQUATION_MARKERS = (
    "=", "→", "∂", "∫", "Ω", "Λ", "σ", "β", "η", "μ", "Σ", "sqrt(",
    "log", "ln ", "d²", "d/", "e²", "h(z)", "d(a)", "fσ", "q(a)",
)


class CensusError(RuntimeError):
    pass


@dataclass(frozen=True)
class Block:
    path: str
    source_sha256: str
    page_scope: str
    manifest_status: str | None
    tag: str
    region: str
    line: int
    text: str


@dataclass(frozen=True)
class Candidate:
    claim_id: str
    path: str
    source_sha256: str
    page_scope: str
    manifest_status: str | None
    tag: str
    region: str
    source_line: int
    text: str
    lexical_categories: list[str]
    equation_like: bool
    explicit_status: str
    limiter_present: bool
    preliminary_risk_score: int
    preliminary_risk_class: str
    adjudication_status: str


class VisibleBlockParser(HTMLParser):
    def __init__(self, path: str, source_sha256: str, page_scope: str, manifest_status: str | None):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.source_sha256 = source_sha256
        self.page_scope = page_scope
        self.manifest_status = manifest_status
        self.stack: list[str] = []
        self.hidden_depth = 0
        self.block_stack: list[dict[str, Any]] = []
        self.blocks: list[Block] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lower = tag.lower()
        self.stack.append(lower)
        if lower in HIDDEN_TAGS:
            self.hidden_depth += 1
        if lower == "meta":
            attributes = {key.lower(): value for key, value in attrs if value is not None}
            if attributes.get("name", "").lower() == "description" and attributes.get("content"):
                self._append("meta-description", self.getpos()[0], attributes["content"])
        if lower in BLOCK_TAGS and self.hidden_depth == 0:
            self.block_stack.append({"tag": lower, "line": self.getpos()[0], "parts": []})

    def handle_endtag(self, tag: str) -> None:
        lower = tag.lower()
        if lower in BLOCK_TAGS and self.hidden_depth == 0 and self.block_stack:
            # Close the nearest matching open block. Nested text remains in the
            # outer block as context; exact duplicates are removed later.
            index = next((i for i in range(len(self.block_stack)-1, -1, -1) if self.block_stack[i]["tag"] == lower), None)
            if index is not None:
                block = self.block_stack.pop(index)
                self._append(block["tag"], block["line"], " ".join(block["parts"]))
        if lower in HIDDEN_TAGS and self.hidden_depth:
            self.hidden_depth -= 1
        for index in range(len(self.stack)-1, -1, -1):
            if self.stack[index] == lower:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if self.hidden_depth or not data.strip():
            return
        for block in self.block_stack:
            block["parts"].append(data)
        if self.stack and self.stack[-1] == "title":
            self._append("title", self.getpos()[0], data)

    def _append(self, tag: str, line: int, value: str) -> None:
        normalized = SPACE.sub(" ", value).strip()
        if len(normalized) < 3:
            return
        region = next((tag for tag in reversed(self.stack) if tag in REGION_TAGS), "document")
        self.blocks.append(Block(
            path=self.path,
            source_sha256=self.source_sha256,
            page_scope=self.page_scope,
            manifest_status=self.manifest_status,
            tag=tag,
            region=region,
            line=line,
            text=normalized,
        ))


def run_git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise CensusError(f"GIT_COMMAND_FAILED:{' '.join(args)}:{result.stderr.strip()}")
    return result.stdout


def tracked_html(root: Path) -> list[str]:
    output = run_git(root, "ls-files", "*.html")
    result = sorted(line.strip() for line in output.splitlines() if line.strip())
    if not result:
        raise CensusError("NO_TRACKED_HTML_FILES")
    return result


def sitemap_paths(root: Path) -> set[str]:
    source = (root / "sitemap.xml").read_text(encoding="utf-8")
    locations = re.findall(r"<loc>([^<]+)</loc>", source)
    result: set[str] = set()
    for location in locations:
        if not location.startswith(BASE_URL):
            raise CensusError(f"NONCANONICAL_SITEMAP_LOCATION:{location}")
        relative = urlsplit(location).path.removeprefix("/UniverseLab/") or "index.html"
        path = PurePosixPath(relative)
        if path.is_absolute() or ".." in path.parts:
            raise CensusError(f"UNSAFE_SITEMAP_PATH:{relative}")
        result.add(path.as_posix())
    return result


def manifest_pages(root: Path) -> dict[str, str]:
    manifest = json.loads((root / "project-manifest.json").read_text(encoding="utf-8"))
    result: dict[str, str] = {}
    for page in manifest.get("canonical_pages", []):
        if isinstance(page, dict) and isinstance(page.get("path"), str):
            result[page["path"]] = str(page.get("status", "UNSPECIFIED"))
    return result


def page_scope(path: str, sitemap: set[str], manifest: dict[str, str]) -> tuple[str, str | None]:
    if path in manifest:
        return "CANONICAL_MANIFEST_PAGE", manifest[path]
    if path in sitemap:
        return "PUBLIC_SITEMAP_PAGE", None
    if path.endswith("-en.html"):
        return "TRACKED_LANGUAGE_OR_LEGACY_PAGE", None
    if any(token in path.lower() for token in ("audit", "archive", "legacy", "test", "debug", "reset", "refresh")):
        return "TRACKED_ARCHIVE_OR_UTILITY_PAGE", None
    return "TRACKED_NON_SITEMAP_PAGE", None


def split_sentences(value: str) -> list[str]:
    # Preserve equations and status literals while splitting long prose blocks.
    pieces = re.split(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ0-9\[])", value)
    result = []
    for piece in pieces:
        normalized = SPACE.sub(" ", piece).strip(" -\t\r\n")
        if len(normalized) >= 18:
            result.append(normalized)
    return result or ([value] if len(value) >= 18 else [])


def categories(text: str) -> list[str]:
    lower = text.casefold()
    return sorted(name for name, terms in LEXICON.items() if any(term.casefold() in lower for term in terms))


def explicit_status(text: str) -> str:
    lower = text.casefold()
    if any(term in lower for term in ("falsifiziert", "falsified")):
        return "FALSIFIED"
    if any(term in lower for term in ("not admissible", "not released", "unreleased", "blocked", "blockiert", "gesperrt", "nicht freigegeben", "nicht veröffentlicht")):
        return "BLOCKED_OR_UNRELEASED"
    if any(term in lower for term in ("not established", "not executed", "offen", "open", "pending", "ausstehend")):
        return "OPEN_OR_NOT_EXECUTED"
    if any(term in lower for term in LEXICON["CONDITIONAL_HEURISTIC"]):
        return "CONDITIONAL_OR_HEURISTIC"
    if any(term in lower for term in ("bewiesen", "proved", "theorem", "satz")):
        return "CLAIMED_PROVEN"
    if any(term in lower for term in ("numerisch bestätigt", "numerically confirmed", "numerically validated")):
        return "CLAIMED_NUMERICALLY_CONFIRMED"
    return "UNCLASSIFIED"


def score(text: str, cats: list[str], equation_like: bool) -> tuple[int, bool]:
    lower = text.casefold()
    limiter = any(term.casefold() in lower for term in EXPLICIT_LIMITERS)
    value = 0
    if any(term.casefold() in lower for term in STRONG_OVERCLAIM):
        value += 7
    if "EVIDENCE_CONFIRMATION" in cats:
        value += 4
    if "DERIVATION_IDENTIFICATION" in cats:
        value += 3
    if "THEORY_6D_PARENT" in cats:
        value += 3
    if "OBSERVATIONAL_DATA" in cats:
        value += 2
    if "PREDICTION_SIGNATURE" in cats:
        value += 2
    if "PHYSICAL_COSMOLOGY" in cats:
        value += 1
    if equation_like:
        value += 1
    if limiter:
        value -= 4
    if "CONDITIONAL_HEURISTIC" in cats:
        value -= 2
    return max(-6, value), limiter


def risk_class(value: int) -> str:
    if value >= 8:
        return "HIGH"
    if value >= 4:
        return "MEDIUM"
    if value >= 1:
        return "LOW"
    return "CONTEXT_OR_FIREWALL"


def candidate_from(block: Block, sentence: str) -> Candidate | None:
    cats = categories(sentence)
    equation_like = any(marker.casefold() in sentence.casefold() for marker in EQUATION_MARKERS)
    if not cats and not equation_like:
        return None
    # Navigation-only labels are retained only if they contain evidence or
    # derivation language; ordinary menu words are not scientific claims.
    if block.region == "nav" and not ({"EVIDENCE_CONFIRMATION", "DERIVATION_IDENTIFICATION", "THEORY_6D_PARENT"} & set(cats)):
        return None
    value, limiter = score(sentence, cats, equation_like)
    digest = hashlib.sha256(f"{block.path}\0{block.line}\0{sentence}".encode("utf-8")).hexdigest()[:16]
    return Candidate(
        claim_id=f"UL-CLAIM-CANDIDATE-{digest.upper()}",
        path=block.path,
        source_sha256=block.source_sha256,
        page_scope=block.page_scope,
        manifest_status=block.manifest_status,
        tag=block.tag,
        region=block.region,
        source_line=block.line,
        text=sentence,
        lexical_categories=cats,
        equation_like=equation_like,
        explicit_status=explicit_status(sentence),
        limiter_present=limiter,
        preliminary_risk_score=value,
        preliminary_risk_class=risk_class(value),
        adjudication_status="AUTOMATED_CANDIDATE_NOT_ADJUDICATED",
    )


def readme_candidates(root: Path) -> list[Candidate]:
    path = root / "README.md"
    if not path.is_file():
        return []
    source = path.read_bytes()
    sha = hashlib.sha256(source).hexdigest()
    result: list[Candidate] = []
    for line_number, line in enumerate(source.decode("utf-8").splitlines(), 1):
        text = SPACE.sub(" ", re.sub(r"^[#>*+\-\d.\s]+", "", line)).strip()
        if len(text) < 18:
            continue
        block = Block("README.md", sha, "PUBLIC_REPOSITORY_README", "ACTIVE", "markdown-line", "document", line_number, text)
        for sentence in split_sentences(text):
            item = candidate_from(block, sentence)
            if item:
                result.append(item)
    return result


def extract(root: Path) -> tuple[list[Candidate], dict[str, Any]]:
    sitemap = sitemap_paths(root)
    manifest = manifest_pages(root)
    paths = tracked_html(root)
    blocks: list[Block] = []
    page_index: list[dict[str, Any]] = []
    for relative in paths:
        path = root / relative
        source = path.read_bytes()
        scope, status = page_scope(relative, sitemap, manifest)
        parser = VisibleBlockParser(relative, hashlib.sha256(source).hexdigest(), scope, status)
        parser.feed(source.decode("utf-8", errors="strict"))
        # Exact duplicate blocks are common with nested div/section markup.
        seen: set[tuple[int, str]] = set()
        unique = []
        for block in parser.blocks:
            key = (block.line, block.text)
            if key not in seen:
                seen.add(key)
                unique.append(block)
        blocks.extend(unique)
        page_index.append({
            "path": relative,
            "scope": scope,
            "manifest_status": status,
            "source_sha256": hashlib.sha256(source).hexdigest(),
            "visible_blocks": len(unique),
            "sitemap_member": relative in sitemap,
            "manifest_member": relative in manifest,
        })

    candidates: dict[str, Candidate] = {}
    for block in blocks:
        for sentence in split_sentences(block.text):
            item = candidate_from(block, sentence)
            if item:
                # Deduplicate nested rendering while preserving the earliest,
                # smallest source block for a path/text pair.
                key = f"{item.path}\0{item.text}"
                previous = candidates.get(key)
                if previous is None or (item.source_line, len(item.text)) < (previous.source_line, len(previous.text)):
                    candidates[key] = item
    for item in readme_candidates(root):
        candidates[f"{item.path}\0{item.text}"] = item

    ordered = sorted(
        candidates.values(),
        key=lambda item: (-item.preliminary_risk_score, item.path, item.source_line, item.claim_id),
    )
    summary = {
        "schema": "universelab.public-scientific-claim-extraction-summary.v1",
        "status": "PASS_AUTOMATED_EXTRACTION_NOT_SCIENTIFIC_ADJUDICATION",
        "basis_commit": run_git(root, "rev-parse", "HEAD").strip(),
        "tracked_html_files": len(paths),
        "sitemap_pages": len(sitemap),
        "manifest_pages": len(manifest),
        "visible_blocks": len(blocks),
        "claim_candidates": len(ordered),
        "risk_classes": dict(Counter(item.preliminary_risk_class for item in ordered)),
        "explicit_statuses": dict(Counter(item.explicit_status for item in ordered)),
        "lexical_categories": dict(Counter(category for item in ordered for category in item.lexical_categories)),
        "page_scopes": dict(Counter(item.page_scope for item in ordered)),
        "page_index": page_index,
        "limitations": [
            "Lexical extraction cannot establish whether a scientific claim is true.",
            "Risk scores prioritize manual review and are not evidence grades.",
            "A visible qualifier may occur in another nearby block and requires contextual review.",
            "Code, tests, data and parent-theory derivations are not inferred by lexical proximity.",
        ],
        "physical_gate_effect": "NONE",
        "physical_evidence_effect": "NONE",
    }
    return ordered, summary


def write_outputs(root: Path, output_dir: Path) -> dict[str, Path]:
    candidates, summary = extract(root)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "UniverseLab_PublicScientificClaimCandidates_v1.0.json"
    summary_path = output_dir / "UniverseLab_PublicScientificClaimExtractionSummary_v1.0.json"
    tsv_path = output_dir / "UniverseLab_PublicScientificClaimCandidates_v1.0.tsv"
    json_path.write_text(json.dumps({
        "schema": "universelab.public-scientific-claim-candidates.v1",
        "status": "AUTOMATED_CANDIDATES_NOT_ADJUDICATED",
        "basis_commit": summary["basis_commit"],
        "candidates": [asdict(item) for item in candidates],
        "physical_gate_effect": "NONE",
        "physical_evidence_effect": "NONE",
    }, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    columns = [field for field in Candidate.__dataclass_fields__]
    rows = ["\t".join(columns)]
    for item in candidates:
        value = asdict(item)
        rows.append("\t".join(
            json.dumps(value[column], ensure_ascii=False) if isinstance(value[column], (list, dict, bool)) else str(value[column]).replace("\t", " ").replace("\n", " ")
            for column in columns
        ))
    tsv_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return {"candidates": json_path, "summary": summary_path, "tsv": tsv_path}


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--root", default=".")
    value.add_argument("--output-dir", default="claim-census-output")
    return value


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(list(argv) if argv is not None else None)
    try:
        root = Path(args.root).resolve()
        outputs = write_outputs(root, (root / args.output_dir).resolve())
        summary = json.loads(outputs["summary"].read_text(encoding="utf-8"))
        print(json.dumps({
            "status": summary["status"],
            "basis_commit": summary["basis_commit"],
            "tracked_html_files": summary["tracked_html_files"],
            "claim_candidates": summary["claim_candidates"],
            "risk_classes": summary["risk_classes"],
            "outputs": {key: str(path) for key, path in outputs.items()},
            "physical_gate_effect": "NONE",
            "physical_evidence_effect": "NONE",
        }, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    except (CensusError, OSError, UnicodeError, json.JSONDecodeError, AssertionError, ValueError) as exc:
        print(json.dumps({
            "status": "FAIL_CLOSED",
            "error": f"{type(exc).__name__}: {exc}",
            "physical_gate_effect": "NONE",
            "physical_evidence_effect": "NONE",
        }, ensure_ascii=False, sort_keys=True, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
