#!/usr/bin/env python3
"""Prepare public-key-only ULSH-01 trust-root candidate artifacts.

The tool never reads, creates, stores or uses a private key and contains no
signing API. It only emits the exact bytes an offline human-controlled signer
may sign with a separate RFC-8032 implementation.
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
ALLOWED_ROLES = {
    "TRUST_ROOT_RATIFIER",
    "AUTHORIZATION_DECISION_ISSUER",
    "SINGLE_USE_GRANT_ISSUER",
}


class PreparationError(RuntimeError):
    def __init__(self, code: str, message: str, detail: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.detail = detail or {}


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_public_key(path: Path) -> bytes:
    raw = path.read_bytes()
    if len(raw) == 32:
        key = raw
    else:
        try:
            key = base64.b64decode(raw.decode("ascii").strip(), validate=True)
        except Exception as exc:
            raise PreparationError("INVALID_PUBLIC_KEY_FILE", "expected 32 raw bytes or Base64 thereof") from exc
    if len(key) != 32:
        raise PreparationError("INVALID_PUBLIC_KEY_LENGTH", "Ed25519 public key must contain exactly 32 bytes")
    try:
        CORE._decode_point(key)
    except CORE.AuthorityVerificationError as exc:
        raise PreparationError(exc.code, str(exc), exc.detail) from exc
    return key


def utc(value: str, field: str) -> datetime:
    try:
        return CORE.parse_utc(value, field)
    except CORE.AuthorityVerificationError as exc:
        raise PreparationError(exc.code, str(exc), exc.detail) from exc


def identifier(value: str, field: str, pattern: Any) -> str:
    try:
        return CORE.require_string(value, field, pattern)
    except CORE.AuthorityVerificationError as exc:
        raise PreparationError(exc.code, str(exc), exc.detail) from exc


def roles(values: Iterable[str]) -> list[str]:
    result = sorted(set(values))
    if "TRUST_ROOT_RATIFIER" not in result:
        raise PreparationError("TRUST_ROOT_RATIFIER_ROLE_REQUIRED", "candidate root key must include TRUST_ROOT_RATIFIER")
    unknown = [value for value in result if value not in ALLOWED_ROLES]
    if unknown:
        raise PreparationError("UNKNOWN_AUTHORITY_ROLE", "unsupported role", {"roles": unknown})
    return result


def build_candidate(args: argparse.Namespace) -> int:
    public_key = read_public_key(Path(args.public_key_file))
    authority_id = identifier(args.authority_id, "authority_id", CORE.AUTHORITY_ID_RE)
    key_id = identifier(args.key_id, "key_id", CORE.KEY_ID_RE)
    selected_roles = roles(args.role)
    valid_from = utc(args.valid_from_utc, "valid_from_utc")
    valid_until = utc(args.valid_until_utc, "valid_until_utc")
    signed_at = utc(args.signed_at_utc, "signed_at_utc")
    proof_expires = utc(args.proof_expires_at_utc, "proof_expires_at_utc")
    if not valid_from < valid_until:
        raise PreparationError("INVALID_KEY_VALIDITY_WINDOW", "valid_from_utc must precede valid_until_utc")
    if not valid_from <= signed_at < valid_until:
        raise PreparationError("SIGNING_TIME_OUTSIDE_KEY_WINDOW", "signed_at_utc must lie inside key validity")
    if not signed_at < proof_expires <= valid_until:
        raise PreparationError("INVALID_PROOF_EXPIRY", "proof expiry must follow signing time and not exceed key validity")
    if len(args.challenge_nonce) < 16:
        raise PreparationError("WEAK_OR_MISSING_CHALLENGE_NONCE", "challenge nonce must contain at least 16 characters")
    identity = args.display_identity.strip()
    if not identity:
        raise PreparationError("MISSING_PROJECT_IDENTITY", "display identity or pseudonym is required")

    fingerprint = hashlib.sha256(public_key).hexdigest()
    candidate = {
        "schema": "universelab.hzt-m0-s6-c-phys-m1.ulsh01-wp2-human-trust-root-candidate.v0.1",
        "date": "2026-09-02",
        "classification": "HUMAN_CONTROLLED_TRUST_ROOT_CANDIDATE_NOT_RATIFIED",
        "status": "CANDIDATE_AWAITING_HUMAN_ADOPTION",
        "contract_id": CONTRACT_ID,
        "authority_signature_contract_id": AUTHORITY_CONTRACT_ID,
        "governed_run_id": RUN_ID,
        "ratified": False,
        "authorities": [{
            "authority_id": authority_id,
            "display_name_or_pseudonymous_project_identity": identity,
            "controller_class": "HUMAN_CONTROLLED_PROJECT_AUTHORITY_CLAIM_PENDING_MANUAL_REVIEW",
            "status": "CANDIDATE_NOT_RATIFIED",
            "roles": selected_roles,
            "keys": [{
                "key_id": key_id,
                "algorithm": "Ed25519-RFC8032",
                "public_key_base64": base64.b64encode(public_key).decode("ascii"),
                "public_key_fingerprint_sha256": fingerprint,
                "status": "CANDIDATE_NOT_RATIFIED",
                "valid_from_utc": args.valid_from_utc,
                "valid_until_utc": args.valid_until_utc,
                "revoked": False,
                "revoked_at_utc": None,
                "roles": selected_roles,
            }],
        }],
        "bootstrap": {
            "root_key_proof_of_possession_required": True,
            "project_owner_adoption_record_required": True,
            "manual_human_attribution_review_required": True,
            "new_versioned_ratified_artifact_required": True,
        },
        "firewall": {
            "this_candidate_establishes_an_authority": False,
            "this_candidate_is_a_ratified_trust_root": False,
            "operative_authorization_decision_allowed": False,
            "operative_single_use_grant_allowed": False,
            "runtime_issuance_allowed": False,
            "backend_import_allowed": False,
            "solver_execution_allowed": False,
            "physical_evidence_effect": "NONE",
        },
        "physical_gate_effect": "NONE",
        "physical_evidence_effect": "NONE",
    }

    out = Path(args.output_dir)
    candidate_path = out / "2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_HumanTrustRootCandidate_v0.1.json"
    dump(candidate_path, candidate)
    candidate_raw = raw_sha256(candidate_path)
    candidate_canonical = CORE.canonical_sha256(candidate)

    protected = {
        "artifact_type": "TRUST_ROOT_PROOF_OF_POSSESSION",
        "attestation_id": args.attestation_id,
        "authority_id": authority_id,
        "contract_id": CONTRACT_ID,
        "key_id": key_id,
        "profile": CORE.PROFILE_ID,
        "signed_at_utc": args.signed_at_utc,
    }
    payload = {
        "candidate_trust_root_raw_sha256": candidate_raw,
        "candidate_trust_root_canonical_sha256": candidate_canonical,
        "public_key_fingerprint_sha256": fingerprint,
        "challenge_nonce": args.challenge_nonce,
        "proof_statement": "I control the Ed25519 private key corresponding to this candidate public key; this proof alone does not establish project authority.",
        "expires_at_utc": args.proof_expires_at_utc,
        "governed_run_id": RUN_ID,
    }
    proof = {
        "schema": "universelab.hzt-m0-s6-c-phys-m1.ulsh01-wp2-root-key-proof-of-possession.v0.1",
        "date": "2026-09-02",
        "classification": "UNSIGNED_ROOT_KEY_PROOF_OF_POSSESSION_CANDIDATE",
        "status": "UNSIGNED_AWAITING_OFFLINE_HUMAN_CONTROLLED_KEY",
        "protected": protected,
        "payload": payload,
        "signature": {
            "algorithm": "Ed25519-RFC8032",
            "encoding": "base64",
            "attestation_id": args.attestation_id,
            "public_key_fingerprint_sha256": fingerprint,
            "signed_bytes_sha256": None,
            "value": None,
        },
        "domain_separator_utf8_plus_nul": "UNIVERSELAB-TRUST-ROOT-PROOF-OF-POSSESSION-V1\\u0000",
        "firewall": {
            "proof_of_possession_is_project_authority": False,
            "proof_of_possession_is_ratification": False,
            "operative_authorization_allowed": False,
            "backend_import_allowed": False,
            "solver_execution_allowed": False,
            "physical_evidence_effect": "NONE",
        },
    }
    proof_path = out / "2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_RootKeyProofOfPossession_v0.1.json"
    message_path = out / "2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_RootKeyProofOfPossessionMessage_v0.1.bin"
    dump(proof_path, proof)
    message = POP_DOMAIN + CORE.canonical_bytes({"protected": protected, "payload": payload})
    message_path.write_bytes(message)
    summary = {
        "status": "CANDIDATE_AND_UNSIGNED_PROOF_PREPARED_NO_RATIFICATION",
        "candidate": str(candidate_path),
        "candidate_raw_sha256": candidate_raw,
        "candidate_canonical_sha256": candidate_canonical,
        "proof": str(proof_path),
        "signed_message": str(message_path),
        "signed_message_sha256": hashlib.sha256(message).hexdigest(),
        "public_key_fingerprint_sha256": fingerprint,
        "private_key_processed": False,
        "signature_created": False,
        "trust_root_ratified": False,
        "operative_authorization_allowed": False,
        "physical_evidence_effect": "NONE",
    }
    dump(out / "2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_HumanTrustRootCandidatePreparationSummary_v0.1.json", summary)
    print(json.dumps(summary, sort_keys=True, indent=2))
    return 0


def verify_pop(candidate: dict[str, Any], proof: dict[str, Any], candidate_path: Path, proof_path: Path, now: datetime) -> None:
    if candidate.get("ratified") is not False or candidate.get("status") != "CANDIDATE_AWAITING_HUMAN_ADOPTION":
        raise PreparationError("CANDIDATE_STATUS_NOT_PREPARATORY", "candidate must remain non-ratified")
    authorities = candidate.get("authorities")
    if not isinstance(authorities, list) or len(authorities) != 1:
        raise PreparationError("INVALID_CANDIDATE_AUTHORITY_COUNT", "candidate must contain exactly one authority")
    authority = authorities[0]
    keys = authority.get("keys")
    if not isinstance(keys, list) or len(keys) != 1:
        raise PreparationError("INVALID_CANDIDATE_KEY_COUNT", "candidate must contain exactly one key")
    key = keys[0]
    try:
        public_key = base64.b64decode(key["public_key_base64"], validate=True)
        signature = base64.b64decode(proof["signature"]["value"], validate=True)
    except Exception as exc:
        raise PreparationError("INVALID_BASE64", "invalid public-key or signature Base64") from exc
    fingerprint = hashlib.sha256(public_key).hexdigest()
    if fingerprint != key.get("public_key_fingerprint_sha256") or fingerprint != proof["signature"].get("public_key_fingerprint_sha256"):
        raise PreparationError("PUBLIC_KEY_FINGERPRINT_MISMATCH", "public-key fingerprint mismatch")
    signed = {"protected": proof.get("protected"), "payload": proof.get("payload")}
    message = POP_DOMAIN + CORE.canonical_bytes(signed)
    digest = hashlib.sha256(message).hexdigest()
    if digest != proof["signature"].get("signed_bytes_sha256"):
        raise PreparationError("SIGNED_BYTES_DIGEST_MISMATCH", "proof signed-bytes digest mismatch")
    if not CORE.ed25519_verify(public_key, message, signature):
        raise PreparationError("INVALID_PROOF_OF_POSSESSION_SIGNATURE", "Ed25519 proof-of-possession verification failed")
    payload = proof["payload"]
    if payload.get("candidate_trust_root_raw_sha256") != raw_sha256(candidate_path):
        raise PreparationError("CANDIDATE_RAW_DIGEST_MISMATCH", "proof does not bind candidate raw bytes")
    if payload.get("candidate_trust_root_canonical_sha256") != CORE.canonical_sha256(candidate):
        raise PreparationError("CANDIDATE_CANONICAL_DIGEST_MISMATCH", "proof does not bind candidate canonical bytes")
    if payload.get("public_key_fingerprint_sha256") != fingerprint:
        raise PreparationError("PROOF_FINGERPRINT_MISMATCH", "proof payload fingerprint mismatch")
    if proof["protected"].get("authority_id") != authority.get("authority_id") or proof["protected"].get("key_id") != key.get("key_id"):
        raise PreparationError("PROOF_IDENTITY_BINDING_MISMATCH", "proof authority/key binding mismatch")
    signed_at = utc(proof["protected"].get("signed_at_utc"), "proof.signed_at_utc")
    expires = utc(payload.get("expires_at_utc"), "proof.expires_at_utc")
    if not signed_at <= now < expires:
        raise PreparationError("PROOF_NOT_CURRENTLY_VALID", "proof is not valid at preparation time")
    if raw_sha256(proof_path) != raw_sha256(proof_path):
        raise AssertionError("unreachable")


def prepare_adoption(args: argparse.Namespace) -> int:
    candidate_path, proof_path = Path(args.candidate), Path(args.proof)
    candidate, proof = CORE.load_json(candidate_path), CORE.load_json(proof_path)
    adopted_at = utc(args.adopted_at_utc, "adopted_at_utc")
    verify_pop(candidate, proof, candidate_path, proof_path, adopted_at)
    authority = candidate["authorities"][0]
    key = authority["keys"][0]
    identity = args.project_identity.strip()
    if not identity:
        raise PreparationError("MISSING_PROJECT_IDENTITY", "project identity or pseudonym is required")
    if identity != authority["display_name_or_pseudonymous_project_identity"]:
        raise PreparationError("PROJECT_IDENTITY_BINDING_MISMATCH", "adoption identity must equal candidate project identity")
    self_review = str(args.single_human_self_review).lower()
    if self_review not in {"true", "false"}:
        raise PreparationError("INVALID_SELF_REVIEW_FLAG", "single-human self-review must be true or false")
    if not args.affirm_private_key_isolated:
        raise PreparationError("PRIVATE_KEY_CUSTODY_AFFIRMATION_REQUIRED", "explicit private-key isolation affirmation is required")

    adoption = {
        "schema": "universelab.hzt-m0-s6-c-phys-m1.ulsh01-wp2-project-owner-adoption-record.v0.1",
        "date": "2026-09-02",
        "classification": "PROJECT_OWNER_ADOPTION_RECORD_PREPARATION_NOT_RATIFICATION",
        "status": "ADOPTION_RECORD_PREPARED_MANUAL_ATTRIBUTION_REVIEW_REQUIRED",
        "contract_id": CONTRACT_ID,
        "adoption_id": args.adoption_id,
        "project_identity_or_pseudonym": identity,
        "adopted_at_utc": args.adopted_at_utc,
        "adoption_statement": "I explicitly adopt the exact candidate trust-root artifact identified by the bound digests for the stated project scope. This preparation record is not itself a ratified active trust root.",
        "governed_run_id": RUN_ID,
        "authority_binding": {
            "authority_id": authority["authority_id"],
            "key_id": key["key_id"],
            "public_key_fingerprint_sha256": key["public_key_fingerprint_sha256"],
            "root_key_proof_attestation_id": proof["protected"]["attestation_id"],
            "candidate_roles": key["roles"],
        },
        "candidate_binding": {
            "candidate_trust_root_raw_sha256": raw_sha256(candidate_path),
            "candidate_trust_root_canonical_sha256": CORE.canonical_sha256(candidate),
            "root_key_proof_raw_sha256": raw_sha256(proof_path),
            "root_key_proof_canonical_sha256": CORE.canonical_sha256(proof),
        },
        "repository_provenance": {
            "repository": "stefanhasselm74314-byte/UniverseLab",
            "commit_or_tag": args.repository_commit_or_tag,
            "commit_or_tag_verified": False,
            "verification_provider": args.verification_provider,
            "verification_reason": args.verification_reason,
            "verification_key_fingerprint_or_identity": None,
        },
        "human_attribution_review": {
            "status": "PENDING_MANUAL_REVIEW",
            "reviewed_by": None,
            "reviewed_at_utc": None,
            "review_notes": None,
            "single_human_project_self_review_disclosed": self_review == "true",
        },
        "custody_and_revocation": {
            "private_key_not_in_repository": True,
            "private_key_not_in_ci": True,
            "private_key_not_shared_with_assistant_or_chat": True,
            "offline_custody_location_class": args.custody_location_class,
            "backup_policy": args.backup_policy,
            "revocation_contact_or_procedure": args.revocation_procedure,
            "compromise_response": "fail closed; publish a versioned revocation artifact; block operational verification",
            "statements_are_human_assertions_not_machine_verified": True,
        },
        "ratified": False,
        "final_ratified_trust_root_artifact": None,
        "firewall": {
            "this_record_alone_is_ratification": False,
            "machine_verifier_may_assert_human_identity": False,
            "operative_authorization_allowed": False,
            "runtime_issuance_allowed": False,
            "backend_import_allowed": False,
            "solver_execution_allowed": False,
            "physical_evidence_effect": "NONE",
        },
        "physical_gate_effect": "NONE",
        "physical_evidence_effect": "NONE",
    }
    output = Path(args.output)
    dump(output, adoption)
    result = {
        "status": "ADOPTION_RECORD_PREPARED_MANUAL_HUMAN_RATIFICATION_REQUIRED",
        "output": str(output),
        "adoption_raw_sha256": raw_sha256(output),
        "adoption_canonical_sha256": CORE.canonical_sha256(adoption),
        "trust_root_ratified": False,
        "operative_authorization_allowed": False,
        "physical_evidence_effect": "NONE",
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    candidate = sub.add_parser("candidate")
    candidate.add_argument("--public-key-file", required=True)
    candidate.add_argument("--authority-id", required=True)
    candidate.add_argument("--display-identity", required=True)
    candidate.add_argument("--key-id", required=True)
    candidate.add_argument("--role", action="append", required=True)
    candidate.add_argument("--valid-from-utc", required=True)
    candidate.add_argument("--valid-until-utc", required=True)
    candidate.add_argument("--signed-at-utc", required=True)
    candidate.add_argument("--attestation-id", required=True)
    candidate.add_argument("--challenge-nonce", required=True)
    candidate.add_argument("--proof-expires-at-utc", required=True)
    candidate.add_argument("--output-dir", required=True)
    candidate.set_defaults(func=build_candidate)

    adoption = sub.add_parser("adoption")
    adoption.add_argument("--candidate", required=True)
    adoption.add_argument("--proof", required=True)
    adoption.add_argument("--adoption-id", required=True)
    adoption.add_argument("--project-identity", required=True)
    adoption.add_argument("--adopted-at-utc", required=True)
    adoption.add_argument("--repository-commit-or-tag", required=True)
    adoption.add_argument("--verification-provider", required=True)
    adoption.add_argument("--verification-reason", required=True)
    adoption.add_argument("--custody-location-class", required=True)
    adoption.add_argument("--backup-policy", required=True)
    adoption.add_argument("--revocation-procedure", required=True)
    adoption.add_argument("--single-human-self-review", required=True)
    adoption.add_argument("--affirm-private-key-isolated", action="store_true")
    adoption.add_argument("--output", required=True)
    adoption.set_defaults(func=prepare_adoption)
    return root


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(list(argv) if argv is not None else None)
    try:
        return int(args.func(args))
    except PreparationError as exc:
        print(json.dumps({
            "status": "FAIL_CLOSED",
            "error_code": exc.code,
            "message": str(exc),
            "detail": exc.detail,
            "trust_root_ratified": False,
            "operative_authorization_allowed": False,
            "backend_imported": False,
            "solver_executed": False,
            "physical_evidence_effect": "NONE",
        }, sort_keys=True, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
