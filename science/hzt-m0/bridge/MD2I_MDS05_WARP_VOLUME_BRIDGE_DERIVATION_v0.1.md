# MD-2I / MDS-05 v0.1 — Warpvolumen und 6D→4D-Gravitationsnormierung

**Projekt:** UniverseLab / HPVS → HZT-M0-S6  
**Parentquelle:** SCI-001/SCI-002 v0.1  
**Datum:** 2026-08-01  
**Status:** `DERIVED_CONDITIONAL_NUMERICAL_VALUE_OPEN`  
**K1-D:** `NOT_RELEASED`  
**K1-E:** `NOT_ADMISSIBLE`  
**Evidenzwirkung:** `NONE`

## 0. Kernergebnis

Für den kanonischen Einstein-Hilbert-Sektor

\[
S_{\rm EH}^{(6)}
=
\frac{M_6^4}{2}
\int d^6X\,\sqrt{-g_6}\,R_6,
\qquad
M_6^4=\kappa_6^{-2},
\]

und den statischen S6-Q1-Ansatz

\[
ds_6^2
=
e^{2A(y)}g_{\mu\nu}^{(4)}(x)\,dx^\mu dx^\nu
+
g_{mn}^{(2)}(y)\,dy^m dy^n
\]

ist der vom Bulk geerbte vierdimensionale Einstein-Hilbert-Koeffizient

\[
\boxed{
M_{4,\rm bulk}^2
=
\frac{1}{\kappa_6^2}
\int d^2y\,\sqrt{g_2}\,e^{2A(y)}
}
\]

oder mit dem Warpvolumen

\[
\boxed{
V_W
\equiv
\int d^2y\,\sqrt{g_2}\,e^{2A(y)}
}
\]

als

\[
\boxed{
M_{4,\rm bulk}^2
=
\frac{V_W}{\kappa_6^2}
=
M_6^4V_W.
}
\]

Ohne lokalisierte Einstein-Hilbert-Terme folgt

\[
\boxed{
\kappa_4^2
=
\frac{\kappa_6^2}{V_W},
\qquad
G_4
=
\frac{\kappa_6^2}{8\pi V_W}.
}
\]

Diese Relation ist aus der kanonischen Parentwirkung hergeleitet. Ein numerischer Wert für \(M_4\), \(\kappa_4\) oder \(G_4\) ist jedoch noch nicht freigegeben, weil der vollständige MD-2S-Profil-, Winkel-, Einheiten- und Framevertrag fehlt.

---

## 1. Gültigkeitsbereich

Die Herleitung gilt für:

```text
HZT-M0-S6
signature (-,+,+,+,+,+)
one physical time
canonical bulk Einstein-Hilbert term
two-dimensional positive-definite internal metric
static internal profiles for the background reduction
```

Nicht automatisch eingeschlossen sind:

- HZT-M0-P5 oder HZT-Full;
- Gauss-Bonnet- oder allgemein höhere Krümmungsterme;
- nichtminimale Kopplungen wie \(F(\phi)R_6\);
- induzierte 5D- oder 4D-Einstein-Hilbert-Terme;
- eine nichtlokale Bulkantwort;
- die vollständige Tensor-Störungsanalyse;
- eine empirische Bestimmung von \(G_4\).

Jede dieser Erweiterungen benötigt eine eigene Reduktion.

---

## 2. Kanonische Quellen und Konventionen

Die SCI-001/SCI-002-v0.1-Parentwirkung enthält:

\[
\frac{M_6^4}{2}(R_6-2\Lambda_6)
-\frac12(\partial\phi)^2
-U(\phi)
-\frac14Z_F(\phi)F^2
\]

sowie GHY- und Kappen-/Spannungssektoren. Der aktuelle Parentkern enthält **keinen** lokalisierten Einstein-Hilbert-Term.

Die Konventionen sind:

\[
M_6^4=\frac{1}{\kappa_6^2},
\qquad
\kappa_6^2=8\pi G_6,
\]

\[
[\kappa_6^2]=L^4=M^{-4},
\qquad
[V_W]=L^2=M^{-2},
\]

\[
[M_4^2]=L^{-2}=M^2,
\qquad
[\kappa_4^2]=L^2=M^{-2}.
\]

Damit ist

\[
\left[\frac{V_W}{\kappa_6^2}\right]
=
L^{-2}
=
[M_4^2].
\]

---

## 3. Reduktion des Einstein-Hilbert-Terms

Für

