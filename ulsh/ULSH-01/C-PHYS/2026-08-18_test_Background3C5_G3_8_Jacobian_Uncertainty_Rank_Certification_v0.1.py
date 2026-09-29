#!/usr/bin/env python3
import math
import numpy as np

Q = 5.0
COND_MAX = 1e6
DERIV_REL_MAX = 1e-2
ANGLE_MAX = 10.0
FORMAL_REL_TOL = 1e-8


def angle_deg(v, w):
    z = abs(float(np.dot(v, w) / (np.linalg.norm(v) * np.linalg.norm(w))))
    return float(np.degrees(np.arccos(np.clip(z, -1.0, 1.0))))


def certify(Jh, Jh2, Jh4, Jh4ref):
    eps_step = float(np.linalg.norm(Jh2 - Jh4, 2))
    eps_solver = float(np.linalg.norm(Jh4 - Jh4ref, 2))
    epsJ = eps_step + eps_solver
    rel = eps_step / max(1.0, float(np.linalg.norm(Jh4, 2)))
    U2, s2, Vh2 = np.linalg.svd(Jh2, full_matrices=False)
    U4, s4, Vh4 = np.linalg.svd(Jh4, full_matrices=False)
    sigmax = float(s4[0])
    sigmin = float(s4[-1])
    formal_rank = int(np.sum(s4 > FORMAL_REL_TOL * sigmax))
    cond = math.inf if sigmin == 0 else sigmax / sigmin
    angle = angle_deg(Vh2[-1], Vh4[-1])
    separated = sigmin > Q * epsJ
    return {
        "eps_step": eps_step,
        "eps_solver": eps_solver,
        "epsJ": epsJ,
        "rel": rel,
        "formal_rank": formal_rank,
        "cond": cond,
        "angle": angle,
        "separated": separated,
        "pass": rel <= DERIV_REL_MAX and formal_rank == 10 and separated and cond <= COND_MAX and angle <= ANGLE_MAX,
    }


def test_weyl_bound():
    rng = np.random.default_rng(7)
    A = rng.normal(size=(10, 10))
    E = 1e-4 * rng.normal(size=(10, 10))
    sA = np.linalg.svd(A, compute_uv=False)
    sB = np.linalg.svd(A + E, compute_uv=False)
    bound = np.linalg.norm(E, 2) + 1e-12
    assert np.all(np.abs(sA - sB) <= bound)


def test_certified_rank10_case():
    base = np.diag(np.linspace(2.0, 1.0, 10))
    E1 = np.diag(np.linspace(1e-3, 1e-4, 10))
    E2 = E1 / 4.0
    E3 = E2 / 4.0
    Jh = base + E1
    Jh2 = base + E2
    Jh4 = base + E3
    Jh4ref = Jh4 + np.eye(10) * 1e-7
    out = certify(Jh, Jh2, Jh4, Jh4ref)
    assert out["formal_rank"] == 10
    assert out["separated"]
    assert out["pass"]


def test_formal_rank_not_enough():
    base = np.diag([2.0] * 9 + [1e-5])
    Jh = base + np.eye(10) * 2e-5
    Jh2 = base + np.eye(10) * 1e-5
    Jh4 = base + np.eye(10) * 5e-6
    Jh4ref = Jh4 + np.eye(10) * 5e-6
    out = certify(Jh, Jh2, Jh4, Jh4ref)
    assert out["formal_rank"] == 10
    assert not out["separated"]
    assert not out["pass"]


def test_conditioning_firewall():
    base = np.diag([1.0] * 9 + [5e-7])
    Jh = base.copy(); Jh2 = base.copy(); Jh4 = base.copy(); Jh4ref = base.copy()
    out = certify(Jh, Jh2, Jh4, Jh4ref)
    assert out["formal_rank"] == 10
    assert out["cond"] > COND_MAX
    assert not out["pass"]


def test_rank_invariant_under_nonsingular_diagonal_scaling():
    rng = np.random.default_rng(11)
    A = rng.normal(size=(10, 10))
    while np.linalg.matrix_rank(A) < 10:
        A = rng.normal(size=(10, 10))
    Dr = np.diag(np.linspace(0.5, 2.0, 10))
    Du = np.diag(np.linspace(3.0, 0.7, 10))
    B = np.linalg.inv(Dr) @ A @ Du
    assert np.linalg.matrix_rank(A) == np.linalg.matrix_rank(B) == 10


if __name__ == "__main__":
    test_weyl_bound()
    test_certified_rank10_case()
    test_formal_rank_not_enough()
    test_conditioning_firewall()
    test_rank_invariant_under_nonsingular_diagonal_scaling()
    print("G3.8 Jacobian uncertainty/rank-certification QA: PASS")
