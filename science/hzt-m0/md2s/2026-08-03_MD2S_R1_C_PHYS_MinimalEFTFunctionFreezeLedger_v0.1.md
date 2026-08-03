# MD2S-R1-C-PHYS — Minimal EFT Function Freeze Ledger v0.1

**Datum:** 2026-08-03  
**Track:** `MD2S-R1-C-PHYS`  
**Phase:** `R1.0`  
**Block:** `C-PHYS-R1.0-FREEZE-1B`  
**Modellfamilie:** `C-PHYS-ME1`  
**Klassifikation:** `VERSIONED_MODEL_SELECTION_NOT_DERIVATION`  
**Status:** `MINIMAL_EFT_FUNCTION_FAMILY_SELECTED_BENCHMARK_INSTANCE_OPEN`  
**Evidenzwirkung:** `MODEL_DEFINITION_ONLY`  
**Physikalische Evidenzwirkung:** `NONE`

---

## 1. Auftrag und harte Firewall

Dieser Block wählt eine **neue, explizite minimale EFT-Modellfamilie** für den aktuellen physikalischen Wiederaufbau `MD2S-R1-C-PHYS`.

Er behauptet ausdrücklich nicht, dass diese Funktionen

- aus C1-V abgeleitet wurden,
- historische A0-Funktionen rekonstruieren,
- durch Beobachtungsdaten bevorzugt sind,
- bereits eine physikalische Hintergrundlösung besitzen,
- oder einen freigegebenen Solver definieren.

Die Auswahl folgt ausschließlich:

1. minimaler funktionaler Komplexität,
2. globaler Regularität auf einer deklarierten Skalardomäne,
3. Positivität der kinetischen Vorfaktoren,
4. Entfernung exakter Parametrisierungsredundanzen,
5. einem expliziten Identifizierbarkeitsbudget,
6. vollständiger Kompatibilität mit Freeze-1A.

---

## 2. Bereits eingefrorene Struktur aus Freeze-1A

Vor Freeze-1B gelten unverändert:

```text
Delta_chi = 2*pi
n_N^r = n_S^r = +1
(global) epsilon_N = +1
epsilon_S = -1
A_chi_N(0) = A_chi_S(0) = 0
A_N(0) = 0
q_sigma = m_sigma q_ref
R_patch and R_flux are one global condition
8 continuous shooting/eigen unknowns
8 independent boundary residuals
```

Die acht kontinuierlichen unbekannten Größen bleiben:

\[
\bigl(
\phi_N(0),Q_N,A_S(0),\phi_S(0),Q_S,\rho_N,\rho_S,K_4
\bigr).
\]

Freeze-1B verändert diese Rollen nicht.

---

## 3. Skalarnormalisierung und Domäne

Der Bulk-Skalar besitzt den bereits fixierten kanonischen kinetischen Term

\[
-\frac12 g^{MN}\partial_M\phi\,\partial_N\phi.
\]

In sechs Dimensionen gilt damit

\[
[\phi]=M^2.
\]

Wir definieren

\[
\varphi\equiv\frac{\phi}{M_6^2},
\]

und frieren die Domäne ein als

\[
\boxed{\varphi\in\mathbb{R}}.
\]

Diese Wahl vermeidet einen künstlichen Feld-Cutoff. Sämtliche in diesem Block gewählten Funktionen sind auf ganz \(\mathbb R\) glatt und frei von Polstellen.

---

## 4. Exakte minimale Funktionswahl

### 4.1 Bulk-Potential

Gewählt wird

\[
\boxed{
U(\phi)=\frac12 m_\phi^2\phi^2
}
\]

mit

\[
\mu_\phi^2\equiv\frac{m_\phi^2}{M_6^2}>0.
\]

Äquivalent:

\[
U(\phi)=M_6^6\frac{\mu_\phi^2}{2}\varphi^2.
\]

Eigenschaften:

\[
U_{,\phi}=m_\phi^2\phi,
\qquad
U_{,\phi\phi}=m_\phi^2>0.
\]

Damit ist

\[
U(\phi)\ge 0
\]

