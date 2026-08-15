# HZT-M0 / S6 / C-PHYS — H4R4B Global Control Witness and Parent-Equivalence Audit v0.1

**Datum:** 2026-08-15  
**Block:** `C-PHYS-PARENT-H4R4B-ADMISSIBLE-CONSTRAINT-SATISFYING-INITIAL-DATA-CONSTRUCTION-GLOBAL-SECTOR-CLOSURE-AND-FULL-PARENT-EQUIVALENCE-AUDIT`  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Baseline main:** `0acefd910f9ba6883e0ce3e025637935917e1d99`  
**Klassifikation:** exakter analytischer Kontrollzeuge; kein numerischer physikalischer Lauf; keine Evidenzwirkung.

## 1. Fragestellung

H4R4A hat den gauge-fixierten lokalen reduzierten IBVP-Satz konditional ratifiziert, aber ausdrücklich offen gelassen, ob überhaupt global zulässige, constraintsatisfizierende M1-Anfangsdaten existieren, die zugleich die beiden glatten Pole, die U(1)-Patchstruktur, die Fluxquantisierung und die Kappenbedingungen erfüllen.

H4R4B beantwortet genau diese Existenzfrage in der schwächsten wissenschaftlich belastbaren Form:

> Gibt es wenigstens einen nichtleeren M1-Untersektor, in dem ein vollständig expliziter globaler Parent-Hintergrund konstruiert werden kann, dessen `tau=0`-Schnitt die H4R4A-Constraints und alle globalen Sektorbedingungen exakt erfüllt?

Die Antwort lautet **ja**, jedoch nur als Kontrollsektor. Das Ergebnis ist **kein** generischer Existenzsatz für alle M1-Parameter und **keine** D2N-Q-Selektion.

## 2. Verwendete kanonische Eingaben

Verwendet werden ausschließlich kanonische Repository-Eingaben:

- einzeitige Signatur `(-,+,+,+,+,+)`,
- Parent-Einsteinfaktor `M6^4/2`, also `kappa6^2=M6^-4` und `kappa6_hat^2=1`,
- M1-Funktionen
  - `U=0.5*mhat_phi_sq*M6^6*varphi^2`,
  - `Z_F=exp(-2*a_F*varphi)`,
  - `lambda=lambda_hat*M6^5`,
  - `Z_sigma=z_sigma_hat*M6^3`,
- `Delta_chi=2*pi`,
- reguläre Polgauge `A_chi,N(0)=A_chi,S(0)=0`,
- Patchbedingung `a_chi,N(cap)-a_chi,S(cap)=N_F/q_hat`,
- Ladungsgitter `q_sigma=m_sigma*q_ref`,
- globale Flux-/Patch-Äquivalenz aus Freeze-1A.

Gemini-Material bleibt vollständig unter

`EXTERNAL_UNVERIFIED_GEMINI_DRAFT`.

## 3. Exakter Produktansatz

Wir betrachten den 6D-Produktansatz

`dS4(k4) x S2(Rbar)`

mit konstantem M1-Skalar und magnetischem U(1)-Flux auf der internen Zweikugel.

In dimensionslosen Variablen ist die 4D-Geometrie in geschlossener Slicing

```text
-dtau^2 + k4^-1 cosh^2(sqrt(k4)*tau) dOmega3_unit^2,
```

wobei `k4>0` die dimensionslose 4D-de-Sitter-Krümmung ist.

Die interne Kugel wird in zwei reguläre Hemisphären zerlegt. Auf jeder Seite gilt

```text
x_s in [0, pi*Rbar/2],
ell_s(x_s) = Rbar sin(x_s/Rbar),
varphi_s = varphi0.
```

Die gemeinsame Kappe liegt am Äquator

```text
x_N=x_S=pi*Rbar/2.
```

Dort ist

```text
partial_x ell_N = partial_x ell_S = 0.
```

Damit verschwindet die radiale Extrinsikkrümmung der internen Kreisrichtung am Interface.

## 4. Algebraischer Existenzsektor

Definiere

```text
rho_F = mhat_phi_sq*varphi0/(2*a_F).
```

Dann wird

```text
k4 = [Lambda_hat + 0.5*mhat_phi_sq*varphi0^2 - rho_F]/6,
```

