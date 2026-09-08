# ULSH-05 / WP1C4B2B — Component Boundary-Residual Linearization

**Datum:** 2026-09-08  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `5a5545ed80a94e99e7c466e5b30919dc47f86d6d`  
**Klassifikation:** analytischer, nichtoperativer lokaler Boundary-Hessian-/Residualblock  
**Physical gate/evidence effect:** `NONE / NONE`

## 1. Kernergebnis

WP1C4B2A hat die zweite Pfadkettenregel der bewegten Interfacewirkung geschlossen, aber die Residualableitungen `Delta R_sigma` und `Delta R_perp` noch nicht komponentisiert. WP1C4B2B schließt genau diese Lücke und assembliert den lokalen linearen Boundary-Residualoperator

\[
\Delta\mathcal R_
=
(\Delta\mathcal R_h^{ab},
\Delta\mathcal R_\phi,
\Delta\mathcal R_A^a,
\Delta\mathcal R_\sigma,
\Delta\mathcal R_\perp)
\]

im bereits eingefrorenen bewegten Interface-Chart.

Das Ergebnis ist **kein globaler physischer Randwertoperator**. Für die gemischte Hessian-Symmetrie wird ausschließlich der lokale Testbereich

\[
\boxed{
\mathscr T_\Sigma
=C_c^\infty(\mathcal M_4)\otimes C_{2\pi}^\infty(S^1_\chi)
}
\]

verwendet: glatte Perturbationen mit kompaktem Support in den vier nichtkompakten Tangentialrichtungen und `2*pi`-Periodizität in `chi`. Auf diesem Testbereich verschwinden integrierte intrinsische Totaldivergenzen und boundary-of-boundary-Terme. Das ist eine mathematische Testdomäne, **keine** Festlegung physischer Anfangs-/Randbedingungen.

Damit wird lokal bewiesen:

```text
WP1_boundary_residual_linearizations = COMPONENTIZED_LOCAL_INTERFACE_OPERATOR
WP1_local_weak_boundary_hessian      = SYMMETRIC_ON_DECLARED_TEST_DOMAIN
WP1_full_global_boundary_hessian     = NOT_CLOSED_PHYSICAL_BC_AND_GLOBAL_CORNER_ADMISSIBILITY_OPEN
```

## 2. Eingefrorene First-Variation-Basis

Aus WP1C4B1D:

\[
B_1
=-\frac12\mathcal R_h^{ab}H_{ab}
-\mathcal R_\phi\Phi_\Sigma
-\mathcal R_A^a\mathcal A_a
+\mathcal R_\sigma s
+\xi\mathcal R_\perp .
\]

Die Residuen sind

\[
\mathcal R_h^{ab}
=M_6^4(\Pi_N^{ab}+\Pi_S^{ab})-S^{ab},
\]

\[
\mathcal R_\phi=Q_{\phi,N}+Q_{\phi,S},
\]

\[
\mathcal R_A^a=Q_{F,N}^a+Q_{F,S}^a-j_\Sigma^a,
\]

\[
\mathcal R_\sigma=D_a(Z_\sigma D^a\sigma),
\]

und in gemeinsamer Normalorientierung

\[
\mathcal R_\perp
=M_6^4[(G_{NN}+\Lambda_6)]_c-[T_{NN}]_c.
\]

Für M1 sind `lambda` und `Z_sigma` konstant in `phi`.

## 3. Notation der bewegten linearen Daten

Die gemeinsame induzierte Metrikvariation ist

\[
H_{ab}=p_{ab}+2\xi K_{ab}+2D_{(a}\tau_{b)},
\qquad
H=\bar h^{ab}H_{ab}.
\]

Für die Kappenphase definieren wir

\[
w_a=D_a\bar\sigma,
\qquad
d_a=D_as-q_\sigma\mathcal A_a.
\]

`d_a` ist unter der linearen U(1)-Transformation invariant.

Auf jeder Bulkseite verwenden wir

\[
q_\phi\equiv N^A\nabla_A\bar\phi,
\qquad
u_a\equiv D_a\bar\phi,
\]

\[
E_a\equiv N^AF_{Aa},
\qquad
B_{ab}\equiv F_{ab},
\]

wobei `N` für den Shape-Kanal die gemeinsame Normalorientierung bezeichnet. Weiter

\[
Z\equiv Z_F(\bar\phi),
\qquad
Q_F^a=ZE^a.
\]

Die totalen bewegten linearen Variationen heißen

\[
\Delta q_\phi=\Delta_\Sigma(N\cdot\nabla\phi),
\qquad
b_{ab}=\Delta_\Sigma F_{ab},
\qquad
e_a=\Delta_\Sigma E_a.
\]

