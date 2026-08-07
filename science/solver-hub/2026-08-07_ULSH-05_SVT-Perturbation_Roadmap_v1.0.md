# ULSH-05 · S/V/T Perturbation Solver Roadmap v1.0

## Ziel
Den vollständig gauge-kontrollierten skalaren, vektoriellen und tensoriellen Perturbationssektor um einen freigegebenen 6D-Hintergrund numerisch lösen.

## Aktueller Stand
`PLANNED`. Die notwendige quadratische Wirkungsstruktur ist noch nicht vollständig geschlossen.

## Upstream
ULSH-01 MD2S-BVP und ULSH-04 Constraint Solver.

## Fehlende Theorie-/Vertragsarbeit
1. Zweite Variation `S^(2)` der kanonischen Wirkung herleiten.
2. S/V/T-Zerlegung und Harmoniken festlegen.
3. Gauge-invariante Variablen beziehungsweise eine vollständig kontrollierte Gaugewahl definieren.
4. Nichtdynamische Variablen über ULSH-04 eliminieren.
5. Physische Randbedingungen an Polen, Kappen und Branen herleiten.

## Implementierungspakete
1. S-, V- und T-Operatoren separat registrieren.
2. Gekoppelte Modengleichungen assemblern.
3. Anfangs-/Randdaten und Normalisierung binden.
4. Zeit-/Radialentwicklung mit stabilen Integratoren implementieren.
5. Transferfunktionen und Mode-Provenienz exportieren.

## Kontrollen
- GR-Tensorgrenze
- decoupled Manufactured Modes
- Gauge-Invarianztests
- Constraint-Residual nach numerischer Entwicklung
- Netz-/Zeitschritt-Konvergenz

## Pflicht-Outputs
Physische Variablen, Modenprofile, Residuen, Gauge-/Constraint-Diagnostik, Transferfunktionen, Stabilitätsmetadaten und Provenienz.

## Freigabegate
`GAUGE_CONTROLLED_QUADRATIC_PERTURBATION_SYSTEM_WITH_REPRODUCIBLE_MODE_EVOLUTION`.

## Downstream
ULSH-06 Ghost/Kinetic, ULSH-08 Radion, ULSH-10 Cosmology und ULSH-13 GW.