und das eindeutige Minimum liegt bei \(\phi=0\).

#### Warum kein konstanter Term?

Ein Term \(U_0\) wäre exakt redundant mit \(\Lambda_6\), weil im Bulk nur die Kombination

\[
M_6^4\Lambda_6+U_0
\]

als konstante Vakuumenergiedichte auftritt. Freeze-1B entfernt daher diese Doppelparametrisierung.

#### Warum \(m_\phi^2>0\)?

Der strikt positive Wert schließt die aktive Shift-symmetrische Nullmodusfläche \(m_\phi^2=0\) aus der Modellfamilie aus. Das ist keine Stabilitätsaussage über das vollständige System, sondern eine identifizierbare Modellgrenze.

---

### 4.2 Maxwell-Kopplung

Gewählt wird

\[
\boxed{Z_F(\phi)=1}.
\]

Daraus folgt

\[
Z_{F,\phi}=0,
\qquad
\partial_\phi\ln Z_F=0.
\]

Die Funktion ist strikt positiv und besitzt keinen zusätzlichen Kopplungsparameter.

Diese Wahl bedeutet ausdrücklich:

- keine postulierte dilatonische Maxwell-Kopplung,
- keine Übernahme einer C1-V-Funktion,
- keine Behauptung, dass eine nichtkonstante Funktion physikalisch ausgeschlossen sei.

Nichtkonstantes \(Z_F\) bleibt eine spätere versionierte Erweiterung, nicht Bestandteil von `C-PHYS-ME1`.

---

### 4.3 Kap-Spannung

Gewählt wird

\[
\boxed{
\lambda(\phi)=M_6^5\tau\exp(\alpha\varphi)
}
\]

mit

\[
\tau>0,
\qquad
\alpha>0.
\]

Ableitungen:

\[
\lambda_{,\phi}
=M_6^3\tau\alpha e^{\alpha\varphi},
\]

\[
\lambda_{,\phi\phi}
=M_6\tau\alpha^2 e^{\alpha\varphi}.
\]

Die Funktion ist auf ganz \(\mathbb R\)

- \(C^\infty\),
- strikt positiv,
- frei von Nullstellen und Singularitäten.

#### Minimalitätsargument

Die exponentielle Form besitzt zwei dimensionslose Parameter und bindet Wert, Steigung und Krümmung zusammen:

\[
\frac{\lambda_{,\phi}}{\lambda}
=\frac{\alpha}{M_6^2},
\qquad
\frac{\lambda_{,\phi\phi}}{\lambda}
=\frac{\alpha^2}{M_6^4}.
\]

Damit werden keine drei voneinander unabhängigen lokalen Taylor-Koeffizienten eingeführt.

#### Vorzeichenredundanz

Da \(U\) gerade und \(Z_F,Z_\sigma\) konstant sind, bildet

\[
\phi\rightarrow-\phi,
\qquad
\alpha\rightarrow-\alpha
\]

dieselbe Modellfamilie ab. Freeze-1B entfernt diese Doppelzählung durch

\[
\boxed{\alpha>0}.
\]

---

### 4.4 Kap-Windungskoeffizient

Gewählt wird

\[
\boxed{
Z_\sigma(\phi)=M_6^3 z_\sigma
}
\]

mit

\[
z_\sigma>0.
\]

Damit gilt

\[
Z_{\sigma,\phi}=0,
\qquad
Z_{\sigma,\phi\phi}=0.
\]

Die Funktion ist strikt positiv und enthält keine zusätzliche Skalarabhängigkeit.

Weil die Phase periodisch und die Ladungsstruktur aus Freeze-1A fixiert ist, darf \(z_\sigma\) nicht stillschweigend durch eine Feldreskalierung entfernt werden.

---

## 5. Ladungsnormalisierung

Freeze-1A fixierte die Gitterrelation

\[
q_\sigma=m_\sigma q_{\rm ref},
\qquad
m_\sigma\in\mathbb Z_{>0},
\]

ließ aber den numerischen Ladungsmaßstab offen.

Freeze-1B postuliert

