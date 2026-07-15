# UniverseLab

UniverseLab ist eine mobile, browserbasierte Simulationsumgebung für zelluläre Universen, Expansion und emergente Strukturbildung.

## Status

**MVP 0.4 — experimenteller Demonstrator mit ΛCDM-Epochenanalyse**

Die Anwendung trennt bewusst zwischen mathematisch definierten Zellautomaten, physikalischer ΛCDM-Hintergrundentwicklung und heuristischer Visualisierung.

## Funktionen

- Conway Game of Life und alternative Regeln
- zufällige, symmetrische und explosive Startzustände
- physikalischer ΛCDM-Hintergrund aus der Friedmann-Gleichung
- RK4-Integration von `da/dτ = aE(a)`
- einstellbare Parameter `H₀`, `Ωₘ`, `Ωᵣ`, `ΩΛ`
- automatische Berechnung von `Ωₖ`
- Diagramme für `ln a`, `ln E(a)` und die zeitabhängigen Dichteanteile
- automatische Dominanzklassifikation: Strahlung, Materie, Krümmung oder Vakuumenergie
- analytische Gleichheitswerte für Strahlung–Materie und Materie–Vakuum
- numerische Bestimmung des Beschleunigungsbeginns aus `q(a)=0`
- Live-Anzeige des Abbremsparameters `q(a)`
- heuristische Gitterexpansion als separater Modus
- lokale Speicherung des Simulationszustands und der Diagrammdaten
- Offline-Betrieb als Progressive Web App
- CSV-Export einschließlich Epochen- und Beschleunigungsdaten

## Start

`index.html` direkt im Browser öffnen oder GitHub Pages aktivieren:

1. Repository → Settings → Pages
2. Source: `Deploy from a branch`
3. Branch: `main`, Ordner: `/ (root)`

## Implementierte Gleichungen

`E(a)² = Ωᵣa⁻⁴ + Ωₘa⁻³ + Ωₖa⁻² + ΩΛ`

`Ωₖ = 1 − Ωᵣ − Ωₘ − ΩΛ`

`da/dτ = aE(a)`, mit `τ = H₀t`

`q(a) = [2Ωᵣa⁻⁴ + Ωₘa⁻³ − 2ΩΛ] / [2E(a)²]`

Strahlung–Materie-Gleichheit:

`a_rm = Ωᵣ / Ωₘ`

Materie–Vakuum-Gleichheit:

`a_mΛ = (Ωₘ / ΩΛ)^(1/3)`

Der Beschleunigungsbeginn wird als Nullstelle von `q(a)` numerisch bestimmt.

## Wissenschaftlicher Status

Die ΛCDM-Hintergrunddynamik, die Gleichheitsbedingungen und der Abbremsparameter sind physikalisch definiert. Die Zellautomaten-Dynamik bleibt davon getrennt. Die Abbildung des Skalenfaktors auf die sichtbare Gittergröße ist eine logarithmisch komprimierte Visualisierung und keine Herleitung kosmologischer Strukturbildung.

Wichtig: Materie–Vakuum-Gleichheit und Beginn der beschleunigten Expansion sind verschiedene Ereignisse. Der Beschleunigungsbeginn folgt aus `ρ + 3p = 0`, nicht aus bloßer Dichtegleichheit.

## Geplante Architektur

- `Cellular Physics`: Automaten und Emergenz
- `Cosmology`: Expansion, Epochen und Strukturbildung
- `Gravity`: Newton/GR/6D-Vergleich
- `Research`: Messgrößen, CSV und Reproduzierbarkeit
- `Visualization`: 2D, später WebGL/3D

## Lizenz

Noch nicht festgelegt.