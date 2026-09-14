#!/usr/bin/env python3
"""Emit a compact, nonoperative WP1D2 status summary.

This tool reads the frozen registry only. It does not import a backend, execute a
solver, construct a physical projector, or change any gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "registry/2026-09-14_UniverseLab_ULSH05_WP1D2_KinematicInvariantProjectorSolvabilityPreflight_v0.1.json"


def build_summary(registry: dict) -> dict:
    gates = registry["gate_state"]
    projectors = registry["projector_solvability_preflight"]
    return {
        "schema": "universelab.ulsh05.wp1d2.summary.v0.1",
        "work_package": registry["work_package"],
        "status": registry["status"],
        "basis_main": registry["basis_main"],
        "successor": registry["successor_assignment"],
        "invariant_candidate_status": gates["WP1D2_invariant_candidate_ledger"],
        "projector_solvability_status": gates["WP1D2_projector_solvability_preflight"],
        "pole_extension_status": gates["WP1D2_pole_extension_audit"],
        "projector_closed_range": {
            "D2": projectors["closed_range_D2"],
            "Delta_1": projectors["closed_range_Delta_1"],
            "Delta_L": projectors["closed_range_Delta_L"],
        },
        "physical_firewalls": {
            "WP1_physical_boundary_domain": gates["WP1_physical_boundary_domain"],
            "WP1D_constraint_elimination": gates["WP1D_constraint_elimination"],
            "WP1D_physical_3plus1_SVT": gates["WP1D_physical_3plus1_SVT"],
            "WP1D_physical_DOF_count": gates["WP1D_physical_DOF_count"],
            "PHYSICAL_BACKGROUND": gates["PHYSICAL_BACKGROUND"],
            "FM-G0": gates["FM-G0"],
            "K1-D": gates["K1-D"],
            "K1-E": gates["K1-E"],
            "BACKEND_IMPORT": gates["BACKEND_IMPORT"],
            "SOLVER_EXECUTION": gates["SOLVER_EXECUTION"],
            "PHYSICAL_RESPONSE_RANK": gates["PHYSICAL_RESPONSE_RANK"],
        },
        "effects": {
            "physical_gate_effect": registry["physical_gate_effect"],
            "physical_evidence_effect": registry["physical_evidence_effect"],
            "solver_authorized": registry["solver_authorized"],
        },
        "next_exact_id": registry["continuation"]["next_exact_id"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    summary = build_summary(registry)
    payload = json.dumps(summary, indent=2, sort_keys=True) + "\n"

    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
