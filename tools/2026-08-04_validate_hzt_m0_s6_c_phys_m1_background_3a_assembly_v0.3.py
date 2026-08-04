#!/usr/bin/env python3
"""Fail-closed validation for Background-3A assembly correction and CP01R1 rebind."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
METHOD = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"
TOPOLOGY = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3ATopologyCorrectionContract_v0.2.json"
ASSEMBLY = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3AAssemblyCorrectionContract_v0.3.json"
RUN_V1 = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.1.json"
RUN_V2 = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"
EXPECTED_RUN_HASH = "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302"


class ContractError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def load_json(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    require(path.is_file(), f"missing required JSON: {relative}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {relative}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root must be object: {relative}")
    return value


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_assembly(method: dict[str, Any], topology: dict[str, Any], assembly: dict[str, Any]) -> dict[str, Any]:
    require(method["classification"] == "NUMERICAL_METHOD_PREREGISTRATION_NO_SOLVER_EXECUTION", "method identity drift")
    require(method["primary_discretization"]["regional_node_counts"] == [24, 32, 48, 64, 96], "node schedule drift")
    require(method["frozen_mathematical_problem"]["augmented_unknown_vector"] == [
        "varphi_N_0", "q_N", "A_S_0", "varphi_S_0", "q_S", "rho_N", "rho_S", "k4"
    ], "augmented variable order drift")
    require(topology["canonical_effective_topological_input"]["ordered_vector"] == ["N_F", "N_sigma", "m_sigma"], "topology correction drift")
    require(assembly["status"] == "PREREGISTERED_NOT_EXECUTED_SQUARE_ASSEMBLY_CORRECTED", "assembly status drift")
    count = assembly["counting_audit"]
    require(count["profile_unknowns"] == "8*N", "profile count drift")
    require(count["augmented_unknowns"] == 8, "augmented count drift")
    require(count["total_unknowns"] == "8*N+8", "unknown total drift")
    require(count["regularized_bulk_residuals_at_all_nodes"] == "8*N", "bulk row count drift")
    require(count["cap_and_global_boundary_residuals"] == 8, "boundary row count drift")
    require(count["total_residuals"] == "8*N+8", "residual total drift")
    canonical = assembly["canonical_assembly"]
    require(canonical["regional_node_counts"] == [24, 32, 48, 64, 96], "corrected node schedule drift")
    require(canonical["degree_rule"] == "degree=node_count-1", "degree rule drift")
    require("every Lobatto point" in canonical["bulk_enforcement"], "all-node enforcement missing")
    require(canonical["constraint_role"] == "C_rr remains an independent propagated QA channel and is not appended to the nonlinear residual vector.", "constraint role drift")
    gates = assembly["gate_state"]
    require(gates["BACKGROUND_3B_CP01"] == "SUPERSEDED_BEFORE_EXECUTION", "old CP01 execution status drift")
    require(gates["BACKGROUND_SOLVER_EXECUTION"] == "NOT_AUTHORIZED", "execution opened")
    require(gates["K1-D"] == "NOT_RELEASED" and gates["K1-E"] == "NOT_ADMISSIBLE", "K1 firewall drift")
    require(gates["physical_evidence_effect"] == "NONE", "physical evidence overclaim")
    return {"unknowns": count["total_unknowns"], "residuals": count["total_residuals"]}


def validate_rebound(run_v1: dict[str, Any], run_v2: dict[str, Any]) -> dict[str, Any]:
    old = run_v1["frozen_run_payload"]
    new = run_v2["frozen_run_payload"]
    require(old["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01", "old CP01 identity drift")
    require(new["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1", "new run identity drift")
    require(run_v2["previous_run"]["solver_executed"] is False, "old CP01 execution overclaim")
    require(run_v2["previous_run"]["result_artifact_created"] is False, "old CP01 result overclaim")
    for key in ("model_parameters_ordered", "dimensional_anchor", "topological_sector_ordered", "alpha_H", "seed_set_id", "seed_spec_sha256", "dependency_lock_path", "dependency_lock_sha256"):
        require(new[key] == old[key], f"unexpected control-point change: {key}")
    require(new["assembly_correction_contract"] == ASSEMBLY, "assembly correction not bound")
    require(new["topology_correction_contract"] == TOPOLOGY, "topology correction not bound")
    require(run_v2["frozen_run_payload_sha256"] == EXPECTED_RUN_HASH, "recorded CP01R1 hash drift")
    require(canonical_sha256(new) == EXPECTED_RUN_HASH, "recomputed CP01R1 hash drift")
    assembly = run_v2["discrete_assembly_binding"]
    require(assembly["regional_node_counts"] == [24, 32, 48, 64, 96], "run node schedule drift")
    require(assembly["degree_rule"] == "degree=node_count-1", "run degree rule drift")
    require(assembly["bulk_rows"] == "8*N_at_all_regularized_Lobatto_nodes", "run bulk assembly drift")
    require(assembly["unknowns"] == assembly["residuals"] == "8*N+8", "run square-count drift")
    firewall = run_v2["execution_firewall"]
    require(all(value is False for key, value in firewall.items() if key != "current_execution"), "execution firewall opened")
    require(firewall["current_execution"] == "NOT_EXECUTED", "execution state drift")
    gates = run_v2["gate_state"]
    require(gates["BACKGROUND_RUN_INPUT"] == "FROZEN_CP01R1", "run-input gate drift")
    require(gates["BACKGROUND_SOLVER_IMPLEMENTATION"] == "NOT_PRESENT", "solver implementation overclaim")
    require(gates["BACKGROUND_SOLVER_EXECUTION"] == "NOT_AUTHORIZED", "solver execution opened")
    require(gates["physical_evidence_effect"] == "NONE", "physical evidence overclaim")
    return {"old_run_id": old["run_id"], "new_run_id": new["run_id"], "run_hash": EXPECTED_RUN_HASH}


def validate() -> dict[str, Any]:
    method = load_json(METHOD)
    topology = load_json(TOPOLOGY)
    assembly = load_json(ASSEMBLY)
    run_v1 = load_json(RUN_V1)
    run_v2 = load_json(RUN_V2)
    return {
        "status": "PASS",
        "contract": assembly["schema"],
        "assembly": validate_assembly(method, topology, assembly),
        "run_rebind": validate_rebound(run_v1, run_v2),
        "solver_executed": False,
        "physical_evidence_effect": "NONE",
        "next_block": run_v2["next_allowed_block"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = validate()
    except ContractError as exc:
        payload = {"status": "FAIL", "error": str(exc)}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"FAIL: {exc}")
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else "PASS: Background-3A assembly correction and CP01R1 rebind")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
