#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry/2026-08-15_HZT-M0_S6_C-PHYS_H4R4_ExactCompatibility_LocalIBVP_ManufacturedSolutionPreflight_v0.1.json"


def load():
    return json.loads(REG.read_text(encoding="utf-8"))


def test_order_zero_channels_are_present():
    d = load()
    o0 = " ".join(d["compatibility_hierarchy"]["order_zero"])
    assert "B(W_N^0,W_S^0,Q_N^0,Q_S^0)=0" in o0
    assert "C_H" in o0 and "C_M" in o0
    assert "R_patch=0" in o0


def test_higher_jet_expansion_is_not_faked():
    d = load()
    ch = d["compatibility_hierarchy"]
    assert "j=1,...,m-1" in ch["recursive_rule"]
    assert "exact first-order evolution equations" in ch["recursive_rule"]
    assert ch["result"] == "HIERARCHY_FORM_DEFINED_EXACT_JETS_BLOCKED_PENDING_COEFFICIENT_EXPORT"
    assert "does not yet export" in ch["why_not_expanded_here"]


def test_theorem_is_not_ratifed_from_principal_data_only():
    d = load()
    th = d["theorem_hypothesis_matrix"]
    assert th["symmetric_hyperbolic_principal_form"].startswith("PASS_H4R3")
    assert th["principal_maximal_boundary_control"] == "PASS_H4R3"
    assert th["compatibility_conditions_through_required_order"] == "NOT_CHECKABLE_YET"
    assert th["local_existence_uniqueness"] == "NOT_RATIFIED"
    assert d["h4r4_theorem_target"]["result"] == "NOT_RATIFIABLE_YET"


def test_mms_is_verification_only_and_not_executed():
    d = load()
    m = d["manufactured_solution_preflight"]
    assert m["execution_authorized"] is False
    assert d["manufactured_solution_execution"] is False
    assert "exact_bulk_operator" in m["bulk_forcing"]
    assert "exact_interface_residual" in m["boundary_forcing"]
    assert any("no clipping" in x.lower() for x in m["required_tests_before_execution"])
    assert m["result"] == "MMS_PROTOCOL_PREFLIGHT_FROZEN_EXECUTION_BLOCKED"


def test_governance_firewall():
    d = load()
    g = d["h4r4_disposition"]
    assert g["physical_parent_solve_authorized"] is False
    assert g["D2NQ_parent_dynamic_selection"] == "OPEN_NOT_EXECUTED"
    assert g["physical_hamiltonian_positivity"] == "OPEN"
    assert g["full_ghost_freedom"] == "OPEN"
    assert g["K1-D"] == "NOT_RELEASED"
    assert g["K1-E"] == "NOT_ADMISSIBLE"
    assert g["WP4"] == "BLOCKED"
    assert g["physical_evidence_effect"] == "NONE"


def main():
    tests = [name for name in globals() if name.startswith("test_")]
    for name in sorted(tests):
        globals()[name]()
        print(f"PASS {name}")
    print(f"{len(tests)} H4R4 tests passed")


if __name__ == "__main__":
    main()
