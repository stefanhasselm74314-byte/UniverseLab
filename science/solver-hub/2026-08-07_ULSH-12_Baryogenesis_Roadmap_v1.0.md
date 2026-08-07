# ULSH-12 · Baryogenesis Transport Solver Roadmap v1.0

## Ziel
Eine aus dem Hyperzeit-/Flux-/Phasenübergangssektor hergeleitete Materie-Antimaterie-Asymmetrie über ein geschlossenes Nichtgleichgewichts-Transportnetz berechnen.

## Aktueller Stand
`PLANNED` mit partieller konzeptioneller Vorarbeit zu Flux-Index, Phasenübergang und Ableitungs-Kopplungen an baryonische Ströme.

## Upstream
ULSH-09 Flux und ULSH-10 Cosmology.

## Fehlende Theorie-/Vertragsarbeit
1. Konkrete CP-verletzende Quelle aus der Parentwirkung herleiten.
2. Übergangs-/Bubble-/Branen-Hintergrund und Temperaturgeschichte festlegen.
3. Reaktions-, Diffusions- und Verletzungsraten versionieren.
4. Sphaleron-/Washout-Bedingungen im gewählten Modell sauber definieren.

## Implementierungspakete
1. Spezies- und Ladungsnetz registrieren.
2. Transportgleichungen assemblern.
3. Quellen, Raten und Diffusion zeit-/raumabhängig integrieren.
4. Washout und Freeze-out berechnen.
5. Endgültiges `eta_B` beziehungsweise `n_B/s` mit Fehlerbudget exportieren.

## Kontrollen
- Null-CP-Quelle muss Nullasymmetrie liefern
- konservierte Ladungskombinationen
- bekannte toy transport networks
- Schrittweiten-/Domänenkonvergenz
- Rate-Sensitivität und dimensionaler Check

## Pflicht-Outputs
Quellprofile, Speziesdichten, Ratenmanifest, Washoutdiagnostik, finale Asymmetrie, Sensitivitäten und Provenienz.

## Freigabegate
`CLOSED_TRANSPORT_NETWORK_WITH_DERIVED_SOURCE_AND_REPRODUCIBLE_BARYON_ASYMMETRY_OUTPUT`.

## Downstream
ULSH-13 GW bei Phasenübergangsquellen sowie phänomenologische Konsistenztests.
