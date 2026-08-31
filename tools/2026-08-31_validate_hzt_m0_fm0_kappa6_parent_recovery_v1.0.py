#!/usr/bin/env python3
"""Fail-closed QA for targeted HZT-M0 FM-0 kappa_6 parent recovery.

Provenance/governance QA only. This script does not import a physics backend,
run a solver, create an authorization/grant, or change physical evidence status.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINDING = ROOT / "registry/2026-08-31_HZT_M0_ForwardMap_FM0_Kappa6Binding_v0.1.json"
INVENTORY = ROOT / "registry/2026-08-31_HZT_M0_ForwardMap_FM0_Inventory_v0.3.json"
GAPS = ROOT / "registry/2026-08-31_HZT_M0_ForwardMap_FM0_GapRegister_v0.2.json"
REPORT = ROOT / "2026-08-31_HZT_M0_ForwardMap_FM0_Kappa6ParentRecovery_v0.1.md"
CONVENTIONS = ROOT / "convention-registry.json"
PARENT_MACHINE = ROOT / "hzt-s6-parent-action-v0.1.json"
PARENT_MD = ROOT / "SCI-001-002_v0.1_Canonical_6D_Parent_Action_and_Boundary_Closure.md"
PREFLIGHT_MD = ROOT / "SCI-001-002_v0.2_MD-2S_Background_Substitution_Preflight.md"

EXPECTED_PARAMETERS = {"a0", "beta_tau", "R_chi", "I_B", "kappa_6"}
EXPECTED_OBSERVABLES = {"O_RAR", "O_cosmo", "O_growth", "O_lensing", "O_GW"}
OPEN_RECOVERY = "OPEN_RECOVERY_REQUIRED"
KAPPA_STATUS = "PARTIALLY_RESOLVED_CANONICAL_PARENT_RECOVERED"
KAPPA_GAP_STATUS = "PARTIALLY_RESOLVED_CANONICAL_PARENT_RECOVERED_MAPPING_OPEN"
INFERENCE_CLASS = "ALGEBRAIC_INFERENCE_NOT_CANONICAL_BINDING"
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


def require_text(path: Path, errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing required file: {path.relative_to(ROOT)}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read {path.relative_to(ROOT)}: {exc}")
        return ""


def main() -> int:
    errors: list[str] = []
    binding = load_json(BINDING, errors)
    inventory = load_json(INVENTORY, errors)
    gaps_doc = load_json(GAPS, errors)
    conventions = load_json(CONVENTIONS, errors)
    parent_machine = load_json(PARENT_MACHINE, errors)
    report_text = require_text(REPORT, errors)
    parent_text = require_text(PARENT_MD, errors)
    preflight_text = require_text(PREFLIGHT_MD, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    # Direct canonical source must actually contain the recovered kappa_6 statements.
    if conventions.get("scope") != "Canonical conventions for current controlled calculations. Branch-specific deviations require explicit rederivation.":
        errors.append("convention registry canonical scope changed")
    units = conventions.get("units", {})
    if units.get("length_mass_relation") != "[L]=[M]^-1":
        errors.append("canonical length/mass convention changed")
    gravity = conventions.get("gravity", {})
    expected_action = "S_EH = (1/(2 kappa_6^2)) integral d^6X sqrt(|g_6|) (R_6 - 2 Lambda_6)"
    if gravity.get("einstein_hilbert_action") != expected_action:
        errors.append("canonical kappa_6 Einstein-Hilbert normalization missing or changed")
    if gravity.get("kappa_relation") != "kappa_6^2 = 8 pi G_6":
        errors.append("canonical kappa_6/G_6 relation missing or changed")
    dimensions = gravity.get("dimensions", {})
    if dimensions.get("kappa_6_squared") != "L^4 = M^-4":
        errors.append("canonical squared kappa_6 dimension missing or changed")

    # Controlled parent action must independently retain M6^4 normalization.
    field_dims = parent_machine.get("field_dimensions_M", {})
    if field_dims.get("M6") != 1:
        errors.append("parent-action M6 mass dimension is not 1")
    equations = parent_machine.get("equations", [])
    eq1 = next((e for e in equations if isinstance(e, dict) and e.get("id") == "HZT-S6-PAR-v0.1-EQ-001"), None)
    if not eq1 or eq1.get("role") != "core_action" or eq1.get("status") != "DEFINED":
        errors.append("controlled parent core-action equation metadata missing")
    if "\\frac{M_6^4}{2}" not in parent_text:
        errors.append("controlled parent action no longer contains M_6^4/2 coefficient")
    if "kappa6^2 lambda_eff / (4 sqrt(K4))" not in preflight_text:
        errors.append("corroborating kappa6 benchmark use missing from MD-2S preflight")

    # Binding may recover direct facts and algebraic consequences, but not silently promote M6 identity.
    if binding.get("item") != "kappa_6" or binding.get("recovery_status") != KAPPA_STATUS:
        errors.append("kappa_6 binding recovery status mismatch")
    if binding.get("status_class") != "CANONICAL_PARENT_GRAVITATIONAL_COUPLING_NORMALIZATION":
        errors.append("kappa_6 status class mismatch")
    parent_binding = binding.get("canonical_parent_binding", {})
    if parent_binding.get("source") != "convention-registry.json":
        errors.append("kappa_6 binding must point to convention-registry.json")
    if parent_binding.get("einstein_hilbert_action") != expected_action:
        errors.append("binding action statement does not match canonical source")
    if parent_binding.get("kappa_relation") != gravity.get("kappa_relation"):
        errors.append("binding kappa relation does not match canonical source")
    if parent_binding.get("canonical_dimension_statement") != "kappa_6_squared: L^4 = M^-4":
        errors.append("binding squared dimension statement mismatch")

    binding_inferences = binding.get("inferences", [])
    if not isinstance(binding_inferences, list) or len(binding_inferences) < 2:
        errors.append("binding must retain explicit dimension and M6 coefficient inferences")
        binding_inferences = []
    for index, inference in enumerate(binding_inferences):
        if not isinstance(inference, dict):
            errors.append(f"binding inference #{index + 1} must be an object")
            continue
        if inference.get("classification") != INFERENCE_CLASS:
            errors.append(f"binding inference #{index + 1} has non-governed classification")
        if not str(inference.get("basis", "")).strip():
            errors.append(f"binding inference #{index + 1} lacks basis")
    m6_inference = next((i for i in binding_inferences if isinstance(i, dict) and i.get("id") == "FM0-K6-INF-002"), None)
    if not m6_inference or m6_inference.get("promotion_status") != "NOT_PROMOTED_TO_DIRECT_CANONICAL_M6_IDENTITY":
        errors.append("M6 coefficient inference must remain explicitly noncanonical")

    gap_decision = binding.get("gap_decision", {})
    if gap_decision != {
        "gap_id": "FM0-GAP-005",
        "blocking": True,
        "status": KAPPA_GAP_STATUS,
        "close_gap": False,
    }:
        errors.append("kappa_6 gap decision must remain blocking and not closed")

    # Inventory and gap register must agree and keep FM-G0 open.
    if inventory.get("gate") != "FM-G0" or inventory.get("gate_status") != "OPEN":
        errors.append("inventory must keep FM-G0 OPEN")
    if gaps_doc.get("gate") != "FM-G0" or gaps_doc.get("gate_status") != "OPEN":
        errors.append("gap register must keep FM-G0 OPEN")
    if inventory.get("gap_register") != "registry/2026-08-31_HZT_M0_ForwardMap_FM0_GapRegister_v0.2.json":
        errors.append("inventory does not bind Gap Register v0.2")

    params = inventory.get("parameter_set", [])
    if {p.get("symbol") for p in params if isinstance(p, dict)} != EXPECTED_PARAMETERS:
        errors.append("inventory parameter set changed")
    kappa = next((p for p in params if isinstance(p, dict) and p.get("symbol") == "kappa_6"), None)
    if not kappa:
        errors.append("inventory kappa_6 entry missing")
    else:
        if kappa.get("recovery_status") != KAPPA_STATUS:
            errors.append("inventory kappa_6 recovery status mismatch")
        if kappa.get("dimension") != "L^2 = M^-2":
            errors.append("inventory kappa_6 dimension mismatch")
        if kappa.get("parent_provenance") != "convention-registry.json::gravity":
            errors.append("inventory kappa_6 parent provenance mismatch")
        if kappa.get("mapping_status") != "PARENT_DEFINITION_RECOVERED_REDUCED_OBSERVABLE_MAPPING_OPEN":
            errors.append("inventory kappa_6 mapping must remain open downstream")
        if kappa.get("downstream_observables") != OPEN_RECOVERY:
            errors.append("inventory kappa_6 downstream observables must remain unresolved")
        for index, inference in enumerate(kappa.get("inferences", [])):
            if not isinstance(inference, dict) or inference.get("classification") != INFERENCE_CLASS or not str(inference.get("basis", "")).strip():
                errors.append(f"inventory kappa_6 inference #{index + 1} violates inference policy")

    for param in params:
        if not isinstance(param, dict) or param.get("symbol") == "kappa_6":
            continue
        if param.get("recovery_status") != OPEN_RECOVERY:
            errors.append(f"{param.get('symbol')}: targeted kappa_6 pass must not promote another parameter")
    a0 = next((p for p in params if isinstance(p, dict) and p.get("symbol") == "a0"), {})
    if a0.get("identity_with_A0") != "NO_IDENTITY_ASSERTED":
        errors.append("a0 lexical guard changed")

    observables = inventory.get("observable_blocks", [])
    if {o.get("id") for o in observables if isinstance(o, dict)} != EXPECTED_OBSERVABLES:
        errors.append("observable set changed")
    for obs in observables:
        if not isinstance(obs, dict):
            errors.append("observable entry must be object")
            continue
        if obs.get("recovery_status") != OPEN_RECOVERY or obs.get("provenance_class") != "PROGRAM_DECLARATION_ONLY":
            errors.append(f"{obs.get('id')}: targeted kappa_6 pass must not promote observable interface")

    gaps = gaps_doc.get("gaps", [])
    if not isinstance(gaps, list) or len(gaps) != 10:
        errors.append("Gap Register v0.2 must contain exactly 10 governed gaps")
        gaps = []
    gap_by_id = {g.get("id"): g for g in gaps if isinstance(g, dict)}
    kappa_gap = gap_by_id.get("FM0-GAP-005", {})
    if kappa_gap.get("blocking") is not True or kappa_gap.get("status") != KAPPA_GAP_STATUS:
        errors.append("FM0-GAP-005 must remain blocking with partial-resolution status")
    missing = set(kappa_gap.get("missing", []))
    required_missing = {
        "explicit_canonical_normalization_identity_to_M6_if_required",
        "parent_to_reduced_parameter_role",
        "downstream_observables",
    }
    if missing != required_missing:
        errors.append("FM0-GAP-005 remaining blockers changed")
    for gap_id, gap in gap_by_id.items():
        if gap_id == "FM0-GAP-005":
            continue
        if gap.get("blocking") is not True or gap.get("status") != OPEN_RECOVERY:
            errors.append(f"{gap_id}: non-kappa gap must remain open/blocking")
    blocking_count = sum(1 for gap in gaps if isinstance(gap, dict) and gap.get("blocking") is True)
    unresolved_count = sum(1 for gap in gaps if isinstance(gap, dict) and gap.get("status") == OPEN_RECOVERY)
    partial_count = sum(1 for gap in gaps if isinstance(gap, dict) and gap.get("status") == KAPPA_GAP_STATUS)
    if gaps_doc.get("blocking_gap_count") != blocking_count or blocking_count != 10:
        errors.append("blocking gap count must remain 10")
    if gaps_doc.get("fully_unresolved_blocking_gap_count") != unresolved_count or unresolved_count != 9:
        errors.append("fully unresolved blocking gap count must be 9")
    if gaps_doc.get("partially_resolved_blocking_gap_count") != partial_count or partial_count != 1:
        errors.append("partially resolved blocking gap count must be 1")

    # Scientific/authorization firewall is immutable for this provenance-only pass.
    if inventory.get("firewall") != EXPECTED_FIREWALL:
        errors.append("scientific/authorization firewall changed")
    for document_name, document in (("binding", binding), ("inventory", inventory), ("gaps", gaps_doc)):
        if document.get("physical_gate_effect") != "NONE":
            errors.append(f"{document_name}: physical_gate_effect must remain NONE")
        if document.get("physical_evidence_effect") != "NONE":
            errors.append(f"{document_name}: physical_evidence_effect must remain NONE")
    if inventory.get("cp01r4_state") != "FROZEN_NO_EXECUTION" or binding.get("cp01r4_state") != "FROZEN_NO_EXECUTION":
        errors.append("CP01R4 must remain FROZEN_NO_EXECUTION")

    if "FM-G0 = **OPEN**" not in report_text or "ALGEBRAIC_INFERENCE_NOT_CANONICAL_BINDING" not in report_text:
        errors.append("recovery report lacks required open-gate/inference declarations")

    if errors:
        print("HZT-M0 FM-0 kappa_6 Parent Recovery QA: FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("HZT-M0 FM-0 kappa_6 Parent Recovery QA: PASS")
    print("kappa_6 parent definition recovered from canonical convention registry")
    print("[kappa_6^2]=L^4=M^-4 direct; [kappa_6]=L^2=M^-2 algebraic")
    print("kappa_6 <-> M6 coefficient match remains noncanonical inference")
    print("FM0-GAP-005 remains blocking; FM-G0=OPEN; physical/release effect=NONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
