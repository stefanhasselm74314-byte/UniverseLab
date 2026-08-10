# ULSH Master Build Order v1.0

## Zweck

Dieses Dokument übersetzt die 14 kanonischen Solver-Roadmaps in eine gemeinsame Arbeitsreihenfolge. Es legt fest, welche Arbeitspakete auf dem kritischen Pfad liegen, welche theoretischen Vorarbeiten parallel zulässig sind und welche Module bis zur Freigabe ihrer Upstream-Gates physisch blockiert bleiben.

**Keine Aussage dieses Dokuments ist eine Solverfreigabe.**

- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical evidence effect = NONE`
- Abschluss eines Work Packages ≠ physische Freigabe
- Control PASS ≠ physikalische Identifikation
- Downstream-Ausführung erfordert ein separat freigegebenes Upstream-Gate

## Kritische Pfade

### CP-A · Identifizierbarkeit und Daten

`ULSH-01 Background → ULSH-02 Junction → ULSH-03 Rank → ULSH-10 Cosmology → ULSH-11 Likelihood`

Dieser Pfad kontrolliert, ob überhaupt eine physisch interpretierbare Forward Map bis zu Daten und Likelihood entstehen kann.

### CP-B · Dynamik und Stabilität

`ULSH-01 Background → ULSH-04 Constraint → ULSH-05 Perturbation → ULSH-06 Ghost/Stability → ULSH-10 Cosmology / ULSH-13 GW`

Dieser Pfad verhindert, dass numerisch stabile, aber dynamisch unphysikalische Lösungen als belastbar behandelt werden.

### CP-C · Interne Moden und Flux

`ULSH-01 Background → ULSH-07 KK / ULSH-09 Flux → ULSH-10 Cosmology → ULSH-12 Baryogenesis → ULSH-13 GW`

### CP-D · Quasistatischer / MOND-Pfad

`ULSH-01 Background → ULSH-04 Constraint / ULSH-08 Radion → ULSH-10 Cosmology → ULSH-14 MOND/RAR`

## Primärer Arbeitsfokus

### ULSH-01 · MD2S-BVP

**Status im Masterplan:** `ACTIVE_CRITICAL_PATH`

1. Targetgleichungs- und Randbedingungsvertrag aus dem kanonischen M1 schließen.
2. Physische BVP-Transaktion gegen den eingefrorenen Target-Payload freigabefähig machen.
3. Unabhängige Backend-Gegenprüfung sowie Mesh-/Residual-Konvergenz ausführen.
4. Einseitigen Bulk/Cap-Randexport samt Provenienz einfrieren.

**Release-Gate:** `REPRODUCIBLE_PHYSICAL_MD2S_BACKGROUND_WITH_ONE_SIDED_BOUNDARY_EXPORT`.

Solange dieses Gate nicht separat freigegeben ist, bleiben sämtliche physische Downstream-Ausführungen blockiert.

## Zulässige parallele Vorarbeiten

Diese Arbeiten dürfen die Wartezeit auf ULSH-01 nutzen, erzeugen aber keine physische Evidenz.

### Lane P1 · Constraint-Theorie

`ULSH-04-WP1`: ADM-/Hamilton-Zerlegung, kanonische Variablen und Momentumstruktur vorbereiten.

Erlaubt: symbolische Herleitung, Konventionsregister, bekannte GR-/Maxwell-Kontrollsysteme.

Nicht erlaubt: physischer DOF-Claim auf einem noch nicht freigegebenen Background.

### Lane P2 · Interne Moden / Flux

- `ULSH-07-WP1`: Sturm-Liouville-Operatorstruktur vorbereiten.
- `ULSH-09-WP1`: globalen Flux-/Quantisierungs- und Topologievertrag schließen.

Erlaubt: Manufactured Tests und analytische Grenzfälle.

Nicht erlaubt: physisches KK-/Fluxspektrum ohne freigegebenen Background.

### Lane P3 · spätere Phänomenologie

- `ULSH-12-WP1`: mögliche CP-verletzende Quelle aus Parent-/Fluxdynamik herleiten.
- `ULSH-14-WP1`: quasistatischen Schwachfeldgrenzfall der Parentwirkung vorbereiten.

Nicht erlaubt: Fit an Baryonenasymmetrie beziehungsweise RAR als physische Evidenz.

## Solver-spezifische Work Packages

### ULSH-02 · Junction
1. Randexport-/Normalenvertrag verifizieren.
2. Beide Junction-Gleichungen und Pure-Tension-Residual auswerten.
3. `Y_sigma_required` und Orientierungs-/Vorzeichenkontrollen reproduzieren.
4. Zwei-Junction-Konsistenzurteil mit Provenienz einfrieren.

### ULSH-03 · Rank Audit
1. Vollständige linearisierte Randantwort ableiten.
2. Parameterperturbationen, Antwortmatrix und Skalierungen einfrieren.
3. SVD/RRQR/Rang-/Konditionskontrollen über mehrere Diskretisierungen durchführen.
4. Diskreten Rang strikt von Kontinuumsinvertierbarkeit trennen.

### ULSH-04 · Constraint
1. ADM-/Hamilton-Zerlegung und kanonische Variablen.
2. Primär-/Sekundärzwänge und Poisson-Algebra.
3. First-/Second-Class-Klassifikation und Gauge-Generatoren.
4. Physischer Freiheitsgrad-Count auf freigegebenem Background.

### ULSH-05 · S/V/T Perturbation
1. Vollständige quadratische Wirkung `S^(2)`.
2. Gauge-invariante S/V/T-Variablen und Randbedingungen.
3. Constraint-Elimination und gekoppelte Modengleichungen.
4. GR-Kontrollgrenzen, Auflösung und Residuen.

### ULSH-06 · Ghost / Kinetic
1. Physische kinetische Matrix nach Constraint-Elimination.
2. Schur-Komplement und kanonische Normierung.
3. Ghost-, Gradient- und Tachyonkriterien.
4. Basis-/Eigenwert-/Konditionsrobustheit.

### ULSH-07 · KK
1. Sturm-Liouville-Operator.
2. Endpunktbedingungen, Maß und Normierung.
3. Eigenwert-/Eigenmodenlöser mit Orthogonalitätskontrollen.
4. Gitter-/Basisverfeinerung und bekannte Grenzfälle.

### ULSH-08 · Radion
1. Kanonische physische Radion-/Skalarmode.
2. Constraint-bereinigter Massenoperator und Materiekopplung.
3. Normalisierung und Stabilitätsdiagnostik.
4. Schweren stabilisierten Radion bestätigen oder Zweig explizit ausschließen.

### ULSH-09 · Flux
1. Globaler Quantisierungs-/Topologievertrag.
2. Regularitäts- und Randdaten.
3. Fluxmoden-/Metastabilitätsoperator.
4. Quantisierung, Regularität und Mode-Diagnostik.

### ULSH-10 · Cosmology / Forward Map
1. Ratifizierte `6D → 4D`-Parameterabbildung.
2. Hintergrund-, Wachstum- und Lensing-Gleichungen.
3. Forward Map zu `H(z)`, Distanzen, `fσ8`, `μ`, `Σ`, `η`.
4. Kontrollgrenzen und K1-D-Identifizierbarkeitsvoraussetzungen.

### ULSH-11 · Likelihood
1. Daten-, Kovarianz-, Prior- und Nuisanceverträge.
2. Likelihood-Schnittstellen für freigegebene Observablen.
3. Synthetische Coverage-/Calibration-/Recovery-Tests.
4. Separate K1-E-Zulässigkeitsprüfung.

### ULSH-12 · Baryogenesis
1. Abgeleitete CP-verletzende Quelle.
2. Nichtgleichgewichts-Übergang sowie Reaktions-/Diffusionsraten.
3. Gekoppeltes Transportnetz.
4. Sensitivitäts- und Robustheitsprüfung der Baryonasymmetrie.

### ULSH-13 · GW
1. Quellklasse und Tensorsektor binden.
2. Propagations-/Quellengleichungen und Transferfunktionen.
3. Spektrum bis zum Beobachterframe.
4. Stabilitäts-, Quellen- und Detektorband-Sensitivität.

### ULSH-14 · MOND/RAR
1. Quasistatischer Schwachfeldgrenzfall aus der Parentwirkung.
2. Materiekopplung, Screening und nichtlokale Bulkantwort.
3. `a0` aus Parentparametern statt als freier Fitparameter.
4. Erst danach RAR/MOND-Observablen und Datenvergleich.

## Arbeitsregel

Jeder Solver durchläuft dieselben vier Klassen von Arbeitspaketen:

1. **Theory / Contract**
2. **Equation / Interface Freeze**
3. **Implementation & Controls**
4. **Validation & separate Release Review**

Ein Paket darf vorbereitet werden, obwohl sein Upstream noch blockiert ist. Es darf jedoch keine physische Ausführung, Freigabe oder Evidenzbehauptung erzeugen, solange das dafür notwendige Upstream-Gate nicht separat veröffentlicht wurde.
