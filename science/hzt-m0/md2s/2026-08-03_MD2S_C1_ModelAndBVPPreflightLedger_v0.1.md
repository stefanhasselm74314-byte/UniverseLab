# MD-2S C1 Model and BVP Preflight Ledger v0.1

**Datum:** 2026-08-03  
**Modell-ID:** HZT-M0-S6-C1  
**Status:** CANDIDATE MODEL DEFINED / STRUCTURAL PREFLIGHT PASS / EXECUTION BLOCKED  
**Evidenzwirkung:** NONE  
**Historische A0-Identität:** NICHT BEHAUPTET  
**Solverfreigabe:** FALSE

## 1. Zweck und Geltungsgrenze

Dieses Ledger führt einen neuen, ausdrücklich versionierten Minimalzweig ein, damit die bereits hergeleiteten radialen Gleichungen, Polserien und Junction-Gleichungen erstmals zu einem vollständig zählbaren Randwertproblem zusammengesetzt werden können.

C1 ist **keine Rekonstruktion des verlorenen historischen A0-Modells**. Die Funktionen und Konventionen dieses Zweigs werden als neue Modellpostulate definiert. Übereinstimmungen mit historischen Formeln oder Benchmarks dürfen nur nach einer separaten Gleichungs- und Normalisierungsprüfung behauptet werden.

Der Block beantwortet ausschließlich:

1. Welche konkreten Funktionen und Konventionen definieren C1?
2. Welche kontinuierlichen Freiheitsgrade bleiben nach Polregularität, Gauge- und Frame-Fixierung?
3. Welche unabhängigen Randresiduen müssen verschwinden?
4. Besteht bereits auf kombinatorischer Ebene eine offensichtliche Rangunterbestimmtheit?

Er beantwortet nicht:

- ob eine globale Lösung existiert,
- ob die Lösung eindeutig oder numerisch gut konditioniert ist,
- ob die Störungen ghostfrei und stabil sind,
- ob C1 die historische A0-Lösung reproduziert,
- ob K1-D oder K1-E freigegeben werden dürfen.

## 2. Quellenbasis

C1 baut ausschließlich auf den bereits kanonisierten Strukturen auf:

- `registry/2026-08-03_MD2S_RadialEquationContract_v0.1.json`
- `registry/2026-08-03_MD2S_JunctionContract_v0.1.json`
- `registry/2026-08-03_MD2S_ParameterAngularFluxContract_v0.1.json`
- `registry/2026-08-03_MD2S_SymbolicDependencyGraph_v0.1.json`

Die fünf bisher offenen Funktionen werden nicht als historisch rekonstruiert, sondern für C1 neu definiert.

## 3. C1-Bulkwirkung

Der Bulkzweig lautet

```text
S_bulk = integral d6x sqrt(|g|) [
  (R - 2 Lambda_geom)/(2 kappa6^2)
  - 1/2 (partial phi)^2
  - U0
  - 1/2 m_phi_sq (phi-phi_star)^2
  - 1/4 F_AB F^AB
].
```

Damit sind

```text
U(phi)   = U0 + 1/2 m_phi_sq (phi-phi_star)^2,
Z_phi    = 1,
Z_F      = 1.
```

Die Parameterbereiche werden festgelegt als

```text
kappa6_sq > 0,
m_phi_sq >= 0,
Lambda_geom, U0, phi_star real.
```

Die Dimensionen lauten

```text
[kappa6_sq] = M^-4,
[Lambda_geom] = M^2,
[U0] = M^6,
[m_phi_sq] = M^2,
[phi_star] = M^2.
```

Die Kombination aus `Lambda_geom` und `U0` bleibt physikalisch unterscheidbar, weil `Lambda_geom` im Einstein-Hilbert-Sektor liegt und `U0` als Materie-Vakuumenergie definiert ist. Eine spätere Reparametrisierung darf diese Trennung nur mit explizitem Wirkungsnachweis ändern.

## 4. C1-Kappenwirkung

Die lokalisierte Wirkung lautet

```text
S_Sigma = - integral_Sigma d5x sqrt(|h|) [
  lambda0 + lambda1 (phi-phi_star)
  + 1/2 z_sigma0 X_sigma
].
```

Damit sind

```text
lambda(phi) = lambda0 + lambda1 (phi-phi_star),
Z_sigma(phi) = z_sigma0.
```

Es gilt

```text
[lambda0] = M^5,
[lambda1] = M^3,
[z_sigma0] = M^3,
z_sigma0 > 0.
```

Die lineare Skalarabhängigkeit ist die minimale nichttriviale Wahl, welche die skalare Junction-Gleichung unabhängig kontrollierbar hält. Sie ist ein C1-Modellpostulat und keine aus dem historischen A0-Zweig abgeleitete Kopplung.

## 5. Winkel-, Ladungs- und Topologiekonvention

C1 verwendet eine dimensionslose Winkelkoordinate

```text
chi ~ chi + 2 pi.
```

Also

