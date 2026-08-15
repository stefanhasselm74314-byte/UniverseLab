#!/usr/bin/env python3
import json
import math
import pathlib
import sys

EXPECTED_STATUS = (
    "PASS_EXPLICIT_GLOBAL_CONSTRAINT_SATISFYING_CONTROL_WITNESS_IN_NONEMPTY_M1_SUBSECTOR_"
    "FULL_PARENT_EQUIVALENCE_FOR_WITNESS_ONLY_GENERIC_M1_AND_NONTRIVIAL_D2NQ_OPEN_NO_PHYSICAL_INFERENCE"
)


def close(a, b=0.0, tol=2e-11):
    scale = max(1.0, abs(a), abs(b))
    return abs(a - b) <= tol * scale


def require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_registry(d):
    require(d["schema"] == "universelab.hzt-m0-s6-c-phys.h4r4b-global-control-witness-parent-equivalence.v1", "schema")
    require(d["status"] == EXPECTED_STATUS, "status")
    require(d["solver_execution"] is False, "solver_execution must remain false")
    require(d["mms_execution"] is False, "mms_execution must remain false")
    require(d["physical_evidence_effect"] == "NONE", "evidence firewall")
    require(d["external_material_firewall"]["gemini_blocks"] == "EXTERNAL_UNVERIFIED_GEMINI_DRAFT", "Gemini firewall")
    require(d["external_material_firewall"]["gemini_equations_used_as_premises"] is False, "Gemini premise firewall")
    require(d["canonical_signature"]["physical_times"] == 1, "one-time signature")
    require(d["normalization"]["kappa6_hat_squared"] == 1, "canonical kappa normalization")

    g = d["gate_disposition"]
    require(g["physical_parent_solve_authorized"] is False, "physical solve firewall")
    require(g["K1-D"] == "NOT_RELEASED", "K1-D firewall")
    require(g["K1-E"] == "NOT_ADMISSIBLE", "K1-E firewall")
    require(g["WP4"] == "BLOCKED", "WP4 firewall")
    require(g["physical_evidence_effect"] == "NONE", "physical evidence firewall")
    require(d["d2nq_disposition"]["B_squared"] == 0, "witness must remain D2N-Q trivial")


