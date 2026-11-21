#!/usr/bin/env python3
"""UniverseLab 2T-02 v0.1 - analytic reference checks (noncanonical).

Limited to exact differential/algebraic/geometric identities and one conditional
4D conformal-shadow example. NOT a field-equation solution, full BRST
quantization, complete 6D cap matching, or a physical ghost-freedom test.
"""
import unittest
import sympy as s


class TwoT02AnalyticChecks(unittest.TestCase):
    def test_a_and_scalar_potential_exponent_in_d4(self):
        d = s.Integer(4)
        a = (d-2)/(8*(d-1))
        degree = 2*d/(d-2)
        self.assertEqual(a, s.Rational(1,12))
        self.assertEqual(degree, 4)

    def test_ambient_W_null_and_kinematic_relation(self):
        t, rho, f = s.symbols('t rho f', real=True, positive=True)
        G = s.diag(-t*t*f, t*t, t*t, t*t)
        B = s.Matrix([[2*rho,t],[t,0]])
        G6 = s.diag(1,1,1,1,1,1)
        G6[:2,:2] = B
        G6[2:,2:] = G
        inv = s.simplify(G6.inv())
        W = 2*rho*t*t
        gradW = s.Matrix([s.diff(W,t),s.diff(W,rho),0,0,0,0])
        self.assertEqual(s.simplify((gradW.T*inv*gradW)[0]-4*W),0)
        self.assertEqual(s.simplify(gradW.subs(rho,0).T*inv.subs(rho,0)*gradW.subs(rho,0))[0],0)

    def test_ambient_induced_metric_rank_four(self):
        t, f = s.symbols('t f', positive=True)
        h = s.diag(0,-t*t*f,t*t,t*t,t*t)
        self.assertEqual(h.rank(), 4)
        self.assertEqual(h.det(), 0)
        self.assertEqual(h[0,0],0)

    def test_m0_cap_rank_five(self):
        A, L = s.symbols('A L', real=True, positive=True)
        h = s.diag(-s.exp(2*A),s.exp(2*A),s.exp(2*A),s.exp(2*A),L*L)
        self.assertEqual(h.rank(), 5)
        self.assertNotEqual(h.det(),0)
        self.assertEqual(s.simplify(h.det()+s.exp(8*A)*L*L),0)

    def test_induced_rank_invariant_under_invertible_chart_change(self):
        t, f = s.symbols('t f', positive=True)
        h = s.diag(0,-t*t*f,t*t,t*t,t*t)
        J = s.diag(2,3,4,5,6)
        self.assertNotEqual(J.det(),0)
        self.assertEqual((J.T*h*J).rank(),h.rank())

    def test_einstein_gauge_hyperbolic_parameterization(self):
        M, sig = s.symbols('M sig', real=True, positive=True)
        q = s.sqrt(6)*M
        chi = q*s.cosh(sig/q)
        h = q*s.sinh(sig/q)
        self.assertEqual(s.simplify(chi**2-h**2),6*M*M)
        self.assertEqual(s.simplify(s.diff(chi,sig)**2-s.diff(h,sig)**2),-1)
        self.assertEqual(s.simplify((chi**2-h**2)/12),M*M/2)

    def test_weyl_weights_of_shadow_potential(self):
        chi, h = s.symbols('chi h', real=True)
        pot = chi**4+3*chi**2*h**2+2*h**4
        self.assertEqual(s.expand(chi*s.diff(pot,chi)+h*s.diff(pot,h)-4*pot),0)

    def test_mass_term_breaks_classical_weyl_if_no_compensator(self):
        mass, h = s.symbols('mass h', positive=True)
        pot = mass**2*h**2
        mismatch=s.expand(4*pot-h*s.diff(pot,h))
        self.assertEqual(mismatch,2*mass*mass*h*h)

    def test_local_weyl_derivative_terms_are_total_divergence(self):
        F, boxom, dot = s.symbols('F boxomega gradF_dot_gradowega')
        curv = -F*boxom/2
        kin = -dot/2
        divergence = -(F*boxom+dot)/2
        self.assertEqual(s.simplify(curv+kin-divergence),0)

    def test_warped_4d_planck_matching(self):
        M6, R = s.symbols('M6 R', positive=True)
        Vw = s.pi*R**2
        M4sq = M6**4*Vw
        self.assertEqual(s.simplify((6*M4sq)/12),M4sq/2)
        self.assertTrue(Vw.is_positive)

    def test_distribution_delta_and_delta_prime_have_distinct_functionals(self):
        u = s.symbols('u', real=True)
        f = 5+3*u+7*u*u
        delta_action = f.subs(u,0)
        delta_prime_action = -s.diff(f,u).subs(u,0)
        self.assertEqual(delta_action,5)
        self.assertEqual(delta_prime_action,-3)
        self.assertNotEqual(delta_action,delta_prime_action)

    def test_4d_gravity_coefficient_requires_positive_branch(self):
        chi,scl=s.symbols('chi scl', real=True)
        F=chi**2-scl**2
        self.assertEqual(s.simplify(F.subs({chi:3,scl:1})),8)
        self.assertEqual(s.simplify(F.subs({chi:1,scl:3})),-8)
        self.assertEqual(s.simplify(F.subs({chi:2,scl:2})),0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
