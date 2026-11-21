#!/usr/bin/env python3
"""UniverseLab SIG-02 / v0.1. Analytische Identitäten und Gegenbeispiele.
NO physical approval, no full HZT-Full/2T field-equation or ghost test.
"""
import math
import unittest
import sympy as sp
import numpy as np


def poisson(f, g, coords, mom):
    return sp.expand(sum(
        sp.diff(f, q) * sp.diff(g, p) - sp.diff(f, p) * sp.diff(g, q)
        for q, p in zip(coords, mom)
    ))


class SIG02AnalyticChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x = sp.symbols("x0:4", real=True)
        cls.p = sp.symbols("p0:4", real=True)
        cls.u, cls.v, cls.piu, cls.piv = sp.symbols(
            "u v pi_u pi_v", real=True
        )
        cls.coords = list(cls.x) + [cls.u, cls.v]
        cls.mom = list(cls.p) + [cls.piu, cls.piv]
        eta = [-1, 1, 1, 1]
        cls.x2 = sum(s * z**2 for s, z in zip(eta, cls.x))
        cls.p2 = sum(s * z**2 for s, z in zip(eta, cls.p))
        cls.xp = sum(z * w for z, w in zip(cls.x, cls.p))  # p canonical covariant
        cls.Q11 = cls.x2 - 2 * cls.u * cls.v
        cls.Q12 = cls.xp + cls.u * cls.piu + cls.v * cls.piv
        cls.Q22 = cls.p2 - 2 * cls.piu * cls.piv

    def test_sp2_poisson_closure(self):
        self.assertEqual(sp.simplify(poisson(self.Q11, self.Q22, self.coords, self.mom) - 4*self.Q12), 0)
        self.assertEqual(sp.simplify(poisson(self.Q11, self.Q12, self.coords, self.mom) - 2*self.Q11), 0)
        self.assertEqual(sp.simplify(poisson(self.Q12, self.Q22, self.coords, self.mom) - 2*self.Q22), 0)

    def test_sp2_gauge_slice(self):
        ell = sp.symbols("ell", real=True, nonzero=True)
        sub = {self.u: ell, self.piv: 0, self.v: self.x2/(2*ell),
               self.piu: -self.xp/ell}
        self.assertEqual(sp.simplify(self.Q11.subs(sub, simultaneous=True)), 0)
        self.assertEqual(sp.simplify(self.Q12.subs(sub, simultaneous=True)), 0)
        self.assertEqual(sp.simplify(self.Q22.subs(sub, simultaneous=True)), self.p2)
        self.assertEqual(sp.simplify(self.piu.subs(sub)), -self.xp/ell)

    def test_phase_space_dimension(self):
        self.assertEqual(2*6 - 2*3, 6)
        self.assertEqual(2*4 - 2*1, 6)

    def test_disk_ansatz_is_one_time(self):
        A, B, C, r = sp.symbols("A B C r", real=True, positive=True)
        warp4 = sp.exp(-2*A)
        diag = [-warp4, warp4, warp4, warp4, sp.exp(2*B), sp.exp(2*C)*r**2]
        self.assertEqual(sp.simplify(sp.prod(diag) + sp.exp(-8*A+2*B+2*C)*r**2), 0)
        self.assertTrue(all(v.subs({A:1,B:1,C:1,r:2}).evalf()>0 for v in diag[1:]))
        self.assertLess(diag[0].subs({A:1}).evalf(), 0)

    def test_signature_2t_null_plane(self):
        g = sp.diag(-1, 1, 1, 1, 1, -1)
        self.assertEqual((sum(1 for v in g.diagonal() if v>0),
                          sum(1 for v in g.diagonal() if v<0)), (4,2))
        self.assertEqual(sp.det(g), 1)
        self.assertEqual(sp.det(sp.Matrix([[0, -1], [-1, 0]])), -1)

    def test_haynsworth_inertia_with_offdiagonal_mixing(self):
        S = sp.diag(-1, 1, 1, 1)
        B = sp.Matrix([[1, 2], [-1, 0], [3, 1], [0, -2]])
        for D, expected in [(sp.diag(-1, 1), (4, 2)), (sp.eye(2), (5, 1))]:
            A = S + B*D.inv()*B.T
            G = A.row_join(B).col_join(B.T.row_join(D))
            self.assertEqual(A - B*D.inv()*B.T, S)
            eig = np.linalg.eigvalsh(np.array(G).astype(float))
            self.assertEqual((int(np.sum(eig > 1e-8)), int(np.sum(eig < -1e-8))), expected)
            self.assertEqual(sp.det(G), sp.det(S)*sp.det(D))

    def test_timelike_compact_kk_tachyonic_mass(self):
        R, n, k = 2.0, 1, 0.1
        m2 = -(n/R)**2
        omega2 = k*k + m2
        self.assertLess(m2, 0)
        self.assertLess(omega2, 0)
        self.assertGreater(math.sqrt(-omega2), 0)
        self.assertEqual(0.0, -(0/R)**2)

    def test_warped_zero_mode_normalization(self):
        A = sp.symbols("A", real=True)
        self.assertEqual(sp.simplify(sp.exp(4*A)*sp.exp(-2*A)-sp.exp(2*A)), 0)

    def test_no_ghost_conclusion_from_one_mode(self):
        K = sp.diag(1, -1)
        self.assertEqual(K[0, 0], 1)
        self.assertEqual(list(K.eigenvals().keys()), [sp.Integer(1), sp.Integer(-1)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
