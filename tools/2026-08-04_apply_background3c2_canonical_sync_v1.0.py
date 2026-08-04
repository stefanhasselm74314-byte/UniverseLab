#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-manifest.json"
DECISIONS = ROOT / "registry/decision-log.jsonl"
LATEST = ROOT / "registry/session-checkpoint-latest.json"
SNAPSHOT = ROOT / "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.21.json"
MERGE_COMMIT = "e9e2deb91046185c9cedae807588ecad60317f35"
NEXT = "C-PHYS-R1.0-BACKGROUND-3C3_EXECUTION_AUTHORIZATION_REVIEW_ONLY"
IND_CONTRACT = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CIndependentBackendContract_v0.1.json"
DUAL_CONTRACT = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CDualBackendPackageContract_v0.1.json"
AUDIT_RESULT = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C2DualBackendAuditResult_v0.1.json"
LEDGER = "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C2IndependentBackendLedger_v0.1.md"
INDEPENDENT_SOURCE = "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_independent_backend_v0.1.py"
DUAL_GATE = "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_dual_backend_gate_v0.1.py"
VALIDATOR = "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3c2_v0.1.py"
TESTS = "tests/2026-08-04_test_hzt_m0_s6_c_phys_m1_background_3c2_v0.1.py"


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sync_manifest() -> None:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if m.get("release") != "2.12-c-phys-m1-background-3c-primary-audited-v0.2":
        raise RuntimeError(f"unexpected basis release: {m.get('release')}")
    m["release"] = "2.13-c-phys-m1-background-3c2-dual-backend-audited-v0.1"
    m["release_date"] = "2026-08-04"
    physical = m["architecture"]["research_tracks"][1]
    physical["status"] = "ACTIVE_EXECUTION_AUTHORIZATION_REVIEW_REMAINING"
    physical["active_model"] = "HZT-M0-S6-C-PHYS-M1"
    g = m["gates"]
    g.update({
        "R1.0": "ACTIVE_EXECUTION_AUTHORIZATION_REVIEW_REMAINING",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "BACKGROUND_RUN_INPUT": "FROZEN_CP01R1",
        "BACKGROUND_3C_PRIMARY_IMPLEMENTATION": "PASS_AUDITED_NO_EXECUTION",
        "BACKGROUND_3C_INDEPENDENT_BACKEND": "PASS_CONTROL_AUDIT_NO_ROOT_SOLVE",
        "BACKGROUND_3C_DUAL_BACKEND_PACKAGE": "PASS_AUDITED_NO_EXECUTION",
        "BACKGROUND_3C_EXECUTION": "NOT_AUTHORIZED",
        "BACKGROUND_SOLVER_IMPLEMENTATION": "DUAL_BACKEND_PRESENT_AUDITED_NO_EXECUTION",
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
        "status": "BACKGROUND_3C_DUAL_BACKEND_AUDITED_EXECUTION_NOT_AUTHORIZED",
        "physical_background": "NOT_ESTABLISHED",
        "solver_authorized": False,
        "next_block": NEXT
    })
    for key in ("parent_action_v0_1", "c_phys_m1", "c_phys_background_3a", "c_phys_background_3b", "c_phys_background_3c"):
        if key in m:
            m[key]["next_block"] = NEXT
    bg = m["c_phys_background_3c"]
    bg.update({
        "status": "DUAL_BACKEND_PASS_AUDITED_NO_EXECUTION",
        "independent_backend": "PASS_CONTROL_AUDIT_NO_ROOT_SOLVE",
        "dual_backend_package": "PASS_AUDITED_NO_EXECUTION",
        "independent_source": INDEPENDENT_SOURCE,
        "independent_source_git_blob_sha": "bed68e11a3682d8b140b6db0cbe71fd696c3ff34",
        "dual_gate": DUAL_GATE,
        "dual_gate_git_blob_sha": "947dc7173ee6c5b9ec69930ec61b654438abf991",
        "dual_audit_status": "PASS_DUAL_BACKEND_CONTROL_AUDIT_NO_NONLINEAR_EXECUTION",
        "independent_control_integrations": 6,
        "independent_shooting_jacobian_calls": 0,
        "independent_shooting_root_calls": 0,
        "target_model_solves": 0,
        "primary_independent_boundary_distance_max": 1.0458300891968975e-13,
        "authorization": "NOT_GRANTED",
        "future_grant_present": False,
        "result_artifact_created": False,
        "solver_executed": False,
        "physical_background": "NOT_ESTABLISHED",
        "physical_evidence_effect": "NONE",
        "independent_backend_contract": IND_CONTRACT,
        "dual_backend_contract": DUAL_CONTRACT,
        "dual_audit_result": AUDIT_RESULT,
        "independent_backend_ledger": LEDGER,
        "dual_backend_validator": VALIDATOR,
        "dual_backend_tests": TESTS,
        "next_block": NEXT
    })
    regs = m["central_registries"]
    regs.update({
        "c_phys_m1_background_3c_independent_backend": IND_CONTRACT,
        "c_phys_m1_background_3c_dual_package": DUAL_CONTRACT,
        "c_phys_m1_background_3c2_audit_result": AUDIT_RESULT,
        "c_phys_m1_background_3c2_ledger": LEDGER,
        "session_checkpoint_snapshot": "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.21.json"
    })
    m["workstream_priority"] = [
        f"MD2S-R1-C-PHYS:{NEXT}",
        "HZT-M0-S6-C1-V:G1.2_PARALLEL_DIAGNOSTIC_ONLY"
    ]
    blockers = [x for x in m.get("next_release_blockers", []) if x not in {
        "c_phys_background_3c_independent_backend_implementation",
        "c_phys_background_3c_independent_residual_assembly",
        "c_phys_background_3c_execution_package_audit"
    }]
    for item in [
        "c_phys_background_3c3_execution_authorization_review",
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
    if ids[-1] != "UL-DEC-0027":
        raise RuntimeError(f"unexpected latest decision: {ids[-1]}")
    if "UL-DEC-0028" not in ids:
        entry = {
            "decision_id": "UL-DEC-0028",
            "date": "2026-08-04",
            "topic": "c_phys_m1_background_3c2_independent_dual_backend_audit",
            "decision": "The separately coded x-space DOP853 backend and audit-only dual-backend package are accepted as control-background software QA. Across pole cutoffs 1e-3, 5e-4 and 2.5e-4, the independent profiles, radial constraint and all eight cap residuals reproduce the exact a_F=0 control background and agree with the primary representation at floating-point precision. No shooting Jacobian, root iteration, target solve or result artifact was produced; execution remains unauthorized.",
            "status": "ACTIVE",
            "reason": "The independent source does not import or wrap the primary residual and uses separate equations, higher pole series and x-space integration. Agreement on an analytic control background validates implementation consistency only and is not physical confirmation.",
            "sources": [IND_CONTRACT, DUAL_CONTRACT, AUDIT_RESULT, LEDGER, INDEPENDENT_SOURCE, DUAL_GATE, VALIDATOR, TESTS, "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.21.json", "project-manifest.json"],
            "evidence_effect": "DUAL_SOFTWARE_CONTROL_BACKGROUND_QA_ONLY",
            "supersedes": None
        }
        lines.append(json.dumps(entry, separators=(",", ":"), ensure_ascii=False))
    DECISIONS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sync_checkpoint() -> None:
    cp = json.loads(LATEST.read_text(encoding="utf-8"))
    if cp.get("checkpoint_id") != "UL-CHK-20260804-020":
        raise RuntimeError(f"unexpected checkpoint basis: {cp.get('checkpoint_id')}")
    cp["checkpoint_id"] = "UL-CHK-20260804-021"
    cp["timestamp"] = "2026-08-04T12:25:00+02:00"
    cp["basis_commit"] = MERGE_COMMIT
    cp["canonical_snapshot"] = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.21.json"
    cp["supersedes"] = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.20.json"
    for source in [IND_CONTRACT, DUAL_CONTRACT, AUDIT_RESULT, LEDGER, INDEPENDENT_SOURCE, DUAL_GATE, VALIDATOR, TESTS]:
        if source not in cp["sources"]:
            cp["sources"].append(source)
    cp["current_goal"] = "Perform a fail-closed CP01R1 execution-authorization review. The review may deny authorization and must not execute either backend."
    cp["current_workstream"] = "PRIMARY_C_PHYS_M1_BACKGROUND_3C3_EXECUTION_AUTHORIZATION_REVIEW_WITH_PARALLEL_C1_V_G1_2_DIAGNOSTIC"
    cp["current_workstreams"][0]["next_block"] = NEXT
    cp["governance_principle"] = "Dual-backend agreement on an analytic control background is software QA, not authorization, a target solution, continuum evidence, stability or physical confirmation."
    cp["gate_state"].update({
        "MD2S-R1-C-PHYS": "ACTIVE_EXECUTION_AUTHORIZATION_REVIEW_REMAINING",
        "R1.0": "ACTIVE_EXECUTION_AUTHORIZATION_REVIEW_REMAINING",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "BACKGROUND_RUN_INPUT": "FROZEN_CP01R1",
        "BACKGROUND_3C_PRIMARY_IMPLEMENTATION": "PASS_AUDITED_NO_EXECUTION",
        "BACKGROUND_3C_INDEPENDENT_BACKEND": "PASS_CONTROL_AUDIT_NO_ROOT_SOLVE",
        "BACKGROUND_3C_DUAL_BACKEND_PACKAGE": "PASS_AUDITED_NO_EXECUTION",
        "BACKGROUND_3C_EXECUTION": "NOT_AUTHORIZED",
        "BACKGROUND_SOLVER_IMPLEMENTATION": "DUAL_BACKEND_PRESENT_AUDITED_NO_EXECUTION",
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
    cp["verified_results"] = [x for x in cp.get("verified_results", []) if x.get("result_id") != "UL-RES-C-PHYS-M1-BG3C2-001"]
    cp["verified_results"].append({
        "result_id": "UL-RES-C-PHYS-M1-BG3C2-001",
        "statement": "A separately coded x-space backend reproduces the analytic a_F=0 control profiles, constraint and cap residuals across three pole cutoffs and agrees with the primary representation while performing no shooting Jacobian or root solve.",
        "status": "PASS_DUAL_BACKEND_CONTROL_AUDIT_NO_NONLINEAR_EXECUTION",
        "evidence_effect": "DUAL_SOFTWARE_CONTROL_BACKGROUND_QA_ONLY",
        "sources": [IND_CONTRACT, DUAL_CONTRACT, AUDIT_RESULT, LEDGER]
    })
    cp["open_blockers"] = [x for x in cp.get("open_blockers", []) if x.get("blocker_id") not in {
        "UL-BLK-C-PHYS-BACKGROUND-3C2-001", "UL-BLK-C-PHYS-BACKGROUND-3C3-001"
    }]
    cp["open_blockers"].insert(1, {
        "blocker_id": "UL-BLK-C-PHYS-BACKGROUND-3C3-001",
        "track_id": "MD2S-R1-C-PHYS",
        "statement": "No append-only execution authorization decision exists for CP01R1. A review must assess implementation, resource, artifact and scientific firewalls without executing either backend.",
        "sources": [DUAL_CONTRACT, AUDIT_RESULT]
    })
    cp["active_assumptions"] = [
        "CP01R1 remains the sole frozen run input.",
        "Primary and independent implementations have passed control-background audits only.",
        "The independent control integrations are not target-background solves.",
        "No shooting Jacobian, root iteration or result artifact exists.",
        "Execution remains unauthorized until a separate append-only decision."
    ]
    cp["forbidden_inferences"] = [
        "Do not interpret dual-backend control agreement as physical confirmation.",
        "Do not treat the control background as a target a_F=1/4 solution.",
        "Do not edit the existing denial artifact into a grant.",
        "Do not execute during authorization review.",
        "Do not infer continuum existence, trace rank, Fredholmness, stability, K1-D or K1-E."
    ]
    cp["entry_points"] = [IND_CONTRACT, DUAL_CONTRACT, AUDIT_RESULT, LEDGER, INDEPENDENT_SOURCE, DUAL_GATE]
    cp["next_exact_action"] = f"Execute {NEXT}: conduct a fail-closed authorization review only; do not run Newton, shooting root or create result artifacts."
    dump(SNAPSHOT, cp)
    dump(LATEST, cp)


if __name__ == "__main__":
    sync_manifest()
    sync_decision()
    sync_checkpoint()
