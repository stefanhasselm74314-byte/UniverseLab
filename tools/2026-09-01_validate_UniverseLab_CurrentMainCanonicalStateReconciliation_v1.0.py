#!/usr/bin/env python3
"""Fail-closed QA for the active UniverseLab current-main state chain.

Historical dated snapshots remain immutable.  The active chain is resolved
from registry/session-checkpoint-latest.json and must agree with the project
manifest, the public SiteState and the canonical state.  No open pull request
is treated as merged canon by this validator.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Iterable

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT_ALIAS = Path("registry/session-checkpoint-latest.json")
MANIFEST = Path("project-manifest.json")
RESEARCH_STATUS_DE = Path("research-status.html")
RESEARCH_STATUS_EN = Path("research-status-en.html")
GLOBAL_SHELL = Path("assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js")
PLATFORM_WORKFLOW = Path(".github/workflows/2026-08-16_UniverseLab_PlatformGovernance_v1.1.yml")
G0_WORKFLOW = Path(".github/workflows/2026-08-03_UniverseLab_G0_ThreeTrackContract_v1.0.yml")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
DATE_PREFIX = re.compile(r"^(\d{4}-\d{2}-\d{2})")


@dataclass(frozen=True)
class ActivePaths:
    checkpoint: Path
    current_state: Path
    site_state: Path


def load_json(root: Path, rel: Path) -> dict[str, Any]:
    path = root / rel
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"{rel} must contain a JSON object")
    return value


def safe_repo_path(value: Any, field: str) -> Path:
    assert isinstance(value, str) and value.strip(), f"{field} must be a non-empty repository path"
    pure = PurePosixPath(value)
    assert not pure.is_absolute() and ".." not in pure.parts, f"unsafe {field}: {value}"
    return Path(pure.as_posix())


def resolve_paths(root: Path = DEFAULT_ROOT) -> ActivePaths:
    alias = load_json(root, CHECKPOINT_ALIAS)
    return ActivePaths(
        checkpoint=safe_repo_path(alias.get("canonical_snapshot"), "canonical_snapshot"),
        current_state=safe_repo_path(alias.get("canonical_state"), "canonical_state"),
        site_state=safe_repo_path(alias.get("site_state"), "site_state"),
    )


def evidence_effect(obj: dict[str, Any]) -> Any:
    for block_name in ("physical_governance", "gates", "governance"):
        block = obj.get(block_name)
        if isinstance(block, dict) and "physical_evidence_effect" in block:
            return block["physical_evidence_effect"]
    return obj.get("physical_evidence_effect")


def gate_block(obj: dict[str, Any]) -> dict[str, Any]:
    for block_name in ("physical_governance", "gates", "governance"):
        block = obj.get(block_name)
        if isinstance(block, dict) and ("K1-D" in block or "K1-E" in block):
            return block
    return obj


def assert_firewalls(obj: dict[str, Any], *, context: str) -> None:
    block = gate_block(obj)
    assert block.get("K1-D") == "NOT_RELEASED", f"{context}: K1-D promotion detected"
    assert block.get("K1-E") == "NOT_ADMISSIBLE", f"{context}: K1-E promotion detected"
    assert evidence_effect(obj) == "NONE", f"{context}: physical evidence effect must remain NONE"

    trust = block.get("ratified_human_trust_root", block.get("RATIFIED_HUMAN_TRUST_ROOT"))
    if trust is not None:
        assert trust == "NOT_RATIFIED", f"{context}: trust-root ratification detected"
    runtime = block.get("runtime_issuance_bindings", block.get("RUNTIME_ISSUANCE_BINDINGS"))
    if runtime is not None:
        assert runtime == "BLOCKED", f"{context}: runtime issuance unexpectedly open"
    decision = block.get("operative_authorization_decision", block.get("AuthorizationDecision"))
    if decision is not None:
        assert decision == "NOT_CREATED", f"{context}: AuthorizationDecision unexpectedly exists"
    grant = block.get("operative_single_use_grant", block.get("SingleUseGrant"))
    if grant is not None:
        assert grant == "NOT_CREATED", f"{context}: SingleUseGrant unexpectedly exists"
    backend = block.get("backend_import", block.get("BACKEND_IMPORT"))
    if backend is not None:
        assert backend == "NOT_EXECUTED", f"{context}: backend import unexpectedly executed"
    solver = block.get("solver_execution", block.get("SOLVER_EXECUTION"))
    if solver is not None:
        assert solver == "NOT_EXECUTED", f"{context}: solver unexpectedly executed"


def assert_source(root: Path, value: Any, *, context: str) -> None:
    rel = safe_repo_path(value, context)
    assert (root / rel).is_file(), f"missing source {context}: {rel}"


def assert_source_list(root: Path, value: Any, *, context: str) -> None:
    assert isinstance(value, list) and value, f"{context}: sources must be a non-empty list"
    for source in value:
        assert_source(root, source, context=context)


def newest_dated_snapshot(root: Path, token: str) -> str:
    candidates: list[tuple[str, str]] = []
    for path in (root / "registry").glob("*.json"):
        if token not in path.name:
            continue
        match = DATE_PREFIX.match(path.name)
        if match:
            candidates.append((match.group(1), path.name))
    assert candidates, f"No dated snapshots found for {token}"
    return sorted(candidates)[-1][1]


def validate(root: Path = DEFAULT_ROOT, *, strict_source_existence: bool = False) -> None:
    root = root.resolve()
    paths = resolve_paths(root)
    alias = load_json(root, CHECKPOINT_ALIAS)
    checkpoint = load_json(root, paths.checkpoint)
    state = load_json(root, paths.current_state)
    site = load_json(root, paths.site_state)
    manifest = load_json(root, MANIFEST)

    assert (root / CHECKPOINT_ALIAS).read_bytes() == (root / paths.checkpoint).read_bytes(), (
        "session-checkpoint-latest.json must be byte-identical to its declared canonical_snapshot"
    )
    assert alias == checkpoint

    assert checkpoint.get("schema") == "universelab.session-checkpoint.v1"
    assert checkpoint.get("privacy_classification") == "PUBLIC_SANITIZED"
    timestamp = datetime.fromisoformat(str(checkpoint.get("timestamp", "")))
    assert timestamp.tzinfo is not None and timestamp.utcoffset() is not None, "checkpoint timestamp needs a timezone"
    date = timestamp.date().isoformat()
    assert checkpoint.get("checkpoint_id") and re.fullmatch(r"UL-CHK-\d{8}-\d{3}", checkpoint["checkpoint_id"])

    base_commit = checkpoint.get("basis_commit")
    base_tree = checkpoint.get("basis_tree")
    assert isinstance(base_commit, str) and SHA40.fullmatch(base_commit), "invalid checkpoint basis_commit"
    assert isinstance(base_tree, str) and SHA40.fullmatch(base_tree), "invalid checkpoint basis_tree"

    assert state.get("schema") == "universelab.current-main-canonical-state.v1"
    assert state.get("snapshot_date") == date
    assert state.get("basis_main_commit") == base_commit
    assert state.get("basis_main_tree") == base_tree
    assert state.get("supersedes") and state["supersedes"] != paths.current_state.as_posix()
    authority_rule = state.get("authority_rule") or state.get("authority") or {}
    assert authority_rule.get("open_pull_requests_have_canonical_effect") is False
    assert authority_rule.get("historical_snapshots_are_append_only") is True
    assert state["physical_governance"]["solver_authorized"] is False
    assert state["physical_governance"]["physical_background"] == "NOT_ESTABLISHED"
    assert state["physical_governance"]["physical_response_rank"] == "NOT_EXECUTED"
    assert state["active_program"]["gate"] == "FM-G0"
    assert state["active_program"]["gate_status"] == "OPEN"
    assert state["active_program"]["blocking_gap_count"] == 10
    assert state["active_program"]["partially_resolved_blocking_gap_count"] == 3
    assert state["active_program"]["fully_unresolved_blocking_gap_count"] == 7
    assert state.get("physical_gate_effect") == "NONE"
    assert state.get("physical_evidence_effect") == "NONE"
    assert_firewalls(state, context="current state")

    assert site.get("schema") == "universelab.site-state.v1"
    assert site.get("snapshot_date") == date
    assert site.get("basis_main_commit") == base_commit
    assert site.get("basis_main_tree") == base_tree
    assert site.get("canonical_state") == paths.current_state.as_posix()
    assert site.get("supersedes") and site["supersedes"] != paths.site_state.as_posix()
    assert site["governance"]["open_pull_requests_have_canonical_effect"] is False
    assert site["governance"]["historical_snapshots_are_append_only"] is True
    assert site.get("physical_gate_effect") == "NONE"
    assert_firewalls(site, context="site state")
    modules = {module["module_id"]: module for module in site.get("modules", [])}
    assert {"ULSH-01", "HZT-M0-FM0", "PUBLIC-COSMOLOGY"} <= set(modules)
    ulsh = modules["ULSH-01"]
    assert ulsh["technical"]["background_execution"] == "NOT_AUTHORIZED"
    assert ulsh["technical"]["physical_response_rank"] == "NOT_EXECUTED"
    assert ulsh["technical"]["backend_import"] == "NOT_EXECUTED"
    assert ulsh["governance"]["solver_release"] == "NOT_AUTHORIZED"
    assert ulsh["scientific"]["physical_background"] == "NOT_ESTABLISHED"
    assert ulsh["release_gate"]["status"] == "NOT_SATISFIED"
    work_packages = {item["id"]: item["status"] for item in ulsh["work_packages"]}
    assert work_packages == {
        "WP1": "CLOSED_TARGET_FROZEN_NO_EXECUTION",
        "WP2": "METHOD_AUTHORITY_PREPARATION_IMPLEMENTED_NOT_AUTHORIZED",
        "WP3": "NOT_STARTED",
        "WP4": "BLOCKED_NOT_AUTHORIZED",
    }
    fm0 = modules["HZT-M0-FM0"]
    assert fm0["technical"]["blocking_gap_count"] == 10
    assert fm0["technical"]["partially_resolved_blocking_gap_count"] == 3
    assert fm0["technical"]["fully_unresolved_blocking_gap_count"] == 7
    assert fm0["governance"]["gate"] == "FM-G0"
    assert fm0["governance"]["gate_status"] == "OPEN"
    assert fm0["release_gate"]["status"] == "NOT_SATISFIED"

    assert checkpoint.get("canonical_snapshot") == paths.checkpoint.as_posix()
    assert checkpoint.get("canonical_state") == paths.current_state.as_posix()
    assert checkpoint.get("site_state") == paths.site_state.as_posix()
    assert checkpoint.get("basis_commit") == base_commit
    assert checkpoint.get("basis_tree") == base_tree
    assert checkpoint.get("physical_gate_effect") == "NONE"
    assert checkpoint.get("physical_evidence_effect") == "NONE"
    for field in ("current_goal", "current_workstream", "next_exact_action"):
        assert isinstance(checkpoint.get(field), str) and checkpoint[field].strip(), f"checkpoint missing {field}"
    for field in ("verified_results", "open_blockers", "active_assumptions", "forbidden_inferences", "entry_points"):
        assert isinstance(checkpoint.get(field), list) and checkpoint[field], f"checkpoint {field} must be non-empty"
    assert_firewalls(checkpoint, context="checkpoint")

    assert manifest.get("release_date") == date
    assert manifest.get("basis_main_commit") == base_commit
    assert manifest.get("basis_main_tree") == base_tree
    assert manifest.get("canonical_state") == paths.current_state.as_posix()
    assert manifest.get("site_state") == paths.site_state.as_posix()
    assert manifest.get("session_checkpoint") == paths.checkpoint.as_posix()
    assert manifest["gates"]["FM-G0"] == "OPEN"
    assert manifest["gates"]["FM0_BLOCKING_GAPS"] == 10
    assert manifest["gates"]["official_MD2S_solver"] == "NOT_AUTHORIZED"
    assert manifest["c_phys_operator_entry"]["solver_authorized"] is False
    registries = manifest.get("central_registries", {})
    if registries:
        assert registries["current_main_canonical_state"] == paths.current_state.as_posix()
        assert registries["site_state"] == paths.site_state.as_posix()
        assert registries["session_checkpoint"] == paths.checkpoint.as_posix()
        assert registries["session_checkpoint_alias"] == CHECKPOINT_ALIAS.as_posix()
    platform = manifest["platform_governance"]
    assert platform["status"] == "ACTIVE_GOVERNED_PLATFORM_V1_CURRENT_STATE_RECONCILED"
    assert platform["navigator_authority"] == "CANONICAL_DIRECT_DOCUMENT"
    assert platform["site_state"] == paths.site_state.as_posix()
    assert platform["physical_gate_effect"] == "NONE"
    assert platform["status_axes_rule"] == "TECHNICAL_GOVERNANCE_SCIENTIFIC_ARE_INDEPENDENT"
    assert manifest.get("physical_gate_effect") == "NONE"
    assert_firewalls(manifest, context="project manifest")

    html_de = (root / RESEARCH_STATUS_DE).read_text(encoding="utf-8")
    html_en = (root / RESEARCH_STATUS_EN).read_text(encoding="utf-8")
    assert paths.current_state.as_posix() in html_de and paths.current_state.as_posix() in html_en
    assert "Offene Pull Requests besitzen keine kanonische Wirkung" in html_de
    assert "Open pull requests have no canonical effect" in html_en
    assert "K1-D" in html_de and "NOT RELEASED" in html_de
    assert "K1-E" in html_de and "NOT ADMISSIBLE" in html_de
    assert "K1-D" in html_en and "NOT RELEASED" in html_en
    assert "K1-E" in html_en and "NOT ADMISSIBLE" in html_en
    assert 'data-ul-export-title="UniverseLab Forschungsstatus"' in html_de
    assert 'data-ul-export-filename="UniverseLab-Forschungsstatus"' in html_de
    assert 'data-ul-export-page-breaks="off"' in html_de

    shell = (root / GLOBAL_SHELL).read_text(encoding="utf-8")
    assert paths.site_state.as_posix() in shell
    assert "registry/2026-08-16_UniverseLab_SiteState_v1.0.json" not in shell

    platform_workflow = (root / PLATFORM_WORKFLOW).read_text(encoding="utf-8")
    assert "manifest['site_state']" in platform_workflow or 'manifest["site_state"]' in platform_workflow
    assert "registry/2026-09-01_UniverseLab_SiteState_v1.1.json" not in platform_workflow
    g0_workflow = (root / G0_WORKFLOW).read_text(encoding="utf-8")
    assert "2026-09-01_validate_UniverseLab_CurrentMainCanonicalStateReconciliation_v1.0.py" in g0_workflow

    families = {
        "CurrentMainCanonicalState": paths.current_state.name,
        "UniverseLab_SiteState": paths.site_state.name,
        "UniverseLab_SessionCheckpoint": paths.checkpoint.name,
    }
    for token, expected in families.items():
        assert newest_dated_snapshot(root, token) == expected, f"{expected} is not newest {token} snapshot"

    if strict_source_existence:
        for label, source in state.get("status_sources", {}).items():
            assert_source(root, source, context=f"state.status_sources.{label}")
        for label, source in site.get("status_sources", {}).items():
            assert_source(root, source, context=f"site.status_sources.{label}")
        for label, source in manifest.get("current_status_sources", {}).items():
            assert_source(root, source, context=f"manifest.current_status_sources.{label}")
        for index, result in enumerate(checkpoint["verified_results"]):
            assert_source_list(root, result.get("sources"), context=f"checkpoint.verified_results[{index}]")
        for index, blocker in enumerate(checkpoint["open_blockers"]):
            assert_source_list(root, blocker.get("sources"), context=f"checkpoint.open_blockers[{index}]")
        for index, source in enumerate(checkpoint["entry_points"]):
            assert_source(root, source, context=f"checkpoint.entry_points[{index}]")

    print(
        "UniverseLab current-main canonical state reconciliation: PASS "
        f"({paths.current_state}, {paths.site_state}, {paths.checkpoint})"
    )


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--strict-source-existence", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    validate(args.root.resolve(), strict_source_existence=args.strict_source_existence)


if __name__ == "__main__":
    main()