und

```text
Rbar_inv_sq
  = 0.5*Lambda_hat
    +0.25*mhat_phi_sq*varphi0^2
    +1.5*rho_F.
```

Für

```text
mhat_phi_sq>0,
a_F>0,
varphi0>0,
k4>0,
Rbar_inv_sq>0
```

existiert damit eine reelle geschlossene de-Sitter-x-S2-Kontrollgeometrie.

Weiter setzen wir

```text
lambda_hat=0,
z_sigma_hat>0.
```

Der Flux-Erstintegralbetrag wird gewählt als

```text
q = sqrt(2*rho_F)*exp(-a_F*varphi0),
q_N=+q,
q_S=-q.
```

Dann ist automatisch

```text
rho_F = 0.5*q^2*exp(2*a_F*varphi0).
```

## 5. Exakte reguläre Gaugepotentiale

Definiere

```text
p = q*exp(2*a_F*varphi0)*Rbar^2.
```

Auf der Nordhemisphäre:

```text
a_chi,N(x_N)=p[1-cos(x_N/Rbar)].
```

Auf der Südhemisphäre:

```text
a_chi,S(x_S)=-p[1-cos(x_S/Rbar)].
```

An beiden glatten Polen gilt exakt

```text
a_chi,s(0)=0,
a_chi,s=O(x_s^2).
```

Die Maxwell-Erstintegralgleichung folgt direkt:

```text
partial_x a_chi,s
  = q_s*ell_s*exp(2*a_F*varphi0).
```

Am Äquator gilt

```text
a_chi,N(cap)=+p,
a_chi,S(cap)=-p.
```

## 6. Globale U(1)-Patch- und Fluxschließung

Wähle einen positiven geraden Fluxsektor

```text
N_F in 2*Z_{>0}
```

und definiere den positiven Modellparameter

```text
q_hat = N_F/(2*p).
```

Dann folgt identisch

```text
R_patch
 = a_chi,N(cap)-a_chi,S(cap)-N_F/q_hat
 = 2*p-N_F/q_hat
 = 0.
```

Mit den regulären Polgauges ist dies nach Freeze-1A zugleich die globale Fluxquantisierung

```text
q_ref*Phi_F = 2*pi*N_F.
```

Der Südpotentialwert wird im lokalen Kappenpatch um den festen Übergang

```text
N_F/q_hat
```

verschoben. Dann stimmen die Potentiale am Interface modulo Gauge exakt überein.

## 7. Kappenphase und verschwindende lokale Kappenenergie

Wähle

```text
m_sigma in Z_{>0},
N_sigma=m_sigma*N_F/2.
```

Da `N_F` gerade ist, ist `N_sigma` ganzzahlig.

Im Nord-Kappenpatch gilt

```text
d_chi
 = N_sigma-m_sigma*q_hat*a_chi,Sigma
 = m_sigma*N_F/2-m_sigma*q_hat*p
 = 0.
```

Somit

```text
Y_hat_sigma=z_sigma_hat*d_chi^2/ell_Sigma^2=0.
```

Zusammen mit `lambda_hat=0` ist die lokale Kappenstressenergie in diesem Kontrollsektor exakt null.

Das ist keine Entfernung des Kappensektors aus der Theorie: die Interface-, Patch- und Ladungsgitterstruktur bleibt vorhanden, aber der gewählte Kontrollhintergrund sitzt auf der stressfreien kovarianten Phase `D_chi sigma=0`.

## 8. Direkte Parent-Gleichungen

Für das Produkt `dS4 x S2` sind die beiden unabhängigen Einstein-Residuen dimensionslos

```text
R_Einstein_internal
 = -6*k4
   +Lambda_hat
   +0.5*mhat_phi_sq*varphi0^2
   -rho_F,
```

und

```text
R_Einstein_4d
 = 3*k4
   +Rbar_inv_sq
   -Lambda_hat
   -0.5*mhat_phi_sq*varphi0^2
   -rho_F.
```

Die konstante Skalargleichung ist

```text
R_scalar
 = mhat_phi_sq*varphi0
   -2*a_F*rho_F.
```

Durch die Definitionen von `rho_F`, `k4` und `Rbar_inv_sq` verschwinden alle drei Residuen identisch.

