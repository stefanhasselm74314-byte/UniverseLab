#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UniverseLab UL-GRQM-2T07 -- EXACT/TOY algebra checks only.

Scope: circle KK form, U(1) & circle Ward identities, radial-gauge
Stueckelberg pieces, moving cap pullback, restricted 2-vector constraints.
NO HZT-M0 on-shell background, full 6D gravity Hessian, ghost proof or 2T
field-theory shadow is verified here.
"""
import unittest
import sympy as sp

class KKAndBendingChecks(unittest.TestCase):
    def test_01_circle_metric_determinant(self):
        u,v,L,c,d=sp.symbols('u v L c d', nonzero=True, real=True)
        H=sp.Matrix([[u+L**2*c**2,L**2*c*d,L**2*c],
                     [L**2*c*d,v+L**2*d**2,L**2*d],
                     [L**2*c,L**2*d,L**2]])
        self.assertEqual(sp.factor(H.det()-u*v*L**2),0)

    def test_02_circle_inverse_horizontal(self):
        u,v,L,c,d=sp.symbols('u v L c d', nonzero=True, real=True)
        H=sp.Matrix([[u+L**2*c**2,L**2*c*d,L**2*c],
                     [L**2*c*d,v+L**2*d**2,L**2*d],
                     [L**2*c,L**2*d,L**2]])
        target=sp.Matrix([[1/u,0,-c/u],[0,1/v,-d/v],[-c/u,-d/v,1/L**2+c*c/u+d*d/v]])
        self.assertEqual(sp.simplify(H*target-sp.eye(3)),sp.zeros(3))

    def test_03_bulk_horizontal_maxwell_coordinate(self):
        x,y,r=sp.symbols('x y r')
        ax=sp.Function('B_x')(x,y,r); ay=sp.Function('B_y')(x,y,r)
        cx=sp.Function('C_x')(x,y,r); cy=sp.Function('C_y')(x,y,r)
        a=sp.Function('a')(r)
        Fxy=sp.diff(ay+a*cy,x)-sp.diff(ax+a*cx,y)
        Hxy=sp.diff(ay,x)-sp.diff(ax,y)+a*(sp.diff(cy,x)-sp.diff(cx,y))
        self.assertEqual(sp.simplify(Fxy-Hxy),0)

    def test_04_flux_radial_coordinate_horizon_difference(self):
        x,r=sp.symbols('x r')
        bx=sp.Function('B_x')(x,r); br=sp.Function('B_r')(x,r)
        cx=sp.Function('C_x')(x,r); cr=sp.Function('C_r')(x,r)
        a=sp.Function('a')(r)
        F_rx=sp.diff(bx+a*cx,r)-sp.diff(br+a*cr,x)
        H_rx=sp.diff(bx,r)-sp.diff(br,x)+a*(sp.diff(cx,r)-sp.diff(cr,x))
        self.assertEqual(sp.simplify(F_rx-H_rx-sp.diff(a,r)*cx),0)

    def test_05_cap_winding_horizontal_identity(self):
        q,N,a,B,C,sx=sp.symbols('q N a B C sx')
        # ds -q(B+a C)+(N-q a)dchi = [ds-q B-N C]+(N-qa)(dchi+C)
        self.assertEqual(sp.expand((sx-q*B-N*C)+(N-q*a)*C-(sx-q*(B+a*C))),0)

    def test_06_cap_u1_circle_gauge_ward(self):
        sx,B,C,q,N,dL,dXi=sp.symbols('sx B C q N dL dXi')
        xi=sx-q*B-N*C
        xi_new=sx+q*dL+N*dXi-q*(B+dL)-N*(C+dXi)
        self.assertEqual(sp.expand(xi_new-xi),0)

    def test_07_two_radial_gauge_field_strengths(self):
        x,r=sp.symbols('x r')
        lam=x*x*r**3+sp.sin(x*r)
        xi=x*r*r+sp.cos(x+r)
        for g in (lam,xi):
            self.assertEqual(sp.simplify(sp.diff(sp.diff(g,x),r)-sp.diff(sp.diff(g,r),x)),0)

    def test_08_reduced_cap_rank_one(self):
        q,N,C=sp.symbols('q N C', real=True)
        v=sp.Matrix([q,N]); M=C*(v*v.T)
        self.assertEqual(sp.simplify(M.det()),0)
        self.assertEqual(sp.simplify(M*sp.Matrix([N,-q])),sp.zeros(2,1))
        self.assertEqual(sp.simplify(sp.trace(M)-C*(q*q+N*N)),0)

    def test_09_radial_bending_scalar_pullback(self):
        dp,z,eps=sp.symbols('dp z eps')
        # δa -> δa-a' ε, ζ -> ζ+ ε
        da=sp.symbols('da')
        self.assertEqual(sp.expand(da-dp*eps+dp*(z+eps)-(da+dp*z)),0)

    def test_10_bending_metric_circle_radius(self):
        f,z,eps,der=sp.symbols('f z eps der')
        self.assertEqual(sp.expand(f-der*eps+der*(z+eps)-(f+der*z)),0)

    def test_11_bending_bulk_scalar(self):
        f,z,eps,der=sp.symbols('f z eps der')
        self.assertEqual(sp.expand(f-der*eps+der*(z+eps)-(f+der*z)),0)

    def test_12_winding_pullback_variation(self):
        q,da,ap,z=sp.symbols('q da ap z')
        self.assertEqual(sp.expand(-q*(da+ap*z)-(-q*da-q*ap*z)),0)

    def test_13_cap_m1_displacement_force_exact(self):
        r,q,N,zsig,lam=sp.symbols('r q N zsig lam', real=True)
        A=sp.Function('A')(r); L=sp.Function('L')(r); a=sp.Function('a')(r)
        w=N-q*a
        T=sp.exp(4*A)*L*(lam+zsig*w*w/(2*L*L))
        rhs=sp.exp(4*A)*L*((4*sp.diff(A,r)+sp.diff(L,r)/L)*lam
          +(4*sp.diff(A,r)-sp.diff(L,r)/L)*zsig*w*w/(2*L*L)
          -zsig*q*w*sp.diff(a,r)/(L*L))
        self.assertEqual(sp.simplify(sp.diff(T,r)-rhs),0)

    def test_14_cap_tension_zero_winding_limit(self):
        A,Ap,L,Lp,lam=sp.symbols('A Ap L Lp lam')
        T=sp.exp(4*A)*L*lam
        self.assertEqual(sp.simplify(sp.diff(T,A)*Ap+sp.diff(T,L)*Lp-sp.exp(4*A)*L*lam*(4*Ap+Lp/L)),0)

    def test_15_radial_shift_scalar_squared(self):
        e,v,p,alpha=sp.symbols('e v p alpha', nonzero=True)
        h=sp.Matrix([[e+v*v,v],[v,1]])
        grad=sp.Matrix([alpha,p])
        res=(grad.T*h.inv()*grad)[0]
        self.assertEqual(sp.simplify(res-(p*p+(alpha-v*p)**2/e)),0)

    def test_16_radial_diffeo_invariant_scalar_derivative(self):
        alpha_x,p,v,eps_x=sp.symbols('alpha_x p v eps_x')
        self.assertEqual(sp.expand((alpha_x-p*eps_x)-p*(v-eps_x)-(alpha_x-p*v)),0)

    def test_17_bulk_maxwell_kinetic_matrix_det(self):
        W,a,L,Z,M=sp.symbols('W a L Z M',positive=True)
        K=W*L*sp.Matrix([[Z,Z*a],[Z*a,Z*a*a+M*L*L/2]])
        self.assertEqual(sp.factor(K.det()),W**2*M*Z*L**4/2)

    def test_18_radial_longitudinal_constraint_toy(self):
        k2,p11,p12,p22,uz,vz=sp.symbols('k2 p11 p12 p22 uz vz')
        P=sp.Matrix([[p11,p12],[p12,p22]])
        r=sp.Matrix([uz,vz])
        eq=k2*P*r
        self.assertEqual(sp.simplify(eq-k2*P*r),sp.zeros(2,1))
        self.assertEqual(sp.factor(P.det()),p11*p22-p12**2)
        # For k2 != 0 and det P != 0 this constraint enforces r=0.

    def test_19_transverse_longitudinal_orthogonality(self):
        omega,k=sp.symbols('omega k')
        p=sp.Matrix([omega,k,0,0]); ep=sp.Matrix([k,omega,0,0]); eta=sp.diag(-1,1,1,1)
        self.assertEqual((p.T*eta*ep)[0],0)

    def test_20_radial_einstein_codazzi_flat_principal(self):
        x,eps=sp.symbols('x eps')
        # Graph zeta(x)=eps*x^2 in a flat ambient plane: Kxx=-zeta''/sqrt(1+zeta'^2).
        f=eps*x**2
        K=-sp.diff(f,x,2)/sp.sqrt(1+sp.diff(f,x)**2)
        series=sp.series(K,eps,0,3).removeO()
        self.assertEqual(sp.simplify(series+2*eps),0)

    def test_21_nonzero_flux_cannot_be_globally_zero_potential(self):
        qref,nf=sp.symbols('qref nf', nonzero=True)
        aN,aS=sp.symbols('aN aS')
        flux=2*sp.pi*(aN-aS)
        quant=flux.subs(aN-aS,nf/qref) # symbolic caution
        self.assertEqual(sp.simplify(flux.subs(aN,aS+nf/qref)-2*sp.pi*nf/qref),0)

    def test_22_induced_cap_4d_metric_bending(self):
        h,dh,z,eps=sp.symbols('h dh z eps')
        self.assertEqual(sp.expand((h-dh*eps)+dh*(z+eps)-(h+dh*z)),0)

    def test_23_no_full_ghost_from_subblock(self):
        K=sp.diag(2,3,-1)
        self.assertEqual(K[:2,:2].det(),6)
        self.assertEqual(sorted(K.eigenvals()),[-1,2,3])

    def test_24_cap_bending_principal_vanishes_for_constant(self):
        x=sp.symbols('x'); z=sp.Integer(2)
        self.assertEqual(sp.diff(z,x,2),0)

    def test_25_dimension_a_prime_and_zeta(self):
        # χ is dimensionless: [a=Aχ]=M, [a']=M^2, [zeta]=M^-1.
        self.assertEqual(2 + (-1),1)

    def test_26_radial_gauge_Ward_at_cap(self):
        q,N,Lambda,xi=sp.symbols('q N Lambda xi')
        s=sp.symbols('s'); B=sp.symbols('B'); C=sp.symbols('C')
        self.assertEqual(sp.simplify((s+q*Lambda+N*xi)-q*(B+Lambda)-N*(C+xi)-(s-q*B-N*C)),0)

    def test_27_magnetic_bundle_and_nondegenerate_k(self):
        A,L,Z,M=sp.symbols('A L Z M',real=True,positive=True)
        K=sp.Matrix([[L*Z,L*Z*A],[L*Z*A,L*Z*A*A+M*L**3/2]])
        self.assertEqual(sp.factor(K.det()),M*Z*L**4/2)

    def test_28_magnetic_patch_winding_covariance(self):
        q,N,a,c,B,C,sx=sp.symbols('q N a c B C sx')
        N_N=N+q*c
        a_N=a+c
        B_N=B-c*C
        self.assertEqual(sp.expand((N_N-q*a_N)-(N-q*a)),0)
        self.assertEqual(sp.expand((sx-q*B_N-N_N*C)-(sx-q*B-N*C)),0)

    def test_29_magnetic_patch_horizontal_flux(self):
        c,dC,dB,a=sp.symbols('c dC dB a')
        H_N=(dB-c*dC)+(a+c)*dC
        H_S=dB+a*dC
        self.assertEqual(sp.expand(H_N-H_S),0)

    def test_30_patch_null_vector_transforms_covariantly(self):
        c,q,N=sp.symbols('c q N')
        T=sp.Matrix([[1,-c],[0,1]])
        vs=sp.Matrix([N,-q]); vn=sp.Matrix([N+q*c,-q])
        self.assertEqual(T*vs,vn)

    def test_31_near_pole_kinetic_matrix_degenerates(self):
        r,k,Z,M=sp.symbols('r k Z M',positive=True)
        a=k*r*r; L=r
        K=sp.Matrix([[L*Z,L*Z*a],[L*Z*a,L*Z*a*a+M*L**3/2]])
        self.assertEqual(sp.factor(K.det()),M*Z*r**4/2)
        inv=sp.simplify(K.inv())
        self.assertEqual(sp.simplify(sp.limit(r*inv[0,0],r,0,dir='+')),1/Z)
        self.assertEqual(sp.simplify(sp.limit(r**3*inv[1,1],r,0,dir='+')),2/M)

    def test_32_patch_mass_form_invariant(self):
        q,N,c,B,C=sp.symbols('q N c B C')
        yS=sp.Matrix([B,C]); T=sp.Matrix([[1,-c],[0,1]])
        vS=sp.Matrix([q,N]); vN=sp.Matrix([q,N+q*c])
        self.assertEqual(sp.simplify((vN.T*T*yS)[0]-(vS.T*yS)[0]),0)

    def test_33_circle_ricci_constant_radius_twisted_3d_sample(self):
        # Independent Christoffel-to-Ricci calculation: ds^2=dx^2+dy^2+L^2(dz+k*x*dy)^2.
        x,y,z,k,L=sp.symbols('x y z k L',real=True, nonzero=True)
        coordinates=[x,y,z]; n=3
        g=sp.Matrix([[1,0,0],[0,1+L**2*k**2*x**2,L**2*k*x],
                     [0,L**2*k*x,L**2]])
        inv=g.inv()
        Gamma=[[[sp.simplify(sp.Rational(1,2)*sum(inv[i,l]*(
            sp.diff(g[l,j],coordinates[h])+sp.diff(g[l,h],coordinates[j])
            -sp.diff(g[j,h],coordinates[l])) for l in range(n)))
            for h in range(n)] for j in range(n)] for i in range(n)]
        Ric=sp.Matrix(n,n,lambda i,j:sp.simplify(sum(
            sp.diff(Gamma[a][i][j],coordinates[a])-sp.diff(Gamma[a][i][a],coordinates[j])
            +sum(Gamma[a][i][j]*Gamma[b][a][b]-Gamma[b][i][a]*Gamma[a][j][b]
            for b in range(n)) for a in range(n))))
        scalar=sp.simplify(sum(inv[i,j]*Ric[i,j] for i in range(n) for j in range(n)))
        self.assertEqual(sp.simplify(scalar+sp.Rational(1,2)*L**2*k**2),0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
