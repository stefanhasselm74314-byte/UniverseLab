#!/usr/bin/env python3
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1C4A_GluingNormalFluxJunctions_v0.1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def central_first(fn, h=1e-6):
    return (fn(h) - fn(-h)) / (2.0 * h)


def assert_close(a, b, tol=2e-9):
    assert math.isclose(a, b, rel_tol=tol, abs_tol=tol), (a, b, a-b)


def test_contract_and_scope():
    c = load(REG)
    assert c["model_id"] == "HZT-M0-S6-C-PHYS-M1"
    assert c["work_package"] == "ULSH-05/WP1C4A"
    assert c["physical_gate_effect"] == "NONE"
    assert c["physical_evidence_effect"] == "NONE"
    assert c["solver_authorized"] is False
    assert c["interface_identification"]["equivalent_constraint"] == "xi_N+xi_S=0"
    assert c["gate_state"]["WP1_two_side_bending_glue"] == "DERIVED"
    assert c["gate_state"]["PERTURBED_JUNCTION_SYSTEM"] == "NOT_RELEASED"


def test_two_side_gluing_from_common_coordinate():
    rhoN, rhoS, xi = 2.3, 1.7, 0.41
    # Common physical y points N -> S.
    rN = lambda y: rhoN + y
    rS = lambda y: rhoS - y
    drN_dy = central_first(rN)
    drS_dy = central_first(rS)
    assert_close(drN_dy, +1.0)
    assert_close(drS_dy, -1.0)
    # Regional outward normals are +partial_r_s. Same physical displacement y=eps*xi.
    xiN = drN_dy * xi
    xiS = drS_dy * xi
    assert_close(xiN, +xi)
    assert_close(xiS, -xi)
    assert_close(xiN + xiS, 0.0)


def test_scalar_normal_flux_moving_pullback():
    rhoN, rhoS, xi = 1.4, 0.9, 0.27
    aN, bN, cN = 0.8, -0.31, 0.22
    aS, bS, cS = -0.5, 0.43, -0.17

    # phibar=a*r+1/2*b*r^2, varphi=c*r; n_s=+partial_r_s.
    def flux(eps, rho, xis, a, b, c):
        r = rho + eps * xis
        return a + b*r + eps*c

    dN = central_first(lambda e: flux(e, rhoN, +xi, aN, bN, cN))
    dS = central_first(lambda e: flux(e, rhoS, -xi, aS, bS, cS))
    assert_close(dN, cN + xi*bN)
    assert_close(dS, cS - xi*bS)


def test_gauge_flux_moving_pullback():
    rhoN, rhoS, xi = 1.2, 1.6, 0.19

    # Direct regional intrinsic flux model Q(eps,r)=Qbar(r)+eps*q1(r).
    def Qbar(r, A, B, C):
        return A + B*r + 0.5*C*r*r

    def q1(r, D, E):
        return D + E*r

    parsN = (0.7, -0.2, 0.13, 0.09, -0.04)
    parsS = (-0.4, 0.31, -0.08, -0.12, 0.06)

    def full(eps, rho, xis, pars):
        A,B,C,D,E = pars
        r = rho + eps*xis
        return Qbar(r,A,B,C) + eps*q1(r,D,E)

    for rho, xis, pars in ((rhoN,+xi,parsN),(rhoS,-xi,parsS)):
        A,B,C,D,E = pars
        fd = central_first(lambda e: full(e,rho,xis,pars))
        expected = q1(rho,D,E) + xis*(B+C*rho)
        assert_close(fd, expected)


def test_cap_current_variation_and_u1_invariance():
    qsig, zsig = 1.7, 0.83
    hdiag = [-1.0, 1.2, 0.9, 1.5, 3.0]
    Hdiag = [0.04, -0.03, 0.02, 0.01, 0.07]
    w = [0.11, -0.2, 0.07, 0.15, 0.42]
    ds = [0.09, -0.04, 0.03, 0.05, -0.08]
    avec = [-0.02, 0.01, 0.04, -0.03, 0.02]
    dalpha = [0.03, -0.05, 0.02, 0.07, -0.01]

    d_before = [x-qsig*y for x,y in zip(ds,avec)]
    ds2 = [x+qsig*da for x,da in zip(ds,dalpha)]
    a2 = [x+da for x,da in zip(avec,dalpha)]
    d_after = [x-qsig*y for x,y in zip(ds2,a2)]
    for x,y in zip(d_before,d_after):
        assert_close(x,y,1e-12)

    # Diagonal control of delta j^a=q Z [hbar^{ab}d_b-H^{ab}w_b].
    hinv = [1.0/x for x in hdiag]
    Hup = [(hi*hi)*H for hi,H in zip(hinv,Hdiag)]
    analytic = [qsig*zsig*(hi*d-Hu*wi) for hi,d,Hu,wi in zip(hinv,d_before,Hup,w)]

    def current(eps):
        h = [hb+eps*H for hb,H in zip(hdiag,Hdiag)]
        win = [wi+eps*di for wi,di in zip(w,d_before)]
        return [qsig*zsig*wi/hi for wi,hi in zip(win,h)]

    for i in range(5):
        fd = central_first(lambda e, i=i: current(e)[i])
        assert_close(fd, analytic[i], 3e-9)


def test_upstream_and_firewalls():
    for rel in [
        "registry/2026-09-07_UniverseLab_ULSH05_WP1C2_FixedInterfaceCapHessian_v0.1.json",
        "registry/2026-09-07_UniverseLab_ULSH05_WP1C3_CapBendingJunctionGeometry_v0.1.json",
        "registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json"
    ]:
        assert (ROOT/rel).is_file(), rel
    g = load(REG)["gate_state"]
    expected = {
        "WP1_full_boundary_hessian":"NOT_CLOSED",
        "WP1_full_quadratic_action":"NOT_CLOSED",
        "PERTURBED_JUNCTION_SYSTEM":"NOT_RELEASED",
        "PHYSICAL_BACKGROUND":"NOT_ESTABLISHED",
        "FM-G0":"OPEN",
        "AuthorizationDecision":"NOT_CREATED",
        "SingleUseGrant":"NOT_CREATED",
        "BACKEND_IMPORT":"NOT_EXECUTED",
        "SOLVER_EXECUTION":"NOT_EXECUTED",
        "PHYSICAL_RESPONSE_RANK":"NOT_EXECUTED",
        "K1-D":"NOT_RELEASED",
        "K1-E":"NOT_ADMISSIBLE"
    }
    for k,v in expected.items(): assert g[k] == v, (k,g[k],v)


def main():
    tests=[
        test_contract_and_scope,
        test_two_side_gluing_from_common_coordinate,
        test_scalar_normal_flux_moving_pullback,
        test_gauge_flux_moving_pullback,
        test_cap_current_variation_and_u1_invariance,
        test_upstream_and_firewalls
    ]
    for fn in tests:
        fn(); print(f"PASS: {fn.__name__}")
    print("PASS: ULSH-05 WP1C4A gluing and normal-flux junctions v0.1")

if __name__ == "__main__": main()
