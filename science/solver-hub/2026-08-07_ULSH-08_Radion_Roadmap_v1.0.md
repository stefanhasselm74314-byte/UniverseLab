# ULSH-08 · Radion Stability Solver Roadmap v1.0

## Ziel
Den physikalischen Radion-/Skalarmodensektor bestimmen, stabilisierte schwere Moden von ausgeschlossenen leichten Varianten trennen und Masse, Normierung sowie Materiekopplung kontrolliert ausgeben.

## Aktueller Stand
`PLANNED`. Der leichte ungescreente Radionzweig ist blockiert; ein schwerer stabilisierter Radion bleibt als kontrollierter Sektor relevant.

## Upstream
ULSH-01 MD2S-BVP, ULSH-04 Constraint und ULSH-05 S/V/T Perturbation.

## Fehlende Theorie-/Vertragsarbeit
1. Kanonische physische Radionvariable nach Constraint-Elimination definieren.
2. Effektiven skalaren Operator beziehungsweise das Radionpotential herleiten.
3. Normierung und Kopplung an 4D-Materie bestimmen.
4. Screening- oder Entkopplungsannahmen explizit ausschließen oder herleiten.

## Implementierungspakete
1. Skalarmodenoperator auf dem freigegebenen Hintergrund assemblern.
2. Eigenmassen und Profile bestimmen.
3. Normierung und Überlappung mit Materiequellen berechnen.
4. Stabilität und Low-Energy-Decoupling testen.
5. ausgeschlossene leichte Zweige als separate No-Go-Klasse erhalten.

## Kontrollen
- schwere entkoppelte Manufactured Mode
- Null-/Fast-Null-Masse
- Kopplungsnormalisierung
- Hintergrund-/Mesh-Sensitivität

## Pflicht-Outputs
Radionmasse(n), Modenprofile, Normierung, Materiekopplung, Stabilitätsklasse, Ausschlussgrund falls relevant und Provenienz.

## Freigabegate
`STABILIZED_HEAVY_RADION_OR_EXPLICIT_EXCLUSION_WITH_COUPLING_AND_MODE_NORMALIZATION`.

## Downstream
ULSH-10 Cosmology und ULSH-14 MOND/RAR.