## 4. Metrischer Residualkanal `Delta R_h`

Setze auf jeder Outward-Seite

\[
\Pi_{ab}=K_{ab}-Kh_{ab}.
\]

WP1C3 liefert

\[
\boxed{
\Delta\Pi_{ab}
=\Delta K_{ab}
-\bar h_{ab}\bar h^{cd}\Delta K_{cd}
+\bar h_{ab}\bar K^{cd}H_{cd}
-\bar K H_{ab}.
}
\]

Die Variation mit hochgestellten Indizes ist

\[
\boxed{
\Delta\Pi^{ab}
=\bar h^{ac}\bar h^{bd}\Delta\Pi_{cd}
-H^{ac}\bar\Pi_c{}^b
-H^{bc}\bar\Pi^a{}_c.
}
\]

Für den M1-Kappenstress

\[
S_{ab}
=-\left(\lambda+\frac12Z_\sigma X\right)h_{ab}
+Z_\sigma w_aw_b,
\qquad
X=w_aw^a,
\]

gilt

\[
\Delta X=2w^ad_a-H^{ab}w_aw_b
\]

und

\[
\boxed{
\begin{aligned}
\Delta S_{ab}={}&
-\frac12Z_\sigma\Delta X\,\bar h_{ab}
-\left(\lambda+\frac12Z_\sigma\bar X\right)H_{ab}\\
&+Z_\sigma(d_aw_b+w_ad_b).
\end{aligned}
}
\]

Daraus

\[
\boxed{
\Delta S^{ab}
=\bar h^{ac}\bar h^{bd}\Delta S_{cd}
-H^{ac}\bar S_c{}^b
-H^{bc}\bar S^a{}_c.
}
\]

Somit ist

\[
\boxed{
\Delta\mathcal R_h^{ab}
=M_6^4\sum_{s=N,S}\Delta\Pi_s^{ab}
-\Delta S^{ab}.
}
\]

Keine Israelgleichung wurde eingesetzt.

## 5. Skalarer Normalflusskanal `Delta R_phi`

Im M1-Freeze gilt `C_phi=0` und auch `Delta C_phi=0`. Daher

\[
\boxed{
\Delta\mathcal R_\phi
=\sum_{s=N,S}\Delta_\Sigma Q_{\phi,s}
}
\]

mit dem bereits in WP1C4A hergeleiteten bewegten Operator

\[
\boxed{
\Delta_\Sigma Q_{\phi,s}
=\bar X_s^*\left[
(\delta n_s^A)\bar\nabla_A\bar\phi_s
+\bar n_s^A\bar\nabla_A\varphi_s
+\mathcal L_{z_s}(\bar n_s^A\bar\nabla_A\bar\phi_s)
\right].
}
\]

`delta n_s^A` ist durch die WP1C3-Normierungs-/Orthogonalitätsbedingungen bestimmt; der Ausdruck ist dadurch vollständig in der doubly-covariant moving-interface-Geometrie definiert.

## 6. Gauge-Normalflusskanal `Delta R_A`

Aus WP1C4A

\[
\boxed{
\Delta_\Sigma Q_{F,s}^a
=\bar X_s^*\left[
\delta(e_B{}^a n_AZ_FF^{AB})
+\mathcal L_{z_s}(e_B{}^a\bar n_A\bar Z_F\bar F^{AB})
\right].
}
\]

Für den M1-Kappenstrom

\[
j_\Sigma^a=q_\sigma Z_\sigma w^a
\]

folgt

\[
\boxed{
\Delta j_\Sigma^a
=q_\sigma Z_\sigma(d^a-H^{ab}w_b).
}
\]

Damit

\[
\boxed{
\Delta\mathcal R_A^a
=\sum_{s=N,S}\Delta_\Sigma Q_{F,s}^a
-q_\sigma Z_\sigma(d^a-H^{ab}w_b).
}
\]

Dieser Kanal ist manifest invariant unter der linearen Kappen-U(1)-Transformation.

## 7. Kappenphasenkanal `Delta R_sigma`

Dies ist der erste in B2A noch fehlende Komponentenblock.

Da `Z_sigma` in M1 konstant ist,

\[
\mathcal R_\sigma=Z_\sigma D_aw^a.
\]

Es gilt

\[
\Delta w_a=d_a,
\qquad
\Delta w^a=d^a-H^{ab}w_b,
\]

und für die Variation der 5D-Verbindung

\[
\Delta\Gamma^a{}_{ac}=\frac12D_cH.
\]

Daher

