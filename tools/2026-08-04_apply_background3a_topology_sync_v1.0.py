#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-manifest.json"
DECISIONS = ROOT / "registry/decision-log.jsonl"
LATEST = ROOT / "registry/session-checkpoint-latest.json"
SNAPSHOT = ROOT / "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.17.json"
CORRECTION_MERGE = "ba7b50cae8ba90d5b36e195238f85c7f2d2b4d3b"
CORRECTION = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3ATopologyCorrectionContract_v0.2.json"
CORRECTION_LEDGER = "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3ATopologyCorrectionLedger_v0.2.md"


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sync_manifest() -> None:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    m["release"] = "2.9-c-phys-m1-background-3a-topology-corrected-v0.2"
    m["release_date"] = "2026-08-04"
    m["architecture"]["research_tracks"][1]["status"] = "ACTIVE_RUN_INPUT_FREEZE_AND_FREDHOLM_ANALYSIS_REMAINING"

    g = m["gates"]
    g.update({
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED_CORRECTED_TO_SINGLE_CAP_PHASE",
        "BACKGROUND_METHOD": "FROZEN_PREREGISTERED",
        "BACKGROUND_TOPOLOGY_SCHEMA": "FROZEN_SINGLE_CAP_PHASE",
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
        "physical_evidence_effect": "NONE",
    })

    bg = m["c_phys_background_3a"]
    bg.update({
        "status": "PREREGISTERED_NOT_EXECUTED_CORRECTED_TO_SINGLE_CAP_PHASE",
        "canonical_correction": CORRECTION,
        "canonical_correction_ledger": CORRECTION_LEDGER,
        "topological_input_order": ["N_F", "N_sigma", "m_sigma"],
        "topological_input_count": 3,
        "forbidden_regional_labels": ["m_N", "m_S", "n_N", "n_S"],
        "topology_schema": "FROZEN_SINGLE_CAP_PHASE",
        "run_input": "NOT_FROZEN",
        "current_execution": "NOT_EXECUTED",
        "physical_background": "NOT_ESTABLISHED",
        "physical_evidence_effect": "NONE",
        "next_block": "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY",
    })

    entry = m["c_phys_operator_entry"]
    entry["status"] = "BACKGROUND_3A_METHOD_AND_SINGLE_CAP_TOPOLOGY_FROZEN_RUN_INPUT_REMAINING"
    entry["next_block"] = "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY"
    entry["solver_authorized"] = False
    entry["physical_background"] = "NOT_ESTABLISHED"

    regs = m["central_registries"]
    regs.update({
        "c_phys_m1_background_3a_topology_correction": CORRECTION,
        "c_phys_m1_background_3a_topology_ledger": CORRECTION_LEDGER,
        "session_checkpoint_snapshot": "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.17.json",
    })
    m["workstream_priority"] = [
        "MD2S-R1-C-PHYS:C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY",
        "HZT-M0-S6-C1-V:G1.2_PARALLEL_DIAGNOSTIC_ONLY",
    ]
    dump(MANIFEST, m)


