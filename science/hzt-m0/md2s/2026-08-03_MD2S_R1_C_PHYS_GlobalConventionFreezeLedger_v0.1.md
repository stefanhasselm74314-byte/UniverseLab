# MD2S-R1-C-PHYS — Global Convention Freeze Ledger v0.1

**Datum:** 2026-08-03  
**Track:** `MD2S-R1-C-PHYS`  
**Block:** `C-PHYS-R1.0-FREEZE-1A`  
**Status:** `GLOBAL_CONVENTIONS_AND_PARAMETER_ROLES_FROZEN_FUNCTIONS_OPEN`  
**Physikalische Evidenzwirkung:** `NONE`

## 1. Ziel

Dieser Block schließt nur jene Teile des C-PHYS-Modells, die aus Koordinatenfreiheit, glatter Polgeometrie, U(1)-Bündelkonsistenz und einer eindeutigen Parameterklassifikation folgen. Die konkreten Funktionen

\[
U(\phi),\quad Z_F(\phi),\quad\lambda(\phi),\quad Z_\sigma(\phi)
\]

werden **nicht** aus dem C1-V-Verifikationsmodell übernommen und nicht als angeblich hergeleitet ausgegeben.

---

## 2. Winkelkonvention

Unter

\[
\chi_{\rm neu}=c\chi,\qquad c>0,
\]

transformieren

\[
\Delta\chi_{\rm neu}=c\Delta\chi,\qquad
L_{\rm neu}=L/c,\qquad
A_{\chi,\rm neu}=A_\chi/c.
\]

Die Größen

\[
X_\sigma,\qquad F_{r\chi}/L,\qquad Q,\qquad\Phi_F
\]

bleiben invariant. Deshalb ist

\[
\boxed{\Delta\chi=2\pi}
\]

eine zulässige Koordinatenfixierung und kein physikalischer Fitparameter.

Für lokale Radialkoordinaten, die jeweils vom glatten Pol zur Kappe wachsen, gilt dann

\[
L_N(0)=L_S(0)=0,\qquad
L_N'(0)=L_S'(0)=+1.
\]

---

## 3. Zwei verschiedene Orientierungsbegriffe

Die bisherige Notation muss zwei Vorzeichenarten strikt trennen.

### 3.1 Randnormalen

Da beide regionalen Koordinaten vom Pol zur Kappe wachsen, zeigen die äußeren Normalen an der gemeinsamen Kappe in beiden lokalen Koordinatenrichtungen nach \(+r_s\):

\[
\boxed{n_N^r=n_S^r=+1.}
\]

Diese Vorzeichen gehören in die Israel-, Skalar- und lokale Gauge-Junctions.

### 3.2 Globale Orientierung der internen Zweiform

Eine global orientierte Zweikugel kann nicht auf beiden Scheiben dieselbe lokale Orientierung \(dr_s\wedge d\chi\) besitzen, wenn beide \(r_s\) vom jeweiligen Pol zum gemeinsamen Äquator wachsen. Deshalb gilt

\[
\boxed{\epsilon_N=+1,\qquad\epsilon_S=-1.}
\]

Diese Vorzeichen gehören in das globale Flussintegral.

Damit ist ausdrücklich

\[
\text{Randnormalzeichen}\neq\text{globale Flussorientierung}.
\]

---

## 4. Reguläre Gauge-Patches

An beiden glatten Polen werden reguläre lokale Eichungen gewählt:

\[
A_{\chi,N}(0)=A_{\chi,S}(0)=0.
\]

Auf dem Überlappungsgebiet gilt

\[
A_N=A_S+d\Lambda_{NS}.
\]

Für die minimale positive Ladungseinheit \(q_{\rm ref}>0\) fordert Einwertigkeit

\[
q_{\rm ref}
\left[
\Lambda_{NS}(\chi+2\pi)-\Lambda_{NS}(\chi)
\right]=2\pi N_F,
\qquad N_F\in\mathbb Z.
\]

Daraus folgt die lineare Übergangsfunktion

\[
\boxed{
\Lambda_{NS}(\chi)=\frac{N_F}{q_{\rm ref}}\chi
}
\]

und damit

\[
\boxed{
R_{\rm patch}
=A_{\chi,N}(\rho_N)-A_{\chi,S}(\rho_S)
-\frac{N_F}{q_{\rm ref}}=0.
}
\]

Diese Gleichung ist eine Eigenschaft des U(1)-Bündels und keine Übernahme eines C1-V-Parameterwertes.

---

## 5. Globaler Flux

Mit den globalen Orientierungszeichen lautet der magnetische Flux

\[
\boxed{
\Phi_F
=2\pi\left[
\int_0^{\rho_N}F_{r\chi,N}\,dr
-
\int_0^{\rho_S}F_{r\chi,S}\,dr
\right].
}
\]

In den regulären Pol-Gauges folgt

\[
\Phi_F
=2\pi
\left[
A_{\chi,N}(\rho_N)-A_{\chi,S}(\rho_S)
\right].
\]

Daher sind

\[
q_{\rm ref}\Phi_F=2\pi N_F
\]

und \(R_{\rm patch}=0\) dieselbe globale topologische Bedingung.

\[
\boxed{
R_{\rm flux}\text{ und }R_{\rm patch}
\text{ dürfen in dieser Zwei-Patch-Konvention nur einmal gezählt werden.}
}
\]