```text
Delta_chi = 2 pi.
```

Die interne Fläche wird als zwei glatte Scheibenregionen dargestellt:

```text
M2 = D_N union_Sigma D_S,
```

wobei jede lokale Koordinate `r_s` vom glatten Pol `r_s=0` bis zur gemeinsamen Kappe `r_s=rho_s` wächst.

Die lokale nach außen gerichtete Normale an der gemeinsamen Kappe ist in beiden lokalen Koordinaten

```text
n_s^r = +1.
```

Die Wicklungs- und Fluxsektoren sind diskret:

```text
N_sigma in Z,
N_F in Z.
```

C1 postuliert, dass die lokalisierte Phase die minimale Referenzladung trägt:

```text
q_sigma = q_ref = q0,
q0 > 0.
```

Diese Identität ist **nur innerhalb von C1 definiert**. Sie ist nicht als allgemeine Eigenschaft des Parentmodells oder des historischen A0-Zweigs bewiesen.

## 6. Polregularität und lokale freie Daten

An jedem glatten Pol gelten bei `Delta_chi=2 pi`:

```text
L_s(0) = 0,
L_s'(0) = 1,
A_s'(0) = 0,
phi_s'(0) = 0.
```

In einer am jeweiligen Pol regulären Gauge wird zusätzlich gesetzt:

```text
A_chi,s(0) = 0.
```

Die führende reguläre Serie besitzt pro Region genau drei kontinuierliche freie Daten:

```text
A_s(0),
phi_s(0),
Q_s.
```

Die höheren Serienkoeffizienten werden durch die radialen Gleichungen bestimmt.

## 7. Frame- und Patch-Fixierung

Die additive 4D-Warp-Redundanz wird durch

```text
A_N(0) = 0
```

fixiert.

`A_S(0)` bleibt als relative Warpnormierung zwischen den beiden lokalen Pol-Patches im Schießvektor.

Die beiden regulären Gauge-Patches verwenden

```text
A_chi,N(0)=0,
A_chi,S(0)=0.
```

Die globale Orientierung wird definiert durch

```text
Phi_F = 2 pi [A_chi,N(rho_N)-A_chi,S(rho_S)].
```

Mit

```text
q0 Phi_F = 2 pi N_F
```

folgt die einzelne Patch-/Fluxbedingung

```text
A_chi,N(rho_N)-A_chi,S(rho_S)-N_F/q0 = 0.
```

In dieser Zwei-Patch-Konvention ist die globale Fluxquantisierung bereits in der Patchrelation enthalten und darf nicht ein zweites Mal als unabhängige Randgleichung gezählt werden.

## 8. Kontinuierlicher Schießvektor

Vor Frame-Fixierung liefern die zwei regulären Regionen

```text
2 x 3 = 6
```

freie Polparameter. Hinzu kommen die zwei Kappenpositionen

```text
rho_N, rho_S.
```

Das ergibt acht Größen. Die globale Warp-Frame-Fixierung entfernt eine, während die gemeinsame 4D-Krümmung `K4` als Eigenwert wieder hinzukommt.

Der quadratische C1-Schießvektor lautet daher

```text
x = (
  phi_N_0,
  Q_N,
  A_S_0,
  phi_S_0,
  Q_S,
  rho_N,
  rho_S,
  K4
).
```

Damit gilt

```text
N_unknown = 8.
```

`N_sigma` und `N_F` sind diskrete Sektorlabels und keine kontinuierlichen Schießparameter.

## 9. Acht unabhängige Randresiduen

Der Residualvektor lautet

```text
R = (
  R_A,
  R_L,
  R_phi,
  R_patch,
  R_4d,
  R_chi,
  R_scalar,
  R_gauge
).
```

### 9.1 Induzierte Kontinuität

```text
R_A   = A_N(rho_N)-A_S(rho_S),
R_L   = L_N(rho_N)-L_S(rho_S),
R_phi = phi_N(rho_N)-phi_S(rho_S).
```

### 9.2 Gauge-Patch und globaler Flux

```text
R_patch = A_chi,N(rho_N)-A_chi,S(rho_S)-N_F/q0.
```

### 9.3 Metrische Junctions

Mit

```text
A_Sigma = A_N'(rho_N)+A_S'(rho_S),
L_Sigma = L_N'(rho_N)/L_N(rho_N)
          + L_S'(rho_S)/L_S(rho_S),
```

lauten

```text
R_4d = -(3 A_Sigma+L_Sigma)
       + kappa6_sq [lambda(phi_cap)+Y_sigma/2],

R_chi = -4 A_Sigma
        + kappa6_sq [lambda(phi_cap)-Y_sigma/2].
```

### 9.4 Skalare Junction

Da `Z_phi=1`, `Z_sigma,phi=0` und `lambda,phi=lambda1`, folgt

```text
R_scalar = phi_N'(rho_N)+phi_S'(rho_S)+lambda1.
```

### 9.5 Lokale Gauge-Junction

Mit

```text
d_chi = N_sigma-q0 A_chi,cap
```

