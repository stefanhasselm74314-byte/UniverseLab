#!/usr/bin/env python3
"""Fail-closed QA for the UniverseLab ULSH HDA delegation v1.0.

This is governance/provenance QA only. It does not import a physics backend,
issue an AuthorizationDecision or SingleUseGrant, claim a nonce, run a solver,
or create physical evidence.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry/2026-08-31_UniverseLab_ULSH_HDA_Delegation_v1.0.json"
DOCUMENT = ROOT / "governance/2026-08-31_UniverseLab_ULSH_HDA_Delegation_v1.0.md"

EXPECTED_STATUS = "RATIFIED_NONOPERATIVE_GOVERNANCE_PENDING_CANONICAL_FORUM_ID"
EXPECTED_CLASSIFICATION = "GOVERNANCE_DELEGATION_NO_OPERATIONAL_AUTHORITY"
EXPECTED_AUTHORITY_ID = "HDA-ULSH-MBO-01"
EXPECTED_AUTHORITY_ROLE = "PRIMARY_SCIENTIFIC_AND_SOLVER_GOVERNANCE_DECISION_AUTHORITY"
EXPECTED_FORUM_TITLE = "ACTIVE — ULSH Master Build Order — 14 Solver"
EXPECTED_IDENTITY_STATUS = "PENDING_CANONICAL_ID_BINDING"
EXPECTED_OWNER_ROLE = "CONSTITUTIONAL_PROJECT_OWNER_AND_DELEGATING_PRINCIPAL"
EXPECTED_DECISIONS = {
    "PROCEED",
    "HOLD",
    "DENY",
    "REVISE",
    "ESCALATE_CONSTITUTIONAL",
}
EXPECTED_FUTURE_EXECUTION_DECISIONS = {
    "GRANT",
    "HOLD",
    "DENY",
}
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
EXPECTED_LAYER_IDS = [
    "SUBSTANTIVE_HDA",
    "DETERMINISTIC_POLICY_VALIDATOR",
    "CRYPTOGRAPHIC_DECISION_SIGNER",
    "SINGLE_USE_GRANT_ISSUER",
    "PERSISTENT_RESERVATION_STORE",
    "EXECUTION_HARNESS",
]
EXPECTED_REQUIRED_DECISION_FIELDS = {
    "decision_id",
    "timestamp_utc",
    "authority_role_id",
    "forum_identity",
    "identity_binding_status",
    "policy_version",
    "canonical_subject_sha",
    "evidence_sources",
    "assumptions",
    "validity_regime",
    "decision",
    "rationale",
    "scope",
    "affected_gates",
    "unresolved_blockers",
    "forbidden_inferences",
    "conflict_or_dissent_notes",
    "physical_gate_effect",
    "physical_evidence_effect",
}
PUBLIC_PRIVACY_PATTERNS = {
    "chat_share_link": re.compile(r"https?://chatgpt\.com/share/", re.I),
    "conversation_metadata_key": re.compile(r"\b(?:source_)?conversation_ids?\b\s*[:=]", re.I),
    "share_link_key": re.compile(r'"share_link"\s*:', re.I),
}


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
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


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def require_exact_keys(obj: Any, keys: set[str], label: str, errors: list[str]) -> None:
    require(isinstance(obj, dict), f"{label} must be an object", errors)
    if isinstance(obj, dict):
        missing = sorted(keys - set(obj))
        if missing:
            errors.append(f"{label} missing keys: {missing}")


def main() -> int:
    errors: list[str] = []
    registry = load_json(REGISTRY, errors)
    if not DOCUMENT.is_file():
        errors.append(f"missing required file: {DOCUMENT.relative_to(ROOT)}")
        document_text = ""
    else:
        document_text = DOCUMENT.read_text(encoding="utf-8")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    registry_text = REGISTRY.read_text(encoding="utf-8")
    for label, pattern in PUBLIC_PRIVACY_PATTERNS.items():
        if pattern.search(registry_text) or pattern.search(document_text):
            errors.append(f"public governance artifact contains forbidden privacy pattern: {label}")

    require(registry.get("schema") == "universelab.ulsh.hda-delegation.v1.0",
            "registry schema mismatch", errors)
    require(registry.get("status") == EXPECTED_STATUS, "registry status mismatch", errors)
    require(registry.get("classification") == EXPECTED_CLASSIFICATION,
            "registry classification mismatch", errors)
    require(registry.get("physical_gate_effect") == "NONE",
            "registry physical_gate_effect must remain NONE", errors)
    require(registry.get("physical_evidence_effect") == "NONE",
            "registry physical_evidence_effect must remain NONE", errors)
    require(registry.get("cp01r4_state") == "FROZEN_NO_EXECUTION",
            "CP01R4 must remain FROZEN_NO_EXECUTION", errors)
    require(registry.get("current_hold_shortened_or_retargeted") is False,
            "current hold must not be shortened or retargeted", errors)

    owner = registry.get("delegating_principal")
    require_exact_keys(owner, {"name", "role", "routine_scientific_gate_decider", "retained_powers"},
                       "delegating_principal", errors)
    if isinstance(owner, dict):
        require(owner.get("role") == EXPECTED_OWNER_ROLE, "owner role mismatch", errors)
        require(owner.get("routine_scientific_gate_decider") is False,
                "Stefan must not remain routine scientific gate decider", errors)
        retained = owner.get("retained_powers")
        require(isinstance(retained, list) and len(retained) >= 4,
                "retained owner powers must be explicit", errors)

    authority = registry.get("authority")
    require_exact_keys(
        authority,
        {
            "authority_id", "role", "authority_class", "decision_agent",
            "assistant_instance_is_persistent_identity", "forum_title", "forum_reference",
            "identity_binding_status", "nonoperative_substantive_authority",
            "operative_authority", "operational_status_on_identity_ambiguity",
        },
        "authority",
        errors,
    )
    if isinstance(authority, dict):
        require(authority.get("authority_id") == EXPECTED_AUTHORITY_ID,
                "authority ID mismatch", errors)
        require(authority.get("role") == EXPECTED_AUTHORITY_ROLE,
                "authority role mismatch", errors)
        require(authority.get("authority_class") == "AI_ASSISTED_GOVERNED_DECISION_FORUM",
                "authority class mismatch", errors)
        require(authority.get("decision_agent") == "ASSISTANT_OPERATING_IN_GOVERNED_FORUM",
                "decision agent mismatch", errors)
        require(authority.get("assistant_instance_is_persistent_identity") is False,
                "assistant instance must not be treated as persistent identity", errors)
        require(authority.get("forum_title") == EXPECTED_FORUM_TITLE,
                "forum title mismatch", errors)
        require(authority.get("identity_binding_status") == EXPECTED_IDENTITY_STATUS,
                "identity binding must remain pending", errors)
        require(authority.get("nonoperative_substantive_authority") is True,
                "nonoperative substantive authority must be enabled", errors)
        require(authority.get("operative_authority") is False,
                "operative authority must remain false", errors)
        require(authority.get("operational_status_on_identity_ambiguity") == "OPERATIONAL_AUTHORITY_SUSPENDED",
                "identity ambiguity must suspend operational authority", errors)
        reference = authority.get("forum_reference")
        require_exact_keys(
            reference,
            {
                "reference_class", "public_locator", "private_locator_available_to_owner",
                "cryptographic_identity", "canonical_repository_identity",
            },
            "authority.forum_reference",
            errors,
        )
        if isinstance(reference, dict):
            require(reference.get("reference_class") == "USER_DECLARED_REFERENCE_NOT_COMMITTED_PUBLICLY",
                    "forum reference class mismatch", errors)
            require(reference.get("public_locator") == "REDACTED_BY_PUBLIC_PRIVACY_GATE",
                    "public forum locator must remain redacted", errors)
            require(reference.get("private_locator_available_to_owner") is True,
                    "owner-held private locator flag must be true", errors)
            require(reference.get("cryptographic_identity") is False,
                    "forum reference cannot be cryptographic identity", errors)
            require(reference.get("canonical_repository_identity") is False,
                    "forum reference cannot yet be canonical repository identity", errors)

    scope = registry.get("substantive_scope")
    require(isinstance(scope, dict), "substantive_scope must be an object", errors)
    if isinstance(scope, dict):
        require(set(scope.get("ordinary_decision_vocabulary", [])) == EXPECTED_DECISIONS,
                "ordinary decision vocabulary mismatch", errors)
        require(
            set(scope.get("future_execution_decision_vocabulary", []))
            == EXPECTED_FUTURE_EXECUTION_DECISIONS,
            "future execution decision vocabulary mismatch",
            errors,
        )
        require(scope.get("future_GRANT_is_operative_SingleUseGrant") is False,
                "future substantive GRANT must not equal operative SingleUseGrant", errors)
        require(scope.get("evidence_bounded") is True,
                "HDA scope must remain evidence-bounded", errors)
        allowed = set(scope.get("allowed_decisions", []))
        for required_item in {
            "ULSH_14_SOLVER_PRIORITIZATION_AND_SEQUENCE",
            "NEXT_ADMISSIBLE_WORK_PACKAGE_AND_BRANCH",
            "NO_GO_ABORT_ROLLBACK_AND_QUARANTINE",
            "MAXIMAL_SCIENTIFICALLY_WARRANTED_CLAIM",
        }:
            require(required_item in allowed, f"missing allowed HDA decision: {required_item}", errors)

    exclusions = set(registry.get("explicit_exclusions", []))
    for required_item in {
        "NO_OPERATIVE_AUTHORIZATION_DECISION_FROM_THIS_AMENDMENT",
        "NO_SINGLE_USE_GRANT_FROM_THIS_AMENDMENT",
        "NO_BACKEND_IMPORT",
        "NO_SOLVER_EXECUTION",
        "NO_PHYSICAL_EVIDENCE_FROM_GOVERNANCE",
        "NO_SILENT_RETARGETING_OF_FROZEN_DIGESTS",
    }:
        require(required_item in exclusions, f"missing explicit exclusion: {required_item}", errors)

    layers = registry.get("decision_to_execution_layers")
    require(isinstance(layers, list) and len(layers) == 6,
            "decision_to_execution_layers must contain exactly six layers", errors)
    if isinstance(layers, list) and len(layers) == 6:
        ordered = sorted(layers, key=lambda item: item.get("layer", 999) if isinstance(item, dict) else 999)
        require([item.get("layer") for item in ordered if isinstance(item, dict)] == [1, 2, 3, 4, 5, 6],
                "layer numbering mismatch", errors)
        require([item.get("id") for item in ordered if isinstance(item, dict)] == EXPECTED_LAYER_IDS,
                "layer identity/order mismatch", errors)
        discretionary = [
            item.get("id") for item in ordered
            if isinstance(item, dict) and item.get("substantive_scientific_discretion") is True
        ]
        require(discretionary == ["SUBSTANTIVE_HDA"],
                f"only layer 1 may have substantive discretion, got {discretionary}", errors)
        executable = [
            item.get("id") for item in ordered
            if isinstance(item, dict) and item.get("operational_execution_power") is True
        ]
        require(executable == ["EXECUTION_HARNESS"],
                f"only execution harness may have operational execution power, got {executable}", errors)

    signer = registry.get("signer_contract")
    require(isinstance(signer, dict), "signer_contract must be an object", errors)
    if isinstance(signer, dict):
        require(signer.get("behavior") == "SIGN_EXACT_PAYLOAD_OR_REJECT",
                "signer behavior mismatch", errors)
        for field in (
            "may_modify_payload", "may_summarize_payload", "may_reinterpret_decision",
            "may_repair_missing_fields", "may_upgrade_gate", "may_create_scientific_evidence",
        ):
            require(signer.get(field) is False, f"signer {field} must be false", errors)

    record = registry.get("decision_record_contract")
    require(isinstance(record, dict), "decision_record_contract must be an object", errors)
    if isinstance(record, dict):
        require(record.get("append_only") is True, "decision record must be append-only", errors)
        require(set(record.get("required_fields", [])) == EXPECTED_REQUIRED_DECISION_FIELDS,
                "decision record required fields mismatch", errors)

    fail_closed = set(registry.get("fail_closed_conditions", []))
    for required_item in {
        "PENDING_OR_AMBIGUOUS_CANONICAL_FORUM_IDENTITY",
        "DUPLICATE_LIVE_AUTHORITY_CLAIMANT",
        "MISSING_OR_MISMATCHED_POLICY_VERSION",
        "MISSING_OR_MISMATCHED_FROZEN_DIGEST",
        "AUTHORIZATION_OR_GRANT_REQUEST_DURING_CURRENT_HOLD",
    }:
        require(required_item in fail_closed, f"missing fail-closed condition: {required_item}", errors)
    require(registry.get("fail_closed_result") == "OPERATIONAL_AUTHORITY_SUSPENDED",
            "fail_closed_result mismatch", errors)

    activation = registry.get("future_operational_activation_requirements")
    require(isinstance(activation, list) and len(activation) >= 12,
            "future operational activation requirements are incomplete", errors)
    if isinstance(activation, list):
        for required_item in {
            "EXACT_CANONICAL_IDENTITY_BINDING_FOR_HDA_ULSH_MBO_01",
            "INDEPENDENT_DETERMINISTIC_POLICY_VALIDATION",
            "AUTHENTICATED_CRYPTOGRAPHIC_SIGNER_WITH_NO_SUBSTANTIVE_DISCRETION",
            "PERSISTENT_ATOMIC_RESERVATION_NONCE_STORE",
            "ONE_TIME_GRANT_AND_ATOMIC_CLAIM_BEFORE_BACKEND_IMPORT",
        }:
            require(required_item in activation,
                    f"missing future activation requirement: {required_item}", errors)

    require(registry.get("firewall") == EXPECTED_FIREWALL,
            "CP01R4 scientific/authorization firewall changed", errors)
    require(registry.get("restart_anchors") == EXPECTED_RESTART_ANCHORS,
            "CP01R4 restart anchors changed", errors)

    mandatory_document_fragments = [
        "HDA-ULSH-MBO-01",
        "PRIMARY_SCIENTIFIC_AND_SOLVER_GOVERNANCE_DECISION_AUTHORITY",
        "ACTIVE — ULSH Master Build Order — 14 Solver",
        "PENDING_CANONICAL_ID_BINDING",
        "USER_DECLARED_REFERENCE_NOT_COMMITTED_PUBLICLY",
        "SIGN_EXACT_PAYLOAD_OR_REJECT",
        "OPERATIONAL_AUTHORITY_SUSPENDED",
        "RATIFIED NONOPERATIVE SCIENTIFIC AND SOLVER-GOVERNANCE AUTHORITY",
        "CP01R4                         = FROZEN_NO_EXECUTION",
        "physical gate effect\n= NONE",
        "physical evidence effect\n= NONE",
    ]
    for fragment in mandatory_document_fragments:
        require(fragment in document_text, f"governance document missing fragment: {fragment}", errors)

    if errors:
        print("ULSH HDA Delegation QA: FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("ULSH HDA Delegation QA: PASS")
    print(f"authority={EXPECTED_AUTHORITY_ID} forum={EXPECTED_FORUM_TITLE}")
    print("substantive_nonoperative_authority=true operative_authority=false")
    print("identity_binding=PENDING_CANONICAL_ID_BINDING; ambiguity => OPERATIONAL_AUTHORITY_SUSPENDED")
    print("layers=6; substantive_discretion=layer1_only; signer=SIGN_EXACT_PAYLOAD_OR_REJECT")
    print("CP01R4=FROZEN_NO_EXECUTION; physical_gate_effect=NONE; physical_evidence_effect=NONE")
    print("PASS means the delegation is represented consistently, not that execution is authorized.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
