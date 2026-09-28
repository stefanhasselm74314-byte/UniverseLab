from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry/2026-09-08_UniverseLab_ULSH05_WP1C4B2B_ComponentBoundaryResidualLinearization_v0.1.json"
DOC = ROOT / "science/solver-hub/2026-09-08_UniverseLab_ULSH05_WP1C4B2B_ComponentBoundaryResidualLinearization_v0.1.md"


def close(a: float, b: float, *, atol: float = 5e-7, rtol: float = 5e-6) -> None:
    scale = max(1.0, abs(a), abs(b))
    assert abs(a - b) <= atol + rtol * scale, (a, b, a - b)


def test_contract() -> None:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    doc = DOC.read_text(encoding="utf-8")
    assert reg["work_package"] == "ULSH-05/WP1C4B2B"
    assert reg["basis_main"] == "5a5545ed80a94e99e7c466e5b30919dc47f86d6d"
    assert reg["physical_gate_effect"] == "NONE"
    assert reg["physical_evidence_effect"] == "NONE"
    assert reg["solver_authorized"] is False
    gates = reg["gate_state"]
    assert gates["WP1_boundary_residual_linearizations"] == "COMPONENTIZED_LOCAL_INTERFACE_OPERATOR"
    assert gates["WP1_local_weak_boundary_hessian"] == "SYMMETRIC_ON_DECLARED_TEST_DOMAIN"
    assert gates["WP1_full_global_boundary_hessian"] == "NOT_CLOSED_PHYSICAL_BC_AND_GLOBAL_CORNER_ADMISSIBILITY_OPEN"
    assert gates["WP1_full_quadratic_action"] == "NOT_CLOSED"
    assert gates["PERTURBED_JUNCTION_SYSTEM"] == "NOT_RELEASED"
    assert gates["PHYSICAL_BACKGROUND"] == "NOT_ESTABLISHED"
    assert gates["BACKEND_IMPORT"] == "NOT_EXECUTED"
    assert gates["SOLVER_EXECUTION"] == "NOT_EXECUTED"
    assert gates["K1-D"] == "NOT_RELEASED"
    assert gates["K1-E"] == "NOT_ADMISSIBLE"
    for token in (
        "Delta\\mathcal R_\\sigma",
        "Delta\\mathcal R_\\perp",
        "SYMMETRIC_ON_DECLARED_TEST_DOMAIN",
        "NOT_CLOSED_PHYSICAL_BC_AND_GLOBAL_CORNER_ADMISSIBILITY_OPEN",
        "kompaktem Support",
        "2*pi",
        "Israel wurde nicht",
    ):
        assert token in doc, token


def test_phase_residual_linearization() -> None:
    Z = 1.7
    x = 0.37

    def H(x: float) -> float:
        return 0.2 + 0.1 * x

    def Hp(x: float) -> float:
        return 0.1

    def w(x: float) -> float:
        return 0.3 + 0.4 * x

    def wp(x: float) -> float:
        return 0.4

    def d(x: float) -> float:
        return -0.2 + 0.05 * x * x

    def dp(x: float) -> float:
        return 0.1 * x

    def direct(eps: float) -> float:
        h = 1.0 + eps * H(x)
        hx = eps * Hp(x)
        we = w(x) + eps * d(x)
        wex = wp(x) + eps * dp(x)
        return Z * (wex / h - 0.5 * hx * we / (h * h))

    eps = 2e-6
    fd = (direct(eps) - direct(-eps)) / (2.0 * eps)
    analytic = Z * (dp(x) - H(x) * wp(x) - 0.5 * Hp(x) * w(x))
    close(fd, analytic, atol=2e-8, rtol=2e-7)


def test_gauss_shape_kernel() -> None:
    h = [-1.2, 1.1, 0.95, 1.3, 0.8]
    H = [0.07, -0.03, 0.02, 0.05, -0.01]
    K = [0.4, -0.2, 0.3, 0.1, -0.15]
    k = [0.05, 0.02, -0.04, 0.03, 0.01]

    def q_of(eps: float) -> float:
        he = [hi + eps * Hi for hi, Hi in zip(h, H)]
        Ke = [Ki + eps * ki for Ki, ki in zip(K, k)]
        Ktr = sum(Ki / hi for Ki, hi in zip(Ke, he))
        KabKab = sum((Ki / hi) ** 2 for Ki, hi in zip(Ke, he))
        return Ktr * Ktr - KabKab

    eps = 1e-6
    fd = (q_of(eps) - q_of(-eps)) / (2.0 * eps)
    hinv = [1.0 / hi for hi in h]
    Ktr = sum(Ki / hi for Ki, hi in zip(K, h))
    Kupper = [Ki / (hi * hi) for Ki, hi in zip(K, h)]
    Piupper = [Kuu - Ktr * inv for Kuu, inv in zip(Kupper, hinv)]
    Hupper = [Hi / (hi * hi) for Hi, hi in zip(H, h)]
    term_k = -2.0 * sum(Pi * ki for Pi, ki in zip(Piupper, k))
    term_H = 2.0 * sum(
        Huu * (Ki * Ki / hi - Ktr * Ki)
        for Huu, Ki, hi in zip(Hupper, K, h)
    )
    close(fd, term_k + term_H, atol=2e-8, rtol=2e-7)


