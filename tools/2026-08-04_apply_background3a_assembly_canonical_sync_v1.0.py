#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-manifest.json"
DECISIONS = ROOT / "registry/decision-log.jsonl"
LATEST = ROOT / "registry/session-checkpoint-latest.json"
SNAPSHOT = ROOT / "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.19.json"
MERGE_COMMIT = "2ad24fe90a76cb41f22f4395271d93660abc9b59"
ASSEMBLY = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3AAssemblyCorrectionContract_v0.3.json"
RUN = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"
LEDGER = "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3AAssemblyCorrectionLedger_v0.3.md"
VALIDATOR = "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3a_assembly_v0.3.py"
TESTS = "tests/2026-08-04_test_hzt_m0_s6_c_phys_m1_background_3a_assembly_v0.3.py"
SEEDS = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BSeedSpecification_v0.1.json"
LOCK = "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3B_v0.1.txt"
NEXT = "C-PHYS-R1.0-BACKGROUND-3C_EXECUTION_IMPLEMENTATION_AND_AUTHORIZATION_GATE"


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sync_manifest() -> None:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if m.get("release") != "2.10-c-phys-m1-background-3b-run-input-frozen-v0.1":
        raise RuntimeError(f"unexpected manifest basis release: {m.get('release')}")
    m["release"] = "2.11-c-phys-m1-background-3a-assembly-corrected-v0.3"
    m["release_date"] = "2026-08-04"
    physical = m["architecture"]["research_tracks"][1]
    physical["status"] = "ACTIVE_EXECUTION_IMPLEMENTATION_AND_AUTHORIZATION_GATE_REMAINING"
    physical["active_model"] = "HZT-M0-S6-C-PHYS-M1"

    g = m["gates"]
    g.update({
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED_SQUARE_ASSEMBLY_CORRECTED",
        "BACKGROUND_3B": "RUN_INPUT_FROZEN_CP01R1_EXECUTION_NOT_AUTHORIZED",
        "BACKGROUND_METHOD": "FROZEN_PREREGISTERED_WITH_ASSEMBLY_CORRECTION",
        "BACKGROUND_TOPOLOGY_SCHEMA": "FROZEN_SINGLE_CAP_PHASE",
        "BACKGROUND_RUN_INPUT": "FROZEN_CP01R1",
        "BACKGROUND_SOLVER_IMPLEMENTATION": "NOT_PRESENT",
        "BACKGROUND_SOLVER_EXECUTION": "NOT_AUTHORIZED",
        "R1.0": "ACTIVE_EXECUTION_IMPLEMENTATION_AND_AUTHORIZATION_GATE_REMAINING",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "FULL_LINEARIZED_BOUNDARY_TRACE_RANK": "NOT_PROVEN",
        "FREDHOLM_PROPERTY": "NOT_PROVEN",
        "CONTINUUM_BVP_JACOBIAN": "NOT_PROVEN",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE"
    })

    entry = m["c_phys_operator_entry"]
    entry.update({
        "status": "BACKGROUND_3B_CP01R1_RUN_INPUT_FROZEN_EXECUTION_NOT_AUTHORIZED",
        "physical_background": "NOT_ESTABLISHED",
        "solver_authorized": False,
        "next_block": NEXT
    })
    for key in ("parent_action_v0_1", "c_phys_m1", "c_phys_background_3a"):
        if key in m:
            m[key]["next_block"] = NEXT

    old = m.get("c_phys_background_3b", {})
    m["c_phys_background_3b"] = {
        "track_id": "MD2S-R1-C-PHYS",
        "model_id": "HZT-M0-S6-C-PHYS-M1",
        "block": "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_REBIND_AFTER_ASSEMBLY_CORRECTION",
        "classification": "EXACT_RUN_INPUT_REBIND_NO_SOLVER_EXECUTION",
        "status": "RUN_INPUT_FROZEN_CP01R1_EXECUTION_NOT_AUTHORIZED",
        "previous_run_id": old.get("run_id", "HZT-M0-S6-C-PHYS-M1-BG3B-CP01"),
        "previous_run_status": "SUPERSEDED_BEFORE_EXECUTION",
        "run_id": "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1",
        "model_parameters_ordered": {
            "Lambda_hat": "1", "mhat_phi_sq": "1", "a_F": "1/4",
            "lambda_hat": "1", "z_sigma_hat": "1", "q_hat": "1"
        },
        "topological_sector_ordered": {"N_F": 1, "N_sigma": 1, "m_sigma": 1},
        "alpha_H": "1/2",
        "seed_set_id": "M1-BG3B-CP01-SEEDS-01",
        "dependency_lock_sha256": "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f",
        "seed_payload_sha256": "b6e4319cc29736799a0b46320002e51cd17b70b724a6b4c6e86567a316996161",
        "run_payload_sha256": "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302",
        "assembly": "8N_regularized_bulk_rows_plus_8_boundary_rows_for_8N_plus_8_unknowns",
        "node_count_to_degree": "degree=node_count-1",
        "base_seed_classification": "EXACT_BULK_AND_PATCH_SEED_BOUNDARY_INEXACT",
        "base_seed_is_solution": False,
        "solver_implementation": "NOT_PRESENT",
        "current_execution": "NOT_EXECUTED",
        "physical_background": "NOT_ESTABLISHED",
        "physical_evidence_effect": "NONE",
        "assembly_correction": ASSEMBLY,
        "contract": RUN,
        "seed_specification": SEEDS,
        "ledger": LEDGER,
        "dependency_lock": LOCK,
        "validator": VALIDATOR,
        "tests": TESTS,
        "next_block": NEXT
    }

    regs = m["central_registries"]
    regs.update({
        "c_phys_m1_background_3a_assembly_correction": ASSEMBLY,
        "c_phys_m1_background_3b_contract": RUN,
        "c_phys_m1_background_3a_assembly_ledger": LEDGER,
        "session_checkpoint_snapshot": "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.19.json"
    })
    m["workstream_priority"] = [
        f"MD2S-R1-C-PHYS:{NEXT}",
        "HZT-M0-S6-C1-V:G1.2_PARALLEL_DIAGNOSTIC_ONLY"
    ]
    blockers = [x for x in m.get("next_release_blockers", []) if x not in {
        "c_phys_background_3b_exact_run_input_freeze", "c_phys_background_3a_square_assembly_correction"
    }]
    for item in [
        "c_phys_background_3c_solver_implementation_audit",
        "c_phys_background_3c_execution_authorization",
        "c_phys_candidate_background_qa",
        "c_phys_background_evaluated_trace_matrix",
        "continuum_Fredholm_and_jacobian_analysis"
    ]:
        if item not in blockers:
            blockers.insert(0, item)
    m["next_release_blockers"] = blockers
    dump(MANIFEST, m)