\[
ds_6^2=e^{2A(y)}g_{\mu\nu}^{(4)}dx^\mu dx^\nu+g_{mn}^{(2)}dy^m dy^n
\]

gilt

\[
\sqrt{-g_6}
=
e^{4A}\sqrt{-g_4}\sqrt{g_2}.
\]

Der sechsdimensionale Ricci-Skalar enthält den vierdimensionalen Anteil

\[
R_6
=
e^{-2A}R_4
+
R_{\rm intern/warp},
\]

wobei \(R_{\rm intern/warp}\) ausschließlich interne Krümmung und Ableitungen von \(A\) enthält.

Daher:

\[
\begin{aligned}
S_{\rm EH}^{(6)}
&\supset
\frac{M_6^4}{2}
\int d^4x\,d^2y\,
e^{4A}\sqrt{-g_4}\sqrt{g_2}\,
e^{-2A}R_4
\\
&=
\frac12
\left[
M_6^4
\int d^2y\,\sqrt{g_2}e^{2A}
\right]
\int d^4x\sqrt{-g_4}\,R_4.
\end{aligned}
\]

Verglichen mit

\[
S_{\rm EH}^{(4)}
=
\frac{M_4^2}{2}
\int d^4x\sqrt{-g_4}\,R_4
\]

folgt das Kernergebnis.

**Status:** `DERIVED` aus dem minimalen Parent-Einstein-Hilbert-Sektor.

---

## 4. Axialsymmetrischer MD-2S-Ausdruck

Für

\[
ds_6^2
=
e^{2A(r)}\bar g_{\mu\nu}dx^\mu dx^\nu
+
dr^2
+
L^2(r)d\chi^2
\]

ist

\[
\sqrt{g_2}=L(r).
\]

Bei einer dimensionslosen Winkelkoordinate mit Periode

\[
\chi\sim\chi+\Delta\chi
\]

folgt:

\[
\boxed{
V_W
=
\Delta\chi
\int_{\mathcal I_r}dr\,
L(r)e^{2A(r)}.
}
\]

Für mehrere Regionen, beispielsweise Bulk und Cap:

\[
\boxed{
V_W
=
\Delta\chi
\sum_s
\int_{\mathcal I_s}dr_s\,
L_s(r_s)e^{2A_s(r_s)}.
}
\]

Die Regionen dürfen nicht doppelt gezählt werden. Ihre Koordinatenorientierung beeinflusst Junction-Gleichungen, aber das Volumenintegral muss mit positivem geometrischem Maß ausgewertet werden.

### Flacher Referenzfall

Für

\[
A=0,\qquad L(r)=r,\qquad 0\le r\le R,\qquad\Delta\chi=2\pi
\]

ergibt sich:

\[
V_W
=
2\pi\int_0^Rr\,dr
=
\pi R^2.
\]

Dies ist der obligatorische geometrische Regressionstest.

---

## 5. Welche Parentsektoren direkt beitragen

### 5.1 Direkter Beitrag

Im kanonischen v0.1-Kern trägt direkt nur der Bulk-Einstein-Hilbert-Term zum Koeffizienten von \(R_4\) bei.

### 5.2 Nur indirekter Beitrag über die Hintergrundlösung

Diese Sektoren beeinflussen \(M_4^2\) nur dadurch, dass sie \(A(r)\), \(L(r)\), die Caplage oder den zulässigen Lösungszweig verändern:

- \(\Lambda_6\);
- Skalarfeld und Potential;
- Maxwell-/Fluxsektor;
- Kappenspannung;
- Kappenphase;
- Junction- und Fluxquantisierungsbedingungen.

### 5.3 Kein eigener \(R_4\)-Koeffizient im minimalen Kern

- Gibbons-Hawking-York-Terme;
- reine Spannungs- oder Materieterme ohne Krümmungskopplung.

Sie sind für eine korrekte Variation unverzichtbar, liefern aber im eingefrorenen Kern keinen zusätzlichen vierdimensionalen Einstein-Hilbert-Koeffizienten.

---

## 6. Optionale lokalisierte Einstein-Hilbert-Terme

Diese Terme sind **nicht** Teil der SCI-001/SCI-002-v0.1-Kernwirkung. Die folgenden Formeln definieren lediglich den Erweiterungsvertrag, falls sie später ausdrücklich eingeführt werden.

### 6.1 Fünfdimensionaler Cap-Term

Für

\[
S_{\Sigma,\rm EH}^{(5)}
=
\frac{M_{5,\Sigma}^3}{2}
\int_{\Sigma_5}d^5x\sqrt{-h}\,R_5
\]