\[
\boxed{
\Delta\mathcal R_\sigma
=Z_\sigma\left[
D_a(d^a-H^{ab}w_b)
+\frac12w^aD_aH
\right].
}
\]

Äquivalent

\[
\boxed{
\Delta\mathcal R_\sigma
=Z_\sigma\left[
D_ad^a
-D_a(H^{ab}w_b)
+\frac12w^aD_aH
\right].
}
\]

**[BEWIESEN]** Dies ist die exakte lineare Variation des intrinsischen M1-Phasenresiduals im deklarierten induzierten Chart.

Dimensionscheck:

\[
[Z_\sigma]=M^3,
\quad[D_a]=M,
\quad[d_a]=M,
\]

also

\[
[\Delta\mathcal R_\sigma]=M^5,
\]

wie für eine 5D-Kappendichtevariation erforderlich.

## 8. Geometrischer Teil von `Delta R_perp`

WP1C4B1C fixiert für eine spacelike Normale

\[
G_{NN}
=\frac12\left(K^2-K_{ab}K^{ab}-R^{(5)}\right).
\]

Setze

\[
k_{ab}\equiv\Delta K_{ab}.
\]

Aus

\[
\Delta K
=\bar h^{ab}k_{ab}-H^{ab}\bar K_{ab}
\]

folgt

\[
\boxed{
\Delta(K^2-K_{ab}K^{ab})
=-2\bar\Pi^{ab}k_{ab}
+2H^{ab}
(\bar K_a{}^c\bar K_{bc}-\bar K\bar K_{ab}).
}
\]

Die intrinsische Skalarkrümmung variiert als

\[
\boxed{
\Delta R^{(5)}
=-\bar R^{(5)ab}H_{ab}
+D^aD^bH_{ab}-D^2H.
}
\]

Damit auf jeder Seite

\[
\boxed{
\begin{aligned}
\Delta G_{NN}={}&
-\bar\Pi^{ab}k_{ab}
+H^{ab}(\bar K_a{}^c\bar K_{bc}-\bar K\bar K_{ab})\\
&+\frac12\bar R^{(5)ab}H_{ab}
-\frac12D^aD^bH_{ab}
+\frac12D^2H.
\end{aligned}
}
\]

### 8.1 Common-normal Jump

Mit

\[
K_{ab}^{c,N}=K_{ab}^{out,N},
\qquad
K_{ab}^{c,S}=-K_{ab}^{out,S}
\]

und analog für `k_ab` ist die erste Fundamentalform auf beiden Seiten identisch. Daher ist auch `Delta R^(5)` identisch und fällt im Jump weg:

\[
\boxed{
[\Delta G_{NN}]_c
=-[\Pi^{ab}k_{ab}]_c
+H^{ab}
[K_a{}^cK_{bc}-KK_{ab}]_c.
}
\]

**[BEWIESEN]** Der linearisierte geometrische Shape-Jump benötigt nach First-Fundamental-Form-Matching keine separate intrinsische `Delta R^(5)`-Jumpquelle.

## 9. Materieller Teil von `Delta R_perp`

Die Parentwirkung liefert

\[
T_{NN}=T_{NN}^{(\phi)}+T_{NN}^{(F)}.
\]

### 9.1 Skalar

Mit

\[
T_{NN}^{(\phi)}
=\frac12q_\phi^2
-\frac12\nu_a\nu^a
-U(\bar\phi)
\]

folgt für die totale bewegte Interfacevariation

\[
\boxed{
\Delta T_{NN}^{(\phi)}
=q_\phi\Delta q_\phi
+\frac12H^{ab}\nu_a\nu_b
-\nu^aD_a\Phi_\Sigma
-U_{,\phi}\Phi_\Sigma.
}
\]

### 9.2 Maxwell

Zerlege

\[
T_{NN}^{(F)}
=Z\left(\frac12E_aE^a-\frac14B_{ab}B^{ab}\right).
\]

Dann

\[
\boxed{
\begin{aligned}
\Delta T_{NN}^{(F)}={}&
Z_{,\phi}\Phi_\Sigma
\left(\frac12E^2-\frac14B^2\right)\\
&+Z\Big[
-\frac12H^{ab}E_aE_b
+E^ae_a
-\frac12B^{ab}b_{ab}
+\frac12H^{ac}B_a{}^dB_{cd}
\Big].
\end{aligned}
}
\]

Der Normal-Elektro-/Fluxperturbator kann vollständig durch den bereits existierenden C4A-Fluxoperator ersetzt werden. Aus

\[
Q_F^a=ZE^a
\]

folgt

