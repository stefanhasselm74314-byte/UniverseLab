#!/usr/bin/env python3
"""Synchronize canonical governance pointers with merged Operator-2B artifacts.

The migration is intentionally narrow and idempotent. It updates only:
- project-manifest.json
- registry/session-checkpoint-latest.json
- registry/decision-log.jsonl

It does not alter scientific equations, claims, status artifacts or release gates.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-manifest.json"
CHECKPOINT_ALIAS = ROOT / "registry/session-checkpoint-latest.json"
CHECKPOINT_V114 = ROOT / "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.14.json"
DECISION_LOG = ROOT / "registry/decision-log.jsonl"

REQUIRED = [
    ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceContract_v0.1.json",
    ROOT / "registry/2026-08-04_UniverseLab_C_PHYS_M1_Operator2B_Status_v0.1.json",
    ROOT / "registry/2026-08-04_UniverseLab_ClaimRegister_C_PHYS_M1_Operator2B_v0.1.json",
    ROOT / "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceLedger_v0.1.md",
    ROOT / "tools/2026-08-04_validate_g0_three_track_sync_v1.6.py",
    ROOT / "tests/2026-08-04_test_g0_three_track_sync_v1.6.py",
]

DECISION_0022 = {
    "decision_id": "UL-DEC-0022",
    "date": "2026-08-04",
    "topic": "md2s_c_phys_m1_operator_2b",
    "decision": (
        "For the active HZT-M0-S6-C-PHYS-M1 candidate family, the fixed "
        "tau=y^2 pole chart, little-Holder profile and target spaces, positive "
        "admissible set, regularized smooth nonlinear operator, continuous cap "
        "traces, 8 by 22 parameter-augmented linearized boundary-trace template, "
        "dense smooth core and future kernel/cokernel protocol are accepted as "
        "formal functional-analytic structure. No candidate background, numerical "
        "trace matrix, rank, kernel, cokernel, Fredholm property, continuum "
        "Jacobian, stability or release gate is established."
    ),
    "status": "ACTIVE",
    "reason": (
        "Exact symbolic verification confirms the fixed-chart derivative identities, "
        "removal of negative tau powers from the regularized residuals, endpoint "
        "trace formulas and cap principal determinant. Little-Holder spaces provide "
        "a dense smooth core and the fixed-background derivative is bounded between "
        "the declared Banach spaces. These are necessary operator-domain and trace "
        "definitions, not existence or invertibility results."
    ),
    "sources": [
        "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceContract_v0.1.json",
        "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceLedger_v0.1.md",
        "registry/2026-08-04_UniverseLab_C_PHYS_M1_Operator2B_Status_v0.1.json",
        "registry/2026-08-04_UniverseLab_ClaimRegister_C_PHYS_M1_Operator2B_v0.1.json",
        "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.14.json",
        "project-manifest.json",
    ],
    "evidence_effect": "FORMAL_FUNCTIONAL_ANALYTIC_STRUCTURE_ONLY",
    "supersedes": None,
}


class SyncError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SyncError(message)


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SyncError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root must be object: {path.relative_to(ROOT)}")
    return value


def update_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    require(manifest.get("schema") == "universelab.project-manifest.v1", "manifest schema drift")

    manifest["release"] = "2.7-c-phys-m1-operator-2b-v0.1"
    manifest["release_date"] = "2026-08-04"

    tracks = manifest["architecture"]["research_tracks"]
    require([item["id"] for item in tracks] == [
        "MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"
    ], "three-track ordering drift")
    physical_track = tracks[1]
    physical_track["status"] = "ACTIVE_BACKGROUND_PREREQUISITE_AND_FREDHOLM_ANALYSIS_REMAINING"
    physical_track["active_model"] = "HZT-M0-S6-C-PHYS-M1"

    gates = manifest["gates"]
    gates.update({
        "OPERATOR_2A": "PASS_FORMAL_OPERATOR_STRUCTURE",
        "OPERATOR_2B": "PASS_FORMAL_FUNCTION_SPACE_AND_TRACE_TEMPLATE",
        "R1.0": "ACTIVE_BACKGROUND_PREREQUISITE_AND_FREDHOLM_ANALYSIS_REMAINING",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "CONTINUUM_BVP_OPERATOR": "FUNCTION_SPACE_AND_TRACE_TEMPLATE_DEFINED",
        "WEIGHTED_FUNCTION_SPACES": "FROZEN",
        "FULL_LINEARIZED_BOUNDARY_TRACE_TEMPLATE": "DEFINED_NOT_EVALUATED",
        "FULL_LINEARIZED_BOUNDARY_TRACE_RANK": "NOT_PROVEN",
        "FREDHOLM_PROPERTY": "NOT_PROVEN",
        "CONTINUUM_BVP_JACOBIAN": "NOT_PROVEN",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    })

    rules = manifest.setdefault("governance_rules", [])
    for rule in [
        "formal_function_space_definition_is_not_solution_existence",
        "symbolic_trace_template_is_not_numeric_trace_rank",
        "bounded_map_closed_graph_is_not_fredholmness",
    ]:
        if rule not in rules:
            rules.append(rule)

    parent = manifest["parent_action_v0_1"]
    parent["status"] = "M1_FUNCTION_SPACE_AND_TRACE_TEMPLATE_DEFINED_BACKGROUND_OPEN"
    parent["active_model"] = "HZT-M0-S6-C-PHYS-M1"
    parent["next_block"] = "C-PHYS-R1.0-BACKGROUND-3A"

    entry = manifest["c_phys_operator_entry"]
    entry.update({
        "model_id": "HZT-M0-S6-C-PHYS-M1",
        "status": "PASS_FORMAL_FUNCTION_SPACE_AND_TRACE_TEMPLATE_BACKGROUND_OPEN",
        "continuum_operator": "FUNCTION_SPACE_AND_TRACE_TEMPLATE_DEFINED",
        "weighted_function_spaces": "FROZEN",
        "full_linearized_boundary_trace_template": "DEFINED_NOT_EVALUATED",
        "full_linearized_boundary_trace_rank": "NOT_PROVEN",
        "Fredholm_property": "NOT_PROVEN",
        "continuum_BVP_Jacobian": "NOT_PROVEN",
        "physical_background": "NOT_ESTABLISHED",
        "solver_authorized": False,
        "operator_2b_contract": "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceContract_v0.1.json",
        "operator_2b_ledger": "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceLedger_v0.1.md",
        "operator_2b_status": "registry/2026-08-04_UniverseLab_C_PHYS_M1_Operator2B_Status_v0.1.json",
        "operator_2b_claim_register": "registry/2026-08-04_UniverseLab_ClaimRegister_C_PHYS_M1_Operator2B_v0.1.json",
        "function_space_chart": "tau=y^2 on two fixed unit intervals",
        "regional_profile_space": "h^{2,alpha_H}^3 x h^{1,alpha_H}",
        "regional_bulk_target": "h^{0,alpha_H}^4",
        "augmented_boundary_template_shape": "8 x 22",
        "remaining_operator_items": [
            "candidate M1 background protocol and construction",
            "numeric evaluation of the full parameter-augmented endpoint trace",
            "trace rank convergence",
            "kernel and cokernel",
            "Fredholm property",
            "continuum Jacobian",
            "physical background existence and uniqueness",
            "conditioning and robustness",
        ],
        "physical_evidence_effect": "NONE",
        "next_block": "C-PHYS-R1.0-BACKGROUND-3A",
    })

    fixed = entry.setdefault("fixed_minimal_structure", [])
    for item in [
        "fixed tau pole-regular affine chart",
        "little-Holder profile target and ambient spaces",
        "regularized smooth nonlinear bulk-boundary operator template",
        "continuous 14-component profile cap trace",
        "8 by 22 parameter-augmented boundary derivative template",
        "dense smooth core and bounded-map closed-graph statement",
        "future kernel and cokernel protocol",
    ]:
        if item not in fixed:
            fixed.append(item)

    cphys = manifest["c_phys_m1"]
    cphys["background_existence"] = "NOT_ESTABLISHED"
    cphys["physical_evidence_effect"] = "NONE"
    cphys["next_block"] = "C-PHYS-R1.0-BACKGROUND-3A"

    registries = manifest["central_registries"]
    registries.update({
        "c_phys_m1_operator_2b_contract": "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceContract_v0.1.json",
        "c_phys_m1_operator_2b_ledger": "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceLedger_v0.1.md",
        "c_phys_m1_operator_2b_status": "registry/2026-08-04_UniverseLab_C_PHYS_M1_Operator2B_Status_v0.1.json",
        "claim_register_c_phys_m1_operator_2b": "registry/2026-08-04_UniverseLab_ClaimRegister_C_PHYS_M1_Operator2B_v0.1.json",
        "session_checkpoint_snapshot": "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.14.json",
    })

    manifest["workstream_priority"] = [
        "MD2S-R1-C-PHYS:C-PHYS-R1.0-BACKGROUND-3A",
        "HZT-M0-S6-C1-V:G1.2_PARALLEL_DIAGNOSTIC_ONLY",
    ]
    manifest["next_release_blockers"] = [
        "legacy_primary_source_recovery",
        "c_phys_candidate_background_protocol_and_construction",
        "c_phys_numeric_parameter_augmented_trace_matrix",
        "c_phys_trace_rank_kernel_and_cokernel",
        "continuum_Fredholm_and_jacobian_analysis",
        "continuum_discrete_convergence",
        "c_phys_parameter_identifiability_and_6d_to_4d_normalization",
        "scalar_vector_tensor_perturbations",
        "ghost_gradient_and_mass_stability",
        "fundamental_to_observable_forward_map",
        "data_likelihood_provenance",
        "runtime_manifest_consumption",
        "central_status_renderer",
        "single_cache_release_version",
        "byte_reproducible_release_lock",
    ]
    return manifest


def update_decision_log() -> str:
    require(DECISION_LOG.is_file(), "missing decision log")
    raw_lines = [line for line in DECISION_LOG.read_text(encoding="utf-8").splitlines() if line.strip()]
    decisions = [json.loads(line) for line in raw_lines]
    ids = [item.get("decision_id") for item in decisions]
    require(len(ids) == len(set(ids)), "duplicate decision ids")
    if "UL-DEC-0022" in ids:
        existing = decisions[ids.index("UL-DEC-0022")]
        require(existing == DECISION_0022, "existing UL-DEC-0022 differs from canonical entry")
    else:
        require(ids and ids[-1] == "UL-DEC-0021", "decision log must end at UL-DEC-0021 before append")
        decisions.append(DECISION_0022)
    return "\n".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in decisions) + "\n"


def expected_outputs() -> dict[Path, str]:
    for path in REQUIRED:
        require(path.is_file(), f"missing merged Operator-2B artifact: {path.relative_to(ROOT)}")
    checkpoint = read_json(CHECKPOINT_V114)
    require(checkpoint.get("checkpoint_id") == "UL-CHK-20260804-014", "checkpoint v1.14 id drift")
    require(
        checkpoint.get("canonical_snapshot")
        == "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.14.json",
        "checkpoint v1.14 canonical path drift",
    )
    manifest = update_manifest(read_json(MANIFEST))
    return {
        MANIFEST: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        CHECKPOINT_ALIAS: CHECKPOINT_V114.read_text(encoding="utf-8"),
        DECISION_LOG: update_decision_log(),
    }


def apply(check_only: bool) -> list[str]:
    changed: list[str] = []
    for path, expected in expected_outputs().items():
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current != expected:
            changed.append(str(path.relative_to(ROOT)))
            if not check_only:
                path.write_text(expected, encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        changed = apply(check_only=args.check)
    except (SyncError, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1
    if args.check and changed:
        print("FAIL: governance drift remains:")
        for path in changed:
            print(f"- {path}")
        return 1
    if args.apply:
        print("Updated:" if changed else "No changes required.")
        for path in changed:
            print(f"- {path}")
    else:
        print("PASS: Operator-2B governance pointers are synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
