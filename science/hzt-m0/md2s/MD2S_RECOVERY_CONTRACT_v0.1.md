# MD-2S Recovery Contract v0.1

**Programm:** UniverseLab Research Continuation Program  
**Zweig:** HZT-M0-S6 / SCI-001 / SCI-002 / MD-2S / B1.4O  
**Datum:** 2026-08-01  
**Status:** CANONICAL RECOVERY SPECIFICATION / NOT A PHYSICAL RELEASE  
**Evidenzwirkung vor erfolgreichem Abschluss:** NONE

## 1. Ziel

Dieser Vertrag definiert die Mindestanforderungen für die Wiederherstellung oder den reproduzierbaren Neuaufbau des MD-2S-Hintergrundproblems. Er verhindert, dass globale Benchmarkzahlen, rekonstruierte Diagrammwerte oder nachträglich angepasste Randdaten als Ersatz für einen vollständigen Solverlauf verwendet werden.

Ein erfolgreicher Recovery-Lauf liefert noch keine K1-D- oder K1-E-Freigabe. Er stellt lediglich die Ausführbarkeit der nachfolgenden Junction-, Constraint-, Stabilitäts- und Identifizierbarkeitsprüfungen her.

## 2. Kanonischer Hintergrundansatz

Der aktuelle MD-2S-Zweig verwendet den statischen, axial symmetrischen 6D-Ansatz

```text
ds₆² = e^{2A(r)} ḡ_{μν}(x) dx^μ dx^ν + dr² + L²(r) dχ²,
```

mit

```text
ḡR_{μν} = 3 K₄ ḡ_{μν}.
```

Definitionen:

- r: radiale interne Koordinate, Dimension Länge,
- χ: dimensionslose Winkelkoordinate,
- A(r): dimensionsloser Warpfaktor,
- L(r): interner Kreisradius, Dimension Länge,
- K₄: vierdimensionale Krümmungsskala, Dimension Länge⁻²,
- ḡ_{μν}: maximalsymmetrische 4D-Metrik.

Dimensionscheck:

- e^{2A} ist dimensionslos,
- dr² und L²dχ² besitzen Dimension Länge²,
- K₄ρ_cap² ist dimensionslos,
- √K₄ ρ_cap ist dimensionslos.

## 3. Parentwirkungs-Skelett

Die v0.1-Recovery muss mindestens mit dem bereits registrierten Einstein-Maxwell-Skalar-Kern konsistent sein:

```text
S_bulk = ∫_M d⁶x √|g₆| [
  (1 / 2κ₆²)(R₆ − 2Λ₆)
  − 1/2 Z_φ(φ) g^{AB} ∂_Aφ ∂_Bφ
  − V(φ)
  − 1/4 Z_F(φ) F_{AB}F^{AB}
].
```

Ergänzt werden müssen die für die konkrete Geometrie erforderlichen Rand-, Kappen- und Branenterme, insbesondere der Gibbons-Hawking-York-Term und die in SCI-001/SCI-002 festgelegten lokalisierten Beiträge.

Definitionen und Dimensionen in natürlichen Einheiten ħ=c=1:

- [x^A] = Masse⁻¹,
- [d⁶x] = Masse⁻⁶,
- [R₆] = [Λ₆] = Masse²,
- [κ₆²] = Masse⁻⁴ = Länge⁴,
- [M₆] = Masse mit κ₆² ∼ M₆⁻⁴,
- eine codimension-1 effektive Spannung λ_eff besitzt Dimension Masse⁵,
- κ₆² λ_eff / √K₄ ist dimensionslos.

Die exakten Normalisierungen von Z_φ, Z_F, Fluxladung und lokalisierten Phasen sind aus der kanonischen SCI-001/SCI-002-Quelle zu übernehmen. Sie dürfen nicht aus Benchmarkzahlen rückwärts angepasst werden.

## 4. Bekannte globale Benchmarks

Für den dokumentierten Normierungsfall K₄=β=1 liegen folgende Werte vor:

```text
√K₄ ρ_cap = 1.1196329253611,
κ₆² λ_eff / (4√K₄) = 0.8931498683204,
K₄ ρ_cap² = 1.2535778875527,
V_W = 0.5318111250097,
R_○ = 0.6661500466003.
```

