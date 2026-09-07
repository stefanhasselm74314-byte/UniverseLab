# ULSH-05 / WP1A — Fixed-Metric Scalar-Maxwell Hessian v0.1

**Datum:** 2026-09-07  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `15ad300a24f6bd54d1a5b82c83e692730f5e753d`  
**Status:** `DERIVED_CONTROL_SUBSECTOR_OFFSHELL_FIXED_METRIC_BULK_INTERIOR`  
**Physikalische Evidenzwirkung:** `NONE`

## 1. Zweck

WP1A isoliert den ersten wirklich vollständig kontrollierbaren Teil der ULSH-05-Zweitvariation:

- feste beliebige 6D-Hintergrundmetrik \(\bar g_{AB}\), also \(h_{AB}=0\),
- nur Bulk-Skalar \(\phi\) und U(1)-Gaugefeld \(A_A\),
- perturbative Felder mit kompaktem Träger im glatten Bulk-Innenraum,
- keine Kappe, keine GHY-Zweitvariation, keine Junctionbedingungen,
- keine on-shell-Annahme,
- keine 6D→4D-Observable-Interpretation.

Damit ist WP1A ein **analytischer Hessian-Kontrollsektor**, nicht der vollständige HZT-Perturbationssektor.

---

## 2. Ausgangswirkung

Auf festem \(\bar g_{AB}\) ist der relevante Parent-Teil

\[
S_{\phi F}
=\int d^6X\sqrt{-\bar g}\left[
-\frac12\bar g^{AB}\partial_A\phi\partial_B\phi
-U(\phi)
-\frac14 Z_F(\phi)F_{AB}F^{AB}
\right].
\]

Wir setzen

\[
\phi=\bar\phi+\epsilon\varphi,
\qquad
A_A=\bar A_A+\epsilon a_A,
\]

und wegen der abelschen Feldstärke

\[
F_{AB}=\bar F_{AB}+\epsilon f_{AB},
\qquad
f_{AB}=2\bar\nabla_{[A}a_{B]}.
\]

Die Metrik wird in WP1A **nicht** perturbiert.

---

## 3. Exakte Expansion bis \(O(\epsilon^2)\)

### 3.1 Skalargradient

\[
(\partial\phi)^2
=(\partial\bar\phi)^2
+2\epsilon\,\bar\nabla_A\bar\phi\,\bar\nabla^A\varphi
+\epsilon^2(\bar\nabla\varphi)^2.
\]

### 3.2 Potential

\[
U(\bar\phi+\epsilon\varphi)
=\bar U
+\epsilon\bar U_{,\phi}\varphi
+\frac{\epsilon^2}{2}\bar U_{,\phi\phi}\varphi^2
+O(\epsilon^3).
\]

### 3.3 Gaugekinetik

\[
Z_F(\bar\phi+\epsilon\varphi)
=\bar Z
+\epsilon\bar Z_{,\phi}\varphi
+\frac{\epsilon^2}{2}\bar Z_{,\phi\phi}\varphi^2
+O(\epsilon^3),
\]

wobei \(\bar Z\equiv Z_F(\bar\phi)\).

### 3.4 Feldstärkequadrat

\[
F_{AB}F^{AB}
=\bar F^2
+2\epsilon\bar F^{AB}f_{AB}
+\epsilon^2 f_{AB}f^{AB}.
\]

---

## 4. Generischer quadratischer Koeffizient

Mit der bereits eingefrorenen Konvention

\[
S=S^{(0)}+\epsilon\,\delta S+\epsilon^2S_{\rm quad}^{(2)}+O(\epsilon^3)
\]

folgt direkt

\[
\boxed{
\begin{aligned}
\mathcal L_{\rm quad}^{(2)}={}&
-\frac12(\bar\nabla\varphi)^2
-\frac12\bar U_{,\phi\phi}\varphi^2
-\frac14\bar Z\,f_{AB}f^{AB}\\
&-\frac12\bar Z_{,\phi}\,\varphi\,\bar F^{AB}f_{AB}
-\frac18\bar Z_{,\phi\phi}\,\bar F^2\varphi^2.
\end{aligned}
}
\]

