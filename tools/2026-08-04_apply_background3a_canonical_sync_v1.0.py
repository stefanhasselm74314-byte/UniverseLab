#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-manifest.json"
DECISIONS = ROOT / "registry/decision-log.jsonl"
LATEST = ROOT / "registry/session-checkpoint-latest.json"
SNAPSHOT = ROOT / "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.16.json"
BACKGROUND_3A_MERGE = "2e20213f4c83c415f1c652078521257591812395"


def dump(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sync_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["release"] = "2.8-c-phys-m1-background-3a-preregistered-v0.1"
    manifest["release_date"] = "2026-08-04"

    physical_track = manifest["architecture"]["research_tracks"][1]
    physical_track["status"] = "ACTIVE_RUN_INPUT_FREEZE_AND_FREDHOLM_ANALYSIS_REMAINING"
    physical_track["active_model"] = "HZT-M0-S6-C-PHYS-M1"

    gates = manifest["gates"]
    gates.update({
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED",
        "BACKGROUND_METHOD": "FROZEN_PREREGISTERED",
        "BACKGROUND_RUN_INPUT": "NOT_FROZEN",
        "BACKGROUND_SOLVER_EXECUTION": "FORBIDDEN_PENDING_BACKGROUND_3B_AND_LATER_GATE",
        "R1.0": "ACTIVE_RUN_INPUT_FREEZE_AND_FREDHOLM_ANALYSIS_REMAINING",
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

    entry = manifest.setdefault("c_phys_operator_entry", {})
    entry.update({
        "track_id": "MD2S-R1-C-PHYS",
        "model_id": "HZT-M0-S6-C-PHYS-M1",
        "phase": "R1.0",
        "status": "BACKGROUND_3A_METHOD_PREREGISTERED_RUN_INPUT_REMAINING",
        "physical_background": "NOT_ESTABLISHED",
        "solver_authorized": False,
        "next_block": "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY"
    })

    if "parent_action_v0_1" in manifest:
        manifest["parent_action_v0_1"]["next_block"] = "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY"
    if "c_phys_m1" in manifest:
        manifest["c_phys_m1"]["next_block"] = "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY"

    manifest["c_phys_background_3a"] = {
        "track_id": "MD2S-R1-C-PHYS",
        "model_id": "HZT-M0-S6-C-PHYS-M1",
        "block": "C-PHYS-R1.0-BACKGROUND-3A",
        "classification": "NUMERICAL_METHOD_PREREGISTRATION_NO_SOLVER_EXECUTION",
        "status": "PREREGISTERED_NOT_EXECUTED",
        "contract": "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json",
        "ledger": "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationLedger_v0.1.md",
        "validator": "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3a_v0.1.py",
        "tests": "tests/2026-08-04_test_hzt_m0_s6_c_phys_m1_background_3a_v0.1.py",
        "primary_method": "CHEBYSHEV_LOBATTO_COLLOCATION_IN_TAU",
        "node_levels": [24, 32, 48, 64, 96],
        "deterministic_seed_count": 7,
        "independent_backend_required": True,
        "run_input": "NOT_FROZEN",
        "current_execution": "NOT_EXECUTED",
        "physical_background": "NOT_ESTABLISHED",
        "physical_evidence_effect": "NONE",
        "next_block": "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY"
    }

    registries = manifest.setdefault("central_registries", {})
    registries.update({
        "c_phys_m1_background_3a_contract": "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json",
        "c_phys_m1_background_3a_ledger": "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationLedger_v0.1.md",
        "session_checkpoint": "registry/session-checkpoint-latest.json",
        "session_checkpoint_snapshot": "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.16.json"
    })

    manifest["workstream_priority"] = [
        "MD2S-R1-C-PHYS:C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY",
        "HZT-M0-S6-C1-V:G1.2_PARALLEL_DIAGNOSTIC_ONLY"
    ]

    blockers = [item for item in manifest.get("next_release_blockers", []) if item != "c_phys_candidate_background_protocol"]
    for item in [
        "c_phys_background_3b_exact_run_input_freeze",
        "c_phys_background_execution_authorization",
        "c_phys_candidate_background_qa",
        "c_phys_background_evaluated_trace_matrix",
        "continuum_Fredholm_and_jacobian_analysis"
    ]:
        if item not in blockers:
            blockers.insert(0, item)
    manifest["next_release_blockers"] = blockers
    dump(MANIFEST, manifest)


def sync_decision() -> None:
    lines = [line for line in DECISIONS.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [json.loads(line)["decision_id"] for line in lines]
    if "UL-DEC-0023" not in ids:
        entry = {
            "decision_id": "UL-DEC-0023",
            "date": "2026-08-04",
            "topic": "c_phys_m1_background_3a_method_preregistration",
            "decision": "The Background-3A numerical construction protocol for HZT-M0-S6-C-PHYS-M1 is preregistered with fixed tau-chart collocation levels, deterministic seeds, nonlinear-method limits, convergence and admissibility thresholds, independent-backend requirements and fail-closed result classes. No parameter/topology instance is frozen and no solver execution, background, rank, Fredholm, stability or physical claim follows.",
            "status": "ACTIVE",
            "reason": "Separating method preregistration from run-input selection and execution prevents post-hoc parameter, seed, mesh and tolerance tuning and preserves the distinction between a numerical candidate and a continuum or physical result.",
            "sources": [
                "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json",
                "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationLedger_v0.1.md",
                "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.16.json",
                "project-manifest.json"
            ],
            "evidence_effect": "NUMERICAL_PROTOCOL_DEFINITION_ONLY",
            "supersedes": None
        }
        lines.append(json.dumps(entry, separators=(",", ":"), ensure_ascii=False))
    DECISIONS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sync_checkpoint() -> None:
    checkpoint = json.loads(LATEST.read_text(encoding="utf-8"))
    checkpoint["checkpoint_id"] = "UL-CHK-20260804-016"
    checkpoint["timestamp"] = "2026-08-04T05:30:00+02:00"
    checkpoint["basis_commit"] = BACKGROUND_3A_MERGE
    checkpoint["canonical_snapshot"] = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.16.json"
    checkpoint["supersedes"] = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.15.json"
    checkpoint.pop("provenance_correction", None)

    for source in [
        "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json",
        "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationLedger_v0.1.md",
        "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3a_v0.1.py",
        "tests/2026-08-04_test_hzt_m0_s6_c_phys_m1_background_3a_v0.1.py"
    ]:
        if source not in checkpoint["sources"]:
            checkpoint["sources"].append(source)

    checkpoint["current_goal"] = "Freeze exactly one C-PHYS-M1 parameter and topology instance, Holder exponent, deterministic seed-set hash and software/dependency hashes without executing the solver."
    checkpoint["current_workstream"] = "PRIMARY_C_PHYS_M1_BACKGROUND_3B_RUN_INPUT_FREEZE_WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC"
    checkpoint["current_workstreams"] = [
        {
            "track_id": "MD2S-R1-C-PHYS",
            "model_id": "HZT-M0-S6-C-PHYS-M1",
            "priority": "PRIMARY",
            "next_block": "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY"
        },
        {
            "track_id": "HZT-M0-S6-C1-V",
            "priority": "PARALLEL_DIAGNOSTIC_ONLY",
            "next_block": "G1.2_LOCAL_SECOND_ORDER_DISCRETE_RESPONSE_DIAGNOSTIC"
        }
    ]
    checkpoint["governance_principle"] = "A preregistered numerical method is not a frozen run input, solver authorization, numerical background, continuum theorem, stability result or physical evidence."

    checkpoint["gate_state"].update({
        "MD2S-R1-C-PHYS": "ACTIVE_RUN_INPUT_FREEZE_AND_FREDHOLM_ANALYSIS_REMAINING",
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED",
        "BACKGROUND_METHOD": "FROZEN_PREREGISTERED",
        "BACKGROUND_RUN_INPUT": "NOT_FROZEN",
        "BACKGROUND_SOLVER_EXECUTION": "FORBIDDEN_PENDING_BACKGROUND_3B_AND_LATER_GATE",
        "R1.0": "ACTIVE_RUN_INPUT_FREEZE_AND_FREDHOLM_ANALYSIS_REMAINING",
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

    checkpoint["verified_results"] = [
        item for item in checkpoint.get("verified_results", [])
        if item.get("result_id") != "UL-RES-C-PHYS-M1-BG3A-001"
    ]
    checkpoint["verified_results"].append({
        "result_id": "UL-RES-C-PHYS-M1-BG3A-001",
        "statement": "The Background-3A candidate-background construction method, deterministic seed policy, fixed mesh sequence, convergence thresholds, independent-backend requirement and fail-closed result classes are preregistered without a run input or execution.",
        "status": "PREREGISTERED_NOT_EXECUTED",
        "evidence_effect": "NUMERICAL_PROTOCOL_DEFINITION_ONLY",
        "sources": [
            "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json",
            "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationLedger_v0.1.md"
        ]
    })

    checkpoint["open_blockers"] = [
        item for item in checkpoint.get("open_blockers", [])
        if item.get("blocker_id") not in {"UL-BLK-C-PHYS-BACKGROUND-3A-001", "UL-BLK-C-PHYS-BACKGROUND-003"}
    ]
    checkpoint["open_blockers"].insert(1, {
        "blocker_id": "UL-BLK-C-PHYS-BACKGROUND-3B-001",
        "track_id": "MD2S-R1-C-PHYS",
        "statement": "No exact M1 parameter/topology run input, Holder exponent, seed-set hash or software/dependency hash has been frozen; solver initialization remains forbidden.",
        "sources": [
            "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"
        ]
    })

    checkpoint["active_assumptions"] = [
        "Background-3A fixes a numerical method and QA protocol only; it contains no physical parameter point.",
        "The future primary discretization uses the frozen Operator-2B tau chart and preregistered node sequence.",
        "All seven seeds are deterministic and all distinct accepted candidates must be retained.",
        "An independent backend is required for any future diagnostic candidate status.",
        "No solver initialization is permitted before Background-3B freezes one exact run input and a later gate authorizes execution."
    ]
    checkpoint["forbidden_inferences"] = [
        "Do not describe Background-3A as a solver run or numerical background result.",
        "Do not select or change parameter values under the Background-3A identifier.",
        "Do not infer continuum existence, uniqueness, trace rank, Fredholmness or Jacobian invertibility.",
        "Do not infer perturbative stability, ghost freedom, observational viability or physical confirmation.",
        "Do not change R1.1, R1.2, solver authorization, K1-D or K1-E."
    ]
    checkpoint["entry_points"] = [
        "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json",
        "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationLedger_v0.1.md",
        "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceContract_v0.1.json",
        "registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json"
    ]
    checkpoint["next_exact_action"] = "Execute C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY. Freeze one exact parameter/topology point and all run hashes; do not execute the solver."

    dump(SNAPSHOT, checkpoint)
    dump(LATEST, checkpoint)


if __name__ == "__main__":
    sync_manifest()
    sync_decision()
    sync_checkpoint()
