# ULSH-05 / WP1C1 — Bulk Metric–Scalar–Maxwell Mixed Hessian v0.1

**Datum:** 2026-09-07  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `2af889e354beaa73e7d5e3c832235328a216a8e5`  
**Status:** `DERIVED_OFFSHELL_BULK_METRIC_SCALAR_MAXWELL_SECOND_ORDER_DENSITY_BOUNDARY_AND_GAUGE_REDUCTION_NOT_CLOSED`  
**Physikalische Evidenzwirkung:** `NONE`

## 1. Ziel

WP1A hat den Skalar-Maxwell-Hessian für feste Metrik hergeleitet. WP1B hat den EH+GHY-Gravitations-Hessian als off-shell Masteridentität eingefroren. Die noch fehlende Bulk-Verbindung ist die gleichzeitige Variation

\[
\{g_{AB},\phi,A_A\}
\rightarrow
\{p_{AB},\varphi,a_A\}
\]

im Materiesektor.

WP1C1 leitet deshalb den exakten \(\epsilon^2\)-Koeffizienten der Bulk-Dichte

\[
\sqrt{-g}\,\mathcal L_{\phi F}
\]

mit

\[
\mathcal L_{\phi F}
=-\frac12g^{AB}\partial_A\phi\partial_B\phi
-U(\phi)
-\frac14Z_F(\phi)F_{AB}F^{AB}
\]

unter simultanen Metrik-, Skalar- und Gaugeperturbationen her.

Der Block ist **off-shell** und enthält keine Kappe, keine Junctionvariation und keine 4D-Observable-Interpretation.

---

## 2. Gemeinsamer Pfad

Wir verwenden denselben kovarianten Metrikpfad wie WP1B:

\[
g_{AB}(\epsilon)=\bar g_{AB}+\epsilon p_{AB},
\]

sowie

\[
\phi(\epsilon)=\bar\phi+\epsilon\varphi,
\qquad
A_A(\epsilon)=\bar A_A+\epsilon a_A,
\]

\[
F_{AB}(\epsilon)=\bar F_{AB}+\epsilon f_{AB},
\qquad
f_{AB}=2\bar\nabla_{[A}a_{B]}.
\]

Definiere

\[
p\equiv \bar g^{AB}p_{AB},
\qquad
p_2\equiv p_{AB}p^{AB},
\]

und

\[
r^{AB}\equiv p^A{}_Cp^{CB}.
\]

Dann

\[
g^{AB}
=\bar g^{AB}-\epsilon p^{AB}+\epsilon^2r^{AB}+O(\epsilon^3).
\]

---

## 3. Volumenelement

Aus der determinantischen Matrixexpansion folgt

\[
\boxed{
\sqrt{-g}
=\sqrt{-\bar g}\left[
1+\epsilon m_1+\epsilon^2m_2+O(\epsilon^3)
\right],
}
\]

mit

\[
\boxed{m_1=\frac p2,}
\]

\[
\boxed{
m_2=\frac{p^2}{8}-\frac{p_{AB}p^{AB}}4.
}
\]

Diese Identität wurde bereits in WP1 eingefroren; WP1C1 verwendet sie nun für den Materie-Hessian.

---

## 4. Skalargradient

Setze

\[
u_A\equiv\partial_A\bar\phi,
\qquad
v_A\equiv\partial_A\varphi.
\]

Definiere

\[
X\equiv g^{AB}\partial_A\phi\partial_B\phi
=X_0+\epsilon X_1+\epsilon^2X_2+O(\epsilon^3).
\]

Direkte Multiplikation liefert

\[
\boxed{X_0=u_Au^A,}
\]

\[
\boxed{
X_1=2u^Av_A-p^{AB}u_Au_B,
}
\]

\[
\boxed{
X_2=v_Av^A-2p^{AB}u_Av_B+r^{AB}u_Au_B.
}
\]

Damit sind alle metrisch-skalaren Gradientmischungen bereits vollständig erfasst.

---

## 5. Maxwell-Kontraktion

Definiere

