# ULSH-05 / WP1C2 — Fixed-Interface Localized Cap Hessian v0.1

**Datum:** 2026-09-07  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `d78cafe423cc86dc9eec80a4c0e2c952177942f4`  
**Status:** `DERIVED_OFFSHELL_FIXED_INTERFACE_LOCALIZED_CAP_HESSIAN_BENDING_AND_PERTURBED_JUNCTIONS_OPEN`  
**Physikalische Evidenzwirkung:** `NONE`

## 1. Zweck

WP1A schließt den festen-Metrik Skalar-Maxwell-Hessian, WP1B den EH+GHY-Gravitationsmaster und WP1C1 die simultane Bulk-Metrik–Skalar–Maxwell-Mischung. Der kleinste verbleibende lokale Randblock ist deshalb die zweite Variation der **lokalisierten Kappenwirkung bei festgehaltener Interface-Einbettung**.

Diese Arbeit setzt **nicht** voraus, dass Kappenbiegung physikalisch verschwindet. Die feste Einbettung ist lediglich ein wohldefinierter analytischer Teilpfad.

## 2. Eingefrorene M1-Kappenwirkung

Für C-PHYS-M1 gilt

\[
S_\Sigma=-\int_{\Sigma_5}d^5x\sqrt{-h}\left[\lambda+\frac12 Z_\sigma X_\sigma\right],
\]

mit

\[
X_\sigma=h^{ab}D_a\sigma D_b\sigma,
\qquad
D_a\sigma=\partial_a\sigma-q_\sigma A_a.
\]

Im M1-Funktionsfreeze sind

\[
\lambda=\hat\lambda M_6^5,
\qquad
Z_\sigma=\hat z_\sigma M_6^3
\]

konstant in \(\phi\). Daher entstehen in diesem **lokalisierten** Hessian keine expliziten \(\varphi\)-Terme aus \(\lambda_{,\phi}\) oder \(Z_{\sigma,\phi}\).

## 3. Deklarierter Perturbationspfad

Wir setzen

\[
h_{ab}(\epsilon)=\bar h_{ab}+\epsilon q_{ab},
\]

\[
\sigma(\epsilon)=\bar\sigma+\epsilon s,
\qquad
A_a(\epsilon)=\bar A_a+\epsilon a_a.
\]

Die Einbettung \(X^A(y)\) des Interfaces wird in WP1C2 nicht variiert.

Definiere

\[
q\equiv\bar h^{ab}q_{ab},
\qquad
q_2\equiv q_{ab}q^{ab},
\qquad
r^{ab}\equiv q^a{}_cq^{cb},
\]

sowie

\[
w_a\equiv \bar D_a\bar\sigma
=\partial_a\bar\sigma-q_\sigma\bar A_a,
\]

\[
d_a\equiv\partial_a s-q_\sigma a_a.
\]

## 4. Determinante und inverse induzierte Metrik

Analog zum Bulk-Metrikpfad:

\[
h^{ab}=\bar h^{ab}-\epsilon q^{ab}+\epsilon^2r^{ab}+O(\epsilon^3),
\]

\[
\sqrt{-h}=\sqrt{-\bar h}\left(1+\epsilon n_1+\epsilon^2n_2+O(\epsilon^3)\right),
\]

mit

\[
\boxed{n_1=\frac q2},
\qquad
\boxed{n_2=\frac{q^2}{8}-\frac{q_{ab}q^{ab}}4}.
\]

## 5. Exakte Expansion von \(X_\sigma\)

Schreibe

\[
X_\sigma=X_0+\epsilon X_1+\epsilon^2X_2+O(\epsilon^3).
\]

Dann folgt durch direkte Multiplikation

\[
\boxed{X_0=w_aw^a},
\]

\[
\boxed{X_1=2w^ad_a-q^{ab}w_aw_b},
\]

\[
\boxed{X_2=d_ad^a-2q^{ab}w_ad_b+r^{ab}w_aw_b}.
\]

Damit sind Phase–Gauge-, Metrik–Phase/Gauge- und rein metrische Antworten der vorhandenen Wicklungsenergie vollständig enthalten.

## 6. Lokalisierter Lagrange-Hessian

Setze

\[
\mathcal L_\Sigma
=-\lambda-\frac12Z_\sigma X_\sigma
=\ell_0+\epsilon\ell_1+\epsilon^2\ell_2+O(\epsilon^3).
\]

Dann

\[
\ell_0=-\lambda-\frac12Z_\sigma X_0,
\]

\[
\ell_1=-\frac12Z_\sigma X_1,
\]

\[
\ell_2=-\frac12Z_\sigma X_2.
\]

Die vollständige Dichte lautet

\[
\sqrt{-h}\,\mathcal L_\Sigma
=\sqrt{-\bar h}
\left[D_0+\epsilon D_1+\epsilon^2D_2+O(\epsilon^3)\right].
\]

