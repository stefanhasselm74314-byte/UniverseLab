#!/usr/bin/env python3
"""Canonical G0 validator v1.12 for audited Background-3C primary implementation."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.20.json"
PRIMARY_VALIDATOR = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3c_v0.2.py"
AUDIT_RESULT = "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CPrimaryImplementationAuditResult_v0.1.json"
NEXT = "C-PHYS-R1.0-BACKGROUND-3C2_INDEPENDENT_BACKEND_AND_EXECUTION_PACKAGE"
FUTURE_GRANT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
OUTPUT_ROOT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"


class ContractError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def load_json(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    require(path.is_file(), f"missing JSON: {relative}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {relative}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root must be object: {relative}")
    return value


def load_primary_validator():
    spec = importlib.util.spec_from_file_location("background3c_primary_validator_for_g0_v112", PRIMARY_VALIDATOR)
    if spec is None or spec.loader is None:
        raise ContractError("unable to import Background-3C primary validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_manifest(manifest: dict[str, Any]) -> dict[str, str]:
    require(manifest["release"] == "2.12-c-phys-m1-background-3c-primary-audited-v0.2", "release drift")
    tracks = manifest["architecture"]["research_tracks"]
    require([item["id"] for item in tracks] == ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"], "track drift")
    require(tracks[1]["status"] == "ACTIVE_INDEPENDENT_BACKEND_AND_EXECUTION_PACKAGE_REMAINING", "physical track status drift")
    expected = {
        "R1.0": "ACTIVE_INDEPENDENT_BACKEND_AND_EXECUTION_PACKAGE_REMAINING",
        "R1.1": "BLOCKED",
        "R1.2": "BLOCKED",
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
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected.items():
        require(manifest["gates"].get(key) == value, f"manifest gate drift: {key}")
    bg = manifest["c_phys_background_3c"]
    require(bg["status"] == "PRIMARY_IMPLEMENTATION_PASS_AUDITED_NO_EXECUTION", "Background-3C status drift")
    require(bg["primary_audit_status"] == "PASS_PRIMARY_IMPLEMENTATION_AUDIT_NO_SOLVER_EXECUTION", "primary audit status drift")
    require(bg["audit_newton_call_count"] == 0, "Newton execution overclaim")
    require(bg["run_command_exit_code"] == 73 and bg["direct_kernel_exit_code"] == 73, "exit-73 firewall drift")
    require(bg["authorization"] == "NOT_GRANTED" and bg["future_grant_present"] is False, "authorization drift")
    require(bg["independent_backend"] == "NOT_PRESENT_BLOCKING", "independent backend overclaim")
    require(bg["result_artifact_created"] is False and bg["solver_executed"] is False, "result or execution overclaim")
    require(bg["next_block"] == NEXT, "next block drift")
    require(manifest["central_registries"]["session_checkpoint_snapshot"] == CHECKPOINT, "checkpoint pointer drift")
    require(manifest["workstream_priority"][0] == f"MD2S-R1-C-PHYS:{NEXT}", "workstream priority drift")
    return expected


def validate_checkpoint(checkpoint: dict[str, Any]) -> dict[str, str]:
    require(checkpoint["checkpoint_id"] == "UL-CHK-20260804-020", "checkpoint id drift")
    require(checkpoint["canonical_snapshot"] == CHECKPOINT, "checkpoint snapshot drift")
    require(checkpoint["supersedes"] == "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.19.json", "checkpoint supersedes drift")
    basis = checkpoint.get("basis_commit")
    require(isinstance(basis, str) and re.fullmatch(r"[0-9a-f]{40}", basis), "checkpoint basis format drift")
    if (ROOT / ".git").exists():
        result = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{basis}^{{commit}}"], capture_output=True, text=True, check=False)
        require(result.returncode == 0, f"checkpoint basis commit absent: {basis}")
    expected = {
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
        "PHYSICAL_EVIDENCE_EFFECT": "NONE",
    }
    for key, value in expected.items():
        require(checkpoint["gate_state"].get(key) == value, f"checkpoint gate drift: {key}")
    require(checkpoint["current_workstreams"][0]["next_block"] == NEXT, "checkpoint next block drift")
    return expected


def validate_alias() -> dict[str, Any]:
    latest = load_json("registry/session-checkpoint-latest.json")
    path = PurePosixPath(latest["canonical_snapshot"])
    require(not path.is_absolute() and ".." not in path.parts, "checkpoint path escape")
    dated = load_json(CHECKPOINT)
    require(latest == dated, "checkpoint alias mismatch")
    return latest


def validate_decision() -> str:
    lines = [line for line in (ROOT / "registry/decision-log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    decisions = [json.loads(line) for line in lines]
    ids = [item["decision_id"] for item in decisions]
    require(len(ids) == len(set(ids)), "duplicate decision ids")
    numeric = []
    for decision_id in ids:
        match = re.fullmatch(r"UL-DEC-(\d{4})", decision_id)
        require(match is not None, f"invalid decision id: {decision_id}")
        numeric.append(int(match.group(1)))
    require(numeric == sorted(numeric), "decision order drift")
    require(ids[-1] == "UL-DEC-0027", "Background-3C primary decision must be latest")
    latest = decisions[-1]
    require(latest["status"] == "ACTIVE", "decision status drift")
    require(latest["evidence_effect"] == "SOFTWARE_IMPLEMENTATION_AND_ALGEBRA_QA_ONLY", "decision evidence drift")
    require(latest["supersedes"] is None, "decision must remain additive")
    return latest["decision_id"]


def validate() -> dict[str, Any]:
    primary = load_primary_validator().validate()
    require(primary["status"] == "PASS", "primary implementation revalidation failed")
    require(primary["audit"]["newton_call_count"] == 0, "Newton executed during G0 validation")
    audit_result = load_json(AUDIT_RESULT)
    require(audit_result["status"] == "PASS_PRIMARY_IMPLEMENTATION_AUDIT_NO_SOLVER_EXECUTION", "recorded audit result drift")
    require(audit_result["firewall_tests"]["solver_executed"] is False, "recorded solver execution overclaim")
    require(audit_result["independent_backend_status"] == "NOT_PRESENT_BLOCKING", "recorded independent backend overclaim")
    require(not FUTURE_GRANT.exists(), "unexpected v0.2 grant present")
    require(not OUTPUT_ROOT.exists(), "unexpected Background-3C result directory present")
    manifest = load_json("project-manifest.json")
    checkpoint = validate_alias()
    return {
        "contract": "G0_BACKGROUND_3C_PRIMARY_AUDITED_V1_12",
        "status": "PASS",
        "primary_implementation": primary["audit"]["status"],
        "newton_call_count": primary["audit"]["newton_call_count"],
        "manifest_gates": validate_manifest(manifest),
        "checkpoint_gates": validate_checkpoint(checkpoint),
        "decision": validate_decision(),
        "independent_backend": "NOT_PRESENT_BLOCKING",
        "execution_authorized": False,
        "result_artifact_created": False,
        "physical_evidence_effect": "NONE",
        "next_block": NEXT,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = validate()
    except (ContractError, RuntimeError, ValueError, KeyError, FloatingPointError) as exc:
        payload = {"status": "FAIL", "error": str(exc), "execution_authorized": False}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"FAIL: {exc}")
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else "PASS: G0 synchronized through Background-3C primary audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
