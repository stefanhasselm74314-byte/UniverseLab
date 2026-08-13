#!/usr/bin/env python3
"""Validate the no-execution H4 axisymmetric time-radial M1 closure contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-08-13_HZT-M0_S6_C-PHYS_H4_AxisymmetricTimeRadial_M1_ClosureRankTest_v0.1.json"


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def validate() -> dict:
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    errors: list[str] = []

    expected = {
        "schema": "universelab.hzt-m0-s6-c-phys.h4-axisymmetric-time-radial-m1-closure.v1",
        "version": "0.1.0",
        "model_id": "HZT-M0-S6-C-PHYS-M1",
        "baseline_main_sha": "713de6edfc9c7fba4e8594f3af12a3d9a80f13af",
        "classification": "FORMAL_REDUCTION_CLOSURE_GAUGE_COUNT_AND_LOCAL_PRINCIPAL_RANK_PREFLIGHT_NO_EXECUTION",
        "solver_execution": False,
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            errors.append(f"{key}: expected {value!r}, got {data.get(key)!r}")

    for binding in data.get("source_bindings", []):
        path = ROOT / binding["path"]
        if not path.exists():
            errors.append(f"missing source binding: {binding['path']}")
            continue
        actual = git_blob_sha1(path)
        if actual != binding["git_blob_sha1"]:
            errors.append(
                f"source binding mismatch {binding['path']}: "
                f"expected {binding['git_blob_sha1']}, got {actual}"
            )

    firewall = data.get("external_material_firewall", {})
    if firewall.get("gemini_blocks") != "EXTERNAL_UNVERIFIED_GEMINI_DRAFT":
        errors.append("Gemini firewall missing")
    if firewall.get("gemini_equations_used_as_premises") is not False:
        errors.append("Gemini equations may not be premises")
    if firewall.get("two_time_signature_imported") is not False:
        errors.append("two-time signature import forbidden")

    sig = data.get("canonical_signature", {})
    if sig.get("ambient_signature") != "(-,+,+,+,+,+)" or sig.get("physical_times") != 1:
        errors.append("canonical one-time signature not preserved")

    count = data.get("gauge_and_equation_count", {})
    if count.get("independent_unknowns_modulo_gauge") != 5:
        errors.append("wrong gauge-reduced unknown count")
    if count.get("independent_equations_modulo_identities") != 5:
        errors.append("wrong independent equation count")
    if count.get("result") != "STRUCTURALLY_SQUARE_MODULO_2D_DIFFEO_GAUGE":
        errors.append("structural square result missing")

    rank = data.get("local_principal_rank_preflight", {})
    if rank.get("gravitational_matrix_determinant") != "12*a^7*L":
        errors.append("gravitational principal determinant changed")
    if rank.get("result") != "PASS_LOCAL_FIELDSPACE_PRINCIPAL_HESSIAN_NONDEGENERATE_RANK_5_IN_STATED_REPRESENTATIVE":
        errors.append("local rank preflight not PASS")

    mixed = data.get("mixed_tr_constraint", {})
    if mixed.get("equation") != "R_tr=kappa6^2*T_tr":
        errors.append("mixed Einstein constraint missing")

    sel = data.get("d2nq_solution_derived_selection_test", {})
    if sel.get("fit_free_differential_residual") != "R_Lambda_m=d2(B_squared)/dN2+3*d(B_squared)/dN":
        errors.append("fit-free Lambda+dust residual missing")
    if "POST_SOLUTION_DIAGNOSTICS" not in sel.get("governance", ""):
        errors.append("post-solution diagnostic firewall missing")

    disp = data.get("h4_disposition", {})
    required_disp = {
        "time_dependent_bulk_closure_in_axisymmetric_Ftr0_subsector": "PASS_FORMAL",
        "structural_square_count": "PASS_MODULO_GAUGE",
        "local_principal_rank_capability": "PASS_FIELDSPACE_NONDEGENERATE",
        "D2NQ_parent_dynamic_selection": "OPEN_NOT_EXECUTED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "WP4": "BLOCKED",
        "physical_evidence_effect": "NONE",
    }
    for key, value in required_disp.items():
        if disp.get(key) != value:
            errors.append(f"gate {key}: expected {value}, got {disp.get(key)}")

    forbidden = set(data.get("forbidden_inferences", []))
    for item in {
        "NO_FORMAL_REDUCED_CLOSURE_AS_EXISTENCE_OR_UNIQUENESS_PROOF",
        "NO_LOCAL_FIELDSPACE_RANK_AS_GLOBAL_HYPERBOLICITY_OR_GHOST_FREEDOM",
        "NO_B_LAMBDA_OR_B_m_AS_FREE_BOUNDARY_KNOBS",
        "NO_PHYSICAL_EVIDENCE_PROMOTION",
    }:
        if item not in forbidden:
            errors.append(f"missing forbidden inference: {item}")

    return {
        "ok": not errors,
        "errors": errors,
        "contract": str(CONTRACT.relative_to(ROOT)),
        "status": data.get("status"),
        "next_candidate": data.get("next_candidate"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["ok"]:
        print("PASS: H4 axisymmetric time-radial M1 closure contract is internally consistent")
    else:
        for error in result["errors"]:
            print(f"FAIL: {error}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