Diese Werte sind Reproduktionsziele. Sie sind keine vollständigen Anfangs- oder Randbedingungen und bestimmen insbesondere nicht automatisch:

- A′ auf beiden Seiten der Kappe,
- L und L′ auf beiden Seiten,
- φ′ auf beiden Seiten,
- Fluxorientierung und Gauge-Potential,
- orientierte Normalen,
- einzelne Junction-Komponenten,
- Constraintresiduen.

## 5. Zu rekonstruierendes Randwertproblem

Vor dem ersten numerischen Lauf müssen vollständig angegeben werden:

### 5.1 Unbekannte Funktionen

Mindestens:

```text
u(r) = {A(r), L(r), φ(r), gauge/flux variable(s)}.
```

Jede zusätzliche Hilfsvariable ist als algebraische Definition oder unabhängige Differentialvariable zu kennzeichnen.

### 5.2 Modellparameter

Mindestens:

```text
p = {κ₆, Λ₆, β, Fluxparameter, K₄, Kappparameter, Branenparameter}.
```

Für jeden Parameter sind anzugeben:

- Symbol,
- numerischer Wert,
- Einheit oder dimensionslose Normierung,
- physikalische Rolle,
- Quelle,
- ob fest, gescannt oder geschossen,
- zulässiger Bereich.

### 5.3 Zentrum-/Polbedingungen

Die Regularitätsbedingungen am glatten Zentrum müssen aus der lokalen Reihenentwicklung gewonnen werden. Mindestens zu prüfen sind:

```text
L(r) = r + O(r³)             nach geeigneter radialer Normierung,
A′(0) = 0,
φ′(0) = 0,
```

sowie die Regularität aller Flux- und Krümmungsinvarianten.

Die Bedingung L′(0)=1 ist koordinaten- und periodenkonventionsabhängig. Die verwendete χ-Periode und eine mögliche Defizitwinkelkonvention müssen explizit dokumentiert werden.

### 5.4 Kappen-/Junction-Bedingungen

An r=ρ_cap sind beide orientierten Seiten getrennt zu exportieren. Die symbolische Minimalstruktur lautet:

```text
A′_−, L_−, L′_−, φ′_−, Flux_−, n^A_−,
A′_+, L_+, L′_+, φ′_+, Flux_+, n^A_+.
```

Die Umbilizitätsdiagnostik verwendet

```text
U_umb = A′ − L′/L,
```

wobei das physikalische Junctionresiduum aus den korrekt orientierten, in SCI-001/SCI-002 definierten Sprüngen oder Summen konstruiert werden muss. Ein einzelner einseitiger Wert ist kein Junction-Urteil.

## 6. Residualvektor

Jeder Lauf muss einen maschinenlesbaren Residualvektor ausgeben:

```text
R = (
  R_bulk,
  R_Hamiltonian,
  R_center,
  R_metric_junction,
  R_scalar_junction,
  R_gauge_junction,
  R_flux_global,
  R_normalization
).
```

Für jede Komponente sind zu speichern:

- Rohresiduum,
- dimensionslose Normierung,
- absolute Toleranz ε_abs,
- relative Toleranz ε_rel,
- PASS/FAIL,
- Auswertungsort,
- Gleichungs-ID.

Die Toleranzen müssen vor der physikalischen Auswertung festgelegt werden. Nachträgliche Lockerungen erfordern einen neuen RUN_ID und eine Begründung.

## 7. Reproduktionsmanifest

Jeder Lauf erhält eine eindeutige RUN_ID und mindestens folgende Metadaten:

```json
{
  "run_id": "MD2S-RUN-YYYYMMDD-NNN",
  "model_version": "...",
  "equation_set_hash": "sha256:...",
  "solver_source_hash": "sha256:...",
  "parameter_file_hash": "sha256:...",
  "software_versions": {},
  "floating_point_precision": "...",
  "solver_method": "...",
  "mesh_or_collocation": {},
  "absolute_tolerance": "...",
  "relative_tolerance": "...",
  "initial_guess_provenance": "...",
  "seed": null,
  "output_hashes": {},
  "status": "PASS|FAIL|INCOMPLETE"
}
```

