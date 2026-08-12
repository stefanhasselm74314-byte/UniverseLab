#!/usr/bin/env python3
"""WP3-D8 static preflight regression. No numerical solve, no issuance."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ISSUER = ROOT / "tools/2026-08-12_ulsh_01_md2s_bvp_wp3_d8_cp01r2_issue_and_execute_v2.0.py"
RELEASE = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2_PhysicalSolveReleaseAuthorization_v2.0.json"
GRANT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D6H1_CP01R2_SingleUseExecutionGrant_v2.0.json"


def main() -> int:
    assert not RELEASE.exists(), "preflight must start without v2 release authorization"
    assert not GRANT.exists(), "preflight must start without v2 grant"
    proc = subprocess.run(
        [sys.executable, str(ISSUER), "--audit"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(f"D8 audit failed rc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    payload = json.loads(proc.stdout)
    assert payload["status"] == "PASS_WP3_D8_STATIC_AUDIT_ELIGIBLE_FOR_FRESH_RUNTIME_RECHECK_NO_EXECUTION"
    assert payload["d6_blockers"] == {"D6-B01": "VERIFIED_CLOSED", "D6-B02": "VERIFIED_CLOSED"}
    assert payload["planned_entry_count"] == 35
    assert payload["solver_calls"] == 0
    assert payload["physical_solve_executed"] is False
    assert payload["future_release_authorization_present"] is False
    assert payload["future_single_use_grant_present"] is False
    assert payload["physical_evidence_effect"] == "NONE"
    assert not RELEASE.exists(), "audit must not issue release authorization"
    assert not GRANT.exists(), "audit must not issue grant"
    print("PASS_WP3_D8_PREFLIGHT_NO_EXECUTION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
