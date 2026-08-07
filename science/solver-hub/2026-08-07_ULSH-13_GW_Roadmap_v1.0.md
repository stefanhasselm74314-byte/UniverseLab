# ULSH-13 · Gravitational-Wave Solver Roadmap v1.0

## Ziel
Hyperzeit-spezifische Gravitationswellensignale aus einem freigegebenen stabilen Tensorsektor und klar definierten Quellen berechnen und bis zu beobachtbaren Spektren propagieren.

## Aktueller Stand
`PLANNED` mit partieller konzeptioneller Vorarbeit zu Tensorpropagation und Phasenübergangs-GW-Signaturen.

## Upstream
ULSH-05 S/V/T Perturbation, ULSH-06 Ghost/Stability, ULSH-10 Cosmology und für Phasenübergangsquellen ULSH-12 Baryogenesis.

## Fehlende Theorie-/Vertragsarbeit
1. Freigegebene Tensorwirkung und physische Tensorvariablen.
2. Dispersionsrelation, effektive Masse und Ausbreitungsgeschwindigkeit herleiten.
3. Quellklasse explizit wählen: primordial, Phasenübergang, Defekt/Relikt oder andere.
4. Transfer vom Entstehungszeitpunkt zum heutigen Detektorrahmen definieren.

## Implementierungspakete
1. Tensor-Mode-Integrator.
2. Quellterm-Module je freigegebener Quellklasse.
3. kosmologische Redshift-/Transferpipeline.
4. Spektrum `Omega_GW(f)` und Polarisationsinformationen.
5. Detektorband- und Sensitivitätsvergleich ohne Evidenzüberinterpretation.

## Kontrollen
- GR-Massless-Tensor-Grenze
- bekannte Power-Law-/Impulsquellen
- Energie-/Normierungskontrolle
- Frequenz-/Zeitschritt-Konvergenz
- unabhängige Transferrechnung

## Pflicht-Outputs
Tensorparameter, Quellmanifest, `Omega_GW(f)`, Polarisations-/Transferdaten, Detektorrahmen-Spektrum, Unsicherheiten und Provenienz.

## Freigabegate
`SOURCE_SPECIFIC_GW_SPECTRUM_WITH_STABLE_TENSOR_PROPAGATION_AND_OBSERVABLE_PROVENANCE`.

## Downstream
Direkte phänomenologische Vergleiche; keine automatische K1-E-Freigabe.
