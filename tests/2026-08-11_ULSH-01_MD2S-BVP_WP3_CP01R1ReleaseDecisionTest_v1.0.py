#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDITOR = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp3_release_decision_v1.0.py"
DECISION = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP3_CP01R1ReleaseDecision_v1.0.json"
RELEASE = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.3.json"
GRANT = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.3.json"
H3_TX = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.4.py"

spec = importlib.util.spec_from_file_location("ulsh_wp3_release_decision", AUDITOR)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

result = module.audit()
assert result["status"] == "PASS_WP3_CP01R1_RELEASE_DECISION_ELIGIBLE_NO_GRANT_NO_SOLVE"
assert result["schedule"] == {"seed_count": 7, "node_counts": [24, 32, 48, 64, 96], "planned_entries": 35}
assert result["release_authorization_present"] is False
assert result["single_use_grant_present"] is False
assert result["solver_calls"] == 0
assert result["physical_solve_authorized"] is False
assert result["physical_solve_executed"] is False
assert result["CP01R1"] == "NOT_EXECUTED"
assert result["K1-D"] == "NOT_RELEASED"
assert result["K1-E"] == "NOT_ADMISSIBLE"
assert result["physical_evidence_effect"] == "NONE"
assert not RELEASE.exists()
assert not GRANT.exists()

decision = json.loads(DECISION.read_text(encoding="utf-8"))
assert decision["decision_status"] == "PASS_ELIGIBLE_FOR_EXACT_H3_SINGLE_USE_RELEASE_ISSUANCE_NO_EXECUTION"
assert decision["release_decision"]["eligible_to_issue_exact_h3_release_authorization"] is True
assert decision["release_decision"]["eligible_to_issue_exact_h3_single_use_grant"] is True
assert decision["release_decision"]["release_authorization_created_by_this_decision"] is False
assert decision["release_decision"]["single_use_grant_created_by_this_decision"] is False
assert decision["decision_boundary"]["this_decision_is_not_a_release_authorization"] is True
assert decision["decision_boundary"]["this_decision_is_not_a_single_use_grant"] is True
assert decision["next_allowed_action"] == "ULSH-01_WP3_ISSUE_EXACT_H3_RELEASE_AUTHORIZATION_AND_SINGLE_USE_GRANT_FOR_IMMEDIATE_CP01R1_TRANSACTION"

source = H3_TX.read_text(encoding="utf-8")
assert "validate_h3_release_and_grant" in source
assert "physical_solve_authorized" in source
assert "single_use" in source

print("PASS: WP3 approves only later exact single-use issuance; no release, grant, or solve occurred")