\[
\boxed{
q_{\rm ref}=\frac1{M_6}
}
\]

beziehungsweise

\[
\boxed{M_6 q_{\rm ref}=1}.
\]

Daraus folgt

\[
q_\sigma=\frac{m_\sigma}{M_6}.
\]

Diese Festlegung ist **keine Koordinatenkonvention**. Nach der Fixierung von

- \(\Delta\chi=2\pi\),
- Maxwell-Normalisierung,
- regelmäßigen Eichpatches,
- und Phasenperiodizität

kann \(q_{\rm ref}\) nicht mehr durch eine harmlose Reskalierung eliminiert werden. Die Wahl ist deshalb ein explizites Modellpostulat von `C-PHYS-ME1`.

---

## 6. Spezialisierte Bulk-Struktur

Aus

\[
F_{r\chi,s}
=\frac{Q_sL_s e^{-4A_s}}{Z_F(\phi_s)}
\]

folgt für \(Z_F=1\)

\[
F_{r\chi,s}=Q_sL_s e^{-4A_s}
\]

und

\[
\boxed{
\rho_{F,s}=\frac{Q_s^2e^{-8A_s}}2
}.
\]

Die skalare Bulk-Gleichung reduziert sich zu

\[
\boxed{
L_s\phi_s''+
\left(4A_s'L_s+L_s'\right)\phi_s'
-L_sm_\phi^2\phi_s=0
}.
\]

Der Term

\[
\rho_{F,s}\partial_\phi\ln Z_F
\]

verschwindet exakt.

Das bedeutet nicht, dass Skalar und Flux vollständig entkoppelt wären: Beide koppeln weiterhin über die Geometrie und die Kap-Randbedingungen.

---

## 7. Spezialisierte Kap-Struktur

Wir unterscheiden eindeutig:

- den gemeinsamen Kap-Feldwert
  \[
  \phi_{\rm cap}
  =\phi_N(\rho_N)=\phi_S(\rho_S),
  \]
- und die orientierte Ableitungssumme
  \[
  \Phi_\Sigma
  =\sum_s n_s\phi_s'(\rho_s).
  \]

Mit konstantem \(Z_\sigma\) wird der skalare Junction-Residual

\[
\boxed{
R_{\rm scalar}
=
\Phi_\Sigma
+M_6^3\tau\alpha
\exp\!\left(\alpha\frac{\phi_{\rm cap}}{M_6^2}\right)
=0
}.
\]

Der gauge-invariante Windungsterm lautet

\[
\boxed{
D_\chi\sigma
\equiv d_\chi
=N_\sigma-\frac{m_\sigma}{M_6}A_{\chi,\rm cap}
}.
\]

Die Windungsenergie ist

\[
\boxed{
Y_\sigma
=M_6^3z_\sigma
\frac{d_\chi^2}{L_{\rm cap}^2}
}.
\]

Der Patch-Residual wird

\[
\boxed{
R_{\rm patch}
=A_{\chi,N}(\rho_N)-A_{\chi,S}(\rho_S)-N_FM_6=0
}.
\]

Er bleibt identisch mit der globalen Fluxbedingung unter den eingefrorenen regelmäßigen Zwei-Patch-Konventionen und wird nur einmal gezählt.

---

## 8. Vollständiges kontinuierliches Modellbudget

### 8.1 Dimensionssetzender Maßstab

\[
M_6>0
\]

setzt Einheiten und die sechsdimensionale Gravitationsskala.

Ein rein dimensionsloser Hintergrundlauf kann \(M_6\) nicht separat identifizieren. Dafür ist später eine kontrollierte 6D→4D-Normalisierung erforderlich.

### 8.2 Kontinuierliche dimensionslose Modellparameter

Die minimale Familie enthält

\[
\boxed{
\Theta_{\rm model}
=
\left(
\widehat\Lambda_6,
\mu_\phi^2,
\tau,
\alpha,
 z_\sigma
\right)
}
\]

mit

\[
\widehat\Lambda_6
=\frac{\Lambda_6}{M_6^2},
\]

