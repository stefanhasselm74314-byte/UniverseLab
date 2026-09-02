#!/usr/bin/env python3
"""Synthetic and adversarial tests for the ULSH-01 trust-root preparation package."""
from __future__ import annotations

import base64
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
REGISTRY = ROOT / "registry"
CORE_PATH = TOOLS / "2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_AuthorityVerificationCore_v0.1.py"
PREP_PATH = TOOLS / "2026-09-02_prepare_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_HumanTrustRootCandidate_v0.1.py"
VERIFY_PATH = TOOLS / "2026-09-02_verify_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_HumanTrustRootRatificationPackage_v0.1.py"
CONTRACT = REGISTRY / "2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_HumanTrustRootRatificationPackageContract_v0.1.json"
CANDIDATE_TEMPLATE = REGISTRY / "2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_HumanTrustRootCandidateTemplate_v0.1.json"
PROOF_TEMPLATE = REGISTRY / "2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_RootKeyProofOfPossessionTemplate_v0.1.json"
ADOPTION_TEMPLATE = REGISTRY / "2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_ProjectOwnerAdoptionRecordTemplate_v0.1.json"


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


CORE = module("ul_core_test", CORE_PATH)
PREP = module("ul_prep_test", PREP_PATH)
VERIFY = module("ul_verify_test", VERIFY_PATH)


def sign(seed: bytes, message: bytes) -> tuple[bytes, bytes]:
    """Test-only RFC-8032 signing helper with an ephemeral runtime seed."""
    digest = hashlib.sha512(seed).digest()
    scalar = int.from_bytes(digest[:32], "little")
    scalar &= (1 << 254) - 8
    scalar |= 1 << 254
    prefix = digest[32:]
    public = CORE._encode_point(CORE._scalar_mult(CORE._BASE, scalar))
    r = int.from_bytes(hashlib.sha512(prefix + message).digest(), "little") % CORE._L
    encoded_r = CORE._encode_point(CORE._scalar_mult(CORE._BASE, r))
    h = int.from_bytes(hashlib.sha512(encoded_r + public + message).digest(), "little") % CORE._L
    s = (r + h * scalar) % CORE._L
    return public, encoded_r + s.to_bytes(32, "little")


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def assert_blocked(result: dict) -> None:
    assert result["trust_root_ratified"] is False
    assert result["operative_authorization_allowed"] is False
    assert result["runtime_issuance_allowed"] is False
    assert result["AuthorizationDecision"] == "NOT_CREATED"
    assert result["SingleUseGrant"] == "NOT_CREATED"
    assert result["backend_imported"] is False
    assert result["solver_executed"] is False
    assert result["K1-D"] == "NOT_RELEASED"
    assert result["K1-E"] == "NOT_ADMISSIBLE"
    assert result["physical_gate_effect"] == "NONE"
    assert result["physical_evidence_effect"] == "NONE"


def expect_error(code: str, fn) -> None:
    try:
        fn()
    except VERIFY.PackageVerificationError as exc:
        assert exc.code == code, (exc.code, code)
    else:
        raise AssertionError(f"expected {code}")


