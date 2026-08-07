# ULSH-03 · B1.4O Rank Audit Roadmap v1.0

## Ziel
Die linearisierte Antwortstruktur des freigegebenen MD-2S-Hintergrunds numerisch analysieren: Rang, Singulärwerte, Kondition und mögliche Nullrichtungen.

## Aktueller Stand
`PREFLIGHT_DEFINED`. Die numerische Rank-/SVD-Logik ist konzeptionell und teilweise technisch vorbereitet; der physische Antwortoperator fehlt.

## Upstream
ULSH-01 MD2S-BVP und ULSH-02 Junction.

## Fehlende Theorie-/Vertragsarbeit
1. Exakte Eingangsparameter und beobachtete/gebundene Randgrößen festlegen.
2. Vollständige linearisierte Boundary-Response-Map herleiten.
3. Diskrete Rangdiagnostik klar von Kontinuumsinvertierbarkeit trennen.
4. Normierung der Spalten/Zeilen und dimensionslose Skalierung definieren.

## Implementierungspakete
1. Störung jedes zulässigen Parameters um den freigegebenen Hintergrund.
2. Antwortmatrix deterministisch aufbauen.
3. RRQR/SVD, Rangschwellen und Konditionsmaße berechnen.
4. Nullrichtungen und degenerierte Kombinationen exportieren.
5. Netz-/Schrittweitenstabilität der Rank-Klassifikation prüfen.

## Kontrollen
- Matrizen bekannten Rangs
- nahezu singuläre Manufactured Cases
- Reskalierungsinvarianz
- Schrittweiten-/Netzsensitivität
- unabhängige RRQR-gegen-SVD-Klassifikation

## Pflicht-Outputs
Antwortmatrix, Skalierungsmetadaten, Singulärwerte, numerischer Rang, Konditionszahl, Nullvektoren, Sensitivitätsbericht und Provenienz.

## Freigabegate
`REPRODUCIBLE_RESPONSE_MATRIX_WITH_RANK_SINGULAR_VALUES_CONDITIONING_AND_CONTINUUM_SCOPE`.

Ein voller diskreter Rang ist kein Beweis eines invertierbaren Kontinuumsoperators.

## Downstream
ULSH-10 Cosmology / Forward Map.
