#!/usr/bin/env python3
"""ULSH-01 WP2 CP01R2 target-transaction preflight v0.1.

This implementation is deliberately non-executing. It binds the canonical 8x8 target,
run payload, resource policy, audited backend source hashes, result schema, release
package manifest and single-use grant semantics. It never imports or invokes either
physical backend.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

TARGET_DIGEST = "237c4b5e08a2106e13e985c4af7925f1899e2ae2e4b7253c7ab73cc2db5f1823"
RUN_ID = "HZT-M0-S6-C-PHYS-M1-ULSH01-WP2-CP01R2"
RUN_PAYLOAD_SHA256 = "990cb9902aabf740db34ce03d69d845588a4b0c6337f9e48633829bbd6a7cea7"
DEPENDENCY_LOCK_SHA256 = "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f"
PRIMARY_SHA256 = "8ce1c0eceed64245d091d4bed492f3cf2a9c8314f631a03045aaa9696fb11c92"
PRIMARY_BASE_SHA256 = "830d4b4fdd28c8888876125479df3542eeb3864d4328764feb96b5d34bd91599"
INDEPENDENT_SHA256 = "a8afd7b548366acf9f5ac72e91bcf07372913cc21a8790d86d0a989a89f03e7b"

PHYSICAL_EXECUTION_AUTHORIZED = False
PHYSICAL_BACKEND_IMPORT_ALLOWED = False
TARGET_SOLVE_ALLOWED = False
PHYSICAL_RESULT_CREATION_ALLOWED = False


class TransactionError(RuntimeError):
    pass


class ReplayError(TransactionError):
    pass


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_sha256(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_utc(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise TransactionError(f"invalid UTC timestamp: {value!r}") from exc
    if dt.tzinfo is None:
        raise TransactionError("timestamp must be timezone-aware")
    return dt.astimezone(timezone.utc)


def verify_target(target: dict[str, Any]) -> None:
    semantics = target.get("target_semantics")
    if not isinstance(semantics, dict):
        raise TransactionError("target_semantics missing")
    actual = canonical_sha256(semantics)
    recorded = target.get("target_contract_digest", {}).get("sha256")
    if actual != TARGET_DIGEST or recorded != TARGET_DIGEST:
        raise TransactionError(f"target digest mismatch actual={actual} recorded={recorded}")
    if target.get("solver_authorized") is not False:
        raise TransactionError("target freeze unexpectedly authorizes solver execution")


def verify_run_input(run_input: dict[str, Any]) -> None:
    if run_input.get("status") != "RUN_INPUT_FROZEN_CP01R2_EXECUTION_NOT_AUTHORIZED":
        raise TransactionError("CP01R2 run input status mismatch")
    payload = run_input.get("frozen_run_payload")
    if not isinstance(payload, dict):
        raise TransactionError("frozen_run_payload missing")
    actual = canonical_sha256(payload)
    recorded = run_input.get("frozen_run_payload_sha256")
    if actual != RUN_PAYLOAD_SHA256 or recorded != RUN_PAYLOAD_SHA256:
        raise TransactionError(f"run payload hash mismatch actual={actual} recorded={recorded}")
    if payload.get("run_id") != RUN_ID:
        raise TransactionError("run id mismatch")
    if payload.get("target_contract_digest_sha256") != TARGET_DIGEST:
        raise TransactionError("run input target digest mismatch")
    if payload.get("model_parameters_ordered", {}).get("a_F") != "1/4":
        raise TransactionError("CP01R2 target a_F must equal 1/4")
    if payload.get("physical_value_M6_assigned") is not False:
        raise TransactionError("M6 must remain unassigned in WP2")
    firewall = run_input.get("execution_firewall", {})
    if firewall.get("solver_authorized") is not False or firewall.get("target_solve_allowed") is not False:
        raise TransactionError("run-input execution firewall mismatch")


def verify_resource_policy(policy: dict[str, Any]) -> None:
    if policy.get("run_id") != RUN_ID:
        raise TransactionError("resource-policy run id mismatch")
    if policy.get("target_contract_digest_sha256") != TARGET_DIGEST:
        raise TransactionError("resource-policy target digest mismatch")
    if policy.get("run_payload_sha256") != RUN_PAYLOAD_SHA256:
        raise TransactionError("resource-policy run payload mismatch")
    env = policy.get("execution_environment", {})
    if env.get("dependency_lock_sha256") != DEPENDENCY_LOCK_SHA256:
        raise TransactionError("dependency lock hash mismatch")
    if env.get("thread_count") != 1 or env.get("gpu_allowed") is not False or env.get("network_access") is not False:
        raise TransactionError("resource environment not fail-closed")
    state = policy.get("current_state", {})
    if state.get("execution_authorized") is not False or state.get("backend_imported") is not False:
        raise TransactionError("resource policy unexpectedly records execution/import")


def verify_backend_rebind(repo_root: Path, rebind: dict[str, Any]) -> None:
    if rebind.get("target_contract_digest_sha256") != TARGET_DIGEST:
        raise TransactionError("backend-rebind target digest mismatch")
    if rebind.get("run_payload_sha256") != RUN_PAYLOAD_SHA256:
        raise TransactionError("backend-rebind run payload mismatch")
    bindings = rebind.get("audited_source_bindings", {})
    expected = {
        "primary_adapter": PRIMARY_SHA256,
        "primary_base": PRIMARY_BASE_SHA256,
        "independent_backend": INDEPENDENT_SHA256,
    }
    for key, expected_sha in expected.items():
        item = bindings.get(key, {})
        if item.get("sha256") != expected_sha:
            raise TransactionError(f"recorded {key} source hash mismatch")
        path = repo_root / str(item.get("path", ""))
        if not path.is_file():
            raise TransactionError(f"missing audited source: {path}")
        actual = file_sha256(path)
        if actual != expected_sha:
            raise TransactionError(f"audited source changed: {item.get('path')} actual={actual}")
    offshell = rebind.get("off_shell_cap_radius_representative", {})
    if offshell.get("classification") != "NUMERICAL_OFF_SHELL_EXTENSION_PRESERVES_TARGET_ZERO_SET":
        raise TransactionError("off-shell cap-radius representative not explicitly classified")
    firewall = rebind.get("firewall", {})
    if firewall.get("backend_import_authorized") is not False or firewall.get("cp01r2_execution_authorized") is not False:
        raise TransactionError("backend rebind unexpectedly authorizes execution")


def verify_interface_and_result(interface: dict[str, Any], result: dict[str, Any]) -> None:
    if interface.get("authority", {}).get("target_digest_sha256") != TARGET_DIGEST:
        raise TransactionError("backend interface target digest mismatch")
    if result.get("target_contract_digest_sha256") != TARGET_DIGEST:
        raise TransactionError("result schema target digest mismatch")
    firewall = interface.get("firewall", {})
    if firewall.get("solver_authorized") is not False or firewall.get("physical_evidence_effect") != "NONE":
        raise TransactionError("backend-interface firewall mismatch")
    gov = result.get("governance", {})
    if gov.get("solver_authorized") is not False or gov.get("physical_evidence_effect") != "NONE":
        raise TransactionError("result-schema firewall mismatch")


def verify_grant_schema(schema: dict[str, Any]) -> None:
    grant = schema.get("grant", {})
    if schema.get("status") != "TEMPLATE_ONLY_NO_GRANT_CREATED":
        raise TransactionError("grant schema status mismatch")
    if grant.get("authorized") is not False or grant.get("automatic_authorization") is not False:
        raise TransactionError("grant template must not authorize execution")
    if grant.get("target_contract_digest_sha256") != TARGET_DIGEST:
        raise TransactionError("grant template target digest mismatch")
    if grant.get("run_payload_sha256") != RUN_PAYLOAD_SHA256:
        raise TransactionError("grant template run payload mismatch")
    if grant.get("target_a_F") != "1/4" or grant.get("control_override_allowed") is not False:
        raise TransactionError("grant target-control contract mismatch")
    protocol = schema.get("consumption_protocol", {})
    if protocol.get("reservation_must_occur_before_backend_import") is not True:
        raise TransactionError("grant reservation order mismatch")
    if protocol.get("replay_after_any_reservation_state") != "REJECT":
        raise TransactionError("grant replay policy mismatch")


def verify_transaction_contract(contract: dict[str, Any]) -> None:
    if contract.get("target_contract_digest_sha256") != TARGET_DIGEST:
        raise TransactionError("transaction target digest mismatch")
    if contract.get("run_payload_sha256") != RUN_PAYLOAD_SHA256:
        raise TransactionError("transaction run payload mismatch")
    firewall = contract.get("firewall", {})
    if firewall.get("physical_execution_authorized") is not False:
        raise TransactionError("transaction unexpectedly authorized")
    if firewall.get("WP3_started") is not False or firewall.get("WP4_started") is not False:
        raise TransactionError("work-package order violated")


def build_release_manifest(repo_root: Path, transaction_contract: dict[str, Any]) -> dict[str, Any]:
    members = transaction_contract.get("release_package_members", [])
    if not isinstance(members, list) or not members:
        raise TransactionError("release package members missing")
    hashes: dict[str, str] = {}
    for rel in members:
        if not isinstance(rel, str) or not rel:
            raise TransactionError("invalid release member path")
        path = repo_root / rel
        if not path.is_file():
            raise TransactionError(f"release member missing: {rel}")
        hashes[rel] = file_sha256(path)
    package_digest = canonical_sha256(hashes)
    return {
        "schema": "universelab.hzt-m0-s6-c-phys-m1.ulsh01-wp2-release-package-manifest.v0.1",
        "classification": "GENERATED_IMPLEMENTATION_QA_ARTIFACT_NO_PHYSICAL_RESULT",
        "run_id": RUN_ID,
        "target_contract_digest_sha256": TARGET_DIGEST,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "member_sha256": hashes,
        "package_digest_sha256": package_digest,
        "solver_executed": False,
        "backend_imported": False,
        "physical_evidence_effect": "NONE",
    }


def validate_grant_bindings(
    grant: dict[str, Any],
    release_manifest: dict[str, Any],
    *,
    repository_commit_sha: str,
    now: datetime,
    control_only: bool,
) -> None:
    if not isinstance(repository_commit_sha, str) or len(repository_commit_sha) != 40:
        raise TransactionError("repository commit SHA must be full 40-hex string")
    try:
        int(repository_commit_sha, 16)
    except ValueError as exc:
        raise TransactionError("repository commit SHA is not hex") from exc
    if grant.get("target_contract_digest_sha256") != TARGET_DIGEST:
        raise TransactionError("grant target digest mismatch")
    if grant.get("run_payload_sha256") != RUN_PAYLOAD_SHA256:
        raise TransactionError("grant run payload mismatch")
    if grant.get("release_package_manifest_sha256") != release_manifest.get("package_digest_sha256"):
        raise TransactionError("grant release package digest mismatch")
    if grant.get("repository_commit_sha") != repository_commit_sha:
        raise TransactionError("grant repository commit mismatch")
    if grant.get("dependency_lock_sha256") != DEPENDENCY_LOCK_SHA256:
        raise TransactionError("grant dependency lock mismatch")
    if grant.get("primary_source_sha256") != PRIMARY_SHA256 or grant.get("primary_base_source_sha256") != PRIMARY_BASE_SHA256:
        raise TransactionError("grant primary source hash mismatch")
    if grant.get("independent_source_sha256") != INDEPENDENT_SHA256:
        raise TransactionError("grant independent source hash mismatch")
    if grant.get("target_a_F") != "1/4" or grant.get("control_override_allowed") is not False:
        raise TransactionError("grant target-control mismatch")
    if grant.get("single_use") is not True or grant.get("automatic_authorization") is not False:
        raise TransactionError("grant single-use/automatic-authorization mismatch")
    if not grant.get("grant_id") or not grant.get("nonce") or not grant.get("authorization_decision_id"):
        raise TransactionError("grant identity fields incomplete")

    if control_only:
        if grant.get("control_only") is not True or grant.get("scope") != "SYNTHETIC_CONTROL_ONLY_NO_BACKEND_IMPORT":
            raise TransactionError("control grant scope mismatch")
    else:
        if grant.get("authorized") is not True:
            raise TransactionError("operative physical grant is not authorized")
        if grant.get("scope") != f"{RUN_ID}_TARGET_ONLY":
            raise TransactionError("operative grant scope mismatch")
        if grant.get("control_only") is True:
            raise TransactionError("control-only grant cannot authorize physical transaction")

    not_before = parse_utc(grant.get("not_before_utc"))
    expires = parse_utc(grant.get("expires_at_utc"))
    now_utc = now.astimezone(timezone.utc)
    if expires <= not_before:
        raise TransactionError("grant time window inverted")
    if now_utc < not_before or now_utc >= expires:
        raise TransactionError("grant outside active time window")


def reservation_path(reservation_dir: str | Path, grant: dict[str, Any]) -> Path:
    gid = str(grant.get("grant_id", ""))
    nonce = str(grant.get("nonce", ""))
    if not gid or not nonce:
        raise TransactionError("grant_id and nonce required for reservation")
    token = hashlib.sha256(f"{gid}\0{nonce}".encode("utf-8")).hexdigest()
    return Path(reservation_dir) / f"{token}.reservation.json"


def atomic_reserve_control_grant(reservation_dir: str | Path, grant: dict[str, Any]) -> Path:
    """Reserve a synthetic CONTROL-ONLY grant. Physical grants are intentionally refused in v0.1."""
    if grant.get("control_only") is not True or grant.get("scope") != "SYNTHETIC_CONTROL_ONLY_NO_BACKEND_IMPORT":
        raise TransactionError("v0.1 reservation API accepts synthetic control grants only")
    root = Path(reservation_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = reservation_path(root, grant)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise ReplayError("single-use grant already reserved; replay rejected") from exc
    record = {
        "schema": "universelab.ulsh01.wp2-control-grant-reservation.v0.1",
        "grant_id": grant["grant_id"],
        "nonce_sha256": hashlib.sha256(str(grant["nonce"]).encode("utf-8")).hexdigest(),
        "state": "RESERVED",
        "control_only": True,
        "backend_imported": False,
        "solver_executed": False,
        "physical_evidence_effect": "NONE",
    }
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    return path


def review(repo_root: Path, manifest_output: Path | None) -> dict[str, Any]:
    target = load_json(repo_root / "ulsh/ULSH-01/C-PHYS/2026-08-21_ULSH01_M1C1_8x8_TargetContract_v0.1.json")
    run_input = load_json(repo_root / "registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_RunInputRebind_v0.1.json")
    resource = load_json(repo_root / "registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_ResourcePolicy_v0.1.json")
    rebind = load_json(repo_root / "registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_BackendRebindContract_v0.1.json")
    grant_schema = load_json(repo_root / "registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_SingleUseGrantSchema_v0.1.json")
    transaction = load_json(repo_root / "registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_TargetTransactionContract_v0.1.json")
    interface = load_json(repo_root / "ulsh/ULSH-01/C-PHYS/2026-08-27_ULSH01_M1C1_8x8_BackendInterfaceContract_v0.1.json")
    result = load_json(repo_root / "ulsh/ULSH-01/C-PHYS/2026-08-27_ULSH01_M1C1_8x8_ResultSchema_v0.1.json")

    verify_target(target)
    verify_run_input(run_input)
    verify_resource_policy(resource)
    verify_backend_rebind(repo_root, rebind)
    verify_interface_and_result(interface, result)
    verify_grant_schema(grant_schema)
    verify_transaction_contract(transaction)
    manifest = build_release_manifest(repo_root, transaction)
    if manifest_output is not None:
        manifest_output.parent.mkdir(parents=True, exist_ok=True)
        manifest_output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "status": "PASS_WP2_TRANSACTION_PREFLIGHT_IMPLEMENTATION_ONLY",
        "run_id": RUN_ID,
        "target_digest_sha256": TARGET_DIGEST,
        "run_payload_sha256": RUN_PAYLOAD_SHA256,
        "release_package_digest_sha256": manifest["package_digest_sha256"],
        "physical_execution_authorized": False,
        "backend_imported": False,
        "solver_executed": False,
        "WP2_closed": False,
        "WP3_started": False,
        "WP4_started": False,
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="ULSH-01 WP2 target-transaction preflight; no physical execution")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--manifest-output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    out = review(args.repo_root.resolve(), args.manifest_output)
    print(json.dumps(out, indent=2, ensure_ascii=False) if args.json else out["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
