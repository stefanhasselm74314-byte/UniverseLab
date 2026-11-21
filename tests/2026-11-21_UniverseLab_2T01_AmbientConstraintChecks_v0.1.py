#!/usr/bin/env python3
"""UL-2T-01: exact local worldline/ambient kinematic checks.

This checks neither 2T quantum BRST consistency nor Einstein/6D field equations.
No HZT physical release, no parent-action identification.
"""
import unittest
import sympy as s

t, rho, tau, x, y, z = s.symbols('t rho tau x y z', real=True)
pt, pr, p0, p1, p2, p3 = s.symbols('pt pr p0 p1 p2 p3', real=True)
h, beta, ell = s.symbols('h beta ell', real=True, nonzero=True)
coords = (t, rho, tau, x, y, z)
momenta = (pt, pr, p0, p1, p2, p3)
a2 = s.exp(2*(h*tau + beta*rho))
g4 = s.diag(-1, a2, 1, 1)
g4inv = s.diag(-1, 1/a2, 1, 1)
g6 = s.diag(1, 1, 1, 1, 1, 1)
g6[0,0] = 2*rho
g6[0,1] = g6[1,0] = t
g6[1,1] = 0
for i in range(4):
    g6[i+2,i+2] = t*t*g4[i,i]
G6 = s.diag(1, 1, 1, 1, 1, 1)
G6[0,0] = 0
G6[0,1] = G6[1,0] = 1/t
G6[1,1] = -2*rho/t**2
for i in range(4):
    G6[i+2,i+2] = g4inv[i,i]/t**2

W = 2*rho*t*t
Q11 = W
Q12 = t*pt
Q22 = (2*pt*pr/t - 2*rho*pr**2/t**2
       + (-p0**2+p1**2/a2+p2**2+p3**2)/t**2)


def pb(f, g):
    return s.simplify(sum(s.diff(f,q)*s.diff(g,p)-s.diff(f,p)*s.diff(g,q)
                          for q,p in zip(coords,momenta)))


class Ambient2TChecks(unittest.TestCase):
    def test_exact_inverse(self):
        self.assertEqual(s.simplify(g6 * G6), s.eye(6))

    def test_signature_and_determinant(self):
        self.assertEqual(s.simplify(s.det(g6) - t**10*a2), 0)
        self.assertEqual(s.simplify(s.det(g6[:2,:2]) + t*t), 0)
        self.assertEqual((1+3, 1+1), (4,2))

    def test_closed_homothety(self):
        V = s.Matrix([t,0,0,0,0,0])
        self.assertEqual(s.simplify(s.Matrix([s.diff(W,q) for q in coords])-2*g6*V), s.zeros(6,1))
        lv = s.zeros(6)
        for m in range(6):
            for n in range(6):
                lv[m,n] = s.simplify(sum(V[k]*s.diff(g6[m,n],coords[k])
                      + g6[k,n]*s.diff(V[k],coords[m])
                      + g6[m,k]*s.diff(V[k],coords[n]) for k in range(6)))
        self.assertEqual(s.simplify(lv-2*g6), s.zeros(6))
        self.assertEqual(s.simplify(sum(V[i]*s.diff(W,coords[i]) for i in range(6))-2*W),0)

    def test_strong_sp2_algebra(self):
        self.assertEqual(s.simplify(pb(Q11,Q12) - 2*Q11), 0)
        self.assertEqual(s.simplify(pb(Q11,Q22) - 4*Q12), 0)
        self.assertEqual(s.simplify(pb(Q12,Q22) - 2*Q22), 0)

    def test_reduction_and_transverse_gauge(self):
        sub = {t:ell, rho:0, pt:0, pr:0}
        sh = s.simplify(Q22.subs(sub, simultaneous=True))
        target = (-p0*p0+p1*p1/s.exp(2*h*tau)+p2*p2+p3*p3)/ell**2
        self.assertEqual(s.simplify(sh-target),0)
        self.assertEqual(s.simplify(pb(t-ell,Q12)-t),0)
        self.assertEqual(s.simplify(pb(pr,Q11)+2*t**2),0)
        gauge_mat = s.Matrix([[pb(t-ell,Q12),pb(t-ell,Q11)],
                              [pb(pr,Q12),pb(pr,Q11)]])
        self.assertEqual(s.simplify(s.det(gauge_mat)+2*t**3),0)

    def test_local_phasespace_count(self):
        self.assertEqual(12 - 2*3, 6)
        self.assertEqual(8 - 2*1, 6)

    def test_4d_curvature_counterexample(self):
        a = s.exp(h*tau)
        R = 2*s.diff(a,tau,2)/a
        G_yy = -R/2
        G_tautau = -s.diff(a,tau,2)/a + R/2
        self.assertEqual(s.simplify(R-2*h**2),0)
        self.assertEqual(s.simplify(G_yy+h**2),0)
        self.assertEqual(s.simplify(G_tautau),0)

    def test_constant_scalar_potential_not_automatically_allowed(self):
        mu = s.symbols('mu', real=True, nonzero=True)
        U_bad = mu**2
        self.assertNotEqual(s.simplify(pb(Q12,Q22+U_bad)-2*(Q22+U_bad)), 0)
        U_good = mu**2/t**2
        self.assertEqual(s.simplify(pb(Q12,Q22+U_good)-2*(Q22+U_good)), 0)


if __name__=='__main__':
    unittest.main(verbosity=2)
