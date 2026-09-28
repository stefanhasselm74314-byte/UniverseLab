# ULSH-05 / WP1C4B1D — direkte Moving-Action-Shape-Variation

**Datum:** 2026-09-08  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `09d9b075f3fc842f1158eb4cf8a56ed3c27185fb`  
**Klassifikation:** analytischer, nichtoperativer First-Variation-Abschluss  
**Physical gate/evidence effect:** `NONE / NONE`

## 1. Ziel

WP1C4B1B hat abstrakt bewiesen, dass der normale Shape-Kanal über die Diffeomorphismus-Ward-Identität an das vollständige Bulk-/Junction-System gebunden ist. WP1C4B1C hat daraus in den konkreten C-PHYS-M1-Konventionen die passive Constraint-Relation

\[
S^{ab}\langle K_{ab}\rangle_c=[T_{NN}]_c
\]

über die beiden regionalen `NN`-Einstein-Constraints plus Israel hergeleitet.

WP1C4B1D liefert den noch fehlenden unabhängigen Weg: die **direkte erste Variation der bewegten Gesamtwirkung**. Die `NN`-Constraints werden dabei nicht eingesetzt. Erst im zweiten Schritt wird gezeigt, wie der direkte Shape-Residual durch Israel auf die C4B1C-Form reduziert und durch die regionalen Constraints redundant wird.

## 2. Warum ein reiner Koordinatenshift nicht genügt

Im asymmetrischen Zwei-Seiten-System ist die Kappe ein einziges geometrisches Interface. Die induzierte Metrik und die gepullbackten Felder sind gemeinsame Interfacevariablen. Ein bloßer Shift der Einbettung bei gleichzeitig eingefrorenen Eulerian-Bulkfeldern würde auf den beiden Seiten im Allgemeinen verschiedene induzierte Variationen erzeugen und damit den Glue-Vertrag verlassen.

Wir verwenden deshalb die bereits eingefrorenen **totalen Pullbackvariationen** zusammen mit einem gemeinsamen Normal-Shape-Parameter.

Mit

\[
N=n_N^{out}=-n_S^{out},
\qquad
\xi_N=+\xi,
\qquad
\xi_S=-\xi
\]

definieren wir im reinen Normalkanal `tau^a=0`:

\[
H_{ab}=q_{ab,s}+2\xi_sK^{out}_{ab,s},
\]

\[
\Phi_\Sigma=\varphi_s+\xi_s Q_{\phi,s},
\qquad
Q_{\phi,s}=n_s^A\nabla_A\bar\phi_s,
\]

sowie gauge-kovariant modulo einen intrinsischen exakten U(1)-Term

\[
\mathcal A_a=a_{a,s}+\xi_sF_{na,s}.
\]

Die Kappenphase `sigma` ist ein intrinsisches Feld auf der abstrakten `Sigma`; ihre unabhängige Variation wird mit `s` bezeichnet.

## 3. Gravitation: direkte bewegte Randvariation

Für eine Region

\[
S_{g,s}
=\frac{M_6^4}{2}\int_{M_s}\sqrt{-g}(R-2\Lambda_6)
+M_6^4\int_\Sigma\sqrt{-h}K_s
\]

liefert WP1B bei fester Einbettung den Brown–York-Randterm

\[
\frac{M_6^4}{2}\int_\Sigma\sqrt{-h}\,\Pi_{ab}\,\delta h^{ab},
\qquad
\Pi_{ab}=K_{ab}-Kh_{ab}.
\]

Für die bewegte Grenze kommen drei Beiträge zusammen:

1. Transport des Einstein-Hilbert-Bulkvolumens;
2. normale Variation der GHY-Dichte;
3. Umschreiben der Eulerian induzierten Metrikvariation in die totale Pullbackvariation `H_ab`.

### 3.1 Lokaler Gaussian-normaler Kontrollraum

In einer boundary-adaptierten GN-Nachbarschaft gilt

\[
ds^2=dn^2+h_{ab}(n,y)dy^ady^b,
\qquad
K_{ab}=\frac12\partial_n h_{ab},
\]

und

\[
R^{(6)}
=R^{(5)}-K^2-K_{ab}K^{ab}-2\partial_nK.
\]

