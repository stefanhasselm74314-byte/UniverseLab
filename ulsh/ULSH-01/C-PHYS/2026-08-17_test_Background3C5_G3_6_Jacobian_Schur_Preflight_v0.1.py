#!/usr/bin/env python3
"""Algebraic QA only for Background3C5 G3.6.

No physical solver import, no BVP solve, no physical evidence.
"""

import numpy as np


def block_matrix(J8, B, C, D):
    return np.block([[J8, B], [C, D]])


def schur(J8, B, C, D):
    return D - C @ np.linalg.solve(J8, B)


def main():
    rng = np.random.default_rng(20260817)

    # Check the determinant identity on diverse nonsingular synthetic blocks.
    for _ in range(64):
        J8 = rng.normal(size=(8, 8)) + 4.0 * np.eye(8)
        B = rng.normal(size=(8, 2))
        C = rng.normal(size=(2, 8))
        D = rng.normal(size=(2, 2))
        J10 = block_matrix(J8, B, C, D)
        S = schur(J8, B, C, D)

        sign10, log10 = np.linalg.slogdet(J10)
        sign8, log8 = np.linalg.slogdet(J8)
        signS, logS = np.linalg.slogdet(S)
        assert sign10 != 0 and sign8 != 0 and signS != 0
        assert sign10 == sign8 * signS
        assert abs(log10 - (log8 + logS)) < 1e-10

    # Raw layer block determinant: [[aN,-aS],[bN,bS]].
    for vals in [(2.0, 3.0, 5.0, 7.0), (1.0, -2.0, 4.0, 6.0), (0.5, 1.25, -3.0, 2.0)]:
        aN, aS, bN, bS = vals
        D = np.array([[aN, -aS], [bN, bS]], dtype=float)
        expected = aN * bS + aS * bN
        assert abs(np.linalg.det(D) - expected) < 1e-12

    # Explicit risk surface: raw layer determinant zero.
    aN, aS, bN = 2.0, 3.0, 5.0
    bS = -(aS * bN) / aN
    D = np.array([[aN, -aS], [bN, bS]], dtype=float)
    assert abs(np.linalg.det(D)) < 1e-12

    # Backreaction can create a Schur null direction even if D is invertible.
    J8 = np.eye(8)
    B = np.zeros((8, 2))
    C = np.zeros((2, 8))
    D = np.eye(2)
    B[0, 0] = 1.0
    C[0, 0] = 1.0
    S = schur(J8, B, C, D)
    assert abs(np.linalg.det(D) - 1.0) < 1e-12
    assert abs(np.linalg.det(S)) < 1e-12
    assert np.linalg.matrix_rank(block_matrix(J8, B, C, D), tol=1e-12) == 9

    # Patch winding compatibility is discrete, not an extra continuous residual.
    for NF, mlayer, nS in [(1, 1, 0), (2, 3, -1), (-1, 2, 4)]:
        nN = nS + mlayer * NF
        assert nN - nS == mlayer * NF

    print("PASS_G3_6_ALGEBRAIC_QA_ONLY_NO_PHYSICAL_VERDICT")


if __name__ == "__main__":
    main()
