# ULSH-10 · Background Cosmology / Forward-Map Solver Roadmap v1.0

## Ziel
Aus freigegebenen 6D-Parametern und einem stabilen Hintergrund eine physikalisch ratifizierte 4D-Forward-Map zu kosmologischen Observablen erzeugen.

## Aktueller Stand
`PLANNED` mit partieller konzeptioneller und Datenpipeline-Vorarbeit. Die fundamentale K1-D-Brücke ist nicht freigegeben.

## Upstream
ULSH-01 BVP, ULSH-02 Junction, ULSH-03 Rank, ULSH-05 Perturbation, ULSH-06 Ghost/Stability, ULSH-07 KK, ULSH-08 Radion und ULSH-09 Flux.

## Fehlende Theorie-/Vertragsarbeit
1. Ratifizierte 6D→4D-Reduktion und Parameterabbildung festlegen.
2. Effektive Friedmann-/Wachstums-/Lensing-Gleichungen aus dem freigegebenen Sektor herleiten.
3. Physische Anfangsbedingungen und Normierungen definieren.
4. Gültigkeitsbereich des EFT-/Low-Energy-Limits ausweisen.

## Implementierungspakete
1. Hintergrundintegration für `H(z)` und Distanzen.
2. Wachstumsgleichungen und `fσ8`.
3. Lensing-/Slip-Funktionen `mu`, `Sigma`, `eta`, `E_G`.
4. Sensitivitäts-/Jacobian-Export für Identifizierbarkeit.
5. Observablen- und Provenienzschema für ULSH-11.

## Kontrollen
- GR/ΛCDM-Low-Energy-Grenze
- dimensionslose Einheitentests
- unabhängige Integrationsmethoden
- Hintergrund-/Perturbationskonsistenz
- Parameter-Sensitivität ohne Datenfit

## Pflicht-Outputs
`H(z)`, `D_M`, `D_H`, Wachstum, `fσ8`, `mu`, `Sigma`, `eta`, `E_G`, Jacobian-/Sensitivitätsdaten, Scope und Provenienz.

## Freigabegate
`K1_D_ELIGIBLE_PHYSICAL_FORWARD_MAP_WITH_BACKGROUND_GROWTH_LENSING_OUTPUTS`.

Vor diesem Gate darf kein guter Datenfit als Evidenz für Hyperzeit interpretiert werden.

## Downstream
ULSH-11 Likelihood, ULSH-12 Baryogenesis, ULSH-13 GW und ULSH-14 MOND/RAR.