\[
W\equiv F_{AB}F^{AB}
=W_0+\epsilon W_1+\epsilon^2W_2+O(\epsilon^3).
\]

Alle folgenden Indizes werden ausschließlich mit \(\bar g_{AB}\) gehoben.

### 5.1 Hintergrund

\[
\boxed{W_0=\bar F_{AB}\bar F^{AB}.}
\]

### 5.2 Erste Ordnung

\[
\boxed{
W_1
=2\bar F^{AB}f_{AB}
-2p^{AC}\bar F_A{}^B\bar F_{CB}.
}
\]

Der erste Term ist die Feldperturbation, der zweite die Variation der beiden inversen Metriken in \(F^2\).

### 5.3 Zweite Ordnung

\[
\boxed{
\begin{aligned}
W_2={}&f_{AB}f^{AB}
-4p^{AC}\bar F_A{}^B f_{CB}\\
&+2r^{AC}\bar F_A{}^B\bar F_{CB}
+p^{AC}p^{BD}\bar F_{AB}\bar F_{CD}.
\end{aligned}
}
\]

Diese Gleichung enthält gleichzeitig:

- den reinen Gauge-Hessian \(f^2\),
- die lineare Metrik-Gauge-Mischung \(p\bar Ff\),
- die beiden unabhängigen quadratischen Metrikantworten des Hintergrundflusses.

---

## 6. Funktionen \(U\) und \(Z_F\)

Generisch:

\[
U(\phi)=\bar U
+\epsilon\bar U_{,\phi}\varphi
+\frac{\epsilon^2}{2}\bar U_{,\phi\phi}\varphi^2
+O(\epsilon^3),
\]

\[
Z_F(\phi)=\bar Z
+\epsilon\bar Z_{,\phi}\varphi
+\frac{\epsilon^2}{2}\bar Z_{,\phi\phi}\varphi^2
+O(\epsilon^3).
\]

Für C-PHYS-M1:

\[
\bar U=\frac12\hat m_\phi^2M_6^2\bar\phi^2,
\]

\[
\bar U_{,\phi}=\hat m_\phi^2M_6^2\bar\phi,
\qquad
\bar U_{,\phi\phi}=\hat m_\phi^2M_6^2,
\]

\[
\bar Z=e^{-2a_F\bar\phi/M_6^2},
\]

\[
\bar Z_{,\phi}=-\frac{2a_F}{M_6^2}\bar Z,
\qquad
\bar Z_{,\phi\phi}=\frac{4a_F^2}{M_6^4}\bar Z.
\]

---

## 7. Ungewichtete Lagrange-Koeffizienten

Schreibe

\[
\mathcal L_{\phi F}
=\ell_0+\epsilon\ell_1+\epsilon^2\ell_2+O(\epsilon^3).
\]

Dann ist

\[
\boxed{
\ell_0=-\frac12X_0-\bar U-\frac14\bar ZW_0,
}
\]

\[
\boxed{
\ell_1
=-\frac12X_1
-\bar U_{,\phi}\varphi
-\frac14\left(
\bar ZW_1+\bar Z_{,\phi}\varphi W_0
\right),
}
\]

\[
\boxed{
\begin{aligned}
\ell_2={}&-\frac12X_2
-\frac12\bar U_{,\phi\phi}\varphi^2\\
&-\frac14\left[
\bar ZW_2
+\bar Z_{,\phi}\varphi W_1
+\frac12\bar Z_{,\phi\phi}\varphi^2W_0
\right].
\end{aligned}
}
\]

---

## 8. Exakter Bulk-Materie-Hessian

Multipliziere

\[
(1+\epsilon m_1+\epsilon^2m_2)
(\ell_0+\epsilon\ell_1+\epsilon^2\ell_2).
\]

Der \(\epsilon^2\)-Koeffizient ist exakt

\[
\boxed{
\mathcal D_2
=\ell_2+m_1\ell_1+m_2\ell_0.
}
\]

Damit

\[
\boxed{
S_{\phi F,\mathrm{quad}}^{(2)}
=\int d^6X\sqrt{-\bar g}\,\mathcal D_2.
}
\]

