#!/usr/bin/env python3
"""UniverseLab UL-GRQM-2T06 -- analytic circle-KK vector-sector checks.

DRAFT / NONCANONICAL. These tests validate restricted action identities,
patch covariance and a manufactured constant-profile example. They do NOT
validate a 6D on-shell background, complete EH+Maxwell Hessian, cap bending,
full 5D gravitational vector constraints, ghost freedom or 4D predictions.
"""
import math
import unittest
import sympy as sp
import numpy as np

class TwoVectorChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.L, cls.Z, cls.a, cls.M4, cls.A = sp.symbols('L Z a M4 A', positive=True, real=True)
        cls.r, cls.R, cls.zeta, cls.q, cls.N = sp.symbols('r R zeta q N', positive=True, real=True)
        cls.pi = sp.pi
        cls.K = 2*sp.pi*cls.L*sp.Matrix([
            [cls.Z, cls.Z*cls.a],
            [cls.Z*cls.a, cls.Z*cls.a**2 + cls.M4*cls.L**2/2]
        ])
        cls.v = sp.Matrix([cls.q, cls.N])

    def test_01_circle_metric_determinant_independent_C(self):
        w, C0, C1, ell = sp.symbols('w C0 C1 ell', real=True, nonzero=True)
        g4=sp.diag(-w,w,w,w)
        c=sp.Matrix([C0,C1,0,0]); block=g4+ell**2*c*c.T
        g5=block.row_join(ell**2*c).col_join((ell**2*c.T).row_join(sp.Matrix([[ell**2]])))
        self.assertEqual(sp.simplify(g5.det()+w**4*ell**2),0)

    def test_02_warped_volume_and_factors(self):
        self.assertEqual(sp.simplify(sp.exp(4*self.A)*sp.exp(-4*self.A)),1)
        self.assertEqual(sp.simplify(sp.exp(4*self.A)*sp.exp(-2*self.A)-sp.exp(2*self.A)),0)

    def test_03_GHY_trace_fixed_radial_gauge(self):
        rr=sp.symbols('rr',real=True)
        Aw=sp.Function('Aw')(rr); Lf=sp.Function('Lf')(rr)
        sqrt_det=sp.exp(4*Aw)*Lf  # Schur determinant of induced metric
        K=sp.diff(sqrt_det,rr)/sqrt_det
        self.assertEqual(sp.simplify(K-4*sp.diff(Aw,rr)-sp.diff(Lf,rr)/Lf),0)

    def test_04_horizontal_F_exact(self):
        Bp,Cp,ap,C=sp.symbols('Bp Cp ap C')
        F_coord= Bp+ap*C+self.a*Cp
        F_horizontal=F_coord-ap*C
        self.assertEqual(sp.simplify(F_horizontal-(Bp+self.a*Cp)),0)

    def test_05_K_matrix_symmetric(self):
        self.assertEqual(self.K, self.K.T)

    def test_06_K_fiber_Maxwell_block(self):
        self.assertEqual(sp.simplify(self.K[0,0]-2*sp.pi*self.L*self.Z),0)

    def test_07_K_fiber_mixed_block(self):
        self.assertEqual(sp.simplify(self.K[0,1]-2*sp.pi*self.L*self.Z*self.a),0)

    def test_08_K_fiber_gravity_block(self):
        extra=sp.simplify(self.K[1,1]-self.a**2*self.K[0,0])
        self.assertEqual(sp.simplify(extra-sp.pi*self.M4*self.L**3),0)

    def test_09_K_determinant(self):
        target= (2*sp.pi)**2*self.M4*self.Z*self.L**4/2
        self.assertEqual(sp.simplify(self.K.det()-target),0)

    def test_10_K_exact_sum_of_squares(self):
        x,y=sp.symbols('x y', real=True)
        quadratic=sp.expand((sp.Matrix([x,y]).T*self.K*sp.Matrix([x,y]))[0])
        target=2*sp.pi*self.L*self.Z*(x+self.a*y)**2+sp.pi*self.M4*self.L**3*y**2
        self.assertEqual(sp.simplify(quadratic-target),0)

    def test_11_K_positive_random(self):
        rng=np.random.default_rng(6206)
        for _ in range(60):
            L,Z,aa,M4=np.exp(rng.normal(size=4)); aa=aa-1
            K=np.array([[Z,Z*aa],[Z*aa,Z*aa*aa+M4*L*L/2]])*2*np.pi*L
            self.assertGreater(np.min(np.linalg.eigvalsh(K)),0)

    def test_12_radial_P_equals_warpK(self):
        P=self.K*sp.exp(2*self.A)
        self.assertEqual(sp.simplify(P[1,1]-sp.exp(2*self.A)*self.K[1,1]),0)

    def test_13_zero_mode_direction(self):
        v0=sp.Matrix([self.N,-self.q])
        self.assertEqual((self.v.T*v0)[0],0)

    def test_14_cap_matrix_rank_one(self):
        Csig=sp.symbols('Csig', positive=True)
        S=Csig*(self.v*self.v.T)
        self.assertEqual(sp.factor(S.det()),0)
        self.assertEqual(sp.simplify(S[0,0]*S[1,1]-S[0,1]**2),0)

    def test_15_cap_matrix_annihilates_null(self):
        Csig=sp.symbols('Csig', positive=True)
        S=Csig*self.v*self.v.T
        self.assertEqual(S*sp.Matrix([self.N,-self.q]),sp.zeros(2,1))

    def test_16_cap_quadratic_square(self):
        Csig,x,y=sp.symbols('Csig x y')
        z=sp.Matrix([x,y])
        S=Csig*self.v*self.v.T
        self.assertEqual(sp.expand((z.T*S*z)[0]-Csig*(self.q*x+self.N*y)**2),0)

    def test_17_bulk_U1_Ward(self):
        ds,dalpha,B,C=sp.symbols('ds dalpha B C')
        xi=ds-self.q*B-self.N*C
        transformed=(ds+self.q*dalpha)-self.q*(B+dalpha)-self.N*C
        self.assertEqual(sp.simplify(transformed-xi),0)

    def test_18_circle_diffeo_Ward(self):
        ds,dlambda,B,C=sp.symbols('ds dlambda B C')
        xi=ds-self.q*B-self.N*C
        transformed=(ds-self.N*dlambda)-self.q*B-self.N*(C-dlambda)
        self.assertEqual(sp.simplify(transformed-xi),0)

    def test_19_transition_of_horizontal_vectors(self):
        B,C,c=sp.symbols('B C c')
        self.assertEqual(sp.expand((B-c*C)+(self.a+c)*C-(B+self.a*C)),0)

    def test_20_transition_of_winding_invariant(self):
        B,C,s,c=sp.symbols('B C s c')
        old=s-self.q*B-self.N*C
        new=s-self.q*(B-c*C)-(self.N+self.q*c)*C
        self.assertEqual(sp.expand(new-old),0)

    def test_21_no_spurious_aprime_C_mass(self):
        aprime, C, Bb, Cp=sp.symbols('aprime C Bb Cp')
        Ftop=Bb+aprime*C+self.a*Cp
        Fhor=sp.expand(Ftop-aprime*C)
        self.assertFalse(Fhor.has(aprime))

    def test_22_constant_trial_zero_energy(self):
        B,C=sp.symbols('B C')
        q=self.q; N=self.N
        boundary=q*B+N*C
        self.assertEqual(sp.simplify(boundary.subs({B:N,C:-q})),0)

    def test_23_flat_disks_K_BB(self):
        L=self.r; Z=1
        I=2*sp.pi*2*sp.integrate(L*Z,(self.r,0,self.R))
        self.assertEqual(sp.simplify(I-2*sp.pi*self.R**2),0)

    def test_24_flat_disks_K_CC(self):
        I=2*sp.pi*2*sp.integrate(self.M4*self.r**3/2,(self.r,0,self.R))
        self.assertEqual(sp.simplify(I-sp.pi*self.M4*self.R**4/2),0)

    def test_25_flat_disks_kinetic_mass_candidate(self):
        zsigma=sp.symbols('zsigma',positive=True)
        K=sp.diag(2*sp.pi*self.R**2,sp.pi*self.M4*self.R**4/2)
        Csig=2*sp.pi*self.R*zsigma
        alpha=sp.simplify(Csig*(self.v.T*K.inv()*self.v)[0])
        target=zsigma*(self.q**2/self.R+4*self.N**2/(self.M4*self.R**3))
        self.assertEqual(sp.simplify(alpha-target),0)

    def test_26_flat_disks_specific_Ritz(self):
        R=1; zsigma=1;M4=1;q=N=1
        K=sp.diag(2*sp.pi*R**2,sp.pi*M4*R**4/2)
        self.assertEqual(sp.simplify(2*sp.pi*R*zsigma*(sp.Matrix([q,N]).T*K.inv()*sp.Matrix([q,N]))[0]),5)

    def test_27_toy_flux_mixing_KBC(self):
        kappa=sp.symbols('kappa',real=True)
        I=2*sp.pi*2*sp.integrate(self.r*kappa*self.r**2,(self.r,0,self.R))
        self.assertEqual(sp.simplify(I-sp.pi*kappa*self.R**4),0)

    def test_28_toy_flux_mixing_KCC(self):
        kappa=sp.symbols('kappa',real=True)
        I=2*sp.pi*2*sp.integrate(self.r*(kappa*self.r**2)**2+self.M4*self.r**3/2,(self.r,0,self.R))
        target=2*sp.pi*kappa**2*self.R**6/3+sp.pi*self.M4*self.R**4/2
        self.assertEqual(sp.simplify(I-target),0)

    def test_29_flux_toy_Ritz_40_over_13(self):
        K=sp.Matrix([[2*sp.pi,sp.pi/2],[sp.pi/2,2*sp.pi/3]])
        v=sp.Matrix([1,1]); cap=2*sp.pi
        val=sp.simplify(cap*(v.T*K.inv()*v)[0])
        self.assertEqual(val,sp.Rational(40,13))

    def test_30_positive_K_with_magnetic_profile(self):
        z=sp.symbols('z',real=True)
        v=sp.Matrix([1,z])
        positive=sp.expand((v.T*self.K*v)[0])
        self.assertEqual(sp.simplify(positive-(2*sp.pi*self.L*self.Z*(1+self.a*z)**2+sp.pi*self.M4*self.L**3*z**2)),0)

    def test_31_matter_charge_undefined_not_autofilled(self):
        model={'sources':['bulk-Maxwell','cap-phase'], 'ordinary_matter_action':None,
               'physical_Ghost_test':False,'on_shell_background':False}
        self.assertIsNone(model['ordinary_matter_action'])
        self.assertFalse(model['on_shell_background'])
        self.assertFalse(model['physical_Ghost_test'])

    def test_32_4d_canonical_mass_rank_no_forced_photon(self):
        K=sp.diag(3,7); v=sp.Matrix([2,5]); c=sp.Rational(4,3)
        M=c*v*v.T
        effective=sp.simplify(K.inv()*M)
        self.assertEqual(effective.det(),0)
        self.assertEqual(sp.simplify(sp.trace(effective)-c*(v.T*K.inv()*v)[0]),0)

if __name__=='__main__':
    unittest.main(verbosity=2)
