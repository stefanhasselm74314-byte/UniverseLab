# ULSH-05 / WP1C4B1C — passive Shape-Constraint in C-PHYS-M1

**Datum:** 2026-09-08  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `9c4795b878360538125029fb1cf4905e2ae1c425`  
**Status:** analytischer, nichtoperativer Constraint-Preflight  
**Physical gate/evidence effect:** `NONE / NONE`

## 1. Ziel

WP1C4B1B hat die abstrakte Diffeomorphismus-Ward-Aussage eingefroren: der Normal-Shape-Residual ist im vollständigen Bulk-plus-Junction-System bedingt redundant, Israel allein reicht aber nicht. WP1C4B1C reduziert den rein gravitativen Constraint-Teil dieser Aussage erstmals komponentenweise in den kanonischen UniverseLab-Konventionen.

Das Ergebnis ist kein physischer Hintergrundlauf und keine zusätzliche Randbedingung. Es ist eine algebraische Konsistenzrelation zwischen den beiden regionalen `NN`-Einstein-Constraints und der metrischen Israel-Junction.

## 2. Gemeinsame Orientierung

Die regionalen Normalen zeigen jeweils aus der Region zur Kappe. Mit dem bereits eingefrorenen gemeinsamen Normalenvektor

\[
N^A=n_N^A=-n_S^A
\]

gilt für die Extrinsikkrümmungen

\[
K^{c,N}_{ab}=K^{out,N}_{ab},\qquad
K^{c,S}_{ab}=-K^{out,S}_{ab}.
\]

Für gemeinsame Normalwerte definieren wir

\[
[X]_c=X_S^c-X_N^c,
\qquad
\langle X\rangle_c=\frac{X_S^c+X_N^c}{2}.
\]

Die UniverseLab-Israelgleichung in Outward-Sum-Notation lautet

\[
\Pi^{out,N}_{ab}+\Pi^{out,S}_{ab}=\kappa_6^2 S_{ab},
\qquad
\Pi_{ab}=K_{ab}-Kh_{ab}.
\]

In gemeinsamer Normalnotation wird daraus

\[
\boxed{[\Pi_{ab}]_c=-\kappa_6^2S_{ab}}.
\]

Für die fünf-dimensionale Kappe folgt aus der Spur

\[
[K]_c=\frac{\kappa_6^2}{4}S,
\]

und daher

\[
[K_{ab}]_c
=-\kappa_6^2\left(S_{ab}-\frac14Sh_{ab}\right).
\]

## 3. Quadratische Jump-Identität

Setze

\[
Q[K]=K^2-K_{ab}K^{ab}.
\]

Dann gilt rein algebraisch

\[
[Q]_c
=2\left(\langle K\rangle_c[K]_c
-\langle K_{ab}\rangle_c[K^{ab}]_c\right).
\]

Einsetzen der Israel-Jumps liefert

\[
\boxed{
[Q]_c=2\kappa_6^2S^{ab}\langle K_{ab}\rangle_c
}.
\]

Dieser Schritt benötigt weder einen Background-Solver noch die Feldgleichungen im Bulk.

## 4. Gauss-/Hamilton-Projektion und Vorzeichen

WP1B verwendet

\[
K_{ab}=+h_a{}^Ah_b{}^B\nabla_An_B.
\]

Für die spacelike Normale `n^2=+1` ist der projektkompatible Normal-Einstein-Constraint

\[
\boxed{
G_{NN}=\frac12\left(K^2-K_{ab}K^{ab}-R^{(5)}\right)
}.
\]

Das Vorzeichen wird unabhängig durch den sechs-dimensionalen Kontrollraum

\[
ds^2=dr^2+e^{2cr}\eta_{ab}dy^ady^b
\]

mit fünf tangentialen Richtungen fixiert. Direkte Berechnung der Verbindung und Ricci-Tensoren ergibt

\[
R_{rr}=-5c^2,\qquad R=-30c^2,
\]

also

\[
G_{rr}=10c^2.
\]

Gleichzeitig gilt `K_ab=c h_ab`, also

\[
\frac12(K^2-K_{ab}K^{ab})
=\frac12(25-5)c^2
=10c^2.
\]

Damit ist das Vorzeichen in der UniverseLab-Konvention kontrolliert.

