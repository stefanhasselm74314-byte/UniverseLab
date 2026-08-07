# UniverseLab Solver Hub (ULSH) v1.0

## Zweck

Der UniverseLab Solver Hub ist die gemeinsame numerische Infrastruktur für Hyperzeit/HPVS. Er ersetzt keine physikalische Herleitung. Jeder Solver muss seine Annahmen, Konventionen, Residuen, Toleranzen und Provenienz explizit exportieren.

## Governance

- K1-D = NOT RELEASED
- K1-E = NOT ADMISSIBLE
- numerische Stabilität != Ghostfreiheit
- technische Ausführbarkeit != physikalische Identifikation
- guter Fit != Theoriebestätigung
- Branch-Transfer nur nach vollständiger Neuberechnung

## Kanonischer erster Solver

`HZT-M0-S6_MD-2S_Background_BVP_Solver_v1.0`

Ziel: Rekonstruktion beziehungsweise Wiedergewinnung des MD-2S-Hintergrund-Randwertproblems für

- A(r)
- L(r)
- phi(r)
- A_chi(r)

und Export der einseitigen Kappendaten für SCI-001/SCI-002 v0.2.

## Solver-Vertrag

Jeder Solver erhält mindestens:

1. Parametervektor
2. Konventions-ID
3. Einheiten/Normierung
4. numerische Toleranzen
5. Provenienz

und erzeugt mindestens:

1. Lösung
2. Residuen
3. Randexport
4. Solverdiagnostik
5. Provenienz/Hashes
6. expliziten Status

## MD-2S Pflicht-Outputs

An r = r_sigma müssen mindestens ausgegeben werden:

- A'_bulk, A'_cap
- L_bulk, L_cap
- L'_bulk, L'_cap
- phi'_bulk, phi'_cap
- A_chi_bulk, A_chi_cap
- Q_bulk, Q_cap
- Z_F_bulk, Z_F_cap
- orientierte Normalen n^r_bulk, n^r_cap

Daraus folgen

A_Sigma = sum_s n_s^r A'_s

L_Sigma = sum_s n_s^r L'_s/L_s

Y_sigma_required = M6^4 (L_Sigma - A_Sigma)

und das Pure-Tension-Gate A_Sigma = L_Sigma.

## Module

- MD2S-BVP
- MD2S-JUNCTION
- MD2S-RANK / B1.4O
- CONSTRAINT
- PERTURBATION
- GHOST
- KK
- RADION
- FLUX
- COSMO
- LIKELIHOOD
- BARYO
- GW
- MOND/RAR

Nur die ersten drei Blöcke besitzen derzeit konkrete Vorarbeiten. Die übrigen Einträge sind Architekturziele und keine bereits vorhandenen Solver.

## Nächster Freigabeschritt

Der nächste harte Gate ist die reproduzierbare MD-2S-Hintergrundlösung mit vollständigem einseitigem Randexport. Erst danach sind das Zwei-Junction-Urteil und der B1.4O-Rankaudit numerisch ausführbar.
