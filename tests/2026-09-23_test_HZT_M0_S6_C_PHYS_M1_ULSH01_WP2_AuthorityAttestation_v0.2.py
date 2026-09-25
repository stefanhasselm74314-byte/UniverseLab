#!/usr/bin/env python3
"""Focused fail-closed QA for the v0.2 owner-ratification bridge."""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LEGACY_TEST_PATH = ROOT / "tests/2026-09-02_test_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_AuthorityAttestation_v0.1.py"
VERIFIER_PATH = ROOT / "tools/2026-09-23_verify_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_AuthorityAttestation_v0.2.py"
CONTRACT_PATH = ROOT / "registry/2026-09-23_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_AuthoritySignatureProvenanceContract_v0.2.json"
TRUST_ROOT_PATH = ROOT / "registry/2026-09-02_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_AuthorityTrustRootCandidate_v0.1.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


LEGACY = load_module("ul_authority_legacy_test_fixtures", LEGACY_TEST_PATH)
V = load_module("ul_authority_verifier_v02", VERIFIER_PATH)

DECISION = LEGACY.DECISION
GRANT = LEGACY.GRANT


def synthetic_contract() -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract["status"] = "RATIFIED_SYNTHETIC_CONTROL_ONLY"
    return contract


def synthetic_root() -> dict:
    return LEGACY.synthetic_root()


def operative_contract_without_owner_ratification() -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract["status"] = "RATIFIED_ACTIVE"
    return contract


def operative_root_without_owner_ratification() -> dict:
    root = synthetic_root()
    root["schema"] = "universelab.test-operative-authority-trust-root.v0.1"
    root["status"] = "RATIFIED_ACTIVE"
    root["authorities"][0]["synthetic_control_only"] = False
    return root


def operative_decision_shape() -> dict:
    decision = copy.deepcopy(DECISION)
    decision["payload"]["decision_status"] = "AUTHORIZED_SINGLE_USE_WP2_CP01R4_PRIMARY_TARGET_EXECUTION"
    decision["payload"]["authorized"] = True
    decision["payload"]["repository_commit_sha"] = "1" * 64
    decision["payload"]["release_package_manifest_sha256"] = "2" * 64
    return decision