def test_static_m1_matter_tnn_linearization() -> None:
    h = [-1.2, 1.1, 0.95, 1.3, 0.8]
    H = [0.03, -0.02, 0.015, 0.025, -0.01]
    q = 0.7
    dq = -0.12
    phi = 0.4
    Phi = 0.07
    m2 = 0.8
    aF = 0.3
    E = [0.0, 0.22, 0.0, -0.09, 0.05]
    e = [0.0, -0.03, 0.0, 0.02, -0.01]

    def tnn(eps: float) -> float:
        he = [hi + eps * Hi for hi, Hi in zip(h, H)]
        inv = [1.0 / hi for hi in he]
        qe = q + eps * dq
        ph = phi + eps * Phi
        Z = math.exp(-2.0 * aF * ph)
        Ee = [Ei + eps * ei for Ei, ei in zip(E, e)]
        E2 = sum(inv_i * Ei * Ei for inv_i, Ei in zip(inv, Ee))
        U = 0.5 * m2 * ph * ph
        return 0.5 * qe * qe - U + 0.5 * Z * E2

    eps = 1e-6
    fd = (tnn(eps) - tnn(-eps)) / (2.0 * eps)
    inv = [1.0 / hi for hi in h]
    Hupper = [Hi / (hi * hi) for Hi, hi in zip(H, h)]
    Z = math.exp(-2.0 * aF * phi)
    Zphi = -2.0 * aF * Z
    E2 = sum(inv_i * Ei * Ei for inv_i, Ei in zip(inv, E))
    DeltaQ = [
        Zphi * Phi * Ei / hi + Z * ei / hi - Z * Ei * Hi / (hi * hi)
        for Ei, ei, hi, Hi in zip(E, e, h, H)
    ]
    scalar = q * dq - (m2 * phi) * Phi
    maxwell = (
        sum(Ei * dQi for Ei, dQi in zip(E, DeltaQ))
        + 0.5 * Z * sum(Huu * Ei * Ei for Huu, Ei in zip(Hupper, E))
        - 0.5 * Zphi * Phi * E2
    )
    close(fd, scalar + maxwell, atol=2e-8, rtol=2e-7)


def cap_D2(h, q, w, d, lam, Z):
    inv = [1.0 / x for x in h]
    qup = [qi / (hi * hi) for qi, hi in zip(q, h)]
    qtrace = sum(qi / hi for qi, hi in zip(q, h))
    q2 = sum((qi / hi) ** 2 for qi, hi in zip(q, h))
    rupper = [(qi * qi) / (hi ** 3) for qi, hi in zip(q, h)]
    wup = [wi / hi for wi, hi in zip(w, h)]
    X0 = sum(wi * wui for wi, wui in zip(w, wup))
    X1 = 2.0 * sum(wui * di for wui, di in zip(wup, d)) - sum(
        qui * wi * wi for qui, wi in zip(qup, w)
    )
    X2 = (
        sum(inv_i * di * di for inv_i, di in zip(inv, d))
        - 2.0 * sum(qui * wi * di for qui, wi, di in zip(qup, w, d))
        + sum(rui * wi * wi for rui, wi in zip(rupper, w))
    )
    l0 = -lam - 0.5 * Z * X0
    l1 = -0.5 * Z * X1
    l2 = -0.5 * Z * X2
    n1 = 0.5 * qtrace
    n2 = qtrace * qtrace / 8.0 - q2 / 4.0
    return l2 + n1 * l1 + n2 * l0


def test_mixed_cap_hessian_symmetry_and_normalization() -> None:
    h = [-1.2, 1.1, 0.95, 1.3, 0.8]
    w = [0.0, 0.21, -0.08, 0.04, 0.12]
    q1 = [0.04, -0.02, 0.01, 0.03, -0.015]
    d1 = [0.0, -0.03, 0.02, 0.01, -0.01]
    q2 = [-0.015, 0.025, -0.02, 0.01, 0.03]
    d2 = [0.0, 0.015, -0.01, 0.025, 0.005]
    lam = 0.6
    Z = 1.4

    def density(eps: float, eta: float) -> float:
        he = [hi + eps * a + eta * b for hi, a, b in zip(h, q1, q2)]
        we = [wi + eps * a + eta * b for wi, a, b in zip(w, d1, d2)]
        det = 1.0
        for hi in he:
            det *= hi
        assert det < 0.0
        sqrt_minus_h = math.sqrt(-det)
        X = sum((wi * wi) / hi for wi, hi in zip(we, he))
        return sqrt_minus_h * (-lam - 0.5 * Z * X)

    eps = 3e-5
    eta = 2e-5
    mixed_fd = (
        density(eps, eta)
        - density(eps, -eta)
        - density(-eps, eta)
        + density(-eps, -eta)
    ) / (4.0 * eps * eta)

    q12 = [a + b for a, b in zip(q1, q2)]
    d12 = [a + b for a, b in zip(d1, d2)]
    D2_1 = cap_D2(h, q1, w, d1, lam, Z)
    D2_2 = cap_D2(h, q2, w, d2, lam, Z)
    D2_12 = cap_D2(h, q12, w, d12, lam, Z)
    det0 = 1.0
    for hi in h:
        det0 *= hi
    analytic_mixed = math.sqrt(-det0) * (D2_12 - D2_1 - D2_2)
    close(mixed_fd, analytic_mixed, atol=2e-6, rtol=2e-5)

    D2_21 = cap_D2(
        h,
        [b + a for a, b in zip(q1, q2)],
        w,
        [b + a for a, b in zip(d1, d2)],
        lam,
        Z,
    )
    analytic_swapped = math.sqrt(-det0) * (D2_21 - D2_2 - D2_1)
    close(analytic_mixed, analytic_swapped, atol=1e-12, rtol=1e-12)


if __name__ == "__main__":
    test_contract()
    test_phase_residual_linearization()
    test_gauss_shape_kernel()
    test_static_m1_matter_tnn_linearization()
    test_mixed_cap_hessian_symmetry_and_normalization()
    print("WP1C4B2B standalone controls: PASS")
