# Hyperzeit-GW-Falsifikationsdossier — Rigor Audit v0.1

**Datum:** 2026-08-01  
**Quelle:** `Hyperzeit-GW-Falsifikationsdossier.docx`  
**Status:** CONDITIONAL PHENOMENOLOGY / REPRODUCIBILITY OPEN  
**Evidenzwirkung:** NONE

## 1. Gesamturteil

Das Dossier enthält ein wertvolles und klar falsifizierbares **effektives GW-Forschungsprogramm**:

```text
Bulk-Schwellenhypothese
→ effektive Phasenkorrektur δΨ_HZ(f)
→ synthetische Injektionen
→ Detektierbarkeit Δρ
→ Fisher-/Hessian-Identifizierbarkeit
→ Projektion auf den GR-Tangentialraum
→ R_unique
```

Seine stärkste belastbare Aussage lautet nicht, dass eine konkrete 6D-Hyperzeit-Theorie Gravitationswellensignaturen erzeugt, sondern:

> Eine lokal aktivierte, frequenzabhängige Phasenkorrektur kann als testbare und prinzipiell falsifizierbare Beyond-GR-Signatur parametrisiert werden.

Die fundamentale Kette

```text
6D-Wirkung → regulärer Hintergrund → physische Bulk-Moden
→ Energiefluss → binäre Dynamik → δΨ_HZ(f)
```

ist im Dossier ausdrücklich nicht geschlossen.

## 2. Statusmatrix der theoretischen Aussagen

### A1 — Constraintstruktur des Schersektors

**Dossierbehauptung:** In `δG_r^θ` heben sich die Ableitungen `b₁′` und `c₁′` auf; die Gleichung ist algebraisch/constraintartig.

**Audit:** Die expliziten Koeffizienten des linearisierten Operators werden nicht angegeben. Ohne vollständige Variation, Eichanalyse und Hintergrundgleichungen ist nicht prüfbar, ob die behauptete Eliminierung allgemein oder nur für einen speziellen Ansatz gilt.

**Status:** `CONDITIONAL / EXPLICIT_OPERATOR_MISSING`.

### A2 — Dynamischer Radionsektor

**Dossierbehauptung:** Die Differenz `δ(R_r^r−R_θ^θ)` enthält eine nichttriviale radiale Dynamik, unter anderem einen Term `−4A₀′c₁′`.

**Audit:** Ein erster Ableitungsterm belegt allein noch keinen unabhängigen propagierenden Freiheitsgrad. Erforderlich sind Constraintzählung und quadratische Wirkung beziehungsweise Hamiltonanalyse.

**Status:** `HEURISTIC_TO_CONDITIONAL`.

### B1 — Existenz regulärer Lösungen

**Dossierargument:** Nach Elimination von `b₁` wird eine Green-Funktion `G(r,r′)` angesetzt; daraus folge Existenz.

**Audit:** Dieses Argument ist zirkulär. Die Existenz einer Green-Funktion setzt bereits einen wohldefinierten Operator, geeigneten Definitionsbereich, Randbedingungen und ausreichende Invertierbarkeit voraus.

Für einen belastbaren Existenzsatz werden mindestens benötigt:

- präziser Funktionenraum,
- geschlossener/dicht definierter Operator,
- Rand- oder Regularitätsbedingungen,
- Fredholm-, Lax-Milgram-, Sturm-Liouville- oder äquivalente Voraussetzungen,
- Behandlung möglicher Nullmoden.

**Status:** `OPEN / NOT_PROVEN`.

### B2 — Eindeutigkeit

**Dossierargument:** Regularität am Ursprung und Abfall im Unendlichen eliminierten alle homogenen Lösungen.

**Audit:** Diese Aussage wird behauptet, nicht bewiesen. Nichttriviale gebundene Zustände oder Nullmoden können dieselben Randbedingungen erfüllen. Eindeutigkeit erfordert beispielsweise eine positive Energieform, ein Wronskianargument oder den Nachweis, dass Null nicht im Spektrum liegt.

**Status:** `OPEN / NOT_PROVEN`.

### C1 — Keine statische normalisierbare KR-Dipolmode

**Dossierargument:** Eine Energieform

```text
E[β] = ∫dr w(r)[(β′)² + U_eff(r)β²]
```

sei nichtnegativ, daher sei nur `β=0` möglich.

**Audit:** Das Resultat gilt nur, wenn

```text
w(r)>0,
U_eff(r)≥0
```

