# ULSH-05 / WP1C2 — Cap Fixed-Interface Hessian v0.1

**Datum:** 2026-09-07  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `d78cafe423cc86dc9eec80a4c0e2c952177942f4`  
**Status:** `DERIVED_FIXED_INTERFACE_CAP_LOCALIZED_HESSIAN_AND_STRESS_RESPONSE_BENDING_AND_FULL_JUNCTION_NOT_CLOSED`  
**Physikalische Evidenzwirkung:** `NONE`

## 1. Ziel

WP1C2 behandelt ausschließlich die lokalisierte Kappenwirkung

\[
S_\Sigma=\int_{\Sigma_5}d^5x\sqrt{-h}\,\mathcal L_\Sigma,
\]

\[
\mathcal L_\Sigma
=-\lambda(\phi)-\frac12Z_\sigma(\phi)h^{ab}D_a\sigma D_b\sigma,
\]

im **Fixed-Interface-Kontrollrahmen**.

Für C-PHYS-M1 sind

\[
\lambda=\hat\lambda M_6^5,
\qquad
Z_\sigma=\hat z_\sigma M_6^3
\]

konstant in \(\phi\). Daher gilt

\[
\lambda_{,\phi}=\lambda_{,\phi\phi}=0,
\qquad
Z_{\sigma,\phi}=Z_{\sigma,\phi\phi}=0.
\]

Die nichttriviale Kappenstruktur steckt in

\[
B_a\equiv D_a\sigma=\partial_a\sigma-q_\Sigma A_a.
\]

WP1C2 leitet den exakten quadratischen Cap-Hessian, die lineare Antwort des Kappenstresstensors und die lineare Kappenstromantwort her. Eine bewegte Kappe wird **nicht** behandelt.

---

## 2. Fixed-Interface-Pfad

Wir setzen

\[
h_{ab}(\epsilon)=\bar h_{ab}+\epsilon q_{ab},
\]

\[
\sigma(\epsilon)=\bar\sigma+\epsilon s,
\qquad
A_a(\epsilon)=\bar A_a+\epsilon a_a.
\]

Damit

\[
B_a(\epsilon)=\bar B_a+\epsilon b_a,
\]

mit

\[
\boxed{
b_a=\partial_a s-q_\Sigma a_a.
}
\]

Definiere

\[
q\equiv\bar h^{ab}q_{ab},
\qquad
q_2\equiv q_{ab}q^{ab},
\]

\[
r_\Sigma^{ab}=q^a{}_cq^{cb}.
\]

Die inverse induzierte Metrik lautet

\[
h^{ab}
=\bar h^{ab}-\epsilon q^{ab}
+\epsilon^2r_\Sigma^{ab}+O(\epsilon^3).
\]

---

## 3. Kappenmaß

\[
\boxed{
\sqrt{-h}
=\sqrt{-\bar h}
\left[1+\epsilon n_1+\epsilon^2n_2+O(\epsilon^3)\right]
}
\]

mit

\[
\boxed{n_1=\frac q2,}
\]

\[
\boxed{
n_2=\frac{q^2}{8}-\frac{q_{ab}q^{ab}}4.
}
\]

---

## 4. Norm des kovarianten Phasengradienten

Setze

\[
Y\equiv h^{ab}B_aB_b
=Y_0+\epsilon Y_1+\epsilon^2Y_2+O(\epsilon^3).
\]

Dann

\[
\boxed{Y_0=\bar B_a\bar B^a,}
\]

\[
\boxed{
Y_1=2\bar B^ab_a-q^{ab}\bar B_a\bar B_b,
}
\]

\[
\boxed{
Y_2=b_ab^a-2q^{ab}\bar B_ab_b+r_\Sigma^{ab}\bar B_a\bar B_b.
}
\]

Alle Indizes werden in dieser Expansion mit \(\bar h_{ab}\) gehoben und gesenkt.

---

## 5. Exakter Cap-Hessian

Da \(\lambda\) und \(Z_\sigma\) im M1-Zweig konstant sind,

\[
\mathcal L_\Sigma
=L_0+\epsilon L_1+\epsilon^2L_2+O(\epsilon^3)
\]

mit

\[
L_0=-\lambda-\frac12Z_\sigma Y_0,
\]

\[
L_1=-\frac12Z_\sigma Y_1,
\]

\[
L_2=-\frac12Z_\sigma Y_2.
\]

Nach Multiplikation mit dem Kappenmaß ist der exakte \(\epsilon^2\)-Koeffizient

\[
\boxed{
\mathcal C_2=L_2+n_1L_1+n_2L_0.
}
\]

Also

\[
\boxed{
\begin{aligned}
\mathcal C_2={}&
-\frac12Z_\sigma Y_2
-\frac q4Z_\sigma Y_1\\
&+\left(\frac{q^2}{8}-\frac{q_{ab}q^{ab}}4\right)
\left(-\lambda-\frac12Z_\sigma Y_0\right).
\end{aligned}
}
\]

