# UniverseLab

UniverseLab ist eine mobile, browserbasierte Simulationsumgebung für zelluläre Universen, ΛCDM-Hintergrundentwicklung und lineare Strukturbildung.

## Status

**MVP 0.5 — experimenteller Demonstrator mit linearer Wachstumsdiagnostik**

Die Anwendung trennt bewusst zwischen mathematisch definierten Zellautomaten, physikalischer ΛCDM-Hintergrundentwicklung, linearer Materieperturbation und heuristischer Visualisierung.

## Funktionen

- Conway Game of Life und alternative Regeln
- physikalischer ΛCDM-Hintergrund aus der Friedmann-Gleichung
- RK4-Integration von `da/dτ = aE(a)`
- einstellbare Parameter `H₀`, `Ωₘ`, `Ωᵣ`, `ΩΛ`
- automatische Berechnung von `Ωₖ`
- Diagramme für `ln a`, `ln E(a)` und die zeitabhängigen Dichteanteile
- Dominanzklassifikation und kosmologische Gleichheitszeitpunkte
- numerische Bestimmung des Beschleunigungsbeginns aus `q(a)=0`
- lineare Wachstumsfunktion `D(a)` mit Normierung `D(1)=1`
- Wachstumsrate `f(a)=d ln D/d ln a`
- Vergleich mit der Näherung `f≈Ωₘ(a)^0,55`
- CSV-Export einschließlich `D`, `f`, `q` und Epochenstatus
- Offline-Betrieb als Progressive Web App

## Implementierte Hintergrundgleichungen

`E(a)² = Ωᵣa⁻⁴ + Ωₘa⁻³ + Ωₖa⁻² + ΩΛ`

`Ωₖ = 1 − Ωᵣ − Ωₘ − ΩΛ`

`da/dτ = aE(a)`, mit `τ = H₀t`

`q(a) = [2Ωᵣa⁻⁴ + Ωₘa⁻³ − 2ΩΛ] / [2E(a)²]`

## Lineare Strukturbildung

Mit `x = ln a` wird die skalenunabhängige GR-Wachstumsgleichung integriert:

`d²D/dx² + [2 + d ln H/dx] dD/dx − (3/2)Ωₘ(a)D = 0`

Die Anfangsbedingungen im frühen materiedominierten Regime lauten näherungsweise:

`D(a_i)=a_i`,

`dD/d ln a|_(a_i)=D(a_i)`.

Anschließend wird auf `D(1)=1` normiert. Die Wachstumsrate ist

`f(a)=d ln D/d ln a`.

Zum Vergleich zeigt die App die häufig verwendete ΛCDM-Näherung

`f(a)≈Ωₘ(a)^γ`, mit `γ≈0,55`.

## Gültigkeitsbereich

Die Wachstumsrechnung ist **konditional** gültig für:

- lineare, subhorizontale Materieperturbationen,
- drucklose Materie,
- allgemeine Relativität,
- skalenunabhängiges Wachstum,
- homogenen ΛCDM-Hintergrund.

Nicht enthalten sind Strahlungsperturbationen, Neutrinofreiströmung, baryonische Akustik, nichtlineares Wachstum, baryonische Rückkopplung, effektive modifizierte Gravitation oder eine hergeleitete 6D-Hyperzeit-Kopplung.

Die Zellautomaten-Dynamik bleibt von der kosmologischen Wachstumsrechnung getrennt. Die Abbildung des Skalenfaktors auf die sichtbare Gittergröße ist nur eine logarithmisch komprimierte Visualisierung.

## Start

`index.html` direkt im Browser öffnen oder GitHub Pages aktivieren:

1. Repository → Settings → Pages
2. Source: `Deploy from a branch`
3. Branch: `main`, Ordner: `/ (root)`

## Lizenz

Noch nicht festgelegt.
