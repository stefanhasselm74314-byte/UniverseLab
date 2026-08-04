#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-manifest.json"
DECISIONS = ROOT / "registry/decision-log.jsonl"
V14 = ROOT / "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.14.json"
V15 = ROOT / "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.15.json"
LATEST = ROOT / "registry/session-checkpoint-latest.json"
OLD_WORKFLOW = ROOT / ".github/workflows/2026-08-04_UniverseLab_G0_ThreeTrackContract_v1.6.yml"


def dump(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sync_manifest() -> None:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    m["release"] = "2.7-c-phys-m1-operator-2b-v0.1"
    m["release_date"] = "2026-08-04"

    physical = m["architecture"]["research_tracks"][1]
    physical["status"] = "ACTIVE_BACKGROUND_PREREQUISITE_AND_FREDHOLM_ANALYSIS_REMAINING"
    physical["active_model"] = "HZT-M0-S6-C-PHYS-M1"

    g = m["gates"]
    g.update({
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

    parent = m.setdefault("parent_action_v0_1", {})
    parent["status"] = "M1_OPERATOR_2B_FUNCTION_SPACES_AND_TRACE_TEMPLATE_DEFINED_BACKGROUND_OPEN"
    parent["active_model"] = "HZT-M0-S6-C-PHYS-M1"
    parent["next_block"] = "C-PHYS-R1.0-BACKGROUND-3A"

    entry = m.setdefault("c_phys_operator_entry", {})
    entry.update({
        "track_id": "MD2S-R1-C-PHYS",
        "model_id": "HZT-M0-S6-C-PHYS-M1",
        "phase": "R1.0",
        "status": "OPERATOR_2B_FUNCTION_SPACES_AND_TRACE_TEMPLATE_DEFINED_BACKGROUND_OPEN",
        "continuum_operator": "FUNCTION_SPACE_AND_TRACE_TEMPLATE_DEFINED",
        "weighted_function_spaces": "FROZEN",
        "full_linearized_boundary_trace_template": "DEFINED_NOT_EVALUATED",
        "full_linearized_boundary_trace_rank": "NOT_PROVEN",
        "Fredholm_property": "NOT_PROVEN",
        "continuum_BVP_Jacobian": "NOT_PROVEN",
        "physical_background": "NOT_ESTABLISHED",
        "solver_authorized": False,
        "augmented_boundary_template_shape": "8 x 22",
        "operator_2b_contract": "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceContract_v0.1.json",
        "operator_2b_status": "registry/2026-08-04_UniverseLab_C_PHYS_M1_Operator2B_Status_v0.1.json",
        "operator_2b_claims": "registry/2026-08-04_UniverseLab_ClaimRegister_C_PHYS_M1_Operator2B_v0.1.json",
        "next_block": "C-PHYS-R1.0-BACKGROUND-3A",
        "remaining_operator_items": [
            "governed candidate-background construction protocol",
            "background-evaluated linearized trace matrix",
            "kernel and cokernel analysis",
            "Fredholm property",
            "continuum Jacobian",
            "existence and uniqueness",
            "conditioning and discretization-to-continuum convergence",
        ],
    })

    if "c_phys_m1" in m:
        m["c_phys_m1"]["next_block"] = "C-PHYS-R1.0-BACKGROUND-3A"

    regs = m.setdefault("central_registries", {})
    regs.update({
        "c_phys_m1_operator_2b_contract": "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceContract_v0.1.json",
        "c_phys_m1_operator_2b_status": "registry/2026-08-04_UniverseLab_C_PHYS_M1_Operator2B_Status_v0.1.json",
        "c_phys_m1_operator_2b_claims": "registry/2026-08-04_UniverseLab_ClaimRegister_C_PHYS_M1_Operator2B_v0.1.json",
        "session_checkpoint": "registry/session-checkpoint-latest.json",
        "session_checkpoint_snapshot": "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.15.json",
    })

    m["workstream_priority"] = [
        "MD2S-R1-C-PHYS:C-PHYS-R1.0-BACKGROUND-3A",
        "HZT-M0-S6-C1-V:G1.2_PARALLEL_DIAGNOSTIC_ONLY",
    ]

    blockers = [x for x in m.get("next_release_blockers", []) if x not in {
        "c_phys_independent_specialized_ode_system",
        "c_phys_rr_constraint_propagation_identity",
        "c_phys_higher_order_pole_series",
        "c_phys_principal_and_complementing_boundary_audit",
    }]
    for item in [
        "c_phys_candidate_background_protocol",
        "c_phys_background_evaluated_trace_matrix",
        "continuum_Fredholm_and_jacobian_analysis",
    ]:
        if item not in blockers:
            blockers.insert(0, item)
    m["next_release_blockers"] = blockers
    dump(MANIFEST, m)


def sync_checkpoint() -> None:
    cp = json.loads(V14.read_text(encoding="utf-8"))
    cp["checkpoint_id"] = "UL-CHK-20260804-015"
    cp["timestamp"] = "2026-08-04T04:55:00+02:00"
    cp["basis_commit"] = os.environ.get("GITHUB_SHA", cp.get("basis_commit"))
    cp["canonical_snapshot"] = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.15.json"
    cp["supersedes"] = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.14.json"
    cp["correction_note"] = (
        "v1.14 contained the Operator-2B scientific state but was not installed as the stable alias and referenced a nonexistent v1.13. "
        "v1.15 is the first canonical alias-backed Operator-2B checkpoint and supersedes v1.14 append-only."
    )
    dump(V15, cp)
    dump(LATEST, cp)


def sync_decision() -> None:
    lines = [line for line in DECISIONS.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [json.loads(line)["decision_id"] for line in lines]
    if "UL-DEC-0022" not in ids:
        entry = {
            "decision_id": "UL-DEC-0022",
            "date": "2026-08-04",
            "topic": "c_phys_m1_operator_2b_function_spaces_and_trace_template",
            "decision": "The fixed tau pole chart, little-Holder domain/target spaces, admissible positive cone, regularized nonlinear bulk map and parameter-augmented 8 by 22 boundary-trace template are accepted for HZT-M0-S6-C-PHYS-M1 as formal functional-analytic structure. No candidate background, evaluated trace matrix, rank, Fredholm property, continuum Jacobian, solver authorization or physical evidence follows.",
            "status": "ACTIVE",
            "reason": "Operator-2B fixes the Banach-space setting required for later background and linearization work while preserving the distinction between a symbolic trace template and a background-evaluated continuum operator.",
            "sources": [
                "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceContract_v0.1.json",
                "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceLedger_v0.1.md",
                "registry/2026-08-04_UniverseLab_C_PHYS_M1_Operator2B_Status_v0.1.json",
                "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.15.json",
                "project-manifest.json",
            ],
            "evidence_effect": "FORMAL_FUNCTIONAL_ANALYTIC_STRUCTURE_ONLY",
            "supersedes": None,
        }
        lines.append(json.dumps(entry, separators=(",", ":"), ensure_ascii=False))
    DECISIONS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def retire_old_workflow() -> None:
    OLD_WORKFLOW.write_text(
        "name: UniverseLab G0 three-track governance v1.6 (historical)\n\n"
        "on:\n  workflow_dispatch:\n\n"
        "permissions:\n  contents: read\n\n"
        "jobs:\n  historical-contract:\n    runs-on: ubuntu-latest\n    steps:\n"
        "      - run: echo 'Superseded by the v1.7 canonical synchronization workflow.'\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    sync_manifest()
    sync_checkpoint()
    sync_decision()
    retire_old_workflow()
