# ULSH-14 · MOND / RAR Diagnostic Solver Roadmap v1.0

## Ziel
Eine schwachfeldige/quasistatische Beschleunigungsrelation aus der Hyperzeit-Parentwirkung ableiten und erst danach gegen RAR/MOND-Daten testen; `a0` darf dabei kein freier Fitknopf sein.

## Aktueller Stand
`PLANNED` mit partieller konzeptioneller Vorarbeit. Der frühere leichte-Radion-Weg ist blockiert; eine gültige Herleitung muss über einen anderen freigegebenen Mechanismus erfolgen.

## Upstream
ULSH-04 Constraint, ULSH-08 Radion und ULSH-10 Cosmology/Forward Map.

## Fehlende Theorie-/Vertragsarbeit
1. Schwachfeld- und quasistatischen Grenzfall der Parentwirkung sauber herleiten.
2. Physisches 4D-Potential und Materiekopplung bestimmen.
3. Screening- oder nichtlokale Bulkantwort explizit behandeln.
4. `a0` aus Parentparametern und Normalisierung ableiten.
5. Interpolations-/Beschleunigungsgesetz vor jedem Datenfit einfrieren.

## Implementierungspakete
1. Baryonische Quellen in das freigegebene effektive Feldsystem einspeisen.
2. Potential-/Beschleunigungsprofil numerisch lösen.
3. `g_bar -> g_obs`-Relation und asymptotische Grenzfälle ausgeben.
4. Galaxiengeometrie-/Massenmodell-Schnittstelle definieren.
5. Erst nach Theorie-Freeze RAR-Datensatz und Likelihood anbinden.

## Kontrollen
- Newton-Grenze bei hoher Beschleunigung
- tiefe Beschleunigungsasymptotik
- Dimensionscheck von `a0`
- Punktmasse/Kugel/Scheibe als Referenzgeometrien
- keine freie nachträgliche Interpolationsfunktion

## Pflicht-Outputs
abgeleitetes `a0`, effektive Feldgleichung, Beschleunigungsprofile, RAR-Kurve, asymptotische Tests, Source-Provenienz und erst separat Datenfitdiagnostik.

## Freigabegate
`DERIVED_ACCELERATION_LAW_WITH_NONFREE_A0_AND_RAR_PREDICTION_BEFORE_DATA_FIT`.

## Downstream
RAR/MOND-Datenvergleich und Vergleich mit alternativen Gravitationstheorien; keine automatische Theoriebestätigung.
