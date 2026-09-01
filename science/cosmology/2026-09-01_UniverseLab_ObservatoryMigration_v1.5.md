# UniverseLab Observatory → kanonischer Kosmologie-Rechenkern v1.5

**Datum:** 2026-09-01  
**Basis-`main`:** `6d603a47c90ceed61f3637d2cd0272ca85b54462`  
**Klassifikation:** öffentliche diagnostische Seite; numerische Engine-Migration; keine physikalische Evidenzwirkung  
**Physical gate effect:** `NONE`

## 1. Geschlossener technischer Fehlerumfang

Die vorherige Observatory-Fassung enthielt einen eigenen lokalen Rechenkern. Für nichtflache Modelle wurden dabei insbesondere

- die radiale komovierende Entfernung `D_C` als Grundlage des Distanzmoduls verwendet, obwohl `D_L=(1+z)D_M` gilt;
- `D_C/r_d` als `D_M/r_d` beschriftet;
- lineares Wachstum durch `D≈a` und `f≈Ω_m(z)^0.55` angenähert;
- ungültige reelle Hintergrunddomänen bis zu `NaN`-Ausgaben durchgereicht.

Die Migration entfernt diese lokalen Implementierungen und bindet die Seite ausschließlich an `UniverseLabCosmology`.

## 2. Hintergrund

Für konstantes `w` gilt

`E²(a)=Ω_r a^-4 + Ω_m a^-3 + Ω_k a^-2 + Ω_DE a^[-3(1+w)]`,

mit

`Ω_k=1-Ω_r-Ω_m-Ω_DE`.

Observatory validiert dicht im sichtbaren Bereich `0≤z≤5` und zusätzlich logarithmisch über `10^-8≤a≤1`, bevor Alter oder Kurven berechnet werden. Bei `E²≤0` gilt fail-closed:

`INVALID_BACKGROUND_DOMAIN`.

Es wird weder ein positiver Floor noch eine komplexe Fortsetzung als reelle Modellkurve ausgegeben.

## 3. Distanzen

Die Seite verwendet nun die vollständige Kette

`D_C → D_M → D_L,D_A`.

Für `Ω_k>0` wird die offene `sinh`-Abbildung, für `Ω_k=0` die Identität und für `Ω_k<0` die geschlossene `sin`-Abbildung verwendet. Das Hubble-Diagramm nutzt

`D_L=(1+z)D_M`,

und der BAO-Modus tatsächlich

`D_M/r_d`.

## 4. Lineares Wachstum

Der Growth-Modus löst die gemeinsame lineare GR-Referenzgleichung

`D''+[2+d ln H/d ln a]D'-(3/2)Ω_m(a)D=0`,

mit Ableitungen nach `ln a` und Normierung `D(1)=1`. Dargestellt wird

`fσ8(z)=f(z)D(z)σ8,0`.

Dies ist eine glatte-DE-GR-Referenz für ΛCDM/konstantes `w`, keine freigegebene HZT-Perturbationsabbildung. Für das effektive Bridge-Modell bleibt Growth durch `UNRELEASED_GROWTH_MAP` gesperrt.

## 5. Didaktische Beispielwerte

Die eingebetteten H(z)-, Supernova-, RSD- und BAO-Punkte bleiben didaktische Beispielwerte. Es existieren in diesem Seitenvertrag kein versionierter Datenvektor, keine Kovarianz, keine Selection Function, kein Nuisance-Modell und keine Likelihood. Daher gilt:

`visueller Kurvenvergleich ≠ Datenfit ≠ Theoriebestätigung`.

## 6. QA

Der Migrationsblock prüft statisch und im Browser:

- Defaultzustand und Engine-Identität;
- offene Geometrie `D_M>D_C` und BAO-Probe `D_M/r_d`;
- geschlossene Geometrie `D_M<D_C` und BAO-Probe `D_M/r_d`;
- Growth-Probe identisch zur kanonischen ODE und materiell verschieden von der alten Näherung;
- sichtbares fail-closed Verhalten für den bekannten ungültigen wCDM-Zeugen;
- keine `NaN`-/`Infinity`-Darstellung;
- Reset-Recovery;
- keine Browser- oder HTTP-Fehler.

## 7. Nicht enthalten

- keine Änderung von Compare oder Emergence;
- kein Likelihood-Fit;
- keine Parent→Reduced→Observable-Herleitung;
- kein physischer 6D-Background- oder Response-Rank-Lauf;
- keine Ghostfreiheits- oder Stabilitätspromotion;
- keine AuthorizationDecision oder Grant-Ausstellung;
- keine K1-D-/K1-E-Hochstufung.