Da die induzierte Metrik auf beiden Seiten identisch ist, ist auch `R^(5)` identisch. Die geometrische `Lambda6` ist im M1-Modell dieselbe Größe auf beiden Seiten. Aus

\[
M_6^4(G_{AB}+\Lambda_6g_{AB})=T_{AB}
\]
folgt daher

\[
[G_{NN}]_c=\kappa_6^2[T_{NN}]_c.
\]

Mit der quadratischen Jump-Identität erhält man

\[
\boxed{
S^{ab}\langle K_{ab}\rangle_c
=[T_{NN}]_c
=T_{NN,S}-T_{NN,N}
}.
\]

Das ist die projekt-spezifische passive Shape-Constraint-Relation in der deklarierten gemeinsamen Normalorientierung.

## 5. Warum Israel allein nicht genügt

Die Israelgleichung bestimmt den Jump der Extrinsikkrümmung. Die passive Gleichung enthält zusätzlich den **Average** der Extrinsikkrümmung sowie den Jump der regionalen Normalspannung.

Man kann daher Israel exakt erfüllen und gleichzeitig einen regionalen `NN`-Einstein-Constraint verletzen. Dann ist

\[
S^{ab}\langle K_{ab}\rangle_c-[T_{NN}]_c\neq0.
\]

Somit

\[
\boxed{
\text{Israel}=0\ \not\Rightarrow\ R_\perp=0
}.
\]

Erst

\[
\text{Israel}=0
\quad\land\quad
E_{NN,N}=E_{NN,S}=0
\]

erzwingt diesen komponentenweisen passiven Kanal.

## 6. C-PHYS-M1-Spezialisierung

Für den statischen `4+1`-Kappenansatz definieren wir die common-normal Mittelwerte

\[
\bar A_n=\frac12(A_{N,x}-A_{S,x}),
\]

\[
\bar L_n
=\frac12\left(\frac{\ell_{N,x}}{\ell_\Sigma}
-\frac{\ell_{S,x}}{\ell_\Sigma}\right).
\]

Die dimensionslosen Oberflächenstresskomponenten sind

\[
\frac{S_\mu{}^\nu}{M_6^5}
=\left(-\hat\lambda-\frac12\hat Y_\sigma\right)\delta_\mu{}^\nu,
\]

\[
\frac{S_\chi{}^\chi}{M_6^5}
=-\hat\lambda+\frac12\hat Y_\sigma.
\]

Daher

\[
\frac{S^{ab}\langle K_{ab}\rangle_c}{M_6^6}
=
4\left(-\hat\lambda-\frac12\hat Y_\sigma\right)\bar A_n
+\left(-\hat\lambda+\frac12\hat Y_\sigma\right)\bar L_n.
\]

Aus dem eingefrorenen M1-`rr_constraint` liest man die dimensionslose Normalspannung

\[
\hat t_{NN,s}
=\frac12\varphi_{s,x}^2
-\frac12\hat m_\phi^2\varphi_\Sigma^2
+\rho_{F,s}.
\]

Die passive Relation lautet deshalb

\[
\boxed{
4\left(-\hat\lambda-\frac12\hat Y_\sigma\right)\bar A_n
+\left(-\hat\lambda+\frac12\hat Y_\sigma\right)\bar L_n
=\hat t_{NN,S}-\hat t_{NN,N}
}.
\]

### Direkte Algebra gegen den `rr_constraint`

Schreibe die regionalen outward slopes als

\[
a_N=A_{N,x},\quad a_S=A_{S,x},\qquad
l_N=\ell_{N,x}/\ell_\Sigma,\quad l_S=\ell_{S,x}/\ell_\Sigma.
\]

Die metrischen Junctions liefern

\[
3(a_N+a_S)+(l_N+l_S)=\hat\lambda+\frac12\hat Y_\sigma,
\]

\[
4(a_N+a_S)=\hat\lambda-\frac12\hat Y_\sigma.
\]

Der Jump des geometrischen `rr`-Terms ist

\[
[6a^2+4al]_{S-N}
=6(a_S^2-a_N^2)+4(a_Sl_S-a_Nl_N).
\]

Mit

\[
\bar A_n=(a_N-a_S)/2,
\qquad
\bar L_n=(l_N-l_S)/2
\]

folgt direkt

