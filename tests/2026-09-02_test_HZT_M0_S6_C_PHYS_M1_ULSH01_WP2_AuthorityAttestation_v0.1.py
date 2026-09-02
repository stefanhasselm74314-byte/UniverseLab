#!/usr/bin/env python3
"""Synthetic positive and adversarial negative QA for the authority verifier."""
from __future__ import annotations

import base64
import copy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
VERIFIER_PATH = ROOT / "tools/2026-09-02_verify_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_AuthorityAttestation_v0.1.py"
CORE_PATH = ROOT / "tools/2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_AuthorityVerificationCore_v0.1.py"
CONTRACT_PATH = ROOT / "registry/2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_AuthoritySignatureProvenanceContract_v0.1.json"
TRUST_ROOT_PATH = ROOT / "registry/2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_AuthorityTrustRootCandidate_v0.1.json"

spec = importlib.util.spec_from_file_location("ul_authority_verifier", VERIFIER_PATH)
assert spec and spec.loader
V = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = V
spec.loader.exec_module(V)

PUBLIC_KEY_B64 = "Ih/e0rXoYDnXSwNSe+gTwQ3GuGautSK0RC/IV4dQ0e0="
FINGERPRINT = "0d86b1b78ea72571fd22bb2ee8248860fb367e1de72620113f27638fc7d34de1"

DECISION = json.loads(r'''{
  "payload": {
    "authorization_decision_id": "SYNTHETIC-CONTROL-DECISION-0001",
    "authorized": false,
    "automatic_execution": false,
    "decision_status": "SYNTHETIC_CONTROL_ONLY_NO_AUTHORIZATION",
    "release_package_manifest_sha256": null,
    "repository_commit_sha": null,
    "run_id": "HZT-M0-S6-C-PHYS-M1-ULSH01-WP2-CP01R4",
    "run_payload_sha256": "8e5976a22c4be78b5e4fe7834c9947de8a4acea7781363c7aeb83aa73982ac8c",
    "target_contract_digest_sha256": "237c4b5e08a2106e13e985c4af7925f1899e2ae2e4b7253c7ab73cc2db5f1823"
  },
  "protected": {
    "artifact_type": "AUTHORIZATION_DECISION",
    "attestation_id": "SYNTHETIC-ATTESTATION-DECISION-0001",
    "authority_id": "SYNTHETIC_TEST_AUTHORITY",
    "contract_id": "ULSH01-WP2-AUTHORITY-SIGNATURE-PROVENANCE-v0.1",
    "key_id": "SYNTHETIC_ED25519_TEST_KEY_01",
    "profile": "UL-ED25519-CANONICAL-JSON-v1",
    "signed_at_utc": "2026-09-02T00:00:00Z"
  },
  "schema": "universelab.signed-authority-envelope.v0.1",
  "signature": {
    "algorithm": "Ed25519-RFC8032",
    "attestation_id": "SYNTHETIC-ATTESTATION-DECISION-0001",
    "encoding": "base64",
    "public_key_fingerprint_sha256": "0d86b1b78ea72571fd22bb2ee8248860fb367e1de72620113f27638fc7d34de1",
    "signed_bytes_sha256": "312aabe0a5e6babc8e445ca30e95003332c947d9b557f10832ef5d449d85d99c",
    "value": "DB1LuDnultnyyovp1xp1CJA9PicPQU8brzPud+S87nGpf91hhiqm+PwZMvp9ocmN+roMneNqY6z04pXFZBrKBw=="
  }
}''')

