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

# SHA-256 over UTF-8 canonical JSON:
# json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
# Lists retain their exact sequence. Therefore every list type, entry, duplicate,
# replacement, omission, addition and (for all lists) order is pinned. This is
# intentionally stricter than the minimum governance requirement.
EXPECTED_REGISTRY_CANONICAL_SHA256 = (
    "321ea2c1301936f02b0da484ef14ada224b4157abd60fb523a542668bb85cf34"
)

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
EXPECTED_FUTURE_EXECUTION_DECISIONS = ["GRANT", "HOLD", "DENY"]
EXPECTED_LAYER_IDS = [
    "SUBSTANTIVE_HDA",
    "DETERMINISTIC_POLICY_VALIDATOR",
    "CRYPTOGRAPHIC_DECISION_SIGNER",
    "SINGLE_USE_GRANT_ISSUER",
    "PERSISTENT_RESERVATION_STORE",
    "EXECUTION_HARNESS",
]
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

PUBLIC_PRIVACY_PATTERNS = {
    "chat_share_link": re.compile(r"https?://chatgpt\.com/share/", re.I),
    "conversation_metadata_key": re.compile(
        r"\b(?:source_)?conversation_ids?\b\s*[:=]", re.I
    ),
    "share_link_key": re.compile(r'"share_link"\s*:', re.I),
}


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON object keys rather than silently taking the last."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def load_registry(errors: list[str]) -> tuple[dict[str, Any], str]:
    if not REGISTRY.is_file():
        errors.append(f"missing required file: {REGISTRY.relative_to(ROOT)}")
        return {}, ""
    try:
        text = REGISTRY.read_text(encoding="utf-8")
        value = json.loads(text, object_pairs_hook=strict_object)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"cannot strictly parse {REGISTRY.relative_to(ROOT)}: {exc}")
        return {}, ""
    if not isinstance(value, dict):
        errors.append("registry top level must be an object")
        return {}, text
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


def validate_pinned_registry(registry: dict[str, Any], errors: list[str]) -> None:
    digest = canonical_sha256(registry)
    require(
        digest == EXPECTED_REGISTRY_CANONICAL_SHA256,
        "registry canonical content digest mismatch; governed fields or list contents drifted",
        errors,
    )

    require(
        read_path(registry, "status")
        == "RATIFIED_NONOPERATIVE_GOVERNANCE_PENDING_CANONICAL_FORUM_ID",
        "registry status mismatch",
        errors,
    )
    require(
        read_path(registry, "classification")
        == "GOVERNANCE_DELEGATION_NO_OPERATIONAL_AUTHORITY",
        "registry classification mismatch",
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
        read_path(registry, "authority", "authority_id") == "HDA-ULSH-MBO-01",
        "authority ID mismatch",
        errors,
    )
    require(
        read_path(registry, "authority", "role")
        == "PRIMARY_SCIENTIFIC_AND_SOLVER_GOVERNANCE_DECISION_AUTHORITY",
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
        read_path(registry, "authority_hierarchy") == EXPECTED_AUTHORITY_HIERARCHY,
        "authority hierarchy ordered contents mismatch",
        errors,
    )
    require(
        read_path(registry, "substantive_scope", "future_execution_decision_vocabulary")
        == EXPECTED_FUTURE_EXECUTION_DECISIONS,
        "future execution decision vocabulary mismatch",
        errors,
    )
    require(
        read_path(registry, "substantive_scope", "future_GRANT_is_operative_SingleUseGrant")
        is False,
        "substantive GRANT must not equal operative SingleUseGrant",
        errors,
    )
    require(
        read_path(registry, "substantive_scope", "evidence_bounded") is True,
        "substantive authority must remain evidence-bounded",
        errors,
    )

    layers = read_path(registry, "decision_to_execution_layers")
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

    require(registry.get("firewall") == EXPECTED_FIREWALL, "CP01R4 firewall changed", errors)
    require(
        registry.get("restart_anchors") == EXPECTED_RESTART_ANCHORS,
        "CP01R4 restart anchors changed",
        errors,
    )
    require(
        registry.get("cp01r4_state") == "FROZEN_NO_EXECUTION",
        "CP01R4 must remain frozen",
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


def main() -> int:
    errors: list[str] = []
    registry, registry_text = load_registry(errors)

    if not DOCUMENT.is_file():
        errors.append(f"missing required file: {DOCUMENT.relative_to(ROOT)}")
        document_text = ""
    else:
        document_text = DOCUMENT.read_text(encoding="utf-8")

    for label, pattern in PUBLIC_PRIVACY_PATTERNS.items():
        if pattern.search(registry_text) or pattern.search(document_text):
            errors.append(f"public governance artifact contains forbidden privacy pattern: {label}")

    if registry:
        validate_pinned_registry(registry, errors)

    for fragment in (
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
    ):
        require(fragment in document_text, f"governance document missing fragment: {fragment}", errors)

    if errors:
        print("ULSH HDA Delegation QA: FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("ULSH HDA Delegation QA: PASS")
    print(f"registry_canonical_sha256={EXPECTED_REGISTRY_CANONICAL_SHA256}")
    print("all governed registry fields and list contents are exactly pinned")
    print("authority=HDA-ULSH-MBO-01")
    print("substantive_nonoperative_authority=true operative_authority=false")
    print("identity_binding=PENDING_CANONICAL_ID_BINDING")
    print("CP01R4=FROZEN_NO_EXECUTION")
    print("physical_gate_effect=NONE physical_evidence_effect=NONE")
    print("PASS is governance consistency, not execution authorization or physical evidence.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
