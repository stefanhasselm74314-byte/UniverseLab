#!/usr/bin/env python3
import importlib.util
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools/2026-08-13_validate_hzt_m0_s6_c_phys_parent_adm_d2nq_recheck_v0.1.py"


def close(a, b, tol=1e-12):
    if abs(a - b) > tol * max(1.0, abs(a), abs(b)):
        raise AssertionError(f"{a} != {b}")


def load_validator():
    spec = importlib.util.spec_from_file_location("parent_recheck_validator", VALIDATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_registry_and_source_bindings():
    result = load_validator().validate()
    assert result["status"] == "PASS"
    assert result["K1-D"] == "NOT_RELEASED"
    assert result["K1-E"] == "NOT_ADMISSIBLE"


def test_d5_adm_momentum_inverse_and_dewitt_factor():
    # Euclidean spatial metric h_ab=delta_ab, sqrt(h)=1, M6=2.
    d = 5
    M6 = 2.0
    M64 = M6 ** 4
    K = [
        [0.31, 0.02, 0.00, -0.01, 0.00],
        [0.02, -0.17, 0.03, 0.00, 0.01],
        [0.00, 0.03, 0.11, 0.02, 0.00],
        [-0.01, 0.00, 0.02, 0.07, -0.04],
        [0.00, 0.01, 0.00, -0.04, -0.09],
    ]
    Ktr = sum(K[i][i] for i in range(d))
    pi = [[0.5 * M64 * (K[i][j] - (Ktr if i == j else 0.0)) for j in range(d)] for i in range(d)]
    pitr = sum(pi[i][i] for i in range(d))
    close(pitr, -2.0 * M64 * Ktr)

    Krec = [[2.0 / M64 * (pi[i][j] - ((pitr / 4.0) if i == j else 0.0)) for j in range(d)] for i in range(d)]
    for i in range(d):
        for j in range(d):
            close(Krec[i][j], K[i][j])

    Ksq = sum(K[i][j] * K[i][j] for i in range(d) for j in range(d))
    pisq = sum(pi[i][j] * pi[i][j] for i in range(d) for j in range(d))
    lhs = 2.0 / M64 * (pisq - pitr * pitr / 4.0)
    rhs = 0.5 * M64 * (Ksq - Ktr * Ktr)
    close(lhs, rhs)


def q_tensor_for_alpha_beta(alpha, beta):
    # Orthonormal 4D frame, g=diag(-1,1,1,1), positive normal metric.
    gdiag = [-1.0, 1.0, 1.0, 1.0]
    Q = [[0.0 for _ in range(4)] for _ in range(4)]
    for a, b in zip(alpha, beta):
        Kcov = [a, b, b, b]  # diagonal K_mn
        Ktrace = sum(gdiag[mu] * Kcov[mu] for mu in range(4))
        Kcontract = sum(Kcov[mu] * Kcov[mu] for mu in range(4))
        scalar = Ktrace * Ktrace - Kcontract
        for mu in range(4):
            # For diagonal components, K_{mu rho} K_mu^{ rho} = g^{mu mu} K_mumu^2.
            second = gdiag[mu] * Kcov[mu] * Kcov[mu]
            Q[mu][mu] += Ktrace * Kcov[mu] - second - 0.5 * gdiag[mu] * scalar
    return Q


def test_flrw_gauss_q_identity():
    alpha = [-0.7, 0.13]
    beta = [0.7, 0.26]
    Q = q_tensor_for_alpha_beta(alpha, beta)
    B2 = sum(b * b for b in beta)
    adotb = sum(a * b for a, b in zip(alpha, beta))
    close(Q[0][0], 3.0 * B2)
    expected_spatial = 2.0 * adotb - B2
    for i in (1, 2, 3):
        close(Q[i][i], expected_spatial)


def test_d2nq_orthogonal_lambda_plus_dust_realization():
    BL = 0.73
    Bm = 0.41
    a_scale = 2.3
    beta = [BL, Bm * a_scale ** (-1.5)]
    alpha = [-BL, 0.5 * Bm * a_scale ** (-1.5)]
    B2 = sum(x * x for x in beta)
    expected_B2 = BL * BL + Bm * Bm * a_scale ** (-3.0)
    close(B2, expected_B2)

    M4 = 3.2
    rho = 3.0 * M4 * M4 * B2
    p = M4 * M4 * (2.0 * sum(x * y for x, y in zip(alpha, beta)) - B2)
    close(rho, 3.0 * M4 * M4 * (BL * BL + Bm * Bm * a_scale ** (-3.0)))
    close(p, -3.0 * M4 * M4 * BL * BL)


def test_source_free_codazzi_special_components():
    H = 0.071
    bL = 0.9
    aL = -bL
    dbL = 0.0
    close(dbL + H * (aL + bL), 0.0)

    bm = 0.4
    am = 0.5 * bm
    dbm = -1.5 * H * bm
    close(dbm + H * (am + bm), 0.0)


def test_dimension_rejection_of_gemini_rho_squared_term():
    # 4D rho has M^4. rho^2/M6^4 therefore has M^4, not H^2~M^2.
    rho_dim = 4
    M6four_dim = 4
    candidate_dim = 2 * rho_dim - M6four_dim
    assert candidate_dim == 4
    assert candidate_dim != 2


def main():
    tests = [
        test_registry_and_source_bindings,
        test_d5_adm_momentum_inverse_and_dewitt_factor,
        test_flrw_gauss_q_identity,
        test_d2nq_orthogonal_lambda_plus_dust_realization,
        test_source_free_codazzi_special_components,
        test_dimension_rejection_of_gemini_rho_squared_term,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS total={len(tests)}")


if __name__ == "__main__":
    main()
