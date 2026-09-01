# UniverseLab Canonical Cosmology Engine Foundation v1.0

**Datum:** 2026-09-01  
**Klassifikation:** numerische Referenzinfrastruktur; keine HZT-Physikevidenz  
**Stacked Base:** PR #193, Head `eb5bdea01bf605fa4a3b63e2c1850622796d1efd`  
**Physical gate effect:** `NONE`

## 1. Zweck

Dieser Block führt erstmals einen einzigen, browser- und Node-fähigen Referenzkern für die kosmologischen Grundrechnungen ein. Er ändert in dieser Stufe noch keine öffentliche Rechenseite. Dadurch werden die mathematischen Verträge und adversarialen Tests vor der UI-Migration eingefroren.

Die bisher getrennten Implementierungen in `compare-safe.html`, `compare-direct.html`, `compare-app.js`, `observatory.html`, `validation.html` und `emergence.html` werden ausdrücklich noch nicht als konsolidiert bezeichnet.

## 2. Kernresultate

### Hintergrund

Für ΛCDM:

`E(a)^2 = Ω_r a^-4 + Ω_m a^-3 + Ω_k a^-2 + Ω_DE`

Für konstantes `w`:

`E(a)^2 = Ω_r a^-4 + Ω_m a^-3 + Ω_k a^-2 + Ω_DE a^[-3(1+w)]`

mit

`Ω_k = 1 - Ω_r - Ω_m - Ω_DE`.

Der Engine-Vertrag verbietet numerische Floors für negative Hintergrundwerte. Es gilt fail-closed:

`E^2(z) <= 0 -> INVALID_BACKGROUND_DOMAIN`.

Für die effektive Brücke gilt zusätzlich:

`1 + Δ(a) <= 0 -> INVALID_BRIDGE_DOMAIN`.

### Distanzen

`D_C = (c/H0) ∫_0^z dz'/E(z')`

und anschließend die krümmungskorrekte Abbildung

- `Ω_k > 0`: `D_M = D_H/sqrt(Ω_k) sinh[sqrt(Ω_k) D_C/D_H]`
- `Ω_k = 0`: `D_M = D_C`
- `Ω_k < 0`: `D_M = D_H/sqrt(|Ω_k|) sin[sqrt(|Ω_k|) D_C/D_H]`

sowie

`D_L=(1+z)D_M`, `D_A=D_M/(1+z)`.

### Wachstum

Für ΛCDM und konstantes `w` wird die lineare GR-Referenzgleichung gelöst:

`D'' + [2 + d ln H/d ln a]D' - (3/2)Ω_m(a)D = 0`,

Ableitungen nach `ln a`, normiert auf `D(1)=1`.

Für das effektive Bridge-Modell existiert keine freigegebene Perturbationsabbildung. Daher liefert der Engine-Vertrag absichtlich:

`UNRELEASED_GROWTH_MAP`.

## 3. Gültigkeitsbereich

Die Growth-Lösung gilt für lineare, drucklose Materieperturbationen in GR auf einem glatten ΛCDM- beziehungsweise konstanten-w-Hintergrund. Nicht enthalten sind:

- Strahlungsperturbationen,
- massive-Neutrino-Skalenabhängigkeit,
- nichtlineares Wachstum,
- baryonisches Feedback,
- modifizierte Poisson- oder Lensingfunktionen,
- eine HZT-spezifische Growth-Forward-Map.

## 4. QA

Der Node-Validator prüft analytische Grenzfälle, Krümmungsgeometrie, Etherington-Reziprozität, ungültige Hintergrunddomänen, Bridge-Domäne, die `βτ I_B`-Degeneration, LCDM-Referenzwerte, den Einstein-de-Sitter-Grenzfall und die Growth-Firewall.

Ein unabhängiger Python-Test rekonstruiert Distanzen und die Growth-ODE getrennt und vergleicht sie mit den Node-Ausgaben.

## 5. Nicht enthalten

- keine Migration öffentlicher Rechner,
- keine Änderung von Slidern oder UI,
- kein Likelihood-Fit,
- keine Parent-Herleitung,
- keine physische Background- oder Response-Rank-Ausführung,
- keine K1-D-/K1-E-Hochstufung.

## 6. Nächster Block

Nach grünem Foundation-PR werden Seiten einzeln migriert. Reihenfolge:

1. `validation.html` als unabhängiges Referenz-Gate,
2. `observatory.html`,
3. `compare-safe.html`,
4. `compare-direct.html` und Stilllegung der doppelten Semantik,
5. `emergence.html` nur über einen expliziten Growth-Adapter.

Jede Migration benötigt Browser-Parität, ungültige-Domänen-Negativtests, Krümmungsdistanztests und exakte Engine-Identität.
