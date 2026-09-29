#!/usr/bin/env python3
"""Generate the G3.10 81-entry Jacobian dry-run plan. Never executes a solver."""
from __future__ import annotations
import argparse, json
from pathlib import Path

FORBIDDEN_KEYS = {"command", "solver_command", "executable", "submit", "run"}

def fail(msg: str) -> None:
    raise SystemExit(msg)

def load(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def validate_contract(c):
    op=c["operator"]; fd=c["finite_difference"]; ev=c["evaluation_schedule"]
    if op["dimension"] != 10 or len(op["coordinates"]) != 10: fail("coordinate contract must be 10D")
    if fd["scheme"] != "CENTRAL_ONLY": fail("central differences required")
    if fd["dimensionless_step_levels"] != [0.01,0.005,0.0025]: fail("step schedule mismatch")
    if fd["one_sided_fallback"] != "FORBIDDEN": fail("one-sided fallback must be forbidden")
    if ev.get("execution_authorized") is not False: fail("execution must remain unauthorized")
    if ev["total_bvp_evaluations"] != 81: fail("G3.9 total must equal 81")

def branch_lock(N_F:int,m_layer:int,n_S:int):
    n_N=n_S+m_layer*N_F
    return {
        "mode":"SYNTHETIC_DRY_RUN_ONLY",
        "N_F":N_F,"m_layer":m_layer,"n_N":n_N,"n_S":n_S,
        "constraint":"n_N-n_S=m_layer*N_F",
        "topology":"TWO_REGION_COMMON_CAP",
        "pole_frobenius_branch":"LOCKED",
        "profile_node_class":"LOCKED",
        "boundary_operator_identity":"G3.6_B10_LOCKED"
    }

def manifest(eid,kind,profile,branch,coordinate=None,step=None,sign=None,level=None):
    signed=0.0 if step is None else float(sign)*float(step)
    m={
      "evaluation_id":eid,"kind":kind,"coordinate":coordinate,
      "dimensionless_offset":signed,"step_magnitude":step,"step_level":level,
      "solver_profile_metadata_only":profile,"branch_lock":branch,
      "expected_input_artifact":f"inputs/{eid}.json",
      "expected_output_artifact":f"future_outputs/{eid}_Rhat.json",
      "execute":False,"evidence_effect":"NONE"
    }
    if FORBIDDEN_KEYS & set(m): fail("execution hook leaked into manifest")
    return m

def make_plan(c,N_F=2,m_layer=1,n_S=0):
    validate_contract(c)
    b=branch_lock(N_F,m_layer,n_S)
    if b["n_N"]-b["n_S"] != b["m_layer"]*b["N_F"]: fail("bundle constraint violated")
    coords=c["operator"]["coordinates"]
    steps=c["finite_difference"]["dimensionless_step_levels"]
    out=[manifest("B000","baseline","nominal",b)]
    k=1
    for j,name in enumerate(coords):
        for level,h in enumerate(steps,1):
            for sign in (-1,1):
                out.append(manifest(f"N{k:03d}","perturbation","nominal",b,name,h,sign,level)); k+=1
    for j,name in enumerate(coords):
        h=steps[-1]
        for sign in (-1,1):
            out.append(manifest(f"R{j*2+(1 if sign<0 else 2):03d}","perturbation","refined_h3",b,name,h,sign,3))
    if len(out)!=81: fail(f"planned {len(out)} evaluations, expected 81")
    frozen=json.dumps(b,sort_keys=True)
    if any(json.dumps(x["branch_lock"],sort_keys=True)!=frozen for x in out): fail("branch lock drift")
    return out

def main():
    p=argparse.ArgumentParser(); p.add_argument("contract"); p.add_argument("--output")
    p.add_argument("--N-F",type=int,default=2,dest="N_F"); p.add_argument("--m-layer",type=int,default=1); p.add_argument("--n-S",type=int,default=0,dest="n_S")
    a=p.parse_args(); c=load(a.contract); jobs=make_plan(c,a.N_F,a.m_layer,a.n_S)
    payload={
      "schema":"ulsh01.background3c5.g3.10.dry-run-plan.v0.1",
      "status":"DRY_RUN_ONLY","evidence_effect":"NONE","execute":False,
      "count":len(jobs),"evaluations":jobs,
      "future_aggregate_targets":["J_hat_h1","J_hat_h2","J_hat_h3","J_hat_h3_refined","epsilon_J","svd_report"],
      "physical_outputs_generated":[]
    }
    text=json.dumps(payload,indent=2,ensure_ascii=False)
    print(text)
    if a.output: Path(a.output).write_text(text+"\n",encoding="utf-8")
if __name__=="__main__": main()