\[
\boxed{
e_a
=Z^{-1}\bar h_{ab}\Delta Q_F^b
+H_a{}^bE_b
-\frac{Z_{,\phi}}{Z}\Phi_\Sigma E_a.
}
\]

### 9.3 Statischer M1-Hintergrundgrenzfall

Für den eingefrorenen radialen M1-Hintergrund gilt tangential

\[
\nu_a=0,
\qquad
B_{ab}=0.
\]

Dann

\[
\boxed{
\Delta T_{NN}^{(\phi)}
=q_\phi\Delta q_\phi-U_{,\phi}\Phi_\Sigma,
}
\]

\[
\boxed{
\Delta T_{NN}^{(F)}
=E_a\Delta Q_F^a
+\frac Z2H^{ab}E_aE_b
-\frac{Z_{,\phi}}2\Phi_\Sigma E^2.
}
\]

Da `phi` und `Phi_Sigma` auf demselben Interface kontinuierlich sind und `U` dieselbe M1-Funktion auf beiden Seiten ist, fällt der reine `U_,phi Phi_Sigma`-Term im common-normal Jump weg. Dies eliminiert **nicht** die übrigen Skalar- oder Maxwellantworten.

## 10. Vollständiger lokaler Shape-Residualoperator

Die kosmologische Konstante trägt wegen `N^2=1` und konstantem `Lambda6` keine lineare Zusatzvariation bei. Somit

\[
\boxed{
\Delta\mathcal R_\perp
=M_6^4[\Delta G_{NN}]_c
-[\Delta T_{NN}^{(\phi)}+\Delta T_{NN}^{(F)}]_c.
}
\]

Mit der geometrischen Jumpform:

\[
\boxed{
\begin{aligned}
\Delta\mathcal R_\perp={}&
-M_6^4[\Pi^{ab}k_{ab}]_c
+M_6^4H^{ab}[K_a{}^cK_{bc}-KK_{ab}]_c\\
&-[\Delta T_{NN}^{(\phi)}+\Delta T_{NN}^{(F)}]_c.
\end{aligned}
}
\]

**[BEWIESEN]** Dies ist die linearisierte direkte `NN`-Constraint-Jump-Form des Shape-Kanals. Israel wurde nicht als Voraussetzung eingesetzt.

## 11. Lokale schwache Hessian-Symmetrie

Definiere für zwei unabhängige Testperturbationen `u,v in T_Sigma`

\[
\mathbb H_\Sigma[u,v]
\equiv
\left.
\frac{\partial^2}{\partial\epsilon\,\partial\eta}
S_\Sigma[\bar\Phi+\epsilon u+\eta v]
\right|_{\epsilon=\eta=0}.
\]

Die kanonische EH+GHY+Materie+Kappenwirkung ist im hier verwendeten regulären nicht-nullartigen lokalen Chart zweimal Fréchet-differenzierbar. WP1C4B2A hat zusätzlich den Pfadbeschleunigungsanteil `DS[v]` von der bilinearen Chart-Hesse getrennt.

Auf `T_Sigma` verschwinden integrierte intrinsische Totaldivergenzen und boundary-of-boundary-Terme. Daher gilt die gewöhnliche Schwarz-Symmetrie

\[
\boxed{
\mathbb H_\Sigma[u,v]
=\mathbb H_\Sigma[v,u].
}
\]

Äquivalent muss der hier assemblierte Residualoperator in der von `B1` festgelegten schwachen Paarung symmetrisch sein.

**[BEWIESEN / KONDITIONAL AUF DIE DEKLARIERTE TESTDOMÄNE]** Lokale gemischte Hessian-Symmetrie.

Diese Aussage ist **nicht**:

- eine globale field-space-kovariante Hessian-Aussage;
- eine Freigabe physischer Randbedingungen;
- ein Ghost-/Positivitätsbeweis;
- ein Modenspektrum;
- ein Background-Solverlauf.

## 12. Unabhängige Kontrollen

### 12.1 Phasenresidual

Für einen eindimensionalen intrinsischen Kontrollchart

\[
h(\epsilon,x)=1+\epsilon H(x),
\qquad
w(\epsilon,x)=w(x)+\epsilon d(x)
\]

wird

\[
R_\sigma(\epsilon)
=\frac{Z_\sigma}{\sqrt h}
\partial_x\left(\frac{w(\epsilon)}{\sqrt h}\right)
\]

direkt differenziert. Das Ergebnis ist

