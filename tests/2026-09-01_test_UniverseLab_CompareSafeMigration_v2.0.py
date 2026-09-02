#!/usr/bin/env python3
"""Static and independent numerical contract for Compare SAFE v2.0."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'compare-safe.html'
ADAPTER = ROOT / 'assets/2026-09-01_UniverseLab_CompareSafeAdapter_v2.0.js'
ENGINE = ROOT / 'assets/2026-09-01_UniverseLab_CosmologyEngine_v1.0.js'
CONTRACT = ROOT / 'registry/2026-09-01_UniverseLab_CompareSafeMigrationContract_v2.0.json'
LEDGER = ROOT / 'science/cosmology/2026-09-01_UniverseLab_CompareSafeMigration_v2.0.md'
OR = 9.2e-5
C_KM_S = 299792.458


def simpson(fn, a: float, b: float, n: int = 12000) -> float:
    if n % 2:
        n += 1
    h = (b-a)/n
    total = fn(a)+fn(b)
    for i in range(1,n):
        total += (4 if i%2 else 2)*fn(a+i*h)
    return total*h/3


def e2(z: float, om: float, ode: float) -> float:
    x=1+z
    ok=1-OR-om-ode
    return OR*x**4+om*x**3+ok*x**2+ode


def dc(z: float, h0: float, om: float, ode: float) -> float:
    return C_KM_S/h0*simpson(lambda x:1/math.sqrt(e2(x,om,ode)),0,z)


def dm(z: float, h0: float, om: float, ode: float) -> float:
    radial=dc(z,h0,om,ode)
    ok=1-OR-om-ode
    if abs(ok)<1e-14:
        return radial
    dh=C_KM_S/h0
    chi=math.sqrt(abs(ok))*radial/dh
    return dh/math.sqrt(ok)*math.sinh(chi) if ok>0 else dh/math.sqrt(-ok)*math.sin(chi)


def bridge_scale(rchi: float) -> float:
    if not rchi > 0:
        raise ValueError('Rchi must be positive')
    return rchi/(rchi+2.5)


def bridge_delta(z: float, beta: float, ib: float, rchi: float) -> float:
    a=1/(1+z)
    ac=bridge_scale(rchi)
    return beta*ib*math.exp(-(a/ac)**2)


def main() -> None:
    html=HTML.read_text(encoding='utf-8')
    adapter=ADAPTER.read_text(encoding='utf-8')
    engine=ENGINE.read_text(encoding='utf-8')
    contract=json.loads(CONTRACT.read_text(encoding='utf-8'))
    ledger=LEDGER.read_text(encoding='utf-8')

    assert '<title>UniverseLab · Vergleichsrechner SAFE</title>' in html
    assert '2026-09-01_UniverseLab_CosmologyEngine_v1.0.js' in html
    assert '2026-09-01_UniverseLab_CompareSafeAdapter_v2.0.js' in html
    assert 'data-ul-split-key="compare-safe"' in html
    assert '<canvas id="chart"></canvas>' in html
    assert 'id="w"' in html and 'disabled' in html
    for element_id in ('H0','Om','Ol','w','s8','beta','ib','rchi','z','ageL','ageB','dev1','S8','dc','dl','da','mu','chart','formula','reset','csv'):
        assert f'id="{element_id}"' in html, element_id
    for forbidden in ('function eL(', 'function eW(', 'function eB(', 'function simp(', 'function dc(', 'Math.sqrt(Math.max('):
        assert forbidden not in html, forbidden

    for required in (
        'C.validateBackgroundDomain','C.e2FromA','C.ageGyr','C.E','C.distanceModulus',
        'C.transverseComovingDistance','C.etheringtonRatio','C.bridgeScale','C.q',
        'INVALID_BACKGROUND_DOMAIN','INVALID_BRIDGE_DOMAIN','CSV_BLOCKED_INVALID_DOMAIN',
        'UNRELEASED_LENSING_MAP','globalThis.UniverseLabCompareSafe'
    ):
        assert required in adapter, required
    for forbidden in ('Math.sqrt(Math.max(', 'Math.max(.02', "C.solveGrowth(p,'bridge'"):
        assert forbidden not in adapter, forbidden
    assert 'UNRELEASED_GROWTH_MAP' in engine
    assert 'Math.max(0.02,p.Rchi)' not in engine
    assert 'function bridgeScale(p){return p.ac??p.Rchi/(p.Rchi+2.5);}' in engine

    assert contract['version']=='2.0.1'
    assert contract['status']=='ACTIVE_MERGED_QA_RECONCILED'
    assert contract['merged_pull_request']==199
    assert contract['models']['base']=='lcdm'
    assert contract['models']['bridge']=='bridge'
    assert contract['models']['bridge_base_w']==-1
    assert contract['models']['bridge_scale']=='a_c=Rchi/(Rchi+2.5) for Rchi>0'
    assert contract['models']['bridge_scale_hidden_floor'] is False
    reference=contract['background_contract']['reference_state']
    assert abs(reference['Omega_r']+reference['Omega_m']+reference['Omega_DE']+reference['Omega_k']-1)<1e-15
    assert contract['distance_contract']['chain']=='D_C_TO_D_M_TO_D_L_AND_D_A'
    assert contract['observable_firewalls']['bridge_growth']=='UNRELEASED_GROWTH_MAP'
    assert contract['observable_firewalls']['bridge_lensing']=='UNRELEASED_LENSING_MAP'
    assert contract['physical_gate_effect']=='NONE'
    assert contract['physical_evidence_effect']=='NONE'
    assert 'rang J_(βτ,𝓘B)≤1' in ledger

    # Product degeneracy: equal beta*I_B gives equal bridge background.
    for z in (0,.5,1,3,8):
        d1=bridge_delta(z,.05,.4,1)
        d2=bridge_delta(z,.1,.2,1)
        assert abs(d1-d2)<1e-15

    # Exact small-Rchi model contract and asymptotic, with no historical .02 floor.
    assert abs(bridge_scale(.02)-.02/2.52)<1e-16
    assert abs(bridge_scale(.01)-.01/2.51)<1e-16
    assert abs(bridge_scale(.01)-bridge_scale(.02))>1e-3
    assert abs(bridge_scale(1e-6)/1e-6-.4)<2e-7

    # Curved geometry must not identify D_C with D_M.
    z=2.33
    dc_open=dc(z,67.4,.2,.5)
    dm_open=dm(z,67.4,.2,.5)
    dc_closed=dc(z,67.4,.5,.8)
    dm_closed=dm(z,67.4,.5,.8)
    assert dm_open>dc_open and abs(dm_open/dc_open-1)>.01
    assert dm_closed<dc_closed and abs(dm_closed/dc_closed-1)>.01
    mu_old=5*math.log10((1+z)*dc_open)+25
    mu_new=5*math.log10((1+z)*dm_open)+25
    assert abs(mu_new-mu_old)>.05

    # Historical slider witness has an invalid real background domain.
    vals=[OR*(1+5*i/20000)**4+.1*(1+5*i/20000)**3+(1-OR-.1-1.2)*(1+5*i/20000)**2+1.2*(1+5*i/20000)**(3*(1-1.5)) for i in range(20001)]
    assert min(vals)<-.02

    # Bridge witness beta*I_B<-1 is invalid in the early-time limit.
    assert 1+bridge_delta(1e8,-3,1,1)<0

    print('UniverseLab Compare SAFE migration v2.0.1 static/numerical contract: PASS')


if __name__=='__main__':
    main()
