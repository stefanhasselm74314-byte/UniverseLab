# ULSH-07 · Kaluza-Klein Spectrum Solver Roadmap v1.0

## Ziel
Das physikalische KK-Eigenspektrum und die zugehörigen normalisierten Modenprofile auf einem freigegebenen 6D-Hintergrund bestimmen.

## Aktueller Stand
`PLANNED`. KK-Skalen und qualitative Erwartungen existieren, aber kein vollständig gebundener sektorabhängiger Eigenwertsolver.

## Upstream
ULSH-01 MD2S-BVP.

## Fehlende Theorie-/Vertragsarbeit
1. Sektorabhängigen linearen Sturm-Liouville-Operator herleiten.
2. Gewichtsfunktion und inneres Produkt definieren.
3. Pol-/Cap-/Branen-Randbedingungen einfrieren.
4. Nullmoden, Gauge-Moden und physische Moden sauber trennen.

## Implementierungspakete
1. Operator- und Massmatrix assemblern.
2. Sparse/generalized Eigenvalue Backend implementieren.
3. Moden sortieren, normalisieren und orthogonalisieren.
4. Cutoff-/Mesh-Sensitivität und fehlende/degenerierte Moden prüfen.
5. Kopplungsüberlappungen zu 4D-Feldern exportieren.

## Kontrollen
- analytische Intervall-/Kreis-Spektren
- bekannte Nullmode
- Degeneracy Manufactured Cases
- Orthogonalitäts- und Normierungsfehler
- Mesh-Konvergenz der niedrigsten Eigenwerte

## Pflicht-Outputs
`m_n^2`, Modenprofile, Normierungsintegrale, Orthogonalitätsmatrix, Randresiduen, Konvergenzdaten und Provenienz.

## Freigabegate
`CONVERGED_KK_EIGENSPECTRUM_WITH_NORMALIZED_MODES_AND_BOUNDARY_PROVENANCE`.

## Downstream
ULSH-10 Cosmology und ULSH-13 GW.
