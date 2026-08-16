#!/usr/bin/env python3
"""Background3C5 full finite-thickness operator candidate v0.3.

G5 implementation-only library.  It extends the canonical bulk residuals with
parent-derived finite-thickness stress/scalar/amplitude terms and a conservative
Maxwell flux equation.  The dimensionless Maxwell source coefficient remains a
provenance gate and is NEVER assigned a default physical value.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
import numpy as np

Array=np.ndarray
PHYSICAL_EXECUTION_AUTHORIZED=False
PHYSICAL_EVIDENCE_EFFECT="NONE_IMPLEMENTATION_ONLY"
RANK_R_CLAIM_ALLOWED=False
G5_STATUS="PARTIAL_PASS_COEFFICIENT_BLOCKED"

@dataclass(frozen=True)
class Model:
    Lambda_hat: float
    mhat_phi_sq: float
    a_F: float
    k4: float

@dataclass(frozen=True)
class Sector:
    n: int
    m_layer: int
    q_hat: float
    @property
    def ghat_sigma(self)->float:
        return float(self.m_layer)*float(self.q_hat)

@dataclass(frozen=True)
class Layer:
    mhat_sigma_sq: Callable[[Array],Array]
    dmhat_sigma_sq_dvarphi: Callable[[Array],Array]
    lambdahat_sigma: float
    Lambda_hat_layer: Callable[[Array],Array]=lambda v: np.zeros_like(np.asarray(v,float))
    dLambda_hat_layer_dvarphi: Callable[[Array],Array]=lambda v: np.zeros_like(np.asarray(v,float))
    def V(self,v:Array,s:Array)->Array:
        return np.asarray(self.Lambda_hat_layer(v),float)+0.5*np.asarray(self.mhat_sigma_sq(v),float)*s**2+0.25*self.lambdahat_sigma*s**4
    def dV_ds(self,v:Array,s:Array)->Array:
        return np.asarray(self.mhat_sigma_sq(v),float)*s+self.lambdahat_sigma*s**3
    def dV_dvarphi(self,v:Array,s:Array)->Array:
        return np.asarray(self.dLambda_hat_layer_dvarphi(v),float)+0.5*np.asarray(self.dmhat_sigma_sq_dvarphi(v),float)*s**2

@dataclass(frozen=True)
class Profile:
    x:Array; A:Array; ell:Array; varphi:Array; s:Array; a_chi:Array

@dataclass(frozen=True)
class Residuals:
    E_A:Array; E_ell:Array; E_varphi:Array; E_s:Array; E_flux:Array; rr_constraint:Array

def d(y:Array,x:Array)->Array:
    return np.gradient(np.asarray(y,float),np.asarray(x,float),edge_order=2)

def validate(p:Profile)->None:
    arrays=[np.asarray(getattr(p,k),float) for k in ('x','A','ell','varphi','s','a_chi')]
    n=len(arrays[0])
    if n<5 or any(a.ndim!=1 or len(a)!=n or not np.all(np.isfinite(a)) for a in arrays): raise ValueError('invalid profile arrays')
    if np.any(np.diff(arrays[0])<=0) or np.any(arrays[0]<=0): raise ValueError('x must be positive/increasing; center uses series')
    if np.any(arrays[2]<=0): raise ValueError('ell must be positive away from axis')

def evaluate(p:Profile,model:Model,sector:Sector,layer:Layer,*,Gamma_Sigma:float|None=None)->Residuals:
    """Evaluate G5 candidate residuals.

    Gamma_Sigma=None is intentionally allowed for algebraic layer/stress QA, but
    then E_flux is returned as NaN and the result is not a closed operator.
    A finite Gamma_Sigma is only an explicit test value; passing one does NOT
    authorize physical execution or establish provenance.
    """
    validate(p); x=np.asarray(p.x,float); A=np.asarray(p.A,float); ell=np.asarray(p.ell,float); v=np.asarray(p.varphi,float); s=np.asarray(p.s,float); ach=np.asarray(p.a_chi,float)
    Ax=d(A,x); Axx=d(Ax,x); ex=d(ell,x); exx=d(ex,x); vx=d(v,x); vxx=d(vx,x); sx=d(s,x); sxx=d(sx,x); achx=d(ach,x)
    Z=np.exp(-2*model.a_F*v); e2A=np.exp(-2*A); w=sector.n-sector.ghat_sigma*ach
    Er=0.5*sx**2; Echi=0.5*s**2*w**2/ell**2; V=layer.V(v,s)
    # Gauge energy in conservative variables, valid independently of source coefficient.
    rhoF=0.5*Z*achx**2/ell**2
    EA=4*Axx+10*Ax**2-6*model.k4*e2A+model.Lambda_hat+0.5*vx**2+0.5*model.mhat_phi_sq*v**2-rhoF + Er-Echi+V
    Eell=exx+3*Axx*ell+6*Ax**2*ell+3*Ax*ex-3*model.k4*e2A*ell+model.Lambda_hat*ell+ell*(0.5*vx**2+0.5*model.mhat_phi_sq*v**2+rhoF+Er+Echi+V)
    Ev=ell*vxx+(4*Ax*ell+ex)*vx-ell*model.mhat_phi_sq*v+2*model.a_F*ell*rhoF-ell*layer.dV_dvarphi(v,s)
    Es=sxx+(4*Ax+ex/ell)*sx-(w**2/ell**2)*s-layer.dV_ds(v,s)
    P=np.exp(4*A)*Z*achx/ell
    if Gamma_Sigma is None:
        Eflux=np.full_like(x,np.nan)
    else:
        if not np.isfinite(Gamma_Sigma): raise ValueError('Gamma_Sigma must be finite')
        Eflux=d(P,x)+Gamma_Sigma*np.exp(4*A)*s**2*w/ell
    Crr=ell*(-6*model.k4*e2A+6*Ax**2+model.Lambda_hat)+4*Ax*ex-ell*(0.5*vx**2-0.5*model.mhat_phi_sq*v**2+rhoF)-ell*Er+ell*Echi+ell*V
    return Residuals(EA,Eell,Ev,Es,Eflux,Crr)

def maxwell_flux(A:Array,ell:Array,varphi:Array,a_chi_x:Array,a_F:float)->Array:
    return np.exp(4*np.asarray(A,float)-2*a_F*np.asarray(varphi,float))*np.asarray(a_chi_x,float)/np.asarray(ell,float)

def governance()->dict[str,object]:
    return {'G5':G5_STATUS,'physical_execution_authorized':PHYSICAL_EXECUTION_AUTHORIZED,'rank_R_claim_allowed':RANK_R_CLAIM_ALLOWED,'evidence_effect':PHYSICAL_EVIDENCE_EFFECT,'Gamma_Sigma':'OPEN_PROVENANCE_IDENTITY'}

if __name__=='__main__':
    raise SystemExit('implementation-only G5 library; physical execution is not authorized')
