#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWER = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_rr4_review_v1.0.py"
REVIEW = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_RR4Review_v1.0.json"
RELEASE = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.3.json"
GRANT = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.3.json"

spec = importlib.util.spec_from_file_location("ulsh_wp2_rr4", REVIEWER)
assert spec and spec.loader
MOD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MOD)

result = MOD.audit()
assert result["status"] == "PASS_RR4_H3_RELEASE_READINESS_REPRODUCED_NO_SOLVE"
assert result["wp2_status"] == "CLOSED_RELEASE_READY_NO_EXECUTION"
assert result["new_release_blockers"] == {}
assert result["solver_calls"] == 0
assert result["physical_solve_authorized"] is False
assert result["physical_solve_executed"] is False
assert result["CP01R1"] == "NOT_EXECUTED"
assert result["K1-D"] == "NOT_RELEASED"
assert result["K1-E"] == "NOT_ADMISSIBLE"
assert result["physical_evidence_effect"] == "NONE"
assert all(result["RR3-B01"].values())
assert all(result["RR3-B02"].values())
assert all(result["future_release_binding"].values())
assert not RELEASE.exists()
assert not GRANT.exists()
review = json.loads(REVIEW.read_text(encoding="utf-8"))
assert review["wp2_completion"]["status"] == "CLOSED_RELEASE_READY_NO_EXECUTION"
assert review["next_allowed_action"] == "ULSH-01_WP3_SEPARATE_CP01R1_SINGLE_USE_RELEASE_DECISION"
print("PASS: WP2-RR4 independently verifies H3 release readiness without solve")
