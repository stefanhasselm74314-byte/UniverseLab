# ULSH-11 · Likelihood and Data Pipeline Roadmap v1.0

## Ziel
Freigegebene Hyperzeit-Observablen reproduzierbar gegen reale Datensätze auswerten, ohne technische Fitqualität mit theoretischer Bestätigung zu verwechseln.

## Aktueller Stand
`PLANNED` mit partieller Infrastruktur aus früheren Pantheon+/DESI/KiDS/Wachstumsarbeiten. K1-E ist nicht zulässig, solange K1-D nicht freigegeben ist.

## Upstream
ULSH-10 Cosmology / Forward Map.

## Fehlende Theorie-/Vertragsarbeit
1. Exakten Observablenvektor und Nuisanceparameter einfrieren.
2. Datensätze, Versionen, Masken und Kovarianzen versionieren.
3. Prioren und Parameterräume unabhängig vom Ergebnis festlegen.
4. K1-E-Admissibility Review nach freigegebenem K1-D durchführen.

## Implementierungspakete
1. Dataset-Loader und Covariance-Validatoren.
2. Likelihoodblöcke für SN, BAO, Wachstum und Lensing.
3. kombinierte Log-Likelihood mit nachvollziehbarer Blockzerlegung.
4. MCMC/Nested-Sampling mit reproduzierbaren Seeds und Konvergenzdiagnostik.
5. Posterior-, Prior-Robustheits- und Informationsgewinn-Exports.

## Kontrollen
- synthetische Gaussian Likelihood
- ΛCDM-Referenzfits
- Kovarianzsymmetrie/Positivität
- Prior-Sensitivität
- unabhängige Sampler-/Optimierer-Gegenchecks

## Pflicht-Outputs
Datensatzmanifest, Kovarianzhashes, Likelihoodbeiträge, Posterior-Samples, Konvergenzdiagnostik, Prioren, Evidenz nur falls zulässig, und vollständige Provenienz.

## Freigabegate
`K1_E_ADMISSIBLE_LIKELIHOOD_WITH_FROZEN_DATA_COVARIANCE_PRIORS_AND_PROVENANCE`.

## Downstream
Kein zwingender Solver. Ergebnisse fließen in HPVS K2-K7 und Modellbewertung ein.
