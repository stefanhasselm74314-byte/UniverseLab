#!/usr/bin/env python3
"""Validate the append-only Background-3A topology correction v0.2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
V01 = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"
V02 = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3ATopologyCorrectionContract_v0.2.json"
PARENT = ROOT / "registry/2026-08-03_MD2S_R1_C_PHYS_ParentActionOperatorEntryContract_v0.1.json"
GLOBAL = ROOT / "registry/2026-08-03_MD2S_R1_C_PHYS_GlobalConventionFreezeContract_v0.1.json"
M1 = ROOT / "registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json"
OP2B = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceContract_v0.1.json"


class ContractError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def load(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing required artifact: {path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    require(isinstance(value, dict), f"artifact must be an object: {path.relative_to(ROOT)}")
    return value


def validate_payloads(
    v01: dict[str, Any],
    v02: dict[str, Any],
    parent: dict[str, Any],
    global_contract: dict[str, Any],
    m1: dict[str, Any],
    op2b: dict[str, Any],
) -> dict[str, Any]:
    require(v01["model_id"] == "HZT-M0-S6-C-PHYS-M1", "v0.1 model drift")
    require(v01["status"] == "PREREGISTERED_NOT_EXECUTED", "v0.1 execution/status drift")
    require(v01["solver_authorized"] is False, "v0.1 solver authorization drift")
    require(
        v01["frozen_mathematical_problem"]["topological_inputs"]
        == ["N_F", "m_N", "m_S", "n_N", "n_S"],
        "historical v0.1 defect no longer represented append-only",
    )

    require(v02["model_id"] == "HZT-M0-S6-C-PHYS-M1", "v0.2 model drift")
    require(v02["track_id"] == "MD2S-R1-C-PHYS", "v0.2 track drift")
    require(
        v02["classification"] == "APPEND_ONLY_MODEL_IDENTITY_CORRECTION_NO_SOLVER_EXECUTION",
        "v0.2 classification drift",
    )
    require(v02["status"] == "ACTIVE_CANONICAL_CORRECTION", "v0.2 status drift")
    require(v02["solver_authorized"] is False, "v0.2 solver authorization drift")
    require(v02["physical_evidence_effect"] == "NONE", "v0.2 physical evidence drift")
    require(v02["corrects_contract"] == str(V01.relative_to(ROOT)), "corrected-contract pointer drift")
    require(v02["corrected_field"] == "frozen_mathematical_problem.topological_inputs", "corrected field drift")
    require(v02["defect"]["detected_before_run_input_freeze"] is True, "detection timing drift")
    require(v02["defect"]["solver_or_result_affected"] is False, "unfounded result contamination claim")

    effective = v02["canonical_effective_topological_input"]
    require(effective["ordered_vector"] == ["N_F", "N_sigma", "m_sigma"], "canonical topology vector drift")
    require(effective["count"] == 3, "canonical topology count drift")
    require(effective["domains"] == {
        "N_F": "integer",
        "N_sigma": "integer",
        "m_sigma": "positive_integer",
    }, "canonical topology domains drift")
    require(effective["fixed_per_run"] is True, "topological sector not fixed per run")
    require(effective["sector_change_requires_new_run_id"] is True, "sector-change firewall lost")

    forbidden = set(v02["forbidden_regional_expansion"]["forbidden_labels"])
    require(forbidden == {"m_N", "m_S", "n_N", "n_S"}, "forbidden regional labels drift")
    require(
        v02["forbidden_regional_expansion"]["future_two_cap_phase_extension"]
        == "REQUIRES_NEW_PARENT_ACTION_NEW_MODEL_ID_AND_NEW_BOUNDARY_OPERATOR",
        "new-model firewall drift",
    )

    require(
        parent["parent_action"]["D_a_sigma"] == "partial_a sigma-q_sigma A_a",
        "parent action no longer has the single sigma field",
    )
    require(
        parent["cap_and_global_system"]["winding"]["d_chi"]
        == "2 pi N_sigma/Delta_chi-q_sigma A_chi_Sigma",
        "parent winding identity drift",
    )
    require(
        global_contract["discrete_sector_roles"]["fixed_per_run"]
        == ["N_F", "N_sigma", "m_sigma"],
        "Freeze-1A topology sector drift",
    )
    require(
        global_contract["charge_lattice"]["cap_charge"] == "q_sigma=m_sigma*q_ref",
        "charge lattice drift",
    )
    require(
        m1["discrete_sector"] == {
            "N_F": "integer",
            "N_sigma": "integer",
            "m_sigma": "positive_integer",
            "fixed_per_BVP_run": True,
            "sector_change_requires_new_run_label": True,
        },
        "M1 discrete sector drift",
    )
    require(
        m1["dimensionless_specialization"]["cap_quantities"]["d_chi"]
        == "N_sigma-m_sigma*q_hat*a_chi_Sigma",
        "M1 cap winding drift",
    )
    require(
        op2b["augmented_parameter_space"]["discrete_sector"]
        == "N_F, N_sigma and m_sigma are fixed integer labels per operator instance.",
        "Operator-2B topology sector drift",
    )

    require(v02["inheritance_from_v0_1"]["override_rule"].startswith("Only frozen_mathematical_problem.topological_inputs"), "override scope drift")
    status = v02["effective_background_3a_status"]
    require(status["status"] == "PREREGISTERED_NOT_EXECUTED_CORRECTED_TO_SINGLE_CAP_PHASE", "effective status drift")
    require(status["method_frozen"] is True, "method freeze lost")
    require(status["topology_schema_frozen"] is True, "topology schema not frozen")
    require(status["exact_run_input_frozen"] is False, "run input overclaim")
    require(status["current_execution"] == "NOT_EXECUTED", "execution overclaim")
    require(status["physical_background"] == "NOT_ESTABLISHED", "background overclaim")

    gates = v02["gate_state"]
    expected_gates = {
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED_CORRECTED_TO_SINGLE_CAP_PHASE",
        "BACKGROUND_TOPOLOGY_SCHEMA": "FROZEN_SINGLE_CAP_PHASE",
        "BACKGROUND_RUN_INPUT": "NOT_FROZEN",
        "BACKGROUND_SOLVER_EXECUTION": "FORBIDDEN_PENDING_BACKGROUND_3B_AND_LATER_GATE",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "full_linearized_boundary_trace_rank": "NOT_PROVEN",
        "Fredholm_property": "NOT_PROVEN",
        "continuum_BVP_Jacobian": "NOT_PROVEN",
        "physical_background": "NOT_ESTABLISHED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected_gates.items():
        require(gates.get(key) == value, f"gate drift: {key}")

    require(v02["next_allowed_block"] == "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY", "next block drift")
    require("(N_F,N_sigma,m_sigma)" in v02["background_3b_requirement"], "Background-3B vector requirement missing")

    return {
        "status": "PASS",
        "historical_v0_1_vector": v01["frozen_mathematical_problem"]["topological_inputs"],
        "canonical_v0_2_vector": effective["ordered_vector"],
        "canonical_count": effective["count"],
        "single_cap_phase": True,
        "solver_authorized": False,
        "current_execution": status["current_execution"],
        "next_block": v02["next_allowed_block"],
        "physical_evidence_effect": v02["physical_evidence_effect"],
        "gate_state": expected_gates,
    }


def validate() -> dict[str, Any]:
    return validate_payloads(load(V01), load(V02), load(PARENT), load(GLOBAL), load(M1), load(OP2B))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = validate()
    except ContractError as exc:
        if args.json:
            print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2, sort_keys=True))
        else:
            print(f"FAIL: {exc}")
        return 1
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("PASS: Background-3A topology corrected to the single-cap-phase sector")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
