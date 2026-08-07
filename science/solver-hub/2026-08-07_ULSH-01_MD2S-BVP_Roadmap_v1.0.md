# ULSH-01 · MD2S-BVP Roadmap v1.0

## Ziel
Reproduzierbare physische Lösung des kanonischen HZT-M0-S6-MD-2S-Randwertproblems für `A(r)`, `L(r)`, `phi(r)` und `A_chi(r)` einschließlich einseitigem Bulk-/Cap-Randexport.

## Aktueller Stand
`INITIAL_SCAFFOLD`. Numerische Infrastruktur, reale analytische `a_F=0`-Backendkontrollen, Seed-/Mesh-Schedule, Ressourcen- und Provenienzschicht sind vorhanden. Ein physischer `a_F=1/4`-Targetlauf ist nicht freigegeben.

## Upstream
Kein anderer Solver. Upstream ist die kanonische Parentwirkung, Konventionsregistry und der freigegebene Equation-Set-Vertrag.

## Fehlende Theorie-/Vertragsarbeit
1. Physisches Target-Equation-Set aus der kanonischen Parentwirkung einfrieren.
2. Vollständige Randbedingungen und Regularitätsbedingungen inklusive Pol-/Cap-Struktur ratifizieren.
3. Parameter-, Einheiten-, Normierungs- und Signaturbindung finalisieren.
4. Target-Pfad und einmalige Autorisierung getrennt reviewen.

## Implementierungspakete
1. Equation-Set-Callback und Resultatschema final binden.
2. Primären BVP-Backendpfad für die eingefrorene 7-Seed/35-Schedule freigabefähig machen.
3. Unabhängigen Gegenbackend-Handoff verwenden.
4. Mesh-/Cutoff-/Seed-Konvergenz und Fail-closed Klassifikation ausführen.
5. Einseitigen Bulk-/Cap-Randexport atomar und hashgebunden erzeugen.

## Kontrollen
- exakte analytische `a_F=0`-Kontrolle
- Manufactured Solutions
- Residuen auf jedem Netz
- Constraint-Residual
- Seed- und Mesh-Sensitivität
- unabhängiger Backendvergleich
- No-overwrite, Timeout, Signal und Provenienzkontrolle

## Pflicht-Outputs
`A, A_prime, L, L_prime, phi, phi_prime, A_chi, Q, Z_F`, Residuen, Solverdiagnostik, Konvergenzdaten, orientierte Normalen und alle einseitigen Randwerte.

## Freigabegate
`REPRODUCIBLE_PHYSICAL_MD2S_BACKGROUND_WITH_ONE_SIDED_BOUNDARY_EXPORT`.

Ein numerisch stabiler Lauf allein beweist weder Existenz/Eindeutigkeit im Kontinuum noch Ghostfreiheit.

## Downstream
ULSH-02 Junction, ULSH-03 Rank, ULSH-07 KK, ULSH-08 Radion, ULSH-09 Flux, ULSH-10 Cosmology.
