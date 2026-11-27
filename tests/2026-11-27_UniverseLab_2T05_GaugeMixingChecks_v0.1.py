#!/usr/bin/env python3
"""UL-GRQM-2T05: finite algebraic checks of the KK vector/cap sector.

DRAFT/NONCANONICAL. These checks do not calculate the coupled 6D
Einstein-Maxwell constraints, eigenmodes, physical stability, or observables.
Requires SymPy. The quadratic "mass matrix" is cap-local, not full EFT.
"""
import unittest
import sympy as sp


class GaugeMixingChecks(unittest.TestCase):
    def setUp(self):
        self.q, self.N, self.a, self.kappa = sp.symbols('q N a kappa', real=True)
        self.A, self.B, self.C, self.ds = sp.symbols('A B C ds', real=True)
        self.dxi, self.dlam = sp.symbols('dxi dlam', real=True)
        self.w = self.N - self.q*self.a
        self.Xi = self.ds - self.q*self.A - self.w*self.C

    def test_01_induced_metric_inverse(self):
        W,L,c=sp.symbols('W L c', positive=True)
        h=sp.Matrix([[W+L**2*c**2,L**2*c],[L**2*c,L**2]])
        h_inv=sp.Matrix([[1/W,-c/W],[-c/W,1/L**2+c**2/W]])
        self.assertEqual(sp.simplify(h*h_inv),sp.eye(2))

    def test_02_induced_volume_independent_C(self):
        W,L,c=sp.symbols('W L c', positive=True)
        h=sp.Matrix([[W+L**2*c**2,L**2*c],[L**2*c,L**2]])
        self.assertEqual(sp.factor(h.det()),W*L**2)

    def test_03_exact_horiz_decomposition(self):
        W,L,c,dmu,dchi=sp.symbols('W L c dmu dchi', positive=True)
        h=sp.Matrix([[W+L**2*c**2,L**2*c],[L**2*c,L**2]])
        lhs=(sp.Matrix([[dmu,dchi]])*h.inv()*sp.Matrix([dmu,dchi]))[0]
        rhs=(dmu-c*dchi)**2/W+dchi**2/L**2
        self.assertEqual(sp.factor(lhs-rhs),0)

    def test_04_Xi_using_B_and_N(self):
        sub=self.q*(self.A-self.a*self.C)+self.N*self.C
        self.assertEqual(sp.expand(self.Xi-(self.ds-sub)),0)

    def test_05_invariance_under_internal_shift(self):
        new=self.Xi.subs({self.ds:self.ds+self.N*self.dxi,
                            self.A:self.A+self.a*self.dxi,
                            self.C:self.C+self.dxi},simultaneous=True)
        self.assertEqual(sp.expand(new-self.Xi),0)

    def test_06_invariance_under_U1(self):
        new=self.Xi.subs({self.ds:self.ds+self.q*self.dlam,
                            self.A:self.A+self.dlam},simultaneous=True)
        self.assertEqual(sp.expand(new-self.Xi),0)

    def test_07_B_is_diffeo_invariant(self):
        B=self.A-self.a*self.C
        new=B.subs({self.A:self.A+self.a*self.dxi,
                    self.C:self.C+self.dxi},simultaneous=True)
        self.assertEqual(sp.expand(new-B),0)

    def test_08_B_is_U1_connection(self):
        B=self.A-self.a*self.C
        self.assertEqual(sp.expand(B.subs(self.A,self.A+self.dlam)-B),self.dlam)

    def test_09_w_is_background_cov_derivative(self):
        self.assertEqual(sp.expand(self.w+self.q*self.a-self.N),0)

    def test_10_cap_mass_matrix_rank_coordinate(self):
        v=sp.Matrix([self.q,self.w]); M=self.kappa*v*v.T
        self.assertEqual(sp.factor(M.det()),0)
        self.assertEqual(M.rank(),1)  # Generic symbols, kappa>0, v != 0

    def test_11_cap_mass_matrix_null_direction(self):
        v=sp.Matrix([self.q,self.w]); M=self.kappa*v*v.T
        null=sp.Matrix([self.w,-self.q])
        self.assertEqual(sp.simplify(M*null),sp.zeros(2,1))

    def test_12_cap_matrix_positive_form(self):
        a1,a2=sp.symbols('a1 a2',real=True)
        v=sp.Matrix([self.q,self.w]); M=self.kappa*v*v.T
        form=(sp.Matrix([[a1,a2]])*M*sp.Matrix([a1,a2]))[0]
        self.assertEqual(sp.expand(form-self.kappa*(self.q*a1+self.w*a2)**2),0)

    def test_13_cap_mass_matrix_in_B_C_basis(self):
        T=sp.Matrix([[1,self.a],[0,1]])  # A = B + a C
        v=sp.Matrix([self.q,self.w]); M=self.kappa*v*v.T
        vb=sp.Matrix([self.q,self.N])
        self.assertEqual(sp.simplify(T.T*M*T-self.kappa*vb*vb.T),sp.zeros(2))

    def test_14_eigenvalues_of_rank_one_matrix(self):
        v=sp.Matrix([self.q,self.N]); M=self.kappa*v*v.T
        tr=sp.factor(sp.trace(M))
        self.assertEqual(tr,self.kappa*(self.N**2+self.q**2))
        self.assertEqual(sp.factor(M.charpoly().as_expr()-sp.Symbol('lambda')*(sp.Symbol('lambda')-tr)),0)

    def test_15_generalized_eigenvalues_with_positive_K(self):
        kB,kC=sp.symbols('kB kC',positive=True)
        v=sp.Matrix([self.q,self.N]); M=self.kappa*v*v.T
        K=sp.diag(kB,kC); mm=sp.symbols('mm')
        determinant=sp.factor((M-mm*K).det())
        expected=kB*kC*mm*(mm-self.kappa*(self.q**2/kB+self.N**2/kC))
        self.assertEqual(sp.simplify(determinant-expected),0)

    def test_16_bulk_mass_can_lift_cap_null(self):
        mB,mC=sp.symbols('mB mC',positive=True)
        v=sp.Matrix([self.q,self.N]); M=self.kappa*v*v.T+sp.diag(mB,mC)
        self.assertEqual(sp.factor(M.det()-(mB*mC+self.kappa*(mC*self.q**2+mB*self.N**2))),0)

    def test_17_n_zero_cap_leaves_C_in_B_basis(self):
        M=sp.simplify(self.kappa*sp.Matrix([self.q,0])*sp.Matrix([[self.q,0]]))
        self.assertEqual(M[1,1],0)
        self.assertEqual(M[0,1],0)

    def test_18_patch_jump_covariant_combo(self):
        # Lambda=alpha*chi; a -> a+alpha, N -> N+q*alpha, B -> B-alpha*C.
        alpha=sp.symbols('alpha',real=True)
        Q=self.q*self.B+self.N*self.C
        Qnew=Q.subs({self.B:self.B-alpha*self.C,self.N:self.N+self.q*alpha},simultaneous=True)
        self.assertEqual(sp.simplify(Qnew-Q),0)

    def test_19_patch_winding_invariant(self):
        alpha=sp.symbols('alpha',real=True)
        wnew=(self.N+self.q*alpha)-self.q*(self.a+alpha)
        self.assertEqual(sp.expand(wnew-self.w),0)

    def test_20_horizontal_F_patch_covariance(self):
        # Under the patch jump, dB -> dB-alpha*dC and a -> a+alpha.
        alpha,FB,FC=sp.symbols('alpha FB FC',real=True)
        before=FB+self.a*FC
        after=FB-alpha*FC+(self.a+alpha)*FC
        self.assertEqual(sp.expand(after-before),0)

    def test_21_radial_F_mixing_with_graviphoton(self):
        # Exact coordinate F_rmu contains a' C; orthogonal KK component removes it.
        r=sp.symbols('r',real=True)
        b=sp.Function('b')(r)
        c=sp.Function('c')(r)
        a=sp.Function('a')(r)
        coordinate_F_rmu=sp.diff(b+a*c,r)
        horizontal_F=coordinate_F_rmu-sp.diff(a,r)*c
        self.assertEqual(sp.simplify(horizontal_F-(sp.diff(b,r)+a*sp.diff(c,r))),0)
        self.assertEqual(sp.simplify(coordinate_F_rmu-horizontal_F-sp.diff(a,r)*c),0)

    def test_22_stueckelberg_unitary_gauge_residual(self):
        # delta s = N xi + q lambda ; residual lambda=-N*xi/q.
        xi=sp.symbols('xi',real=True)
        self.assertEqual(sp.simplify(self.N*xi+self.q*(-self.N*xi/self.q)),0)

    def test_23_isolated_A_only_recovers_old_boundary_mass(self):
        pure=self.Xi.subs({self.C:0,self.ds:0})
        self.assertEqual(sp.expand(pure**2-self.q**2*self.A**2),0)

    def test_24_internal_shift_requires_radial_KK_connection(self):
        # For xi=xi(x,r), both C_r and A_r shift; B_r=A_r-a*C_r stays invariant.
        Cr,Ar,dri=sp.symbols('Cr Ar dri',real=True)
        Br=Ar-self.a*Cr
        transformed=Br.subs({Cr:Cr+dri,Ar:Ar+self.a*dri},simultaneous=True)
        self.assertEqual(sp.expand(transformed-Br),0)
        self.assertEqual(sp.expand((Cr+dri)-Cr),dri)

    def test_25_localized_sources_from_cap_variation(self):
        # L_cap = -kappa/2*(ds-q*B-N*C)^2; q and N source channels.
        Xi=self.ds-self.q*self.B-self.N*self.C
        lag=-self.kappa*Xi**2/2
        self.assertEqual(sp.expand(sp.diff(lag,self.B)-self.kappa*self.q*Xi),0)
        self.assertEqual(sp.expand(sp.diff(lag,self.C)-self.kappa*self.N*Xi),0)

    def test_26_localized_ward_identities(self):
        # In 4D, J_s=kappa*div Xi; div J_B=q J_s, div J_C=N J_s.
        divXi=sp.symbols('divXi')
        Js=self.kappa*divXi
        divJB=self.q*self.kappa*divXi
        divJC=self.N*self.kappa*divXi
        self.assertEqual(sp.expand(divJB-self.q*Js),0)
        self.assertEqual(sp.expand(divJC-self.N*Js),0)

    def test_27_generic_interface_quadratic_variation(self):
        # Boundary q=1/2*k*(q*fB+N*fC)^2.
        fB,fC=sp.symbols('fB fC')
        qbd=self.kappa*(self.q*fB+self.N*fC)**2/2
        grad=sp.Matrix([sp.diff(qbd,fB),sp.diff(qbd,fC)])
        v=sp.Matrix([self.q,self.N])
        self.assertEqual(sp.simplify(grad-self.kappa*v*(v.T*sp.Matrix([fB,fC]))[0]),sp.zeros(2,1))

    def test_28_fixed_cap_source_orthogonal_vector(self):
        # The cap source vector is orthogonal to (N,-q) for every field value.
        fB,fC=sp.symbols('fB fC')
        v=sp.Matrix([self.q,self.N]);null=sp.Matrix([self.N,-self.q])
        source=self.kappa*v*(v.T*sp.Matrix([fB,fC]))[0]
        self.assertEqual(sp.simplify((null.T*source)[0]),0)


if __name__=='__main__':
    unittest.main(verbosity=2)
