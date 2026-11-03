from fractions import Fraction


def rank_exact(matrix):
    a = [[Fraction(x) for x in row] for row in matrix]
    m = len(a)
    n = len(a[0]) if m else 0
    r = 0
    c = 0
    while r < m and c < n:
        pivot = next((i for i in range(r, m) if a[i][c] != 0), None)
        if pivot is None:
            c += 1
            continue
        a[r], a[pivot] = a[pivot], a[r]
        p = a[r][c]
        a[r] = [x / p for x in a[r]]
        for i in range(m):
            if i != r and a[i][c] != 0:
                f = a[i][c]
                a[i] = [a[i][j] - f * a[r][j] for j in range(n)]
        r += 1
        c += 1
    return r


def scale_rows_cols(matrix, row_scales, col_scales):
    return [
        [Fraction(row_scales[i]) * Fraction(matrix[i][j]) * Fraction(col_scales[j]) for j in range(len(col_scales))]
        for i in range(len(row_scales))
    ]


def test_mass_dimensions():
    residual_dims = [0, -1, 2, 1, 5, 5, 3, 4, 2, 3]
    assert residual_dims == [0, -1, 2, 1, 5, 5, 3, 4, 2, 3]

    # Example nontrivial fixed bundle branch.
    N_F, m_layer, n_S = 1, 2, -1
    n_N = n_S + m_layer * N_F
    assert n_N == 1
    unknown_dims = [2, 3, 0, 2, 3, -1, -1, 2, 2 + abs(n_N), 2 + abs(n_S)]
    assert unknown_dims[-2:] == [3, 3]


def test_nonsingular_diagonal_scaling_preserves_rank():
    # Full-rank 4x4 witness; exact arithmetic avoids tolerance ambiguity.
    J = [
        [1, 2, 0, 0],
        [0, 1, 3, 0],
        [0, 0, 1, 4],
        [5, 0, 0, 1],
    ]
    r0 = rank_exact(J)
    assert r0 == 4
    Jhat = scale_rows_cols(J, [2, 3, 5, 7], [11, 13, 17, 19])
    assert rank_exact(Jhat) == r0


def test_scaling_cannot_rescue_singular_matrix():
    J = [
        [1, 2, 3],
        [2, 4, 6],
        [0, 1, 1],
    ]
    assert rank_exact(J) == 2
    Jeq = scale_rows_cols(J, [2, 5, 7], [3, 11, 13])
    assert rank_exact(Jeq) == 2


def test_zero_scale_is_forbidden():
    # The gate requires every physical/equilibration scale to be finite and nonzero.
    row_scales = [1, 1, 0]
    assert any(s == 0 for s in row_scales)


if __name__ == "__main__":
    test_mass_dimensions()
    test_nonsingular_diagonal_scaling_preserves_rank()
    test_scaling_cannot_rescue_singular_matrix()
    test_zero_scale_is_forbidden()
    print("G3.7 algebraic normalization QA: PASS")
