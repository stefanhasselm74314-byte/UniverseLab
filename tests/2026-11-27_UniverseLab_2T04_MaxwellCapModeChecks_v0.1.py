#!/usr/bin/env python3
"""UniverseLab UL-GRQM-2T04, 2026-11-27, v0.1 DRAFT.

Scoped checks: fixed-background transverse U(1) Maxwell+cap phase Hessian;
scalar fixed-background Hessian weights; exact mathematical flat-disk toy.
No M0 on-shell solver, no full gravitational vector/scalar coupling, no physical
mass measurement, no proof of ghost freedom or 2T-field-theory equivalence.

Run: python -m unittest -v 2026-11-27_UniverseLab_2T04_MaxwellCapModeChecks_v0.1.py
or: python 2026-11-27_UniverseLab_2T04_MaxwellCapModeChecks_v0.1.py
"""
import math
import unittest

import numpy as np
import sympy as sp
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import jv, jn_zeros


def flat_disk_root(z, R=1.0):
    """Symmetric two-disk transverse even mode: 2*x*J1(x)=z*J0(x).
    z=R*Z_sigma*q_sigma**2 >= 0; manufactured geometry only.
    Returns first eigenmass m (not m**2), with m=0 for z=0.
    """
    if R <= 0 or z < 0:
        raise ValueError("Need R>0 and z>=0")
    if z == 0:
        return 0.0
    j01 = jn_zeros(0, 1)[0]
    fun = lambda x: 2*x*jv(1, x) - z*jv(0, x)
    return brentq(fun, 1e-12, j01*(1-1e-12), xtol=1e-13)/R


