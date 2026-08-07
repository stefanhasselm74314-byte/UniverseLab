# ULSH-02 · Junction Analyzer Roadmap v1.0

## Ziel
Aus einem freigegebenen MD-2S-Hintergrund die beiden Junctions reproduzierbar auswerten und Pure-Tension-/Matter-Support-Bedingungen samt erforderlichem `Y_sigma` bestimmen.

## Aktueller Stand
`PROTOTYPE_EXISTS`. Die algebraische Struktur ist vorhanden; echte physische Randdaten fehlen noch.

## Upstream
ULSH-01 MD2S-BVP.

## Fehlende Theorie-/Vertragsarbeit
1. Orientierungs- und Normalenkonventionen für Bulk und Cap einfrieren.
2. Vollständige Junction-Gleichungen aus der Parentwirkung mit allen Vorzeichen und Faktoren ratifizieren.
3. Zulässige Branen-/Cap-Materiestruktur und Interpretation von `Y_sigma` explizit definieren.

## Implementierungspakete
1. Einseitige ULSH-01-Randexports direkt einlesen.
2. `A_Sigma`, `L_Sigma` und weitere Sprunggrößen berechnen.
3. Pure-Tension-Residual und erforderliche Zusatzquelle ausgeben.
4. Beide Junctions getrennt klassifizieren und gemeinsame Konsistenz prüfen.
5. Vollständige Provenienz zum zugrunde liegenden Background-Run mitführen.

## Kontrollen
- symmetrische Manufactured Junction
- Vorzeichenumkehr der orientierten Normalen
- identische Bulk/Cap-Grenze
- absichtlich inkonsistente Randdaten
- Rundungs-/Toleranzsensitivität

## Pflicht-Outputs
`A_Sigma`, `L_Sigma`, alle einzelnen Seitenbeiträge, `Y_sigma_required`, Pure-Tension-Residual, Toleranzklasse, Junction-Status und Provenienz.

## Freigabegate
`TWO_JUNCTION_RESIDUALS_AND_REQUIRED_Y_SIGMA_REPRODUCED_FROM_RELEASED_BACKGROUND`.

## Downstream
ULSH-03 Rank Audit und Teile von ULSH-10 Cosmology.
