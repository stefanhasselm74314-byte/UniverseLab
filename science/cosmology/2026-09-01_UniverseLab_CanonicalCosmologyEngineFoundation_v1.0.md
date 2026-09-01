# UniverseLab Canonical Cosmology Engine v1.0 · Implementierungsrevision 1.0.1

**Datum:** 2026-09-01  
**Klassifikation:** numerische Referenzinfrastruktur; keine HZT-Physikevidenz  
**Foundation:** gemergter PR #196  
**Aktuelle Härtung:** PR #201 auf Basis `67c92e2644cee1f2c3a5526cd914f81a3b40a7b8`  
**API-Version:** `1.0.0`  
**Implementierungsrevision:** `1.0.1`  
**Physical gate effect:** `NONE`

## 1. Zweck

Der gemeinsame browser- und Node-fähige Rechenkern ist die einzige Referenzimplementierung für die kosmologischen Grundrechnungen von Validation, Observatory, Compare und – nach Review von PR #201 – Emergence. Die stabile API-Version bleibt `1.0.0`; Revision `1.0.1` korrigiert ausschließlich den konstruktiven Endpunkt des Growth-RK4-Solvers.

Die Konsolidierung bedeutet nicht, dass eine Modellimplementierung aus dem 6D-Parentsektor hergeleitet oder empirisch bestätigt ist. Sie reduziert Rechendrift zwischen Benutzeroberflächen.

## 2. Kernresultate

### Hintergrund

Für ΛCDM:

`E(a)^2 = Ω_r a^-4 + Ω_m a^-3 + Ω_k a^-2 + Ω_DE`

Für konstantes `w`:

`E(a)^2 = Ω_r a^-4 + Ω_m a^-3 + Ω_k a^-2 + Ω_DE a^[-3(1+w)]`

mit

`Ω_k = 1 - Ω_r - Ω_m - Ω_DE`.

Der Engine-Vertrag verbietet numerische Floors für negative Hintergrundwerte:

`E^2(z) <= 0 -> INVALID_BACKGROUND_DOMAIN`.

Für die effektive Brücke gilt zusätzlich:

`1 + Δ(a) <= 0 -> INVALID_BRIDGE_DOMAIN`.

Die öffentliche Redshift-Domäne bleibt strikt

`z >= 0`.

Eine negative Toleranzzone wurde durch die Endpunkthärtung ausdrücklich nicht eingeführt.

### Distanzen

`D_C = (c/H0) ∫_0^z dz'/E(z')`

und anschließend

- `Ω_k > 0`: `D_M = D_H/sqrt(Ω_k) sinh[sqrt(Ω_k) D_C/D_H]`
- `Ω_k = 0`: `D_M = D_C`
- `Ω_k < 0`: `D_M = D_H/sqrt(|Ω_k|) sin[sqrt(|Ω_k|) D_C/D_H]`

sowie

`D_L=(1+z)D_M`, `D_A=D_M/(1+z)`.

### Wachstum

Für ΛCDM und konstantes `w` wird die lineare GR-Referenzgleichung gelöst:

`D'' + [2 + d ln H/d ln a]D' - (3/2)Ω_m(a)D = 0`,

mit Ableitungen nach `x=ln a`, wachsendem Materiemodus als Anfangsbedingung und Normierung `D(1)=1`.

Für das effektive Bridge-Modell existiert keine freigegebene Perturbationsabbildung:

`UNRELEASED_GROWTH_MAP`.

## 3. Endpunkthärtung 1.0.1

### 3.1 Gefundener Gegenfall

Ein realer Chromium-Test lud einen historischen, physikalisch gültigen Parametersatz:

`H0=70`, `Ω_m=0.3`, `Ω_r=0.000092`, `Ω_Λ=0.699908`.

Der frühere Solver verwendete eine konstante Schrittweite

`h=(0-x_i)/N`

und aktualisierte wiederholt

`x <- x+h`.

Durch kumulierte Gleitkommarundung lag der letzte RK4-Stützpunkt minimal oberhalb von null. Dann war

`z=exp(-x)-1 < 0`

um ungefähr Maschinenpräzision. Der strikte Engine-Vertrag blockierte dies korrekt mit `NEGATIVE_REDSHIFT`; der Fehler lag in der nicht konstruktiv gepinnten Integrationsabzisse.

### 3.2 Korrektur

Für jeden Schritt wird nun ein Zielpunkt `nextX` gebildet. Im letzten Schritt gilt exakt

`nextX=0`,

und die lokale Schrittweite lautet

`h=nextX-x`.

Der vierte RK4-Stützpunkt wird bei `nextX` ausgewertet; die letzte gespeicherte Zeile besitzt konstruktiv

`x=0`, `a=1`.

Die Physikgleichung, Anfangsbedingungen, Anzahl der Standardschritte und Normierung bleiben unverändert. Die Korrektur ist daher eine numerische Endpunkthärtung, keine Modelländerung.

### 3.3 Regressionsanker

Für den Standardreferenzsatz bleibt

`D(z=1)=0.6068047406056`

innerhalb der bisherigen Toleranzen unverändert.

Für den nichtstandardmäßigen Gegenfall wird unabhängig geprüft:

`D(z=1)=0.6118580969986`,

mit exakt

`(x_end,a_end)=(0,1)`.

## 4. Gültigkeitsbereich

Die Growth-Lösung gilt für lineare, drucklose Materieperturbationen in GR auf einem glatten ΛCDM- beziehungsweise konstanten-w-Hintergrund. Nicht enthalten sind:

- Strahlungsperturbationen,
- massive-Neutrino-Skalenabhängigkeit,
- nichtlineares Wachstum,
- baryonisches Feedback,
- modifizierte Poisson-, Slip- oder Lensingfunktionen,
- eine HZT-spezifische Growth-Forward-Map.

## 5. QA

Der Node-Validator prüft:

- API-Version und Implementierungsrevision,
- analytische Grenzfälle,
- Krümmungsgeometrie,
- Etherington-Reziprozität,
- ungültige Hintergrund- und Bridge-Domänen,
- die `βτ I_B`-Degeneration,
- ΛCDM-Referenzwerte,
- den Einstein-de-Sitter-Grenzfall,
- exakte Growth-Endpunkte für Standard- und nichtstandardmäßige Anfangsepochen,
- die Bridge-Growth-Firewall.

Ein unabhängiger Python-Test rekonstruiert Distanzen und beide Growth-Fälle getrennt und vergleicht sie mit den Node-Ausgaben.

## 6. Migrationsstatus

Bereits an den gemeinsamen Kern gebunden sind:

1. Validation Console,
2. Observatory,
3. Compare SAFE,
4. die konsolidierten Vergleichsrouten.

`emergence.html` befindet sich in PR #201 im Review. Der dortige Zellautomat bleibt dynamisch vom Kosmologiekanal getrennt.

## 7. Nicht enthalten

- kein Likelihood-Fit,
- keine Parent-Herleitung,
- keine physische Background- oder Response-Rank-Ausführung,
- keine Ghostfreiheits- oder Stabilitätsaussage,
- keine K1-D-/K1-E-Hochstufung.

`korrekte Numerik ≠ physikalische Identifikation ≠ empirische Evidenz`.
