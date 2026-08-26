#!/usr/bin/env python3
from __future__ import annotations

import fnmatch
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
C_PHYS = ROOT / "ulsh" / "ULSH-01" / "C-PHYS"
MANIFEST_PATH = C_PHYS / "2026-08-26_ULSH01_WP2_WP3_ReconciliationManifest_v0.1.json"
TARGET_PATH = C_PHYS / "2026-08-21_ULSH01_M1C1_8x8_TargetContract_v0.1.json"

manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
target = json.loads(TARGET_PATH.read_text(encoding="utf-8"))

canonical = json.dumps(
    target["target_semantics"],
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
).encode("utf-8")
actual_digest = hashlib.sha256(canonical).hexdigest()
expected_digest = manifest["authority"]["target_digest"]

assert actual_digest == expected_digest
assert target["target_contract_digest"]["sha256"] == expected_digest
assert manifest["authority"]["continuous_unknown_order"] == target["target_semantics"]["continuous_unknown_vector"]
assert manifest["authority"]["boundary_residual_order"] == target["target_semantics"]["boundary_operator"]["residual_order"]

patch = manifest["wp2_patch_binding"]
assert patch["representation"] == "a_chi_Sigma := a_chi_S(cap)"
assert patch["patch_residual"] == target["target_semantics"]["boundary_operator"]["patch"]["R_patch"]
assert patch["cap_combination"] == target["target_semantics"]["boundary_operator"]["cap_definitions"]["d_chi"]

rules = manifest["asset_classification_rules"]
allowed = {"COMPATIBLE_REBOUND", "DEVELOPMENT_ONLY", "INCOMPATIBLE", "SUPERSEDED_FOR_CANONICAL_TARGET"}
assert rules and all(rule["classification"] in allowed for rule in rules)

keywords = ("background3c5", "physical_response", "cphys_response")
candidates = []
for base in (C_PHYS, ROOT / ".github" / "workflows"):
    for path in base.iterdir():
        relative = path.relative_to(ROOT).as_posix()
        if any(keyword in path.name.lower() for keyword in keywords):
            candidates.append(relative)

unclassified = [
    path for path in candidates
    if not any(fnmatch.fnmatchcase(path, rule["glob"]) for rule in rules)
]
assert not unclassified, f"Unclassified WP2/WP3 assets: {unclassified}"

backend = manifest["canonical_8x8_backend"]
assert backend["status"] == "NOT_IMPLEMENTED_NOT_BOUND"
assert backend["compatible_rebound_assets"] == []

firewall = manifest["firewall"]
assert firewall["solver_authorized"] is False
assert firewall["physical_evidence_effect"] == "NONE"
assert firewall["physical_response_rank"] == "NOT_EXECUTED"
assert set(firewall["forbidden_fields_in_canonical_8x8_backend"]) == {"Sigma_FT", "c_N", "c_S"}
assert manifest["reconciliation_verdict"]["ULSH-01-WP4"] == "BLOCKED_NOT_AUTHORIZED"

print(f"WP2/WP3 reconciliation QA: PASS ({len(candidates)} assets classified)")
