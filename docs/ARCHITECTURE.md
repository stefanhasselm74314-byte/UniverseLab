# UniverseLab – Architektur- und Evidenzvertrag

## 1. Ziel

UniverseLab ist eine mobile, browserbasierte Forschungs- und Simulationsumgebung. Die Plattform soll zelluläre Automaten, kosmologische Hintergrundmodelle, Gravitation, Datenexport und spätere 6D-/Hyperzeit-Modelle in einer reproduzierbaren Struktur zusammenführen.

Die Architektur verhindert ausdrücklich einen Evidenzsprung von einer visuellen Simulation zu einer physikalischen Identifikation.

## 2. Verbindliche Modellschichten

### L0 – Visualisierung

Darstellung, Farbgebung, Kameralogik, logarithmische Skalierung und Animation.

**Status:** illustrativ.

L0 darf keine physikalische Aussage allein begründen.

### L1 – Diskrete Dynamik

Mathematisch definierte zelluläre Automaten, Nachbarschaften, Randbedingungen und stochastische Regeln.

**Status:** exakt innerhalb der gewählten Automatenregeln.

Ein stabiler Attraktor oder ein außergewöhnliches Muster ist keine kosmologische Beobachtung.

### L2 – Hintergrundkosmologie

Homogene Expansion mit

```text
E(a)^2 = Ω_r a^-4 + Ω_m a^-3 + Ω_k a^-2 + Ω_Λ
Ω_k = 1 - Ω_r - Ω_m - Ω_Λ
da/dτ = a E(a)
τ = H_0 t
```

**Status:** numerisch integriertes FLRW-/ΛCDM-Hintergrundmodell.

L2 enthält noch keine kosmologische Störungstheorie und keine Strukturbildung.

### L3 – Störungstheorie und Gravitation

Geplante Module für lineare Störungen, Wachstum, Potentiale, Geodäten, Linsenwirkung und Gravitationswellen.

**Status:** noch nicht implementiert.

### L4 – 6D-/Hyperzeit-Modelle

Zusätzliche Dimensionen, Branen, Bulk-Felder, KK-Moden, Radion- und Warp-Dynamik.

**Status:** Forschungsmodell; erst zulässig, wenn Wirkung, Randbedingungen, Freiheitsgrade, Stabilität und Forward Map explizit definiert sind.

### L5 – Datenvergleich und Inferenz

Likelihoods, χ², Bayes-Faktoren, Posterioren, Parameterkorrelationen und systematische Fehler.

**Status:** noch nicht implementiert.

Ein guter Fit bestätigt nicht automatisch die zugrunde liegende Theorie.

## 3. Zielstruktur

```text
UniverseLab/
├── index.html                 # schlanke App-Hülle
├── manifest.webmanifest
├── sw.js
├── src/
│   ├── app/                   # Zustand, Ereignisse, Persistenz
│   ├── cellular/              # Regeln, Gitter, Randbedingungen
│   ├── cosmology/             # FLRW-Hintergrund, Integratoren
│   ├── gravity/               # Newton, GR, später 6D
│   ├── research/              # Messgrößen, Export, Provenienz
│   ├── visualization/         # Canvas/WebGL, rein darstellend
│   └── shared/                # Einheiten, Validierung, Numerik
├── tests/
│   ├── cellular/
│   ├── cosmology/
│   └── regression/
└── docs/
    ├── ARCHITECTURE.md
    ├── MODEL_STATUS.md
    └── VALIDATION.md
```

## 4. Abhängigkeitsregel

Die Abhängigkeiten verlaufen nur in dieser Richtung:

```text
shared → cellular/cosmology/gravity/research → app → visualization
```

Die Visualisierung darf keine Modellparameter heimlich verändern. Physikalische Module dürfen nicht vom Canvas oder DOM abhängen.

## 5. Numerischer Vertrag

Jeder Integrator muss dokumentieren:

1. Differentialgleichung und unabhängige Variable,
2. Anfangsbedingungen,
3. Schrittweitenregel,
4. Abbruch- und Fehlerkriterien,
5. Gültigkeitsbereich,
6. Einheiten oder dimensionslose Normierung,
7. Referenzlösung oder Grenzfall.

Für die Hintergrundkosmologie sind mindestens zu testen:

- reine Strahlung: a(τ) ∝ τ^(1/2),
- reine Materie: a(τ) ∝ τ^(2/3),
- reine de-Sitter-Phase: a(τ) ∝ exp(τ),
- geschlossene/rekollabierende Parameterwahl,
- unphysikalische Bereiche mit E(a)^2 < 0.

## 6. Evidenzstatus

Jedes Modul und jede Ausgabe erhält einen Status:

- **bewiesen** – analytisch aus den angegebenen Annahmen hergeleitet,
- **numerisch bestätigt** – gegen Referenzlösung oder Konvergenztest geprüft,
- **konditional** – gültig unter expliziten Modellannahmen,
- **heuristisch** – illustrativ oder phänomenologisch,
- **offen** – noch nicht entschieden,
- **blockiert/falsifiziert** – mathematisch oder empirisch ausgeschlossen.

## 7. MVP-Folgeplan

### MVP 0.3 – Numerische Härtung

- adaptives oder kontrolliert unterteiltes RK4,
- Parameter- und Domänenvalidierung,
- reproduzierbarer Zufalls-Seed,
- Export von Modellversion und Parametern,
- Referenztests für Strahlung, Materie und de Sitter.

### MVP 0.4 – Modularisierung

- Auslagerung von Automaten-, Kosmologie- und Darstellungslogik,
- keine Änderung des sichtbaren Funktionsumfangs,
- Regressionstests gegen MVP 0.3.

### MVP 0.5 – Forschungsmodus

- Diagramme für a(τ), E(a), q(a) und Dichteanteile,
- Metadaten und Provenienz im Export,
- gespeicherte Szenarien mit stabilen IDs.

### MVP 1.0 – Validierter Demonstrator

- dokumentierte Testabdeckung,
- mobile PWA mit Icons und Installationsprüfung,
- klare Trennung von Modell, Numerik, Visualisierung und Inferenz,
- keine unbelegten Hyperzeit- oder 6D-Identifikationsaussagen.

## 8. Nicht-Ziele der aktuellen Version

MVP 0.2/0.3 ist kein Ersatz für:

- relativistische Feldsimulation,
- N-Körper-Kosmologie,
- Boltzmann-Code,
- nichtlineare Strukturbildung,
- Datenanalyse mit vollständiger Likelihood,
- Nachweis einer 6D- oder Hyperzeit-Theorie.