def sync_decision() -> None:
    lines = [line for line in DECISIONS.read_text(encoding="utf-8").splitlines() if line.strip()]
    items = [json.loads(line) for line in lines]
    ids = [item["decision_id"] for item in items]
    if ids[-1] != "UL-DEC-0025":
        raise RuntimeError(f"unexpected latest decision: {ids[-1]}")
    if "UL-DEC-0026" not in ids:
        entry = {
            "decision_id": "UL-DEC-0026",
            "date": "2026-08-04",
            "topic": "c_phys_m1_background_3a_square_assembly_correction_and_cp01r1_rebind",
            "decision": "Background-3A is corrected append-only so that all eight regularized regional bulk residual blocks are enforced at every Lobatto node and the eight cap/global residuals are appended, producing 8N+8 equations for 8N+8 unknowns. The unexecuted CP01 run is superseded for execution and rebound without parameter, topology, Holder-exponent or seed changes as CP01R1 with a new immutable payload hash.",
            "status": "ACTIVE",
            "reason": "Literal strict-interior collocation was incompatible with the frozen nodal and augmented unknown count. The correction was detected before solver implementation or execution, and the Background-3B immutability rule requires a new run ID after any method-contract correction.",
            "sources": [ASSEMBLY, RUN, LEDGER, VALIDATOR, TESTS, "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.19.json", "project-manifest.json"],
            "evidence_effect": "NUMERICAL_PROTOCOL_AND_RUN_IDENTITY_DEFINITION_ONLY",
            "supersedes": None
        }
        lines.append(json.dumps(entry, separators=(",", ":"), ensure_ascii=False))
    DECISIONS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sync_checkpoint() -> None:
    cp = json.loads(LATEST.read_text(encoding="utf-8"))
    if cp.get("checkpoint_id") != "UL-CHK-20260804-018":
        raise RuntimeError(f"unexpected checkpoint basis: {cp.get('checkpoint_id')}")
    cp["checkpoint_id"] = "UL-CHK-20260804-019"
    cp["timestamp"] = "2026-08-04T11:25:00+02:00"
    cp["basis_commit"] = MERGE_COMMIT
    cp["canonical_snapshot"] = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.19.json"
    cp["supersedes"] = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.18.json"
    for source in [ASSEMBLY, RUN, LEDGER, VALIDATOR, TESTS]:
        if source not in cp["sources"]:
            cp["sources"].append(source)
    cp["current_goal"] = "Define and audit a quarantined CP01R1 solver implementation and a separate execution-authorization gate without executing the solver or claiming a background."
    cp["current_workstream"] = "PRIMARY_C_PHYS_M1_BACKGROUND_3C_IMPLEMENTATION_AND_AUTHORIZATION_GATE_WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC"
    cp["current_workstreams"][0]["next_block"] = NEXT
    cp["governance_principle"] = "A square discrete assembly and hash-frozen run input are not a solver implementation, execution authorization, numerical background, continuum theorem, stability result or physical evidence."
    cp["gate_state"].update({
        "MD2S-R1-C-PHYS": "ACTIVE_EXECUTION_IMPLEMENTATION_AND_AUTHORIZATION_GATE_REMAINING",
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED_SQUARE_ASSEMBLY_CORRECTED",
        "BACKGROUND_3B": "RUN_INPUT_FROZEN_CP01R1_EXECUTION_NOT_AUTHORIZED",
        "BACKGROUND_METHOD": "FROZEN_PREREGISTERED_WITH_ASSEMBLY_CORRECTION",
        "BACKGROUND_TOPOLOGY_SCHEMA": "FROZEN_SINGLE_CAP_PHASE",
        "BACKGROUND_RUN_INPUT": "FROZEN_CP01R1",
        "BACKGROUND_SOLVER_IMPLEMENTATION": "NOT_PRESENT",
        "BACKGROUND_SOLVER_EXECUTION": "NOT_AUTHORIZED",
        "R1.0": "ACTIVE_EXECUTION_IMPLEMENTATION_AND_AUTHORIZATION_GATE_REMAINING",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "FULL_LINEARIZED_BOUNDARY_TRACE_RANK": "NOT_PROVEN",
        "FREDHOLM_PROPERTY": "NOT_PROVEN",
        "CONTINUUM_BVP_JACOBIAN": "NOT_PROVEN",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "OFFICIAL_MD2S_SOLVER": "NOT_AUTHORIZED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "PHYSICAL_EVIDENCE_EFFECT": "NONE"
    })
    cp["verified_results"] = [x for x in cp.get("verified_results", []) if x.get("result_id") not in {
        "UL-RES-C-PHYS-M1-BG3B-001", "UL-RES-C-PHYS-M1-BG3A-ASSEMBLY-001"
    }]
    cp["verified_results"].extend([
        {
            "result_id": "UL-RES-C-PHYS-M1-BG3A-ASSEMBLY-001",
            "statement": "The corrected collocation bookkeeping has 8N regularized bulk rows plus eight cap/global rows for 8N+8 profile-and-augmented unknowns.",
            "status": "SQUARE_DISCRETE_COUNT_PREREGISTERED_NOT_EXECUTED",
            "evidence_effect": "NUMERICAL_PROTOCOL_DEFINITION_ONLY",
            "sources": [ASSEMBLY, LEDGER]
        },
        {
            "result_id": "UL-RES-C-PHYS-M1-BG3B-002",
            "statement": "The unchanged M1 control point is rebound as CP01R1 after the assembly correction with immutable payload hash 0ecf1a2e... and no solver implementation or execution.",
            "status": "RUN_INPUT_FROZEN_CP01R1_EXECUTION_NOT_AUTHORIZED",
            "evidence_effect": "NUMERICAL_RUN_INPUT_DEFINITION_ONLY",
            "sources": [RUN]
        }
    ])
    cp["open_blockers"] = [x for x in cp.get("open_blockers", []) if x.get("blocker_id") not in {
        "UL-BLK-C-PHYS-BACKGROUND-3C-001", "UL-BLK-C-PHYS-BACKGROUND-3A-ASSEMBLY-001"
    }]
    cp["open_blockers"].insert(1, {
        "blocker_id": "UL-BLK-C-PHYS-BACKGROUND-3C-001",
        "track_id": "MD2S-R1-C-PHYS",
        "statement": "No audited solver implementation or separate execution authorization exists for the frozen CP01R1 run input.",
        "sources": [RUN]
    })
    cp["active_assumptions"] = [
        "CP01R1 is the same order-one rational control point as unexecuted CP01, rebound solely because of the assembly correction.",
        "All eight regularized bulk blocks are collocated at all N Lobatto points per region and eight boundary/global equations are appended.",
        "The discrete sector is exactly (N_F,N_sigma,m_sigma)=(1,1,1).",
        "The exact a_F=0 base seed is bulk-and-patch exact but cap-inexact and is not a solution at target a_F=1/4.",
        "No solver implementation or execution is authorized."
    ]
    cp["forbidden_inferences"] = [
        "Do not treat the square discrete count as existence, uniqueness or continuum invertibility.",
        "Do not execute the superseded CP01 run ID.",
        "Do not describe CP01R1 as an observational fit, physical prediction or preferred point.",
        "Do not describe the analytic control seed as a full background solution.",
        "Do not infer trace rank, Fredholmness, stability, K1-D or K1-E."
    ]
    cp["entry_points"] = [ASSEMBLY, RUN, LEDGER, SEEDS, LOCK]
    cp["next_exact_action"] = f"Execute {NEXT}. Define and audit implementation only; do not execute without a separate versioned authorization."
    dump(SNAPSHOT, cp)
    dump(LATEST, cp)


if __name__ == "__main__":
    sync_manifest()
    sync_decision()
    sync_checkpoint()
