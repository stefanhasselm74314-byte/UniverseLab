#!/usr/bin/env python3
"""Fail-closed QA for FM-0 targeted lowercase a0 provenance recovery.

Governance/provenance only: no solver/backend import, authorization, grant,
physical background, response-rank execution or evidence/release effect.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INV = ROOT / "registry/2026-08-31_HZT_M0_ForwardMap_FM0_Inventory_v0.4.json"
GAPS = ROOT / "registry/2026-08-31_HZT_M0_ForwardMap_FM0_GapRegister_v0.3.json"
BIND = ROOT / "registry/2026-08-31_HZT_M0_ForwardMap_FM0_a0Binding_v0.1.json"
REPORT = ROOT / "2026-08-31_HZT_M0_ForwardMap_FM0_a0ParentRecovery_v0.1.md"
FORMULAS = ROOT / "legacy-formeln-H1-H64.csv"
SNAPSHOT = ROOT / "legacy-snapshot-2026-06-29.json"

A0_STATUS = "HISTORICAL_PROVENANCE_RECOVERED_CANONICAL_PARENT_OPEN"
GAP_STATUS = "PARTIALLY_RESOLVED_HISTORICAL_PROVENANCE_RECOVERED_CANONICAL_PARENT_OPEN"
OPEN = "OPEN_RECOVERY_REQUIRED"
INF = "ALGEBRAIC_INFERENCE_NOT_CANONICAL_BINDING"
EXPECTED_FIREWALL = {
    "WP1": "CLOSED_TARGET_FROZEN_NO_EXECUTION",
    "WP2": "READY_FOR_SEPARATE_AUTHORIZATION_DECISION_NOT_AUTHORIZED",
    "operative_AuthorizationDecision": "NOT_CREATED",
    "SingleUseGrant": "NOT_CREATED",
    "backend_import": "NOT_EXECUTED",
    "solver_run": "NOT_EXECUTED",
    "physical_background": "NOT_ESTABLISHED",
    "WP3": "NOT_STARTED",
    "WP4": "BLOCKED_NOT_AUTHORIZED",
    "rank_R": "OPEN_NOT_EXECUTED",
    "K1-D": "NOT_RELEASED",
    "K1-E": "NOT_ADMISSIBLE",
}


def load_json(path: Path, errors: list[str]) -> dict:
    if not path.is_file():
        errors.append(f"missing required file: {path.relative_to(ROOT)}")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot parse {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"top-level JSON must be object: {path.relative_to(ROOT)}")
        return {}
    return data


def formula_rows(errors: list[str]) -> dict[str, dict[str, str]]:
    if not FORMULAS.is_file():
        errors.append("missing legacy-formeln-H1-H64.csv")
        return {}
    try:
        with FORMULAS.open(encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh, delimiter=";"))
    except OSError as exc:
        errors.append(f"cannot read formula source: {exc}")
        return {}
    return {row.get("id", ""): row for row in rows}


def main() -> int:
    errors: list[str] = []
    inv = load_json(INV, errors)
    gaps = load_json(GAPS, errors)
    bind = load_json(BIND, errors)
    snap = load_json(SNAPSHOT, errors)
    rows = formula_rows(errors)

    if not REPORT.is_file():
        errors.append("missing a0 recovery report")

    if inv.get("gate") != "FM-G0" or inv.get("gate_status") != "OPEN":
        errors.append("FM-G0 must remain OPEN")
    if inv.get("cp01r4_state") != "FROZEN_NO_EXECUTION":
        errors.append("CP01R4 must remain FROZEN_NO_EXECUTION")
    if inv.get("physical_gate_effect") != "NONE" or inv.get("physical_evidence_effect") != "NONE":
        errors.append("inventory physical effects must remain NONE")
    if inv.get("firewall") != EXPECTED_FIREWALL:
        errors.append("scientific/authorization firewall changed")

    params = inv.get("parameter_set")
    if not isinstance(params, list):
        errors.append("parameter_set must be list")
        params = []
    by_symbol = {p.get("symbol"): p for p in params if isinstance(p, dict)}
    if set(by_symbol) != {"a0", "beta_tau", "R_chi", "I_B", "kappa_6"}:
        errors.append("FM-0 parameter set changed")
    a0 = by_symbol.get("a0", {})
    if a0.get("recovery_status") != A0_STATUS:
        errors.append("a0 recovery_status must preserve historical/current-canonical distinction")
    for key in ("definition", "dimension", "parent_provenance"):
        if a0.get(key) != OPEN:
            errors.append(f"a0 {key} must remain OPEN_RECOVERY_REQUIRED")
    if a0.get("identity_with_A0") != "NO_IDENTITY_ASSERTED":
        errors.append("lowercase a0 must not be aliased to uppercase A0")
    if a0.get("blocking_gap") != "FM0-GAP-001":
        errors.append("a0 must remain bound to FM0-GAP-001")
    inferences = a0.get("inferences")
    if not isinstance(inferences, list) or len(inferences) != 1:
        errors.append("a0 must contain exactly one explicit historical dimensional inference")
    else:
        inf = inferences[0]
        if inf.get("classification") != INF or not str(inf.get("basis", "")).strip():
            errors.append("a0 inference must be explicitly noncanonical and source-based")

    gap_list = gaps.get("gaps")
    if not isinstance(gap_list, list):
        errors.append("gap register gaps must be list")
        gap_list = []
    gap_by_id = {g.get("id"): g for g in gap_list if isinstance(g, dict)}
    g1 = gap_by_id.get("FM0-GAP-001", {})
    if g1.get("blocking") is not True or g1.get("status") != GAP_STATUS:
        errors.append("FM0-GAP-001 must remain blocking with partial historical-resolution status")
    if g1.get("guard") != "NO_IDENTITY_WITH_A0_WITHOUT_EXPLICIT_CANONICAL_BINDING":
        errors.append("a0/A0 lexical guard changed")
    if gaps.get("blocking_gap_count") != 10:
        errors.append("blocking_gap_count must remain 10")
    if gaps.get("partially_resolved_blocking_gap_count") != 2:
        errors.append("partially_resolved_blocking_gap_count must be 2")
    if gaps.get("fully_unresolved_blocking_gap_count") != 8:
        errors.append("fully_unresolved_blocking_gap_count must be 8")
    if gaps.get("gate_status") != "OPEN":
        errors.append("gap register FM-G0 must remain OPEN")
    if gaps.get("physical_gate_effect") != "NONE" or gaps.get("physical_evidence_effect") != "NONE":
        errors.append("gap register physical effects must remain NONE")

    if bind.get("item") != "a0" or bind.get("recovery_status") != A0_STATUS:
        errors.append("a0 binding artifact identity/status mismatch")
    if bind.get("current_canonical_definition") != OPEN:
        errors.append("binding must not promote a historical a0 definition to current canonical")
    if bind.get("current_canonical_dimension") != OPEN:
        errors.append("binding must keep current canonical a0 dimension open")
    if bind.get("current_parent_provenance") != OPEN:
        errors.append("binding must keep current Parent derivation open")
    guard = bind.get("uppercase_A0_guard")
    if not isinstance(guard, dict) or guard.get("identity_with_A0") != "NO_IDENTITY_ASSERTED":
        errors.append("binding must preserve lowercase-a0/uppercase-A0 separation")
    if bind.get("physical_gate_effect") != "NONE" or bind.get("physical_evidence_effect") != "NONE":
        errors.append("binding physical effects must remain NONE")

    expected = {
        "H31": "open",
        "H34": "historical",
        "H35": "historical",
        "H36": "historical",
        "H37": "historical",
        "H38": "historical",
        "H39": "historical",
        "H40": "historical",
        "H41": "historical",
        "H42": "historical",
    }
    for fid, status in expected.items():
        row = rows.get(fid)
        if not row:
            errors.append(f"missing historical source formula {fid}")
        elif row.get("status") != status:
            errors.append(f"{fid} status changed: expected {status}, got {row.get('status')}")

    ranges = snap.get("formula_bible", {}).get("ranges", []) if isinstance(snap.get("formula_bible"), dict) else []
    h34_range = next((r for r in ranges if isinstance(r, dict) and r.get("ids") == "H34-H42"), None)
    if not h34_range or h34_range.get("status") != "historical":
        errors.append("legacy snapshot must classify H34-H42 as historical")
    claims = snap.get("claim_audit", [])
    mond_claim = next((c for c in claims if isinstance(c, dict) and c.get("claim") == "MOND_exact_no_free_parameters"), None)
    if not mond_claim or mond_claim.get("status") != "historical":
        errors.append("legacy MOND exact/no-free-parameters claim must remain historical")
    quarantine = snap.get("import_policy", {}).get("quarantine", []) if isinstance(snap.get("import_policy"), dict) else []
    if "MOND and a0 result claims" not in quarantine:
        errors.append("legacy import policy must quarantine MOND and a0 result claims")

    if errors:
        print("FM-0 a0 Parent Recovery QA: FAIL")
        for err in errors:
            print(f"ERROR: {err}")
        return 1

    print("FM-0 a0 Parent Recovery QA: PASS")
    print("a0=HISTORICAL_PROVENANCE_RECOVERED_CANONICAL_PARENT_OPEN")
    print("FM0-GAP-001 remains blocking; FM-G0=OPEN")
    print("lowercase a0 != uppercase A0 unless a future explicit canonical alias is recovered")
    print("CP01R4 frozen; physical/release effect=NONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