Damit

\[
\boxed{
S_{\Sigma,\mathrm{quad}}^{(2)}
=\int_{\Sigma_5}d^5x\sqrt{-\bar h}\,\mathcal C_2.
}
\]

`[BEWIESEN]` Diese Gleichung ist die exakte algebraische zweite Variation der lokalisierten C-PHYS-M1-Kappenwirkung für eine feste Einbettung.

---

## 6. Linearer Kappenstresstensor

Der kanonische Parent-Stresstensor ist

\[
S_{ab}
=-\left(\lambda+\frac12Z_\sigma Y\right)h_{ab}
+Z_\sigma B_aB_b.
\]

Mit

\[
S_{ab}(\epsilon)=\bar S_{ab}+\epsilon\,\delta S_{ab}+O(\epsilon^2)
\]

folgt direkt

\[
\boxed{
\begin{aligned}
\delta S_{ab}={}&
-\left(\lambda+\frac12Z_\sigma Y_0\right)q_{ab}
-\frac12Z_\sigma Y_1\bar h_{ab}\\
&+Z_\sigma(\bar B_ab_b+b_a\bar B_b).
\end{aligned}
}
\]

`[BEWIESEN]` Dies ist die exakte erste Variation von Parent-EQ-006 im Fixed-Interface-M1-Zweig.

### 6.1 Späterer Israel-Residual

WP1B liefert bereits \(\delta\Pi_{ab}^{(s)}\) im lokalen Fixed-Interface-GN-Kontrollrahmen. Damit ist der **Residualkernel**

\[
\boxed{
\delta\mathcal J_{ab}
=M_6^4\sum_{s=\pm}\delta\Pi_{ab}^{(s)}-\delta S_{ab}
}
\]

formal definiert.

`[WICHTIG]` Die Gleichung

\[
\delta\mathcal J_{ab}=0
\]

darf erst als echte linearisierte Junctiongleichung interpretiert werden, wenn der Hintergrund selbst die unperturbierte Israel-Bedingung erfüllt. Da

```text
PHYSICAL_BACKGROUND = NOT_ESTABLISHED
```

gilt, bleibt dies derzeit ein Residualkernel und keine freigegebene physikalische Randgleichung.

---

## 7. Kappenstrom

Der Parentstrom ist

\[
J_\Sigma^a=q_\Sigma Z_\sigma D^a\sigma
=q_\Sigma Z_\sigma h^{ab}B_b.
\]

Daraus folgt

\[
\boxed{
\delta J_\Sigma^a
=q_\Sigma Z_\sigma
\left(b^a-q^{ab}\bar B_b\right).
}
\]

`[BEWIESEN]` Dies ist die exakte Fixed-Interface-Variation der rechten Seite des Gauge-Matchings EQ-009.

Die linke Bulk-Flussseite von EQ-009 wird erst in der vollständigen perturbierten Junction-Assembly zusammengesetzt.

---

## 8. Kappenphasengleichung in Dichteform

Für konstantes \(Z_\sigma\) lautet EQ-010

\[
D_a(Z_\sigma B^a)=0.
\]

In Dichteform

\[
\partial_a\left(\sqrt{-h}Z_\sigma h^{ab}B_b\right)=0.
\]

Definiere

\[
\mathscr K_\sigma^a
=\sqrt{-h}Z_\sigma h^{ab}B_b.
\]

Dann

\[
\bar{\mathscr K}_\sigma^a
=\sqrt{-\bar h}Z_\sigma\bar B^a
\]

und

\[
\boxed{
\delta\mathscr K_\sigma^a
=\sqrt{-\bar h}Z_\sigma
\left[
 b^a-q^{ab}\bar B_b+\frac q2\bar B^a
\right].
}
\]

Diese Größe definiert den linearen **Residualkernel** auch off-shell. Nur wenn die Hintergrundphasengleichung erfüllt ist, folgt für eine echte lineare Perturbationslösung

\[
\partial_a\delta\mathscr K_\sigma^a=0.
\]

---

## 9. U(1)-Gaugeinvarianz

Die Kappenwirkung besitzt die Stückelberg-Transformation

\[
A_a\rightarrow A_a+\partial_a\alpha,
\qquad
\sigma\rightarrow\sigma+q_\Sigma\alpha.
\]

Auf Perturbationsebene

\[
a_a\rightarrow a_a+\partial_a\alpha,
\qquad
s\rightarrow s+q_\Sigma\alpha.
\]

Damit

\[
\boxed{
b_a\rightarrow b_a.}
\]

Folglich sind

\[
\mathcal C_2,
\qquad
\delta S_{ab},
\qquad
\delta J_\Sigma^a,
\qquad
\delta\mathscr K_\sigma^a
\]

unter dieser lokalen U(1)-Transformation invariant.

`[BEWIESEN]` Lokale U(1)-Gaugeinvarianz des Fixed-Interface-Cap-Kontrollsektors.

