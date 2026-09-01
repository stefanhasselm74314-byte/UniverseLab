# UniverseLab Validation Console Migration v2.0

**Datum:** 2026-09-01  
**Basis-`main`:** `8a0dc1ae9aee8cdbde346b2a6ef5003f21cf2b08`  
**Klassifikation:** interne mathematische und numerische Validierung; keine empirische oder physikalische Evidenzwirkung  
**Physical gate effect:** `NONE`

## 1. Zweck

Die deutsche und englische Validation Console verwenden ab diesem Block keine getrennten eingebetteten Friedmann-, Integrations- oder Distanzimplementierungen mehr. Beide Seiten laden denselben kanonischen Rechenkern und denselben sprachneutralen Testadapter. Übersetzt werden nur Beschriftungen und Kriterien; Testidentität, numerische Werte, Toleranzen und Status bleiben identisch.

## 2. Stabile Testidentität

Jeder Test besitzt eine sprachunabhängige `data-test-id`. Browser-Parität wird nicht mehr über eine fest verdrahtete Zahl von Tabellenzeilen oder lokalisierte Texte festgestellt, sondern über:

1. identische geordnete Test-IDs,
2. identische Engine-Version,
3. identische numerische Werte und Toleranzen,
4. identische Fehlercodes,
5. `PASS` aller internen Tests in beiden Sprachfassungen.

## 3. Validierter mathematischer Scope

### Hintergrund

Für ΛCDM und konstantes `w`:

`E(a)^2 = Omega_r a^-4 + Omega_m a^-3 + Omega_k a^-2 + Omega_DE a^[-3(1+w)]`.

Es gilt fail-closed:

`E^2 <= 0 -> INVALID_BACKGROUND_DOMAIN`.

Für die effektive Brücke zusätzlich:

`1 + Delta <= 0 -> INVALID_BRIDGE_DOMAIN`.

Numerische Floors sind im kanonischen Kern unzulässig.

### Distanzen

Die Console prüft explizit:

`D_C -> D_M -> D_L, D_A`,

mit offener, flacher und geschlossener Krümmungsabbildung sowie Etherington-Reziprozität

`D_L = (1+z)^2 D_A`.

### Wachstum

Geprüft werden die lineare GR-Wachstumsgleichung in `ln a`, ΛCDM-Referenzwerte und der Einstein-de-Sitter-Grenzfall `D=a`, `f=1`.

Für das Bridge-Modell muss die Growth-Anfrage mit `UNRELEASED_GROWTH_MAP` scheitern, weil keine freigegebene HZT-Perturbationsabbildung vorliegt.

## 4. Evidenzgrenze

Ein grüner Console-Status bedeutet ausschließlich:

- die implementierten Referenzgleichungen bestehen die angegebenen analytischen und numerischen Selbsttests;
- deutsche und englische Seite sind semantisch und numerisch identisch;
- ungültige Domänen werden nicht still regularisiert.

Nicht daraus folgen:

- empirische Bestätigung von ΛCDM, wCDM oder HZT;
- Parent-Herleitung eines effektiven Parameters;
- physischer 6D-Background oder Response-Rang;
- Ghostfreiheit oder Hamilton-Positivität;
- Zulässigkeit von K1-D oder K1-E.
