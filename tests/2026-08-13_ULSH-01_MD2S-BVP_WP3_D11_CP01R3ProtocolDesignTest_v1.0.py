#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "registry/2026-08-13_ULSH-01_MD2S-BVP_WP3_D11_CP01R3ProtocolDesign_v1.0.json"
D10 = ROOT / "registry/2026-08-13_ULSH-01_MD2S-BVP_WP3_D10_CP01R2FailureDiagnosis_v1.0.json"
KERNEL = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.1.py"
RUN_INPUT = ROOT / "registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3_CP01R2RunInputFreeze_v1.0.json"


def projected_residuals(*, A0: float, L0: float, Y: float, lam: float) -> tuple[float, float]:
    A_star = (lam - 0.5 * Y) / 4.0
    L_star = -3.0 * A_star + lam + 0.5 * Y
    dA = A_star - A0
    dL = L_star - L0
    A = A0 + dA
    L = L0 + dL
    return (-3.0 * A - L + lam + 0.5 * Y, -4.0 * A + lam - 0.5 * Y)


def field_block_rms_metric(delta: list[float], seed: list[float]) -> float:
    assert len(delta) == len(seed) and delta
    seed_rms = math.sqrt(sum(v * v for v in seed) / len(seed))
    scale = max(1.0, seed_rms)
    return math.sqrt(sum((v / scale) ** 2 for v in delta) / len(delta))


