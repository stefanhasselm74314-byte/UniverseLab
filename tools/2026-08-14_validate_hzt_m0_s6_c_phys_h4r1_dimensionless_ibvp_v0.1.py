#!/usr/bin/env python3
"""Fail-closed validator for the H4R1 formal IBVP preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REGISTRY = Path("registry/2026-08-14_HZT-M0_S6_C-PHYS_H4R1_DimensionlessIBVP_ConstraintBoundaryRank_v0.1.json")
LEDGER = Path("science/hzt-m0/md2s/2026-08-14_HZT-M0_S6_C-PHYS_H4R1_DimensionlessIBVP_ConstraintBoundaryRank_v0.1.md")


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def det3(m):
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def validate() -> dict:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    ledger = LEDGER.read_text(encoding="utf-8")

    assert reg["block_id"] == "C-PHYS-PARENT-H4R1-DIMENSIONLESS-IBVP-CONSTRAINT-PROPAGATION-AND-BOUNDARY-RANK-PREFLIGHT"
    assert reg["solver_execution"] is False
    assert reg["physical_backend_imported"] is False
    assert reg["physical_evidence_effect"] == "NONE"

    source_results = []
    for binding in reg["source_bindings"]:
        path = Path(binding["path"])
        assert path.exists(), path
        actual = git_blob_sha1(path)
        assert actual == binding["git_blob_sha1"], (path, actual, binding["git_blob_sha1"])
        source_results.append({"path": str(path), "sha1": actual})

    firewall = reg["external_material_firewall"]
    assert firewall["gemini_blocks"] == "EXTERNAL_UNVERIFIED_GEMINI_DRAFT"
    assert firewall["gemini_equations_used_as_premises"] is False
    assert firewall["two_time_signature_imported"] is False
    assert reg["canonical_signature"]["ambient_signature"] == "(-,+,+,+,+,+)"
    assert reg["canonical_signature"]["physical_times"] == 1

    dim = reg["dimensionless_variables"]
    assert dim["tau"] == "M6*t"
    assert dim["x"] == "M6*r"
    assert dim["varphi"] == "phi/M6^2"
    assert dim["ell"] == "M6*L"
    assert dim["a_chi"] == "A_chi/M6"

    principal = reg["principal_characteristic_preflight"]
    assert principal["result"] == "PASS_LOCAL_WAVE_TYPE_CHARACTERISTIC_PREFLIGHT"
    assert principal["global_hyperbolicity_proven"] is False
    assert principal["ghost_freedom_proven"] is False

    prop = reg["bulk_constraint_propagation"]
    assert prop["combined_identity"] == "nabla^A E_AB=0"
    assert prop["result"] == "PASS_FORMAL_HOMOGENEOUS_BULK_CONSTRAINT_PROPAGATION_IDENTITY"
    assert prop["incoming_boundary_constraint_compatibility"] == "OPEN"

    boundary = reg["cap_boundary_normal_rank"]
    assert det3(boundary["metric_jacobian"]) == -4
    assert boundary["metric_determinant"] == -4
    assert boundary["result"] == "PASS_LOCAL_ALGEBRAIC_BOUNDARY_NORMAL_RANK_5"
    assert boundary["full_two_sided_complementing_condition"] == "OPEN"

    flux = reg["flux_patch_propagation"]
    assert flux["R_patch"] == "a_chi_N-a_chi_S-N_F/q_hat"
    assert flux["result"] == "PASS_EXACT_PROPAGATION_CONDITION_NOT_AUTOMATIC_GLOBAL_CLOSURE"

    gate = reg["gate_disposition"]
    assert gate["physical_parent_solve_authorized"] is False
    assert gate["D2NQ_parent_dynamic_selection"] == "OPEN_NOT_EXECUTED"
    assert gate["K1-D"] == "NOT_RELEASED"
    assert gate["K1-E"] == "NOT_ADMISSIBLE"
    assert gate["WP4"] == "BLOCKED"
    assert gate["physical_evidence_effect"] == "NONE"
    assert gate["boundary_constraint_preservation"] == "OPEN"
    assert gate["global_IBVP_existence_uniqueness"] == "OPEN"

    for phrase in [
        "det B_g=-4",
        "bulk Bianchi propagation identity: PASS",
        "cap incoming-constraint compatibility: OPEN",
        "PHYSICAL_PARENT_SOLVE = NOT_AUTHORIZED",
        "K1-D = NOT_RELEASED",
        "PHYSICAL_EVIDENCE_EFFECT = NONE",
    ]:
        assert phrase in ledger, phrase

    return {
        "status": "PASS",
        "block_id": reg["block_id"],
        "source_bindings": source_results,
        "boundary_metric_det": boundary["metric_determinant"],
        "physical_solver_executed": False,
        "physical_evidence_effect": "NONE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS H4R1 dimensionless IBVP / constraint / boundary-rank contract")


if __name__ == "__main__":
    main()
