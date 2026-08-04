#!/usr/bin/env python3
"""Canonical BACKGROUND-3C entry point with fail-closed authorization v0.3.

This module imports the v0.2 schema adapter, then replaces the legacy
authorization lookup with the canonical 3B `frozen_run_payload` contract.
No numerical execution is permitted by the repository's v0.1 authorization.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_solver_v0.2.py"
RUN_CONTRACT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.1.json"
IMPLEMENTATION_CONTRACT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CImplementationContract_v0.1.json"
AUTHORIZATION = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.1.json"

SPEC = importlib.util.spec_from_file_location("background_3c_schema_adapter_v0_2", ADAPTER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import BACKGROUND-3C v0.2 adapter")
ADAPTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ADAPTER
SPEC.loader.exec_module(ADAPTER)


def require_execution_authorization() -> dict[str, Any]:
    authorization = ADAPTER.BASE.load_json(AUTHORIZATION)
    implementation = ADAPTER.BASE.load_json(IMPLEMENTATION_CONTRACT)
    run = ADAPTER.BASE.load_json(RUN_CONTRACT)
    frozen = run["frozen_run_payload"]
    source = implementation["implementation_source"]

    if authorization.get("authorized") is not True:
        raise ADAPTER.BASE.AuthorizationError(
            "BACKGROUND-3C execution authorization is NOT_GRANTED"
        )
    if authorization.get("status") != "GRANTED_QUARANTINED_DIAGNOSTIC":
        raise ADAPTER.BASE.AuthorizationError(
            "authorization status is not GRANTED_QUARANTINED_DIAGNOSTIC"
        )
    if authorization.get("run_id") != frozen["run_id"]:
        raise ADAPTER.BASE.AuthorizationError("authorization run_id mismatch")
    if authorization.get("implementation_source") != source["canonical_entry_point"]:
        raise ADAPTER.BASE.AuthorizationError("authorization source-path mismatch")
    if (
        authorization.get("implementation_git_blob_sha")
        != source["canonical_entry_point_git_blob_sha"]
    ):
        raise ADAPTER.BASE.AuthorizationError("authorization implementation hash mismatch")
    if authorization.get("run_input_payload_sha256") != run["frozen_run_payload_sha256"]:
        raise ADAPTER.BASE.AuthorizationError("authorization run-input hash mismatch")
    return authorization


# The v0.2 execution function calls the numerical kernel's authorization global.
# Patch that exact global before exposing either command.
ADAPTER.BASE.require_execution_authorization = require_execution_authorization


def audit() -> dict[str, Any]:
    payload = ADAPTER.audit()
    payload["authorization_adapter"] = "v0.3"
    payload["authorization_status"] = ADAPTER.BASE.load_json(AUTHORIZATION)["status"]
    return payload


def execute_quarantined() -> dict[str, Any]:
    require_execution_authorization()
    return ADAPTER.execute_quarantined()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit", "run"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = audit() if args.command == "audit" else execute_quarantined()
    except ADAPTER.BASE.AuthorizationError as exc:
        payload = {"status": "NOT_AUTHORIZED", "error": str(exc), "solver_executed": False}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"NOT AUTHORIZED: {exc}")
        return ADAPTER.BASE.EXIT_NOT_AUTHORIZED
    except (ADAPTER.BASE.ImplementationError, ValueError, KeyError, FloatingPointError) as exc:
        payload = {"status": "FAIL", "error": str(exc)}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"FAIL: {exc}")
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
