#!/usr/bin/env python3
"""ULSH-01 / WP3-D3H1 CP01R2 transaction supervisor v1.1.

Append-only audit wrapper around v1.0. It corrects only the static H3 provenance
probe; the source-bound transaction execution implementation remains v1.0 and
is pinned independently in the D3H1 contract. Default invocation is no-execute.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3h1_cp01r2_transaction_v1.0.py"
TARGET_PATH = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3h1_cp01r2_target_v1.0.py"
H3_REFERENCE = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.4.py"

_SPEC = importlib.util.spec_from_file_location("ulsh_cp01r2_transaction_v10", BASE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("cannot load CP01R2 transaction v1.0")
BASE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = BASE
_SPEC.loader.exec_module(BASE)

RUN_ID = BASE.RUN_ID
AuthorizationDenied = BASE.AuthorizationDenied
TransactionError = BASE.TransactionError
ResultClosureError = BASE.ResultClosureError


def static_preflight() -> dict[str, object]:
    if BASE.RELEASE_PATH.exists() or BASE.GRANT_PATH.exists():
        raise TransactionError("D3H1 no-execution phase requires release/grant absence")
    if BASE.git_blob_sha1(BASE.TARGET) != BASE.EXPECTED_TARGET_BLOB:
        raise TransactionError("CP01R2 target blob drift")
    if BASE.git_blob_sha1(BASE.RESULT_SCHEMA) != BASE.EXPECTED_RESULT_SCHEMA_BLOB:
        raise TransactionError("CP01R2 result schema blob drift")
    d3 = BASE.load_json(BASE.D3_REVIEW)
    if d3["release_blockers"]["D3-B01"]["status"] != "OPEN_RELEASE_BLOCKER" or d3["release_blockers"]["D3-B02"]["status"] != "OPEN_RELEASE_BLOCKER":
        raise TransactionError("D3 blocker basis drift")
    contract = BASE.load_json(BASE.CONTRACT)
    if contract["status"] != "PASS_D3H1_IMPLEMENTED_NO_EXECUTION_PENDING_INDEPENDENT_REVIEW":
        raise TransactionError("D3H1 contract status drift")
    if contract["run_id"] != BASE.RUN_ID or contract["run_payload_sha256"] != BASE.RUN_PAYLOAD_SHA256 or contract["schedule_sha256"] != BASE.SCHEDULE_SHA256:
        raise TransactionError("D3H1 contract run binding drift")
    bundle = BASE.source_bundle_sha256(contract)

    target_spec = importlib.util.spec_from_file_location("ulsh_cp01r2_target_audit_v11", TARGET_PATH)
    if target_spec is None or target_spec.loader is None:
        raise TransactionError("cannot load target audit")
    target = importlib.util.module_from_spec(target_spec)
    sys.modules[target_spec.name] = target
    target_spec.loader.exec_module(target)
    target_audit = target.audit_target()
    if target_audit["solver_calls"] != 0 or target_audit["physical_solve_executed"] is not False:
        raise TransactionError("target audit violated no-execution firewall")

    h3_source = H3_REFERENCE.read_text(encoding="utf-8")
    for fragment in ("COMMITTING_RESULT", "json_safe_diagnostic_projection", "COMMITTED_INDETERMINATE"):
        if fragment not in h3_source:
            raise TransactionError(f"H3 provenance invariant missing: {fragment}")

    return {
        "status": "PASS_WP3_D3H1_CP01R2_TRANSACTION_STATIC_PREFLIGHT_NO_EXECUTION",
        "run_id": BASE.RUN_ID,
        "run_payload_sha256": BASE.RUN_PAYLOAD_SHA256,
        "schedule_sha256": BASE.SCHEDULE_SHA256,
        "source_bundle_sha256": bundle,
        "D3-B01": "IMPLEMENTED_PENDING_INDEPENDENT_REVIEW",
        "D3-B02": "IMPLEMENTED_PENDING_INDEPENDENT_REVIEW",
        "release_authorization_present": False,
        "single_use_grant_present": False,
        "solver_calls": 0,
        "physical_solve_authorized": False,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
    }


def execute(transaction_root: Path) -> dict[str, object]:
    return BASE.execute(transaction_root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--transaction-root")
    args = parser.parse_args()
    if args.execute:
        if not args.transaction_root:
            raise AuthorizationDenied("--transaction-root required")
        print(json.dumps(execute(Path(args.transaction_root)), indent=2, sort_keys=True))
        return 0
    print(json.dumps(static_preflight(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
