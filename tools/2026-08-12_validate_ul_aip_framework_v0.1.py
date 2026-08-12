#!/usr/bin/env python3
"""Fail-closed validator for UniverseLab AI-for-Physics Framework v0.1."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry/2026-08-12_UniverseLab_AIForPhysicsFramework_v0.1.json"
DOC = ROOT / "science/ai-for-physics/2026-08-12_UniverseLab_AIForPhysicsFramework_v0.1.md"

REQUIRED_MODULES = {
    "AIP-SYM",
    "AIP-SURR",
    "AIP-SBI",
    "AIP-ANOM",
    "AIP-LENS",
    "AIP-GW",
    "AIP-COSMO",
}
REQUIRED_GATES = {f"AIP-G{i}" for i in range(8)}
REQUIRED_PRINCIPLES = {
    "AI_ACCELERATION_NE_SOLVER_VALIDATION_NE_PHYSICAL_IDENTIFICATION_NE_EVIDENCE",
    "ML_ACCURACY_NE_PHYSICAL_ADMISSIBILITY",
    "SIMULATOR_VALIDATION_NE_REAL_DATA_VALIDATION",
    "AUTHORITATIVE_SOLVER_RETURN_PATH_REQUIRED",
    "NEITHER_MODEL_STATE_REQUIRED_WHEN_CLOSED_CLASSIFICATION_IS_NOT_JUSTIFIED",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"UL-AIP validation failed: {message}")


def main() -> None:
    require(REGISTRY.is_file(), f"missing registry: {REGISTRY}")
    require(DOC.is_file(), f"missing canonical document: {DOC}")

    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    doc = DOC.read_text(encoding="utf-8")

    require(data.get("schema") == "universelab.ai-for-physics.framework.v1", "unexpected schema")
    require(data.get("framework_id") == "UL-AIP-v0.1", "unexpected framework id")
    require(data.get("status") == "METHODS_FRAMEWORK_DEFINED_NOT_RELEASED", "framework must remain not released")
    require(data.get("architecture") == "HPVS -> HZT-M0 -> HZT-Full", "architecture drift")
    require(data.get("canonical_document") == str(DOC.relative_to(ROOT)).replace("\\", "/"), "canonical document binding mismatch")

    require(set(data.get("modules", {})) == REQUIRED_MODULES, "module set mismatch")
    require(set(data.get("gates", {})) == REQUIRED_GATES, "gate set mismatch")
    require(REQUIRED_PRINCIPLES.issubset(set(data.get("principles", []))), "required principle missing")

    for name, module in data["modules"].items():
        require(module.get("initial_status") == "DEFINED_NOT_RELEASED", f"{name} unexpectedly released")

    anom_states = data["modules"]["AIP-ANOM"].get("required_state_space", [])
    require("NEITHER_OR_OOD" in anom_states, "neither/OOD state is mandatory")
    require(data["modules"]["AIP-SBI"].get("evidential_use_requires_forward_map_admissible") is True, "SBI forward-map firewall missing")

    fw = data.get("governance_firewall", {})
    require(fw.get("model_training") is False, "model training must be false")
    require(fw.get("model_execution") is False, "model execution must be false")
    require(fw.get("solver_state_modified") is False, "solver state modified")
    require(fw.get("likelihood_modified") is False, "likelihood modified")
    require(fw.get("physical_parameters_modified") is False, "physical parameters modified")
    require(fw.get("topology_modified") is False, "topology modified")
    require(fw.get("WP4") == "BLOCKED", "WP4 firewall drift")
    require(fw.get("K1-D") == "NOT_RELEASED", "K1-D firewall drift")
    require(fw.get("K1-E") == "NOT_ADMISSIBLE", "K1-E firewall drift")
    require(fw.get("physical_evidence_effect") == "NONE", "physical evidence must remain NONE")

    for token in (
        "AI acceleration != solver validation != physical identification != evidence",
        "ML accuracy != physical admissibility",
        "simulator validation != real-data validation",
        "AIP-G0",
        "AIP-G7",
        "AIP-LENS-01-NULL",
        "authoritative solver verification",
        "physical_evidence_effect = NONE",
    ):
        require(token in doc, f"canonical document missing required text: {token}")

    forbidden_release_strings = (
        "K1-D = RELEASED",
        "K1-E = ADMISSIBLE",
        "WP4 = RELEASED",
        "physical_evidence_effect = CONFIRMING",
    )
    for token in forbidden_release_strings:
        require(token not in doc, f"forbidden promotion language present: {token}")

    print("UL-AIP v0.1 validation PASS: methods-only framework, all firewalls intact")


if __name__ == "__main__":
    main()
