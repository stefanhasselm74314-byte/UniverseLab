#!/usr/bin/env python3
"""Fail-closed ULSH-01 WP2 authority attestation verifier; no signing API."""
from __future__ import annotations

import argparse
import base64
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Iterable

_CORE_PATH=Path(__file__).with_name("2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_AuthorityVerificationCore_v0.1.py")
_spec=importlib.util.spec_from_file_location("ul_authority_verification_core",_CORE_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError("AUTHORITY_VERIFICATION_CORE_LOAD_FAILED")
_core=importlib.util.module_from_spec(_spec)
sys.modules[_spec.name]=_core
_spec.loader.exec_module(_core)

AuthorityVerificationError=_core.AuthorityVerificationError
VerificationResult=_core.VerificationResult
CONTRACT_ID=_core.CONTRACT_ID
PROFILE_ID=_core.PROFILE_ID
DOMAIN_SEPARATOR=_core.DOMAIN_SEPARATOR
RUN_ID=_core.RUN_ID
TARGET_DIGEST=_core.TARGET_DIGEST
RUN_PAYLOAD_DIGEST=_core.RUN_PAYLOAD_DIGEST
KEY_ID_RE=_core.KEY_ID_RE
AUTHORITY_ID_RE=_core.AUTHORITY_ID_RE
strict_json_loads=_core.strict_json_loads
load_json=_core.load_json
canonical_bytes=_core.canonical_bytes
canonical_sha256=_core.canonical_sha256
parse_utc=_core.parse_utc
require_hex64=_core.require_hex64
require_mapping=_core.require_mapping
require_string=_core.require_string
ed25519_verify=_core.ed25519_verify

def _find_unique(items: Any, key: str, expected: str, missing_code: str) -> dict[str, Any]:
    if not isinstance(items, list):
        raise AuthorityVerificationError("INVALID_TRUST_ROOT", f"expected list for {key}")
    matches = [item for item in items if isinstance(item, dict) and item.get(key) == expected]
    if len(matches) != 1:
        raise AuthorityVerificationError(missing_code, f"expected exactly one {key}={expected!r}", {"matches": len(matches)})
    return matches[0]


def _required_role(artifact_type: str) -> str:
    roles = {
        "AUTHORIZATION_DECISION": "AUTHORIZATION_DECISION_ISSUER",
        "SINGLE_USE_GRANT": "SINGLE_USE_GRANT_ISSUER",
        "TRUST_ROOT_RATIFICATION": "TRUST_ROOT_RATIFIER",
    }
    try:
        return roles[artifact_type]
    except KeyError as exc:
        raise AuthorityVerificationError("UNSUPPORTED_ARTIFACT_TYPE", f"unsupported artifact type: {artifact_type}") from exc


def _verify_payload_bindings(payload: dict[str, Any], artifact_type: str, synthetic: bool) -> None:
    if payload.get("run_id") != RUN_ID:
        raise AuthorityVerificationError("RUN_ID_MISMATCH", "signed payload run_id mismatch")
    if payload.get("target_contract_digest_sha256") != TARGET_DIGEST:
        raise AuthorityVerificationError("TARGET_DIGEST_MISMATCH", "signed payload target digest mismatch")
    if payload.get("run_payload_sha256") != RUN_PAYLOAD_DIGEST:
        raise AuthorityVerificationError("RUN_PAYLOAD_DIGEST_MISMATCH", "signed payload run-payload digest mismatch")
    if not synthetic:
        require_hex64(payload.get("repository_commit_sha"), "payload.repository_commit_sha")
        require_hex64(payload.get("release_package_manifest_sha256"), "payload.release_package_manifest_sha256")
    if payload.get("automatic_execution") is not False:
        raise AuthorityVerificationError("AUTOMATIC_EXECUTION_FORBIDDEN", "signed payload must set automatic_execution=false")

    if artifact_type == "AUTHORIZATION_DECISION":
        require_string(payload.get("authorization_decision_id"), "payload.authorization_decision_id")
        if synthetic:
            if payload.get("decision_status") != "SYNTHETIC_CONTROL_ONLY_NO_AUTHORIZATION":
                raise AuthorityVerificationError("SYNTHETIC_DECISION_STATUS_MISMATCH", "synthetic decision status mismatch")
            if payload.get("authorized") is not False:
                raise AuthorityVerificationError("SYNTHETIC_AUTHORIZATION_FORBIDDEN", "synthetic decision cannot authorize")
        else:
            if payload.get("decision_status") != "AUTHORIZED_SINGLE_USE_WP2_CP01R4_PRIMARY_TARGET_EXECUTION":
                raise AuthorityVerificationError("OPERATIVE_DECISION_STATUS_MISMATCH", "operative decision status mismatch")
            if payload.get("authorized") is not True:
                raise AuthorityVerificationError("OPERATIVE_DECISION_NOT_AUTHORIZED", "operative decision authorized flag must be true")
    elif artifact_type == "SINGLE_USE_GRANT":
        require_string(payload.get("grant_id"), "payload.grant_id")
        require_string(payload.get("authorization_decision_id"), "payload.authorization_decision_id")
        require_string(payload.get("nonce"), "payload.nonce")
        if payload.get("single_use") is not True:
            raise AuthorityVerificationError("SINGLE_USE_REQUIRED", "grant must be single-use")
        if synthetic:
            if payload.get("scope") != "SYNTHETIC_CONTROL_ONLY_NO_BACKEND_IMPORT" or payload.get("authorized") is not False:
                raise AuthorityVerificationError("SYNTHETIC_GRANT_SCOPE_MISMATCH", "synthetic grant must remain non-authorizing")
        else:
            if payload.get("scope") != f"{RUN_ID}_TARGET_ONLY" or payload.get("authorized") is not True:
                raise AuthorityVerificationError("OPERATIVE_GRANT_SCOPE_MISMATCH", "operative grant scope/authorization mismatch")


def verify_envelope(
    contract: dict[str, Any],
    trust_root: dict[str, Any],
    envelope: dict[str, Any],
    *,
    expected_artifact_type: str,
    now: datetime | None = None,
) -> VerificationResult:
    contract_meta = require_mapping(contract, "contract")
    root = require_mapping(trust_root, "trust_root")
    env = require_mapping(envelope, "envelope")

    if contract_meta.get("contract_id") != CONTRACT_ID:
        raise AuthorityVerificationError("CONTRACT_ID_MISMATCH", "authority contract id mismatch")
    contract_status = contract_meta.get("status")
    root_status = root.get("status")
    synthetic = contract_status == "RATIFIED_SYNTHETIC_CONTROL_ONLY" and root_status == "RATIFIED_SYNTHETIC_CONTROL_ONLY"
    operative = contract_status == "RATIFIED_ACTIVE" and root_status == "RATIFIED_ACTIVE"
    if not (synthetic or operative):
        raise AuthorityVerificationError(
            "TRUST_ROOT_NOT_RATIFIED",
            "contract and trust root are not jointly ratified for verification",
            {"contract_status": contract_status, "trust_root_status": root_status},
        )

    if env.get("schema") != "universelab.signed-authority-envelope.v0.1":
        raise AuthorityVerificationError("ENVELOPE_SCHEMA_MISMATCH", "signed envelope schema mismatch")
    protected = require_mapping(env.get("protected"), "envelope.protected")
    payload = require_mapping(env.get("payload"), "envelope.payload")
    signature_block = require_mapping(env.get("signature"), "envelope.signature")

    artifact_type = require_string(protected.get("artifact_type"), "protected.artifact_type")
    if artifact_type != expected_artifact_type:
        raise AuthorityVerificationError("ARTIFACT_TYPE_MISMATCH", "unexpected artifact type", {"actual": artifact_type, "expected": expected_artifact_type})
    if protected.get("contract_id") != CONTRACT_ID:
        raise AuthorityVerificationError("SIGNED_CONTRACT_ID_MISMATCH", "protected contract id mismatch")
    if protected.get("profile") != PROFILE_ID:
        raise AuthorityVerificationError("SIGNATURE_PROFILE_MISMATCH", "unsupported signature profile")

    authority_id = require_string(protected.get("authority_id"), "protected.authority_id", AUTHORITY_ID_RE)
    key_id = require_string(protected.get("key_id"), "protected.key_id", KEY_ID_RE)
    attestation_id = require_string(protected.get("attestation_id"), "protected.attestation_id")
    signed_at = parse_utc(protected.get("signed_at_utc"), "protected.signed_at_utc")
    now_utc = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if signed_at > now_utc:
        raise AuthorityVerificationError("SIGNATURE_FROM_FUTURE", "signed_at_utc is later than verification time")

    authority = _find_unique(root.get("authorities"), "authority_id", authority_id, "UNKNOWN_AUTHORITY")
    if authority.get("status") != "ACTIVE":
        raise AuthorityVerificationError("AUTHORITY_NOT_ACTIVE", "authority status is not ACTIVE")
    if bool(authority.get("synthetic_control_only")) != synthetic:
        raise AuthorityVerificationError("SYNTHETIC_AUTHORITY_CLASSIFICATION_MISMATCH", "authority synthetic classification mismatch")

    key = _find_unique(authority.get("keys"), "key_id", key_id, "UNKNOWN_KEY")
    if key.get("status") != "ACTIVE":
        raise AuthorityVerificationError("KEY_NOT_ACTIVE", "key status is not ACTIVE")
    if key.get("algorithm") != "Ed25519-RFC8032":
        raise AuthorityVerificationError("KEY_ALGORITHM_MISMATCH", "key algorithm must be Ed25519-RFC8032")
    required_role = _required_role(artifact_type)
    roles = key.get("roles")
    if not isinstance(roles, list) or required_role not in roles:
        raise AuthorityVerificationError("KEY_ROLE_NOT_AUTHORIZED", f"key lacks role {required_role}")

    valid_from = parse_utc(key.get("valid_from_utc"), "key.valid_from_utc")
    valid_until = parse_utc(key.get("valid_until_utc"), "key.valid_until_utc")
    if not (valid_from <= signed_at < valid_until):
        raise AuthorityVerificationError("KEY_NOT_VALID_AT_SIGNING_TIME", "key validity window excludes signed_at_utc")
    if not synthetic and not (valid_from <= now_utc < valid_until):
        raise AuthorityVerificationError("KEY_NOT_CURRENTLY_VALID", "operative verification requires a currently valid key")
    if key.get("revoked") is not False or key.get("revoked_at_utc") is not None:
        raise AuthorityVerificationError("KEY_REVOKED", "revoked keys fail closed")

    try:
        public_key = base64.b64decode(require_string(key.get("public_key_base64"), "key.public_key_base64"), validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise AuthorityVerificationError("INVALID_PUBLIC_KEY_BASE64", "invalid public key base64") from exc
    if len(public_key) != 32:
        raise AuthorityVerificationError("INVALID_PUBLIC_KEY_LENGTH", "Ed25519 public key must be 32 bytes")
    fingerprint = hashlib.sha256(public_key).hexdigest()
    recorded_key_fingerprint = require_hex64(key.get("public_key_fingerprint_sha256"), "key.public_key_fingerprint_sha256")
    recorded_signature_fingerprint = require_hex64(signature_block.get("public_key_fingerprint_sha256"), "signature.public_key_fingerprint_sha256")
    if fingerprint != recorded_key_fingerprint or fingerprint != recorded_signature_fingerprint:
        raise AuthorityVerificationError("PUBLIC_KEY_FINGERPRINT_MISMATCH", "public key fingerprint mismatch")

    if signature_block.get("algorithm") != "Ed25519-RFC8032" or signature_block.get("encoding") != "base64":
        raise AuthorityVerificationError("SIGNATURE_METADATA_MISMATCH", "signature algorithm/encoding mismatch")
    if signature_block.get("attestation_id") != attestation_id:
        raise AuthorityVerificationError("ATTESTATION_ID_MISMATCH", "signature attestation_id mismatch")

    signed_structure = {"protected": protected, "payload": payload}
    signed_body = canonical_bytes(signed_structure)
    message = DOMAIN_SEPARATOR + signed_body
    digest = hashlib.sha256(message).hexdigest()
    if require_hex64(signature_block.get("signed_bytes_sha256"), "signature.signed_bytes_sha256") != digest:
        raise AuthorityVerificationError("SIGNED_BYTES_DIGEST_MISMATCH", "signed-bytes digest mismatch")
    try:
        signature = base64.b64decode(require_string(signature_block.get("value"), "signature.value"), validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise AuthorityVerificationError("INVALID_SIGNATURE_BASE64", "invalid signature base64") from exc
    if len(signature) != 64:
        raise AuthorityVerificationError("INVALID_SIGNATURE_LENGTH", "Ed25519 signature must be 64 bytes")
    if not ed25519_verify(public_key, message, signature):
        raise AuthorityVerificationError("INVALID_SIGNATURE", "Ed25519 signature verification failed")

    _verify_payload_bindings(payload, artifact_type, synthetic)

    return VerificationResult(
        status="PASS_SYNTHETIC_CONTROL_ONLY_NO_AUTHORIZATION" if synthetic else "PASS_OPERATIVE_AUTHORITY_ATTESTATION",
        artifact_type=artifact_type,
        authority_id=authority_id,
        key_id=key_id,
        signed_bytes_sha256=digest,
        synthetic_control_only=synthetic,
        operative_authorization_allowed=operative,
    )


def verification_error_payload(error: AuthorityVerificationError) -> dict[str, Any]:
    return {
        "schema": "universelab.authority-attestation-verification-result.v0.1",
        "status": "FAIL_CLOSED",
        "error_code": error.code,
        "message": str(error),
        "detail": copy.deepcopy(error.detail),
        "operative_authorization_allowed": False,
        "backend_imported": False,
        "solver_executed": False,
        "physical_evidence_effect": "NONE",
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--trust-root", required=True)
    parser.add_argument("--envelope", required=True)
    parser.add_argument("--expected-artifact-type", required=True, choices=["AUTHORIZATION_DECISION", "SINGLE_USE_GRANT", "TRUST_ROOT_RATIFICATION"])
    parser.add_argument("--now-utc", help="Optional deterministic RFC3339 UTC verification time")
    parser.add_argument("--output")
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        now = parse_utc(args.now_utc, "--now-utc") if args.now_utc else None
        result = verify_envelope(
            load_json(args.contract),
            load_json(args.trust_root),
            load_json(args.envelope),
            expected_artifact_type=args.expected_artifact_type,
            now=now,
        ).as_dict()
        exit_code = 0
    except AuthorityVerificationError as error:
        result = verification_error_payload(error)
        exit_code = 2

    output = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    print(output)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
