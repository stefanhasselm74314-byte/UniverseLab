#!/usr/bin/env python3
"""ULSH-01/C-PHYS Background-3C5 response orchestrator v1.0.
Evidence-neutral: invokes an external ratified BVP kernel; it does not solve 6D equations.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,subprocess
from datetime import datetime,timezone
from pathlib import Path

C=["Lambda6_over_Lambda_ref","Lambda_layer_over_Lambda_ref","mSigma2_over_mref2","gSigma","lambdaSigma"]
Y=["delta_beta_over_beta","delta_Xi","delta_U_umb","delta_m0sq_Rcap2"]
LEVELS=[("h",0),("h2",1),("h4",2)]

def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(o): return hashlib.sha256(canon(o)).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def dump(p,o): Path(p).parent.mkdir(parents=True,exist_ok=True); Path(p).write_text(json.dumps(o,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
def finite_map(name,o,keys):
    if any(k not in o for k in keys): raise ValueError(f"{name}: missing keys")
    if any(not isinstance(o[k],(int,float)) or not math.isfinite(float(o[k])) for k in keys): raise ValueError(f"{name}: non-finite value")
def validate_cfg(x):
    finite_map("baseline_controls",x.get("baseline_controls",{}),C); finite_map("perturbation_scales",x.get("perturbation_scales",{}),C)
    if any(float(x["perturbation_scales"][k])<=0 for k in C): raise ValueError("perturbation scales must be >0")
    b=x.get("branch",{});
    if not isinstance(b.get("winding_n"),int) or not isinstance(b.get("flux_N"),int): raise ValueError("branch labels must be integers")
    s=x.get("relative_steps",[])
    if len(s)!=3 or not math.isclose(s[1],s[0]/2,rel_tol=1e-12) or not math.isclose(s[2],s[0]/4,rel_tol=1e-12): raise ValueError("relative_steps must be [h,h/2,h/4]")
    cmd=x.get("solver_command",[]); joined=" ".join(cmd) if isinstance(cmd,list) else ""
    if not cmd or "{input}" not in joined or "{output}" not in joined: raise ValueError("solver_command requires {input} and {output}")
def payload(cfg,jid,controls,tol="nominal"):
    return {"schema":"ulsh01.background3c5.solver-input.v1","job_id":jid,"architecture":"HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01","evidence_mode":cfg.get("evidence_mode","SOFTWARE_QA_ONLY"),"branch":cfg["branch"],"controls":controls,"fields_required":["A","L","phi","s","A_chi"],"boundary_contract":{"center":{"L":0.0,"L_prime":1.0,"A_prime":0.0,"phi_prime":0.0,"s_if_n_nonzero":0.0},"outer":{"match_to_bulk":True,"scalar_layer_decay":True,"gauge_flux_quantization":True}},"solver_settings":cfg.get("solver_settings",{}).get(tol,{}),"tolerance_class":tol}
def validate_out(o,p):
    if o.get("schema")!="ulsh01.background3c5.solver-output.v1" or o.get("job_id")!=p["job_id"]: raise ValueError("solver output identity/schema mismatch")
    if o.get("input_sha256")!=sha(p): raise ValueError("input hash mismatch")
    if o.get("branch")!=p["branch"]: raise ValueError("discrete branch drift")
    if o.get("synthetic",False) and p["evidence_mode"] not in {"SOFTWARE_QA_ONLY","SYNTHETIC_SMOKE_ONLY"}: raise ValueError("synthetic output forbidden")
    finite_map("outputs",o.get("outputs",{}),Y); finite_map("diagnostics",o.get("diagnostics",{}),["m0_squared","residual_norm"])
    req=["converged","smooth_center","metric_scalar_gauge_matching","same_profile_node_class","continuation_trace_ok","conical_rescue_mode_used","reduced_kinetic_matrix_positive","off_shell_tube_valid"]
    if any(not isinstance(o.get("gates",{}).get(k),bool) for k in req): raise ValueError("missing/non-boolean physics gate")
def gate_ok(o):
    g=o["gates"]; d=o["diagnostics"]
    return g["converged"] and g["smooth_center"] and g["metric_scalar_gauge_matching"] and g["same_profile_node_class"] and g["continuation_trace_ok"] and not g["conical_rescue_mode_used"] and float(d["m0_squared"])>=0 and g["reduced_kinetic_matrix_positive"] and g["off_shell_tube_valid"]
def plan(cfg):
    base={k:float(cfg["baseline_controls"][k]) for k in C}; jobs=[payload(cfg,"baseline",base)]
    for label,i in LEVELS:
        h=float(cfg["relative_steps"][i])
        for c in C:
            d=h*float(cfg["perturbation_scales"][c])
            for sn,sgn in (("plus",1),("minus",-1)):
                cc=dict(base); cc[c]+=sgn*d; jobs.append(payload(cfg,f"{label}__{c}__{sn}",cc))
    if cfg.get("require_solver_tolerance_refinement",True):
        h=float(cfg["relative_steps"][2])
        for c in C:
            d=h*float(cfg["perturbation_scales"][c])
            for sn,sgn in (("plus",1),("minus",-1)):
                cc=dict(base); cc[c]+=sgn*d; jobs.append(payload(cfg,f"refined__h4__{c}__{sn}",cc,"refined"))
    return jobs
def execute(cfg,outdir,p,force):
    jp=outdir/"jobs"; ip=jp/f"{p['job_id']}.input.json"; op=jp/f"{p['job_id']}.output.json"; dump(ip,p)
    if op.exists() and not force:
        o=load(op); validate_out(o,p); return o
    cmd=[z.replace("{input}",str(ip.resolve())).replace("{output}",str(op.resolve())) for z in cfg["solver_command"]]
    q=subprocess.run(cmd,capture_output=True,text=True,timeout=cfg.get("timeout_seconds",3600)); dump(jp/f"{p['job_id']}.process.json",{"command":cmd,"returncode":q.returncode,"stdout":q.stdout,"stderr":q.stderr})
    if q.returncode!=0 or not op.exists(): raise RuntimeError(f"solver failed: {p['job_id']}")
    o=load(op); validate_out(o,p); return o
def matrix(r,cfg,level,prefix=""):
    label,i=LEVELS[level]; h=float(cfg["relative_steps"][i]); a=[[0.0]*len(C) for _ in Y]
    for j,c in enumerate(C):
        p=r[f"{prefix}{label}__{c}__plus"]["outputs"]; m=r[f"{prefix}{label}__{c}__minus"]["outputs"]; d=h*float(cfg["perturbation_scales"][c])
        for k,y in enumerate(Y): a[k][j]=(float(p[y])-float(m[y]))/(2*d)
    return a
def write_matrix(path,a):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["output"]+C)
        for y,row in zip(Y,a): w.writerow([y]+[f"{v:.17g}" for v in row])
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("config",type=Path); ap.add_argument("output_dir",type=Path); ap.add_argument("--dry-run",action="store_true"); ap.add_argument("--force",action="store_true"); a=ap.parse_args()
    cfg=load(a.config); validate_cfg(cfg); a.output_dir.mkdir(parents=True,exist_ok=True); jobs=plan(cfg)
    m={"schema":"ulsh01.background3c5.response-run-manifest.v1","status":"PLANNED" if a.dry_run else "RUNNING","created_utc":datetime.now(timezone.utc).isoformat(),"config_sha256":sha(cfg),"job_count":len(jobs),"perturbation_job_count":30,"solver_refinement_job_count":max(0,len(jobs)-31),"branch":cfg["branch"],"evidence_mode":cfg.get("evidence_mode","SOFTWARE_QA_ONLY"),"governance":{"K1-D":"NOT_RELEASED","K1-E":"NOT_ADMISSIBLE"},"jobs":[p["job_id"] for p in jobs]}; dump(a.output_dir/"manifest.json",m)
    if a.dry_run: dump(a.output_dir/"plan.json",jobs); print(json.dumps(m,indent=2)); return
    r={p["job_id"]:execute(cfg,a.output_dir,p,a.force) for p in jobs}; failed=[k for k,v in r.items() if not gate_ok(v)]; synthetic=[k for k,v in r.items() if v.get("synthetic",False)]
    for z in range(3): write_matrix(a.output_dir/f"R_{LEVELS[z][0]}.csv",matrix(r,cfg,z))
    if cfg.get("require_solver_tolerance_refinement",True): write_matrix(a.output_dir/"R_h4_refined.csv",matrix(r,cfg,2,"refined__"))
    allowed=not failed and not synthetic and cfg.get("evidence_mode")=="AUTHORIZED_PHYSICAL_RUN"; m.update({"status":"COMPLETED_SOFTWARE_QA_ONLY" if synthetic else ("COMPLETED_GATE_ELIGIBLE" if not failed else "COMPLETED_PHYSICS_GATE_FAILURE"),"failed_physics_gate_jobs":failed,"synthetic_jobs":synthetic,"rank_claim_allowed":allowed,"evidence_effect":"ELIGIBLE_FOR_INDEPENDENT_RANK_AUDIT_ONLY" if allowed else "NONE_SYNTHETIC_OR_QA"}); dump(a.output_dir/"manifest.json",m); print(json.dumps(m,indent=2))
if __name__=="__main__": main()
