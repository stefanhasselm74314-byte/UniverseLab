#!/usr/bin/env python3
"""Synthetic Background-3C5 v1.1 contract stub. SOFTWARE QA ONLY; never physical evidence."""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path

C=["Lambda6_over_Lambda_ref","Lambda_layer_over_Lambda_ref","mSigma2_over_mref2","q_hat","lambdaSigma"]
Y=["delta_beta_over_beta","delta_Xi","delta_U_umb","delta_m0sq_Rcap2"]
M=[[1.0,0.2,0.1,0.0,0.05],[0.1,1.2,0.3,0.2,0.0],[0.0,0.4,1.1,0.8,0.1],[0.1,0.0,0.5,0.2,1.3]]
def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def main():
    p=argparse.ArgumentParser(); p.add_argument("input"); p.add_argument("output"); a=p.parse_args()
    inp=json.loads(Path(a.input).read_text(encoding="utf-8"))
    M6=float(inp["M6"]); ml=int(inp["branch"]["m_layer"]); qhat=float(inp["controls"]["q_hat"])
    qref=qhat/M6; gsigma=ml*qref
    dc=inp.get("derived_couplings",{})
    if not math.isclose(float(dc.get("q_ref",math.nan)),qref,rel_tol=1e-12,abs_tol=1e-15): raise ValueError("q_ref derivation mismatch")
    if not math.isclose(float(dc.get("gSigma",math.nan)),gsigma,rel_tol=1e-12,abs_tol=1e-15): raise ValueError("gSigma charge-lattice mismatch")
    c=[float(inp["controls"][k]) for k in C]; y=[]
    for r,row in enumerate(M):
        lin=sum(v*x for v,x in zip(row,c)); nonlin=1e-3*sum((j+1)*x*x for j,x in enumerate(c))/(r+1); y.append(lin+nonlin)
    out={"schema":"ulsh01.background3c5.solver-output.v1.1","job_id":inp["job_id"],"input_sha256":hashlib.sha256(canon(inp)).hexdigest(),"synthetic":True,"branch":inp["branch"],"outputs":dict(zip(Y,y)),"gates":{"converged":True,"smooth_center":True,"metric_scalar_gauge_matching":True,"same_profile_node_class":True,"continuation_trace_ok":True,"conical_rescue_mode_used":False,"reduced_kinetic_matrix_positive":True,"off_shell_tube_valid":True,"charge_lattice_consistent":True},"diagnostics":{"m0_squared":1.0,"residual_norm":1e-12},"provenance":{"backend":"SYNTHETIC_CONTRACT_STUB_V1_1","physical_equations_solved":False,"gSigma":gsigma}}
    Path(a.output).write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__": main()