GRANT = json.loads(r'''{
  "payload": {
    "authorization_decision_id": "SYNTHETIC-CONTROL-DECISION-0001",
    "authorized": false,
    "automatic_execution": false,
    "grant_id": "SYNTHETIC-CONTROL-GRANT-0001",
    "nonce": "SYNTHETIC-NONCE-0001",
    "release_package_manifest_sha256": null,
    "repository_commit_sha": null,
    "run_id": "HZT-M0-S6-C-PHYS-M1-ULSH01-WP2-CP01R4",
    "run_payload_sha256": "8e5976a22c4be78b5e4fe7834c9947de8a4acea7781363c7aeb83aa73982ac8c",
    "scope": "SYNTHETIC_CONTROL_ONLY_NO_BACKEND_IMPORT",
    "single_use": true,
    "target_contract_digest_sha256": "237c4b5e08a2106e13e985c4af7925f1899e2ae2e4b7253c7ab73cc2db5f1823"
  },
  "protected": {
    "artifact_type": "SINGLE_USE_GRANT",
    "attestation_id": "SYNTHETIC-ATTESTATION-GRANT-0001",
    "authority_id": "SYNTHETIC_TEST_AUTHORITY",
    "contract_id": "ULSH01-WP2-AUTHORITY-SIGNATURE-PROVENANCE-v0.1",
    "key_id": "SYNTHETIC_ED25519_TEST_KEY_01",
    "profile": "UL-ED25519-CANONICAL-JSON-v1",
    "signed_at_utc": "2026-09-02T00:00:00Z"
  },
  "schema": "universelab.signed-authority-envelope.v0.1",
  "signature": {
    "algorithm": "Ed25519-RFC8032",
    "attestation_id": "SYNTHETIC-ATTESTATION-GRANT-0001",
    "encoding": "base64",
    "public_key_fingerprint_sha256": "0d86b1b78ea72571fd22bb2ee8248860fb367e1de72620113f27638fc7d34de1",
    "signed_bytes_sha256": "773f212535a59e204c55c60cb45cc3afaec1f2eccd944dfa602df4ab94be09e9",
    "value": "6Qiba/vE+0meXjEPth1biZNTRjsCrJ9Qo0TMKA3/UH4yLG5VjOpWdWIFk9eJY8zVcFA7Y0MYQBo1xJ96mePoCA=="
  }
}''')

WRONG_RUN_VALID_SIGNATURE = json.loads(r'''{
  "payload": {
    "authorization_decision_id": "SYNTHETIC-CONTROL-DECISION-0001",
    "authorized": false,
    "automatic_execution": false,
    "decision_status": "SYNTHETIC_CONTROL_ONLY_NO_AUTHORIZATION",
    "release_package_manifest_sha256": null,
    "repository_commit_sha": null,
    "run_id": "WRONG-RUN-ID",
    "run_payload_sha256": "8e5976a22c4be78b5e4fe7834c9947de8a4acea7781363c7aeb83aa73982ac8c",
    "target_contract_digest_sha256": "237c4b5e08a2106e13e985c4af7925f1899e2ae2e4b7253c7ab73cc2db5f1823"
  },
  "protected": {
    "artifact_type": "AUTHORIZATION_DECISION",
    "attestation_id": "SYNTHETIC-ATTESTATION-WRONG-RUN-0001",
    "authority_id": "SYNTHETIC_TEST_AUTHORITY",
    "contract_id": "ULSH01-WP2-AUTHORITY-SIGNATURE-PROVENANCE-v0.1",
    "key_id": "SYNTHETIC_ED25519_TEST_KEY_01",
    "profile": "UL-ED25519-CANONICAL-JSON-v1",
    "signed_at_utc": "2026-09-02T00:00:00Z"
  },
  "schema": "universelab.signed-authority-envelope.v0.1",
  "signature": {
    "algorithm": "Ed25519-RFC8032",
    "attestation_id": "SYNTHETIC-ATTESTATION-WRONG-RUN-0001",
    "encoding": "base64",
    "public_key_fingerprint_sha256": "0d86b1b78ea72571fd22bb2ee8248860fb367e1de72620113f27638fc7d34de1",
    "signed_bytes_sha256": "3e22ce837d569069f1cd5697c0682f33a487c278e58e51241eeba7297be2c640",
    "value": "zDXtt5SgKh4UxWAp+o5fn/kfi42tMFk6l+MWCPqk5grQdJ0RZLIBL6IUgL+aN/4zgQL5Uzic8mL6C1cBt6urDQ=="
  }
}''')


def synthetic_contract() -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract["status"] = "RATIFIED_SYNTHETIC_CONTROL_ONLY"
    return contract


def synthetic_root() -> dict:
    return {
        "schema": "universelab.synthetic-authority-trust-root.v0.1",
        "status": "RATIFIED_SYNTHETIC_CONTROL_ONLY",
        "contract_id": V.CONTRACT_ID,
        "authorities": [
            {
                "authority_id": "SYNTHETIC_TEST_AUTHORITY",
                "status": "ACTIVE",
                "synthetic_control_only": True,
                "keys": [
                    {
                        "key_id": "SYNTHETIC_ED25519_TEST_KEY_01",
                        "algorithm": "Ed25519-RFC8032",
                        "public_key_base64": PUBLIC_KEY_B64,
                        "public_key_fingerprint_sha256": FINGERPRINT,
                        "status": "ACTIVE",
                        "valid_from_utc": "2026-01-01T00:00:00Z",
                        "valid_until_utc": "2027-01-01T00:00:00Z",
                        "revoked": False,
                        "revoked_at_utc": None,
                        "roles": [
                            "AUTHORIZATION_DECISION_ISSUER",
                            "SINGLE_USE_GRANT_ISSUER",
                            "TRUST_ROOT_RATIFIER"
                        ]
                    }
                ]
            }
        ]
    }