in der `Delta_chi=2 pi`-Konvention gilt

```text
R_gauge = exp(-4A_cap)/L_cap (Q_N+Q_S)
          - q0 z_sigma0 d_chi/L_cap^2.
```

## 10. Nicht zusätzlich gezählte Gleichungen

### 10.1 Phasengleichung

Für den statischen homogenen Wicklungsansatz und konstantes `z_sigma0` ist

```text
D_a(z_sigma0 D^a sigma)=0
```

entlang der Kappe automatisch erfüllt. Sie bleibt ein QA-Kanal, ist aber keine neunte unabhängige algebraische Randbedingung.

### 10.2 Radiale Einstein-Nebenbedingungen

Die `rr`-Gleichung wird an jedem Pol durch die reguläre Serie erfüllt und muss entlang der Integration propagieren. Ihre Werte an der Kappe sind zwingende numerische Qualitätsdiagnosen, aber keine zusätzlich frei auferlegten Randgleichungen.

### 10.3 Globale Fluxquantisierung

Die Fluxquantisierung ist in C1 bereits durch `R_patch` kodiert. Ein separates `R_flux` würde dieselbe topologische Bedingung doppelt zählen.

## 11. Struktureller Rang-Preflight

Für die acht Residuen und acht Unbekannten wird ein bipartiter Abhängigkeitsgraph definiert. Der Graph besitzt ein vollständiges Matching, zum Beispiel

```text
R_A      -> A_S_0,
R_L      -> rho_N,
R_phi    -> phi_N_0,
R_patch  -> Q_N,
R_4d     -> rho_S,
R_chi    -> K4,
R_scalar -> phi_S_0,
R_gauge  -> Q_S.
```

Damit ist der maximale **strukturelle** Rang

```text
rank_structural,max = 8.
```

Das beweist nur:

> Im deklarierten Abhängigkeitsmuster existiert keine offensichtliche kombinatorische Rangbarriere.

Es beweist nicht, dass der tatsächliche Jacobian

```text
J_ij = partial R_i / partial x_j
```

an einer Lösung Rang acht besitzt.

## 12. Zwei wichtige Rangrisiken

### 12.1 Skalarer Shift-Zweig

Wenn gleichzeitig

```text
m_phi_sq = 0,
lambda1 = 0,
```

ist die Wirkung invariant unter einer konstanten Verschiebung von `phi`. Dann ist eine kontinuierliche skalare Nullrichtung zu erwarten, sofern keine weitere skalare Normierungsbedingung eingeführt wird.

Dieser Parameterunterraum ist für einen vollen Rang auszuschließen oder separat als symmetrischer Zweig zu behandeln.

### 12.2 Fest vorgegebenes K4

Wird `K4` extern festgehalten und bleiben alle Modellparameter fix, reduziert sich der kontinuierliche Schießvektor auf sieben Größen, während acht unabhängige Residuen verbleiben:

```text
N_unknown = 7,
N_residual = 8.
```

Das Problem ist dann generisch von Kodimension eins. Eine konsistente Fortsetzung verlangt entweder

1. genau einen klar benannten Modellparameter als Fortsetzungs-/Tuningvariable, oder
2. den Verzicht auf eine tatsächlich nicht unabhängige Zielbedingung mit mathematischem Nachweis.

Ein stilles Fitten mehrerer Parameter ist unzulässig.

## 13. Statuswirkung

Für den neuen Modellzweig gilt:

```text
C1_FUNCTIONS                = CANDIDATE_FROZEN
C1_TOPOLOGY                 = CANDIDATE_FROZEN
C1_FRAME_AND_PATCH          = CANDIDATE_FROZEN
C1_BVP_COUNT                = STRUCTURAL_PREFLIGHT_PASS
C1_MAX_STRUCTURAL_RANK      = 8
C1_ACTUAL_JACOBIAN_RANK     = OPEN
C1_GLOBAL_BACKGROUND        = NOT_COMPUTED
C1_HISTORICAL_A0_IDENTITY   = NOT_CLAIMED
R1.1                        = BLOCKED
MD2S_SOLVER                 = NOT_AUTHORIZED
K1-D                        = NOT_RELEASED
K1-E                        = NOT_ADMISSIBLE
```

## 14. Nächste Freigabeschritte

Vor einem offiziellen BVP-Lauf sind mindestens erforderlich:

1. dimensionslose Variablen und Referenzskala,
2. normierter Residualvektor und vorregistrierte Toleranzen,
3. analytischer Startpunkt oder lokaler Fortsetzungsanker,
4. tatsächlicher symbolischer oder automatisch differenzierter Jacobian,
5. Constraint-Propagation und Schrittweitenkonvergenz,
6. getrennte Behandlung der Rangrisikoflächen,
7. ausdrückliche Governance-Entscheidung zur diagnostischen Solverfreigabe.

Bis dahin bleibt C1 eine klar definierte, formal zählbare Kandidatenstruktur ohne Evidenzwirkung.