Ein deterministischer Solver darf `seed=null` verwenden. Stochastische oder randomisierte Initialisierungen müssen den Seed speichern.

## 8. Pflichtausgaben

Jeder vollständige Recovery-Lauf erzeugt:

1. `parameters.json`
2. `conventions.json`
3. `solver-config.json`
4. `profiles.csv` oder äquivalentes verlustfreies Format
5. `boundary-left.json`
6. `boundary-right.json`
7. `residuals.json`
8. `benchmarks.json`
9. `environment.json`
10. `manifest.json`
11. optionales menschenlesbares `report.md`

Die Profilpunkte müssen mindestens r, A, A′, L, L′, φ, φ′ und die verwendeten Fluxvariablen enthalten.

## 9. Reproduktionskriterien R1

R1 gilt nur als bestanden, wenn:

- alle bekannten A0-Benchmarks innerhalb vorab deklarierter Toleranzen reproduziert sind,
- die Lösung unter Gitter-/Kollokationsverfeinerung konvergiert,
- die Bulk- und Constraintresiduen kontrolliert abfallen,
- die lokale Zentrumserweiterung numerisch bestätigt wird,
- Krümmungsinvarianten im vorgesehenen Bereich regulär bleiben,
- keine Benchmarks durch nachträgliche unabhängige Parameteranpassung einzeln erzwungen wurden,
- alle Dateien über SHA-256-Prüfsummen verbunden sind.

Ein guter Benchmark-Fit bei großen Residuen ist FAIL.

## 10. Übergangs- und Grenzregime

### 10.1 Zentrum r→0

Erforderlich ist eine reguläre Reihenentwicklung. Führende ungerade oder gerade Potenzen richten sich nach Tensorcharakter und Symmetrie. Numerische Differenzen direkt bei r=0 dürfen nicht unkontrolliert verwendet werden.

### 10.2 Kappennähe r→ρ_cap^− und r→ρ_cap^+

Einseitige Grenzwerte sind getrennt zu bestimmen. Eine zentrale Differenz über eine Junction hinweg ist unzulässig.

### 10.3 Schwache 4D-Krümmung K₄→0

Der bestehende MD-2S-Befund, dass im untersuchten Zweig kein flacher K₄=0-Zweig vorliegt, ist als zu testender Strukturpunkt zu behandeln. Eine numerische Fortsetzung in Richtung K₄→0 darf nicht automatisch als existierende flache Lösung interpretiert werden.

### 10.4 Schwere interne Moden

Für m_χ,m_KK→∞ bei festen 4D-Skalen wird eine GR-nahe Niedrigenergiegrenze erwartet. Dieser Grenzfall gehört nicht zum reinen Hintergrund-Recovery, muss aber später in der Reduktion geprüft werden.

## 11. B1.4O-Anschluss

Erst nach bestandenem R1–R3 wird die Response-Matrix konstruiert:

```text
c_i = kontrollierte geometrische oder mikrophysikalische Variationen,
y_a = Zielgrößen und normalisierte Residuen,
J_ai = ∂y_a/∂c_i.
```

Pflichtdiagnostik:

- Rang von J,
- Singulärwerte σ_i,
- Konditionszahl κ(J)=σ_max/σ_min für den nichtverschwindenden Unterraum,
- rechter Nullraum: nicht identifizierbare Kontrollrichtungen,
- linker Nullraum: nicht erreichbare Zielkombinationen,
- Robustheit unter Schrittweite, Diskretisierung, Regulator und Normierung,
- physische Zulässigkeit jedes Kontrollvektors.

Numerischer Vollrang allein beweist keine physikalische Identifikation.

## 12. Freigabelogik

```text
R0 RECOVERED
  -> prüfe Provenienz und reproduziere den Originalrun.

R0 NOT FOUND
  -> R1 REBUILD.

R1 PASS
  -> R2 boundary export.

R2 PASS
  -> R3 SCI-001/SCI-002 complete junction and flux gates.

R3 PASS
  -> R4 B1.4O rank/conditioning audit.

R4 PASS
  -> Hintergrundzweig bleibt nur für die nachfolgende Störungsanalyse zulässig.
```

Keiner dieser Schritte allein setzt K1-D oder K1-E auf PASS.
