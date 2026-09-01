#!/usr/bin/env python3
"""ULSH-01/C-PHYS physical response-rank auditor v1.3.
Uses dimensionless J=Sy^-1 R Sc, step refinement, and optional h/4 solver refinement.
Numerical gate only: never releases K1-D/K1-E.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
import numpy as np

def read_matrix(path):
    with open(path,newline="",encoding="utf-8") as f: rows=list(csv.reader(f))
    if len(rows)<2 or len(rows[0])<2: raise ValueError(f"invalid matrix: {path}")
    c=[x.strip() for x in rows[0][1:]]; o=[]; a=[]
    for r in rows[1:]:
        if len(r)!=len(c)+1 or any(not x.strip() for x in r[1:]): raise ValueError(f"invalid row: {path}")
        o.append(r[0].strip()); a.append([float(x) for x in r[1:]])
    A=np.asarray(a,float)
    if np.any(~np.isfinite(A)): raise ValueError(f"non-finite matrix: {path}")
    return o,c,A
def scales(path,c,o):
    x=json.loads(Path(path).read_text(encoding="utf-8")); cm=x.get("control_scales",{}); ym=x.get("output_scales",{})
    if any(k not in cm for k in c) or any(k not in ym for k in o): raise ValueError("scale coverage incomplete")
    sc=np.array([float(cm[k]) for k in c]); sy=np.array([float(ym[k]) for k in o])
    if np.any(~np.isfinite(sc)) or np.any(~np.isfinite(sy)) or np.any(sc<=0) or np.any(sy<=0): raise ValueError("scales must be finite and >0")
    return sc,sy,x
def J(R,sc,sy): return (R*sc[None,:])/sy[:,None]
def decomp(A):
    U,s,V=np.linalg.svd(A,full_matrices=False); k=float(s[0]/s[-1]) if s[-1]>0 else math.inf; return U,s,V,k
def angle(v,w):
    z=abs(float(np.dot(v,w)/(np.linalg.norm(v)*np.linalg.norm(w)))); return float(np.degrees(np.arccos(np.clip(z,-1,1))))
def clean(x):
    if isinstance(x,dict): return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [clean(v) for v in x]
    if isinstance(x,np.ndarray): return clean(x.tolist())
    if isinstance(x,(np.floating,float)): return float(x) if math.isfinite(float(x)) else None
    if isinstance(x,np.integer): return int(x)
    return x
def main():
    p=argparse.ArgumentParser(); p.add_argument("matrix_h"); p.add_argument("matrix_h2"); p.add_argument("matrix_h4"); p.add_argument("scales_json")
    p.add_argument("--matrix-h4-refined"); p.add_argument("--solver-refinement-epsilon",type=float,default=None); p.add_argument("--run-manifest",required=True)
    p.add_argument("--q",type=float,default=5.0); p.add_argument("--cond-max",type=float,default=1e6); p.add_argument("--deriv-rel-max",type=float,default=1e-2); p.add_argument("--angle-max-deg",type=float,default=10.0); p.add_argument("--formal-rel-tol",type=float,default=1e-8); p.add_argument("--branch-ok",action="store_true"); p.add_argument("--output"); a=p.parse_args()
    o,c,R=read_matrix(a.matrix_h); o2,c2,R2=read_matrix(a.matrix_h2); o4,c4,R4=read_matrix(a.matrix_h4)
    if (o,c)!=(o2,c2) or (o,c)!=(o4,c4): raise ValueError("labels/order differ")
    if R4.shape[0]!=4 or R4.shape[1]<4: raise ValueError(f"response shape not gate-eligible: {R4.shape}")
    sc,sy,meta=scales(a.scales_json,c,o); manifest=json.loads(Path(a.run_manifest).read_text(encoding="utf-8")); evidence_eligible=bool(manifest.get("rank_claim_allowed",False)) and manifest.get("evidence_effect")=="ELIGIBLE_FOR_INDEPENDENT_RANK_AUDIT_ONLY" and not manifest.get("synthetic_jobs",[]); j,j2,j4=[J(x,sc,sy) for x in (R,R2,R4)]; U2,s2,V2,k2=decomp(j2); U4,s4,V4,k4=decomp(j4)
    eps_step=float(np.linalg.norm(j2-j4,2)); eps_solver=0.0; solver_source="none"
    if a.matrix_h4_refined:
        orf,crf,Rrf=read_matrix(a.matrix_h4_refined)
        if (orf,crf)!=(o,c): raise ValueError("refined matrix labels/order differ")
        eps_solver=float(np.linalg.norm(j4-J(Rrf,sc,sy),2)); solver_source="matrix_h4_refined"
    elif a.solver_refinement_epsilon is not None:
        eps_solver=max(0.0,float(a.solver_refinement_epsilon)); solver_source="explicit_scalar"
    epsJ=eps_step+eps_solver; rel=eps_step/max(1.0,float(np.linalg.norm(j4,2))); d1=float(np.linalg.norm(j-j2,2)); d2=eps_step; rich=d1/d2 if d2>0 else (4.0 if d1==0 else math.inf)
    sigmax=float(s4[0]); sigmin=float(s4[-1]); thr=a.formal_rel_tol*sigmax; rank=int(np.sum(s4>thr)); sep=sigmin/epsJ if epsJ>0 else (math.inf if sigmin>0 else 0.0); ang=angle(V2[-1],V4[-1])
    conv=rel<=a.deriv_rel_max; separated=rank==4 and sigmin>a.q*epsJ; cond=k4<=a.cond_max; direction=math.isfinite(ang) and ang<=a.angle_max_deg; refinement_present=(a.matrix_h4_refined is not None or a.solver_refinement_epsilon is not None)
    if not evidence_eligible: verdict,reason="SOFTWARE_QA_ONLY_NO_PHYSICAL_VERDICT","run manifest is not eligible for physical rank adjudication"
    elif not a.branch_ok: verdict,reason="NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT","external branch/physics gates not asserted"
    elif not refinement_present: verdict,reason="NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT","solver-tolerance refinement missing"
    elif not conv: verdict,reason="NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT","no stable step-refinement plateau"
    elif rank<4 and sigmin<=a.q*epsJ: verdict,reason="PHYSICAL_RESPONSE_RANK_DEFICIENT","converged normalized response robustly rank-deficient at benchmark"
    elif not separated: verdict,reason="NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT","sigma_4 not separated from empirical Jacobian uncertainty"
    elif not cond: verdict,reason="NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT","conditioning exceeds guardrail"
    elif not direction: verdict,reason="NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT","sigma_4 direction unstable"
    else: verdict,reason="PHYSICAL_RESPONSE_RANK_4_CONFIRMED","ULSH-01 numerical response-rank gate passed"
    out={"schema":"ulsh01.cphys.response-rank.audit.v1.3","status":"NUMERICAL_AUDIT_ONLY","governance":{"K1-D":"NOT_RELEASED","K1-E":"NOT_ADMISSIBLE"},"outputs":o,"controls":c,"shape":list(j4.shape),"normalization":{"formula":"J=Sy^{-1}RSc","control_scales":dict(zip(c,sc)),"output_scales":dict(zip(o,sy)),"metadata":meta},"refinement":{"relative_change_h2_h4":rel,"richardson_difference_ratio":rich,"epsilon_step":eps_step,"epsilon_solver":eps_solver,"epsilon_solver_source":solver_source,"epsilon_J":epsJ},"svd":{"singular_values":s4,"formal_rank":rank,"condition_number":k4,"sigma_4_over_epsilon_J":sep,"sigma_4_right_direction":V4[-1],"sigma_4_direction_angle_h2_h4_deg":ang},"run_manifest":{"rank_claim_allowed":manifest.get("rank_claim_allowed"),"evidence_effect":manifest.get("evidence_effect"),"synthetic_job_count":len(manifest.get("synthetic_jobs",[])),"evidence_eligible":evidence_eligible},"gates":{"branch_ok":a.branch_ok,"solver_refinement_present":refinement_present,"derivative_convergence_ok":conv,"rank4_uncertainty_separated":separated,"conditioning_ok":cond,"sigma_4_direction_stable":direction},"verdict":verdict,"reason":reason,"evidence_effect":"NONE_BEYOND_ULSH01_NUMERICAL_GATE"}
    text=json.dumps(clean(out),indent=2,ensure_ascii=False,allow_nan=False); print(text)
    if a.output: Path(a.output).write_text(text+"\n",encoding="utf-8")
if __name__=="__main__": main()
