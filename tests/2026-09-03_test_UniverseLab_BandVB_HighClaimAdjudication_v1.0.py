#!/usr/bin/env python3
"""Band V-B HIGH-claim adjudication and current-state reconciliation gate.

This test closes the two Band-V-A HIGH review items at the public-text and
repository-governance level only. It must not promote physical evidence,
K1-D/K1-E, solver authorization, or any parent-theory result.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = "8351f2d7d9d0852768014c1fdfbbecfb4432fa55"
STATE = ROOT / "registry/2026-09-03_UniverseLab_CurrentMainCanonicalState_v1.2.json"
SITE = ROOT / "registry/2026-09-03_UniverseLab_SiteState_v1.3.json"
CHECKPOINT = ROOT / "registry/2026-09-03_UniverseLab_SessionCheckpoint_v1.33.json"
ALIAS = ROOT / "registry/session-checkpoint-latest.json"
LEDGER = ROOT / "registry/2026-09-03_UniverseLab_PublicScientificHighClaimAdjudication_v1.0.json"
MANIFEST = ROOT / "project-manifest.json"
OBS_EN = ROOT / "observatory-en.html"
STATUS_DE = ROOT / "research-status.html"
STATUS_EN = ROOT / "research-status-en.html"
SHELL = ROOT / "assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js"
VALIDATOR = ROOT / "tools/2026-09-01_validate_UniverseLab_CurrentMainCanonicalStateReconciliation_v1.0.py"
SCANNER = ROOT / "tools/2026-09-03_extract_UniverseLab_PublicScientificClaims_v1.0.py"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def assert_closed_gates(value: dict) -> None:
    gates = value.get("physical_governance") or value.get("gates") or value.get("governance") or value
    assert gates.get("K1-D") == "NOT_RELEASED"
    assert gates.get("K1-E") == "NOT_ADMISSIBLE"
    assert gates.get("physical_evidence_effect", value.get("physical_evidence_effect")) == "NONE"
    if "solver_authorized" in gates:
        assert gates["solver_authorized"] is False
    for names, expected in (
        (("ratified_human_trust_root", "RATIFIED_HUMAN_TRUST_ROOT"), "NOT_RATIFIED"),
        (("runtime_issuance_bindings", "RUNTIME_ISSUANCE_BINDINGS"), "BLOCKED"),
        (("operative_authorization_decision", "AuthorizationDecision"), "NOT_CREATED"),
        (("operative_single_use_grant", "SingleUseGrant"), "NOT_CREATED"),
        (("backend_import", "BACKEND_IMPORT"), "NOT_EXECUTED"),
        (("solver_execution", "SOLVER_EXECUTION"), "NOT_EXECUTED"),
    ):
        present = [gates[name] for name in names if name in gates]
        if present:
            assert present[0] == expected, (names, present[0], expected)


def main() -> None:
    # Reuse the pre-existing fail-closed state-chain validator, including the
    # strongest source-existence mode. The new state must satisfy the old
    # safety contract; the validator is not weakened for this changeset.
    validator = module("ul_current_state_validator_vb", VALIDATOR)
    validator.validate(ROOT, strict_source_existence=True)

    ledger = load(LEDGER)
    assert ledger["status"] == "HIGH_CLAIMS_MANUALLY_CONTEXT_ADJUDICATED_NO_PHYSICAL_EVIDENCE_EFFECT"
    assert ledger["high_candidate_count"] == 2
    assert ledger["adjudicated_count"] == 2
    assert ledger["unadjudicated_high_count"] == 0
    assert len(ledger["records"]) == 2
    result = ledger["global_result"]
    assert result["high_overclaim_count"] == 0
    assert result["high_scope_firewall_count"] == 1
    assert result["high_governance_claim_count"] == 1
    assert result["physical_claim_promotions"] == 0
    assert result["public_wording_repairs_required"] == 2
    assert result["public_wording_repairs_completed_in_changeset"] == 2
    assert result["public_wording_repairs_remaining"] == 0
    assert ledger["physical_gate_effect"] == "NONE"
    assert ledger["physical_evidence_effect"] == "NONE"

    by_id = {row["claim_id"]: row for row in ledger["records"]}
    obs_record = by_id["UL-CLAIM-CANDIDATE-978286FC7F925D9A"]
    gov_record = by_id["UL-CLAIM-CANDIDATE-AA0AA1DAAC06DFF6"]
    assert obs_record["adjudication"]["is_positive_physical_hzt_claim"] is False
    assert obs_record["adjudication"]["is_empirical_confirmation_claim"] is False
    assert obs_record["adjudication"]["is_parent_derivation_claim"] is False
    assert obs_record["underlying_physical_status"]["ghost_freedom"] == "OFFEN"
    assert obs_record["underlying_physical_status"]["observational_confirmation_of_hzt"] == "OFFEN_NOT_ESTABLISHED"
    assert obs_record["public_action_status"] == "IMPLEMENTED_IN_CHANGESET_REVIEW_PENDING"
    assert gov_record["adjudication"]["primary_status"] == "NICHT_WISSENSCHAFTLICHER_CLAIM"
    assert gov_record["adjudication"]["secondary_status"] == "BEWIESEN_AS_REPOSITORY_STATE_CONTRACT"
    assert gov_record["adjudication"]["is_positive_physical_hzt_claim"] is False
    assert gov_record["content_validity"]["physical_evidence"] == "NONE"
    assert gov_record["separate_provenance_defect"]["repair_status"] == "IMPLEMENTED_IN_CHANGESET_REVIEW_PENDING"

    obs = OBS_EN.read_text(encoding="utf-8")
    de = STATUS_DE.read_text(encoding="utf-8")
    en = STATUS_EN.read_text(encoding="utf-8")
    shell = SHELL.read_text(encoding="utf-8")
    assert obs_record["replacement_text"] in obs
    assert "As a status rule only — not evidence for HZT and not a physical measurement" in en
    assert "Als reine Statusregel – keine Evidenz für HZT und keine physikalische Messung" in de
    assert "registry/2026-09-03_UniverseLab_CurrentMainCanonicalState_v1.2.json" in de
    assert "registry/2026-09-03_UniverseLab_CurrentMainCanonicalState_v1.2.json" in en
    assert "registry/2026-09-03_UniverseLab_SiteState_v1.3.json" in shell
    for stale in (
        "<code>30b781f84d9c…</code>",
        "CurrentMainCanonicalState_v1.1.json\">Current-main Canonical State v1.1",
    ):
        assert stale not in de
        assert stale not in en

    state = load(STATE)
    site = load(SITE)
    checkpoint = load(CHECKPOINT)
    manifest = load(MANIFEST)
    assert state["basis_main_commit"] == BASE
    assert site["basis_main_commit"] == BASE
    assert checkpoint["basis_commit"] == BASE
    assert manifest["basis_main_commit"] == BASE
    assert state["merged_analysis_blocks"]["band_iv_b"]["status"] == "MERGED_QA_RECONCILED"
    assert state["merged_analysis_blocks"]["band_v_a"]["status"] == "MERGED_PUBLIC_CLAIM_CENSUS_AND_ROUTING_COVERAGE"
    assert state["active_analysis_block"]["substantive_high_overclaims"] == 0
    assert state["active_analysis_block"]["physical_claim_promotions"] == 0
    assert manifest["canonical_state"] == STATE.relative_to(ROOT).as_posix()
    assert manifest["site_state"] == SITE.relative_to(ROOT).as_posix()
    assert manifest["session_checkpoint"] == CHECKPOINT.relative_to(ROOT).as_posix()
    assert ALIAS.read_bytes() == CHECKPOINT.read_bytes()
    assert_closed_gates(state)
    assert_closed_gates(site)
    assert_closed_gates(checkpoint)
    assert_closed_gates(manifest)

    # Re-extract the live branch corpus. The two former HIGH items must now be
    # self-contained firewalls/governance qualifiers, and no unresolved HIGH
    # lexical item may remain before the HIGH gate closes.
    scanner = module("ul_band_va_scanner_vb", SCANNER)
    rows, summary = scanner.extract(ROOT)
    high = [row for row in rows if row.preliminary_risk_class == "HIGH"]
    assert high == [], [(row.path, row.source_line, row.text) for row in high]

    obs_rows = [row for row in rows if row.path == "observatory-en.html" and "may not establish ghost freedom" in row.text]
    assert len(obs_rows) == 1, obs_rows
    assert obs_rows[0].limiter_present is True
    assert obs_rows[0].preliminary_risk_class == "CONTEXT_OR_FIREWALL"

    status_rows = [row for row in rows if row.path == "research-status.html" and "keine Evidenz für HZT" in row.text]
    assert status_rows, "self-contained German governance qualifier not extracted"
    assert all(row.preliminary_risk_class != "HIGH" for row in status_rows)
    assert summary["physical_gate_effect"] == "NONE"
    assert summary["physical_evidence_effect"] == "NONE"

    print(
        "UniverseLab Band V-B HIGH gate: PASS "
        f"historical_high=2 adjudicated=2 current_high={len(high)} "
        "physical_promotions=0"
    )


if __name__ == "__main__":
    main()