`[BEWIESEN]` Dies ist die vollständige algebraische zweite Variation des Bulk-Skalar-Maxwell-Sektors entlang des deklarierten simultanen linearen Feldpfads.

Es wurde **keine** Hintergrundgleichung eingesetzt.

---

## 9. Expliziter Skalarteil

Der Skalarbeitrag kann ausgeschrieben werden als

\[
\boxed{
\begin{aligned}
\mathcal D_{2,\phi}={}&
-\frac12X_2
-\frac12\bar U_{,\phi\phi}\varphi^2\\
&+\frac p2\left[
-\frac12X_1-\bar U_{,\phi}\varphi
\right]\\
&+\left(\frac{p^2}{8}-\frac{p_{AB}p^{AB}}4\right)
\left[-\frac12X_0-\bar U\right].
\end{aligned}
}
\]

Der unmittelbar sichtbare metrisch-skalare Mischkern ist

\[
\boxed{
p^{AB}u_Av_B
-\frac p2u^Av_A
-\frac p2\bar U_{,\phi}\varphi.
}
\]

Zusätzlich enthält \(\mathcal D_{2,\phi}\) die reinen quadratischen Metrikantworten der Hintergrund-Skalarenergie.

---

## 10. Expliziter Maxwellteil

\[
\boxed{
\begin{aligned}
\mathcal D_{2,F}
=-\frac14\Bigg\{&
\bar ZW_2
+\bar Z_{,\phi}\varphi W_1
+\frac12\bar Z_{,\phi\phi}\varphi^2W_0\\
&+\frac p2\left[
\bar ZW_1+\bar Z_{,\phi}\varphi W_0
\right]\\
&+\left(\frac{p^2}{8}-\frac{p_{AB}p^{AB}}4\right)
\bar ZW_0
\Bigg\}.
\end{aligned}
}
\]

Damit sind in einer einzigen kontrollierten Formel enthalten:

- \(p\bar Ff\): metric–gauge mixing,
- \(p\varphi\bar F^2\): metric–scalar–flux mixing,
- \(\varphi\bar Ff\): scalar–gauge mixing,
- quadratische Metrikantwort des Hintergrundflusses,
- der bereits in WP1A bekannte feste-Metrik Skalar-Maxwell-Hessian.

---

## 11. Harte Konsistenzgrenzen

### 11.1 WP1A-Grenze

Setze

\[
p_{AB}=0.
\]

Dann

\[
m_1=m_2=0,
\]

\[
X_1=2u\cdot v,
\qquad
X_2=v^2,
\]

\[
W_1=2\bar F\cdot f,
\qquad
W_2=f^2.
\]

Damit reduziert sich \(\mathcal D_2\) exakt auf

\[
-\frac12v^2
-\frac12\bar U_{,\phi\phi}\varphi^2
-\frac14\bar Zf^2
-\frac12\bar Z_{,\phi}\varphi\bar F\cdot f
-\frac18\bar Z_{,\phi\phi}\bar F^2\varphi^2,
\]

also genau auf WP1A.

`[BEWIESEN]` WP1C1 enthält WP1A als exakten Spezialfall.

### 11.2 Keine Feldperturbationen

Für

\[
\varphi=0,\qquad f_{AB}=0
\]

bleibt ausschließlich die zweite Metrikvariation der vorhandenen Skalar-/Fluss-Hintergrundenergie.

### 11.3 Kein Hintergrundfluss

Für

\[
\bar F_{AB}=0
\]

verschwinden alle Hintergrundfluss-Mischungen; der gewöhnliche Gauge-Hessian

\[
-\frac14\bar Zf^2
\]

bleibt bestehen.

### 11.4 Konstanter Hintergrundskalar

Für

\[
\partial_A\bar\phi=0
\]

verschwinden die Gradientmischungen, aber Potential-Maßterme und die durch \(Z_F(\phi)\) vermittelten Flussmischungen bleiben erhalten.

---

## 12. Unabhängiger numerischer Rekonstruktionstest

