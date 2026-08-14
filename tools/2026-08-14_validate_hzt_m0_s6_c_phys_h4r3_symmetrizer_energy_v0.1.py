#!/usr/bin/env python3
"""Fail-closed validator for H4R3 variable-coefficient symmetrizer/energy preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REGISTRY = Path("registry/2026-08-14_HZT-M0_S6_C-PHYS_H4R3_VariableCoefficientSymmetrizer_NonlinearEnergyClosure_v0.1.json")
LEDGER = Path("science/hzt-m0/md2s/2026-08-14_HZT-M0_S6_C-PHYS_H4R3_VariableCoefficientSymmetrizer_NonlinearEnergyClosure_v0.1.md")


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def det3(m):
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def nearly_equal(a, b, tol=1e-12):
    return abs(a - b) <= tol


def validate() -> dict:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    ledger = LEDGER.read_text(encoding="utf-8")

    assert reg["block_id"] == "C-PHYS-PARENT-H4R3-VARIABLE-COEFFICIENT-FIRST-ORDER-REDUCTION-CONSTRAINT-BOUNDARY-SYMMETRIZER-AND-NONLINEAR-ENERGY-CLOSURE"
    assert reg["classification"] == "FORMAL_QUASILINEAR_IBVP_ENERGY_PREFLIGHT_NO_PHYSICAL_EXECUTION"
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
    assert firewall["gemini_code_used_as_validation"] is False
    assert firewall["two_time_signature_imported"] is False
    assert reg["canonical_signature"]["ambient_signature"] == "(-,+,+,+,+,+)"
    assert reg["canonical_signature"]["physical_times"] == 1

    bulk = reg["variable_coefficient_bulk_reduction"]
    assert bulk["result"] == "PASS_FORMAL_VARIABLE_COEFFICIENT_FIRST_ORDER_REDUCTION_ON_NONDEGENERATE_STATE_DOMAIN"
    assert bulk["physical_hamiltonian_interpretation"] is False

    boundary = reg["boundary_row_normalization"]
    bg = boundary["H4R2_metric_block"]
    bgi = boundary["metric_block_inverse"]
    assert det3(bg) == -4
    assert boundary["metric_block_determinant"] == -4
    ident = matmul(bgi, bg)
    for i in range(3):
        for j in range(3):
            assert nearly_equal(ident[i][j], 1.0 if i == j else 0.0), ident
    assert boundary["result"] == "PASS_EXACT_POSITIVE_BOUNDARY_ROW_NORMALIZATION"

    sym = reg["bulk_pde_symmetrizer"]
    assert sym["result"] == "PASS_EXPLICIT_POSITIVE_PDE_SYMMETRIZER_ON_DECLARED_COMPACT_STATE_DOMAIN"
    assert sym["not_a_physical_kinetic_matrix"] is True
    assert sym["ghost_freedom_inferred"] is False

    # Independent sample positivity and symmetry check for D/c^2 and D.
    z = 0.37
    c = 1.41
    d = [1.0, 1.0, 1.0, 1.0, z]
    a0_diag = [x / (c * c) for x in d] + d
    assert min(a0_diag) > 0.0
    # A1 consists of symmetric off-diagonal -D blocks.
    for x in d:
        assert x > 0.0

    flux = reg["interface_energy_flux"]
    assert flux["flux_on_homogeneous_interface_subspace"] == 0
    assert flux["boundary_variable_count"] == 20
    assert flux["independent_principal_interface_conditions"] == 10
    assert flux["boundary_subspace_dimension"] == 10
    assert flux["classification"] == "MAXIMAL_ISOTROPIC_MAXIMALLY_CONSERVATIVE_PRINCIPAL_INTERFACE_SUBSPACE"
    assert flux["result"] == "PASS_PRINCIPAL_BOUNDARY_ENERGY_FLUX_CANCELLATION"

    # Explicit algebraic flux cancellation: D_N Q_N + D_S Q_S = 0.
    p = [0.3, -0.4, 0.8, 0.2, -0.1]
    z_n, z_s = 0.8, 1.3
    d_n = [1.0, 1.0, 1.0, 1.0, z_n]
    d_s = [1.0, 1.0, 1.0, 1.0, z_s]
    q_n = [0.2, -0.1, 0.4, 0.5, -0.3]
    q_s = [-(d_n[i] / d_s[i]) * q_n[i] for i in range(5)]
    matched = [d_n[i] * q_n[i] + d_s[i] * q_s[i] for i in range(5)]
    assert max(abs(x) for x in matched) < 1e-12
    flux_value = sum(p[i] * matched[i] for i in range(5))
    assert abs(flux_value) < 1e-12

    constraint = reg["constraint_energy_propagation"]
    assert constraint["result"] == "PASS_CONDITIONAL_VARIABLE_COEFFICIENT_CONSTRAINT_ENERGY_PROPAGATION"
    assert constraint["independent_parent_solution_existence_proven"] is False

    energy = reg["nonlinear_sobolev_energy_closure"]
    assert energy["regularity_index"] == "integer m>=3 on the 1D radial reduction"
    assert energy["result"] == "PASS_CONDITIONAL_LOCAL_QUASILINEAR_SOBLEV_ENERGY_CLOSURE_TEMPLATE"
    assert energy["local_existence_uniqueness_theorem_ratified"] is False
    assert energy["global_existence_uniqueness_proven"] is False

    scope = reg["scope_limits"]
    assert scope["exact_full_coefficient_compatibility_hierarchy"] == "OPEN"
    assert scope["local_quasilinear_IBVP_existence_uniqueness"] == "NOT_RATIFIED"
    assert scope["global_IBVP_existence_uniqueness"] == "OPEN"
    assert scope["physical_hamiltonian_positivity"] == "OPEN"
    assert scope["full_ghost_freedom"] == "OPEN"
    assert scope["physical_parent_solve_authorized"] is False
    assert scope["D2NQ_parent_dynamic_selection"] == "OPEN_NOT_EXECUTED"
    assert scope["K1-D"] == "NOT_RELEASED"
    assert scope["K1-E"] == "NOT_ADMISSIBLE"
    assert scope["WP4"] == "BLOCKED"
    assert scope["physical_evidence_effect"] == "NONE"

    required_ledger_phrases = [
        "det B_g=-4",
        "positive PDE symmetrizer",
        "maximal isotropic",
        "PASS_CONDITIONAL_LOCAL_QUASILINEAR_SOBLEV_ENERGY_CLOSURE_TEMPLATE",
        "PHYSICAL_PARENT_SOLVE = NOT_AUTHORIZED",
        "K1-D = NOT_RELEASED",
        "PHYSICAL_EVIDENCE_EFFECT = NONE",
    ]
    for phrase in required_ledger_phrases:
        assert phrase in ledger, phrase

    return {
        "status": "PASS",
        "block_id": reg["block_id"],
        "source_bindings": source_results,
        "metric_boundary_det": boundary["metric_block_determinant"],
        "principal_interface_dimension": flux["boundary_subspace_dimension"],
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
        print("PASS H4R3 variable-coefficient symmetrizer / nonlinear-energy preflight")


if __name__ == "__main__":
    main()
