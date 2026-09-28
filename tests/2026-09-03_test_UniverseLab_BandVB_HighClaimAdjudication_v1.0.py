#!/usr/bin/env python3
"""Band V-B HIGH historical adjudication + current-corpus regression gate."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ALIAS = ROOT / "registry/session-checkpoint-latest.json"
LEDGER = ROOT / "registry/2026-09-03_UniverseLab_PublicScientificHighClaimAdjudication_v1.0.json"
SUMMARY = ROOT / "registry/2026-09-03_UniverseLab_PublicScientificClaimExtractionSummary_v0.1.json"
ASSIGNMENTS = ROOT / "registry/2026-09-03_UniverseLab_PublicScientificClaimFamilyAssignments_v0.1.json"
DELTA = ROOT / "registry/2026-09-04_UniverseLab_BandVC_StatusPageMediumDeltaAdjudication_v1.0.json"
MANIFEST = ROOT / "project-manifest.json"
OBS_EN = ROOT / "observatory-en.html"
STATUS_DE = ROOT / "research-status.html"
STATUS_EN = ROOT / "research-status-en.html"
SHELL = ROOT / "assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js"
VALIDATOR = ROOT / "tools/2026-09-01_validate_UniverseLab_CurrentMainCanonicalStateReconciliation_v1.0.py"
SCANNER = ROOT / "tools/2026-09-03_extract_UniverseLab_PublicScientificClaims_v1.0.py"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load(path: Path):
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def rel(value: str) -> Path:
    path = ROOT / value
    assert path.is_file(), value
    return path


def gates(value: dict) -> dict:
    return value.get("physical_governance") or value.get("gates") or value.get("governance") or value


def assert_closed(value: dict) -> None:
    g = gates(value)
    assert g.get("K1-D") == "NOT_RELEASED"
    assert g.get("K1-E") == "NOT_ADMISSIBLE"
    assert g.get("physical_evidence_effect", value.get("physical_evidence_effect")) == "NONE"
    for names, expected in (
        (("ratified_human_trust_root", "RATIFIED_HUMAN_TRUST_ROOT"), "NOT_RATIFIED"),
        (("runtime_issuance_bindings", "RUNTIME_ISSUANCE_BINDINGS"), "BLOCKED"),
        (("operative_authorization_decision", "AuthorizationDecision"), "NOT_CREATED"),
        (("operative_single_use_grant", "SingleUseGrant"), "NOT_CREATED"),
        (("backend_import", "BACKEND_IMPORT"), "NOT_EXECUTED"),
        (("solver_execution", "SOLVER_EXECUTION"), "NOT_EXECUTED"),
    ):
        present = [g[name] for name in names if name in g]
        if present:
            assert present[0] == expected, (names, present[0], expected)


def main() -> None:
    validator = module("ul_state_validator_high_current", VALIDATOR)
    validator.validate(ROOT, strict_source_existence=True)

    # Historical HIGH adjudication remains immutable.
    ledger = load(LEDGER)
    assert ledger["high_candidate_count"] == 2
    assert ledger["adjudicated_count"] == 2
    assert ledger["unadjudicated_high_count"] == 0
    result = ledger["global_result"]
    assert result["high_overclaim_count"] == 0
    assert result["high_scope_firewall_count"] == 1
    assert result["high_governance_claim_count"] == 1
    assert result["physical_claim_promotions"] == 0
    assert ledger["physical_gate_effect"] == ledger["physical_evidence_effect"] == "NONE"

    by_id = {row["claim_id"]: row for row in ledger["records"]}
    obs_record = by_id["UL-CLAIM-CANDIDATE-978286FC7F925D9A"]
    gov_record = by_id["UL-CLAIM-CANDIDATE-AA0AA1DAAC06DFF6"]
    assert obs_record["adjudication"]["is_positive_physical_hzt_claim"] is False
    assert obs_record["underlying_physical_status"]["ghost_freedom"] == "OFFEN"
    assert gov_record["adjudication"]["primary_status"] == "NICHT_WISSENSCHAFTLICHER_CLAIM"
    assert gov_record["content_validity"]["physical_evidence"] == "NONE"

    # Active append-only pointer chain and public firewalls.
    alias = load(ALIAS)
    checkpoint = load(rel(alias["canonical_snapshot"]))
    state = load(rel(alias["canonical_state"]))
    site = load(rel(alias["site_state"]))
    manifest = load(MANIFEST)
    assert ALIAS.read_bytes() == rel(alias["canonical_snapshot"]).read_bytes()
    assert checkpoint == alias
    de = STATUS_DE.read_text(encoding="utf-8")
    en = STATUS_EN.read_text(encoding="utf-8")
    shell = SHELL.read_text(encoding="utf-8")
    obs = OBS_EN.read_text(encoding="utf-8")
    assert obs_record["replacement_text"] in obs
    assert "As a status rule only — not evidence for HZT and not a physical measurement" in en
    assert "Als reine Statusregel – keine Evidenz für HZT und keine physikalische Messung" in de
    assert "Open pull requests have no canonical effect" in en
    assert "Offene Pull Requests besitzen keine kanonische Wirkung" in de
    assert "As a repository-audit mapping only" in en and "not physical evidence for HZT" in en
    assert "Als reine Repository-Auditzuordnung" in de and "keine physische Evidenz für HZT" in de
    assert alias["canonical_state"] in de and alias["canonical_state"] in en
    assert alias["site_state"] in shell
    assert manifest["canonical_state"] == alias["canonical_state"]
    assert manifest["site_state"] == alias["site_state"]
    assert manifest["session_checkpoint"] == alias["canonical_snapshot"]
    assert state["basis_main_commit"] == site["basis_main_commit"] == checkpoint["basis_commit"] == manifest["basis_main_commit"]
    for value in (state, site, checkpoint, manifest):
        assert_closed(value)

    # Current materialized corpus: 993, HIGH=0, MEDIUM=46.
    summary = load(SUMMARY)
    assignments = load(ASSIGNMENTS)
    delta = load(DELTA)
    assert summary["claim_candidates"] == 993
    assert summary["tracked_html_files"] == 72
    assert summary["risk_classes"].get("HIGH", 0) == 0
    assert summary["risk_classes"]["MEDIUM"] == 46
    assert summary["physical_gate_effect"] == summary["physical_evidence_effect"] == "NONE"
    assert assignments["candidate_count"] == 993
    assert assignments["assignment_count"] == 993
    assert assignments["high_medium_candidate_count"] == 46
    assert assignments["unknown_family_ids"] == 0
    assert assignments["unmapped_candidates"] == 0
    assert delta["global_result"]["contextually_adjudicated"] == 7
    assert delta["global_result"]["physical_claim_promotions"] == 0

    scanner = module("ul_scanner_high_current", SCANNER)
    rows, live_summary = scanner.extract(ROOT)
    high = [row for row in rows if row.preliminary_risk_class == "HIGH"]
    medium = [row for row in rows if row.preliminary_risk_class == "MEDIUM"]
    assert high == [], [(row.path, row.source_line, row.text) for row in high]
    assert len(rows) == 993
    assert len(medium) == 46
    assert live_summary["physical_gate_effect"] == live_summary["physical_evidence_effect"] == "NONE"

    print(
        "UniverseLab Band V-B HIGH gate: PASS historical_high=2/2 current_claims=993 "
        "current_high=0 current_medium=46 successor_delta=7/7 physical_promotions=0"
    )


if __name__ == "__main__":
    main()
