#!/usr/bin/env python3
"""Regression checks for UL-AIP v0.1."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry/2026-08-12_UniverseLab_AIForPhysicsFramework_v0.1.json"
VALIDATOR = ROOT / "tools/2026-08-12_validate_ul_aip_framework_v0.1.py"
WORKFLOW = ROOT / ".github/workflows/2026-08-12_UniverseLab_AIForPhysicsFramework_v0.1.yml"


def main() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))

    assert data["framework_id"] == "UL-AIP-v0.1"
    assert data["status"] == "METHODS_FRAMEWORK_DEFINED_NOT_RELEASED"
    assert len(data["modules"]) == 7
    assert len(data["gates"]) == 8
    assert data["pilot_sequence"][0] == "AIP-LENS-01-NULL"
    assert data["modules"]["AIP-ANOM"]["required_state_space"] == [
        "BASELINE",
        "CANDIDATE",
        "NEITHER_OR_OOD",
    ]

    firewall = data["governance_firewall"]
    assert firewall == {
        "model_training": False,
        "model_execution": False,
        "solver_state_modified": False,
        "likelihood_modified": False,
        "physical_parameters_modified": False,
        "topology_modified": False,
        "WP4": "BLOCKED",
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "physical_evidence_effect": "NONE",
    }

    forbidden = " ".join(data["forbidden_promotions"])
    assert "NO_DIRECT_ML_OUTPUT_TO_PHYSICAL_EVIDENCE" in forbidden
    assert "NO_SYNTHETIC_CLASSIFIER_SCORE_AS_HZT_CONFIRMATION" in forbidden

    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "python tools/2026-08-12_validate_ul_aip_framework_v0.1.py" in workflow
    assert "python tests/2026-08-12_test_ul_aip_framework_v0.1.py" in workflow
    assert "workflow_dispatch" not in workflow
    assert "schedule:" not in workflow

    completed = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "validation PASS" in completed.stdout

    print("UL-AIP v0.1 regression PASS")


if __name__ == "__main__":
    main()
