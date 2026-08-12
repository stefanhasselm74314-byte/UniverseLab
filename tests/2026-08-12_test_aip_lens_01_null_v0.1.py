#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-08-12_UniverseLab_AIP-LENS-01-NULL_Contract_v0.1.json"
VALIDATOR = ROOT / "tools/2026-08-12_validate_aip_lens_01_null_v0.1.py"
PROTOCOL = ROOT / "science/ai-for-physics/2026-08-12_UniverseLab_AIP-LENS-01-NULL_Protocol_v0.1.md"
WORKFLOW = ROOT / ".github/workflows/2026-08-12_UniverseLab_AIP-LENS-01-NULL_v0.1.yml"


def test_contract_invariants() -> None:
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert data["status"] == "PILOT_PROTOCOL_FROZEN_NOT_EXECUTED"
    assert data["targets"]["required"] == ["Omega_m", "S8"]
    assert data["targets"]["hzt_parameters_allowed"] is False
    assert data["stages"]["N1"]["status"].startswith("NOT_AUTHORIZED")
    assert data["stages"]["N2"]["status"] == "BLOCKED_UNTIL_N1_PASS"
    assert data["gate_state"]["AIP-G0"] == "FROZEN_BY_PROTOCOL"
    assert data["gate_state"]["AIP-G7"] == "SEPARATE_REVIEW_REQUIRED"
    assert data["governance_firewall"]["physical_evidence_effect"] == "NONE"
    assert data["governance_firewall"]["K1-D"] == "NOT_RELEASED"
    assert data["governance_firewall"]["K1-E"] == "NOT_ADMISSIBLE"


def test_protocol_is_nonexecuting() -> None:
    text = PROTOCOL.read_text(encoding="utf-8").lower()
    for forbidden in ["model.fit(", "optimizer.step(", "torch.", "tensorflow", "jax."]:
        assert forbidden not in text
    assert "aip-lens-01-null-n1" in text
    assert "largest model -> best score" in text


def test_workflow_is_validation_only() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "validate_aip_lens_01_null_v0.1.py" in text
    assert "test_aip_lens_01_null_v0.1.py" in text
    for forbidden in ["pip install torch", "pip install tensorflow", "model.fit", "--execute", "workflow_dispatch:"]:
        assert forbidden not in text


def test_validator_passes() -> None:
    result = subprocess.run([sys.executable, str(VALIDATOR)], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS:" in result.stdout


if __name__ == "__main__":
    test_contract_invariants()
    test_protocol_is_nonexecuting()
    test_workflow_is_validation_only()
    test_validator_passes()
    print("PASS: AIP-LENS-01-NULL regression suite")