\[
Z_\sigma[d'-Hw'-\tfrac12H'w],
\]

identisch mit der Komponentenform aus Abschnitt 7.

### 12.2 Gauss-Shape-Kernel

Für konstante diagonale `h_ab`, `K_ab`, `H_ab`, `k_ab` wird `K^2-K_ab K^ab` direkt entlang `h+epsilon H`, `K+epsilon k` differenziert. Die zentrale Finite Difference stimmt mit

\[
-2\Pi^{ab}k_{ab}
+2H^{ab}(K_a{}^cK_{bc}-KK_{ab})
\]

überein.

### 12.3 Materieller `T_NN`-Kernel

Ein unabhängiger diagonaler Lorentz-Kontrollfall differenziert direkt

\[
\frac12q_\phi^2-\frac12\nu^2-U
+Z\left(\frac12E^2-\frac14B^2\right)
\]

gegen die Formeln aus Abschnitt 9.

### 12.4 Gemischter Kappen-Hessian

Der direkte Zwei-Parameter-Koeffizient der unexpandierten M1-Kappendichte wird mit der Polarisation des gemergten WP1C2-Quadratkoeffizienten verglichen. Dadurch werden sowohl die gemischte Symmetrie als auch die Faktoren `1/2` unabhängig kontrolliert.

## 13. Gültigkeitsbereich und Grenzfälle

### Fixed interface

Für `xi=tau=0` reduziert sich `H_ab` auf den festen Pullback `p_ab`, und die Kappenkomponenten gehen auf WP1C2 zurück.

### Kein Winding

Für `w_a=0` wird

\[
\Delta\mathcal R_\sigma=Z_\sigma D_ad^a.
\]

### Kein tangentialer Skalargradient / kein tangentiales Maxwellfeld

Für den statischen M1-Hintergrund gelten die vereinfachten `Delta T_NN`-Formeln aus Abschnitt 9.3.

### Common-normal First-Fundamental-Form-Matching

Nur unter

\[
H_{ab}^{(N)}=H_{ab}^{(S)}
\]

fällt `Delta R^(5)` im Shape-Jump weg. Ohne dieses Matching muss die vollständige per-side Formel aus Abschnitt 8 verwendet werden.

## 14. Status

**[BEWIESEN]** `Delta R_sigma` ist komponentisiert und U(1)-invariant.

**[BEWIESEN]** `Delta R_perp` ist als direkter linearer regionaler `NN`-Constraint-Jump in common-normal Orientierung komponentisiert.

**[BEWIESEN]** Der intrinsische `Delta R^(5)`-Anteil fällt bei gemeinsamer erster Fundamentalform aus dem Jump.

**[BEWIESEN/KONDITIONAL]** Der lokale schwache Boundary-Hessian ist auf `T_Sigma` gemischt symmetrisch.

**[OFFEN]** Globale Tangential-/Corner-Admissibilität für physische, nicht kompakt getragene Randdaten.

**[OFFEN]** Physische Anfangs-/Randbedingungen, S/V/T-Reduktion und Constraint-Elimination.

**[OFFEN]** Global kovarianter field-space-Hessian mit Konfigurationsraumverbindung.

## 15. Firewalls

```text
WP1_boundary_second_variation_chain_rule = DERIVED
WP1_boundary_residual_linearizations      = COMPONENTIZED_LOCAL_INTERFACE_OPERATOR
WP1_local_weak_boundary_hessian           = SYMMETRIC_ON_DECLARED_TEST_DOMAIN
WP1_full_global_boundary_hessian          = NOT_CLOSED_PHYSICAL_BC_AND_GLOBAL_CORNER_ADMISSIBILITY_OPEN
WP1_full_quadratic_action                  = NOT_CLOSED
PERTURBED_JUNCTION_SYSTEM                  = NOT_RELEASED
PHYSICAL_BACKGROUND                        = NOT_ESTABLISHED
FM-G0                                      = OPEN
AuthorizationDecision                      = NOT_CREATED
SingleUseGrant                             = NOT_CREATED
BACKEND_IMPORT                             = NOT_EXECUTED
SOLVER_EXECUTION                           = NOT_EXECUTED
PHYSICAL_RESPONSE_RANK                     = NOT_EXECUTED
K1-D                                       = NOT_RELEASED
K1-E                                       = NOT_ADMISSIBLE
physical_gate_effect                       = NONE
physical_evidence_effect                   = NONE
```

Nächster zulässiger Block ist `ULSH-05/WP1C4B2C`: globale Corner-/Support-Admissibilität und physische Boundary-domain-Preflight **oder**, falls diese globale Domain nicht ohne Hintergrundfreigabe bestimmbar ist, der Übergang zu einer explizit konditionalen S/V/T-Gauge-/Constraint-Struktur ohne Solverausführung.
