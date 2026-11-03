#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
C_PHYS = ROOT / "ulsh" / "ULSH-01" / "C-PHYS"
MODULE_PATH = C_PHYS / "2026-08-27_hzt_m1c1_8x8_backend_interface_v0.1.py"
TARGET_PATH = C_PHYS / "2026-08-21_ULSH01_M1C1_8x8_TargetContract_v0.1.json"
CONTRACT_PATH = C_PHYS / "2026-08-27_ULSH01_M1C1_8x8_BackendInterfaceContract_v0.1.json"
RESULT_SCHEMA_PATH = C_PHYS / "2026-08-27_ULSH01_M1C1_8x8_ResultSchema_v0.1.json"

spec = importlib.util.spec_from_file_location("ulsh01_m1c1_backend_interface", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def expect_contract_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except module.ContractError:
        return
    raise AssertionError("expected ContractError")


def test_exact_target_binding():
    target = module.load_json(TARGET_PATH)
    module.verify_target(target)
    assert module.canonical_target_digest(target) == module.TARGET_DIGEST
    assert module.TARGET_DIGEST == "237c4b5e08a2106e13e985c4af7925f1899e2ae2e4b7253c7ab73cc2db5f1823"


def test_interface_and_result_schema():
    contract = module.load_json(CONTRACT_PATH)
    result_schema = module.load_json(RESULT_SCHEMA_PATH)
    module.verify_interface_contract(contract)
    module.verify_result_schema(result_schema)
    assert contract["interface"]["continuous_unknown_order"] == list(module.UNKNOWN_ORDER)
    assert contract["interface"]["boundary_residual_order"] == list(module.BOUNDARY_RESIDUAL_ORDER)
    assert result_schema["solution"]["boundary_residual_order"] == list(module.BOUNDARY_RESIDUAL_ORDER)


def test_south_patch_binding_exactly_once():
    bound = module.patch_binding(
        a_chi_N_cap=0.75,
        a_chi_S_cap=0.25,
        N_F=1,
        q_hat=2.0,
        N_sigma=3,
        m_sigma=2,
    )
    assert bound["a_chi_Sigma"] == 0.25
    assert abs(bound["R_patch"]) < 1e-15
    assert abs(bound["d_chi"] - 2.0) < 1e-15


def test_fail_closed_domains():
    expect_contract_error(
        module.patch_binding,
        a_chi_N_cap=0.0,
        a_chi_S_cap=0.0,
        N_F=0,
        q_hat=0.0,
        N_sigma=0,
        m_sigma=1,
    )
    expect_contract_error(
        module.patch_binding,
        a_chi_N_cap=0.0,
        a_chi_S_cap=0.0,
        N_F=0,
        q_hat=1.0,
        N_sigma=0,
        m_sigma=0,
    )


def test_noncanonical_field_firewall():
    module.reject_noncanonical_keys({
        "target_digest": module.TARGET_DIGEST,
        "profiles": {"A_s": [], "ell_s": [], "varphi_s": [], "a_chi_s": []},
    })
    for forbidden in sorted(module.FORBIDDEN_CANONICAL_KEYS):
        expect_contract_error(module.reject_noncanonical_keys, {forbidden: 1})


def test_governance_firewall():
    assert module.PHYSICAL_EXECUTION_AUTHORIZED is False
    assert module.PHYSICAL_BACKEND_IMPORT_ALLOWED is False
    assert module.TARGET_SOLVE_ALLOWED is False
    assert module.RANK_R_CLAIM_ALLOWED is False
    assert module.PHYSICAL_EVIDENCE_EFFECT == "NONE"
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert "scipy" not in source.lower()
    assert "solve_bvp" not in source


def test_target_contract_excludes_sigma_ft():
    target = json.loads(TARGET_PATH.read_text(encoding="utf-8"))
    excluded = set(target["target_semantics"]["field_content"]["noncanonical_excluded_from_target"])
    assert {"Sigma_FT", "c_N", "c_S"}.issubset(excluded)
    assert target["target_semantics"]["boundary_operator"]["not_additional_residuals"]["R_flux"] == "equivalent_to_R_patch"
    assert target["target_semantics"]["rr_constraint"]["role"] == "PROPAGATED_QA_CHANNEL_NOT_ADDITIONAL_NONLINEAR_OR_ENDPOINT_RESIDUAL"


if __name__ == "__main__":
    test_exact_target_binding()
    test_interface_and_result_schema()
    test_south_patch_binding_exactly_once()
    test_fail_closed_domains()
    test_noncanonical_field_firewall()
    test_governance_firewall()
    test_target_contract_excludes_sigma_ft()
    print("ULSH-01 M1/C1 8x8 backend-interface QA: PASS (NO SOLVER EXECUTION)")
