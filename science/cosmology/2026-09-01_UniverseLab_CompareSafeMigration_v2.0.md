# UniverseLab Compare SAFE → kanonischer Kosmologie-Rechenkern v2.0

**Datum:** 2026-09-01  
**Basis-`main`:** `3d989304678280491951d46f0ac6b261f4d0c720`  
**Klassifikation:** öffentliche diagnostische Vergleichsseite; keine physikalische Evidenzwirkung  
**Physical gate effect:** `NONE`

## 1. Geschlossener Fehlerumfang

Die vorherige Seite enthielt einen unabhängigen Inline-Rechenkern mit drei voneinander abweichenden Hintergrundpfaden. Dabei wurden negative Werte durch positive Floors ersetzt,

`E² → max(10^-12,E²)` und `1+Δ → max(0.02,1+Δ)`,

und die radiale Entfernung `D_C` wurde auch bei `Ω_k≠0` unmittelbar für `D_L` und `D_A` verwendet. Diese Migration entfernt den Inline-Kern vollständig.

## 2. Modellidentität

Verglichen werden jetzt exakt zwei deklarierte Modelle:

1. `lcdm`;
2. `bridge` mit `E_bridge²=E_LCDM²(1+Δ)`.

Der frühere, seitenlokale Hybrid `wCDM×bridge` besitzt keinen freigegebenen Parent- oder Effektivvertrag und wird nicht fortgeführt. Das bestehende `w`-Feld bleibt aus UI-Kompatibilitätsgründen sichtbar, ist aber auf `w=-1` eingefroren.

## 3. Brückenkanal und Identifizierbarkeit

`Δ(a)=βτ 𝓘B exp[-(a/a_c)²]`.

Für alle nur von diesem Hintergrundkanal abhängigen Observablen gilt mit `A_B=βτ𝓘B`:

`∂O/∂βτ=𝓘B ∂O/∂A_B`,

`∂O/∂𝓘B=βτ ∂O/∂A_B`.

Die beiden Jacobian-Spalten sind proportional; somit ist

`rang J_(βτ,𝓘B)≤1`.

Die Seite darf daher nur das Produkt, nicht die getrennte physikalische Identifikation beider Parameter darstellen.

## 4. Domänen

Vor jeder Kurve, Distanz, Altersintegration oder CSV-Ausgabe werden Basis und Brücke geprüft:

- `0≤z≤8` für sichtbare Hintergrund-/Distanzpfade;
- `10^-8≤a≤1` für die Altersintegration.

Es gilt fail-closed:

- `E²≤0 → INVALID_BACKGROUND_DOMAIN`;
- `1+Δ≤0 → INVALID_BRIDGE_DOMAIN`.

Bei Verletzung werden keine Kurven, Statistiken oder CSV-Werte erzeugt. `NaN` und `Infinity` sind keine zulässigen Ersatzoutputs.

## 5. Distanzen

Die vollständige Kette lautet

`D_C → D_M → D_L,D_A`,

mit `sinh` für `Ω_k>0`, Identität für `Ω_k=0` und `sin` für `Ω_k<0`. Zusätzlich gilt Etherington-Reziprozität:

`D_L=(1+z)^2D_A`.

## 6. Observablen-Firewalls

Der Brückenhintergrund definiert keine freigegebene Perturbations- oder Lensing-Dynamik. Deshalb zeigt die Seite ausdrücklich:

- `UNRELEASED_GROWTH_MAP`;
- `UNRELEASED_LENSING_MAP`.

Die verfügbare lineare GR-Wachstumslösung für ΛCDM darf nicht als HZT-Brückenwachstum verwendet werden. Ebenso ist `Σ=η=1` nur die GR-Referenz, keine Brückenherleitung.

## 7. Gültigkeitsgrenze

Ein interner PASS belegt ausschließlich, dass der deklarierte numerische Vertrag innerhalb seiner Domäne konsistent ausgeführt wurde. Er belegt weder empirische Modellbestätigung noch Parent-Herleitung, separate Parameteridentifikation, Ghostfreiheit, Hamilton-Positivität oder K1-D/K1-E-Zulässigkeit.
