#!/usr/bin/env python3
"""Canonical v0.2 Background-3C audit gate.

This adapter binds the audit to the exact Background-3B seed specification and
the canonical primary-kernel v0.2 adapter. Execution remains denied.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_gate_v0.1.py"
CANONICAL_KERNEL = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py"
CANONICAL_KERNEL_BLOB = "e232537ab80f099b0b3a914c509041c13825e950"
SPEC = importlib.util.spec_from_file_location("background3c_gate_base_v01", BASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import Background-3C gate v0.1")
BASE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)

BASE.KERNEL_PATH = CANONICAL_KERNEL
BASE.EXPECTED_KERNEL_BLOB = CANONICAL_KERNEL_BLOB


def verify_contract_chain() -> dict[str, Any]:
    method = BASE.load_json(BASE.METHOD_PATH)
    topology = BASE.load_json(BASE.TOPOLOGY_PATH)
    assembly = BASE.load_json(BASE.ASSEMBLY_PATH)
    run = BASE.load_json(BASE.RUN_PATH)
    seeds = BASE.load_json(BASE.SEED_PATH)
    authorization = BASE.load_json(BASE.AUTH_DENIED_PATH)
    result_schema = BASE.load_json(BASE.RESULT_SCHEMA_PATH)
    resources = BASE.load_json(BASE.RESOURCE_POLICY_PATH)

    payload = run["frozen_run_payload"]
    BASE.require(payload["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1", "run id drift")
    BASE.require(run["frozen_run_payload_sha256"] == BASE.EXPECTED_RUN_HASH, "recorded run hash drift")
    BASE.require(BASE.canonical_sha256(payload) == BASE.EXPECTED_RUN_HASH, "recomputed run hash drift")
    BASE.require(payload["topological_sector_ordered"] == {"N_F": 1, "N_sigma": 1, "m_sigma": 1}, "topological sector drift")
    BASE.require(topology["canonical_effective_topological_input"]["ordered_vector"] == ["N_F", "N_sigma", "m_sigma"], "topology contract drift")
    BASE.require(assembly["canonical_assembly"]["regional_node_counts"] == [24, 32, 48, 64, 96], "assembly node schedule drift")
    BASE.require(assembly["canonical_assembly"]["degree_rule"] == "degree=node_count-1", "degree rule drift")
    BASE.require(assembly["counting_audit"]["total_unknowns"] == assembly["counting_audit"]["total_residuals"] == "8*N+8", "square count drift")
    BASE.require(method["primary_discretization"]["regional_node_counts"] == [24, 32, 48, 64, 96], "method node schedule drift")
    BASE.require(method["nonlinear_method"]["method"] == "DAMPED_NEWTON_TRUST_REGION", "nonlinear method drift")
    BASE.require(method["nonlinear_method"]["linear_solver"] == "rank-revealing QR primary with SVD diagnostic", "linear solver drift")
    BASE.require(method["normalization_and_norms"]["bulk_component_scaling"] == "unit dimensionless scaling; every component also reported separately", "bulk scaling drift")
    BASE.require(method["normalization_and_norms"]["boundary_component_scaling"] == "unit dimensionless scaling; every component also reported separately", "boundary scaling drift")

    seed_generation = seeds["seed_generation"]
    BASE.require(seeds["seed_set_id"] == payload["seed_set_id"], "seed set identity drift")
    BASE.require(seed_generation["seed_count"] == 7, "seed count drift")
    BASE.require(seed_generation["amplitude_scale"] == "1/20", "seed amplitude drift")
    BASE.require(seed_generation["multipliers_in_order"] == ["0", "1/8", "-1/8", "1/4", "-1/4", "1/2", "-1/2"], "seed multiplier drift")

    BASE.require(authorization["status"] == "NOT_GRANTED" and authorization["authorized"] is False, "authorization denial drift")
    BASE.require(authorization["required_future_grant_artifact"] == str(BASE.FUTURE_GRANT_PATH.relative_to(ROOT)), "future grant path drift")
    BASE.require(not BASE.FUTURE_GRANT_PATH.exists(), "unexpected execution grant artifact present")
    BASE.require(result_schema["status"] == "FROZEN_NOT_INSTANTIATED", "result schema status drift")
    BASE.require(result_schema["current_state"]["result_artifact_created"] is False, "result artifact overclaim")
    BASE.require(resources["status"] == "FROZEN_EXECUTION_NOT_AUTHORIZED", "resource policy status drift")
    BASE.require(resources["execution_environment"]["network_access"] is False, "network access opened")
    BASE.require(resources["execution_environment"]["randomness"] is False, "randomness opened")
    return {
        "method": method,
        "assembly": assembly,
        "run": run,
        "payload": payload,
        "authorization": authorization,
        "result_schema": result_schema,
        "resources": resources,
        "seeds": seeds,
    }


BASE.verify_contract_chain = verify_contract_chain


def audit() -> dict[str, Any]:
    payload = BASE.audit()
    kernel = BASE.load_kernel()
    payload["gate_adapter"] = "v0.2"
    payload["canonical_kernel"] = str(CANONICAL_KERNEL.relative_to(ROOT))
    payload["seed_amplitude_scale"] = kernel.SEED_AMPLITUDE_SCALE
    payload["seed_multipliers"] = list(kernel.SEED_MULTIPLIERS)
    BASE.require(kernel.SEED_AMPLITUDE_SCALE == 1.0 / 20.0, "kernel seed amplitude drift")
    BASE.require(kernel.SEED_MULTIPLIERS == (0.0, 1/8, -1/8, 1/4, -1/4, 1/2, -1/2), "kernel seed multiplier drift")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit", "run"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "run":
            BASE.require_execution_authorization()
            raise BASE.GateError("unreachable execution path")
        payload = audit()
    except BASE.AuthorizationError as exc:
        payload = {"status": "NOT_AUTHORIZED", "error": str(exc), "solver_executed": False, "result_artifact_created": False}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"NOT AUTHORIZED: {exc}")
        return BASE.EXIT_NOT_AUTHORIZED
    except (BASE.GateError, ValueError, KeyError, FloatingPointError) as exc:
        payload = {"status": "FAIL", "error": str(exc), "solver_executed": False}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"FAIL: {exc}")
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
