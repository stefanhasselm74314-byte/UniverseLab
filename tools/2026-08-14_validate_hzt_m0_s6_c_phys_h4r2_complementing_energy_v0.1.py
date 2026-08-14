#!/usr/bin/env python3
"""Fail-closed validator for H4R2 frozen two-sided IBVP preflight."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REGISTRY = Path("registry/2026-08-14_HZT-M0_S6_C-PHYS_H4R2_BoundaryConstraintComplementingEnergyPreflight_v0.1.json")
LEDGER = Path("science/hzt-m0/md2s/2026-08-14_HZT-M0_S6_C-PHYS_H4R2_BoundaryConstraintComplementingEnergyPreflight_v0.1.md")


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


def interface_det(k_n: complex, k_s: complex, z_n: float, z_s: float) -> complex:
    return -4.0 * (k_n + k_s) ** 4 * (k_n * z_n + k_s * z_s)


def validate() -> dict:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    ledger = LEDGER.read_text(encoding="utf-8")

    assert reg["block_id"] == "C-PHYS-PARENT-H4R2-BOUNDARY-CONSTRAINT-COMPATIBILITY-TWO-SIDED-COMPLEMENTING-AND-ENERGY-ESTIMATE-PREFLIGHT"
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

    fw = reg["external_material_firewall"]
    assert fw["gemini_blocks"] == "EXTERNAL_UNVERIFIED_GEMINI_DRAFT"
    assert fw["gemini_equations_used_as_premises"] is False
    assert fw["gemini_code_used_as_validation"] is False
    assert fw["two_time_signature_imported"] is False

    interface = reg["two_sided_interface_symbol"]
    assert det3(interface["metric_block"]) == -4
    assert interface["metric_block_determinant"] == -4
    assert interface["result"] == "PASS_NO_NONTRIVIAL_DECAYING_HOMOGENEOUS_MODE_FOR_Re_zeta_GT_0"
    assert interface["classification"] == "FROZEN_TWO_SIDED_LOPATINSKII_COMPLEMENTING_PASS"

    # Representative normalized frequencies, including a complex Laplace frequency.
    for zeta in (1.0 + 0.0j, 1.0 + 0.7j, 0.25 + 1.0j):
        for c_n, c_s, z_n, z_s in (
            (1.0, 1.0, 1.0, 1.0),
            (0.4, 2.0, 0.2, 3.0),
            (1.3, 0.8, 2.1, 0.7),
        ):
            d = interface_det(c_n * zeta, c_s * zeta, z_n, z_s)
            assert abs(d) > 0.0

    uniform = reg["uniform_lopatinskii_preflight"]
    assert uniform["result"] == "PASS_UNIFORM_FROZEN_PRINCIPAL_COMPLEMENTING_BOUND"
    c_min = 0.25
    z_min = 0.125
    lower = 128.0 * c_min**5 * z_min
    exact_corner = abs(interface_det(c_min, c_min, z_min, z_min))
    assert abs(exact_corner - lower) < 1e-14

    constraints = reg["boundary_constraint_compatibility"]
    assert constraints["result"] == "PASS_CONDITIONAL_FORMAL_TWO_SIDED_CONSTRAINT_FLUX_COMPATIBILITY"
    assert "initial constraints vanish" in constraints["required_conditions"]

    energy = reg["linear_energy_resolvent_preflight"]
    assert energy["result"] == "PASS_FROZEN_LINEAR_PRINCIPAL_RESOLVENT_ESTIMATE_PREFLIGHT"
    assert energy["physical_hamiltonian_positivity_inferred"] is False
    assert energy["variable_coefficient_energy_estimate"] == "OPEN"
    assert energy["nonlinear_energy_estimate"] == "OPEN"

    gate = reg["gate_disposition"]
    assert gate["frozen_two_sided_complementing_condition"] == "PASS"
    assert gate["uniform_frozen_lopatinskii_bound"] == "PASS_ON_DECLARED_COMPACT_DOMAIN"
    assert gate["variable_coefficient_kreiss_estimate"] == "OPEN"
    assert gate["nonlinear_energy_estimate"] == "OPEN"
    assert gate["global_IBVP_existence_uniqueness"] == "OPEN"
    assert gate["full_ghost_freedom"] == "OPEN"
    assert gate["physical_parent_solve_authorized"] is False
    assert gate["D2NQ_parent_dynamic_selection"] == "OPEN_NOT_EXECUTED"
    assert gate["K1-D"] == "NOT_RELEASED"
    assert gate["K1-E"] == "NOT_ADMISSIBLE"
    assert gate["WP4"] == "BLOCKED"
    assert gate["physical_evidence_effect"] == "NONE"

    for phrase in [
        "det B_g=-4",
        "|\\det M|\\ge128",
        "PASS, conditional/formal",
        "physical evidence}=\\mathrm{NONE}",
        "H4R3 must not start a physical parent solve",
    ]:
        assert phrase in ledger, phrase

    return {
        "status": "PASS",
        "block_id": reg["block_id"],
        "source_bindings": source_results,
        "metric_boundary_det": -4,
        "uniform_corner_lower_bound": lower,
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
        print("PASS H4R2 frozen complementing / constraint-energy preflight")


if __name__ == "__main__":
    main()
