# UniverseLab

UniverseLab ist eine mobile, browserbasierte Simulationsumgebung für zelluläre Universen, Expansion und emergente Strukturbildung.

## Status

**MVP 0.3 — experimenteller Demonstrator mit ΛCDM-Diagnostik**

Die Anwendung trennt bewusst zwischen mathematisch definierten Zellautomaten, physikalischer ΛCDM-Hintergrundentwicklung und heuristischer Visualisierung.

Der verbindliche Architektur- und Evidenzvertrag steht in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

**Nächster Meilenstein:** MVP 0.3 – numerische Härtung, reproduzierbare Zufallszustände, validierte Grenzfälle und vollständigere Exportmetadaten.

## Funktionen

- Conway Game of Life und alternative Regeln
- zufällige, symmetrische und explosive Startzustände
- physikalischer ΛCDM-Hintergrund aus der Friedmann-Gleichung
- RK4-Integration von `da/dτ = aE(a)`
- einstellbare Parameter `H₀`, `Ωₘ`, `Ωᵣ`, `ΩΛ`
- automatische Berechnung von `Ωₖ`
- Diagramme für `ln a`, `ln E(a)` und die zeitabhängigen Dichteanteile
- Live-Anzeige der Beiträge von Strahlung, Materie, Krümmung und Vakuumenergie
- heuristische Gitterexpansion als separater Modus
- lokale Speicherung des Simulationszustands und der Diagrammdaten
- Offline-Betrieb als Progressive Web App
- erweiterter CSV-Export der kosmologischen Zeitreihe

## Start

`index.html` direkt im Browser öffnen oder GitHub Pages aktivieren:

1. Repository → Settings → Pages
2. Source: `Deploy from a branch`
3. Branch: `main`, Ordner: `/ (root)`

## Implementierte Gleichungen

`E(a)² = Ωᵣa⁻⁴ + Ωₘa⁻³ + Ωₖa⁻² + ΩΛ`

`Ωₖ = 1 − Ωᵣ − Ωₘ − ΩΛ`

`da/dτ = aE(a)`, mit `τ = H₀t`

Die zeitabhängigen normierten Beiträge werden als jeweiliger Term geteilt durch `E(a)²` berechnet.

## Wissenschaftlicher Status

Die ΛCDM-Hintergrunddynamik ist physikalisch definiert und numerisch integriert. Die Zellautomaten-Dynamik ist davon getrennt. Die Abbildung des Skalenfaktors auf die sichtbare Gittergröße ist eine logarithmisch komprimierte Visualisierung und keine Herleitung kosmologischer Strukturbildung.

## Geplante Architektur

- `Cellular Physics`: Automaten und Emergenz
- `Cosmology`: Expansion, Epochen und Strukturbildung
- `Gravity`: Newton/GR/6D-Vergleich
- `Research`: Messgrößen, CSV und Reproduzierbarkeit
- `Visualization`: 2D, später WebGL/3D

Details, Abhängigkeitsregeln, Evidenzstatus und MVP-Folgeplan: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Lizenz

Noch nicht festgelegt.