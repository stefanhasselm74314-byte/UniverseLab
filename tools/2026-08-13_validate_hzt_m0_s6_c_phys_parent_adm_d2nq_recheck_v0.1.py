#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG_PATH = ROOT / "registry/2026-08-13_HZT-M0_S6_C-PHYS_ParentADM_D2NQ_Recheck_v0.1.json"


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    hdr = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(hdr + data).hexdigest()


def fail(msg: str):
    raise SystemExit(f"FAIL: {msg}")


def require(cond: bool, msg: str):
    if not cond:
        fail(msg)


def validate() -> dict:
    reg = json.loads(REG_PATH.read_text(encoding="utf-8"))

    require(reg["schema"] == "universelab.hzt-m0-s6-c-phys.parent-adm-d2nq-recheck.v1", "schema drift")
    require(reg["recheck_id"] == "C-PHYS-PARENT-ADM-D2NQ-RECHECK-01", "recheck id drift")
    require(reg["track_id"] == "MD2S-R1-C-PHYS", "track drift")
    require(reg["model_id"] == "HZT-M0-S6-C-PHYS-M1", "model drift")
    require(reg["classification"] == "INDEPENDENT_REDERIVATION_FROM_CANONICAL_REPOSITORY_INPUTS_ONLY", "classification drift")

    for src in reg["source_bindings"]:
        path = ROOT / src["path"]
        require(path.is_file(), f"missing source {src['path']}")
        got = git_blob_sha1(path)
        require(got == src["git_blob_sha1"], f"source blob drift {src['path']}: {got}")

    parent = json.loads((ROOT / "hzt-s6-parent-action-v0.1.json").read_text(encoding="utf-8"))
    require(parent["signature"] == "(-,+,+,+,+,+)", "parent signature is not one-time")
    require(parent["control_core"] == "S6-Q1 / RB0-heavy-GR-quiet", "parent control core drift")
    require(parent["field_dimensions_M"]["Lambda6"] == 2, "Lambda6 dimension must be M^2 in canonical normalization")
    require(parent["field_dimensions_M"]["phi"] == 2, "phi dimension drift")
    require(parent["governance"]["K1-D"] == "NOT_RELEASED", "parent K1-D drift")
    require(parent["governance"]["K1-E"] == "NOT_ADMISSIBLE", "parent K1-E drift")

    m1 = json.loads((ROOT / "registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json").read_text(encoding="utf-8"))
    require(m1["model_id"] == "HZT-M0-S6-C-PHYS-M1", "M1 id drift")
    require(m1["field_and_unit_conventions"]["canonical_scalar_kinetic"] == "Z_phi=1", "scalar kinetic normalization drift")
    require(m1["exact_functions"]["Z_F"]["formula"] == "Z_F(phi)=exp(-2*a_F*varphi)", "Z_F formula drift")
    require("strictly_positive_for_all_finite_phi" in m1["exact_functions"]["Z_F"]["properties"], "Z_F positivity not frozen")
    require("strictly_positive_on_active_winding_branch" in m1["exact_functions"]["Z_sigma"]["properties"], "Z_sigma positivity not frozen")

    fw = reg["external_material_firewall"]
    require(fw["gemini_blocks"] == "EXTERNAL_UNVERIFIED_GEMINI_DRAFT", "Gemini quarantine missing")
    require(fw["gemini_equations_used_as_premises"] is False, "Gemini equations imported")
    require(fw["two_time_signature_imported"] is False, "two-time signature imported")

    adm = reg["temporal_adm"]
    require(adm["spatial_dimension_d"] == 5, "ADM spatial dimension drift")
    require("pi/4" in adm["canonical_momenta"]["K_ab_inverse"], "5D trace divisor must be 4")
    require("pi^2/4" in adm["hamiltonian_constraint_bulk"], "Hamiltonian DeWitt trace coefficient drift")

    dims = reg["dimension_audit"]
    require(dims["pi_ab"] == "M^5", "pi dimension drift")
    require(dims["p_phi"] == "M^3", "scalar momentum dimension drift")
    require(dims["Pi_A"] == "M^3", "gauge momentum dimension drift")
    require(dims["H_perp"] == "M^6", "Hamiltonian density dimension drift")
    require(dims["gemini_rho2_over_M6four_as_H2"] == "FAIL_DIMENSIONALLY_AS_WRITTEN", "rho^2 dimensional audit weakened")

    proj = reg["four_dimensional_projection"]
    require(proj["normal_metric"] == "delta_ij_positive_definite", "normal signature drift")
    require(proj["exact_flrw_components"]["Q_00"] == "3*B_squared", "Q00 identity drift")
    require(proj["effective_fluid_if_Einstein_normalized"]["rho_Q"] == "3*M4^2*B_squared", "rho_Q normalization drift")

    d2 = reg["d2nq_exact_conditional_construction"]
    require(d2["consequences"]["B_squared"] == "B_Lambda^2+B_m^2*a^(-3)", "D2N-Q scaling drift")
    require(d2["classification"] == "EXACT_KINEMATIC_REALIZATION_NOT_PARENT_DYNAMICAL_DERIVATION", "D2N-Q overclaim")

    gates = reg["gate_disposition"]
    require(gates["full_parent_to_B_squared_map"] == "OPEN", "parent->B2 map overclaimed")
    require(gates["full_ghost_freedom"] == "OPEN", "ghost freedom overclaimed")
    require(gates["global_bounce"] == "OPEN", "bounce overclaimed")
    require(gates["K1-D"] == "NOT_RELEASED", "K1-D illegally advanced")
    require(gates["K1-E"] == "NOT_ADMISSIBLE", "K1-E illegally advanced")
    require(gates["WP4"] == "BLOCKED", "WP4 illegally advanced")
    require(gates["physical_evidence_effect"] == "NONE", "evidence illegally advanced")

    require(reg["bounce_disposition"]["negative_rho_squared_term_derived"] is False, "negative rho2 term falsely derived")
    require(reg["bounce_disposition"]["bounce_derived"] is False, "bounce falsely derived")

    return {
        "status": "PASS",
        "recheck_id": reg["recheck_id"],
        "source_bindings": len(reg["source_bindings"]),
        "signature": parent["signature"],
        "K1-D": gates["K1-D"],
        "K1-E": gates["K1-E"],
        "physical_evidence_effect": gates["physical_evidence_effect"]
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = validate()
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print("PASS C-PHYS parent ADM / D2N-Q recheck")


if __name__ == "__main__":
    main()
