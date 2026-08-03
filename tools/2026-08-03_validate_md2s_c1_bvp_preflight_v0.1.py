#!/usr/bin/env python3
"""Validate the HZT-M0-S6-C1 model and structural BVP preflight.

This tool checks model definitions, dimensions, governance invariants, the
8-by-8 boundary-value count and the maximum bipartite matching of the declared
residual-to-unknown dependency graph. It does not integrate the radial field
equations and has no evidence effect.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable


MODEL_PATH = Path("registry/2026-08-03_MD2S_C1_ModelContract_v0.1.json")
PREFLIGHT_PATH = Path("registry/2026-08-03_MD2S_C1_BVPPreflightContract_v0.1.json")


class ContractError(ValueError):
    """Raised when the C1 model or preflight contract is inconsistent."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"missing contract: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ContractError(f"top-level JSON object required: {path}")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def unique_strings(values: Iterable[Any], label: str) -> list[str]:
    items = list(values)
    require(all(isinstance(item, str) and item for item in items),
            f"{label} must contain non-empty strings")
    require(len(items) == len(set(items)), f"{label} contains duplicates")
    return items


def maximum_matching(edges: dict[str, list[str]]) -> tuple[int, dict[str, str]]:
    """Return maximum row-to-column matching size using the Kuhn algorithm."""
    matched_column: dict[str, str] = {}

    def augment(row: str, seen: set[str]) -> bool:
        for column in edges[row]:
            if column in seen:
                continue
            seen.add(column)
            if column not in matched_column or augment(matched_column[column], seen):
                matched_column[column] = row
                return True
        return False

    size = 0
    for row in edges:
        if augment(row, set()):
            size += 1
    return size, matched_column


def validate_model(model: dict[str, Any]) -> None:
    require(model.get("schema") == "universelab.md2s-c1-model-contract.v0.1",
            "unexpected model schema")
    require(model.get("model_id") == "HZT-M0-S6-C1", "unexpected model_id")
    require(model.get("status") == "CANDIDATE_MODEL_DEFINED_NOT_RELEASED",
            "candidate status must remain not released")
    require(model.get("evidence_effect") == "NONE", "evidence_effect must be NONE")
    require(model.get("historical_A0_identity") == "NOT_CLAIMED",
            "historical A0 identity must not be claimed")
    require(model.get("solver_authorized") is False, "solver must remain unauthorized")

    bulk = model.get("bulk_functions", {})
    require(bulk.get("U") == "U0+0.5*m_phi_sq*(phi-phi_star)^2",
            "unexpected C1 scalar potential")
    require(bulk.get("Z_phi") == "1", "C1 requires Z_phi=1")
    require(bulk.get("Z_F") == "1", "C1 requires Z_F=1")

    localized = model.get("localized_functions", {})
    require(localized.get("lambda") == "lambda0+lambda1*(phi-phi_star)",
            "unexpected C1 cap tension function")
    require(localized.get("Z_sigma") == "z_sigma0", "C1 requires constant Z_sigma")

    dimensions = model.get("parameter_dimensions", {})
    expected_dimensions = {
        "kappa6_sq": "M^-4",
        "Lambda_geom": "M^2",
        "U0": "M^6",
        "m_phi_sq": "M^2",
        "phi_star": "M^2",
        "lambda0": "M^5",
        "lambda1": "M^3",
        "z_sigma0": "M^3",
        "q0": "M^-1",
        "K4": "M^2",
    }
    require(dimensions == expected_dimensions, "parameter dimension table drift")

    domains = model.get("parameter_domains", {})
    require(domains.get("kappa6_sq") == "strictly_positive", "kappa6_sq domain drift")
    require(domains.get("m_phi_sq") == "nonnegative", "m_phi_sq domain drift")
    require(domains.get("z_sigma0") == "strictly_positive", "z_sigma0 domain drift")
    require(domains.get("q0") == "strictly_positive", "q0 domain drift")

    conventions = model.get("coordinate_and_charge_conventions", {})
    require(conventions.get("Delta_chi") == "2*pi", "C1 requires Delta_chi=2*pi")
    require(conventions.get("q_sigma") == "q0", "C1 q_sigma definition drift")
    require(conventions.get("q_ref") == "q0", "C1 q_ref definition drift")
    require(conventions.get("charge_identity_status") == "C1_MODEL_POSTULATE_NOT_DERIVED",
            "charge identity must remain an explicit C1 postulate")

    topology = model.get("topology_and_regions", {})
    require(topology.get("regions") == ["N", "S"], "C1 requires N and S regions")
    require(topology.get("shared_bulk_functions") is True, "bulk functions must be shared")
    require(topology.get("shared_bulk_parameters") is True, "bulk parameters must be shared")
    require(topology.get("outward_normal_at_cap") == "n_s^r=+1 in each local coordinate",
            "outward-normal convention drift")

    pole = model.get("pole_conditions", {})
    require(pole.get("L_s_0") == 0, "smooth pole requires L(0)=0")
    require(pole.get("L_prime_s_0") == 1, "Delta_chi=2*pi requires L'(0)=1")
    require(pole.get("A_prime_s_0") == 0, "smooth pole requires A'(0)=0")
    require(pole.get("phi_prime_s_0") == 0, "smooth pole requires phi'(0)=0")
    require(pole.get("A_chi_s_0") == 0, "regular pole gauge requires A_chi(0)=0")

    frame = model.get("frame_and_patch", {})
    require(frame.get("frame_condition") == "A_N(0)=0", "frame condition drift")
    require(frame.get("patch_relation") ==
            "A_chi_N(rho_N)-A_chi_S(rho_S)=N_F/q0",
            "gauge-patch relation drift")

    governance = model.get("governance", {})
    require(governance.get("R1.1") == "BLOCKED", "R1.1 must remain blocked")
    require(governance.get("MD2S_SOLVER") == "NOT_AUTHORIZED",
            "solver gate must remain closed")
    require(governance.get("K1-D") == "NOT_RELEASED", "K1-D gate drift")
    require(governance.get("K1-E") == "NOT_ADMISSIBLE", "K1-E gate drift")


