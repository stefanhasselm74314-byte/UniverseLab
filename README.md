# UniverseLab

UniverseLab ist eine mobile, browserbasierte Simulationsumgebung für zelluläre Universen, kosmologische Expansion und emergente Strukturbildung.

## Status

**MVP 0.5 — numerisch gehärteter ΛCDM-Kern, Browser-Anbindung in Arbeit**

Die Anwendung trennt bewusst zwischen mathematisch definierten Zellautomaten, physikalischer ΛCDM-Hintergrundentwicklung und heuristischer Visualisierung.

## Implementiert

- Conway Game of Life und alternative Automatenregeln
- zufällige, symmetrische und explosive Startzustände
- ΛCDM-Hintergrund aus der Friedmann-Gleichung
- Diagramme für `ln a`, `ln E(a)` und zeitabhängige Dichteanteile
- Epochen- und Beschleunigungsdiagnostik
- adaptive Dormand–Prince-RK45-Integration im DOM-freien Numerikmodul
- eingebetteter 5(4)-Fehlerschätzer mit adaptiver Schrittweite
- kontrollierter Abbruch bei nicht reellem Friedmann-Zweig
- analytische Referenztests für Strahlungs-, Materie- und de-Sitter-Grenzfälle
- Friedmann-Closure-, Übergangs- und Seed-Reproduzierbarkeitstests
- deterministischer Mulberry32-Zufallsgenerator
- automatische Tests über GitHub Actions
- lokale Speicherung, CSV-Export und Offline-Betrieb

## Numerischer Kern

`src/numerics.js` enthält die zentrale Implementierung von

- `friedmannTerms(a,p)`
- `E(a,p)`
- `fractions(a,p)`
- `deceleration(a,p)`
- `dominantComponent(a,p)`
- `equalityPoints(p)`
- `advanceAdaptive(a,Δτ,p,options)`
- `seededRandom(seed)`

Die adaptive Integration akzeptiert einen Teilschritt nur, wenn der eingebettete lokale Fehler die kombinierte absolute und relative Toleranz erfüllt.

## Tests

```bash
npm test
```

Die Tests vergleichen die Numerik gegen analytisch lösbare FLRW-Grenzfälle. Ein bestandener Test bestätigt die korrekte Implementierung des ΛCDM-Hintergrundmodells, nicht die physikalische Kopplung des Zellautomaten und nicht die 6D-Hyperzeit-Hypothese.

## Browser-Anbindung

Der gegenwärtige Browser-Client in `index.html` verwendet noch die ältere monolithische Integrationsroutine. Die geprüfte RK45-Engine ist deshalb noch nicht als aktive Laufzeitquelle freigegeben. Die Verdrahtung erfolgt erst, wenn `index.html` auf ES-Module umgestellt ist und die mobilen Speicher-, Diagramm- und Offline-Pfade gemeinsam regressionsgeprüft wurden.

## Implementierte Gleichungen

`E(a)² = Ωᵣa⁻⁴ + Ωₘa⁻³ + Ωₖa⁻² + ΩΛ`

`Ωₖ = 1 − Ωᵣ − Ωₘ − ΩΛ`

`da/dτ = aE(a)`, mit `τ = H₀t`

`q(a) = Ωᵣ(a) + ½Ωₘ(a) − ΩΛ(a)`

## Wissenschaftlicher Status

Die homogene ΛCDM-Hintergrunddynamik ist physikalisch definiert. Die Zellautomaten-Dynamik bleibt davon getrennt. Die Abbildung des Skalenfaktors auf die sichtbare Gittergröße ist eine logarithmisch komprimierte Visualisierung und keine Herleitung kosmologischer Strukturbildung.

## Start

`index.html` direkt im Browser öffnen oder GitHub Pages aktivieren:

1. Repository → Settings → Pages
2. Source: `Deploy from a branch`
3. Branch: `main`, Ordner: `/ (root)`

## Lizenz

Noch nicht festgelegt.