und

\[
ds_{\Sigma_5}^2
=
e^{2A_\Sigma}g_{\mu\nu}^{(4)}dx^\mu dx^\nu
+
L_\Sigma^2d\chi^2
\]

folgt:

\[
\boxed{
\Delta M_{4,\Sigma}^2
=
\Delta\chi\,
M_{5,\Sigma}^3
L_\Sigma e^{2A_\Sigma}.
}
\]

### 6.2 Vierdimensionaler lokalisierter Term

Für

\[
S_{i,\rm EH}^{(4)}
=
\frac{M_{4,i,\rm loc}^2}{2}
\int d^4x\sqrt{-\gamma_i}\,R[\gamma_i],
\qquad
\gamma_{i,\mu\nu}=e^{2A_i}g_{\mu\nu}^{(4)}
\]

folgt im verwendeten \(g_{\mu\nu}^{(4)}\)-Frame:

\[
\boxed{
\Delta M_{4,i}^2
=
M_{4,i,\rm loc}^2e^{2A_i}.
}
\]

### 6.3 Gesamtkoeffizient

\[
\boxed{
M_{4,\rm eff}^2
=
\frac{V_W}{\kappa_6^2}
+
\sum_\Sigma
\Delta\chi_\Sigma M_{5,\Sigma}^3L_\Sigma e^{2A_\Sigma}
+
\sum_i
M_{4,i,\rm loc}^2e^{2A_i}.
}
\]

Im aktuellen Parentkern sind beide Summen exakt null, solange keine neue Wirkungsversion sie einführt.

---

## 7. Frame- und Warp-Normalisierung

Die Zerlegung besitzt eine konstante Redundanz:

\[
A(y)\rightarrow A(y)+c,
\qquad
g_{\mu\nu}^{(4)}
\rightarrow e^{-2c}g_{\mu\nu}^{(4)}.
\]

Die sechsdimensionale Metrik bleibt dabei unverändert, der numerische Koeffizient von \(R_4[g^{(4)}]\) hängt jedoch vom gewählten 4D-Frame ab.

Vor einer numerischen MDS-05-Freigabe muss deshalb eine Bedingung eingefroren werden, zum Beispiel:

\[
A(r_{\rm obs})=0,
\]

oder eine äquivalente Festlegung, dass \(g_{\mu\nu}^{(4)}\) der auf der beobachtbaren Brane induzierte Jordan-/Einstein-Frame ist.

Ohne diese Festlegung ist ein berichtetes \(M_4\) nicht eindeutig interpretierbar.

---

## 8. Historischer MD-2S-Wert \(V_W=0.5318111250097\)

Der derzeitige MD-2S-Preflight führt den Wert unter `known_dimensionless_benchmarks`, nennt den Schlüssel aber lediglich `V_W`.

Geometrisch besitzt das rohe Warpvolumen die Dimension \(L^2\). Eine dimensionslose Größe wäre bei \(\mathcal K_4>0\):

\[
\widehat V_W
=
\mathcal K_4V_W.
\]

Zusätzlich ist nicht dokumentiert, ob der Winkelintegralfaktor \(\Delta\chi=2\pi\) bereits enthalten ist.

Daher bleiben mindestens zwei nicht äquivalente Interpretationen offen:

### Interpretation A — vollständiges dimensionsloses Warpvolumen

\[
0.5318111250097
=
\mathcal K_4V_W.
\]

Für \(\mathcal K_4=1\):

\[
V_W=0.5318111250097.
\]

### Interpretation B — dimensionsloses radiales Integral pro Winkelradian

\[
0.5318111250097
=
\mathcal K_4
\int dr\,L e^{2A}.
\]

Für \(\mathcal K_4=1\) und \(\Delta\chi=2\pi\):

\[
V_W
=
2\pi(0.5318111250097)
=
3.341467846855593.
\]

Der Faktorunterschied ist \(2\pi\). Keine der beiden Interpretationen darf ohne Originaldefinition gewählt werden.

**Status des historischen Zahlenwertes:** `AMBIGUOUS_NORMALIZATION / NOT_USABLE_FOR_KAPPA4_RELEASE`.

---

## 9. Positivität und Tensorsektor

Für einen regulären positiven internen Maßfaktor gilt im minimalen Bulk:

\[
V_W>0.
\]

Mit \(\kappa_6^2>0\) folgt:

\[
M_{4,\rm bulk}^2>0.
\]

