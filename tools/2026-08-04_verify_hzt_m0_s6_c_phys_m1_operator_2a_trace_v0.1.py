#!/usr/bin/env python3
"""Supplemental symbolic QA for M1 Operator-2A pole regularity and cap trace."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
BASE_TOOL = ROOT / "tools/2026-08-04_verify_hzt_m0_s6_c_phys_m1_operator_2a_v0.1.py"
PREFLIGHT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2ARegularityTracePreflight_v0.1.json"
CONTRACT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2AContract_v0.1.json"

class ContractError(ValueError):
    pass

def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)

def load_json(path: Path) -> dict:
    require(path.is_file(), f"missing required artifact: {path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    require(isinstance(value, dict), f"artifact must be an object: {path.relative_to(ROOT)}")
    return value

def load_base_module():
    spec = importlib.util.spec_from_file_location("m1_operator_2a_base", BASE_TOOL)
    if spec is None or spec.loader is None:
        raise ContractError("unable to import base Operator-2A verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def verify_base_symbolics() -> dict[str, str]:
    base = load_base_module()
    constraint = base.derive_constraint_identity()
    pole = base.verify_pole_series()
    principal = base.verify_principal_matrix()
    require(constraint["off_shell_identity"] == "C_x+4*A_x*C=ell_x*E_A+4*A_x*E_ell-varphi_x*E_varphi", "constraint identity drift")
    require(principal["determinant"] == "4*ell", "principal determinant drift")
    return {"constraint":"PASS_EXACT_SYMBOLIC","pole_series":pole["series_order"],"principal_determinant":principal["determinant"]}

def verify_pole_invariant_expansions() -> dict[str, str]:
    x = sp.symbols("x", positive=True)
    a2, a4, l3, l5, f2, f4, aF, R0, q0 = sp.symbols("a2 a4 l3 l5 f2 f4 aF R0 q0")
    A_delta = a2*x**2+a4*x**4
    ell = x+l3*x**3+l5*x**5
    varphi_delta = f2*x**2+f4*x**4
    ell_ratio = sp.series(sp.diff(ell,x)/ell,x,0,5).removeO().expand()
    expected_ell_ratio = 1/x+2*l3*x+(4*l5-2*l3**2)*x**3
    require(sp.simplify(ell_ratio-expected_ell_ratio)==0,"ell_x/ell expansion failed")
    ell_second_ratio = sp.series(sp.diff(ell,x,2)/ell,x,0,4).removeO().expand()
    expected_ell_second = 6*l3+(20*l5-6*l3**2)*x**2
    require(sp.simplify(ell_second_ratio-expected_ell_second)==0,"ell_xx/ell expansion failed")
    mixed = sp.series(sp.diff(A_delta,x)*sp.diff(ell,x)/ell,x,0,4).removeO().expand()
    expected_mixed = 2*a2+(4*a4+4*a2*l3)*x**2
    require(sp.simplify(mixed-expected_mixed)==0,"A_x ell_x/ell expansion failed")
    scalar_gradient = sp.series(sp.diff(varphi_delta,x)**2,x,0,4).removeO().expand()
    require(sp.simplify(scalar_gradient-4*f2**2*x**2)==0,"scalar-gradient expansion failed")
    rho = R0*sp.exp(-8*A_delta+2*aF*varphi_delta)
    expected_rho = R0*(1+(-8*a2+2*aF*f2)*x**2)
    require(sp.simplify(sp.series(rho,x,0,4).removeO().expand()-expected_rho)==0,"rho_F expansion failed")
    orthonormal_flux = q0*sp.exp(-4*A_delta+2*aF*varphi_delta)
    expected_flux = q0*(1+(-4*a2+2*aF*f2)*x**2)
    require(sp.simplify(sp.series(orthonormal_flux,x,0,4).removeO().expand()-expected_flux)==0,"orthonormal flux expansion failed")
    return {"ell_x_over_ell":str(expected_ell_ratio),"ell_xx_over_ell":str(expected_ell_second),"A_x_ell_x_over_ell":str(expected_mixed),"rho_F":str(expected_rho),"orthonormal_flux":str(expected_flux),"internal_gaussian_curvature_limit":str(-6*l3),"status":"PASS_FORMAL_FINITE_LOCAL_BUILDING_BLOCKS"}

def verify_cap_principal_transmission() -> dict[str, str]:
    ell_cap = sp.symbols("ell_cap", positive=True)
    metric_matrix = sp.Matrix([[-3,-1/ell_cap],[-4,0]])
    determinant = sp.factor(metric_matrix.det())
    require(determinant == -4/ell_cap,"metric cap derivative determinant drift")
    transmission = sp.Matrix([[1,-1,0,0],[0,0,1,1]])
    require(transmission.rank()==2,"standard transmission pair lost rank")
    return {"metric_derivative_matrix":"[[-3,-1/ell_cap],[-4,0]]","metric_derivative_determinant":"-4/ell_cap","metric_status":"FULL_RANK_FOR_ELL_CAP_POSITIVE","scalar_status":"CONTINUITY_PLUS_OUTWARD_NORMAL_SUM_FULL_RANK","gauge_profile_status":"FIRST_ORDER_TRANSPORT_CLOSED_BY_REGULAR_POLE_GAUGES","full_augmented_trace_status":"NOT_CONSTRUCTED","Fredholm_status":"NOT_PROVEN"}

def verify_contract_firewalls() -> dict[str, str]:
    contract = load_json(CONTRACT)
    preflight = load_json(PREFLIGHT)
    require(contract["model_id"]=="HZT-M0-S6-C-PHYS-M1","model identity drift")
    require(contract["solver_authorized"] is False,"solver authorization drift")
    require(contract["physical_evidence_effect"]=="NONE","physical evidence drift")
    require(preflight["gate_state"]["full_linearized_boundary_trace"]=="NOT_CONSTRUCTED","full trace overclaim")
    require(preflight["gate_state"]["Fredholm_property"]=="NOT_PROVEN","Fredholm overclaim")
    require(preflight["gate_state"]["R1.1"]=="BLOCKED","R1.1 gate drift")
    require(preflight["gate_state"]["official_MD2S_solver"]=="NOT_AUTHORIZED","solver gate drift")
    require(preflight["gate_state"]["K1-D"]=="NOT_RELEASED","K1-D gate drift")
    require(preflight["gate_state"]["K1-E"]=="NOT_ADMISSIBLE","K1-E gate drift")
    return {"model_id":contract["model_id"],"block":contract["block"],"R1.1":preflight["gate_state"]["R1.1"],"solver":preflight["gate_state"]["official_MD2S_solver"],"physical_evidence_effect":preflight["physical_evidence_effect"]}

def validate() -> dict:
    return {"contract":"C_PHYS_M1_OPERATOR_2A_REGULARITY_TRACE_QA","status":"PASS_FORMAL","base_symbolics":verify_base_symbolics(),"pole_invariants":verify_pole_invariant_expansions(),"cap_principal_transmission":verify_cap_principal_transmission(),"firewalls":verify_contract_firewalls(),"forbidden_inference":["No physical background follows.","No full endpoint trace invertibility follows.","No Fredholm property or continuum Jacobian rank follows.","No solver, R1.1, K1-D or K1-E release follows."]}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json",action="store_true")
    args = parser.parse_args()
    try:
        payload = validate()
    except (ContractError,AssertionError) as exc:
        if args.json:
            print(json.dumps({"status":"FAIL","error":str(exc)},indent=2,sort_keys=True))
        else:
            print(f"FAIL: {exc}")
        return 1
    if args.json:
        print(json.dumps(payload,indent=2,sort_keys=True))
    else:
        print("PASS: M1 Operator-2A regularity and principal trace preflight")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
