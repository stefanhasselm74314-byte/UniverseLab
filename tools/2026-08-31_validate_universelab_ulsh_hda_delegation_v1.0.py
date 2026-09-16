#!/usr/bin/env python3
"""Fail-closed QA for the UniverseLab ULSH HDA delegation v1.0.

Governance/provenance QA only. This script does not import a physics backend,
issue an AuthorizationDecision or SingleUseGrant, claim a nonce, execute a
solver, or create physical evidence.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry/2026-08-31_UniverseLab_ULSH_HDA_Delegation_v1.0.json"
DOCUMENT = ROOT / "governance/2026-08-31_UniverseLab_ULSH_HDA_Delegation_v1.0.md"
CANONICAL_STATE = ROOT / "registry/2026-09-04_UniverseLab_CurrentMainCanonicalState_v1.3.json"

# SHA-256 over UTF-8 canonical JSON:
# json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
# Lists retain sequence, so every governed field, list type, entry, duplicate,
# addition, omission, replacement, and order is pinned.
EXPECTED_REGISTRY_CANONICAL_SHA256 = (
    "714999ee0e552286c31535ae66d43c9b793c5ea5dde8c0f9cdd34e3e874a6d8c"
)
EXPECTED_DOCUMENT_SHA256 = (
    "52acdf0eba61595f22ce20fa1ad206772fe28213c1ebd409e8851b3cab8ef473"
)

EXPECTED_CANONICAL_BASIS = {
    "path": "registry/2026-09-04_UniverseLab_CurrentMainCanonicalState_v1.3.json",
    "schema": "universelab.current-main-canonical-state.v1",
    "version": "1.3.0",
    "snapshot_date": "2026-09-04",
    "status": "POST_BAND_VC_RECONCILED_CURRENT_STATE",
    "basis_main_commit": "3022dc8aac27ed2054fdb7643708fe57440b9256",
    "synchronization_class": "CURRENT_CANONICAL_NONEXECUTION_BASELINE",
}

EXPECTED_METHOD_PREPARATION = {
    "technical_authority_signature_verifier": "IMPLEMENTED_AND_QA_GREEN",
    "human_trust_root_preparation_package": "IMPLEMENTED_AND_QA_GREEN",
    "ratified_human_trust_root": "NOT_RATIFIED",
    "human_trust_root_action": "PARKED_UNTIL_EXCLUSIVELY_USER_CONTROLLED_COMPUTER_EXISTS",
    "authority_signature_provenance": "BLOCKED_PENDING_EXPLICIT_HUMAN_TRUST_ROOT_RATIFICATION",
    "runtime_issuance_bindings": "BLOCKED",
}

EXPECTED_FIREWALL = {
    "WP1": "CLOSED_TARGET_FROZEN_NO_EXECUTION",
    "WP2": "METHOD_AUTHORITY_PREPARATION_IMPLEMENTED_NOT_AUTHORIZED",
    "operative_AuthorizationDecision": "NOT_CREATED",
    "SingleUseGrant": "NOT_CREATED",
    "backend_import": "NOT_EXECUTED",
    "solver_run": "NOT_EXECUTED",
    "physical_background": "NOT_ESTABLISHED",
    "WP3": "NOT_STARTED",
    "WP4": "BLOCKED_NOT_AUTHORIZED",
    "rank_R": "NOT_EXECUTED",
    "K1-D": "NOT_RELEASED",
    "K1-E": "NOT_ADMISSIBLE",
}

EXPECTED_RESTART_ANCHORS = {
    "release_subject": "d8890b9ef47936edf8bb7e758b882c898241b314",
    "target": "237c4b5e08a2106e13e985c4af7925f1899e2ae2e4b7253c7ab73cc2db5f1823",
    "cp01r4_payload": "8e5976a22c4be78b5e4fe7834c9947de8a4acea7781363c7aeb83aa73982ac8c",
    "release_package_16_file": "1d6f45725a66b145d2907943ddc7fe3a989411e5ccfe6c0f29053c91253c7621",
}

CANONICAL_TO_FIREWALL = {
    "ULSH-01-WP1": "WP1",
    "ULSH-01-WP2": "WP2",
    "operative_authorization_decision": "operative_AuthorizationDecision",
    "operative_single_use_grant": "SingleUseGrant",
    "backend_import": "backend_import",
    "solver_execution": "solver_run",
    "physical_background": "physical_background",
    "ULSH-01-WP3": "WP3",
    "ULSH-01-WP4": "WP4",
    "physical_response_rank": "rank_R",
    "K1-D": "K1-D",
    "K1-E": "K1-E",
}

EXPECTED_AUTHORITY_HIERARCHY = [
    "CURRENT_EXPLICIT_CONSTITUTIONAL_OWNER_DECISION",
    "PROJECT_CONSTITUTION_AND_MD_0",
    "CURRENT_CANONICAL_REPOSITORY_REGISTRY_OR_GOVERNANCE_ARTIFACT",
    "CURRENT_RATIFIED_OR_FROZEN_PROJECT_FILE",
    "CURRENT_GOVERNED_HDA_DECISION_RECORD",
    "CURRENT_PROJECT_OR_CHAT_CONTEXT",
    "PERSISTENT_MEMORY",
    "HISTORICAL_CHATS_AND_EARLIER_ASSISTANT_SUMMARIES",
]

EXPECTED_ORDINARY_DECISIONS = [
    "PROCEED",
    "HOLD",
    "DENY",
    "REVISE",
    "ESCALATE_OWNER_RATIFICATION",
]
EXPECTED_FUTURE_EXECUTION_DECISIONS = [
    "RECOMMEND_GRANT",
    "HOLD",
    "DENY",
    "ESCALATE_OWNER_RATIFICATION",
]
EXPECTED_RESERVED_MATTERS = [
    "K1_D_K1_E_OR_EQUIVALENT_GATE_OPENING_RELEASE_OR_STATUS_PROMOTION",
    "AUTHORITY_IDENTITY_TRUST_ROOT_SIGNATURE_POLICY_OR_DELEGATION_CHANGE",
    "AUTHORIZATION_DECISION_SINGLE_USE_GRANT_BACKEND_IMPORT_OR_SOLVER_EXECUTION",
    "PHYSICAL_EVIDENCE_EXISTENCE_UNIQUENESS_STABILITY_GHOST_FREEDOM_OR_RESPONSE_RANK_CLAIM",
    "CANONICAL_FROZEN_RATIFIED_OR_PUBLICATION_STATUS_PROMOTION",
    "PUBLICATION_EXTERNAL_COMMITMENT_OR_MAXIMAL_PUBLIC_CLAIM",
    "PROJECT_CONSTITUTION_MD0_HPVS_HZT_ARCHITECTURE_OR_SCOPE_CHANGE",
    "MATERIAL_CHANGE_TO_FROZEN_TARGET_DIGEST_HOLD_OR_RESTART_ANCHOR",
]
EXPECTED_LAYER_IDS = [
    "SUBSTANTIVE_HDA",
    "DETERMINISTIC_POLICY_VALIDATOR",
    "CRYPTOGRAPHIC_DECISION_SIGNER",
    "SINGLE_USE_GRANT_ISSUER",
    "PERSISTENT_RESERVATION_STORE",
    "EXECUTION_HARNESS",
]

PUBLIC_PRIVACY_PATTERNS = {
    "chat_share_link": re.compile(r"https?://chatgpt\.com/share/", re.I),
    "conversation_metadata_key": re.compile(
        r"\b(?:source_)?conversation_ids?\b\s*[:=]", re.I
    ),
    "share_link_key": re.compile(r'"share_link"\s*:', re.I),
}


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON object keys instead of taking the last value."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def load_json_object(
    path: Path, errors: list[str], label: str
) -> tuple[dict[str, Any] | None, str]:
    if not path.is_file():
        errors.append(f"missing required {label}: {path.relative_to(ROOT)}")
        return None, ""
    try:
        text = path.read_text(encoding="utf-8")
        value = json.loads(text, object_pairs_hook=strict_object)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"cannot strictly parse {label} {path.relative_to(ROOT)}: {exc}")
        return None, ""
    if not isinstance(value, dict):
        errors.append(f"{label} top level must be an object")
        return None, text
    return value, text


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def read_path(value: dict[str, Any], *path: str) -> Any:
    current: Any = value
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def validate_registry(registry: dict[str, Any], errors: list[str]) -> None:
    require(
        canonical_sha256(registry) == EXPECTED_REGISTRY_CANONICAL_SHA256,
        "registry canonical content digest mismatch; governed content drifted",
        errors,
    )
    require(
        registry.get("schema") == "universelab.ulsh.hda-delegation.v1.0",
        "registry schema mismatch",
        errors,
    )
    require(
        registry.get("status")
        == "RATIFIED_LIMITED_NONOPERATIVE_GOVERNANCE_PENDING_CANONICAL_FORUM_ID",
        "registry status mismatch",
        errors,
    )
    require(
        registry.get("classification")
        == "LIMITED_GOVERNANCE_DELEGATION_NO_OPERATIONAL_AUTHORITY",
        "registry classification mismatch",
        errors,
    )
    require(
        registry.get("canonical_state_basis") == EXPECTED_CANONICAL_BASIS,
        "canonical state basis mismatch",
        errors,
    )
    require(
        registry.get("method_authority_preparation") == EXPECTED_METHOD_PREPARATION,
        "method/authority preparation state mismatch",
        errors,
    )
    require(
        read_path(registry, "delegating_principal", "role")
        == "CONSTITUTIONAL_PROJECT_OWNER_AND_DELEGATING_PRINCIPAL",
        "delegating principal role mismatch",
        errors,
    )
    require(
        read_path(registry, "delegating_principal", "routine_scientific_gate_decider")
        is False,
        "Stefan must not remain the routine scientific gate decider",
        errors,
    )
    require(
        read_path(
            registry,
            "delegating_principal",
            "exclusive_final_ratifier_for_reserved_matters",
        )
        is True,
        "Stefan must remain exclusive final ratifier for reserved matters",
        errors,
    )
    require(
        read_path(registry, "authority", "authority_id") == "HDA-ULSH-MBO-01",
        "authority ID mismatch",
        errors,
    )
    require(
        read_path(registry, "authority", "role")
        == "PRIMARY_ROUTINE_NONOPERATIVE_SCIENTIFIC_AND_SOLVER_GOVERNANCE_AUTHORITY",
        "authority role mismatch",
        errors,
    )
    require(
        read_path(registry, "authority", "forum_title")
        == "ACTIVE — ULSH Master Build Order — 14 Solver",
        "authority forum title mismatch",
        errors,
    )
    require(
        read_path(registry, "authority", "identity_binding_status")
        == "PENDING_CANONICAL_ID_BINDING",
        "identity binding must remain pending",
        errors,
    )
    require(
        read_path(registry, "authority", "nonoperative_substantive_authority") is True,
        "nonoperative substantive authority must be true",
        errors,
    )
    require(
        read_path(registry, "authority", "routine_nonoperative_decision_authority")
        is True,
        "routine nonoperative decision authority must be true",
        errors,
    )
    require(
        read_path(registry, "authority", "reserved_matter_final_decision_authority")
        is False,
        "HDA must not have final reserved-matter authority",
        errors,
    )
    require(
        read_path(registry, "authority", "may_unilaterally_hold_or_deny_reserved_matter")
        is True,
        "HDA must retain fail-closed HOLD/DENY authority",
        errors,
    )
    require(
        read_path(registry, "authority", "operative_authority") is False,
        "operative authority must remain false",
        errors,
    )
    require(
        read_path(registry, "authority", "assistant_instance_is_persistent_identity")
        is False,
        "assistant instance must not be treated as persistent identity",
        errors,
    )
    require(
        read_path(registry, "authority", "operational_status_on_identity_ambiguity")
        == "OPERATIONAL_AUTHORITY_SUSPENDED",
        "identity ambiguity must suspend operational authority",
        errors,
    )
    require(
        registry.get("authority_hierarchy") == EXPECTED_AUTHORITY_HIERARCHY,
        "authority hierarchy ordered contents mismatch",
        errors,
    )
    require(
        read_path(registry, "substantive_scope", "ordinary_decision_vocabulary")
        == EXPECTED_ORDINARY_DECISIONS,
        "ordinary decision vocabulary mismatch",
        errors,
    )
    require(
        read_path(registry, "substantive_scope", "future_execution_decision_vocabulary")
        == EXPECTED_FUTURE_EXECUTION_DECISIONS,
        "future execution recommendation vocabulary mismatch",
        errors,
    )
    require(
        read_path(
            registry,
            "substantive_scope",
            "future_RECOMMEND_GRANT_is_operative_AuthorizationDecision_or_SingleUseGrant",
        )
        is False,
        "HDA RECOMMEND_GRANT must not equal operative authorization or grant",
        errors,
    )
    require(
        read_path(
            registry,
            "substantive_scope",
            "may_open_release_promote_or_operationalize_reserved_matter",
        )
        is False,
        "HDA must not positively dispose reserved matters",
        errors,
    )
    require(
        read_path(registry, "reserved_matter_boundary", "owner_ratifier")
        == "STEFAN_HASSELMEYER",
        "reserved-matter owner ratifier mismatch",
        errors,
    )
    require(
        read_path(
            registry,
            "reserved_matter_boundary",
            "explicit_owner_ratification_required",
        )
        is True,
        "explicit owner ratification must be required",
        errors,
    )
    require(
        read_path(registry, "reserved_matter_boundary", "implied_consent_forbidden")
        is True,
        "implied owner consent must remain forbidden",
        errors,
    )
    require(
        read_path(
            registry,
            "reserved_matter_boundary",
            "bare_go_without_unambiguous_proposal_reference_is_insufficient",
        )
        is True,
        "unreferenced Go must remain insufficient for reserved ratification",
        errors,
    )
    require(
        read_path(registry, "reserved_matter_boundary", "reserved_matters")
        == EXPECTED_RESERVED_MATTERS,
        "reserved matters mismatch",
        errors,
    )
    require(
        read_path(registry, "substantive_scope", "evidence_bounded") is True,
        "substantive authority must remain evidence-bounded",
        errors,
    )

    layers = registry.get("decision_to_execution_layers")
    require(isinstance(layers, list) and len(layers) == 6, "six layers required", errors)
    if isinstance(layers, list):
        require(
            [item.get("id") for item in layers if isinstance(item, dict)]
            == EXPECTED_LAYER_IDS,
            "decision-to-execution layer identity/order mismatch",
            errors,
        )
        require(
            [
                item.get("id")
                for item in layers
                if isinstance(item, dict)
                and item.get("substantive_scientific_discretion") is True
            ]
            == ["SUBSTANTIVE_HDA"],
            "only layer 1 may hold substantive scientific discretion",
            errors,
        )
        require(
            read_path(
                registry,
                "decision_to_execution_layers",
            )[0].get("reserved_matter_final_authority")
            is False,
            "layer 1 must not hold final reserved-matter authority",
            errors,
        )
        require(
            [
                item.get("id")
                for item in layers
                if isinstance(item, dict)
                and item.get("operational_execution_power") is True
            ]
            == ["EXECUTION_HARNESS"],
            "only the execution harness may hold operational execution power",
            errors,
        )

    require(
        read_path(registry, "signer_contract", "behavior")
        == "SIGN_EXACT_PAYLOAD_OR_REJECT",
        "signer behavior mismatch",
        errors,
    )
    require(
        read_path(
            registry,
            "signer_contract",
            "requires_explicit_owner_ratification_for_reserved_matter",
        )
        is True,
        "signer must require explicit owner ratification for reserved matters",
        errors,
    )
    for field in (
        "may_modify_payload",
        "may_summarize_payload",
        "may_reinterpret_decision",
        "may_repair_missing_fields",
        "may_upgrade_gate",
        "may_create_scientific_evidence",
    ):
        require(
            read_path(registry, "signer_contract", field) is False,
            f"signer {field} must remain false",
            errors,
        )

    require(registry.get("firewall") == EXPECTED_FIREWALL, "firewall mismatch", errors)
    require(
        registry.get("restart_anchors") == EXPECTED_RESTART_ANCHORS,
        "restart anchors changed",
        errors,
    )
    require(
        registry.get("cp01r4_state") == "METHOD_FROZEN_NO_EXECUTION",
        "CP01R4 state mismatch",
        errors,
    )
    require(
        registry.get("current_hold_shortened_or_retargeted") is False,
        "current hold must not be shortened or retargeted",
        errors,
    )
    require(
        registry.get("physical_gate_effect") == "NONE",
        "physical gate effect must remain NONE",
        errors,
    )
    require(
        registry.get("physical_evidence_effect") == "NONE",
        "physical evidence effect must remain NONE",
        errors,
    )


def validate_against_canonical_state(
    registry: dict[str, Any], canonical: dict[str, Any], errors: list[str]
) -> None:
    basis = registry.get("canonical_state_basis")
    require(isinstance(basis, dict), "canonical state basis must be an object", errors)
    if isinstance(basis, dict):
        for field in ("schema", "version", "snapshot_date", "status", "basis_main_commit"):
            require(
                basis.get(field) == canonical.get(field),
                f"canonical state basis field does not match current state: {field}",
                errors,
            )

    physical = canonical.get("physical_governance")
    require(isinstance(physical, dict), "canonical physical_governance missing", errors)
    firewall = registry.get("firewall")
    require(isinstance(firewall, dict), "delegation firewall missing", errors)
    if isinstance(physical, dict) and isinstance(firewall, dict):
        for canonical_key, firewall_key in CANONICAL_TO_FIREWALL.items():
            require(
                firewall.get(firewall_key) == physical.get(canonical_key),
                f"delegation firewall stale versus canonical physical_governance: {firewall_key}",
                errors,
            )
        require(
            registry.get("cp01r4_state") == physical.get("CP01R4"),
            "delegation CP01R4 state stale versus canonical physical_governance",
            errors,
        )
        require(
            registry.get("method_authority_preparation")
            == {key: physical.get(key) for key in EXPECTED_METHOD_PREPARATION},
            "delegation method-authority preparation stale versus canonical state",
            errors,
        )
        require(
            physical.get("solver_authorized") is False,
            "canonical state unexpectedly authorizes solver execution",
            errors,
        )
        require(
            physical.get("physical_evidence_effect") == "NONE",
            "canonical physical evidence effect must remain NONE",
            errors,
        )

    require(
        canonical.get("physical_gate_effect") == "NONE",
        "canonical physical gate effect must remain NONE",
        errors,
    )
    require(
        canonical.get("physical_evidence_effect") == "NONE",
        "canonical top-level physical evidence effect must remain NONE",
        errors,
    )


def main() -> int:
    errors: list[str] = []
    registry, registry_text = load_json_object(REGISTRY, errors, "delegation registry")
    canonical, _ = load_json_object(CANONICAL_STATE, errors, "canonical state")

    if not DOCUMENT.is_file():
        errors.append(f"missing governance document: {DOCUMENT.relative_to(ROOT)}")
        document_text = ""
    else:
        document_text = DOCUMENT.read_text(encoding="utf-8")
        require(
            hashlib.sha256(document_text.encode("utf-8")).hexdigest()
            == EXPECTED_DOCUMENT_SHA256,
            "governance document content digest mismatch",
            errors,
        )

    for label, pattern in PUBLIC_PRIVACY_PATTERNS.items():
        if pattern.search(registry_text) or pattern.search(document_text):
            errors.append(f"public governance artifact contains forbidden privacy pattern: {label}")

    # Do not use truthiness here: an empty JSON object must still reach the
    # pinned validation and fail closed through its digest and required fields.
    if registry is not None:
        validate_registry(registry, errors)
    if registry is not None and canonical is not None:
        validate_against_canonical_state(registry, canonical, errors)

    for fragment in (
        "HDA-ULSH-MBO-01",
        "PRIMARY_ROUTINE_NONOPERATIVE_SCIENTIFIC_AND_SOLVER_GOVERNANCE_AUTHORITY",
        "ACTIVE — ULSH Master Build Order — 14 Solver",
        "PENDING_CANONICAL_ID_BINDING",
        "USER_DECLARED_REFERENCE_NOT_COMMITTED_PUBLICLY",
        "SIGN_EXACT_PAYLOAD_OR_REJECT",
        "OPERATIONAL_AUTHORITY_SUSPENDED",
        "registry/2026-09-04_UniverseLab_CurrentMainCanonicalState_v1.3.json",
        "WP2                            = METHOD_AUTHORITY_PREPARATION_IMPLEMENTED_NOT_AUTHORIZED",
        "ratified_human_trust_root               = NOT_RATIFIED",
        "runtime_issuance_bindings               = BLOCKED",
        "CP01R4                         = METHOD_FROZEN_NO_EXECUTION",
        "RATIFIED LIMITED ROUTINE NONOPERATIVE SCIENTIFIC AND SOLVER-GOVERNANCE AUTHORITY",
        "EXCLUSIVE FINAL RATIFIER FOR RESERVED MATTERS",
        "ESCALATE_OWNER_RATIFICATION",
        "RECOMMEND_GRANT",
        "CP01R4\n= METHOD_FROZEN_NO_EXECUTION",
        "physical gate effect\n= NONE",
        "physical evidence effect\n= NONE",
    ):
        require(fragment in document_text, f"governance document missing fragment: {fragment}", errors)

    if errors:
        print("ULSH HDA Delegation QA: FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("ULSH HDA Delegation QA: PASS")
    print(f"registry_canonical_sha256={EXPECTED_REGISTRY_CANONICAL_SHA256}")
    print("all governed registry content is exactly pinned")
    print("canonical_state=v1.3.0 and physical_governance cross-check=PASS")
    print("authority=HDA-ULSH-MBO-01")
    print("routine_nonoperative_authority=true reserved_matter_final_authority=false")
    print("exclusive_owner_final_ratifier=STEFAN_HASSELMEYER")
    print("operative_authority=false")
    print("identity_binding=PENDING_CANONICAL_ID_BINDING")
    print("WP2=METHOD_AUTHORITY_PREPARATION_IMPLEMENTED_NOT_AUTHORIZED")
    print("CP01R4=METHOD_FROZEN_NO_EXECUTION")
    print("physical_gate_effect=NONE physical_evidence_effect=NONE")
    print("PASS is limited-governance consistency, not owner ratification of a reserved matter, execution authorization, or physical evidence.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
