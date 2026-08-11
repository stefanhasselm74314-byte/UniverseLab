#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TX_PATH = ROOT / "tools/2026-08-11_ulsh_01_md2s_bvp_wp2_transaction_v1.4.py"
CONTRACT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_H3Contract_v1.0.json"
RELEASE_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_PhysicalSolveReleaseAuthorization_v1.3.json"
GRANT_PATH = ROOT / "registry/2026-08-11_ULSH-01_MD2S-BVP_WP2_SingleUseExecutionGrant_v1.3.json"

spec = importlib.util.spec_from_file_location("ulsh_wp2_h3_tx", TX_PATH)
assert spec and spec.loader
TX = importlib.util.module_from_spec(spec)
spec.loader.exec_module(TX)

contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
assert contract["status"] == "PASS_WP2_H3_IMPLEMENTED_NO_SOLVE_PENDING_RR4"
assert contract["rr3_blocker_closure"]["RR3-B01"]["status"] == "IMPLEMENTED_PENDING_RR4"
assert contract["rr3_blocker_closure"]["RR3-B02"]["status"] == "IMPLEMENTED_PENDING_RR4"
assert contract["physical_solve_authorized"] is False
assert contract["physical_solve_executed"] is False
assert contract["physical_evidence_effect"] == "NONE"
assert not RELEASE_PATH.exists()
assert not GRANT_PATH.exists()

# RR3-B01: representative no-candidate, partial, rejected-root and singular-diagnostic sentinels.
raw = {
    "final_classification": "NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL",
    "acceptance_audit": {
        "per_seed": [
            {"classification": "NO_N96_ROOT", "fine_pair_profile_difference": math.inf},
            {"classification": "NUMERICAL_ROOT_REJECTED_BY_QA", "independent_backend_distance": math.inf},
        ]
    },
    "primary_backend": {"condition_estimates": [{"value": math.inf, "label": "DISCRETE_DIAGNOSTIC"}]},
    "candidate_inventory": [{"classification": "NUMERICAL_ROOT_REJECTED_BY_QA", "admissibility_gates": {"Y_sigma": -math.inf}}],
    "matrix_entries": [{"status": "PARTIAL", "diagnostic": float("nan")}],
}
safe = TX.sanitize_raw_result_for_immutable_json(raw)
json.dumps(safe, allow_nan=False)
replacements = safe["acceptance_audit"]["json_safe_nonfinite_replacements"]
assert len(replacements) == 5, replacements
assert all(item["replacement"] == "null" for item in replacements)
assert all("NOT_A_FINITE_MEASUREMENT" in item["reason"] for item in replacements)
assert TX._walk_nonfinite(safe) == []
assert safe["acceptance_audit"]["per_seed"][0]["fine_pair_profile_difference"] is None
assert safe["candidate_inventory"][0]["admissibility_gates"]["Y_sigma"] is None

# RR3-B02: deterministic commit-awareness and exact hash verification.
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    result_dir = root / "result"
    absent = TX.inspect_committed_result(result_dir, None)
    assert absent["result_package_committed"] is False
    assert absent["verification_status"] == "NOT_COMMITTED"

    result_dir.mkdir()
    (result_dir / "result.json").write_text('{"ok":true}\n', encoding="utf-8")
    (result_dir / "artifact-manifest.json").write_text('{"manifest":true}\n', encoding="utf-8")
    expected = {
        "result_sha256": sha256(result_dir / "result.json"),
        "artifact_manifest_sha256": sha256(result_dir / "artifact-manifest.json"),
    }
    committed = TX.inspect_committed_result(result_dir, expected)
    assert committed["result_package_committed"] is True
    assert committed["verification_status"] == "COMMITTED_HASHES_MATCH_PRECOMMIT_PACKAGE"
    mismatch = TX.inspect_committed_result(result_dir, {"result_sha256": "0" * 64, "artifact_manifest_sha256": "0" * 64})
    assert mismatch["verification_status"] == "COMMITTED_HASH_MISMATCH_INDETERMINATE"

source = TX_PATH.read_text(encoding="utf-8")
execute = source[source.index("def execute(transaction_root"):]
assert execute.index('mark_state(grant_dir, "COMMITTING_RESULT"') < execute.index("os.replace(staging, result_dir)")
assert execute.index("os.replace(staging, result_dir)") < execute.index('grant_dir / "result-commit.json"')
assert execute.index('grant_dir / "result-commit.json"') < execute.index('mark_state(grant_dir, "SUCCEEDED"')
assert 'durable_state = "COMMITTED_INDETERMINATE" if committed else' in execute
assert '"result_package_committed": committed' in execute
assert 'replay_permitted=False' in execute
assert "result_dir.exists()" not in execute  # helper uses is_dir() and exact hash verification instead.

preflight = TX.static_preflight()
assert preflight["status"] == "PASS_WP2_H3_STATIC_PREFLIGHT_NO_SOLVE_PENDING_RR4"
assert preflight["solver_calls"] == 0
assert preflight["physical_solve_authorized"] is False
assert preflight["physical_solve_executed"] is False
assert preflight["physical_evidence_effect"] == "NONE"

print("PASS: ULSH-01 WP2-H3 closes RR3-B01/RR3-B02 in no-solve scope; RR4 remains required")