Bei einer Outward-Verschiebung `xi_s` liefert der Bulktransport

\[
\frac{M_6^4}{2}\sqrt{-h}\,\xi_s(R^{(6)}-2\Lambda_6),
\]

während

\[
\delta_{move}(\sqrt{-h}K)
=\sqrt{-h}\,\xi_s(K^2+\partial_nK).
\]

Außerdem gilt

\[
q_{ab,s}=H_{ab}-2\xi_sK_{ab,s},
\]

und daher für die inverse Eulerian-Variation

\[
\delta h^{ab}_{Eulerian}
=-H^{ab}+2\xi_sK^{ab}.
\]

Einsetzen in den WP1B-Brown–York-Term und Zusammenfassen ergibt

\[
\boxed{
\delta S_{g,s}|_\Sigma
=
\sqrt{-h}\left[
-\frac{M_6^4}{2}\Pi_s^{ab}H_{ab}
-\xi_sM_6^4(G_{NN,s}+\Lambda_6)
\right]
}
\]

plus Bulk-Euler-Lagrange-, Tangential- und gegebenenfalls Corner-Terme.

Die GN-Rechnung dient nur der lokalen Komponentenreduktion. Das Endergebnis ist der geometrische Normal-Einstein-Residual und damit unabhängig von dieser lokalen Kontrollkoordinate.

### 3.2 Direkter 6D-Warp-Kontrollfall

Für

\[
ds^2=dr^2+e^{2cr}\eta_{ab}dy^ady^b
\]

mit fünf tangentialen Richtungen gilt

\[
R=-30c^2,
\qquad
K=5c,
\qquad
G_{rr}=10c^2.
\]

Pro Einheit des tangentialen Koordinatenvolumens hat ein Intervall mit bewegtem oberen Rand `rho`

\[
S_g(\rho)
=\frac12\int_0^\rho dr\,e^{5cr}(-30c^2-2\Lambda_6)
+5c\,e^{5c\rho}
+\text{konstanter unterer Randterm}.
\]

Direkte Ableitung ergibt

\[
\frac{dS_g}{d\rho}
=e^{5c\rho}(10c^2-\Lambda_6).
\]

Auf der anderen Seite besitzt ein festes Ambientfeld bei bewegtem Rand

\[
H_{ab}=2K_{ab},
\]

und

\[
-\frac12\Pi^{ab}H_{ab}=20c^2,
\qquad
-(G_{rr}+\Lambda_6)=-(10c^2+\Lambda_6).
\]

Die Summe ist exakt

\[
10c^2-\Lambda_6,
\]

also derselbe direkte Randableitungswert.

## 4. Skalarsektor

Für `Z_phi=1` ist der regionale Bulk-Skalarfluss

\[
Q_{\phi,s}=n_s^A\nabla_A\bar\phi_s.
\]

Die Eulerian Skalarvariation lautet

\[
\varphi_s=\Phi_\Sigma-\xi_sQ_{\phi,s}.
\]

Der integrierte Bulk-Skalarterm liefert am Rand `-Q_phi varphi`; der bewegte Bulkbereich liefert zusätzlich die Lagrangedichte. Zusammen entsteht

\[
\boxed{
\delta S_{\phi,s}|_\Sigma
=\sqrt{-h}\left[
-Q_{\phi,s}\Phi_\Sigma
+\xi_sT_{NN,\phi,s}
\right]
}
\]

plus Bulk-Skalar-Euler-Lagrange-Term.

Ein flacher Kontrollfall `phi=v r`, `L=-v^2/2-U` ergibt direkt `dS/d rho=L`. Die Interfaceform liefert

\[
-v^2+\left(\frac12v^2-U\right)
=-\frac12v^2-U=L.
\]

## 5. Maxwellsektor

Definiere

\[
Q_{F,s}^a=n_AZ_FF^{Aa}.
\]

Modulo einen intrinsischen U(1)-exakten Term kann die totale tangentiale Pullbackvariation als

\[
\mathcal A_a=a_{a,s}+\xi_sF_{na,s}
\]

geschrieben werden. Der regionale Randterm `-Q_F^a a_a` plus Bulktransport ergibt