Eine orientierungslose Summe beider regionalen Integrale ist bei den gewählten lokalen Radialrichtungen falsch.

---

## 6. Ladungsgitter

\(q_{\rm ref}\) definiert die minimale positive U(1)-Ladungseinheit. Die Kappenphase muss auf demselben Ladungsgitter liegen:

\[
\boxed{
q_\sigma=m_\sigma q_{\rm ref},
\qquad m_\sigma\in\mathbb Z_{>0}.
}
\]

Damit ist

\[
q_\sigma=q_{\rm ref}
\]

nur der spezielle Sektor \(m_\sigma=1\), nicht die allgemeine Theorie.

Für \(\Delta\chi=2\pi\) lautet die statische Wicklung

\[
\partial_\chi\sigma=N_\sigma,\qquad N_\sigma\in\mathbb Z,
\]

und

\[
\boxed{
d_\chi=N_\sigma-q_\sigma A_{\chi,\Sigma}.}
\]

---

## 7. Vierdimensionaler Frame

Die additive Warpredundanz wird durch

\[
\boxed{A_N(0)=0}
\]

entfernt. \(A_S(0)\) bleibt eine kontinuierliche Schießvariable. Es ist unzulässig, gleichzeitig \(A_S(0)=0\) zu setzen, sofern keine zusätzliche physikalische Symmetrie dies erzwingt.

---

## 8. Parameterrollen

### Kontinuierliche Schieß- oder Eigenwertgrößen

\[
\boxed{
\left(
\phi_N(0),Q_N,A_S(0),\phi_S(0),Q_S,ho_N,ho_S,\mathcal K_4
\right)
}
\]

Anzahl: acht.

### Diskrete Sektoren

\[
(N_F,N_\sigma,m_\sigma)\in
\mathbb Z\times\mathbb Z\times\mathbb Z_{>0}.
\]

Ein Wechsel dieser Zahlen ist ein Wechsel des topologischen beziehungsweise Ladungssektors und kein kontinuierlicher Solver-Schritt.

### Modellparameter

Innerhalb eines einzelnen Modellinstanz bleiben fest:

- \(M_6,\Lambda_6,q_{\rm ref}\),
- die exakten Funktionen \(U,Z_F,\lambda,Z_\sigma\),
- sämtliche Koeffizienten dieser Funktionen.

Sie dürfen zwischen klar gekennzeichneten Modellinstanzen gescannt, aber nicht stillschweigend als zusätzliche Schießvariablen benutzt werden.

---

## 9. Konditionale quadratische BVP-Zählung

Nach Frame-, Gauge-, Winkel- und Topologiefixierung stehen acht kontinuierliche Unbekannte acht unabhängigen Randresiduen gegenüber:

1. \(R_A\),
2. \(R_L\),
3. \(R_\phi\),
4. \(R_{\rm patch}\),
5. \(R_{4D}\),
6. \(R_\chi\),
7. \(R_{\rm scalar}\),
8. \(R_{\rm gauge,local}\).

Der globale Flux ist durch \(R_{\rm patch}\) bereits enthalten. Die \(rr\)-Constraints sind nach noch ausstehendem Abhängigkeitsbeweis QA-Kanäle.

Damit gilt

```text
STRUCTURAL_BVP_COUNT = SQUARE_CONDITIONAL
```

Nicht daraus folgen:

- Existenz,
- Eindeutigkeit,
- Fredholm-Eigenschaft,
- nichtverschwindender Kontinuums-Jacobian,
- numerische Konditionierung,
- Stabilität.

---

## 10. Warum die Funktionsformen offen bleiben

Die aktuellen C-PHYS-Quellen legen zwar die Parentwirkungsstruktur fest, bestimmen aber nicht eindeutig

\[
U(\phi),Z_F(\phi),\lambda(\phi),Z_\sigma(\phi).
\]

Die C1-V-Formen sind ausdrücklich manufactured verification data und dürfen nicht in C-PHYS migrieren. Eine konkrete Wahl wäre daher eine **neue Modellselektion**, keine Herleitung.

Bis zur nächsten versionierten Entscheidung gelten nur die Funktionsklassen:

- \(U\in C^2\), Dimension \(M^6\), im gewählten Feldbereich nach unten beschränkt,
- \(Z_F\in C^2\), strikt positiv und dimensionslos,
- \(\lambda\in C^2\), Dimension \(M^5\),
- \(Z_\sigma\in C^2\), im aktiven Winding-Zweig strikt positiv, Dimension \(M^3\).

---

## 11. Gate-Wirkung

```text
R1.0                       = ACTIVE_FUNCTION_FREEZE_REMAINING
R1.1                       = BLOCKED
R1.2                       = BLOCKED
structural BVP count       = SQUARE_CONDITIONAL
continuum BVP operator     = SCAFFOLD_ONLY
continuum BVP Jacobian     = NOT_PROVEN
official MD-2S solver      = NOT_AUTHORIZED
K1-D                       = NOT_RELEASED
K1-E                       = NOT_ADMISSIBLE
physical evidence effect   = NONE
```

## 12. Nächster Block

```text
C-PHYS-R1.0-FREEZE-1B
```

Dieser Block muss die exakten minimalen EFT-Funktionen, den skalaren Feldbereich, Positivität, Beschränktheit, Redundanzen und das Parameter-Identifizierbarkeitsbudget als **neue versionierte Modellwahl** festlegen.
