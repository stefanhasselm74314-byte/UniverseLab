# MD-2S Canonical Radial Equation Ledger v0.1

**Datum:** 2026-08-03  
**Zweig:** HZT-M0-S6 / MD-2S / canonical rebuild track  
**Status:** PARTIAL_CONDITIONAL / MODEL FREEZE NOT COMPLETE  
**Evidenzwirkung:** NONE  
**Solverfreigabe:** FALSE

## 1. Zweck und Geltungsgrenze

Dieses Ledger leitet die generische statische radiale Gleichungsstruktur des aktuellen Einstein-Maxwell-Skalar-Skeletts her. Es ist kein Nachweis der Identität mit dem historischen A0-Solver. Die exakten Funktionen `V(phi)`, `Z_phi(phi)`, `Z_F(phi)`, die Winkelperiode, die Kappenwirkung und die orientierten Junction-Konventionen bleiben einzufrieren.

Insbesondere darf die historische Aussage `V(phi)=Lambda6+beta phi^2` nicht unbesehen in die aktuelle Wirkung eingesetzt werden, weil die aktuelle Gravitationswirkung `Lambda6` bereits explizit enthält. Bis zur Quellenklärung bleiben `Lambda6` und `V(phi)` getrennte Terme.

## 2. Wirkung und Ansatz

Verwendet wird

```text
S_bulk = integral d6x sqrt(|g|) [
  (R - 2 Lambda6)/(2 kappa6^2)
  - 1/2 Z_phi(phi) (partial phi)^2
  - V(phi)
  - 1/4 Z_F(phi) F_AB F^AB
].
```

Die Feldgleichungen lauten

```text
G_AB + Lambda6 g_AB = kappa6^2 T_AB,

nabla_A (Z_F F^AB) = 0,

nabla_A(Z_phi nabla^A phi)
- 1/2 Z_phi,phi (partial phi)^2
- V_,phi
- 1/4 Z_F,phi F^2 = 0.
```

Der Hintergrundansatz ist

```text
ds6^2 = exp(2A(r)) gbar_munu dx^mu dx^nu + dr^2 + L(r)^2 dchi^2,
Rbar_munu = 3 K4 gbar_munu,
phi = phi(r),
F_rchi = f(r).
```

Definitionen:

```text
H = A',
S = L'/L,
psi = phi',
B^2 = F_rchi^2/L^2.
```

## 3. Maxwell-Erstintegral

Die Maxwell-Gleichung reduziert sich zu

```text
d/dr [ exp(4A) Z_F F_rchi/L ] = 0.
```

Damit

```text
Q = exp(4A) Z_F F_rchi/L = konstant,
F_rchi = Q L exp(-4A)/Z_F,
B^2 = Q^2 exp(-8A)/Z_F^2.
```

Für die Einstein-Gleichungen ist die magnetische Energiedichte

```text
M = Z_F B^2 = Q^2 exp(-8A)/Z_F.
```

Ein gesunder Maxwell-Kinetikterm verlangt im betrachteten Bereich `Z_F > 0`.

## 4. Krümmung

Mit den Konventionen aus `convention-registry.json` gilt

```text
R_munu/g_munu = 3 K4 exp(-2A) - A'' - 4 A'^2 - A' L'/L,
R_rr = -L''/L - 4(A'' + A'^2),
R_chichi/g_chichi = -L''/L - 4 A' L'/L,

R6 = 12 K4 exp(-2A)
     - 20 A'^2
     - 8 A''
     - 8 A' L'/L
     - 2 L''/L.
```

Die gemischten Einstein-Komponenten sind

```text
G_4 = 3 A'' + 6 A'^2 + 3 A' L'/L + L''/L - 3 K4 exp(-2A),
G_r = 6 A'^2 + 4 A' L'/L - 6 K4 exp(-2A),
G_chi = 4 A'' + 10 A'^2 - 6 K4 exp(-2A).
```

Hier bezeichnet `G_4` jede der vier identischen externen Diagonalkomponenten.

## 5. Materiekomponenten

Für den radialen Skalar und den internen magnetischen Flux gilt

```text
T_4 = -1/2 Z_phi psi^2 - V - 1/2 M,
T_r = +1/2 Z_phi psi^2 - V + 1/2 M,
T_chi = -1/2 Z_phi psi^2 - V + 1/2 M.
```

## 6. Radiale Feldgleichungen

### EQ-MD2S-RAD-001 — externe Einstein-Gleichung

```text
3 A'' + 6 A'^2 + 3 A' L'/L + L''/L
- 3 K4 exp(-2A) + Lambda6
= kappa6^2 (-1/2 Z_phi phi'^2 - V - 1/2 M).
```

### EQ-MD2S-RAD-002 — radiale Hamilton-Nebenbedingung

```text
6 A'^2 + 4 A' L'/L
- 6 K4 exp(-2A) + Lambda6
= kappa6^2 (+1/2 Z_phi phi'^2 - V + 1/2 M).
```

### EQ-MD2S-RAD-003 — interne Einstein-Gleichung

```text
4 A'' + 10 A'^2
- 6 K4 exp(-2A) + Lambda6
= kappa6^2 (-1/2 Z_phi phi'^2 - V + 1/2 M).
```

### EQ-MD2S-RAD-004 — Skalar-Gleichung