\[
\boxed{
\delta S_{F,s}|_\Sigma
=\sqrt{-h}\left[
-Q_{F,s}^a\mathcal A_a
+\xi_sT_{NN,F,s}
\right]
}
\]

plus Maxwell-Euler-Lagrange- und intrinsisch gauge-exakte Terme.

Für einen flachen Kontrollsektor mit konstantem `F_{r chi}=f` und konstantem `Z_F=Z` gilt

\[
L_F=-\frac12Zf^2,
\qquad
Q_F^\chi=Zf,
\qquad
T_{NN,F}=\frac12Zf^2.
\]

Bei `A_chi=f r` ist `mathcal A_chi=f` für Einheitsverschiebung und damit

\[
-Q_F^\chi\mathcal A_\chi+T_{NN,F}
=-\frac12Zf^2=L_F,
\]

wieder gleich der direkten Moving-Interval-Ableitung.

## 6. Intrinsische Kappenwirkung

Die M1-Kappenwirkung ist intrinsisch auf dem festen abstrakten `Sigma` konstruiert:

\[
S_\Sigma=-\int_\Sigma\sqrt{-h}
\left[\lambda+\frac12Z_\sigma D_a\sigma D^a\sigma\right].
\]

Ihre erste Variation in den **totalen** induzierten Variablen lautet

\[
\boxed{
\delta S_\Sigma
=\int_\Sigma\sqrt{-h}
\left[
\frac12S^{ab}H_{ab}
-C_\phi\Phi_\Sigma
+j_\Sigma^a\mathcal A_a
+\mathcal R_\sigma s
\right]
}
\]

mit

\[
C_\phi=\lambda_{,\phi}+\frac12Z_{\sigma,\phi}X_\sigma,
\]

\[
j_\Sigma^a=q_\sigma Z_\sigma D^a\sigma,
\qquad
\mathcal R_\sigma=D_a(Z_\sigma D^a\sigma).
\]

Im eingefrorenen M1 gilt

\[
C_\phi=0.
\]

Es existiert **kein zusätzlicher nackter `xi`-Term** der intrinsischen Kappenwirkung. Die Einbettungsabhängigkeit läuft über die gepullbackten induzierten Felder. Ein unde­klarierter normaler Lie-Drag einer intrinsischen 5-Form bleibt verboten.

## 7. Vollständige Interfacebasis der ersten Variation

Definiere

\[
\mathcal R_h^{ab}
=M_6^4(\Pi_N^{ab}+\Pi_S^{ab})-S^{ab},
\]

\[
\mathcal R_\phi
=Q_{\phi,N}+Q_{\phi,S}+C_\phi,
\]

\[
\mathcal R_A^a
=Q_{F,N}^a+Q_{F,S}^a-j_\Sigma^a,
\]

\[
\mathcal R_\sigma
=D_a(Z_\sigma D^a\sigma).
\]

Mit `xi_N=+xi`, `xi_S=-xi` ist der direkte Normal-Shape-Residual

\[
\boxed{
\mathcal R_\perp^{direct}
=M_6^4[(G_{NN}+\Lambda_6)]_c-[T_{NN}]_c
}.
\]

Damit lautet der Interfaceanteil

\[
\boxed{
\delta S|_\Sigma
=\int_\Sigma\sqrt{-h}
\left[
-\frac12\mathcal R_h^{ab}H_{ab}
-\mathcal R_\phi\Phi_\Sigma
-\mathcal R_A^a\mathcal A_a
+\mathcal R_\sigma s
+\xi\mathcal R_\perp^{direct}
\right]
}
\]

plus den hier nicht erneut reduzierten tangentialen Reparameterisierungs-/Corner-Kanälen.

Diese Darstellung ist der projektinterne konkrete First-Variation-Inhalt der abstrakten WP1C4B1B-Ward-Struktur.

## 8. Äquivalenz zu WP1C4B1C

### 8.1 Mit Israel

Wenn

\[
\mathcal R_h^{ab}=0,
\]

gilt die metrische Israel-Junction. Dann liefert die in C4B1C hergeleitete Gauss-/Israel-Identität

\[
M_6^4[G_{NN}]_c
=S^{ab}\langle K_{ab}\rangle_c.
\]

Ein gemeinsames `Lambda6` fällt im Jump weg. Daher