`[BEWIESEN]` Diese Gleichung ist die exakte \(\epsilon^2\)-Koeffizientenextraktion des eingefrorenen Parent-Skalar-Maxwell-Sektors bei fester Metrik.

Sie benötigt **keine** Hintergrundgleichung und ist deshalb off-shell gültig.

---

## 5. Spezialisierung auf C-PHYS-M1

Für

\[
U(\phi)=\frac12\hat m_\phi^2M_6^2\phi^2,
\]

\[
Z_F(\phi)=\exp\left(-2a_F\frac{\phi}{M_6^2}\right)
\]

gilt

\[
\bar U_{,\phi\phi}=\hat m_\phi^2M_6^2,
\]

\[
\bar Z_{,\phi}=-\frac{2a_F}{M_6^2}\bar Z,
\qquad
\bar Z_{,\phi\phi}=\frac{4a_F^2}{M_6^4}\bar Z.
\]

Einsetzen ergibt

\[
\boxed{
\begin{aligned}
\mathcal L_{\rm quad,M1}^{(2)}={}&
-\frac12(\bar\nabla\varphi)^2
-\frac12\left[
\hat m_\phi^2M_6^2
+\frac{a_F^2}{M_6^4}\bar Z\bar F^2
\right]\varphi^2\\
&-\frac14\bar Z f_{AB}f^{AB}
+\frac{a_F}{M_6^2}\bar Z\,\varphi\,\bar F^{AB}f_{AB}.
\end{aligned}
}
\]

Definiere zur Buchhaltung

\[
\mathcal M_{\varphi\varphi}(X)
=\hat m_\phi^2M_6^2
+\frac{a_F^2}{M_6^4}\bar Z\bar F^2,
\]

\[
\mathcal C_{\varphi f}(X)
=\frac{a_F}{M_6^2}\bar Z.
\]

Dann

\[
\mathcal L_{\rm quad,M1}^{(2)}
=-\frac12(\bar\nabla\varphi)^2
-\frac12\mathcal M_{\varphi\varphi}\varphi^2
-\frac14\bar Z f^2
+\mathcal C_{\varphi f}\varphi\bar F^{AB}f_{AB}.
\]

### Wichtige Positivitäts-Firewall

`[OFFEN]` \(\mathcal M_{\varphi\varphi}\) ist hier nur ein lokaler Hessian-Koeffizient. Er darf **nicht** ohne on-shell Hintergrund und vollständigen kinetischen/gravitationalen Sektor als beobachtete Masse oder als Stabilitätsbeweis interpretiert werden.

Insbesondere ist in Lorentz-Signatur das Vorzeichen von \(\bar F^2\) hintergrundabhängig.

---

## 6. Hessian-Euler-Lagrange-Operator

Für kompakt getragene Bulkperturbationen verschwinden die Randterme beim partiellen Integrieren.

### 6.1 Skalar

Variation nach \(\varphi\) liefert

\[
\boxed{
\bar\Box\varphi
-\left[
\hat m_\phi^2M_6^2
+\frac{a_F^2}{M_6^4}\bar Z\bar F^2
\right]\varphi
+\frac{a_F}{M_6^2}\bar Z\bar F^{AB}f_{AB}
=0.
}
\]

### 6.2 Maxwell

Variation nach \(a_B\) liefert

\[
\boxed{
\bar\nabla_A\left[
\bar Z f^{AB}
-\frac{2a_F}{M_6^2}\bar Z\varphi\bar F^{AB}
\right]=0.
}
\]

---

## 7. Direkter Linearisationstest

Die Parent-Gleichungen bei fester Metrik lauten

\[
\Box\phi-U_{,\phi}-\frac14 Z_{F,\phi}F^2=0,
\]

\[
\nabla_A(Z_FF^{AB})=0.
\]

Direkte erste Linearisation ergibt generisch

\[
\bar\Box\varphi
-\bar U_{,\phi\phi}\varphi
-\frac14\bar Z_{,\phi\phi}\bar F^2\varphi
-\frac12\bar Z_{,\phi}\bar F^{AB}f_{AB}=0,
\]

