#!/usr/bin/env python3
"""Validate the WP3-D7 CP01R2 fresh release decision without execution."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D7_CP01R2FreshReleaseDecision_v1.0.json"
D6R1 = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6R1_CP01R2IndependentReview_v1.0.json"
D6H1 = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2HardeningContract_v1.0.json"
FUTURE_RELEASE = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2_PhysicalSolveReleaseAuthorization_v2.0.json"
FUTURE_GRANT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2_SingleUseExecutionGrant_v2.0.json"
EXPECTED_STATUS = "PASS_WP3_D7_CP01R2_ELIGIBLE_FOR_FRESH_SINGLE_USE_RELEASE_ISSUANCE_NO_EXECUTION"
EXPECTED_RUN = "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2"
EXPECTED_PAYLOAD = "e8b8e82d2cb1472d91c387a40c8f84024c2549a3dcc2c897df5561f7bf721b36"
EXPECTED_SCHEDULE = "929f59d018cc511f36c98ef26a8614ed495fe699a067b1b33e6c5b53efaf8e0b"
EXPECTED_LOCK = "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: Path) -> str:
    rel = path.relative_to(ROOT)
    return subprocess.check_output(["git", "hash-object", str(rel)], cwd=ROOT, text=True).strip()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate() -> dict:
    d = load_json(DECISION)
    r = load_json(D6R1)
    h = load_json(D6H1)

    require(d.get("status") == EXPECTED_STATUS, "D7 status mismatch")
    require(d.get("baseline_main_commit") == "6db86509d55a0ee0e51c6cf52d32d4c6c522960a", "D7 baseline drift")
    require(d.get("run_id") == EXPECTED_RUN, "run id drift")
    require(d.get("run_payload_sha256") == EXPECTED_PAYLOAD, "payload drift")
    require(d.get("schedule_sha256") == EXPECTED_SCHEDULE, "schedule drift")
    require(d.get("dependency_lock_sha256") == EXPECTED_LOCK, "dependency lock drift")
    require(d.get("planned_entry_count") == 35, "schedule cardinality drift")

    require(r.get("review_status") == "PASS_WP3_D6R1_D6_BLOCKERS_VERIFIED_CLOSED_NO_EXECUTION", "D6R1 is not PASS")
    require(r.get("new_release_blockers") == [], "D6R1 has release blockers")
    disposition = r.get("D6_blocker_disposition", {})
    require(disposition.get("D6-B01", {}).get("status") == "VERIFIED_CLOSED", "D6-B01 not closed")
    require(disposition.get("D6-B02", {}).get("status") == "VERIFIED_CLOSED", "D6-B02 not closed")
    failed = r.get("failed_attempt_disposition", {})
    require(failed.get("d5_grant") == "SPENT_NON_REPLAYABLE", "old D5 grant disposition drift")
    require(failed.get("retrospective_reclassification_permitted") is False, "old result reclassification must remain forbidden")
    require(failed.get("rerun_of_actions_run_31573154936_permitted") is False, "old run must remain non-rerunnable")

    require(h.get("run_id") == EXPECTED_RUN and h.get("run_payload_sha256") == EXPECTED_PAYLOAD, "D6H1 run binding drift")
    require(h.get("schedule_sha256") == EXPECTED_SCHEDULE, "D6H1 schedule binding drift")
    require(h.get("dependency_lock_sha256") == EXPECTED_LOCK, "D6H1 dependency lock drift")

    for name, spec in d.get("review_basis", {}).items():
        path = ROOT / spec["path"]
        require(path.is_file(), f"missing review basis {name}")
        require(git_blob(path) == spec["git_blob_sha1"], f"review basis blob drift: {name}")
    for name, spec in d.get("source_bindings", {}).items():
        path = ROOT / spec["path"]
        require(path.is_file(), f"missing source binding {name}")
        require(git_blob(path) == spec["git_blob_sha1"], f"source binding blob drift: {name}")

    decision = d.get("decision", {})
    require(decision.get("eligible_for_fresh_release_issuance") is True, "fresh issuance eligibility not granted")
    require(decision.get("execution_in_this_work_package") is False, "D7 may not execute")
    require(decision.get("runtime_release_authorization_issued_in_this_work_package") is False, "D7 may not issue release")
    require(decision.get("runtime_single_use_grant_issued_in_this_work_package") is False, "D7 may not issue grant")
    require(decision.get("fresh_runtime_recheck_required_immediately_before_issuance") is True, "fresh runtime recheck missing")
    require(decision.get("grant_replay_permitted") is False, "grant replay must be forbidden")
    for forbidden_flag in ("parallel_execution", "adaptive_retry", "parameter_or_topology_mutation", "method_or_threshold_relaxation", "branch_scan", "fallback_method", "old_grant_reuse", "failed_attempt_result_reclassification"):
        require(decision.get(forbidden_flag) is False, f"forbidden decision flag enabled: {forbidden_flag}")

    frozen = d.get("frozen_scientific_scope", {})
    require(frozen.get("seeds") == 7 and frozen.get("node_counts") == [24, 32, 48, 64, 96] and frozen.get("schedule_entries") == 35, "frozen schedule scope drift")
    require(frozen.get("a_F") == "1/4", "a_F drift")

    firewall = d.get("no_execution_firewall", {})
    require(not FUTURE_RELEASE.exists() and not FUTURE_GRANT.exists(), "future runtime release/grant must remain absent in D7")
    require(firewall.get("future_release_authorization_present") is False, "firewall release mismatch")
    require(firewall.get("future_single_use_grant_present") is False, "firewall grant mismatch")
    require(firewall.get("physical_solve_executed") is False, "D7 executed solver")
    require(firewall.get("audit_solver_calls") == 0, "D7 solver call count nonzero")
    require(firewall.get("physical_evidence_effect") == "NONE", "D7 evidence firewall mismatch")
    require("numpy" not in sys.modules and "scipy" not in sys.modules, "numerical backend imported by D7 validator")

    governance = d.get("governance_after_decision", {})
    require(governance.get("WP4") == "BLOCKED", "WP4 advanced improperly")
    require(governance.get("K1-D") == "NOT_RELEASED", "K1-D advanced improperly")
    require(governance.get("K1-E") == "NOT_ADMISSIBLE", "K1-E advanced improperly")
    require(governance.get("physical_evidence_effect") == "NONE", "evidence effect advanced improperly")

    return {
        "status": EXPECTED_STATUS,
        "decision_id": d["decision_id"],
        "run_id": EXPECTED_RUN,
        "release_blockers": [],
        "fresh_runtime_recheck_required": True,
        "future_release_authorization_present": False,
        "future_single_use_grant_present": False,
        "solver_calls": 0,
        "physical_solve_executed": False,
        "physical_evidence_effect": "NONE",
        "decision_sha256": hashlib.sha256(DECISION.read_bytes()).hexdigest()
    }


def main() -> int:
    try:
        print(json.dumps(validate(), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "BLOCKED_WP3_D7_CP01R2_FRESH_RELEASE_DECISION", "error": f"{type(exc).__name__}: {exc}"}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