def expect_error(code: str, fn) -> None:
    try:
        fn()
    except V.AuthorityVerificationError as error:
        assert error.code == code, (error.code, code, str(error))
    else:
        raise AssertionError(f"expected {code}")


def verify(envelope: dict, artifact_type: str, *, contract: dict | None = None, root: dict | None = None):
    return V.verify_envelope(
        contract or synthetic_contract(),
        root or synthetic_root(),
        envelope,
        expected_artifact_type=artifact_type,
        now=datetime(2026, 9, 2, 1, 0, tzinfo=timezone.utc),
    )


def main() -> None:
    repo_contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    repo_root = json.loads(TRUST_ROOT_PATH.read_text(encoding="utf-8"))
    assert repo_contract["status"] == "DRAFT_NOT_RATIFIED"
    assert repo_root["status"] == "DRAFT_NO_RATIFIED_TRUST_ROOT"
    assert repo_root["authorities"] == []
    assert repo_root["firewall"]["this_file_establishes_an_authority"] is False
    assert repo_contract["authority_and_key_policy"]["private_keys_may_be_committed"] is False
    expect_error("TRUST_ROOT_NOT_RATIFIED", lambda: verify(DECISION, "AUTHORIZATION_DECISION", contract=repo_contract, root=repo_root))

    # RFC 8032 test vector 1, empty message.
    rfc_public = bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
    rfc_signature = bytes.fromhex(
        "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
        "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
    )
    assert V.ed25519_verify(rfc_public, b"", rfc_signature)
    assert not V.ed25519_verify(rfc_public, b"x", rfc_signature)

    decision_result = verify(DECISION, "AUTHORIZATION_DECISION")
    assert decision_result.status == "PASS_SYNTHETIC_CONTROL_ONLY_NO_AUTHORIZATION"
    assert decision_result.synthetic_control_only is True
    assert decision_result.operative_authorization_allowed is False
    assert decision_result.physical_evidence_effect == "NONE"

    grant_result = verify(GRANT, "SINGLE_USE_GRANT")
    assert grant_result.status == "PASS_SYNTHETIC_CONTROL_ONLY_NO_AUTHORIZATION"
    assert grant_result.operative_authorization_allowed is False

    expect_error("RUN_ID_MISMATCH", lambda: verify(WRONG_RUN_VALID_SIGNATURE, "AUTHORIZATION_DECISION"))

    mutated_payload = copy.deepcopy(DECISION)
    mutated_payload["payload"]["authorization_decision_id"] = "MUTATED"
    expect_error("SIGNED_BYTES_DIGEST_MISMATCH", lambda: verify(mutated_payload, "AUTHORIZATION_DECISION"))

    mutated_signature = copy.deepcopy(DECISION)
    signature = bytearray(base64.b64decode(mutated_signature["signature"]["value"]))
    signature[10] ^= 1
    mutated_signature["signature"]["value"] = base64.b64encode(signature).decode("ascii")
    expect_error("INVALID_SIGNATURE", lambda: verify(mutated_signature, "AUTHORIZATION_DECISION"))

    unknown_authority = copy.deepcopy(DECISION)
    unknown_authority["protected"]["authority_id"] = "UNKNOWN_AUTHORITY"
    expect_error("UNKNOWN_AUTHORITY", lambda: verify(unknown_authority, "AUTHORIZATION_DECISION"))

    unknown_key = copy.deepcopy(DECISION)
    unknown_key["protected"]["key_id"] = "UNKNOWN_KEY_001"
    expect_error("UNKNOWN_KEY", lambda: verify(unknown_key, "AUTHORIZATION_DECISION"))

    root = synthetic_root()
    root["authorities"][0]["keys"][0]["roles"] = ["SINGLE_USE_GRANT_ISSUER"]
    expect_error("KEY_ROLE_NOT_AUTHORIZED", lambda: verify(DECISION, "AUTHORIZATION_DECISION", root=root))

    root = synthetic_root()
    root["authorities"][0]["keys"][0]["revoked"] = True
    root["authorities"][0]["keys"][0]["revoked_at_utc"] = "2026-09-01T00:00:00Z"
    expect_error("KEY_NOT_ACTIVE" if root["authorities"][0]["keys"][0]["status"] != "ACTIVE" else "KEY_REVOKED", lambda: verify(DECISION, "AUTHORIZATION_DECISION", root=root))

    root = synthetic_root()
    root["authorities"][0]["keys"][0]["valid_until_utc"] = "2026-08-01T00:00:00Z"
    expect_error("KEY_NOT_VALID_AT_SIGNING_TIME", lambda: verify(DECISION, "AUTHORIZATION_DECISION", root=root))

    root = synthetic_root()
    root["authorities"][0]["keys"][0]["public_key_fingerprint_sha256"] = "0" * 64
    expect_error("PUBLIC_KEY_FINGERPRINT_MISMATCH", lambda: verify(DECISION, "AUTHORIZATION_DECISION", root=root))

    future = copy.deepcopy(DECISION)
    future["protected"]["signed_at_utc"] = "2027-09-02T00:00:00Z"
    expect_error("SIGNATURE_FROM_FUTURE", lambda: verify(future, "AUTHORIZATION_DECISION"))

    floating = copy.deepcopy(DECISION)
    floating["payload"]["unsafe_float"] = 0.1
    expect_error("FLOAT_FORBIDDEN_IN_SIGNED_PAYLOAD", lambda: verify(floating, "AUTHORIZATION_DECISION"))

    expect_error("DUPLICATE_JSON_KEY", lambda: V.strict_json_loads('{"a":1,"a":2}'))
    expect_error("INTEGER_OUTSIDE_CANONICAL_RANGE", lambda: V.canonical_bytes({"n": 2**53}))
    expect_error("ARTIFACT_TYPE_MISMATCH", lambda: verify(DECISION, "SINGLE_USE_GRANT"))

    # CLI positive and repository fail-closed paths.
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        synthetic_contract_path = root / "contract.json"
        synthetic_root_path = root / "root.json"
        envelope_path = root / "envelope.json"
        synthetic_contract_path.write_text(json.dumps(synthetic_contract()), encoding="utf-8")
        synthetic_root_path.write_text(json.dumps(synthetic_root()), encoding="utf-8")
        envelope_path.write_text(json.dumps(DECISION), encoding="utf-8")
        command = [
            sys.executable, str(VERIFIER_PATH),
            "--contract", str(synthetic_contract_path),
            "--trust-root", str(synthetic_root_path),
            "--envelope", str(envelope_path),
            "--expected-artifact-type", "AUTHORIZATION_DECISION",
            "--now-utc", "2026-09-02T01:00:00Z",
        ]
        success = subprocess.run(command, check=False, capture_output=True, text=True)
        assert success.returncode == 0, success.stderr + success.stdout
        success_payload = json.loads(success.stdout)
        assert success_payload["status"] == "PASS_SYNTHETIC_CONTROL_ONLY_NO_AUTHORIZATION"
        assert success_payload["operative_authorization_allowed"] is False
        assert success_payload["solver_executed"] is False

        failure = subprocess.run([
            sys.executable, str(VERIFIER_PATH),
            "--contract", str(CONTRACT_PATH),
            "--trust-root", str(TRUST_ROOT_PATH),
            "--envelope", str(envelope_path),
            "--expected-artifact-type", "AUTHORIZATION_DECISION",
            "--now-utc", "2026-09-02T01:00:00Z",
        ], check=False, capture_output=True, text=True)
        assert failure.returncode == 2
        failure_payload = json.loads(failure.stdout)
        assert failure_payload["status"] == "FAIL_CLOSED"
        assert failure_payload["error_code"] == "TRUST_ROOT_NOT_RATIFIED"
        assert failure_payload["operative_authorization_allowed"] is False
        assert failure_payload["physical_evidence_effect"] == "NONE"

    source_text = VERIFIER_PATH.read_text(encoding="utf-8") + CORE_PATH.read_text(encoding="utf-8")
    assert "private_bytes" not in source_text
    assert "sign(" not in source_text
    assert "solver" not in source_text.lower() or "solver_executed" in source_text

    print("ULSH-01 WP2 authority/signature provenance synthetic QA: PASS")


if __name__ == "__main__":
    main()