\[
\bar\nabla_A\left(
\bar Z f^{AB}
+\bar Z_{,\phi}\varphi\bar F^{AB}
\right)=0.
\]

Mit der M1-Spezialisierung werden diese Gleichungen **identisch** mit Abschnitt 6.

`[BEWIESEN]` Der aus dem Hessian abgeleitete Kontrolloperator stimmt damit mit der direkten festen-Metrik-Linearisation der Parent-Gleichungen überein.

---

## 8. U(1)-Gaugeinvarianz

Unter

\[
a_A\rightarrow a_A+\bar\nabla_A\alpha
\]

ist

\[
f_{AB}=2\bar\nabla_{[A}a_{B]}
\]

invariant, weil für einen Skalar \(\alpha\)

\[
\bar\nabla_{[A}\bar\nabla_{B]}\alpha=0.
\]

Da \(\mathcal L_{\rm quad}^{(2)}\) nur über \(f_{AB}\) von \(a_A\) abhängt, gilt

\[
\boxed{\delta_\alpha S_{\rm quad,WP1A}^{(2)}=0.}
\]

`[BEWIESEN]` Lokale U(1)-Gaugeinvarianz des WP1A-Kontrollsektors.

Dies ist **keine** Aussage über Diffeomorphismus-Gaugekontrolle, weil \(h_{AB}=0\) in WP1A bewusst abgeschaltet ist.

---

## 9. Was dieser Block schließt

WP1A schließt genau **einen** vorher offenen Teil:

```text
bulk_scalar_Maxwell_fixed_metric_control = DERIVED
```

Nicht geschlossen werden:

```text
full_S_quad_2                                  NOT_DERIVED
Einstein_Hilbert_Hessian                       NOT_DERIVED
GHY_second_variation                           NOT_DERIVED
metric-scalar / metric-Maxwell mixing          NOT_DERIVED
cap_Hessian                                    NOT_DERIVED
cap_bending_or_fixed_interface_gauge            MISSING_REQUIRED_LINK
perturbed_junction_conditions                  NOT_DERIVED
SVT_and_diffeomorphism_gauge_control            NOT_DERIVED
constraint_elimination                         NOT_DERIVED
PHYSICAL_BACKGROUND                            NOT_ESTABLISHED
matter_Delta_m_coupling                        MISSING_REQUIRED_LINK
6D_to_4D_perturbative_reduction                MISSING_REQUIRED_LINK
mu_eta_Sigma_growth_lensing                    UNRELEASED
```

---

## 10. Wissenschaftlicher Status

- `[BEWIESEN]` exakte feste-Metrik-\(\epsilon^2\)-Expansion des Skalar-Maxwell-Bulksektors;
- `[BEWIESEN]` exakte M1-Spezialisierung;
- `[BEWIESEN]` Übereinstimmung Hessian-Euler-Lagrange ↔ direkte Parent-Linearisation;
- `[BEWIESEN]` lokale U(1)-Gaugeinvarianz;
- `[OFFEN]` Gravitations-/Diffeomorphismus-Sektor;
- `[OFFEN]` Cap-/Boundary-Hessian;
- `[OFFEN]` on-shell Hintergrund;
- `[OFFEN]` Observable-Map;
- `[OFFEN]` Ghost-/Stabilitätsanalyse.

Physikalische Gates bleiben unverändert:

```text
FM-G0                  OPEN
PHYSICAL_BACKGROUND    NOT_ESTABLISHED
PHYSICAL_RESPONSE_RANK NOT_EXECUTED
K1-D                    NOT_RELEASED
K1-E                    NOT_ADMISSIBLE
physical_gate_effect    NONE
physical_evidence_effect NONE
```

---

## 11. Nächster Block

Der nächste strukturell notwendige Schritt ist

```text
ULSH05-WP1B — Einstein-Hilbert + GHY Hessian with boundary bookkeeping
```

Erst danach darf der metrisch gekoppelte Voll-Hessian mit WP1A zusammengesetzt werden.