```text
Z_phi [phi'' + (4A' + L'/L) phi']
+ 1/2 Z_phi,phi phi'^2
- V_,phi
- 1/2 Z_F,phi B^2 = 0.
```

## 7. Unabhängiges Evolutionssystem

Für `L>0`, `Z_phi>0` und `Z_F>0` kann ein mögliches unabhängiges System gewählt werden als:

```text
A'' = 1/4 [
  kappa6^2(-1/2 Z_phi phi'^2 - V + 1/2 M)
  + 6 K4 exp(-2A) - Lambda6 - 10 A'^2
],

L''/L =
  kappa6^2(-1/2 Z_phi phi'^2 - V - 1/2 M)
  - 3 A'' - 6 A'^2 - 3 A' L'/L
  + 3 K4 exp(-2A) - Lambda6,

phi'' =
  -(4A' + L'/L) phi'
  - (Z_phi,phi/(2 Z_phi)) phi'^2
  + V_,phi/Z_phi
  + (Z_F,phi/(2 Z_phi)) B^2.
```

Dazu kommen das Maxwell-Erstintegral und die radiale Nebenbedingung als unabhängiger Residualtest.

## 8. Abhängigkeits- und Bianchi-Identität

Definiere die vollständigen Residuen

```text
E4 = G_4 + Lambda6 - kappa6^2 T_4,
Er = G_r + Lambda6 - kappa6^2 T_r,
Echi = G_chi + Lambda6 - kappa6^2 T_chi.
```

Nach Erfüllung der Skalar- und Maxwell-Gleichung folgt aus der kontrahierten Bianchi-Identität

```text
Er' + 4 A' (Er - E4) + (L'/L)(Er - Echi) = 0.
```

Wenn `E4=0`, `Echi=0` und `Er=0` an einem Startpunkt gelten, bleibt die radiale Nebenbedingung formal erhalten. Numerisch muss `Er` dennoch als separater Residualkanal exportiert werden.

## 9. Glatte Zentrumserie

Sei die Winkelperiode `Delta_chi`. Ein lokal glatter Pol verlangt

```text
Delta_chi L'(0) = 2 pi.
```

Mit

```text
A(r) = A0 + a2 r^2 + O(r^4),
L(r) = ell1 r [1 + c2 r^2 + O(r^4)],
phi(r) = phi0 + p2 r^2 + O(r^4),
ell1 = 2 pi/Delta_chi,
```

und

```text
Kc = K4 exp(-2A0),
M0 = Q^2 exp(-8A0)/Z_F(phi0),
B0^2 = Q^2 exp(-8A0)/Z_F(phi0)^2,
```

folgen

```text
a2 = [6 Kc - Lambda6 - kappa6^2 V0 + 1/2 kappa6^2 M0]/8,

c2 = kappa6^2 V0/12
     - 5 kappa6^2 M0/24
     - Kc
     + Lambda6/12,

p2 = [V_,phi(phi0) + 1/2 Z_F,phi(phi0) B0^2]
     / [4 Z_phi(phi0)].
```

Der Flux verhält sich regulär als

```text
F_rchi = Q ell1 exp(-4A0)/Z_F(phi0) r + O(r^3),
A_chi = Q ell1 exp(-4A0)/(2 Z_F(phi0)) r^2 + O(r^4)
```

bis auf eine reguläre Gaugekonstante.

## 10. Konischer Modus

Bei fester Winkelperiode ist der Defizitwinkel

```text
delta = 2 pi - Delta_chi L'(0).
```

`delta=0` ist der glatte Zentrumzweig. Das freie Variieren von `L'(0)` bei festem `Delta_chi` aktiviert einen konischen Zentrumparameter. Dieser darf nicht als regulärer zusätzlicher Schießparameter maskiert werden.

## 11. Dimensionshygiene

In natürlichen Einheiten:

```text
[r]=[L]=M^-1,
[A]=1,
[K4]=[Lambda6]=M^2,
[kappa6^2]=M^-4,
[phi]=M^2,
[Q]=M^3 bei dimensionslosem Z_F und dimensionslosem chi,
[V]=M^6,
[M]=M^6.
```

Jede spätere dimensionslose Reskalierung muss eine explizite Variablentabelle und Rücktransformation besitzen.

## 12. Freeze-Status

Dieses Ledger verbessert den Stand wie folgt:

```text
MF-003 reduced radial equations = PARTIAL_CONDITIONAL
MF-004 smooth-centre series = PARTIAL_CONDITIONAL
```

Weiter offen bleiben:

- exaktes `V(phi)` und die Trennung oder Identität mit `Lambda6`,
- exaktes `Z_phi(phi)` und `Z_F(phi)`,
- Fluxquantisierung und Ladungsnormalisierung,
- `Delta_chi` und Defizitwinkelkonvention,
- GHY-, Kappen- und lokalisierte Wirkung,
- orientierte Junction-Gleichungen,
- dimensionslose Solvervariablen,
- Benchmarkdefinitionen und Toleranzen.

Daher gilt weiterhin:

```text
R1.1 = BLOCKED_BY_R1.0
OFFICIAL_SOLVER_IMPLEMENTATION = FORBIDDEN
K1-D = NOT_RELEASED
K1-E = NOT_ADMISSIBLE
```
