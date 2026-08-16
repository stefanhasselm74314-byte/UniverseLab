#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, pathlib, sys
import numpy as np

HERE=pathlib.Path(__file__).resolve().parent
TARGET=HERE/'2026-08-16_hzt_background3c5_full_operator_candidate_v0.3.py'
spec=importlib.util.spec_from_file_location('g5op',TARGET); m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)

def layer_zero():
    z=lambda v: np.zeros_like(np.asarray(v,float))
    return m.Layer(z,z,0.0,z,z)

def main():
    # Governance must remain fail-closed.
    g=m.governance(); assert g['physical_execution_authorized'] is False; assert g['rank_R_claim_allowed'] is False; assert g['Gamma_Sigma']=='OPEN_PROVENANCE_IDENTITY'
    # Smooth synthetic profile, used only for algebraic identities.
    x=np.linspace(0.1,1.0,64); A=0.03*x*x; ell=x+0.01*x**3; v=0.2+0.02*x*x; ach=0.04*x*x
    p0=m.Profile(x,A,ell,v,np.zeros_like(x),ach); model=m.Model(0.2,0.7,0.3,0.01); sec=m.Sector(1,2,0.4)
    r0=m.evaluate(p0,model,sec,layer_zero(),Gamma_Sigma=0.0)
    # With s=0 and V_layer=0, layer equation and Maxwell source vanish; P derivative is the only gauge residual.
    assert np.max(np.abs(r0.E_s))<1e-12
    # Explicit no-coefficient call must refuse closure by returning NaN flux residual.
    rn=m.evaluate(p0,model,sec,layer_zero(),Gamma_Sigma=None); assert np.all(np.isnan(rn.E_flux))
    # Charge lattice identity.
    assert abs(sec.ghat_sigma-sec.m_layer*sec.q_hat)<1e-15
    # Stress sign regression: constant nonzero s, flat layer potential; compare against layer-off at same geometry.
    const=lambda v: np.full_like(np.asarray(v,float),0.6); zero=lambda v: np.zeros_like(np.asarray(v,float))
    lay=m.Layer(const,zero,0.5,zero,zero); s=np.full_like(x,0.15); p=m.Profile(x,A,ell,v,s,ach)
    r=m.evaluate(p,model,sec,lay,Gamma_Sigma=0.0)
    V=0.5*0.6*s**2+0.25*0.5*s**4; w=sec.n-sec.ghat_sigma*ach; Echi=0.5*s**2*w**2/ell**2
    # Er=0 for constant s. Exact Einstein insertion signs.
    assert np.max(np.abs((r.E_A-r0.E_A)-(-Echi+V)))<2e-10
    assert np.max(np.abs((r.E_ell-r0.E_ell)-ell*(Echi+V)))<2e-10
    assert np.max(np.abs((r.rr_constraint-r0.rr_constraint)-ell*(Echi+V)))<2e-10
    # Conservative bulk flux identity: choose a_chi_x from frozen first integral => P=q_s.
    qs=0.37; achx=qs*ell*np.exp(-4*A+2*model.a_F*v); P=m.maxwell_flux(A,ell,v,achx,model.a_F)
    assert np.max(np.abs(P-qs))<1e-12
    print('G5 operator candidate v0.3 regression QA: PASS (software/algebra only)')

if __name__=='__main__': main()
