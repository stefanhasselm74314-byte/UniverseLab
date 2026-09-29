#!/usr/bin/env python3
"""ULSH-01/C-PHYS physical response-rank auditor v1.2.

Input: R(h), R(h/2), R(h/4) as CSV and frozen normalization scales as JSON.
Audit matrix: J = Sy^{-1} R Sc.
This audits only the ULSH-01 response-rank gate; it does not release K1-D/K1-E.
"""
from __future__ import annotations
import argparse, csv, json, math
from pathlib import Path
import numpy as np


def read_matrix(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows=list(csv.reader(f))
    if len(rows)<2 or len(rows[0])<2: raise ValueError(f"Invalid matrix CSV: {path}")
    controls=[x.strip() for x in rows[0][1:]]
    outputs=[]; data=[]
    for row in rows[1:]:
        if len(row)!=len(controls)+1: raise ValueError(f"Row-width mismatch: {path}")
        outputs.append(row[0].strip())
        if any(x.strip()=="" for x in row[1:]): raise ValueError(f"Blank derivative: {path}")
        data.append([float(x) for x in row[1:]])
    return outputs,controls,np.asarray(data,float)


def read_scales(path,controls,outputs):
    obj=json.loads(Path(path).read_text(encoding="utf-8"))
    cm=obj.get("control_scales",{}); ym=obj.get("output_scales",{})
    if any(k not in cm for k in controls) or any(k not in ym for k in outputs):
        raise ValueError("Scale file does not cover every control/output.")
    sc=np.asarray([float(cm[k]) for k in controls]); sy=np.asarray([float(ym[k]) for k in outputs])
    if np.any(~np.isfinite(sc)) or np.any(~np.isfinite(sy)) or np.any(sc<=0) or np.any(sy<=0):
        raise ValueError("All frozen scales must be finite and >0.")
    return sc,sy,obj


def norm_j(R,sc,sy): return (R*sc[None,:])/sy[:,None]

def svd(J):
    # Reduced SVD is mandatory for the 4x5 response matrix.  With full_matrices=True,
    # Vt contains an additional exact domain-null direction because 5 controls > 4 outputs;
    # that direction is NOT the sigma_4 right-singular vector.
    U,s,Vt=np.linalg.svd(J,full_matrices=False)
    cond=float(s[0]/s[-1]) if len(s) and s[-1]>0 else math.inf
    return U,s,Vt,cond

def angle_deg(v,w):
    nv=np.linalg.norm(v); nw=np.linalg.norm(w)
    if nv==0 or nw==0: return math.nan
    z=abs(float(np.dot(v,w)/(nv*nw)))
    return float(np.degrees(np.arccos(np.clip(z,-1,1))))

def safe_json(x):
    if isinstance(x,dict): return {k:safe_json(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [safe_json(v) for v in x]
    if isinstance(x,np.ndarray): return safe_json(x.tolist())
    if isinstance(x,(np.floating,float)):
        v=float(x); return v if math.isfinite(v) else None
    if isinstance(x,np.integer): return int(x)
    return x


def main():
    p=argparse.ArgumentParser()
    p.add_argument("matrix_h"); p.add_argument("matrix_h2"); p.add_argument("matrix_h4"); p.add_argument("scales_json")
    p.add_argument("--q",type=float,default=5.0)
    p.add_argument("--cond-max",type=float,default=1e6)
    p.add_argument("--deriv-rel-max",type=float,default=1e-2)
    p.add_argument("--angle-max-deg",type=float,default=10.0)
    p.add_argument("--formal-rel-tol",type=float,default=1e-8)
    p.add_argument("--solver-refinement-epsilon",type=float,default=0.0)
    p.add_argument("--branch-ok",action="store_true")
    p.add_argument("--output")
    a=p.parse_args()

    o,c,Rh=read_matrix(a.matrix_h); o2,c2,Rh2=read_matrix(a.matrix_h2); o4,c4,Rh4=read_matrix(a.matrix_h4)
    if (o,c)!=(o2,c2) or (o,c)!=(o4,c4): raise ValueError("Labels/order differ across step sizes.")
    if Rh.shape[0]!=4: raise ValueError(f"Required target dimension is 4; got {Rh.shape}.")
    if Rh.shape[1]<4: raise ValueError(f"At least four continuous controls are required; got {Rh.shape}.")
    sc,sy,meta=read_scales(a.scales_json,c,o)
    Jh,Jh2,Jh4=[norm_j(R,sc,sy) for R in (Rh,Rh2,Rh4)]
    U2,s2,V2,k2=svd(Jh2); U4,s4,V4,k4=svd(Jh4)

    eps_step=float(np.linalg.norm(Jh2-Jh4,2))
    eps_solver=max(0.0,float(a.solver_refinement_epsilon))
    epsJ=eps_step+eps_solver
    rel_change=float(eps_step/max(1.0,np.linalg.norm(Jh4,2)))
    d1=float(np.linalg.norm(Jh-Jh2,2)); d2=float(np.linalg.norm(Jh2-Jh4,2))
    rich=d1/d2 if d2>0 else (4.0 if d1==0 else math.inf)
    sigmax=float(s4[0]); sigmin=float(s4[-1]); threshold=a.formal_rel_tol*sigmax
    rank=int(np.sum(s4>threshold))
    sep=sigmin/epsJ if epsJ>0 else (math.inf if sigmin>0 else 0.0)
    # V[-1] is now the right-singular vector associated with sigma_4, not the trivial 5D null vector.
    ang=angle_deg(V2[-1],V4[-1])

    converged=rel_change<=a.deriv_rel_max
    separated=(rank==4 and sigmin>a.q*epsJ)
    cond_ok=k4<=a.cond_max
    direction_ok=math.isfinite(ang) and ang<=a.angle_max_deg

    if not a.branch_ok:
        verdict="NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT"; reason="External branch/physics gates not asserted."
    elif not converged:
        verdict="NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT"; reason="No stable step-refinement plateau."
    elif rank<4 and sigmin<=a.q*epsJ:
        verdict="PHYSICAL_RESPONSE_RANK_DEFICIENT"; reason="Converged normalized response is robustly rank-deficient at this benchmark."
    elif not separated:
        verdict="NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT"; reason="sigma_4 is not separated from empirical Jacobian uncertainty."
    elif not cond_ok:
        verdict="NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT"; reason="Formal full rank but conditioning exceeds guardrail."
    elif not direction_ok:
        verdict="NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT"; reason="sigma_4 right-singular direction is unstable under refinement."
    else:
        verdict="PHYSICAL_RESPONSE_RANK_4_CONFIRMED"; reason="ULSH-01 numerical response-rank conditions passed."

    out={
      "schema":"ulsh01.cphys.response-rank.audit.v1.2","status":"NUMERICAL_AUDIT_ONLY",
      "governance":{"K1-D":"NOT_RELEASED","K1-E":"NOT_ADMISSIBLE"},
      "outputs":o,"controls":c,"shape":list(Jh4.shape),
      "normalization":{"formula":"J=Sy^{-1}RSc","control_scales":dict(zip(c,sc)),"output_scales":dict(zip(o,sy)),"metadata":meta},
      "refinement":{"relative_change_h2_h4":rel_change,"required_max":a.deriv_rel_max,"richardson_difference_ratio":rich,"epsilon_step":eps_step,"epsilon_solver":eps_solver,"epsilon_J":epsJ},
      "svd":{"singular_values":s4,"formal_rank":rank,"formal_threshold":threshold,"condition_number":k4,"condition_number_max":a.cond_max,"sigma_4_over_epsilon_J":sep,"required_q":a.q,"sigma_4_right_direction":V4[-1],"sigma_4_direction_angle_h2_h4_deg":ang,"angle_max_deg":a.angle_max_deg,"left_nullspace":U4[:,rank:]},
      "gates":{"branch_ok":a.branch_ok,"derivative_convergence_ok":converged,"rank4_uncertainty_separated":separated,"conditioning_ok":cond_ok,"sigma_4_direction_stable":direction_ok},
      "verdict":verdict,"reason":reason,"evidence_effect":"NONE_BEYOND_ULSH01_NUMERICAL_GATE"
    }
    text=json.dumps(safe_json(out),indent=2,ensure_ascii=False,allow_nan=False)
    if a.output: Path(a.output).write_text(text+"\n",encoding="utf-8")
    print(text)

if __name__=="__main__": main()