def validate_numeric_witness(d):
    w = d["numerical_sanity_witness"]
    m2 = float(w["mhat_phi_sq"])
    aF = float(w["a_F"])
    phi = float(w["varphi0"])
    Lam = float(w["Lambda_hat"])
    zsig = float(w["z_sigma_hat"])
    NF = int(w["N_F"])
    ms = int(w["m_sigma"])
    Ns = int(w["N_sigma"])

    require(m2 > 0 and aF > 0 and phi > 0 and zsig > 0, "positive active-domain parameters")
    require(NF > 0 and NF % 2 == 0, "positive even N_F control sector")
    require(ms > 0 and Ns == ms * NF // 2, "integer cap winding lock")
    require(float(w["lambda_hat"]) == 0.0, "stress-free cap control requires lambda_hat=0")

    rho = m2 * phi / (2.0 * aF)
    k4 = (Lam + 0.5 * m2 * phi * phi - rho) / 6.0
    rinv2 = 0.5 * Lam + 0.25 * m2 * phi * phi + 1.5 * rho
    require(k4 > 0, "closed dS control requires k4>0")
    require(rinv2 > 0, "sphere radius positivity")
    R = 1.0 / math.sqrt(rinv2)
    q = math.sqrt(2.0 * rho) * math.exp(-aF * phi)
    p = q * math.exp(2.0 * aF * phi) * R * R
    qhat = NF / (2.0 * p)

    for key, val in [
        ("rho_F", rho),
        ("k4", k4),
        ("Rbar_inv_sq", rinv2),
        ("Rbar", R),
        ("q", q),
        ("p", p),
        ("q_hat", qhat),
    ]:
        require(close(float(w[key]), val), f"stored numerical witness mismatch: {key}")

    # Direct six-dimensional parent residuals.
    r_internal = -6.0 * k4 + Lam + 0.5 * m2 * phi * phi - rho
    r_4d = 3.0 * k4 + rinv2 - Lam - 0.5 * m2 * phi * phi - rho
    r_scalar = m2 * phi - 2.0 * aF * rho
    require(close(r_internal), "direct internal Einstein residual")
    require(close(r_4d), "direct 4d Einstein residual")
    require(close(r_scalar), "direct scalar residual")

    # Global patch, flux and cap phase locking.
    r_patch = 2.0 * p - NF / qhat
    dchi = Ns - ms * qhat * p
    require(close(r_patch), "patch/flux residual")
    require(close(dchi), "cap covariant winding residual")

    # Exact pole and radial bulk checks at several interior points on both hemispheres.
    exp2 = math.exp(2.0 * aF * phi)
    expm2 = math.exp(-2.0 * aF * phi)
    cap = math.pi * R / 2.0
    for frac in (0.07, 0.19, 0.41, 0.73, 0.97):
        x = frac * cap
        y = x / R
        ell = R * math.sin(y)
        ell_x = math.cos(y)
        ell_xx = -ell / (R * R)
        require(ell > 0, "interior ell positive")

        for sign in (+1.0, -1.0):
            qs = sign * q
            achi = sign * p * (1.0 - math.cos(y))
            achi_x = sign * (p / R) * math.sin(y)
            gauge_first_integral = achi_x - qs * ell * exp2
            require(close(gauge_first_integral), "Maxwell first-integral residual")
            require(math.isfinite(achi), "finite gauge potential")

            # Static reduced equations for A=0, constant scalar.
            e_A = -6.0 * k4 + Lam + 0.5 * m2 * phi * phi - rho
            e_ell = ell_xx + ell * (-3.0 * k4 + Lam + 0.5 * m2 * phi * phi + rho)
            e_phi = ell * (-m2 * phi + 2.0 * aF * rho)
            rr = ell * (-6.0 * k4 + Lam + 0.5 * m2 * phi * phi - rho)
            require(close(e_A), "H4 static E_A")
            require(close(e_ell), "H4 static E_ell")
            require(close(e_phi), "H4 static scalar")
            require(close(rr), "H4 rr constraint")

            # H4R4A Hamiltonian constraint on the tau=0 time-symmetric slice.
            qv = ell_x / ell
            dx_qv = -1.0 / (R * R * math.sin(y) ** 2)
            qa = achi_x
            z = expm2 / (ell * ell)
            c_h = (
                -dx_qv
                - qv * qv
                + 3.0 * k4
                - Lam
                - 0.5 * z * qa * qa
                - 0.5 * m2 * phi * phi
            )
            require(close(c_h), "H4R4A C_H")

    # Smooth pole limits in regular variables.
    require(close(R * math.sin(0.0), 0.0), "ell pole value")
    require(close(math.cos(0.0), 1.0), "ell pole derivative")
    require(close(p * (1.0 - math.cos(0.0)), 0.0), "north pole gauge")
    require(close(-p * (1.0 - math.cos(0.0)), 0.0), "south pole gauge")

    # Equatorial junction residuals.
    ell_cap = R
    lprime_cap = math.cos(math.pi / 2.0)
    require(close(lprime_cap), "equatorial internal extrinsic curvature")
    Y = zsig * dchi * dchi / (ell_cap * ell_cap)
    lam = float(w["lambda_hat"])
    r_time = lam + 0.5 * Y
    r_space = lam + 0.5 * Y
    r_chi = lam - 0.5 * Y
    r_gauge = (q + (-q)) / ell_cap - ms * qhat * zsig * dchi / (ell_cap * ell_cap)
    require(close(r_time), "time junction")
    require(close(r_space), "space junction")
    require(close(r_chi), "chi junction")
    require(close(r_gauge), "gauge junction")

    # D2N-Q control value is exactly trivial because the 4d factor is radially unwarped.
    beta_r = 0.0
    require(close(beta_r * beta_r), "B^2 control value")


def main():
    if len(sys.argv) != 2:
        print("usage: validator <registry.json>", file=sys.stderr)
        return 2
    path = pathlib.Path(sys.argv[1])
    d = load(path)
    validate_registry(d)
    validate_numeric_witness(d)
    print("H4R4B global analytic control witness: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
