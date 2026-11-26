#!/usr/bin/env python3
"""UL-GRQM-2T03: 12 small algebraic checks.

DRAFT / NONCANONICAL. These checks do NOT solve HZT-M0 6D dynamics,
compute a physical M0 mode basis, prove ghost freedom or test data.
Requires SymPy.
"""
import unittest
import sympy as sp


class FourDEFTWeylBridgeChecks(unittest.TestCase):
    def setUp(self):
        self.M, self.theta, self.psi = sp.symbols(
            "M theta psi", positive=True, real=True
        )
        self.chi = sp.sqrt(6)*self.M*self.theta*sp.cosh(
            self.psi/(sp.sqrt(6)*self.M))
        self.s = sp.sqrt(6)*self.M*self.theta*sp.sinh(
            self.psi/(sp.sqrt(6)*self.M))

    def test_01_compensator_relation(self):
        self.assertEqual(sp.simplify(
            self.chi**2-self.s**2-6*self.M**2*self.theta**2), 0)

    def test_02_einstein_coefficient(self):
        self.assertEqual(sp.simplify(
            (self.chi**2-self.s**2)/(12*self.theta**2)-self.M**2/2), 0)

    def test_03_scalar_inverse_patch(self):
        psi_inv=sp.sqrt(6)*self.M*sp.atanh(self.s/self.chi)
        self.assertEqual(sp.simplify(sp.diff(psi_inv,self.psi)-1), 0)

    def test_04_kinetic_pullback(self):
        dtheta,dpsi=sp.symbols("dtheta dpsi", real=True)
        dchi=sp.diff(self.chi,self.theta)*dtheta + sp.diff(self.chi,self.psi)*dpsi
        ds=sp.diff(self.s,self.theta)*dtheta + sp.diff(self.s,self.psi)*dpsi
        residual=(dchi*dchi-ds*ds)/2 - 3*self.M**2*dtheta**2 + self.theta**2*dpsi**2/2
        self.assertEqual(sp.simplify(residual),0)

    def test_05_gravitational_gradient_cancel(self):
        z=sp.symbols("z", real=True)
        self.assertEqual(3*self.M**2*z*z-3*self.M**2*z*z,0)

    def test_06_quartic_homogeneity(self):
        c,s,lam=sp.symbols("c s lam", real=True)
        V=lam*(c*c-s*s)**2
        self.assertEqual(sp.simplify(c*sp.diff(V,c)+s*sp.diff(V,s)-4*V),0)

    def test_07_naked_mass_not_weyl_homogeneous(self):
        c,s,m=sp.symbols("c s m", real=True,nonzero=True)
        V=m*m*s*s/2
        self.assertNotEqual(sp.simplify(c*sp.diff(V,c)+s*sp.diff(V,s)-4*V),0)

    def test_08_kinetic_rank_invariance(self):
        a,b=sp.symbols("a b",real=True,nonzero=True)
        J=sp.diag(a,b)
        self.assertEqual((J.T*sp.eye(2)*J).rank(),2)
        ghost=(J.T*sp.diag(1,-1)*J)
        self.assertEqual(ghost[1,1],-b*b)

    def test_09_warp_volume_flat_disk(self):
        R,r=sp.symbols("R r",positive=True,real=True)
        volume=2*sp.pi*sp.integrate(r,(r,0,R))
        self.assertEqual(sp.simplify(volume-sp.pi*R**2),0)

    def test_10_scalar_constant_profile(self):
        R,r=sp.symbols("R r",positive=True,real=True)
        f=1/sp.sqrt(sp.pi*R**2)
        self.assertEqual(sp.simplify(
            2*sp.pi*sp.integrate(r*f*f,(r,0,R))-1),0)

    def test_11_independent_gauge_normalization(self):
        R,g6,z=sp.symbols("R g6 z",positive=True,real=True)
        g4_inv_sq=sp.pi*R**2*z/g6**2
        self.assertNotEqual(sp.simplify(
            g4_inv_sq.subs(z,2)-g4_inv_sq.subs(z,1)),0)

    def test_12_toy_yukawa_decoupling(self):
        beta,k,a,m=sp.symbols("beta k a m",positive=True,real=True)
        mu=1+2*beta**2*k**2/(k**2+a**2*m**2)
        self.assertEqual(mu.subs(beta,0),1)
        self.assertEqual(sp.simplify(mu.subs(k,0)-1),0)


if __name__=="__main__":
    unittest.main(verbosity=2)