Die Maxwell-Gleichung ist für den monopolförmigen Zweiform-Flux auf jeder glatten Hemisphäre identisch erfüllt; die nichttriviale globale Information sitzt in der Patch-/Fluxquantisierung, die oben separat geschlossen wurde.

Damit ist dieser Hintergrund nicht nur eine Lösung der reduzierten H4-Gleichungen, sondern direkt eine Lösung der verwendeten Parent-Einstein-Maxwell-Skalar-Gleichungen.

## 9. H4-Reduktionsgleichungen

Im statischen radialen Sektor mit verschwindendem radialen 4D-Warpgradienten ergibt die kanonische M1-Spezialisierung

```text
E_A
 = -6*k4
   +Lambda_hat
   +0.5*mhat_phi_sq*varphi0^2
   -rho_F
 = 0.
```

Für

```text
ell_xx=-ell/Rbar^2
```

wird

```text
E_ell/ell
 = -Rbar_inv_sq
   -3*k4
   +Lambda_hat
   +0.5*mhat_phi_sq*varphi0^2
   +rho_F
 = 0,
```

was genau dem negativen 4D-Parent-Einsteinresiduum entspricht.

Die Skalargleichung reduziert sich auf

```text
-mhat_phi_sq*varphi0+2*a_F*rho_F=0.
```

Der rr-Constraint ist identisch mit `E_A=0`.

Damit ist die Reduktion auf diesem Zeugen direkt mit dem Parent-System kompatibel.

## 10. Exakte Anfangsdaten bei tau=0

Für die geschlossene de-Sitter-Slicing gilt

```text
abar(tau)=k4^-1/2*cosh(sqrt(k4)*tau).
```

Am Zeitsymmetriepunkt `tau=0`:

```text
abar0=1/sqrt(k4),
partial_tau abar=0.
```

In H4R4A-Variablen kann `abar_ref=abar0` gewählt werden. Dann

```text
u=0,
omega=0,
P_omega=P_u=P_v=P_varphi=P_a_chi=0.
```

Der Momentumconstraint ist daher

```text
C_M=0
```

identisch.

Der Hamiltonconstraint reduziert sich auf

```text
C_H
 = Rbar_inv_sq
   +3*k4
   -Lambda_hat
   -0.5*mhat_phi_sq*varphi0^2
   -rho_F
 = 0.
```

Damit ist der `tau=0`-Schnitt ein expliziter globaler constraintsatisfizierender Anfangsdatensatz.

## 11. Glatte Pole

Für jede Hemisphäre:

```text
ell_s(0)=0,
partial_x ell_s(0)=1.
```

Zusätzlich

```text
varphi_x(0)=0,
a_chi,s(0)=0,
a_chi,s=O(x_s^2).
```

Damit sind die Pole geometrisch glatt und die regulären U(1)-Polepatches wohldefiniert.

Wichtig: die H4R4A-Variable

```text
v=ln(ell/ell_ref)
```

ist am Pol nicht regulär, weil `ell=0`. Das ist eine Chart-Degeneration, keine geometrische Singularität. H4R4A wird daher nur auf nichtdegenerierten inneren Charts angewendet; die Polregularität wird in den regulären Variablen `ell` und `a_chi` separat geprüft.

## 12. Kappen-Junctions

Am Äquator sind alle radialen 4D-Warpgradienten null und

```text
partial_x ell_N=partial_x ell_S=0.
```

Daher verschwinden

```text
K_t,
K_a,
K_chi
```

auf beiden Seiten.

Mit

```text
lambda_hat=0,
Y_hat_sigma=0
```

sind alle drei metrischen Junctiongleichungen exakt erfüllt.

Da `varphi` konstant ist, ist auch das skalare Matching exakt erfüllt.

Für das Gauge-Matching gilt wegen

```text
q_N+q_S=0
```

und `d_chi=0` ebenfalls exakt Nullresiduum.

Die Phasengleichung ist trivial erfüllt, weil die kovariante Wicklung verschwindet.

## 13. Kompatibilitätsjets

Der Kontrollhintergrund ist eine exakte zeitabhängige Parent-Lösung, nicht nur ein Anfangsschnitt.

