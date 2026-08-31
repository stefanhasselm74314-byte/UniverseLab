#!/usr/bin/env python3
"""Fail-closed QA for the HZT-M0 FM-0 beta_tau recovery.

Governance and provenance QA only. This script does not import a physics
backend, execute a solver, create an authorization/grant, or produce physical
evidence.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "registry/2026-08-31_HZT_M0_ForwardMap_FM0_Inventory_v0.5.json"
GAPS = ROOT / "registry/2026-08-31_HZT_M0_ForwardMap_FM0_GapRegister_v0.4.json"
BINDING = ROOT / "registry/2026-08-31_HZT_M0_ForwardMap_FM0_BetaTauBinding_v0.1.json"
REPORT = ROOT / "2026-08-31_HZT_M0_ForwardMap_FM0_BetaTauParentRecovery_v0.1.md"
SCAN = ROOT / "tools/2026-08-31_scan_hzt_m0_fm0_beta_tau_provenance_v0.1.py"

GUIDE = ROOT / "guide.html"
COMPARE = ROOT / "compare-app.js"
HYPERLAB = ROOT / "hyperlab.html"
MD2F = ROOT / "science/hzt-m0/bridge/MD2F_H_I_INTEGRATION_AUDIT_v0.1.md"
MD2NQ = ROOT / "science/hzt-m0/bridge/MD2N_Q_PACKAGE_RIGOR_AUDIT_v0.1.md"
MD2P = ROOT / "science/hzt-m0/bridge/MD2P_CORR_OVERLAP_DERIVATION_v0.1.md"
LEGACY = ROOT / "legacy-formeln-H1-H64.csv"

EXPECTED_PARAMETERS = {"a0", "beta_tau", "R_chi", "I_B", "kappa_6"}
EXPECTED_OBSERVABLES = {"O_RAR", "O_cosmo", "O_growth", "O_lensing", "O_GW"}
EXPECTED_BETA_STATUS = (
    "PARTIALLY_RESOLVED_CURRENT_EFFECTIVE_PROXY_AND_MAPPING_ROLES_"
    "RECOVERED_PARENT_DERIVATION_OPEN"
)
EXPECTED_GAP_STATUS = (
    "PARTIALLY_RESOLVED_EFFECTIVE_PROXY_AND_MAPPING_ROLES_"
    "RECOVERED_PARENT_DERIVATION_OPEN"
)
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
EXPECTED_RESTART_ANCHORS = {
    "release_subject": "d8890b9ef47936edf8bb7e758b882c898241b314",
    "target": "237c4b5e08a2106e13e985c4af7925f1899e2ae2e4b7253c7ab73cc2db5f1823",
    "cp01r4_payload": "8e5976a22c4be78b5e4fe7834c9947de8a4acea7781363c7aeb83aa73982ac8c",
    "release_package_16_file": "1d6f45725a66b145d2907943ddc7fe3a989411e5ccfe6c0f29053c91253c7621",
}
CLOSED_GATE_STATES = {"CLOSED", "PASS", "PASSED", "RELEASED", "COMPLETE", "COMPLETED"}


def load_json(path: Path, errors: list[str]) -> dict:
    if not path.is_file():
        errors.append(f"missing required file: {path.relative_to(ROOT)}")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot parse {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"top-level JSON must be an object: {path.relative_to(ROOT)}")
        return {}
    return value


def require_file_fragments(path: Path, fragments: list[str], errors: list[str]) -> None:
    if not path.is_file():
        errors.append(f"missing source file: {path.relative_to(ROOT)}")
        return
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read {path.relative_to(ROOT)}: {exc}")
        return
    for fragment in fragments:
        if fragment not in text:
            errors.append(f"{path.relative_to(ROOT)} missing required fragment: {fragment}")


def entries_by_key(entries: object, key: str, errors: list[str], label: str) -> dict[str, dict]:
    if not isinstance(entries, list):
        errors.append(f"{label} must be a list")
        return {}
    result: dict[str, dict] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append(f"{label} entries must be objects")
            continue
        value = entry.get(key)
        if not isinstance(value, str) or not value:
            errors.append(f"{label} entry lacks string {key}")
            continue
        if value in result:
            errors.append(f"duplicate {label} {key}: {value}")
        result[value] = entry
    return result


def main() -> int:
    errors: list[str] = []
    inventory = load_json(INVENTORY, errors)
    gaps_doc = load_json(GAPS, errors)
    binding = load_json(BINDING, errors)

    for path in (REPORT, SCAN):
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")

    require_file_fragments(
        GUIDE,
        [
            "E²_eff(a) = E²_LCDM(a)·[1 + βτ·𝓘B·exp{−(a/a_c)²}]",
            "<strong>βτ:</strong> effektive Mischamplitude.",
            "βτ und 𝓘B treten nur als Produkt auf",
            "βτ → 0",
            "Korrektur verschwindet; ΛCDM wird reproduziert.",
        ],
        errors,
    )
    require_file_fragments(
        COMPARE,
        [
            "eq:'Δ(a)=βτ·𝓘B·exp[−(a/a_c)²]'",
            "status:'Modellabhängig'",
            "unit:'dimensionslos'",
            "Keine freigegebene fundamentale 6D-Vorhersage.",
        ],
        errors,
    )
    require_file_fragments(
        HYPERLAB,
        [
            "Die Kurven visualisieren ausschließlich die eingesetzten effektiven Ansätze.",
            "Sie sind keine aus der vollständigen 6D-Parentwirkung berechneten Vorhersagen.",
            "E²eff=E²ΛCDM[1+βτ 𝓘B exp{−(a/ac)²}]",
        ],
        errors,
    )
    require_file_fragments(
        MD2F,
        [
            "P_phys = (a₀, β_τ, R_χ, I_B, κ₆)",
            "### MDS-02: `(β_τ, I_B, κ₆) → ω_c`",
            "Einheiten und Normalisierungen von `β_τ` und `I_B`",
            "### MDS-03: `(a₀, β_τ, I_B) → η`",
            "### MDS-04: `(R_χ, β_τ) → s`",
            "K1-D  = NOT RELEASED",
            "K1-E  = NOT ADMISSIBLE",
        ],
        errors,
    )
    require_file_fragments(
        MD2NQ,
        [
            "MDS-02 | `beta_tau,I_B,kappa_6 -> omega_c`",
            "OPEN / BYPASSED",
            "MDS-03 | `a0,beta_tau,I_B -> eta`",
            "ALTERNATIVE EFFECTIVE ANSATZ, NOT DERIVED",
            "MDS-04 | `R_chi,beta_tau -> s`",
            "FIXED EFFECTIVE",
        ],
        errors,
    )
    require_file_fragments(
        MD2P,
        [
            "MDS-02 `beta_tau,I_B,kappa_6 -> omega_c` | not addressed | OPEN",
            "MDS-03 `a0,beta_tau,I_B -> eta` | replaced by a conditional partition-mixing ansatz",
            "MDS-04 `R_chi,beta_tau -> s` | not addressed; `s=2` remains fixed",
        ],
        errors,
    )
    require_file_fragments(
        LEGACY,
        [
            "H32;7.2 Effektive Driftgleichung;∂_τ ϑ = βϑ - λ_Θ ∇²ϑ;open",
            "H33;7.2 Effektive Driftgleichung;∇²ϑ - (β/λ_Θ)ϑ = 0;open",
            "H34;8.1 Kosmische Verankerung;a₀ = λ_Θ c β;historical",
            "H35;8.1 Kosmische Verankerung;β = H₀;historical",
            "H36;8.1 Kosmische Verankerung;a₀ = λ_Θ c H₀;historical",
            "H52;10. GW-Sektor;δφ(f) = β / f;open",
            "H53;10. GW-Sektor;β ↔ H₀;open",
        ],
        errors,
    )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    if inventory.get("schema") != "hzt-m0.forward-map.fm0.inventory.v0.5":
        errors.append("inventory schema must be v0.5")
    if inventory.get("supersedes") != "registry/2026-08-31_HZT_M0_ForwardMap_FM0_Inventory_v0.4.json":
        errors.append("inventory must supersede v0.4")
    if inventory.get("gate") != "FM-G0" or inventory.get("gate_status") != "OPEN":
        errors.append("inventory must keep FM-G0 = OPEN")
    if inventory.get("gap_register") != "registry/2026-08-31_HZT_M0_ForwardMap_FM0_GapRegister_v0.4.json":
        errors.append("inventory gap_register must point to v0.4")
    if inventory.get("physical_gate_effect") != "NONE" or inventory.get("physical_evidence_effect") != "NONE":
        errors.append("inventory physical effects must remain NONE")
    if inventory.get("cp01r4_state") != "FROZEN_NO_EXECUTION":
        errors.append("inventory must keep CP01R4 frozen")
    if inventory.get("firewall") != EXPECTED_FIREWALL:
        errors.append("inventory scientific/authorization firewall changed")
    if inventory.get("restart_anchors") != EXPECTED_RESTART_ANCHORS:
        errors.append("inventory restart anchors changed")

    by_symbol = entries_by_key(inventory.get("parameter_set"), "symbol", errors, "parameter_set")
    if set(by_symbol) != EXPECTED_PARAMETERS:
        errors.append(f"parameter symbols mismatch: {sorted(by_symbol)}")
    by_observable = entries_by_key(inventory.get("observable_blocks"), "id", errors, "observable_blocks")
    if set(by_observable) != EXPECTED_OBSERVABLES:
        errors.append(f"observable IDs mismatch: {sorted(by_observable)}")

    beta = by_symbol.get("beta_tau", {})
    if beta.get("recovery_status") != EXPECTED_BETA_STATUS:
        errors.append("beta_tau recovery_status mismatch")
    if beta.get("effective_dimension") != "1":
        errors.append("beta_tau effective dimension must be 1")
    if beta.get("effective_dimension_scope") != "CURRENT_MODEL_DEPENDENT_DIAGNOSTIC_IMPLEMENTATION_ONLY":
        errors.append("beta_tau effective dimension scope is not sufficiently restricted")
    if beta.get("physical_parent_dimension") != "OPEN_RECOVERY_REQUIRED":
        errors.append("beta_tau physical parent dimension must remain open")
    if beta.get("physical_parent_normalization") != "OPEN_RECOVERY_REQUIRED":
        errors.append("beta_tau physical parent normalization must remain open")
    if beta.get("parent_provenance") != "OPEN_RECOVERY_REQUIRED":
        errors.append("beta_tau parent provenance must remain open")
    if beta.get("blocking_gap") != "FM0-GAP-002":
        errors.append("beta_tau must bind FM0-GAP-002")
    if beta.get("binding_artifact") != "registry/2026-08-31_HZT_M0_ForwardMap_FM0_BetaTauBinding_v0.1.json":
        errors.append("beta_tau binding artifact path mismatch")

    identifiability = beta.get("identifiability")
    if not isinstance(identifiability, dict):
        errors.append("beta_tau identifiability block missing")
    else:
        if identifiability.get("current_effective_combination") != "beta_tau * I_B":
            errors.append("beta_tau-I_B effective combination changed")
        if identifiability.get("separate_beta_tau_I_B_identifiability") != "NO_IN_CURRENT_IMPLEMENTATION":
            errors.append("beta_tau-I_B degeneracy must remain explicit")

    edge_status = {
        edge.get("id"): edge.get("status")
        for edge in beta.get("declared_physical_mapping_edges", [])
        if isinstance(edge, dict)
    }
    expected_edges = {
        "MDS-02": "OPEN_CRITICAL_BLOCKER",
        "MDS-03": "OPEN_ALTERNATIVE_EFFECTIVE_ANSATZ_DOES_NOT_DERIVE_EDGE",
        "MDS-04": "OPEN_S_FIXED_EFFECTIVELY",
    }
    if edge_status != expected_edges:
        errors.append(f"beta_tau MDS edge states mismatch: {edge_status}")

    history = beta.get("historical_beta_context")
    if not isinstance(history, dict) or history.get("identity_with_beta_tau") != "NO_IDENTITY_ASSERTED":
        errors.append("legacy beta must not be identified with beta_tau")

    required_guards = {
        "NO_IDENTITY_WITH_LEGACY_DRIFT_BETA",
        "NO_IDENTITY_WITH_MD2S_POTENTIAL_BETA",
        "NO_IDENTITY_WITH_NORMAL_BUNDLE_BETA_I",
        "NO_IDENTITY_WITH_CONICAL_OR_METRIC_BETA",
        "NO_IDENTITY_WITH_BETA_0",
        "NO_IDENTITY_WITH_RG_BETA_FUNCTIONS",
    }
    if set(beta.get("notation_guards", [])) != required_guards:
        errors.append("beta_tau notation guards are incomplete or changed")

    if binding.get("schema") != "hzt-m0.forward-map.fm0.beta-tau-binding.v0.1":
        errors.append("binding schema mismatch")
    if binding.get("decision") != EXPECTED_BETA_STATUS:
        errors.append("binding decision mismatch")
    if binding.get("gap_status") != EXPECTED_GAP_STATUS or binding.get("gap_blocking") is not True:
        errors.append("binding must keep FM0-GAP-002 partially resolved and blocking")
    if binding.get("gate_status") != "OPEN":
        errors.append("binding must keep FM-G0 OPEN")
    if binding.get("physical_gate_effect") != "NONE" or binding.get("physical_evidence_effect") != "NONE":
        errors.append("binding physical effects must remain NONE")
    if binding.get("cp01r4_state") != "FROZEN_NO_EXECUTION":
        errors.append("binding must keep CP01R4 frozen")
    implementation = binding.get("current_effective_implementation")
    if not isinstance(implementation, dict):
        errors.append("binding current_effective_implementation missing")
    else:
        if implementation.get("effective_dimension") != "1":
            errors.append("binding effective dimension must be 1")
        if implementation.get("evidence_effect") != "NONE":
            errors.append("effective implementation must have no evidence effect")
        ident = implementation.get("identifiability")
        if not isinstance(ident, dict) or ident.get("separate_identifiability_in_current_bridge") != "NO":
            errors.append("binding must record beta_tau-I_B non-identifiability")

    physical = binding.get("current_physical_mapping_declaration")
    if not isinstance(physical, dict):
        errors.append("binding current_physical_mapping_declaration missing")
    else:
        if physical.get("physical_parent_definition") != "OPEN_RECOVERY_REQUIRED":
            errors.append("binding physical parent definition must remain open")
        if physical.get("physical_parent_dimension_and_normalization") != "OPEN_RECOVERY_REQUIRED":
            errors.append("binding physical parent dimension/normalization must remain open")
        if physical.get("parent_to_reduced_derivation") != "OPEN_RECOVERY_REQUIRED":
            errors.append("binding Parent-to-Reduced derivation must remain open")
        if physical.get("released_observable_mapping") != "NOT_RELEASED":
            errors.append("binding observable mapping must remain NOT_RELEASED")

    historical = binding.get("historical_beta_candidate")
    if not isinstance(historical, dict) or historical.get("identity_with_current_beta_tau") != "NO_IDENTITY_ASSERTED":
        errors.append("binding must separate historical beta from current beta_tau")

    gap_by_id = entries_by_key(gaps_doc.get("gaps"), "id", errors, "gaps")
    if len(gap_by_id) != 10:
        errors.append(f"gap register must contain 10 unique gaps, got {len(gap_by_id)}")
    if gaps_doc.get("blocking_gap_count") != 10:
        errors.append("blocking_gap_count must remain 10")
    if gaps_doc.get("partially_resolved_blocking_gap_count") != 3:
        errors.append("partially resolved gap count must be 3")
    if gaps_doc.get("fully_unresolved_blocking_gap_count") != 7:
        errors.append("fully unresolved gap count must be 7")
    if gaps_doc.get("gate_status") != "OPEN":
        errors.append("gap register must keep FM-G0 OPEN")
    if gaps_doc.get("cp01r4_state") != "FROZEN_NO_EXECUTION":
        errors.append("gap register must keep CP01R4 frozen")
    if gaps_doc.get("physical_gate_effect") != "NONE" or gaps_doc.get("physical_evidence_effect") != "NONE":
        errors.append("gap register physical effects must remain NONE")

    beta_gap = gap_by_id.get("FM0-GAP-002", {})
    if beta_gap.get("status") != EXPECTED_GAP_STATUS:
        errors.append("FM0-GAP-002 status mismatch")
    if beta_gap.get("blocking") is not True:
        errors.append("FM0-GAP-002 must remain blocking")
    if beta_gap.get("binding_artifact") != "registry/2026-08-31_HZT_M0_ForwardMap_FM0_BetaTauBinding_v0.1.json":
        errors.append("FM0-GAP-002 binding artifact mismatch")
    if not beta_gap.get("missing"):
        errors.append("FM0-GAP-002 must retain explicit missing requirements")

    open_blocking = [
        gap
        for gap in gap_by_id.values()
        if gap.get("blocking") is True
        and (
            gap.get("status") == "OPEN_RECOVERY_REQUIRED"
            or "OPEN" in str(gap.get("status", ""))
        )
    ]
    gate_states = {
        str(inventory.get("gate_status", "")).upper(),
        str(gaps_doc.get("gate_status", "")).upper(),
        str(binding.get("gate_status", "")).upper(),
    }
    if open_blocking and gate_states & CLOSED_GATE_STATES:
        errors.append("FM-G0 cannot be closed while blocking gaps remain open")
    if open_blocking and gate_states != {"OPEN"}:
        errors.append("all beta_tau recovery artifacts must keep FM-G0 OPEN")

    report_text = REPORT.read_text(encoding="utf-8") if REPORT.is_file() else ""
    for fragment in (
        EXPECTED_BETA_STATUS,
        "rank J_(beta_tau,I_B) <= 1",
        "legacy beta != current beta_tau",
        "FM-G0                      = OPEN",
        "CP01R4 = FROZEN_NO_EXECUTION",
        "physical evidence effect = `NONE`",
    ):
        if fragment not in report_text:
            errors.append(f"report missing required statement: {fragment}")

    policy = inventory.get("inference_policy")
    if not isinstance(policy, dict):
        errors.append("inventory inference_policy missing")
    else:
        if policy.get("implemented_effective_proxy_never_promotes_to_physical_parent_parameter_without_explicit_normalization_and_reduction") is not True:
            errors.append("effective-proxy promotion firewall missing")
        if policy.get("shared_symbol_spelling_is_not_parent_derivation") is not True:
            errors.append("shared-symbol firewall missing")

    if errors:
        print("FM-0 beta_tau Parent Recovery QA: FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("FM-0 beta_tau Parent Recovery QA: PASS")
    print("beta_tau=current dimensionless effective proxy + open MDS roles; 6D Parent derivation remains open")
    print("beta_tau/I_B structural proxy rank <= 1; legacy beta identity not asserted")
    print("blocking_gaps=10 partial=3 fully_unresolved=7 FM-G0=OPEN")
    print("CP01R4 remains frozen; physical/release effect=NONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
