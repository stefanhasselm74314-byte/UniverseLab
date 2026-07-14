# UniverseLab

UniverseLab ist eine mobile, browserbasierte Simulationsumgebung für zelluläre Universen, kosmologische Expansion und emergente Strukturbildung.

## Status

**MVP 0.2 — experimenteller Demonstrator mit ΛCDM-Hintergrund**

Die Anwendung trennt bewusst zwischen drei Modellschichten:

1. mathematisch exakt definierten zellulären Automaten,
2. numerisch integrierter ΛCDM-Hintergrundexpansion,
3. heuristischen Visualisierungs- und Kopplungsregeln.

## Funktionen

- Conway Game of Life und alternative Regeln
- zufällige, symmetrische und explosive Startzustände
- physikalischer ΛCDM-Modus mit numerischer Friedmann-Integration
- einstellbare Parameter H₀, Ωₘ, Ωᵣ und ΩΛ
- automatisch berechnete Krümmungsdichte Ωₖ = 1 − Ωᵣ − Ωₘ − ΩΛ
- optionaler heuristischer Expansionsmodus
- lokale Speicherung des Simulationszustands
- Offline-Betrieb als Progressive Web App
- CSV-Export inklusive a, E(a) und τ = H₀t

## Dynamik des ΛCDM-Modus

Die dimensionslose Hubble-Funktion lautet

```text
E(a)² = Ωᵣ a⁻⁴ + Ωₘ a⁻³ + Ωₖ a⁻² + ΩΛ
```

mit

```text
E(a) = H(a)/H₀
Ωₖ = 1 − Ωᵣ − Ωₘ − ΩΛ
τ = H₀ t
da/dτ = a E(a)
```

Die Differentialgleichung wird mit einem Runge-Kutta-Verfahren vierter Ordnung integriert.

## Wissenschaftliche Grenze

Die Hintergrundexpansion ist eine numerische Lösung der homogenen Friedmann-Gleichung für die gewählten Dichteparameter. Die Übertragung des Skalenfaktors auf die sichtbare Gittergröße ist dagegen logarithmisch komprimiert und rein illustrativ. Der Zellautomat beschreibt weder relativistische Materiefelder noch lineare oder nichtlineare kosmologische Störungstheorie.

Ein visueller Fit oder eine stabile Zellstruktur ist daher keine Bestätigung von ΛCDM, einer 6D-Theorie oder der Hyperzeit-Hypothese.

## Start

`index.html` direkt im Browser öffnen oder GitHub Pages aktivieren:

1. Repository → Settings → Pages
2. Source: `Deploy from a branch`
3. Branch: `main`, Ordner: `/ (root)`

## Geplante Architektur

- `Cellular Physics`: Automaten und Emergenz
- `Cosmology`: Hintergrund und später Störungstheorie
- `Gravity`: Newton/GR/6D-Vergleich
- `Research`: Messgrößen, CSV und Reproduzierbarkeit
- `Visualization`: 2D, später WebGL/3D

## Lizenz

Noch nicht festgelegt.