def main() -> int:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    diagnosis = json.loads(D10.read_text(encoding="utf-8"))
    run_input = json.loads(RUN_INPUT.read_text(encoding="utf-8"))
    kernel = KERNEL.read_text(encoding="utf-8")

    assert design["classification"] == "BOUNDARY_AWARE_INITIALIZATION_AND_STATE_METRIC_TRUST_PROTOCOL_DESIGN_NO_EXECUTION"
    assert design["status"] == "PASS_CP01R3_PROTOCOL_DESIGNED_NOT_IMPLEMENTED_NOT_AUTHORIZED_NOT_EXECUTED"
    assert design["source_diagnosis"].endswith("D10_CP01R2FailureDiagnosis_v1.0.json")
    assert diagnosis["status"].startswith("PASS_CP01R2_FAILURE_MODE_DIAGNOSIS")

    identity = design["new_run_identity"]
    assert identity["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R3"
    assert identity["state"] == "DESIGNED_NOT_IMPLEMENTED_NOT_AUTHORIZED_NOT_EXECUTED"
    assert identity["preserves_CP01R1_and_CP01R2_as_immutable_results"] is True

    freeze = design["physical_identity_freeze"]
    for key in (
        "model_parameters_identical_to_CP01R2",
        "topological_sector_identical_to_CP01R2",
        "alpha_H_identical_to_CP01R2",
        "physical_equations_identical_to_CP01R2",
        "boundary_residual_equations_identical_to_CP01R2",
        "acceptance_thresholds_identical_to_CP01R2",
        "node_counts_identical_to_CP01R2",
        "seed_multiplier_count_identical_to_CP01R2",
        "progress_continuation_rule_identical_to_CP01R2",
    ):
        assert freeze[key] is True
    assert len(freeze["changed_components"]) == 2

    # Static source binding for the exact frozen junction equations.
    assert "-3.0 * A_sum - ell_sum + model.lambda_hat + 0.5 * Y_sigma" in kernel
    assert "-4.0 * A_sum + model.lambda_hat - 0.5 * Y_sigma" in kernel

    projection = design["boundary_projection"]
    assert projection["id"] == "BJP-01_EXACT_JUNCTION_DERIVATIVE_PROJECTION"
    assert "R_4D_and_R_chi_are_exactly_zero_in_exact_arithmetic_after_projection" in projection["analytic_invariants"]

    # Pure algebraic design sanity checks. No physical backend is imported.
    synthetic_cases = (
        (0.0, 0.0, 1.25, 1.0),
        (0.2, -0.4, 0.0, 1.0),
        (-0.3, 0.8, 2.0, 1.0),
        (1.0, -1.0, 0.75, 0.5),
    )
    for A0, L0, Y, lam in synthetic_cases:
        r4, rchi = projected_residuals(A0=A0, L0=L0, Y=Y, lam=lam)
        assert abs(r4) < 1e-14
        assert abs(rchi) < 1e-14

    seed = design["new_seed_family"]
    assert seed["seed_set_id_reserved"] == "M1-BG3B-CP01R3-BJP01-SEEDS-01"
    assert seed["seed_spec_sha256"] == "PENDING_D12_IMPLEMENTATION_FREEZE"
    assert seed["uses_result_fitting"] is False
    assert seed["uses_changed_physical_parameters"] is False
    assert seed["uses_extra_seed_multipliers"] is False

    etrn = design["etrn02_design"]
    assert etrn["id"] == "ETRN-02_EQUILIBRATED_LINEAR_SOLVE_WITH_MESH_NORMALIZED_STATE_METRIC_TRUST"
    assert etrn["linear_direction"]["row_and_column_equilibration"] == "PRESERVED_FOR_LINEAR_SOLVE_ONLY"
    assert etrn["trust_metric"]["column_equilibration_affects_trust_metric"] is False
    assert etrn["trust_metric"]["mesh_normalized_by_construction"] is True
    assert etrn["progress_continuation"]["unchanged_from_CP01R2"] is True
    assert etrn["stagnation_and_iteration"]["unchanged_from_CP01R2"] is True

    trust = etrn["trust_update"]
    assert 0 < trust["minimum_radius"] < trust["initial_radius"] < trust["maximum_radius"]
    assert trust["rho_accept_min"] == 0.10
    assert trust["rho_shrink"] == 0.25
    assert trust["rho_expand"] == 0.75

    # RMS block metric is mesh normalized for a repeated constant perturbation.
    norms = []
    for n in (24, 32, 48, 64, 96):
        norms.append(field_block_rms_metric([0.2] * n, [0.5] * n))
    assert max(norms) - min(norms) < 1e-15

    controls = {row["id"] for row in design["manufactured_control_suite_required_before_binding"]}
    assert controls == {"D11-C1", "D11-C2", "D11-C3", "D11-C4", "D11-C5", "D11-C6"}

    firewall = design["execution_firewall"]
    assert set(firewall.values()) == {False}

    governance = design["governance_state"]
    assert governance["WP3"].startswith("OPEN_CP01R3_PROTOCOL_DESIGNED")
    assert governance["WP4"].startswith("BLOCKED")
    assert governance["ULSH-02"].startswith("BLOCKED")
    assert governance["K1-D"] == "NOT_RELEASED"
    assert governance["K1-E"] == "NOT_ADMISSIBLE"
    assert governance["physical_evidence_effect"] == "NONE"

    payload = run_input["frozen_run_payload"]
    assert payload["model_parameters_ordered"]["lambda_hat"] == "1"
    assert payload["model_parameters_ordered"]["a_F"] == "1/4"

    assert design["next_allowed_action"] == "ULSH-01_WP3_D12_CP01R3_BJP01_ETRN02_IMPLEMENTATION_AND_MANUFACTURED_CONTROLS_ONLY"
    forbidden = set(design["forbidden_next_actions"])
    assert "DO_NOT_EXECUTE_CP01R3_IN_D11" in forbidden
    assert "DO_NOT_AUTHORIZE_A_PHYSICAL_RUN_BEFORE_D12_D13_D14_AND_D15_REVIEWS" in forbidden
    assert "DO_NOT_ADVANCE_TO_WP4_OR_ULSH-02" in forbidden

    print("PASS_WP3_D11_CP01R3_PROTOCOL_DESIGN_NO_EXECUTION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