def sync_decision() -> None:
    lines = [line for line in DECISIONS.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [json.loads(line)["decision_id"] for line in lines]
    if "UL-DEC-0024" not in ids:
        entry = {
            "decision_id": "UL-DEC-0024",
            "date": "2026-08-04",
            "topic": "c_phys_m1_background_3a_single_cap_topology_correction",
            "decision": "Background-3A is append-only corrected from an unsupported five-label regional topology input to the canonical single-cap-phase sector (N_F,N_sigma,m_sigma). The current M1 parent action contains one common localized sigma field; any regionalized cap phases require a new parent action, model ID and boundary operator. No run input or solver execution follows.",
            "status": "ACTIVE",
            "reason": "Freeze-1A, the M1 function contract, Operator-2B and the parent action all define one localized cap phase with q_sigma=m_sigma q_ref and d_chi=N_sigma-m_sigma q_hat a_chi,Sigma. The defect was found before Background-3B or any numerical result.",
            "sources": [CORRECTION, CORRECTION_LEDGER, "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.17.json", "project-manifest.json"],
            "evidence_effect": "NUMERICAL_PROTOCOL_AND_MODEL_IDENTITY_CORRECTION_ONLY",
            "supersedes": None,
        }
        lines.append(json.dumps(entry, separators=(",", ":"), ensure_ascii=False))
    DECISIONS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sync_checkpoint() -> None:
    cp = json.loads(LATEST.read_text(encoding="utf-8"))
    cp["checkpoint_id"] = "UL-CHK-20260804-017"
    cp["timestamp"] = "2026-08-04T06:05:00+02:00"
    cp["basis_commit"] = CORRECTION_MERGE
    cp["canonical_snapshot"] = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.17.json"
    cp["supersedes"] = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.16.json"
    for source in [CORRECTION, CORRECTION_LEDGER]:
        if source not in cp["sources"]:
            cp["sources"].append(source)
    cp["current_goal"] = "Freeze exactly one M1 model point and the corrected single-cap topological sector (N_F,N_sigma,m_sigma), plus all run hashes, without executing the solver."
    cp["current_workstream"] = "PRIMARY_C_PHYS_M1_BACKGROUND_3B_SINGLE_CAP_RUN_INPUT_FREEZE_WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC"
    cp["current_workstreams"][0]["next_block"] = "C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY"
    cp["governance_principle"] = "The two regional bulk charts share one localized cap phase; regional cap charges or windings require a new model and may not enter M1 run inputs."
    cp["gate_state"].update({
        "MD2S-R1-C-PHYS": "ACTIVE_RUN_INPUT_FREEZE_AND_FREDHOLM_ANALYSIS_REMAINING",
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED_CORRECTED_TO_SINGLE_CAP_PHASE",
        "BACKGROUND_METHOD": "FROZEN_PREREGISTERED",
        "BACKGROUND_TOPOLOGY_SCHEMA": "FROZEN_SINGLE_CAP_PHASE",
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
        "PHYSICAL_EVIDENCE_EFFECT": "NONE",
    })
    cp["verified_results"] = [item for item in cp.get("verified_results", []) if item.get("result_id") != "UL-RES-C-PHYS-M1-BG3A-TOPO-001"]
    cp["verified_results"].append({
        "result_id": "UL-RES-C-PHYS-M1-BG3A-TOPO-001",
        "statement": "The effective Background-3A topological input schema is corrected to the one-cap vector (N_F,N_sigma,m_sigma); the prior regional five-label vector is noncanonical and forbidden.",
        "status": "PROVEN_CONDITIONAL_ON_CURRENT_M1_PARENT_ACTION",
        "evidence_effect": "NUMERICAL_PROTOCOL_AND_MODEL_IDENTITY_CORRECTION_ONLY",
        "sources": [CORRECTION, CORRECTION_LEDGER],
    })
    cp["active_assumptions"] = [
        "The active M1 parent action contains one common localized cap phase sigma.",
        "The discrete run sector is exactly (N_F,N_sigma,m_sigma).",
        "Background-3A methods and thresholds remain otherwise unchanged from v0.1.",
        "No exact run input is frozen and no solver initialization is permitted.",
    ]
    cp["forbidden_inferences"] = [
        "Do not use m_N,m_S,n_N or n_S in an M1 run input.",
        "Do not interpret the topology correction as a numerical result or background solution.",
        "Do not infer trace rank, Fredholmness, continuum invertibility, stability or physical confirmation.",
        "Do not change R1.1, R1.2, solver authorization, K1-D or K1-E.",
    ]
    cp["entry_points"] = [CORRECTION, CORRECTION_LEDGER, "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json", "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceContract_v0.1.json"]
    cp["next_exact_action"] = "Execute C-PHYS-R1.0-BACKGROUND-3B_RUN_INPUT_FREEZE_ONLY using exactly (N_F,N_sigma,m_sigma); do not execute the solver."
    dump(SNAPSHOT, cp)
    dump(LATEST, cp)


if __name__ == "__main__":
    sync_manifest()
    sync_decision()
    sync_checkpoint()
