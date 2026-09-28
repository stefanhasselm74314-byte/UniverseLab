#!/usr/bin/env python3
"""Fail-closed QA for HZT-M0 FM-0 Parent/Canon Recovery.

Governance/provenance QA only. This script does not import a physics backend,
run a solver, authorize CP01R4, or create physical evidence/release status.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "registry/2026-08-31_HZT_M0_ForwardMap_FM0_Inventory_v0.2.json"
GAPS = ROOT / "registry/2026-08-31_HZT_M0_ForwardMap_FM0_GapRegister_v0.1.json"
REPORT = ROOT / "2026-08-31_HZT_M0_ForwardMap_FM0_ParentCanonRecovery_v0.1.md"

EXPECTED_PARAMETERS = {"a0", "beta_tau", "R_chi", "I_B", "kappa_6"}
EXPECTED_OBSERVABLES = {"O_RAR", "O_cosmo", "O_growth", "O_lensing", "O_GW"}
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
CLOSED_GATE_STATES = {"CLOSED", "PASS", "PASSED", "RELEASED", "COMPLETE", "COMPLETED"}
OPEN_RECOVERY = "OPEN_RECOVERY_REQUIRED"
INFERENCE_CLASS = "ALGEBRAIC_INFERENCE_NOT_CANONICAL_BINDING"


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
        errors.append(f"top-level JSON must be an object: {path.relative_to(ROOT)}")
        return {}
    return data


def main() -> int:
    errors: list[str] = []
    inventory = load_json(INVENTORY, errors)
    gaps_doc = load_json(GAPS, errors)

    if not REPORT.is_file():
        errors.append(f"missing required file: {REPORT.relative_to(ROOT)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if inventory.get("work_package") != "FM-0":
        errors.append("inventory work_package must be FM-0")
    if inventory.get("gate") != "FM-G0":
        errors.append("inventory gate must be FM-G0")
    if inventory.get("physical_gate_effect") != "NONE":
        errors.append("physical_gate_effect must remain NONE")
    if inventory.get("physical_evidence_effect") != "NONE":
        errors.append("physical_evidence_effect must remain NONE")
    if inventory.get("cp01r4_state") != "FROZEN_NO_EXECUTION":
        errors.append("CP01R4 must remain FROZEN_NO_EXECUTION")

    params = inventory.get("parameter_set")
    if not isinstance(params, list):
        errors.append("parameter_set must be a list")
        params = []
    symbols = {entry.get("symbol") for entry in params if isinstance(entry, dict)}
    if symbols != EXPECTED_PARAMETERS:
        errors.append(f"parameter set mismatch: got {sorted(str(x) for x in symbols)}")

    observables = inventory.get("observable_blocks")
    if not isinstance(observables, list):
        errors.append("observable_blocks must be a list")
        observables = []
    observable_ids = {entry.get("id") for entry in observables if isinstance(entry, dict)}
    if observable_ids != EXPECTED_OBSERVABLES:
        errors.append(f"observable set mismatch: got {sorted(str(x) for x in observable_ids)}")

    gaps = gaps_doc.get("gaps")
    if not isinstance(gaps, list):
        errors.append("gap register gaps must be a list")
        gaps = []
    gap_by_id = {
        entry.get("id"): entry
        for entry in gaps
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    if len(gap_by_id) != len(gaps):
        errors.append("gap IDs must be present and unique")

    blocking_open = [
        entry
        for entry in gaps
        if isinstance(entry, dict)
        and entry.get("blocking") is True
        and entry.get("status") == OPEN_RECOVERY
    ]
    declared_count = gaps_doc.get("blocking_gap_count")
    if declared_count != len(blocking_open):
        errors.append(
            f"blocking_gap_count={declared_count!r} does not equal open blocking gaps={len(blocking_open)}"
        )

    inv_gate_status = str(inventory.get("gate_status", "")).upper()
    gap_gate_status = str(gaps_doc.get("gate_status", "")).upper()
    if blocking_open and (inv_gate_status in CLOSED_GATE_STATES or gap_gate_status in CLOSED_GATE_STATES):
        errors.append("FM-G0 cannot be CLOSED/PASS while an open blocking gap exists")
    if blocking_open and (inv_gate_status != "OPEN" or gap_gate_status != "OPEN"):
        errors.append("current open blocking gaps require FM-G0 = OPEN in both registries")

    for entry in params:
        if not isinstance(entry, dict):
            errors.append("parameter entries must be objects")
            continue
        symbol = entry.get("symbol")
        if entry.get("recovery_status") == OPEN_RECOVERY:
            gap_id = entry.get("blocking_gap")
            gap = gap_by_id.get(gap_id)
            if not gap or gap.get("blocking") is not True or gap.get("status") != OPEN_RECOVERY:
                errors.append(f"{symbol}: unresolved parameter lacks matching open blocking gap")

        if symbol == "a0" and entry.get("recovery_status") == OPEN_RECOVERY:
            if entry.get("identity_with_A0") != "NO_IDENTITY_ASSERTED":
                errors.append("a0: unresolved state must keep identity_with_A0 = NO_IDENTITY_ASSERTED")

        inferences = entry.get("inferences", [])
        if inferences is None:
            inferences = []
        if not isinstance(inferences, list):
            errors.append(f"{symbol}: inferences must be a list when present")
            continue
        for index, inference in enumerate(inferences):
            if not isinstance(inference, dict):
                errors.append(f"{symbol}: inference #{index + 1} must be an object")
                continue
            if inference.get("classification") != INFERENCE_CLASS:
                errors.append(f"{symbol}: inference #{index + 1} lacks required classification")
            basis = inference.get("basis")
            if not isinstance(basis, str) or not basis.strip():
                errors.append(f"{symbol}: inference #{index + 1} lacks explicit basis")

    for entry in observables:
        if not isinstance(entry, dict):
            errors.append("observable entries must be objects")
            continue
        obs_id = entry.get("id")
        if entry.get("recovery_status") == OPEN_RECOVERY:
            if entry.get("provenance_class") != "PROGRAM_DECLARATION_ONLY":
                errors.append(f"{obs_id}: unresolved observable must remain PROGRAM_DECLARATION_ONLY")
            gap_id = entry.get("blocking_gap")
            gap = gap_by_id.get(gap_id)
            if not gap or gap.get("blocking") is not True or gap.get("status") != OPEN_RECOVERY:
                errors.append(f"{obs_id}: unresolved observable lacks matching open blocking gap")

    firewall = inventory.get("firewall")
    if firewall != EXPECTED_FIREWALL:
        errors.append("scientific/authorization firewall does not exactly match the frozen baseline")

    if gaps_doc.get("physical_gate_effect") != "NONE":
        errors.append("gap register physical_gate_effect must remain NONE")
    if gaps_doc.get("physical_evidence_effect") != "NONE":
        errors.append("gap register physical_evidence_effect must remain NONE")

    policy = inventory.get("inference_policy")
    if not isinstance(policy, dict):
        errors.append("inference_policy must be present")
    else:
        if policy.get("required_inference_class") != INFERENCE_CLASS:
            errors.append("inference policy class changed")
        if policy.get("basis_required") is not True:
            errors.append("inference policy must require a basis")
        if policy.get("inference_never_closes_parent_provenance_gap_by_itself") is not True:
            errors.append("inference alone must never close a parent-provenance gap")

    if errors:
        print("FM-0 Parent/Canon Recovery QA: FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("FM-0 Parent/Canon Recovery QA: PASS")
    print(f"parameters={len(params)} observables={len(observables)} open_blocking_gaps={len(blocking_open)}")
    print("FM-G0=OPEN; PASS means the unresolved state is represented consistently, not that FM-0 is complete.")
    print("CP01R4 remains frozen; physical/release effect=NONE.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
