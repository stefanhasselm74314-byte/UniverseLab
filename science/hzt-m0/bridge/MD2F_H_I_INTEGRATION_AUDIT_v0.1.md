# MD-2F / MD-2H / MD-2I Integration Audit v0.1

**Datum:** 2026-08-01  
**Zweig:** HPVS → HZT-M0 → K1-D  
**Status:** SOURCE-INTEGRATED / K1-D NOT RELEASED  
**Evidenzwirkung:** NONE

## 1. Kernergebnis

Die hochgeladenen Dokumente MD-2F, MD-2H und MD-2I bilden eine konsistente Auditkette:

```text
MD-2F: Mappingproblem klassifiziert
→ MD-2H: Brückengleichungsrahmen definiert
→ MD-2I: minimale Herleitungsmenge MDS-01 … MDS-05 festgelegt
→ K1-D bleibt gesperrt
```

Die Dateien liefern keinen neuen evidenziellen Jacobian. Sie präzisieren, warum ein technisch berechenbarer Jacobian ohne physikalisch freigegebenes Mapping nicht als Identifizierbarkeitsnachweis gelten darf.

## 2. Parameter- und Mappingebenen

Es sind drei Ebenen strikt zu unterscheiden:

```text
P_phys = (a₀, β_τ, R_χ, I_B, κ₆)
P_mod  = (m, ω_c, η, s; k_c abgeleitet)
O      = Observablen oder diagnostische Modellantworten
```

Die Kette für K1-D lautet:

```text
P_phys → P_mod → O → J = ∂O/∂P_phys → rank(J), ker(J).
```

Ein Jacobian bezüglich freier Proxyparameter in `P_mod` beantwortet nur die technische Frage, ob die gewählte Parametrisierung lokal unterscheidbare Kurven erzeugt. Er beantwortet nicht, ob die fundamentalen HZT-M0-Parameter physikalisch identifizierbar sind.

## 3. Bereits belastbare Teilrelationen

### 3.1 Dämpfungsskala

```text
k_c = m / ω_c.
```

Mit

- `[m] = Mpc⁻¹`,
- `[ω_c] = 1`,

folgt

```text
[k_c] = Mpc⁻¹.
```

Diese Relation ist **abgeleitet, aber konditional**. Sie definiert weder den mikrophysikalischen Ursprung von `m` noch von `ω_c`.

### 3.2 Kernel

```text
A(k) = exp[−(k/k_c)²].
```

Der Exponent ist dimensionslos, falls `[k]=[k_c]=Mpc⁻¹`. Die Form des Kernels ist damit mathematisch wohldefiniert. Seine physikalische Herkunft aus dem 6D-Sektor bleibt jedoch offen.

## 4. Härtung der minimalen Herleitungsmenge

### MDS-01: `R_χ → m`

Die physikalisch saubere Form ist nicht bloß eine frei gewählte Konvention, sondern ein Eigenwertproblem auf dem internen Raum:

```text
𝓛_int u_n = λ_n u_n,

m_n² = λ_n / R_χ²,

m_n = √λ_n / R_χ.
```

Dabei sind:

- `𝓛_int` der dimensionslose interne Operator nach Skalierung mit `R_χ`,
- `λ_n` ein dimensionsloser Eigenwert,
- `R_χ` eine Länge,
- `m_n` eine inverse Länge.

Dimensionscheck:

```text
[m_n] = 1/[R_χ].
```

Die in MD-2H/MD-2I verwendete Größe `ξ_m` entspricht damit höchstens `√λ_1`. Sie darf erst festgelegt werden, wenn interne Geometrie, Operator, Eichbedingungen und Randbedingungen bestimmt sind.

**Status:** konditional herleitbar, aber noch nicht freigegeben.

### MDS-02: `(β_τ, I_B, κ₆) → ω_c`

Da `ω_c` dimensionslos ist, muss jede zulässige Brücke ausschließlich dimensionslose Kombinationen enthalten:

```text
ω_c = Ω(Π₁, Π₂, …),
```

wobei jede `Π_i` eine dimensionslose Invariante des reduzierten Modells ist.

Eine bloße Funktionssignatur

```text
ω_c = Ω(β_τ, I_B, κ₆)
```

ist nicht hinreichend, solange Einheiten und Normalisierungen von `β_τ` und `I_B` sowie die Kombination mit `κ₆` unbekannt sind.

**Status:** offen; kritischer Blocker.

### MDS-03: `(a₀, β_τ, I_B) → η`

`η` ist dimensionslos. Eine zulässige Brücke benötigt mindestens eine Referenzbeschleunigung `a_ref` oder eine aus dem Modell hergeleitete dimensionslose Größe:

```text
η = Η(a₀/a_ref, Π_β, Π_B, …).
```

