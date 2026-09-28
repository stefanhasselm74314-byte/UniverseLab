#!/usr/bin/env python3
"""Fail-closed validation of the manifest-declared UniverseLab state chain."""
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
    value = json.loads((root / rel).read_text(encoding="utf-8"))
    assert isinstance(value, dict), f"{rel} must contain an object"
    return value


def safe_repo_path(value: Any, field: str) -> Path:
    assert isinstance(value, str) and value.strip(), f"{field} must be non-empty"
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


def gate_block(value: dict[str, Any]) -> dict[str, Any]:
    for name in ("physical_governance", "gates", "governance"):
        block = value.get(name)
        if isinstance(block, dict) and ("K1-D" in block or "K1-E" in block):
            return block
    return value


def evidence_effect(value: dict[str, Any]) -> Any:
    for name in ("physical_governance", "gates", "governance"):
        block = value.get(name)
        if isinstance(block, dict) and "physical_evidence_effect" in block:
            return block["physical_evidence_effect"]
    return value.get("physical_evidence_effect")


def assert_firewalls(value: dict[str, Any], context: str) -> None:
    gates = gate_block(value)
    assert gates.get("K1-D") == "NOT_RELEASED", f"{context}: K1-D"
    assert gates.get("K1-E") == "NOT_ADMISSIBLE", f"{context}: K1-E"
    assert evidence_effect(value) == "NONE", f"{context}: physical evidence"
    checks = (
        (("ratified_human_trust_root", "RATIFIED_HUMAN_TRUST_ROOT"), "NOT_RATIFIED"),
        (("runtime_issuance_bindings", "RUNTIME_ISSUANCE_BINDINGS"), "BLOCKED"),
        (("operative_authorization_decision", "AuthorizationDecision"), "NOT_CREATED"),
        (("operative_single_use_grant", "SingleUseGrant"), "NOT_CREATED"),
        (("backend_import", "BACKEND_IMPORT"), "NOT_EXECUTED"),
        (("solver_execution", "SOLVER_EXECUTION"), "NOT_EXECUTED"),
    )
    for aliases, expected in checks:
        actual = next((gates[name] for name in aliases if name in gates), None)
        if actual is not None:
            assert actual == expected, f"{context}: {aliases[0]}={actual}"


def assert_source(root: Path, value: Any, context: str) -> None:
    rel = safe_repo_path(value, context)
    assert (root / rel).is_file(), f"missing source {context}: {rel}"


def assert_sources(root: Path, value: Any, context: str) -> None:
    assert isinstance(value, list) and value, f"{context}: sources must be non-empty"
    for source in value:
        assert_source(root, source, context)


def newest_snapshot(root: Path, token: str) -> str:
    candidates = []
    for path in (root / "registry").glob("*.json"):
        match = DATE_PREFIX.match(path.name)
        if match and token in path.name:
            candidates.append((match.group(1), path.name))
    assert candidates, f"no snapshots for {token}"
    return sorted(candidates)[-1][1]