\[
\boxed{
\mathcal R_\perp^{direct}
=S^{ab}\langle K_{ab}\rangle_c-[T_{NN}]_c
}.
\]

Dies ist exakt die C4B1C-passive Relation als Residuum.

### 8.2 Mit den regionalen `NN`-Constraints

Wenn in beiden Regionen

\[
M_6^4(G_{NN,s}+\Lambda_6)-T_{NN,s}=0,
\]

dann gilt unmittelbar

\[
\boxed{
\mathcal R_\perp^{direct}=0
}.
\]

Dafür wird Israel **nicht** benötigt. Israel wird erst benötigt, um denselben verschwindenden Constraint-Jump als Oberflächenform `S<K>-[T]` auszudrücken.

Damit ist die Logik exakt:

1. regionale `NN`-Constraints `=>` direkter Shape-Residual verschwindet;
2. Israel `=>` der direkte Residual ist äquivalent zum passiven C4B1C-Residual;
3. Israel allein `!=` Shape-Abschluss.

## 9. Noether-/Ward-Interpretation

Die fünf Interfacekanäle

\[
H_{ab},\quad \Phi_\Sigma,\quad \mathcal A_a,\quad s,\quad \xi
\]

besitzen die Residuen

\[
\mathcal R_h^{ab},\quad
\mathcal R_\phi,\quad
\mathcal R_A^a,\quad
\mathcal R_\sigma,\quad
\mathcal R_\perp^{direct}.
\]

Sie sind nicht fünf unabhängige physikalische Gleichungen. Diffeomorphismus- und U(1)-Invarianz erzeugen Ward-/Noether-Relationen zwischen Bulk- und Interfacekanälen. WP1C4B1D macht diese Residualbasis explizit, ohne daraus neue Freiheitsgrade zu erfinden.

Insbesondere ist die Shape-Gleichung kein zusätzlicher Shooting-Residual, wenn beide regionalen `NN`-Constraints bereits Bestandteil des BVP sind.

## 10. Status

Neu bewiesen:

- direkte erste Moving-Action-Interfacezerlegung;
- gravitativer Shape-Koeffizient `-M6^4(G_NN+Lambda6)` pro Region;
- Materie-Shape-Koeffizient `+T_NN` pro Region;
- kompletter gemeinsamer Shape-Residual als Jump der regionalen `NN`-Constraint-Residuals;
- explizite Metric-/Scalar-/Gauge-/Phase-/Shape-Residualbasis;
- Äquivalenz zur C4B1C-passiven Relation nach Israel;
- Redundanz des Shape-Kanals bei beiden regionalen `NN`-Constraints.

Weiter offen:

- zweite bewegte GHY-/Kappenvariation;
- vollständige Boundary-Hesse;
- configuration-space connection;
- tangentiale Surface-Ward-Komponentenreduktion in demselben Paket;
- released perturbed BVP operator;
- S/V/T und Constraint-Elimination;
- physischer Background;
- Ghostfreiheit und Stabilität;
- 6D→4D-Observablen.

## 11. Unveränderte Gates

```text
WP1 first shape level          CLOSED_ANALYTICALLY_AS_REDUNDANT_CONSTRAINT_CHANNEL
WP1 full boundary Hessian      NOT_CLOSED
WP1 full quadratic action      NOT_CLOSED
PERTURBED_JUNCTION_SYSTEM      NOT_RELEASED
PHYSICAL_BACKGROUND            NOT_ESTABLISHED
FM-G0                          OPEN
AuthorizationDecision          NOT_CREATED
SingleUseGrant                 NOT_CREATED
BACKEND_IMPORT                 NOT_EXECUTED
SOLVER_EXECUTION               NOT_EXECUTED
PHYSICAL_RESPONSE_RANK         NOT_EXECUTED
K1-D                           NOT_RELEASED
K1-E                           NOT_ADMISSIBLE
physical_gate_effect           NONE
physical_evidence_effect       NONE
```

Der nächste zulässige Block ist `ULSH-05/WP1C4B2A`: zweite bewegte GHY- und intrinsische Kappenvariation im deklarierten affinen Chart, mit expliziter Trennung von First-Residual×Path-Acceleration und bilinearer Chart-Hesse.