def main() -> None:
    draft = VERIFY.verify_empty_templates(
        VERIFY.load(CONTRACT), VERIFY.load(CANDIDATE_TEMPLATE),
        VERIFY.load(PROOF_TEMPLATE), VERIFY.load(ADOPTION_TEMPLATE),
    )
    assert draft["status"] == VERIFY.PREPARATION_PASS
    assert_blocked(draft)

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        seed = os.urandom(32)
        public, _ = sign(seed, b"bootstrap")
        key_file = work / "public-key.b64"
        key_file.write_text(base64.b64encode(public).decode("ascii") + "\n", encoding="ascii")

        rc = PREP.main([
            "candidate",
            "--public-key-file", str(key_file),
            "--authority-id", "PROJECT-AUTHORITY-01",
            "--display-identity", "UNIVERSELAB-PROJECT-OWNER",
            "--key-id", "ROOT-ED25519-01",
            "--role", "TRUST_ROOT_RATIFIER",
            "--valid-from-utc", "2026-09-02T00:00:00Z",
            "--valid-until-utc", "2031-09-02T00:00:00Z",
            "--signed-at-utc", "2026-09-02T01:00:00Z",
            "--attestation-id", "ROOT-POP-01",
            "--challenge-nonce", "SYNTHETIC-NONCE-00000001",
            "--proof-expires-at-utc", "2026-09-03T00:00:00Z",
            "--output-dir", str(work),
        ])
        assert rc == 0
        candidate_path = work / "2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_HumanTrustRootCandidate_v0.1.json"
        proof_path = work / "2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_RootKeyProofOfPossession_v0.1.json"
        message_path = work / "2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_RootKeyProofOfPossessionMessage_v0.1.bin"
        candidate = VERIFY.load(candidate_path)
        proof = VERIFY.load(proof_path)
        message = message_path.read_bytes()
        public_again, signature = sign(seed, message)
        assert public_again == public
        proof["status"] = "SIGNED_AWAITING_HUMAN_ADOPTION"
        proof["signature"]["signed_bytes_sha256"] = hashlib.sha256(message).hexdigest()
        proof["signature"]["value"] = base64.b64encode(signature).decode("ascii")
        dump(proof_path, proof)

        adoption_path = work / "adoption.json"
        rc = PREP.main([
            "adoption",
            "--candidate", str(candidate_path),
            "--proof", str(proof_path),
            "--adoption-id", "OWNER-ADOPTION-01",
            "--project-identity", "UNIVERSELAB-PROJECT-OWNER",
            "--adopted-at-utc", "2026-09-02T02:00:00Z",
            "--repository-commit-or-tag", "FUTURE-HUMAN-ADOPTION-COMMIT",
            "--verification-provider", "HUMAN_REVIEW",
            "--verification-reason", "EXPLICIT_PROJECT_OWNER_ADOPTION",
            "--custody-location-class", "OFFLINE_ENCRYPTED_REMOVABLE_MEDIA",
            "--backup-policy", "HUMAN_DEFINED_OFFLINE_BACKUP",
            "--revocation-procedure", "PUBLISH_VERSIONED_REVOCATION_AND_FAIL_CLOSED",
            "--single-human-self-review", "true",
            "--affirm-private-key-isolated",
            "--output", str(adoption_path),
        ])
        assert rc == 0

        result = VERIFY.verify_candidate(
            CONTRACT, candidate_path, proof_path, adoption_path,
            VERIFY.parse_utc("2026-09-02T12:00:00Z", "now"),
        )
        assert result["status"] == VERIFY.CANDIDATE_PASS
        assert result["detail"]["proof_of_possession_valid"] is True
        assert result["detail"]["machine_verified_human_identity"] is False
        assert result["detail"]["manual_human_attribution_review_status"] == "PENDING_MANUAL_REVIEW"
        assert_blocked(result)

        mutated_candidate = copy.deepcopy(candidate)
        mutated_candidate["authorities"][0]["display_name_or_pseudonymous_project_identity"] = "MUTATED"
        mutated_path = work / "mutated-candidate.json"
        dump(mutated_path, mutated_candidate)
        expect_error("CANDIDATE_RAW_DIGEST_MISMATCH", lambda: VERIFY.verify_candidate(
            CONTRACT, mutated_path, proof_path, adoption_path,
            VERIFY.parse_utc("2026-09-02T12:00:00Z", "now"),
        ))

        ratified = copy.deepcopy(candidate)
        ratified["status"] = "RATIFIED_ACTIVE"
        ratified["ratified"] = True
        ratified_path = work / "ratified.json"
        dump(ratified_path, ratified)
        expect_error("RATIFIED_STATE_FORBIDDEN", lambda: VERIFY.verify_candidate(
            CONTRACT, ratified_path, proof_path, adoption_path,
            VERIFY.parse_utc("2026-09-02T12:00:00Z", "now"),
        ))

        bad_proof = copy.deepcopy(proof)
        raw_sig = bytearray(base64.b64decode(bad_proof["signature"]["value"]))
        raw_sig[0] ^= 1
        bad_proof["signature"]["value"] = base64.b64encode(raw_sig).decode("ascii")
        bad_proof_path = work / "bad-proof.json"
        dump(bad_proof_path, bad_proof)
        bad_adoption = VERIFY.load(adoption_path)
        bad_adoption["candidate_binding"]["root_key_proof_raw_sha256"] = hashlib.sha256(bad_proof_path.read_bytes()).hexdigest()
        bad_adoption["candidate_binding"]["root_key_proof_canonical_sha256"] = CORE.canonical_sha256(bad_proof)
        bad_adoption_path = work / "bad-adoption.json"
        dump(bad_adoption_path, bad_adoption)
        expect_error("INVALID_PROOF_OF_POSSESSION_SIGNATURE", lambda: VERIFY.verify_candidate(
            CONTRACT, candidate_path, bad_proof_path, bad_adoption_path,
            VERIFY.parse_utc("2026-09-02T12:00:00Z", "now"),
        ))

    production = PREP_PATH.read_text() + "\n" + VERIFY_PATH.read_text()
    forbidden = ["Ed25519PrivateKey", "private_bytes(", ".sign(", "--private-key", "PRIVATE_KEY_FILE"]
    found = [token for token in forbidden if token in production]
    assert found == [], found
    assert "public-key-only" in PREP_PATH.read_text()
    assert "rejects RATIFIED_ACTIVE" in VERIFY_PATH.read_text()

    contract = json.loads(CONTRACT.read_text())
    assert contract["status"] == "PREPARATION_ONLY_NOT_RATIFIED"
    assert contract["verifier_statuses"]["ratified_active_status_accepted_by_this_verifier"] is False
    assert contract["key_custody_policy"]["private_key_may_be_committed"] is False
    assert contract["key_custody_policy"]["private_key_may_be_pasted_into_chat"] is False
    assert contract["current_gate_state"]["runtime_issuance_bindings"] == "BLOCKED"
    assert contract["current_gate_state"]["AuthorizationDecision"] == "NOT_CREATED"
    assert contract["current_gate_state"]["SingleUseGrant"] == "NOT_CREATED"
    print("ULSH-01 human trust-root ratification preparation package: PASS")


if __name__ == "__main__":
    main()