def operative_grant_shape() -> dict:
    grant = copy.deepcopy(GRANT)
    grant["payload"]["scope"] = f"{V.RUN_ID}_TARGET_ONLY"
    grant["payload"]["authorized"] = True
    grant["payload"]["repository_commit_sha"] = "3" * 64
    grant["payload"]["release_package_manifest_sha256"] = "4" * 64
    return grant


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
    assert repo_contract["contract_id"] == "ULSH01-WP2-AUTHORITY-SIGNATURE-PROVENANCE-v0.2"
    assert repo_contract["signed_envelope_contract_id"] == V.CONTRACT_ID
    assert repo_contract["owner_ratification_bridge"]["positive_operational_verification_available_in_this_revision"] is False
    assert repo_contract["owner_ratification_bridge"]["independently_verifiable_owner_ratification_schema"] == "NOT_IMPLEMENTED"
    assert repo_root["status"] == "DRAFT_NO_RATIFIED_TRUST_ROOT"

    expect_error(
        "TRUST_ROOT_NOT_RATIFIED",
        lambda: verify(DECISION, "AUTHORIZATION_DECISION", contract=repo_contract, root=repo_root),
    )

    operative_contract = operative_contract_without_owner_ratification()
    operative_root = operative_root_without_owner_ratification()
    operative_decision = operative_decision_shape()
    operative_grant = operative_grant_shape()

    # These are deliberately operative-shaped: authorized=true, operative
    # status/scope and non-null repository/package digests.
    for artifact_type, envelope in (
        ("AUTHORIZATION_DECISION", operative_decision),
        ("SINGLE_USE_GRANT", operative_grant),
    ):
        expect_error(
            "OWNER_RATIFICATION_NOT_VERIFIABLE",
            lambda artifact_type=artifact_type, envelope=envelope: V.verify_envelope(
                operative_contract,
                operative_root,
                envelope,
                expected_artifact_type=artifact_type,
                now=datetime(2026, 9, 2, 1, 0, tzinfo=timezone.utc),
            ),
        )

    # v0.2 promises no positive operative result of any artifact class.
    # The guard must therefore also fire before a TRUST_ROOT_RATIFICATION
    # envelope can reach the common PASS_OPERATIVE return path.
    expect_error(
        "OWNER_RATIFICATION_NOT_VERIFIABLE",
        lambda: V.verify_envelope(
            operative_contract,
            operative_root,
            {},
            expected_artifact_type="TRUST_ROOT_RATIFICATION",
            now=datetime(2026, 9, 2, 1, 0, tzinfo=timezone.utc),
        ),
    )

    # Ad-hoc or implied-consent fields cannot bypass the bridge.
    for base, artifact_type in (
        (operative_decision, "AUTHORIZATION_DECISION"),
        (operative_grant, "SINGLE_USE_GRANT"),
    ):
        for forged_fields in (
            {"owner_ratification_status": "APPROVED"},
            {"owner_ratification_record": {"owner": "STEFAN_HASSELMEYER"}},
            {"owner_ratification_status": "APPROVED", "owner_ratification_record": "Go"},
        ):
            forged = copy.deepcopy(base)
            forged["payload"].update(forged_fields)
            expect_error(
                "OWNER_RATIFICATION_NOT_VERIFIABLE",
                lambda forged=forged, artifact_type=artifact_type: V.verify_envelope(
                    operative_contract,
                    operative_root,
                    forged,
                    expected_artifact_type=artifact_type,
                    now=datetime(2026, 9, 2, 1, 0, tzinfo=timezone.utc),
                ),
            )

    unsafe_contract = copy.deepcopy(operative_contract)
    unsafe_contract["owner_ratification_bridge"]["positive_operational_verification_available_in_this_revision"] = True
    expect_error(
        "UNSAFE_BRIDGE_CONFIGURATION",
        lambda: V.verify_envelope(
            unsafe_contract,
            operative_root,
            operative_decision,
            expected_artifact_type="AUTHORIZATION_DECISION",
            now=datetime(2026, 9, 2, 1, 0, tzinfo=timezone.utc),
        ),
    )

    # Existing signed synthetic controls remain usable and nonoperative because
    # the frozen signed-envelope protocol id is unchanged.
    decision_result = verify(DECISION, "AUTHORIZATION_DECISION")
    assert decision_result.status == "PASS_SYNTHETIC_CONTROL_ONLY_NO_AUTHORIZATION"
    assert decision_result.operative_authorization_allowed is False
    assert decision_result.physical_evidence_effect == "NONE"

    grant_result = verify(GRANT, "SINGLE_USE_GRANT")
    assert grant_result.status == "PASS_SYNTHETIC_CONTROL_ONLY_NO_AUTHORIZATION"
    assert grant_result.operative_authorization_allowed is False

    # CLI path must expose the same fail-closed result and unchanged firewalls.
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        contract_path = tmp / "operative-contract.json"
        root_path = tmp / "operative-root.json"
        envelope_path = tmp / "operative-envelope.json"
        contract_path.write_text(json.dumps(operative_contract), encoding="utf-8")
        root_path.write_text(json.dumps(operative_root), encoding="utf-8")
        envelope_path.write_text(json.dumps(operative_decision), encoding="utf-8")
        proc = subprocess.run([
            sys.executable, str(VERIFIER_PATH),
            "--contract", str(contract_path),
            "--trust-root", str(root_path),
            "--envelope", str(envelope_path),
            "--expected-artifact-type", "AUTHORIZATION_DECISION",
            "--now-utc", "2026-09-02T01:00:00Z",
        ], check=False, capture_output=True, text=True)
        assert proc.returncode == 2
        payload = json.loads(proc.stdout)
        assert payload["status"] == "FAIL_CLOSED"
        assert payload["error_code"] == "OWNER_RATIFICATION_NOT_VERIFIABLE"
        assert payload["operative_authorization_allowed"] is False
        assert payload["backend_imported"] is False
        assert payload["solver_executed"] is False
        assert payload["physical_evidence_effect"] == "NONE"

    print("ULSH-01 WP2 owner-ratification bridge v0.2 QA: PASS")


if __name__ == "__main__":
    main()