Der exakte quadratische Koeffizient ist

\[
\boxed{
D_{2,\Sigma}
=\ell_2+n_1\ell_1+n_2\ell_0.
}
\]

also explizit

\[
\boxed{
D_{2,\Sigma}
=-\frac12Z_\sigma X_2
-\frac q4 Z_\sigma X_1
+\left(\frac{q^2}{8}-\frac{q_{ab}q^{ab}}4\right)
\left(-\lambda-\frac12Z_\sigma X_0\right).
}
\]

Damit

\[
\boxed{
S^{(2)}_{\Sigma,\mathrm{fixed}}
=\int_{\Sigma_5}d^5x\sqrt{-\bar h}\,D_{2,\Sigma}.
}
\]

`[BEWIESEN]` Dies ist der exakte \(\epsilon^2\)-Koeffizient der eingefrorenen M1-Kappenwirkung entlang des deklarierten linearen Feldpfads bei fester Interface-Einbettung.

## 7. U(1)-Gaugekontrolle

Unter der linearen Transformation

\[
a_a\rightarrow a_a+\partial_a\alpha,
\qquad
s\rightarrow s+q_\sigma\alpha
\]

gilt

\[
d_a\rightarrow d_a.
\]

Da \(D_{2,\Sigma}\) nur über \(d_a\), \(w_a\) und metrische Größen von \(s,a_a\) abhängt, ist

\[
\boxed{\delta_\alpha D_{2,\Sigma}=0}.
\]

`[BEWIESEN]` Der WP1C2-Hessian besitzt die korrekte linearisierte U(1)-Gaugeinvarianz.

## 8. Harte Grenzfälle

### 8.1 Keine Metrikperturbation

Für \(q_{ab}=0\):

\[
\boxed{D_{2,\Sigma}=-\frac12Z_\sigma d_ad^a}.
\]

### 8.2 Kein Hintergrundwinding

Für \(w_a=0\) bleiben keine Hintergrund-Winding-Mischungen; der Phase–Gauge-Hessian \(-Z_\sigma d^2/2\) bleibt bestehen.

### 8.3 Keine Phase-/Gaugeperturbation

Für \(d_a=0\) verbleibt die reine Metrikantwort der vorhandenen Kappenspannung und Hintergrund-Wicklungsenergie.

## 9. Warum WP1 damit noch nicht geschlossen ist

Die feste Einbettung eliminiert **nicht** physikalisch den Biegungsmodus. Bei einer verschobenen Kappe

\[
X^A(y)\rightarrow \bar X^A(y)+\epsilon\xi^\perp n^A+\cdots
\]

ändern sich zusätzlich

- die Pullbacks der Bulkfelder,
- die induzierte Metrik,
- die Einheitsnormale,
- die Extrinsikkrümmung,
- die GHY-/Junction-Beiträge,
- die Lage, an der Hintergrundgradienten ausgewertet werden.

Diese Terme gehören in WP1C3.

## 10. Status

Neu geschlossen:

- fixed-interface lokalisierter M1-Kappen-Hessian;
- exakte Phase–Gauge–Metrik-Mischungen der Kappenwirkung;
- U(1)-Gaugeinvarianz dieses Teilblocks;
- exakte Grenzfälle.

Weiter offen:

- cap bending / perturbed embedding;
- \(\delta n^A\), \(\delta K_{ab}\) und bewegte-Grenze-Terme;
- vollständige pertubierte Israel-/Skalar-/Gauge-Junctions;
- Diffeomorphismus-Gaugekontrolle;
- S/V/T-Zerlegung und Constraint-Elimination;
- physischer Hintergrund und 6D→4D-Reduktion;
- \(\mu,\eta,\Sigma\), Growth/Lensing;
- Ghostfreiheit und Stabilität.

Daher unverändert:

```text
PHYSICAL_BACKGROUND = NOT_ESTABLISHED
FM-G0 = OPEN
AuthorizationDecision = NOT_CREATED
SingleUseGrant = NOT_CREATED
BACKEND_IMPORT = NOT_EXECUTED
SOLVER_EXECUTION = NOT_EXECUTED
PHYSICAL_RESPONSE_RANK = NOT_EXECUTED
K1-D = NOT_RELEASED
K1-E = NOT_ADMISSIBLE
physical_gate_effect = NONE
physical_evidence_effect = NONE
```

## 11. Nächster Block

`ULSH-05/WP1C3 — Cap bending and perturbed junction geometry preflight`

Zuerst müssen Einbettungsperturbation, \(\delta h_{ab}\), \(\delta n^A\), \(\delta K_{ab}\) und die bewegten Pullbacks sauber hergeleitet werden. Erst danach darf das vollständige Rand-Hessian/Junction-System assembliert werden.
