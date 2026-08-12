#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registry/2026-08-12_UniverseLab_AIP-LENS-01-NULL_Contract_v0.1.json"
PROTOCOL = ROOT / "science/ai-for-physics/2026-08-12_UniverseLab_AIP-LENS-01-NULL_Protocol_v0.1.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    require(CONTRACT.is_file(), f"missing contract: {CONTRACT}")
    require(PROTOCOL.is_file(), f"missing protocol: {PROTOCOL}")

    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    text = PROTOCOL.read_text(encoding="utf-8")

    require(data["schema"] == "universelab.ai-for-physics.aip-lens-01-null.contract.v1", "schema mismatch")
    require(data["pilot_id"] == "AIP-LENS-01-NULL", "pilot id mismatch")
    require(data["parent_framework"] == "UL-AIP-v0.1", "parent framework mismatch")
    require(data["status"] == "PILOT_PROTOCOL_FROZEN_NOT_EXECUTED", "status must remain non-executed")

    targets = data["targets"]
    require(targets["required"] == ["Omega_m", "S8"], "required target set drift")
    require(targets["hzt_parameters_allowed"] is False, "HZT parameters are forbidden in null pilot")

    stages = data["stages"]
    require(stages["N0"]["status"] == "AUTHORIZED_BY_THIS_CONTRACT", "N0 must be the only authorized stage")
    require(stages["N1"]["status"] == "NOT_AUTHORIZED_REQUIRES_SEPARATE_EXECUTABLE_CONTRACT", "N1 must remain not authorized")
    require(stages["N2"]["status"] == "BLOCKED_UNTIL_N1_PASS", "N2 must remain blocked")

    expected_partitions = {"TRAIN", "VALIDATION", "CALIBRATION", "FINAL_TEST", "OOD_STRESS"}
    require(set(data["required_partitions"]) == expected_partitions, "partition contract incomplete")

    split = data["split_firewall"]
    require(all(value is False for value in split.values()), "split firewall must fail closed")

    gates = data["gate_state"]
    require(gates["AIP-G0"] == "FROZEN_BY_PROTOCOL", "G0 not frozen")
    for gate in ["AIP-G1", "AIP-G2", "AIP-G3", "AIP-G4", "AIP-G5", "AIP-G6"]:
        require(gates[gate] == "REQUIREMENTS_DEFINED_NOT_PASSED", f"{gate} must not be pre-passed")
    require(gates["AIP-G7"] == "SEPARATE_REVIEW_REQUIRED", "G7 must remain separate")

    firewall = data["governance_firewall"]
    for field in [
        "model_training",
        "model_execution",
        "hzt_comparison",
        "solver_state_modified",
        "likelihood_modified",
        "physical_parameters_modified",
        "topology_modified",
    ]:
        require(firewall[field] is False, f"firewall field {field} must be false")
    require(firewall["WP4"] == "BLOCKED", "WP4 drift")
    require(firewall["K1-D"] == "NOT_RELEASED", "K1-D drift")
    require(firewall["K1-E"] == "NOT_ADMISSIBLE", "K1-E drift")
    require(firewall["physical_evidence_effect"] == "NONE", "evidence firewall drift")

    required_protocol_tokens = [
        "PILOT_PROTOCOL_FROZEN_NOT_EXECUTED",
        "AIP-LENS-01-NULL-N1",
        "Omega_m",
        "S8 = sigma8 * sqrt(Omega_m / 0.3)",
        "AIP-G0",
        "AIP-G7",
        "train/test leakage",
        "simulator fingerprint",
        "WP4 = BLOCKED",
        "K1-D = NOT_RELEASED",
        "K1-E = NOT_ADMISSIBLE",
        "physical_evidence_effect = NONE",
    ]
    for token in required_protocol_tokens:
        require(token in text, f"protocol missing required token: {token}")

    forbidden_execution_tokens = [
        "tensorflow",
        "torch.",
        "jax.",
        "model.fit(",
        "optimizer.step(",
    ]
    lower_text = text.lower()
    for token in forbidden_execution_tokens:
        require(token.lower() not in lower_text, f"protocol unexpectedly contains execution primitive: {token}")

    print("PASS: AIP-LENS-01-NULL v0.1 protocol/contract is internally consistent and non-executing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
