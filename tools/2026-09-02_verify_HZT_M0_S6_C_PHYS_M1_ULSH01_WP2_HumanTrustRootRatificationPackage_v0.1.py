#!/usr/bin/env python3
"""Fail-closed verifier for the ULSH-01 human trust-root preparation package.

It can verify empty committed templates or cryptographic candidate bindings.
It deliberately rejects RATIFIED_ACTIVE and never authorizes runtime activity.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Iterable

CORE_PATH = Path(__file__).with_name(
    "2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_AuthorityVerificationCore_v0.1.py"
)
SPEC = importlib.util.spec_from_file_location("ul_authority_core", CORE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("AUTHORITY_VERIFICATION_CORE_LOAD_FAILED")
CORE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CORE
SPEC.loader.exec_module(CORE)

CONTRACT_ID = "ULSH01-WP2-HUMAN-TRUST-ROOT-RATIFICATION-PACKAGE-v0.1"
AUTHORITY_CONTRACT_ID = "ULSH01-WP2-AUTHORITY-SIGNATURE-PROVENANCE-v0.1"
RUN_ID = "HZT-M0-S6-C-PHYS-M1-ULSH01-WP2-CP01R4"
POP_DOMAIN = b"UNIVERSELAB-TRUST-ROOT-PROOF-OF-POSSESSION-V1\x00"
PREPARATION_PASS = "PASS_PREPARATION_ONLY_NO_RATIFICATION"
CANDIDATE_PASS = "PASS_CRYPTOGRAPHIC_BINDINGS_MANUAL_HUMAN_RATIFICATION_REQUIRED"


class PackageVerificationError(RuntimeError):
    def __init__(self, code: str, message: str, detail: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.detail = detail or {}


def fail(code: str, message: str, detail: dict[str, Any] | None = None) -> None:
    raise PackageVerificationError(code, message, detail)


def load(path: str | Path) -> dict[str, Any]:
    try:
        value = CORE.load_json(path)
    except CORE.AuthorityVerificationError as exc:
        fail(exc.code, str(exc), exc.detail)
    if not isinstance(value, dict):
        fail("INVALID_TOP_LEVEL_OBJECT", f"{path} must contain a JSON object")
    return value


def raw_sha(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_sha(value: Any) -> str:
    try:
        return CORE.canonical_sha256(value)
    except CORE.AuthorityVerificationError as exc:
        fail(exc.code, str(exc), exc.detail)


def parse_utc(value: Any, field: str) -> datetime:
    try:
        return CORE.parse_utc(value, field)
    except CORE.AuthorityVerificationError as exc:
        fail(exc.code, str(exc), exc.detail)


def require(condition: bool, code: str, message: str, detail: dict[str, Any] | None = None) -> None:
    if not condition:
        fail(code, message, detail)


def reject_ratified(value: dict[str, Any], label: str) -> None:
    status = value.get("status")
    require(value.get("ratified") is not True, "RATIFIED_STATE_FORBIDDEN", f"{label} may not set ratified=true")
    require(status != "RATIFIED_ACTIVE", "RATIFIED_STATE_FORBIDDEN", f"{label} may not use RATIFIED_ACTIVE")


def verify_contract(contract: dict[str, Any]) -> None:
    require(contract.get("contract_id") == CONTRACT_ID, "CONTRACT_ID_MISMATCH", "package contract id mismatch")
    require(contract.get("status") == "PREPARATION_ONLY_NOT_RATIFIED", "CONTRACT_STATUS_MISMATCH", "package contract must remain preparation-only")
    require(contract.get("physical_gate_effect") == "NONE", "PHYSICAL_GATE_FIREWALL_BROKEN", "physical gate effect must be NONE")
    require(contract.get("physical_evidence_effect") == "NONE", "PHYSICAL_EVIDENCE_FIREWALL_BROKEN", "physical evidence effect must be NONE")
    gates = contract.get("current_gate_state") or {}
    expected = {
        "ratified_human_trust_root": "NOT_RATIFIED",
        "runtime_issuance_bindings": "BLOCKED",
        "AuthorizationDecision": "NOT_CREATED",
        "SingleUseGrant": "NOT_CREATED",
        "backend_import": "NOT_EXECUTED",
        "solver_execution": "NOT_EXECUTED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
    }
    for key, value in expected.items():
        require(gates.get(key) == value, "GATE_STATE_MISMATCH", f"contract gate {key} mismatch")
    require(contract.get("verifier_statuses", {}).get("ratified_active_status_accepted_by_this_verifier") is False,
            "RATIFIED_ACCEPTANCE_FIREWALL_BROKEN", "this verifier must reject ratified-active state")


def verify_empty_templates(contract: dict[str, Any], candidate: dict[str, Any], proof: dict[str, Any], adoption: dict[str, Any]) -> dict[str, Any]:
    verify_contract(contract)
    require(candidate.get("status") == "EMPTY_TEMPLATE_NOT_A_TRUST_ROOT", "CANDIDATE_TEMPLATE_STATUS_MISMATCH", "candidate template status mismatch")
    require(candidate.get("ratified") is False, "CANDIDATE_TEMPLATE_RATIFIED", "candidate template must not be ratified")
    require(candidate.get("authorities") == [], "CANDIDATE_TEMPLATE_NOT_EMPTY", "candidate template authorities must be empty")
    require(proof.get("status") == "UNSIGNED_TEMPLATE_NO_PROOF", "PROOF_TEMPLATE_STATUS_MISMATCH", "proof template status mismatch")
    require(proof.get("signature", {}).get("value") is None, "PROOF_TEMPLATE_SIGNED", "proof template must be unsigned")
    require(adoption.get("status") == "EMPTY_TEMPLATE_NO_HUMAN_ADOPTION", "ADOPTION_TEMPLATE_STATUS_MISMATCH", "adoption template status mismatch")
    require(adoption.get("ratified") is False, "ADOPTION_TEMPLATE_RATIFIED", "adoption template must not be ratified")
    for label, value in (("candidate", candidate), ("proof", proof), ("adoption", adoption)):
        firewall = value.get("firewall") or {}
        require(firewall.get("operative_authorization_allowed", firewall.get("operative_authorization_decision_allowed")) is False,
                "OPERATIVE_FIREWALL_BROKEN", f"{label} operational authorization firewall must be false")
        require(firewall.get("backend_import_allowed") is False, "BACKEND_FIREWALL_BROKEN", f"{label} backend firewall must be false")
        require(firewall.get("solver_execution_allowed") is False, "SOLVER_FIREWALL_BROKEN", f"{label} solver firewall must be false")
    return safe_result(PREPARATION_PASS, {
        "templates_empty": True,
        "cryptographic_proof_present": False,
        "manual_human_ratification_required": True,
    })


def one_authority(candidate: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    authorities = candidate.get("authorities")
    require(isinstance(authorities, list) and len(authorities) == 1, "INVALID_AUTHORITY_COUNT", "candidate must contain exactly one authority")
    authority = authorities[0]
    keys = authority.get("keys") if isinstance(authority, dict) else None
    require(isinstance(keys, list) and len(keys) == 1, "INVALID_KEY_COUNT", "candidate must contain exactly one key")
    key = keys[0]
    require(isinstance(key, dict), "INVALID_KEY_OBJECT", "candidate key must be an object")
    return authority, key


def verify_candidate(
    contract_path: str | Path,
    candidate_path: str | Path,
    proof_path: str | Path,
    adoption_path: str | Path,
    now: datetime,
) -> dict[str, Any]:
    contract, candidate, proof, adoption = map(load, (contract_path, candidate_path, proof_path, adoption_path))
    verify_contract(contract)
    for label, value in (("candidate", candidate), ("proof", proof), ("adoption", adoption)):
        reject_ratified(value, label)

    require(candidate.get("contract_id") == CONTRACT_ID, "CANDIDATE_CONTRACT_MISMATCH", "candidate contract id mismatch")
    require(candidate.get("authority_signature_contract_id") == AUTHORITY_CONTRACT_ID, "AUTHORITY_CONTRACT_MISMATCH", "authority contract id mismatch")
    require(candidate.get("governed_run_id") == RUN_ID, "RUN_ID_MISMATCH", "candidate run id mismatch")
    require(candidate.get("status") == "CANDIDATE_AWAITING_HUMAN_ADOPTION", "CANDIDATE_STATUS_MISMATCH", "candidate must await human adoption")
    authority, key = one_authority(candidate)
    require(authority.get("status") == "CANDIDATE_NOT_RATIFIED" and key.get("status") == "CANDIDATE_NOT_RATIFIED",
            "CANDIDATE_AUTHORITY_STATUS_MISMATCH", "authority and key must remain candidates")
    require(authority.get("controller_class") == "HUMAN_CONTROLLED_PROJECT_AUTHORITY_CLAIM_PENDING_MANUAL_REVIEW",
            "CONTROLLER_CLASS_MISMATCH", "controller claim must remain pending manual review")
    roles = key.get("roles")
    require(isinstance(roles, list) and "TRUST_ROOT_RATIFIER" in roles, "TRUST_ROOT_ROLE_MISSING", "root key lacks TRUST_ROOT_RATIFIER")
    require(sorted(set(roles)) == roles, "NONCANONICAL_ROLE_LIST", "roles must be sorted and unique")
    require(authority.get("roles") == roles, "AUTHORITY_KEY_ROLE_MISMATCH", "authority and key roles differ")
    require(key.get("revoked") is False and key.get("revoked_at_utc") is None, "KEY_REVOKED", "candidate key is revoked")

    try:
        public_key = base64.b64decode(key.get("public_key_base64"), validate=True)
    except Exception as exc:
        fail("INVALID_PUBLIC_KEY_BASE64", "candidate public key is not valid Base64", {"exception": str(exc)})
    require(len(public_key) == 32, "INVALID_PUBLIC_KEY_LENGTH", "Ed25519 public key must be 32 bytes")
    try:
        CORE._decode_point(public_key)
    except CORE.AuthorityVerificationError as exc:
        fail(exc.code, str(exc), exc.detail)
    fingerprint = hashlib.sha256(public_key).hexdigest()
    require(fingerprint == key.get("public_key_fingerprint_sha256"), "PUBLIC_KEY_FINGERPRINT_MISMATCH", "candidate fingerprint mismatch")

    protected, payload, signature_block = proof.get("protected"), proof.get("payload"), proof.get("signature")
    require(isinstance(protected, dict) and isinstance(payload, dict) and isinstance(signature_block, dict), "INVALID_PROOF_STRUCTURE", "proof envelope is incomplete")
    require(proof.get("status") in {"SIGNED_AWAITING_HUMAN_ADOPTION", "SIGNED_PROOF_CANDIDATE"}, "PROOF_STATUS_MISMATCH", "proof must be signed but non-ratifying")
    require(protected.get("artifact_type") == "TRUST_ROOT_PROOF_OF_POSSESSION", "PROOF_TYPE_MISMATCH", "proof artifact type mismatch")
    require(protected.get("contract_id") == CONTRACT_ID and protected.get("profile") == CORE.PROFILE_ID, "PROOF_PROFILE_MISMATCH", "proof contract/profile mismatch")
    require(protected.get("authority_id") == authority.get("authority_id") and protected.get("key_id") == key.get("key_id"), "PROOF_IDENTITY_BINDING_MISMATCH", "proof authority/key binding mismatch")
    require(signature_block.get("attestation_id") == protected.get("attestation_id"), "ATTESTATION_ID_MISMATCH", "proof attestation id mismatch")
    require(signature_block.get("public_key_fingerprint_sha256") == fingerprint, "PROOF_FINGERPRINT_MISMATCH", "proof signature fingerprint mismatch")
    require(signature_block.get("algorithm") == "Ed25519-RFC8032" and signature_block.get("encoding") == "base64", "PROOF_SIGNATURE_METADATA_MISMATCH", "proof signature metadata mismatch")

    candidate_raw, candidate_canonical = raw_sha(candidate_path), canonical_sha(candidate)
    require(payload.get("candidate_trust_root_raw_sha256") == candidate_raw, "CANDIDATE_RAW_DIGEST_MISMATCH", "proof candidate raw digest mismatch")
    require(payload.get("candidate_trust_root_canonical_sha256") == candidate_canonical, "CANDIDATE_CANONICAL_DIGEST_MISMATCH", "proof candidate canonical digest mismatch")
    require(payload.get("public_key_fingerprint_sha256") == fingerprint, "PROOF_PAYLOAD_FINGERPRINT_MISMATCH", "proof payload fingerprint mismatch")
    require(payload.get("governed_run_id") == RUN_ID, "PROOF_RUN_ID_MISMATCH", "proof run id mismatch")
    require(isinstance(payload.get("challenge_nonce"), str) and len(payload["challenge_nonce"]) >= 16, "WEAK_CHALLENGE_NONCE", "proof nonce is too short")
    require(payload.get("proof_statement") == "I control the Ed25519 private key corresponding to this candidate public key; this proof alone does not establish project authority.",
            "PROOF_STATEMENT_MISMATCH", "proof statement mismatch")

    signed_at = parse_utc(protected.get("signed_at_utc"), "proof.signed_at_utc")
    expires = parse_utc(payload.get("expires_at_utc"), "proof.expires_at_utc")
    valid_from = parse_utc(key.get("valid_from_utc"), "key.valid_from_utc")
    valid_until = parse_utc(key.get("valid_until_utc"), "key.valid_until_utc")
    require(valid_from <= signed_at < valid_until, "SIGNING_TIME_OUTSIDE_KEY_WINDOW", "proof signing time lies outside key validity")
    require(signed_at <= now < expires <= valid_until, "PROOF_NOT_CURRENTLY_VALID", "proof is expired, future-dated or exceeds key validity")

    message = POP_DOMAIN + CORE.canonical_bytes({"protected": protected, "payload": payload})
    digest = hashlib.sha256(message).hexdigest()
    require(signature_block.get("signed_bytes_sha256") == digest, "SIGNED_BYTES_DIGEST_MISMATCH", "proof signed bytes digest mismatch")
    try:
        signature = base64.b64decode(signature_block.get("value"), validate=True)
    except Exception as exc:
        fail("INVALID_SIGNATURE_BASE64", "proof signature is not valid Base64", {"exception": str(exc)})
    require(len(signature) == 64, "INVALID_SIGNATURE_LENGTH", "Ed25519 signature must be 64 bytes")
    require(CORE.ed25519_verify(public_key, message, signature), "INVALID_PROOF_OF_POSSESSION_SIGNATURE", "root-key proof of possession is invalid")

    require(adoption.get("contract_id") == CONTRACT_ID and adoption.get("governed_run_id") == RUN_ID, "ADOPTION_SCOPE_MISMATCH", "adoption contract/run binding mismatch")
    require(adoption.get("status") == "ADOPTION_RECORD_PREPARED_MANUAL_ATTRIBUTION_REVIEW_REQUIRED", "ADOPTION_STATUS_MISMATCH", "adoption record must remain pending manual review")
    require(adoption.get("final_ratified_trust_root_artifact") is None, "FINAL_RATIFIED_ARTIFACT_FORBIDDEN", "preparation record may not name a ratified artifact")
    identity = authority.get("display_name_or_pseudonymous_project_identity")
    require(adoption.get("project_identity_or_pseudonym") == identity, "PROJECT_IDENTITY_BINDING_MISMATCH", "adoption identity differs from candidate")
    ab = adoption.get("authority_binding") or {}
    require(ab.get("authority_id") == authority.get("authority_id") and ab.get("key_id") == key.get("key_id"), "ADOPTION_AUTHORITY_BINDING_MISMATCH", "adoption authority/key mismatch")
    require(ab.get("public_key_fingerprint_sha256") == fingerprint, "ADOPTION_FINGERPRINT_MISMATCH", "adoption fingerprint mismatch")
    require(ab.get("root_key_proof_attestation_id") == protected.get("attestation_id"), "ADOPTION_ATTESTATION_MISMATCH", "adoption proof attestation mismatch")
    require(ab.get("candidate_roles") == roles, "ADOPTION_ROLE_BINDING_MISMATCH", "adoption roles mismatch")
    binding = adoption.get("candidate_binding") or {}
    require(binding.get("candidate_trust_root_raw_sha256") == candidate_raw, "ADOPTION_CANDIDATE_RAW_MISMATCH", "adoption candidate raw digest mismatch")
    require(binding.get("candidate_trust_root_canonical_sha256") == candidate_canonical, "ADOPTION_CANDIDATE_CANONICAL_MISMATCH", "adoption candidate canonical digest mismatch")
    require(binding.get("root_key_proof_raw_sha256") == raw_sha(proof_path), "ADOPTION_PROOF_RAW_MISMATCH", "adoption proof raw digest mismatch")
    require(binding.get("root_key_proof_canonical_sha256") == canonical_sha(proof), "ADOPTION_PROOF_CANONICAL_MISMATCH", "adoption proof canonical digest mismatch")
    review = adoption.get("human_attribution_review") or {}
    require(review.get("status") == "PENDING_MANUAL_REVIEW" and review.get("reviewed_by") is None and review.get("reviewed_at_utc") is None,
            "HUMAN_REVIEW_NOT_PENDING", "human attribution must remain pending")
    custody = adoption.get("custody_and_revocation") or {}
    for field in ("private_key_not_in_repository", "private_key_not_in_ci", "private_key_not_shared_with_assistant_or_chat"):
        require(custody.get(field) is True, "CUSTODY_ASSERTION_MISSING", f"missing custody assertion {field}")
    require(custody.get("statements_are_human_assertions_not_machine_verified") is True, "CUSTODY_SEMANTICS_MISMATCH", "custody statements must be labelled human assertions")
    adopted_at = parse_utc(adoption.get("adopted_at_utc"), "adoption.adopted_at_utc")
    require(signed_at <= adopted_at <= now, "ADOPTION_TIME_INVALID", "adoption time precedes proof or lies in the future")
    provenance = adoption.get("repository_provenance") or {}
    require(provenance.get("repository") == "stefanhasselm74314-byte/UniverseLab", "REPOSITORY_BINDING_MISMATCH", "adoption repository mismatch")
    require(isinstance(provenance.get("commit_or_tag"), str) and provenance["commit_or_tag"], "MISSING_REPOSITORY_PROVENANCE", "adoption commit/tag is required")
    require(provenance.get("commit_or_tag_verified") is False, "AUTOMATIC_IDENTITY_VERIFICATION_FORBIDDEN", "preparation verifier may not claim commit/tag identity verification")

    return safe_result(CANDIDATE_PASS, {
        "authority_id": authority.get("authority_id"),
        "key_id": key.get("key_id"),
        "public_key_fingerprint_sha256": fingerprint,
        "candidate_raw_sha256": candidate_raw,
        "candidate_canonical_sha256": candidate_canonical,
        "proof_raw_sha256": raw_sha(proof_path),
        "proof_canonical_sha256": canonical_sha(proof),
        "proof_of_possession_valid": True,
        "manual_human_attribution_review_status": "PENDING_MANUAL_REVIEW",
        "machine_verified_human_identity": False,
        "trust_root_ratified": False,
    })


def safe_result(status: str, detail: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "universelab.hzt-m0-s6-c-phys-m1.ulsh01-wp2-human-trust-root-package-verification-result.v0.1",
        "status": status,
        "detail": detail,
        "trust_root_ratified": False,
        "operative_authorization_allowed": False,
        "runtime_issuance_allowed": False,
        "AuthorizationDecision": "NOT_CREATED",
        "SingleUseGrant": "NOT_CREATED",
        "backend_imported": False,
        "solver_executed": False,
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_gate_effect": "NONE",
        "physical_evidence_effect": "NONE",
    }


def cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    draft = sub.add_parser("draft")
    draft.add_argument("--contract", required=True)
    draft.add_argument("--candidate-template", required=True)
    draft.add_argument("--proof-template", required=True)
    draft.add_argument("--adoption-template", required=True)
    candidate = sub.add_parser("candidate")
    candidate.add_argument("--contract", required=True)
    candidate.add_argument("--candidate", required=True)
    candidate.add_argument("--proof", required=True)
    candidate.add_argument("--adoption", required=True)
    candidate.add_argument("--now-utc", required=True)
    parser.add_argument("--output")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = cli().parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "draft":
            result = verify_empty_templates(load(args.contract), load(args.candidate_template), load(args.proof_template), load(args.adoption_template))
        else:
            result = verify_candidate(args.contract, args.candidate, args.proof, args.adoption, parse_utc(args.now_utc, "--now-utc"))
        text = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False)
        if args.output:
            Path(args.output).write_text(text + "\n", encoding="utf-8")
        print(text)
        return 0
    except PackageVerificationError as exc:
        result = safe_result("FAIL_CLOSED", {"error_code": exc.code, "message": str(exc), "error_detail": exc.detail})
        text = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False)
        if getattr(args, "output", None):
            Path(args.output).write_text(text + "\n", encoding="utf-8")
        print(text, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
