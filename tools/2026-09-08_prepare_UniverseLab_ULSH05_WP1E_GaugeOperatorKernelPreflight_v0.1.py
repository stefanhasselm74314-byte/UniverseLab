from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry/2026-09-08_UniverseLab_ULSH05_WP1E_GaugeOperatorKernelPreflight_v0.1.json"


def main() -> None:
    d = json.loads(REGISTRY.read_text(encoding="utf-8"))
    g = d["gate_state"]
    p = d["projector_kernel_audit"]
    f = d["interface_full_gauge_firewall"]
    summary = {
        "work_package": d["work_package"],
        "model_id": d["model_id"],
        "basis_main": d["basis_main"],
        "status": d["status"],
        "raw_gauge_operator": g["WP1E_raw_gauge_operator"],
        "coefficient_gauge_matrix": g["WP1E_coefficient_gauge_matrix"],
        "projector_kernel_audit": g["WP1E_projector_kernel_audit"],
        "conditional_bulk_kinematic_invariants": g["WP1E_conditional_bulk_kinematic_invariants"],
        "full_interface_rho_invariant_basis": g["WP1E_full_interface_rho_invariant_basis"],
        "raw_G_projector_dependency": p["raw_G_dependency_on_projector"],
        "coefficient_G_projector_dependency": p["coefficient_G_dependency_on_projector"],
        "global_D2_inverse": p["global_D2_inverse"],
        "interface_rho_firewall": f["componentwise_full_rho_invariant_basis"],
        "PHYSICAL_BACKGROUND": g["PHYSICAL_BACKGROUND"],
        "WP1D_constraint_elimination": g["WP1D_constraint_elimination"],
        "WP1D_physical_DOF_count": g["WP1D_physical_DOF_count"],
        "K1-D": g["K1-D"],
        "K1-E": g["K1-E"],
        "BACKEND_IMPORT": g["BACKEND_IMPORT"],
        "SOLVER_EXECUTION": g["SOLVER_EXECUTION"],
        "physical_gate_effect": d["physical_gate_effect"],
        "physical_evidence_effect": d["physical_evidence_effect"],
        "solver_authorized": d["solver_authorized"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