\[
\mu_\phi^2>0,
\qquad
\tau>0,
\qquad
\alpha>0,
\qquad
z_\sigma>0,
\]

während

\[
\widehat\Lambda_6\in\mathbb R.
\]

Damit beträgt das kontinuierliche dimensionslose Modellbudget

\[
\boxed{N_{\rm model}=5}.
\]

### 8.3 Diskrete Sektoren

Pro Modelllauf werden festgehalten:

\[
N_F\in\mathbb Z,
\qquad
N_\sigma\in\mathbb Z,
\qquad
m_\sigma\in\mathbb Z_{>0}.
\]

Diese Größen sind Sektorlabels, keine differenzierbaren Fitparameter.

### 8.4 BVP-Unbekannte

Die acht kontinuierlichen Shooting-/Eigenwert-Unbekannten bleiben:

\[
N_{\rm shoot}=8.
\]

Die unabhängigen Boundary-Residuals bleiben:

\[
N_{\rm boundary}=8.
\]

Daher lautet der Status jetzt präziser:

```text
SQUARE_FUNCTIONALLY_SPECIALIZED_CONDITIONAL
```

Das ist lediglich eine Zählung. Es ist kein Existenz- oder Invertierbarkeitssatz.

---

## 9. Identifizierbarkeitsanalyse

### 9.1 Exakt entfernte Redundanzen

Entfernt wurden:

1. \(U_0\) gegen \(\Lambda_6\),
2. das Vorzeichen von \(\alpha\) gegen \(\phi\to-\phi\),
3. additive Warp-Verschiebung durch \(A_N(0)=0\),
4. Winkelreskalierung durch \(\Delta\chi=2\pi\),
5. doppelte Patch-/Fluxzählung.

### 9.2 Nicht entfernbar

Nach kanonischer Skalar- und Maxwell-Normalisierung sind nicht redundant:

- \(\mu_\phi^2\),
- \(\alpha\),
- \(\tau\),
- \(z_\sigma\),
- \(q_{\rm ref}\).

### 9.3 Erwartete, aber nicht bewiesene Korrelationen

Eine einzelne Hintergrundlösung tastet am Kap primär die Kombinationen

\[
\tau e^{\alpha\varphi_{\rm cap}},
\]

\[
\alpha\tau e^{\alpha\varphi_{\rm cap}},
\]

und

\[
z_\sigma d_\chi^2
\]

ab. Daher können starke praktische Korrelationen zwischen

\[
\tau,\ \alpha,\ \varphi_{\rm cap}
\]

auftreten.

Diese Beobachtung ist nur eine strukturelle Warnung. Tatsächliche Identifizierbarkeit verlangt einen späteren Jacobian- und Informationsbudget-Test.

### 9.4 Noch offen

Nicht etabliert sind:

- kontinuierlicher Jacobianrang,
- strukturelle Identifizierbarkeit des Kontinuumsmodells,
- praktische Identifizierbarkeit,
- Konditionierung,
- Posteriorstruktur,
- Identifizierbarkeit aus Observablen.

Ein Parameterfit ist nicht autorisiert.

---

## 10. Positivitäts- und Boundedness-Audit

| Objekt | Ergebnis |
|---|---|
| \(U\) | auf \(\mathbb R\) nach unten beschränkt |
| \(Z_F\) | strikt positiv |
| \(\lambda\) | strikt positiv |
| \(Z_\sigma\) | strikt positiv |
| Funktionssingularitäten | keine auf \(\mathbb R\) |

Diese Aussagen betreffen ausschließlich die gewählten Funktionen.

Sie beweisen nicht:

- Positivität der vollständigen perturbativen kinetischen Matrix,
- Ghostfreiheit,
- Gradientenstabilität,
- Tachyonfreiheit,
- Stabilität der Hintergrundlösung.

---

## 11. Was mit Freeze-1B geschlossen wird

