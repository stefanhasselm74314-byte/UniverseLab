from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "registry/2026-09-08_UniverseLab_ULSH05_WP1D_ConditionalSVTGaugeConstraintReduction_v0.1.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit the nonoperative ULSH05/WP1D reduction-domain summary.")
    parser.add_argument("--registry", type=Path, default=DEFAULT)
    args = parser.parse_args()

    data = json.loads(args.registry.read_text(encoding="utf-8"))
    gate = data["gate_state"]
    summary = {
        "work_package": data["work_package"],
        "status": data["status"],
        "successor_assignment": data["successor_assignment"]["status"],
        "analytic_domain": gate["WP1D_analytic_field_domain"],
        "svt_bookkeeping": gate["WP1D_4D_covariant_SVT_bookkeeping"],
        "constraint_elimination": gate["WP1D_constraint_elimination"],
        "physical_3plus1_svt": gate["WP1D_physical_3plus1_SVT"],
        "physical_dof_count": gate["WP1D_physical_DOF_count"],
        "physical_background": gate["PHYSICAL_BACKGROUND"],
        "solver_execution": gate["SOLVER_EXECUTION"],
        "physical_gate_effect": data["physical_gate_effect"],
        "physical_evidence_effect": data["physical_evidence_effect"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