Die radiale Junctionstruktur und die U(1)-Patchdaten sind zeitunabhängig; die 4D-de-Sitter-Geometrie wird auf beiden Seiten identisch induziert.

Daher gilt die lokale H4R4A-Randabbildung für alle `tau`:

```text
B_local(tau)=0.
```

Folglich

```text
J_j = partial_tau^j B_local = 0
```

für jedes endliche `j`.

Damit existiert im Kontrollsektor ein glatter Datensatz, der die gesamte formale Kompatibilitätshierarchie erfüllt.

## 14. Expliziter numerischer Sanity-Punkt

Nur zur reproduzierbaren Formelprüfung, nicht als physikalisch bevorzugter Punkt:

```text
mhat_phi_sq = 1,
a_F = 1/2,
varphi0 = 1,
Lambda_hat = 2,
lambda_hat = 0,
z_sigma_hat = 1,
N_F = 2,
m_sigma = 1,
N_sigma = 1.
```

Dann

```text
rho_F = 1,
k4 = 1/4,
Rbar_inv_sq = 11/4,
Rbar = 2/sqrt(11) ~= 0.6030226892,
q ~= 0.8577638850,
p ~= 0.8478705388,
q_hat ~= 1.1794253418.
```

Alle Parent-, H4-, Constraint-, Junction- und Patchresiduen verschwinden bis auf Rundungsfehler.

## 15. D2N-Q-Audit

Der 4D-Faktor ist radial ungewarpt. Deshalb

```text
beta_r=0,
B^2=0.
```

Dieser Zeuge beweist also **nicht** die nichttriviale D2N-Q-Selektion

```text
B^2=B_Lambda^2+B_m^2*a^-3
```

mit physikalisch relevanten von Null verschiedenen Koeffizienten.

Seine Rolle ist enger und wichtiger für die mathematische Architektur:

```text
nichtleere globale zulässige M1-Datenmenge = bewiesen durch expliziten Kontrollzeugen.
```

Die nichttriviale D2N-Q-Dynamik bleibt offen.

## 16. Bounce-Firewall

Die geschlossene de-Sitter-Slicing besitzt am Symmetriepunkt

```text
H=0,
dH/dtau>0
```

bei regulären Krümmungsinvarianten.

Das wird ausschließlich als bekannte de-Sitter-Kontrollgeometrie klassifiziert. Daraus folgt **keine** HZT-spezifische Erklärung einer primordialen Singularitätsauflösung und kein neuer Bounce-Mechanismus.

## 17. Exaktes Urteil

H4R4B erreicht:

```text
PASS: nichtleerer global zulässiger M1-Untersektor durch expliziten analytischen Parent-Zeugen,
PASS: constraintsatisfizierende Anfangsdaten existieren in diesem Untersektor,
PASS: Pole, Patch, Flux, Junction und Phase schließen für diesen Zeugen,
PASS: volle Parent-zu-H4-Äquivalenz für diesen Zeugen,
OPEN: generische M1-Parameterexistenz,
OPEN: globaler generischer IBVP-Satz inklusive Pole,
OPEN: nichttriviale D2N-Q-Selektion,
OPEN: Hamilton-Positivität,
OPEN: volle Ghostfreiheit.
```

Unverändert:

```text
PHYSICAL_PARENT_SOLVE_AUTHORIZED = FALSE,
MMS_EXECUTION = FALSE,
K1-D = NOT_RELEASED,
K1-E = NOT_ADMISSIBLE,
WP4 = BLOCKED,
PHYSICAL_EVIDENCE = NONE.
```

## 18. Nächster Block

Der nächste sinnvolle Schritt ist nicht ein blindes physikalisches PDE-Running, sondern die kontrollierte Deformation dieses exakten Zeugen:

`C-PHYS-PARENT-H4R4C-GLOBAL-REGULAR-POLE-IBVP-CLOSURE-LINEARIZED-DEFORMATION-AND-NONTRIVIAL-B2-BRANCH-PREFLIGHT`

Ziel ist zu prüfen, ob um den exakt kontrollierten `B^2=0`-Hintergrund ein regulärer globaler Zweig mit nichtverschwindendem radialen 4D-Warpgradienten existieren kann, ohne D2N-Q als Randbedingung einzubauen.