```text
exact U(phi)              = FROZEN
exact Z_F(phi)            = FROZEN
exact lambda(phi)         = FROZEN
exact Z_sigma(phi)        = FROZEN
scalar domain             = R, FROZEN
q_ref normalization       = 1/M6, FROZEN AS MODEL POSTULATE
coefficient dimensions    = FROZEN
coefficient domains       = FROZEN
redundancy audit          = COMPLETED
function positivity audit = COMPLETED
model parameter budget    = 5 continuous dimensionless parameters
```

---

## 12. Was weiterhin offen bleibt

```text
benchmark continuous parameter tuple
benchmark integer sector
dimensionless specialized operator normalization
constraint propagation proof
principal symbol audit
complementing boundary conditions
Fredholm property
continuum Jacobian
physical background existence
perturbative stability
ghost freedom
4D observable bridge
```

---

## 13. Gate-Wirkung

```text
R1.0                      = ACTIVE_MODEL_FREEZE_INCOMPLETE
R1.0 substate             = FUNCTION_FAMILY_FROZEN_BENCHMARK_INSTANCE_OPEN
R1.1                      = BLOCKED
R1.2                      = BLOCKED
structural BVP count      = SQUARE_FUNCTIONALLY_SPECIALIZED_CONDITIONAL
continuum BVP operator    = SCAFFOLD_ONLY
continuum BVP Jacobian    = NOT_PROVEN
official MD-2S solver     = NOT_AUTHORIZED
K1-D                      = NOT_RELEASED
K1-E                      = NOT_ADMISSIBLE
physical evidence effect  = NONE
```

---

## 14. Verbotene Schlussfolgerungen

- Die Funktionswahl ist keine Ableitung aus Naturdaten.
- Sie ist keine historische A0-Rekonstruktion.
- Sie übernimmt keine C1-V-Parameter.
- Funktionspositivität ist keine Ghostfreiheit.
- Eine quadratische BVP-Zählung ist kein Existenzsatz.
- Es existiert noch keine physikalische Hintergrundlösung.
- Es existiert noch kein freigegebener Solver.
- Es folgt keine Freigabe von R1.1, R1.2, K1-D oder K1-E.

---

## 15. Exakt nächster zulässiger Primärblock

```text
C-PHYS-R1.0-FREEZE-1C
```

Titel:

```text
Freeze one benchmark model instance, discrete sector and dimensionless normalization
```

Freeze-1C muss vor jeder numerischen Ausführung fixieren:

1. einen konkreten Parametervektor
   \[
   (\widehat\Lambda_6,\mu_\phi^2,\tau,\alpha,z_\sigma),
   \]
2. einen diskreten Sektor
   \[
   (N_F,N_\sigma,m_\sigma),
   \]
3. dimensionslose Variablen und Residualskalen,
4. Hierarchien und Naturalness-Annahmen,
5. einen Pre-Solver-Regularitäts- und Identifizierbarkeitscheck.

Auch Freeze-1C darf noch keinen physikalischen Solverlauf enthalten.

---

## 16. Standardisierter Blockabschluss

### A. Was wurde gemacht?

Eine exakte minimale EFT-Funktionsfamilie, Skalardomäne und Ladungsnormalisierung wurden als neues C-PHYS-Modellpostulat ausgewählt.

### B. Was wurde tatsächlich bestätigt?

Bestätigt wurde nur die interne mathematische Konsistenz der Funktionswahl mit den bereits eingefrorenen Dimensionen, Regularitäts- und Positivitätsanforderungen.

### C. Was wurde nicht bewiesen?

Keine Lösung, keine Identifizierbarkeit, keine Stabilität und keine physikalische Evidenz.

### D. Bearbeiteter Track

```text
MD2S-R1-C-PHYS
```

### E. Gate-Wirkung

Nur der Funktionsfamilien-Teil von R1.0 wird geschlossen. Der Benchmark-Modellinstanz-Block bleibt offen; alle Solver- und Release-Gates bleiben geschlossen.

### F. Neue Artefakte

Funktionsvertrag, dieses Ledger, Statusartefakt, Validator, Tests, CI-Vertrag, Entscheidung und Checkpoint.

### G. Nächster Block

```text
C-PHYS-R1.0-FREEZE-1C
```
