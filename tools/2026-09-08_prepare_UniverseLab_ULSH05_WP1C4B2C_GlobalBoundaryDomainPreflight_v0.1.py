from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry/2026-09-08_UniverseLab_ULSH05_WP1C4B2C_GlobalBoundaryDomainPreflight_v0.1.json"


def build_summary() -> dict:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    gates = reg["gate_state"]
    return {
        "work_package": reg["work_package"],
        "model_id": reg["model_id"],
        "basis_main": reg["basis_main"],
        "status": reg["status"],
        "local_test_domain": reg["domain_candidates"]["D0_local_test"]["status"],
        "physical_boundary_domain": gates["WP1_physical_boundary_domain"],
        "global_boundary_hessian": gates["WP1_full_global_boundary_hessian"],
        "full_quadratic_action": gates["WP1_full_quadratic_action"],
        "physical_background": gates["PHYSICAL_BACKGROUND"],
        "fm_g0": gates["FM-G0"],
        "k1_d": gates["K1-D"],
        "k1_e": gates["K1-E"],
        "solver_authorized": reg["solver_authorized"],
        "physical_gate_effect": reg["physical_gate_effect"],
        "physical_evidence_effect": reg["physical_evidence_effect"],
        "next_exact_work_package_id": reg["continuation"]["next_exact_work_package_id"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Emit the nonoperative WP1C4B2C global boundary-domain preflight summary."
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    summary = build_summary()
    payload = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    main()
