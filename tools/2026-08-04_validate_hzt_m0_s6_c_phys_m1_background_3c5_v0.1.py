#!/usr/bin/env python3
"""Fail-closed validator for the Background-3C5 authorization review."""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C5ExecutionPackageAuthorizationReview_v0.1.json"
RUNNER = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_execution_runner_v0.1.py"
BG3C4_VALIDATOR = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3c4_v0.1.py"
GRANT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
ARTIFACT_ROOT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
EXPECTED_DIGEST = "f274333e6d0a94e9c4bedfe179e9781d7175e484dc70de5396aedee7872033cd"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def function_source_flags(path: Path) -> dict[str, bool]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    run_node = next(
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "run_authorized"
    )
    segment = ast.get_source_segment(source, run_node) or ""
    return {
        "verifies_grant": "GrantVerifier(digest).verify" in segment,
        "creates_result_skeleton": "build_result_skeleton" in segment,
        "explicitly_refuses_execution_release": "not an execution release" in segment,
        "calls_primary_adapter": "PrimaryRootAdapter" in segment,
        "calls_independent_adapter": "IndependentRootAdapter" in segment,
        "commits_atomic_writer": ".commit(" in segment,
        "uses_subprocess_resource_hook": "posix_preexec_fn" in segment,
        "uses_wall_clock_alarm": "wall_clock_alarm" in segment,
    }


def validate() -> dict:
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    package_result = load_module(BG3C4_VALIDATOR, "bg3c4_for_bg3c5").validate()
    flags = function_source_flags(RUNNER)

    assert package_result["status"] == "PASS"
    assert package_result["package_manifest_sha256"] == EXPECTED_DIGEST
    assert package_result["solver_calls"] == 0

    assert review["status"] == "DENIED_INTEGRATED_EXECUTION_RELEASE_INCOMPLETE"
    assert review["reviewed_package_manifest_sha256"] == EXPECTED_DIGEST
    assert review["authorization_decision"]["authorized"] is False
    assert review["authorization_decision"]["grant_artifact_created"] is False
    assert review["authorization_decision"]["primary_newton_allowed"] is False
    assert review["authorization_decision"]["independent_root_allowed"] is False
    assert review["solver_executed"] is False
    assert review["result_artifact_created"] is False
    assert review["physical_evidence_effect"] == "NONE"

    assert flags["verifies_grant"] is True
    assert flags["creates_result_skeleton"] is True
    assert flags["explicitly_refuses_execution_release"] is True
    assert flags["calls_primary_adapter"] is False
    assert flags["calls_independent_adapter"] is False
    assert flags["commits_atomic_writer"] is False
    assert flags["uses_subprocess_resource_hook"] is False
    assert flags["uses_wall_clock_alarm"] is False

    assert not GRANT.exists()
    assert not ARTIFACT_ROOT.exists()

    return {
        "status": "PASS",
        "review_status": review["status"],
        "reviewed_package_manifest_sha256": EXPECTED_DIGEST,
        "package_audit": "PASS",
        "integrated_execution_release": "INCOMPLETE",
        "grant_created": False,
        "solver_calls": 0,
        "result_artifact_created": False,
        "physical_evidence_effect": "NONE",
        "next_block": review["next_allowed_block"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate()
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else "PASS: Background-3C5 authorization denied fail-closed")


if __name__ == "__main__":
    main()
