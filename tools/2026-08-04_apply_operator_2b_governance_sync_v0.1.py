#!/usr/bin/env python3
"""Synchronize Operator-2B governance pointers with checkpoint v1.15.

The scientific Operator-2B state is already frozen. This migration is limited
to provenance and canonical pointer hygiene:

- project-manifest.json -> checkpoint snapshot v1.15
- registry/session-checkpoint-latest.json -> byte-identical v1.15 alias
- registry/decision-log.jsonl -> verify append-only UL-DEC-0022

It never changes equations, scientific claims, evidence effects or release gates.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "project-manifest.json"
CHECKPOINT_ALIAS = ROOT / "registry/session-checkpoint-latest.json"
CHECKPOINT_V115 = ROOT / "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.15.json"
DECISION_LOG = ROOT / "registry/decision-log.jsonl"

REQUIRED = [
    ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceContract_v0.1.json",
    ROOT / "registry/2026-08-04_UniverseLab_C_PHYS_M1_Operator2B_Status_v0.1.json",
    ROOT / "registry/2026-08-04_UniverseLab_ClaimRegister_C_PHYS_M1_Operator2B_v0.1.json",
    ROOT / "science/hzt-m0/md2s/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceLedger_v0.1.md",
    ROOT / "tools/2026-08-04_validate_g0_three_track_sync_v1.6.py",
    ROOT / "tests/2026-08-04_test_g0_three_track_sync_v1.6.py",
    CHECKPOINT_V115,
]


class SyncError(RuntimeError):
    """Raised when the narrow synchronization cannot proceed safely."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SyncError(message)


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing required file: {path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SyncError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root must be object: {path.relative_to(ROOT)}")
    return value


def validate_basis_commit(commit: Any) -> None:
    require(
        isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit) is not None,
        "checkpoint v1.15 basis_commit must be a lowercase 40-character SHA-1",
    )
    if (ROOT / ".git").exists():
        result = subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "-e", f"{commit}^{{commit}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        require(result.returncode == 0, f"checkpoint v1.15 basis_commit is absent: {commit}")


def validate_checkpoint_v115() -> str:
    checkpoint = read_json(CHECKPOINT_V115)
    require(checkpoint.get("checkpoint_id") == "UL-CHK-20260804-015", "checkpoint v1.15 id drift")
    require(
        checkpoint.get("canonical_snapshot")
        == "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.15.json",
        "checkpoint v1.15 canonical path drift",
    )
    require(
        checkpoint.get("supersedes")
        == "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.14.json",
        "checkpoint v1.15 supersedes drift",
    )
    correction = checkpoint.get("provenance_correction")
    require(isinstance(correction, dict), "checkpoint v1.15 provenance correction missing")
    require(correction.get("scientific_state_changed") is False, "scientific-state correction overclaim")
    require(correction.get("gate_state_changed") is False, "gate-state correction overclaim")
    require(
        correction.get("evidence_effect") == "GOVERNANCE_PROVENANCE_ONLY",
        "checkpoint v1.15 correction evidence drift",
    )
    validate_basis_commit(checkpoint.get("basis_commit"))

    gates = checkpoint.get("gate_state", {})
    expected = {
        "OPERATOR_2B": "PASS_FORMAL_FUNCTION_SPACE_AND_TRACE_TEMPLATE",
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
    }
    for key, value in expected.items():
        require(gates.get(key) == value, f"checkpoint v1.15 gate drift: {key}")
    return CHECKPOINT_V115.read_text(encoding="utf-8")


def update_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    require(manifest.get("schema") == "universelab.project-manifest.v1", "manifest schema drift")
    require(
        manifest.get("release") == "2.7-c-phys-m1-operator-2b-v0.1",
        "manifest must already represent Operator-2B release 2.7",
    )
    gates = manifest.get("gates", {})
    expected = {
        "OPERATOR_2B": "PASS_FORMAL_FUNCTION_SPACE_AND_TRACE_TEMPLATE",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
        "FULL_LINEARIZED_BOUNDARY_TRACE_RANK": "NOT_PROVEN",
        "FREDHOLM_PROPERTY": "NOT_PROVEN",
        "CONTINUUM_BVP_JACOBIAN": "NOT_PROVEN",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "official_MD2S_solver": "NOT_AUTHORIZED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected.items():
        require(gates.get(key) == value, f"manifest gate drift: {key}")

    registries = manifest.get("central_registries")
    require(isinstance(registries, dict), "manifest central_registries missing")
    registries["session_checkpoint_snapshot"] = (
        "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.15.json"
    )
    return manifest


def validate_decision_log() -> str:
    require(DECISION_LOG.is_file(), "missing decision log")
    text = DECISION_LOG.read_text(encoding="utf-8")
    entries = [json.loads(line) for line in text.splitlines() if line.strip()]
    ids = [item.get("decision_id") for item in entries]
    require(len(ids) == len(set(ids)), "duplicate decision ids")
    require(ids and ids[-1] == "UL-DEC-0022", "decision log must end at UL-DEC-0022")
    decision = entries[-1]
    require(decision.get("status") == "ACTIVE", "UL-DEC-0022 must remain active")
    require(
        decision.get("evidence_effect") == "FORMAL_FUNCTIONAL_ANALYTIC_STRUCTURE_ONLY",
        "UL-DEC-0022 evidence drift",
    )
    require(decision.get("supersedes") is None, "UL-DEC-0022 must remain additive")
    return text


def expected_outputs() -> dict[Path, str]:
    for path in REQUIRED:
        require(path.is_file(), f"missing merged Operator-2B artifact: {path.relative_to(ROOT)}")
    checkpoint_text = validate_checkpoint_v115()
    manifest = update_manifest(read_json(MANIFEST))
    decision_text = validate_decision_log()
    return {
        MANIFEST: json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        CHECKPOINT_ALIAS: checkpoint_text,
        DECISION_LOG: decision_text,
    }


def apply(*, check_only: bool) -> list[str]:
    changed: list[str] = []
    for path, expected in expected_outputs().items():
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current != expected:
            changed.append(str(path.relative_to(ROOT)))
            if not check_only:
                path.write_text(expected, encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        changed = apply(check_only=args.check)
    except (SyncError, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1
    if args.check and changed:
        print("FAIL: governance drift remains:")
        for path in changed:
            print(f"- {path}")
        return 1
    if args.apply:
        print("Updated:" if changed else "No changes required.")
        for path in changed:
            print(f"- {path}")
    else:
        print("PASS: Operator-2B governance pointers are synchronized to checkpoint v1.15")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
