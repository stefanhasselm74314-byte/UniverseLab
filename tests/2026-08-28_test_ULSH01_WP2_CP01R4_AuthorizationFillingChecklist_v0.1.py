#!/usr/bin/env python3
"""Fail-closed QA for the nonoperative CP01R4 decision/grant filling checklist.

This test uses only the Python standard library. It must not import a physical
backend, create an authorization decision or grant, reserve a nonce, or call a
solver.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CHECKLIST_PATH = ROOT / "registry/2026-08-28_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_AuthorizationDecisionGrantFillingChecklist_v0.1.json"
DECISION_TEMPLATE_PATH = ROOT / "registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_AuthorizationDecisionSchema_v0.1.json"
GRANT_TEMPLATE_PATH = ROOT / "registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_SingleUseGrantSchema_v0.2.json"
RELEASE_MANIFEST_V02_PATH = ROOT / "registry/2026-08-28_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_ReleasePackageManifest_v0.2.json"
RELEASE_MANIFEST_V03_PATH = ROOT / "registry/2026-08-28_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_ReleasePackageManifest_v0.3.json"

RUN_ID = "HZT-M0-S6-C-PHYS-M1-ULSH01-WP2-CP01R4"
RELEASE_SUBJECT = "d8890b9ef47936edf8bb7e758b882c898241b314"
TARGET_DIGEST = "237c4b5e08a2106e13e985c4af7925f1899e2ae2e4b7253c7ab73cc2db5f1823"
RUN_PAYLOAD = "8e5976a22c4be78b5e4fe7834c9947de8a4acea7781363c7aeb83aa73982ac8c"
PACKAGE_DIGEST = "1d6f45725a66b145d2907943ddc7fe3a989411e5ccfe6c0f29053c91253c7621"

EXPECTED_MEMBER_HASHES = {
    "target_contract_file_sha256": (
        "ulsh/ULSH-01/C-PHYS/2026-08-21_ULSH01_M1C1_8x8_TargetContract_v0.1.json",
        "1b3f410e837371f11b50d8550c86c2d6409efeb25232114284f778754d1ae31f",
    ),
    "resource_policy_sha256": (
        "registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_ResourcePolicy_v0.2.json",
        "f01a4c13248dcc82d759da7ff291b68a3100bb7bec91d81cc515b6ff067c3fa7",
    ),
    "backend_rebind_contract_sha256": (
        "registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_BackendRebindContract_v0.2.json",
        "e60cc73cd3f1211dc8f4f504c427ac4f7b4dc59587d88ad1be4d710089b294a8",
    ),
    "result_schema_sha256": (
        "ulsh/ULSH-01/C-PHYS/2026-08-27_ULSH01_M1C1_8x8_ResultSchema_v0.1.json",
        "c9ed6807d36872ebcb2070d861fe472f4fd168b0c2f3abd630bbd3250d1d581d",
    ),
    "backend_interface_contract_sha256": (
        "ulsh/ULSH-01/C-PHYS/2026-08-27_ULSH01_M1C1_8x8_BackendInterfaceContract_v0.1.json",
        "ce40d78f3ab50ebab5ca2bc7d43b86ab54371a492bfab6a8bedb6e1d0de23048",
    ),
    "dependency_lock_sha256": (
        "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C_v0.1.txt",
        "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f",
    ),
    "primary_source_sha256": (
        "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py",
        "8ce1c0eceed64245d091d4bed492f3cf2a9c8314f631a03045aaa9696fb11c92",
    ),
    "primary_base_source_sha256": (
        "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.1.py",
        "830d4b4fdd28c8888876125479df3542eeb3864d4328764feb96b5d34bd91599",
    ),
}


def load(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing file: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"top-level JSON object required: {path.name}")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    checklist = load(CHECKLIST_PATH)
    decision_template = load(DECISION_TEMPLATE_PATH)
    grant_template = load(GRANT_TEMPLATE_PATH)
    release_v02 = load(RELEASE_MANIFEST_V02_PATH)
    release_v03 = load(RELEASE_MANIFEST_V03_PATH)

    require(
        checklist.get("schema")
        == "universelab.hzt-m0-s6-c-phys-m1.ulsh01-wp2-authorization-decision-grant-filling-checklist.v0.1",
        "checklist schema mismatch",
    )
    require(
        checklist.get("status")
        == "CHECKLIST_COMPLETE_AUTHORITY_AND_RUNTIME_ISSUANCE_INPUTS_UNRESOLVED_NOT_AUTHORIZED",
        "checklist status mismatch",
    )

    identity = checklist["frozen_release_identity"]
    require(identity["run_id"] == RUN_ID, "run identity drift")
    require(identity["release_subject_repository_commit_sha"] == RELEASE_SUBJECT, "release-subject drift")
    require(identity["target_contract_digest_sha256"] == TARGET_DIGEST, "target digest drift")
    require(identity["run_payload_sha256"] == RUN_PAYLOAD, "run payload drift")
    require(identity["release_package_manifest_sha256"] == PACKAGE_DIGEST, "package digest drift")
    require(identity["release_package_member_count"] == 16, "package member-count drift")
    require(identity["later_review_or_checklist_commit_retargets_release_subject"] is False, "silent retargeting enabled")

    require(release_v03["run_id"] == RUN_ID, "release v0.3 run mismatch")
    require(release_v03["release_subject_repository_commit_sha"] == RELEASE_SUBJECT, "release v0.3 subject mismatch")
    require(release_v03["target_contract_digest_sha256"] == TARGET_DIGEST, "release v0.3 target mismatch")
    require(release_v03["run_payload_sha256"] == RUN_PAYLOAD, "release v0.3 payload mismatch")
    require(release_v03["package_digest_sha256"] == PACKAGE_DIGEST, "release v0.3 package mismatch")
    require(release_v03["member_count"] == 16, "release v0.3 member-count mismatch")
    require(release_v03["execution_state"]["solver_executed"] is False, "release manifest reports solver execution")
    require(release_v03["execution_state"]["backend_imported"] is False, "release manifest reports backend import")

    member_hashes = release_v02["member_sha256"]
    for checklist_key, (member_path, expected_hash) in EXPECTED_MEMBER_HASHES.items():
        require(identity[checklist_key] == expected_hash, f"checklist {checklist_key} drift")
        require(member_hashes[member_path] == expected_hash, f"release-member {member_path} drift")

    decision = checklist["authorization_decision"]
    decision_source = decision_template["decision"]
    require(decision_template["status"] == "TEMPLATE_ONLY_NOT_AUTHORIZED", "decision template became operative")
    require(decision_source["authorization_decision_id"] is None, "decision ID unexpectedly filled")
    require(decision_source["decision_status"] == "NOT_AUTHORIZED", "decision template status changed")
    require(decision["current_artifact_created"] is False, "checklist claims decision artifact exists")
    require(decision["current_operatively_authorized"] is False, "checklist claims operative decision")
    require(decision["unfilled_fields"]["authorization_decision_id"] is None, "checklist decision ID filled")
    require(decision["unfilled_fields"]["decision_status"] == "NOT_AUTHORIZED", "checklist decision status operative")
    require(decision["unfilled_fields"]["not_before_utc"] is None, "checklist decision start time filled")
    require(decision["unfilled_fields"]["expires_at_utc"] is None, "checklist decision expiry filled")

    for key in (
        "authorized_run_id",
        "authorized_scope",
        "target_contract_digest_sha256",
        "run_payload_sha256",
        "single_use_grant_required",
        "automatic_execution",
        "wp3_authorized",
        "wp4_authorized",
        "physical_response_rank_authorized",
        "K1_D_release_authorized",
        "K1_E_admissible",
    ):
        require(decision["prebound_fields"][key] == decision_source[key], f"decision field mismatch: {key}")

    grant = checklist["single_use_grant"]
    grant_source = grant_template["grant"]
    require(grant_template["status"] == "TEMPLATE_ONLY_NO_GRANT_CREATED", "grant template became operative")
    require(grant_source["grant_id"] is None and grant_source["nonce"] is None, "grant identity unexpectedly filled")
    require(grant_source["authorized"] is False, "grant template became authorized")
    require(grant_source["control_only"] is False, "grant control_only drift")
    require(grant["prebound_fields"]["authorized"] is False, "checklist grant became authorized")
    require(grant["prebound_fields"]["control_only"] is False, "checklist grant control_only drift")
    require(grant["current_artifact_created"] is False, "checklist claims operative grant exists")
    require(grant["current_operatively_authorized"] is False, "checklist claims operative grant")
    for key, value in grant["unfilled_fields"].items():
        require(value is None, f"unfilled grant field became populated: {key}")

    for key in (
        "single_use",
        "scope",
        "control_only",
        "authorized",
        "target_contract_digest_sha256",
        "run_payload_sha256",
        "dependency_lock_sha256",
        "primary_source_sha256",
        "primary_base_source_sha256",
        "target_a_F",
        "control_override_allowed",
        "automatic_authorization",
    ):
        require(grant["prebound_fields"][key] == grant_source[key], f"grant field mismatch: {key}")

    authority_keys = {
        "issuing_authority_id",
        "issuer_identity",
        "signer_identity",
        "signer_key_fingerprint",
        "trust_root",
        "signature_algorithm",
        "signature",
        "revocation_status",
    }
    require(authority_keys.isdisjoint(decision_source), "decision template unexpectedly contains partial authority fields")
    require(authority_keys.isdisjoint(grant_source), "grant template unexpectedly contains partial authority fields")
    authority_gate = checklist["authority_and_signature_provenance_gate"]
    require(authority_gate["status"].startswith("BLOCKED_MISSING_RATIFIED_ISSUING_AUTHORITY"), "authority gap not fail-closed")
    require(authority_gate["current_chat_command_is_operative_authorization"] is False, "chat command treated as authorization")
    require(authority_gate["assistant_or_automation_may_self_authorize"] is False, "self-authorization enabled")
    require(authority_gate["operative_decision_permitted_now"] is False, "operative decision permitted despite gap")

    runtime_gate = checklist["runtime_issuance_gate"]
    require(runtime_gate["status"] == "BLOCKED_RUNTIME_BINDINGS_NOT_YET_DESIGNATED", "runtime gate not blocked")
    require(runtime_gate["ephemeral_tmp_or_CI_store_allowed_for_operative_grant"] is False, "ephemeral operative store allowed")
    require(runtime_gate["operative_grant_permitted_now"] is False, "operative grant permitted despite runtime gaps")
    require(len(runtime_gate["unfilled_fields"]) >= 10, "runtime issuance checklist unexpectedly incomplete")

    state = checklist["current_gate_state"]
    require(state["ULSH-01-WP2"] == "READY_FOR_SEPARATE_AUTHORIZATION_DECISION_NOT_AUTHORIZED", "WP2 status drift")
    require(state["ULSH-01-WP3"] == "NOT_STARTED", "WP3 started")
    require(state["ULSH-01-WP4"] == "BLOCKED_NOT_AUTHORIZED", "WP4 unblocked")
    require(state["operative_authorization_decision_created"] is False, "operative decision claimed")
    require(state["operative_single_use_grant_created"] is False, "operative grant claimed")
    require(state["backend_imported"] is False, "backend import claimed")
    require(state["solver_executed"] is False, "solver execution claimed")
    require(state["physical_background"] == "NOT_ESTABLISHED", "physical background promoted")
    require(state["K1-D"] == "NOT_RELEASED", "K1-D promoted")
    require(state["K1-E"] == "NOT_ADMISSIBLE", "K1-E promoted")
    require(state["physical_evidence_effect"] == "NONE", "physical evidence effect changed")

    result = {
        "status": "PASS_NONOPERATIVE_FILLING_CHECKLIST_QA_AUTHORITY_GATE_BLOCKED_NO_EXECUTION",
        "run_id": RUN_ID,
        "release_subject_repository_commit_sha": RELEASE_SUBJECT,
        "target_contract_digest_sha256": TARGET_DIGEST,
        "run_payload_sha256": RUN_PAYLOAD,
        "release_package_manifest_sha256": PACKAGE_DIGEST,
        "technical_field_mapping": "COMPLETE",
        "authority_signature_provenance": "BLOCKED",
        "runtime_issuance_bindings": "BLOCKED",
        "operative_authorization_decision_created": False,
        "operative_single_use_grant_created": False,
        "backend_imported": False,
        "solver_executed": False,
        "physical_background": "NOT_ESTABLISHED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