Der Repository-Test evaluiert die **ursprüngliche**, nicht expandierte lokale Dichte

\[
\mathscr D(\epsilon)
=\sqrt{-\det g(\epsilon)}
\left[
-\frac12g^{AB}(\epsilon)u_A(\epsilon)u_B(\epsilon)
-U(\phi(\epsilon))
-\frac14Z_F(\phi(\epsilon))F^2(\epsilon)
\right]
\]

für deterministische Lorentz-signierte \(6\times6\)-Kontrollmatrizen.

Aus

\[
\mathscr D_2^{\rm FD}
=\frac{\mathscr D(+\epsilon)+\mathscr D(-\epsilon)-2\mathscr D(0)}{2\epsilon^2}
\]

wird der direkte \(\epsilon^2\)-Koeffizient rekonstruiert und mit

\[
\sqrt{-\det\bar g}\,\mathcal D_2
\]

verglichen.

Mindestens ein Testfall besitzt

\[
\bar F^2<0,
\]

um jede versteckte euklidische beziehungsweise Positivitätsannahme auszuschließen.

Zusätzlich wird \(W(\epsilon)\) separat finite-differenziert, sodass \(W_1\) und \(W_2\) unabhängig vom restlichen Lagrangetest geprüft werden.

---

## 13. Verhältnis zu WP1B

WP1B liefert den Gravitationsblock

\[
S_{g,\mathrm{quad}}^{(2)}.
\]

WP1C1 liefert nun den vollständigen Bulk-Materieblock

\[
S_{\phi F,\mathrm{quad}}^{(2)}.
\]

Daher ist der **Bulk-Innenraum-Hessian** formal zusammensetzbar als

\[
\boxed{
S_{\rm bulk,quad}^{(2)}
=S_{g,\rm bulk,quad}^{(2)}
+S_{\phi F,\rm quad}^{(2)}.
}
\]

Diese Summe ist jedoch noch **nicht gauge-reduziert**, nicht on-shell und enthält noch nicht den lokalisierten Cap-Hessian oder die vollständige perturbierte Junctionstruktur.

Insbesondere werden die off-shell \(\bar{\mathcal E}_{AB}\)-Terme aus WP1B nicht vorzeitig gestrichen. Erst der vollständig zusammengesetzte Parent-Hessian und später separat freigegebene on-shell-Bedingungen erlauben entsprechende Vereinfachungen.

---

## 14. Was WP1C1 schließt

Neu:

```text
bulk metric-scalar mixing                         DERIVED
bulk metric-Maxwell mixing                        DERIVED
bulk metric-scalar-flux mixing                    DERIVED
full scalar-Maxwell-metric quadratic density      DERIVED
WP1A fixed-metric limit                           EXACTLY_RECOVERED
bulk gravity+matter Hessian                        ASSEMBLABLE_NOT_GAUGE_REDUCED
```

Weiter offen:

```text
cap localized-action Hessian                      NOT_DERIVED
cap bending / global fixed-interface gauge        MISSING_REQUIRED_LINK
perturbed junction assembly                       NOT_DERIVED
SVT / diffeomorphism gauge control                NOT_DERIVED
constraint elimination                            NOT_DERIVED
PHYSICAL_BACKGROUND                               NOT_ESTABLISHED
matter Delta_m observable coupling                MISSING_REQUIRED_LINK
6D -> 4D perturbative reduction                   MISSING_REQUIRED_LINK
mu / eta / Sigma / growth / lensing               UNRELEASED
ghost freedom / stability                         OPEN
```

Somit bleibt

```text
ULSH05-WP1 = PREPARATORY_IN_PROGRESS_NOT_CLOSED
G01        = OPEN_BLOCKING
```

und die physischen Gates bleiben unverändert.

---

## 15. Nächster analytischer Block

Der nächste Block wird bewusst wieder getrennt:

```text
ULSH05-WP1C2 — Cap localized-action Hessian in fixed-interface control
```

Erst danach folgt ein eigenständiges Upgrade für Cap-Bending/Embedding und die vollständige perturbierte Junction-Assembly.