Solange `a_ref` und die Responsegleichung nicht aus dem 6D-/4D-Sektor folgen, ist `η` ein effektiver Amplitudenparameter.

**Status:** offen. Für einen reduzierten K1-D-Test muss `η` entweder hergeleitet, festgehalten oder ausgeschlossen werden.

### MDS-04: `(R_χ, β_τ) → s`

Ein Formexponent `s` ist nicht automatisch ein fundamentaler Freiheitsgrad. Er kann entstehen aus:

- einer asymptotischen Potenz eines hergeleiteten Operators,
- einer Spektraldichte,
- einer Interpolationskonvention,
- oder einer rein phänomenologischen Fitform.

Ohne solche Herleitung darf `s` nicht als unabhängige physikalische Richtung in K1-D eingehen.

**Empfohlene v0.1-Entscheidung:** `s` für einen reduzierten Dry-Run fixieren; keine Evidenzwirkung.

### MDS-05: `κ₆ → 4D-Normalisierung`

Für einen metrischen Ansatz

```text
ds₆² = e^{2A(y)} g_{μν}(x)dx^μdx^ν + g_{ab}(y)dy^ady^b
```

enthält die Einstein-Hilbert-Wirkung den 4D-Term

```text
S₆ ⊃ [1/(2κ₆²)] ∫d⁴x√|g₄| R₄
      × ∫d²y√g₂ e^{2A(y)}.
```

Daraus folgt das generische Normierungsskelett

```text
1/κ₄² = V_W/κ₆²,

V_W := ∫d²y √g₂ e^{2A(y)}.
```

Dimensionscheck in natürlichen Einheiten:

```text
[κ₆²] = M⁻⁴,
[V_W] = M⁻²,
[V_W/κ₆²] = M² = [κ₄⁻²].
```

Diese Gleichung ist nur das gravitative Normierungsskelett. Für konkrete Observablen werden zusätzlich benötigt:

- normierte Modenprofile,
- Branen-/Kappenlokalisierung,
- Materiekopplung,
- mögliche lokalisierte Einstein-Terme,
- Feldredefinition in den 4D-Einstein-Rahmen.

**Status:** formal herleitbares Skelett; numerische Freigabe hängt direkt vom MD-2S-Hintergrund und seiner Provenienz ab.

## 5. Verbindung zum MD-2S-Recovery

MD-2S ist nicht ein paralleles Nebenproblem, sondern liefert zentrale Eingaben für die Brückenkette:

```text
MD-2S-Hintergrund
→ A(r), L(r), interne Geometrie und Randbedingungen
→ V_W
→ κ₆-zu-κ₄-Normalisierung
→ interner Eigenwertoperator
→ λ_n und m_n
→ mögliche physikalische Herkunft von m und Teilen der Dämpfungsantwort.
```

Damit können erfolgreiche R1–R3-Arbeiten am MD-2S-Zweig unmittelbar MDS-01 und MDS-05 härten. Sie lösen MDS-02 und MDS-03 nicht automatisch.

## 6. Reduzierter K1-D-Kandidat

Ein reduzierter technischer Test könnte später verwenden:

- `s` fest,
- `η` ausgeschlossen oder fest,
- `k_c` abgeleitet,
- `m` aus einem freigegebenen internen Eigenwert,
- `ω_c` nur dann variabel, wenn eine dimensionslose physikalische Brücke vorliegt.

Ohne freigegebenes `ω_c` verbleibt kein vollständiger physikalischer Dämpfungssektor. Daher ist selbst der reduzierte K1-D-Kandidat gegenwärtig **nicht freigegeben**.

## 7. Gate-Entscheidung

```text
MDS-01 = CONDITIONAL / DEPENDS ON INTERNAL SPECTRUM
MDS-02 = OPEN / CRITICAL
MDS-03 = OPEN
MDS-04 = FIX_OR_EXCLUDE CANDIDATE
MDS-05 = FORMAL SKELETON / DEPENDS ON MD-2S
K1-D  = NOT RELEASED
K1-E  = NOT ADMISSIBLE
```

## 8. Nächster zulässiger Schritt

1. MD-2S-Wirkung und Hintergrund vollständig einfrieren.
2. Warped Volume `V_W` reproduzieren und normieren.
3. Internen Fluktuationsoperator samt Randbedingungen definieren.
4. Niedrigstes zulässiges Eigenwertspektrum berechnen.
5. `m=√λ₁/R_χ` als physikalische Brücke prüfen.
6. Separat die dimensionslose Herkunft von `ω_c` ableiten oder `ω_c` als festen effektiven Parameter deklarieren.

Ein Fit oder Proxywert darf keinen dieser Schritte ersetzen.
