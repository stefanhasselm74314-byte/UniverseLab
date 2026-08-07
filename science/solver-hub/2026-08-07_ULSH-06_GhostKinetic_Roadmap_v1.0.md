# ULSH-06 · Ghost / Kinetic-Matrix Audit Roadmap v1.0

## Ziel
Die physische kinetische, Gradient- und Massenstruktur nach vollständiger Constraint-Elimination bestimmen und Ghost-, Gradient- sowie Tachyon-Gates sektorspezifisch prüfen.

## Aktueller Stand
`PLANNED`. Einzelne Schur-Komplement- und Kinetikideen existieren konzeptionell, aber keine freigegebene vollständige physische Matrixpipeline.

## Upstream
ULSH-04 Constraint und ULSH-05 S/V/T Perturbation.

## Fehlende Theorie-/Vertragsarbeit
1. Physische Variablenbasis nach Constraint-Elimination einfrieren.
2. Kinetische Matrix `K_phys`, Gradientmatrix `G_phys` und Massenmatrix `M_phys` herleiten.
3. Schur-Komplement-Reduktion und Normalisierung exakt dokumentieren.
4. Hintergrundabhängige Gültigkeitsbereiche definieren.

## Implementierungspakete
1. Symbolischen/numerischen Matrixassembler bauen.
2. Symmetrie- und Dimensionsprüfungen erzwingen.
3. Eigenwerte, Hauptminoren und Kondition berechnen.
4. Gradientgeschwindigkeiten aus `K_phys^{-1} G_phys` bestimmen.
5. Tachyon-/Zeitskalenkriterien getrennt klassifizieren.

## Kontrollen
- bekannte positive/indefinite Testmatrizen
- Schur-Komplement-Manufactured Cases
- Basiswechsel-Invarianz zulässiger Signaturen
- Hochpräzisions-Gegenrechnung nahe Nullmoden

## Pflicht-Outputs
`K_phys`, `G_phys`, `M_phys`, Eigenwerte, Hauptminoren, Kondition, Modezuordnung, Scope, Toleranzen und Provenienz.

## Freigabegate
`POSITIVE_PHYSICAL_KINETIC_SECTOR_AND_ACCEPTABLE_GRADIENT_TACHYON_GATES_WITH_SCOPE`.

Numerische Stabilität eines Background-Solvers ist ausdrücklich kein Ersatz für dieses Gate.

## Downstream
ULSH-10 Cosmology und ULSH-13 GW.
