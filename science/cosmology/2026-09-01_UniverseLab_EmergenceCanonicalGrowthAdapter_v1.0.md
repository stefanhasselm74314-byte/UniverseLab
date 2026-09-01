# UniverseLab Emergence: kanonischer Hintergrund- und Growth-Adapter v1.0

**Datum:** 2026-09-01  
**Basis-`main`:** `67c92e2644cee1f2c3a5526cd914f81a3b40a7b8`  
**Klassifikation:** öffentliche diagnostische Visualisierung; keine physikalische Evidenzwirkung  
**Physical gate effect:** `NONE`

## 1. Ziel und strikte Systemtrennung

Die Seite vereint zwei mathematisch verschiedene Systeme:

1. einen zweidimensionalen diskreten Zellautomaten;
2. eine kosmologische Hintergrund- und lineare Growth-Diagnostik.

Die Migration erzwingt die direkte Produkstruktur

`Zustand = Zustand_Zellautomat × Zustand_Kosmologie`.

Es existiert kein Term, durch den die Zellbelegung in `E(a)`, `q(a)`, `D(a)` oder `f(a)` eingeht. Umgekehrt verändert die Growth-Amplitude keine Geburts- oder Überlebensregel. Die optionale Änderung der sichtbaren Gitterauflösung ist ausschließlich eine Resampling-Konvention.

Daher gilt:

`zelluläres Muster ≠ kosmische Dichteperturbation ≠ 6D-Strukturbildungsherleitung`.

Eine ungültige Kosmologiedomäne sperrt ausschließlich die Kosmologiediagnose. Der diskrete Zellautomat kann weiter iterieren; dadurch ist die behauptete dynamische Entkopplung im Browser direkt prüfbar.

## 2. Hintergrunddynamik

Für den deklarierten ΛCDM-Referenzpfad gilt

`E²(a)=Ω_r a^-4+Ω_m a^-3+Ω_k a^-2+Ω_Λ`,

mit

`Ω_k=1-Ω_r-Ω_m-Ω_Λ`.

`E=H/H0` ist dimensionslos. Für die reine Anzeigezeit wird

`τ=H0 t`

verwendet. Damit ist

`d ln(a)/dτ=E(a)`

und äquivalent

`da/dτ=a E(a)`.

Der Adapter integriert nur bis `a=1`. Eine Fortsetzung in die Zukunft `a>1` ist im derzeitigen Engine-Vertrag nicht enthalten.

### Dimensionsprüfung

- `a`, `E`, `Ω_i`, `q`, `D/D(1)` und `f` sind dimensionslos;
- `H0` besitzt die Einheit `km s^-1 Mpc^-1`;
- `τ=H0 t` ist dimensionslos;
- die Zellgeneration ist ein diskreter Index ohne physikalische Zeiteinheit.

Eine Gleichsetzung von Zellgeneration und kosmischer Eigenzeit wäre daher ohne zusätzliche Kalibrierungsabbildung unzulässig.

## 3. Fail-closed Domäne

Vor jeder kosmologischen Auswertung wird logarithmisch über

`10^-8 <= a <= 1`

geprüft:

`E²(a)>0`.

Bei einem nichtendlichen oder nichtpositiven Wert gilt

`INVALID_BACKGROUND_DOMAIN`.

Dann werden keine kosmologischen Zeitreihen fortgesetzt, keine scheinbar endlichen Ersatzwerte gezeichnet und kein Ausdruck der Form

`sqrt(max(epsilon,E²))`

verwendet. Der Zellautomat bleibt als diskrete Visualisierung funktionsfähig; die kosmologische Diagnose bleibt gesperrt.

## 4. Lineares Wachstum

Verwendet wird ausschließlich die gemeinsame lineare GR-Referenzgleichung

`D''+[2+d ln(H)/d ln(a)]D'-(3/2)Ω_m(a)D=0`,

wobei Striche Ableitungen nach `ln(a)` bezeichnen. Der wachsende Materiemodus wird bei

`a_i=max(10^-3,10 Ω_r/Ω_m)`

initialisiert und auf

`D(1)=1`

normiert. Die logarithmische Wachstumsrate ist

`f=d ln(D)/d ln(a)`.

Die Seite zeigt zusätzlich

`f_gamma=Ω_m(a)^0.55`

als diagnostische Näherung. Dieser Ausdruck steuert weder die Growth-ODE noch den Zellautomaten. Die Abweichung

`delta_f=(f_gamma-f)/f`

wird sichtbar ausgewiesen.

Für das effektive Bridge-Modell existiert weiterhin keine freigegebene Perturbationsabbildung:

`UNRELEASED_GROWTH_MAP`.

## 5. Epochen

Die analytischen Gleichheitsskalen im ΛCDM-Referenzmodell lauten

`a_RM=Ω_r/Ω_m`,

`a_MΛ=(Ω_m/Ω_Λ)^(1/3)`.

Der Beschleunigungsbeginn wird nicht aus einer separaten Näherungsformel übernommen, sondern numerisch aus dem kanonischen Hintergrund bestimmt:

`q(a_acc)=0`.

Diese Skalen sind Eigenschaften des deklarierten homogenen Referenzhintergrunds, keine aus dem Zellautomaten emergenten Größen.

## 6. Gültigkeitsbereich und ausgeschlossene Physik

Die Growth-Gleichung gilt für lineare, drucklose Materieperturbationen in GR mit glatter Λ-Komponente. Nicht enthalten sind:

- Strahlungsperturbationen und vollständige Boltzmann-Hierarchien;
- massive-Neutrino-Skalenabhängigkeit;
- baryonische Rückkopplung;
- nichtlineare Modenkopplung;
- modifizierte Poisson-, Slip- oder Lensing-Funktionen;
- HZT-spezifische Perturbationen;
- eine Parent→Reduced→Observable-Herleitung;
- Ghost- oder Hamilton-Positivitätsanalyse.

## 7. Falsifikations- und QA-Struktur

Der Migrationsvertrag verlangt:

- Identität der sichtbaren Diagnose mit direkten Aufrufen des kanonischen Rechenkerns;
- unverändertes `a`, wenn der Zellautomat im statischen Kosmologiemodus einen Schritt ausführt;
- wachsendes `a`, wenn die ΛCDM-Anzeigezeit aktiviert ist;
- fail-closed Verhalten für einen expliziten negativen-`E²`-Zeugen;
- weiterhin iterierbaren Zellautomaten bei gesperrter Kosmologiediagnose;
- unabhängige Python-Rekonstruktion der ΛCDM-Growth-ODE;
- deutsch/englische Laufzeitparität;
- keine Browser- oder HTTP-Fehler.

Ein grüner Test bedeutet ausschließlich interne mathematische, numerische und UI-Vertragskonsistenz.

`grüne QA ≠ empirische Evidenz ≠ Ghostfreiheit ≠ K1-D/K1-E-Freigabe`.