\[
[6a^2+4al]_{S-N}
=4\left(-\hat\lambda-\frac12\hat Y_\sigma\right)\bar A_n
+\left(-\hat\lambda+\frac12\hat Y_\sigma\right)\bar L_n.
\]

Da die gemeinsamen Terme `k4`, `Lambda_hat` und das kontinuierliche skalare Potential im Constraint beim Jump wegfallen, ist dies exakt derselbe Jump wie `t_NN,S-t_NN,N`.

## 7. Zusätzliche konditionale Reduktion

Wenn zusätzlich die bereits eingefrorene M1-Skalarjunction

\[
\varphi_{N,x}+\varphi_{S,x}=0
\]

gilt, dann sind die Quadrate der radialen Skalarableitungen gleich. Wegen der skalaren Kontinuität fällt auch der Potentialterm aus dem Jump heraus. Dann reduziert sich der Bulk-Kraftjump auf

\[
\boxed{
\hat t_{NN,S}-\hat t_{NN,N}
=\rho_{F,S}-\rho_{F,N}
}.
\]

Das ist **konditional** und darf nicht ohne die Skalarjunction verwendet werden.

## 8. Z2-Grenzfall

Für spiegelbildliche Seiten sind die outward radial slopes gleich. Wegen `N=n_N=-n_S` sind die common-normal Extrinsikkrümmungen entgegengesetzt und damit

\[
\langle K_{ab}\rangle_c=0.
\]

Sind zugleich die regionalen Normalspannungen gleich, gilt

\[
[T_{NN}]_c=0.
\]

Die passive Gleichung ist dann identisch erfüllt. Das erklärt, warum sie unter einer von Hand auferlegten Reflexionssymmetrie keinen zusätzlichen Informationskanal liefert.

## 9. Was damit bewiesen ist

**[BEWIESEN]** In den eingefrorenen UniverseLab-Outward-/Common-Normal-Konventionen gilt

\[
S^{ab}\langle K_{ab}\rangle_c=[T_{NN}]_c
\]

als Folge der zwei regionalen Normal-Einstein-Constraints und der metrischen Israel-Junction.

**[BEWIESEN]** Israel allein reicht nicht.

**[BEWIESEN]** Die statische dimensionslose M1-Form besitzt exakt dasselbe Vorzeichen und dieselbe Algebra wie der eingefrorene `rr_constraint`.

**[KONDITIONAL]** Mit zusätzlicher M1-Skalarjunction reduziert sich der Kraftjump auf den Fluxenergie-Jump.

## 10. Was weiterhin offen bleibt

Nicht geschlossen sind:

- die direkte Variation der gesamten bewegten Wirkung nach der Einbettung ohne Benutzung der `NN`-Constraints;
- der vollständige off-shell Ward-Ausdruck mit expliziten Scalar-/Gauge-/Phase-Residualkoeffizienten;
- die zweite bewegte GHY-/Kappenvariation;
- die vollständige Boundary-Hesse;
- eine configuration-space connection;
- ein released perturbed BVP operator;
- der physische Background;
- Ghostfreiheit, kinetische Positivität, Gradientenstabilität oder Spektrum;
- die 6D→4D-Observable-Map.

## 11. Unveränderte Gates

```text
WP1 full shape residual       NOT_ASSEMBLED_FROM_DIRECT_MOVING_ACTION
WP1 full boundary Hessian     NOT_CLOSED
WP1 full quadratic action     NOT_CLOSED
PERTURBED_JUNCTION_SYSTEM     NOT_RELEASED
PHYSICAL_BACKGROUND           NOT_ESTABLISHED
FM-G0                         OPEN
AuthorizationDecision         NOT_CREATED
SingleUseGrant                NOT_CREATED
BACKEND_IMPORT                NOT_EXECUTED
SOLVER_EXECUTION              NOT_EXECUTED
PHYSICAL_RESPONSE_RANK        NOT_EXECUTED
K1-D                          NOT_RELEASED
K1-E                          NOT_ADMISSIBLE
physical_gate_effect          NONE
physical_evidence_effect      NONE
```

Der nächste zulässige Block ist `ULSH-05/WP1C4B1D`: direkte Assembly der ersten bewegten Shape-Variation und Äquivalenzprüfung gegen die hier hergeleitete Constraint-Relation.