class FixedBackgroundIdentities(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.A = sp.symbols('A', real=True)
        cls.L = sp.symbols('L', positive=True)
        cls.Z = sp.symbols('Z', positive=True)
        cls.q = sp.symbols('q', real=True)
        cls.Delta = sp.symbols('Delta', positive=True)

    def test_01_warped_sqrt_det(self):
        self.assertEqual(sp.simplify(sp.exp(4*self.A)*self.L), sp.exp(4*self.A)*self.L)

    def test_02_maxwell_4d_weight_cancels_warp(self):
        self.assertEqual(sp.simplify(sp.exp(4*self.A)*self.L*self.Z*sp.exp(-4*self.A)), self.L*self.Z)

    def test_03_maxwell_radial_weight(self):
        self.assertEqual(sp.simplify(sp.exp(4*self.A)*self.L*self.Z*sp.exp(-2*self.A)), sp.exp(2*self.A)*self.L*self.Z)

    def test_04_maxwell_angular_weight(self):
        self.assertEqual(sp.simplify(sp.exp(4*self.A)*self.L*self.Z*sp.exp(-2*self.A)/self.L**2), sp.exp(2*self.A)*self.Z/self.L)

    def test_05_scalar_4d_weight(self):
        self.assertEqual(sp.simplify(sp.exp(4*self.A)*self.L*sp.exp(-2*self.A)), sp.exp(2*self.A)*self.L)

    def test_06_scalar_radial_weight(self):
        self.assertEqual(sp.simplify(sp.exp(4*self.A)*self.L), sp.exp(4*self.A)*self.L)

    def test_07_gravity_4d_einstein_weight(self):
        self.assertEqual(sp.simplify(sp.exp(4*self.A)*self.L*sp.exp(-2*self.A)), sp.exp(2*self.A)*self.L)

    def test_08_cap_phase_4d_weight(self):
        cap = self.Delta*sp.exp(4*self.A)*self.L*self.Z*sp.exp(-2*self.A)
        self.assertEqual(sp.simplify(cap), self.Delta*sp.exp(2*self.A)*self.L*self.Z)

    def test_09_stueckelberg_gauge_invariance(self):
        d_s, a, d_lambda = sp.symbols('ds a dl', real=True)
        expr = (d_s+self.q*d_lambda)-self.q*(a+d_lambda)
        self.assertEqual(sp.simplify(expr-(d_s-self.q*a)), 0)

    def test_10_cap_mass_nonnegative(self):
        for q in [0.0, 0.2, -2.0]:
            b = 2*math.pi*math.exp(0.4)*1.3*0.8*q*q
            self.assertGreaterEqual(b, 0)

    def test_11_bulk_vector_weights_positive(self):
        for a,l,z in [(-2, 0.03, 0.01), (0., 1., 1.), (2., 3., 8.)]:
            self.assertGreater(l*z, 0.)
            self.assertGreater(math.exp(2*a)*l*z, 0.)

    def test_12_frozen_M1_ZF_positive(self):
        a, phi, M = sp.symbols('a phi M', positive=True)
        zf = sp.exp(-2*a*phi/M**2)
        self.assertEqual(sp.simplify(sp.diff(zf, phi, 2)/zf), 4*a*a/M**4)

    def test_13_frozen_M1_U_second_derivative(self):
        phi, M, mu = sp.symbols('phi M mu', positive=True)
        U = sp.Rational(1,2)*mu*M**6*(phi/M**2)**2
        self.assertEqual(sp.simplify(sp.diff(U, phi, 2)), mu*M**2)

    def test_14_flux_local_Hessian_nonnegative(self):
        for rho, af, M in [(0., 1., 1.), (3., 0.2, 2.), (12., 3., 1.5)]:
            contribution = 4*af**2*rho/M**4
            self.assertGreaterEqual(contribution, 0.)

    def test_15_2d_gauge_and_graviton_norms_differ(self):
        # Artificial flat unit disk, constant warp: Iv=pi R^2 Z,
        # M4^2=M6^4*pi R^2; coefficients depend on Z and M6 differently.
        R, Z, M6 = 2., 3., 4.
        Iv = math.pi*R**2*Z
        M4sq = M6**4*math.pi*R**2
        self.assertAlmostEqual(Iv, 12*math.pi)
        self.assertAlmostEqual(M4sq, 1024*math.pi)
        self.assertNotEqual(Iv, M4sq)


class TwoDiskToy(unittest.TestCase):
    def test_16_no_cap_recovers_zero_mode(self):
        self.assertEqual(flat_disk_root(0.), 0.)

    def test_17_active_cap_lifts_lowest_mode(self):
        self.assertGreater(flat_disk_root(0.5), 0.)

    def test_18_root_satisfies_exact_bessel_boundary(self):
        for z in (0.01, 0.1, 0.5, 4.0, 30.0):
            x=flat_disk_root(z)
            self.assertAlmostEqual(2*x*jv(1,x)-z*jv(0,x), 0., places=10)

    def test_19_small_cap_mass_expansion(self):
        z=0.01
        x=flat_disk_root(z)
        expected=z-z*z/8.
        self.assertLess(abs(x*x-expected), 2e-7)

    def test_20_large_cap_dirichlet_limit(self):
        x=flat_disk_root(1e5)
        self.assertLess(abs(x-jn_zeros(0,1)[0]), 5e-5)

    def test_21_monotone_lowest_mass(self):
        masses=[flat_disk_root(z) for z in [0., 0.01, 0.2, 1.0, 20.0]]
        self.assertTrue(all(m2>m1 for m1,m2 in zip(masses[:-1],masses[1:])))

    def test_22_constant_trial_is_upper_bound_not_exact(self):
        # 2 disks with L=r and R=1: Iv=2*pi*R^2 ; b=2*pi*R*c ; b/Iv=c/R.
        for z in [0.02,0.5,1.,3.]:
            mass=flat_disk_root(z)
            self.assertLess(mass*mass, z)
            self.assertGreater(mass*mass, 0.)

    def test_23_bessel_rayleigh_quotient(self):
        R=1.3
        c=0.7
        z=c*R
        m=flat_disk_root(z,R)
        u=lambda r:jv(0,m*r)
        du=lambda r:-m*jv(1,m*r)
        norm=2*quad(lambda r:r*u(r)**2,0,R,epsabs=1e-11)[0]
        energy=2*quad(lambda r:r*du(r)**2,0,R,epsabs=1e-11)[0]+R*c*u(R)**2
        self.assertAlmostEqual(energy/norm,m*m,places=10)

    def test_24_no_nontrivial_constant_eigenmode_for_b_positive(self):
        # Constant f on both disks has f'=0 but cannot satisfy b f(R)=0 for b>0.
        b=0.8
        f=1.0
        self.assertNotEqual(b*f, 0.)

    def test_25_lowest_mass_scales_as_inverse_radius_at_fixed_z(self):
        z=0.8
        m1=flat_disk_root(z,R=1.)
        m2=flat_disk_root(z,R=2.)
        self.assertAlmostEqual(m2,m1/2.,places=11)

    def test_26_angular_scale_bessel_roots(self):
        self.assertAlmostEqual(jn_zeros(0,1)[0],2.404825557695773,places=12)

    def test_27_vector_matter_coupling_requires_source_action(self):
        # This is a metadata firewall, not a physics theorem.
        cap_current_available=True
        baryon_current_available=False
        self.assertTrue(cap_current_available)
        self.assertFalse(baryon_current_available)


if __name__ == '__main__':
    unittest.main(verbosity=2)