Dies ist eine notwendige Positivitätsbedingung für den vierdimensionalen Einstein-Hilbert-Koeffizienten.

Sie beweist jedoch nicht:

- die vollständige Ghostfreiheit des Tensorsektors;
- die Positivität der reduzierten skalaren kinetischen Matrix;
- das Fehlen leichter oder tachyonischer KK-Moden;
- die Existenz und Normalisierbarkeit eines isolierten masselosen Tensor-Nullmodus;
- die GR-Niedrigenergiegrenze.

Diese Aussagen erfordern die quadratische, constraint-bereinigte Störungswirkung.

---

## 10. MDS-05-Eingabe-/Ausgabevertrag

### Pflichtinputs

```text
kappa6_squared
A(r) in jeder internen Region
L(r) in jeder internen Region
region domains and non-overlap rule
chi_period
four-dimensional frame normalization
units or explicit dimensionless rescaling
optional localized EH coefficients, default exactly zero
profile and equation hashes
quadrature and convergence settings
```

### Pflichtoutputs

```text
V_W per region
V_W total
K4 * V_W when K4 > 0
bulk M4_squared
localized M4_squared contributions
total M4_squared
kappa4_squared
G4
normalization interpretation
positivity status
quadrature convergence record
provenance hashes
```

### Fail-closed-Regeln

Die Berechnung muss abbrechen bei:

- nichtmonotonem radialem Gitter;
- nichtendlichen Profilwerten;
- negativem \(L\);
- nichtpositiver Winkelperiode;
- \(\kappa_6^2\le0\);
- nichtpositivem Gesamtkoeffizienten \(M_{4,\rm eff}^2\);
- unbekannter Einheiten- oder Winkelkonvention bei einer Freigabeberechnung;
- nicht eingefrorenem 4D-Frame.

---

## 11. Freigabegates

MDS-05 kann erst auf `RELEASED` gesetzt werden, wenn:

1. der MD-2S-Hintergrund reproduzierbar vorliegt;
2. \(A(r)\) und \(L(r)\) für alle Regionen exportiert sind;
3. \(\Delta\chi\) und Defizitwinkelkonvention dokumentiert sind;
4. die Definition des historischen \(V_W\) geklärt oder neu berechnet ist;
5. der 4D-Frame fixiert ist;
6. lokalisierte Krümmungsterme ausdrücklich ausgeschlossen oder vollständig spezifiziert sind;
7. das Volumenintegral unter Gitterverfeinerung konvergiert;
8. \(M_{4,\rm eff}^2>0\) gilt;
9. die Tensor-Nullmodennorm aus der quadratischen Wirkung mit demselben Koeffizienten übereinstimmt;
10. die schwere-Moden-/GR-Grenze separat geprüft ist.

Bis dahin:

```text
MDS-05 formal relation = DERIVED
MDS-05 numerical value = OPEN
physical identification = NOT_RELEASED
K1-D = NOT_RELEASED
K1-E = NOT_ADMISSIBLE
```

---

## 12. Reproduzierbare Referenzimplementierung

Die Referenzdatei

```text
tools/hzt_m0_warp_volume_bridge_v0_1.py
```

implementiert:

- axialsymmetrisches Warpvolumen;
- Summation nicht überlappender Regionen;
- optionale 5D-Cap- und 4D-Branen-EH-Beiträge;
- \(M_4^2\), \(\kappa_4^2\) und \(G_4\);
- dimensionsloses \(\mathcal K_4V_W\);
- beide offenen Interpretationen des historischen Benchmarks;
- explizite Fehlermodi.

Die Tests prüfen:

- die flache Scheibe \(V_W=\pi R^2\);
- einen konstant gewarpten Zylinder;
- Additivität mehrerer Regionen;
- \(V_W\rightarrow s^2V_W\) bei Längenskalierung;
- lokalisierte Beiträge;
- Planck- und Newton-Normierung;
- Benchmark-Mehrdeutigkeit;
- fail-closed-Eingaben.

---

## 13. Nächster physikalischer Anschluss

Die MDS-05-Formel verbindet den MD-2S-Hintergrund mit der 4D-Gravitationsnormierung, löst aber noch nicht die gesamte Forward Map.

Der nächste zulässige Anschluss ist:

```text
reproducible MD-2S profiles
→ unambiguous V_W
→ M4 normalization
→ tensor zero-mode and KK normalization
→ controlled 4D EFT
→ observable response
```

Ein guter Wert von \(V_W\) oder \(M_4\) allein ist keine Bestätigung der 6D-Theorie.