def validate(root: Path = DEFAULT_ROOT, *, strict_source_existence: bool = False) -> None:
    root = root.resolve()
    paths = resolve_paths(root)
    alias = load_json(root, CHECKPOINT_ALIAS)
    checkpoint = load_json(root, paths.checkpoint)
    state = load_json(root, paths.current_state)
    site = load_json(root, paths.site_state)
    manifest = load_json(root, MANIFEST)

    assert (root / CHECKPOINT_ALIAS).read_bytes() == (root / paths.checkpoint).read_bytes(), "checkpoint alias must be byte-identical"
    assert alias == checkpoint
    assert checkpoint["schema"] == "universelab.session-checkpoint.v1"
    assert checkpoint["privacy_classification"] == "PUBLIC_SANITIZED"
    stamp = datetime.fromisoformat(checkpoint["timestamp"])
    assert stamp.tzinfo is not None and stamp.utcoffset() is not None
    date = stamp.date().isoformat()
    assert re.fullmatch(r"UL-CHK-\d{8}-\d{3}", checkpoint["checkpoint_id"])
    base, tree = checkpoint["basis_commit"], checkpoint["basis_tree"]
    assert SHA40.fullmatch(base) and SHA40.fullmatch(tree)

    assert state["schema"] == "universelab.current-main-canonical-state.v1"
    assert state["snapshot_date"] == date
    assert state["basis_main_commit"] == base and state["basis_main_tree"] == tree
    assert state["supersedes"] != paths.current_state.as_posix()
    rule = state.get("authority_rule") or state.get("authority") or {}
    assert rule["open_pull_requests_have_canonical_effect"] is False
    assert rule["historical_snapshots_are_append_only"] is True
    assert state["active_program"]["gate"] == "FM-G0"
    assert state["active_program"]["gate_status"] == "OPEN"
    assert state["active_program"]["blocking_gap_count"] == 10
    assert state["active_program"]["partially_resolved_blocking_gap_count"] == 3
    assert state["active_program"]["fully_unresolved_blocking_gap_count"] == 7
    assert state["physical_governance"]["solver_authorized"] is False
    assert state["physical_governance"]["physical_background"] == "NOT_ESTABLISHED"
    assert state["physical_governance"]["physical_response_rank"] == "NOT_EXECUTED"
    assert state["physical_gate_effect"] == "NONE"
    assert_firewalls(state, "current state")

    assert site["schema"] == "universelab.site-state.v1"
    assert site["snapshot_date"] == date
    assert site["basis_main_commit"] == base and site["basis_main_tree"] == tree
    assert site["canonical_state"] == paths.current_state.as_posix()
    assert site["supersedes"] != paths.site_state.as_posix()
    assert site["governance"]["open_pull_requests_have_canonical_effect"] is False
    assert site["governance"]["historical_snapshots_are_append_only"] is True
    assert site["physical_gate_effect"] == "NONE"
    assert_firewalls(site, "site state")
    modules = {item["module_id"]: item for item in site["modules"]}
    assert {"ULSH-01", "HZT-M0-FM0", "PUBLIC-COSMOLOGY"} <= set(modules)
    ulsh = modules["ULSH-01"]
    assert ulsh["technical"]["background_execution"] == "NOT_AUTHORIZED"
    assert ulsh["technical"]["physical_response_rank"] == "NOT_EXECUTED"
    assert ulsh["technical"]["backend_import"] == "NOT_EXECUTED"
    assert ulsh["governance"]["solver_release"] == "NOT_AUTHORIZED"
    assert ulsh["scientific"]["physical_background"] == "NOT_ESTABLISHED"
    assert ulsh["release_gate"]["status"] == "NOT_SATISFIED"
    assert {item["id"]: item["status"] for item in ulsh["work_packages"]} == {
        "WP1": "CLOSED_TARGET_FROZEN_NO_EXECUTION",
        "WP2": "METHOD_AUTHORITY_PREPARATION_IMPLEMENTED_NOT_AUTHORIZED",
        "WP3": "NOT_STARTED",
        "WP4": "BLOCKED_NOT_AUTHORIZED",
    }
    fm0 = modules["HZT-M0-FM0"]
    assert fm0["technical"]["blocking_gap_count"] == 10
    assert fm0["technical"]["partially_resolved_blocking_gap_count"] == 3
    assert fm0["technical"]["fully_unresolved_blocking_gap_count"] == 7
    assert fm0["governance"]["gate"] == "FM-G0" and fm0["governance"]["gate_status"] == "OPEN"

    assert checkpoint["canonical_snapshot"] == paths.checkpoint.as_posix()
    assert checkpoint["canonical_state"] == paths.current_state.as_posix()
    assert checkpoint["site_state"] == paths.site_state.as_posix()
    assert checkpoint["physical_gate_effect"] == "NONE"
    assert checkpoint["physical_evidence_effect"] == "NONE"
    for field in ("current_goal", "current_workstream", "next_exact_action"):
        assert isinstance(checkpoint.get(field), str) and checkpoint[field].strip(), f"checkpoint missing {field}"
    for field in ("verified_results", "open_blockers", "active_assumptions", "forbidden_inferences", "entry_points"):
        assert isinstance(checkpoint.get(field), list) and checkpoint[field], f"checkpoint {field} empty"
    assert_firewalls(checkpoint, "checkpoint")

    assert manifest["release_date"] == date
    assert manifest["basis_main_commit"] == base and manifest["basis_main_tree"] == tree
    assert manifest["canonical_state"] == paths.current_state.as_posix()
    assert manifest["site_state"] == paths.site_state.as_posix()
    assert manifest["session_checkpoint"] == paths.checkpoint.as_posix()
    assert manifest["gates"]["FM-G0"] == "OPEN"
    assert manifest["gates"]["FM0_BLOCKING_GAPS"] == 10
    assert manifest["gates"]["official_MD2S_solver"] == "NOT_AUTHORIZED"
    assert manifest["c_phys_operator_entry"]["solver_authorized"] is False
    registries = manifest["central_registries"]
    assert registries["current_main_canonical_state"] == paths.current_state.as_posix()
    assert registries["site_state"] == paths.site_state.as_posix()
    assert registries["session_checkpoint"] == paths.checkpoint.as_posix()
    assert registries["session_checkpoint_alias"] == CHECKPOINT_ALIAS.as_posix()
    platform = manifest["platform_governance"]
    assert platform["version"] == "1.2.0"
    assert platform["status"] == "ACTIVE_GOVERNED_PLATFORM_CURRENT_STATE_RECONCILED_2026_09_03"
    assert platform["navigator_authority"] == "CANONICAL_DIRECT_DOCUMENT"
    assert platform["site_state"] == paths.site_state.as_posix()
    assert platform["physical_gate_effect"] == "NONE"
    assert platform["status_axes_rule"] == "TECHNICAL_GOVERNANCE_SCIENTIFIC_ARE_INDEPENDENT"
    assert manifest["physical_gate_effect"] == "NONE"
    assert_firewalls(manifest, "project manifest")

    de = (root / RESEARCH_STATUS_DE).read_text(encoding="utf-8")
    en = (root / RESEARCH_STATUS_EN).read_text(encoding="utf-8")
    for html in (de, en):
        assert paths.current_state.as_posix() in html
        assert "K1-D" in html and "NOT RELEASED" in html
        assert "K1-E" in html and "NOT ADMISSIBLE" in html
    assert "Offene Pull Requests besitzen keine kanonische Wirkung" in de
    assert "Open pull requests have no canonical effect" in en
    assert 'data-ul-export-title="UniverseLab Forschungsstatus"' in de
    assert 'data-ul-export-filename="UniverseLab-Forschungsstatus"' in de
    assert 'data-ul-export-page-breaks="off"' in de

    shell = (root / GLOBAL_SHELL).read_text(encoding="utf-8")
    assert paths.site_state.as_posix() in shell
    assert "registry/2026-08-16_UniverseLab_SiteState_v1.0.json" not in shell
    platform_workflow = (root / PLATFORM_WORKFLOW).read_text(encoding="utf-8")
    assert "manifest['site_state']" in platform_workflow or 'manifest["site_state"]' in platform_workflow
    assert "registry/2026-09-01_UniverseLab_SiteState_v1.1.json" not in platform_workflow
    assert "2026-09-01_validate_UniverseLab_CurrentMainCanonicalStateReconciliation_v1.0.py" in (root / G0_WORKFLOW).read_text(encoding="utf-8")

    for token, expected in {
        "CurrentMainCanonicalState": paths.current_state.name,
        "UniverseLab_SiteState": paths.site_state.name,
        "UniverseLab_SessionCheckpoint": paths.checkpoint.name,
    }.items():
        assert newest_snapshot(root, token) == expected, f"{expected} is not newest {token}"

    if strict_source_existence:
        for label, source in state.get("status_sources", {}).items():
            assert_source(root, source, f"state.status_sources.{label}")
        for label, source in site.get("status_sources", {}).items():
            assert_source(root, source, f"site.status_sources.{label}")
        for label, source in manifest.get("current_status_sources", {}).items():
            assert_source(root, source, f"manifest.current_status_sources.{label}")
        for index, result in enumerate(checkpoint["verified_results"]):
            assert_sources(root, result.get("sources"), f"checkpoint.verified_results[{index}]")
        for index, blocker in enumerate(checkpoint["open_blockers"]):
            assert_sources(root, blocker.get("sources"), f"checkpoint.open_blockers[{index}]")
        for index, source in enumerate(checkpoint["entry_points"]):
            assert_source(root, source, f"checkpoint.entry_points[{index}]")

    print(f"UniverseLab current-main canonical state reconciliation: PASS ({paths.current_state}, {paths.site_state}, {paths.checkpoint})")


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--strict-source-existence", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    validate(args.root, strict_source_existence=args.strict_source_existence)


if __name__ == "__main__":
    main()
