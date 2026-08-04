#!/usr/bin/env python3
"""Canonical schema adapter for the quarantined BACKGROUND-3C solver v0.1.

The numerical kernel remains in v0.1. This adapter fixes only repository-schema
bindings:

- M1 model parameters and the single-cap sector come from the canonical 3B
  `frozen_run_payload`.
- preregistered node counts come from the canonical 3A method contract.
- node count N maps to polynomial degree N-1.

The execution authorization remains a separate fail-closed artifact.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_solver_v0.1.py"
RUN_CONTRACT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.1.json"
METHOD_CONTRACT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"

SPEC = importlib.util.spec_from_file_location("background_3c_kernel_v0_1", BASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to import BACKGROUND-3C v0.1 numerical kernel")
BASE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BASE
SPEC.loader.exec_module(BASE)


def _as_float(value: Any) -> float:
    if isinstance(value, str) and "/" in value:
        return float(Fraction(value))
    return float(value)


def model_from_run_contract(*, control_a_F: bool = False):
    run = BASE.load_json(RUN_CONTRACT)
    values = run["frozen_run_payload"]["model_parameters_ordered"]
    return BASE.Model(
        Lambda_hat=_as_float(values["Lambda_hat"]),
        mhat_phi_sq=_as_float(values["mhat_phi_sq"]),
        a_F=0.0 if control_a_F else _as_float(values["a_F"]),
        lambda_hat=_as_float(values["lambda_hat"]),
        z_sigma_hat=_as_float(values["z_sigma_hat"]),
        q_hat=_as_float(values["q_hat"]),
    )


def sector_from_run_contract():
    run = BASE.load_json(RUN_CONTRACT)
    values = run["frozen_run_payload"]["topological_sector_ordered"]
    return BASE.Sector(
        N_F=int(values["N_F"]),
        N_sigma=int(values["N_sigma"]),
        m_sigma=int(values["m_sigma"]),
    )


def preregistered_node_counts() -> tuple[int, ...]:
    method = BASE.load_json(METHOD_CONTRACT)
    counts = tuple(int(value) for value in method["primary_discretization"]["regional_node_counts"])
    if counts != (24, 32, 48, 64, 96):
        raise BASE.ImplementationError(f"unexpected 3A node schedule: {counts}")
    return counts


def degree_from_node_count(node_count: int) -> int:
    if node_count < 3:
        raise ValueError("node count must be at least three")
    return node_count - 1


def execute_quarantined() -> dict[str, Any]:
    BASE.require_execution_authorization()
    run = BASE.load_json(RUN_CONTRACT)
    model = model_from_run_contract(control_a_F=False)
    sector = sector_from_run_contract()
    node_count = preregistered_node_counts()[0]
    degree = degree_from_node_count(node_count)
    results = []
    for index, seed in enumerate(BASE.seven_seeds(degree)):
        solve = BASE.damped_newton(seed, degree, model, sector)
        results.append(
            {
                "seed_index": index,
                "converged": bool(solve["converged"]),
                "history": solve["history"],
            }
        )
    return {
        "classification": "QUARANTINED_DIAGNOSTIC_EXECUTION_RAW",
        "run_id": run["frozen_run_payload"]["run_id"],
        "regional_node_count": node_count,
        "polynomial_degree": degree,
        "seed_results": results,
        "physical_evidence_effect": "NONE",
    }


# Patch the imported module's global bindings so BASE.audit() uses the canonical
# 3A/3B schemas without altering the frozen numerical kernel.
BASE.model_from_run_contract = model_from_run_contract
BASE.sector_from_run_contract = sector_from_run_contract
BASE.execute_quarantined = execute_quarantined


def audit() -> dict[str, Any]:
    payload = BASE.audit()
    payload["schema_adapter"] = "v0.2"
    payload["run_id"] = BASE.load_json(RUN_CONTRACT)["frozen_run_payload"]["run_id"]
    payload["preregistered_node_counts"] = list(preregistered_node_counts())
    payload["node_count_to_degree_rule"] = "degree=node_count-1"
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit", "run"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = audit() if args.command == "audit" else execute_quarantined()
    except BASE.AuthorizationError as exc:
        payload = {"status": "NOT_AUTHORIZED", "error": str(exc), "solver_executed": False}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"NOT AUTHORIZED: {exc}")
        return BASE.EXIT_NOT_AUTHORIZED
    except (BASE.ImplementationError, ValueError, KeyError, FloatingPointError) as exc:
        payload = {"status": "FAIL", "error": str(exc)}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"FAIL: {exc}")
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