def validate_preflight(preflight: dict[str, Any]) -> dict[str, Any]:
    require(preflight.get("schema") == "universelab.md2s-c1-bvp-preflight.v0.1",
            "unexpected preflight schema")
    require(preflight.get("model_id") == "HZT-M0-S6-C1", "preflight model mismatch")
    require(preflight.get("status") == "STRUCTURAL_PREFLIGHT_PASS_EXECUTION_BLOCKED",
            "preflight status drift")
    require(preflight.get("evidence_effect") == "NONE", "preflight evidence drift")
    require(preflight.get("solver_authorized") is False, "solver must remain unauthorized")

    unknowns = unique_strings(preflight.get("continuous_unknowns_square_bvp", []),
                              "continuous_unknowns_square_bvp")
    expected_unknowns = [
        "phi_N_0", "Q_N", "A_S_0", "phi_S_0",
        "Q_S", "rho_N", "rho_S", "K4",
    ]
    require(unknowns == expected_unknowns, "C1 shooting vector drift")

    residual_entries = preflight.get("independent_residuals", [])
    require(isinstance(residual_entries, list), "independent_residuals must be a list")
    residual_ids = unique_strings((item.get("id") for item in residual_entries),
                                  "independent residual IDs")
    expected_residuals = [
        "R_A", "R_L", "R_phi", "R_patch",
        "R_4d", "R_chi", "R_scalar", "R_gauge",
    ]
    require(residual_ids == expected_residuals, "C1 residual vector drift")
    require(len(unknowns) == len(residual_ids) == 8, "C1 square count must be 8 by 8")

    count = preflight.get("count_derivation", {})
    require(count.get("two_region_regular_data_count") == 6, "regular data count drift")
    require(count.get("cap_location_count") == 2, "cap location count drift")
    require(count.get("global_frame_redundancy_removed") == 1,
            "frame redundancy count drift")
    require(count.get("K4_eigenvalue_added") == 1, "K4 eigenvalue count drift")
    require(count.get("continuous_unknown_count") == 8, "unknown count drift")

    not_counted = preflight.get("not_counted_as_independent_boundary_residuals", {})
    require("encoded once" in not_counted.get("global_flux", ""),
            "global flux must not be double counted")
    require("propagated QA" in not_counted.get("rr_constraints", ""),
            "rr constraints must remain QA channels")

    raw_edges = preflight.get("structural_dependency_edges", {})
    require(isinstance(raw_edges, dict), "structural_dependency_edges must be an object")
    require(list(raw_edges) == residual_ids, "dependency rows must match residual order")
    edges: dict[str, list[str]] = {}
    for row, columns in raw_edges.items():
        columns = unique_strings(columns, f"dependency columns for {row}")
        require(set(columns).issubset(set(unknowns)), f"unknown dependency column in {row}")
        require(columns, f"empty dependency row: {row}")
        edges[row] = columns

    matching_size, matched_columns = maximum_matching(edges)
    declared_rank = preflight.get("structural_rank", {})
    require(matching_size == 8, f"maximum structural matching is {matching_size}, expected 8")
    require(declared_rank.get("maximum_bipartite_matching") == matching_size,
            "declared structural rank does not match computed matching")
    require(declared_rank.get("row_count") == 8, "row count drift")
    require(declared_rank.get("column_count") == 8, "column count drift")

    declared_matching = preflight.get("declared_perfect_matching", {})
    require(set(declared_matching) == set(residual_ids), "declared matching rows incomplete")
    require(len(set(declared_matching.values())) == 8, "declared matching columns not unique")
    for row, column in declared_matching.items():
        require(column in edges[row], f"declared matching edge missing: {row}->{column}")

    fixed_k4 = preflight.get("fixed_K4_variant", {})
    require(fixed_k4.get("continuous_unknown_count") == 7, "fixed-K4 count drift")
    require(fixed_k4.get("residual_count") == 8, "fixed-K4 residual count drift")
    require(fixed_k4.get("generic_codimension") == 1, "fixed-K4 codimension drift")

    risks = {item.get("id"): item for item in preflight.get("rank_risk_surfaces", [])}
    require("C1-RISK-SCALAR-SHIFT" in risks, "scalar-shift risk missing")
    require("m_phi_sq=0 and lambda1=0" == risks["C1-RISK-SCALAR-SHIFT"].get("condition"),
            "scalar-shift condition drift")

    gate = preflight.get("next_execution_gate", {})
    require(gate.get("R1.1") == "BLOCKED", "R1.1 preflight gate drift")
    require(gate.get("MD2S_SOLVER") == "NOT_AUTHORIZED", "solver gate drift")

    governance = preflight.get("governance", {})
    require(governance.get("K1-D") == "NOT_RELEASED", "K1-D gate drift")
    require(governance.get("K1-E") == "NOT_ADMISSIBLE", "K1-E gate drift")
    require(governance.get("evidence_effect") == "NONE", "governance evidence drift")

    return {
        "unknown_count": len(unknowns),
        "residual_count": len(residual_ids),
        "maximum_structural_matching": matching_size,
        "matched_columns": sorted(matched_columns),
        "fixed_K4_unknown_count": fixed_k4["continuous_unknown_count"],
        "fixed_K4_codimension": fixed_k4["generic_codimension"],
    }


def scalar_shift_risk(*, m_phi_sq: float, lambda1: float, atol: float = 0.0) -> bool:
    values = (float(m_phi_sq), float(lambda1), float(atol))
    if not all(math.isfinite(value) for value in values):
        raise ContractError("scalar-shift inputs must be finite")
    if atol < 0.0:
        raise ContractError("atol must be nonnegative")
    if m_phi_sq < 0.0:
        raise ContractError("m_phi_sq must be nonnegative")
    return abs(m_phi_sq) <= atol and abs(lambda1) <= atol


def validate_repository(root: Path) -> dict[str, Any]:
    model = load_json(root / MODEL_PATH)
    preflight = load_json(root / PREFLIGHT_PATH)
    validate_model(model)
    summary = validate_preflight(preflight)
    return {
        "status": "PASS",
        "model_id": "HZT-M0-S6-C1",
        "candidate_status": model["status"],
        "preflight_status": preflight["status"],
        "evidence_effect": "NONE",
        "solver_authorized": False,
        **summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."),
                        help="repository root (default: current directory)")
    parser.add_argument("--pretty", action="store_true", help="pretty-print JSON")
    args = parser.parse_args()
    try:
        result = validate_repository(args.root)
    except ContractError as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
