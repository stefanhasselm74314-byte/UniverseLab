# UniverseLab

UniverseLab ist eine mobile, browserbasierte Simulationsumgebung für zelluläre Universen, kosmologische Expansion und emergente Strukturbildung.

## Status

**MVP 0.5.1 — modularer Browser-Client mit aktiver adaptiver RK45-Integration**

Die Anwendung trennt bewusst zwischen mathematisch definierten Zellautomaten, physikalischer ΛCDM-Hintergrundentwicklung und heuristischer Visualisierung.

## Implementiert

- Conway Game of Life und alternative Automatenregeln
- zufällige, symmetrische und explosive Startzustände
- reproduzierbare Startzustände über einen deterministischen Seed
- ΛCDM-Hintergrund aus der Friedmann-Gleichung
- adaptive Dormand–Prince-RK45-Integration als einzige kosmologische Laufzeitquelle
- eingebetteter 5(4)-Fehlerschätzer mit adaptiver Schrittweite
- kontrollierter Abbruch bei nicht reellem Friedmann-Zweig
- Diagramme für `ln a`, `ln E(a)` und zeitabhängige Dichteanteile
- Epochen-, Closure- und Beschleunigungsdiagnostik
- Speicherung von Zellautomat, Kosmologie, Seed und Diagrammdaten
- CSV-Export mit `q(a)`, Closure-Fehler und RK45-Schrittstatistik
- Offline-Betrieb als Progressive Web App
- automatische analytische Referenztests über GitHub Actions

## Modulstruktur

```text
index.html
src/
  app.js
  cellular.js
  cosmology-controller.js
  numerics.js
  chart.js
  storage.js
```

`src/numerics.js` ist die einzige Quelle für Friedmann-Terme, normierte Beiträge, Verzögerungsparameter, Epochenpunkte und RK45-Integration. `index.html` enthält keine eigene Integrationsroutine mehr.

## Numerischer Kern

- `friedmannTerms(a,p)`
- `E(a,p)`
- `fractions(a,p)`
- `deceleration(a,p)`
- `dominantComponent(a,p)`
- `equalityPoints(p)`
- `advanceAdaptive(a,Δτ,p,options)`
- `seededRandom(seed)`

Ein Teilschritt wird nur akzeptiert, wenn der eingebettete lokale Fehler die kombinierte absolute und relative Toleranz erfüllt.

## Tests

```bash
npm test
```

Die Tests vergleichen die Numerik gegen analytisch lösbare Strahlungs-, Materie- und de-Sitter-Grenzfälle. Zusätzlich werden Closure, Übergangspunkte, Seed-Reproduzierbarkeit und die Syntax aller Browsermodule geprüft.

Ein bestandener Test bestätigt die korrekte Implementierung des ΛCDM-Hintergrundmodells. Er bestätigt weder eine physikalische Zellautomat–Kosmologie-Kopplung noch die 6D-Hyperzeit-Hypothese.

## Start

Die modulare Anwendung muss über HTTP(S) ausgeliefert werden.

### GitHub Pages

1. Repository → Settings → Pages
2. Source: `Deploy from a branch`
3. Branch: Zielbranch beziehungsweise nach dem Merge `main`, Ordner `/ (root)`

### Lokaler Test

```bash
python -m http.server 8000
```

Danach im Browser `http://localhost:8000` öffnen. Direktes Öffnen von `index.html` über `file://` wird wegen ES-Modul- und Service-Worker-Regeln nicht unterstützt.

## Implementierte Gleichungen

`E(a)² = Ωᵣa⁻⁴ + Ωₘa⁻³ + Ωₖa⁻² + ΩΛ`

`Ωₖ = 1 − Ωᵣ − Ωₘ − ΩΛ`

`da/dτ = aE(a)`, mit `τ = H₀t`

`q(a) = Ωᵣ(a) + ½Ωₘ(a) − ΩΛ(a)`

## Wissenschaftlicher Status

Die homogene ΛCDM-Hintergrunddynamik ist physikalisch definiert und numerisch getestet. Die Zellautomaten-Dynamik bleibt davon getrennt. Die Abbildung des Skalenfaktors auf die sichtbare Gittergröße ist eine logarithmisch komprimierte Visualisierung und keine Herleitung kosmologischer Strukturbildung.

## Lizenz

Noch nicht festgelegt.
