#!/usr/bin/env python3
"""Fail-closed validator for the post-migration UniverseLab current-main reconciliation."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-01"
BASIS_MAIN = "2f03998fbb36185123fc02f4fd3cb1df5749834a"
STATE = Path("registry/2026-09-01_UniverseLab_CurrentMainCanonicalState_v1.1.json")
SITE = Path("registry/2026-09-01_UniverseLab_SiteState_v1.2.json")
SCHEMA = Path("schemas/2026-09-01_UniverseLab_SiteStateSchema_v1.2.json")
CHECKPOINT = Path("registry/2026-09-01_UniverseLab_SessionCheckpoint_v1.32.json")
CHECKPOINT_ALIAS = Path("registry/session-checkpoint-latest.json")
CLOSURE = Path("registry/2026-09-01_UniverseLab_CanonicalCosmologyPublicMigrationClosure_v1.0.json")
ENGINE_CONTRACT = Path("registry/2026-09-01_UniverseLab_CanonicalCosmologyEngineContract_v1.0.json")
MANIFEST = Path("project-manifest.json")
RESEARCH_STATUS = Path("research-status.html")


def load_json(root: Path, rel: Path) -> dict[str, Any]:
    path = root / rel
    assert path.is_file(), f"missing JSON artifact: {rel}"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{rel} must contain a JSON object"
    return data


def assert_firewalls(obj: dict[str, Any], *, context: str) -> None:
    physical = obj.get("physical_governance", obj.get("gate_state", obj.get("governance", obj)))
    assert physical.get("K1-D") == "NOT_RELEASED", f"{context}: K1-D promotion detected"
    assert physical.get("K1-E") == "NOT_ADMISSIBLE", f"{context}: K1-E promotion detected"
    evidence = physical.get("physical_evidence_effect", obj.get("physical_evidence_effect"))
    assert evidence == "NONE", f"{context}: physical evidence effect must remain NONE"
    assert obj.get("physical_gate_effect", "NONE") == "NONE", f"{context}: physical gate effect must remain NONE"


def assert_source_paths(root: Path, mapping: dict[str, Any], *, context: str) -> None:
    for label, value in mapping.items():
        if not isinstance(value, str):
            continue
        if value.startswith(("http://", "https://")):
            continue
        candidate = root / value
        assert candidate.exists(), f"{context}: missing source {label}: {value}"


def validate(root: Path = DEFAULT_ROOT) -> None:
    state = load_json(root, STATE)
    site = load_json(root, SITE)
    schema = load_json(root, SCHEMA)
    checkpoint = load_json(root, CHECKPOINT)
    alias = load_json(root, CHECKPOINT_ALIAS)
    closure = load_json(root, CLOSURE)
    engine = load_json(root, ENGINE_CONTRACT)
    manifest = load_json(root, MANIFEST)

    # Canonical basis and version chain.
    assert state["version"] == "1.1.0"
    assert state["snapshot_date"] == DATE
    assert state["basis_main_commit"] == BASIS_MAIN
    assert state["supersedes"].endswith("CurrentMainCanonicalState_v1.0.json")
    assert site["version"] == "1.2.0"
    assert site["snapshot_date"] == DATE
    assert site["basis_main_commit"] == BASIS_MAIN
    assert site["canonical_state"] == STATE.as_posix()
    assert site["schema_contract"] == SCHEMA.as_posix()
    assert schema["$id"] == "universelab.site-state.v1.2"
    assert schema["properties"]["version"]["const"] == "1.2.0"
    assert checkpoint["checkpoint_id"] == "UL-CHK-20260901-032"
    assert checkpoint["basis_commit"] == BASIS_MAIN
    assert checkpoint["canonical_state"] == STATE.as_posix()
    assert checkpoint["site_state"] == SITE.as_posix()
    assert checkpoint["canonical_snapshot"] == CHECKPOINT.as_posix()

    dated_bytes = (root / CHECKPOINT).read_bytes()
    alias_bytes = (root / CHECKPOINT_ALIAS).read_bytes()
    assert dated_bytes == alias_bytes, "session-checkpoint-latest.json must be byte-identical to v1.32"
    assert alias == checkpoint

    # Public numerical migration closure.
    assert closure["basis_main_commit"] == BASIS_MAIN
    assert closure["status"] == "MERGED_MAIN_TECHNICAL_CLOSURE"
    assert closure["scope"]["migration_status"] == "COMPLETE_FOR_DECLARED_PUBLIC_SET"
    assert closure["scope"]["remaining_independent_public_cosmology_engines_in_declared_set"] == []
    assert closure["scope"]["canonical_engine_api_version"] == "1.0.0"
    assert closure["scope"]["canonical_engine_implementation_revision"] == "1.0.1"
    prs = closure["merged_pull_requests"]
    assert [row["number"] for row in prs] == [196, 197, 198, 199, 200, 201]
    assert all(row["status"] == "MERGED" for row in prs)
    assert closure["qa_closure"]["open_review_threads_at_merge"] == 0
    assert closure["qa_closure"]["regular_exact_head_workflows"] == "SUCCESS"
    assert closure["scientific_status_effect"]["FM-G0"] == "OPEN"
    assert_firewalls(closure, context="migration closure")

    # Engine contract is numerical infrastructure only.
    assert engine["engine"]["api_version"] == "1.0.0"
    assert engine["engine"]["implementation_revision"] == "1.0.1"
    assert engine["growth_reference"]["endpoint"] == "EXACT_X_0_A_1"
    assert engine["models"]["bridge"]["growth"] == "UNRELEASED_GROWTH_MAP"
    assert engine["fail_closed_domain_rules"]["floors_for_negative_E2"] is False
    assert engine["physical_gate_effect"] == "NONE"
    assert engine["physical_evidence_effect"] == "NONE"

    # Program and FM-0 remain open and unchanged by UI/numerics work.
    program = state["program"]
    assert program["active_workstream"] == "WS1"
    assert program["active_work_package"] == "FM-0"
    assert program["gate"] == "FM-G0"
    assert program["gate_status"] == "OPEN"
    assert program["blocking_gap_count"] == 10
    assert program["fully_unresolved_blocking_gap_count"] == 7
    assert program["partially_resolved_blocking_gap_count"] == 3
    assert state["fm0"]["effective_identifiability"]["implemented_combination"] == "beta_tau * I_B"
    assert "<= 1" in state["fm0"]["effective_identifiability"]["structural_rank_bound"]

    # Physical execution remains forbidden.
    pg = state["physical_governance"]
    assert pg["ULSH-01-WP1"] == "CLOSED_TARGET_FROZEN_NO_EXECUTION"
    assert pg["ULSH-01-WP2"] == "READY_FOR_SEPARATE_AUTHORIZATION_DECISION_NOT_AUTHORIZED"
    assert pg["ULSH-01-WP3"] == "NOT_STARTED"
    assert pg["ULSH-01-WP4"] == "BLOCKED_NOT_AUTHORIZED"
    assert pg["CP01R4"] == "METHOD_FROZEN_NO_EXECUTION"
    assert pg["operative_authorization_decision"] == "NOT_CREATED"
    assert pg["operative_single_use_grant"] == "NOT_CREATED"
    assert pg["backend_import"] == "NOT_EXECUTED"
    assert pg["solver_execution"] == "NOT_EXECUTED"
    assert pg["solver_authorized"] is False
    assert pg["physical_background"] == "NOT_ESTABLISHED"
    assert pg["physical_response_rank"] == "NOT_EXECUTED"
    assert_firewalls(state, context="canonical state")
    assert_firewalls(site, context="site state")
    assert_firewalls(checkpoint, context="checkpoint")

    # Page status reconciliation.
    page_status = {row["path"]: row["status"] for row in site["pages"]}
    expected_pages = {
        "validation.html": "ACTIVE_CANONICAL_COSMOLOGY_ENGINE",
        "validation-en.html": "ACTIVE_CANONICAL_COSMOLOGY_ENGINE",
        "observatory.html": "ACTIVE_CANONICAL_COSMOLOGY_ENGINE",
        "compare-safe.html": "ACTIVE_CANONICAL_COSMOLOGY_ENGINE",
        "compare.html": "CONSOLIDATED_CANONICAL_ROUTE",
        "compare-direct.html": "CONSOLIDATED_CANONICAL_ROUTE",
        "emergence.html": "ACTIVE_CANONICAL_BACKGROUND_AND_GROWTH_ADAPTER",
        "emergence-en.html": "ACTIVE_CANONICAL_BACKGROUND_AND_GROWTH_ADAPTER",
    }
    for path, expected in expected_pages.items():
        assert page_status.get(path) == expected, (path, page_status.get(path), expected)
        assert (root / path).exists(), f"registered page missing: {path}"
    assert len(page_status) == len(site["pages"]), "duplicate SiteState page paths"

    # Manifest is the current compact entry point and must not carry pre-migration labels.
    assert manifest["release_date"] == DATE
    assert manifest["basis_main_commit"] == BASIS_MAIN
    assert manifest["canonical_state"] == STATE.as_posix()
    assert manifest["site_state"] == SITE.as_posix()
    assert manifest["site_state_schema"] == SCHEMA.as_posix()
    assert manifest["session_checkpoint"] == CHECKPOINT.as_posix()
    assert manifest["session_checkpoint_alias"] == CHECKPOINT_ALIAS.as_posix()
    assert manifest["public_numerics_closure"] == CLOSURE.as_posix()
    assert manifest["public_cosmology_engine"]["migration_status"] == "COMPLETE_FOR_DECLARED_PUBLIC_SET"
    assert manifest["public_cosmology_engine"]["remaining_independent_public_cosmology_engines"] == 0
    assert manifest["gates"]["FM-G0"] == "OPEN"
    assert manifest["gates"]["FM0_BLOCKING_GAPS"] == 10
    assert manifest["gates"]["official_MD2S_solver"] == "NOT_AUTHORIZED"
    assert_firewalls(manifest, context="project manifest")
    manifest_text = (root / MANIFEST).read_text(encoding="utf-8")
    for stale in (
        "ACTIVE_DIAGNOSTIC_PENDING_ENGINE_RECONCILIATION",
        "ACTIVE_DIAGNOSTIC_PENDING_NUMERICAL_RECONCILIATION",
    ):
        assert stale not in manifest_text, f"stale pre-migration page status remains: {stale}"

    # PR #137 remains explicitly noncanonical.
    for obj, context in ((state, "state"), (checkpoint, "checkpoint"), (manifest, "manifest")):
        row = next(item for item in obj["open_noncanonical_work"] if item["pull_request"] == 137)
        assert row["state"] == "OPEN_DRAFT"
        assert row["canonical_effect"].startswith("NONE_"), f"{context}: PR137 canonical promotion detected"

    # Public status page must bind to the new state and preserve the no-evidence interpretation.
    html = (root / RESEARCH_STATUS).read_text(encoding="utf-8")
    for token in (
        "1. September 2026",
        BASIS_MAIN[:12],
        STATE.as_posix(),
        SITE.as_posix(),
        CHECKPOINT.as_posix(),
        CLOSURE.as_posix(),
        "Offene Pull Requests besitzen keine kanonische Wirkung",
        "K1-D",
        "NOT RELEASED",
        "K1-E",
        "NOT ADMISSIBLE",
        "FM-G0",
        "TECHNISCH GESCHLOSSEN",
        "Physical evidence effect: NONE",
        'data-ul-export-title=',
        'data-ul-export-filename=',
        'data-ul-export-page-breaks="off"',
    ):
        assert token in html, f"research-status missing token: {token}"
    for stale_path in (
        "CurrentMainCanonicalState_v1.0.json",
        "SiteState_v1.1.json",
        "SessionCheckpoint_v1.31.json",
    ):
        assert stale_path not in html, f"research-status still binds stale source: {stale_path}"

    # Memory protocol compatibility and next-action firewall.
    for key in (
        "current_goal", "current_workstream", "current_workstreams", "gate_state",
        "verified_results", "open_blockers", "active_assumptions", "forbidden_inferences",
        "entry_points", "next_exact_action",
    ):
        assert key in checkpoint, f"checkpoint missing memory-protocol field: {key}"
    assert checkpoint["next_exact_action"].endswith("do not execute CP01R4, a physical background solve or a physical response-rank run.")
    assert all("source" in row for row in checkpoint["verified_results"])
    assert all("source" in row for row in checkpoint["open_blockers"])

    # Every registered local source must exist in the repository.
    assert_source_paths(root, state["status_sources"], context="canonical state")
    assert_source_paths(root, site["status_sources"], context="site state")
    assert_source_paths(root, manifest["central_registries"], context="manifest central registries")
    assert_source_paths(root, checkpoint["entry_points"], context="checkpoint entry points")

    # Dated snapshot family monotonicity.
    registry = root / "registry"
    families = {
        "CurrentMainCanonicalState": STATE.name,
        "UniverseLab_SiteState": SITE.name,
        "UniverseLab_SessionCheckpoint": CHECKPOINT.name,
    }
    for token, expected in families.items():
        names = [path.name for path in registry.glob("*.json") if token in path.name]
        assert expected in names, f"missing current snapshot family member: {expected}"
        dated = sorted(name for name in names if re.match(r"^\d{4}-\d{2}-\d{2}_", name))
        assert dated, f"no dated snapshots found for {token}"

    print("UniverseLab post-migration current-main reconciliation: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    validate(args.root.resolve())


if __name__ == "__main__":
    main()
