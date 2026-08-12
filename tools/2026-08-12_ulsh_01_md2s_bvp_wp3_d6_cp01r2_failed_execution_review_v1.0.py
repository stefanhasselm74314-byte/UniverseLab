#!/usr/bin/env python3
"""ULSH-01 / WP3-D6 CP01R2 failed-execution review audit.

Stdlib-only. This audit never imports NumPy/SciPy, the physical target, or any
solver backend. It binds the preserved review record to the exact source bytes
that explain the observed post-schedule finalization failure.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6_CP01R2FailedExecutionReview_v1.0.json"
D4 = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D4_CP01R2ReleaseDecision_v1.0.json"
D5_TRIGGER = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D5_CP01R2ImmediateExecutionTrigger_v1.0.json"
D5_ISSUER = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d5_cp01r2_issue_and_execute_v1.0.py"
TARGET = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3h1_cp01r2_target_v1.0.py"
TRANSACTION_V11 = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3h1_cp01r2_transaction_v1.1.py"
TRANSACTION_V10 = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d3h1_cp01r2_transaction_v1.0.py"
LEGACY_FINALIZER = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_target_entrypoint_v1.1.py"
RUNTIME_RELEASE = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2_PhysicalSolveReleaseAuthorization_v1.0.json"
RUNTIME_GRANT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2_SingleUseExecutionGrant_v1.0.json"

EXPECTED = {
    str(D4.relative_to(ROOT)): "a50a9f44947e816d732320b832c4220b97e75b8f",
    str(D5_TRIGGER.relative_to(ROOT)): "6ef8c525358310e56bfe1f4948fa3653a3805085",
    str(D5_ISSUER.relative_to(ROOT)): "43499c27c983eddebb8254a117a01a63d8db9441",
    str(TARGET.relative_to(ROOT)): "199815ac9e4014cc0d68fde71d634cdac24516ce",
    str(TRANSACTION_V11.relative_to(ROOT)): "07d1532be17e5d5d81c96ad4438c3195ca4653aa",
    str(TRANSACTION_V10.relative_to(ROOT)): "315cfb4eae8c07efb66d264d66a601d5f888ce38",
    str(LEGACY_FINALIZER.relative_to(ROOT)): "304592405f843822e142110ba6a65fc845579489",
}

EXPECTED_STATUS = "BLOCKED_WP3_D6_CP01R2_RESULT_REVIEW_FINALIZATION_DEFECT_NO_REPLAY"
EXPECTED_RUN_ID = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2"
EXPECTED_ARTIFACT_SHA256 = "e34e11495707b4f96070e348148a80c7d045a53fa029f9a02798786dbc4335ba"
EXPECTED_GRANT_NONCE = "feff4d8455f0589ea72743db57eceb72"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"top-level JSON object required: {path}")
    return value


def git_blob_sha1(path: Path) -> str:
    completed = subprocess.run(
        ["git", "hash-object", str(path.relative_to(ROOT))],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def audit() -> dict[str, Any]:
    review = load_json(REVIEW)
    require(review.get("review_status") == EXPECTED_STATUS, "D6 review status mismatch")
    require(review.get("run_id") == EXPECTED_RUN_ID, "D6 run id mismatch")
    require(review.get("planned_entry_count") == 35, "D6 planned entry count mismatch")

    observed: dict[str, str] = {}
    for relative, expected in EXPECTED.items():
        path = ROOT / relative
        actual = git_blob_sha1(path)
        require(actual == expected, f"source drift: {relative}: {actual} != {expected}")
        observed[relative] = actual

    d4 = load_json(D4)
    require(d4.get("status") == "PASS_WP3_D4_CP01R2_SINGLE_USE_RELEASE_AUTHORIZED_NO_EXECUTION", "D4 decision no longer PASS")
    require(d4.get("decision_id") == "ULSH-01-WP3-D4-CP01R2-RELEASE-DEC-20260812-A", "D4 decision id drift")

    trigger = load_json(D5_TRIGGER)
    require(trigger.get("operator_intent") == "ISSUE_EXACT_CP01R2_RELEASE_AND_FRESH_SINGLE_USE_GRANT_AFTER_MANDATORY_RECHECK_THEN_START_CP01R2_IMMEDIATELY", "D5 operator intent drift")
    require(trigger.get("planned_entry_count") == 35, "D5 schedule size drift")

    execution = review["execution_record"]
    require(execution["github_actions_run_id"] == 31573154936, "reviewed workflow run id mismatch")
    require(execution["github_actions_job_id"] == 94039283759, "reviewed workflow job id mismatch")
    require(execution["workflow_conclusion"] == "failure", "workflow conclusion must be failure")
    require(execution["grant_nonce"] == EXPECTED_GRANT_NONCE, "spent grant nonce mismatch")
    require(execution["transaction_state"] == "FAILED", "transaction state mismatch")
    require(execution["result_package_committed"] is False, "failed run unexpectedly claims committed result")
    require(execution["verification_status"] == "NOT_COMMITTED", "failed run verification status mismatch")
    require(execution["replay_permitted"] is False, "spent grant replay must remain forbidden")

    artifact = review["preserved_actions_artifact"]
    require(artifact["artifact_id"] == 9132540539, "Actions artifact id mismatch")
    require(artifact["artifact_zip_sha256"] == EXPECTED_ARTIFACT_SHA256, "Actions artifact digest mismatch")
    hashes = artifact["artifact_file_sha256"]
    require(hashes["runtime_single_use_grant_json"] == "4f3217f1c26b79aba05641040fdf61eb54876aa93f6eab75fbe0e3810a0db0f3", "runtime grant hash mismatch")
    require(hashes["runtime_release_authorization_json"] == "9b077e73ed877625afea237b3c85a134e317d3258eb447ee75106fc2a39527f6", "runtime release hash mismatch")
    require(hashes["target_stderr_txt"] == "7e21448544a625dd76ad8518730fa18f2d72c4239e4710e25457fa9cf4ae5355", "target stderr hash mismatch")

    # Runtime authorization/grant were ephemeral Actions workspace artifacts. They
    # must not be committed into the canonical repository after the spent run.
    require(not RUNTIME_RELEASE.exists(), "spent runtime release artifact is committed in repository")
    require(not RUNTIME_GRANT.exists(), "spent runtime grant artifact is committed in repository")

    target_source = TARGET.read_text(encoding="utf-8")
    legacy_source = LEGACY_FINALIZER.read_text(encoding="utf-8")

    # Exact source bytes are pinned above. These fragment checks make the
    # compatibility defect explicit without importing or executing any solver.
    required_target_fragments = (
        'internal_states[(seed_index, node_count)] = state.copy()',
        'local_candidate = bool(result.get("converged")',
        'finalized = legacy._finalize(entries, internal_states, internal_details, independent_records, primary, model, sector, thresholds)',
    )
    for fragment in required_target_fragments:
        require(fragment in target_source, f"CP01R2 target semantic fragment missing: {fragment}")

    require('if n96_key in internal_states:' in legacy_source, "legacy finalizer internal-state branch missing")
    require('if has_n96_root:' in legacy_source, "legacy finalizer root branch missing")
    require('classification = (\n                    "NUMERICAL_CANDIDATE_BACKGROUND_DIAGNOSTIC"' in legacy_source, "legacy root classification assignment missing")
    require('classification = "NO_N96_ROOT"' in legacy_source, "legacy no-state classification assignment missing")
    require('"classification": classification' in legacy_source, "legacy unconditional classification consumption missing")

    findings = review["control_flow_findings"]
    require(findings["schedule_loop_reached_end_before_failure"] is True, "control-flow finding missing")
    require(findings["in_memory_matrix_entry_count_at_finalizer_entry"] == 35, "in-memory matrix count finding mismatch")
    require(findings["at_least_one_n96_terminal_state_without_local_root"] is True, "N96 non-root inference missing")
    require(findings["numerical_values_recoverable_from_preserved_artifact"] is False, "review must not claim numerical values are recoverable")
    require(findings["numerical_outcome_classification"] == "INDETERMINATE_UNPRESERVED_DUE_FINALIZATION_FAILURE", "numerical classification firewall mismatch")

    blockers = review["new_release_blockers"]
    require(set(blockers) == {"D6-B01", "D6-B02"}, "unexpected D6 blocker set")
    require(all(item.get("status") == "OPEN_RELEASE_BLOCKER" for item in blockers.values()), "D6 blockers are not open")

    disposition = review["grant_and_governance_disposition"]
    require(disposition["d4_single_use_execution_permission_consumed"] is True, "D4 single-use permission not marked consumed")
    require(disposition["runtime_grant_spent"] is True, "runtime grant not marked spent")
    require(disposition["runtime_grant_replay_permitted"] is False, "grant replay incorrectly permitted")
    require(disposition["fresh_execution_grant_permitted_now"] is False, "fresh grant incorrectly permitted before hardening")
    require(disposition["fresh_release_decision_required_after_hardening_and_independent_review"] is True, "fresh release decision requirement missing")
    require(disposition["WP4"] == "BLOCKED", "WP4 advanced")
    require(disposition["K1-D"] == "NOT_RELEASED", "K1-D advanced")
    require(disposition["K1-E"] == "NOT_ADMISSIBLE", "K1-E advanced")
    require(disposition["physical_evidence_effect"] == "NONE", "physical evidence effect changed")

    return {
        "status": EXPECTED_STATUS,
        "run_id": EXPECTED_RUN_ID,
        "exact_source_blobs_verified": len(observed),
        "workflow_run": 31573154936,
        "grant": "SPENT_NON_REPLAYABLE",
        "result_package": "NOT_COMMITTED",
        "root_cause": "CP01R2_PROGRESS_STATE_LEGACY_FINALIZER_CLASSIFICATION_GAP",
        "control_flow_35_entries": "REACHED_FINALIZER_NOT_DURABLY_PRESERVED",
        "numerical_outcome": "INDETERMINATE_UNPRESERVED",
        "release_blockers": ["D6-B01", "D6-B02"],
        "solver_calls_by_review": 0,
        "physical_evidence_effect": "NONE",
        "next_allowed_action": review["next_allowed_action"],
    }


def main() -> int:
    try:
        result = audit()
    except Exception as exc:
        print(json.dumps({"status": "D6_REVIEW_AUDIT_FAILED_CLOSED", "error": f"{type(exc).__name__}: {exc}"}, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