Dies ist **keine** Diffeomorphismus- oder Cap-Bending-Gaugekontrolle.

---

## 10. Harte Spezialfälle

### 10.1 Feste induzierte Metrik

Für

\[
q_{ab}=0
\]

ist

\[
Y_1=2\bar B\cdot b,
\qquad
Y_2=b^2,
\]

und

\[
\boxed{\mathcal C_2=-\frac12Z_\sigma b^2.}
\]

Der Hintergrund-Winding-Term erzeugt bei fester Metrik keine zusätzliche quadratische Masse für \(s\); er koppelt über den gauge-invarianten Gradienten \(b_a\).

### 10.2 Keine Phasen-/Gaugeperturbation

Für

\[
b_a=0
\]

bleibt ausschließlich die zweite induzierte-Metrikantwort aus Kappenspannung und Hintergrund-Windingenergie.

### 10.3 Kein Hintergrund-Winding

Für

\[
\bar B_a=0
\]

verschwinden alle Hintergrund-Winding-Mischungen. Bei zusätzlich \(q_{ab}=0\) bleibt wieder nur

\[
-\frac12Z_\sigma b^2.
\]

### 10.4 Isotroper ausgeschalteter Phasensektor

Der Parentkanon erlaubt einen minimalen isotropen Fall mit ausgeschaltetem Phasensektor. Wenn ein solcher Zweig explizit gewählt ist, darf WP1C2 **nicht** dazu benutzt werden, einen propagierenden Kappenmodus zu behaupten.

---

## 11. Unabhängige QA

Der Regressionstest führt vier voneinander getrennte Kontrollen aus:

1. **Direkte Dichte-Rekonstruktion:**
   
   \[
   \sqrt{-\det h(\epsilon)}
   \left[-\lambda-\frac12Z_\sigma h^{ab}(\epsilon)B_a(\epsilon)B_b(\epsilon)\right]
   \]
   
   wird für Lorentz-signierte \(5\times5\)-Kontrollmatrizen direkt bei \(\pm\epsilon\) ausgewertet. Der zentrale \(\epsilon^2\)-Koeffizient muss \(\sqrt{-\bar h}\mathcal C_2\) reproduzieren.

2. **Stresstensor:** Parent-EQ-006 wird direkt finite-differenziert und komponentenweise mit \(\delta S_{ab}\) verglichen.

3. **Kappenstrom:** \(J_\Sigma^a=q_\Sigma Z_\sigma h^{ab}B_b\) wird direkt finite-differenziert und mit \(\delta J_\Sigma^a\) verglichen.

4. **Gaugekontrolle:** Simultane Shifts
   
   \[
   a_a\to a_a+\xi_a,
   \qquad
   \partial_as\to\partial_as+q_\Sigma\xi_a
   \]
   
   müssen \(b_a\), \(\mathcal C_2\), \(\delta S_{ab}\) und \(\delta J_\Sigma^a\) unverändert lassen.

---

## 12. Stand des Parent-Hessians

Nach WP1A, WP1B, WP1C1 und WP1C2 sind folgende Teile kontrolliert:

```text
WP1A  fixed-metric bulk scalar-Maxwell Hessian      DERIVED_CONTROL_SUBSECTOR
WP1B  EH+GHY variational Hessian master              DERIVED_CONTROL_TEMPLATE
WP1C1 full bulk metric-scalar-Maxwell density        DERIVED
WP1C2 localized cap fixed-interface Hessian          DERIVED_CONTROL_SUBSECTOR
```

Damit ist

```text
bulk + fixed-interface cap parent Hessian
= ASSEMBLABLE_CONTROL_LEVEL_NOT_BENDING_COMPLETE_NOT_GAUGE_REDUCED
```

Noch **nicht** geschlossen:

```text
moving-cap / bending sector                          NOT_DERIVED
complete perturbed two-sided junction system          NOT_DERIVED
diffeomorphism / SVT gauge reduction                 NOT_DERIVED
constraint elimination                               NOT_DERIVED
PHYSICAL_BACKGROUND                                   NOT_ESTABLISHED
matter Delta_m observable coupling                    MISSING_REQUIRED_LINK
6D -> 4D perturbative reduction                       MISSING_REQUIRED_LINK
mu / eta / Sigma / growth / lensing                   UNRELEASED
ghost freedom / stability                             OPEN
```

Daher bleibt

```text
ULSH05-WP1 = PREPARATORY_IN_PROGRESS_NOT_CLOSED
G01        = OPEN_BLOCKING
```

---

## 13. Nächster Block

Der nächste mathematisch notwendige Block ist

```text
ULSH05-WP1C3 — Cap bending/embedding + complete perturbed junction assembly
```

Erst danach ist die Randseite des vollständigen Parent-Hessians strukturell geschlossen. Die anschließende S/V/T-/Gauge-/Constraint-Reduktion bleibt ein eigener nachgelagerter Schritt.