fast überall gelten und alle Randterme tatsächlich verschwinden. Im Dossier ist

```text
U_eff = M_KR² − V_eff(r)
```

definiert; die Positivität folgt nicht allein aus `M_KR²>0`. Zusätzlich müssen Eichredundanzen und der physische Hilbertraum des massiven antisymmetrischen Feldes geklärt werden.

**Status:** `CONDITIONAL_POSITIVITY_THEOREM / CONDITIONS_NOT_ESTABLISHED`.

### C2 — Dynamische Schwellenaktivierung

**Dossierbehauptung:** Ein lokaler Vorzeichenwechsel von `Q(r,ω)` bei `ω>ω_crit` erzeuge propagierende Lösungen.

**Audit:** Ein lokaler Vorzeichenwechsel ist eine WKB-/Turning-Point-Diagnose, aber kein globaler Existenz- oder Transmissionsbeweis. Für eine physische Onset-Frequenz werden Spektrum, Randbedingungen, Tunnelbarrieren, Normalisierung und Kopplung an die Quelle benötigt.

**Status:** `HEURISTIC_WKB_THRESHOLD`.

## 3. Effektive Phasenparametrisierung

Das Dossier definiert schematisch

```text
δΨ_HZ(f)
= α_dyn β_dyn(f) (π𝓜_c f)^q
  Θ_smooth(f;f_thr,Δ) T(f;f_star,p).
```

Diese Form ist als **effektive Testfamilie** zulässig, sofern:

- jede Funktion explizit definiert wird,
- der GR-Grenzfall `α_dyn→0` exakt reproduziert wird,
- Parameterbereiche vorregistriert sind,
- Dimensionslosigkeit der Phase geprüft ist,
- keine mehrfachen äquivalenten Parametrisierungen als unabhängige Physik interpretiert werden.

Die Identifikation

```text
f_thr = ω_crit/(2π)
```

ist gegenwärtig semantisch motiviert, aber nicht aus einer vollständigen 6D-Quellantwort hergeleitet.

**Status:** `EFFECTIVE_WITH_PARTIAL_PHYSICAL_SEMANTICS`.

## 4. Numerische Audits N1–N4

Das Dossier berichtet:

- No-Noise-Recovery,
- Injection-Recovery,
- SNR-Skalierung,
- Robustheit gegen alternative Onsetformen.

Im hochgeladenen Dokument fehlen jedoch die vollständigen ausführbaren Artefakte:

- Code/Notebook,
- Detektor-PSD-Dateien und Versionen,
- Injektionsparameter,
- Priors,
- Seeds,
- Likelihoodnormalisierung,
- Konvergenzdiagnostik,
- Rohposterior oder Samples,
- Hashmanifest.

Daher gilt:

```text
reported numerical result ≠ independently reproduced result.
```

**Status N1–N4:** `REPORTED_NOT_REPRODUCED_FROM_SOURCE_BATCH`.

## 5. Morphologieaudit M1

Das Dossier interpretiert eine große Zahl linearer PCA-Komponenten zur Erklärung von 99,9 % der globalen Varianz als hochdimensionale Signaturmannigfaltigkeit.

Diese Interpretation ist nicht korrekt ohne Zusatzanalyse:

- Eine glatte Familie mit fünf Parametern besitzt lokal höchstens fünf Tangentialrichtungen.
- Eine stark gekrümmte, aber fünfdimensionale Mannigfaltigkeit kann global sehr viele **lineare** PCA-Komponenten benötigen.
- Viele PCA-Komponenten belegen daher globale Nichtlinearität oder Krümmung, nicht automatisch hohe intrinsische Dimension.

Das spätere Ergebnis `N_eff≈1,1` aus einer lokalen Fisher-/Informationsanalyse kann gleichzeitig auftreten. Es misst eine andere Größe: die lokal durch das gewählte Experiment getragene Informationsdimension.

**Korrekte Trennung:**

```text
global PCA dimension = lineare Approximation des gesamten Formraums,
local manifold dimension ≤ Anzahl unabhängiger Modellparameter,
Fisher N_eff = experimentell zugängliche lokale Informationsdimension.
```

**Status der Aussage „dim_999 > 100 ⇒ intrinsisch hochdimensional“:** `FALSIFIED_INTERPRETATION`.

**Status der Aussage „der Formraum ist global nichttrivial/gekrümmt“:** `CONDITIONAL_NUMERICAL_CLAIM`.

