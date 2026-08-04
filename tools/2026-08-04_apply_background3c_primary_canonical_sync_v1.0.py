#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-manifest.json"
DECISIONS = ROOT / "registry/decision-log.jsonl"
LATEST = ROOT / "registry/session-checkpoint-latest.json"
SNAPSHOT = ROOT / "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.20.json"
MERGE_COMMIT = "f046a55ea06187c7ae6059e613cab96610e7a396"
NEXT = "C-PHYS-R1.0-BACKGROUND-3C2_INDEPENDENT_BACKEND_AND_EXECUTION_PACKAGE"
IMPL = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CImplementationContract_v0.2.json"
AUTH = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.1.json"
RESULT_SCHEMA = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResultSchema_v0.1.json"
RESOURCE = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
AUDIT_RESULT = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CPrimaryImplementationAuditResult_v0.1.json"
LEDGER = "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CPrimaryImplementationLedger_v0.1.md"
KERNEL = "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py"
GATE = "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_gate_v0.2.py"
VALIDATOR = "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3c_v0.2.py"
TESTS = "tests/2026-08-04_test_hzt_m0_s6_c_phys_m1_background_3c_v0.2.py"
LOCK = "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C_v0.1.txt"


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sync_manifest() -> None:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if m.get("release") != "2.11-c-phys-m1-background-3a-assembly-corrected-v0.3":
        raise RuntimeError(f"unexpected basis release: {m.get('release')}")
    m["release"] = "2.12-c-phys-m1-background-3c-primary-audited-v0.2"
    m["release_date"] = "2026-08-04"
    physical = m["architecture"]["research_tracks"][1]
    physical["status"] = "ACTIVE_INDEPENDENT_BACKEND_AND_EXECUTION_PACKAGE_REMAINING"
    physical["active_model"] = "HZT-M0-S6-C-PHYS-M1"
    g = m["gates"]
    g.update({
        "R1.0": "ACTIVE_INDEPENDENT_BACKEND_AND_EXECUTION_PACKAGE_REMAINING",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED_SQUARE_ASSEMBLY_CORRECTED",
        "BACKGROUND_3B": "RUN_INPUT_FROZEN_CP01R1_EXECUTION_NOT_AUTHORIZED",
        "BACKGROUND_RUN_INPUT": "FROZEN_CP01R1",
        "BACKGROUND_3C_PRIMARY_IMPLEMENTATION": "PASS_AUDITED_NO_EXECUTION",
        "BACKGROUND_3C_INDEPENDENT_BACKEND": "NOT_PRESENT",
        "BACKGROUND_3C_EXECUTION": "NOT_AUTHORIZED",
        "BACKGROUND_SOLVER_IMPLEMENTATION": "PRIMARY_PRESENT_INDEPENDENT_MISSING",
        "BACKGROUND_SOLVER_EXECUTION": "NOT_AUTHORIZED",
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
        "status": "BACKGROUND_3C_PRIMARY_IMPLEMENTATION_AUDITED_INDEPENDENT_BACKEND_MISSING",
        "physical_background": "NOT_ESTABLISHED",
        "solver_authorized": False,
        "next_block": NEXT
    })
    for key in ("parent_action_v0_1", "c_phys_m1", "c_phys_background_3a", "c_phys_background_3b"):
        if key in m:
            m[key]["next_block"] = NEXT
    m["c_phys_background_3c"] = {
        "track_id": "MD2S-R1-C-PHYS",
        "model_id": "HZT-M0-S6-C-PHYS-M1",
        "block": "C-PHYS-R1.0-BACKGROUND-3C1_PRIMARY_IMPLEMENTATION_AUDIT",
        "classification": "QUARANTINED_PRIMARY_IMPLEMENTATION_NO_EXECUTION",
        "status": "PRIMARY_IMPLEMENTATION_PASS_AUDITED_NO_EXECUTION",
        "run_id": "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1",
        "run_payload_sha256": "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302",
        "canonical_kernel": KERNEL,
        "canonical_kernel_git_blob_sha": "e232537ab80f099b0b3a914c509041c13825e950",
        "canonical_gate": GATE,
        "canonical_gate_git_blob_sha": "6a91651d2b34a603a972266a76451deb850699ea",
        "primary_audit_status": "PASS_PRIMARY_IMPLEMENTATION_AUDIT_NO_SOLVER_EXECUTION",
        "audit_node_count": 24,
        "audit_polynomial_degree": 23,
        "audit_state_and_residual_size": 200,
        "audit_derivative_error_max": 1.1368683772161603e-13,
        "audit_control_bulk_raw_inf": 6.845900235585844e-11,
        "audit_control_constraint_raw_inf": 1.3877787807814457e-17,
        "audit_newton_call_count": 0,
        "run_command_exit_code": 73,
        "direct_kernel_exit_code": 73,
        "authorization": "NOT_GRANTED",
        "future_grant_present": False,
        "independent_backend": "NOT_PRESENT_BLOCKING",
        "result_schema": "FROZEN_NOT_INSTANTIATED",
        "resource_policy": "FROZEN_EXECUTION_NOT_AUTHORIZED",
        "result_artifact_created": False,
        "solver_executed": False,
        "physical_background": "NOT_ESTABLISHED",
        "physical_evidence_effect": "NONE",
        "implementation_contract": IMPL,
        "authorization_contract": AUTH,
        "result_schema_contract": RESULT_SCHEMA,
        "resource_policy_contract": RESOURCE,
        "audit_result": AUDIT_RESULT,
        "ledger": LEDGER,
        "dependency_lock": LOCK,
        "validator": VALIDATOR,
        "tests": TESTS,
        "next_block": NEXT
    }
    regs = m["central_registries"]
    regs.update({
        "c_phys_m1_background_3c_implementation": IMPL,
        "c_phys_m1_background_3c_authorization": AUTH,
        "c_phys_m1_background_3c_result_schema": RESULT_SCHEMA,
        "c_phys_m1_background_3c_resource_policy": RESOURCE,
        "c_phys_m1_background_3c_audit_result": AUDIT_RESULT,
        "c_phys_m1_background_3c_ledger": LEDGER,
        "session_checkpoint_snapshot": "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.20.json"
    })
    m["workstream_priority"] = [
        f"MD2S-R1-C-PHYS:{NEXT}",
        "HZT-M0-S6-C1-V:G1.2_PARALLEL_DIAGNOSTIC_ONLY"
    ]
    blockers = [x for x in m.get("next_release_blockers", []) if x not in {
        "c_phys_background_3c_solver_implementation_audit",
        "c_phys_background_3c_primary_implementation"
    }]
    for item in [
        "c_phys_background_3c_independent_backend_implementation",
        "c_phys_background_3c_independent_residual_assembly",
        "c_phys_background_3c_execution_package_audit",
        "c_phys_background_3c_append_only_execution_decision",
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
    if ids[-1] != "UL-DEC-0026":
        raise RuntimeError(f"unexpected latest decision: {ids[-1]}")
    if "UL-DEC-0027" not in ids:
        entry = {
            "decision_id": "UL-DEC-0027",
            "date": "2026-08-04",
            "topic": "c_phys_m1_background_3c_primary_implementation_audit",
            "decision": "The CP01R1 primary all-node Chebyshev-Lobatto implementation is accepted as source-hash-bound and audit-passing without solver execution. The audit reproduces the control-seed bulk, constraint and cap-defect values, the exact seven-seed rule, RRQR regression and both exit-73 firewalls with zero Newton calls. Execution remains unauthorized because the independently coded backend and append-only grant do not exist.",
            "status": "ACTIVE",
            "reason": "Implementation audit establishes software and algebra consistency only. Background-3A requires independent residual assembly before execution can be considered, and no numerical candidate or result artifact exists.",
            "sources": [IMPL, AUTH, RESULT_SCHEMA, RESOURCE, AUDIT_RESULT, LEDGER, KERNEL, GATE, VALIDATOR, TESTS, "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.20.json", "project-manifest.json"],
            "evidence_effect": "SOFTWARE_IMPLEMENTATION_AND_ALGEBRA_QA_ONLY",
            "supersedes": None
        }
        lines.append(json.dumps(entry, separators=(",", ":"), ensure_ascii=False))
    DECISIONS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sync_checkpoint() -> None:
    cp = json.loads(LATEST.read_text(encoding="utf-8"))
    if cp.get("checkpoint_id") != "UL-CHK-20260804-019":
        raise RuntimeError(f"unexpected checkpoint basis: {cp.get('checkpoint_id')}")
    cp["checkpoint_id"] = "UL-CHK-20260804-020"
    cp["timestamp"] = "2026-08-04T12:05:00+02:00"
    cp["basis_commit"] = MERGE_COMMIT
    cp["canonical_snapshot"] = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.20.json"
    cp["supersedes"] = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.19.json"
    for source in [IMPL, AUTH, RESULT_SCHEMA, RESOURCE, AUDIT_RESULT, LEDGER, KERNEL, GATE, VALIDATOR, TESTS, LOCK]:
        if source not in cp["sources"]:
            cp["sources"].append(source)
    cp["current_goal"] = "Implement and audit a genuinely independent CP01R1 residual backend and a new dual-backend execution package without executing either backend."
    cp["current_workstream"] = "PRIMARY_C_PHYS_M1_BACKGROUND_3C2_INDEPENDENT_BACKEND_AND_EXECUTION_PACKAGE_WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC"
    cp["current_workstreams"][0]["next_block"] = NEXT
    cp["governance_principle"] = "A source-hash-bound primary implementation and passing audit are not execution authorization, a numerical background, a continuum theorem, stability or physical evidence."
    cp["gate_state"].update({
        "MD2S-R1-C-PHYS": "ACTIVE_INDEPENDENT_BACKEND_AND_EXECUTION_PACKAGE_REMAINING",
        "R1.0": "ACTIVE_INDEPENDENT_BACKEND_AND_EXECUTION_PACKAGE_REMAINING",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "BACKGROUND_3A": "PREREGISTERED_NOT_EXECUTED_SQUARE_ASSEMBLY_CORRECTED",
        "BACKGROUND_3B": "RUN_INPUT_FROZEN_CP01R1_EXECUTION_NOT_AUTHORIZED",
        "BACKGROUND_RUN_INPUT": "FROZEN_CP01R1",
        "BACKGROUND_3C_PRIMARY_IMPLEMENTATION": "PASS_AUDITED_NO_EXECUTION",
        "BACKGROUND_3C_INDEPENDENT_BACKEND": "NOT_PRESENT",
        "BACKGROUND_3C_EXECUTION": "NOT_AUTHORIZED",
        "BACKGROUND_SOLVER_IMPLEMENTATION": "PRIMARY_PRESENT_INDEPENDENT_MISSING",
        "BACKGROUND_SOLVER_EXECUTION": "NOT_AUTHORIZED",
        "FULL_LINEARIZED_BOUNDARY_TRACE_RANK": "NOT_PROVEN",
        "FREDHOLM_PROPERTY": "NOT_PROVEN",
        "CONTINUUM_BVP_JACOBIAN": "NOT_PROVEN",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "OFFICIAL_MD2S_SOLVER": "NOT_AUTHORIZED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "PHYSICAL_EVIDENCE_EFFECT": "NONE"
    })
    cp["verified_results"] = [x for x in cp.get("verified_results", []) if x.get("result_id") != "UL-RES-C-PHYS-M1-BG3C1-001"]
    cp["verified_results"].append({
        "result_id": "UL-RES-C-PHYS-M1-BG3C1-001",
        "statement": "The CP01R1 primary collocation implementation is source-hash-bound and passes audit-only algebra, seed, RRQR and authorization-firewall tests with zero Newton calls and no result artifact.",
        "status": "PASS_PRIMARY_IMPLEMENTATION_AUDIT_NO_SOLVER_EXECUTION",
        "evidence_effect": "SOFTWARE_IMPLEMENTATION_AND_ALGEBRA_QA_ONLY",
        "sources": [IMPL, AUDIT_RESULT, LEDGER]
    })
    cp["open_blockers"] = [x for x in cp.get("open_blockers", []) if x.get("blocker_id") not in {
        "UL-BLK-C-PHYS-BACKGROUND-3C-001", "UL-BLK-C-PHYS-BACKGROUND-3C2-001"
    }]
    cp["open_blockers"].insert(1, {
        "blocker_id": "UL-BLK-C-PHYS-BACKGROUND-3C2-001",
        "track_id": "MD2S-R1-C-PHYS",
        "statement": "No independently coded CP01R1 residual backend or dual-backend execution package exists; execution authorization therefore remains inadmissible.",
        "sources": [IMPL, AUTH]
    })
    cp["active_assumptions"] = [
        "CP01R1 remains the sole frozen run input.",
        "The primary kernel is audited but has not performed a Newton iteration.",
        "The required independent backend must not import or wrap the primary residual function.",
        "The exact a_F=0 seed remains bulk-and-patch exact but cap-inexact.",
        "No solver execution or result artifact is authorized."
    ]
    cp["forbidden_inferences"] = [
        "Do not interpret implementation audit as a numerical root or candidate background.",
        "Do not edit the v0.1 denial artifact into a grant.",
        "Do not call a wrapper around the primary residual an independent backend.",
        "Do not infer continuum existence, trace rank, Fredholmness, stability or physical evidence.",
        "Do not change K1-D or K1-E."
    ]
    cp["entry_points"] = [IMPL, AUDIT_RESULT, AUTH, RESULT_SCHEMA, RESOURCE, LEDGER, KERNEL, GATE]
    cp["next_exact_action"] = f"Execute {NEXT}: implement and audit independent residual assembly and a dual-backend runner, but do not run Newton or create result artifacts."
    dump(SNAPSHOT, cp)
    dump(LATEST, cp)


if __name__ == "__main__":
    sync_manifest()
    sync_decision()
    sync_checkpoint()