## 6. Detektierbarkeit D1

Die Metrik

```text
Δρ² = (δh|δh)
```

ist eine sinnvolle Forecastgröße für den Abstand zweier festgelegter Signale im rauschgewichteten Hilbertraum.

Sie ist jedoch keine Entdeckungsstatistik, solange nicht berücksichtigt werden:

- Maximierung über GR-Parameter,
- Look-elsewhere-Effekt,
- Modellprioren,
- Waveformsystematik,
- PSD- und Kalibrationsunsicherheit,
- Populationsselektion.

Konturen `Δρ=5` oder `10` sind daher Diagnosekonturen, keine universellen Evidenzschwellen.

**Status:** `VALID_DIAGNOSTIC_FORECAST / NOT_EVIDENCE`.

## 7. GR-Projektion und R_unique

Mit einer Tangentenbasis `e_i=∂h/∂Θ_i` und Fishermatrix `Γ_ij=(e_i|e_j)` wird lokal

```text
P_GR = Σ_ij |e_i⟩(Γ⁻¹)_ij⟨e_j|
```

definiert. Die Größe

```text
R_unique = ||(I−P_GR)δh_HZ|| / ||δh_HZ||
```

ist mathematisch sinnvoll, wenn:

- `Γ` regulär oder kontrolliert pseudoinvertiert ist,
- die Basis mit derselben PSD und Frequenzmaske normiert wird,
- der gewählte GR-Unterraum hinreichend vollständig ist,
- nichtlineare Reoptimierungseffekte klein sind.

`R_unique>0` belegt nur Orthogonalität zum **gewählten lokalen Tangentialraum**. Es beweist keine fundamentale Nicht-GR-Ursache.

**Status:** `CONDITIONAL_LOCAL_GEOMETRIC_DIAGNOSTIC`.

## 8. Konsistente Statushierarchie

| Dossierblock | Auditstatus |
|---|---|
| lineare Operatoridee | konditional |
| Existenz/Eindeutigkeit | offen, nicht bewiesen |
| statischer KR-No-Go | konditional auf Positivität und Domäne |
| dynamische Schwelle | heuristisch/WKB |
| δΨ_HZ-Testfamilie | effektive Phänomenologie |
| N1–N4 | berichtet, nicht reproduziert |
| M1 hohe intrinsische Dimension | Interpretation falsifiziert |
| Δρ-Forecasts | diagnostisch |
| R_unique | lokale konditionale Diagnose |
| reale Evidenz | nicht vorhanden |

## 9. Erforderliches Reproduktionspaket

UniverseLab soll für jeden GW-Lauf erzeugen:

```text
run.json
waveform-config.json
psd-manifest.json
parameters.json
priors.json
injection.json
likelihood-config.json
samples.*
fisher.json
projection.json
metrics.json
environment.json
manifest.json
```

Alle Eingaben und Ausgaben benötigen SHA-256-Verknüpfungen.

## 10. Falsifikationspfade

Die effektive Modellklasse kann ausgeschlossen oder eingeschränkt werden, wenn:

1. reale Daten keine Onsetstruktur zulassen und robuste Obergrenzen auf `α_dyn(f_thr)` liefern;
2. realistische IMR-Waveforms die vermeintlich eindeutige Signatur vollständig absorbieren;
3. Systematiken die prognostizierte `δh`-Richtung imitieren;
4. der fundamentale 6D-Sektor keine positive, gekoppelte dynamische Mode mit passender Schwelle besitzt;
5. die hergeleitete Energieflusskorrektur nicht zur verwendeten `δΨ_HZ`-Form führt.

## 11. Einordnung in HPVS → HZT-M0 → HZT-Full

Das GW-Dossier darf als eigenständiges **phenomenological falsification laboratory** in UniverseLab erhalten bleiben. Es darf jedoch nicht die MD-2S-/K1-D-Hauptkette ersetzen.

Empfohlene Architektur:

```text
GW-PHENO-LAB
  Status: effective / diagnostic / forecast
  Input: explizite δΨ-Testfamilie
  Output: Detektierbarkeit, Identifizierbarkeit, GR-Degenerenz

HZT-M0 FUNDAMENTAL BRIDGE
  Status: open
  Aufgabe: 6D → physische Mode → Energiefluss → δΨ
```

Nur wenn beide Ebenen verbunden sind, wird aus dem GW-Labor ein Test einer konkreten HZT-M0-Realisierung.
